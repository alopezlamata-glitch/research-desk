# Encargo de la Coordinación a Econometría — 2026-11-08 · F15: requisitos previos a estimar `s1r_*`

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Dejar el código listo para estimar exactamente el prerregistro aprobado (congelado en `prereg_commit: 3d6b508`), **sin
estimar nada con la inversión real**. Es el "Requisito previo a estimar" de la propia sección de prerregistro.

## Regla dura
No estimes `s1r_*` ni nada con la inversión real, ni mires cómo responde a los choques. Los tests usan datos simulados.

## Lee primero
- `papers/p01-liquidity/SPEC.md`, sección "## Prerregistro de la etapa 1 rediseñada" (lo que obliga) y la Desviación del
  2026-11-08 con las respuestas de los autores (controles, diagnósticos, refutación con la muestra completa, BS exploratoria).
- `code/analysis/s1r_lp.py` y `code/mc/f9_power.py` (tu código de F9) y `tools/research.py` (`log_spec`).

## Entregable
1. `s1r_lp.py` alineado con el texto congelado: `h1_verdict` sin la rama (b); V3s exactamente como está escrita (H0 solo con la
   muestra completa; (a) solo con la muestra completa; "no concluyente" si la completa confirma y sin Volcker β̂_C > 0 es
   significativo); los controles aprobados.
2. Los ids `s1r_lin`, `s1r_liq`, `s1r_liq_nov` y los `r1r_*` del bloque implementados en un script de análisis numerado
   (`code/analysis/<nn>_s1r_estimate.py`) que, **cuando se ejecute**, registre cada especificación con `research.log_spec`, exporte
   `output/estimates_py.csv` y los diagnósticos de los choques. No lo ejecutes sobre la inversión real.
3. La réplica en R (`code/replication_r/`) de `s1r_lin`, `s1r_liq` y `s1r_liq_nov` con NW5+HC3, lista para la paridad.
4. Tests con datos simulados (DGP de F9) que comprueben que el script de análisis y la réplica en R dan lo mismo y que el árbol
   de decisión devuelve el veredicto correcto en casos construidos a mano.

## Criterios de aceptación
`uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity` en verde; paridad Python–R comprobada con datos
simulados; ningún archivo de `output/` con estimaciones sobre la inversión real.

## Condición de parada
Cuando 1–4 estén hechos. Si algo del texto congelado es inaplicable al implementarlo, no lo cambies: márcalo `[!]` en
`TASKS.md` con la línea de la SPEC y para.

## Cierre
`## HANDOFF` en `papers/p01-liquidity/output/F15_REQUISITOS.md`. Marca **F15** en `TASKS.md` y añade lecciones a
`kb/lessons/econometrics.md` (`Estado: candidata`). No hagas commit.
