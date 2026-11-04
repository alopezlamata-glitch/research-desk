"""Etapa 1 (EE. UU.) de p01: trae al paper las fuentes del datalake y las registra en data/raw/MANIFEST.csv.

El datalake ya descargó cada fuente (datalake/fetch/*.py); aquí solo se copian los archivos que usa esta etapa,
comprobando el sha256 contra datalake/MANIFEST.csv, y se anota la fila del paper. No se modifica ningún dato.
Uso: uv run python papers/p01-liquidity/code/data/download_stage1_us.py
"""

import csv
import hashlib
import shutil
from pathlib import Path

PAPER = Path(__file__).resolve().parents[2]
LAKE = PAPER.parents[1] / "datalake"
RAW = PAPER / "data" / "raw"
MANIFEST = RAW / "MANIFEST.csv"
COLS = ["file", "source_url", "downloaded_at", "sha256", "notes"]

BS = "shocks/bauer_swanson/"
# (ruta en datalake/raw, nota). El xlsx etiquetado vintage2025-08 en el lago es idéntico al de dic-2023: no se copia.
FILES = [
    (BS + "monetary-policy-surprises-data_vintage2023-12.xlsx", "Bauer-Swanson vintage dic-2023 (MPS_ORTH, hoja 'FOMC (update 2023)')"),
    (BS + "monetary-policy-surprises_vintage2025-08.zip", "Bauer-Swanson vintage ago-2025 (mps.csv: STMT/PC/ME; otra construcción)"),
    ("bis/WS_DSR.parquet", "BIS DSR, todos los países; se usan Q|US|P y Q|US|N"),
    ("fed_z1/z1_csv_files_20260911.zip", "Z.1 release 2026-09-11; se usa csv/S11_1_b.csv y S11_1_t.csv"),
    ("fed_board/ebp_csv.csv", "Excess bond premium (Gilchrist-Zakrajsek), mensual"),
] + [(f"fred/csv/{s}.csv", "FRED") for s in
     ["GDPC1", "GDPDEF", "A008RA3Q086SBEA", "PNFIC1", "GPDIC1", "FEDFUNDS", "DGS2", "DRTSCILM", "DRTSCIS", "DRSDCILM"]]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lake_rows() -> dict[str, dict[str, str]]:
    with (LAKE / "MANIFEST.csv").open(encoding="utf-8", newline="") as f:
        return {r["path"]: r for r in csv.DictReader(f)}


def main() -> None:
    lake = lake_rows()
    dest = RAW / "stage1_us"
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel, note in FILES:
        src = LAKE / "raw" / rel
        meta = lake.get("raw/" + rel)
        if meta is None:
            raise SystemExit(f"{rel} no está en datalake/MANIFEST.csv")
        if sha256(src) != meta["sha256"]:
            raise SystemExit(f"sha256 de {rel} no coincide con el MANIFEST del datalake")
        out = dest / Path(rel).name
        shutil.copy2(src, out)
        rows.append({"file": out.relative_to(RAW).as_posix(), "source_url": meta["url"],
                     "downloaded_at": meta["downloaded"], "sha256": meta["sha256"],
                     "notes": f"{note}; copiado de datalake/raw/{rel}"})
    new = not MANIFEST.exists() or MANIFEST.stat().st_size == 0
    prev = set() if new else {r["file"] for r in csv.DictReader(MANIFEST.open(encoding="utf-8", newline=""))}
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        if new:
            w.writeheader()
        w.writerows(r for r in rows if r["file"] not in prev)
    print(f"{len(rows)} archivos en {dest}")


if __name__ == "__main__":
    main()
