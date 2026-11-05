"""Panel trimestral de p07 (1994T1–2023T4, T = 120): series simuladas con el DGP de la SPEC («Datos») y sus transformaciones.

Salida: data/clean/panel.parquet y data/clean/DICTIONARY.md.
Uso: uv run python papers/p07-credit/code/data/build_panel.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[2]
SEED = 20261105
T = 120
START = "1994Q1"
BURN = 40

# Parámetros del DGP (SPEC, «Datos»). La inversión responde al choque con más fuerza cuando el crédito está restringido.
PARAMS = {"mu": 0.5, "rho": 0.3, "beta": -1.0, "gamma": -0.8, "delta": -0.4, "sigma": 1.0}
FCI_COMPONENTS = ["term_spread", "baa_spread"]


def zscore(x: pd.Series | np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    return (x - x.mean()) / x.std(ddof=1)


def ar1(n: int, rho: float, mean: float, sd: float, rng: np.random.Generator) -> np.ndarray:
    """AR(1) estacionario de longitud n con media `mean` y desviación típica incondicional `sd`."""
    e = rng.normal(0, sd * np.sqrt(1 - rho**2), n)
    x = np.empty(n)
    x[0] = mean + rng.normal(0, sd)
    for t in range(1, n):
        x[t] = mean + rho * (x[t - 1] - mean) + e[t]
    return x


def simulate(T: int, rng: np.random.Generator, params: dict[str, float] = PARAMS) -> pd.DataFrame:
    """Series observadas. El estado y el choque entran en el DGP estandarizados en la muestra (como en el panel)."""
    n = T + BURN
    ff4 = rng.normal(0, 0.05, n)  # sorpresa de alta frecuencia en el futuro de fed funds (pp)
    sloos = ar1(n, 0.85, 5.0, 20.0, rng)  # % neto de bancos que endurecen las condiciones de crédito
    term = ar1(n, 0.9, 1.5, 1.0, rng)
    baa = ar1(n, 0.8, 2.2, 0.6, rng)
    dgdp = ar1(n, 0.5, 0.6, 0.7, rng)
    infl = ar1(n, 0.7, 0.5, 0.3, rng)
    shock, credit = zscore(ff4[BURN:]), zscore(sloos[BURN:])
    p = params
    dinv = np.empty(T)
    prev, eps = p["mu"] / (1 - p["rho"]), rng.normal(0, p["sigma"], T)
    for t in range(T):
        s_lag = credit[t - 1] if t else 0.0
        dinv[t] = (p["mu"] + p["rho"] * prev + (p["beta"] + p["gamma"] * s_lag) * shock[t]
                   + p["delta"] * (baa[BURN + t - 1] - 2.2) + eps[t])
        prev = dinv[t]
    return pd.DataFrame({
        "date": pd.period_range(START, periods=T, freq="Q").astype(str),
        "loginv": 400 + np.cumsum(dinv), "dgdp": dgdp[BURN:], "infl": infl[BURN:], "term_spread": term[BURN:],
        "baa_spread": baa[BURN:], "sloos": sloos[BURN:], "ff4": ff4[BURN:],
    })


def build(series: pd.DataFrame) -> pd.DataFrame:
    """Transformaciones del panel: choque y estado estandarizados, índice de condiciones financieras."""
    panel = series.copy()
    panel["dinv"] = panel["loginv"].diff()
    panel["shock"] = zscore(panel["ff4"])
    panel["credit"] = zscore(panel["sloos"])
    panel["fci"] = np.mean([zscore(panel[c]) for c in FCI_COMPONENTS], axis=0)
    return panel


DICTIONARY = """# Diccionario de data/clean/panel.parquet

Trimestral, 1994T1–2023T4 (T = 120). Generado por `code/data/build_panel.py` (semilla {seed}).

| Columna | Descripción | Unidad |
|---|---|---|
| date | Trimestre | AAAAQn |
| loginv | 100 × log de la inversión no residencial real | log × 100 |
| dinv | Crecimiento trimestral de la inversión (Δ loginv) | pp |
| dgdp | Crecimiento trimestral del PIB real | pp |
| infl | Inflación trimestral del deflactor | pp |
| term_spread | Diferencial 10 años − 3 meses | pp |
| baa_spread | Diferencial Baa − bono a 10 años | pp |
| sloos | % neto de bancos que endurecen el crédito a empresas | % |
| ff4 | Sorpresa monetaria de alta frecuencia (futuro de fed funds, ventana de 30 min) | pp |
| shock | ff4 estandarizada en la muestra | desv. típ. |
| credit | sloos estandarizada en la muestra (estado del crédito; > 0 = restringido) | desv. típ. |
| fci | Índice de condiciones financieras: media de {components} estandarizados | desv. típ. |
"""


def main() -> None:
    panel = build(simulate(T, np.random.default_rng(SEED)))
    out = PAPER / "data" / "clean"
    out.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(out / "panel.parquet", index=False)
    (out / "DICTIONARY.md").write_text(
        DICTIONARY.format(seed=SEED, components=", ".join(FCI_COMPONENTS)), encoding="utf-8")
    print(f"panel: {len(panel)} trimestres, {panel['date'].iloc[0]}–{panel['date'].iloc[-1]}")


if __name__ == "__main__":
    main()
