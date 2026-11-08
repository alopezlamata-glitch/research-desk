# Encargo de la Coordinación a Econometría — 2026-11-08 · F21: cifras del paper A generadas por código

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Que todas las cifras que usará el borrador del paper A (teoría + medición acotada de la etapa 1) salgan de código, como macros
LaTeX en `output/macros.tex`, para que Redacción no teclee ningún número. **No se estima nada nuevo**: todo sale de tablas y
CSV que ya existen y están auditados.

## Lee primero
- La Desviación del 2026-11-08 sobre el paper A al final de `papers/p01-liquidity/SPEC.md` (qué se muestra: las 6 filas de b_C con
  p unilateral e IC, como medición sin veredicto).
- `output/F16_RESULTADOS.md` (`## HANDOFF`) y los archivos de donde salen las cifras: `output/estimates_py.csv`,
  `output/estimates_py_robustness.csv`, `output/tables/s1r_estimates.md`, `output/tables/s1r_shock_diagnostics.md`,
  `output/tables/f13_checks.md` (potencia y MDE ex ante) y `output/tables/f9_power.md` (β_ref).

## Entregable
- `code/analysis/02_paper_macros.py`: lee esas fuentes y escribe `output/macros.tex` con una macro por cifra (estimaciones, ee,
  IC, p, N, β_ref, MDE en c·β_ref y en pp por pp, potencia con β_ref, diagnósticos de los choques y el veredicto). Nombres
  legibles y documentados en el propio script.
- Un test que compruebe que cada macro coincide con su fuente (que el script no redondea ni transforma de más) y que el script
  es reproducible.

## Criterios de aceptación
`uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity` en verde; ninguna cifra nueva que no esté ya en las
fuentes auditadas; las macros de b_C cubren las 6 filas.

## Condición de parada
Cuando el script, `macros.tex` y el test estén hechos. Si una cifra que hace falta no está en ninguna fuente auditada, no la
calcules: anótala en el HANDOFF como pendiente.

## Cierre
`## HANDOFF` en `papers/p01-liquidity/output/F21_MACROS.md` (lista de macros y su fuente). Marca **F21** en `TASKS.md`. No hagas
commit: después audita el Referee (F22), porque la puerta de `paper/` caduca al cambiar `code/` y `output/`.
