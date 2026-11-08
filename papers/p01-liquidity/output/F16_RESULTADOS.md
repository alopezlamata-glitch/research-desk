# F16 · Estimación de `s1r_*` con la inversión real (Econometría, 2026-11-08)

Encargo: `desks/econometria/ENCARGO_2026-11-08_f16-estimacion-s1r.md`. Texto que obliga: `SPEC.md:49-221` (prereg_commit 3d6b508,
huella `prereg 1d9476332d29`). Se han ejecutado `code/analysis/01_s1r_estimate.py` y `code/replication_r/s1r_replication.R` tal como
están en bd4f7bc: `git diff bd4f7bc -- papers/p01-liquidity/code` solo muestra archivos de F14a en `code/data/` (`qfr_*`,
`*_qfr_f14a.py`), ninguno de análisis ni de R. No se ha cambiado nada al ver los resultados. No hay estimaciones exploratorias.

**Resultado: `h0_falla`. H0 no se confirma, así que H1 no se interpreta y se escala al Director científico (`SPEC.md:148-150`).**

## 1. Estimaciones (`output/tables/s1r_estimates.md:5-19`)
`aum`, NW(5)+HC3, t de N − k g.l. Unidades: pp de ȳ (h = 4..12) por pp de choque (ε sumado en el trimestre). El p es unilateral, de β < 0.

| id | término | β̂ | ee | g.l. | p (β < 0) | IC al 95 % | fuente |
|---|---|---|---|---|---|---|---|
| s1r_lin | b_lin | −1,655 | 1,786 | 114 | 0,178 | [−5,193; 1,883] | `s1r_estimates.md:7` |
| s1r_liq | b_C | −2,874 | 1,653 | 112 | 0,042 | [−6,149; 0,400] | `:8` |
| s1r_liq | b_U | 0,841 | 4,341 | 112 | 0,577 | [−7,760; 9,441] | `:9` |
| s1r_liq_nov | b_C | −4,981 | 2,814 | 99 | 0,040 | [−10,565; 0,603] | `:10` |
| s1r_liq_nov | b_U | 1,024 | 4,687 | 99 | 0,586 | [−8,276; 10,324] | `:11` |

Coeficientes y ee completos: `output/estimates_py.csv` (100 filas, los tres `s1r_*`).

## 2. Veredicto según el árbol V3s, paso a paso (`SPEC.md:146-162`; `code/analysis/s1r_lp.py:59-90`)
1. **Puerta H0** (`s1r_lin`, muestra completa). Hace falta β̂_lin < 0 con p < 0,05. Sale β̂_lin = −1,655 con p = 0,178
   (`s1r_estimates.md:7`), así que **H0 no se confirma**. `decide("V3s", h0_full=False, ...)` devuelve `h0_falla` (`s1r_lp.py:85-86`;
   `s1r_estimates.md:21`).
2. El paso 2 (β_C en `s1r_liq`) **no se evalúa como veredicto**. Según `SPEC.md:149-150`, β̂_C, β̂_U y sus IC se publican como
   medición, sin veredicto (tabla del §1).
3. El paso 3 (V3s, `s1r_liq_nov`) tampoco se evalúa. Su resultado se publica siempre (`SPEC.md:162`; tabla del §1).

- **H0:** no se confirma.
- **H1:** no se interpreta. Ni se confirma, ni se refuta, ni es «no concluyente»: el árbol no llega a evaluarla.
- Lo que la SPEC prevé en este caso es escalar al Director científico. Esta desk no lo resuelve.

## 3. Diagnósticos de los choques (`output/tables/s1r_shock_diagnostics.md:5-8`; no usan la inversión)
| muestra | N | D1 restr./holg. | D2 Σ\|ε\| restr./holg. | D3 F (p) | Ljung-Box(12) (p) | Predictibilidad F (g.l.; p) |
|---|---|---|---|---|---|---|
| completa | 146 | 73 / 73 | 31,036 / 21,754 | 0,50 (0,606) | 16,78 (0,158) | 1,07 (12, 133; 0,391) |
| sin Volcker | 133 | 62 / 71 | 18,195 / 19,810 | 0,49 (0,613) | 22,86 (0,029) | 1,66 (12, 120; 0,085) |

- El Ljung-Box y la predictibilidad coinciden con las cifras ex ante de `SPEC.md:106-109` (`f13_shock_diagnostics.md:7-8`).
- D3 no rechaza el balance del choque entre estados en ninguna muestra (p = 0,606 y 0,613).
- **Consecuencia** (`SPEC.md:110-115`): ninguna sobre la especificación ni sobre el veredicto. El Ljung-Box rechaza sin Volcker
  (p = 0,029). Por eso, en `s1r_liq_nov` el estimando de choque aislado no es comparable uno a uno con β_ref, y la lectura en
  múltiplos de β_ref es aproximada. La cifra que vale ahí es el MDE en pp de ȳ por pp de choque. Como `s1r_liq_nov` no decide
  (paso 3 no evaluado), la salvedad solo afecta a cómo se presenta esa medición.

