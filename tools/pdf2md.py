"""Convierte los PDFs de kb/library/ a Markdown (kb/library/md/) para que los agentes lean menos tokens.

Incremental: solo convierte PDFs nuevos o modificados. Marca cada página con <!-- p. N --> para poder citar
con número de página. Las fórmulas y tablas complejas pueden salir dañadas: ante la duda, se mira el PDF.
Uso: uv run python tools/pdf2md.py [carpeta]   (por defecto kb/library)
"""

import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import pymupdf4llm

NOISE = re.compile(r"^\*\*==> picture .* <==\*\*$|^-+ (Start|End) of picture text -+$", re.MULTILINE)


def clean(text: str) -> str:
    text = NOISE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


HEADING = re.compile(r"^#{1,3} +\**(.+?)\**\s*$", re.MULTILINE)


def toc(pages: list[dict]) -> str:
    """Índice de secciones con página, para leer solo lo necesario.

    Usa el índice del PDF si lo trae; si no, los encabezados detectados en el texto.
    """
    items = [(lvl, title, pg) for p in pages for lvl, title, pg, *_ in p.get("toc_items", [])]
    if not items:
        items = [
            (1, m.group(1).strip(), i)
            for i, p in enumerate(pages, start=1)
            for m in HEADING.finditer(p["text"])
            if 3 <= len(m.group(1).strip()) <= 90
        ]
    lines = [f"{'  ' * (lvl - 1)}- {title} — p. {pg}" for lvl, title, pg in items[:80]]
    return "## Índice\n" + ("\n".join(lines) if lines else "(sin índice detectable)") + "\n\n"


def convert(pdf: Path, out_dir: Path) -> Path:
    pages = pymupdf4llm.to_markdown(str(pdf), page_chunks=True)
    body = "\n\n".join(
        f"<!-- p. {i} -->\n{clean(p['text'])}" for i, p in enumerate(pages, start=1)
    )
    header = (
        f"<!-- fuente: {pdf.name} · {len(pages)} páginas · convertido {date.today()} · "
        "texto extraído automáticamente: verificar fórmulas y tablas contra el PDF -->\n\n"
        + toc(pages)
    )
    md = out_dir / f"{pdf.stem}.md"
    md.write_text(header + body + "\n", encoding="utf-8")
    return md


def main(folder: Path) -> None:
    out_dir = folder / "md"
    out_dir.mkdir(exist_ok=True)
    pending = [
        pdf for pdf in sorted(folder.glob("*.pdf"))
        if not ((md := out_dir / f"{pdf.stem}.md").exists() and md.stat().st_mtime >= pdf.stat().st_mtime)
    ]
    skipped = len(list(folder.glob("*.pdf"))) - len(pending)
    done = failed = 0
    pdf_chars = md_chars = 0
    # ponytail: cada proceso carga un modelo de maquetación (~1 GB); con 8 GB de RAM más de 2 agota la memoria.
    workers = max(1, min(len(pending), int(os.environ.get("PDF2MD_WORKERS", "2"))))
    with ProcessPoolExecutor(workers) as pool:
        futures = {pool.submit(convert, pdf, out_dir): pdf for pdf in pending}
        for fut in as_completed(futures):
            pdf = futures[fut]
            try:
                md = fut.result()
                done += 1
                pdf_chars += pdf.stat().st_size
                md_chars += md.stat().st_size
            except Exception as e:  # noqa: BLE001 — un PDF roto no debe parar el lote
                failed += 1
                print(f"FALLO {pdf.name}: {e}")
    print(f"convertidos={done} ya_al_día={skipped} fallidos={failed}")
    if done:
        print(f"PDF {pdf_chars / 1e6:.1f} MB -> MD {md_chars / 1e6:.2f} MB (~{md_chars // 4:,} tokens)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kb/library"))
