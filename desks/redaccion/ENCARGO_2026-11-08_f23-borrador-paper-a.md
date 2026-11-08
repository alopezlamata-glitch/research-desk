# Encargo de la Coordinación a Redacción — 2026-11-08 · F23: borrador del paper A de p01

Modelo: opus
Esfuerzo: high

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Un primer borrador completo del working paper p01 en `papers/p01-liquidity/paper/main.tex`, que compile, con la estructura del
paper A que decidieron los autores: **la teoría verificada más una medición prerregistrada y auditada de la etapa 1, presentada
como medición acotada con la potencia declarada ex ante.** Ni más ni menos que eso.

## Lo que el paper puede y no puede decir (no negociable)
- H0 no se confirma (`h0_falla`): el efecto lineal no se distingue ni de cero ni del efecto de referencia. **No es evidencia de
  que no haya efecto**; con la potencia escrita ex ante era el resultado más probable.
- **H1 no se interpreta.** Las 6 filas de b_C se muestran todas, con su p unilateral y su IC, como "medición sin veredicto"
  (también las dos que no son significativas). No escribas que los datos "sugieren", "apoyan" o "son coherentes con" la
  amplificación en el estado restringido.
- Las etapas 1b y 2 se cierran como "no pasan la puerta" y aparecen solo como trabajo futuro condicionado a datos.
- Lenguaje calibrado a la identificación: sin verbos causales que el diseño no sostenga.

## Lee primero
- `papers/p01-liquidity/SPEC.md`: la pregunta, la sección "## Prerregistro de la etapa 1 rediseñada" y las Desviaciones desde
  el 2026-11-07 (sobre todo las del 2026-11-08: paper A y cierre de las etapas 1b y 2).
- La teoría: `theory/VERIFICACIONES_2026-11-04.md` y los `check_*.py` (solo entran proposiciones con verificación SymPy).
- Los resultados: `output/F16_RESULTADOS.md` (`## HANDOFF`) y `output/macros.tex` con su tabla macro → fuente en
  `output/F21_MACROS.md`. Las auditorías que lo aprueban: `audits/2026-11-08_F16_estimacion.md`, `audits/2026-11-08_F21_macros.md`
  y su adenda.
- `paper/references.bib`: solo las entradas VERIFICADAS se pueden citar.

## Entregable
`papers/p01-liquidity/paper/main.tex` (y secciones en archivos aparte si lo prefieres) con introducción, modelo y proposiciones,
diseño prerregistrado, resultados (tabla de las estimaciones desde macros, veredicto paso a paso, diagnósticos de los choques),
potencia y qué permite descartar la medición, limitaciones y conclusión. `\input{../output/macros.tex}` para todas las cifras.

## Criterios de aceptación
- `uv run python tools/integrity.py --only citations,numbers` en verde (ninguna cifra tecleada; una que no salga de macros
  lleva `% num-ok <motivo>`).
- `latexmk -pdf` compila; reporta los warnings.
- El MDE se escribe como "≈ 10 pp" o con su macro, no con dos decimales tecleados (F22).

## Condición de parada
Cuando el borrador esté completo y compile. Si una frase necesitaría una cifra o una cita que no existe en `output/` o en el
`.bib` verificado, no la inventes: déjala marcada en el texto como `\todo{…}` y anótala en el HANDOFF. **No toques `code/`,
`data/`, `output/`, `theory/` ni la SPEC** (cualquier cambio ahí haría caducar la aprobación del Referee).

## Cierre
`## HANDOFF` en `papers/p01-liquidity/paper/F23_HANDOFF.md`: hecho, qué secciones, warnings de LaTeX, `\todo` pendientes. Marca
**F23** en `TASKS.md` y añade lecciones a `kb/lessons/writer.md` (créalo si no existe, con `Estado: candidata`). No hagas commit.
