# Research Desk — reglas de la desk

Desk de investigación económica operada por agentes Claude. Objetivo: **working papers
publicables**, con econometría seria y resultados replicables. Estas reglas aplican a todos
los papers; lo específico de cada paper vive en `papers/<slug>/SPEC.md`.

## Estructura

- `.claude/agents/` — las 6 desks (literatura, teoría, datos, econometría, redacción, referee).
- `kb/` — memoria compartida entre papers. Es lo que hace que la desk "aprenda".
- `specs/research-desk/` — diseño de la infraestructura de la desk.
- `papers/_template/` — esqueleto de un paper nuevo (`/new-paper <slug>`).
- `papers/<slug>/` — un paper: `SPEC.md` (pregunta + hipótesis prerregistradas), `PLAN.md`,
  `TASKS.md`, `prior/`, `data/`, `code/`, `theory/`, `audits/`, `output/`, `paper/`.

## Gobierno

- **Autores (humanos): la última palabra.** Deciden la pregunta, el diseño, las hipótesis, las
  desviaciones y qué se publica. Son los **únicos** que pueden levantar un RECHAZADO del Referee;
  la decisión queda registrada en `audits/` con su justificación.
- **Dirección**, con dos roles que comparten despacho:
  - **Director científico** (sesión en `desks/direccion-cientifica/`, rol en
    `.claude/agents/scientific-director.md`): qué merece la pena investigar y cómo. Genera y critica
    diseños y empuja hacia lo más ambicioso que sea creíble.
  - **Coordinación** (la sesión de la raíz del repo): quién hace qué y cuándo (ver abajo).
  - Cuando discrepan, presentan las dos posiciones a los autores, que arbitran.
- **Reunión de Dirección:** `/standup`.

## Coordinación (la sesión lanzada en la raíz del repo)

- Mantiene `SPEC.md`, `PLAN.md` y `TASKS.md` de cada paper y **asigna** cada tarea a una desk.
- **No hace el trabajo de una desk.** Lo delega de una de dos formas:
  - **Sesión de desk** (por defecto para trabajo sustantivo): se lanza en `desks/<desk>/`, desde
    **+ Agent** en la oficina o con `claude` en esa carpeta, y el personaje se sienta en su sala.
  - **Subagente** (`.claude/agents/<desk>.md`): solo para consultas cortas. Aparece al lado de la
    Dirección, no en la sala de la desk.
- Las sesiones largas de las desks se lanzan con `tools/desk.py launch` como **proceso independiente** (no ligado a la sesión de la
  Coordinación) con un encargo escrito en `desks/<desk>/ENCARGO_<fecha>.md` y su salida en
  `desks/<desk>/run_<fecha>.log`. Si la Coordinación se cierra, la desk sigue trabajando.
- Revisa lo entregado contra el criterio de "hecho" de la tarea y ordena la auditoría del Referee.
- Escala a los autores los bloqueos `[!]` científicos y los RECHAZADO del Referee; no los resuelve ella.
- Registra en la SPEC, como "Desviación" fechada, los cambios que deciden los autores.
- Como máximo 2 desks trabajando a la vez (límite de la suscripción).

## Flujo de trabajo

1. La **Coordinación** reparte las tareas en `TASKS.md` (ver arriba).
2. Las **hipótesis y reglas de decisión se escriben en `SPEC.md` antes de ver resultados**.
   Si después cambian, se añade una entrada fechada en la sección "Desviaciones" del SPEC
   explicando por qué. Nunca se reescriben en silencio.
3. Ningún resultado pasa a `paper/` sin un informe del **Referee** en `audits/` que lo apruebe.
   El Referee se lanza en **sesión nueva** desde `papers/<slug>/audits/` (no como subagente
   de la sesión del autor) para que no herede su razonamiento.
4. Al cerrar cada tarea, la desk añade lecciones a `kb/lessons/<desk>.md`. El humano revisa
   `kb/lessons/` semanalmente y promueve las buenas al prompt del agente.

## Reglas científicas (no negociables)

- **Nada de "duct tape" numérico.** Si un resultado es "casi correcto", hay un error. Se
  investiga la causa, no se ajusta un parámetro para que encaje.
- **No simplificar el modelo en silencio.** Si una especificación no converge o no es
  identificable, se documenta en `TASKS.md` y se escala al director. No se sustituye por
  otra más fácil sin registrarlo como desviación.
- **Toda derivación se verifica con SymPy** (`theory/check_*.py`). Una proposición sin
  verificación simbólica no entra en el paper.
- **Todo estimador nuevo o no estándar se valida con Monte Carlo** antes de aplicarlo a datos
  reales: ¿recupera los parámetros verdaderos con el T que tenemos?
- **Los tests se hacen sobre datos o sobre objetos no construidos con la hipótesis que se
  testea.** Un test calculado sobre una variable construida bajo el modelo no es "model-free".
