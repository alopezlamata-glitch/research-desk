# Encargo de la Coordinación a Econometría — 2026-11-08 · F13: comprobaciones para el prerregistro `s1r_*`

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Cerrar las cifras que el prerregistro nuevo necesita y que F10 y F12 dejaron abiertas, sin rehacer el MC de F9.

## Regla dura (la de F4 y F9)
No estimes nada con la inversión real ni mires cómo responde a los choques. Los choques, el estado y el fed funds sí.

## Lee primero
- La Desviación del 2026-11-08 al final de `papers/p01-liquidity/SPEC.md` (diseño fijado: V3s con `aum`, β_ref en h = 0).
- `papers/p01-liquidity/audits/2026-11-08_F9_mc.md`: hallazgos 3, 4, 5 y 7.
- `papers/p01-liquidity/exploration/F12_CITAS_2026-11-08.md`, punto 1 (Tenreyro-Thwaites promedian el choque por trimestre;
  F7 lo agregó sumando los meses).
- Tu código: `code/mc/f9_power.py` y `code/analysis/s1r_lp.py`.

## Qué hacer
1. **Equivalencia del h = 0.** Comprueba si β_ref y la potencia frente a β_ref cambian al agregar el choque por promedio en vez
   de por suma. Si la normalización por el fed funds los hace invariantes, demuéstralo numéricamente; si no, di cuánto cambian.
2. **MDE simulado en c = 4** para V3s con `aum` (F10 pidió no interpolar entre c = 3 y c = 5), y la fila del rival
   (β_C = 0, β_U = c·β_ref) para V3s con c hasta 5.
3. **Tabla de diagnósticos de los choques** generada por código en `output/tables/`: Ljung-Box(12) y el contraste de
   predictibilidad con PIB, deflactor y fed funds pasados, para Romer-Romer con la muestra completa y sin Volcker (el Referee
   obtuvo p = 0,029 y p = 0,085 sin Volcker).
4. **Corrige `output/F9_MC_REPORT.md:108`**: el MDE invariante es por pp de choque, no por pp de fed funds (F10, hallazgo 5).

## Entregable
Tablas nuevas en `papers/p01-liquidity/output/tables/` generadas por un script en `code/mc/` (con su test) y
`papers/p01-liquidity/output/F13_COMPROBACIONES.md` con una página: respuesta a 1–3 con sus cifras y la ruta de cada tabla.

## Criterios de aceptación
`uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity` en verde; las cifras salen de tablas generadas; el
MC usa la misma semilla y el mismo número de réplicas que F9 en lo que reutilice.

## Condición de parada
Cuando 1–4 estén hechos. Si la equivalencia del punto 1 falla de forma que cambie la potencia de manera material, para,
márcalo `[!]` en `TASKS.md` y explícalo: los autores tienen que saberlo antes de aprobar el prerregistro.

## Cierre
Sección `## HANDOFF` al final de `F13_COMPROBACIONES.md`. Marca **F13** en `TASKS.md` y añade lecciones a
`kb/lessons/econometrics.md` (`Estado: candidata`). No hagas commit.
