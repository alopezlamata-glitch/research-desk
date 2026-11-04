# IMPROVEMENT_PROPOSAL — Mejora de las desks (Dirección, 2026-11-04)

Estado: **propuesta, pendiente de aprobación de los autores.** No se ha modificado ningún agente, skill ni hook.
Encargo: `desks/direccion-cientifica/ENCARGO_2026-11-04_mejora-desks.md`. Tarea: T8.

## 0. Cómo leer este documento

**Fuerza de la evidencia:** `DOC` documentación oficial · `PAPER` paper o preprint (casi todos son preprints 2025–26, no revisados) ·
`PRÁCTICA` práctica reportada por varios usuarios · `OPINIÓN` fuente aislada · `[criterio propio]` mío, sin fuente.
**Coste:** B/M/A. **Prioridad:** P1 (hacer ya) · P2 · P3.

**Limitaciones de la investigación (importante):**
- **No he leído** foros (r/ClaudeAI, r/ClaudeCode, Hacker News): la herramienta de búsqueda no los devolvió. Nada de lo que sigue se apoya en ellos.
- `github.com/jfimbett/cloco` devolvió **404**; no lo uso.
- Las notas sobre Cunningham y Goldsmith-Pinkham vienen de **resúmenes de terceros** (wiki de Velikov, páginas de skills), no de sus textos originales. Su fuerza es PRÁCTICA, no verificada en origen.
- Varios papers los conozco solo por resumen del buscador (marcados "resumen"). Antes de implantar algo que dependa de uno, Literatura debe leerlo.
- De arXiv 2601.03315 la página solo lista los modos de fallo; **no pude ver las 4 recomendaciones de diseño** de los autores. Leer el PDF antes de citarlas.

### Fuentes (todas abiertas o devueltas por búsqueda en esta sesión)
| ID | Fuente | URL | Tipo |
|---|---|---|---|
| S1 | Subagentes (frontmatter `memory`, `skills`, `hooks`, `isolation`, `model`) | https://code.claude.com/docs/en/sub-agents | DOC |
| S2 | Skills (`SKILL.md`, `disable-model-invocation`, `context: fork`, `paths`, evaluar con/sin skill) | https://code.claude.com/docs/en/skills | DOC |
| S3 | Hooks (determinismo; hooks de prompt y de agente) | https://code.claude.com/docs/en/hooks-guide | DOC |
| S4 | Anthropic, *Writing tools for agents* (evals realistas, verificables, set de validación) | https://www.anthropic.com/engineering/writing-tools-for-agents | DOC |
| S5 | Anthropic, *Effective context engineering* (notas estructuradas, subagentes, recuperación just-in-time) | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | DOC |
| S6 | Repositorio oficial de skills | https://github.com/anthropics/skills | DOC |
| S7 | Trehan & Chopra, *Why LLMs Aren't Scientists Yet* | https://arxiv.org/abs/2601.03315 | PAPER |
| S8 | Sant'Anna, `claude-code-my-workflow` | https://github.com/pedrohcgs/claude-code-my-workflow | PRÁCTICA (repo leído) |
| S9 | Skill `did-event-study` de ese repo | https://raw.githubusercontent.com/pedrohcgs/claude-code-my-workflow/main/.claude/skills/did-event-study/SKILL.md | PRÁCTICA (solo snippet) |
| S10 | Korinek, *AI Agents for Economic Research*, NBER w34202 | https://www.nber.org/papers/w34202 | PAPER (solo abstract) |
| S11 | Cunningham, serie Claude Code (Referee 2, medición de error) | https://causalinf.substack.com/p/claude-code-changes-how-i-work-part · resumen: https://velikov-mihail.github.io/ai-econ-wiki/summaries/cc-series-24-agents-auditing-did | PRÁCTICA (secundaria) |
| S12 | Goldsmith-Pinkham, miniserie Markus Academy (resumen) | https://velikov-mihail.github.io/ai-econ-wiki/summaries/getting-started-economists | PRÁCTICA (secundaria) |
| S13 | Zhao et al., auditoría de ~111 M referencias | https://arxiv.org/abs/2605.07723 | PAPER (resumen) |
| S14 | Preprint de citas fabricadas, taxonomía existing/unresolved/fabricated | https://arxiv.org/pdf/2603.07287 | PAPER (resumen) |
| S15 | Survey de memoria en agentes (error autorreforzante) | https://arxiv.org/pdf/2603.07670 | PAPER (resumen) |
| S16 | *Honest Lying* (confabulación en agentes reflexivos) | https://arxiv.org/pdf/2605.29463 | PAPER (resumen, crítica de tercero) |
| S17 | ExpeL | https://arxiv.org/pdf/2308.10144 | PAPER |
| S18 | Shin (Philadelphia Fed), bucle de agente auditable: evaluador inmutable, log de búsqueda, holdout | https://arxiv.org/pdf/2603.17381 | PAPER (resumen) |
| S19 | Vaccaro, preregistro para experimentos con agentes | https://arxiv.org/pdf/2606.11217 | PAPER (resumen) |
| S20 | `phack`, benchmark de p-hacking para agentes | https://pypi.org/project/phack/0.4.1/ | PRÁCTICA (paquete) |
| S21 | CORE-Bench | https://arxiv.org/pdf/2409.11363 | PAPER |
| S22 | PaperBench | https://arxiv.org/abs/2504.01848v3 | PAPER |
| S23 | Vocabulario LLM en escritura científica (los marcadores decaen) | https://neurips.cc/virtual/2026/164099 | PAPER (resumen) |
| S24 | Marcadores estilométricos en abstracts | https://arxiv.org/pdf/2602.03864 | PAPER (resumen) |
| S25 | Skill Referee 2 de la comunidad | https://lcrawfurd.github.io/claude-skills/referee2 | PRÁCTICA |
| S26 | Bug reportado: subagentes que devuelven informes sin ejecutar herramientas | https://claudeissues.com/issue/67730-subagents-return-fully-hallucinated-results-with-zero-tool-calls-leaked-tool-cal | OPINIÓN (un issue) |

