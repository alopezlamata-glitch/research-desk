# F21 · Macros del paper A (`output/macros.tex`)

Generadas por `code/analysis/02_paper_macros.py` (`uv run python papers/p01-liquidity/code/analysis/02_paper_macros.py`). 135 macros, sin
estimar nada. Nombres y convención documentados en el docstring del script (LaTeX no admite dígitos en los nombres).

| Macros | Fuente |
|---|---|
| `bLin*`, `bC*` (6 filas: `Liq`, `LiqNov`, `RobFrom`, `RobQuart`, `RobLogit`, `RobLags`), `bU*` · `Est`, `Se`, `Dof` | `output/estimates_py.csv`, `output/estimates_py_robustness.csv` (3 decimales; el script comprueba que coinciden con la tabla) |
| `*P`, `*CiLo`, `*CiHi`, `\verdictoVs` | `output/tables/s1r_estimates.md:7-19,21` (tal como están impresos, sin recalcular) |
| `\NShockFull`, `\NShockNoV`, `\DiagFull*`, `\DiagNoV*` | `output/tables/s1r_shock_diagnostics.md:7-8` |
| `\betaRef`, `\betaRefSd`, `\piZero`, `\piZeroSe`, `\sdEps` | `output/tables/f13_checks.md:9` (= `f9_power.md:14`) |
| `\mdeEpsUnit`, `\mdeFfrUnit`, `\PwHomo*`, `\PwHet*` (c = 1: `HzeroFalla` = P(h0_falla), `Confirma`, `NoConc`, `PowHzero` = potencia H0, `PowHone`; «Hzero» porque LaTeX no admite dígitos en nombres, F25) | `f13_checks.md:31,47` |
| `\CovAumNwHcLo`, `\CovAumNwHcHi` (F25: cobertura NW5+HC3 de `aum`, T completo; mín. y máx. de las 6 filas) | `f9_power.md:52-53` y las 4 filas `aum` T = 146/133 de §1b; = `F9_MC_REPORT.md:30` |
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

## HANDOFF F25 (Econometría, 2026-11-11)
**Hecho.**
- Renombradas a solo letras: `PwHomoHzeroFalla`, `PwHetHzeroFalla`, `PwHomoPowHzero`, `PwHetPowHzero` (`code/analysis/02_paper_macros.py:83`).
- Test `test_macro_names_are_latex_control_words` (`code/analysis/test_paper_macros.py:54`): falla si un nombre no es solo letras.
- `\todo` 6 de F23: el rango 0,948–0,990 SÍ está en una tabla auditada (`output/tables/f9_power.md` §1b, aum, NW5+HC3, T completo; coincide con `F9_MC_REPORT.md:30`, auditado en `audits/2026-11-05_F9*`). Macros `\CovAumNwHcLo`=0.948, `\CovAumNwHcHi`=0.990 (`02_paper_macros.py:91-97`) y test `test_aum_coverage_range_matches_f9_report`.
- Valores: `git diff output/macros.tex` solo toca los 4 nombres y añade 2 líneas; ningún valor existente cambia.
- `pytest papers/p01-liquidity --ignore=audits`: 108 passed; `ruff check` limpio. F25 marcada `[x]` en `TASKS.md`. Sin commit.

**Decisiones y quién las tomó.** Nombre `Hzero` (el que ya usa `main.tex`): Econometría. Rango tomado con T completo (6 filas), no T/2: coincide con la cifra del `\todo`.

**Supuestos y límites.** Comparé valores contra el `macros.tex` de HEAD (no extraje 67bc9c2 por permisos del shell); solo cambian las 4 líneas de nombre.

**Descartado.** Calcular nada nuevo: el rango se lee de la tabla.

**Pendiente de decidir.**
- `uv run pytest papers/p01-liquidity` completo falla en la colección: `audits/replication_2026-11-08_F22/check_macros.py:63` (del Referee) usa los nombres viejos. No lo toco; lo actualiza el Referee en F28.
- `integrity.py` da 1 violación esperada (puerta de `paper/` caducada hasta F28). `main.tex` no se toca; Redacción quita el rodeo en F29.
