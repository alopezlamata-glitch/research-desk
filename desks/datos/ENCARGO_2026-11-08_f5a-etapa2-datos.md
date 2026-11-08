# Encargo de la Coordinación a Datos — 2026-11-08 · F5a: datos de la puerta de la etapa 2 (zona euro)

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Decidir con datos si la etapa 2 de p01 (panel de la zona euro) puede pasar la parte de datos de su puerta, tal como la aprobaron
los autores el 2026-11-04 (`papers/p01-liquidity/SPEC.md`, Desviación de esa fecha, punto 2): **datos por país en el MANIFEST**
y una **exposición contractual × stock** por país, con una muestra **sin ZLB** que deje **10–12 clústeres**. El MC de potencia
(≥ 0,8) es F5b, de Econometría, y solo se hace si esta parte pasa.

## Regla dura
No estimes nada con la inversión ni mires cómo responde a los choques. Solo disponibilidad, cobertura, construcción de variables
y recuentos.

## Lee primero
- La Desviación del 2026-11-04 (diseño F, etapa 2) y la del 2026-11-08 (se abre solo la puerta) en la SPEC.
- `papers/p01-liquidity/exploration/F18_TRAS_H0_2026-11-08.md`, opción C, y `kb/data_catalog.md` (entradas de la zona euro, hoy
  "sin probar").
- `datalake/raw/shocks/jarocinski_karadi/ecb_202310/` (choques de política y de información del BCE, ya en el lago).

## Entregable
`papers/p01-liquidity/exploration/F5A_ETAPA2_2026-11-08.md` con:
1. **Inversión trimestral por país** (Eurostat u otra fuente oficial gratuita): países, años y huecos.
2. **Exposición contractual:** cuota de préstamos a tipo variable o de fijación inicial corta por país (MIR del BCE), y el stock
   (saldos vivos) para construir exposición × stock; cobertura por país y año.
3. **Muestra sin ZLB:** qué trimestres quedan (p. ej., 1999–2008 y 2022–23) y cuántos países con datos completos en ellos:
   ese es el número de clústeres.
4. **Choques:** cobertura de los de Jarociński-Karadi (política e información) en esa muestra.
5. Veredicto de la parte de datos: pasa / no pasa, y por qué.

Las series nuevas entran por scripts `datalake/fetch/` con su fila en el MANIFEST (el check `rawhash` lo exige) y se añaden a
`kb/data_catalog.md`. Los recuentos salen de tablas generadas por código.

## Criterios de aceptación
`uv run python tools/integrity.py` (incluido `rawhash`) y `uv run pytest papers/p01-liquidity` en verde; los clústeres y la
cobertura salen de tablas generadas, no de recuentos a mano.

## Condición de parada
Cuando 1–5 tengan respuesta, o en cuanto quede claro que no hay 10 países con inversión y exposición en una muestra sin ZLB:
en ese caso, para y dilo, porque la etapa 2 no pasaría la puerta.

## Cierre
`## HANDOFF` al final del informe. Marca **F5a** en `TASKS.md` y añade lecciones a `kb/lessons/data.md` (`Estado: candidata`).
No hagas commit.
