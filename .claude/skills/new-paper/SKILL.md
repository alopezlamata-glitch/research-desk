---
name: new-paper
description: Crea un paper nuevo en la desk a partir de papers/_template. Úsalo cuando el usuario quiera empezar un paper o escriba /new-paper <slug>.
---

1. Pide el `slug` si no viene (formato `pNN-palabras-clave`; NN = siguiente número libre en `papers/`).
2. Copia la plantilla: `cp -r papers/_template papers/<slug>`.
3. Entrevista breve al usuario para rellenar `papers/<slug>/SPEC.md`: pregunta, contribución,
   hipótesis con su regla de decisión, datos candidatos y qué paper de referencia se replicará primero.
   No rellenes las hipótesis tú solo: son decisión del usuario.
4. Si el tema es nuevo, crea `kb/topics/<topic>/README.md` y pide a la desk de Literatura un mapa inicial.
5. Si hay versiones previas del paper (PDF), cópialas a `prior/` y pide al Referee un diagnóstico.
6. Escribe `PLAN.md` y `TASKS.md` con tareas pequeñas, cada una asignada a una desk.
