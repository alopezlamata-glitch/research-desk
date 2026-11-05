"""Utilidades comunes: descarga, escritura en raw/ y fila en MANIFEST.csv.

Un archivo de raw/ nunca se pierde al volver a descargarlo: si el contenido nuevo es distinto, el anterior pasa a
`raw/<source>/_vintages/<stem>.<sha12><suffix>`, de modo que cualquier sha256 del MANIFEST se puede recuperar.
`tools/integrity.py` (check `rawhash`) comprueba que raw/ coincide con el MANIFEST y los vintages con su nombre.
"""

import csv
import hashlib
import json
import os
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
MANIFEST = ROOT / "MANIFEST.csv"
UA = {"User-Agent": "Mozilla/5.0 (research-desk datalake; contacto: alopezlamata@gmail.com)"}


def get(url, timeout=120, **kw):
    r = requests.get(url, headers=UA, timeout=timeout, **kw)
    r.raise_for_status()
    head = r.content[:300].lower()
    if (b"<html" in head or b"<!doctype" in head) and not url.endswith((".htm", ".html")):
        raise ValueError(f"respuesta HTML (¿página de error?) en {url}")
    return r


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def install(p, write):
    """Escribe `p` con `write(tmp)` sin perder la versión anterior si el contenido cambia (va a _vintages/)."""
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    write(tmp)
    if p.exists():
        old = sha256(p)
        if old == sha256(tmp):
            tmp.unlink()
            return p
        keep = p.parent / "_vintages" / f"{p.stem}.{old[:12]}{p.suffix}"
        keep.parent.mkdir(exist_ok=True)
        if keep.exists():
            p.unlink()
        else:
            os.replace(p, keep)
    os.replace(tmp, p)
    return p


def save(source, name, content, url, vintage=""):
    """Guarda bytes en raw/<source>/<name> y añade fila al MANIFEST."""
    p = install(RAW / source / name, lambda tmp: tmp.write_bytes(content))
    _manifest_row(p, url, vintage)
    return p


def save_frame(source, name, df, url, vintage=""):
    """Guarda un DataFrame en raw/<source>/<name> (parquet) y añade fila al MANIFEST."""
    p = install(RAW / source / name, lambda tmp: df.to_parquet(tmp, index=False))
    _manifest_row(p, url, vintage)
    return p


def save_long(source, name, df, url, meta=None, vintage=""):
    """df con columnas date, series_id, value -> parquet largo + meta.json."""
    df = df.dropna(subset=["value"]).copy()
    assert not df.duplicated(["date", "series_id"]).any(), f"duplicados en {source}/{name}"
    p = save_frame(source, f"{name}.parquet", df, url, vintage)
    if meta is not None:
        mp = RAW / source / "meta.json"
        old = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
        old.update(meta)
        mp.write_text(json.dumps(old, indent=1, ensure_ascii=False), encoding="utf-8")
    return p


def _manifest_row(p, url, vintage):
    b = p.read_bytes()
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["path", "url", "downloaded", "sha256", "bytes", "vintage"])
        w.writerow([p.relative_to(ROOT).as_posix(), url, date.today().isoformat(),
                    hashlib.sha256(b).hexdigest(), len(b), vintage])


def download(source, name, url, vintage="", tries=4, min_bytes=1000):
    """GET con reintentos (429/5xx) -> raw/<source>/<name> + MANIFEST. Devuelve la ruta."""
    import time
    last = None
    for i in range(tries):
        try:
            r = get(url, timeout=300)
            if len(r.content) < min_bytes:
                raise ValueError(f"demasiado pequeño ({len(r.content)} B)")
            return save(source, name, r.content, url, vintage)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(10 * (i + 1))
    raise last


def run(fn, label):
    """Ejecuta una descarga y devuelve True/False sin abortar el resto."""
    try:
        fn()
        print(f"[OK]    {label}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[ROTO]  {label}: {str(e)[:150]}")
        return False


def check(df, label):
    """Resumen de validación: rango, nº obs, duplicados."""
    d = pd.to_datetime(df["date"])
    return f"{label}: n={len(df)} series={df['series_id'].nunique()} {d.min().date()}..{d.max().date()}"
