# F4 · Monte Carlo de la especificación prerregistrada `s1_liq` — informe de Econometría (2026-11-04)

Encargo: `desks/econometria/ENCARGO_2026-11-04_f4-montecarlo.md`. Este informe **no** es una auditoría (eso es del Referee).
**Todas las cifras salen de `output/tables/f4_power.md`** (y de la tabla estándar `output/tables/mc_s1_liq.txt`), generadas por
`code/mc/f4_power.py` (semilla 20261104, 1000 réplicas por escenario y 500 en la curva de potencia). Se reproducen con
`uv run python papers/p01-liquidity/code/mc/f4_power.py` (≈ 8 min). Tests: `code/mc/test_f4_power.py`.

**Regla dura cumplida.** No se ha estimado `s1_lin` ni `s1_liq` con la inversión real, ni se ha mirado cómo responde la inversión a los
choques. De la inversión real solo se usa un AR(2) univariante de su crecimiento, sin choques, porque es la serie del control
"Δlog inversión" y fija el nivel de ruido (ver §1).

## 0. Conclusión (una página)

1. **Errores estándar.** El NW(5) prerregistrado **sale de la banda**: cubre entre 0,86 y 0,90 con T = 102 en todos los escenarios y
   términos, y entre 0,78 y 0,88 con T/2. Por eso `tools/mc.py` lanza `CoverageOutOfBand`. La causa no es el solape sino el
   **apalancamiento**: en cada celda estado × signo, dos trimestres suman el 36–45 % de Σε², y el apalancamiento máximo es 0,41
   (media 0,16). Hay dos pistas que lo apoyan:
   - HC1 (sin HAC) cubre bien los términos menos apalancados;
   - corregir los grados de libertad (×N/(N−k)) no basta.

   **Recomiendo NW(5) en trimestres naturales con residuos HC3** (u_i/(1−h_ii)). Cubre entre 0,935 y 0,963 con T en los cuatro
   escenarios, y entre 0,951 y 0,986 con T/2 (conservador). `tools/mc.py` lo da por bueno, y también a HC3 sin HAC, que cubre entre
   0,950 y 0,980 con T y llega a 0,999 con T/2, más conservador. **Es una Desviación que tienen que registrar los autores antes de estimar.**
2. **Potencia.** Frente a la alternativa de referencia (β_U = β_C = β_ref = −0,88), la potencia de "confirma" (Holm, unilateral) es
   **0,033 en subidas y 0,025 en bajadas** con el error recomendado, y 0,085 y 0,073 con el NW(5) prerregistrado, que está
   sobredimensionado. Es decir, potencia ≈ tamaño. La potencia de 0,8 se alcanza con β ≈ −35 pp de ȳ por 1 pp de ε (**≈ 40·β_ref**;
   tabla 2). Con β_ref, un choque de 1 desviación típica mueve ȳ 0,067 pp, frente a errores estándar de 9–17 pp.
3. **¿Qué veredictos son alcanzables?** Con potencia < 0,8, la SPEC prohíbe declarar refutación por un β_C no significativo, así que
   la regla (b) queda **inactiva**. Por construcción, el resultado más probable en todos los escenarios es **"no concluyente por
   potencia"**, con una probabilidad de 0,89–0,93 con el error recomendado. "Confirma" y "refuta (a)" solo ocurren a la tasa del
   error de tipo I: 2–6 %.
4. **¿Tiene sentido estimar?** Con la β_ref de Tenreyro-Thwaites, **la etapa 1 tal como está prerregistrada no puede discriminar
   H1**. Estimar solo produce información si el efecto verdadero es ≈ 30–40 veces el de referencia. Eso equivale a ≈ 15–20 pp de
   inversión no residencial por 1 pp del fed funds en la media de h = 0..4 (con π_ffr = 1,761), frente a 0,5 pp en la referencia:
   una cifra **implausible**. **Recomiendo no estimar
   `s1_liq` hasta que los autores y el Director decidan** entre:
   - (i) aceptar y prerregistrar que el resultado esperado es "no concluyente por potencia" y presentarlo como tal;
   - (ii) rediseñar para ganar potencia antes de ver datos: choque con más varianza o instrumento más fuerte, más T o un panel
     (etapa 2), menos parámetros, o una variable de resultado más sensible.

   Es una decisión científica: la escalo y no la tomo yo.

## 1. DGP (cada elección, documentada)

