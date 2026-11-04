# datalake — base de datos económica permanente de la desk

Datos descargados de fuentes públicas para usar en cualquier paper, presente o futuro. Lo mantiene la desk
de Datos. Un paper **no edita el datalake**: lo lee y construye sus `data/clean/` a partir de él.

## Estructura
```
datalake/
├── fetch/<fuente>.py     # un script por fuente; reproduce la descarga (versionado)
├── fetch/update_all.py   # ejecuta todos los fetch (versionado)
├── raw/<fuente>/...      # datos tal cual se descargan (NO versionado, solo lectura: hook)
├── CATALOG.md            # qué hay, para qué sirve, cobertura y estado (versionado)
└── MANIFEST.csv          # una fila por archivo: ruta, URL, fecha, sha256, vintage (versionado)
```

## Reglas
- **Solo se escribe en `raw/` mediante `fetch/*.py`.** El hook bloquea Edit/Write.
- **Formato:** el original tal cual (csv/xlsx/zip) y, si es tabular, también `.parquet` en formato largo
  (`date, series_id, value`) con metadatos (unidades, frecuencia, ajuste estacional) en `raw/<fuente>/meta.json`.
- **Sin claves de API en el código.** FRED se baja de `fredgraph.csv`; si una fuente exige clave, se lee de una
  variable de entorno y se documenta en `CATALOG.md`.
- **Vintages:** las series que se revisan (PIB, deuda…) llevan la fecha de descarga en el MANIFEST. Para tiempo
  real se usa ALFRED.
- **Solo fuentes públicas y gratuitas**, sin login. Nada de scraping que viole los términos de uso.
- **Tamaño:** un archivo de más de 200 MB necesita el visto bueno de los autores.
- Cada fuente nueva se añade a `CATALOG.md` y a `kb/data_catalog.md`.
