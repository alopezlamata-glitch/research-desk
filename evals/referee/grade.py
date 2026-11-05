"""Puntuación determinista de un informe del Referee contra la clave de un caso (specs/referee-eval/SPEC.md).

- Detección: un hallazgo mayor cuya línea `Evidencia:` cita un archivo de las ubicaciones del caso con una línea a ±TOL
  del rango (o solo el archivo, si la ubicación es `any_line`).
- Veredicto: el `verdict` de la cabecera está entre los aceptados del caso.
- Falsos positivos (solo en el control, un caso sin ubicaciones): hallazgos mayores cuya evidencia no apunta a un
  problema conocido de la base (base/KNOWN_ISSUES.yaml).
- Protocolo: el informe pasa `check_referee`; la sesión ejecutó `tools/integrity.py` (completo) y `pytest`; hay un
  script propio en audits/replication_*/.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from integrity import check_referee, front_matter

TOL = 3
SCRIPT_SUFFIXES = {".py", ".R", ".r"}
CITE = re.compile(r"(?P<path>[\w.\\/:-]*?[\w-]+\.[A-Za-z]{1,5})`?(?::L?(?P<a>\d+)(?:\s*[-–]\s*L?(?P<b>\d+))?)?(?![\w/])")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _norm(path: str) -> list[str]:
    parts = [p for p in path.replace("\\", "/").split("/") if p not in ("", ".", "..")]
    return [p for p in parts if not re.fullmatch(r"[A-Za-z]:", p)]


def citations(evidence: str) -> list[tuple[list[str], int | None, int | None]]:
    """(ruta normalizada, línea inicial, línea final) de cada archivo citado en una línea de evidencia."""
    out = []
    for m in CITE.finditer(evidence):
        a = int(m["a"]) if m["a"] else None
        out.append((_norm(m["path"]), a, int(m["b"]) if m["b"] else a))
    return out


def findings(text: str) -> list[dict]:
    """Hallazgos `### título` con su gravedad y sus citas. Mayor: el título lo dice o cuelga de un `##` de mayores."""
    out, section, current = [], "", None
    for line in text.splitlines():
        if line.startswith("### "):
            title = line[4:].strip()
            low = title.lower()
            major = "mayor" in low or ("menor" not in low and "mayor" in section)
            current = {"title": title, "major": major, "cites": []}
            out.append(current)
        elif line.startswith(("## ", "# ")):
            section, current = line.lower(), None
        elif current is not None and line.startswith("Evidencia:"):
            current["cites"] += citations(line)
    return out


def hits(finding: dict, locations: list[dict]) -> bool:
    for parts, a, b in finding["cites"]:
        for loc in locations:
            lp = _norm(loc["file"])
            n = min(len(parts), len(lp))
            if not n or parts[-n:] != lp[-n:]:
                continue
            if loc.get("any_line"):
                return True
            lo, hi = loc["lines"]
            if a is not None and a <= hi + TOL and b >= lo - TOL:
                return True
    return False


def format_ok(report_text: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        rel = "papers/x/audits/report.md"
        (Path(tmp) / rel).parent.mkdir(parents=True)
        (Path(tmp) / rel).write_text(report_text, encoding="utf-8")
        return not check_referee(Path(tmp), [rel])


def grade(report_text: str | None, case: dict, known: list[dict], commands: list[str],
          replication_files: list[str]) -> dict:
    """Puntuación de un informe. `commands`: comandos Bash de la sesión; `replication_files`: rutas en replication_*/."""
    text = report_text or ""
    verdict = (front_matter(text) or {}).get("verdict")
    major = [f for f in findings(text) if f["major"]]
    locations = case.get("locations") or []
    integrity_runs = [c for c in commands if "tools/integrity.py" in c.replace("\\", "/") and "--only" not in c]
    out = {
        "verdict": verdict,
        "verdict_ok": verdict in case["verdicts"],
        "detected": any(hits(f, locations) for f in major) if locations else None,
        "false_positives": sum(not hits(f, known) for f in major) if not locations else None,
        "format_ok": bool(report_text) and format_ok(text),
        "ran_integrity": bool(integrity_runs),
        "ran_pytest": any(re.search(r"\bpytest\b", c) for c in commands),
        "replication": any(Path(f).suffix in SCRIPT_SUFFIXES for f in replication_files),
    }
    out["protocol_ok"] = all(out[k] for k in ("format_ok", "ran_integrity", "ran_pytest", "replication"))
    return out


def bash_commands(transcript: Path | None) -> list[str]:
    """Comandos Bash que la sesión ejecutó, según su transcripción de Claude Code (jsonl)."""
    if transcript is None or not transcript.exists():
        return []
    cmds = []
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            msg = json.loads(line).get("message")
        except json.JSONDecodeError:
            continue
        content = msg.get("content") if isinstance(msg, dict) else None
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "Bash":
                cmds.append(str(item.get("input", {}).get("command", "")))
    return cmds