## 1. Diagnóstico de partida (qué falla hoy, con evidencia del propio repo)

1. **Las citas de los borradores eran falsas o mal atribuidas** (`LITERATURE_REPORT.md` §1: ≥6 graves, p. ej. Caballero-Simsek AER 2021, Reichlin-Turner-Woodford JEP). Hoy la verificación es manual, por prompt, y se hizo *después* de que el error entrara. Los datos externos van en la misma dirección (S13, S14).
2. **Cobertura incompleta y silenciosa:** ~25 clásicos y "~60 citas" sin verificar; la Línea 2 tiene ~5 verificados de 8–10 pedidos; v22 no se pudo leer. No hay un indicador que diga "esto está al X % verificado".
3. **Las lecciones son texto libre sin procedencia ni caducidad.** `kb/README.md` solo dice "borra lo trivial y promueve las recurrentes". Una lección falsa se promovería igual que una verdadera (riesgo descrito en S15, S16).
4. **No existe ninguna eval** de ninguna desk. Un cambio de prompt hoy no se puede medir ni revertir (S4, S2 recomiendan medir con/sin).
5. **Grados de libertad del investigador:** el CLAUDE.md prerregistra hipótesis, pero nada impide que un agente pruebe 200 especificaciones y reporte una (S18, S19, S20).
6. **Falta `kb/lessons/econometrics.md` y `kb/lessons/writer.md`:** los prompts les mandan escribir ahí y los ficheros no existen; `kb/methods/` tiene 1 receta.
7. **El Referee es una sola persona-prompt** sin checklist ejecutable ni protocolo de qué replicar; y su independencia depende de que alguien lo lance en sesión nueva (la regla vive en prosa).

## 2. Mejoras por departamento

> Convención: los borradores de skills van completos pero cortos. Las skills de Claude Code se cargan solo cuando son relevantes, por lo que el coste en contexto es bajo (S2).

### 2.1 Literatura

**L1 · Skill `verify-citation` + estados de verificación en el `.bib`** — P1 · coste M
- *Problema:* citas inventadas pasan con revista, volumen y páginas completos (diagnóstico 1). Verificar "por plausibilidad" no funciona.
- *Propuesta:* skill con un protocolo fijo de tres estados (existing / unresolved / fabricated; taxonomía de S14) y un campo obligatorio en cada entrada de `references.bib`: `note = {verified: <estado>; via: <URL/DOI>; checked: <fecha>}`. Un test `pytest` (ver T1 en §4) falla si una entrada citada en `paper/*.tex` no está `verified: existing` o si el título del registro no coincide con el del `.bib`.
- *Fuente / evidencia:* S13, S14 (PAPER, resumen); el problema es medido en el propio repo (`LITERATURE_REPORT.md`) — evidencia local fuerte.

Borrador `.claude/skills/verify-citation/SKILL.md`:
```markdown
---
name: verify-citation
description: Verifica que una referencia existe y dice lo que se le atribuye. Úsalo antes de añadir o citar cualquier entrada de references.bib.
---
Para cada referencia, en este orden y deteniéndote en el primer acierto:
1. DOI → resolver en doi.org / Crossref. 2. RePEc/IDEAS (`RePEc:<handle>`). 3. NBER/SSRN/BIS/Fed.
4. Web del autor o de la revista.
Compara **título exacto, autores, año y revista** del registro con los del .bib. Cualquier diferencia = `unresolved`.
Estados: `existing` (coincide), `unresolved` (no se pudo comprobar), `fabricated` (el registro contradice la cita
o no existe tras 3 vías). "Accepted/forthcoming" solo se admite con la página de la revista; si no, cita el WP.
Escribe el resultado en el campo `note` del .bib y una línea en `kb/topics/<topic>/verification_log.md`
(referencia · estado · vía · fecha). Nunca "reparar" una cita completando datos que no figuran en el registro.
Verificar la existencia no verifica la afirmación: para cualquier cifra o resultado atribuido, abre el texto
(o márcalo `claim: unread`).
```

