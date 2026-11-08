"""Lanzador de desks: una sesión por desk, como máximo MAX_CONCURRENT a la vez y con memoria suficiente.

Uso:
  uv run python tools/desk.py launch <desk> <ENCARGO.md>   # lanza la desk como proceso independiente
  uv run python tools/desk.py status                       # qué desks están trabajando
  uv run python tools/desk.py resume <desk> [session_id] [--msg TEXTO]  # continúa la última sesión de la desk
                                                         # (cortada, o con una instrucción nueva en --msg)
  uv run python tools/desk.py usage [desk]                 # tokens, caché, pico de contexto y duración por sesión
  uv run python tools/desk.py estado <desk> <estado>       # la Coordinación marca la última sesión al revisarla
                                                         # (aceptada, rechazada, bloqueada o incompleta)
  uv run python tools/desk.py setup                        # activa el pre-commit en este clon

Cada lanzamiento deja `desks/<desk>/.lock` (PID, encargo, hora) mientras la sesión vive, su salida en
`desks/<desk>/run_<fecha>.log` y una fila en `desks/RUNS.csv`. Un lock cuyo proceso ya no existe es obsoleto
y se ignora. Cada sesión recibe un `session_id` fijo: con él se reanuda (`resume`) y se lee su consumo de la
transcripción que Claude Code guarda en `~/.claude/projects/*/<session_id>.jsonl` (`usage`).
"""

from __future__ import annotations

import csv
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKS = ROOT / "desks"
MAX_CONCURRENT = int(os.environ.get("DESK_MAX_CONCURRENT", "2"))
# Memoria comprometida disponible (RAM + paginación): agotarla es lo que provoca "bad allocation".
MIN_FREE_GB = float(os.environ.get("DESK_MIN_COMMIT_GB", "2.0"))
RUNS = DESKS / "RUNS.csv"
RUNS_FIELDS = ["started", "desk", "encargo", "pid", "log", "model", "session_id", "effort", "estado"]
# Sin servidores MCP ni lista de skills: las desks no usan MCP y leen las skills por ruta (../../.claude/skills/).
# No se usa --setting-sources: desactivaría los hooks de usuario de Pixel Agents.
LEAN_CONTEXT = ["--strict-mcp-config", "--disable-slash-commands"]
TRANSCRIPTS = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"

BASE_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep"]
WEB = ["WebSearch", "WebFetch"]
PY = ["Bash(uv run:*)", "Bash(ls:*)", "Bash(head:*)", "Bash(wc:*)", "Bash(git status:*)",
      "Bash(git diff:*)", "Bash(git log:*)"]
TOOLS = {
    "literatura": BASE_TOOLS + WEB + PY + ["Bash(curl:*)"],
    "teoria": BASE_TOOLS + WEB + PY + ["Bash(curl:*)"],
    "datos": BASE_TOOLS + WEB + PY + ["Bash(curl:*)", "Bash(du:*)", "Bash(mkdir:*)"],
    "econometria": BASE_TOOLS + PY + ["Bash(Rscript:*)"],
    "redaccion": BASE_TOOLS + PY + ["Bash(latexmk:*)"],
    "referee": BASE_TOOLS + PY + ["Bash(Rscript:*)"],
    "direccion-cientifica": BASE_TOOLS + WEB + PY,  # Python solo para comprobar cuentas; no implementa
}

# Modelo por defecto de cada desk según el tipo de trabajo. Un encargo lo cambia con una línea `Modelo: <alias>`
# (p. ej., haiku para tareas mecánicas, opus para una tarea de datos con juicio de identificación).
#   opus:   juicio científico, derivaciones, identificación y auditoría adversarial, donde un error es caro.
#   sonnet: trabajo largo y bien especificado (búsqueda, descarga y limpieza).
#   haiku:  tareas mecánicas y acotadas (conversiones, inventarios, comprobaciones de formato).
MODELS = ("opus", "sonnet", "haiku")
DEFAULT_MODEL = {
    "direccion-cientifica": "opus",
    "teoria": "opus",
    "econometria": "opus",
    "referee": "opus",
    "redaccion": "opus",
    "literatura": "sonnet",
    "datos": "sonnet",
}
# Esfuerzo de razonamiento (`--effort` de la CLI). Sin línea `Esfuerzo: <nivel>` en el encargo, el de la CLI: el alto solo
# donde lo justifique la tarea. Se fija al lanzar y no cambia en la sesión (cambiarlo a mitad puede invalidar la caché).
EFFORTS = ("low", "medium", "high", "xhigh", "max")


