"""Tests de F21: cada macro de `output/macros.tex` coincide con su fuente auditada, sin redondeo ni transformación de más."""

import importlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
mod = importlib.import_module("02_paper_macros")
OUT = mod.OUT


def parse(tex: str) -> dict[str, str]:
    out = {}
    for name, body in re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", tex, flags=re.MULTILINE):
        out[name] = re.sub(r"\\ensuremath\{(.*)\}", r"\1", body)
    return out


def test_macro_names_are_latex_control_words():
    text = (OUT / "macros.tex").read_text(encoding="utf-8")
    declared = re.findall(r"^\\newcommand\{\\([^}]*)\}", text, flags=re.MULTILINE)
    assert declared and all(re.fullmatch(r"[A-Za-z]+", n) for n in declared)


def test_aum_coverage_range_matches_f9_report():
    m = parse((OUT / "macros.tex").read_text(encoding="utf-8"))
    assert (m["CovAumNwHcLo"], m["CovAumNwHcHi"]) == ("0.948", "0.990")  # F9_MC_REPORT.md:30


def test_macros_file_is_reproducible():
    before = (OUT / "macros.tex").read_text(encoding="utf-8")
    mod.main()
    assert (OUT / "macros.tex").read_text(encoding="utf-8") == before
    assert before == mod.render(mod.build())


def test_b_estimates_match_csv_and_table():
    m = parse((OUT / "macros.tex").read_text(encoding="utf-8"))
    csv = mod.csv_rows("estimates_py.csv") | mod.csv_rows("estimates_py_robustness.csv")
    md = {(r[0], r[1]): r for r in mod.md_rows("s1r_estimates.md") if r[0] != "id"}
    keys = {("s1r_lin", "b_lin"): "bLin"} | {(s, f"b_{t}"): f"b{t}{n}" for s, n in mod.SPECS.items() for t in "CU"}
    assert sum(k[1] == "b_C" for k in keys) == 6  # las 6 filas de b_C
    for key, name in keys.items():
        assert float(m[f"{name}Est"]) == round(float(csv[key]["estimate"]), 3)
        assert float(m[f"{name}Se"]) == round(float(csv[key]["std_error"]), 3)
        assert m[f"{name}Dof"] == csv[key]["dof"]
        _, _, beta, ee, dof, p, ci = md[key]
        assert (m[f"{name}Est"], m[f"{name}Se"], m[f"{name}Dof"], m[f"{name}P"]) == (beta, ee, dof, p)
        assert f"[{m[f'{name}CiLo']}, {m[f'{name}CiHi']}]" == ci


def test_verdict_diagnostics_and_ex_ante_figures():
    m = parse((OUT / "macros.tex").read_text(encoding="utf-8"))
    assert m["verdictoVs"].replace("\\", "") == "h0_falla"
    diag = {r[0]: r for r in mod.md_rows("s1r_shock_diagnostics.md")}
    assert (m["DiagFullN"], m["DiagFullLBP"], m["DiagNoVLBP"], m["DiagNoVPredDfB"]) == (diag["completa"][1], diag["completa"][9],
                                                                                    diag["sin Volcker"][9], "120")
    assert (m["betaRef"], m["piZero"], m["piZeroSe"]) == ("-1.820", "0.949", "0.248")
    assert (m["PwHomoConfirma"], m["PwHetConfirma"], m["PwHomoPowHzero"]) == ("0.037", "0.059", "0.176")
    assert (m["MdeHomoC"], m["MdeHomoEps"], m["MdeHetFfr"], m["MdeHetRivalMax"]) == ("5.5", "10.01", "9.97", "0.033")
    assert (m["SizeHomo"], m["SizeHet"]) == ("0.004", "0.011")
