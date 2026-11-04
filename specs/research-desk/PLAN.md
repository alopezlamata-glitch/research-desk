# Research Desk — PLAN

## Arquitectura
```
Humano (director) ── Claude Code (sesión principal, suscripción)
                        ├── subagentes .claude/agents/*  (literatura, teoría, datos, econometría, redacción)
                        ├── Referee: sesión nueva aparte en papers/<slug>/audits/
                        ├── hooks: protect-raw (PreToolUse) + eventos de Pixel Agents
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

## Riesgos
- **Límites de la suscripción** con varios agentes en paralelo → por defecto, trabajo secuencial.
- **OneDrive + git:** la sincronización puede corromper `.git` o hacer lentos los datos grandes. Mitigación:
  datos fuera de git; si da problemas, mover el repo fuera de OneDrive.
- **Pixel Agents** puede no etiquetar a cada subagente con su nombre: verificar en T3.
- **Hook protect-raw** no cubre escrituras vía Bash (ver el comentario `ponytail:` en el script).
