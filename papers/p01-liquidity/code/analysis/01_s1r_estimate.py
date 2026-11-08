"""F16 · Estimación de `s1r_*` y de la robustez `r1r_*` (SPEC, «Prerregistro de la etapa 1 rediseñada», prereg_commit 3d6b508).

NO SE EJECUTA hasta el visto bueno de los autores para F16: es el primer script que mira la respuesta de la inversión real. Escrito en
F15 y probado solo con datos simulados (`test_s1r_estimate.py`).

Todo con `aum` (ε_{t−10..t+12} como controles, `s1r_lp.AUM`) y NW(5) de Bartlett en trimestres naturales con residuos HC3, t de N − k
g.l. (`s1_lp.fit(..., leverage=True)`). Estado D_{t−1}: s_{t−1} < mediana de s_{t−1} en la muestra completa; quitar filas (sin Volcker,
desde 1971Q3) no lo recalcula, ni tampoco los retardos, adelantos y ȳ de las demás filas.
- `s1r_lin`, `s1r_liq`: 1969Q1–2005Q2 (N = 146). `s1r_liq_nov`: sin 1979Q4–1982Q4 (N = 133).
- `r1r_from1971q3`: `s1r_liq` sin 1969Q1–1971Q2. `r1r_state_q25`: restringido = s_{t−1} < cuartil inferior (muestra completa).
- `r1r_state_logistic`: D → F(z) = 1 / (1 + exp(γ z)), z = (s_{t−1} − mediana) / desv. típ. de s_{t−1} (muestra completa), γ = 3: la
  logística de Tenreyro-Thwaites con z de varianza unitaria, orientada para que F → 1 con liquidez baja (el estado restringido).
- `r1r_lags4`: `s1r_liq` con 4 retardos de los controles.

Salidas: `output/estimates_py.csv` (s1r_*, todos los coeficientes; la réplica en R escribe `estimates_r.csv` para la paridad),
`output/estimates_py_robustness.csv` (r1r_*, sin réplica en R), `output/tables/s1r_estimates.md` (términos que deciden y veredicto V3s)
y `output/tables/s1r_shock_diagnostics.md` (D1, D2, D3, Ljung-Box y predictibilidad; sin la inversión).
Uso: uv run python papers/p01-liquidity/code/analysis/01_s1r_estimate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
sys.path[:0] = [str(HERE), str(PAPER / "code" / "data"), str(PAPER.parents[1] / "tools")]
import build_stage1_us
import research
import s1_lp
import s1r_lp
import sample_counts_s1r

VOLCKER = pd.period_range(*sample_counts_s1r.VOLCKER, freq="Q")
FROM = pd.Period("1971Q3", "Q")
GAMMA = 3.0
SE_LAGS = 5
DIAG_LAGS = 4  # predictibilidad: retardos de PIB, deflactor y fed funds (SPEC, DP)
COLUMNS = ["spec_id", "term", "estimate", "std_error", "dof"]
CONFIRMATORY = ("s1r_lin", "s1r_liq", "s1r_liq_nov")
# id → (modelo, muestra, estado, retardos de los controles, descripción para log_spec)
SPECS = {
    "s1r_lin": ("lin", "full", "median", 2, "H0: ȳ(4..12) sobre ε, aum, 1969Q1–2005Q2, NW5+HC3"),
    "s1r_liq": ("liq", "full", "median", 2, "H1: β_C y β_U por estado de liquidez, aum, 1969Q1–2005Q2, NW5+HC3"),
    "s1r_liq_nov": ("liq", "nov", "median", 2, "H1 sin 1979Q4–1982Q4 (V3s), aum, NW5+HC3"),
    "r1r_from1971q3": ("liq", "from1971q3", "median", 2, "robustez: s1r_liq desde 1971Q3"),
    "r1r_state_q25": ("liq", "full", "q25", 2, "robustez: s1r_liq con restringido = cuartil inferior de s"),
    "r1r_state_logistic": ("liq", "full", "logistic", 2, "robustez: s1r_liq con estado logístico, γ = 3, c = mediana"),
    "r1r_lags4": ("liq", "full", "median", 4, "robustez: s1r_liq con 4 retardos de los controles"),
}


def panel() -> pd.DataFrame:
    """Panel trimestral de F7 con la inversión, el PIB y el deflactor de FRED (el mismo que el MC, `f9_power.panel`)."""
    df = sample_counts_s1r.panel()
    for col, name in (("inv", "A008RA3Q086SBEA"), ("gdp", "GDPC1"), ("defl", "GDPDEF")):
        s = build_stage1_us.fred(name)
        s.index = s.index.to_period("Q")
        df[col] = s.reindex(df.index)
    return df


def samples(df: pd.DataFrame) -> dict[str, pd.Index]:
    full = df.index[df["in_rr_sample"].astype(bool) & df["s_lag"].notna() & df["rr_shock"].notna()]  # = sample_counts_s1r.samples
    return {"full": full, "nov": full[~full.isin(VOLCKER)], "from1971q3": full[full >= FROM]}


def states(s_lag: pd.Series, full: pd.Index) -> dict[str, pd.Series]:
    s = s_lag.loc[full]
    z = (s_lag - s.median()) / s.std()
    return {"median": s1_lp.state(s_lag, full), "q25": (s_lag < s.quantile(0.25)).astype(float),
            "logistic": 1 / (1 + np.exp(GAMMA * z))}


def estimates(df: pd.DataFrame, ids=tuple(SPECS)) -> pd.DataFrame:
    """Estimaciones de `ids` sobre un panel con `rr_shock`, `s_lag`, `in_rr_sample`, `inv`, `gdp`, `defl` y `ffr` (columnas COLUMNS)."""
    smp = samples(df)
    D = states(df["s_lag"], smp["full"])
    y = s1r_lp.ybar(np.log(df["inv"]))
    ctrl = s1r_lp.controls(df)
    out = []
    for sid in ids:
        model, sample, state, ctrl_lags, _ = SPECS[sid]
        rows = smp[sample]
        X = s1r_lp.design(df["rr_shock"], D[state], ctrl, rows, model, *s1r_lp.AUM, ctrl_lags=ctrl_lags)
        yr = y.loc[rows]
        assert yr.notna().all() and X.notna().all().all(), f"{sid}: faltan datos en la muestra"
        b, se, dof = s1_lp.fit(yr.to_numpy(), X.to_numpy(), s1_lp.hac_weights(rows.asi8, SE_LAGS), leverage=True)
        out.append(pd.DataFrame({"spec_id": sid, "term": X.columns, "estimate": b, "std_error": se, "dof": dof}))
    return pd.concat(out, ignore_index=True)[COLUMNS]


def term(est: pd.DataFrame, sid: str, name: str) -> tuple[float, float, int]:
    r = est[(est["spec_id"] == sid) & (est["term"] == name)].iloc[0]
    return float(r["estimate"]), float(r["std_error"]), int(r["dof"])


def verdict(est: pd.DataFrame) -> str:
    """Árbol V3s de la SPEC: H0 con `s1r_lin` (completa), H1 con `s1r_liq` (completa) y `s1r_liq_nov`."""
    h0 = s1r_lp.h0_confirms(*term(est, "s1r_lin", "b_lin"))
    h1_full = s1r_lp.h1_verdict(*term(est, "s1r_liq", "b_C"))
    h1_nov = s1r_lp.h1_verdict(*term(est, "s1r_liq_nov", "b_C"))
    return s1r_lp.decide("V3s", h0, h1_full, h1_nov=h1_nov)


def shock_diagnostics(df: pd.DataFrame) -> str:
    """D1, D2, D3, Ljung-Box(12) y predictibilidad del choque, con y sin Volcker. No usa la inversión."""
    smp = samples(df)
    D = states(df["s_lag"], smp["full"])["median"]
    x = pd.DataFrame({"dlgdp": 100 * np.log(df["gdp"]).diff(), "dldefl": 100 * np.log(df["defl"]).diff(), "dffr": df["ffr"].diff()})
    Z = pd.concat({f"{v}_l{j}": x[v].shift(j) for v in x for j in range(1, DIAG_LAGS + 1)}, axis=1)
    L = ["# Diagnósticos de los choques de `s1r_*` (generado por `code/analysis/01_s1r_estimate.py`)\n",
         ("Sin la inversión (SPEC, «Diagnósticos de los choques»). D1/D2: trimestres y Σ|ε| por estado de D_{t−1} (mediana de la muestra "
          "completa). D3: MCO de ε_t sobre (1, D_{t−1}, s_{t−1}), ee HC1, F de Wald de las 2 pendientes. Ljung-Box con 12 retardos. "
          f"Predictibilidad: MCO de ε_t sobre una constante y {DIAG_LAGS} retardos de 100·Δlog PIB real, 100·Δlog deflactor y Δffr, "
          f"F de Wald HC1 de las {3 * DIAG_LAGS} pendientes. Sin Volcker = sin 1979Q4–1982Q4, con el hueco concatenado.\n"),
         "| muestra | N | D1 restr. | D1 holg. | D2 Σ\\|ε\\| restr. | D2 Σ\\|ε\\| holg. | D3 F | D3 p | Ljung-Box(12) | p | F predict. | g.l. | p |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in ("full", "nov"):
        rows = smp[name]
        e, d = df["rr_shock"].loc[rows], D.loc[rows]
        bal = sm.OLS(e, sm.add_constant(pd.DataFrame({"D": d, "s_lag": df["s_lag"].loc[rows]}))).fit(cov_type="HC1")
        f3 = bal.f_test(np.eye(3)[1:])
        lb = acorr_ljungbox(e.to_numpy(), lags=[12])
        pr = sm.OLS(e, sm.add_constant(Z.loc[rows])).fit(cov_type="HC1")
        fp = pr.f_test(np.eye(len(pr.params))[1:])
        L.append(f"| {'completa' if name == 'full' else 'sin Volcker'} | {len(rows)} | {int(d.sum())} | {int((1 - d).sum())} | "
                 f"{e[d == 1].abs().sum():.3f} | {e[d == 0].abs().sum():.3f} | {float(np.squeeze(f3.fvalue)):.2f} | {float(f3.pvalue):.3f} | "
                 f"{float(lb['lb_stat'].iloc[0]):.2f} | {float(lb['lb_pvalue'].iloc[0]):.3f} | {float(np.squeeze(fp.fvalue)):.2f} | "
                 f"({int(fp.df_num)}, {int(fp.df_denom)}) | {float(fp.pvalue):.3f} |")
    return "\n".join(L) + "\n"


def results_table(est: pd.DataFrame) -> str:
    L = ["# Estimaciones de `s1r_*` y `r1r_*` (generado por `code/analysis/01_s1r_estimate.py`)\n",
         "`aum`, NW(5)+HC3, t de N − k g.l.; p unilateral de β < 0. Pp de ȳ (h = 4..12) por pp de choque (ε sumado en el trimestre).\n",
         "| id | término | β̂ | ee | g.l. | p (β < 0) | IC al 95 % |", "|---|---|---|---|---|---|---|"]
    for sid, (model, *_rest) in SPECS.items():
        for name in s1r_lp.TERMS[model]:
            b, se, dof = term(est, sid, name)
            p = s1_lp.one_sided_p(np.array([b]), np.array([se]), dof)[0]
            h = stats.t.ppf(0.975, dof) * se
            L.append(f"| {sid} | {name} | {b:.3f} | {se:.3f} | {dof} | {p:.3f} | [{b - h:.3f}, {b + h:.3f}] |")
    L.append(f"\n**Veredicto V3s** (`s1r_lp.decide`): `{verdict(est)}`. Se presenta con el IC y el MDE de la SPEC; `s1r_liq_nov` lleva la "
             "salvedad del Ljung-Box sin Volcker (SPEC, «Diagnósticos de los choques»).\n")
    return "\n".join(L)


def main() -> None:
    df = panel()
    script = Path(__file__).relative_to(PAPER).as_posix()
    for sid, spec in SPECS.items():
        research.log_spec(PAPER, sid, script, spec[-1])
    est = estimates(df)
    out = PAPER / "output"
    conf = est["spec_id"].isin(CONFIRMATORY)
    est[conf].to_csv(out / "estimates_py.csv", index=False)
    est[~conf].to_csv(out / "estimates_py_robustness.csv", index=False)
    (out / "tables" / "s1r_shock_diagnostics.md").write_text(shock_diagnostics(df), encoding="utf-8")
    (out / "tables" / "s1r_estimates.md").write_text(results_table(est), encoding="utf-8")
    print(f"escrito {out / 'estimates_py.csv'}; veredicto V3s: {verdict(est)}")


if __name__ == "__main__":
    main()
