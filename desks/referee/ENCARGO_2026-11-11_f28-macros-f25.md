# Encargo de la Coordinación al Referee — 2026-11-11 · F28: comprobación corta de F25

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol y el formato de `.claude/skills/referee-report/SKILL.md`.
Sesión nueva: no leas el razonamiento de Econometría, solo su código y sus outputs.

## Objetivo
Un veredicto sobre el cambio de F25 (commit **a534f33**, auditado sobre HEAD) en `code/analysis/02_paper_macros.py`,
`code/analysis/test_paper_macros.py` y `output/macros.tex`. Última auditoría de estas macros: `audits/2026-11-08_F21_macros.md`
(F22), sobre 67bc9c2. La puerta de `paper/` está caducada hasta tu informe.

## Lee primero
- `papers/p01-liquidity/output/F21_MACROS.md` (`## HANDOFF F25`).
- `git diff 67bc9c2 HEAD -- papers/p01-liquidity/code papers/p01-liquidity/output`.
- `papers/p01-liquidity/output/tables/f9_power.md` §1b y `output/F9_MC_REPORT.md:30`.

## Qué auditar
1. Que el diff solo renombra las 4 macros con dígito (`PwHomoHzeroFalla`, `PwHetHzeroFalla`, `PwHomoPowHzero`, `PwHetPowHzero`)
   y añade `\CovAumNwHcLo/Hi`; que ningún valor existente cambia (compara macro a macro con 67bc9c2).
2. Que 0,948 y 0,990 son el rango real de cobertura aum, NW5+HC3, T completo (recalcúlalo desde el CSV/tabla fuente) y que
   la descripción "T completo" es correcta.
3. Que `macros.tex` compila: nombres solo letras, y una prueba mínima con `pdflatex`/`xelatex` (o `tex` disponible) de
   `\input{macros.tex}` + uso de cada macro nueva. Si no hay TeX instalado, dilo y valida con regex de control words.
4. Que ningún `.tex`/macro del repo sigue usando los nombres viejos. Actualiza (en `audits/`) tu `replication_2026-11-08_F22/check_macros.py:63`
   a los nombres nuevos, pues rompe la colección de `uv run pytest papers/p01-liquidity`.
5. Cita `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`.

## Entregable
`papers/p01-liquidity/audits/2026-11-11_F25_macros.md` con veredicto y hallazgos con `Evidencia:`.

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde.

## Condición de parada
Cuando hayas cubierto 1–5. Auditoría corta: no rehagas estimaciones.

## Cierre
`## HANDOFF` al final. Marca **F28** en `papers/p01-liquidity/TASKS.md`. No hagas commit.
