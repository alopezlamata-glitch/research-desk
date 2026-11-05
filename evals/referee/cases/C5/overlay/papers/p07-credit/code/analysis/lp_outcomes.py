"""Otras variables de actividad: la LP de h = 12 con el empleo, las viviendas iniciadas o el paro (con el signo cambiado,
para que una caída sea siempre una contracción) como variable dependiente, con los controles de la LP principal.

Especificaciones exploratorias (no están en el prerregistro). Salida: output/macros_outcomes.tex.
Uso: uv run python papers/p07-credit/code/analysis/lp_outcomes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PAPER = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PAPER.parents[1] / "tools"), str(Path(__file__).resolve().parent)]
import lp
import research

OUTCOMES = {"Payems": lambda p: 100 * np.log(p["payems"]), "Houst": lambda p: 100 * np.log(p["houst"]),
            "Unrate": lambda p: -p["unrate"]}


def estimate_outcome(panel: pd.DataFrame, name: str) -> tuple[float, float]:
    d = panel.copy()
    d["lip"] = OUTCOMES[name](panel)  # misma especificación y controles que la principal; cambia solo y
    b, se = lp.fit(*lp.design(d, lp.H_MAIN))
    return b["shock"], se["shock"]


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    lines = ["% Generado por code/analysis/lp_outcomes.py: no editar a mano."]
    for name in OUTCOMES:
        research.log_spec(PAPER, f"lp_h{lp.H_MAIN}_{name.lower()}", "code/analysis/lp_outcomes.py",
                          f"LP h={lp.H_MAIN} con {name.lower()} como resultado", exploratory=True)
        b, se = estimate_outcome(panel, name)
        lines += [f"\\newcommand{{\\b{name}Htwelve}}{{{b:.2f}}}", f"\\newcommand{{\\se{name}Htwelve}}{{{se:.2f}}}",
                  f"\\newcommand{{\\p{name}Htwelve}}{{{lp.p_text(stats.norm.cdf(b / se))}}}"]
        print(f"{name}: b_12 = {b:.3f} ({se:.3f})")
    (PAPER / "output" / "macros_outcomes.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
