# Encargo de la Coordinación a Datos — 2026-11-07 · F7: datos para la etapa 1 rediseñada de p01

Modelo: sonnet

Rutas relativas a la raíz del repo (`../../`). Contexto: los autores han decidido rediseñar la etapa 1 (Desviación del
2026-11-07 al final de `papers/p01-liquidity/SPEC.md`; resumen en `exploration/DECISIONES_AUTORES_2026-11-07.md`).
El choque principal pasa a ser **Romer-Romer**, el estadístico es la media de h = 4..12 trimestres y se abre una etapa 1b
transversal condicionada a datos.

## Regla dura
**No estimes nada con la inversión ni mires cómo responde ninguna variable de resultado a los choques.** De la inversión
solo puedes comprobar disponibilidad y fechas. El estado `D_{t−1}` y los choques sí puedes tabularlos.

## Qué hacer
1. **Serie de Romer-Romer** (la extensión de Coibion que usa el Handbook de Ramey, u otra versión documentada si esa no está
   disponible; justifícalo). Mira primero `kb/data_catalog.md` (hoy figura "sin probar").
   - Descárgala con un script `datalake/fetch/` que use `_common.download` (registra fuente, fecha y sha256 en el MANIFEST;
     si la vuelves a bajar, la versión anterior queda en `_vintages/`).
   - Tráela al paper con `papers/p01-liquidity/code/data/download_stage1_us.py` o un script hermano, con su fila en
     `data/raw/MANIFEST.csv` (el check `rawhash` lo exige).
   - Agregación a trimestres: documenta la regla (suma de los choques mensuales del trimestre, salvo que la fuente indique
     otra) en `data/clean/DICTIONARY.md`.
2. **Fecha de corte exacta.** La muestra de choques empieza en 1969Q1 y acaba en el último trimestre t tal que la ventana
   h = 12 (t + 12) termina antes de 2008Q3. Da también la muestra de la réplica con `mps_bs23_orth` (posterior a 1984).
3. **D1/D2 en la muestra nueva** (tabla en `data/clean/SAMPLE_COUNTS_S1R.md`): para cada estado de `D_{t−1}` (el mismo de la
   etapa 1: liquidez de Z.1 frente a su media móvil de 12 trimestres), número de observaciones, número de trimestres con
   choque ≠ 0 y Σ|ε| del choque; con y sin 1979Q4–1982Q4. **Si los trimestres de Volcker caen casi todos en un estado, márcalo
   `[!]` en `TASKS.md` y para**: los autores tienen que saberlo antes del MC.
4. **Etapa 1b:** informe breve de disponibilidad del **QFR** del Census (variables por tamaño o sector, frecuencia, años,
   acceso gratuito o no, número de grupos G) y de cualquier alternativa gratuita con G ≥ 40 y una medida de exposición a tipo
   variable por grupo. Si no hay nada gratuito, dilo: los autores están confirmando si tienen acceso a WRDS.
5. Añade a `kb/data_catalog.md` las fuentes probadas, con su estado.

## Entregables
`data/clean/` actualizado con su diccionario, `SAMPLE_COUNTS_S1R.md`, el informe de la etapa 1b en
`papers/p01-liquidity/exploration/F7_DATOS_2026-11-07.md` y tests de los datos nuevos en `code/data/`.
`uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity` en verde. Marca **F7** en `TASKS.md`. Lecciones en
`kb/lessons/data.md` (`Estado: candidata`). No hagas commit.
