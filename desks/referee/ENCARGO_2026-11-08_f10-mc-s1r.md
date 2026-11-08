# Encargo de la Coordinación al Referee — 2026-11-08 · F10: auditoría del Monte Carlo de F9

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol (`.claude/agents/referee.md`) y el formato de
`.claude/skills/referee-report/SKILL.md`.

## Objetivo
Un veredicto sobre el Monte Carlo de F9 (diseño `s1r_*` de la etapa 1 rediseñada de p01), en el **commit d1a77f5**, antes de
que los autores decidan el prerregistro nuevo (F11). Sus conclusiones (un sesgo nuevo y su corrección, el error estándar, la
potencia con la condición de H0, la variante de Volcker y el umbral (b)) son la base de esa decisión.

## Regla dura (la misma de F4 y F9)
**No estimes `s1r_*` ni ninguna otra especificación con la inversión real, ni mires cómo responde la inversión a los choques.**
De `data/clean/stage1r_us.parquet` puedes usar los choques, el estado, los controles y la muestra; la variable dependiente se
simula. Si para auditar algo necesitaras saltarte esta regla, para y anótalo como bloqueo.

## Lee primero
- `papers/p01-liquidity/output/F9_MC_REPORT.md` (§0, conclusiones) y las tablas que cita (`output/tables/f9_power.md`).
- Lo que obliga: las Desviaciones del 2026-11-07 al final de `papers/p01-liquidity/SPEC.md` (rediseño y variantes V1–V3).
- El código: `code/analysis/s1r_lp.py` (el estimador que usará el análisis real, con el árbol de decisión) y
  `code/mc/f9_power.py` (+ `test_f9_power.py`); `tools/mc.py`.
- Para contexto, solo si lo necesitas: tu auditoría anterior de F4 (`audits/2026-11-05_F4_mc.md`) y el encargo de F9
  (`desks/econometria/ENCARGO_2026-11-07_f9-mc-s1r.md`).

## Qué auditar (como mínimo)
1. Que F9 cumplió la regla dura.
2. **El sesgo de la LP con ventana h = 4..12** (§1a de las tablas): si es real o un artefacto del DGP (la respuesta supuesta
   es una rampa permanente), y si la especificación `aum` (choques de t−10 a t+12 como controles) es una corrección válida
   y no introduce otro problema. Los adelantos del choque como control merecen una justificación explícita.
3. **Error estándar:** NW(5) con residuos HC3 sobre `aum` cubre 0,948–0,990, por encima de la banda en varias celdas. ¿Es
   aceptable esa sobrecobertura o indica otro problema? ¿Hay una alternativa mejor?
4. **Potencia y veredictos:** si el árbol implementado (condición de H0, V1/V2/V3s, reglas (a) y (b)) es exactamente el de
   la SPEC y la Desviación, y si la potencia de 0,04–0,10 frente a β_ref y el MDE ≈ 3,9–5,5·β_ref se siguen de él.
5. **β_ref con Romer-Romer** y su sensibilidad a medir el fed funds en h = 0 o h = 1.
6. **Replicación independiente** en `papers/p01-liquidity/audits/replication_2026-11-08/`, en R (Rscript está en el PATH),
   sin reutilizar el código del autor. Puedes usar menos réplicas que F9 si lo justificas con el error de Monte Carlo.
7. `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`, citados en el informe.

## Entregable
`papers/p01-liquidity/audits/2026-11-08_F9_mc.md`, con veredicto, hallazgos con `Evidencia:` y el resultado de la
replicación.

## Criterios de aceptación
`uv run python tools/integrity.py --only referee` en verde; la replicación en R reproduce los valores deterministas
(β_ref, sesgo sin ruido) y queda dentro del error de Monte Carlo en cobertura y potencia, o explica la diferencia.

## Condición de parada
Cuando hayas cubierto los puntos 1–7. Si una comprobación exigiera estimar con la inversión real, para y anótalo. No rehagas
la curva de potencia completa si la replicación de los escenarios principales ya coincide.

## Cierre
Sección `## HANDOFF` al final del informe: hecho; evidencia (ruta:línea, commit); qué se sostiene y qué no; pendiente de
decidir por los autores en F11. Marca **F10** en `papers/p01-liquidity/TASKS.md` y añade lo que aprendas a
`kb/lessons/referee.md` (`Estado: candidata`). No hagas commit.
