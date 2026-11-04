import pytest

import integrity as ig
import research as rs


@pytest.fixture
def paper(tmp_path):
    (tmp_path / "SPEC.md").write_text("```prereg\nH1\n```\n", encoding="utf-8")
    return tmp_path


def test_log_spec_marks_prereg_and_refuses_undeclared(paper):
    rs.log_spec(paper, "H1", "04_lp.py", "principal")
    rs.log_spec(paper, "R7", "05_rob.py", "robustez", exploratory=True)
    with pytest.raises(rs.SpecNotPreregistered):
        rs.log_spec(paper, "R8", "05_rob.py", "olvidé marcarla")
    rows = ig._read_csv(paper / "output/spec_log.csv")
    assert [(r["spec_id"], r["preregistered"], r["exploratory"]) for r in rows] == [
        ("H1", "True", "False"), ("R7", "False", "True")]


def test_log_spec_output_passes_speclog_check(tmp_path):
    paper = tmp_path / "papers/p"
    paper.mkdir(parents=True)
    (paper / "SPEC.md").write_text("```prereg\nH1\n```\n", encoding="utf-8")
    rs.log_spec(paper, "H1", "s.py", "d")
    rs.log_spec(paper, "X1", "s.py", "d", exploratory=True)
    assert ig.check_speclog(tmp_path, []) == []


def test_holdout_opens_once_and_needs_prereg(paper, tmp_path_factory):
    empty = tmp_path_factory.mktemp("sin_prereg")
    with pytest.raises(rs.SpecNotPreregistered):
        rs.open_holdout(empty, "prueba")
    assert rs.open_holdout(paper, "validación final").name == "holdout"
    assert "H1" in (paper / rs.HOLDOUT_MARKER).read_text(encoding="utf-8")
    with pytest.raises(rs.HoldoutAlreadyOpened):
        rs.open_holdout(paper, "otra vez")
