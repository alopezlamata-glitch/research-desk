"""F30 (Referee): compilación completa de paper/main.tex (pdflatex + bibtex + 2 pdflatex) en un directorio temporal, sin tocar
paper/. Informa de errores, referencias y citas indefinidas, cajas desbordadas y de cómo sale cada entrada citada en el .bbl.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F30/compile_full.py
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[2]


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace", check=False)


with tempfile.TemporaryDirectory() as d:
    pdir = Path(d) / "paper"
    pdir.mkdir()
    (Path(d) / "output").mkdir()
    for pat in ("*.bib", "*.bst", "main.tex"):
        for f in (PAPER / "paper").glob(pat):
            shutil.copy(f, pdir)
    shutil.copy(PAPER / "output" / "macros.tex", Path(d) / "output")
    pdflatex = [shutil.which("pdflatex"), "-interaction=nonstopmode", "main.tex"]
    rcs = [run(pdflatex, pdir).returncode, run([shutil.which("bibtex"), "main"], pdir).returncode]
    rcs += [run(pdflatex, pdir).returncode, run(pdflatex, pdir).returncode]
    log = (pdir / "main.log").read_text(encoding="latin-1")
    blg = (pdir / "main.blg").read_text(encoding="latin-1")
    print("rc (pdflatex, bibtex, pdflatex, pdflatex):", rcs)
    print("errores LaTeX:", len(re.findall(r"^! ", log, re.M)))
    print("referencias/citas indefinidas:", re.findall(r"(?:Reference|Citation) `[^']+' .*undefined", log))
    print("avisos de bibtex:", re.findall(r"^Warning--.*", blg, re.M))
    print("cajas desbordadas (Overfull):", len(re.findall(r"^Overfull", log, re.M)))
    for m in re.finditer(r"^Overfull .*lines (\d+)--(\d+)", log, re.M):
        print("  Overfull en main.tex líneas", m.group(1), "-", m.group(2))
    pages = re.search(r"Output written on main.pdf \((\d+) pages", log)
    print("páginas:", pages.group(1) if pages else "?")
    tex = (pdir / "main.tex").read_text(encoding="utf-8")
    keys = sorted({k.strip() for g in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]+)\}", tex) for k in g.split(",")})
    bbl = (pdir / "main.bbl").read_text(encoding="latin-1")
    print(f"claves citadas ({len(keys)}):")
    for k in keys:
        m = re.search(r"\\bibitem\[([^\]]*)\]\{" + re.escape(k) + r"\}", bbl)
        print(f"  {k}: {m.group(1).replace(chr(10), ' ') if m else 'NO ESTÁ EN EL .bbl'}")