**L2 · Campo `claim: read | abstract-only | unread` en cada ficha de `kb/topics/*/papers/`** — P1 · coste B
- *Problema:* las fichas "provisionales hasta leer el texto" se pueden citar como si fueran lecturas. Esto ya pasó con v22 (no extraída).
- *Propuesta:* cada ficha lleva ese campo; Redacción solo puede apoyar una afirmación cuantitativa en fichas `read`. Añadir al prompt de Literatura: "no extraigas cifras de un abstract".
- *Fuente:* [criterio propio], motivado por S7 (sobreafirmación) y por `kb/lessons/literature.md`.

**L3 · Informe de cobertura al cierre de cada mapa** — P2 · coste B
- *Problema:* "no he llegado a 8–10 por línea" quedó escondido en el texto.
- *Propuesta:* tabla fija al inicio de todo `LITERATURE_REPORT`: nº de refs por estado y por línea frente al objetivo. [criterio propio]

**L4 · Segundo pase independiente sobre las citas "graves"** — P2 · coste B
- *Propuesta:* una verificación hecha por la desk de Literatura se contrasta por muestreo (10 %) por una segunda sesión sin acceso a la primera. Es la misma lógica que el Referee, aplicada a las citas. [criterio propio] apoyado en S11 (independencia entre ejecuciones).

**L5 · Golden eval de Literatura** — P1 · coste B (ver §3.2).

### 2.2 Teoría

**T-1 · Skill `sympy-check` con plantilla de verificación** — P1 · coste B
- *Problema:* el error de signo de v22 (`kb/lessons/theory.md`) se halló a posteriori. La regla ya existe ("toda derivación con SymPy") pero cada check se reescribe desde cero.
- *Propuesta:* skill con una plantilla `check_<nombre>.py`: (a) restar el resultado del paper y el derivado simbólicamente y exigir `simplify(...) == 0`; (b) evaluar numéricamente en el punto de calibración; (c) contraejemplo numérico aleatorio de 50 puntos para signos. Tres capas porque la simbólica puede fallar por simplificación y la numérica por elegir un punto malo.
- *Fuente:* [criterio propio]; el caso real es el de `kb/lessons/theory.md`.

Borrador `.claude/skills/sympy-check/SKILL.md`:
```markdown
---
name: sympy-check
description: Plantilla para verificar una proposición, signo o umbral con SymPy. Úsalo en toda derivación nueva.
---
Crea `papers/<slug>/theory/check_<nombre>.py` con: 1) `claim` (texto + ecuación del .tex); 2) derivación simbólica
independiente (no copies el resultado del texto); 3) `assert simplify(texto - derivado) == 0`; 4) evaluación
numérica en la calibración, con la cifra impresa; 5) 50 puntos aleatorios en el dominio para signos de derivadas;
6) un test negativo: el mismo check aplicado a la afirmación *contraria* debe fallar.
Si algo falla, la proposición no entra; escribe la lección en kb/lessons/theory.md.
```

