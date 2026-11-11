"""F28 (Referee): ¿compila paper/main.tex (sin tocarlo) con el output/macros.tex de F25? Copia ambos a un directorio temporal.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F28/compile_main.py
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[2]

with tempfile.TemporaryDirectory() as d:
    (Path(d) / "paper").mkdir()
    (Path(d) / "output").mkdir()
    for f in (PAPER / "paper").glob("*.bib"):
        shutil.copy(f, Path(d) / "paper")
    shutil.copy(PAPER / "paper" / "main.tex", Path(d) / "paper")
    shutil.copy(PAPER / "output" / "macros.tex", Path(d) / "output")
    r = subprocess.run([shutil.which("pdflatex"), "-interaction=nonstopmode", "main.tex"], cwd=Path(d) / "paper",
                       capture_output=True, text=True, errors="replace", check=False)
    lines = r.stdout.splitlines()
    errs = [i for i, ln in enumerate(lines) if ln.startswith("!")]
    print(f"pdflatex rc={r.returncode}; {len(errs)} errores")
    for i in errs[:6]:
        print("\n".join(lines[i:i + 3]))
        print("--")
