"""F22 (Referee): comprueba cada macro de output/macros.tex contra una celda fijada a mano (archivo:línea:columna) de su fuente.

Independiente de 02_paper_macros.py: no lo importa. Falla si una macro no tiene celda asignada o si alguna celda no coincide.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-08_F22/check_macros.py
"""

import csv
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "output"
T = OUT / "tables"


def cells(path: Path, line: int) -> list[str]:
    row = path.read_text(encoding="utf-8").splitlines()[line - 1]
    return [c.strip() for c in row.replace("\\|", "¦").strip().strip("|").split("|")]


expected: dict[str, str] = {}

# s1r_estimates.md:7-19 → id, término, β̂, ee, g.l., p, IC
specs = {"s1r_lin": "Lin", "s1r_liq": "Liq", "s1r_liq_nov": "LiqNov", "r1r_from1971q3": "RobFrom", "r1r_state_q25": "RobQuart",
         "r1r_state_logistic": "RobLogit", "r1r_lags4": "RobLags"}
n_bc = 0
for ln in range(7, 20):
    sid, term, b, se, dof, p, ci = cells(T / "s1r_estimates.md", ln)
    name = "bLin" if term == "b_lin" else f"b{term[-1]}{specs[sid]}"
    n_bc += term == "b_C"
    lo, hi = ci.strip("[]").split(", ")
    expected |= {f"{name}Est": b, f"{name}Se": se, f"{name}Dof": dof, f"{name}P": p, f"{name}CiLo": lo, f"{name}CiHi": hi}
assert n_bc == 6, n_bc
expected["verdictoVs"] = r"h0\_falla"
assert "`h0_falla`" in (T / "s1r_estimates.md").read_text(encoding="utf-8").splitlines()[20]

# Las estimaciones y ee de la tabla, contra los CSV a precisión completa
rows = {}
for f in ("estimates_py.csv", "estimates_py_robustness.csv"):
    with (OUT / f).open(encoding="utf-8", newline="") as fh:
        rows |= {(r["spec_id"], r["term"]): r for r in csv.DictReader(fh)}
max_round = 0.0
for ln in range(7, 20):
    sid, term, b, se, dof, *_ = cells(T / "s1r_estimates.md", ln)
    r = rows[(sid, term)]
    max_round = max(max_round, abs(float(r["estimate"]) - float(b)), abs(float(r["std_error"]) - float(se)))
    assert f"{float(r['estimate']):.3f}" == b and f"{float(r['std_error']):.3f}" == se and r["dof"] == dof, (sid, term)

# s1r_shock_diagnostics.md:7-8
for ln, tag in ((7, "Full"), (8, "NoV")):
    c = cells(T / "s1r_shock_diagnostics.md", ln)
    a, bb = c[11].strip("()").split(", ")
    expected |= dict(zip([f"Diag{tag}{k}" for k in ("N", "DoneRestr", "DoneHolg", "DtwoRestr", "DtwoHolg", "DthreeF", "DthreeP", "LB",
                                                      "LBP", "PredF")], c[1:11]))
    expected |= {f"Diag{tag}PredDfA": a, f"Diag{tag}PredDfB": bb, f"Diag{tag}PredP": c[12], f"NShock{tag}": c[1]}

# f13_checks.md:9 (β_ref), :31/:47 (c = 1), :68/:69 (MDE)
c = cells(T / "f13_checks.md", 9)
pz, pzse = re.fullmatch(r"(\S+) \((\S+)\)", c[2]).groups()
expected |= {"sdEps": c[1], "piZero": pz, "piZeroSe": pzse, "betaRef": c[3], "betaRefSd": c[4]}
for ln, n in ((31, "Homo"), (47, "Het")):
    c = cells(T / "f13_checks.md", ln)
    assert c[1:3] == ["1", "1"]
    expected |= {f"Pw{n}HzeroFalla": c[5], f"Pw{n}Confirma": c[6], f"Pw{n}NoConc": c[8], f"Pw{n}PowHzero": c[9],
                 f"Pw{n}PowHone": c[10]}
    if n == "Homo":
        expected |= {"mdeEpsUnit": c[3], "mdeFfrUnit": c[4]}
for ln, n in ((68, "Homo"), (69, "Het")):
    c = cells(T / "f13_checks.md", ln)
    expected |= {f"Mde{n}C": c[1], f"Mde{n}Eps": c[2], f"Mde{n}Ffr": c[3], f"Mde{n}RivalMax": c[4]}

# f9_power.md:719, 791 (β = 0, aum, RR, V3s)
for ln, n in ((719, "Homo"), (791, "Het")):
    c = cells(T / "f9_power.md", ln)
    assert c[:6] == ["aum", "RR", {"Homo": "homo", "Het": "het_eps"}[n], "1", "0", "V3s"], c
    expected[f"Size{n}"] = c[7]

# f9_power.md:44-45, 52-53, 60-61 (§1b, aum, NW5+HC3, T completo; añadido en F28): mínimo y máximo de la columna NW5+HC3
cov = []
for ln in (44, 45, 52, 53, 60, 61):
    c = cells(T / "f9_power.md", ln)
    assert c[0] == "aum" and c[3].startswith("T = "), c
    cov += re.match(r"(\d\.\d+)–(\d\.\d+)", c[5]).groups()
expected |= {"CovAumNwHcLo": min(cov), "CovAumNwHcHi": max(cov)}

got = {k: re.sub(r"^\\ensuremath\{(.*)\}$", r"\1", v)
       for k, v in re.findall(r"^\\newcommand\{\\(\w+)\}\{(.*)\}$", (OUT / "macros.tex").read_text(encoding="utf-8"), re.MULTILINE)}
extra, missing = sorted(set(got) - set(expected)), sorted(set(expected) - set(got))
diff = {k: (got[k], expected[k]) for k in set(got) & set(expected) if got[k] != expected[k]}
print(f"macros: {len(got)}; esperadas: {len(expected)}; sin fuente: {extra}; ausentes: {missing}; distintas: {diff}")
print(f"max |CSV - tabla| en estimate y std_error (redondeo a 3 decimales): {max_round:.2e}")
assert not (extra or missing or diff)
print("OK")