**T-2 · Test negativo obligatorio ("el check puede fallar")** — P1 · coste B. Un check que nunca falla no prueba nada (el repo de Sant'Anna exige probar cada comprobación contra defectos plantados; S8, PRÁCTICA). Incluido en el borrador anterior.

**T-3 · `kb/methods/` como biblioteca de derivaciones verificadas** — P2 · coste M. Cada derivación genérica con su `check_` adjunto y la fecha de verificación; la desk la lee antes de re-derivar. Es recuperación just-in-time (S5, DOC). Hoy solo existe `ces-nesting.md`.

**T-4 · Tabla de supuestos → propiedades en cada modelo (`theory/ASSUMPTIONS.md`)** — P2 · coste B. Ya está en el prompt; convertirlo en entregable con formato fijo permite al Referee auditarlo. [criterio propio]

**T-5 · Contar parámetros calibrados vs estimados antes de cerrar un DGP** — P2 · coste B. Es el fallo nº 3 de `kb/lessons/referee.md` (≥12 calibrados vs 8 estimados, T = 135). Salida obligatoria `theory/PARAMS.csv` con columnas {parámetro, estimado/calibrado, fuente, identificado por}. [criterio propio]

### 2.3 Datos

**D1 · Tests de integridad como contrato (`pytest` parametrizado)** — P1 · coste M
- *Problema:* los cinco errores de `kb/lessons/data.md` (extrapolar y estimar, `bfill`, renombrar series, marcadores que se quedan, claves) son todos *detectables mecánicamente*.
- *Propuesta:* un `tests/test_data_hygiene.py` común que recorre `papers/*/code/` y falla si encuentra: `bfill(`, `interpolate(` fuera de una lista permitida documentada, el literal `TODO_SERIE_REAL` o patrones de clave (`api_key\s*=\s*["']`), y, por cada parquet, que no haya fechas posteriores al último dato original (columna `is_extended`). Un hook `PostToolUse` sobre Write/Edit de `code/data/` puede avisar antes.
- *Fuente:* hooks = determinismo (S3, DOC); contenido [criterio propio] a partir de lecciones locales.

**D2 · Columna `observed` y política de extensión** — P1 · coste B. Toda serie extendida lleva una máscara booleana en el parquet; econometría filtra por ella. Evita el error nº 1 (AR(1) hasta el final). [criterio propio]

**D3 · Diccionario con "papel" separado del "nombre"** — P2 · coste B. Cada fila: `nombre_real`, `papel` (proxy de X / instrumento / control). Resuelve el error nº 3, y habilita la tabla "qué serie entra dónde" que pedía el Referee (`kb/lessons/referee.md` nº 2). [criterio propio]

**D4 · Segunda descarga de contraste (hash) en fuentes críticas** — P3 · coste B. Redescargar a un directorio temporal y comparar hash; detecta revisiones silenciosas (caso de la serie FRBSF actualizada en ago-2025). [criterio propio]

**D5 · Golden eval de Datos** — P2 (ver §3.2).

### 2.4 Econometría

**E1 · Registro de especificaciones y evaluador inmutable** — P1 · coste M
- *Problema:* un agente puede lanzar cientos de especificaciones en una sesión y no hay traza; el CLAUDE.md prerregistra hipótesis, pero no controla la búsqueda.
- *Propuesta:* (a) todo script de `code/analysis/` escribe una fila por especificación estimada en `output/spec_log.csv` (id, hash del script, muestra, N, parámetro, estimación, p) vía una función común; (b) el resultado principal solo puede ser una especificación **declarada en SPEC.md** (el log demuestra que se ejecutó tal cual); (c) el *holdout* temporal o de submuestra se reserva en la SPEC y se abre una sola vez; (d) el informe de robustez reporta cuántas especificaciones se probaron en total.
- *Fuente:* S18 (PAPER, resumen; encuentra que las ganancias del agente no se sostienen en el holdout), S19 (PAPER, resumen), S20 (herramienta: en datos con efecto cero halló 1.000 de 25.920 especificaciones significativas al 5 %). Fuerza: media, tres fuentes convergentes, todas preprints.

**E2 · Skill `mc-validate` (Monte Carlo antes de datos reales)** — P1 · coste M
- *Problema:* la regla existe en el CLAUDE.md pero no hay un formato de informe; el Referee no puede comprobar qué se simuló.
- *Propuesta:* skill con salida fija `output/tables/mc_<estimador>.csv`: sesgo, RMSE, cobertura nominal vs empírica del IC al 95 %, potencia, para el T real **y** para T/2, con ≥1.000 réplicas y semilla. Regla de parada: cobertura fuera de [0.92, 0.98] ⇒ estimador no interpretable, se escala a la Dirección. [criterio propio] (umbral convencional; ajustable).

Borrador `.claude/skills/mc-validate/SKILL.md`:
```markdown
---
name: mc-validate
description: Valida un estimador con Monte Carlo antes de usarlo con datos reales. Úsalo para todo estimador nuevo o no estándar.
---
1. Importa el DGP de `theory/dgp.py`; no lo reescribas. 2. Mismo T, mismas variables observadas que en los datos reales.
3. ≥1000 réplicas, semilla fija, y repite con T/2. 4. Guarda `output/tables/mc_<estimador>.csv` con sesgo, RMSE,
cobertura del IC 95 % y potencia por parámetro. 5. Si la cobertura empírica sale de [0.92, 0.98] o el sesgo supera el 10 %
del parámetro, el estimador queda `NO INTERPRETABLE`: registra en TASKS.md y escala. No cambies el DGP para que salga bien.
```

**E3 · Replicación en R como entregable de la propia desk** — P1 · coste M. El CLAUDE.md ya la exige (`code/replication_r/`, `fixest`). Añadir: script que compara automáticamente Python y R y falla si difieren en >1e-6 relativo en coeficientes y errores estándar. Cunningham y la comunidad usan la replicación en un segundo lenguaje porque un error de implementación rara vez coincide en ambos (S11, S25; PRÁCTICA, secundaria). Nota: la aritmética de "independencia de errores" que se cita en el resumen de S11 es [criterio propio] hasta leer el original; un modelo comparte sesgos entre lenguajes, así que no la trataría como independencia total.

**E4 · Skills de diseño con defaults razonados** (p. ej. `did-event-study`, `local-projections`, `iv-weak`) — P3 · coste M. S9 muestra el patrón: semilla obligatoria, TWFE solo como benchmark, parar si el tratamiento no es absorbente. Para esta desk, el primer candidato es `local-projections` (el diseño de p01); contenido a definir con Teoría/Dirección. Evidencia PRÁCTICA, un único repo.

**E5 · `kb/lessons/econometrics.md` y `kb/methods/` con recetas** — P2 · coste B. El prompt lo exige y el archivo no existe. Crear al aprobar.

### 2.5 Redacción

**R1 · Tabla afirmación → evidencia (`paper/CLAIMS.csv`) y comprobación mecánica** — P1 · coste M
- *Problema:* "cada afirmación tiene evidencia" es hoy una frase del prompt. Y los borradores previos tenían cifras incoherentes entre figura y tabla (`kb/lessons/referee.md` nº 5).
- *Propuesta:* cada afirmación cuantitativa o causal del texto tiene una fila: `claim_id, sección, tipo (descriptiva/asociación/causal/literatura), fuente (output/..., o bib key), informe del Referee que la cubre`. Un script comprueba que (i) todo `\cite{}` está `verified: existing`, (ii) toda cifra en el `.tex` sale de `\input` o de una macro generada, nunca tecleada, (iii) cada fila `causal` apunta a un diseño que el Referee aprobó como identificado.
- *Fuente:* [criterio propio]; el principio "juicio humano y verificación por scripts" aparece en S12 (PRÁCTICA, secundaria) y S7 (sobreafirmación como fallo típico).

**R2 · Skill `slop-check` basada en evidencia, no en listas de palabras** — P2 · coste B
- *Problema:* "no uses fórmulas retóricas" es vago. Pero las listas de palabras "de IA" **decaen**: el vocabulario se difunde en toda la población y los marcadores más reconocibles desaparecen bajo presión de detección (S23, resumen). Una lista de palabras prohibidas es frágil y puede dar falsos positivos (S24: pensado para tendencias poblacionales, no para juzgar un texto).
- *Propuesta:* la skill no prohíbe vocabulario: pide revisar cinco **funciones** del texto: (1) frase sin afirmación comprobable (relleno), (2) adjetivo de énfasis sin cifra, (3) verbo causal sin diseño causal, (4) contraste retórico "no X sino Y" donde X no lo sostiene nadie, (5) párrafo que podría ir en cualquier paper del campo (genérico). Cada hallazgo se resuelve borrando o ligando a una fila de `CLAIMS.csv`.
- *Fuente:* S23, S24 para el diseño; las cinco funciones son [criterio propio]. No encontré una guía de estilo de revista económica con checklist anti-IA; **no cito ninguna**.

Borrador `.claude/skills/slop-check/SKILL.md`:
```markdown
---
name: slop-check
description: Revisa un borrador académico por relleno, énfasis sin evidencia y lenguaje causal injustificado. Úsalo antes de enviar una sección al Referee.
---
Lee la sección y, por cada párrafo, marca solo estos casos (no busques palabras concretas):
A. Frase sin contenido comprobable → bórrala. B. Énfasis sin cifra ("striking", "substantial") → pon la cifra o quítalo.
C. Verbo causal ("drives", "causes", "effect of") sin diseño causal aprobado → baja a "is associated with".
D. Contraste retórico cuyo polo negado no defiende nadie → reescribe afirmando lo que se muestra.
E. Párrafo intercambiable con otro paper del campo → concreta con el objeto, dato o parámetro de este paper.
Salida: tabla {línea, caso, acción}. No reescribas la sección entera: la autoría de cada frase es de la desk.
```

**R3 · Cifras solo por macros generadas** — P1 · coste M. Script `output/make_macros.py` que genera `numbers.tex` (`\newcommand{\betaMain}{0.158}`); el hook rechaza un número de tres o más dígitos significativos tecleado en una sección. [criterio propio]; encaja con la regla actual ("las cifras salen de código").

**R4 · Registro de correcciones de estilo (`kb/lessons/writer.md`)** — P3 · coste B. Crear el archivo; entradas con el formato nuevo (§3.1).

### 2.6 Referee

**F1 · Checklist ejecutable y salida estructurada** — P1 · coste B
- *Problema:* el informe es prosa libre; no se puede comparar entre auditorías ni medir si el Referee detecta errores (necesario para evals).
- *Propuesta:* informe con cabecera YAML (`veredicto`, `objeto`, `hallazgos: [{id, severidad, evidencia, prueba_que_lo_resuelve}]`) y secciones fijas. La skill del Referee añade el protocolo de "cinco dimensiones" que ya usa y la lista de patrones de `kb/lessons/referee.md` como checklist de arranque. Fuente de formato: S25 y S11 (informe con Major/Minor concerns, PRÁCTICA).

**F2 · Independencia forzada por hook y no solo por norma** — P1 · coste B
- *Problema:* la independencia depende de que alguien lance la sesión desde `audits/`.
- *Propuesta:* hook `SessionStart` en `papers/*/audits/.claude/settings.json` que verifica que no hay historial del autor en el contexto (carga solo SPEC y rutas) y deja constancia en el informe: "sesión nueva: sí". Alternativa más simple: skill con `context: fork`, que arranca un subagente sin el historial (S2, DOC). Mi preferencia: sesión nueva desde `audits/` (ya es la regla), más la línea de constancia. Cunningham insiste en que el auditor que revisó dentro de la misma sesión viola el protocolo (S25, PRÁCTICA).

**F3 · "Verifica que el subagente ejecutó algo"** — P2 · coste B. Un issue público reporta subagentes que entregaron informes completos sin una sola llamada a herramientas (S26, OPINIÓN: un único reporte). Aun así, la defensa es barata: el Referee debe citar en cada hallazgo el comando que ejecutó o el archivo:línea que leyó; un hallazgo sin eso se descarta. [criterio propio]

**F4 · Tests de detección de errores plantados** — P1 · coste M (ver §3.2). Es la mejor forma de medir la sensibilidad del Referee.

**F5 · Registro de RECHAZADO y levantamientos** — P3 · coste B. `audits/LEDGER.csv` (fecha, objeto, veredicto, quién levantó, justificación). Hoy la norma exige registro, pero sin formato. [criterio propio]

### 2.7 Dirección (Director científico)

**C1 · Ficha de candidato con test "paper mínimo si sale cero"** — P2 · coste B. Ya está en el prompt; hacerlo campo obligatorio y puntuable. Evita proyectos sin salida si el resultado es negativo.

**C2 · Dos revisiones adversarias antes de elevar un candidato** — P2 · coste B. Cunningham usa un agente "abogado del diablo" distinto del que propone, y el segundo reconoció vulnerabilidades que el primero había minimizado (S11, resumen). Propuesta: cada candidato pasa por una sesión con el único encargo de rebatirlo y cuyos argumentos se anexan a la ficha.

**C3 · Prerregistro con registro del espacio de decisión (Vaccaro)** — P2 · coste B. En SPEC.md, sección nueva: "decisiones de análisis permitidas" y "decisiones fijadas". Mismas fuentes que E1 (S19).

**C4 · Revisión de novedad con 3–5 vecinos verificados** — P1 · coste B. Ya figura en el prompt; la novedad se afirma sólo con referencias `verified: existing` y fichas `claim: read` (L1, L2). El caso `LITERATURE_REPORT.md` §3 (tres papers que amenazan la contribución, leídos solo por resumen) lo ilustra: cualquier decisión de continuar o abandonar sobre esa base debe esperar a la lectura.

**C5 · Trazabilidad de decisiones de Dirección** — P3 · coste B. Cada elección entre candidatos queda en `exploration/DECISIONS.md` con fecha y alternativas. [criterio propio]

## 3. Sistema transversal de mejora continua

### 3.1 Cómo entra una lección y quién la valida
El problema: una lección escrita por un agente tras una tarea puede ser **falsa pero plausible** (causalidad mal diagnosticada) y, una vez en un prompt, se aplica en todos los papers. La literatura sobre memoria de agentes lo describe como error autorreforzante cuya gravedad crece con la vida del agente (S15) y critica que reglas globales destiladas sin restricción pueden consolidarse como confabulaciones (S16, crítica de tercero; el propio ExpeL, S17, es el sistema criticado). Ambos son preprints; tratar como riesgo plausible, no como hecho medido.

**Formato nuevo de lección** (sustituye al actual; las entradas existentes se migran):
```
## 2026-11-04 · p01 · <título>
estado: candidata | validada | retirada
evidencia: <ruta o URL reproducible: informe del Referee, check_*.py, commit>
alcance: <desk> | <paper concreto | general>
caduca: <fecha de revisión, por defecto +6 meses>
regla: <una frase imperativa y comprobable>
```
**Reglas del ciclo:**
1. **Entrada:** la desk escribe como `candidata`, sin tocar prompts. Obligatorio enlazar **evidencia reproducible** (un test, un informe, un commit). Sin evidencia ⇒ no entra.
2. **Validación:** nunca la valida la misma desk que la escribió. La valida (a) el Referee (si es de método/error), o (b) un autor humano en la curación semanal. Una lección `validada` exige que se haya visto **en ≥2 ocasiones o en ≥2 papers**, o que un check automático la reproduzca. [criterio propio]
3. **Preferencia por automatizar:** si la lección se puede convertir en un test, hook o check, se hace eso en vez de añadir prosa al prompt (S3: los hooks son deterministas y no dependen de que el modelo obedezca).
4. **Promoción al prompt:** sólo las `validadas` y recurrentes, de una en una, cada una con su eval (§3.2). El repo de Sant'Anna usa un proceso de "promoción" por consejo de críticos (S8, PRÁCTICA); lo adoptamos con humano como decisor final.
5. **Caducidad y retirada:** a la fecha `caduca`, se revisa; se retira si ya no se reproduce, si el modelo mejoró, o si choca con una lección más reciente. Las retiradas no se borran: pasan a `estado: retirada` con motivo (evita reintroducirlas).
6. **Presupuesto:** los prompts de las desks no pasan de ~150 líneas (cada línea es contexto permanente; S2). Cuando se llegue al límite, para añadir una regla hay que retirar otra. Lo largo va a skills o a `kb/methods/` y se carga solo cuando hace falta (S2, S5).

### 3.2 Evals: cómo se mide que una desk mejora
Principio: tareas realistas con resultado verificable, ejecutables de forma programática, con un conjunto de *validación* separado del de desarrollo para no sobreajustar los prompts a las evals (S4, DOC). Y comparar con/sin el cambio en sesiones nuevas (S2, DOC).

**Directorio:** `evals/<desk>/<id>/` con `task.md` (encargo), `fixtures/`, `expected.yaml` (respuesta conocida) y `grade.py` (puntúa 0–1 de forma determinista cuando se pueda).

| Desk | Tarea golden (con respuesta conocida) | Se puntúa por |
|---|---|---|
| Literatura | Lista de 20 referencias: 10 reales, 5 con un dato alterado (año/revista), 5 inventadas. Debe clasificarlas existing/unresolved/fabricated. | Precisión y *recall* de `fabricated`; cero falsos `existing` es el criterio duro. |
| Teoría | Proposición del repo con signo conocido (la convexidad de $\delta(d)$ de `kb/lessons/theory.md`) y otra con signo *invertido* plantado. | ¿El check detecta el error plantado y confirma la correcta? |
| Datos | Descargar un dataset FRED pequeño con respuesta conocida y limpiar un CSV con defectos plantados (duplicados, salto de unidades, `bfill` tentador). | Defectos detectados / plantados; el hash final coincide. |
| Econometría | Replicar un resultado publicado con datos públicos y coeficiente conocido (a elegir por los autores; CORE-Bench, S21, es el modelo de tarea, pero pertenece a otras disciplinas), y un Monte Carlo con DGP de sesgo conocido. | Error relativo del coeficiente; cobertura estimada vs verdadera. |
| Redacción | Sección con resultados de un `output/` de prueba y un resultado no causal: debe escribirse sin lenguaje causal y con cada cifra procedente de macro. | `CLAIMS.csv` completo; 0 cifras tecleadas; 0 verbos causales injustificados. |
| Referee | Un mini-paper con **3 errores plantados** (circularidad, signo, cifra tabla≠figura). | Errores detectados / 3; falsos positivos. |
| Dirección | 5 fichas, 2 con un defecto de identificación conocido. | ¿Las puntúa por debajo de las demás, con la razón correcta? |

**Disciplina:**
- **Dos conjuntos:** desarrollo (se usa para iterar) y validación (se mira sólo al decidir). [S4]
- **Repetir**: 3 ejecuciones por tarea; el LLM es estocástico. Se reporta media y mínimo. [criterio propio]
- **Métricas auxiliares:** nº de llamadas a herramientas, tokens, errores, tiempo (S4). Además, para Referee y Literatura: tasa de falsos positivos.
- **Disparadores:** se ejecutan las evals de la desk afectada cuando cambia su `.claude/agents/<desk>.md`, una skill que usa, o una lección promovida; y todas ellas ante un cambio de modelo.
- Los benchmarks externos de replicación (CORE-Bench, PaperBench; S21, S22) muestran que los agentes aún reproducen mal resultados publicados (mejores resultados originales ≈21 %), lo que justifica no esperar de las desks una fiabilidad que las evals no hayan medido. Son resultados de 2024–25 con modelos anteriores.

### 3.3 Cómo se revierte un cambio que empeora
1. **Un cambio por commit** (prompt, skill, lección promovida), con mensaje que cite la eval que lo justifica (regla ya presente en el CLAUDE.md global: commits atómicos).
2. Cada cambio se evalúa **antes y después** con las evals de su desk. Si la métrica principal baja o aparece un falso `existing` (Literatura) o un error plantado no detectado (Referee), **se revierte con `git revert`** y la lección pasa a `retirada` con el motivo.
3. `evals/RESULTS.csv` (fecha, commit, desk, métrica) como histórico; una caída respecto a la media móvil de 3 ejecuciones abre una tarea `[!]` para los autores.
4. Los autores deciden siempre; la reversión automática no existe, sólo la **propuesta** de reversión.

### 3.4 Contra la deriva y la sobreafirmación (S7)
S7 lista como fallos de un científico automatizado: sesgo por defecto, deriva de la implementación, pérdida de contexto, exceso de confianza, poco conocimiento de dominio y mal juicio experimental. Mapa a nuestras medidas: deriva → E1 (log de especificaciones); pérdida de contexto → notas estructuradas en `TASKS.md` y `kb/` (S5); exceso de confianza → F1/F3 (hallazgos con prueba) y R1; juicio experimental → C2 y Referee; dominio → `kb/methods/` y `kb/topics/` (T-3).

## 4. Plan por fases

**Fase 0 (1–2 días, bajo coste, desbloquea todo)**
- Crear `kb/lessons/econometrics.md` y `kb/lessons/writer.md`; migrar las lecciones existentes al formato nuevo (§3.1). [E5, R4]
- Campo `verified:` en `.bib` y `claim:` en fichas. [L1 parcial, L2]
- Decidir, los autores, el paper de replicación publicado para la eval de Econometría.

**Fase 1 (semana 1–2): guardarraíles deterministas (P1)**
- T1: un `tests/test_integrity.py` con (i) citas del `.tex` todas `verified: existing` [L1], (ii) higiene de datos [D1, D2], (iii) cifras solo por macros [R3], (iv) la comparación Python–R [E3].
- Skills: `verify-citation`, `sympy-check`, `mc-validate`.
- Log de especificaciones `spec_log.csv` y regla de holdout en SPEC [E1].
- Informe del Referee con YAML y constancia de sesión nueva [F1, F2].

**Fase 2 (semana 3–4): evals (P1/P2)**
- Montar `evals/` con las 3 desks de mayor riesgo: **Literatura, Referee, Teoría** (tareas con respuesta conocida y baratas de construir).
- Línea base de cada una *antes* de cualquier cambio de prompt.
- Curación semanal con el nuevo flujo de lecciones.

**Fase 3 (mes 2): resto de evals y skills de contenido (P2)**
- Evals de Datos, Econometría, Redacción, Dirección. `slop-check`, `CLAIMS.csv`. Abogado del diablo para candidatos [C2].
- Biblioteca `kb/methods/` con derivaciones verificadas [T-3].

**Fase 4 (más adelante, P3)**
- Skills de diseño por método (`local-projections` primero), doble descarga de datos, ledger de RECHAZADO.

## 5. Lo que NO recomiendo (y por qué)

1. **Memoria automática o base vectorial que se alimenta sola de las sesiones.** El campo describe el error autorreforzante (S15, S16), y la desk ya decidió (PLAN.md) una memoria auditable. Mantener el humano como validador. *(Existe `memory:` para subagentes, S1, DOC: útil para notas locales de la desk, no para conocimiento que entra en el prompt. Si se usa, `project` scope, versionado.)*
2. **Listas fijas de "palabras de IA" prohibidas.** Decaen y dan falsos positivos (S23, S24). Mejor revisión por función (R2).
3. **Un "consejo de agentes" que se vote a sí mismo para validar lecciones o resultados.** Los agentes comparten sesgos del modelo; el voto no sustituye a una prueba reproducible ni a un humano. [criterio propio]
4. **Confiar en la independencia total entre Python y R.** Sirve para errores de implementación, no para errores de concepto del modelo (§2.4 E3). Mantener también la auditoría conceptual.
5. **Más de 2 desks en paralelo, o Agent Teams por defecto.** Va contra los límites de suscripción ya decididos (CLAUDE.md, PLAN.md). Sin cambios.
6. **Subir el tamaño de los prompts de las desks.** Cada regla permanente cuesta contexto en cada tarea (S2). Preferir skills que se cargan al necesitarlas y hooks.
7. **Hooks con modelo (tipo prompt/agente) para decisiones críticas.** Existen (S3, DOC) pero un hook determinista y verificable es preferible para bloqueos; reservar los de modelo para avisos.
8. **Evals que usan siempre el mismo LLM como juez sin comprobación.** Donde se pueda, `grade.py` determinista; si hace falta juez, validarlo contra una muestra revisada por un humano (S4 recomienda criterios de comprobación flexibles pero verificables).
9. **Usar los foros como fuente de "mejores prácticas" sin contraste.** No pude leerlos y la práctica reportada es anecdótica; sólo adoptar lo que se pueda convertir en un test local.

## 6. Decisiones que necesito de los autores
1. ¿Aprobáis la Fase 0–1 tal como está?
2. ¿Qué paper publicado con datos públicos queremos como eval de replicación de Econometría?
3. ¿Quién valida las lecciones `candidata → validada`: ¿vosotros en la curación semanal, o el Referee para las de método?
4. ¿Se permite a Literatura leer PDFs completos (aprobación de scripts de extracción) para poder pasar fichas a `claim: read`? Es el principal bloqueo de calidad actual.
