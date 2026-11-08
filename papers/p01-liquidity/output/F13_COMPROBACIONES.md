# F13 · Comprobaciones para el prerregistro `s1r_*` (Econometría, 2026-11-08)

Encargo: `desks/econometria/ENCARGO_2026-11-08_f13-comprobaciones-s1r.md`. Código: `code/mc/f13_checks.py` (test
`code/mc/test_f13_checks.py`). Tablas: `output/tables/f13_checks.md` (§1 y §2) y `output/tables/f13_shock_diagnostics.md`.
Semilla 20261107 y 1000 réplicas, como F9. Las celdas que repiten F9 usan su semilla y reproducen sus cifras (c = 1, 2, 3, 5 y 7;
m = 1 y m = 0). Regla dura cumplida: de la inversión real solo entra el AR(2) univariante del DGP de F9.

## 1. Equivalencia del h = 0: suma o promedio del choque (`f13_checks.md`, §1, líneas 7–23)
- **Promedio de los 3 meses (lo que hacen Tenreyro-Thwaites con la serie mensual de Romer-Romer): invariancia exacta.** Todos los
  trimestres tienen 3 meses (`build_stage1r_us.py:41`), así que ε_media = ε_suma/3. π(h = 0) pasa de 0,949 a 2,848 y β_ref de −1,820 a
  −5,459 (×3,000000). Con las mismas réplicas, los t de b_lin, b_C y b_U difieren como mucho en 1,3·10⁻¹², y los veredictos de V3s
  son idénticos. La potencia frente a β_ref no cambia: P(confirma) de V3s con c = 1 es 0,037 (homo) y 0,059 (het_eps) en los dos casos.
  El efecto de 1 desv. típ. de ε también es el mismo (−1,092 pp).
- **Lo que sí cambia es la unidad del MDE «por pp de ε»**, que se multiplica por 3 con el promedio. El MDE por pp de fed funds
  (c × 1,917) no depende de la agregación. El prerregistro tiene que decir que ε es la **suma** mensual.
- **Sensibilidad: media de los meses con choque ≠ 0** (aproxima la media por reunión; el Handbook no trae los datos por reunión). No es
  un reescalado, porque 1–3 meses por trimestre tienen choque. β_ref = −3,445 y P(confirma) de V3s con c = 1 = 0,032 (homo) y 0,034
  (het_eps), frente a 0,037 y 0,059. **No es un cambio material:** la potencia sigue en 0,03–0,06. No se activa la condición de parada.

## 2. MDE simulado y fila del rival, V3s con `aum` (`f13_checks.md`, §2, líneas 29–69)
- **c = 4:** P(confirma) = 0,590 (homo) y 0,600 (het_eps); MDE implícito de 7,28 pp de ȳ por pp de ε (7,67 por pp de fed funds).
- **c = 4 no alcanza 0,8 en V3s.** El cruce de V3s cae entre c = 5 y c = 7, no entre 3 y 5 (ese intervalo era el de V1).
  Por eso simulé también c = 5,5 y c = 6. Con c = 5,5, P(confirma) = 0,797 (homo) y 0,840 (het_eps). **MDE de V3s: c ≈ 5,5 (homo) y
  5,2 (het_eps)**, es decir, 10,0 y 9,5 pp de ȳ por pp de ε (10,5 y 10,0 por pp de fed funds). El 5,5 de F9 se confirma con una celda
  simulada en el propio punto.
- **Rival (β_C = 0, β_U = c·β_ref):** P(confirma) de V3s ≤ 0,035 (homo) y ≤ 0,033 (het_eps) para c ≤ 5, y ≤ 0,035 en toda la rejilla
  hasta c = 7. El tamaño queda por debajo de α en todo lo simulado. `refuta_a` vale 0 en todas las celdas.

## 3. Diagnósticos de los choques (`output/tables/f13_shock_diagnostics.md`, líneas 74–77)
| muestra | Ljung-Box(12) | p | F de predictibilidad (HC1) | p |
|---|---|---|---|---|
| completa (N = 146) | 16,78 | 0,158 | F(12, 133) = 1,07 | 0,391 |
| sin Volcker (N = 133) | 22,86 | 0,029 | F(12, 120) = 1,66 | 0,085 |

Reproducen al tercer decimal la réplica del Referee (`audits/replication_2026-11-08/rep_f9_R_output.txt:51-56`).

## 4. Corrección de `output/F9_MC_REPORT.md:108`
El texto ahora dice que el MDE invariante es por pp de choque (≈ 10 pp de ȳ por pp de ε en V2/V3s). Por pp de fed funds es c × 1,92:
≈ 10,6 con h = 0 y ≈ 6,0 con h = 1 (F10, hallazgo 5).

## HANDOFF
**Hecho.** Están los puntos 1–4 del encargo. No se ha activado la condición de parada.

**Evidencia.**
- `output/tables/f13_checks.md:7-23`: equivalencia del h = 0.
- `output/tables/f13_checks.md:29-69`: c = 4, rival y MDE.
- `output/tables/f13_shock_diagnostics.md:74-77`: diagnósticos de los choques.
- `output/F9_MC_REPORT.md:107-110`: corrección del punto 4.
- Código en `code/mc/f13_checks.py`; reutiliza `f9_power.DGP`, `simulate` y `verdict_probs` sin cambiarlos.
- `uv run python tools/integrity.py`: OK. `uv run pytest papers/p01-liquidity`: 78 passed. `uv run ruff check .`: OK.
- Sin commit, como pide el encargo.

**Decisiones y quién las tomó** (Econometría, criterio propio):
- Simular también c = 5,5 y c = 6, porque c = 4 no encuadra el MDE de V3s.
- Contar `refuta_b` como no concluyente, porque los autores retiraron la regla (b) en la Desviación del 2026-11-08, punto 6. En
  `aum` vale 0 en todas las celdas.
- Semillas nuevas con j = 7, 8 y 9 en el esquema de F9 (`f13_checks.py::seed`).
- Usar la media de los meses ≠ 0 como sensibilidad del promedio por reunión.

**Supuestos y límites.**
- Leo «quarterly averages» de TT (F12, punto 1.2) como la media de los 3 meses de la serie mensual. Si TT promediaran por reunión, la
  aproximación es la media de los meses ≠ 0, y no puedo verificarla sin los datos por reunión.
- El MDE es una interpolación lineal en una rejilla de 0,5–1 en c, con 1000 réplicas: el error MC de P es ±0,013.
- Ruido solo homo y het_eps, como el §2–3 de F9.

**Descartado y por qué.**
- Repetir los diagnósticos con la media ≠ 0: no lo pide el encargo. Ljung-Box y la F son invariantes a reescalar, pero no a esa
  agregación.
- Rehacer el MC de F9: el encargo lo excluye.

**Pendiente de decidir (autores / F11).**
1. Escribir en el prerregistro que ε es la suma mensual por trimestre y que el MDE se da por pp de ε y por pp de fed funds (h = 0).
2. Qué MDE de V3s se escribe: 5,5 (homo) o la horquilla 5,2–5,5.
3. Cómo se declara la autocorrelación de RR sin Volcker (p = 0,029) en el supuesto de choque aislado (Desviación 2026-11-08, punto 3).
