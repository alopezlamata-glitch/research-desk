"""F13 · Comprobaciones para el prerregistro `s1r_*` (encargo desks/econometria/ENCARGO_2026-11-08_f13-comprobaciones-s1r.md).

Regla dura (la de F4 y F9): nada se estima con la inversión real ni se mira cómo responde a los choques. El MC reutiliza el DGP de
F9 (`f9_power.DGP`: de la inversión solo entra el AR(2) univariante de su crecimiento) y la misma semilla y réplicas en las celdas que
repite. Los diagnósticos de los choques usan solo el choque, el PIB, el deflactor y el fed funds.

1. Agregación del choque: F7 suma los 3 meses; Tenreyro-Thwaites los promedian (F12, punto 1). Se compara la suma con la media de los
   3 meses y, como sensibilidad, con la media de los meses con choque ≠ 0 (aproxima la media por reunión, que el Handbook no trae).
2. V3s con `aum`: P(confirma) del árbol en c = 4 (y 5,5 y 6, entre los que cae el MDE de F9) y la fila del rival (β_C = 0).
3. Ljung-Box(12) y predictibilidad de Romer-Romer con PIB, deflactor y fed funds pasados (F de Wald HC1), como R-F10.

Uso: uv run python papers/p01-liquidity/code/mc/f13_checks.py   (escribe output/tables/f13_checks.md y f13_shock_diagnostics.md; ≈ 10 min)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "data"), str(HERE.parent / "analysis")]
import build_stage1r_us
import f9_power as f9
import s1r_lp

SEED, REPS = f9.SEED, f9.REPS
KIND = f9.TESTED_SE
NOISES = ("homo", "het_eps")  # los de la potencia de F9 (§2–3)
CS_F9 = [0, 1, 2, 3, 5, 7, 10]  # rejilla de F9: su índice j fija la semilla
CS_NEW = {4: 7, 5.5: 8, 6: 9}  # c nuevos → j que no usó F9
CS = [1, 2, 3, 4, 5, 5.5, 6, 7]
OUT = ["h0_falla", "confirma", "refuta_a", "no_concluyente"]  # la regla (b) se retira (Desviación 2026-11-08): refuta_b → no concluyente
DIAG_LAGS = 4


def seed(noise: str, m: int, c: float) -> int:
    """Semilla de la celda (ruido, m, c) de F9 (§2–4); los c nuevos usan j ≥ 7."""
    j = CS_F9.index(c) if c in CS_F9 else CS_NEW[c]
    return SEED + 10_000 + 1000 * NOISES.index(noise) + 100 * m + j


def aggregations(monthly: pd.Series) -> pd.DataFrame:
    """Choque trimestral: 'suma' (F7), 'media3' (media de los 3 meses) y 'media_nz' (media de los meses con choque ≠ 0; 0 si no hay)."""
    g = monthly.groupby(monthly.index.asfreq("Q"))
    nz = monthly.where(monthly != 0).groupby(monthly.index.asfreq("Q"))
    return pd.DataFrame({"suma": g.sum(), "media3": g.mean(), "media_nz": nz.mean().fillna(0.0)})


def tree(R: dict, bref: float) -> pd.Series:
    """Probabilidades del árbol V3s (con la puerta H0) sobre las réplicas de `simulate`, especificación 'aum'."""
    p = f9.verdict_probs(R["aum"], KIND, "fijo", bref, "RR", "RR_noV")["V3s"]
    p = p.reindex(f9.OUTCOMES, fill_value=0.0)
    p["no_concluyente"] += p.pop("refuta_b")
    return p


def h_power(A: np.ndarray) -> tuple[float, float]:
    """Potencia sin condicionar de H0 (β_lin < 0) y H1 (β_C < 0), p unilateral < 0,05."""
    return tuple(float((f9.stats.t.cdf(A[:, i] / A[:, i + 1], A[:, d]) < 0.05).mean()) for i, d in ((0, 6), (2, 7)))


def run(df: pd.DataFrame, shock: str, smp: dict, bref: float, m: int, c: float, noise: str) -> dict:
    dgp = f9.DGP(df, shock, smp, m * c * bref, c * bref, noise, specs=("aum",))
    return f9.simulate(dgp, len(smp["RR"]), REPS, seed(noise, m, c), (KIND,))


def ljung_box(x: pd.Series, lags: int = 12) -> tuple[float, float]:
    r = acorr_ljungbox(x.to_numpy(), lags=[lags])
    return float(r["lb_stat"].iloc[0]), float(r["lb_pvalue"].iloc[0])


def predictability(df: pd.DataFrame, shock: str, rows: pd.Index, lags: int = DIAG_LAGS):
    """F de Wald HC1 de que los retardos 1..lags de Δlog PIB, Δlog deflactor y Δffr no predicen el choque. (F, g.l.1, g.l.2, p)."""
    x = pd.DataFrame({"dlgdp": 100 * np.log(df["gdp"]).diff(), "dldefl": 100 * np.log(df["defl"]).diff(), "dffr": df["ffr"].diff()})
    Z = pd.concat({f"{v}_l{j}": x[v].shift(j) for v in x for j in range(1, lags + 1)}, axis=1).loc[rows]
    res = sm.OLS(df[shock].loc[rows], sm.add_constant(Z)).fit(cov_type="HC1")
    ft = res.f_test(np.eye(len(res.params))[1:])
    return float(np.squeeze(ft.fvalue)), int(ft.df_num), int(ft.df_denom), float(ft.pvalue)


def diagnostics(df: pd.DataFrame, smp: dict) -> str:
    L = ["# F13 · Diagnósticos del choque de Romer-Romer (generado por `code/mc/f13_checks.py`)\n",
         ("Sin la inversión. Choque `rr_shock` (suma de los 3 meses, F7); los dos contrastes son invariantes a reescalar el choque. "
         "Sin Volcker = la muestra completa sin 1979Q4–1982Q4, con el hueco concatenado (como R-F10). Ljung-Box con 12 retardos. "
         f"Predictibilidad: MCO del choque sobre una constante y {DIAG_LAGS} retardos de 100·Δlog PIB real (`GDPC1`), 100·Δlog deflactor "
         f"(`GDPDEF`) y Δ fed funds; F de Wald HC1 de las {3 * DIAG_LAGS} pendientes = 0.\n"),
         "| muestra | N | ρ1 | ρ2 | ρ3 | ρ4 | Ljung-Box(12) | p | F de predictibilidad | g.l. | p |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, rows in smp.items():
        x = df["rr_shock"].loc[rows]
        rho = [float(sm.tsa.acf(x.to_numpy(), nlags=4)[k]) for k in range(1, 5)]
        q, pq = ljung_box(x)
        F, d1, d2, pf = predictability(df, "rr_shock", rows)
        L.append(f"| {'completa' if name == 'RR' else 'sin Volcker'} | {len(rows)} | " + " | ".join(f"{r:.3f}" for r in rho)
                 + f" | {q:.2f} | {pq:.3f} | {F:.2f} | ({d1}, {d2}) | {pf:.3f} |")
    return "\n".join(L) + "\n"


def main() -> None:
    df = f9.panel()
    agg = aggregations(build_stage1r_us.rr_monthly()).reindex(df.index)
    assert np.allclose(agg["suma"].dropna(), df["rr_shock"].dropna()), "la suma no reproduce el choque de F7"
    df = df.join(agg)
    full = f9.samples(df)
    smp = {k: full[k] for k in ("RR", "RR_noV")}
    m_w = f9.signal_share(s1r_lp.HORIZONS)
    L = [f"# F13 · Comprobaciones para `s1r_*` (generado por `code/mc/f13_checks.py`, semilla {SEED}, {REPS} réplicas)\n",
         (f"V3s con `aum`, ee {KIND}, T = N, DGP y semillas de F9 (`f9_power.py`, §2–4). Regla (b) retirada: `refuta_b` cuenta como no "
         "concluyente. β_ref = −2,5 × m_W × π(h = 0), π de ffr_t − ffr_(t−1) sobre ε_t en la muestra completa.\n")]

    # 1. Agregación del choque
    bref, pis, R1 = {}, {}, {}
    for a in agg:
        pis[a] = f9.rate_response(df, smp["RR"], a, 0)
        bref[a] = f9.beta_ref(pis[a][0])
        R1[a] = {n: run(df, a, smp, bref[a], 1, 1, n) for n in NOISES}
    L += ["## 1. ¿Cambian β_ref y la potencia frente a β_ref al promediar el choque en vez de sumarlo?\n",
          ("| agregación | sd(ε) completa | π(h = 0) (ee) | β_ref (pp de ȳ por pp de ε) | β_ref × sd(ε) | ruido | P(confirma) V3s, c = 1 | "
          "potencia H0 | potencia H1 (completa) |"), "|---|---|---|---|---|---|---|---|---|"]
    for a in agg:
        for n in NOISES:
            A = R1[a][n]["aum"]["RR"][KIND]
            p0, p1 = h_power(A)
            L.append(f"| {a} | {df[a].loc[smp['RR']].std():.4f} | {pis[a][0]:.3f} ({pis[a][1]:.3f}) | {bref[a]:.3f} | "
                     f"{bref[a] * df[a].loc[smp['RR']].std():.3f} | {n} | {tree(R1[a][n], bref[a])['confirma']:.3f} | {p0:.3f} | {p1:.3f} |")
    L.append("\n**Media de 3 meses frente a suma, en las mismas réplicas** (misma semilla): ε_media3 = ε_suma/3 en todos los trimestres, "
             "así que π, β_ref, β̂ y ee se multiplican por 3 y los estadísticos t no cambian.\n")
    L.append("| ruido | máx. \\|ε_suma/3 − ε_media3\\| | π_media3/π_suma | β_ref,media3/β_ref,suma | máx. \\|Δt\\| (b_lin, b_C, b_U; completa y sin Volcker) "
             "| máx. \\|β̂_media3/β̂_suma − 3\\| | veredictos V3s idénticos |")
    L.append("|---|---|---|---|---|---|---|")
    for n in NOISES:
        dt, dr = 0.0, 0.0
        for s in smp:
            A, B = R1["suma"][n]["aum"][s][KIND], R1["media3"][n]["aum"][s][KIND]
            for i in (0, 2, 4):
                dt = max(dt, float(np.abs(A[:, i] / A[:, i + 1] - B[:, i] / B[:, i + 1]).max()))
                dr = max(dr, float(np.abs(B[:, i] / A[:, i] - 3).max()))
        same = tree(R1["suma"][n], bref["suma"]).equals(tree(R1["media3"][n], bref["media3"]))
        L.append(f"| {n} | {float((df['suma'] / 3 - df['media3']).abs().max()):.1e} | {pis['media3'][0] / pis['suma'][0]:.6f} | "
                 f"{bref['media3'] / bref['suma']:.6f} | {dt:.1e} | {dr:.1e} | {'sí' if same else 'NO'} |")
    L.append(f"\nEl MDE en pp de ȳ por pp de fed funds (c × 2,5 × m_W = c × {2.5 * m_w:.3f}) no depende de la agregación; el MDE en pp de ȳ por "
             "pp de ε sí (×3 con la media), así que el prerregistro tiene que fijar la unidad de ε.\n")

    # 2. MDE en c = 4 y fila del rival, V3s con `aum`
    R2 = {(n, m, c): run(df, "rr_shock", smp, bref["suma"], m, c, n) for n in NOISES for m in (1, 0) for c in CS}
    L += ["## 2. V3s con `aum` (choque sumado, como F9): P(desenlace) frente a c, H1 cierta (m = 1) y rival (m = 0: β_C = 0, β_U = c·β_ref)\n",
          (f"c = 4, 5,5 y 6 son celdas nuevas; las demás repiten las de F9 con su semilla. β_ref = {bref['suma']:.3f}. MDE en pp de ȳ por pp de ε "
          f"= c × {abs(bref['suma']):.3f}; por pp de fed funds = c × {2.5 * m_w:.3f}.\n"),
          "| ruido | m | c | MDE pp/pp ε | MDE pp/pp ffr | " + " | ".join(OUT) + " | potencia H0 | potencia H1 (completa) |",
          "|---|---|---|---|---|" + "---|" * (len(OUT) + 2)]
    for (n, m, c), R in R2.items():
        p = tree(R, bref["suma"])
        p0, p1 = h_power(R["aum"]["RR"][KIND])
        L.append(f"| {n} | {m} | {c:g} | {c * abs(bref['suma']):.2f} | {c * 2.5 * m_w:.2f} | " + " | ".join(f"{p[o]:.3f}" for o in OUT)
                 + f" | {p0:.3f} | {p1:.3f} |")
    L.append("\n### 2b. c con P(confirma) = 0,8 (interpolación lineal en la rejilla de arriba)\n")
    L += ["| ruido | c con 0,8 | MDE pp de ȳ por pp de ε | MDE pp de ȳ por pp de fed funds | máx. P(confirma) del rival, c ≤ 5 |", "|---|---|---|---|---|"]
    for n in NOISES:
        c8 = f9.c80(CS, [tree(R2[(n, 1, c)], bref["suma"])["confirma"] for c in CS])
        num = c8[0].isdigit()
        riv = max(tree(R2[(n, 0, c)], bref["suma"])["confirma"] for c in CS if c <= 5)
        L.append(f"| {n} | {c8} | {float(c8) * abs(bref['suma']):.2f} | {float(c8) * 2.5 * m_w:.2f} | {riv:.3f} |" if num else
                 f"| {n} | {c8} | — | — | {riv:.3f} |")

    f9.TABLES.mkdir(parents=True, exist_ok=True)
    (f9.TABLES / "f13_checks.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (f9.TABLES / "f13_shock_diagnostics.md").write_text(diagnostics(df, smp), encoding="utf-8")
    print(f"escrito {f9.TABLES / 'f13_checks.md'} y {f9.TABLES / 'f13_shock_diagnostics.md'}")


if __name__ == "__main__":
    main()
