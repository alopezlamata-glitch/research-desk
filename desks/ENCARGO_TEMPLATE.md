# Encargo de la Coordinación a <Desk> — <fecha> · <Fn>: <título>

Modelo: <opus|sonnet|haiku>        <!-- sin línea, el de la desk (DEFAULT_MODEL en tools/desk.py) -->
Esfuerzo: <low|medium|high|xhigh|max>  <!-- opcional; sin línea, el de la CLI. Alto solo si la tarea lo justifica -->

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Una decisión o un resultado concreto, no "avanzar en X".

## Lee primero
- El `## HANDOFF` de la entrega anterior, si la hay (`<ruta>`). Abre los originales que cita solo cuando los necesites.
- Los archivos imprescindibles (`<ruta>`, `<ruta>:<sección>`). Lo que no esté aquí, no hace falta leerlo entero.

## Entregable
Qué archivo, en qué ruta y con qué contenido.

## Criterios de aceptación
Cómo comprueba la Coordinación que está hecho (tests, integrity.py, cifras que deben reproducirse…).

## Condición de parada
Cuándo parar aunque no esté todo: p. ej., "si tras N fuentes nuevas ninguna cambia la conclusión", "si el estimador no
converge con la especificación prerregistrada (no la cambies: anótalo en TASKS.md)".

## Cierre
Sección `## HANDOFF` al final del entregable: hecho; evidencia (ruta:línea, commit); decisiones y quién las tomó;
supuestos y límites; descartado y por qué; pendiente de decidir. La Coordinación revisa y marca la sesión con
`uv run python tools/desk.py estado <desk> <aceptada|rechazada|bloqueada|incompleta>`.
