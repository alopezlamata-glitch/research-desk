# Encargo de la Coordinación a Econometría — 2026-11-07 · F9: Monte Carlo de la etapa 1 rediseñada de p01

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Lo que obliga: las Desviaciones del 2026-11-07 al final de
`papers/p01-liquidity/SPEC.md` (rediseño y variantes de Volcker). Contexto: `exploration/DECISIONES_AUTORES_2026-11-07.md`,
la propuesta del Director (`exploration/REDESIGN_POWER_2026-11-04.md`, §4) y la auditoría de tu F4
(`audits/2026-11-05_F4_mc.md`). Usa `../../.claude/skills/mc-validate/SKILL.md` y `tools/mc.py` (**`mc.validate`**, no
`mc.run`: la regla de parada de cobertura tiene que poder saltar).

## Regla dura (la misma de F4)
**No estimes nada con la inversión real ni mires cómo responde la inversión (ni otra variable de resultado) a los choques.**
De `data/clean/stage1r_us.parquet` puedes usar los choques, el estado, los controles y la muestra; de la inversión, solo un
AR(2) univariante de su crecimiento **sin choques**, para fijar el ruido, como en F4. La variable dependiente se simula.

## Diseño que se valida (`s1r_*`)
- Choque principal: Romer-Romer (`rr_shock`), muestra 1969Q1–2005Q2 (N = 146). Réplica: `mps_bs23_orth`, 1988Q1–2005Q2.
- Estadístico: media de h = 4..12 del cambio acumulado de la inversión.
- Estado: `D_{t−1}` como en el prerregistro (mediana de `s_{t−1}` en la muestra completa de cada choque).
- H0 lineal (`s1r_lin`); **H1 con subidas y bajadas juntas** (β_C < 0 en el estado restringido); la asimetría es
  exploratoria.

## Qué medir
1. **β_ref con Romer-Romer**, traducido como en F4 pero con la primera etapa del fed funds sobre `rr_shock`, sin usar la
   inversión. Da la sensibilidad a medir la respuesta del fed funds en h = 0 y en h = 1 (R-F4 vio −0,88 frente a −1,20).
2. **Las tres variantes de Volcker** (V1 muestra completa; V2 sin 1979Q4–1982Q4; V3 muestra completa con H1 confirmada solo si
   también se sostiene sin Volcker), y la réplica con BS-orth. Para cada una, con T y con T/2:
   - sesgo;
   - **cobertura del IC al 95 %** con NW(5) con residuos HC3 **y** con NW(5) simple, en dos DGP: ruido homocedástico y
     **ruido heterocedástico ligado a los trimestres de alto apalancamiento** (p. ej., varianza que crece con |ε_t| o mayor en
     recesiones; justifica la elección). Banda [0,92; 0,98]. Si NW(5)+HC3 sale de la banda en el DGP heterocedástico, prueba la
     alternativa más defendible (bootstrap por bloques, wild bootstrap…) y recomiéndala;
   - **curva de potencia** con efectos c·β_ref, c ∈ {1, 2, 3, 5}, y el efecto mínimo detectable con potencia 0,8;
   - **probabilidades de cada veredicto con el árbol de decisión completo, incluida la condición de H0** (H1 solo se
     interpreta si H0 se confirma). Esto es lo que faltó en F4.
3. **Umbral de refutación (b).** Con δ = 0,146·|β̂_U| el umbral es ruido cuando ee(β̂_U) ≫ |β_U| (R-F4). Mide E[δ̂] frente al
   valor verdadero en tu DGP y propón una regla que no dependa de un β̂_U ruidoso (p. ej., fijada con β_ref ex ante),
   evaluada con las mismas tablas. La decisión es de los autores en F11.
4. Comprueba si la pérdida LP frente al oráculo (×1,2–1,4) y la ganancia de la ventana (×1,34) se componen como supone el
   Director (`redesign_power_calc.py`, [T§7]).

## Entregable
`papers/p01-liquidity/code/mc/f9_power.py`, reproducible con semilla, y su test; `papers/p01-liquidity/output/F9_MC_REPORT.md`
con una página de conclusiones: para cada variante de Volcker, potencia, MDE, cobertura en los dos DGP y probabilidades de
veredicto; el error estándar que recomiendas; la regla (b) que propones; y qué variante es más defendible y por qué. Las
cifras salen de tablas generadas en `output/tables/`. `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity`
en verde. Marca **F9** en `TASKS.md`. Lecciones en `kb/lessons/econometrics.md` (`Estado: candidata`). No hagas commit.
