# Encargo de la Coordinación a Literatura — 2026-11-08 · F26: citas pendientes del borrador del paper A

Modelo: sonnet
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). Usa `../../.claude/skills/verify-citation/SKILL.md` para cada entrada; para leer
PDF, `uv run python tools/pdf2md.py` (está permitido).

## Objetivo
Resolver los `\todo` de citas del borrador (`papers/p01-liquidity/paper/F23_HANDOFF.md`, `\todo` 2–6) dejando cada entrada de
`paper/references.bib` VERIFICADA con su fuente, o en DISCREPANCIA con el motivo.

## Qué verificar
1. **Jeenas** (`main.tex:100`): la entrada `Jeenas2026` está en DISCREPANCIA porque el borrador previo la citaba como JPE. Deja
   una entrada verificada de la versión que existe (BSE WP 1409 / UPF 1872) y comprueba si ya hay versión publicada.
2. **TFG1 y TFG2** (`main.tex:109`), la base del modelo. Son trabajos previos de los autores: busca los documentos en
   `papers/p01-liquidity/prior/` (no en `prior/archive/`, que tiene claves antiguas). Si no hay forma de citarlos de manera
   verificable (repositorio, DOI o web), dilo: lo decidirán los autores.
3. **Procedencia de la extensión de Romer-Romer** (`main.tex:233`): la hoja `Wieland` del Handbook de Ramey (openICPSR 135741,
   que dio 403). Busca otra vía pública para verificar qué es y quién la construyó.
4. **Datos** (`main.tex:238`): citas formales verificadas de FRED, BEA (índice de cantidad de la inversión no residencial) y las
   Cuentas Financieras Z.1 de la Fed (`FRED2026` y `BEA2021` existen sin verificar).
5. **Newey y West (1987)** (`main.tex:282`).

## Entregable
Las entradas en `paper/references.bib` y `papers/p01-liquidity/exploration/F26_CITAS_2026-11-08.md` con, para cada cita, qué
respalda, la fuente y la página o el enlace.

## Criterios de aceptación
`uv run python tools/integrity.py --only citations` en verde.

## Condición de parada
Cuando los cinco puntos tengan respuesta, verificada o explicada. No edites `main.tex` (lo hará Redacción) ni nada de `code/`,
`data/`, `output/` o la SPEC.

## Cierre
`## HANDOFF` al final del informe. Marca **F26** en `TASKS.md` y añade lecciones a `kb/lessons/literature.md`
(`Estado: candidata`). No hagas commit.
