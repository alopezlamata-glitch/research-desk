# Inventario de iteraciones previas (p01)

Preparado por la Coordinación el 2026-11-04 a partir de un perfil automático de cada archivo (celdas,
palabras clave, cabeceras y salidas) y de la lectura directa de una parte de ellos. **No es la revisión
de fondo**: esa corresponde a las tareas 0.2 y 0.3.

## Dónde está
- `prior/archive/originals/`: los 57 archivos únicos, copiados de `Downloads`. Las subcarpetas de origen se
  conservan en el nombre (`Duplicados__…`, `ICADE__…`).
- `prior/archive/unzipped/z01…z04`: el contenido de los 4 zips.
- `prior/archive/_profile.json`: perfil automático (hash, tamaño, fecha, celdas, palabras clave).
- **`prior/archive/` está excluido de git**: contiene una clave de API de FRED escrita en el código (ver Seguridad).

Se listaron 62 archivos: 57 únicos y 5 duplicados exactos (mismo hash), que no se copian. Hay además
muchos **casi duplicados** (versiones que difieren en pocas líneas), agrupados abajo.

## Seguridad
**Una misma clave de API de FRED aparece escrita en 23 notebooks y en los zips.** Si alguno de esos archivos
se ha compartido (Colab, correo, coautor), conviene **revocarla y generar otra** en fred.stlouisfed.org.
En la desk no hace falta clave: los datos se descargan de `fredgraph.csv`; si alguna vez hiciera falta, se
leerá de la variable de entorno `FRED_API_KEY`.

## Cronología de la línea principal (transmisión / LDC)

| Fecha | Iteración | Archivos | Método | Estado |
|---|---|---|---|---|
| 2025-11 | **Coherence v5**: Kalman con estados k, κ, Γ, d | `Coherence2`, `CoherenceRobust`, `Duplicados__Untitled16 (3)`, `Duplicados__Untitled11 (2)` | Kalman lineal + Hamilton | Superada |
| 2025-11 | Suite de robustez | `CoherenceRobust_RobustnessSuite` | Tests A–H (aditivo vs multiplicativo, perfil θ/γ, MSPE, multistart) | **Solo con datos simulados aleatorios**: nunca se aplicó a datos reales. Las ideas de los tests son reutilizables |
| 2026-01 | "Liquidity, Debt, and Institutional Coherence: Empirical Proxies and Structural Estimation" | `FinalModel (1–4)`, `CommentedModel` (+`(1)`, `_tuned`), `Duplicados__Untitled21 (1)` | Kalman + LP de Jordà | 4–7 casi duplicados; el más completo parece `CommentedModel_tuned` (pendiente de confirmar) |
| 2026-01-25 | Paquete de datos FRED "auditable" | `Duplicados__Untitled26 (1)`, `Código definitivo limpio.pdf`, `FRED API Export Code.pdf` | Descarga + construcción de observables | Útil como referencia de series; los PDF son exportaciones de código |
| 2026-02 | **CoreBank EKF** (núcleo + banca) | `Best_CoreBank_EKF_sintetizado`, `CoreBank_EKF_6x6_paperdata`, `…_fixed_fallbacks` | EKF 3–6 estados | **Con errores** (ver abajo) |
| 2026-02-09 | Modelo de 6 estados | `liquidity_6state_full` | Kalman con k, κ, Γ, d, n, πᵉ | Más parámetros todavía: dirección opuesta a la que necesita el problema |
| 2026-03-09 | **LP con shocks monetarios externos** | `modelshock`, `Duplicados__modelshock (1)` | LP + shock de Jarociński-Karadi (2020); índice de canales multiplicativo (geométrico/log) frente a aditivo; bootstrap | **El antecedente más cercano al candidato B.** Resultado: la interacción shock × índice de canales sale significativa a h = 4 y h = 8 (θ geo ≈ 2,2, boot-p ≈ 0,001–0,003; θ log ≈ 0,46, p < 0,001). **Pendiente de auditoría** |
| 2026-03-10 | **Arquitectura TC_t** | `ICADE__…tc_architecture_colab` (v1–v3), `Duplicados__tc_architecture_colab` | LP + hipótesis rivales + no linealidad + bootstrap + pseudo-OOS + leave-episode-out | **El diseño metodológicamente más maduro.** v3 es la última. No se han visto sus salidas (se guardó sin ejecutar) |
| 2026-03-14/16 | S1 2026 + presentación de Frankfurt | `Liquidity_Adrian_Yannis…\Liquidity_Transmission_Coherence_S1_2026` (+ `_v19`), zips z02–z04 (PDF del paper (5), (6), (8) y `Frankfurt Presentation v2.pdf`) | GMM-EKF | Antecesora de v22 |
| 2026-05 a 09 | **v22 / JME** | `ModelJME (1)`, `(2)`, `(3) (1)` | GMM en dos etapas + EKF, Shapley | Es el PDF `prior/v22_transmission_capacity.pdf`. Diagnóstico en `prior/diagnosis_v22.md` |
| 2026-05-02 | **Réplica en Reino Unido** | `LDC_UK_v1_0` … `v1_4` | Mismo pipeline de v22 con datos ONS/OCDE/BIS vía DBnomics | **Con errores** (ver abajo). Valor: demuestra que hay datos de Reino Unido sin clave |
| 2026-10-20 | **Última iteración** ("Simulate This", TFG) | zip z01: `Policy_Confidence_Coherence.tex` + proyecto con `data/raw` (FRED, sorpresas monetarias) y `results/` | Modelo teórico simulado (patrimonio bancario N, deuda D, escenarios "Borrowing room" / "Weak bank") + sorpresas de política monetaria | **La más reciente: hay que leerla primero en la tarea 0.3** |