| Elemento | Elección | Por qué |
|---|---|---|
| Muestra | Las 102 filas exactas de `sample_counts.sample()` (celdas 22/29/28/23) | Encargo; conserva el desequilibrio entre celdas |
| Choque y estado | `mps_bs23_orth` y `D_{t−1}` **reales y fijos** en todas las réplicas | Conserva la varianza y la cola del choque, que es lo que determina la potencia |
| Variable dependiente | Se simula g_t = 100·Δlog I_t = μ + φ1 g_{t−1} + φ2 g_{t−2} + b_t ε_t + e_t sobre el **calendario completo** 1985Q1–2026Q4 (40 trimestres de *burn-in*); ȳ_t se construye con la misma función `s1_lp.ybar` que se usará con los datos reales | El solape h = 0..4 genera el MA(4) del error de forma estructural. ȳ_t contiene además la respuesta a los choques futuros ε_{t+1..t+4}, como en los datos. Los huecos (ZLB, 2019–21) quedan bien tratados |
| Dinámica y ruido | AR(2) de 100·Δlog `inv_nonres_q` en las 102 filas, **sin choques**: φ1 = 0,465, φ2 = 0,271, σ_e = 1,357. Las innovaciones se remuestrean (iid) de sus residuos centrados, para conservar las colas | El control "Δlog inversión" es una serie que el encargo permite usar. El σ univariante incluye la parte del choque, así que es ligeramente **conservador** |
| Sensibilidad del ruido | σ_e condicionado a los 10 controles (×0,909, tabla 3) | La potencia apenas cambia: 0,032 y 0,023 con el error recomendado |
| Efecto | Impulso b·ε_t en g_t, propagado por el AR(2); b = β/κ, con κ = 1,865 el efecto en ȳ de un impulso unitario (test `test_kappa_…`) | Así β es exactamente el coeficiente de ȳ en la población |
| Controles | Los otros 4 (Δlog PIB, Δlog deflactor, Δy2, EBP) son **reales**. Δlog inversión es la **simulada**. Todos con 2 retardos, como en la SPEC | Así el control de la variable dependiente es coherente con el DGP |
| T/2 | Bloque contiguo aleatorio de 51 filas, con el estado de la muestra completa | `mc.validate` exige T y T/2 |

**Error de diseño condicional** (columna "error de diseño" de la tabla 1a). Como los choques son fijos, la respuesta a ε_{t+1..t+4} que
contiene ȳ_t deja un error determinista, casi proporcional a β, que no se promedia entre réplicas. Con β_ref vale entre −0,02 y +0,32,
despreciable frente a una desviación típica de β̂ de 8–16. Lo separa la función `design_error`. El test comprueba que el sesgo restante
(el del ruido) es cero dentro de 4 errores de Monte Carlo. **Advertencia:** si el efecto verdadero fuera grande, este término atenuaría
β_U en un ≈ 30 % en nuestra muestra concreta (diagnóstico con β = −40). Afecta a E1 (β_C − β_U), que es exploratoria.

## 2. β_ref

- **Fuente.** Tenreyro y Thwaites (2016), pp. 11–12. En el modelo lineal, la inversión empresarial cae **≈ 2,5 % en el pico** por 1 pp
  del fed funds, y el output toca fondo "two to three years after the shock" (p. 11). Se mantiene la propuesta del borrador: es la
  única fuente con página en la biblioteca que da una respuesta de la inversión por pp del tipo oficial.
- **Supuesto de forma [criterio propio].** Rampa lineal desde 0 en h = 0 hasta el pico en h = 10, es decir, 2,5 años, el centro de
  "two to three years". La media de h = 0..4 es entonces 0,2 × pico.
- **Traducción a unidades de ε.** π_ffr es la respuesta del fed funds (media trimestral) en h = 0 a 1 pp de `mps_bs23_orth`: MCO de
  ffr_t − ffr_{t−1} sobre ε_t en la muestra. Sale **1,761 (ee 0,856)**. No usa la inversión.
  - Con el rendimiento a 2 años sale 0,697 (ee 0,732), y con h = 1 se obtiene 2,406 para el fed funds.
  - Se elige el fed funds porque Tenreyro-Thwaites normalizan sus IRF con él.
- **β_ref = −2,5 × 0,2 × 1,761 = −0,881** pp de ȳ por 1 pp de ε.
  - Sensibilidad: con el pico en h = 8, −1,101; con el pico en h = 12, −0,734; con π_ffr ± 1,645 ee, entre −1,585 y −0,176.
  - Incluso el extremo más favorable (≈ −1,6) está ≈ 20 veces por debajo de lo que haría falta para una potencia de 0,8 (tabla 2).
    **La conclusión de potencia no depende de estos supuestos.**

## 3. Resultados (T = 102; columnas: ee prerregistrado NW(5) | ee recomendado NW(5)+HC3)

Cobertura del IC al 95 % (t con 86 g.l.), mínimo–máximo de los cuatro términos (tabla 1a):

| β_C / β_ref | NW(5) prerreg. | NW(5)+HC3 | NW(5)+HC3, T/2 |
|---|---|---|---|
| 1 | 0,872–0,900 | 0,949–0,963 | 0,963–0,983 |
| 0,5 | 0,869–0,890 | 0,940–0,958 | 0,951–0,983 |
| 0,146 | 0,864–0,895 | 0,936–0,955 | 0,968–0,985 |
| 0 (rival TFG1 / límite rígido) | 0,861–0,895 | 0,935–0,962 | 0,963–0,986 |

