"""Cuentas rápidas de potencia para REDESIGN_POWER_2026-11-04.md (Director científico). No es un análisis ni un Monte Carlo.

Regla dura: no se usa la respuesta de la inversión a ningún choque. De la inversión solo entran σ_e y κ del AR(2) univariante
que ya publicó F4 (`output/tables/f4_power.md`). Del resto de variables se usa su ruido univariante (AR(2) sin choques) y la
respuesta de los TIPOS a los choques (primera etapa), nunca la de una variable de resultado.

Uso: uv run python -I papers/p01-liquidity/exploration/redesign_power_calc.py  → escribe exploration/redesign_power_tables.md
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lfilter

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
sys.path[:0] = [str(PAPER / "code" / "data")]
import sample_counts

OUT = PAPER / "exploration" / "redesign_power_tables.md"
# De output/tables/f4_power.md (AR(2) univariante de 100·Δlog inv_nonres_q en las 102 filas, sin choques)
SIGMA_E, KAPPA, PI_FFR, BETA_REF = 1.357, 1.865, 1.761, -0.881
CONTROLS_SHRINK = 0.909  # σ_e condicionado a los controles (F4, tabla 3)
F4_MULT_08 = (40, 30)  # F4 tabla 2: c con potencia ≥ 0,8 (subida 0,84 con c=40; bajada 0,72 con c=30 y 0,93 con c=40)


def power(beta: float, se: float, alpha: float) -> float:
    """Potencia del contraste unilateral β < 0 (aproximación normal)."""
    return float(stats.norm.cdf(abs(beta) / se - stats.norm.ppf(1 - alpha)))


def mde(se: float, alpha: float, pw: float = 0.8) -> float:
    """Efecto mínimo detectable (en valor absoluto) con potencia pw."""
    return float(se * (stats.norm.ppf(1 - alpha) + stats.norm.ppf(pw)))


def ar2_noise(y: pd.Series, rows: pd.Index) -> tuple[float, float]:
    """σ de las innovaciones y κ (efecto en ȳ de un impulso unitario) de un AR(2) univariante en `rows`, sin choques.
    Los retardos se toman del calendario completo (como en F4)."""
    Z = np.column_stack([np.ones(len(rows)), y.shift(1).loc[rows], y.shift(2).loc[rows]])
    coef, *_ = np.linalg.lstsq(Z, y.loc[rows].to_numpy(), rcond=None)
    resid = y.loc[rows].to_numpy() - Z @ coef
    psi = lfilter([1.0], [1.0, -coef[1], -coef[2]], np.r_[1.0, np.zeros(4)])
    return float(resid.std(ddof=3)), float(np.cumsum(psi).mean())


def oracle_se(X: np.ndarray, sigma: float, kappa: float) -> np.ndarray:
    """ee de MCO del impulso en g_t si el DGP de F4 fuera conocido (cota de información), en unidades de ȳ."""
    return kappa * sigma * np.sqrt(np.diag(np.linalg.inv(X.T @ X)))


def first_stage(dffr: pd.Series, shock: pd.Series) -> tuple[float, float]:
    """π y F de Δffr_t (media trimestral) sobre el choque del trimestre; ee de White."""
    X = np.column_stack([np.ones(len(shock)), shock])
    y = dffr.to_numpy()
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ b
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ (X.T * u**2) @ X @ XtXi * len(y) / (len(y) - 2)
    return float(b[1]), float(b[1] ** 2 / V[1, 1])


def top_share(s: pd.Series, k: int = 4) -> float:
    e2 = (s**2).sort_values(ascending=False)
    return float(e2.iloc[:k].sum() / e2.sum())


def ramey_monthly() -> pd.DataFrame:
    z = zipfile.ZipFile(ROOT / "datalake/raw/narrative/ramey/Ramey_HOM_monetary.zip")
    m = pd.read_excel(io.BytesIO(z.read("Monetarydat.xlsx")), sheet_name="Monthly", engine="openpyxl")
    k = (m.DATES * 12).round().astype(int)  # meses desde el año 0; DATES = año + (mes−1)/12
    m["q"] = pd.PeriodIndex(pd.to_datetime({"year": k // 12, "month": k % 12 + 1, "day": 1}), freq="Q")
    return m.groupby("q").agg(ffr=("FFR", "mean"), rr=("RRSHOCK", lambda x: x.sum(min_count=1)))


def jk_quarterly() -> pd.Series:
    j = pd.read_csv(ROOT / "datalake/raw/shocks/jarocinski_karadi/fed_202401/shocks_fed_jk_m.csv")
    j["q"] = pd.PeriodIndex(pd.to_datetime({"year": j.year, "month": j.month, "day": 1}), freq="Q")
    return j.groupby("q")["MP_pm"].sum()


def filt(idx: pd.PeriodIndex, ffr: pd.Series) -> pd.PeriodIndex:
    """Mismos filtros que la muestra principal: sin ZLB ni 2019Q1–2021Q4."""
    covid = (idx >= pd.Period(sample_counts.COVID[0], "Q")) & (idx <= pd.Period(sample_counts.COVID[1], "Q"))
    return idx[(ffr.reindex(idx) >= sample_counts.ZLB).to_numpy() & ~covid]


def main() -> None:
    df = sample_counts.panel()
    d, _ = sample_counts.sample(df)
    rows = d.index
    eps = d["mps_bs23_orth"]
    D = (d["s_lag"] < d["s_lag"].median()).astype(float)
    lines = ["# Cuentas de REDESIGN_POWER_2026-11-04 (generado por `exploration/redesign_power_calc.py`)", ""]

    # --- 1. Cota de información (oráculo) frente a la LP de F4 ---
    pos, neg = eps.clip(lower=0), eps.clip(upper=0)
    Xc = np.column_stack([np.ones(len(d)), D, D * pos, (1 - D) * pos, D * neg, (1 - D) * neg])
    Xl = np.column_stack([np.ones(len(d)), eps])
    se_c = oracle_se(Xc, SIGMA_E, KAPPA)[2:]
    se_l = oracle_se(Xl, SIGMA_E, KAPPA)[1]
    lines += ["## 1. Cota de información con el DGP de F4 conocido (ee del impulso, en unidades de ȳ)", "",
              f"σ_e = {SIGMA_E}, κ = {KAPPA}, β_ref = {BETA_REF} (F4). Con controles, multiplicar los ee por {CONTROLS_SHRINK}.",
              "", ("| término | ee oráculo | ee LP de F4 (NW5+HC3, desv. típ. de β̂) | pérdida LP/oráculo | potencia oráculo con β_ref (α=0,025) "
              "| c = MDE/|β_ref| oráculo |"), "|---|---|---|---|---|---|"]
    f4_sd = {"b_pos_C": 10.892, "b_pos_U": 15.797, "b_neg_C": 7.842, "b_neg_U": 13.581}  # F4 tabla 1a, m=1, T=102
    for name, se in zip(["b_pos_C", "b_pos_U", "b_neg_C", "b_neg_U"], se_c, strict=True):
        lines.append(f"| {name} | {se:.2f} | {f4_sd[name]:.2f} | {f4_sd[name] / se:.1f} | {power(BETA_REF, se, 0.025):.3f} "
                     f"| {mde(se, 0.025) / abs(BETA_REF):.1f} |")
    lines.append(f"| β_lin (s1_lin, sin celdas) | {se_l:.2f} | — (F4 no lo simuló) | — | {power(BETA_REF, se_l, 0.05):.3f} (α=0,05) "
                 f"| {mde(se_l, 0.05) / abs(BETA_REF):.1f} |")
    lines += ["", (f"R² poblacional del choque en ȳ con β_ref: {(BETA_REF * eps.std()) ** 2 / (KAPPA * SIGMA_E) ** 2:.5f} "
              f"(β_ref·sd(ε) = {BETA_REF * eps.std():.3f} pp frente a κσ_e = {KAPPA * SIGMA_E:.2f} pp)."), ""]

    # --- 2. Varianza del choque en unidades de fed funds ---
    rm = ramey_monthly()
    ffr_all = pd.concat([rm["ffr"].loc[:"1984Q4"], df["ffr"]])
    dffr = ffr_all.diff()
    jk = jk_quarterly()
    cand = {
        "BS-2023 orth (FOMC), muestra prerreg.": d["mps_bs23_orth"],
        "BS-2023 raw (FOMC), misma muestra": d["mps_bs23_raw"],
        "BS-2025 ME, 1994–2023 filtrada": df["mps_bs25_me"].loc["1994Q1":"2023Q4"],
        "JK MP_pm, 1990–2023 filtrada": jk.loc["1990Q1":"2023Q4"],
        "Romer-Romer (Coibion), 1969–2007": rm["rr"].loc["1969Q1":"2007Q4"],
        "Romer-Romer, 1969–2007 sin 1979Q4–1982Q4": rm["rr"].loc["1969Q1":"2007Q4"].drop(
            pd.period_range("1979Q4", "1982Q4", freq="Q")),
        "Romer-Romer, 1988–2007 filtrada": rm["rr"].loc["1988Q2":"2007Q4"],
    }
    lines += ["## 2. Choques: varianza en unidades de fed funds (primera etapa sobre Δffr_t; no usa ninguna variable de resultado)", "",
              "Ganancia = √(N·π²·var(ε)) relativa a la fila 1: factor en el estadístico t con el mismo ruido de la variable de resultado.",
              "", "| choque | N | sd(ε) | π (Δffr_t) | F primera etapa | sd ffr-equiv. = π·sd(ε) | % de Σε² en los 4 mayores | ganancia t |",
              "|---|---|---|---|---|---|---|---|"]
    base = None
    for name, s in cand.items():
        s = s.dropna()
        if "1969" not in name:
            s = s.loc[filt(s.index, ffr_all)]
        pi, F = first_stage(dffr.reindex(s.index), s)
        info = np.sqrt(len(s)) * abs(pi) * s.std()
        base = base or info
        lines.append(f"| {name} | {len(s)} | {s.std():.3f} | {pi:.2f} | {F:.1f} | {abs(pi) * s.std():.3f} | {top_share(s):.0%} "
                     f"| {info / base:.1f} |")
    # Innovación recursiva del fed funds (identificación por calendario; tope de varianza, no un choque limpio)
    for lab, a, b in [("1969–2007", "1969Q1", "2007Q4"), ("1988–2023 filtrada", "1988Q2", "2023Q4")]:
        y = dffr.loc[a:b]
        Z = pd.concat({f"l{k}": dffr.shift(k) for k in range(1, 5)}, axis=1).loc[y.index]
        ok = Z.notna().all(axis=1) & y.notna()
        idx = y.index[ok]
        if "filtrada" in lab:
            idx = filt(idx, ffr_all)
        Zm = np.column_stack([np.ones(len(idx)), Z.loc[idx]])
        u = y.loc[idx].to_numpy() - Zm @ np.linalg.lstsq(Zm, y.loc[idx].to_numpy(), rcond=None)[0]
        info = np.sqrt(len(idx)) * u.std()
        lines.append(f"| Innovación de Δffr (4 retardos), {lab} | {len(idx)} | {u.std():.3f} | 1 (def.) | — | {u.std():.3f} | "
                     f"{top_share(pd.Series(u)):.0%} | {info / base:.1f} |")
    lines.append("")

    # --- 3. Panel con efectos fijos de tiempo: factor en t frente al agregado ---
    lines += ["## 3. Panel con efectos fijos de tiempo: t_panel / t_agregado = √G · (σ_agg/σ_idio) · (Δβ·sd_X / |β|)", "",
              ("G = grupos con ruido idiosincrásico independiente; Δβ·sd_X/|β| = diferencia de respuesta entre grupos a 1 sd de X, "
              "relativa a la respuesta media."), "", "| G | σ_idio/σ_agg | Δβ·sd_X/|β| | factor en t | c necesario (≈35/factor) |",
              "|---|---|---|---|---|"]
    for G in (2, 8, 40, 200):
        for r in (1, 2, 4):
            f = np.sqrt(G) / r * 0.5
            lines.append(f"| {G} | {r} | 0,5 | {f:.2f} | {35 / f:.0f} |")
    lines.append("")

    # --- 4. MDE de otras variables de resultado (ruido univariante, sin choques) ---
    lines += ["## 4. Efecto mínimo detectable (potencia 0,8, α = 0,05 unilateral, oráculo lineal, choque BS orth, N = 102)", "",
              ("ȳ = media h=0..4 del cambio acumulado. Ruido = AR(2) univariante en las 102 filas, **sin choques**. "
              "MDE por 1 pp de fed funds = MDE por 1 pp de ε / π_ffr."), "",
              "| variable | transformación | σ innov. | κ | MDE por 1 pp ε | MDE por 1 pp de fed funds |", "|---|---|---|---|---|---|"]
    outcomes = {
        "inversión no residencial (F4)": None,
        "liquidez amplia NFC (Z.1)": ("nfc_liq_broad", "100·Δlog"),
        "préstamos bancarios NFC (Z.1)": ("nfc_bank_loans", "100·Δlog"),
        "deuda NFC (Z.1)": ("nfc_debt", "100·Δlog"),
        "PIB real": ("gdp_real", "100·Δlog"),
        "EBP": ("ebp", "Δ (pp)"),
    }
    sx = np.sqrt(((eps - eps.mean()) ** 2).sum())
    for name, spec in outcomes.items():
        if spec is None:
            sig, kap, tr = SIGMA_E, KAPPA, "100·Δlog"
        else:
            col, tr = spec
            y = 100 * np.log(df[col]).diff() if tr.startswith("100") else df[col].diff()
            sig, kap = ar2_noise(y, rows)
        m = mde(kap * sig / sx, 0.05)
        lines.append(f"| {name} | {tr} | {sig:.3f} | {kap:.2f} | {m:.1f} | {m / PI_FFR:.1f} |")
    lines.append("")

    # --- 5. Diseños combinados: cota del oráculo por choque y muestra, con el ruido univariante de la inversión de ESA muestra ---
    inv = pd.read_csv(ROOT / "datalake/raw/fred/csv/A008RA3Q086SBEA.csv", parse_dates=["observation_date"])
    inv = inv.set_index(pd.PeriodIndex(inv.observation_date, freq="Q"))["A008RA3Q086SBEA"]
    g = 100 * np.log(inv).diff()
    rr = rm["rr"].loc["1969Q1":"2007Q4"].dropna()
    volcker = pd.period_range("1979Q4", "1982Q4", freq="Q")
    yz = dffr.loc["1969Q1":"2007Q4"]
    Zr = np.column_stack([np.ones(len(yz))] + [dffr.shift(k).loc[yz.index] for k in range(1, 5)])
    innov = pd.Series(yz.to_numpy() - Zr @ np.linalg.lstsq(Zr, yz.to_numpy(), rcond=None)[0], index=yz.index)
    designs = {
        "BS-2023 orth, 1988–2023 (prerreg.)": (eps, PI_FFR),
        "Romer-Romer, 1969–2007": (rr, first_stage(dffr.reindex(rr.index), rr)[0]),
        "Romer-Romer, 1969–2007 sin Volcker": (rr.drop(volcker), first_stage(dffr.reindex(rr.drop(volcker).index),
                                                                                 rr.drop(volcker))[0]),
        "Innovación recursiva de Δffr, 1969–2007": (innov, 1.0),
    }
    lines += ["## 5. Diseños combinados: c = MDE/|β_ref| con el oráculo (potencia 0,8)", "",
              ("β_ref = −0,5 pp de ȳ por 1 pp de fed funds (F4: −2,5 % en el pico, TT pp. 11–12, rampa a h=10) × π del choque. "
               "Ruido: AR(2) univariante de 100·Δlog A008RA3Q086SBEA **en la muestra de cada fila**, sin choques. "
               "Estado: mitad de la muestra, independiente de ε (supuesto). La LP real pierde ×1,2–1,4 frente al oráculo (§1)."), "",
              ("| diseño | N | σ_e | κ | c lineal (α=0,05) | c estado C, signos juntos (α=0,05) | c estado C por signo, subida (α=0,025) "
              "| potencia lineal con β_ref |"), "|---|---|---|---|---|---|---|---|"]
    for name, (s, pi) in designs.items():
        sig, kap = (SIGMA_E, KAPPA) if "prerreg" in name else ar2_noise(g, s.index)
        bref = 0.5 * abs(pi)
        se_lin = kap * sig / np.sqrt(((s - s.mean()) ** 2).sum())
        sp = s.clip(lower=0)
        se_pos = kap * sig / np.sqrt(len(s) / 2 * sp.var())
        lines.append(f"| {name} | {len(s)} | {sig:.2f} | {kap:.2f} | {mde(se_lin, 0.05) / bref:.1f} "
                     f"| {mde(se_lin * np.sqrt(2), 0.05) / bref:.1f} | {mde(se_pos, 0.025) / bref:.1f} "
                     f"| {power(bref, se_lin, 0.05):.2f} |")
    lines.append("")

    # --- 6. Ventana de horizontes del estadístico (LP): señal con la forma de TT frente al ruido del AR(2) de F4 ---
    phi1, phi2, peak_h = 0.465, 0.271, 10  # F4 (AR(2) sin choques) y supuesto de rampa de F4
    psi = lfilter([1.0], [1.0, -phi1, -phi2], np.r_[1.0, np.zeros(24)])
    C = np.cumsum(psi)  # efecto de e_{t+k} en log I_{t+h} − log I_{t−1}: C_{h−k}

    def snr(window: range) -> float:
        hs = np.array(window)
        signal = np.minimum(hs / peak_h, 1).mean()
        w = [np.mean([C[h - k] for h in hs if h >= k]) * (hs >= k).mean() for k in range(hs.max() + 1)]
        return float(signal / np.sqrt(np.sum(np.square(w))))

    base_snr = snr(range(5))
    lines += ["## 6. Ventana de horizontes del estadístico: señal/ruido relativa a ȳ (h = 0..4)", "",
              ("Señal: rampa de F4 hasta el pico en h = 10 (TT p. 11: mínimo a 2–3 años). Ruido: innovaciones futuras e_{t..t+h} "
               "propagadas por el AR(2) de F4 (φ1 = 0,465, φ2 = 0,271). No usa datos."), "",
              "| ventana | señal media / pico | ratio señal/ruido relativo a h=0..4 |", "|---|---|---|"]
    for a, b in [(0, 4), (0, 8), (4, 12), (8, 12), (0, 12)]:
        r = range(a, b + 1)
        lines.append(f"| h = {a}..{b} | {np.minimum(np.array(r) / peak_h, 1).mean():.2f} | {snr(r) / base_snr:.2f} |")
    lines.append("")

    # --- 7. Combinación: c de §5 / ganancia de ventana de §6 × pérdida LP/oráculo de §1, y potencia con β_ref ---
    win = snr(range(4, 13)) / base_snr
    lines += ["## 7. Diseños de §5 con la ventana h = 4..12 (§6) y la pérdida de la LP (§1: ×1,2 a ×1,4)", "",
              (f"c_LP = c_oráculo(§5) / {win:.2f} × pérdida. Potencia con β_ref = Φ((z_α + z_0,8)/c_LP − z_α). Aproximación: supone que la pérdida de §1 y la ganancia de §6 se componen."), "",
              "| diseño | contraste | α | c_LP (pérdida 1,2–1,4) | potencia con β_ref |", "|---|---|---|---|---|"]
    za8 = {a: stats.norm.ppf(1 - a) + stats.norm.ppf(0.8) for a in (0.05, 0.025)}
    for name, (s, pi) in designs.items():
        sig, kap = (SIGMA_E, KAPPA) if "prerreg" in name else ar2_noise(g, s.index)
        bref = 0.5 * abs(pi)
        se_lin = kap * sig / np.sqrt(((s - s.mean()) ** 2).sum())
        se_pos = kap * sig / np.sqrt(len(s) / 2 * s.clip(lower=0).var())
        for lab, se, a in [("lineal (H0)", se_lin, 0.05), ("estado C, signos juntos", se_lin * np.sqrt(2), 0.05),
                           ("estado C, subida (Holm)", se_pos, 0.025)]:
            c = [mde(se, a) / bref / win * loss for loss in (1.2, 1.4)]
            p = [stats.norm.cdf(za8[a] / ci - stats.norm.ppf(1 - a)) for ci in c]
            lines.append(f"| {name} | {lab} | {a} | {c[0]:.1f}–{c[1]:.1f} | {p[1]:.2f}–{p[0]:.2f} |")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
