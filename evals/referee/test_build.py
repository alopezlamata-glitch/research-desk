"""Cada caso se construye en un repo temporal sin la clave de respuestas, pasa integrity.py (ningún check determinista
detecta el error plantado) y su `marker` está en las líneas que declara su case.yaml."""

import shutil
import subprocess
import sys

import build
import grade
import pandas as pd
import pytest

sys.path.insert(0, str(build.ROOT / "tools"))
import integrity

DRAFT = f"{build.PAPER}/draft/main.tex"


def run(repo, *cmd):
    return subprocess.run(cmd, cwd=repo, env=build.env(), capture_output=True, text=True, check=False)


@pytest.fixture(scope="module", params=build.case_ids())
def built(request, tmp_path_factory):
    case = request.param
    return case, build.load_case(case), build.build(case, tmp_path_factory.mktemp(case) / "repo")


def test_repo_has_no_answer_key_and_two_neutral_commits(built):
    case, _, repo = built
    names = {p.name for p in repo.rglob("*") if ".git" not in p.parts}
    assert not names & {"case.yaml", "KNOWN_ISSUES.yaml", "evals", "overlay"}
    assert "evals" not in (repo / "pyproject.toml").read_text(encoding="utf-8")
    log = build._git(repo, "log", "--format=%s").splitlines()
    assert len(log) == 2 and not any(w in " ".join(log).lower() for w in ("eval", "caso", "error", case.lower()))
    assert build._git(repo, "status", "--porcelain") == ""


def test_case_passes_integrity(built):
    _, _, repo = built
    r = run(repo, "uv", "run", "python", "tools/integrity.py")
    assert r.returncode == 0, r.stdout + r.stderr


def test_draft_has_no_typed_numbers_or_unverified_citations(built, tmp_path):
    """El borrador no está en paper/ (check `gate`): se le aplican igualmente los checks de números y citas."""
    _, _, repo = built
    rel = f"{build.PAPER}/paper/main.tex"
    (tmp_path / rel).parent.mkdir(parents=True)
    shutil.copy(repo / DRAFT, tmp_path / rel)
    assert integrity.check_numbers(tmp_path, [rel]) + integrity.check_citations(tmp_path, [rel]) == []


def test_markers_are_in_their_lines(built):
    case, key, repo = built
    assert key["id"] == case and key["verdicts"]
    assert (case == "C0") == (not key["locations"])
    assert build.marker_errors(key, repo) == []


def test_case_passes_pytest(built):
    """Como integrity.py: un test del paper que falla sería una señal determinista que delata el error plantado."""
    _, _, repo = built
    r = run(repo, "uv", "run", "pytest", "-q", "-p", "no:cacheprovider")
    assert r.returncode == 0, r.stdout[-2000:]


def test_marker_errors_detects_a_moved_marker(built):
    case, key, repo = built
    if case == "C0":
        pytest.skip("sin ubicaciones")
    loc = key["locations"][0]
    moved = {"locations": [{**loc, "lines": [loc["lines"][1] + 50, loc["lines"][1] + 60]}]}
    assert build.marker_errors(moved, repo)


def test_clean_data_come_from_raw_by_code(built):
    """Hallazgo 1 del Referee en la línea base de C0 (2026-11-05): el panel tiene que salir de data/raw/ por código."""
    case, _, repo = built
    data_code = repo / build.PAPER / "code" / "data"
    assert not any(w in f.read_text(encoding="utf-8") for f in data_code.glob("*.py") for w in ("simulate", "random"))
    if case not in ("C0", "C2", "C5"):
        pytest.skip("solo los casos que cambian los datos")
    clean = repo / build.PAPER / "data" / "clean" / "panel.parquet"
    before = pd.read_parquet(clean)
    r = run(repo, "uv", "run", "python", f"{build.PAPER}/code/data/build_panel.py")
    assert r.returncode == 0, r.stderr
    pd.testing.assert_frame_equal(pd.read_parquet(clean), before)


def test_known_issue_markers_are_in_the_base():
    """Los problemas conocidos se declaran por ubicación, como los errores plantados: si la base cambia, este test falla."""
    known = {"locations": grade.load_yaml(build.BASE / "KNOWN_ISSUES.yaml").get("issues") or []}
    assert build.marker_errors(known, build.BASE) == []


def test_repo_does_not_reveal_the_eval(built):
    """Nada del repo temporal menciona la eval: ni la regla de CLAUDE.md ni rutas de evals/."""
    _, _, repo = built
    claude_md = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Eval del Referee" in (build.ROOT / "CLAUDE.md").read_text(encoding="utf-8")  # el test no es vacuo
    assert "Eval del Referee" not in claude_md and "Guardarraíles" in claude_md
    leaks = [p.relative_to(repo).as_posix() for p in repo.rglob("*")
             if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".py", ".tex", ".R", ".json", ".yaml"}
             and any(s in p.read_text(encoding="utf-8", errors="ignore")
                     for s in ("evals/referee", "error plantado", "errores plantados", "KNOWN_ISSUES"))]
    assert leaks == []
