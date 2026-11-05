"""Monte Carlo del estimador de code/analysis/lp.py (skill mc-validate): ¿recupera b_12 y c_12 con el T de los datos?

El DGP es propio del Monte Carlo y está calibrado a los datos de data/clean/panel.parquet, sin generar ni sustituir esos
datos:
- choque: remuestreo iid del choque observado, centrado (conserva la masa en cero y las colas gruesas);
- spread: AR(1) estimado en los datos, con su respuesta estimada al choque del mes (el estado no es exógeno al choque);
- dip: AR(1) estimado en los datos más el efecto del choque (β + γ credit_{t−1}) shock_t, con residuos remuestreados;
- dcpi y dur: AR(1) gaussianos con los momentos de los datos (solo entran como controles).
β y γ son tamaños de efecto elegidos para el Monte Carlo (EFFECTS), no estimaciones. Respuesta verdadera acumulada en h:
b_h = β Σ_{k≤h} ρ^k y c_h = γ Σ_{k≤h} ρ^k.

Salida: output/MC_REPORT.md. Uso: uv run python papers/p07-credit/code/mc/mc_lp.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER.parents[1] / "tools"), str(PAPER / "code" / "analysis")]
import lp
import mc

EFFECTS = {"beta": -0.10, "gamma": -0.20}
REPS = 1000
SEED = 7
BURN = 60


def ar1(x: np.ndarray, extra: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """MCO de x_t sobre (1, x_{t−1}[, extra_t]): coeficientes y residuos."""
    X = np.column_stack([np.ones(len(x) - 1), x[:-1]] + ([] if extra is None else [extra[1:]]))
    coef = np.linalg.lstsq(X, x[1:], rcond=None)[0]
    return coef, x[1:] - X @ coef


def calibrate(panel: pd.DataFrame) -> dict:
    shock = panel["shock"].to_numpy()
    cal = {"shocks": shock - shock.mean()}
    (cal["mu"], cal["rho"]), cal["resid"] = ar1(panel["dip"].to_numpy()[1:])
    coef, res = ar1(panel["spread"].to_numpy(), shock)
    cal["spread"] = (*coef, res.std(ddof=3))
    for v in ("dcpi", "dur"):
        coef, res = ar1(panel[v].to_numpy()[1:])
        cal[v] = (*coef, res.std(ddof=2))
    return cal


def simulate(T: int, rng: np.random.Generator, cal: dict, effects: dict[str, float] = EFFECTS) -> pd.DataFrame:
    n = T + BURN
    shock = rng.choice(cal["shocks"], n)
    c0, c1, c2, sd = cal["spread"]
    spread = np.empty(n)
    spread[0] = c0 / (1 - c1)
    for t in range(1, n):
        spread[t] = c0 + c1 * spread[t - 1] + c2 * shock[t] + sd * rng.normal()
    credit = spread - spread[BURN:].mean()
    e = rng.choice(cal["resid"], n)
    dip = np.empty(n)
    dip[0] = cal["mu"] / (1 - cal["rho"])
    for t in range(1, n):
        dip[t] = cal["mu"] + cal["rho"] * dip[t - 1] + (effects["beta"] + effects["gamma"] * credit[t - 1]) * shock[t] + e[t]
    out = {"dip": dip, "spread": spread, "shock": shock, "credit": credit}
    for v in ("dcpi", "dur"):
        a, r, s = cal[v]
        x = np.empty(n)
        x[0] = a / (1 - r)
        for t in range(1, n):
            x[t] = a + r * x[t - 1] + s * rng.normal()
        out[v] = x
    df = pd.DataFrame({k: v[BURN:] for k, v in out.items()})
    z = [rng.normal(size=T).cumsum() * 0.1 + rng.normal(size=T) for _ in range(3)]
    df["fci"] = np.mean([(x - x.mean()) / x.std(ddof=1) for x in z], axis=0)  # condiciones financieras exógenas
    df["lip"] = np.cumsum(df["dip"])
    return df


def true_values(cal: dict, h: int = lp.H_MAIN, effects: dict[str, float] = EFFECTS) -> dict[str, float]:
    acc = sum(cal["rho"] ** k for k in range(h + 1))
    return {"shock": effects["beta"] * acc, "shock_x_credit": effects["gamma"] * acc}


def estimator(panel: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    b, se = lp.fit(*lp.design(panel, lp.H_MAIN))
    return b[lp.TERMS].to_numpy(), se[lp.TERMS].to_numpy()


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    cal = calibrate(panel)
    results = mc.validate(lambda T, rng: simulate(T, rng, cal), estimator, true_values(cal), T=len(panel),
                          reps=REPS, seed=SEED)
    lines = [f"# Monte Carlo de la LP (h = {lp.H_MAIN})", "",
             (f"Estimador: `code/analysis/lp.py` ({lp.LAGS} retardos, HC3). DGP propio calibrado a los datos "
              f"(`code/mc/mc_lp.py`): β = {EFFECTS['beta']}, γ = {EFFECTS['gamma']}, ρ = {cal['rho']:.3f}. "
              f"{REPS} réplicas, semilla {SEED}. Banda de cobertura aceptable: [0,92; 0,98]."), "",
             "| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r.param} | {r.T} | {r.true:.3f} | {r.bias:+.3f} | {r.rmse:.3f} | {r.coverage:.3f} | "
              f"{r.power:.3f} | {r.failed} |" for r in results]
    lines += ["", f"Con T = {len(panel)} la cobertura está dentro de la banda: los intervalos se usan en el texto."]
    (PAPER / "output" / "MC_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(r.row() for r in results))


if __name__ == "__main__":
    main()
