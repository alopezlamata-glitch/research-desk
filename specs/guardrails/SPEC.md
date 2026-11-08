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
| `prereg` | El prerregistro congelado no cambia sin Desviación (ver abajo) | `papers/*/SPEC.md` con bloque `prereg` |
| `gate` | Un `.tex` que usa resultados (`output/`) exige un informe APROBADO cuyo commit sea antecesor de HEAD y sin cambios científicos del paper desde entonces | `papers/*/paper/` + `papers/*/audits/` |
| `rawhash` | Cada archivo de `raw/` tiene fila en su MANIFEST y su sha256 es el de la última; cada vintage coincide con el hash de su nombre | `datalake/raw/`, `papers/*/data/raw/` |
| `lessons` | Cada lección tiene `Estado: candidata/validada/retirada`; las validadas, quién las validó | `kb/lessons/` |

## Hook de Claude Code (`guard.js`, sustituye a `protect-raw.js`)
- Escritura en `data/raw/`, `datalake/raw/` o `data/holdout/`: bloqueada.
- Lectura de `data/holdout/` (Read, Grep, Bash) antes de abrir la muestra reservada: bloqueada.
- `git commit --no-verify` / `-n` y cambios de `core.hooksPath`: bloqueados.
- **Referee** (2026-11-05): si la sesión se lanzó en `desks/referee/` o en `papers/<slug>/audits/` (`CLAUDE_PROJECT_DIR`,
  que no cambia con un `cd`), Write/Edit solo pasan en `papers/<slug>/audits/`, `papers/<slug>/TASKS.md` (marcar su tarea)
  y `kb/lessons/referee.md`. Comprobado en vivo con una sesión real del Referee.

## Herramientas para las desks
- `tools/research.py`: `log_spec()` (registro de especificaciones) y `open_holdout()` (abre la muestra
  reservada una sola vez y deja constancia con el commit).
- `tools/desk.py`: lanzador de desks con bloqueo (una sesión por desk), máximo 2 a la vez, comprobación de
  memoria libre y registro de ejecuciones.
- `tools/symcheck.py` y `tools/mc.py`: utilidades de las skills `sympy-check` y `mc-validate`.

## Skills (procedimientos que se cargan al necesitarse)
`verify-citation`, `sympy-check`, `mc-validate`, `referee-report`.

## Prerregistro congelado (`prereg`, 2026-11-05)
- **Qué se congela:** el texto desde el último encabezado `## ` anterior al bloque ```prereg``` hasta el cierre del bloque
  (pregunta, hipótesis, reglas de decisión e ids). Lo que va después (requisitos previos, replicación) puede tacharse sin Desviación.
- **Cómo:** una línea `prereg_commit: <sha>` en el SPEC, con el commit en que los autores aprobaron el prerregistro.
  `integrity.py` compara el texto congelado actual con el de ese commit (`git show`).
- **Cambiar el prerregistro:** si el texto difiere, su huella (`prereg <12 hex>`, sha256 del texto normalizado) tiene que
  aparecer en la sección `## Desviaciones`, en la entrada fechada que registra la decisión de los autores. El mensaje de
  la violación da la huella que hay que copiar. Así cada versión del prerregistro es la aprobada o una declarada.
- **Por estimación:** `research.log_spec()` guarda la huella vigente en `spec_log.csv` (columna `prereg`).
- **Por qué no solo el commit de `log_spec`:** ese commit prueba con qué código se estimó, pero no que el prerregistro
  fuese el aprobado; un id añadido después al bloque pasaba como prerregistrado.

## Puerta de `paper/` (`gate`, 2026-11-05)
- Un `.tex` de `papers/<slug>/paper/` que referencia `output/` (macros, tablas o figuras) solo pasa si en `audits/` hay un
  informe con `verdict: APROBADO` o `APROBADO CON CAMBIOS` cuyo `commit` es antecesor de HEAD (`git merge-base --is-ancestor`)
  y sin cambios desde ese commit en `code/`, `data/`, `output/`, `theory/` ni `SPEC.md` del paper, salvo su párrafo `Estado:` (`git diff --name-only`
  contra el árbol de trabajo, 2026-11-08). Un cambio científico posterior exige una auditoría nueva; uno de redacción no.
- El texto sin resultados (introducción, literatura) no necesita auditoría.

## Datos brutos verificables (`rawhash` y vintages, 2026-11-05)
- `guard.js` solo intercepta Write/Edit; un script podía modificar `raw/` sin dejar rastro. `rawhash` compara cada
  archivo con su MANIFEST en cada commit (162 MB en ~1 s), así que cualquier escritura fuera de los scripts de descarga
  bloquea el commit, venga de la herramienta que venga.
- Un archivo registrado que falta no es violación: `raw/` no está en git y se regenera.
- **Vintages:** `datalake/fetch/_common.install()` no sobrescribe un archivo con contenido distinto: el anterior pasa a
  `raw/<source>/_vintages/<stem>.<sha12><suffix>`. Así se recupera cualquier sha256 del MANIFEST aunque la fuente
  revise la serie.
- Al implantarlo aparecieron dos fallos: `us_misc.py` escribía los parquets de Treasury sin registrarlos (corregido y
  registrados tras comprobar que son `DataFrame` del JSON registrado), y dos xlsx de Bauer-Swanson que no genera ningún
  script, copias exactas del vintage 2023-12 (uno de ellos con el nombre `…_vintage2025-08.xlsx`).

## Límites conocidos (aceptados)
- `rawhash` no impide la escritura, la detecta en el siguiente commit; y quien edite a la vez el archivo y su fila del
  MANIFEST lo esquiva (el MANIFEST sí está en git, así que el cambio se ve en el diff).
- Referee: la regla cubre Write/Edit, no un script lanzado con `uv run python` que escriba fuera de `audits/`. La
  barrera completa es auditar en un worktree de solo lectura del commit auditado (pendiente). Un Referee lanzado como
  subagente desde otra carpeta no se reconoce; CLAUDE.md ya exige sesión nueva.
- `prereg`: quien cambie la línea `prereg_commit` re-congela el prerregistro; es un cambio visible en el diff, y se
  reserva a los autores. Sin git (copia sin historial), `prereg` y `gate` fallan en vez de pasar.
- `gate` no comprueba que el informe aprobado cubra precisamente los outputs citados ni que no haya un RECHAZADO
  posterior; ligar los hashes de los outputs al informe es el siguiente paso.
- `numbers` no detecta enteros tecleados (p. ej., "135 observaciones").
- `hygiene` es léxico: un relleno escrito a mano con un bucle no se detecta.
- El pre-commit comprueba el árbol de trabajo, no solo lo preparado para el commit.
- Un agente podría saltarse el hook de holdout con un intérprete (p. ej., Python leyendo el archivo); el
  registro de apertura y la auditoría del Referee son la segunda barrera.
