"""Estimador de `s1_liq` (SPEC, «Prerregistro de la etapa 1»). Lo usan el Monte Carlo F4 y, sin cambios, el análisis real.

ȳ_t = (1/5) Σ_{h=0..4} 100·[log I_{t+h} − log I_{t−1}]
    = α + δ D + β⁺_C D ε⁺ + β⁺_U (1−D) ε⁺ + β⁻_C D ε⁻ + β⁻_U (1−D) ε⁻ + Σ_{ℓ=1,2} Γ_ℓ' x_{t−ℓ} + u_t

Errores estándar: Newey-West (Bartlett, 5 retardos) con los retardos medidos en **trimestres naturales**: la muestra tiene huecos
(ZLB, 2019–2021) y dos filas separadas por un hueco no comparten error de solape. Sin huecos coincide con el NW habitual.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

TERMS = ["b_pos_C", "b_pos_U", "b_neg_C", "b_neg_U"]  # D·ε⁺, (1−D)·ε⁺, D·ε⁻, (1−D)·ε⁻
CONTROLS = ["dlinv", "dlgdp", "dldefl", "dy2", "ebp"]
H = 4  # ȳ promedia h = 0..4


def controls(panel: pd.DataFrame, dlinv: pd.Series | None = None) -> pd.DataFrame:
    """Controles contemporáneos en el calendario del panel (100·Δlog o Δ en pp). `dlinv` sustituye a la inversión real (MC)."""
    c = pd.DataFrame(index=panel.index)
    c["dlinv"] = 100 * np.log(panel["inv_nonres_q"]).diff() if dlinv is None else dlinv
    c["dlgdp"] = 100 * np.log(panel["gdp_real"]).diff()
    c["dldefl"] = 100 * np.log(panel["gdp_deflator"]).diff()
    c["dy2"] = panel["y2_mean"].diff()
    c["ebp"] = panel["ebp"]
    return c


def ybar(log_level: pd.Series) -> pd.Series:
    """ȳ_t a partir de log I en el calendario (índice trimestral contiguo)."""
    base = log_level.shift(1)
    return sum(100 * (log_level.shift(-h) - base) for h in range(H + 1)) / (H + 1)


def state(s_lag: pd.Series, rows: pd.Index) -> pd.Series:
    """D_{t−1} = 1 si s_{t−1} < mediana de s_{t−1} en la muestra de estimación `rows`."""
    return (s_lag < s_lag.loc[rows].median()).astype(float)


def design(eps: pd.Series, D: pd.Series, ctrl: pd.DataFrame, rows: pd.Index) -> pd.DataFrame:
    """Matriz de regresores en las filas `rows` (16 columnas)."""
    ep, en = eps.clip(lower=0), eps.clip(upper=0)
    X = pd.DataFrame({"const": 1.0, "D": D,
                      "b_pos_C": D * ep, "b_pos_U": (1 - D) * ep, "b_neg_C": D * en, "b_neg_U": (1 - D) * en},
                     index=eps.index)
    for lag in (1, 2):
        X = X.join(ctrl.shift(lag).add_suffix(f"_l{lag}"))
    return X.loc[rows]


def hac_weights(quarters: np.ndarray, lags: int) -> np.ndarray:
    """Pesos de Bartlett según la distancia en trimestres naturales. Es una submatriz principal de la matriz de Toeplitz de
    Bartlett en la rejilla completa, así que es semidefinida positiva."""
    d = np.abs(quarters[:, None] - quarters[None, :])
    return np.clip(1 - d / (lags + 1), 0, None)


def fit(y: np.ndarray, X: np.ndarray, W: np.ndarray, small_sample: bool = False,
        leverage: bool = False) -> tuple[np.ndarray, np.ndarray, int]:
    """MCO con varianza sándwich X'ΩX, Ω = W ∘ uu'. Devuelve (β, ee, grados de libertad N−k).
    `W` = hac_weights(...) (W = I da White/HC0). `small_sample` multiplica la varianza por N/(N−k).
    `leverage` usa u_i/(1−h_ii) (HC3 de MacKinnon-White; con W de Bartlett, NW con residuos HC3)."""
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    beta = bread @ (X.T @ y)
    u = y - X @ beta
    if leverage:
        u = u / (1 - np.einsum("ij,jk,ik->i", X, bread, X))
    s = X * u[:, None]
    V = bread @ (s.T @ W @ s) @ bread * (n / (n - k) if small_sample else 1.0)
    return beta, np.sqrt(np.diag(V)), n - k


def one_sided_p(beta: np.ndarray, se: np.ndarray, dof: int, lower: bool = True) -> np.ndarray:
    """p unilateral de H0: β = 0 frente a β < 0 (`lower`) o β > 0, con la t de N−k grados de libertad."""
    t = beta / se
    return stats.t.cdf(t, dof) if lower else stats.t.sf(t, dof)


def holm(p: np.ndarray) -> np.ndarray:
    """p ajustados por Holm (step-down)."""
    order = np.argsort(p)
    adj = np.minimum(1, np.maximum.accumulate(p[order] * (len(p) - np.arange(len(p)))))
    out = np.empty_like(adj)
    out[order] = adj
    return out


OMEGA_MIN = 0.146  # ω_min de TFG2 (check_nesting.py::test_minimum_transmission_with_g0_at_tfg2_calibration)


def verdicts(b: dict[str, float], se: dict[str, float], dof: int, alpha: float = 0.05) -> dict[str, str]:
    """Reglas de decisión de la SPEC para H1⁺ y H1⁻. Devuelve {'pos'|'neg': 'confirma'|'refuta_a'|'refuta_b'|'no_concluyente'}.
    Orden de prioridad: confirma > refuta (a) > refuta (b) (la SPEC no las ordena; confirma y (b) pueden coincidir con un IC
    estrecho dentro de (−δ, 0): se cuenta como confirma y se informa aparte, ver `refute_b_also`)."""
    dirs = ("pos", "neg")
    bc = np.array([b[f"b_{d}_C"] for d in dirs])
    sc = np.array([se[f"b_{d}_C"] for d in dirs])
    p_conf = holm(one_sided_p(bc, sc, dof, lower=True))
    p_wrong = one_sided_p(bc, sc, dof, lower=False)
    t90 = stats.t.ppf(0.95, dof)  # IC al 90 %: β ± t_{0,95}·ee
    out = {}
    for i, d in enumerate(dirs):
        delta = OMEGA_MIN * abs(b[f"b_{d}_U"])
        if p_conf[i] < alpha:
            out[d] = "confirma"
        elif p_wrong[i] < alpha:
            out[d] = "refuta_a"
        elif bc[i] - t90 * sc[i] > -delta:
            out[d] = "refuta_b"
        else:
            out[d] = "no_concluyente"
    return out


def refute_b_also(b: dict[str, float], se: dict[str, float], dof: int, d: str) -> bool:
    """¿Se cumple la condición (b) aunque el veredicto asignado sea otro?"""
    return b[f"b_{d}_C"] - stats.t.ppf(0.95, dof) * se[f"b_{d}_C"] > -OMEGA_MIN * abs(b[f"b_{d}_U"])
