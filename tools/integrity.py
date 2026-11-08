"""Comprobaciones deterministas de integridad de la Research Desk.

Cada regla comprobable de CLAUDE.md es una función `check_<id>(root, files) -> list[Violation]`.
El pre-commit de git, pytest y las desks llaman a estas mismas funciones (spec: specs/guardrails/SPEC.md).

Uso: uv run python tools/integrity.py [--only id1,id2]   (sale con 1 si hay violaciones)
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".tex", ".bib", ".json", ".toml", ".yaml", ".yml", ".txt", ".csv",
                 ".js", ".mjs", ".sh", ".ps1", ".R", ".r", ".ipynb", ".cfg", ".ini", ""}


@dataclass(frozen=True)
class Violation:
    check: str
    path: str
    line: int
    msg: str

    def __str__(self) -> str:
        return f"[{self.check}] {self.path}:{self.line}: {self.msg}"


def repo_files(root: Path) -> list[str]:
    """Archivos versionados o preparados (git); sin git, todos menos los ignorables obvios."""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             cwd=root, capture_output=True, check=True).stdout
        return [p for p in out.decode("utf-8").split("\0") if p and (root / p).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        skip = {".git", ".venv", "__pycache__", "node_modules"}
        return [p.relative_to(root).as_posix() for p in root.rglob("*")
                if p.is_file() and not skip & set(p.relative_to(root).parts)]


def _read(root: Path, rel: str) -> str | None:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


# ---------------------------------------------------------------- secrets
SECRET_PATTERNS = [
    re.compile(r"""(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key|password|passwd)\b\s*[:=]\s*['"][A-Za-z0-9_\-]{16,}['"]"""),
    re.compile(r"\b(?:ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9\-_]{24,}"),
    re.compile(r"""['"][0-9a-f]{32}['"]"""),  # formato de clave FRED
]
SECRET_SKIP = {"uv.lock"}


def check_secrets(root: Path, files: list[str]) -> list[Violation]:
    real_key = os.environ.get("FRED_API_KEY", "")
    out = []
    for rel in files:
        if Path(rel).name in SECRET_SKIP or Path(rel).suffix not in TEXT_SUFFIXES:
            continue
        text = _read(root, rel)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if (len(real_key) >= 16 and real_key in line) or any(p.search(line) for p in SECRET_PATTERNS):
                out.append(Violation("secrets", rel, n, "posible clave/token en un archivo versionado"))
    return out


# ---------------------------------------------------------------- hygiene
HYGIENE_SCOPE = re.compile(r"^(papers/[^/]+/code/|datalake/fetch/).+\.py$")
HYGIENE_RULES = [
    (re.compile(r"\.bfill\(|\.backfill\(|method\s*=\s*['\"](?:bfill|backfill)['\"]"),
     "relleno hacia atrás (usa información futura)"),
    (re.compile(r"\.interpolate\("), "interpolación (inventa datos entre observaciones)"),
]
WAIVER = re.compile(r"#\s*hygiene-ok:\s*\S")


