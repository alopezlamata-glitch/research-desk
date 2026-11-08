"""F9 · Monte Carlo de la etapa 1 rediseñada `s1r_*` (encargo desks/econometria/ENCARGO_2026-11-07_f9-mc-s1r.md).

Regla dura: no se estima nada con la inversión real ni se mira cómo responde a los choques. De la inversión real solo entra un AR(2)
univariante de su crecimiento, sin choques, para fijar el ruido (como en F4). Del panel se usan los choques, el estado, los demás
controles y la muestra. La primera etapa usa el fed funds.

DGP (calendario 1960Q1–2008Q4, con 40 trimestres de burn-in):
    100·log I_t = L_t + Σ_{j≥0} r_j a_{t−j},   r_j = min(j, 10)/10: rampa de Tenreyro-Thwaites hasta el pico en h = 10, luego plana
    a_s = (β_C D_{s−1} + β_U (1 − D_{s−1})) ε_s / m_W,   m_W = media de r_h en la ventana  →  β es el coeficiente de ȳ en la población
    ΔL_t = μ + φ1 ΔL_{t−1} + φ2 ΔL_{t−2} + σ_t e_t,   e_t remuestreo iid de los residuos centrados del AR(2) univariante de
    100·Δlog inversión no residencial real en la muestra de cada choque.
    σ_t (varianza media 1 en la muestra):
      'homo'    = 1;
      'het_eps' ∝ √(1 + media_{k=0..12} (ε_{t−k}/sd ε)²). El error de ȳ_t contiene e_t..e_{t+12}, así que la varianza del error de la
                fila t crece con su choque: las filas de alto apalancamiento son las más ruidosas. Generaliza la prueba de R-F4
                (1 + (ε_t/sd)²) a la ventana de 12 trimestres.
      'het_rec' = √ρ en trimestres con Δlog PIB real < 0 y 1 en el resto, con ρ = cociente de varianzas de los residuos del AR(2)
                univariante de la inversión en esos trimestres frente al resto (no usa choques).
    ε, D_{t−1} y los controles distintos de la inversión son reales y fijos. ȳ y el control Δlog inversión salen de la simulada.
    El estado se fija con la mediana de la muestra completa de cada choque, también sin Volcker y con T/2 (SPEC, Desviación 2026-11-07).

Especificaciones: 'base' (controles) y 'aum' (además ε_{t−1..t−10} y ε_{t+1..t+12}; ver s1r_lp). La réplica BS (N = 70) solo con 'base'.

Uso: uv run python papers/p01-liquidity/code/mc/f9_power.py   (escribe output/tables/f9_power.md y mc_s1r.txt; ≈ 1,5 h)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lfilter

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER / "code" / "data"), str(PAPER / "code" / "analysis"), str(PAPER / "code" / "mc"),
                str(PAPER.parents[1] / "tools")]
import build_stage1_us
import mc
import s1_lp
import s1r_lp
import sample_counts_s1r
from f4_power import ar2

SEED = 20261107
REPS = 1000
TT_PEAK, PEAK_H = -2.5, 10  # β_ref como en F4: −2,5 % en el pico por 1 pp de fed funds (TT pp. 11–12), pico en h = 10
VOLCKER = pd.period_range(*sample_counts_s1r.VOLCKER, freq="Q")
SPECS = {"base": (0, 0), "aum": (PEAK_H, max(s1r_lp.HORIZONS))}  # (retardos, adelantos) del choque como controles
SE_KINDS = {"NW5 (prerreg.)": (5, False), "NW5+HC3": (5, True), "HC3": (0, True), "NW12+HC3": (12, True)}
TESTED_SE = "NW5+HC3"  # la Desviación de F4 que hay que validar; F9 la recomienda con la especificación 'aum'
NOISES = ("homo", "het_eps", "het_rec")
VARIANTS = ("V1", "V2", "V3s", "V3l")
OUTCOMES = ["h0_falla", "confirma", "refuta_a", "refuta_b", "no_concluyente"]
COL = {"b_lin": (0, 1, 6), "b_C": (2, 3, 7), "b_U": (4, 5, 7)}  # columnas (estimación, ee, g.l.) de las salidas de simulate
Z80 = stats.norm.ppf(0.95) + stats.norm.ppf(0.8)  # MDE = Z80 · ee (unilateral, α = 0,05, potencia 0,8)
OMEGA = s1r_lp.OMEGA_MIN
TABLES = PAPER / "output" / "tables"


def ramp(n: int) -> np.ndarray:
    return np.minimum(np.arange(n), PEAK_H) / PEAK_H


def signal_share(horizons: range) -> float:
    """m_W: media de la rampa en la ventana (fracción del pico que recoge ȳ)."""
    return float(ramp(max(horizons) + 1)[list(horizons)].mean())


def panel() -> pd.DataFrame:
    df = sample_counts_s1r.panel()
    for col, name in (("inv", "A008RA3Q086SBEA"), ("gdp", "GDPC1"), ("defl", "GDPDEF")):
        s = build_stage1_us.fred(name)
        s.index = s.index.to_period("Q")
        df[col] = s.reindex(df.index)
    return df


def samples(df: pd.DataFrame) -> dict[str, pd.Index]:
    s = sample_counts_s1r.samples(df)
    full = s["rr_shock"][0].index
    return {"RR": full, "RR_noV": full[~full.isin(VOLCKER)], "BS": s["mps_bs23_orth"][0].index}


def rate_response(df: pd.DataFrame, rows: pd.Index, shock: str, h: int = 0) -> tuple[float, float]:
    """Primera etapa: MCO de ffr_{t+h} − ffr_{t−1} sobre (1, ε_t), ee de White ×N/(N−k). No usa la inversión."""
    y = (df["ffr"].shift(-h) - df["ffr"].shift(1)).loc[rows].to_numpy()
    X = np.column_stack([np.ones(len(rows)), df[shock].loc[rows]])
    b, se, _ = s1_lp.fit(y, X, np.eye(len(rows)), small_sample=True)
    return float(b[1]), float(se[1])


def beta_ref(pi_ffr: float, horizons: range = s1r_lp.HORIZONS) -> float:
    """β_ref en pp de ȳ por 1 pp de ε."""
    return TT_PEAK * signal_share(horizons) * pi_ffr


class DGP:
    """Simula ȳ y el control Δlog inversión en el calendario; `samples` son las muestras de estimación (la primera es la base de los
    bloques de T/2 y la que fija estado y calibración)."""

    def __init__(self, df: pd.DataFrame, shock: str, samples: dict[str, pd.Index], beta_C: float, beta_U: float,
                 noise: str = "homo", horizons: range = s1r_lp.HORIZONS, sigma_scale: float = 1.0, burn: int = 40,
                 specs: tuple[str, ...] = ("base",)):
        self.df, self.samples, self.horizons, self.burn, self.specs = df, samples, horizons, burn, specs
        rows = next(iter(samples.values()))
        g_real = 100 * np.log(df["inv"]).diff()
        (self.mu, self.phi1, self.phi2), resid = ar2(g_real, rows)
        self.resid = resid - resid.mean()
        self.pool = sigma_scale * self.resid
        self.eps = df[shock]
        self.D = s1_lp.state(df["s_lag"], rows)
        a = (beta_C * self.D + beta_U * (1 - self.D)) * self.eps.fillna(0.0) / signal_share(horizons)
        self.signal = np.convolve(a.to_numpy(), ramp(len(df)))[:len(df)]
        self.rec = (100 * np.log(df["gdp"]).diff() < 0).to_numpy()
        self.sigma = self.noise_scale(noise, rows)
        self.ctrl = s1r_lp.controls(df)
        self.q = np.asarray(df.index.asi8)
        self.all_rows = rows
        for r in samples.values():
            self.all_rows = self.all_rows.union(r)

    def noise_scale(self, noise: str, rows: pd.Index) -> np.ndarray:
        in_rows = self.df.index.isin(rows)
        if noise == "homo":
            v = np.ones(len(self.df))
        elif noise == "het_eps":
            z = (self.eps.fillna(0.0) / self.eps.loc[rows].std()) ** 2
            v = 1 + z.rolling(13, min_periods=1).mean().to_numpy()
        elif noise == "het_rec":
            v = np.where(self.rec, self.rec_ratio(), 1.0)
        else:
            raise ValueError(noise)
        return np.sqrt(v / v[in_rows].mean())

    def rec_ratio(self) -> float:
        """ρ: varianza de los residuos del AR(2) de la inversión en trimestres con Δlog PIB < 0 frente al resto (sin choques).
        Se calibra siempre en 1969Q1–2005Q2 (18 trimestres así): la muestra de BS solo tiene 4."""
        rr_rows = self.df.index[self.df["in_rr_sample"].astype(bool)]
        _, res = ar2(100 * np.log(self.df["inv"]).diff(), rr_rows)
        r = self.rec[self.df.index.get_indexer(rr_rows)]
        return float(res[r].var() / res[~r].var())

    def draw(self, rng: np.random.Generator) -> tuple[pd.Series, dict[tuple[str, str], pd.DataFrame]]:
        """Una réplica: ȳ y las matrices de regresores de cada (especificación, modelo) en todas las filas de las muestras."""
        n = len(self.df)
        e = np.r_[rng.choice(self.pool, self.burn), self.sigma * rng.choice(self.pool, n)]
        g = lfilter([1.0], [1.0, -self.phi1, -self.phi2], self.mu + e)[self.burn:]
        level = pd.Series(np.cumsum(g) + self.signal, index=self.df.index)
        ctrl = self.ctrl.assign(dlinv=level.diff())
        X = {(sp, m): s1r_lp.design(self.eps, self.D, ctrl, self.all_rows, m, *SPECS[sp])
             for sp in self.specs for m in ("lin", "liq")}
        return s1r_lp.ybar(level / 100, self.horizons), X

    def block(self, rng: np.random.Generator, T: int) -> dict[str, pd.Index]:
        """Con T < N, bloque contiguo de T filas de la muestra base; las demás muestras se recortan a ese bloque."""
        base = next(iter(self.samples.values()))
        if T >= len(base):
            return self.samples
        start = int(rng.integers(0, len(base) - T + 1))
        blk = base[start:start + T]
        return {name: r[r.isin(blk)] for name, r in self.samples.items()}

    def data(self, y: pd.Series, X: dict, rows: pd.Index, spec: str) -> dict:
        return {"y": y.loc[rows].to_numpy(), "q": self.q[self.df.index.get_indexer(rows)],
                "lin": X[(spec, "lin")].loc[rows], "liq": X[(spec, "liq")].loc[rows]}

    def for_sample(self, name: str, spec: str):
        """Adaptador `dgp(T, rng)` de tools/mc.py para una muestra (con T < N, bloque contiguo de esa muestra)."""
        def f(T: int, rng: np.random.Generator) -> dict:
            y, X = self.draw(rng)
            rows = self.samples[name]
            if T < len(rows):
                start = int(rng.integers(0, len(rows) - T + 1))
                rows = rows[start:start + T]
            return self.data(y, X, rows, spec)
        return f


def estimate(data: dict, model: str, kind: str) -> tuple[np.ndarray, np.ndarray, int]:
    X = data[model]
    lags, lev = SE_KINDS[kind]
    b, se, dof = s1_lp.fit(data["y"], X.to_numpy(), s1_lp.hac_weights(data["q"], lags), False, lev)
    idx = [X.columns.get_loc(t) for t in s1r_lp.TERMS[model]]
    return b[idx], se[idx], dof


def mc_estimator(kind: str):
    """Adaptador para tools/mc.py: (β̂, ee) de (b_lin, b_C, b_U)."""
    def f(data: dict):
        bl, sl, _ = estimate(data, "lin", kind)
        bq, sq, _ = estimate(data, "liq", kind)
        return np.r_[bl, bq], np.r_[sl, sq]
    return f


def simulate(dgp: DGP, T: int, reps: int, seed: int, kinds=tuple(SE_KINDS)) -> dict:
    """R[spec][muestra][ee]: matriz reps × 8 (b_lin, ee, b_C, ee, b_U, ee, g.l. lin, g.l. liq). Todas las muestras de una réplica
    usan la misma ȳ, para que V3 combine la muestra completa y la de sin Volcker de los mismos datos."""
    rng = np.random.default_rng(seed)
    out = {sp: {s: {k: np.empty((reps, 8)) for k in kinds} for s in dgp.samples} for sp in dgp.specs}
    for r in range(reps):
        y, X = dgp.draw(rng)
        for s, rows in dgp.block(rng, T).items():
            for sp in dgp.specs:
                d = dgp.data(y, X, rows, sp)
                for k in kinds:
                    bl, sl, dl = estimate(d, "lin", k)
                    bq, sq, dq = estimate(d, "liq", k)
                    out[sp][s][k][r] = [bl[0], sl[0], bq[0], sq[0], bq[1], sq[1], dl, dq]
    return out


def term_stats(A: np.ndarray, term: str, truth: float) -> dict[str, float]:
    i, j, d = COL[term]
    err = A[:, i] - truth
    return {"bias": err.mean(), "sd": A[:, i].std(), "se_mean": A[:, j].mean(),
            "cover": float((np.abs(err) <= stats.t.ppf(0.975, A[:, d]) * A[:, j]).mean())}


def delta(rule: str, A: np.ndarray, bref: float) -> np.ndarray:
    """Umbral de la regla (b): 'spec' = 0,146·|β̂_U| (SPEC vigente); 'fijo' = 0,146·|β_ref|, fijado ex ante."""
    return OMEGA * (np.abs(A[:, 4]) if rule == "spec" else np.full(len(A), abs(bref)))


def branches(A: np.ndarray, rule: str, bref: float) -> tuple[np.ndarray, np.ndarray]:
    """(H0 confirma, veredicto de H1) por réplica, con las funciones del análisis (s1r_lp)."""
    dl = delta(rule, A, bref)
    h0 = np.array([s1r_lp.h0_confirms(a[0], a[1], int(a[6])) for a in A])
    h1 = np.array([s1r_lp.h1_verdict(a[2], a[3], int(a[7]), d) for a, d in zip(A, dl, strict=True)])
    return h0, h1


def verdict_probs(R: dict, kind: str, rule: str, bref: float, main: str, nov: str | None) -> dict[str, pd.Series]:
    """Probabilidad de cada desenlace del árbol completo, por variante de Volcker (`R` de una especificación)."""
    h0f, h1f = branches(R[main][kind], rule, bref)
    if nov is None:
        return {"V1": pd.Series([s1r_lp.decide("V1", a, b) for a, b in zip(h0f, h1f, strict=True)]).value_counts(normalize=True)}
    h0n, h1n = branches(R[nov][kind], rule, bref)
    bcn = R[nov][kind][:, 2]
    return {v: pd.Series([s1r_lp.decide(v, h0f[r], h1f[r], h0n[r], h1n[r], bcn[r]) for r in range(len(h0f))])
            .value_counts(normalize=True) for v in VARIANTS}


def design_error(df: pd.DataFrame, shock: str, smp: dict, beta_C: float, beta_U: float, specs: tuple[str, ...]) -> dict:
    """β̂ − β sin ruido con T = N: lo que dejan en ȳ_t las respuestas a los demás choques reales (no se promedia entre réplicas
    porque los choques son fijos). err[spec][muestra][término]."""
    dgp = DGP(df, shock, smp, beta_C, beta_U, sigma_scale=0.0, specs=specs)
    y, X = dgp.draw(np.random.default_rng(0))
    out = {}
    for sp in specs:
        out[sp] = {}
        for s, rows in smp.items():
            d = dgp.data(y, X, rows, sp)
            bl, _, _ = estimate(d, "lin", TESTED_SE)
            bq, _, _ = estimate(d, "liq", TESTED_SE)
            out[sp][s] = {"b_lin": bl[0] - beta_U if beta_C == beta_U else np.nan, "b_C": bq[0] - beta_C, "b_U": bq[1] - beta_U}
    return out


def c80(cs: list[float], p: list[float]) -> str:
    """c con potencia 0,8, interpolado linealmente en la rejilla."""
    for c0, p0, c1, p1 in zip(cs, p, cs[1:], p[1:], strict=False):
        if p0 < 0.8 <= p1:
            return f"{c0 + (0.8 - p0) / (p1 - p0) * (c1 - c0):.1f}"
    return f"> {cs[-1]}" if p[-1] < 0.8 else f"≤ {cs[0]}"


def fmt_probs(v: pd.Series) -> str:
    return " | ".join(f"{v.get(x, 0.0):.3f}" for x in OUTCOMES)


def main() -> None:
    df = panel()
    smp = samples(df)
    designs = {"RR": ("rr_shock", {k: smp[k] for k in ("RR", "RR_noV")}, ("base", "aum")),
               "BS": ("mps_bs23_orth", {"BS": smp["BS"]}, ("base",))}
    pis = {(name, s, h): rate_response(df, smp[s], shock, h)
           for name, (shock, _, _) in designs.items() for s in ([name, "RR_noV"] if name == "RR" else [name]) for h in (0, 1)}
    bref = {name: beta_ref(pis[(name, name, 0)][0]) for name in designs}
    m_w = signal_share(s1r_lp.HORIZONS)
    L = [f"# F9 · tablas del Monte Carlo de `s1r_*` (generado por `code/mc/f9_power.py`, semilla {SEED}, {REPS} réplicas)\n",
         "## 0. Calibración (sin la respuesta de la inversión)\n"]
    for name, (shock, s, _) in designs.items():
        base = next(iter(s.values()))
        dgp = DGP(df, shock, s, bref[name], bref[name])
        eps = df[shock].loc[base]
        L.append(f"### {name} (`{shock}`), {base[0]}–{base[-1]}")
        for sn, rows in s.items():
            Dr, er = dgp.D.loc[rows], df[shock].loc[rows]
            e2 = [(er[Dr == st] ** 2).sort_values(ascending=False) for st in (1, 0)]
            L.append(f"- {sn}: N = {len(rows)}; restringido (D = 1) {int(Dr.sum())}, holgado {int((1 - Dr).sum())}; sd(ε) = {er.std():.3f}; "
                     f"autocorrelación de ε (1, 2, 4): {er.autocorr(1):.2f}, {er.autocorr(2):.2f}, {er.autocorr(4):.2f}; "
                     f"% de Σε² en los 4 mayores: restringido {e2[0].iloc[:4].sum() / e2[0].sum():.0%}, "
                     f"holgado {e2[1].iloc[:4].sum() / e2[1].sum():.0%}; Σε² restringido / total = {e2[0].sum() / (er ** 2).sum():.2f}.")
        L.append(f"- AR(2) de 100·Δlog `A008RA3Q086SBEA` en las {len(base)} filas (sin choques): μ = {dgp.mu:.3f}, φ1 = {dgp.phi1:.3f}, "
                 f"φ2 = {dgp.phi2:.3f}, σ_e = {dgp.resid.std(ddof=3):.3f}; ρ (het_rec, calibrado en 1969Q1–2005Q2) = "
                 f"{dgp.rec_ratio():.2f}; {int(dgp.rec[df.index.get_indexer(base)].sum())} trimestres con Δlog PIB < 0 en esta muestra.")
        sig_e = DGP(df, shock, s, 0, 0, "het_eps").sigma[df.index.get_indexer(base)]
        L.append(f"- het_eps: σ_t en la muestra entre {sig_e.min():.2f} y {sig_e.max():.2f} (media de σ_t² = 1).")
        for (n_, sn, h), (b, se) in pis.items():
            if n_ == name:
                L.append(f"- Primera etapa ffr_(t+{h}) − ffr_(t−1) sobre ε, {sn}: π = {b:.3f} (ee {se:.3f}) → β_ref = {beta_ref(b):.3f}")
        L.append(f"- **β_ref = {TT_PEAK} × m_W × π(h=0) = {TT_PEAK} × {m_w:.4f} × {pis[(name, name, 0)][0]:.3f} = {bref[name]:.3f}** "
                 f"pp de ȳ por 1 pp de ε (m_W = media de min(h/{PEAK_H}, 1) en h = 4..12). Efecto de 1 sd de ε: {bref[name] * eps.std():.3f} pp.\n")

    # 1. Error de diseño, sesgo y cobertura
    L.append("## 1. Error de diseño, sesgo y cobertura del IC al 95 % (t con N−k g.l.)\n")
    L.append("### 1a. Error de diseño relativo: (β̂ − β)/β sin ruido, T = N, β_C = β_U (es lineal en β)\n")
    L.append("| choque | especificación | muestra | b_lin | b_C | b_U |")
    L.append("|---|---|---|---|---|---|")
    derr = {}
    for name, (shock, s, specs) in designs.items():
        derr[name] = {m: design_error(df, shock, s, m * bref[name], bref[name], specs) for m in (1, 0)}
        for sp in specs:
            for sn in s:
                e = derr[name][1][sp][sn]
                L.append(f"| {name} | {sp} | {sn} | " + " | ".join(f"{e[t] / bref[name]:+.2f}" for t in ("b_lin", "b_C", "b_U")) + " |")
    cover = {}
    for name, (shock, s, specs) in designs.items():
        N = len(next(iter(s.values())))
        for i, noise in enumerate(NOISES):
            for m in (1, 0):
                dgp = DGP(df, shock, s, m * bref[name], bref[name], noise, specs=specs)
                for T in (N, N // 2):
                    R = simulate(dgp, T, REPS, SEED + 100 * i + 10 * m + (T != N) + (name == "BS") * 5000)
                    truth = {"b_C": m * bref[name], "b_U": bref[name]} | ({"b_lin": bref[name]} if m == 1 else {})
                    for sp in specs:
                        for sn in s:
                            for k in SE_KINDS:
                                A = R[sp][sn][k]
                                cover[(sp, sn, noise, m, T == N, k)] = {
                                    "terms": {t: term_stats(A, t, v) for t, v in truth.items()},
                                    "pseudo": {t: term_stats(A, t, v + derr[name][m][sp][sn][t])["cover"] for t, v in truth.items()},
                                    "T": int(np.median(A[:, 7])) + 12 + sum(SPECS[sp])}
    L.append("\n### 1b. Resumen: cobertura mínima–máxima sobre términos (b_lin, b_C, b_U) y escenarios (m = β_C/β_ref ∈ {1, 0})\n")
    L.append("Centrada en el β verdadero (lo que decide la regla de parada). Entre paréntesis, solo los términos que deciden (b_lin, b_C). "
             "✗ = fuera de [0,92; 0,98]. T/2 sin Volcker: mediana de filas del bloque.\n")
    L.append("| espec. | muestra | ruido | T | " + " | ".join(SE_KINDS) + " |")
    L.append("|---|---|---|---|" + "---|" * len(SE_KINDS))
    for (sp, sn, noise, m, full, k) in cover:
        if m != 1 or k != TESTED_SE:
            continue
        cells = []
        for kk in SE_KINDS:
            res = [cover[(sp, sn, noise, mm, full, kk)]["terms"] for mm in (1, 0)]
            allc = [st["cover"] for r in res for st in r.values()]
            dec = [st["cover"] for r in res for t, st in r.items() if t != "b_U"]
            flag = "" if 0.92 <= min(allc) and max(allc) <= 0.98 else " ✗"
            cells.append(f"{min(allc):.3f}–{max(allc):.3f}{flag} ({min(dec):.3f}–{max(dec):.3f})")
        L.append(f"| {sp} | {sn} | {noise} | {'T' if full else 'T/2'} = {cover[(sp, sn, noise, 1, full, k)]['T']} | " + " | ".join(cells) + " |")
    L.append("\n### 1c. Detalle (cobertura «pseudo» = centrada en β + error de diseño: mide solo el error estándar)\n")
    L.append("| espec. | muestra | ruido | m | T | ee | término | verdadero | sesgo | error de diseño | desv. típ. β̂ | ee medio | cobertura | cobertura pseudo |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (sp, sn, noise, m, full, k), res in cover.items():
        name = sn[:2]
        for t, st in res["terms"].items():
            true = m * bref[name] if t == "b_C" else bref[name]
            de = derr[name][m][sp][sn][t]
            L.append(f"| {sp} | {sn} | {noise} | {m} | {'T' if full else 'T/2'} | {k} | {t} | {true:.3f} | {st['bias']:+.3f} | {de:+.3f} | "
                     f"{st['sd']:.3f} | {st['se_mean']:.3f} | {st['cover']:.3f} | {res['pseudo'][t]:.3f} |")

    # 2–4. Potencia, MDE, veredictos y regla (b): β_C = m·c·β_ref, β_U = c·β_ref, T = N
    CS = [0, 1, 2, 3, 5, 7, 10]
    kinds = (TESTED_SE,)
    power, verd = {}, {}
    for name, (shock, s, specs) in designs.items():
        N = len(next(iter(s.values())))
        for i, noise in enumerate(("homo", "het_eps")):
            for m in (1, 0):
                for j, c in enumerate(CS):
                    if c == 0 and m == 0:
                        continue
                    dgp = DGP(df, shock, s, m * c * bref[name], c * bref[name], noise, specs=specs)
                    R = simulate(dgp, N, REPS, SEED + 10_000 + 1000 * i + 100 * m + j + (name == "BS") * 50_000, kinds)
                    for sp in specs:
                        for k in kinds:
                            for sn in s:
                                A = R[sp][sn][k]
                                power[(sp, sn, noise, m, c, k)] = {
                                    "H0": float((stats.t.cdf(A[:, 0] / A[:, 1], A[:, 6]) < 0.05).mean()),
                                    "H1": float((stats.t.cdf(A[:, 2] / A[:, 3], A[:, 7]) < 0.05).mean()),
                                    "E_delta": float(OMEGA * np.abs(A[:, 4]).mean()), "sd_U": float(A[:, 4].std()),
                                    "sd_lin": float(A[:, 0].std()), "sd_C": float(A[:, 2].std())}
                            nov = "RR_noV" if name == "RR" else None
                            for rule in ("spec", "fijo"):
                                verd[(sp, name, noise, m, c, k, rule)] = verdict_probs(R[sp], k, rule, bref[name], name, nov)

    L.append("\n## 2. Potencia (T = N, sin condicionar) y efecto mínimo detectable\n")
    L.append(f"β_U = β_C = c·β_ref, ee {TESTED_SE}. H0: β_lin < 0, p unilateral < 0,05. H1: β_C < 0, p unilateral < 0,05 (una sola "
             "hipótesis: sin Holm). Con la especificación 'base' la potencia incluye el error de diseño (sesgo condicional a los choques reales).\n")
    L.append("| espec. | muestra | ruido | contraste | " + " | ".join(f"c = {c}" for c in CS) + " | c con potencia 0,8 | MDE (pp de ȳ por pp de ε) |")
    L.append("|---|---|---|---|" + "---|" * (len(CS) + 2))
    for (sp, sn, noise, m, c, k) in power:
        if m != 1 or c != 1:
            continue
        for h in ("H0", "H1"):
            p = [power[(sp, sn, noise, 1, cc, k)][h] for cc in CS]
            c8 = c80(CS[1:], p[1:])
            mde = f"{float(c8) * abs(bref[sn[:2]]):.2f}" if c8[0].isdigit() else "—"
            L.append(f"| {sp} | {sn} | {noise} | {h} | " + " | ".join(f"{x:.3f}" for x in p) + f" | {c8} | {mde} |")
    L.append("\nc = 1 equivale a 2,5 × m_W = " f"{2.5 * m_w:.2f} pp de ȳ por pp de fed funds (media de h = 4..12); el MDE en pp de ȳ por pp de fed "
             "funds es c × " f"{2.5 * m_w:.2f}.\n")

    L.append("## 3. Probabilidad de cada desenlace con el árbol completo (incluida la condición de H0), T = N\n")
    L.append(f"ee {TESTED_SE}. `h0_falla` = H0 no se confirma: H1 no se interpreta y se escala. `refuta_b` antes de la cláusula de "
             "potencia (con potencia < 0,8 frente a β_ref la SPEC la convierte en «no concluyente por potencia»). Regla (b) de la SPEC: "
             "δ = 0,146·|β̂_U|. V3s: H1 confirmada solo si también se confirma sin Volcker; V3l: si sin Volcker β̂_C < 0. "
             "m = β_C/(c·β_ref) con β_U = c·β_ref (m = 0: β_C = 0, el rival).\n")
    L.append("| espec. | choque | ruido | m | c | variante | " + " | ".join(OUTCOMES) + " |")
    L.append("|---|---|---|---|---|---|" + "---|" * len(OUTCOMES))
    for (sp, name, noise, m, c, k, rule), vp in verd.items():
        if rule == "spec" and c in (0, 1, 2, 3, 5):
            for v, probs in vp.items():
                L.append(f"| {sp} | {name} | {noise} | {m} | {c} | {v} | {fmt_probs(probs)} |")

    L.append("\n### 3b. P(confirma) del árbol completo frente a c (β_C = β_U = c·β_ref) y c con P(confirma) = 0,8\n")
    L.append("| espec. | choque | ruido | variante | " + " | ".join(f"c = {c}" for c in CS) + " | c con 0,8 |")
    L.append("|---|---|---|---|" + "---|" * (len(CS) + 1))
    for (sp, name, noise, m, c, k, rule), vp in verd.items():
        if rule != "spec" or m != 1 or c != 1:
            continue
        for v in vp:
            p = [verd[(sp, name, noise, 1, cc, k, "spec")][v].get("confirma", 0.0) for cc in CS]
            L.append(f"| {sp} | {name} | {noise} | {v} | " + " | ".join(f"{x:.3f}" for x in p) + f" | {c80(CS[1:], p[1:])} |")

    L.append("\n## 4. Regla (b): umbral de la SPEC (δ = 0,146·|β̂_U|) frente a un umbral fijo ex ante (δ = 0,146·|β_ref|)\n")
    L.append("δ verdadero = 0,146·|β_U| = 0,146·c·|β_ref|. P(refuta_b) del árbol completo antes de la cláusula de potencia; con m = 1 "
             "H1 es cierta (refutar es un error); con m = 0, β_C = 0 (refutar es correcto). Homo.\n")
    L.append("| espec. | choque | m | c | variante | desv. típ. β̂_U | δ verdadero | E[δ̂] (SPEC) | δ fijo | P(refuta_b) SPEC | P(refuta_b) fijo | P(refuta_a) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (sp, name, noise, m, c, k, rule), vp in verd.items():
        if rule != "spec" or noise != "homo" or c not in (1, 3, 5):
            continue
        for v in vp:
            pw = power[(sp, "RR_noV" if v == "V2" else name, noise, m, c, k)]
            fixed = verd[(sp, name, noise, m, c, k, "fijo")][v]
            L.append(f"| {sp} | {name} | {m} | {c} | {v} | {pw['sd_U']:.2f} | {OMEGA * c * abs(bref[name]):.3f} | {pw['E_delta']:.3f} | "
                     f"{OMEGA * abs(bref[name]):.3f} | {vp[v].get('refuta_b', 0.0):.3f} | {fixed.get('refuta_b', 0.0):.3f} | "
                     f"{vp[v].get('refuta_a', 0.0):.3f} |")

    # 5. Composición pérdida LP × ganancia de ventana (Director, [T§7])
    L.append("\n## 5. ¿Se componen la pérdida LP/oráculo y la ganancia de la ventana? (RR, muestra completa, homo, c = 1)\n")
    shock, s, _ = designs["RR"]
    base = s["RR"]
    sd = {}
    for w, hz in (("0..4", range(5)), ("4..12", s1r_lp.HORIZONS)):
        b_w = beta_ref(pis[("RR", "RR", 0)][0], hz)
        R = simulate(DGP(df, shock, {"RR": base}, b_w, b_w, horizons=hz, specs=("base",)), len(base), REPS, SEED + 90_000, kinds)
        A = R["base"]["RR"][TESTED_SE]
        sd[w] = {"bref": b_w, "lin": A[:, 0].std(), "C": A[:, 2].std()}
    dgp = DGP(df, shock, {"RR": base}, 0, 0)
    psi = lfilter([1.0], [1.0, -dgp.phi1, -dgp.phi2], np.r_[1.0, np.zeros(4)])
    eps = df[shock].loc[base]
    se_or = np.cumsum(psi).mean() * dgp.resid.std(ddof=3) / np.sqrt(((eps - eps.mean()) ** 2).sum())
    aum = {t: Z80 * power[("aum", "RR", "homo", 1, 1, TESTED_SE)][f"sd_{t}"] / abs(bref["RR"]) for t in ("lin", "C")}
    L.append(f"Oráculo del Director ([T§1, §5]): ee = κ_(0..4)·σ_e/√Σ(ε−ε̄)² = {se_or:.3f} (lineal) y ×√2 = {se_or * np.sqrt(2):.3f} "
             "(estado C: mitad de la muestra, independiente de ε). Predicción [T§7]: c_LP = c_oráculo(0..4) / 1,34 × (1,2 a 1,4). "
             f"MC: c = {Z80:.3f}·desv. típ.(β̂)/|β_ref| de cada ventana, especificación 'base' ({TESTED_SE}); la última columna, con 'aum' (§2).\n")
    L.append("| contraste | c oráculo (0..4) | c predicho (4..12) | c MC (0..4) | c MC (4..12) | pérdida LP/oráculo medida (0..4) | ganancia de ventana medida | c MC (4..12), 'aum' |")
    L.append("|---|---|---|---|---|---|---|---|")
    for term, f in (("lin", 1.0), ("C", np.sqrt(2))):
        c_or = Z80 * se_or * f / abs(sd["0..4"]["bref"])
        c04, c412 = (Z80 * sd[w][term] / abs(sd[w]["bref"]) for w in ("0..4", "4..12"))
        L.append(f"| {'H0 lineal' if term == 'lin' else 'H1, estado C'} | {c_or:.2f} | {c_or / 1.34 * 1.2:.2f}–{c_or / 1.34 * 1.4:.2f} | "
                 f"{c04:.2f} | {c412:.2f} | {c04 / c_or:.2f} | {c04 / c412:.2f} | {aum[term]:.2f} |")

    # 6. Tabla estándar de tools/mc.py (regla de parada), m = 1, c = 1
    std_rows = []
    for name, (shock, s, specs) in designs.items():
        for noise in NOISES:
            dgp = DGP(df, shock, s, bref[name], bref[name], noise, specs=specs)
            truth = {"b_lin": bref[name], "b_C": bref[name], "b_U": bref[name]}
            for sp in specs:
                for sn in s:
                    N = len(s[sn])
                    try:
                        res = mc.validate(dgp.for_sample(sn, sp), mc_estimator(TESTED_SE), truth, T=N, reps=REPS, seed=SEED + 70_000)
                        status = "dentro de [0,92; 0,98]"
                    except mc.CoverageOutOfBand:
                        res = mc.run(dgp.for_sample(sn, sp), mc_estimator(TESTED_SE), truth, N, REPS, SEED + 70_000) + \
                            mc.run(dgp.for_sample(sn, sp), mc_estimator(TESTED_SE), truth, N // 2, REPS, SEED + 70_001)
                        status = "**CoverageOutOfBand** con T"
                    std_rows.append(f"[{sp} · {sn} · {noise} · {TESTED_SE}] {status}")
                    std_rows += [x.row() for x in res]
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "mc_s1r.txt").write_text("\n".join(std_rows) + "\n", encoding="utf-8")
    L.append("\n## 6. Tabla estándar de `tools/mc.py` (`mc.validate`; IC con z normal; potencia bilateral), m = 1, c = 1\n")
    L.append("En `RR_noV` con T/2, `tools/mc.py` toma la mitad de las 133 filas (bloque contiguo que puede cruzar el hueco).\n")
    L.append("```\n" + "\n".join(std_rows) + "\n```")
    (TABLES / "f9_power.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito {TABLES / 'f9_power.md'}")


if __name__ == "__main__":
    main()
