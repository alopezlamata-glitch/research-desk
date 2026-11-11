"""F28 (Referee): comprobación de F25. No importa 02_paper_macros.py.

1. Compara macro a macro output/macros.tex de 67bc9c2 con el de HEAD (renombrado H0 -> Hzero).
2. Recalcula desde f9_power.md §1b el rango de cobertura aum, NW5+HC3, con T y con T/2, en todos los términos y en los que
   deciden (entre paréntesis).
3. Compila con pdflatex un documento mínimo que hace \\input de macros.tex y usa las 6 macros nuevas.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F28/check_f25.py
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[2]
REPO = PAPER.parents[1]
OUT = PAPER / "output"
DEF = re.compile(r"^\\newcommand\{\\([^}]*)\}\{(.*)\}$", re.MULTILINE)

# 1. Diff de macros
old_tex = subprocess.run(["git", "show", "67bc9c2:papers/p01-liquidity/output/macros.tex"], cwd=REPO, capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout
new_tex = (OUT / "macros.tex").read_text(encoding="utf-8")
old, new = dict(DEF.findall(old_tex)), dict(DEF.findall(new_tex))
renamed = {k: k.replace("H0", "Hzero") for k in old}
old_r = {renamed[k]: v for k, v in old.items()}
changed = {k: (old_r[k], new[k]) for k in old_r.keys() & new.keys() if old_r[k] != new[k]}
print(f"67bc9c2: {len(old)} macros; HEAD: {len(new)}")
print("renombradas:", sorted((k, v) for k, v in renamed.items() if k != v))
print("solo en HEAD:", sorted(new.keys() - old_r.keys()), "| perdidas:", sorted(old_r.keys() - new.keys()))
print("valores distintos:", changed)
print("orden conservado:", [renamed[k] for k in old] == [k for k in new if k in old_r])
assert not changed and old_r.keys() <= new.keys()
bad = [k for k in new if not re.fullmatch(r"[A-Za-z]+", k)]
print("nombres que no son control words:", bad)
assert not bad

# 2. Rango de cobertura NW5+HC3 de aum (f9_power.md §1b)
rows = []
for i, line in enumerate((OUT / "tables" / "f9_power.md").read_text(encoding="utf-8").splitlines(), 1):
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) == 8 and c[0] == "aum" and c[3].startswith("T"):
        m = re.fullmatch(r"(\d\.\d+)–(\d\.\d+)(?: ✗)? \((\d\.\d+)–(\d\.\d+)\)", c[5])
        rows.append((i, c[1], c[2], c[3].split(" = ")[0], *map(float, m.groups())))
for t in ("T", "T/2"):
    sel = [r for r in rows if r[3] == t]
    print(f"{t}: filas {[r[0] for r in sel]} ({len(sel)}); todos los términos {min(r[4] for r in sel):.3f}–"
          f"{max(r[5] for r in sel):.3f}; términos que deciden {min(r[6] for r in sel):.3f}–{max(r[7] for r in sel):.3f}")

# 3. Compilación
tex = shutil.which("pdflatex")
print("pdflatex:", tex)
if tex:
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(OUT / "macros.tex", Path(d) / "macros.tex")
        new_names = ["PwHomoHzeroFalla", "PwHetHzeroFalla", "PwHomoPowHzero", "PwHetPowHzero", "CovAumNwHcLo", "CovAumNwHcHi"]
        body = "\n".join(f"{n}: \\{n}\\par" for n in new_names) + "\nAll: " + " ".join(f"\\{n}{{}}" for n in new) + "\n"
        (Path(d) / "t.tex").write_text("\\documentclass{article}\n\\usepackage{amsmath}\n\\input{macros.tex}\n"
                                       "\\begin{document}\n" + body + "\\end{document}\n", encoding="utf-8")
        r = subprocess.run([tex, "-interaction=nonstopmode", "-halt-on-error", "t.tex"], cwd=d, capture_output=True, text=True,
                           errors="replace", check=False)
        errs = [ln for ln in r.stdout.splitlines() if ln.startswith("!")]
        print(f"pdflatex rc={r.returncode}; errores: {errs}")
        txt = subprocess.run(["pdftotext", "t.pdf", "-"], cwd=d, capture_output=True, text=True, check=False).stdout if shutil.which(
            "pdftotext") else ""
        print("texto:", " | ".join(txt.splitlines()[:6]))
        assert r.returncode == 0 and not errs
print("OK")