## Las dos líneas vigentes (según los autores, las más relevantes)

| Línea | Propuesta | Borrador | Núcleo |
|---|---|---|---|
| **TFG1** · *Simulating Liquidity Transmission and the Limits of Fiscal and Monetary Policy Coordination: A Short-Run Sectoral Model* | `prior/archive/tfg/TFG1_*` | z01 `…TFG_1_Simulate_This_2026_10_20.tex` | Hogares/empresas/bancos; I* = min{H(D), q/a}; capital bancario N; límite H(D) = [Ā − ωD]⁺; juego de Nash entre autoridades (componente común + brecha, cointegración); estados financieros; LP con sorpresas Bauer-Swanson |
| **TFG2** · *Policy Coordination, Debt Service and Liquidity Transmission: Precautionary Reserves, Contract Repricing and Spending Capacity* | `prior/archive/tfg/TFG2_*` | z01 `…TFG_2_October_20_2026/Liquidity_Transmission_Debt_Service.tex` | Liquidez de pagos y reservas precautorias; I + γm ≤ H; repreciación de la deuda dentro del intervalo de pago; cierre monetario; dos vencimientos; SMM + Sobol |

Ambas sustituyen la estructura de tres canales de v22 por **micro-fundamentos explícitos con pocos parámetros**
y comparten el contexto empírico (FRED 1991Q2–2025Q4 + LP con sorpresas de Bauer-Swanson 2023).

## Otras líneas (no son el paper, pero son experiencia reutilizable)

| Línea | Archivos | Qué es | Relevancia para p01 |
|---|---|---|---|
| **Predicción de recesiones / puntos de giro** | `Modelo_1 (A1)`, `Modelo_1 (A2)`, `Modelo_1_(A2)`, `Duplicados__Untitled22 (1)` y `(3)`, `Duplicados__Untitled25 (1) (1)`, `Duplicados__Untitled21 (2)`, `ICADE__…refactor_turning_points_us` | Hazard logit L1 con walk-forward, umbral por falsos positivos/año, lead time por recesión | **Alta para "regímenes"**: es una forma probada y sin look-ahead de fechar regímenes de estrés |
| Default de empresas (España, 2008–2011) | `Untitled11_(5)` y 3 variantes, `MODELO`, `TheModelv5` | Logit/ML de impago con ratios contables; AUC ≈ 0,73–0,75 | Baja. El dataset (`Variablesvf5.xlsx`) no está incluido |
| Estrategias de equity por liquidez | `liquidity_strategy`, `macro_liquidity_strategy` (+`_v2`) | Market timing con balance de la Fed, M2, tipos reales, DXY y NFCI | Baja para el paper. Sesgo de supervivencia y fundamentales actuales aplicados al pasado (look-ahead), reconocidos en el propio notebook |

## Errores concretos detectados (verificados leyendo el código)
1. **`LDC_UK_v1_x`: se estima con trimestres inventados.** `ar1_extend` proyecta con un AR(1) cada serie hasta
   2025-12 y después la muestra de estimación llega a 2025-12. v22 sí excluía esos trimestres. Además,
   `interpolate().ffill().bfill()` rellena huecos en ambos sentidos.
2. **`LDC_UK_v1_x`: instrumentos con etiquetas que no corresponden.** `z_vix_s` es −confianza empresarial,
   `z_drc_s` (morosidad) es la tasa de paro y `z_ted_s` es el spread gilt-OIS, que también entra en el FCI y en κ.
3. **`LDC_UK_v1_x`: γ elegido a la vista de los datos**, maximizando la correlación con el saldo primario ajustado.
4. **`LDC_UK_v1_x`: `y_gap_CBO` no es el gap de la CBO** sino un filtro de Hamilton. El nombre induce a error.
5. **`Best_CoreBank_EKF_sintetizado`: la "encuesta κ" es `UNRATE`** (un marcador de posición que nunca se sustituyó).
6. **`CoreBank_EKF_6x6_…fixed_fallbacks`: no se ejecuta.** Descarga en `series` pero luego usa `raw`, y llama a
   `to_quarterly(..., "sum")`, que no existe (solo `mean`/`last`).
7. **`CoreBank_EKF_6x6`** usa el filtro HP, en contra de la elección de Hamilton del resto de la línea.
8. **`CoherenceRobust_RobustnessSuite`** solo se ejecutó con datos aleatorios: sus resultados no informan de nada.
9. Lo que ya recoge `prior/diagnosis_v22.md` (convexidad, tests circulares, solapamiento de proxies e instrumentos).

## Qué se salva (propuesta para 0.3, a confirmar)
- **El diseño de `tc_architecture_colab_v3`**: estructura de evaluación (rivales, pseudo-OOS, leave-episode-out).
- **El resultado de `modelshock`**: es la pista empírica más prometedora; hay que auditarlo y replicarlo.
- **El hazard de recesiones**: una medida de régimen sin look-ahead.
- **Los datos**: DBnomics para Reino Unido y otros países; sorpresas monetarias (zip z01; también JK en `modelshock`).
- **La teoría de "Simulate This"** (patrimonio bancario, deuda): candidata a micro-fundamento más parsimonioso que el de v22.