**Sesgo.** Con T, |sesgo| ≤ 1,2 en todos los escenarios, frente a desviaciones típicas de β̂ de 7,8–16,6. Es cero dentro del error de
Monte Carlo, salvo el error de diseño descrito arriba. El estimador puntual es insesgado; el problema es solo de precisión.

Probabilidad de cada veredicto con T (tabla 1b), en formato subida / bajada:

| β_C / β_ref | ee | confirma | refuta (a) | refuta (b)* | no concluyente |
|---|---|---|---|---|---|
| 1 | NW(5) prerreg. | 0,085 / 0,073 | 0,082 / 0,070 | 0,032 / 0,017 | 0,801 / 0,840 |
| 1 | NW(5)+HC3 | 0,033 / 0,025 | 0,033 / 0,027 | 0,017 / 0,022 | 0,917 / 0,926 |
| 0,5 | NW(5)+HC3 | 0,034 / 0,037 | 0,043 / 0,036 | 0,026 / 0,021 | 0,897 / 0,906 |
| 0,146 | NW(5)+HC3 | 0,030 / 0,023 | 0,059 / 0,041 | 0,017 / 0,020 | 0,894 / 0,916 |
| 0 | NW(5)+HC3 | 0,034 / 0,016 | 0,055 / 0,042 | 0,019 / 0,016 | 0,892 / 0,926 |

\* Antes de aplicar la cláusula de potencia. Con potencia < 0,8, la SPEC convierte (b) en "no concluyente por potencia". "Confirma" y
"(b)" no coinciden nunca (columna de solape = 0).

**Lectura:**
- Las probabilidades apenas cambian entre β_C = β_ref y β_C = 0: el diseño no distingue H1 de sus rivales.
- Con el NW(5) prerregistrado, "confirma" y "refuta (a)" ocurren ≈ 4–10 % de las veces por puro ruido: tamaño real de hasta ≈ 2 veces el nominal.
- Hay un riesgo de **falsa refutación (a)** cuando H1 es cierta (β_C = β_ref): **3,3 % / 2,7 %** con el error recomendado, frente a
  **8,2 % / 7,0 %** con el prerregistrado.

**Potencia de "confirma" frente a la magnitud del efecto** (tabla 2, β_U = β_C = c·β_ref, NW(5)+HC3, subida / bajada):
- c = 1: 0,034 / 0,016;
- c = 10: 0,122 / 0,144;
- c = 20: 0,394 / 0,392;
- c = 30: 0,652 / 0,720;
- **c = 40: 0,840 / 0,930**.

## 4. Recomendación de errores estándar (para la Desviación)

> `s1_liq` (y, por coherencia, `s1_lin` y las robusteces) usan una varianza sándwich HAC con kernel de Bartlett y 5 retardos medidos
> en **trimestres naturales** (las filas separadas por un hueco de la muestra no comparten solape), calculada con los **residuos HC3**
> u_i/(1−h_ii). Valores críticos de la t con N−k grados de libertad. Implementación: `code/analysis/s1_lp.py::fit(..., leverage=True)`
> con `hac_weights(quarters, 5)`. Validado por F4: cobertura 0,935–0,963 con T = 102.

- **Alternativas descartadas.**
  - NW por filas: igual que NW en calendario, 0,86–0,90.
  - NW ×N/(N−k): 0,89–0,93, fuera de la banda en varios términos.
  - HC1: 0,90–0,95, `b_pos_C` fuera.
  - HC3 sin HAC: válido, pero descarta la corrección del solape que motiva la SPEC; queda como robustez si los autores lo prefieren.
- **No he probado el bootstrap por bloques.** Con 102 filas, huecos y 2 trimestres que dominan cada celda, un bloque que excluya o
  duplique uno de ellos cambia el diseño. Además, la alternativa analítica ya entra en la banda.
- **Requisito del análisis real.** El script de `s1_liq` tiene que llamar a `s1_lp.fit` con `leverage=True` y `hac_weights` sobre
  `quarter.asi8`: la misma función que se ha validado. `s1_lin` no se ha simulado (el encargo era `s1_liq`); si la Dirección lo
  pide, es un escenario más del mismo script.

## 5. Qué falta y riesgos

- **Decisiones de los autores, antes de estimar:**
  - (1) la Desviación de los errores estándar;
  - (2) qué hacer con una potencia ≈ tamaño (§0.4).
- **El Referee** debe auditar este MC en sesión nueva, en particular el DGP con choques fijos y la traducción de β_ref.
- **Riesgos:**
  - el AR(2) univariante no reproduce la heterocedasticidad condicional de la inversión (crisis de 2008), aunque los residuos remuestreados conservan las colas;
  - el estado se trata como exógeno a ȳ;
  - la cobertura con T/2 es conservadora (hasta 0,986), así que con submuestras (p. ej., `r_bs23orth_1994`) los IC serán anchos.
