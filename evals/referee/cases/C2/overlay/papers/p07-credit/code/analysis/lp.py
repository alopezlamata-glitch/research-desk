"""LP de la inversión ante un choque monetario con interacción por el estado del crédito (SPEC, H1).

y_{t,h} = loginv_{t+h} − loginv_{t−1}
        = a_h + b_h shock_t + d_h credit_{t−1} + c_h shock_t · credit_{t−1} + Γ_h' x_t + u_{t,h},   h = 0..4

x: crecimiento de la inversión, del PIB e inflación con un retardo, y fci del trimestre. Errores estándar de Newey-West
(Bartlett, h + 1 retardos: el solapamiento de y_{t,h}) sobre residuos HC3, u_t / (1 − h_tt), por el T pequeño.
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

H = 4
CONTROLS = ["dinv_l1", "dgdp_l1", "infl_l1", "fci"]
TERMS = ["shock", "shock_x_credit"]


def design(panel: pd.DataFrame, h: int) -> tuple[np.ndarray, pd.DataFrame]:
    """(y, X) del horizonte h, sin las filas con retardos o adelantos que no existen."""
    df = pd.DataFrame({"y": panel["loginv"].shift(-h) - panel["loginv"].shift(1), "const": 1.0,
                       "shock": panel["shock"], "credit_l1": panel["credit"].shift(1)})
    df["shock_x_credit"] = df["shock"] * df["credit_l1"]
    df["fci"] = panel["fci"]
    for c in ("dinv", "dgdp", "infl"):
        df[f"{c}_l1"] = panel[c].shift(1)
    df = df[["y", "const", *TERMS, "credit_l1", *CONTROLS]].dropna()
    return df["y"].to_numpy(), df.drop(columns="y")


def newey_west(X: np.ndarray, u: np.ndarray, lags: int) -> np.ndarray:
    """Varianza sándwich con pesos de Bartlett 1 − l/(lags + 1)."""
    bread = np.linalg.inv(X.T @ X)
    s = X * u[:, None]
    meat = s.T @ s
    for lag in range(1, lags + 1):
        g = s[lag:].T @ s[:-lag]
        meat += (1 - lag / (lags + 1)) * (g + g.T)
    return bread @ meat @ bread


def nw_lags(h: int) -> int:
    return h + 1


def fit(y: np.ndarray, X: pd.DataFrame, lags: int) -> tuple[pd.Series, pd.Series]:
    Xa = X.to_numpy()
    bread = np.linalg.inv(Xa.T @ Xa)
    beta = bread @ (Xa.T @ y)
    u = y - Xa @ beta
    u = u / (1 - np.einsum("ij,jk,ik->i", Xa, bread, Xa))  # residuos HC3
    se = np.sqrt(np.diag(newey_west(Xa, u, lags)))
    return pd.Series(beta, X.columns), pd.Series(se, X.columns)


def estimate(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for h in range(H + 1):
        y, X = design(panel, h)
        b, se = fit(y, X, nw_lags(h))
        rows += [{"spec_id": f"lp_h{h}", "term": t, "estimate": b[t], "std_error": se[t], "nobs": len(y)}
                 for t in TERMS]
    return pd.DataFrame(rows)


def macro_name(term: str, h: int) -> str:
    words = {"shock": "Shock", "shock_x_credit": "Inter"}
    return words[term] + "H" + ["zero", "one", "two", "three", "four"][h]


def write_macros(est: pd.DataFrame, path: Path) -> None:
    z = stats.norm.ppf(0.975)
    lines = ["% Generado por code/analysis/lp.py: no editar a mano."]
    for r in est.itertuples():
        h = int(r.spec_id.removeprefix("lp_h"))
        name = macro_name(r.term, h)
        p = stats.norm.cdf(r.estimate / r.std_error)  # unilateral, H1: coeficiente < 0
        lines += [f"\\newcommand{{\\b{name}}}{{{r.estimate:.2f}}}",
                  f"\\newcommand{{\\se{name}}}{{{r.std_error:.2f}}}",
                  f"\\newcommand{{\\lo{name}}}{{{r.estimate - z * r.std_error:.2f}}}",
                  f"\\newcommand{{\\hi{name}}}{{{r.estimate + z * r.std_error:.2f}}}",
                  f"\\newcommand{{\\p{name}}}{{{p:.3f}}}"]
        if r.term == "shock":
            lines.append(f"\\newcommand{{\\nobs{name.removeprefix('Shock')}}}{{{r.nobs}}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel = pd.read_parquet(PAPER / "data" / "clean" / "panel.parquet")
    est = estimate(panel)
    for h in range(H + 1):
        research.log_spec(PAPER, f"lp_h{h}", "code/analysis/lp.py",
                          f"LP h={h}: choque × crédito_(t−1), controles x, NW({nw_lags(h)})")
    out = PAPER / "output"
    est[["spec_id", "term", "estimate", "std_error"]].to_csv(out / "estimates_py.csv", index=False,
                                                             float_format="%.10g")
    write_macros(est, out / "macros.tex")
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
