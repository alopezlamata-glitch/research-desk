"""Ejecuta casos de la eval del Referee: construye el repo, lanza al Referee como lo lanza desk.py, recoge y puntúa.

Uso:
  uv run python evals/referee/run.py --set dev|val | --case C1 [--reps N] [--model opus] [--dry-run]

Cada ejecución lanza una sesión síncrona del Referee en papers/p07-credit/audits/ del repo temporal, con las herramientas
de su perfil (desk.TOOLS, desk.builtin_tools, desk.LEAN_CONTEXT) y un session_id fijo; ocupa el puesto de la desk
`referee` (desk.check_can_launch: máximo de desks activas y memoria) mientras dura. Añade una fila por ejecución a
evals/referee/RESULTS.csv y deja el repo temporal para revisarlo a mano.

--dry-run sustituye `claude` por fake_claude.py, usa una carpeta de desks y una configuración de Claude temporales, y
escribe en RESULTS_dry-run.csv dentro de %TEMP%/referee-eval/: no gasta cuota ni bloquea a las desks reales.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

import build
import grade
import integrity

desk = build.desk
EVAL = build.EVAL
RESULTS = EVAL / "RESULTS.csv"
FIELDS = ["date", "commit", "case", "set", "rep", "model", "verdict", "verdict_ok", "detected", "false_positives",
          "protocol_ok", "format_ok", "ran_integrity", "ran_pytest", "replication", "tokens_in", "tokens_out",
          "peak_ctx", "minutes", "session_id", "repo"]
TIMEOUT_S = 2 * 3600
PROMPT = ("Eres el Referee de esta desk (rol en ../../../.claude/agents/referee.md). Audita el resultado principal del "
          "borrador ../draft/main.tex antes de que pase a paper/ (Redacción): el código, los datos, la teoría y el texto "
          "del paper p07-credit en el commit actual. Escribe el informe en esta carpeta con el formato de "
          "../../../.claude/skills/referee-report/SKILL.md. Al final, resume en 10 líneas el veredicto y por qué.")


class SessionFailed(RuntimeError):
    """La sesión no llegó a auditar (límite de la suscripción, error de la API): no se puntúa ni se anota."""


def session_error(stdout: str, returncode: int) -> str | None:
    """Motivo por el que la sesión falló, según la salida JSON de `claude -p`; None si terminó bien."""
    try:
        out = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else {}
    except json.JSONDecodeError:
        out = {}
    if out.get("is_error") or out.get("terminal_reason") == "api_error":
        return str(out.get("result") or out.get("terminal_reason") or "error de la API")
    return None if returncode == 0 and out else f"claude salió con código {returncode} y sin resultado JSON"


def cases_for(selected_set: str | None, case: str | None) -> list[str]:
    if case:
        return [case]
    return [c for c in build.case_ids() if selected_set in build.load_case(c)["sets"]]


def claude_args(exe: list[str], session_id: str, model: str, repo: Path) -> list[str]:
    """Los de desk._start, más `--add-dir` del repo (las desks lo tienen en additionalDirectories) y salida JSON."""
    return exe + ["-p", PROMPT, "--session-id", session_id, "--model", model, "--permission-mode", "acceptEdits",
                  "--add-dir", str(repo),
                  "--allowedTools", " ".join(desk.TOOLS["referee"]), *desk.LEAN_CONTEXT,
                  "--tools", ",".join(desk.builtin_tools("referee")), "--output-format", "json"]


def latest_report(audits: Path) -> str | None:
    reports = [p for p in audits.glob("*.md") if not integrity.REFEREE_SKIP.match(p.name)]
    return max(reports, key=lambda p: p.stat().st_mtime).read_text(encoding="utf-8") if reports else None


def run_one(case: str, rep: int, model: str, exe: list[str], *, desks_dir: Path, transcripts: Path,
            extra_env: dict[str, str] | None = None) -> dict:
    """Una ejecución: construye, lanza (ocupando el puesto de la desk referee), recoge y puntúa. Devuelve la fila."""
    desk.check_can_launch("referee", desks_dir)
    build.load_case(case)  # falla antes de construir si el caso no existe o su clave está mal
    repo = build.build(case)
    audits = repo / build.PAPER / "audits"
    session_id = str(uuid.uuid4())
    lock = desks_dir / "referee" / ".lock"
    lock.write_text(json.dumps({"pid": os.getpid(), "encargo": f"eval {case} rep {rep}", "model": model,
                                "started": datetime.now().strftime("%Y-%m-%d_%H%M"), "session_id": session_id}),
                    encoding="utf-8")
    try:
        proc = subprocess.run(claude_args(exe, session_id, model, repo), cwd=audits, env={**build.env(), **(extra_env or {})},
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=TIMEOUT_S, check=False)  # cp1252 por defecto rompía con caracteres UTF-8
    finally:
        lock.unlink(missing_ok=True)
    (repo.parent / f"{repo.name}.session.json").write_text(proc.stdout or proc.stderr, encoding="utf-8")
    if reason := session_error(proc.stdout or "", proc.returncode):
        raise SessionFailed(f"{case} rep {rep}: {reason}")
    return score(case, rep, model, repo, session_id, transcripts)


def score(case: str, rep: int, model: str, repo: Path, session_id: str, transcripts: Path) -> dict:
    """Puntúa una sesión ya terminada a partir de su repo temporal y su transcripción. Devuelve la fila."""
    key = build.load_case(case)
    audits = repo / build.PAPER / "audits"
    transcript = next(iter(sorted(transcripts.glob(f"*/{session_id}.jsonl"))), None)
    replication = [p.relative_to(repo).as_posix() for p in audits.glob("replication_*/**/*") if p.is_file()]
    known = grade.load_yaml(build.BASE / "KNOWN_ISSUES.yaml").get("issues") or []
    score = grade.grade(latest_report(audits), key, known, grade.bash_commands(transcript), replication)
    usage = desk.session_usage(session_id, transcripts) or {}
    return {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "commit": build._git(build.ROOT, "rev-parse", "--short",
            "HEAD"), "case": case, "set": "+".join(key["sets"]), "rep": rep, "model": model, **score,
            "tokens_in": usage.get("input", 0) + usage.get("cache_write", 0) + usage.get("cache_read", 0),
            "tokens_out": usage.get("output", 0), "peak_ctx": usage.get("peak_ctx", 0),
            "minutes": usage.get("minutes", 0.0), "session_id": session_id, "repo": str(repo)}


def append_result(row: dict, path: Path) -> None:
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--set", choices=["dev", "val"])
    group.add_argument("--case")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--model", default=desk.DEFAULT_MODEL["referee"], choices=desk.MODELS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rescore", nargs=2, metavar=("REPO", "SESSION_ID"),
                    help="puntúa una sesión ya hecha (con --case) sin lanzar otra, p. ej. si falló la lectura de su salida")
    a = ap.parse_args(argv)
    if a.rescore:
        if not a.case:
            print("--rescore necesita --case")
            return 2
        row = score(a.case, 1, a.model, Path(a.rescore[0]), a.rescore[1], desk.TRANSCRIPTS)
        append_result(row, RESULTS)
        print(f"{a.case} puntuado: veredicto {row['verdict']} (ok={row['verdict_ok']}), detectado {row['detected']}, "
              f"falsos positivos {row['false_positives']}, protocolo {row['protocol_ok']}")
        return 0
    if a.dry_run:
        scratch = build.WORKDIR / f"dry-run-{uuid.uuid4().hex[:8]}"
        (scratch / "desks" / "referee").mkdir(parents=True)
        config = scratch / "claude-config"
        exe, desks_dir, transcripts = [sys.executable, str(EVAL / "fake_claude.py")], scratch / "desks", config / "projects"
        extra_env, results = {"CLAUDE_CONFIG_DIR": str(config)}, build.WORKDIR / "RESULTS_dry-run.csv"
    else:
        if not build.rscript():
            print("No se lanza: no encuentro Rscript (el Referee no podría replicar en R).")
            return 1
        exe, desks_dir, transcripts, extra_env, results = desk.claude_cmd(), desk.DESKS, desk.TRANSCRIPTS, None, RESULTS
    try:
        for case in cases_for(a.set, a.case):
            for rep in range(1, a.reps + 1):
                row = run_one(case, rep, a.model, exe, desks_dir=desks_dir, transcripts=transcripts,
                              extra_env=extra_env)
                append_result(row, results)
                print(f"{case} rep {rep}: veredicto {row['verdict']} (ok={row['verdict_ok']}), detectado "
                      f"{row['detected']}, falsos positivos {row['false_positives']}, protocolo {row['protocol_ok']}, "
                      f"{row['tokens_out']} tokens de salida, {row['minutes']} min · {row['repo']}")
    except desk.LaunchRefused as e:
        print(f"No se lanza: {e}")
        return 1
    except SessionFailed as e:  # p. ej., límite de la suscripción: seguir solo produciría filas falsas
        print(f"Se para sin anotar: {e}")
        return 1
    print(f"Resultados en {results}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
