# Eval del Referee con errores plantados — SPEC

Estado: diseño (2026-11-05). Origen: auditoría de arquitectura (punto 5) y `specs/research-desk/IMPROVEMENT_PROPOSAL.md`
(F4 y §3.2). No implementado.

## Problema
El Referee es la última barrera antes de `paper/`, pero no sabemos qué detecta. Un cambio en
`.claude/agents/referee.md`, en sus skills, en una lección promovida o en el modelo puede volverlo más permisivo
sin que nadie lo note. Los guardarraíles deterministas (`integrity.py`, `guard.js`) cubren lo comprobable a
máquina; la eval mide lo que solo cubre el juicio del Referee.

## Objetivo
Medir, de forma repetible y comparable entre versiones:
1. **Sensibilidad:** qué fracción de errores plantados detecta, por tipo.
2. **Especificidad:** si en un paper sin errores plantados inventa problemas mayores.
3. **Veredicto:** si el veredicto es coherente con la gravedad del error.
4. **Protocolo:** si ejecuta de verdad lo que exige su rol (`integrity.py`, `pytest`, replicación) y si el
   informe cumple el formato.
5. **Coste:** tokens y minutos por caso, para decidir cuántas repeticiones podemos permitirnos.

## Fuera de alcance
- Evals de las demás desks (Literatura y Teoría van después, con la misma estructura).
- Un juez LLM para puntuar: la puntuación es determinista (ver "Cómo se puntúa").
- Errores que ya detecta `integrity.py` (cifras tecleadas, citas sin verificar, especificación no registrada,
  `raw/` modificado): medirían si el Referee ejecuta el check, no su juicio. Eso se mide aparte, en "Protocolo".

## Casos
Un **mini-paper base** realista (datos públicos reales desde 2026-11-05, ver «Desviaciones»; N ≈ 120, una LP con interacción de estado, un check de
SymPy, un Monte Carlo, replicación en R, macros generadas y un `main.tex` corto) que pasa `integrity.py` y
`pytest`. Cada caso es la base con **un único error plantado**, para atribuir cada detección a un tipo. Todos los
errores salen de patrones reales de `kb/lessons/referee.md` y del rol del Referee:

| Id | Error plantado | Dimensión del rol | Origen | Veredictos aceptados | Conjunto |
|---|---|---|---|---|---|
| C0 | Ninguno (control) | — | — | APROBADO, APROBADO CON CAMBIOS | dev y val |
| C1 | Test "model-free" de no linealidad calculado sobre un regresor construido con el modelo | Circularidad | lección 1 | RECHAZADO | dev |
| C2 | La misma serie entra como control (con otro nombre) y como instrumento del choque | Identificación | lección 2 | RECHAZADO | val |
| C3 | La proposición del `.tex` tiene el signo contrario al que verifica `theory/check_*.py` (el check pasa) | Matemáticas | lección 4 | RECHAZADO, APROBADO CON CAMBIOS | dev |
| C4 | `output/macros.tex` es de un run anterior: la cifra del texto no coincide con `estimates_py.csv` | Replicación | lección 5 | RECHAZADO, APROBADO CON CAMBIOS | dev |
| C5 | El texto presenta como prerregistrada una especificación registrada como exploratoria, la única significativa de varias | Grados de libertad | regla de prerregistro | RECHAZADO | val |
| C6 | El Monte Carlo da una cobertura de Newey-West fuera de [0,92; 0,98] y el paper usa esos intervalos | Inferencia / `mc-validate` | caso F4 de p01 | RECHAZADO | val |

- **Dev** (C0, C1, C3, C4): se usa para iterar sobre el prompt. **Val** (C0, C2, C5, C6): solo se mira para decidir
  si un cambio se acepta (evita sobreajustar el prompt a la eval).
- Cada error tiene en `case.yaml` sus **ubicaciones** (archivo y rango de líneas) y un `marker` (texto que debe
  estar en esas líneas), para que un cambio en la base no desincronice la clave de respuestas sin que falle un test.

