"""Construye el repo temporal de un caso de la eval del Referee: base + overlay del caso + infraestructura real.

Uso:
  uv run python evals/referee/build.py <caso> [destino]   # C0 = la base sin cambios; imprime la ruta del repo
  uv run python evals/referee/build.py regen <caso>       # regenera por código data/clean y output/ de la base o del caso

El repo queda fuera de OneDrive (%TEMP%/referee-eval/) y sin nada de evals/: ni case.yaml ni KNOWN_ISSUES.yaml. Tiene dos
commits con mensajes neutros, como un paper real: el del prerregistro (fecha y autor fijos, así que su hash es el mismo en
todas las construcciones; a él apuntan `prereg_commit` del SPEC y la columna `commit` de spec_log.csv) y el del trabajo
que se audita.
"""

from __future__ import annotations

import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EVAL = Path(__file__).resolve().parent
BASE = EVAL / "base"
CASES = EVAL / "cases"
SLUG = "p07-credit"
PAPER = f"papers/{SLUG}"
WORKDIR = Path(tempfile.gettempdir()) / "referee-eval"
INFRA = [
    "CLAUDE.md", ".gitignore", "pyproject.toml", "uv.lock",
    ".claude/settings.json", ".claude/hooks/guard.js", ".claude/agents/referee.md",
    ".claude/skills/referee-report/SKILL.md", ".claude/skills/sympy-check/SKILL.md",
    ".claude/skills/mc-validate/SKILL.md",
    "tools/integrity.py", "tools/research.py", "tools/symcheck.py", "tools/mc.py",
]
PREREG_LINE = "prereg_commit: {PREREG_COMMIT}"
GENERATED = ["data/clean", "output"]  # lo que produce el pipeline del paper
GIT_ID = {"GIT_AUTHOR_NAME": "Research Desk", "GIT_AUTHOR_EMAIL": "desk@research.local",
          "GIT_COMMITTER_NAME": "Research Desk", "GIT_COMMITTER_EMAIL": "desk@research.local"}


def case_ids() -> list[str]:
    return sorted(p.name for p in CASES.iterdir() if (p / "case.yaml").exists())


def load_case(case: str) -> dict:
    return yaml.safe_load((CASES / case / "case.yaml").read_text(encoding="utf-8"))


def rscript() -> str | None:
    found = shutil.which("Rscript")
    default = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "R" / "R-4.5.1" / "bin" / "Rscript.exe"
    return found or (str(default) if default.exists() else None)


def env() -> dict[str, str]:
    """Entorno para el pipeline y la sesión: el .venv del repo real (pyproject y uv.lock son idénticos) y R en el PATH."""
    out = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(ROOT / ".venv")}
    if (r := rscript()) and not shutil.which("Rscript"):
        out["PATH"] = str(Path(r).parent) + os.pathsep + out.get("PATH", "")
    return out


def _git(dest: Path, *args: str, date: str | None = None) -> str:
    e = {**os.environ, **GIT_ID}
    if date:
        e |= {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    r = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args], cwd=dest,
                       env=e, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def tree(case: str, dest: Path) -> None:
    """Copia infraestructura, base y overlay en `dest` (sin git)."""
    for rel in INFRA:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest / rel)
    pyproject = dest / "pyproject.toml"  # evals/ no existe en el repo temporal
    pyproject.write_text(pyproject.read_text(encoding="utf-8").replace(', "evals"', ""), encoding="utf-8")
    shutil.copytree(BASE / "papers", dest / "papers", dirs_exist_ok=True)
    if case != "C0":
        overlay = CASES / case / "overlay"
        if not overlay.is_dir():
            raise SystemExit(f"no existe {overlay}")
        shutil.copytree(overlay, dest, dirs_exist_ok=True)


