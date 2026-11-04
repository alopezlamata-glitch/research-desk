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
    "direccion-cientifica": BASE_TOOLS + WEB,
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
    return ["cmd", "/c", exe] if exe.lower().endswith(".cmd") else [exe]


def launch(desk: str, encargo: str) -> int:
    check_can_launch(desk)
    desk_dir = DESKS / desk
    if not (desk_dir / encargo).is_file():
        raise LaunchRefused(f"no existe {desk_dir / encargo}")
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    prompt = (f"Lee y ejecuta el encargo de {encargo} (en esta carpeta). Trabaja hasta completar los "
              "entregables. Al final, resume en 10 líneas lo hecho, lo que falta y cualquier riesgo.")
    args = claude_cmd() + ["-p", prompt, "--permission-mode", "acceptEdits",
                           "--allowedTools", " ".join(TOOLS.get(desk, BASE_TOOLS))]
    log = (desk_dir / f"run_{stamp}.log").open("w", encoding="utf-8")
    err = (desk_dir / f"run_{stamp}.err").open("w", encoding="utf-8")
    flags = 0x00000008 | 0x00000200 | 0x08000000 if os.name == "nt" else 0  # DETACHED|NEW_GROUP|NO_WINDOW
    proc = subprocess.Popen(args, cwd=desk_dir, stdout=log, stderr=err, stdin=subprocess.DEVNULL,
                            creationflags=flags, start_new_session=os.name != "nt")
    info = {"pid": proc.pid, "encargo": encargo, "started": stamp, "log": f"run_{stamp}.log"}
    (desk_dir / ".lock").write_text(json.dumps(info), encoding="utf-8")
    runs = DESKS / "RUNS.csv"
    new = not runs.exists()
    with runs.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["started", "desk", "encargo", "pid", "log"])
        w.writerow([stamp, desk, encargo, proc.pid, info["log"]])
    return proc.pid


def setup() -> None:
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
    print("pre-commit activado (.githooks)")


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "status"
    try:
        if cmd == "launch" and len(argv) == 3:
            print(f"{argv[1]} lanzada, PID {launch(argv[1], argv[2])}")
        elif cmd == "status":
            running = active()
            for desk, info in running.items():
                print(f"{desk:22} PID {info['pid']:>6}  desde {info['started']}  {info['encargo']}")
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
