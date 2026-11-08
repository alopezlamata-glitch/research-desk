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


def test_invalid_effort_is_refused():
    with pytest.raises(desk.LaunchRefused, match="no válido"):
        desk.encargo_field("Esfuerzo", "Esfuerzo: altísimo", desk.EFFORTS)


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


def test_resume_with_a_new_instruction_keeps_the_session(fake_spawn):
    desk.launch("datos", "E.md")
    desk.resume("datos", message="Completa ahora la replicación en R.")
    prompt = fake_spawn[1][fake_spawn[1].index("-p") + 1]
    assert prompt.startswith("Completa ahora la replicación en R.") and "se cortó" not in prompt
    assert fake_spawn[1][fake_spawn[1].index("--resume") + 1] == desk.read_runs()[0]["session_id"]
    with pytest.raises(desk.LaunchRefused, match="%"):
        desk.resume("datos", message="usa %PATH%")


def test_resume_cli_parses_msg(fake_spawn, monkeypatch):
    desk.launch("datos", "E.md")
    monkeypatch.setattr(desk, "read_lock", lambda d: {"session_id": "x"})
    assert desk.main(["resume", "datos", "--msg", "Haz X."]) == 0
    assert fake_spawn[1][fake_spawn[1].index("-p") + 1].startswith("Haz X.")
    assert desk.main(["resume", "datos", "--msg"]) == 2  # --msg sin texto


@pytest.mark.skipif(os.name != "nt", reason="la hora de creación del proceso solo se lee en Windows")
def test_lock_with_a_reused_pid_is_stale(desks):
    from datetime import datetime
    me = desk.process_created(os.getpid())
    assert me and abs((datetime.now() - me).total_seconds()) < 3600  # este proceso, en hora local
    info = {"pid": os.getpid(), "encargo": "E.md"}
    (desks / "datos" / ".lock").write_text(json.dumps({**info, "started": "2026-01-01_0000"}))
    assert desk.read_lock(desks / "datos") is None  # el PID vive, pero nació mucho después del lanzamiento
    (desks / "datos" / ".lock").write_text(json.dumps({**info, "started": me.strftime("%Y-%m-%d_%H%M")}))
    assert desk.read_lock(desks / "datos") is not None


def test_lock_time_is_taken_after_a_slow_launch(fake_spawn, monkeypatch):
    """Caso real del 2026-11-07: el lanzamiento tardó 11 min y el lock quedó con una hora anterior al proceso."""
    from datetime import datetime as real_dt
    from datetime import timedelta

    clock = {"t": real_dt(2026, 11, 7, 23, 30)}

    class FakeDateTime(real_dt):
        @classmethod
        def now(cls, tz=None):
            return clock["t"]

    def slow_spawn(args, *a):
        clock["t"] += timedelta(minutes=11)  # el proceso nace 11 minutos después de empezar
        return 4242

    monkeypatch.setattr(desk, "datetime", FakeDateTime)
    monkeypatch.setattr(desk, "spawn_detached", slow_spawn)
    monkeypatch.setattr(desk, "pid_alive", lambda pid: True)
    monkeypatch.setattr(desk, "process_created", lambda pid: real_dt(2026, 11, 7, 23, 41, 43))
    desk.launch("datos", "E.md")
    assert desk.read_lock(desk.DESKS / "datos")["started"] == "2026-11-07_2341"


def test_effort_from_encargo_goes_to_the_cli_and_resume_keeps_it(fake_spawn, tmp_path):
    desk.launch("datos", "E.md")
    assert "--effort" not in fake_spawn[0]  # sin línea Esfuerzo:, el de la CLI
    (tmp_path / "datos" / "F.md").write_text("Modelo: opus\n**Esfuerzo:** high\n", encoding="utf-8")
    desk.launch("datos", "F.md")
    assert fake_spawn[1][fake_spawn[1].index("--effort") + 1] == "high"
    assert desk.read_runs()[-1]["effort"] == "high"
    desk.resume("datos")
    assert fake_spawn[2][fake_spawn[2].index("--effort") + 1] == "high"


def test_estado_marks_the_last_session_and_usage_reports_cost_per_accepted(fake_spawn, monkeypatch, capsys):
    with pytest.raises(desk.LaunchRefused, match="no válido"):
        desk.set_estado("datos", "genial")
    desk.launch("datos", "E.md")
    first = desk.read_runs()[-1]["session_id"]
    desk.set_estado("datos", "rechazada")
    desk.launch("datos", "E.md")
    desk.resume("datos")  # dos filas de la misma sesión: se marcan las dos
    second = desk.set_estado("datos", "aceptada")
    assert [(r["session_id"], r["estado"]) for r in desk.read_runs()] == [
        (first, "rechazada"), (second, "aceptada"), (second, "aceptada")]
    usage = {"turns": 1, "input": 0, "cache_write": 10, "cache_read": 100, "output": 1, "peak_ctx": 0, "minutes": 0}
    monkeypatch.setattr(desk, "session_usage", lambda sid: usage)
    desk.print_usage()
    # el coste de la rechazada se carga a la única aceptada
    assert "1/2 aceptadas · caché leída 200 · caché escrita 20 · salida 2" in capsys.readouterr().out


def test_launch_prompt_bounds_scope_and_asks_for_handoff_except_for_the_referee(fake_spawn, tmp_path):
    (tmp_path / "referee").mkdir()
    (tmp_path / "referee" / "R.md").write_text("encargo", encoding="utf-8")
    desk.launch("datos", "E.md")
    desk.launch("referee", "R.md")
    datos, referee = (call[call.index("-p") + 1] for call in fake_spawn)
    assert "condición de parada" in datos and "## HANDOFF" in datos
    # el prompt del Referee no cambia sin pasar la eval (CLAUDE.md, «Eval del Referee»)
    assert referee == ("Lee y ejecuta el encargo de R.md (en esta carpeta). Trabaja hasta completar los entregables. "
                       "Al final, resume en 10 líneas lo hecho, lo que falta y cualquier riesgo.")