# Resultado de la revisión de la Coordinación. La métrica de eficiencia es el consumo por sesión aceptada, no por sesión.
ESTADOS = ("aceptada", "rechazada", "bloqueada", "incompleta")


class LaunchRefused(RuntimeError):
    """La desk no se puede lanzar ahora (ya activa, demasiadas desks o poca memoria)."""


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        k32 = ctypes.windll.kernel32
        handle = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = k32.GetExitCodeProcess(handle, ctypes.byref(code))
        k32.CloseHandle(handle)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def process_created(pid: int) -> datetime | None:
    """Hora local de creación del proceso (solo Windows); None si no se puede saber."""
    if os.name != "nt":
        return None
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None
    times = [ctypes.c_ulonglong() for _ in range(4)]  # creación, salida, kernel, usuario (FILETIME)
    ok = k32.GetProcessTimes(handle, *(ctypes.byref(x) for x in times))
    k32.CloseHandle(handle)
    if not ok:
        return None
    utc = datetime(1601, 1, 1, tzinfo=UTC) + timedelta(microseconds=times[0].value // 10)
    return utc.astimezone().replace(tzinfo=None)  # hora local sin zona, como el `started` del lock


def free_memory_gb() -> float:
    if os.name != "nt":
        return float("inf")

    class MemStatus(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    st = MemStatus()
    st.dwLength = ctypes.sizeof(MemStatus)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPageFile / 1024**3


def read_lock(desk_dir: Path) -> dict | None:
    lock = desk_dir / ".lock"
    if not lock.exists():
        return None
    try:
        info = json.loads(lock.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    pid = int(info.get("pid", 0))
    if not pid_alive(pid):
        return None
    # Windows reutiliza PIDs: si el proceso con ese PID nació después del lanzamiento, no es la desk (2026-11-05).
    try:
        started = datetime.strptime(info.get("started", ""), "%Y-%m-%d_%H%M")
    except ValueError:
        return info
    created = process_created(pid)
    return None if created and created > started + timedelta(minutes=2) else info


def active(desks_dir: Path = DESKS) -> dict[str, dict]:
    return {d.name: info for d in sorted(desks_dir.iterdir()) if d.is_dir() and (info := read_lock(d))}


def check_can_launch(desk: str, desks_dir: Path = DESKS, free_gb: float | None = None) -> None:
    if not (desks_dir / desk).is_dir():
        raise LaunchRefused(f"no existe la desk '{desk}'")
    running = active(desks_dir)
    if desk in running:
        raise LaunchRefused(f"'{desk}' ya está trabajando (PID {running[desk]['pid']}, {running[desk]['encargo']})")
    if len(running) >= MAX_CONCURRENT:
        raise LaunchRefused(f"ya hay {len(running)} desks activas ({', '.join(running)}); máximo {MAX_CONCURRENT}")
    gb = free_memory_gb() if free_gb is None else free_gb
    if gb < MIN_FREE_GB:
        raise LaunchRefused(f"solo hay {gb:.1f} GB libres; hacen falta {MIN_FREE_GB} GB de memoria comprometida")


def claude_cmd() -> list[str]:
    exe = shutil.which("claude.cmd") or shutil.which("claude")
    if not exe:
        raise LaunchRefused("no encuentro el ejecutable de Claude Code")
    return [exe]  # en Windows, spawn_detached lo ejecuta dentro de cmd, que sabe abrir un .cmd


def encargo_field(name: str, encargo_text: str, allowed: tuple[str, ...]) -> str | None:
    """El valor de una línea `<name>: x` del encargo (también `**<name>:** x` o `- <name>: x`); None si no la tiene."""
    m = re.search(rf"^\W*{name}\W+(\w+)", encargo_text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    if (value := m.group(1).lower()) not in allowed:
        raise LaunchRefused(f"{name.lower()} '{value}' no válido en el encargo; usa uno de {', '.join(allowed)}")
    return value


def model_for(desk: str, encargo_text: str) -> str:
    """El `Modelo:` del encargo si lo declara; si no, el de la desk."""
    return encargo_field("Modelo", encargo_text, MODELS) or DEFAULT_MODEL.get(desk, "sonnet")


def launch(desk: str, encargo: str) -> int:
    check_can_launch(desk)
    desk_dir = DESKS / desk
    if not (desk_dir / encargo).is_file():
        raise LaunchRefused(f"no existe {desk_dir / encargo}")
    text = (desk_dir / encargo).read_text(encoding="utf-8")
    model, effort = model_for(desk, text), encargo_field("Esfuerzo", text, EFFORTS)
    prompt = (f"Lee y ejecuta el encargo de {encargo} (en esta carpeta). Trabaja hasta completar los "
              "entregables. Al final, resume en 10 líneas lo hecho, lo que falta y cualquier riesgo.")
    return _start(desk, encargo, model, effort, str(uuid.uuid4()), prompt, resuming=False)


def resume(desk: str, session_id: str | None = None, message: str | None = None) -> int:
    """Continúa una sesión anterior de la desk con su contexto (por defecto, la última registrada).

    Sin `message`, sigue el encargo donde se cortó; con `message`, le da esa instrucción nueva sobre el mismo encargo.
    """
    check_can_launch(desk)
    runs = [r for r in read_runs() if r["desk"] == desk and r.get("session_id")]
    if session_id:
        runs = [r for r in runs if r["session_id"] == session_id]
    if not runs:
        which = f" con session_id {session_id}" if session_id else " con session_id"
        raise LaunchRefused(f"no hay en {RUNS.name} ninguna sesión de '{desk}'{which}")
    last = runs[-1]
    if message and "%" in message:
        raise LaunchRefused("el mensaje no puede llevar '%': cmd lo expandiría como variable")
    start = message or (f"La sesión se cortó antes de terminar el encargo de {last['encargo']}. Sigue desde donde lo "
                        "dejaste, sin rehacer lo hecho.")
    prompt = f"{start} Al final, resume en 10 líneas lo hecho, lo que falta y cualquier riesgo."
    model = last["model"] or DEFAULT_MODEL.get(desk, "sonnet")
    return _start(desk, last["encargo"], model, last.get("effort") or None, last["session_id"], prompt, resuming=True)


def builtin_tools(desk: str) -> list[str]:
    """Herramientas internas que se cargan en la sesión: las del perfil de la desk, sin patrones (`Bash(uv run:*)` → `Bash`).

    `--allowedTools` solo decide qué se ejecuta sin pedir permiso; sin `--tools` se cargan también las definiciones de
    todas las demás (Agent, navegador, tareas…), unos 37K tokens que se releen en cada turno (medido el 2026-11-05).
    """
    return list(dict.fromkeys(t.split("(")[0] for t in TOOLS.get(desk, BASE_TOOLS)))


def _start(desk: str, encargo: str, model: str, effort: str | None, session_id: str, prompt: str, *,
           resuming: bool) -> int:
    desk_dir = DESKS / desk
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    # --resume conserva el session_id y sigue escribiendo en la misma transcripción (comprobado con la CLI 2.1.306).
    args = claude_cmd() + ["-p", prompt, "--resume" if resuming else "--session-id", session_id, "--model", model,
                           "--permission-mode", "acceptEdits", "--allowedTools", " ".join(TOOLS.get(desk, BASE_TOOLS)),
                           *LEAN_CONTEXT, "--tools", ",".join(builtin_tools(desk)), *(["--effort", effort] if effort else [])]
    log, err = desk_dir / f"run_{stamp}.log", desk_dir / f"run_{stamp}.err"
    pid = spawn_detached(args, desk_dir, log, err)
    # La hora del lock se toma después de lanzar: si el lanzamiento se retrasa (el equipo se suspendió a medias, 2026-11-07),
    # el proceso nacería después de `stamp` y read_lock lo tomaría por un PID reutilizado.
    started = datetime.now().strftime("%Y-%m-%d_%H%M")
    info = {"pid": pid, "encargo": encargo, "started": started, "log": log.name, "model": model, "session_id": session_id,
            "effort": effort or ""}
    (desk_dir / ".lock").write_text(json.dumps(info), encoding="utf-8")
    append_run({"desk": desk, **info})
    return pid


def read_runs(runs: Path | None = None) -> list[dict]:
    runs = runs or RUNS
    if not runs.exists():
        return []
    with runs.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def append_run(row: dict, runs: Path | None = None) -> None:
    """Añade una fila a RUNS.csv. Si el archivo no tiene la cabecera actual (anterior a G7), lo reescribe con ella."""
    runs = runs or RUNS
    header = runs.read_text(encoding="utf-8").partition("\n")[0].strip() if runs.exists() else ""
    current = header == ",".join(RUNS_FIELDS)
    old_rows = [] if current else read_runs(runs)
    with runs.open("a" if current else "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RUNS_FIELDS, restval="", extrasaction="ignore")
        if not current:
            w.writeheader()
            w.writerows(old_rows)
        w.writerow(row)


def set_estado(desk: str, estado: str, runs: Path | None = None) -> str:
    """Marca con `estado` la última sesión de la desk (todas sus filas, si se reanudó). Devuelve su session_id."""
    if estado not in ESTADOS:
        raise LaunchRefused(f"estado '{estado}' no válido; usa uno de {', '.join(ESTADOS)}")
    runs = runs or RUNS
    rows = read_runs(runs)
    sids = [r["session_id"] for r in rows if r["desk"] == desk and r.get("session_id")]
    if not sids:
        raise LaunchRefused(f"no hay en {runs.name} ninguna sesión de '{desk}' con session_id")
    for r in rows:
        if r.get("session_id") == sids[-1]:
            r["estado"] = estado
    with runs.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RUNS_FIELDS, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return sids[-1]


def session_usage(session_id: str, transcripts: Path | None = None) -> dict | None:
    """Consumo de una sesión según su transcripción de Claude Code; None si no la encuentra.

    Claude Code parte cada respuesta en varias entradas con el mismo `message.id` y el mismo `usage`: cuenta una vez.
    """
    files = sorted((transcripts or TRANSCRIPTS).glob(f"*/{session_id}.jsonl"))
    if not files:
        return None
    usage_by_msg: dict[str, dict] = {}
    times: list[datetime] = []
    for line in files[0].read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # la última línea puede estar a medio escribir si la sesión sigue viva
        if ts := entry.get("timestamp"):
            times.append(datetime.fromisoformat(ts))
        msg = entry.get("message")
        if entry.get("type") == "assistant" and isinstance(msg, dict) and msg.get("usage"):
            usage_by_msg[msg.get("id") or f"sin-id-{len(usage_by_msg)}"] = msg["usage"]
    out = {"turns": len(usage_by_msg), "input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "peak_ctx": 0}
    for u in usage_by_msg.values():
        inp, cw, cr = (u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        out["input"] += inp
        out["cache_write"] += cw
        out["cache_read"] += cr
        out["output"] += u.get("output_tokens", 0)
        out["peak_ctx"] = max(out["peak_ctx"], inp + cw + cr)
    out["minutes"] = round((max(times) - min(times)).total_seconds() / 60, 1) if times else 0.0
    return out


def print_usage(desk: str | None = None) -> None:
    sessions: dict[str, dict] = {}  # una sesión reanudada tiene varias filas en RUNS.csv y una sola transcripción
    for r in read_runs():
        if r.get("session_id") and desk in (None, r["desk"]):
            s = sessions.setdefault(r["session_id"], {**r, "launches": 0})
            s["launches"] += 1
            s["estado"] = r.get("estado", "")  # el de la última fila: una reanudación vuelve a quedar sin revisar
    if not sessions:
        print("No hay sesiones con session_id en RUNS.csv (las anteriores a G7 no lo registran).")
        return
    print(f"{'inicio':16} {'desk':20} {'modelo':6} {'lanz':>4} {'turnos':>6} {'salida':>8} {'caché leída':>12} "
          f"{'caché escrita':>13} {'pico ctx':>9} {'min':>6} {'estado':10}  encargo")
    by_desk: dict[str, dict] = {}
    for sid, r in sessions.items():
        head = f"{r['started']:16} {r['desk']:20} {r['model']:6} {r['launches']:>4}"
        if (u := session_usage(sid)) is None:
            print(f"{head}  sin transcripción ({sid})")
            continue
        print(f"{head} {u['turns']:>6} {u['output']:>8} {u['cache_read']:>12} {u['cache_write']:>13} "
              f"{u['peak_ctx']:>9} {u['minutes']:>6} {r['estado'] or '-':10}  {r['encargo']}")
        if r["estado"]:  # solo las revisadas: una sesión sin revisar no es ni coste perdido ni entregable aceptado
            d = by_desk.setdefault(r["desk"], {"revisadas": 0, "aceptadas": 0, "cache_read": 0, "cache_write": 0,
                                               "output": 0})
            d["revisadas"] += 1
            d["aceptadas"] += r["estado"] == "aceptada"
            for k in ("cache_read", "cache_write", "output"):
                d[k] += u[k]
    if by_desk:
        print("\nPor sesión aceptada (el consumo de las rechazadas, bloqueadas o incompletas también cuenta):")
        for name, d in by_desk.items():
            if not d["aceptadas"]:
                print(f"  {name:20} {d['revisadas']} revisadas, ninguna aceptada")
                continue
            per = {k: d[k] // d["aceptadas"] for k in ("cache_read", "cache_write", "output")}
            print(f"  {name:20} {d['aceptadas']}/{d['revisadas']} aceptadas · caché leída {per['cache_read']} · "
                  f"caché escrita {per['cache_write']} · salida {per['output']}")


def r_bin() -> str | None:
    """Carpeta `bin` de R para las desks: `DESK_R_BIN`, la del `Rscript` del PATH o la versión más alta instalada."""
    if env := os.environ.get("DESK_R_BIN"):
        return env
    if found := shutil.which("Rscript"):
        return str(Path(found).parent)
    installs = list(Path(os.environ.get("ProgramFiles", r"C:\Program Files"), "R").glob("R-*/bin/Rscript.exe"))
    if not installs:
        return None
    newest = max(installs, key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.parent.parent.name)))
    return str(newest.parent)


def spawn_detached(args: list[str], cwd: Path, log: Path, err: Path) -> int:
    """Lanza `args` fuera del árbol de procesos de quien llama y devuelve el PID.

    En Windows, un hijo de Popen (aunque sea DETACHED) murió junto con las desks activas al cerrarse el
    comando de Bash de la sesión que lo lanzó (2026-11-04, código 137). Win32_Process.Create (WMI) crea
    el proceso como hijo del servicio WMI, sin relación con la sesión.
    """
    if os.name != "nt":
        with log.open("w") as out, err.open("w") as e:
            return subprocess.Popen(args, cwd=cwd, stdout=out, stderr=e, stdin=subprocess.DEVNULL,
                                    start_new_session=True).pid
    # El proceso de WMI no hereda nuestro entorno; R no está en el PATH del sistema y `Bash(Rscript:*)` no casaba.
    path = f'set "PATH={rbin};%PATH%" && ' if (rbin := r_bin()) else ""
    cmdline = f'cmd /s /c "{path}{subprocess.list2cmdline(args)} > "{log}" 2> "{err}" < NUL"'
    ps = ("$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
          "@{CommandLine=$env:DESK_CMDLINE; CurrentDirectory=$env:DESK_CWD}; "
          "if ($r.ReturnValue -ne 0) { exit [int]$r.ReturnValue }; $r.ProcessId")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True,
                       text=True, check=False, env={**os.environ, "DESK_CMDLINE": cmdline, "DESK_CWD": str(cwd)})
    if r.returncode != 0 or not r.stdout.strip().isdigit():
        raise LaunchRefused(f"Win32_Process.Create falló ({r.returncode}): {r.stderr.strip() or r.stdout.strip()}")
    return int(r.stdout.strip())


def setup() -> None:
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
    print("pre-commit activado (.githooks)")


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "status"
    try:
        if cmd == "launch" and len(argv) == 3:
            pid = launch(argv[1], argv[2])
            print(f"{argv[1]} lanzada con {read_lock(DESKS / argv[1])['model']}, PID {pid}")
        elif cmd == "resume" and 2 <= len(argv) and ("--msg" not in argv or argv.index("--msg") == len(argv) - 2):
            message = argv.pop() if "--msg" in argv else None
            argv = [a for a in argv if a != "--msg"]
            if len(argv) not in (2, 3):
                print(__doc__)
                return 2
            pid = resume(argv[1], argv[2] if len(argv) == 3 else None, message)
            print(f"{argv[1]} reanudada (sesión {read_lock(DESKS / argv[1])['session_id']}), PID {pid}")
        elif cmd == "estado" and len(argv) == 3:
            print(f"{argv[1]}: sesión {set_estado(argv[1], argv[2])} marcada como {argv[2]}")
        elif cmd == "usage" and len(argv) in (1, 2):
            print_usage(argv[1] if len(argv) == 2 else None)
        elif cmd == "status":
            running = active()
            for desk, info in running.items():
                print(f"{desk:22} {info.get('model', '?'):7} PID {info['pid']:>6}  desde {info['started']}  {info['encargo']}")
            print(f"{len(running)}/{MAX_CONCURRENT} desks activas · {free_memory_gb():.1f} GB de memoria comprometida disponible")
        elif cmd == "setup":
            setup()
        else:
            print(__doc__)
            return 2
    except LaunchRefused as e:
        print(f"No se lanza: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
