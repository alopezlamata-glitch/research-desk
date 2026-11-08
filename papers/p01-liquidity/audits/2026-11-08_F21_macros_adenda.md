---
verdict: APROBADO
object: "Adenda a F22: las macros del paper A (F21) siguen válidas en 8dfa290, tras el commit de F5a"
date: 2026-11-08
commit: 8dfa290
reviewer: referee
session: fresh
---
## Resumen
La aprobación de F22 (`audits/2026-11-08_F21_macros.md`, commit 67bc9c2) caducó porque el commit de F5a (8dfa290) añade archivos en
`code/` y `output/`. Entre 67bc9c2 y 8dfa290, en las carpetas de la puerta solo hay archivos nuevos de F5a. `02_paper_macros.py`,
`macros.tex`, sus fuentes y `SPEC.md` no han cambiado, y `macros.tex` se regenera igual byte a byte. Se mantiene el veredicto y los
hallazgos de F22, sin hallazgos nuevos.

## Hallazgos
### En las carpetas de la puerta solo hay altas de F5a (comprobación, sin defecto)
`git diff --name-status 67bc9c2 8dfa290` da, en `code/` y `output/`, solo estado `A`: `code/data/f5a_coverage.py`,
`code/data/test_f5a.py` y cinco `output/tables/f5a_*`. No hay ningún `M` ni `D`. `data/`, `theory/`, `SPEC.md` y `paper/` no tienen
cambios. Fuera de la puerta solo cambian `TASKS.md` (F21, F22 y F5a/F5b marcadas), el informe y la replicación de F22, y
`exploration/F5A_ETAPA2_2026-11-08.md`. F5a escribe solo sus propios `f5a_*` (`code/data/f5a_coverage.py:90,95,116,136,143`) y no lee
ni escribe `macros.tex` ni sus fuentes.
Evidencia: `git diff --name-status 67bc9c2 8dfa290 -- papers/p01-liquidity`

### Script, macros y fuentes idénticos en los dos commits (comprobación, sin defecto)
Los blobs coinciden en 67bc9c2 y 8dfa290 para `code/analysis/02_paper_macros.py` (03f32ec), `output/macros.tex` (e91fee1),
`tables/s1r_estimates.md` (2be5406), `tables/s1r_shock_diagnostics.md` (af4e583), `tables/f13_checks.md` (b79fa4d),
`tables/f9_power.md` (e380076), `estimates_py.csv` (1d88be4), `estimates_py_robustness.csv` (01e8870) y `SPEC.md` (4bbef97).
Evidencia: `git rev-parse 67bc9c2:papers/p01-liquidity/output/macros.tex 8dfa290:papers/p01-liquidity/output/macros.tex` (lo mismo para cada ruta)

### `macros.tex` se regenera byte a byte (comprobación, sin defecto)
Con HEAD = 8dfa290, al regenerar `macros.tex`, git sigue sin ver cambios en el paper. El sha256 es `f0509801…484bd`, el mismo que en F22.
La replicación de F22 vuelve a dar 134/134 macros iguales a su celda de origen.
Evidencia: `uv run python papers/p01-liquidity/code/analysis/02_paper_macros.py` seguido de `sha256sum papers/p01-liquidity/output/macros.tex`
y `uv run python papers/p01-liquidity/audits/replication_2026-11-08_F22/check_macros.py`

## Replicación
Se reutiliza sin cambios `audits/replication_2026-11-08_F22/check_macros.py` sobre 8dfa290: 134 macros, 0 sin fuente, 0 ausentes,
0 distintas. La dif. máx. CSV−tabla es 4,81·10⁻⁴, de redondeo, igual que en F22.

## HANDOFF
**Veredicto:** APROBADO en 8dfa290. Siguen valiendo los hallazgos menores de F22: el MDE va como "≈ 10 pp" y F13 no tiene una
auditoría propia. Redacción (F23) puede usar `\input{../output/macros.tex}`.
**Límite:** esta adenda no audita F5a (puerta de la etapa 2); solo comprueba que no toca lo auditado en F22.
**Caducidad:** como siempre, cualquier cambio posterior en `code/`, `data/`, `output/`, `theory/` o `SPEC.md` exige otra comprobación.
