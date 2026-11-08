r"""F21: escribe `output/macros.tex`, las cifras del paper A, a partir de tablas y CSV ya auditados. No estima nada.

Fuentes (todas en `output/`):
- `estimates_py.csv` y `estimates_py_robustness.csv`: estimación, ee y g.l. (se escriben con 3 decimales, como `s1r_estimates.md`).
- `tables/s1r_estimates.md`: p unilateral (β < 0) e IC al 95 % tal como están impresos (no se recalculan) y el veredicto.
- `tables/s1r_shock_diagnostics.md`: diagnósticos de los choques (completa y sin Volcker).
- `tables/f13_checks.md`: β_ref, π(h = 0), MDE y probabilidades de desenlace ex ante (V3s, c = 1; MDE con P(confirma) = 0,8).
- `tables/f9_power.md` §3: tamaño con β = 0 (P(confirma) del árbol V3s).

Nombres (LaTeX no admite dígitos en un nombre de macro). Cada cifra es `\<prefijo><Campo>`:
- Estimaciones: prefijo `bC`, `bU` o `bLin` + especificación (`Liq`, `LiqNov`, `RobFrom` = r1r_from1971q3, `RobQuart` =
  r1r_state_q25, `RobLogit` = r1r_state_logistic, `RobLags` = r1r_lags4) + campo `Est`, `Se`, `Dof`, `P` (p de β < 0), `CiLo`, `CiHi`.
  Ej.: `\bCLiqEst`, `\bCRobLagsCiHi`, `\bLinP`.
- `\NShockFull`, `\NShockNoV`: N de las muestras de choques (146 / 133), de las diagnósticas.
- Diagnósticos: `\Diag<Full|NoV><Campo>`: `N`, `DoneRestr`, `DoneHolg`, `DtwoRestr`, `DtwoHolg` (Σ|ε|), `DthreeF`, `DthreeP`,
  `LB`, `LBP`, `PredF`, `PredDfA`, `PredDfB`, `PredP`.
- Referencia: `\betaRef`, `\piZero`, `\piZeroSe`, `\sdEps`, `\betaRefSd` (efecto de 1 sd de ε), `\mdeEpsUnit` / `\mdeFfrUnit`
  (c = 1: pp de ȳ por pp de ε / de fed funds).
- Ex ante, por ruido `Homo` / `Het`: `\Pw<Ruido><Campo>` con `H0Falla`, `Confirma`, `NoConc`, `PowH0`, `PowHone` (c = 1);
  `\Mde<Ruido><Campo>` con `C`, `Eps`, `Ffr`, `RivalMax` (P(confirma) = 0,8); `\Size<Ruido>` (β = 0).
- `\verdictoVs`: veredicto de `s1r_lp.decide` (V3s).
"""

import csv
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "output"
SPECS = {"s1r_liq": "Liq", "s1r_liq_nov": "LiqNov", "r1r_from1971q3": "RobFrom", "r1r_state_q25": "RobQuart",
         "r1r_state_logistic": "RobLogit", "r1r_lags4": "RobLags"}
NOISE = {"homo": "Homo", "het_eps": "Het"}


