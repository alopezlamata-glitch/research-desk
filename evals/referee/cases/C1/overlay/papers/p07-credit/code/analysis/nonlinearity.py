"""Test model-free de no linealidad: ¿la transmisión del choque a la producción depende del estado del crédito?

Compara la varianza de la transmisión mensual en los meses con crédito caro (credit_{t−1} > 0) y barato, con un
contraste F de igualdad de varianzas. No impone la forma funcional de la LP.
Salida: output/macros_nl.tex. Uso: uv run python papers/p07-credit/code/analysis/nonlinearity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

PAPER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lp


def transmission(panel: pd.DataFrame) -> pd.Series:
    """Transmisión del choque a la producción en cada mes."""
    b, _ = lp.fit(*lp.design(panel, lp.H_MAIN))
    te = (b["shock"] + b["shock_x_credit"] * panel["credit"].shift(1)) * panel["shock"]
    return te.dropna()


def variance_test(te: pd.Series, credit_l1: pd.Series) -> tuple[float, float]:
    tight = credit_l1.loc[te.index] > 0
    a, b = te[tight], te[~tight]
    ratio = a.var(ddof=1) / b.var(ddof=1)
    return ratio, float(stats.f.sf(ratio, len(a) - 1, len(b) - 1))


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    ratio, p = variance_test(transmission(panel), panel["credit"].shift(1))
    (PAPER / "output" / "macros_nl.tex").write_text(
        "% Generado por code/analysis/nonlinearity.py: no editar a mano.\n"
        f"\\newcommand{{\\nlRatio}}{{{ratio:.2f}}}\n\\newcommand{{\\nlP}}{{{lp.p_text(p)}}}\n", encoding="utf-8")
    print(f"razón de varianzas {ratio:.3f}, p {lp.p_text(p)}")


if __name__ == "__main__":
    main()
