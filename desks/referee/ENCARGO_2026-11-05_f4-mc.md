# Encargo de la Coordinación al Referee — 2026-11-05 · R-F4: auditoría del Monte Carlo de F4

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Sigue tu rol (`.claude/agents/referee.md`) y el formato obligatorio de
`.claude/skills/referee-report/SKILL.md`.

## Objeto
El Monte Carlo de F4 sobre la especificación prerregistrada `s1_liq` de p01, tal como está en el **commit 1880c23**
(los archivos de F4 no han cambiado desde `f93dc43`, donde se entregaron):
- informe: `papers/p01-liquidity/output/F4_MC_REPORT.md`;
- tablas: `papers/p01-liquidity/output/tables/f4_power.md` y `mc_s1_liq.txt`;
- código: `papers/p01-liquidity/code/mc/f4_power.py` (+ `test_f4_power.py`), estimador en `code/analysis/s1_lp.py`,
  herramienta `tools/mc.py`;
- lo que obliga: `papers/p01-liquidity/SPEC.md`, sección "Prerregistro de la etapa 1"; el encargo original de F4 en
  `desks/econometria/ENCARGO_2026-11-04_f4-montecarlo.md`.

Sus conclusiones (errores estándar, potencia y veredictos alcanzables) son la base sobre la que los autores van a decidir
si rediseñan la etapa 1. Por eso se auditan antes de esa decisión.

## Regla dura (igual que para Econometría)
**No estimes `s1_lin` ni `s1_liq` con la inversión real, ni mires cómo responde la inversión a los choques.** De
`data/clean/stage1_us.parquet` puedes usar los choques, el estado, los controles y la muestra; la variable dependiente se
simula. Si para auditar algo necesitaras saltarte esta regla, para y anótalo como bloqueo.

## Qué auditar (como mínimo)
1. **Cumplimiento de la regla dura** por parte de F4: qué usa el código de la inversión real y si eso informa de algún
   modo sobre la respuesta a los choques.
2. **DGP:** si reproduce la estructura de `s1_liq` y de la muestra real (choques, estados, desequilibrio entre celdas,
   MA(4) del solape h = 0..4, controles), y qué sesgos introduce cada elección.
3. **β_ref:** la traducción de la fuente a las unidades de ȳ, con la aritmética rehecha. La existencia de la cita es
   cosa de Literatura; aquí se audita la cuenta.
4. **Errores estándar:** la cobertura de NW(5) y la de la alternativa recomendada, y si el diagnóstico de su causa se
   sostiene.
5. **Potencia y veredictos:** si la regla de decisión implementada (Holm unilateral, confirma / refuta (a) / refuta (b) /
   no concluyente) es exactamente la del SPEC, y si las probabilidades de cada veredicto se siguen de ella.
6. **Replicación independiente** en `papers/p01-liquidity/audits/replication_2026-11-05/`, en R si es posible y si no en
   Python sin reutilizar el código del autor. Puedes usar menos réplicas que F4 si lo justificas con el error de
   Monte Carlo.
7. `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`, citados en el informe.

## Entregable
`papers/p01-liquidity/audits/2026-11-05_F4_mc.md`, con veredicto, hallazgos con `Evidencia:` y el resultado de la
replicación. Comprueba el formato con `uv run python tools/integrity.py --only referee`.
Marca la tarea **R-F4** en `papers/p01-liquidity/TASKS.md` (`[~]` al empezar, `[x]` o `[!]` al terminar).
Añade lo que aprendas a `kb/lessons/referee.md` (`Estado: candidata`). No hagas commit.
