# Encargo de la Coordinación a Literatura — 2026-11-08 · F12: normalización de Tenreyro-Thwaites y Teulings-Zubanov

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Dos comprobaciones de las que dependen decisiones del prerregistro nuevo de p01 (F11):
1. **Cómo normaliza Tenreyro-Thwaites (2016) su respuesta de la inversión de −2,5 %**: ¿por punto de qué (fed funds,
   choque), en qué horizonte (impacto, pico, media, h concreto) y con qué frecuencia (mensual, trimestral)? De eso depende si
   β_ref se mide con la respuesta del fed funds en h = 0 o en h = 1 (la potencia cambia de 0,04–0,10 a 0,14–0,27).
2. **Teulings y Zubanov**: que existe y qué dice sobre el sesgo de las LP por choques posteriores en la ventana y la
   corrección con adelantos del choque como control (la especificación `aum` de F9).

## Lee primero
- `papers/p01-liquidity/audits/2026-11-08_F9_mc.md`, hallazgos 3 y 5 (qué se necesita y por qué).
- `kb/library/INDEX.md`: Tenreyro-Thwaites ya está en la biblioteca (lo citaron F4 y el Director con pp. 2, 9–11 y 16);
  léelo en `kb/library/md/<clave>.md`. Si falta Teulings-Zubanov, descárgalo de una fuente legal y gratuita, añádelo al
  INDEX y conviértelo con `uv run python tools/pdf2md.py` (está permitido; no hace falta pdftotext).

## Entregable
- Entradas en `papers/p01-liquidity/paper/references.bib` (`VERIFICADA` con página, o `DISCREPANCIA:`).
- `papers/p01-liquidity/exploration/F12_CITAS_2026-11-08.md`: para (1), la cita breve y la página que fijan la
  normalización, y qué implica para β_ref (h = 0 o h = 1, o ninguno de los dos); para (2), qué respalda y en qué página.

## Criterios de aceptación
`uv run python tools/integrity.py --only citations` en verde; cada afirmación con su página del texto leído.

## Condición de parada
Cuando las dos preguntas tengan respuesta con página, o cuando hayas comprobado que el texto no lo dice: en ese caso, di
exactamente qué dice y qué queda ambiguo. No hagas el cálculo de β_ref: eso es de Econometría.

## Cierre
Sección `## HANDOFF` al final del informe (hecho, evidencia, ambigüedades, pendiente). Marca **F12** en
`papers/p01-liquidity/TASKS.md` y añade lecciones a `kb/lessons/literature.md` (`Estado: candidata`). No hagas commit.
