"""F17 · Réplica independiente del Referee de s1r_lin, s1r_liq y s1r_liq_nov (y de los r1r_*, el veredicto y los diagnósticos).

Escrita desde la SPEC (prereg_commit 3d6b508), sin importar nada de code/ (ni s1_lp, ni s1r_lp, ni la réplica en R del autor).
Datos: data/clean/stage1r_us.parquet + CSV de FRED en data/raw/stage1_us (solo lectura; se comprueba su hash con el MANIFEST).
Coeficientes con numpy.linalg.lstsq (QR) y, como control, statsmodels OLS; ee NW(5) Bartlett en trimestres naturales con residuos
HC3 escritos a mano; t de N − k g.l.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-08b/replicate_s1r.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox

PAPER = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RAW = PAPER / "data" / "raw"


def check_raw_hashes(ids):
    man = pd.read_csv(RAW / "MANIFEST.csv")
    for i in ids:
        rel = f"stage1_us/{i}.csv"
        want = man.loc[man.iloc[:, 0] == rel].iloc[0, 3]
        got = hashlib.sha256((RAW / rel).read_bytes()).hexdigest()
        assert got == want, f"hash de {rel} no coincide con el MANIFEST"


def load() -> pd.DataFrame:
    d = pd.read_parquet(PAPER / "data" / "clean" / "stage1r_us.parquet")
    d.index = pd.PeriodIndex(d.pop("quarter"), freq="Q")
    assert (np.diff(d.index.asi8) == 1).all()
    ids = {"inv": "A008RA3Q086SBEA", "gdp": "GDPC1", "defl": "GDPDEF"}
    check_raw_hashes(ids.values())
    for col, i in ids.items():
        f = pd.read_csv(RAW / "stage1_us" / f"{i}.csv")
        f.index = pd.PeriodIndex(pd.to_datetime(f["observation_date"]), freq="Q")
        d[col] = pd.to_numeric(f[i], errors="coerce").reindex(d.index)
    return d


def lag(x: np.ndarray, k: int) -> np.ndarray:
    """x_{t−k} (k < 0: adelanto) con NaN en los bordes."""
    out = np.full(len(x), np.nan)
    if k >= 0:
        out[k:] = x[:len(x) - k]
    else:
        out[:k] = x[-k:]
    return out


def nw_hc3(X: np.ndarray, y: np.ndarray, q: np.ndarray, L: int = 5):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    Q, R = np.linalg.qr(X)
    h = (Q ** 2).sum(1)  # palanca h_ii sin invertir X'X
    u = (y - X @ b) / (1 - h)
    Rinv = np.linalg.inv(R)
    bread = Rinv @ Rinv.T
    W = np.maximum(1 - np.abs(q[:, None] - q[None, :]) / (L + 1), 0)
    S = X * u[:, None]
    V = bread @ S.T @ W @ S @ bread
    n, k = X.shape
    b_sm = sm.OLS(y, X).fit().params
    assert np.allclose(b, b_sm, rtol=1e-10, atol=1e-12)
    return b, np.sqrt(np.diag(V)), n - k


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    d = load()
    q = d.index.asi8
    eps = d["rr_shock"].to_numpy()
    e0 = np.nan_to_num(eps, nan=0.0)
    s_lag = d["s_lag"].to_numpy()
    li = np.log(d["inv"].to_numpy())
    ybar = np.mean([100 * (lag(li, -h) - lag(li, 1)) for h in range(4, 13)], axis=0)
    ctl = {"dlinv": 100 * np.diff(li, prepend=np.nan), "dlgdp": 100 * np.diff(np.log(d["gdp"].to_numpy()), prepend=np.nan),
           "dldefl": 100 * np.diff(np.log(d["defl"].to_numpy()), prepend=np.nan), "dffr": np.diff(d["ffr"].to_numpy(), prepend=np.nan)}

    full = np.flatnonzero(d["in_rr_sample"].to_numpy(bool) & ~np.isnan(s_lag) & ~np.isnan(eps))
    vk = (d.index >= pd.Period("1979Q4", "Q")) & (d.index <= pd.Period("1982Q4", "Q"))
    nov = full[~vk[full]]
    from71 = full[d.index[full] >= pd.Period("1971Q3", "Q")]
    med = np.median(s_lag[full])
    sf = s_lag[full]
    states = {"median": (s_lag < med).astype(float), "q25": (s_lag < np.quantile(sf, 0.25)).astype(float),
              "logistic": 1 / (1 + np.exp(3.0 * (s_lag - med) / sf.std(ddof=1)))}

    def build(model, D, ctrl_lags=2):
        cols = {"const": np.ones(len(d))}
        cols |= {"b_lin": eps} if model == "lin" else {"D": D, "b_C": D * eps, "b_U": (1 - D) * eps}
        cols |= {f"eps_l{j}": lag(e0, j) for j in range(1, 11)}
        cols |= {f"eps_f{j}": lag(e0, -j) for j in range(1, 13)}
        cols |= {f"{v}_l{l}": lag(x, l) for l in range(1, ctrl_lags + 1) for v, x in ctl.items()}
        return cols

    specs = {"s1r_lin": ("lin", full, "median", 2), "s1r_liq": ("liq", full, "median", 2), "s1r_liq_nov": ("liq", nov, "median", 2),
             "r1r_from1971q3": ("liq", from71, "median", 2), "r1r_state_q25": ("liq", full, "q25", 2),
             "r1r_state_logistic": ("liq", full, "logistic", 2), "r1r_lags4": ("liq", full, "median", 4)}
    rows = []
    for sid, (model, idx, st, cl) in specs.items():
        cols = build(model, states[st], cl)
        X = np.column_stack(list(cols.values()))[idx]
        y = ybar[idx]
        assert not np.isnan(X).any() and not np.isnan(y).any(), sid
        b, se, dof = nw_hc3(X, y, q[idx])
        rows += [{"spec_id": sid, "term": t, "estimate": bi, "std_error": si, "dof": dof} for t, bi, si in zip(cols, b, se)]
    mine = pd.DataFrame(rows)
    mine.to_csv(OUT / "estimates_referee.csv", index=False)

    # comparación con el autor
    auth = pd.concat([pd.read_csv(PAPER / "output" / f) for f in ("estimates_py.csv", "estimates_py_robustness.csv")])
    m = mine.merge(auth, on=["spec_id", "term"], suffixes=("_ref", "_aut"), how="outer", indicator=True)
    assert (m["_merge"] == "both").all(), m[m["_merge"] != "both"]
    m["d_est"] = (m["estimate_ref"] - m["estimate_aut"]).abs()
    m["d_se"] = (m["std_error_ref"] - m["std_error_aut"]).abs()
    assert (m["dof_ref"] == m["dof_aut"]).all()
    print(f"filas comparadas: {len(m)}; máx |Δβ| = {m['d_est'].max():.2e}; máx |Δee| = {m['d_se'].max():.2e}")
    for grp, g in m.groupby(m["spec_id"].str.startswith("s1r")):
        print(f"  {'s1r_*' if grp else 'r1r_*'}: {len(g)} filas, máx |Δβ| = {g['d_est'].max():.2e}, máx |Δee| = {g['d_se'].max():.2e}")

    # términos que deciden y veredicto V3s, escritos desde la SPEC:148-157
    def tp(sid, t):
        r = mine[(mine.spec_id == sid) & (mine.term == t)].iloc[0]
        tt = r.estimate / r.std_error
        return r.estimate, r.std_error, int(r.dof), stats.t.cdf(tt, r.dof), stats.t.sf(tt, r.dof)

    print("\n| id | término | β̂ | ee | g.l. | p (β<0) | IC 95 % |")
    for sid, (model, *_r) in specs.items():
        for t in (["b_lin"] if model == "lin" else ["b_C", "b_U"]):
            b, se, dof, pl, _ = tp(sid, t)
            h = stats.t.ppf(0.975, dof) * se
            print(f"| {sid} | {t} | {b:.6f} | {se:.6f} | {dof} | {pl:.4f} | [{b - h:.3f}, {b + h:.3f}] |")
    b, se, dof, pl, _ = tp("s1r_lin", "b_lin")
    if not (b < 0 and pl < 0.05):
        v = "h0_falla"
    else:
        _, _, _, plc, puc = tp("s1r_liq", "b_C")
        _, _, _, pln, _ = tp("s1r_liq_nov", "b_C")
        v = "refuta_a" if puc < 0.05 else ("no_concluyente" if plc >= 0.05 else ("confirma" if pln < 0.05 else "no_concluyente"))
    print(f"\nveredicto V3s (réplica): {v}")

    # diagnósticos de los choques (sin la inversión)
    D = states["median"]
    Z = np.column_stack([lag(ctl[v], j) for v in ("dlgdp", "dldefl", "dffr") for j in range(1, 5)])
    for name, idx in (("completa", full), ("sin Volcker", nov)):
        e = eps[idx]
        bal = sm.OLS(e, sm.add_constant(np.column_stack([D[idx], s_lag[idx]]))).fit(cov_type="HC1")
        f3 = bal.f_test(np.eye(3)[1:])
        lb = acorr_ljungbox(e, lags=[12])
        pr = sm.OLS(e, sm.add_constant(Z[idx])).fit(cov_type="HC1")
        fp = pr.f_test(np.eye(13)[1:])
        print(f"{name}: N={len(idx)} D1={int(D[idx].sum())}/{int((1 - D[idx]).sum())} D2={np.abs(e[D[idx] == 1]).sum():.3f}/"
              f"{np.abs(e[D[idx] == 0]).sum():.3f} D3 F={float(np.squeeze(f3.fvalue)):.2f} p={float(f3.pvalue):.3f} "
              f"LB={float(lb.lb_stat.iloc[0]):.2f} p={float(lb.lb_pvalue.iloc[0]):.3f} "
              f"DP F={float(np.squeeze(fp.fvalue)):.2f} ({int(fp.df_num)},{int(fp.df_denom)}) p={float(fp.pvalue):.3f}")

    # lecturas de implementación de F15 (sin la inversión: solo estado)
    med71 = np.median(s_lag[from71])
    switch = int(((s_lag[from71] < med) != (s_lag[from71] < med71)).sum())
    print(f"\nr1r_from1971q3: mediana completa {med:.5f}, mediana desde 1971Q3 {med71:.5f}; filas que cambian de estado: {switch} de "
          f"{len(from71)}; restringidas con la completa: {int((s_lag[from71] < med).sum())}")
    sd = sf.std(ddof=1)
    raw_F = 1 / (1 + np.exp(3.0 * (sf - med)))
    std_F = states["logistic"][full]
    print(f"logística: sd(s_lag)={sd:.4f}; F sin estandarizar en [{raw_F.min():.3f}, {raw_F.max():.3f}]; estandarizada en "
          f"[{std_F.min():.3f}, {std_F.max():.3f}], media {std_F.mean():.3f}; corr(F, D_mediana) = "
          f"{np.corrcoef(std_F, D[full])[0, 1]:.3f}")

    # comprobación de datos: s = log(liq) − media de los 12 trimestres anteriores; s_lag = s_{t−1}
    ll = np.log(d["liq_broad_debt"])
    s_chk = ll - ll.shift(1).rolling(12).mean()
    ok = (s_chk - d["s"]).abs().max(), (d["s"].shift(1) - d["s_lag"]).abs().max()
    print(f"datos: máx |s − reconstruida| = {ok[0]:.2e}; máx |s_lag − s.shift(1)| = {ok[1]:.2e}")
    pre = d.index < pd.Period("1969Q1", "Q")
    print(f"rr_shock con dato antes de 1969Q1: {int(d.loc[pre, 'rr_shock'].notna().sum())}; muestra: {d.index[full][0]}–{d.index[full][-1]}")


if __name__ == "__main__":
    main()
