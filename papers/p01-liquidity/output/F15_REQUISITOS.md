# F15 · Requisitos previos a estimar `s1r_*` (Econometría, 2026-11-08)

Encargo: `desks/econometria/ENCARGO_2026-11-08_f15-requisitos-s1r.md`. Cumple el «Requisito previo a estimar» de `SPEC.md:220-221`.
**No se ha estimado nada con la inversión real**: el script de análisis y la réplica en R no se han ejecutado sobre los datos reales;
los tests sustituyen la inversión por la simulada del DGP de F9. `output/` no contiene `estimates_*.csv` ni `spec_log.csv`.

## Qué hay
1. **`code/analysis/s1r_lp.py`, alineado con el texto congelado.**
   - `h1_verdict` (`s1r_lp.py:64`) solo devuelve `confirma`, `refuta_a` o `no_concluyente`: sin la regla (b) (`SPEC.md:158-160`).
   - El árbol `decide("V3s")` (`s1r_lp.py:75`) ya era el de `SPEC.md:148-157`, y no cambia:
     - H0 y la refutación (a) se evalúan solo con la muestra completa.
     - Sin Volcker solo cuenta si confirma. Si la completa confirma y sin Volcker β̂_C > 0 es significativo, el veredicto es `no_concluyente`.
     - El docstring lo dice ahora explícitamente.
   - `design` acepta `ctrl_lags` (para `r1r_lags4`) y un D continuo. La constante `AUM = (10, 12)` fija los retardos y adelantos del choque.
   - Los controles son los aprobados (`SPEC.md:91`).
   - La regla (b) que estudió F9 pasa a `f9_power.h1_verdict_b` (`code/mc/f9_power.py:232`), con la misma lógica de antes, para
     que F9 y F13 sigan reproduciendo sus tablas.
   - `DGP.level` (`f9_power.py:146`) es una extracción sin cambio de comportamiento: misma secuencia de `rng`.
2. **`code/analysis/01_s1r_estimate.py`.**
   - Los 7 ids del bloque están en `SPECS` (`:49`), todos con `aum` y NW5+HC3.
   - `main` (`:156`) registra cada id con `research.log_spec` y escribe:
     - `output/estimates_py.csv` (los `s1r_*`, todos los coeficientes, columnas `spec_id, term, estimate, std_error, dof`);
     - `output/estimates_py_robustness.csv` (los `r1r_*`);
     - `output/tables/s1r_estimates.md` (términos que deciden, p, IC y veredicto V3s);
     - `output/tables/s1r_shock_diagnostics.md` (D1, D2, D3, Ljung-Box(12), predictibilidad; sin la inversión).
   - **No se ha ejecutado.**
3. **`code/replication_r/s1r_replication.R`.** Replica `s1r_lin`, `s1r_liq` y `s1r_liq_nov`.
   - Construye por su cuenta el panel (parquet + CSV de FRED), ȳ, el estado y los regresores.
   - Coeficientes con `fixest::feols`; NW(5) en trimestres naturales con residuos HC3, escrito a mano.
   - Sin argumentos escribe `output/estimates_r.csv`. Con `panel.csv salida.csv` lo usan los tests. **No se ha ejecutado sobre los datos reales.**
4. **`code/analysis/test_s1r_estimate.py`** (8 tests, 16 casos), con el DGP de F9 (β_C = −6, β_U = −1, `het_eps`):
   - `test_v3s_tree_on_hand_built_estimates` (`:54`): 9 casos construidos a mano del árbol completo, conectado a las filas reales
     de las estimaciones.
   - `test_h0_only_uses_full_sample` (`:58`): la puerta H0 solo mira la muestra completa.
   - `test_h1_verdict_has_no_rule_b` (`:28`): el veredicto de H1 ya no tiene la rama (b).
   - `test_analysis_script_equals_the_mc_estimator` (`:93`): el script reproduce el estimador del MC de F9 (rel. 1e-10).
   - `test_python_r_parity_on_simulated_data` (`:107`): paridad Python–R en los 100 coeficientes y ee, con la tolerancia de
     `integrity.PARITY_RTOL`. Diferencia máxima observada: 2,5·10⁻¹³ en β y 2,3·10⁻¹³ en ee.
   - `test_samples_states_and_robustness_designs` (`:75`): N = 146 / 133 / 136, 73 y 62 restringidos, g.l. de cada id.
   - `test_shock_diagnostics_reproduce_f13` (`:124`): los diagnósticos reproducen `f13_shock_diagnostics.md:7-8`.