def check_hygiene(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for rel in files:
        if not HYGIENE_SCOPE.match(rel):
            continue
        for n, line in enumerate((_read(root, rel) or "").splitlines(), 1):
            if "TODO_SERIE_REAL" in line:
                out.append(Violation("hygiene", rel, n, "marcador TODO_SERIE_REAL sin sustituir"))
            for pat, why in HYGIENE_RULES:
                if pat.search(line) and not WAIVER.search(line):
                    out.append(Violation("hygiene", rel, n, f"{why}; justifícalo con '# hygiene-ok: <motivo>'"))
    return out


# ---------------------------------------------------------------- bib / tex helpers
def parse_bib(text: str) -> dict[str, dict[str, str]]:
    """Entradas BibTeX -> {clave: {campo: valor}}; respeta llaves anidadas."""
    entries: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in {"comment", "string", "preamble"}:
            continue
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body, fields = text[m.end():i - 1], {}
        for f in re.finditer(r"(\w+)\s*=\s*\{", body):
            d, j = 1, f.end()
            while j < len(body) and d:
                d += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
            fields[f.group(1).lower()] = body[f.end():j - 1].strip()
        entries[m.group(2)] = fields
    return entries


def strip_tex_comments(line: str) -> str:
    return re.sub(r"(?<!\\)%.*$", "", line)


CITE = re.compile(r"\\(?:[Cc]ite[a-zA-Z]*|nocite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")


def _paper_tex(files: list[str]) -> list[str]:
    return [f for f in files if re.match(r"^papers/[^/]+/paper/.+\.tex$", f)]


def check_citations(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for rel in _paper_tex(files):
        paper_dir = (root / rel).parent
        bib = {}
        for b in paper_dir.glob("*.bib"):
            bib.update(parse_bib(b.read_text(encoding="utf-8")))
        for n, raw in enumerate((_read(root, rel) or "").splitlines(), 1):
            for m in CITE.finditer(strip_tex_comments(raw)):
                for key in (k.strip() for k in m.group(1).split(",")):
                    if not key or key == "*":
                        continue
                    if key not in bib:
                        out.append(Violation("citations", rel, n, f"'{key}' no está en el .bib del paper"))
                    elif not bib[key].get("note", "").upper().startswith("VERIFICADA"):
                        estado = bib[key].get("note", "sin estado")[:40]
                        out.append(Violation("citations", rel, n, f"'{key}' no está VERIFICADA ({estado})"))
    return out


# ---------------------------------------------------------------- numbers
NUM_STRIP = re.compile(
    r"\\(?:ref|eqref|label|cite[a-zA-Z]*|input|include|includegraphics|url|href|bibliography|"
    r"bibliographystyle|vspace|hspace|setlength|addtolength|usepackage|documentclass|geometry)"
    r"\*?(?:\[[^\]]*\])*\{[^}]*\}(?:\{[^}]*\})?"
)
DECIMAL = re.compile(r"(?<![\w.\\])\d+\.\d+(?![\w.])")
PERCENT = re.compile(r"(?<![\w.\\])\d+(?:\.\d+)?\s*\\%")


def check_numbers(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for rel in _paper_tex(files):
        in_body = False
        for n, raw in enumerate((_read(root, rel) or "").splitlines(), 1):
            if "\\begin{document}" in raw:
                in_body = True
                continue
            if not in_body or "% num-ok" in raw:
                continue
            line = NUM_STRIP.sub("", strip_tex_comments(raw))
            for m in list(DECIMAL.finditer(line)) + list(PERCENT.finditer(line)):
                out.append(Violation("numbers", rel, n,
                                     f"cifra tecleada '{m.group(0)}': genérala como macro desde output/ "
                                     "(o marca la línea con '% num-ok' si no es un resultado)"))
    return out


# ---------------------------------------------------------------- parity
PARITY_RTOL = 1e-6


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_parity(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for py in sorted(root.glob("papers/*/output/estimates_py.csv")):
        rel = py.relative_to(root).as_posix()
        r = py.with_name("estimates_r.csv")
        if not r.exists():
            out.append(Violation("parity", rel, 0, "falta estimates_r.csv (replicación cruzada en R)"))
            continue
        key = lambda row: (row["spec_id"], row["term"])
        a = {key(x): x for x in _read_csv(py)}
        b = {key(x): x for x in _read_csv(r)}
        for k in sorted(a.keys() ^ b.keys()):
            out.append(Violation("parity", rel, 0, f"{k} solo existe en {'Python' if k in a else 'R'}"))
        for k in sorted(a.keys() & b.keys()):
            for col in ("estimate", "std_error"):
                x, y = float(a[k][col]), float(b[k][col])
                if abs(x - y) > PARITY_RTOL * max(1.0, abs(x)):
                    out.append(Violation("parity", rel, 0, f"{k} {col}: Python {x!r} ≠ R {y!r}"))
    return out


# ---------------------------------------------------------------- speclog
SPECLOG_COLUMNS = ["timestamp", "commit", "script", "spec_id", "preregistered", "exploratory", "description",
                   "prereg"]


def prereg_ids(spec_text: str) -> set[str]:
    """Ids del bloque ```prereg ... ``` del SPEC (una por línea; '#' comenta)."""
    ids: set[str] = set()
    for block in re.findall(r"```prereg\s*\n(.*?)```", spec_text, re.DOTALL):
        ids |= {ln.split("#")[0].strip() for ln in block.splitlines()} - {""}
    return ids


def prereg_text(spec_text: str) -> str | None:
    """Texto congelado: del último encabezado `## ` anterior al bloque prereg al cierre del bloque, normalizado."""
    end = re.search(r"```prereg\s*\n.*?```", spec_text, re.DOTALL)
    if not end:
        return None
    start = max((m.start() for m in re.finditer(r"^## ", spec_text[:end.start()], re.MULTILINE)), default=0)
    return "\n".join(ln.rstrip() for ln in spec_text[start:end.end()].replace("\r\n", "\n").splitlines())


def prereg_hash(spec_text: str) -> str:
    """Huella de 12 hex del texto congelado ('' si el SPEC no tiene bloque prereg)."""
    text = prereg_text(spec_text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12] if text is not None else ""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    except FileNotFoundError:
        return None


def check_speclog(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for paper in sorted(p for p in root.glob("papers/*") if p.is_dir() and p.name != "_template"):
        log = paper / "output" / "spec_log.csv"
        est = paper / "output" / "estimates_py.csv"
        spec = paper / "SPEC.md"
        prereg = prereg_ids(spec.read_text(encoding="utf-8")) if spec.exists() else set()
        rows = _read_csv(log) if log.exists() else []
        rel = log.relative_to(root).as_posix()
        logged = {r["spec_id"] for r in rows}
        if est.exists():
            for sid in sorted({r["spec_id"] for r in _read_csv(est)} - logged):
                out.append(Violation("speclog", rel, 0, f"'{sid}' estimada pero no registrada (usa research.log_spec)"))
        for n, r in enumerate(rows, 2):
            is_prereg = r["spec_id"] in prereg
            if r["preregistered"].lower() != str(is_prereg).lower():
                out.append(Violation("speclog", rel, n, f"'{r['spec_id']}': preregistered={r['preregistered']} no coincide con el SPEC"))
            if not is_prereg and r["exploratory"].lower() != "true":
                out.append(Violation("speclog", rel, n, f"'{r['spec_id']}' no está prerregistrada y no va marcada como exploratoria"))
    return out


# ---------------------------------------------------------------- prereg
def check_prereg(root: Path, files: list[str]) -> list[Violation]:
    """El prerregistro congelado en `prereg_commit` solo cambia con una Desviación que declare la huella nueva."""
    out = []
    for paper in sorted(p for p in root.glob("papers/*") if p.is_dir() and p.name != "_template"):
        spec = paper / "SPEC.md"
        text = spec.read_text(encoding="utf-8") if spec.exists() else ""
        if not prereg_ids(text):
            continue  # sin prerregistro todavía (Fase 0)
        rel = spec.relative_to(root).as_posix()
        m = re.search(r"^\W*prereg_commit\W+([0-9a-f]{7,40})\b", text, re.MULTILINE)
        if not m:
            out.append(Violation("prereg", rel, 0, "hay bloque prereg sin `prereg_commit: <sha>` del commit aprobado"))
            continue
        frozen = _git(root, "show", f"{m.group(1)}:{rel}")
        if frozen is None or frozen.returncode != 0:
            out.append(Violation("prereg", rel, 0, f"no encuentro {rel} en el commit {m.group(1)} (prereg_commit)"))
            continue
        current = prereg_hash(text)
        if current == prereg_hash(frozen.stdout.decode("utf-8")):
            continue
        deviations = text.partition("\n## Desviaciones")[2]
        if not re.search(rf"\bprereg\W+{current}\b", deviations):
            out.append(Violation("prereg", rel, 0, f"el prerregistro cambió desde {m.group(1)} sin Desviación: si lo "
                                 f"aprueban los autores, añade a su entrada fechada `prereg {current}`"))
    return out


# ---------------------------------------------------------------- referee
VERDICTS = {"APROBADO", "APROBADO CON CAMBIOS", "RECHAZADO"}
REFEREE_SKIP = re.compile(r"^(README|_|holdout_opened)", re.IGNORECASE)


def front_matter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    return {k.strip(): v.strip().strip("'\"") for k, _, v in
            (ln.partition(":") for ln in m.group(1).splitlines() if ":" in ln)}


def check_referee(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for rel in files:
        if not re.match(r"^papers/[^/]+/audits/[^/]+\.md$", rel) or REFEREE_SKIP.match(Path(rel).name):
            continue
        text = _read(root, rel) or ""
        fm = front_matter(text)
        if fm is None:
            out.append(Violation("referee", rel, 1, "falta la cabecera YAML (ver skill referee-report)"))
            continue
        if fm.get("verdict") not in VERDICTS:
            out.append(Violation("referee", rel, 1, f"verdict inválido: {fm.get('verdict')!r}"))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm.get("date", "")):
            out.append(Violation("referee", rel, 1, "date debe ser AAAA-MM-DD"))
        if not re.fullmatch(r"[0-9a-f]{7,40}", fm.get("commit", "")):
            out.append(Violation("referee", rel, 1, "commit auditado ausente o inválido"))
        if fm.get("session") != "fresh" or fm.get("reviewer") != "referee" or not fm.get("object"):
            out.append(Violation("referee", rel, 1, "requiere object, reviewer: referee y session: fresh"))
        for f in re.finditer(r"^### (.+)$((?:\n(?!#{1,3} ).*)*)", text, re.MULTILINE):
            if not re.search(r"^Evidencia:.*(`[^`]+`|\S+:\d+)", f.group(2), re.MULTILINE):
                line = text[:f.start()].count("\n") + 1
                out.append(Violation("referee", rel, line, f"hallazgo '{f.group(1)[:50]}' sin 'Evidencia:' (comando o archivo:línea)"))
    return out


# ---------------------------------------------------------------- gate
APPROVED = {"APROBADO", "APROBADO CON CAMBIOS"}
USES_OUTPUT = re.compile(r"\\(?:input|include|includegraphics)(?:\[[^\]]*\])?\{[^}]*\boutput/")


# Lo que audita el Referee. Un cambio aquí después del commit auditado invalida la aprobación; uno en paper/ (redacción),
# TASKS.md o audits/ no. Git ya guarda el hash de cada archivo: comparar commits basta para ligar la aprobación al objeto.
SCIENTIFIC = ("code", "data", "output", "theory", "SPEC.md")


def _approval_holds(root: Path, paper: str, fm: dict | None) -> bool:
    """Informe APROBADO de un commit antecesor de HEAD, sin cambios científicos del paper desde entonces."""
    if not (fm and fm.get("verdict") in APPROVED and re.fullmatch(r"[0-9a-f]{7,40}", fm.get("commit", ""))):
        return False
    r = _git(root, "merge-base", "--is-ancestor", fm["commit"], "HEAD")
    if not r or r.returncode != 0:
        return False
    # Contra el árbol de trabajo, no contra HEAD: así cuenta también lo que entra en el commit que se está haciendo.
    d = _git(root, "diff", "--name-only", fm["commit"], "--", *(f"papers/{paper}/{s}" for s in SCIENTIFIC))
    return bool(d) and d.returncode == 0 and not d.stdout.strip()


def check_gate(root: Path, files: list[str]) -> list[Violation]:
    """Ningún resultado (`output/`) entra en un .tex sin un informe APROBADO vigente: de un commit antecesor de HEAD y
    sin cambios en `code/`, `data/`, `output/`, `theory/` ni `SPEC.md` del paper desde ese commit."""
    out = []
    approved_by_paper: dict[str, bool] = {}
    for rel in _paper_tex(files):
        lines = [strip_tex_comments(ln) for ln in (_read(root, rel) or "").splitlines()]
        n = next((i for i, ln in enumerate(lines, 1) if USES_OUTPUT.search(ln)), 0)
        if not n:
            continue
        paper = rel.split("/")[1]
        if paper == "_template":
            continue
        if paper not in approved_by_paper:
            approved_by_paper[paper] = any(
                _approval_holds(root, paper, front_matter(_read(root, a) or ""))
                for a in files if re.match(rf"^papers/{re.escape(paper)}/audits/[^/]+\.md$", a))
        if not approved_by_paper[paper]:
            out.append(Violation("gate", rel, n, "usa resultados de output/ sin un informe APROBADO vigente del Referee "
                                 "en audits/ (de un commit antecesor de HEAD y sin cambios en code/, data/, output/, "
                                 "theory/ ni SPEC.md desde ese commit)"))
    return out


# ---------------------------------------------------------------- rawhash
RAW_SKIP = {"MANIFEST.csv", ".gitkeep", "meta.json"}  # meta.json: metadatos de save_long, no datos
VINTAGE = re.compile(r"\.([0-9a-f]{12})(\.[^./]*)?$")  # _vintages/<stem>.<sha12><suffix>


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def raw_manifests(root: Path) -> list[tuple[Path, str, Path]]:
    """(MANIFEST, columna de la ruta, carpeta a la que es relativa) del datalake y de cada paper."""
    out = [(root / "datalake" / "MANIFEST.csv", "path", root / "datalake")]
    out += [(m, "file", m.parent) for m in sorted(root.glob("papers/*/data/raw/MANIFEST.csv"))]
    return [t for t in out if t[0].exists()]


def check_rawhash(root: Path, files: list[str]) -> list[Violation]:
    """Cada archivo de raw/ coincide con la última fila de su MANIFEST; los vintages, con el hash de su nombre.

    raw/ no está en git: un archivo que falta no es violación (se regenera con los scripts de descarga).
    """
    out = []
    for manifest, col, base in raw_manifests(root):
        last = {r[col]: r["sha256"] for r in _read_csv(manifest)}
        raw_dir = base / "raw" if col == "path" else base
        for p in sorted(raw_dir.rglob("*")):
            if not p.is_file() or p.name in RAW_SKIP or "__pycache__" in p.parts:
                continue
            rel, shown = p.relative_to(base).as_posix(), p.relative_to(root).as_posix()
            if "_vintages" in p.parts:
                m = VINTAGE.search(p.name)
                if not m or not _sha256(p).startswith(m.group(1)):
                    out.append(Violation("rawhash", shown, 0, "vintage cuyo contenido no coincide con el hash de su nombre"))
            elif rel not in last:
                out.append(Violation("rawhash", shown, 0, f"sin fila en {manifest.relative_to(root).as_posix()}: "
                                     "los datos brutos solo entran con un script de descarga"))
            elif _sha256(p) != last[rel]:
                out.append(Violation("rawhash", shown, 0, "su sha256 no es el de la última descarga registrada: "
                                     "se modificó fuera de los scripts de descarga"))
    return out


# ---------------------------------------------------------------- lessons
def check_lessons(root: Path, files: list[str]) -> list[Violation]:
    out = []
    for rel in files:
        if not re.match(r"^kb/lessons/[^/]+\.md$", rel):
            continue
        text = _read(root, rel) or ""
        for m in re.finditer(r"^## (\d{4}-\d{2}-\d{2}.*)$((?:\n(?!## ).*)*)", text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            estado = re.search(r"^Estado:\s*(candidata|validada|retirada)\b", m.group(2), re.MULTILINE)
            if not estado:
                out.append(Violation("lessons", rel, line, "falta 'Estado: candidata|validada|retirada'"))
            elif estado.group(1) == "validada" and not re.search(r"^Validada por:\s*\S", m.group(2), re.MULTILINE):
                out.append(Violation("lessons", rel, line, "lección validada sin 'Validada por:'"))
    return out


CHECKS = {
    "secrets": check_secrets, "hygiene": check_hygiene, "citations": check_citations,
    "numbers": check_numbers, "parity": check_parity, "speclog": check_speclog,
    "prereg": check_prereg, "referee": check_referee, "gate": check_gate, "rawhash": check_rawhash,
    "lessons": check_lessons,
}


def run(root: Path = ROOT, only: set[str] | None = None) -> list[Violation]:
    files = repo_files(root)
    return [v for name, fn in CHECKS.items() if not only or name in only for v in fn(root, files)]


def main(argv: list[str]) -> int:
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    violations = run(ROOT, only)
    for v in violations:
        print(v)
    print(f"integridad: {len(violations)} violaciones" if violations else "integridad: OK")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
