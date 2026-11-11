# Encargo de la Coordinación a Teoría — 2026-11-11 · F27: test SymPy de la Observación tras el Corolario 1

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). Sigue `../../.claude/skills/sympy-check/SKILL.md` (tres capas, con test negativo).

## Objetivo
Decidir si la Observación de `papers/p01-liquidity/paper/main.tex:166-169` se queda en el paper: o tiene un test SymPy propio
que la demuestra, o propones quitarla (o debilitarla) con el motivo.

La Observación dice: con `g ≥ 0`, las ecuaciones `eq:Iu` (`main.tex:135`) y `eq:wmin` (`main.tex:154`) dan
`I_u ≥ ω p_f/a > ω_min p_f/a > 0`, es decir, en un óptimo interior una empresa restringida siempre transmite una fracción
positiva de la respuesta sin restricción.

## Lee primero
- `papers/p01-liquidity/paper/main.tex:112-170` (Prop. 1–3, Corolario 1 y la Observación).
- `papers/p01-liquidity/theory/check_nesting.py`: ya verifica las dos piezas por separado
  (`test_weighted_form`, `test_weight_is_bounded_below_by_w_min`, `test_minimum_transmission_with_g0_at_tfg2_calibration`).
  No leas enteros los demás `check_*.py`.

## Entregable
1. Un test nuevo en `papers/p01-liquidity/theory/check_nesting.py` que demuestre la cadena completa de la Observación bajo
   los supuestos que el paper declara (capa simbólica, capa numérica en una rejilla y test negativo: un caso que deba fallar,
   p. ej. `g < 0`, y falle). Comprueba en particular la primera desigualdad (`I_u ≥ ω p_f/a` con `g ≥ 0`) y si las
   desigualdades son estrictas o débiles en los bordes (`g = 0`, `B → 0`).
2. Si la Observación no se sostiene tal como está escrita, **no la arregles tú en `main.tex`**: escribe el enunciado correcto
   (o la propuesta de quitarla) para que Redacción lo aplique en F29.
3. Nota breve en `papers/p01-liquidity/theory/F27_OBSERVACION_2026-11-11.md`: veredicto (se sostiene / se sostiene con este
   enunciado / quitarla), supuestos usados y el nombre del test.

## Criterios de aceptación
`uv run pytest papers/p01-liquidity/theory -q` en verde, con el test nuevo; `uv run ruff check papers/p01-liquidity/theory` limpio.

## Condición de parada
Cuando haya veredicto con su test. No toques `paper/`, `code/`, `output/` ni la SPEC. Si para demostrarla hiciera falta un
supuesto que el paper no declara, no lo añadas en silencio: dilo en la nota y para.

## Cierre
`## HANDOFF` al final de la nota. Marca **F27** en `papers/p01-liquidity/TASKS.md` y añade lecciones a
`kb/lessons/theory.md` (`Estado: candidata`). No hagas commit.