- **Replicación cruzada:** el resultado principal se reproduce en R (`code/replication_r/`).
- **Las cifras del paper se generan con código**, nunca se copian a mano. Cada tabla y figura
  sale de `output/` y apunta al script que la produce.
- **Las citas tienen que ser verificables.** No se cita nada que la desk de Literatura no haya
  comprobado que existe (DOI, NBER, SSRN o la web del autor).

## Guardarraíles (automáticos; diseño en `specs/guardrails/SPEC.md`)

Las reglas comprobables no dependen de la memoria de nadie:
- **`tools/integrity.py`** comprueba claves, higiene de datos, citas, cifras tecleadas, paridad Python–R,
  registro de especificaciones, informes del Referee y lecciones. Lo ejecutan el **pre-commit** (nada que
  incumpla entra en git) y `uv run pytest`.
- **Hook `guard.js`:** datos brutos y `data/holdout/` son de solo lectura; `data/holdout/` no se lee hasta
  abrirla con `research.open_holdout()`; no se usa `--no-verify` ni se cambia `core.hooksPath`.
- **En los scripts de análisis:** cada especificación estimada se registra con `research.log_spec()`. Lo
  que no está en el bloque ```prereg``` del SPEC solo puede registrarse como exploratorio. Las estimaciones
  se exportan a `output/estimates_py.csv` y `output/estimates_r.csv` con las columnas
  `spec_id, term, estimate, std_error`.
- **En el `.tex`:** los resultados se escriben como macros generadas en `output/` (`\input{../output/macros.tex}`);
  una cifra no generada se marca `% num-ok` con su motivo.
- **Desks:** se lanzan con `uv run python tools/desk.py launch <desk> <ENCARGO.md>`, que impide dos sesiones
  de la misma desk, más de 2 desks a la vez y lanzar con poca memoria. `tools/desk.py status` muestra qué
  hay activo. En un clon nuevo, lo primero es `uv run python tools/desk.py setup`, que activa el pre-commit.
- **Skills** (en `.claude/skills/`): `verify-citation`, `sympy-check`, `mc-validate`, `referee-report`,
  `standup`, `new-paper`. Las desks las leen en `../../.claude/skills/<nombre>/SKILL.md`.
- **Lecciones:** cada una lleva `Estado: candidata|validada|retirada`. Solo los autores las pasan a
  `validada` (con `Validada por:`), y solo las validadas pueden promoverse al prompt de una desk.

## Datos

- `data/raw/` y `datalake/raw/` son **solo lectura**: el hook `guard.js` bloquea Edit/Write. Los datos brutos solo entran
  mediante scripts `code/data/download_*.py` que registran la fuente, la fecha de descarga y el
  hash en `data/raw/MANIFEST.csv`.
- `data/raw/` no se sube a git (se regenera con los scripts). `MANIFEST.csv` sí se versiona.
- **Nunca hay claves de API en el código.** FRED se descarga de `fredgraph.csv` sin clave; si una fuente
  necesita clave, se lee de una variable de entorno.
- `papers/*/prior/archive/` (material previo de los autores) está fuera de git: contiene claves antiguas.
- Antes de buscar una fuente nueva, mira `kb/data_catalog.md`. Las fuentes nuevas que se prueben
  se añaden al catálogo.

## Entorno

- Python ≥ 3.12 con `uv` (`pyproject.toml` en la raíz, un entorno compartido por todos los
  papers). Ejecutar con `uv run python ...`.
- R 4.5 (`C:\Program Files\R\R-4.5.1`) solo para la replicación cruzada (paquete `fixest`).
- Tests: `uv run pytest`. Linter: `uv run ruff check .`.
- Windows + OneDrive: no metas datos grandes en el repo. OneDrive sincroniza `.git` y puede
  generar conflictos.

## Visualización

La oficina visual es Pixel Agents (`npx -y pixel-agents --port 3100`, configuración `office` en
`.claude/launch.json`). Solo observa: recibe los eventos de Claude Code por hooks y no ejecuta nada.
Distribución:
- **Arriba, en planta abierta y en orden del pipeline:** Literatura → Teoría → Datos → Econometría.
- **Abajo:** Redacción (abierta), Dirección (despacho cerrado con mesa de reuniones) y Referee
  (cerrado y aislado).

Cada zona es un Area asociada a su carpeta (`.` para la Dirección, `desks/<desk>/` para el resto).
- **Lanzar una desk:** `cd desks/<desk>` y `claude`, o **+ Agent** en la oficina. Su personaje se sienta en su zona.
- **Configuración de cada desk:** `desks/<desk>/.claude/settings.json` hereda el hook `guard.js` y da acceso
  al repo (`additionalDirectories: ../..`).
- **Regenerar la oficina y esa configuración:** `node .claude/office/build_office.mjs`, **con el servidor parado**.
- **Vista previa en imagen:** `uv run python .claude/office/preview_office.py <assets> <salida.png>`.
