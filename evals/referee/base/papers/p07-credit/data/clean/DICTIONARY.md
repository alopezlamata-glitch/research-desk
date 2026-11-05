# Diccionario de data/clean/panel.parquet

Mensual, 1990-02 – 2019-12 (T = 359). Generado por `code/data/build_panel.py` a partir de `data/raw/` (fuentes, fechas de
descarga y sha256 en `data/raw/MANIFEST.csv`).

| Columna | Descripción | Unidad |
|---|---|---|
| date | Mes | AAAA-MM |
| indpro | Producción industrial (FRED INDPRO) | índice, 2017 = 100 |
| cpi | IPC (FRED CPIAUCSL) | índice |
| unrate | Tasa de paro (FRED UNRATE) | % |
| baa | Rentabilidad Baa de Moody's (FRED BAA) | % |
| gs10 | Rentabilidad del Tesoro a 10 años (FRED GS10) | % |
| mp_pm | Choque de política monetaria de Jarociński-Karadi (MP_pm, suma de los anuncios del mes; 0 sin anuncio) | pp de pc1 |
| lip | 100 × log(indpro) | log × 100 |
| dip | Δ lip | pp |
| dcpi | 100 × Δ log(cpi) | pp |
| dur | Δ unrate | pp |
| spread | baa − gs10: diferencial de crédito corporativo | pp |
| shock | mp_pm / desviación típica muestral de mp_pm (sin restar la media: el 0 es «sin anuncio») | desv. típ. |
| credit | spread − media muestral de spread (estado del crédito; > 0 = más restringido que la media) | pp |
