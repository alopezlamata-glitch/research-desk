import json
import os
import sys
import time
from pathlib import Path

import desk
import pytest


@pytest.fixture
def desks(tmp_path):
    for d in ("datos", "teoria", "literatura"):
        (tmp_path / d).mkdir()
    return tmp_path


def lock(desks, name, pid):
    (desks / name / ".lock").write_text(json.dumps({"pid": pid, "encargo": "E.md", "started": "x"}))


def test_pid_alive():
    assert desk.pid_alive(os.getpid())
    assert not desk.pid_alive(0)
    assert not desk.pid_alive(2**22 + 12345)


def test_refuses_same_desk_twice_but_ignores_stale_locks(desks):
    lock(desks, "datos", os.getpid())
    with pytest.raises(desk.LaunchRefused, match="ya está trabajando"):
        desk.check_can_launch("datos", desks, free_gb=8)
    lock(desks, "datos", 2**22 + 12345)  # proceso muerto: lock obsoleto
    desk.check_can_launch("datos", desks, free_gb=8)


def test_refuses_above_max_concurrent(desks, monkeypatch):
    monkeypatch.setattr(desk, "MAX_CONCURRENT", 2)
    lock(desks, "datos", os.getpid())
    lock(desks, "teoria", os.getpid())
    with pytest.raises(desk.LaunchRefused, match="máximo 2"):
        desk.check_can_launch("literatura", desks, free_gb=8)


def test_refuses_low_memory_and_unknown_desk(desks):
    with pytest.raises(desk.LaunchRefused, match="GB libres"):
        desk.check_can_launch("datos", desks, free_gb=0.5)
    with pytest.raises(desk.LaunchRefused, match="no existe"):
        desk.check_can_launch("inventada", desks, free_gb=8)


def test_spawn_detached_runs_with_cwd_and_redirects_output(tmp_path):
    log, err = tmp_path / "run.log", tmp_path / "run.err"
    args = [sys.executable, "-c", "import os; print('cwd=' + os.getcwd())"]
    pid = desk.spawn_detached(args, tmp_path, log, err)
    assert pid > 0
    deadline = time.time() + 30
    while time.time() < deadline and not (log.exists() and "cwd=" in log.read_text()):
        time.sleep(0.2)
    assert log.read_text().strip() == f"cwd={tmp_path}"


def test_every_real_desk_has_a_tool_profile_and_a_model():
    real = {d.name for d in desk.DESKS.iterdir() if d.is_dir()}
    assert real <= set(desk.TOOLS), real - set(desk.TOOLS)
    assert real <= set(desk.DEFAULT_MODEL), real - set(desk.DEFAULT_MODEL)
    assert set(desk.DEFAULT_MODEL.values()) <= set(desk.MODELS)


@pytest.mark.parametrize(("text", "expected"), [("# Encargo\nsin modelo", "opus"),
                                                ("Modelo: haiku\n", "haiku"),
                                                ("intro\n**Modelo:** Sonnet\n", "sonnet"),
                                                ("- Modelo: opus", "opus")])
def test_model_from_encargo_or_desk_default(text, expected):
    assert desk.model_for("teoria", text) == expected


def test_invalid_model_is_refused():
    with pytest.raises(desk.LaunchRefused, match="no válido"):
        desk.model_for("datos", "Modelo: gpt5")


