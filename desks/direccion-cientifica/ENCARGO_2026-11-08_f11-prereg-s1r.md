# Encargo de la Coordinación al Director científico — 2026-11-08 · F11: borrador del prerregistro `s1r_*`

Modelo: opus
Esfuerzo: high

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
El texto exacto, listo para que lo aprueben los autores, de la nueva sección de prerregistro de la etapa 1 de p01 y su
bloque ```prereg```. Las decisiones ya están tomadas: no las reabras; tu trabajo es escribirlas sin ambigüedad.

## Lee primero
- Lo que obliga: las Desviaciones del 2026-11-07 y del 2026-11-08 al final de `papers/p01-liquidity/SPEC.md` (esta última fija
  las 7 decisiones) y la sección actual "## Prerregistro de la etapa 1", que la nueva sustituye.
- `papers/p01-liquidity/exploration/DECISIONES_AUTORES_F11_2026-11-08.md` (resumen y porqués).
- `papers/p01-liquidity/audits/2026-11-08_F9_mc.md`, `## HANDOFF` (qué exige el Referee que diga el prerregistro). Abre
  `output/F9_MC_REPORT.md` y `output/tables/f9_power.md` solo para las cifras que cites.
- `papers/p01-liquidity/exploration/F12_CITAS_2026-11-08.md` (normalización de Tenreyro-Thwaites y límites de
  Teulings-Zubanov).

## Entregable
`papers/p01-liquidity/exploration/PREREG_S1R_DRAFT.md` con:
1. **La sección completa** que sustituirá a "## Prerregistro de la etapa 1" en la SPEC: pregunta; muestra (1969Q1–2005Q2,
   choque Romer-Romer y réplica BS-orth); estado `D_{t−1}`; especificación `aum` exacta (variables, retardos, adelantos,
   controles, ventana h = 4..12); estimando "respuesta a un choque aislado" y su supuesto, con los diagnósticos (Ljung-Box y
   predictibilidad) y qué se hace si fallan; errores estándar NW(5)+HC3 con la excepción a la banda; **hipótesis H0 y H1 con su
   regla de decisión completa** (puerta H0, V3s definida exactamente, refutación solo por (a)); β_ref en h = 0 con su fuente y
   página; potencia y MDE escritos ex ante (en c·β_ref y en pp de ȳ por pp de choque); robustez prerregistrada; qué queda
   exploratorio (asimetría, V1/V2, `aumi`, h = 1).
2. **El bloque ```prereg```** con los ids nuevos (`s1r_lin`, `s1r_liq` y los de robustez que justifiques). Los ids `s1_*` de
   la etapa 1 anterior salen del bloque: no se estimarán (Desviación del 2026-11-07).
3. Una lista de las cifras que dependen de F13 (Econometría está comprobando el h = 0 frente a la agregación del choque, el MDE
   simulado en c = 4 y la tabla de diagnósticos): márcalas `[F13]` en el texto y no las inventes.

## Criterios de aceptación
Cada número del borrador apunta a una tabla generada (`output/tables/…`) o queda marcado `[F13]`; cada cita tiene página
(o `[pendiente de Literatura]`); las 7 decisiones de la Desviación del 2026-11-08 aparecen tal cual, sin cambiarlas.

## Condición de parada
Cuando el borrador cubra los puntos 1–3. Si alguna decisión es inaplicable o contradictoria al escribirla, no la cambies:
anótala en el `## HANDOFF` como pregunta para los autores. **No edites la SPEC** (eso lo hace la Coordinación tras la
aprobación) ni `TASKS.md` salvo para marcar F11.

## Cierre
Sección `## HANDOFF` al final del borrador: hecho; evidencia; preguntas abiertas para los autores; dependencias de F13.
Lección en `kb/lessons/scientific-director.md` (`Estado: candidata`). No hagas commit.
