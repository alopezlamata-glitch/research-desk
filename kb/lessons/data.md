# Lecciones — Datos

## 2026-11-04 · p01 · Errores de datos en las iteraciones previas
1. **Extrapolar con AR(1) hasta el final de la muestra y luego estimar sobre esos trimestres** (LDC_UK) mete datos
   inventados en la estimación. Regla: la muestra de estimación termina en el último dato observado; si una
   serie se extiende, la extensión se marca y se excluye.
2. **`ffill().bfill()` e `interpolate()` sobre todo el índice** rellenan huecos con datos futuros (look-ahead).
   Regla: nunca `bfill` en series que entran en una estimación; los NaN se documentan.
3. **Renombrar una serie como si fuera otra** (paro → "delinquency", −confianza empresarial → "VIX") esconde que
   el instrumento no es lo que dice el paper. Regla: el nombre de la variable describe la serie real; el papel
   (proxy de X) va en el diccionario de datos.
4. **Marcadores de posición que se quedan** (`UNRATE` como encuesta de confianza). Regla: los marcadores se
   escriben `TODO_SERIE_REAL` para que fallen y no se estimen en silencio.
5. **Claves de API en el código.** Regla: FRED se descarga de `fredgraph.csv` sin clave; si hiciera falta clave, se
   lee de `FRED_API_KEY`.

## 2026-11-04 · datalake · Descarga masiva de fuentes públicas
1. **Comprobar la identidad del archivo, no solo el HTTP 200.** La URL "JSTdatasetR6.xlsx" servía un `.dta`; el xlsx de
   Bauer-Swanson de la web era byte a byte el de dic-2023 (la "actualización ago-2025" estaba en un zip con otro formato).
   Regla: hash + cabecera (PK/D0CF/`<stata_dta>`) + rango de fechas antes de etiquetar un vintage.
2. **Wayback fija vintages** (`web.archive.org/web/<ts>id_/<url>`) pero devuelve 429 si se abusa: reintentos con espera.
3. **imf.org, cbo.gov y la API SDMX de la OCDE devuelven 403 a scripts**: usar espejos (DBnomics, JST, WDI) o marcar "manual".
4. **BIS bulk (`WS_*_csv_flat.zip`)**: las dimensiones van entre `ACTION` y `TIME_PERIOD`; no hay columna `KEY`. Un CSV
   puede pesar 500 MB descomprimido (CBPOL): leer por bloques.
5. **Un `series_id` duplicado delata dimensiones mal elegidas** (WDI: agregados sin ISO3). Validar unicidad al guardar.
6. **OneDrive bloquea el borrado de carpetas**: no regenerar borrando `raw/`; los fetch sobrescriben y el MANIFEST se reinicia aparte.
7. FRED `GDPPOT` llega a 2036 (proyección CBO): no estimar sobre ella.
