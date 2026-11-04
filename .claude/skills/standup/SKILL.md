---
name: standup
description: Reunión de Dirección. Lee el estado de todos los papers y presenta a los autores una página con lo hecho, lo bloqueado, lo que espera decisión y las asignaciones propuestas. Úsalo cuando el usuario escriba /standup o pida "estado", "reunión" o "qué toca".
---

1. Lee `papers/*/TASKS.md` (excepto `_template`) y `papers/*/audits/` modificados desde el último standup
   (fecha en `kb/standups.md`; si no existe, todo).
2. Presenta **una página**, en este orden:
   - **Necesita decisión de los autores:** tareas `[!]`, informes del Referee RECHAZADO y desviaciones propuestas.
   - **Hecho desde el último standup:** una línea por tarea, con la ruta del output.
   - **En curso:** qué desk y desde cuándo.
   - **Asignaciones propuestas:** como máximo 2 desks a la vez (límite de la suscripción), indicando
     cómo lanzar cada una (`cd desks/<desk>` + `claude`, o **+ Agent** en la oficina).
   - **Lecciones nuevas en `kb/lessons/`** que conviene promover a un prompt.
3. No asignes nada hasta que los autores aprueben. Después marca las tareas asignadas en `TASKS.md`.
4. Añade la fecha y un resumen de 3 líneas a `kb/standups.md`.
