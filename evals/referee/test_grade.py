import json

import grade
import pytest

CASE = {"id": "CX", "verdicts": ["RECHAZADO"], "locations": [
    {"file": "papers/p07-credit/code/analysis/lp.py", "lines": [40, 42], "marker": "x"},
    {"file": "papers/p07-credit/output/estimates_py.csv", "lines": [1, 1], "marker": "spec_id", "any_line": True},
]}
CONTROL = {"id": "C0", "verdicts": ["APROBADO", "APROBADO CON CAMBIOS"], "locations": []}
KNOWN = [{"file": "papers/p07-credit/draft/main.tex", "lines": [10, 12]}]
OK_CMDS = ["uv run python ../../../tools/integrity.py", "uv run pytest"]
REPL = ["papers/p07-credit/audits/replication_2026-11-05/lp_check.R"]


def report(verdict="RECHAZADO", findings=(), header=True):
    head = (f"---\nverdict: {verdict}\nobject: LP h=4\ndate: 2026-11-05\ncommit: abc1234\nreviewer: referee\n"
            "session: fresh\n---\n") if header else ""
    body = "".join(f"### {title}\nTexto.\nEvidencia: {ev}\n\n" for title, ev in findings)
    return f"{head}## Resumen\nAuditoría.\n\n## Hallazgos\n{body}## Replicación\nOK.\n"


def g(text, case=CASE, known=KNOWN, cmds=OK_CMDS, repl=REPL):
    return grade.grade(text, case, known, cmds, repl)


@pytest.mark.parametrize("evidence", [
    "papers/p07-credit/code/analysis/lp.py:41",
    "`../code/analysis/lp.py:44-50`",  # rango que se solapa con 40–42 ± 3
    r"C:\tmp\referee-eval\r1\papers\p07-credit\code\analysis\lp.py:37",
    "`uv run python lp.py` y lp.py:L39",
])
def test_detects_major_finding_with_evidence_in_range(evidence):
    out = g(report(findings=[("Interacción mal construida — mayor", evidence)]))
    assert out["detected"] and out["verdict_ok"] and out["protocol_ok"]
    assert out["false_positives"] is None


@pytest.mark.parametrize("title,evidence", [
    ("Interacción mal construida — mayor", "papers/p07-credit/code/analysis/lp.py:60"),  # fuera de ±3
    ("Interacción mal construida — mayor", "papers/p07-credit/code/analysis/lp.py"),  # sin línea, no any_line
    ("Interacción mal construida — mayor", "papers/p07-credit/code/replication_r/lp.R:41"),  # otro archivo
    ("Interacción mal construida — menor", "papers/p07-credit/code/analysis/lp.py:41"),  # menor
])
def test_does_not_detect(title, evidence):
    assert g(report(findings=[(title, evidence)]))["detected"] is False


def test_any_line_location_matches_file_only():
    assert g(report(findings=[("Cifras — mayor", "`output/estimates_py.csv`")]))["detected"]


def test_major_by_section_heading():
    text = report().replace("## Hallazgos\n", "## Problemas mayores\n### Interacción\nEvidencia: lp.py:41\n\n")
    assert g(text)["detected"]


def test_verdict_must_be_accepted():
    out = g(report(verdict="APROBADO CON CAMBIOS", findings=[("X — mayor", "lp.py:41")]))
    assert out["detected"] and not out["verdict_ok"]


def test_false_positives_only_in_control_and_known_issues_do_not_count():
    findings = [("Signo — mayor", "papers/p07-credit/draft/main.tex:11"),  # conocido
                ("Datos — mayor", "papers/p07-credit/data/clean/DICTIONARY.md:3"),
                ("Sin evidencia citable — mayor", "`uv run pytest`"),
                ("Estilo — menor", "papers/p07-credit/draft/main.tex:30")]
    out = g(report(verdict="APROBADO CON CAMBIOS", findings=findings), case=CONTROL)
    assert out["false_positives"] == 2 and out["verdict_ok"] and out["detected"] is None


def test_broken_format_and_missing_report():
    out = g(report(header=False, findings=[("X — mayor", "lp.py:41")]))
    assert out["verdict"] is None and not out["verdict_ok"] and not out["format_ok"] and not out["protocol_ok"]
    assert out["detected"]  # la detección no depende de la cabecera
    missing = g(None)
    assert missing["detected"] is False and not missing["format_ok"]


def test_protocol_requires_full_integrity_pytest_and_replication_script():
    text = report(findings=[("X — mayor", "lp.py:41")])
    assert not g(text, cmds=["uv run python tools/integrity.py --only referee", "uv run pytest"])["ran_integrity"]
    assert not g(text, cmds=["uv run python tools/integrity.py"])["protocol_ok"]
    assert not g(text, repl=["papers/p07-credit/audits/replication_x/notes.md"])["replication"]


def test_bash_commands_from_transcript(tmp_path):
    t = tmp_path / "s.jsonl"
    lines = [{"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "uv run pytest"}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": "x"}}]}},
             {"type": "user", "message": {"content": "hola"}}]
    t.write_text("\n".join(map(json.dumps, lines)) + "\n{roto", encoding="utf-8")
    assert grade.bash_commands(t) == ["uv run pytest"]
    assert grade.bash_commands(tmp_path / "no.jsonl") == []


def test_evidence_continues_on_following_lines_until_blank():
    text = ("### El test es circular (mayor)\n"
            "Texto.\n"
            "Evidencia: `uv run python replicate.py` (bloque y\n"
            "placebo); papers/p07-credit/code/analysis/nonlinearity.py:23-32; draft/main.tex:57-60\n"
            "\n"
            "No es evidencia: papers/x.py:1\n")
    (f,) = grade.findings(text)
    assert grade.hits(f, [{"file": "papers/p07-credit/code/analysis/nonlinearity.py", "lines": [22, 25]}])
    assert not grade.hits(f, [{"file": "papers/x.py", "lines": [1, 1]}])  # tras la línea en blanco ya no cuenta
