# Encargo de los autores a la Dirección — 2026-11-04 · Mejora de los departamentos

## Petición literal de los autores
> "Quiero que la dirección investigue en foros o similares cómo mejorar las habilidades de cada
> departamento, meterle skills, info o estructura a los agentes de los distintos departamentos para que el
> proyecto sea mucho mejor. Que los agentes mejoren con más datos y más experiencia sin caer en
> alucinaciones o AI slop."

## Qué investigar (fuentes externas, con URL de cada afirmación)
1. **Diseño de agentes de investigación con Claude Code:** documentación oficial de Anthropic (subagents, skills,
   hooks, memoria, context engineering, evals); repositorios de flujos académicos (p. ej.,
   `pedrohcgs/claude-code-my-workflow`, `jfimbett/cloco`, el repositorio oficial de skills de Anthropic) y
   foros (r/ClaudeAI, r/ClaudeCode, Hacker News, blogs de economistas que usan agentes: Goldsmith-Pinkham,
   Cunningham ("Referee 2"), Sant'Anna, Korinek NBER w34202).
2. **Fallos de los "AI scientists" y cómo mitigarlos:** p. ej., arXiv 2601.03315 (*Why LLMs Aren't Scientists
   Yet*); citas alucinadas y protocolos de verificación; deriva de implementación; "eureka" / sobreafirmar.
3. **Aprendizaje desde la experiencia sin degradarse:** memoria episódica/reflexiva en agentes (p. ej., Reflexion,
   ExpeL, agent workflow memory), curación de memorias, cuándo la memoria empeora el rendimiento
   (contaminación, lecciones falsas), procedencia y caducidad de lecciones.
4. **Evaluación de agentes:** tareas "golden" con respuesta conocida por desk (replicar un resultado publicado,
   verificar citas conocidas, detectar un error plantado), tests de regresión al cambiar un prompt o una skill.
5. **Anti-"AI slop" en la escritura académica:** guías de estilo de revistas de economía, listas de patrones de
   texto generado que hay que evitar, cómo forzar que cada afirmación tenga evidencia.

## Qué tienes que entregar
`specs/research-desk/IMPROVEMENT_PROPOSAL.md`, con:
- **Por departamento** (Literatura, Teoría, Datos, Econometría, Redacción, Referee, Dirección): 3–6 mejoras
  concretas. Cada mejora indica:
  - el problema que resuelve;
  - la propuesta exacta: skill nueva (`.claude/skills/<nombre>/SKILL.md` con su contenido en borrador),
    checklist, documento de referencia en `kb/methods/`, hook, cambio en el prompt de `.claude/agents/<desk>.md`
    o tarea golden de evaluación;
  - la fuente (URL) y la **fuerza de la evidencia** (documentación oficial / paper / práctica reportada por
    varios usuarios / opinión aislada);
  - el coste (bajo/medio/alto) y la prioridad.
- **Un sistema transversal de mejora continua:** cómo entran las lecciones, quién las valida, cómo se evita
  que una lección falsa se propague, cómo se mide que una desk ha mejorado (evals) y cómo se revierte un cambio
  que empeora.
- **Un plan por fases** (qué implantar primero) y lo que **no** recomiendas, con el motivo.
- Las citas exactas no pueden pasar de 15 palabras por fuente; resume con tus palabras.

Añade además tus lecciones en `kb/lessons/scientific-director.md`.

## Reglas
- **No modifiques los agentes, las skills ni los hooks existentes.** Esto es una propuesta: la aprueban los
  autores y la implanta después la Coordinación.
- Cada recomendación con su fuente. Si algo es tu criterio y no viene de una fuente, márcalo **[criterio propio]**.
- No inventes URLs ni nombres de repositorios. Si una fuente no carga, dilo.
- Lee primero el estado actual: `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `kb/README.md`,
  `kb/lessons/*.md`, `specs/research-desk/*.md` y `papers/p01-liquidity/exploration/LITERATURE_REPORT.md`
  (ejemplo real de cómo trabajó Literatura: aprovéchalo para detectar los puntos débiles).
