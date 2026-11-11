# Encargo de la Coordinación al Referee — 2026-11-11 · F32: relectura corta del texto tras los cambios de F30

Modelo: opus
Esfuerzo: medium

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol y el formato de `.claude/skills/referee-report/SKILL.md`.
Sesión nueva: no leas el razonamiento de Redacción (su HANDOFF), solo el texto y los objetos que cita.

## Objetivo
Un veredicto sobre los **cambios** que Redacción ha hecho en `papers/p01-liquidity/paper/main.tex` (árbol de trabajo, sin
commitear) para aplicar el informe `papers/p01-liquidity/audits/2026-11-11_F30_texto.md` (APROBADO CON CAMBIOS sobre 3a1242f),
más dos decisiones de los autores. No es una auditoría nueva del paper: lo que no cambió ya está auditado en F30.

El `commit` de la cabecera es **HEAD** (`git rev-parse --short HEAD`): desde 3a1242f no ha cambiado nada de `code/`, `data/`,
`output/`, `theory/` ni la SPEC.

## Lee primero
- `papers/p01-liquidity/audits/2026-11-11_F30_texto.md`: hallazgos 1, 2 y 4–8.
- `git diff HEAD -- papers/p01-liquidity/paper/main.tex`: los cambios que auditas. Abre el resto de `main.tex` solo para el contexto
  de cada cambio.

## Qué auditar
1. **Los dos mayores de F30:** que el hallazgo 1 (alcance del diseño en la introducción) y el 2 (procedencia de la serie extendida de
   Romer-Romer) están resueltos sin introducir afirmaciones nuevas sin respaldo.
2. **La §2, que ya no es solo redacción:** el objetivo de la empresa con penalización cuadrática del déficit, `a>0`, qué `a` es (la de
   la empresa representativa) y `L=\sum_j s_j I_j`. Comprueba con tu réplica de F30
   (`audits/replication_2026-11-11_F30/check_remark.py`) que de ese objetivo salen las condiciones de óptimo escritas, y que ninguna
   proposición ni enunciado cambió.
3. **La frase nueva sobre H1:** «its aggregate counterpart is Proposition (iii), which holds whatever the mass of constrained types».
   ¿La sostiene la Prop. 3(iii) y su test (`theory/check_aggregation.py:116-123`)? Si no, la corrección mínima.
4. **El MDE con macros** (`\MdeHetC{}` a `\MdeHomoC{}`, en 4 sitios): que el orden y la descripción son correctos.
5. **El apéndice:** el test de la Observación añadido y las frases sobre la verificación, frente a lo que hacen los tests.
6. **Decisiones de los autores (2026-11-11), no son hallazgos:** TFG1/TFG2 son borradores propios y no se citan (se quitó el `\todo`);
   Jeenas se cita en su versión publicada (`JeenasJPE2026`) mencionando el documento de trabajo. Comprueba solo que la frase de Jeenas
   no afirma nada que la nota de su entrada en `references.bib` no respalde.
7. **Guardarraíles:** `audits/replication_2026-11-11_F30/compile_full.py`, `uv run python tools/integrity.py` (la única violación
   esperada es `[gate]`) y `uv run pytest papers/p01-liquidity`. En `main.tex` solo debe quedar el `\todo` de la lista de autores.

## Entregable
`papers/p01-liquidity/audits/2026-11-11_F32_relectura.md`, con veredicto y cada hallazgo con `Evidencia:` (`main.tex:<línea>`).

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde.

## Condición de parada
Cuando hayas cubierto 1–7. Auditoría corta: no rehagas F30 ni toques nada fuera de `audits/`.

## Cierre
`## HANDOFF` al final. Añade una línea **F32** a `papers/p01-liquidity/TASKS.md`, marcada, y lecciones a `kb/lessons/referee.md`
(`Estado: candidata`) solo si hay patrones nuevos. No hagas commit.
