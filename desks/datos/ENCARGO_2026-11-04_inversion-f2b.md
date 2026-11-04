# Encargo de la Coordinación a Datos — 2026-11-04 · F2b: serie de inversión de la etapa 1

Rutas relativas a la raíz del repo (`../../`). Tarea F2b de `papers/p01-liquidity/TASKS.md`.

`PNFIC1` solo empieza en 2007Q1 en FRED. La Coordinación ha comprobado que el índice de cantidad
`A008RA3Q086SBEA` (inversión privada no residencial real, 2017=100) cubre 1947Q1–2026Q3 en `fredgraph.csv`.

1. Añádelo al lago (`datalake/fetch/` + `datalake/MANIFEST.csv`, como las demás series de FRED) y a
   `papers/p01-liquidity/code/data/{download,build}_stage1_us.py`, con el nombre `inv_nonres_q` y sin rellenar huecos.
2. Que sea la **variable principal de inversión** en `DICTIONARY.md`. `inv_nonres_real` (PNFIC1) queda como comprobación
   desde 2007: tasa de crecimiento con correlación ≈ 1.
3. Añade a `test_stage1_us.py` un test de cobertura (≥ 1985Q1) y uno de coherencia con PNFIC1.
4. Regenera `stage1_us.parquet`, `coverage.csv` y la figura; actualiza `kb/data_catalog.md`.

No hagas commit: lo hace la Coordinación. Lecciones en `kb/lessons/data.md` (`Estado: candidata`).
