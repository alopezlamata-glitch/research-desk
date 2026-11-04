# Encargo de la Coordinación al Director científico — 2026-11-04 · Borrador del prerregistro de p01 (F3)

Rutas relativas a la raíz del repo (`../../`). Los autores aprobaron el diseño F (`papers/p01-liquidity/SPEC.md`, Desviaciones).

## Material
- `papers/p01-liquidity/exploration/DEVILS_ADVOCATE_2026-11-04.md` (tu informe, §5) y `FIRST_PRINCIPLES.md` (§6.6, con la nota de corrección).
- `papers/p01-liquidity/theory/VERIFICACIONES_2026-11-04.md` y los scripts `theory/check_*.py`: lo que **está** verificado.
- `papers/p01-liquidity/data/clean/DICTIONARY.md` y `coverage.csv`: qué variables existen y desde cuándo. La inversión principal pasará a ser
  el índice de cantidad `A008RA3Q086SBEA` (1947–2026Q3; tarea F2b).
- `papers/_template/SPEC.md` (formato del bloque ```prereg```) y `tools/research.py` (`log_spec`).

## Qué hacer
Escribir `papers/p01-liquidity/exploration/PREREG_DRAFT.md`, una propuesta para los autores. **No edites la SPEC.**
1. **Pregunta** e **identificación** de la etapa 1 (EE. UU.): LP con un solo estado (liquidez o servicio de la deuda), con subida y bajada separadas.
2. **Bloque ```prereg```:** 2–4 especificaciones confirmatorias con `spec_id`, ecuación, horizonte, errores estándar y muestra.
   - Cada hipótesis lleva el **signo esperado** y **la ecuación de un `check_*.py` de la que sale**. Por ejemplo, ω ≥ ω_min ⇒ la transmisión
     con restricción no es cero; el amortiguamiento 1/(1+φΘ); ∂I_u/∂g = 1−ω > 0 solo con restricción activa.
   - Lo que no tenga signo fijo en la teoría, como el efecto de la coordinación sobre la pendiente, va como exploratorio.
3. **Reglas de decisión:** qué resultado confirma, cuál refuta y cuál no es concluyente (con la potencia, que estimará F4).
4. **Exploratorio:** la lista explícita, incluida la interacción triple y la etapa 2.
5. **Vintage de Bauer-Swanson:** recomendación argumentada entre `mps_bs23_orth` y `mps_bs25_*`, con la referencia del paper (BS 2023 en
   `kb/library/md/`). La decisión es de los autores.
6. **Muestra y robustez:** ZLB, 2020, fin de muestra en tiempo real o en revisión, y con qué estado se mide (DSR o liquidez de Z.1).

## Reglas
Ninguna afirmación sobre la literatura sin página. Marca **[criterio propio]**. Lecciones en `kb/lessons/scientific-director.md`
(`Estado: candidata`). No edites nada más.
