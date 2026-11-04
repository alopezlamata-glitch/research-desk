"""F4 · Monte Carlo de la especificación prerregistrada `s1_liq` (encargo ENCARGO_2026-11-04_f4-montecarlo.md).

Regla dura: no se estima `s1_lin`/`s1_liq` con la inversión real ni se mira su respuesta a los choques. Del panel se usan los
choques, el estado D_{t−1}, los controles (incluido el retardo de Δlog inversión, como serie AR) y la muestra exacta (N = 102).

DGP (calendario trimestral completo del panel, para respetar solapes y huecos):
    g_t = μ + φ1 g_{t−1} + φ2 g_{t−2} + b_t ε_t + e_t,   g = 100·Δlog I simulado
    b_t = b^{signo(ε_t)}_{D_{t−1}},  b = β/κ,  κ = efecto en ȳ de un impulso unitario en g_t (respuesta AR(2) acumulada, media h=0..4)
    e_t: remuestreo iid de los residuos del AR(2) univariante de la Δlog inversión real en la muestra (sin choques).
    ε_t, D_{t−1} y los otros 4 controles: reales. ȳ, y el control Δlog inversión, se construyen con el g simulado.
El error de ȳ es MA(4) por el solape (más la respuesta a choques futuros ε_{t+1..t+4}), como en los datos.

Uso: uv run python papers/p01-liquidity/code/mc/f4_power.py   (escribe output/tables/f4_power.md y mc_s1_liq.txt)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lfilter

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER / "code" / "data"), str(PAPER / "code" / "analysis"), str(PAPER.parents[1] / "tools")]
import mc
import s1_lp
import sample_counts

SEED = 20261104
REPS = 1000
NW_LAGS = 5
# β_ref (PREREG_DRAFT §3): Tenreyro-Thwaites (2016) pp. 11–12: la inversión empresarial cae ≈2,5 % en el pico por 1 pp del
# fed funds (modelo lineal); el pico del output llega "two to three years after the shock" (p. 11). Supuesto: rampa lineal
# desde 0 en h=0 hasta el pico en h = PEAK_H; la media de h=0..4 es entonces PEAK·mean(h)/PEAK_H.
TT_PEAK = -2.5
PEAK_H = 10  # 2,5 años; sensibilidad con 8 y 12
SE_KINDS = {  # nombre → (pesos, corrección N/(N−k), residuos corregidos por apalancamiento)
    "NW5 calendario (prerreg.)": ("cal", False, False),
    "NW5 filas": ("rows", False, False),
    "NW5 calendario ×N/(N−k)": ("cal", True, False),
    "HC1 (White ×N/(N−k))": ("white", True, False),
    "HC3": ("white", False, True),
    "NW5 calendario con residuos HC3": ("cal", False, True),
}
MAIN_SE = "NW5 calendario (prerreg.)"
RECOMMENDED_SE = "NW5 calendario con residuos HC3"  # la que F4 recomienda (ver F4_MC_REPORT.md)


def ar2(g: pd.Series, rows: pd.Index) -> tuple[np.ndarray, np.ndarray]:
    """MCO de g_t sobre (1, g_{t−1}, g_{t−2}) en las filas de la muestra → (μ, φ1, φ2), residuos."""
    Z = np.column_stack([np.ones(len(rows)), g.shift(1).loc[rows], g.shift(2).loc[rows]])
    y = g.loc[rows].to_numpy()
    coef = np.linalg.lstsq(Z, y, rcond=None)[0]
    return coef, y - Z @ coef


def kappa(phi1: float, phi2: float) -> float:
    """Efecto en ȳ de un impulso unitario en g_t: (1/5) Σ_{h=0..4} Σ_{j≤h} ψ_j, con ψ la respuesta del AR(2)."""
    psi = lfilter([1.0], [1.0, -phi1, -phi2], np.r_[1.0, np.zeros(s1_lp.H)])
    return float(np.cumsum(psi).mean())


def rate_response(df: pd.DataFrame, rows: pd.Index, var: str, h: int = 0) -> tuple[float, float]:
    """Respuesta de un tipo (no de la inversión) a ε: MCO de var_{t+h} − var_{t−1} sobre (1, ε_t), ee de White."""
    y = (df[var].shift(-h) - df[var].shift(1)).loc[rows].to_numpy()
    X = np.column_stack([np.ones(len(rows)), df["mps_bs23_orth"].loc[rows]])
    b, se, _ = s1_lp.fit(y, X, np.eye(len(rows)), small_sample=True)
    return float(b[1]), float(se[1])


def beta_ref(pi_ffr: float, peak_h: int = PEAK_H) -> float:
    """β_ref en unidades de ȳ (pp) por 1 pp de ε (escala ED4 de Bauer-Swanson)."""
    return TT_PEAK * np.arange(s1_lp.H + 1).mean() / peak_h * pi_ffr


class DGP:
    """Simula ȳ con los choques, estados, controles y muestra reales. Llamable como `dgp(T, rng)` para tools/mc.py."""

    def __init__(self, df: pd.DataFrame, rows: pd.Index, betas: dict[str, float], sigma_scale: float = 1.0, burn: int = 40):
        self.df, self.rows, self.burn = df, rows, burn
        g_real = 100 * np.log(df["inv_nonres_q"]).diff()
        (self.mu, self.phi1, self.phi2), resid = ar2(g_real, rows)
        self.resid = sigma_scale * (resid - resid.mean())
        self.eps = df["mps_bs23_orth"]
        self.D = s1_lp.state(df["s_lag"], rows)  # estado verdadero = el de la muestra completa (también con T/2)
        e0 = self.eps.fillna(0.0).to_numpy()
        Dn = self.D.to_numpy()
        k = kappa(self.phi1, self.phi2)
        b = {name: v / k for name, v in betas.items()}
        self.impulse = np.where(e0 > 0, Dn * b["b_pos_C"] + (1 - Dn) * b["b_pos_U"],
                                Dn * b["b_neg_C"] + (1 - Dn) * b["b_neg_U"]) * e0
        self.ctrl = s1_lp.controls(df)
        self.qord = np.asarray(df.index.asi8)
        self.pos = df.index.get_indexer(rows)

    def g(self, rng: np.random.Generator) -> np.ndarray:
        n = len(self.df) + self.burn
        shock = self.mu + np.r_[np.zeros(self.burn), self.impulse] + rng.choice(self.resid, n)
        return lfilter([1.0], [1.0, -self.phi1, -self.phi2], shock)[self.burn:]

    def __call__(self, T: int, rng: np.random.Generator):
        g = pd.Series(self.g(rng), index=self.df.index)
        y = s1_lp.ybar((g / 100).cumsum())
        start = 0 if T >= len(self.rows) else int(rng.integers(0, len(self.rows) - T + 1))
        rows = self.rows[start:start + T]
        ctrl = self.ctrl.assign(dlinv=g)
        X = s1_lp.design(self.eps, self.D, ctrl, rows)
        return y.loc[rows].to_numpy(), X, self.qord[self.df.index.get_indexer(rows)]


def estimate(data, kind: str) -> tuple[dict[str, float], dict[str, float], int]:
    y, X, q = data
    w, small, lev = SE_KINDS[kind]
    W = {"cal": lambda: s1_lp.hac_weights(q, NW_LAGS), "rows": lambda: s1_lp.hac_weights(np.arange(len(q)), NW_LAGS),
         "white": lambda: np.eye(len(q))}[w]()
    b, se, dof = s1_lp.fit(y, X.to_numpy(), W, small, lev)
    idx = [X.columns.get_loc(t) for t in s1_lp.TERMS]
    return dict(zip(s1_lp.TERMS, b[idx])), dict(zip(s1_lp.TERMS, se[idx])), dof


def design_error(df: pd.DataFrame, rows: pd.Index, betas: dict[str, float]) -> np.ndarray:
    """β̂ − β sin ruido (e = 0): error determinista que dejan las respuestas a choques futuros ε_{t+1..t+4} dentro de ȳ_t,
    dados los choques reales. Es (casi) proporcional a β y no se promedia entre réplicas porque los choques son fijos."""
    data = DGP(df, rows, betas, sigma_scale=0.0)(len(rows), np.random.default_rng(0))
    b, _, _ = estimate(data, MAIN_SE)
    return np.array([b[t] - betas[t] for t in s1_lp.TERMS])


def mc_estimator(kind: str):
    """Adaptador para tools/mc.py: (estimaciones, ee) en el orden de s1_lp.TERMS."""
    def f(data):
        b, se, _ = estimate(data, kind)
        return [b[t] for t in s1_lp.TERMS], [se[t] for t in s1_lp.TERMS]
    return f


def simulate(dgp: DGP, betas: dict[str, float], T: int, reps: int, seed: int, kinds=tuple(SE_KINDS)) -> dict:
    """Por tipo de ee: sesgo, RMSE, cobertura (t de N−k) por término; probabilidad de cada veredicto por sentido."""
    rng = np.random.default_rng(seed)
    B = {k: np.empty((reps, 4)) for k in kinds}
    S = {k: np.empty((reps, 4)) for k in kinds}
    V = {k: {"pos": [], "neg": []} for k in kinds}
    overlap = {k: 0 for k in kinds}
    dof = 0
    for r in range(reps):
        data = dgp(T, rng)
        for k in kinds:
            b, se, dof = estimate(data, k)
            B[k][r] = [b[t] for t in s1_lp.TERMS]
            S[k][r] = [se[t] for t in s1_lp.TERMS]
            v = s1_lp.verdicts(b, se, dof)
            for d in ("pos", "neg"):
                V[k][d].append(v[d])
                overlap[k] += v[d] == "confirma" and s1_lp.refute_b_also(b, se, dof, d)
    truth = np.array([betas[t] for t in s1_lp.TERMS])
    tc = stats.t.ppf(0.975, dof)
    out = {}
    for k in kinds:
        err = B[k] - truth
        out[k] = {
            "bias": err.mean(0), "rmse": np.sqrt((err ** 2).mean(0)), "sd": B[k].std(0), "se_mean": S[k].mean(0),
            "cover": (np.abs(err) <= tc * S[k]).mean(0),
            "verdicts": {d: pd.Series(V[k][d]).value_counts(normalize=True) for d in ("pos", "neg")},
            "overlap": overlap[k] / (2 * reps),
        }
    return out


def scenario_betas(bref: float, m: float) -> dict[str, float]:
    return {"b_pos_C": m * bref, "b_pos_U": bref, "b_neg_C": m * bref, "b_neg_U": bref}


VERDICTS = ["confirma", "refuta_a", "refuta_b", "no_concluyente"]


def main() -> None:
    df = sample_counts.panel()
    rows, _ = sample_counts.sample(df)
    rows = rows.index
    N = len(rows)
    pi_ffr, pi_se = rate_response(df, rows, "ffr")
    rates = {(v, h): rate_response(df, rows, v, h) for v in ("ffr", "y2_mean") for h in (0, 1)}
    bref = beta_ref(pi_ffr)
    g_real = 100 * np.log(df["inv_nonres_q"]).diff()
    (mu, p1, p2), resid = ar2(g_real, rows)
    eps_s = df["mps_bs23_orth"].loc[rows]
    L = [f"# F4 · tablas del Monte Carlo de `s1_liq` (generado por `code/mc/f4_power.py`, semilla {SEED}, {REPS} réplicas)\n",
         "## Calibración",
         f"- N = {N}; k = 16 regresores; N−k = {N - 16}. Desv. típica de ε en la muestra = {eps_s.std():.4f}; autocorrelación(1) = {eps_s.autocorr():.3f}.",
         f"- AR(2) de 100·Δlog `inv_nonres_q` en las {N} filas (sin choques): μ = {mu:.3f}, φ1 = {p1:.3f}, φ2 = {p2:.3f}, σ_e = {resid.std(ddof=3):.3f}; κ = {kappa(p1, p2):.3f}.",
         "- Respuesta de los tipos a ε (MCO, ee White ×N/(N−k)), `var_{t+h} − var_{t−1}`:"]
    L += [f"  - {v}, h={h}: {b:.3f} (ee {s:.3f})" for (v, h), (b, s) in rates.items()]
    L += [(f"- **β_ref = {TT_PEAK} × media(h=0..4)/{PEAK_H} × π_ffr = {bref:.3f}** pp de ȳ por 1 pp de ε "
           f"(π_ffr = {pi_ffr:.3f}). Sensibilidad: pico en h=8 → {beta_ref(pi_ffr, 8):.3f}; h=12 → {beta_ref(pi_ffr, 12):.3f}; "
           f"π_ffr ± 1,645 ee → [{beta_ref(pi_ffr + 1.645 * pi_se):.3f}, {beta_ref(pi_ffr - 1.645 * pi_se):.3f}]."),
          f"- Efecto en ȳ de un choque de 1 desv. típica con β_ref: {bref * eps_s.std():.4f} pp.\n"]

    # 1. Escenarios prerregistrados (+ β_C = 0, el rival TFG1 / límite rígido), con T y T/2
    L.append("## 1. Escenarios: β_U = β_ref, β_C = m·β_ref (subidas y bajadas a la vez)\n")
    scen = [1.0, 0.5, 0.146, 0.0]
    results = {}
    for i, m in enumerate(scen):
        betas = scenario_betas(bref, m)
        dgp = DGP(df, rows, betas)
        for T in (N, N // 2):
            results[(m, T)] = simulate(dgp, betas, T, REPS, SEED + 10 * i + (T != N))
    L.append("### 1a. Sesgo, RMSE y cobertura del IC al 95 % (t con N−k g.l.), ee prerregistrado y alternativas\n")
    L.append("«error de diseño» = β̂ − β sin ruido con T = N (respuesta a choques futuros reales; ver `design_error`).\n")
    L.append("| m | T | ee | término | verdadero | sesgo | error de diseño | RMSE | desv. típ. β̂ | ee medio | cobertura |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for (m, T), res in results.items():
        betas = scenario_betas(bref, m)
        derr = design_error(df, rows, betas)
        for k, r in res.items():
            for j, t in enumerate(s1_lp.TERMS):
                de = f"{derr[j]:+.3f}" if T == N else "—"
                L.append(f"| {m} | {T} | {k} | {t} | {betas[t]:.3f} | {r['bias'][j]:+.3f} | {de} | {r['rmse'][j]:.3f} | "
                         f"{r['sd'][j]:.3f} | {r['se_mean'][j]:.3f} | {r['cover'][j]:.3f} |")
    L.append("\n### 1b. Probabilidad de cada veredicto (reglas de la SPEC; Holm unilateral; δ = 0,146·|β̂_U|)\n")
    L.append("| m | T | ee | sentido | " + " | ".join(VERDICTS) + " | confirma y (b) a la vez |")
    L.append("|---|---|---|---|" + "---|" * (len(VERDICTS) + 1))
    for (m, T), res in results.items():
        for k, r in res.items():
            for d in ("pos", "neg"):
                v = r["verdicts"][d]
                L.append(f"| {m} | {T} | {k} | {'subida' if d == 'pos' else 'bajada'} | "
                         + " | ".join(f"{v.get(x, 0.0):.3f}" for x in VERDICTS) + f" | {r['overlap']:.3f} |")

    # 2. Curva de potencia: β_U = β_C = c·β_ref; c mínimo con P(confirma) ≥ 0,8
    L.append("\n## 2. Potencia de «confirma» (T = N) con β_U = β_C = c·β_ref\n")
    L.append("| c | β_C | ee | P(confirma) subida | P(confirma) bajada | P(refuta) subida | P(refuta) bajada |")
    L.append("|---|---|---|---|---|---|---|")
    for i, c in enumerate([1, 2, 5, 10, 15, 20, 30, 40]):
        betas = scenario_betas(c * bref, 1.0)
        res = simulate(DGP(df, rows, betas), betas, N, REPS // 2, SEED + 1000 + i, kinds=(MAIN_SE, RECOMMENDED_SE))
        for k, rk in res.items():
            r = rk["verdicts"]
            conf = [r[d].get("confirma", 0.0) for d in ("pos", "neg")]
            ref = [r[d].get("refuta_a", 0.0) + r[d].get("refuta_b", 0.0) for d in ("pos", "neg")]
            L.append(f"| {c} | {c * bref:.2f} | {k} | {conf[0]:.3f} | {conf[1]:.3f} | {ref[0]:.3f} | {ref[1]:.3f} |")

    # 3. Sensibilidad del ruido: σ_e del AR(2) con los 4 controles adicionales (menos ruido)
    Z = pd.concat([s1_lp.controls(df).shift(lag).add_suffix(f"_l{lag}") for lag in (1, 2)], axis=1).loc[rows]
    Z.insert(0, "const", 1.0)
    yz = g_real.loc[rows].to_numpy()
    rz = yz - Z.to_numpy() @ np.linalg.lstsq(Z.to_numpy(), yz, rcond=None)[0]
    scale = rz.std(ddof=Z.shape[1]) / resid.std(ddof=3)
    betas = scenario_betas(bref, 1.0)
    res = simulate(DGP(df, rows, betas, sigma_scale=scale), betas, N, REPS, SEED + 2000, kinds=(MAIN_SE, RECOMMENDED_SE))
    L.append(f"\n## 3. Sensibilidad: ruido con σ_e condicionado a los 10 controles (×{scale:.3f}), m = 1, T = N\n")
    L.append("| ee | sentido | " + " | ".join(VERDICTS) + " | cobertura (b_pos_C, b_pos_U, b_neg_C, b_neg_U) |")
    L.append("|---|---|" + "---|" * (len(VERDICTS) + 1))
    for k, r in res.items():
        for d in ("pos", "neg"):
            L.append(f"| {k} | {d} | " + " | ".join(f"{r['verdicts'][d].get(x, 0.0):.3f}" for x in VERDICTS)
                     + " | " + ", ".join(f"{c:.3f}" for c in r["cover"]) + " |")

    # 4. Tabla estándar de tools/mc.py (z normal, T y T/2), escenario m = 1, por tipo de ee
    std_rows = []
    betas = scenario_betas(bref, 1.0)
    for k in SE_KINDS:
        try:
            res = mc.validate(DGP(df, rows, betas), mc_estimator(k), betas, T=N, reps=REPS, seed=SEED + 3000)
            status = "dentro de [0,92; 0,98]"
        except mc.CoverageOutOfBand:
            res = mc.run(DGP(df, rows, betas), mc_estimator(k), betas, N, REPS, SEED + 3000) + \
                mc.run(DGP(df, rows, betas), mc_estimator(k), betas, N // 2, REPS, SEED + 3001)
            status = "**CoverageOutOfBand** con T"
        std_rows.append(f"[{k}] {status}")
        std_rows += [x.row() for x in res]
    (PAPER / "output" / "tables").mkdir(parents=True, exist_ok=True)
    (PAPER / "output" / "tables" / "mc_s1_liq.txt").write_text("\n".join(std_rows) + "\n", encoding="utf-8")
    L.append("\n## 4. Tabla estándar de `tools/mc.py` (IC con z normal; potencia bilateral), m = 1\n")
    L.append("```\n" + "\n".join(std_rows) + "\n```")
    (PAPER / "output" / "tables" / "f4_power.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito {PAPER / 'output' / 'tables' / 'f4_power.md'}")


if __name__ == "__main__":
    main()