def build(case: str, dest: Path | None = None) -> Path:
    """Repo temporal del caso con sus dos commits. Devuelve la ruta."""
    dest = dest or WORKDIR / f"{case}-{uuid.uuid4().hex[:8]}"
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"{dest} ya existe y no está vacío")
    dest.mkdir(parents=True, exist_ok=True)
    tree(case, dest)
    spec = dest / PAPER / "SPEC.md"
    text = spec.read_text(encoding="utf-8")
    if PREREG_LINE not in text:
        raise SystemExit(f"{spec} no tiene la línea '{PREREG_LINE}'")
    _git(dest, "init", "-q", "-b", "main")
    spec.write_text(text.replace(PREREG_LINE + "\n", ""), encoding="utf-8")
    _git(dest, "add", f"{PAPER}/SPEC.md")
    _git(dest, "commit", "-q", "-m", f"{SLUG}: pregunta, diseño y prerregistro", date="2026-10-20T10:00:00+02:00")
    sha = _git(dest, "rev-parse", "--short", "HEAD")
    spec.write_text(text.replace(PREREG_LINE, f"prereg_commit: {sha} (aprobación de los autores, 2026-10-20)"),
                    encoding="utf-8")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-q", "-m", f"{SLUG}: datos, LP, replicación en R, Monte Carlo y borrador")
    return dest


PIPELINE = [
    ["uv", "run", "python", f"{PAPER}/code/data/build_panel.py"],
    ["uv", "run", "python", f"{PAPER}/code/analysis/lp.py"],
    ["RSCRIPT", f"{PAPER}/code/replication_r/lp.R"],
    ["uv", "run", "python", f"{PAPER}/code/mc/mc_lp.py"],
]


def regen(case: str) -> None:
    """Ejecuta el pipeline del paper en un repo temporal y trae data/clean y output/ a la base (C0) o al overlay."""
    if case != "C0" and load_case(case).get("regen") is False:
        raise SystemExit(f"{case} declara regen: false (sus salidas son a propósito de otro run)")
    r = rscript()
    if not r:
        raise SystemExit("no encuentro Rscript")
    with tempfile.TemporaryDirectory() as tmp:
        dest = build(case, Path(tmp) / "repo")
        # Como en un paper real, los resultados se calculan sobre el commit del prerregistro (spec_log.csv lo registra).
        _git(dest, "reset", "-q", "--soft", "HEAD~1")
        for rel in GENERATED:
            for f in (dest / PAPER / rel).glob("*"):
                f.unlink()
        for cmd in PIPELINE:
            subprocess.run([r if c == "RSCRIPT" else c for c in cmd], cwd=dest, env=env(), check=True)
        for rel in GENERATED:
            for f in sorted((dest / PAPER / rel).glob("*")):
                base_f = BASE / PAPER / rel / f.name
                target = base_f if case == "C0" else CASES / case / "overlay" / PAPER / rel / f.name
                if case != "C0" and base_f.exists() and filecmp.cmp(f, base_f, shallow=False):
                    target.unlink(missing_ok=True)  # igual que la base: no hace falta en el overlay
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
                print(f"regenerado {target.relative_to(EVAL).as_posix()}")


def marker_errors(case: dict, repo: Path) -> list[str]:
    """Ubicaciones cuyo `marker` no está en su rango de líneas del repo construido."""
    out = []
    for loc in case.get("locations") or []:
        path = repo / loc["file"]
        if not path.exists():
            out.append(f"{loc['file']}: no existe")
            continue
        lo, hi = loc["lines"]
        lines = path.read_text(encoding="utf-8").splitlines()[lo - 1:hi]
        if not any(loc["marker"] in ln for ln in lines):
            out.append(f"{loc['file']}:{lo}-{hi}: no contiene {loc['marker']!r}")
    return out


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "regen":
        regen(argv[1])
    elif len(argv) in (1, 2) and re.fullmatch(r"C\d+", argv[0]):
        print(build(argv[0], Path(argv[1]) if len(argv) == 2 else None))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
