# Encargo de la Coordinación al Referee — 2026-11-08 · F22: auditoría corta de las cifras del paper (F21)

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol y el formato de `.claude/skills/referee-report/SKILL.md`.

## Objetivo
Un veredicto sobre `code/analysis/02_paper_macros.py` y `output/macros.tex` en el **commit 67bc9c2**: que cada macro reproduce
su fuente auditada (F9, F13, F16/F17) sin transformarla, y que no aparece ninguna cifra nueva. La puerta de `paper/` caducó al
cambiar `code/` y `output/`; tu aprobación es la que permite a Redacción usar estas macros.

## Lee primero
- `papers/p01-liquidity/output/F21_MACROS.md` (`## HANDOFF`: tabla macro → fuente).
- El script, su test (`test_paper_macros.py`) y `output/macros.tex`.
- La Desviación del 2026-11-08 sobre el paper A al final de `papers/p01-liquidity/SPEC.md` (las 6 filas de b_C se muestran todas).

## Qué auditar
1. Que cada macro coincide con su fuente (CSV o tabla) y que los redondeos no cambian ninguna conclusión.
2. Que están las 6 filas de b_C y que no hay macros de cifras que no salgan de una fuente auditada.
3. Que el script es determinista y no estima nada.
4. `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`, citados en el informe.

## Entregable
`papers/p01-liquidity/audits/2026-11-08_F21_macros.md` con veredicto y hallazgos con `Evidencia:`.

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde.

## Condición de parada
Cuando hayas cubierto 1–4. Es una auditoría corta: no rehagas las estimaciones (ya replicadas en F17).

## Cierre
`## HANDOFF` al final. Marca **F22** en `papers/p01-liquidity/TASKS.md`. No hagas commit.
