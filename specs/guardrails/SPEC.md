# Guardarraíles — SPEC

Aprobado por los autores el 2026-11-04 (Fases 0–1 de `specs/research-desk/IMPROVEMENT_PROPOSAL.md`).

## Objetivo
Que los errores que ya han ocurrido (citas inventadas, datos rellenados hacia atrás, claves en el código,
cifras tecleadas, resultados elegidos a posteriori, dos sesiones de la misma desk a la vez) **no puedan
volver a pasar en silencio**. Cada regla de CLAUDE.md que se pueda comprobar de forma determinista se
convierte en una comprobación automática; lo que no se pueda comprobar sigue siendo una regla escrita.

## Principios de arquitectura
1. **Determinista antes que modelo.** Una comprobación es código con tests, no un prompt.
2. **Un único punto de verdad por regla.** Cada regla vive en una función de `tools/integrity.py`; el
   pre-commit, pytest y las desks llaman a esa misma función.
3. **Varias capas de aplicación** (defensa en profundidad):
   - hook de Claude Code (`.claude/hooks/guard.js`): bloquea la acción antes de que ocurra;
   - pre-commit de git (`.githooks/pre-commit`): nada incumplidor entra en el historial;
   - `uv run pytest`: comprobación completa antes de dar algo por terminado.
4. **Excepciones explícitas y auditables.** Donde una regla admite excepción, se marca en la misma línea
   (`# hygiene-ok: <motivo>`, `% num-ok`) y queda en el diff.
5. **Cada comprobación tiene tests positivos y negativos** (detecta lo que debe y no da falsos positivos).

## Comprobaciones (`tools/integrity.py`)
| Id | Regla | Ámbito |
|---|---|---|
| `secrets` | Ninguna clave/token en archivos versionados (patrones + el valor real de `FRED_API_KEY`) | todo lo versionado |
| `hygiene` | Sin `bfill`/`backfill`, `interpolate` ni `TODO_SERIE_REAL` en código de datos/análisis | `papers/*/code/`, `datalake/fetch/` |
| `citations` | Toda cita del `.tex` existe en el `.bib` del paper con estado VERIFICADA | `papers/*/paper/` |
| `numbers` | Sin decimales ni porcentajes tecleados en el cuerpo del `.tex` (salen de macros generadas) | `papers/*/paper/` |
| `parity` | `estimates_py.csv` y `estimates_r.csv` coinciden (tolerancia 1e-6 relativa) | `papers/*/output/` |
| `speclog` | Toda especificación estimada está registrada; las no prerregistradas van marcadas como exploratorias | `papers/*/output/spec_log.csv` + bloque `prereg` del SPEC |
| `referee` | Informes del Referee con cabecera YAML válida y cada hallazgo con evidencia | `papers/*/audits/` |
| `lessons` | Cada lección tiene `Estado: candidata/validada/retirada`; las validadas, quién las validó | `kb/lessons/` |

## Hook de Claude Code (`guard.js`, sustituye a `protect-raw.js`)
- Escritura en `data/raw/`, `datalake/raw/` o `data/holdout/`: bloqueada.
- Lectura de `data/holdout/` (Read, Grep, Bash) antes de abrir la muestra reservada: bloqueada.
- `git commit --no-verify` / `-n` y cambios de `core.hooksPath`: bloqueados.

## Herramientas para las desks
- `tools/research.py`: `log_spec()` (registro de especificaciones) y `open_holdout()` (abre la muestra
  reservada una sola vez y deja constancia con el commit).
- `tools/desk.py`: lanzador de desks con bloqueo (una sesión por desk), máximo 2 a la vez, comprobación de
  memoria libre y registro de ejecuciones.
- `tools/symcheck.py` y `tools/mc.py`: utilidades de las skills `sympy-check` y `mc-validate`.

## Skills (procedimientos que se cargan al necesitarse)
`verify-citation`, `sympy-check`, `mc-validate`, `referee-report`.

## Límites conocidos (aceptados)
- `numbers` no detecta enteros tecleados (p. ej., "135 observaciones").
- `hygiene` es léxico: un relleno escrito a mano con un bucle no se detecta.
- El pre-commit comprueba el árbol de trabajo, no solo lo preparado para el commit.
- Un agente podría saltarse el hook de holdout con un intérprete (p. ej., Python leyendo el archivo); el
  registro de apertura y la auditoría del Referee son la segunda barrera.
