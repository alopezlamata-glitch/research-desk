# Encargo de la Coordinación a Datos — 2026-11-08 · F14a: datos para la puerta de la etapa 1b (QFR)

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Decidir con datos si la etapa 1b (panel del QFR del Census, gradiente de exposición ∂I_u/∂g = 1 − ω > 0) puede pasar la puerta
que fijaron los autores: **G ≥ 40 grupos** y una medida de exposición a tipo variable por grupo. La parte de Monte Carlo
(potencia ≥ 0,8) es F14b, de Econometría, y empieza con tu entrega.

## Regla dura
No estimes nada con la inversión (ni del QFR ni agregada) ni mires cómo responde a los choques. Solo disponibilidad,
recuentos, construcción de variables y tabulaciones descriptivas que no usen la respuesta a choques.

## Lee primero
- `papers/p01-liquidity/exploration/F7_DATOS_2026-11-07.md` (tu informe del QFR: G ≈ 50–65 sin verificar, sin tipo variable,
  proxy propuesto: cuota de deuda bancaria; `qfr10q1f.xls` descargado pero sin abrir porque faltaba `xlrd`).
- La Desviación del 2026-11-07 (decisión 6) al final de `papers/p01-liquidity/SPEC.md` y `datalake/fetch/qfr.py`.
- `papers/p01-liquidity/exploration/F12_CITAS_2026-11-08.md` y `F8_CITAS_2026-11-07.md` (Kirti 2017 sobre el tamaño como proxy).

## Entregable
`papers/p01-liquidity/exploration/F14A_QFR_2026-11-08.md` con:
1. **G verificado:** número exacto de celdas industria × tamaño sin solape, con datos continuos desde 2006Q3, y las que se
   pierden por huecos o reclasificaciones (tabla generada por código desde `raw/`, con su fila en el MANIFEST).
2. **Variables por grupo:** inversión (o su mejor proxy en el QFR), deuda bancaria, deuda total, activos, y la serie de la
   cuota de deuda bancaria; diccionario en `data/clean/`.
3. **El proxy de exposición:** qué respalda que la cuota de deuda bancaria aproxime la exposición a tipo variable (cita con
   página: Kirti u otra que verifique Literatura; si no hay, dilo), y su variación entre grupos y en el tiempo.
4. Veredicto de la parte de datos: pasa / no pasa la puerta de G y de la medida, y por qué.

Si hace falta `xlrd` para leer el `.xls`, no lo instales tú: dilo en el HANDOFF y usa otra vía si la hay (p. ej., el CSV del
Census o `pandas` con otro motor ya instalado).

## Criterios de aceptación
`uv run python tools/integrity.py` (incluido `rawhash`) y `uv run pytest papers/p01-liquidity` en verde; G sale de una tabla
generada, no de un recuento a mano.

## Condición de parada
Cuando 1–4 tengan respuesta, o en cuanto quede claro que G < 40 o que no hay medida de exposición defendible: en ese caso,
para y dilo, porque la etapa 1b no pasaría la puerta y el MC no haría falta.

## Cierre
`## HANDOFF` al final del informe. Marca **F14a** en `TASKS.md`, actualiza `kb/data_catalog.md` y añade lecciones a
`kb/lessons/data.md` (`Estado: candidata`). No hagas commit.
