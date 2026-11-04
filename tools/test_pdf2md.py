import pymupdf
from pdf2md import main


def test_converts_with_page_markers_and_is_incremental(tmp_path, capsys):
    doc = pymupdf.open()
    for text in ("Liquidity Transmission Title", "Second page body"):
        doc.new_page().insert_text((72, 72), text)
    doc.save(tmp_path / "Paper2026.pdf")

    main(tmp_path)
    md = (tmp_path / "md" / "Paper2026.md").read_text(encoding="utf-8")
    assert "<!-- p. 1 -->" in md and "<!-- p. 2 -->" in md
    assert "Liquidity Transmission Title" in md and "Second page body" in md
    assert md.index("## Índice") < md.index("<!-- p. 1 -->")

    main(tmp_path)  # segunda pasada: no reconvierte
    assert "convertidos=0 ya_al_día=1" in capsys.readouterr().out
