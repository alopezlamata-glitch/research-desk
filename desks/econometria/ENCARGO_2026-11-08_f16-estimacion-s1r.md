# Encargo de la Coordinación a Econometría — 2026-11-08 · F16: estimación de `s1r_*` con la inversión real

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). **Los autores dan el visto bueno el 2026-11-08** a estimar con la inversión real
el prerregistro congelado en `prereg_commit: 3d6b508`.

## Objetivo
El resultado de la etapa 1 de p01 tal como está prerregistrado: las estimaciones de `s1r_lin`, `s1r_liq`, `s1r_liq_nov` y los
`r1r_*`, la paridad con R y el veredicto que da el árbol V3s. Sin interpretar más allá de lo que dice el texto congelado.

## Reglas (no negociables)
- **Ejecuta `code/analysis/01_s1r_estimate.py` y `code/replication_r/s1r_replication.R` tal como están en el commit bd4f7bc.**
  No cambies especificaciones, controles, muestra, errores estándar ni la regla de decisión al ver resultados. Si encuentras un
  error de código, no lo arregles en silencio: para, márcalo `[!]` en `TASKS.md` con la evidencia y deja que decidan los autores.
- Toda estimación que no esté en el bloque ```prereg``` es exploratoria: se registra con `log_spec(..., exploratory=True)`, va en
  un script `xx_exploratory_*.py` aparte y se presenta como tal. Ninguna puede cambiar el veredicto.
- Los diagnósticos de los choques se reportan, y su consecuencia es la que fija la SPEC (no cambian la especificación ni el
  veredicto; solo matizan la comparación con β_ref).

## Lee primero
- `papers/p01-liquidity/SPEC.md`, sección "## Prerregistro de la etapa 1 rediseñada" y la Desviación del 2026-11-08.
- `papers/p01-liquidity/output/F15_REQUISITOS.md` (`## HANDOFF`).

## Entregable
- `output/estimates_py.csv` y `output/estimates_r.csv` (paridad), `output/estimates_py_robustness.csv`, `output/spec_log.csv` y
  las tablas que genere el script en `output/tables/`.
- `papers/p01-liquidity/output/F16_RESULTADOS.md`: la tabla de estimaciones con sus IC; el veredicto de H0 y de H1 según el árbol,
  paso a paso, con la cifra que decide cada paso; los diagnósticos de los choques y su consecuencia; la robustez; y una frase que
  sitúe el resultado frente a la potencia escrita ex ante (medición acotada).

## Criterios de aceptación
`uv run python tools/integrity.py` en verde (incluidos `parity` y `speclog`); `uv run pytest papers/p01-liquidity` en verde;
cada cifra del informe sale de un archivo de `output/`.

## Condición de parada
Cuando el entregable esté completo. Si la paridad Python–R falla con los datos reales o el script no corre, para y documéntalo
en `TASKS.md` (`[!]`); no ajustes nada para que cuadre.

## Cierre
`## HANDOFF` al final de `F16_RESULTADOS.md`. Marca **F16** en `TASKS.md` y añade lecciones a `kb/lessons/econometrics.md`
(`Estado: candidata`). No hagas commit: lo hace la Coordinación, y después audita el Referee (F17).
