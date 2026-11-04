# kb — memoria compartida de la desk

Los modelos no aprenden entre sesiones; lo que aprende es esta carpeta. Las desks la leen al
empezar una tarea y escriben en ella al terminar.

| Carpeta | Contenido | Quién escribe |
|---|---|---|
| `lessons/<desk>.md` | Errores cometidos y cómo evitarlos. Entradas fechadas y breves. | Cada desk al cerrar una tarea |
| `methods/` | Recetas reutilizables: cómo hacemos X aquí, con sus trampas | Econometría, Teoría |
| `topics/<topic>/` | Conocimiento de dominio: README con el mapa de literatura y `papers/` con fichas | Literatura |
| `library/` | Biblioteca de papers: `*.pdf` (originales), `md/*.md` (texto para leer), `INDEX.md` (estado y fuente de cada uno). Solo `INDEX.md` va a git | Teoría/Literatura descargan; `tools/pdf2md.py` convierte |
| `data_catalog.md` | Fuentes de datos con su estado (probada / rota / sin probar) | Datos, Literatura |

**Leer papers (todas las desks):**
1. Busca el paper en `library/INDEX.md`.
2. Lee `library/md/<clave>.md`, no el PDF: cuesta muchos menos tokens. Lee solo las páginas que necesites, guiándote por los marcadores `<!-- p. N -->`. Cita siempre con número de página.
3. Abre el PDF solo para fórmulas, tablas o figuras: la extracción automática puede dañarlas.
4. Tras añadir PDFs nuevos: `uv run python tools/pdf2md.py`. Es incremental: solo convierte lo nuevo.

**Curación (humano, semanal):** revisa `lessons/`, borra lo trivial y promueve las lecciones
recurrentes al prompt de la desk (`.claude/agents/<desk>.md`).

Formato de una lección:
```
## 2026-11-03 · p01 · <título corto>
Qué pasó. Por qué. Regla para la próxima vez.
```
