"""Lanzador de desks: una sesión por desk, como máximo MAX_CONCURRENT a la vez y con memoria suficiente.

Uso:
  uv run python tools/desk.py launch <desk> <ENCARGO.md>   # lanza la desk como proceso independiente
  uv run python tools/desk.py status                       # qué desks están trabajando
  uv run python tools/desk.py setup                        # activa el pre-commit en este clon

Cada lanzamiento deja `desks/<desk>/.lock` (PID, encargo, hora) mientras la sesión vive, su salida en
`desks/<desk>/run_<fecha>.log` y una fila en `desks/RUNS.csv`. Un lock cuyo proceso ya no existe es obsoleto
y se ignora.
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
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKS = ROOT / "desks"
MAX_CONCURRENT = int(os.environ.get("DESK_MAX_CONCURRENT", "2"))
# Memoria comprometida disponible (RAM + paginación): agotarla es lo que provoca "bad allocation".
MIN_FREE_GB = float(os.environ.get("DESK_MIN_COMMIT_GB", "2.0"))

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
    return info if pid_alive(int(info.get("pid", 0))) else None


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


def model_for(desk: str, encargo_text: str) -> str:
    """El `Modelo:` del encargo si lo declara; si no, el de la desk."""
    m = re.search(r"^\W*Modelo\W+(\w+)", encargo_text, re.MULTILINE | re.IGNORECASE)  # "Modelo: x", "**Modelo:** x"
    model = m.group(1).lower() if m else DEFAULT_MODEL.get(desk, "sonnet")
    if model not in MODELS:
        raise LaunchRefused(f"modelo '{model}' no válido en el encargo; usa uno de {', '.join(MODELS)}")
    return model


def launch(desk: str, encargo: str) -> int:
    check_can_launch(desk)
    desk_dir = DESKS / desk
    if not (desk_dir / encargo).is_file():
        raise LaunchRefused(f"no existe {desk_dir / encargo}")
    model = model_for(desk, (desk_dir / encargo).read_text(encoding="utf-8"))
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    prompt = (f"Lee y ejecuta el encargo de {encargo} (en esta carpeta). Trabaja hasta completar los "
              "entregables. Al final, resume en 10 líneas lo hecho, lo que falta y cualquier riesgo.")
    args = claude_cmd() + ["-p", prompt, "--model", model, "--permission-mode", "acceptEdits",
                           "--allowedTools", " ".join(TOOLS.get(desk, BASE_TOOLS))]
    log, err = desk_dir / f"run_{stamp}.log", desk_dir / f"run_{stamp}.err"
    pid = spawn_detached(args, desk_dir, log, err)
    info = {"pid": pid, "encargo": encargo, "started": stamp, "log": log.name, "model": model}
    (desk_dir / ".lock").write_text(json.dumps(info), encoding="utf-8")
    runs = DESKS / "RUNS.csv"
    new = not runs.exists()
    with runs.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["started", "desk", "encargo", "pid", "log", "model"])
        w.writerow([stamp, desk, encargo, pid, info["log"], model])
    return pid


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
    cmdline = f'cmd /s /c "{subprocess.list2cmdline(args)} > "{log}" 2> "{err}" < NUL"'
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
