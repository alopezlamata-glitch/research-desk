# F21 · Macros del paper A (`output/macros.tex`)

Generadas por `code/analysis/02_paper_macros.py` (`uv run python papers/p01-liquidity/code/analysis/02_paper_macros.py`). 135 macros, sin
estimar nada. Nombres y convención documentados en el docstring del script (LaTeX no admite dígitos en los nombres).

| Macros | Fuente |
|---|---|
| `bLin*`, `bC*` (6 filas: `Liq`, `LiqNov`, `RobFrom`, `RobQuart`, `RobLogit`, `RobLags`), `bU*` · `Est`, `Se`, `Dof` | `output/estimates_py.csv`, `output/estimates_py_robustness.csv` (3 decimales; el script comprueba que coinciden con la tabla) |
| `*P`, `*CiLo`, `*CiHi`, `\verdictoVs` | `output/tables/s1r_estimates.md:7-19,21` (tal como están impresos, sin recalcular) |
| `\NShockFull`, `\NShockNoV`, `\DiagFull*`, `\DiagNoV*` | `output/tables/s1r_shock_diagnostics.md:7-8` |
| `\betaRef`, `\betaRefSd`, `\piZero`, `\piZeroSe`, `\sdEps` | `output/tables/f13_checks.md:9` (= `f9_power.md:14`) |
| `\mdeEpsUnit`, `\mdeFfrUnit`, `\PwHomo*`, `\PwHet*` (c = 1: P(h0_falla), P(confirma), P(no concluyente), potencia H0, potencia H1) | `f13_checks.md:31,47` |
| `\MdeHomo*`, `\MdeHet*` (c con P(confirma) = 0,8; MDE en pp por pp de ε y de fed funds; máx. P(confirma) del rival) | `f13_checks.md:68-69` |
| `\SizeHomo`, `\SizeHet` (β = 0) | `output/tables/f9_power.md:719,791` |

## HANDOFF
**Hecho.**
- Script `code/analysis/02_paper_macros.py`, `output/macros.tex` y test `code/analysis/test_paper_macros.py` (3 tests: reproducibilidad,
  cada b contra CSV y tabla, y veredicto/diagnósticos/cifras ex ante).
- `uv run python tools/integrity.py`: `integridad: OK`. `uv run pytest papers/p01-liquidity`: 103 passed. `ruff check` limpio.
- F21 marcada `[x]` en `TASKS.md`. Sin commit, como pide el encargo.

**Evidencia.** Tabla de arriba (ruta:línea). Las 6 filas de b_C: `s1r_estimates.md:8,10,12,14,16,18`.

**Decisiones y quién las tomó.** Solo de formato, por esta desk: estimaciones y ee a 3 decimales (los de las tablas); p e IC tal cual
vienen impresos; los negativos van en `\ensuremath{}`.

**Supuestos y límites.**
- p e IC solo existen en la tabla markdown (3 decimales); no se recalculan.
- N de las muestras de choques (146 / 133) viene de los diagnósticos; los g.l. de cada regresión, del CSV.

**Descartado y por qué.**
- Macros de P(confirma) para c = 2…7 (están en `f13_checks.md:32-37,48-53`): no hacen falta para lo que fija la SPEC; se añaden si
  Redacción las pide.

**Pendiente de decidir.**
- El N de regresión de las filas `r1r_*` no está en ninguna fuente auditada (solo sus g.l.): no se ha calculado.
- Auditoría del Referee (F22): `code/` y `output/` han cambiado, así que la puerta de `paper/` caduca hasta entonces.
