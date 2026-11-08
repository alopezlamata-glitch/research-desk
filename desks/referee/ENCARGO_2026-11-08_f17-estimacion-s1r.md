# Encargo de la Coordinación al Referee — 2026-11-08 · F17: auditoría de la estimación de `s1r_*`

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol (`.claude/agents/referee.md`) y el formato de
`.claude/skills/referee-report/SKILL.md`.

## Objetivo
Un veredicto sobre la estimación de la etapa 1 de p01 (F16) en el **commit 1c98c81**: que se ejecutó exactamente el
prerregistro congelado (`prereg_commit: 3d6b508`), que el veredicto `h0_falla` se sigue del árbol V3s y que el informe no dice
más de lo que los datos y el prerregistro permiten.

## Lee primero
- `papers/p01-liquidity/output/F16_RESULTADOS.md` (incluido su `## HANDOFF`).
- Lo que obliga: `papers/p01-liquidity/SPEC.md`, sección "## Prerregistro de la etapa 1 rediseñada", y la Desviación del
  2026-11-08 (respuestas de los autores).
- El código ejecutado: `code/analysis/01_s1r_estimate.py`, `code/analysis/s1r_lp.py` y `code/replication_r/s1r_replication.R`
  (deben ser los de bd4f7bc), y `output/estimates_*.csv`, `output/spec_log.csv` y `output/tables/s1r_*.md`.
- Para contexto, solo si lo necesitas: tus auditorías de F4 y F9 en `papers/p01-liquidity/audits/`.

## Qué auditar (como mínimo)
1. **Que se ejecutó lo congelado:** el código no cambió desde bd4f7bc; muestra, controles, `aum`, NW5+HC3 y los 7 ids son los
   del texto; `spec_log.csv` no esconde especificaciones.
2. **El veredicto:** que `h0_falla` se sigue de la regla escrita, con las cifras que deciden cada paso.
3. **La lectura de β̂_C.** β̂_C tiene p unilateral < 0,05 en las dos muestras y dos robusteces también, pero H0 falla y el árbol
   no permite interpretar H1. Comprueba que el informe no lo presenta como evidencia de H1 ni sugiere cambiar la regla, y valora
   si la frase que lo describe como "medición sin veredicto" es correcta.
4. **Los diagnósticos de los choques** y que su consecuencia es la que fija la SPEC.
5. **Las dos lecturas de implementación de F15 en la robustez** (estado logístico estandarizado; mediana de la muestra completa
   en `r1r_from1971q3`): si son la lectura razonable del texto congelado.
6. **Replicación independiente** de `s1r_lin`, `s1r_liq` y `s1r_liq_nov` en `papers/p01-liquidity/audits/replication_2026-11-08b/`,
   escrita por ti (no reutilices la réplica en R del autor), con los datos reales de `data/clean/stage1r_us.parquet`.
7. `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`, citados en el informe.

## Entregable
`papers/p01-liquidity/audits/2026-11-08_F16_estimacion.md`, con veredicto, hallazgos con `Evidencia:` y la replicación.

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde; tu replicación reproduce las estimaciones y los errores de F16 al
6.º decimal o explica la diferencia.

## Condición de parada
Cuando hayas cubierto los puntos 1–7. No propongas especificaciones nuevas para "rescatar" H1: si crees que hace falta otro
análisis, anótalo como pendiente para el Director y los autores.

## Cierre
`## HANDOFF` al final del informe. Marca **F17** en `papers/p01-liquidity/TASKS.md` y añade lo que aprendas a
`kb/lessons/referee.md` (`Estado: candidata`). No hagas commit.
