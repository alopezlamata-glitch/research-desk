# Research Desk — PLAN

## Arquitectura
```
Humano (director) ── Claude Code (sesión principal, suscripción)
                        ├── subagentes .claude/agents/*  (literatura, teoría, datos, econometría, redacción)
                        ├── Referee: sesión nueva aparte en papers/<slug>/audits/
                        ├── hooks: guard.js (PreToolUse; ver specs/guardrails) + eventos de Pixel Agents
                        └── git = registro de todo
Pixel Agents (npx, :3100) ── lee los eventos de Claude Code ── oficina en el navegador (solo observa)
```

## Decisiones
| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| Claude Code como orquestador | FastAPI + Agent SDK + Redis | Cero código propio; compatible con la suscripción; subagentes, hooks y skills ya existen |
| Pixel Agents (MIT) para la oficina | Construir una oficina en Next.js/PixiJS | Ya soporta Windows, modo navegador, subagentes y Agent Teams, y zonas mapeadas a carpetas |
| Referee en sesión aparte | Referee como subagente | Independencia: no hereda el razonamiento del autor |
| Memoria en Markdown (`kb/`) curada por el humano | Memoria automática / vector DB | Auditable, versionada en git; el humano filtra el ruido |
| Un entorno `uv` compartido | Un entorno por paper | Más simple; si un paper necesita fijar versiones distintas, se le da su propio `pyproject` |
| Hooks en Node | Hooks en Python | Node ya está instalado y Python no; sin dependencias |
| Subagentes por defecto, Agent Teams solo en sprints | Agent Teams siempre | Agent Teams es experimental y consume mucha cuota de la suscripción |
| Telemetría de desks leída de la transcripción de Claude Code (`~/.claude/projects/*/<session_id>.jsonl`), con el `session_id` fijado al lanzar | `--output-format json`/`stream-json` en el log | La transcripción ya guarda `usage` por turno y sobrevive a una sesión muerta; `json` solo da el resultado al final y quita el resumen legible del log |
| `desk.py resume` con `--resume <session_id>` | Escribir un encargo de continuación | Una sesión cortada por el límite de la suscripción sigue con su contexto en vez de releerlo todo (caso del 2026-11-04 23:48) |

## Riesgos
- **Límites de la suscripción** con varios agentes en paralelo → por defecto, trabajo secuencial.
- **OneDrive + git:** la sincronización puede corromper `.git` o hacer lentos los datos grandes. Mitigación:
  datos fuera de git; si da problemas, mover el repo fuera de OneDrive.
- **Pixel Agents** puede no etiquetar a cada subagente con su nombre: verificar en T3.
- **Hook guard.js:** sus límites conocidos están en `specs/guardrails/SPEC.md`.
