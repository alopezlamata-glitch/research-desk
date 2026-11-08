---
verdict: APROBADO
object: "Segunda adenda a F22: las macros del paper A (F21) siguen válidas en 4b51d5f, tras la Desviación que cierra la etapa 2"
date: 2026-11-08
commit: 4b51d5f
reviewer: referee
session: fresh
---
## Resumen
La aprobación de F22 se renovó en 8dfa290 (`audits/2026-11-08_F21_macros_adenda.md`) y caducó con 4b51d5f, que modifica `SPEC.md`.
Entre 8dfa290 y 4b51d5f, lo único que cambia en las carpetas de la puerta son 4 líneas añadidas al final de las Desviaciones de la
SPEC: el cierre de la etapa 2. El prerregistro congelado conserva la huella 1d9476332d29. `code/`, `data/`, `output/`, `theory/` y
`paper/` no cambian, y `macros.tex` se regenera igual byte a byte. Se mantiene el veredicto, sin hallazgos nuevos.

## Hallazgos
### En la puerta solo cambia la Desviación añadida al final de la SPEC (comprobación, sin defecto)
`git diff --name-status 8dfa290 4b51d5f` lista `SPEC.md`, `TASKS.md`, la adenda anterior, `desks/RUNS.csv` y el encargo de F23. De
ellos, solo `SPEC.md` está en la puerta. Su diff es un único bloque de 4 líneas `+`, sin ninguna `-`, después de la última línea del
archivo: la entrada del 2026-11-08 "Los autores cierran la etapa 2 como 'no pasa la puerta'" (`SPEC.md:317-320`). No trae cifras
nuevas para el paper ni cambia la línea `Estado:`. El diff restringido a `code/ data/ output/ theory/ paper/` sale vacío.
Evidencia: `git diff 8dfa290 4b51d5f -- papers/p01-liquidity/SPEC.md` y
`git diff --name-status 8dfa290 4b51d5f -- papers/p01-liquidity/code papers/p01-liquidity/data papers/p01-liquidity/output papers/p01-liquidity/theory papers/p01-liquidity/paper`

### El prerregistro congelado no cambia (comprobación, sin defecto)
`uv run python tools/integrity.py --only prereg` → `integridad: OK`. `prereg_hash` de `tools/integrity.py:238`, aplicado a `SPEC.md`,
da `1d9476332d29` en 8dfa290, en 4b51d5f y en el árbol de trabajo. Es la huella que declara la Desviación de aprobación
(`SPEC.md:306`).
Evidencia: `uv run python tools/integrity.py --only prereg`

### Macros, script y fuentes idénticos; regeneración byte a byte (comprobación, sin defecto)
Los árboles git completos coinciden en los dos commits: `output/` 73bbd02, `code/` f04b7ba, `data/` 989ca18 y `theory/` e49d7cd. Eso
cubre `02_paper_macros.py` (03f32ec), `macros.tex` (e91fee1) y todas sus fuentes. Con HEAD = 4b51d5f, al regenerar `macros.tex` el
sha256 sigue siendo `f0509801…484bd`, el de F22, y git no ve cambios. La replicación de F22 da 134/134 macros iguales a su celda de
origen.
Evidencia: `git rev-parse 8dfa290:papers/p01-liquidity/output 4b51d5f:papers/p01-liquidity/output` y
`uv run python papers/p01-liquidity/audits/replication_2026-11-08_F22/check_macros.py`

## Replicación
Se reutiliza sin cambios `audits/replication_2026-11-08_F22/check_macros.py` sobre 4b51d5f: 134 macros, 0 sin fuente, 0 ausentes,
0 distintas. La dif. máx. CSV−tabla es 4,81·10⁻⁴, de redondeo, como en F22.

## HANDOFF
**Veredicto:** APROBADO en 4b51d5f. Siguen valiendo los hallazgos menores de F22: el MDE va como "≈ 10 pp" y F13 no tiene una
auditoría propia. Redacción (F23) puede usar `\input{../output/macros.tex}`.
**Límite:** no audito el contenido de la Desviación (es una decisión de los autores); solo compruebo que no toca lo auditado.
**Caducidad:** cualquier cambio posterior en `code/`, `data/`, `output/`, `theory/` o `SPEC.md` exige otra comprobación.
