# Encargo de la Coordinación a Redacción — 2026-11-11 · F31: aplicar al texto los cambios del Referee (F30)

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Que `papers/p01-liquidity/paper/main.tex` (con los cambios de F29, aún sin commitear) recoja las correcciones del informe
`papers/p01-liquidity/audits/2026-11-11_F30_texto.md` (APROBADO CON CAMBIOS), para poder commitearlo con ese informe.

## Lee primero
- `papers/p01-liquidity/audits/2026-11-11_F30_texto.md`: hallazgos 1, 2 y 4–8, y su `## HANDOFF`. Cada hallazgo trae la corrección
  mínima y la línea de `main.tex`. Abre las notas de `references.bib` que cita solo si las necesitas.

## Entregable: cambios en `paper/main.tex`
**Obligatorios (mayores):**
1. Hallazgo 1 (`main.tex:82-83`): acotar la frase de la introducción a **este diseño prerregistrado**, con la corrección que propone el
   informe o una equivalente. Revisa que ninguna otra frase del abstract o de la conclusión diga lo mismo sin acotar.
2. Hallazgo 2 (`main.tex:221-224`): reescribir la procedencia de la serie extendida de Romer-Romer con la **opción (a)** del informe:
   sin afirmar que la serie de los ficheros de Ramey sea la de Wieland, y sin citar `WielandYang2020` como fuente de quién la
   construyó.

**Recomendados (menores), solo texto:**
3. Hallazgo 4: «five to five and a half times» donde el texto dice «about five times» el efecto de referencia; «the linear point
   estimate is negative»; «unusually low relative to their recent trend».
4. Hallazgo 5: nota a la tabla 2 que diga que la estandarización de `s` y la mediana de la muestra completa en `r1r_from1971q3` son
   decisiones de implementación fijadas antes de estimar.
5. Hallazgo 6: escribir el objetivo con la penalización cuadrática del déficit del que salen las condiciones de óptimo
   (`main.tex:106-117`), tal como lo da el informe, y declarar `a>0`. No cambies ninguna proposición ni su enunciado.
6. Hallazgo 7: decir en §2.1 que la `a` es la de la empresa representativa (o la notación equivalente que propone el informe), que
   `L` es la suma ponderada de la inversión de los tipos, y citar en el paso a H1 la Prop. 3(iii) junto con la Observación.
7. Hallazgo 8: añadir al apéndice el test de la Observación (`test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0`) y ajustar las dos
   frases sobre la verificación («each positive test has a negative counterpart»; «all results are verified symbolically») a lo que
   hacen los tests, con la redacción que propone el informe.

**No toques:** la cita de Jeenas (hallazgo 9), la lista de autores ni los trabajos previos TFG1/TFG2: los deciden los autores.

## Criterios de aceptación
- `uv run python papers/p01-liquidity/audits/replication_2026-11-11_F30/compile_full.py` termina sin errores, sin citas ni
  referencias indefinidas.
- `uv run python tools/integrity.py --only citations,numbers` en verde (una cifra nueva no generada lleva `% num-ok <motivo>`;
  «five to five and a half» es descripción de las macros del MDE: si puedes, usa las macros en vez de palabras).
- En `main.tex` siguen exactamente los 2 `\todo` de los autores.

## Condición de parada
Cuando 1–7 estén hechos y compile. Si una corrección exigiera cambiar una proposición, una cifra o algo de `code/`, `output/`,
`theory/`, `references.bib` o la SPEC, no lo hagas: anótalo en el HANDOFF y sigue con lo demás.

## Cierre
Sección `## HANDOFF F31` al final de `paper/F23_HANDOFF.md`, con una línea por hallazgo: aplicado (`main.tex:<línea>`) o no y por
qué. Marca **F31** en `papers/p01-liquidity/TASKS.md` y añade lecciones a `kb/lessons/writer.md` (`Estado: candidata`). No hagas
commit.
