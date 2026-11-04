"""Utilidades de disciplina de investigación para los scripts de análisis de los papers.

- log_spec(): registra cada especificación estimada en output/spec_log.csv. Una especificación que no está en
  el bloque ```prereg``` del SPEC solo se puede registrar como exploratoria.
- open_holdout(): abre la muestra reservada (data/holdout/) una única vez y deja constancia con el commit.

Las comprueba tools/integrity.py (checks 'speclog') y el hook .claude/hooks/guard.js (holdout).
"""

from __future__ import annotations

import csv
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from integrity import SPECLOG_COLUMNS, prereg_ids

HOLDOUT_MARKER = "audits/holdout_opened.md"


class SpecNotPreregistered(ValueError):
    """La especificación no está prerregistrada y no se ha declarado exploratoria."""


class HoldoutAlreadyOpened(RuntimeError):
    """La muestra reservada ya se abrió: no se puede volver a abrir."""


def _commit(cwd: Path) -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd,
                             capture_output=True, text=True, check=True)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=cwd,
                               capture_output=True, text=True, check=True).stdout.strip()
        return out.stdout.strip() + ("-dirty" if dirty else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "sin-git"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_spec(paper_dir: Path | str, spec_id: str, script: str, description: str,
             exploratory: bool = False) -> None:
    """Añade una fila a output/spec_log.csv. Llamar en cada script de estimación, por cada especificación."""
    paper = Path(paper_dir)
    spec = paper / "SPEC.md"
    is_prereg = spec_id in prereg_ids(spec.read_text(encoding="utf-8")) if spec.exists() else False
    if not is_prereg and not exploratory:
        raise SpecNotPreregistered(
            f"'{spec_id}' no está en el bloque prereg de {spec}; regístrala con exploratory=True")
    log = paper / "output" / "spec_log.csv"
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(SPECLOG_COLUMNS)
        w.writerow([_now(), _commit(paper), script, spec_id, is_prereg, not is_prereg, description])


def open_holdout(paper_dir: Path | str, reason: str) -> Path:
    """Abre data/holdout/ una sola vez: exige prerregistro no vacío y deja el registro en audits/."""
    paper = Path(paper_dir)
    marker = paper / HOLDOUT_MARKER
    if marker.exists():
        raise HoldoutAlreadyOpened(f"ya se abrió: ver {marker}")
    spec = paper / "SPEC.md"
    ids = prereg_ids(spec.read_text(encoding="utf-8")) if spec.exists() else set()
    if not ids:
        raise SpecNotPreregistered("no se abre el holdout sin un bloque prereg no vacío en el SPEC")
    if not reason.strip():
        raise ValueError("hace falta un motivo")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        f"# Apertura de la muestra reservada\n\n- Fecha: {_now()}\n- Commit: {_commit(paper)}\n"
        f"- Especificaciones prerregistradas: {', '.join(sorted(ids))}\n- Motivo: {reason}\n",
        encoding="utf-8")
    return paper / "data" / "holdout"
