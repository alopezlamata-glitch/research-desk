# Encargo de la Coordinación a Econometría — 2026-11-08 · F25: macros con nombres válidos en LaTeX

Modelo: sonnet
Esfuerzo: low

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Que `output/macros.tex` compile sin rodeos: hoy cuatro macros llevan el dígito 0 en el nombre (`\PwHomoH0Falla`,
`\PwHetH0Falla`, `\PwHomoPowH0`, `\PwHetPowH0`) y LaTeX no las acepta (`paper/main.tex:18-27` las lee con un rodeo provisional).

## Lee primero
- `papers/p01-liquidity/paper/F23_HANDOFF.md`, puntos sobre las macros y el `\todo` 6.
- `code/analysis/02_paper_macros.py`, su test y `output/F21_MACROS.md`.

## Entregable
1. Renombrar en `02_paper_macros.py` esas cuatro macros a nombres solo con letras (p. ej., `\PwHomoHzeroFalla`, que es como las
   llama ya `main.tex`), regenerar `output/macros.tex` y actualizar `F21_MACROS.md`.
2. Un test que falle si algún nombre de macro de `macros.tex` no es un control word válido de LaTeX (solo letras).
3. `\todo` 6 de F23: si el rango de cobertura de NW5+HC3 sobre `aum` (0,948–0,990) está en una tabla auditada (F9 o F13), añade
   sus macros; si no está, no lo calcules: dilo.
4. No cambies ningún valor: solo nombres y, en su caso, las macros nuevas del punto 3.

## Criterios de aceptación
`uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity` en verde; los valores de todas las macros que ya
existían son idénticos a los de 67bc9c2.

## Condición de parada
Cuando 1–4 estén hechos. No toques `paper/` (Redacción quitará el rodeo de `main.tex` después).

## Cierre
`## HANDOFF` al final de `output/F21_MACROS.md` (sección nueva, F25). Marca **F25** en `TASKS.md`. No hagas commit: después el
Referee comprobará el cambio, porque toca `code/` y `output/`.
