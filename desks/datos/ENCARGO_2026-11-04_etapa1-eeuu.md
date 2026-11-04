# Encargo de la Coordinación a Datos — 2026-11-04 · Etapa 1 de p01 (EE. UU.)

Rutas relativas a la raíz del repo (`../../`). Diseño aprobado: `papers/p01-liquidity/SPEC.md` (Desviaciones,
2026-11-04) y `papers/p01-liquidity/exploration/DEVILS_ADVOCATE_2026-11-04.md` §5. Tarea F2 de `papers/p01-liquidity/TASKS.md`.

## Qué hace falta (trimestral, la muestra más larga posible)
1. **Shocks de política monetaria de Bauer-Swanson:** las **dos** vintages (dic-2023 `MPS_ORTH` y la de ago-2025),
   cada una con su propio identificador. Agregar de FOMC a trimestre (suma) con el script documentado. La vintage la
   eligen los autores; tú documenta las diferencias (cobertura, construcción, correlación entre ambas).
2. **Estado de liquidez / servicio de la deuda:** BIS DSR (sector privado no financiero y empresas, EE. UU.);
   Z.1, con liquidez de las empresas no financieras (activos líquidos / activos o deuda) y, si existe, la parte de
   deuda a tipo variable o a corto plazo.
3. **Controles y resultados:** inversión fija privada no residencial real, PIB real, deflactor, fed funds y el rendimiento a 2 años;
   SLOOS (estándares para C&I) y excess bond premium.

Mira antes `datalake/CATALOG.md` y `kb/data_catalog.md`: gran parte ya está en el lago de datos.

## Entregable
- Scripts `papers/p01-liquidity/code/data/download_*.py` / `build_*.py` (sin rellenar huecos; respeta `integrity.py`),
  `data/raw/MANIFEST.csv` actualizado, `papers/p01-liquidity/data/clean/stage1_us.parquet` y su diccionario
  `data/clean/DICTIONARY.md` (fuente, transformación, cobertura, huecos).
- Un párrafo en el diccionario sobre las dos vintages de Bauer-Swanson.
- Fuentes nuevas, en `kb/data_catalog.md`; lecciones, en `kb/lessons/data.md` (`Estado: candidata`).

## Reglas
Sin claves de API en el código (FRED sin clave vía `fredgraph.csv`). No toques `data/raw/` a mano. No estimes nada.
