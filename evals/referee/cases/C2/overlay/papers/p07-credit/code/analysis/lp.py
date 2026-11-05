"""LP de la producción industrial ante un choque monetario, con interacción por el estado del crédito (SPEC, H1).

y_{t,h} = lip_{t+h} − lip_{t−1}
        = a_h + b_h shock_t + c_h shock_t · credit_{t−1} + Σ_{j=1..LAGS} Γ_{h,j}' x_{t−j} + u_{t,h}

x = (dip, dcpi, dur, spread, shock), más fci_t (condiciones financieras del mes) como control. El nivel del estado
entra por spread_{t−1} (credit es spread centrado). Con los retardos del propio choque y de las demás variables («lag augmentation»),
la inferencia sobre los coeficientes del choque no necesita corregir la autocorrelación del solape de y_{t,h}: errores
heterocedásticos-robustos con residuos HC3, u_t / (1 − h_tt), por las colas gruesas del choque (output/MC_REPORT.md).
Salida: output/estimates_py.csv y output/macros.tex.
Uso: uv run python papers/p07-credit/code/analysis/lp.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PAPER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAPER.parents[1] / "tools"))
import research

HORIZONS = (0, 6, 12, 18, 24)
H_MAIN = 12
LAGS = 6
LAGGED = ["dip", "dcpi", "dur", "spread", "shock"]
TERMS = ["shock", "shock_x_credit"]
CI_LEVEL = 95
WORDS = {0: "zero", 6: "six", 12: "twelve", 18: "eighteen", 24: "twentyfour"}


def design(panel: pd.DataFrame, h: int) -> tuple[np.ndarray, pd.DataFrame]:
    """(y, X) del horizonte h, sin las filas con retardos o adelantos que no existen."""
    df = pd.DataFrame({"y": panel["lip"].shift(-h) - panel["lip"].shift(1), "const": 1.0,
                       "shock": panel["shock"]})
    df["shock_x_credit"] = panel["shock"] * panel["credit"].shift(1)
    df["fci"] = panel["fci"]
    for v in LAGGED:
        for j in range(1, LAGS + 1):
            df[f"{v}_l{j}"] = panel[v].shift(j)
    df = df.dropna()
    return df["y"].to_numpy(), df.drop(columns="y")


def fit(y: np.ndarray, X: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """MCO con varianza sándwich sobre residuos HC3."""
    Xa = X.to_numpy()
    bread = np.linalg.inv(Xa.T @ Xa)
    beta = bread @ (Xa.T @ y)
    u = y - Xa @ beta
    u = u / (1 - np.einsum("ij,jk,ik->i", Xa, bread, Xa))  # residuos HC3
    s = Xa * u[:, None]
    se = np.sqrt(np.diag(bread @ (s.T @ s) @ bread))
    return pd.Series(beta, X.columns), pd.Series(se, X.columns)


def estimate(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for h in HORIZONS:
        y, X = design(panel, h)
        b, se = fit(y, X)
        rows += [{"spec_id": f"lp_h{h}", "term": t, "estimate": b[t], "std_error": se[t], "nobs": len(y)}
                 for t in TERMS]
    return pd.DataFrame(rows)


def p_text(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def write_macros(est: pd.DataFrame, path: Path) -> None:
    z = stats.norm.ppf(0.5 + CI_LEVEL / 200)
    lines = ["% Generado por code/analysis/lp.py: no editar a mano.", f"\\newcommand{{\\ciLevel}}{{{CI_LEVEL}}}",
             f"\\newcommand{{\\lags}}{{{LAGS}}}"]
    for r in est.itertuples():
        h = int(r.spec_id.removeprefix("lp_h"))
        name = {"shock": "Shock", "shock_x_credit": "Inter"}[r.term] + "H" + WORDS[h]
        p = stats.norm.cdf(r.estimate / r.std_error)  # unilateral, H1: coeficiente < 0
        lines += [f"\\newcommand{{\\b{name}}}{{{r.estimate:.2f}}}",
                  f"\\newcommand{{\\se{name}}}{{{r.std_error:.2f}}}",
                  f"\\newcommand{{\\lo{name}}}{{{r.estimate - z * r.std_error:.2f}}}",
                  f"\\newcommand{{\\hi{name}}}{{{r.estimate + z * r.std_error:.2f}}}",
                  f"\\newcommand{{\\p{name}}}{{{p_text(p)}}}"]
        if r.term == "shock":
            lines.append(f"\\newcommand{{\\nobsH{WORDS[h]}}}{{{r.nobs}}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    est = estimate(panel)
    for h in HORIZONS:
        research.log_spec(PAPER, f"lp_h{h}", "code/analysis/lp.py",
                          f"LP h={h}: choque × crédito_(t−1), {LAGS} retardos de x, HC3")
    out = PAPER / "output"
    est[["spec_id", "term", "estimate", "std_error"]].to_csv(out / "estimates_py.csv", index=False,
                                                             float_format="%.10g")
    write_macros(est, out / "macros.tex")
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
