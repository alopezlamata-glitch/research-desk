"""Trae al paper las series que usa desde el datalake y las registra en data/raw/MANIFEST.csv.

El datalake ya descargó cada fuente (datalake/fetch/*.py) y guardó su URL, fecha y sha256. Aquí solo se copian los
archivos de SOURCES, comprobando el sha256 contra datalake/MANIFEST.csv, y se escribe la fila del paper. No se modifica
ningún dato. La ruta del datalake es la variable DATALAKE (por defecto, <raíz del repo>/datalake).
Uso: uv run python papers/p07-credit/code/data/download_series.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
from pathlib import Path

PAPER = Path(__file__).resolve().parents[2]
RAW = PAPER / "data" / "raw"
COLS = ["file", "source_url", "downloaded_at", "sha256", "notes"]

# (ruta en datalake/raw, nota)
SOURCES = [
    ("fred/csv/INDPRO.csv", "FRED INDPRO: índice de producción industrial (2017 = 100), mensual, desestacionalizado"),
    ("fred/csv/CPIAUCSL.csv", "FRED CPIAUCSL: IPC de consumidores urbanos, mensual, desestacionalizado"),
    ("fred/csv/UNRATE.csv", "FRED UNRATE: tasa de paro, mensual, desestacionalizada"),
    ("fred/csv/BAA.csv", "FRED BAA: rentabilidad de bonos corporativos Baa de Moody's, media mensual"),
    ("fred/csv/GS10.csv", "FRED GS10: rentabilidad del bono del Tesoro a 10 años, media mensual"),
    ("fred/csv/TB3MS.csv", "FRED TB3MS: letra del Tesoro a 3 meses, media mensual"),
    ("fed_board/ebp_csv.csv", "Fed Board: excess bond premium de Gilchrist-Zakrajšek, mensual"),
    ("shocks/jarocinski_karadi/fed_202401/shocks_fed_jk_m.csv",
     ("Jarociński-Karadi, actualización fed_202401: choques de política monetaria (MP_pm) agregados a mes por los "
     "autores (suma de los anuncios FOMC del mes; 0 si no hay anuncio)")),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    lake = Path(os.environ.get("DATALAKE", PAPER.parents[1] / "datalake"))
    with (lake / "MANIFEST.csv").open(encoding="utf-8", newline="") as f:
        meta = {r["path"]: r for r in csv.DictReader(f)}
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel, note in SOURCES:
        src, m = lake / "raw" / rel, meta.get("raw/" + rel)
        if m is None or sha256(src) != m["sha256"]:
            raise SystemExit(f"{rel}: no está en datalake/MANIFEST.csv o su sha256 no coincide")
        out = RAW / Path(rel).name
        shutil.copy2(src, out)
        rows.append({"file": out.name, "source_url": m["url"], "downloaded_at": m["downloaded"],
                     "sha256": m["sha256"], "notes": f"{note}; copiado de datalake/raw/{rel}"})
    with (RAW / "MANIFEST.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} archivos en {RAW}")


if __name__ == "__main__":
    main()
