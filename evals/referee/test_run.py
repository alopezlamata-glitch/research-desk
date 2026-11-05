import csv
import json
import os
import sys

import build
import pytest
import run


@pytest.fixture(autouse=True)
def enough_memory(monkeypatch):
    """La memoria libre de la máquina no es parte de lo que se prueba (la negativa por memoria está en test_desk.py)."""
    monkeypatch.setattr(build.desk, "free_memory_gb", lambda: 8.0)


@pytest.fixture
def dry(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "WORKDIR", tmp_path / "work")
    desks = tmp_path / "desks"
    for d in ("referee", "datos", "teoria"):
        (desks / d).mkdir(parents=True)
    config = tmp_path / "config"
    return {"exe": [sys.executable, str(run.EVAL / "fake_claude.py")], "desks_dir": desks,
            "transcripts": config / "projects", "extra_env": {"CLAUDE_CONFIG_DIR": str(config)}}


def test_dry_run_builds_launches_collects_and_grades(dry):
    row = run.run_one("C4", 1, "opus", **dry)
    assert row["verdict"] == "RECHAZADO" and row["verdict_ok"] and row["detected"]
    assert row["protocol_ok"] and row["false_positives"] is None
    assert (row["tokens_in"], row["tokens_out"], row["minutes"]) == (2 * 6010, 400, 1.0)
    args = json.loads((dry["transcripts"].parent / "last_args.json").read_text(encoding="utf-8"))
    assert args[args.index("--tools") + 1] == ",".join(build.desk.builtin_tools("referee"))
    assert all(flag in args for flag in build.desk.LEAN_CONTEXT) and row["session_id"] in args
    assert args[args.index("--add-dir") + 1] == row["repo"]
    assert not (dry["desks_dir"] / "referee" / ".lock").exists()  # el puesto se libera al terminar


def test_control_counts_false_positives(dry):
    row = run.run_one("C0", 1, "opus", **dry)
    assert row["detected"] is None and row["false_positives"] == 1 and not row["verdict_ok"]


def test_respects_active_desks(dry):
    for d in ("datos", "teoria"):
        (dry["desks_dir"] / d / ".lock").write_text(json.dumps({"pid": os.getpid(), "encargo": "x", "started": "x"}))
    with pytest.raises(build.desk.LaunchRefused, match="máximo"):
        run.run_one("C1", 1, "opus", **dry)


def test_main_dry_run_writes_results(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "WORKDIR", tmp_path)
    assert run.main(["--set", "dev", "--dry-run"]) == 0
    rows = list(csv.DictReader((tmp_path / "RESULTS_dry-run.csv").open(encoding="utf-8")))
    assert [r["case"] for r in rows] == run.cases_for("dev", None) == ["C0", "C1", "C3", "C4"]
    assert set(rows[0]) == set(run.FIELDS)


def test_api_error_stops_the_run_without_recording(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "WORKDIR", tmp_path)
    monkeypatch.setenv("FAKE_CLAUDE_LIMIT", "1")
    assert run.main(["--set", "dev", "--dry-run"]) == 1
    assert not (tmp_path / "RESULTS_dry-run.csv").exists()  # ni una fila falsa
    assert run.session_error('{"is_error": false, "result": "ok"}', 0) is None
    assert run.session_error("", 1).startswith("claude salió")


def test_rescore_grades_a_finished_session_without_launching(dry, tmp_path, monkeypatch):
    row = run.run_one("C4", 1, "opus", **dry)  # la salida del falso lleva UTF-8 no representable en cp1252
    monkeypatch.setattr(run, "RESULTS", tmp_path / "R.csv")
    monkeypatch.setattr(run.desk, "TRANSCRIPTS", dry["transcripts"])
    assert run.main(["--case", "C4", "--rescore", row["repo"], row["session_id"]]) == 0
    (again,) = csv.DictReader((tmp_path / "R.csv").open(encoding="utf-8"))
    assert again["detected"] == "True" and again["session_id"] == row["session_id"]
    assert run.main(["--set", "dev", "--rescore", row["repo"], row["session_id"]]) == 2
