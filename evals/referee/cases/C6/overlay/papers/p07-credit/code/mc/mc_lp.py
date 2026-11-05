"""Monte Carlo de la LP principal (skill mc-validate): el estimador de code/analysis/lp.py, sin cambios, sobre el DGP de
code/data/build_panel.py con T = 120 y T/2. Mide sesgo, RMSE, cobertura del IC al 95 % y potencia de b_1 y c_1 (H1).

Salida: output/MC_REPORT.md. Uso: uv run python papers/p07-credit/code/mc/mc_lp.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER.parents[1] / "tools"), str(PAPER / "code" / "data"), str(PAPER / "code" / "analysis")]
import build_panel
import lp
import mc

H_MAIN = 1
REPS = 1000
SEED = 7


def true_values(params: dict[str, float] = build_panel.PARAMS, h: int = H_MAIN) -> dict[str, float]:
    """Respuesta acumulada verdadera en h: el choque mueve dinv_t y se propaga con ρ (Σ_{k≤h} ρ^k)."""
    acc = sum(params["rho"] ** k for k in range(h + 1))
    return {"shock": params["beta"] * acc, "shock_x_credit": params["gamma"] * acc}


def dgp(T: int, rng: np.random.Generator):
    return build_panel.build(build_panel.simulate(T, rng))


def estimator(panel) -> tuple[np.ndarray, np.ndarray]:
    y, X = lp.design(panel, H_MAIN)
    b, se = lp.fit(y, X, lp.nw_lags(H_MAIN))
    return b[lp.TERMS].to_numpy(), se[lp.TERMS].to_numpy()


def main() -> None:
    results = (mc.run(dgp, estimator, true_values(), T=build_panel.T, reps=REPS, seed=SEED)
               + mc.run(dgp, estimator, true_values(), T=build_panel.T // 2, reps=REPS, seed=SEED + 1))
    lines = ["# Monte Carlo de la LP (h = 1)", "",
             (f"Estimador: `code/analysis/lp.py` (NW({lp.nw_lags(H_MAIN)})). DGP: `code/data/build_panel.py`. "
             f"{REPS} réplicas, semilla {SEED}. Banda de cobertura aceptable: [0,92; 0,98]."), "",
             "| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r.param} | {r.T} | {r.true:.3f} | {r.bias:+.3f} | {r.rmse:.3f} | {r.coverage:.3f} | "
              f"{r.power:.3f} | {r.failed} |" for r in results]
    lines += ["", "Los intervalos de NW de esta especificación son los que se usan en el texto."]
    (PAPER / "output" / "MC_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(r.row() for r in results))


if __name__ == "__main__":
    main()