def md_rows(name: str) -> list[list[str]]:
    """Filas de las tablas markdown de un archivo, como listas de celdas (sin cabecera ni separadores)."""
    rows = []
    for line in (OUT / "tables" / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not set(line) <= set("|- "):
            rows.append([c.strip().replace("\\|", "|") for c in line.strip("|").split("|")])
    return rows


def csv_rows(name: str) -> dict[tuple[str, str], dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as f:
        return {(r["spec_id"], r["term"]): r for r in csv.DictReader(f)}


def build() -> dict[str, str]:
    m: dict[str, str] = {}
    csv_est = csv_rows("estimates_py.csv") | csv_rows("estimates_py_robustness.csv")

    est = {(r[0], r[1]): r for r in md_rows("s1r_estimates.md") if r[0] != "id"}
    ids = {("s1r_lin", "b_lin"): "bLin"} | {(s, f"b_{t}"): f"b{t}{n}" for s, n in SPECS.items() for t in "CU"}
    for key, name in ids.items():
        _, _, beta, ee, dof, p, ci = est[key]
        src = csv_est[key]
        assert f"{float(src['estimate']):.3f}" == beta and f"{float(src['std_error']):.3f}" == ee and src["dof"] == dof, key
        lo, hi = re.fullmatch(r"\[(.+), (.+)\]", ci).groups()
        m |= {f"{name}Est": beta, f"{name}Se": ee, f"{name}Dof": dof, f"{name}P": p, f"{name}CiLo": lo, f"{name}CiHi": hi}

    verdict = re.search(r"\*\*Veredicto V3s\*\* \(`s1r_lp.decide`\): `(\w+)`",
                        (OUT / "tables" / "s1r_estimates.md").read_text(encoding="utf-8")).group(1)
    m["verdictoVs"] = verdict.replace("_", r"\_")

    diag = {r[0]: r for r in md_rows("s1r_shock_diagnostics.md") if r[0] in ("completa", "sin Volcker")}
    fields = ["N", "DoneRestr", "DoneHolg", "DtwoRestr", "DtwoHolg", "DthreeF", "DthreeP", "LB", "LBP", "PredF", "PredDf", "PredP"]
    for muestra, tag in (("completa", "Full"), ("sin Volcker", "NoV")):
        for f, v in zip(fields, diag[muestra][1:]):
            if f == "PredDf":
                a, b = re.fullmatch(r"\((\d+), (\d+)\)", v).groups()
                m[f"Diag{tag}PredDfA"], m[f"Diag{tag}PredDfB"] = a, b
            else:
                m[f"Diag{tag}{f}"] = v
        m[f"NShock{tag}"] = diag[muestra][1]

    f13 = md_rows("f13_checks.md")
    ref = next(r for r in f13 if r[0] == "suma" and r[5] == "homo")  # β_ref no depende del ruido
    m["sdEps"], m["betaRef"], m["betaRefSd"] = ref[1], ref[3], ref[4]
    m["piZero"], m["piZeroSe"] = re.fullmatch(r"(\S+) \((\S+)\)", ref[2]).groups()
    for r in f13:
        if len(r) == 11 and r[0] in NOISE and r[1] == "1" and r[2] == "1":  # §2: H1 cierta (m = 1), c = 1
            n = NOISE[r[0]]
            m |= {f"Pw{n}H0Falla": r[5], f"Pw{n}Confirma": r[6], f"Pw{n}NoConc": r[8], f"Pw{n}PowH0": r[9], f"Pw{n}PowHone": r[10]}
            if r[0] == "homo":  # el MDE por unidad de c no depende del ruido
                m["mdeEpsUnit"], m["mdeFfrUnit"] = r[3], r[4]
        elif len(r) == 5 and r[0] in NOISE:  # §2b
            n = NOISE[r[0]]
            m |= {f"Mde{n}C": r[1], f"Mde{n}Eps": r[2], f"Mde{n}Ffr": r[3], f"Mde{n}RivalMax": r[4]}

    for r in md_rows("f9_power.md"):  # §3: aum, RR, V3s con c = 0 (β = 0)
        if len(r) == 11 and r[:6] == ["aum", "RR", r[2], "1", "0", "V3s"] and r[2] in NOISE:
            m[f"Size{NOISE[r[2]]}"] = r[7]
    return m


def render(m: dict[str, str]) -> str:
    def tex(v: str) -> str:
        return rf"\ensuremath{{{v}}}" if v.startswith("-") else v

    head = ("% Generado por code/analysis/02_paper_macros.py. No editar a mano. Fuentes y nombres: ver ese script.\n")
    return head + "".join(f"\\newcommand{{\\{k}}}{{{tex(v)}}}\n" for k, v in m.items())


def main() -> None:
    (OUT / "macros.tex").write_text(render(build()), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
