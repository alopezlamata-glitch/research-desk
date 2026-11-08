"""Estimador de la etapa 1 rediseñada (`s1r_*`; Desviaciones del 2026-11-07 en la SPEC). Lo usan el MC F9 y, sin cambios, el
análisis real.

ȳ_t = (1/9) Σ_{h=4..12} 100·[log I_{t+h} − log I_{t−1}]
s1r_lin: ȳ_t = α + β ε_t + Σ_{ℓ=1,2} Γ_ℓ' x_{t−ℓ} + u_t
s1r_liq: ȳ_t = α + δ D + β_C D ε_t + β_U (1−D) ε_t + Σ_{ℓ=1,2} Γ_ℓ' x_{t−ℓ} + u_t      (subidas y bajadas juntas)

Controles x (propuesta de F9 para F11): Δlog inversión, Δlog PIB real, Δlog deflactor y Δffr. Los de `s1_liq` no sirven antes de
1973–76 (EBP empieza en 1973 y el rendimiento a 2 años en 1976), y la muestra de Romer-Romer empieza en 1969.
Especificación aumentada (`shock_lags`, `shock_leads`): añade ε_{t−1..t−p} y ε_{t+1..t+q} sin interactuar. ȳ_t contiene la respuesta
a los choques reales de t−10..t+12; con choques correlacionados en la muestra, omitirlos sesga β̂ (F9, §1 de f9_power.md).
Los choques sin dato (antes de 1969 o después de 2007 en Romer-Romer) cuentan como 0.
Errores estándar: `s1_lp.fit` con pesos de Bartlett en trimestres naturales (`s1_lp.hac_weights`).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import s1_lp
from scipy import stats

HORIZONS = range(4, 13)
CONTROLS = ["dlinv", "dlgdp", "dldefl", "dffr"]
TERMS = {"lin": ["b_lin"], "liq": ["b_C", "b_U"]}
OMEGA_MIN = s1_lp.OMEGA_MIN


def controls(panel: pd.DataFrame, dlinv: pd.Series | None = None) -> pd.DataFrame:
    """Controles contemporáneos (100·Δlog o Δ en pp). `panel` lleva `inv`, `gdp`, `defl` y `ffr`; `dlinv` sustituye a la
    inversión real (MC)."""
    return pd.DataFrame({"dlinv": 100 * np.log(panel["inv"]).diff() if dlinv is None else dlinv,
                         "dlgdp": 100 * np.log(panel["gdp"]).diff(),
                         "dldefl": 100 * np.log(panel["defl"]).diff(),
                         "dffr": panel["ffr"].diff()}, index=panel.index)


def ybar(log_level: pd.Series, horizons: range = HORIZONS) -> pd.Series:
    """ȳ_t a partir de log I en un calendario trimestral contiguo."""
    base = log_level.shift(1)
    return sum(100 * (log_level.shift(-h) - base) for h in horizons) / len(horizons)


def design(eps: pd.Series, D: pd.Series, ctrl: pd.DataFrame, rows: pd.Index, spec: str,
           shock_lags: int = 0, shock_leads: int = 0) -> pd.DataFrame:
    """Regresores de `s1r_lin` (11 columnas) o `s1r_liq` (12), más los retardos y adelantos del choque, en las filas `rows`."""
    cols = {"const": 1.0, "b_lin": eps} if spec == "lin" else {"const": 1.0, "D": D, "b_C": D * eps, "b_U": (1 - D) * eps}
    e = eps.fillna(0.0)
    cols |= {f"eps_l{j}": e.shift(j) for j in range(1, shock_lags + 1)}
    cols |= {f"eps_f{j}": e.shift(-j) for j in range(1, shock_leads + 1)}
    X = pd.DataFrame(cols, index=eps.index)
    for lag in (1, 2):
        X = X.join(ctrl.shift(lag).add_suffix(f"_l{lag}"))
    return X.loc[rows]


def h0_confirms(b_lin: float, se_lin: float, dof: int, alpha: float = 0.05) -> bool:
    """H0 (`s1r_lin`): β_lin < 0 con p unilateral < α."""
    return bool(s1_lp.one_sided_p(np.array([b_lin]), np.array([se_lin]), dof)[0] < alpha)


def h1_verdict(b_C: float, se_C: float, dof: int, delta: float, alpha: float = 0.05) -> str:
    """H1 (`s1r_liq`, signos juntos): 'confirma' (β_C < 0, p < α) > 'refuta_a' (β_C > 0, p < α) > 'refuta_b' (IC al 90 % dentro
    de (−δ, ∞)) > 'no_concluyente'. δ lo fija la regla (b) que se adopte (SPEC vigente: 0,146·|β̂_U|)."""
    t = b_C / se_C
    if stats.t.cdf(t, dof) < alpha:
        return "confirma"
    if stats.t.sf(t, dof) < alpha:
        return "refuta_a"
    if b_C - stats.t.ppf(0.95, dof) * se_C > -delta:
        return "refuta_b"
    return "no_concluyente"


def decide(variant: str, h0_full: bool, h1_full: str, h0_nov: bool | None = None, h1_nov: str | None = None,
           b_C_nov: float | None = None) -> str:
    """Árbol de decisión completo con la condición de H0 ('h0_falla': H1 no se interpreta y se escala).
    V1: muestra completa (sin Volcker solo como comprobación). V2: muestra sin 1979Q4–1982Q4.
    V3: muestra completa; H1 se confirma solo si también se confirma sin Volcker (V3s) o si β̂_C sin Volcker < 0 (V3l).
    Una confirmación con muestra completa que no se sostiene sin Volcker es 'no_concluyente'."""
    if variant == "V2":
        return h1_nov if h0_nov else "h0_falla"
    if not h0_full:
        return "h0_falla"
    if variant == "V1" or h1_full != "confirma":
        return h1_full
    holds = h1_nov == "confirma" if variant == "V3s" else b_C_nov < 0
    return "confirma" if holds else "no_concluyente"
