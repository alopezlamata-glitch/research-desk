# Encargo de la Coordinación al Director científico — 2026-11-08 · F18: qué hacer con p01 tras `h0_falla`

Modelo: opus
Esfuerzo: high

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Una propuesta, para que decidan los autores, de cómo sigue p01 ahora que la etapa 1 prerregistrada ha dado `h0_falla` (la SPEC
dice: "Si no se confirma, H1 no se interpreta y se escala al Director"). Entre 2 y 4 opciones de familias distintas, puntuadas
con la rúbrica de la SPEC, con una recomendación.

## Hechos (auditados; no se discuten)
- F16 (`output/F16_RESULTADOS.md`, commit 1c98c81) y su auditoría F17 (`audits/2026-11-08_F16_estimacion.md`, **APROBADO**,
  réplica independiente al 1e-12): β̂_lin = −1,655, p = 0,178, IC 95 % [−5,19; 1,88], que contiene el 0 y β_ref = −1,820.
  Era el resultado más probable según la potencia escrita ex ante (P(h0_falla) ≈ 0,82–0,85 con β_ref).
- **Las 6 filas de b_C, todas** (`output/tables/s1r_estimates.md`), no solo las favorables: `s1r_liq` p = 0,042; `s1r_liq_nov`
  p = 0,040; `r1r_from1971q3` p = 0,152; `r1r_state_q25` p = 0,024; `r1r_state_logistic` p = 0,020; `r1r_lags4` p = 0,082. Por el
  árbol prerregistrado son **medición sin veredicto**.
- La etapa 1b **no pasa la puerta de datos** con el criterio de los autores (F14a, `exploration/F14A_QFR_2026-11-08.md`: G = 28–32
  frente a 40; proxy de exposición sin cita verificada; sin capex). La Coordinación recomendó no relajarla; los autores no han
  decidido todavía.
- La etapa 2 (zona euro, F5 en `TASKS.md`) sigue sin abrir, con su propia puerta.

## Reglas
- **No reinterpretes H1 ni propongas cambiar la regla de decisión de `s1r_*` después de ver los datos.** Si alguna opción usa
  β̂_C, tiene que ser como análisis nuevo, prerregistrado antes de ver datos nuevos (otra muestra, otro país, otra variable), y
  decirlo.
- No escribas código ni estimes nada; si una opción necesita un cálculo de potencia, pídelo como tarea en `TASKS.md`.

## Lee primero
- `papers/p01-liquidity/SPEC.md`: rúbrica, sección de prerregistro vigente y Desviaciones desde el 2026-11-04.
- Los `## HANDOFF` de F16, F17 y F14a. El resto, solo si lo necesitas.

## Entregable
`papers/p01-liquidity/exploration/F18_TRAS_H0_2026-11-08.md`: qué contribución sigue siendo defendible con lo que hay; las
opciones (p. ej., escribir la etapa 1 como medición acotada con potencia declarada; abrir la etapa 2 con su puerta; replantear
la pregunta; otra que veas), cada una con la rúbrica, el coste en semanas de desks y qué guardarraíl la comprobaría; y tu
recomendación sobre la etapa 1b.

## Criterios de aceptación
Cada afirmación empírica apunta a un archivo de `output/` o `audits/`; las 6 filas de b_C aparecen; ninguna opción reinterpreta
H1 con estos datos.

## Condición de parada
Cuando las opciones estén puntuadas y haya recomendación. Sin búsquedas de literatura nuevas salvo que una opción lo exija; en
ese caso, pídela a Literatura en `TASKS.md`.

## Cierre
`## HANDOFF` al final. Marca **F18** en `TASKS.md` y añade la lección a `kb/lessons/scientific-director.md`
(`Estado: candidata`). No hagas commit.
