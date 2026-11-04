"""Tests de tools/integrity.py: cada comprobación detecta lo que debe y no da falsos positivos."""

from pathlib import Path

import integrity as ig
import pytest


def write(root: Path, rel: str, text: str) -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return rel


def run(check, root, *rels):
    return check(root, list(rels))


# ---------------------------------------------------------------- secrets
def test_secrets_detects_keys_and_real_env_value(tmp_path, monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "zz9plural9alpha9zz9plural9alpha9")
    # Las claves falsas se construyen por partes para que este archivo no dispare la propia comprobación.
    a = write(tmp_path, "a.py", 'API_KEY = "' + "0123456789abcdef" * 2 + '"\n')
    b = write(tmp_path, "b.md", "token " + "ghp" + "_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456\n")
    c = write(tmp_path, "c.txt", "la clave es zz9plural9alpha9zz9plural9alpha9\n")
    assert {v.path for v in run(ig.check_secrets, tmp_path, a, b, c)} == {a, b, c}


def test_secrets_ignores_env_lookups_and_hashes(tmp_path, monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    ok = write(tmp_path, "ok.py", 'key = os.environ["FRED_API_KEY"]\nsha = 64*"a"\n')
    manifest = write(tmp_path, "MANIFEST.csv", "f,url,2026,"
                     "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855,v\n")
    assert run(ig.check_secrets, tmp_path, ok, manifest) == []


# ---------------------------------------------------------------- hygiene
def test_hygiene_flags_backfill_interpolate_and_placeholders(tmp_path):
    rel = write(tmp_path, "papers/p/code/data/build.py",
                "s = s.bfill()\nt = t.interpolate()\nu = u.fillna(method='backfill')\nx = 'TODO_SERIE_REAL'\n")
    assert [v.line for v in run(ig.check_hygiene, tmp_path, rel)] == [1, 2, 3, 4]


def test_hygiene_waiver_and_scope(tmp_path):
    rel = write(tmp_path, "datalake/fetch/x.py", "s = s.interpolate()  # hygiene-ok: solo para la figura\n")
    outside = write(tmp_path, "tools/x.py", "s = s.bfill()\n")
    assert run(ig.check_hygiene, tmp_path, rel, outside) == []


def test_hygiene_waiver_needs_a_reason(tmp_path):
    rel = write(tmp_path, "datalake/fetch/x.py", "s = s.interpolate()  # hygiene-ok:\n")
    assert len(run(ig.check_hygiene, tmp_path, rel)) == 1


# ---------------------------------------------------------------- citations
BIB = """
@article{Good2020, title = {A {Nested} Title}, note = {VERIFICADA. doi ok}}
@article{Bad2021, title = {X}, note = {DISCREPANCIA: año}}
@article{Unk2022, title = {Y}, note = {NO VERIFICADA}}
"""


def test_parse_bib_handles_nested_braces():
    bib = ig.parse_bib(BIB)
    assert bib["Good2020"]["title"] == "A {Nested} Title"
    assert bib["Good2020"]["note"].startswith("VERIFICADA")


def test_citations_only_verified_entries_pass(tmp_path):
    write(tmp_path, "papers/p/paper/references.bib", BIB)
    tex = write(tmp_path, "papers/p/paper/main.tex",
                "\\citet{Good2020} and \\citep[p.~3][]{Bad2021, Unk2022}\n"
                "% \\cite{Commented2020}\n\\cite{Missing2019}\n")
    msgs = [v.msg for v in run(ig.check_citations, tmp_path, tex)]
    assert len(msgs) == 3
    assert any("Bad2021" in m for m in msgs) and any("Unk2022" in m for m in msgs)
    assert any("Missing2019" in m and "no está" in m for m in msgs)


# ---------------------------------------------------------------- numbers
def test_numbers_flags_typed_results_only_in_body(tmp_path):
    tex = write(tmp_path, "papers/p/paper/main.tex",
                "\\usepackage[margin=2.5cm]{geometry}\n\\begin{document}\n"
                "The elasticity is 0.42 and falls by 12\\%.\n"
                "See Section~\\ref{sec:2.1} and \\cite{A2020}; \\input{../output/tab1.tex}\n"
                "We use $\\theta = 0.693$. % num-ok calibración citada\n"
                "The estimate is \\hatbeta{} in 2020.\n")
    found = [(v.line, v.msg.split("'")[1]) for v in run(ig.check_numbers, tmp_path, tex)]
    assert found == [(3, "0.42"), (3, "12\\%")]


# ---------------------------------------------------------------- parity
HEADER = "spec_id,term,estimate,std_error\n"


def test_parity_requires_r_and_matches_within_tolerance(tmp_path):
    out = tmp_path / "papers/p/output"
    out.mkdir(parents=True)
    (out / "estimates_py.csv").write_text(HEADER + "H1,beta,1.0000000,0.5\nH1,gamma,2.0,0.1\n")
    assert "falta estimates_r" in run(ig.check_parity, tmp_path)[0].msg
    (out / "estimates_r.csv").write_text(HEADER + "H1,beta,1.0000004,0.5\nH1,gamma,2.1,0.1\n")
    msgs = [v.msg for v in run(ig.check_parity, tmp_path)]
    assert len(msgs) == 1 and "gamma" in msgs[0]


# ---------------------------------------------------------------- speclog
def test_speclog_prereg_and_exploratory(tmp_path):
    paper = tmp_path / "papers/p"
    (paper / "output").mkdir(parents=True)
    (paper / "SPEC.md").write_text("## H\n```prereg\nH1  # principal\nH2\n```\n")
    (paper / "output/estimates_py.csv").write_text(HEADER + "H1,b,1,1\nX9,b,1,1\nH3,b,1,1\n")
    cols = ",".join(ig.SPECLOG_COLUMNS)
    (paper / "output/spec_log.csv").write_text(
        cols + "\n"
        "t,c,s.py,H1,True,False,principal\n"
        "t,c,s.py,X9,False,True,robustez\n"
        "t,c,s.py,H2,False,False,mal marcada\n")
    msgs = [v.msg for v in run(ig.check_speclog, tmp_path)]
    assert any("'H3' estimada pero no registrada" in m for m in msgs)
    assert any("'H2': preregistered=False no coincide" in m for m in msgs)
    assert len(msgs) == 2


def test_prereg_ids_ignores_comments_and_blank_lines():
    assert ig.prereg_ids("```prereg\nH1 # a\n\n# solo comentario\nH2\n```") == {"H1", "H2"}


# ---------------------------------------------------------------- referee
GOOD_REPORT = """---
verdict: APROBADO CON CAMBIOS
object: LP de la tarea D4
date: 2026-11-05
commit: 793f40d
reviewer: referee
session: fresh
---
## Hallazgos
### Errores estándar sin HAC
Evidencia: `uv run python code/analysis/04_lp.py` y code/analysis/04_lp.py:57
"""


@pytest.mark.parametrize("bad, expected", [
    (GOOD_REPORT.replace("APROBADO CON CAMBIOS", "OK"), "verdict inválido"),
    (GOOD_REPORT.replace("session: fresh", "session: same"), "session: fresh"),
    (GOOD_REPORT.replace("commit: 793f40d", "commit: HEAD"), "commit"),
    (GOOD_REPORT.replace("Evidencia: `uv run python code/analysis/04_lp.py` y code/analysis/04_lp.py:57",
                         "Me parece mal."), "sin 'Evidencia:'"),
    ("Informe sin cabecera", "cabecera YAML"),
])
def test_referee_report_format(tmp_path, bad, expected):
    good = write(tmp_path, "papers/p/audits/2026-11-05_ok.md", GOOD_REPORT)
    assert run(ig.check_referee, tmp_path, good) == []
    rel = write(tmp_path, "papers/p/audits/2026-11-05_bad.md", bad)
    assert any(expected in v.msg for v in run(ig.check_referee, tmp_path, rel))


# ---------------------------------------------------------------- lessons
def test_lessons_require_status_and_validator(tmp_path):
    rel = write(tmp_path, "kb/lessons/x.md",
                "# L\n\n## 2026-11-04 · a\nEstado: candidata\ntexto\n\n"
                "## 2026-11-04 · b\nEstado: validada\n\n"
                "## 2026-11-04 · c\nsin estado\n")
    assert [v.line for v in run(ig.check_lessons, tmp_path, rel)] == [7, 10]


# ---------------------------------------------------------------- repositorio real
def test_repository_passes_all_checks():
    violations = ig.run()
    assert violations == [], "\n" + "\n".join(map(str, violations))
