---
name: referee-report
description: Formato obligatorio del informe del Referee (cabecera YAML + hallazgos con evidencia). Úsalo siempre que el Referee escriba un informe en papers/<slug>/audits/.
---

El check `referee` de `tools/integrity.py` rechaza cualquier informe que no siga este formato, y el
pre-commit impide guardarlo en git.

**Archivo:** `papers/<slug>/audits/<AAAA-MM-DD>_<objeto>.md`

```markdown
---
verdict: APROBADO | APROBADO CON CAMBIOS | RECHAZADO
object: <qué se audita, p. ej. "LP de la tarea D4">
date: AAAA-MM-DD
commit: <hash corto auditado: git rev-parse --short HEAD>
reviewer: referee
session: fresh
---
## Resumen
Dos o tres líneas: qué se auditó y por qué el veredicto.

## Hallazgos
### <Título del hallazgo — mayor/menor>
Qué está mal, por qué importa y qué prueba lo resolvería.
Evidencia: `<comando que lo reproduce>` y/o <archivo>:<línea>

## Replicación
Script propio en audits/replication_<fecha>/, qué se comparó y la diferencia máxima.
```

**Reglas:**
- `session: fresh` solo si la sesión se lanzó nueva para la auditoría, sin heredar el razonamiento del autor.
- `commit` es el que se auditó. Si el autor cambia algo después, hace falta otra auditoría.
- **Cada hallazgo lleva su `Evidencia:`**, con un comando entre comillas invertidas o una ruta `archivo:línea`.
  Sin evidencia no es un hallazgo, es una opinión.
- Un RECHAZADO solo lo levantan los autores humanos.

Comprueba al final: `uv run python tools/integrity.py --only referee`.
