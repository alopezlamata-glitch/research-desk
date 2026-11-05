"""R-F4 · Replicación independiente del Monte Carlo de F4 (Referee, 2026-11-05).

No importa código del autor (s1_lp, f4_power, sample_counts, tools/mc). Regla dura: la inversión real solo entra como serie
univariante (AR(2) del control Δlog inversión, sin choques) y como control retardado en el diagnóstico de apalancamiento;
no se estima ninguna regresión de la inversión sobre los choques. La variable dependiente se simula.

Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-05/rep_f4.py [reps]   → resultados en stdout
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
PAPER = Path(__file__).resolve().parents[2]
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEED = 5112026
OMEGA_MIN = 0.146
BURN = 40


# ---------- datos y muestra (reconstruida desde la SPEC, no desde sample_counts.py) ----------
def load():
    df = pd.read_parquet(PAPER / "data" / "clean" / "stage1_us.parquet").set_index("quarter")
    df.index = pd.PeriodIndex(df.index, freq="Q")
    ll = np.log(df["liq_broad_debt"])
    s = ll - sum(ll.shift(j) for j in range(1, 13)) / 12
    df["s_prev"] = s.shift(1)
    q = df.index
    keep = ((q >= pd.Period("1988Q2", "Q")) & (q <= pd.Period("2023Q4", "Q")) & (df["ffr"] >= 0.25)
            & ~((q >= pd.Period("2019Q1", "Q")) & (q <= pd.Period("2021Q4", "Q")))
            & df["mps_bs23_orth"].notna() & df["s_prev"].notna())
    pos = np.flatnonzero(keep.to_numpy())
    return df, pos


def ols(y, X):
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    return b, y - X @ b, XtXi


# ---------- estimador propio ----------
def sandwich(X, u, XtXi, qd, lags, hc3):
    if hc3:
        h = np.sum((X @ XtXi) * X, axis=1)
        u = u / (1 - h)
    W = np.maximum(0.0, 1 - np.abs(qd[:, None] - qd[None, :]) / (lags + 1)) if lags else np.eye(len(u))
    S = X * u[:, None]
    return np.sqrt(np.diag(XtXi @ S.T @ W @ S @ XtXi))


def verdict(bc, sc, bu, dof):
    """SPEC: Holm unilateral sobre {H1⁺, H1⁻}; (a) p unilateral contrario < 0,05; (b) IC90 ⊂ (−0,146|β̂_U|, ∞)."""
    p = stats.t.cdf(bc / sc, dof)
    o = np.argsort(p)
    padj = np.empty(2)
    padj[o[0]] = min(1, 2 * p[o[0]])
    padj[o[1]] = min(1, max(2 * p[o[0]], p[o[1]]))
    out = []
    for i in range(2):
        if padj[i] < 0.05:
            out.append(0)  # confirma
        elif stats.t.sf(bc[i] / sc[i], dof) < 0.05:
            out.append(1)  # refuta (a)
        elif bc[i] - stats.t.ppf(0.95, dof) * sc[i] > -OMEGA_MIN * abs(bu[i]):
            out.append(2)  # (b) antes de la cláusula de potencia
        else:
            out.append(3)
    return out


def main():
    df, pos = load()
    n = len(pos)
    eps_all = df["mps_bs23_orth"].to_numpy()
    eps = eps_all[pos]
    sp = df["s_prev"].to_numpy()
    D_all = (sp < np.median(sp[pos])).astype(float)  # NaN < x → False, irrelevante fuera de la muestra
    D = D_all[pos]
    cells = {(c, sg): int(((D == c) & (np.sign(eps) == sg)).sum()) for c in (1, 0) for sg in (1, -1)}
    print("N =", n, "celdas (C+, C−, U+, U−):", cells[(1, 1)], cells[(1, -1)], cells[(0, 1)], cells[(0, -1)],
          "ε=0:", int((eps == 0).sum()))

    # AR(2) univariante del control Δlog inversión (sin choques)
    g_real = 100 * np.diff(np.log(df["inv_nonres_q"].to_numpy()), prepend=np.nan)
    Z = np.column_stack([np.ones(n), g_real[pos - 1], g_real[pos - 2]])
    (mu, f1, f2), e_ar, _ = ols(g_real[pos], Z)
    psi = [1.0, f1]
    for _ in range(3):
        psi.append(f1 * psi[-1] + f2 * psi[-2])
    kap = np.mean(np.cumsum(psi))
    print(f"AR(2): mu={mu:.9f} phi1={f1:.9f} phi2={f2:.9f} sd(ddof=3)={e_ar.std(ddof=3):.9f} kappa={kap:.9f}")

    # π_ffr y β_ref
    ffr = df["ffr"].to_numpy()
    Xp = np.column_stack([np.ones(n), eps])
    bp, up, Ip = ols(ffr[pos] - ffr[pos - 1], Xp)
    sep = sandwich(Xp, up, Ip, None, 0, False)[1] * np.sqrt(n / (n - 2))
    ramp = np.mean(np.arange(5) / 10)
    bref = -2.5 * ramp * bp[1]
    print(f"pi_ffr={bp[1]:.9f} (ee HC1 {sep:.9f}); rampa media h0..4/pico={ramp}; beta_ref={bref:.9f}")
    print(f"sd(eps)={eps.std(ddof=1):.6f}; efecto 1 sd = {bref * eps.std(ddof=1):.6f} pp")

    # controles reales retardados (los 4 que no son la inversión)
    lgdp, ldef = np.log(df["gdp_real"].to_numpy()), np.log(df["gdp_deflator"].to_numpy())
    other = np.column_stack([100 * np.diff(lgdp, prepend=np.nan), 100 * np.diff(ldef, prepend=np.nan),
                             np.diff(df["y2_mean"].to_numpy(), prepend=np.nan), df["ebp"].to_numpy()])
    ep, en = np.maximum(eps, 0), np.minimum(eps, 0)
    Xcore = np.column_stack([np.ones(n), D, D * ep, (1 - D) * ep, D * en, (1 - D) * en])
    Xoth = np.column_stack([other[pos - 1], other[pos - 2]])
    qd = df.index.asi8[pos].astype(float)

    def X_of(g):
        return np.column_stack([Xcore, g[pos - 1], g[pos - 2], Xoth])

    # diagnóstico de apalancamiento con el diseño real (sin y)
    Xr = X_of(g_real)
    h = np.sum((Xr @ np.linalg.inv(Xr.T @ Xr)) * Xr, axis=1)
    print(f"apalancamiento (diseño real): max={h.max():.3f} media={h.mean():.3f} (k/N={Xr.shape[1] / n:.3f})")
    for j, name in zip(range(2, 6), ("C+", "U+", "C-", "U-")):
        e2 = np.sort(Xcore[:, j] ** 2)[::-1]
        top = np.argsort(Xcore[:, j] ** 2)[::-1][:2]
        print(f"  celda {name}: top2 Σε² = {e2[:2].sum() / e2.sum():.3f}; trimestres {[str(df.index[pos[t]]) for t in top]}; "
              f"h de esos = {np.round(h[top], 3).tolist()}")

    # ---------- DGP propio (recursión explícita) ----------
    e0 = np.nan_to_num(eps_all)
    resid = e_ar - e_ar.mean()
    T_all = len(df)
    sd_eps = eps.std(ddof=1)

    def simulate(bC, bU, rng, hetero=0.0, sigma0=1.0, normal=False):
        b = np.where(e0 > 0, D_all * bC[0] + (1 - D_all) * bU[0], D_all * bC[1] + (1 - D_all) * bU[1]) / kap
        if normal:
            inn = rng.normal(0, resid.std(), BURN + T_all)
        else:
            inn = rng.choice(resid, BURN + T_all)
        if hetero:  # varianza ∝ 1 + a·(ε_t/sd)², normalizada a varianza media 1 en la muestra
            sc = np.sqrt(1 + hetero * (e0 / sd_eps) ** 2)
            sc = sc / np.sqrt(np.mean(sc[pos] ** 2))
            inn[BURN:] *= sc
        imp = np.r_[np.zeros(BURN), b * e0] + sigma0 * inn + mu
        g = np.zeros(BURN + T_all)
        for t in range(BURN + T_all):
            g[t] = imp[t] + (f1 * g[t - 1] if t >= 1 else 0) + (f2 * g[t - 2] if t >= 2 else 0)
        g = g[BURN:]
        L = np.cumsum(g) / 100
        Lp = np.r_[np.nan, L]  # Lp[t] = L[t-1]
        ybar = np.array([np.mean([100 * (L[t + k] - Lp[t]) for k in range(5)]) for t in pos])
        return ybar, g

    def one(bC, bU, rng, **kw):
        y, g = simulate(bC, bU, rng, **kw)
        X = X_of(g)
        b, u, I = ols(y, X)
        dof = n - X.shape[1]
        r = {}
        for name, lags, hc3 in (("NW5", 5, False), ("NW5-HC3", 5, True)):
            se = sandwich(X, u, I, qd, lags, hc3)
            r[name] = (b[2:6], se[2:6], verdict(b[[2, 4]], se[[2, 4]], b[[3, 5]], dof))
        # s1_lin: ȳ sobre (1, ε, controles)
        XL = np.column_stack([np.ones(n), eps, X[:, 6:]])
        bl, ul, IL = ols(y, XL)
        sl = sandwich(XL, ul, IL, qd, 5, True)[1]
        r["lin_conf"] = stats.t.cdf(bl[1] / sl, n - XL.shape[1]) < 0.05
        return r, dof

    # error de diseño determinista (σ = 0) para comparar con F4 (tabla 1a, m = 1)
    yd, gd = simulate([bref, bref], [bref, bref], np.random.default_rng(0), sigma0=0.0)
    bd = ols(yd, X_of(gd))[0][2:6]
    print("error de diseño m=1 (C+,U+,C−,U−):", np.round(bd - bref, 6).tolist())
    # comprobación determinista de los estimadores (y sin ruido): ee y s1_lin, para comparar con el script R
    Xd = X_of(gd)
    _, ud, Id = ols(yd, Xd)
    XLd = np.column_stack([np.ones(n), eps, Xd[:, 6:]])
    bld, uld, ILd = ols(yd, XLd)
    print("determinista: ee NW5", [f"{v:.9f}" for v in sandwich(Xd, ud, Id, qd, 5, False)[2:6]],
          "| ee NW5-HC3", [f"{v:.9f}" for v in sandwich(Xd, ud, Id, qd, 5, True)[2:6]],
          "| s1_lin b, ee", f"{bld[1]:.9f}", f"{sandwich(XLd, uld, ILd, qd, 5, True)[1]:.9f}")
    if len(sys.argv) > 2 and sys.argv[2] == "det":
        return

    def run(m, c=1.0, reps=REPS, seed=0, **kw):
        rng = np.random.default_rng(SEED + seed)
        bC, bU = [c * m * bref] * 2, [c * bref] * 2
        truth = np.array([bC[0], bU[0], bC[1], bU[1]])
        cov = {k: np.zeros(4) for k in ("NW5", "NW5-HC3")}
        ver = {k: np.zeros((2, 4)) for k in ("NW5", "NW5-HC3")}
        joint = np.zeros(2)  # confirma H1^d y H0 confirmada (HC3)
        lin = 0
        for _ in range(reps):
            r, dof = one(bC, bU, rng, **kw)
            tc = stats.t.ppf(0.975, dof)
            for k in cov:
                b, se, v = r[k]
                cov[k] += np.abs(b - truth) <= tc * se
                ver[k][0, v[0]] += 1
                ver[k][1, v[1]] += 1
            lin += r["lin_conf"]
            joint += [(r["NW5-HC3"][2][i] == 0) and r["lin_conf"] for i in range(2)]
        tag = f"m={m} c={c} {kw}"
        for k, cv in cov.items():
            print(f"[{tag}] {k}: cobertura {np.round(cv / reps, 3).tolist()}; veredictos subida "
                  f"{np.round(ver[k][0] / reps, 3).tolist()} bajada {np.round(ver[k][1] / reps, 3).tolist()}")
        print(f"[{tag}] P(H0 confirma, NW5-HC3) = {lin / reps:.3f}; P(H0 y confirma H1^d) = {np.round(joint / reps, 3).tolist()}")

    if len(sys.argv) > 2 and sys.argv[2] == "m1":  # solo m = 1 con otra semilla (comprobación de discrepancias)
        run(1.0, seed=99)
        return
    run(1.0, seed=1)
    run(0.0, seed=2)
    run(1.0, c=40, reps=REPS // 2, seed=3)
    run(1.0, seed=4, hetero=1.0)  # heterocedasticidad ligada a |ε|: el peor caso para HC con apalancamiento alto
    run(1.0, seed=5, normal=True)


if __name__ == "__main__":
    main()
