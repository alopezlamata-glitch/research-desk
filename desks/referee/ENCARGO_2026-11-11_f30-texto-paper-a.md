# Encargo de la Coordinación al Referee — 2026-11-11 · F30: auditoría del texto del paper A y del test de F27

Modelo: opus
Esfuerzo: high

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol y el formato de `.claude/skills/referee-report/SKILL.md`.
Sesión nueva: no leas el razonamiento de Redacción ni de Teoría (sus HANDOFF), solo el texto, el código y los outputs.

## Objetivo
Un veredicto sobre dos objetos:
1. **El texto** `papers/p01-liquidity/paper/main.tex` tal como está en el árbol de trabajo (sin commitear; lleva los cambios
   de F29 sobre el borrador de F23). Es la primera auditoría del texto.
2. **El cambio de `theory/` de F27** (commit **3a1242f**, que es HEAD): el test
   `test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0` de `papers/p01-liquidity/theory/check_nesting.py`.

El `commit` de la cabecera del informe es **3a1242f** (`git rev-parse --short HEAD`): contiene toda la ciencia auditada. El
texto se commiteará junto con tu informe.

## Lee primero
- `papers/p01-liquidity/paper/main.tex` entero (12 pp.).
- `papers/p01-liquidity/SPEC.md`: el prerregistro vigente (`## Prerregistro de la etapa 1 rediseñada`) y `## Desviaciones`.
- `papers/p01-liquidity/output/macros.tex` y los informes aprobados `audits/2026-11-08_F16_estimacion.md`,
  `audits/2026-11-08_F9_mc.md` y `audits/2026-11-11_F25_macros.md` (sus resúmenes y hallazgos; no rehagas esas auditorías).

## Qué auditar
1. **Lenguaje frente a identificación.** Que el texto no afirme más de lo que el diseño identifica. En particular, que
   **no lee `b_C` como un contraste** de la hipótesis ni presenta como evidencia a favor un resultado sin potencia; que las
   potencias y los MDE citados son los de las macros y están descritos correctamente (ex ante frente a ex post).
2. **Fidelidad al prerregistro.** Que cada especificación, regla de decisión y resultado del texto coincide con la SPEC y con
   sus Desviaciones; que lo exploratorio va etiquetado como tal; que las etapas cerradas (etapa 2) se cuentan como lo que son.
3. **Cifras.** Que cada macro se usa en una frase que describe lo que la macro mide (muestra, estimador de varianza, horizonte,
   T completo o T/2). Caso concreto: la frase de la cobertura de NW5+HC3 habla de «the coefficients that decide» y las macros
   `\CovAumNwHcLo/Hi` se calculan sobre todos los términos (hallazgo menor de F28): comprueba si la frase es exacta.
4. **Teoría.** Que las proposiciones, el corolario y la Observación del texto coinciden con lo que verifican los
   `theory/check_*.py`, supuestos incluidos (p. ej., si `a > 0` está declarado). Audita el test nuevo de F27: que demuestra lo
   que dice, que el test negativo puede fallar de verdad y que no hay circularidad.
5. **Citas.** Que cada cita respalda la frase en la que aparece, según la nota de su entrada en `paper/references.bib`. Atiende
   a las que solo están verificadas en metadatos (`WielandYang2020`) y a la frase sobre la procedencia de la serie extendida de
   Romer-Romer (no está verificado que la serie de los ficheros de Ramey sea exactamente la de Wieland).
6. **Compilación y guardarraíles.** `uv run python papers/p01-liquidity/audits/replication_2026-11-11_F28/compile_main.py`,
   `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`. La violación `[gate]` de `integrity.py` es la
   esperada hasta que tu informe entre en git; cualquier otra es un hallazgo.

Quedan a propósito dos `\todo` que deciden los autores (lista de autores, `main.tex:22`; cita de TFG1/TFG2, `main.tex:99`): no
son hallazgos, pero di si alguna afirmación del texto depende de ellos.

## Entregable
`papers/p01-liquidity/audits/2026-11-11_F30_texto.md`, con veredicto y cada hallazgo con `Evidencia:` (`main.tex:<línea>`).
Para cada problema mayor, la corrección mínima que lo resolvería, sin editar tú el texto.

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde.

## Condición de parada
Cuando hayas cubierto 1–6. No rehagas estimaciones ni el Monte Carlo: audita el texto contra lo ya auditado. Si encuentras un
error en un resultado ya aprobado, anótalo como hallazgo mayor y para ahí: no lo persigas en esta sesión.

## Cierre
`## HANDOFF` al final. Marca **F30** en `papers/p01-liquidity/TASKS.md` y añade lecciones a `kb/lessons/referee.md`
(`Estado: candidata`). No hagas commit.