## Verificación
- `uv run pytest papers/p01-liquidity`: 93 passed.
- `uv run python tools/integrity.py`: OK.
- `uv run ruff check papers/p01-liquidity/code/analysis papers/p01-liquidity/code/mc`: limpio. El `ruff check .` del repo da 5 avisos,
  todos en `code/data/qfr_read.py`, que no es de esta tarea: es de F14a, en curso.

## HANDOFF
**Hecho.** Los puntos 1–4 del entregable (ver arriba). F15 queda marcada `[x]` en `TASKS.md`. No hay commit, como pide el encargo.

**Evidencia.**
- Código: `code/analysis/s1r_lp.py:64,75`, `code/analysis/01_s1r_estimate.py:49,82,105,113,156`,
  `code/replication_r/s1r_replication.R:45,62,73,80` y `code/mc/f9_power.py:146,232`.
- Tests: `code/analysis/test_s1r_estimate.py` y `code/mc/test_f9_power.py:37`, con el assert de (b) reapuntado a `h1_verdict_b`,
  no borrado.
- Base: HEAD 4b28fde con el árbol de trabajo sin commit.
- Texto que obliga: `SPEC.md:85-221` (prereg_commit 3d6b508).

**Decisiones y quién las tomó.** Todas son de esta desk, de implementación, y ninguna cambia el texto congelado:
1. Los `r1r_*` van a `estimates_py_robustness.csv` y no a `estimates_py.csv`, porque `SPEC.md:217-218` y el encargo piden en R solo los
   tres `s1r_*`. El check `parity` (`tools/integrity.py:195`) falla si un id está solo en Python. Alternativa: replicar también
   los `r1r_*` en R; son cuatro variaciones pequeñas del mismo script.
2. Los diagnósticos de los choques no pasan por `log_spec` ni por `estimates_py.csv`, porque no son especificaciones con la inversión.
   D3 usa ee HC1, como DP en `SPEC.md:107`: el texto no fija el ee de D3 (`SPEC.md:117`).
3. Se añade la columna `dof` a los CSV de estimaciones. `integrity` solo lee las cuatro obligatorias.

**Supuestos y límites** (texto aplicable, pero con una lectura que conviene que vean el Referee y la Dirección):
- `r1r_state_logistic` (`SPEC.md:183-184`):
  - Se usa F(z) = 1/(1+exp(γz)), con z = (s_{t−1} − mediana)/desv. típ. de s_{t−1} en la muestra completa y γ = 3.
  - Es la forma de Tenreyro-Thwaites, con z de varianza unitaria, orientada para que F → 1 con poca liquidez (el estado restringido).
  - La SPEC no dice que z se estandarice. Sin estandarizar, con γ = 3, F quedaría casi plana, en ≈ [0,36; 0,64]: la desv. típ. de
    s_{t−1} es 0,088 y su rango, [−0,20; 0,19].
- `r1r_from1971q3` (`SPEC.md:180-181`) conserva el D_{t−1} de la mediana de la muestra completa (146 filas): «solo se quitan
  filas», como sin Volcker (`SPEC.md:73-74, 83`). `r1r_state_q25` usa el cuartil de la muestra completa.
- La paridad está probada con datos simulados. Con los reales se comprueba al ejecutar F16: el pre-commit corre `parity`.
- El script exige que no falte ningún dato en la muestra: tiene un assert, en vez de quitar filas en silencio.

**Descartado y por qué.**
- Reutilizar `sample_counts_s1r.samples` en el script de análisis: exige la columna `mps_bs23_orth`, que no hace falta. La muestra se
  define con lo mínimo y el test comprueba que da 146 / 133 filas.
- Importar `f9_power` o `f13_checks` desde el análisis: el script de análisis no depende del código del MC. La equivalencia se
  comprueba en los tests.
- Usar `sandwich` en R: no combina HC3 con el núcleo de Bartlett en trimestres naturales.

**Pendiente de decidir** (Dirección y autores):
- Si se acepta la lectura de `r1r_state_logistic` (z estandarizada) y la del estado en `r1r_from1971q3`, o se registra otra como
  aclaración antes de F16.
- Si los `r1r_*` también se replican en R.
- F16 (estimar con la inversión real) necesita el visto bueno explícito de los autores (`TASKS.md:41`). Después, el Referee (F17).
