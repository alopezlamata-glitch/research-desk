# Encargo de la Coordinación a Redacción — 2026-11-11 · F29: cerrar los `\todo` del borrador y quitar el rodeo de las macros

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`).

## Objetivo
Que `papers/p01-liquidity/paper/main.tex` compile sin errores con el `output/macros.tex` actual y solo le queden los `\todo`
que dependen de una decisión de los autores.

## Lee primero (solo los `## HANDOFF`; abre los originales que citan si los necesitas)
- `papers/p01-liquidity/audits/2026-11-11_F25_macros.md` (F28): por qué `main.tex` no compila hoy y cómo se arregla.
- `papers/p01-liquidity/exploration/F26_CITAS_2026-11-08.md` (F26): claves nuevas de `references.bib`.
- `papers/p01-liquidity/theory/F27_OBSERVACION_2026-11-11.md` (F27): la Observación se sostiene tal como está.
- `papers/p01-liquidity/paper/F23_HANDOFF.md`: lista de los 7 `\todo`.

## Entregable: cambios en `paper/main.tex`
1. **Rodeo de las macros:** borra `main.tex:18-21` y `:23-27` y deja solo `\input{../output/macros.tex}`.
2. **Cobertura de NW5+HC3** (`\todo` de `:284`): usa `\CovAumNwHcLo`–`\CovAumNwHcHi` (rango con T completo, especificación `aum`).
3. **Observación** (`\todo` de `:558`): quita el `\todo`; el enunciado no cambia. Opcional: escribir `a>0` explícito donde se
   introduce la pendiente del coste marginal (`:117-118`).
4. **Citas** (solo entradas VERIFICADAS de `references.bib`):
   - Jeenas (`:100`): cita el documento de trabajo `Jeenas2026`, que es la versión cuyas páginas están comprobadas. No cites
     `JeenasJPE2026`: si se cambia a la versión publicada lo deciden los autores.
   - Procedencia de la serie extendida de Romer-Romer (`:233`): `WielandRomerShocks2021` y `WielandYang2020`, diciendo solo lo
     que F26 verificó (la construye Wieland, cubre hasta 2007).
   - Datos (`:238`): `FRED2026`, `BEA2026NonresInv`, `FedZ12026`. No cites número de tabla NIPA.
   - Newey y West (`:282`): `NeweyWest1987`.
5. **Se quedan como `\todo`** (decisión de los autores, no los resuelvas): lista de autores y afiliaciones (`:31`) y la cita de
   los trabajos previos TFG1/TFG2 (`:109`).

## Criterios de aceptación
- `latexmk -pdf` compila sin errores y `uv run python papers/p01-liquidity/audits/replication_2026-11-11_F28/compile_main.py`
  termina con rc=0. Reporta los warnings.
- `uv run python tools/integrity.py --only citations,numbers` en verde.
- En `main.tex` quedan exactamente 2 `\todo` (los del punto 5), además de la definición del comando.

## Condición de parada
Cuando 1–5 estén hechos y compile. No reescribas secciones ni cambies afirmaciones: es un cierre de pendientes, no una
revisión. No toques `code/`, `data/`, `output/`, `theory/`, `references.bib` ni la SPEC. Si una cita no respalda lo que el
texto afirma, no fuerces la frase: deja el `\todo` con el motivo y dilo en el HANDOFF.

## Cierre
Sección `## HANDOFF F29` al final de `paper/F23_HANDOFF.md`. Marca **F29** en `papers/p01-liquidity/TASKS.md` y añade lecciones
a `kb/lessons/writer.md` (`Estado: candidata`). **No hagas commit:** el texto entra en git junto con el informe del Referee
(F30), que audita el texto y el cambio de `theory/` de F27.
