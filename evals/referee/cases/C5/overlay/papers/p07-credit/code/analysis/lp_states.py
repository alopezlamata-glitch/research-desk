"""Estado del crédito como indicador: LP h = 1 con credit_{t−1} = 1 si sloos_{t−1} supera un cuantil de la muestra.

Especificaciones exploratorias (no están en el prerregistro): cuantiles 0,50, 0,67, 0,75 y 0,90.
Salida: output/macros_states.tex. Uso: uv run python papers/p07-credit/code/analysis/lp_states.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER.parents[1] / "tools"), str(Path(__file__).resolve().parent)]
import lp
import research

H = 1
QUANTILES = {"Qfifty": 0.5, "Qsixtyseven": 2 / 3, "Qseventyfive": 0.75, "Qninety": 0.9}


def estimate_state(panel: pd.DataFrame, q: float) -> tuple[float, float]:
    indicator = panel.copy()
    indicator["credit"] = (panel["sloos"] > panel["sloos"].quantile(q)).astype(float)
    b, se = lp.fit(*lp.design(indicator, H), lp.nw_lags(H))
    return b["shock_x_credit"], se["shock_x_credit"]


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    lines = ["% Generado por code/analysis/lp_states.py: no editar a mano."]
    for name, q in QUANTILES.items():
        research.log_spec(PAPER, f"lp_h1_q{round(100 * q)}", "code/analysis/lp_states.py",
                          f"LP h=1 con indicador sloos > cuantil {q:.2f}", exploratory=True)
        b, se = estimate_state(panel, q)
        lines += [f"\\newcommand{{\\b{name}}}{{{b:.2f}}}", f"\\newcommand{{\\se{name}}}{{{se:.2f}}}",
                  f"\\newcommand{{\\p{name}}}{{{stats.norm.cdf(b / se):.3f}}}"]
        print(f"q={q:.2f}: c_1 = {b:.3f} ({se:.3f})")
    (PAPER / "output" / "macros_states.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
