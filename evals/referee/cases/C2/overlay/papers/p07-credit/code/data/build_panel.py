"""Panel mensual de p07 (1990-02 – 2019-12) a partir de data/raw/ (code/data/download_series.py).

La muestra empieza con la serie de choques de Jarociński-Karadi (1990-02) y acaba antes de la COVID (SPEC, «Datos»).
Salida: data/clean/panel.parquet y data/clean/DICTIONARY.md.
Uso: uv run python papers/p07-credit/code/data/build_panel.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[2]
RAW = PAPER / "data" / "raw"
START, END = "1990-02", "2019-12"
FCI_COMPONENTS = ["ebp", "term", "mp_pm"]  # índice de condiciones financieras del mes


def fred(series: str) -> pd.Series:
    d = pd.read_csv(RAW / f"{series}.csv", parse_dates=["observation_date"])
    return d.set_index("observation_date")[series].astype(float)


def jk_shocks() -> pd.Series:
    d = pd.read_csv(RAW / "shocks_fed_jk_m.csv")
    d.index = pd.to_datetime({"year": d["year"], "month": d["month"], "day": 1})
    return d["MP_pm"]


def zscore(x: pd.Series) -> pd.Series:
    return (x - x.mean()) / x.std(ddof=1)


def ebp() -> pd.Series:
    d = pd.read_csv(RAW / "ebp_csv.csv", parse_dates=["date"])
    return d.set_index("date")["ebp"]


def build() -> pd.DataFrame:
    p = pd.DataFrame({"indpro": fred("INDPRO"), "cpi": fred("CPIAUCSL"), "unrate": fred("UNRATE"),
                      "baa": fred("BAA"), "gs10": fred("GS10"), "tb3ms": fred("TB3MS"), "ebp": ebp(),
                      "mp_pm": jk_shocks()})
    p = p.loc[START:END].copy()
    if p.isna().any().any():
        raise SystemExit(f"faltan datos en la muestra: {p.isna().sum()[lambda s: s > 0].to_dict()}")
    p["lip"] = 100 * np.log(p["indpro"])
    p["dip"] = p["lip"].diff()
    p["dcpi"] = 100 * np.log(p["cpi"]).diff()
    p["dur"] = p["unrate"].diff()
    p["spread"] = p["baa"] - p["gs10"]
    p["shock"] = p["mp_pm"] / p["mp_pm"].std(ddof=1)
    p["credit"] = p["spread"] - p["spread"].mean()
    p["term"] = p["gs10"] - p["tb3ms"]
    p["fci"] = sum(zscore(p[c]) for c in FCI_COMPONENTS) / len(FCI_COMPONENTS)
    p.index.name = "date"
    return p.reset_index().assign(date=lambda d: d["date"].dt.strftime("%Y-%m"))


DICTIONARY = """# Diccionario de data/clean/panel.parquet

Mensual, {start} – {end} (T = {T}). Generado por `code/data/build_panel.py` a partir de `data/raw/` (fuentes, fechas de
descarga y sha256 en `data/raw/MANIFEST.csv`).

| Columna | Descripción | Unidad |
|---|---|---|
| date | Mes | AAAA-MM |
| indpro | Producción industrial (FRED INDPRO) | índice, 2017 = 100 |
| cpi | IPC (FRED CPIAUCSL) | índice |
| unrate | Tasa de paro (FRED UNRATE) | % |
| baa | Rentabilidad Baa de Moody's (FRED BAA) | % |
| gs10 | Rentabilidad del Tesoro a 10 años (FRED GS10) | % |
| tb3ms | Letra del Tesoro a 3 meses (FRED TB3MS) | % |
| ebp | Excess bond premium de Gilchrist-Zakrajšek (Fed Board) | pp |
| mp_pm | Choque de política monetaria de Jarociński-Karadi (MP_pm, suma de los anuncios del mes; 0 sin anuncio) | pp de pc1 |
| lip | 100 × log(indpro) | log × 100 |
| dip | Δ lip | pp |
| dcpi | 100 × Δ log(cpi) | pp |
| dur | Δ unrate | pp |
| spread | baa − gs10: diferencial de crédito corporativo | pp |
| shock | mp_pm / desviación típica muestral de mp_pm (sin restar la media: el 0 es «sin anuncio») | desv. típ. |
| credit | spread − media muestral de spread (estado del crédito; > 0 = más restringido que la media) | pp |
| term | gs10 − tb3ms: pendiente de la curva | pp |
| fci | Condiciones financieras del mes: media de {components} estandarizados | desv. típ. |
"""


def main() -> None:
    panel = build()
    out = PAPER / "data" / "clean"
    out.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(out / "panel.parquet", index=False)
    (out / "DICTIONARY.md").write_text(DICTIONARY.format(start=START, end=END, T=len(panel), components=", ".join(FCI_COMPONENTS)), encoding="utf-8")
    print(f"panel: {len(panel)} meses, {panel['date'].iloc[0]} – {panel['date'].iloc[-1]}")


if __name__ == "__main__":
    main()