@pytest.fixture
def fake_spawn(tmp_path, monkeypatch):
    """Lanzamientos sin proceso real: DESKS y RUNS en tmp y spawn_detached captura los argumentos."""
    (tmp_path / "datos").mkdir()
    (tmp_path / "datos" / "E.md").write_text("Modelo: haiku\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(desk, "DESKS", tmp_path)
    monkeypatch.setattr(desk, "RUNS", tmp_path / "RUNS.csv")
    monkeypatch.setattr(desk, "check_can_launch", lambda d: None)
    monkeypatch.setattr(desk, "claude_cmd", lambda: ["claude"])
    monkeypatch.setattr(desk, "spawn_detached", lambda args, *a: calls.append(args) or 4242)
    return calls


def test_launch_fixes_session_id_and_resume_reuses_it(fake_spawn):
    desk.launch("datos", "E.md")
    sid = fake_spawn[0][fake_spawn[0].index("--session-id") + 1]
    assert desk.read_runs()[-1]["session_id"] == sid
    desk.resume("datos")
    assert fake_spawn[1][fake_spawn[1].index("--resume") + 1] == sid
    assert "--session-id" not in fake_spawn[1]
    assert fake_spawn[1][fake_spawn[1].index("--model") + 1] == "haiku"  # el modelo de la sesión original
    assert [r["session_id"] for r in desk.read_runs()] == [sid, sid]


def test_resume_refuses_without_a_recorded_session(fake_spawn):
    with pytest.raises(desk.LaunchRefused, match="ninguna sesión"):
        desk.resume("datos")
    desk.launch("datos", "E.md")
    with pytest.raises(desk.LaunchRefused, match="ninguna sesión"):
        desk.resume("datos", "otro-id")


def test_append_run_upgrades_old_header_without_losing_rows(tmp_path):
    runs = tmp_path / "RUNS.csv"
    runs.write_text("started,desk,encargo,pid,log,model\nA,datos,E.md,1,run.log,\nB,teoria,F.md,2,run.log,opus\n",
                    encoding="utf-8")
    desk.append_run({"started": "C", "desk": "datos", "session_id": "s1"}, runs)
    desk.append_run({"started": "D", "desk": "datos", "session_id": "s2"}, runs)
    rows = desk.read_runs(runs)
    assert runs.read_text(encoding="utf-8").splitlines()[0] == ",".join(desk.RUNS_FIELDS)
    assert [(r["started"], r["model"], r["session_id"]) for r in rows] == [
        ("A", "", ""), ("B", "opus", ""), ("C", "", "s1"), ("D", "", "s2")]


def test_session_usage_counts_each_message_once(tmp_path):
    def msg(mid, ts, inp, cw, cr, out):
        return json.dumps({"type": "assistant", "timestamp": ts, "message": {"id": mid, "usage": {
            "input_tokens": inp, "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr,
            "output_tokens": out}}})
    lines = [json.dumps({"type": "user", "timestamp": "2026-11-05T10:00:00Z", "message": {"content": "x"}}),
             msg("m1", "2026-11-05T10:00:05Z", 2, 50_000, 0, 100),
             msg("m1", "2026-11-05T10:00:06Z", 2, 50_000, 0, 100),  # misma respuesta partida en dos entradas
             msg("m2", "2026-11-05T10:30:00Z", 3, 1_000, 50_000, 400),
             '{"type": "assistant", "message": {"id"']  # línea a medio escribir
    (tmp_path / "proj").mkdir()
    (tmp_path / "proj" / "sid.jsonl").write_text("\n".join(lines), encoding="utf-8")
    u = desk.session_usage("sid", tmp_path)
    assert u == {"turns": 2, "input": 5, "cache_write": 51_000, "cache_read": 50_000, "output": 500,
                 "peak_ctx": 51_003, "minutes": 30.0}
    assert desk.session_usage("otra", tmp_path) is None


def test_sessions_load_only_the_desk_builtin_tools(fake_spawn):
    assert desk.builtin_tools("econometria") == ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
    assert desk.builtin_tools("datos") == ["Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Bash"]
    desk.launch("datos", "E.md")
    args = fake_spawn[0]
    assert args[args.index("--tools") + 1] == ",".join(desk.builtin_tools("datos"))
    assert {"--strict-mcp-config", "--disable-slash-commands"} <= set(args)


@pytest.mark.skipif(os.name != "nt" or desk.r_bin() is None, reason="R solo se añade al PATH en Windows")
def test_detached_desks_find_rscript_on_path(tmp_path):
    assert "R-4.5" in desk.r_bin() or os.environ.get("DESK_R_BIN")  # la versión más alta instalada
    log, err = tmp_path / "run.log", tmp_path / "run.err"
    args = [sys.executable, "-c", "import shutil; print('rscript=' + str(shutil.which('Rscript')))"]
    desk.spawn_detached(args, tmp_path, log, err)
    deadline = time.time() + 30
    while time.time() < deadline and not (log.exists() and "rscript=" in log.read_text()):
        time.sleep(0.2)
    found = log.read_text().strip().removeprefix("rscript=")
    assert Path(found).parent == Path(desk.r_bin())
