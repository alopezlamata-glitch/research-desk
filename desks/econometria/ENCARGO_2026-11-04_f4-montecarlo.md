# Encargo de la Coordinación a Econometría — 2026-11-04 · F4: Monte Carlo de la especificación prerregistrada

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Lee primero `papers/p01-liquidity/SPEC.md` (sección "Prerregistro de la etapa 1"), que
**obliga**, y `exploration/PREREG_DRAFT.md` §3 ("alternativas de referencia para la potencia"). Usa `../../.claude/skills/mc-validate/SKILL.md` y `tools/mc.py`.

## Regla dura
**No estimes `s1_lin` ni `s1_liq` con la inversión real, ni mires cómo responde la inversión a los choques.** El Monte Carlo puede usar del panel
(`data/clean/stage1_us.parquet`) solo la serie de choques, el estado `D_{t−1}`, los controles y la muestra exacta (N = 102, `SAMPLE_COUNTS.md`).
La variable dependiente se **simula**.

## Qué hacer
1. **DGP:** ȳ simulado con la estructura de `s1_liq`, los choques y estados reales (para conservar el desequilibrio entre celdas y la varianza
   del choque), un error con la autocorrelación MA(4) que induce el solape de h = 0..4 y controles realistas. Documenta cada elección.
2. **β_ref:** tradúcela con una fuente con página (Tenreyro-Thwaites pp. 11–12 es la propuesta del borrador; si usas otra, justifícalo).
   Hazlo **sin** usar la respuesta de la inversión en nuestros datos. Puedes usar la respuesta del rendimiento a 2 años o del fed funds al choque BS
   (no es la variable de resultado).
3. **Escenarios:** β_U = β_ref y β_C ∈ {β_ref, 0,5·β_ref, 0,146·β_ref}, para subidas y bajadas.
4. **Medir** con `tools/mc.py` (T y T/2):
   - el sesgo;
   - la cobertura del IC al 95 % con Newey-West(5) (banda [0,92; 0,98]);
   - la potencia de la regla "confirma" (Holm, unilateral);
   - la probabilidad de cada veredicto (confirma / refuta (a) / refuta (b) / no concluyente).
5. **Si Newey-West(5) sale de la banda:** prueba la alternativa más defendible (p. ej., bootstrap por bloques, o NW con corrección de
   muestra pequeña) y recomiéndala. El cambio lo registran los autores como Desviación **antes** de estimar.
6. **Código:** `papers/p01-liquidity/code/mc/f4_power.py`, reproducible con semilla, y su test.

## Entregable
`papers/p01-liquidity/audits/` **no** (eso es del Referee): escribe `papers/p01-liquidity/output/F4_MC_REPORT.md`, con las tablas y la potencia por
escenario, una conclusión clara (¿tiene sentido estimar? ¿qué veredictos son alcanzables?) y la recomendación de errores estándar.
No hagas commit. Lecciones en `kb/lessons/econometrics.md` (`Estado: candidata`).