## 4. Robustez prerregistrada (`output/tables/s1r_estimates.md:12-19`; `output/estimates_py_robustness.csv`). No decide.
| id | b_C (ee; p; IC 95 %) | b_U (ee; p; IC 95 %) | fuente |
|---|---|---|---|
| r1r_from1971q3 | −2,035 (1,974; 0,152; [−5,950; 1,879]) | 0,059 (4,097; 0,506; [−8,067; 8,184]) | `:12-13` |
| r1r_state_q25 | −6,085 (3,045; 0,024; [−12,118; −0,052]) | −0,840 (2,488; 0,368; [−5,769; 4,089]) | `:14-15` |
| r1r_state_logistic | −4,576 (2,196; 0,020; [−8,928; −0,225]) | 1,890 (5,289; 0,639; [−8,589; 12,369]) | `:16-17` |
| r1r_lags4 | −2,219 (1,582; 0,082; [−5,356; 0,917]) | 3,034 (4,028; 0,773; [−4,953; 11,021]) | `:18-19` |

Como `s1r_liq`, estas filas son medición sin veredicto. La puerta H0 no se ha superado y la robustez no decide (`SPEC.md:178`).

## 5. Frente a la potencia escrita ex ante (medición acotada)
- `SPEC.md:166-168` anticipaba que, con un efecto del tamaño de β_ref = −1,820, el resultado más probable sería precisamente
  «H0 no se confirma»: P = 0,824 / 0,854 (f13:31, 47).
- El IC al 95 % de β_lin, [−5,193; 1,883], contiene tanto 0 como β_ref. Los datos no distinguen entre ausencia de efecto y un
  efecto del tamaño de referencia.
- Por eso este resultado **no es evidencia de ausencia de efecto** (`SPEC.md:161`). El MDE ex ante es de unos 10 pp de ȳ por pp de
  choque (`SPEC.md:171-173`).

## 6. Paridad Python–R
- `output/estimates_r.csv` tiene 100 filas, las mismas (spec_id, term) que `estimates_py.csv`.
- Diferencia relativa máxima: 2,0·10⁻¹² en β y 3,3·10⁻¹⁴ en ee. La tolerancia es `PARITY_RTOL = 1e-6` (`tools/integrity.py:187`).
- Los términos que deciden coinciden con todos los decimales mostrados.

## Verificación
- `uv run python tools/integrity.py`: `integridad: OK` (incluye `parity` y `speclog`).
- `uv run pytest papers/p01-liquidity`: 100 passed.
- `uv run ruff check papers/p01-liquidity/code/analysis`: limpio.
- `output/spec_log.csv:2-8`: los 7 ids registrados como prerregistrados (`exploratory=False`), con huella 1d9476332d29.

## HANDOFF
**Hecho.**
- Se ha ejecutado el análisis prerregistrado y su réplica en R sobre la inversión real.
- Salidas: `output/estimates_py.csv`, `output/estimates_r.csv`, `output/estimates_py_robustness.csv`, `output/spec_log.csv`,
  `output/tables/s1r_estimates.md` y `output/tables/s1r_shock_diagnostics.md`.
- Veredicto V3s: `h0_falla`.
- F16 queda marcada `[x]` en `TASKS.md`. Sin commit, como pide el encargo.

**Evidencia.**
- Veredicto: `output/tables/s1r_estimates.md:7,21` y `code/analysis/s1r_lp.py:85-86`.
- Medición: `s1r_estimates.md:8-19`.
- Diagnósticos: `output/tables/s1r_shock_diagnostics.md:7-8`.
- Registro: `output/spec_log.csv:2-8` (commit `690658d-dirty`). El dirty es el árbol de trabajo con `desks/RUNS.csv` y los
  `output/` de esta tarea. El código de análisis y el de R son los de bd4f7bc.
- Texto que obliga: `SPEC.md:146-162` (árbol) y `SPEC.md:110-115` (diagnósticos).

**Decisiones y quién las tomó.**
- Ninguna nueva. Se ha aplicado el árbol congelado por los autores (prereg_commit 3d6b508) y el código revisado en F15.
- No se ha corrido ninguna especificación exploratoria. El encargo no la pedía, y ninguna puede cambiar el veredicto.

**Supuestos y límites.**
- Se mantienen las lecturas de implementación de F15 que siguen pendientes de ver la Dirección y el Referee
  (`output/F15_REQUISITOS.md:67-76`):
  - z estandarizada en `r1r_state_logistic`;
  - mediana de la muestra completa en `r1r_from1971q3`.
- Ambas afectan solo a la robustez, que no decide.
- Los `r1r_*` no se replican en R (`F15_REQUISITOS.md:60-62`).

**Descartado y por qué.**
- Evaluar los pasos 2 y 3 del árbol como veredicto: la SPEC lo prohíbe cuando falla H0 (`SPEC.md:148-150`).
- Cualquier análisis adicional (V1/V2, `base`, IRF, asimetría…): es exploratorio, fuera del alcance del encargo, y no puede cambiar
  el veredicto.

**Pendiente de decidir** (Director científico y autores; `SPEC.md:149-150`):
- Qué se hace tras «H0 no se confirma». La SPEC lo escala al Director científico y esta desk no lo resuelve.
- Hecho que deben tener a la vista, sin que sea un veredicto:
  - b_C tiene p unilateral < 0,05 en la muestra completa y en la muestra sin Volcker (`s1r_estimates.md:8,10`);
  - pero sus IC al 95 % contienen el 0;
  - y el árbol prerregistrado no permite leerlo como confirmación porque H0 falla.
- Cualquier uso de este hecho distinto de «medición sin veredicto» sería una Desviación posterior a ver los datos.
- Auditoría del Referee (F17), en sesión nueva.