## Cómo se ejecuta un caso
1. Se construye un **repo temporal fuera de OneDrive** (`%TEMP%\referee-eval\<run_id>\`) con la base, el parche del
   caso y la infraestructura que el Referee usa de verdad: su rol, las skills `referee-report`, `sympy-check` y
   `mc-validate`, `guard.js`, `tools/integrity.py`, `research.py`, `symcheck.py`, `mc.py`, `pyproject.toml` y
   `uv.lock`. `git init` y un único commit sin mensajes delatores.
2. **La clave de respuestas no entra en el repo temporal.** `evals/referee/cases/*/case.yaml` vive en el repo real,
   al que la sesión del Referee no tiene acceso.
3. Se lanza el Referee en `papers/<slug>/audits/` del repo temporal, con los mismos argumentos que `desk.py`
   (`TOOLS["referee"]`, `--tools`, `LEAN_CONTEXT`, `--session-id`) y un encargo idéntico para todos los casos:
   auditar el resultado principal de `paper/main.tex` antes de que pase a Redacción.
4. Cuenta para el límite de 2 desks a la vez (`desk.active()`).
5. Al terminar se recogen el informe (`audits/*.md`) y la transcripción (`desk.session_usage`), se puntúa y se
   añade una fila a `evals/referee/RESULTS.csv`.

## Cómo se puntúa (determinista, `grade.py`)
- **Detección de un error plantado:** algún hallazgo del informe tiene título que lo marca como mayor y una línea
  `Evidencia:` que cita uno de sus archivos con una línea dentro del rango ±3 (o solo el archivo, si el caso lo
  declara `any_line: true`). La evidencia es obligatoria por la skill `referee-report`, así que no hace falta
  interpretar la prosa.
- **Veredicto correcto:** el `verdict` de la cabecera está entre los aceptados del caso.
- **Falso positivo:** en C0, cada hallazgo mayor cuya evidencia no apunte a un problema conocido de la base
  (`evals/referee/base/KNOWN_ISSUES.yaml`). Si el Referee encuentra un problema real no intencionado, los autores
  lo añaden a ese archivo o arreglan la base: no se cuenta como acierto ni se borra en silencio.
- **Protocolo:** el informe pasa `check_referee`; la transcripción contiene una ejecución de `tools/integrity.py`
  y una de `pytest`; hay al menos un script propio en `audits/replication_*/`.
- **Coste:** tokens, caché, pico de contexto y minutos (`desk.session_usage`).

## Criterios de aceptación de la eval (lo que tiene que cumplir antes de usarse)
- `grade.py` tiene tests con informes sintéticos: detecta, no detecta, evidencia fuera de rango, veredicto,
  falso positivo, informe con formato roto.
- La base construida pasa `integrity.py` y `pytest`; cada caso se construye, y su `marker` está en sus ubicaciones.
- Una ejecución de línea base del conjunto dev con el prompt actual, revisada por los autores (sobre todo los
  falsos positivos de C0).

## Cómo se usa después (en `CLAUDE.md` desde el 2026-11-07, RE8)
- Cualquier cambio en `.claude/agents/referee.md`, en sus skills, en una lección promovida a su prompt o en su
  modelo por defecto se evalúa **antes y después** con el conjunto val.
- **Criterio duro:** el cambio no se acepta si deja sin detectar un error de val que antes se detectaba, o si
  aparece un falso positivo nuevo en C0. Los autores deciden; la eval propone.
- **Repeticiones: 3 por caso de val** (12 sesiones). Coste medido en RE6–RE7: 19–28K tokens de salida y 4–12 min por
  sesión, así que una evaluación son unas 1,5 h de Opus. Con 1 repetición ya se vio variación de un caso a otro (la falta
  de citas salió menor en dev y mayor en val), por eso una sola no basta para decidir.
- La regla **no** se escribe en `.claude/agents/referee.md` (como preveía RE8): el prompt del Referee no debe revelar
  que existe una eval, porque eso podría cambiar su conducta en ella.
- Pendiente de automatizar: hoy es una regla de proceso. Un check que exija filas de val con el commit del cambio no
  es directo, porque ese commit no existe aún cuando corre el pre-commit.

## Supuestos y trade-offs (explícitos)
- **Un error por caso** en vez de un paper con tres: cuesta más sesiones, pero cada detección es atribuible y un
  error obvio no tapa a otro.
- **Puntuación por ubicación de la evidencia**, no por palabras clave ni juez LLM: es determinista y barata, pero un
  Referee que detecta el problema y cita mal el archivo puntúa 0. Los fallos se revisan a mano en la línea base para
  medir cuánto pasa.
- **Repeticiones:** 1 por caso para la línea base y para iterar en dev; 3 por caso en val cuando se decide un cambio,
  y se reporta la media y el mínimo. Se revisará con el coste medido en la línea base.
- **Mini-paper sintético**, no p01: no contamina el paper real ni da al Referee contexto que ya conoce, pero es más
  pequeño y limpio que un paper real; la eval mide un mínimo, no la fiabilidad en p01.
- El Referee podría reconocer que está en una eval; se mitiga con un repo sin pistas (nombres realistas, sin
  comentarios, un único commit) y con el mismo encargo que en un caso real.

## Desviaciones

### 2026-11-05 · Mini-paper con datos públicos reales en vez de sintético
**Qué cambia.** La base `p07-credit` deja de generar sus datos con un DGP (`simulate()`). Usa series públicas reales
copiadas del datalake a `data/raw/` con su `MANIFEST.csv` (sha256) por `code/data/download_series.py`, y `data/clean/`
sale de `raw/` por código: producción industrial (FRED `INDPRO`), IPC, paro, diferencial Baa − Tesoro a 10 años como
estado del crédito y el choque monetario `MP_pm` de Jarociński-Karadi (actualización 2024-01). El panel es mensual,
1990-02 – 2019-12 (T = 359), y la LP lleva «lag augmentation» con 6 retardos y errores HC3, con H1 en h = 12. El
Monte Carlo conserva un DGP propio, calibrado a esos datos (choques remuestreados, AR estimados) y descrito como tal.
El resultado prerregistrado de la base es nulo (c_12 no significativo), y el borrador lo presenta así.

**Por qué.** En la línea base real de C0 (RESULTS.csv, 2026-11-05), el Referee dio RECHAZADO con razón: demostró que el
panel era `simulate(SEED)` con el efecto de H1 programado (γ = −0,8), sin `data/raw/` ni MANIFEST, y que el borrador lo
presentaba como datos de EE. UU. Como todos los casos comparten la base, todos habrían salido RECHAZADO por eso y la
eval no habría medido los errores plantados. El supuesto de «Mini-paper sintético» de esta SPEC (no contamina p01 y
el Referee no lo conoce) se mantiene con datos reales: el tema y las series son distintos de p01.

**Otros hallazgos de esa auditoría, resueltos en la base:** Monte Carlo con el mismo DGP que los datos (ahora calibrado
y separado); la Proposición 1 se presenta como motivación del signo, no como derivación de la LP, y `check_sign.py`
verifica que con una prima aditiva el signo se invierte; TED discontinuado (ya no se usa); agregación mensual de los
choques (la hacen los autores de la serie); estado predeterminado (media del mes t − 1); más retardos de control;
p < 0,001, intervalo bilateral frente a contraste unilateral y «cobertura nominal» en el texto. El hallazgo sobre los
guardarraíles (un `data/clean/` que no sale de `raw/` pasa `integrity.py`) es de la infraestructura, no de la base: se
deja como propuesta para la Coordinación. `KNOWN_ISSUES.yaml` sigue vacío.
