# p01 · F11 · Borrador del prerregistro nuevo de la etapa 1 (`s1r_*`) — Director científico (2026-11-08)

Encargo: `desks/direccion-cientifica/ENCARGO_2026-11-08_f11-prereg-s1r.md`. Lo aprueban los autores; después la Coordinación
sustituye con la **parte 1** la sección "## Prerregistro de la etapa 1: EE. UU." de `SPEC.md` (líneas 49–129 en 104aad5).

Obliga: SPEC, Desviaciones del 2026-11-07 (`SPEC.md:155-182`) y del 2026-11-08 (`SPEC.md:183-201`, las 7 decisiones).
Contexto: `exploration/DECISIONES_AUTORES_F11_2026-11-08.md`, `audits/2026-11-08_F9_mc.md` (F10), `output/F9_MC_REPORT.md`,
`exploration/F12_CITAS_2026-11-08.md`. **Las cifras salen de `output/tables/f9_power.md` (abreviado `f9:<línea>`)** o de
`data/clean/SAMPLE_COUNTS_S1R.md`; las que dependen de F13 van marcadas **`[F13]`** y no se dan.

**Nota de formato para la Coordinación.** `integrity.py::prereg_text` congela el texto desde el último encabezado `## ` anterior
al bloque hasta el cierre del bloque (regex `^## `; `### ` no cuenta). Por eso la sección no lleva ningún `## ` intermedio: si se
añadiera uno, la parte de arriba quedaría fuera del texto congelado.

---

# Parte 1 · Texto para la SPEC (sustituye a la sección actual)

## Prerregistro de la etapa 1 rediseñada: EE. UU. (`s1r_*`; aprobado por los autores el [fecha])

Sustituye al prerregistro de la etapa 1 aprobado el 2026-11-04 (`prereg_commit: af1c346`), cuyos ids `s1_*` y `r_*` no se
estiman (Desviación del 2026-11-07). Decisiones de los autores: Desviaciones del 2026-11-07 y del 2026-11-08; justificación en
`exploration/DECISIONES_AUTORES_F11_2026-11-08.md` y `exploration/PREREG_S1R_DRAFT.md`. El MC que respalda este diseño es F9
(`output/F9_MC_REPORT.md`, tablas `output/tables/f9_power.md`), auditado en F10 (`audits/2026-11-08_F9_mc.md`, APROBADO CON
CAMBIOS), con las comprobaciones de F13 (`output/F13_COMPROBACIONES.md`). Nada de esto ha usado la respuesta de la inversión.

**Pregunta.** ¿Se transmite un choque monetario a la inversión no residencial de EE. UU. cuando la liquidez de las empresas no
financieras está por debajo de su tendencia, como predice el margen interior de reservas (ω ≥ ω_min > 0)? Se mide como la
respuesta media en h = 4..12 trimestres, con subidas y bajadas juntas (la asimetría es exploratoria).

**Muestra y datos.**
- Choque principal: `rr_shock` (Romer-Romer, extensión de Coibion reestimada por Wieland, `resid_full`; agregado al trimestre
  como suma de los 3 meses, `data/clean/DICTIONARY.md:121,128`) **[F13: si la agregación por suma frente a promedio cambia β_ref
  o la potencia de forma material, los autores lo deciden antes de aprobar]**.
- t ∈ 1969Q1–2005Q2 (`in_rr_sample`; el último t con t + 12 ≤ 2008Q2): N = 146, 73 trimestres en el estado restringido y 73 en el
  holgado (f9:6; `data/clean/SAMPLE_COUNTS_S1R.md:11-12`).
- Muestra sin Volcker: la anterior sin las filas t ∈ 1979Q4–1982Q4 (13 trimestres). N = 133, con 62 y 71 por estado (f9:7;
  `SAMPLE_COUNTS_S1R.md:18-19`). Solo se quitan filas: el estado, los adelantos y retardos del choque y ȳ_t de las demás filas
  se calculan con la serie completa, como en el MC (`code/analysis/s1r_lp.py:44-54`).
- Réplica con `mps_bs23_orth`: t ∈ 1988Q1–2005Q2, N = 70 (f9:17). No decide (ver robustez).
- Inversión `A008RA3Q086SBEA` (índice de cantidad, BEA vía FRED), PIB real `GDPC1`, deflactor `GDPDEF`, fed funds `ffr` (media
  trimestral). Datos en última revisión, congelados por el hash de `data/raw/MANIFEST.csv`; refrescarlos es una Desviación.
- Choques sin dato (antes de 1969Q1 en los retardos de las primeras filas; 2008Q1–Q2 en los adelantos de las dos últimas) cuentan
  como 0 (`s1r_lp.py:12`).

**Estado.** `D_{t−1}` = 1 (restringido) si `s_{t−1}` < mediana de `s_{t−1}` en la muestra completa de cada choque, con s =
log(`liq_broad_debt`) menos su media móvil de los 12 trimestres anteriores (`DICTIONARY.md:123`). La mediana no se recalcula en la
muestra sin Volcker (Desviación del 2026-11-07, Volcker).

**Especificación `aum`** (forma reducida, MCO; estimador `code/analysis/s1r_lp.py`, el mismo del MC):
- Variable dependiente: ȳ_t = (1/9) Σ_{h=4..12} 100·[log I_{t+h} − log I_{t−1}].
- `s1r_lin`: ȳ_t = α + β_lin ε_t + Σ_{j=1..10} λ_j ε_{t−j} + Σ_{j=1..12} φ_j ε_{t+j} + Σ_{ℓ=1,2} Γ_ℓ' x_{t−ℓ} + u_t.
- `s1r_liq`: ȳ_t = α + δ D_{t−1} + β_C D_{t−1} ε_t + β_U (1 − D_{t−1}) ε_t + Σ_{j=1..10} λ_j ε_{t−j} + Σ_{j=1..12} φ_j ε_{t+j}
  + Σ_{ℓ=1,2} Γ_ℓ' x_{t−ℓ} + u_t. Los retardos y adelantos del choque no se interactúan con el estado.
- `s1r_liq_nov`: `s1r_liq` en la muestra sin Volcker.
- Controles x_t: Δlog inversión, Δlog PIB real, Δlog deflactor (todos ×100) y Δffr, con 2 retardos (`s1r_lp.py:24,29-35`). El EBP
  y el rendimiento a 2 años de `s1_liq` salen porque no existen antes de 1973–76.
- Los retardos llegan a t−10 (pico supuesto de la respuesta, ver β_ref) y los adelantos a t+12 (horizonte máximo de ȳ).
- Ventana h = 4..12, en vez del h = 0..4 del prerregistro anterior (Desviación del 2026-11-07, punto 4).

**Estimando y su supuesto.** Al controlar por los choques de t+1..t+12, β_C, β_U y β_lin estiman la **respuesta media en h = 4..12
a un choque aislado**, con los choques futuros fijos. Coincide con la respuesta total (la de una LP sin adelantos) solo si los
choques no están autocorrelacionados en la población, y ese es el **supuesto de identificación declarado**. Sin `aum`, la LP de la
ventana 4..12 está sesgada por la autocorrelación muestral de los choques (error de diseño sin ruido de +0,66·β en `s1r_lin` sin
Volcker y +0,83·β en β_U con la muestra completa; f9:30-31). La idea de controlar por los choques intermedios es la de Teulings y
Zubanov (2014, §2.2, pp. 11–13 del WP Tinbergen TI 2010-040/3), que la demuestran para choques independientes y en panel con
efectos fijos (p. 6, E[u_s d_t] = 0): **se cita como idea, no como prueba de que `aum` sea insesgada con choques autocorrelados**.

**Diagnósticos de los choques** (sin la inversión; se publican siempre; tabla `[F13]` en `output/tables/`):
- DL: Ljung-Box(12) de ε en la muestra completa y sin Volcker **[F13]**.
- DP: predictibilidad, F de Wald (HC1) de ε_t sobre 4 retardos de Δlog PIB real, Δlog deflactor y Δffr (12 restricciones), en las
  dos muestras **[F13]**.
- Qué se hace si rechazan (p < 0,05): **no cambia la especificación ni la regla de decisión**, porque cambiarlas por un diagnóstico
  sería elegir la especificación con los datos. El veredicto se refiere al estimando de choque aislado; el paper declara que, en
  esa muestra, no es comparable uno a uno con β_ref (respuesta total) y que la lectura en múltiplos c de β_ref es aproximada; la
  que vale es el MDE en pp de ȳ por pp de choque. Se sabe ex ante que la muestra sin Volcker rechazará probablemente el
  Ljung-Box: F10 obtuvo p = 0,029 y en predictibilidad p = 0,085 (`audits/2026-11-08_F9_mc.md:63-65`), cifras que F13 rehace.
- Además se publican, como en el prerregistro anterior: D1, trimestres por estado; D2, Σ|ε| por estado (con y sin Volcker,
  `SAMPLE_COUNTS_S1R.md`); D3, contraste de balance ε_t ~ D_{t−1} + s_{t−1}.

**Errores estándar.** Newey-West con núcleo de Bartlett y 5 retardos en trimestres naturales, con los residuos HC3 (u_i/(1−h_ii));
t de Student con N − k grados de libertad (`s1_lp.fit(..., hac_weights(q, 5), small_sample=False, leverage=True)`). Cierra la
decisión 5 del 2026-11-07. **Excepción declarada a la banda de `mc.validate`** ([0,92; 0,98], f9:38): con `aum`, la cobertura del
IC al 95 % de los términos que deciden (b_lin, b_C) es 0,948–0,990 en los tres DGP con T (f9:44-45, 52-53, 60-61). Se acepta la
sobrecobertura hasta 0,99 porque es conservadora (cuesta potencia, no tamaño); ninguna de las 7 alternativas probadas por F10 lo
hace mejor (`audits/2026-11-08_F9_mc.md:118-159`). La infracobertura no se aceptaría.

**β_ref (alternativa de referencia).** β_ref = −2,5 × m_W × π_0 = **−1,820 pp de ȳ por pp de ε** (f9:14) **[F13: equivalencia del
h = 0 con la agregación del choque]**.
- −2,5 %: respuesta del modelo lineal de Tenreyro y Thwaites (2016) para los índices de gasto duradero de los hogares y de inversión
  empresarial, ante una subida de 1 pp del fed funds (pp. 11–12 del PDF del WP). Es una sola cifra para los dos agregados y **el
  texto no dice en qué horizonte se lee** (`F12_CITAS_2026-11-08.md:26-33`): esa parte de la comparación no es verificable.
- π_0 = 0,949 (ee 0,248): respuesta del fed funds en h = 0 (ffr_t − ffr_{t−1}) al choque, en la muestra completa (f9:10); sin
  Volcker, 0,943 (f9:12). **La normalización al impacto es la de Tenreyro y Thwaites** («initial 1pp rise», p. 10; «scaled so that
  the shock results in a 1pp increase», p. 11; «on impact», p. 13; choques trimestrales promediados, p. 9).
- m_W = 0,7667: media de min(h/10, 1) en h = 4..12, es decir, una rampa lineal hasta el pico en h = 10 (f9:14). La forma es un
  supuesto de la desk (F4, `output/F4_MC_REPORT.md:67`), centrado en el mínimo del PIB «two to three years after the shock» de
  Tenreyro y Thwaites (p. 10); no es una cifra de su texto.
- c = 1 equivale a 1,92 pp de ȳ por pp de fed funds en el impacto (f9:705).

**Hipótesis** (β < 0: la inversión cae tras una subida y sube tras una bajada):
- **H0** (`s1r_lin`, muestra completa): β_lin < 0. Sale de L_u > 0 con g ≥ 0 y ω ≥ ω_min
  (`theory/check_aggregation.py::test_L_u_positive_with_nonnegative_g_and_w_above_min`).
- **H1** (`s1r_liq` y `s1r_liq_nov`): β_C < 0 en el estado restringido, con subidas y bajadas juntas. Sale de I_u = ω p_f/a +
  (1−ω) g con ω ≥ ω_min > 0 y g ≥ 0 (`theory/check_nesting.py`, `check_aggregation.py`).
  - **Supuesto declarado A-g:** la exposición neta a la repreciación es g ≥ 0. Una refutación refuta "el nido con g ≥ 0".

**Regla de decisión** (α = 0,05; p unilaterales con la t de N − k g.l.; una sola H1, sin Holm). Variante **V3s** (Desviación del
2026-11-08, decisión 5); árbol de `s1r_lp.decide(variant="V3s")`:
1. **Puerta H0.** Si β_lin de `s1r_lin` (muestra completa) no es < 0 con p < 0,05, el resultado es **"H0 no se confirma"**: H1 no
   se interpreta y se escala al Director científico. β̂_C, β̂_U y sus IC se publican igualmente como medición, sin veredicto. H0
   no se exige en la muestra sin Volcker.
2. Si H0 se confirma, se evalúa β_C en `s1r_liq` (muestra completa):
   - si β̂_C < 0 con p < 0,05, pasa al paso 3;
   - si β̂_C > 0 con p < 0,05: **H1 REFUTADA** (regla (a));
   - en otro caso: **NO CONCLUYENTE**.
3. **V3s:** H1 queda **CONFIRMADA** solo si en `s1r_liq_nov` también β̂_C < 0 con p < 0,05. Si no, **NO CONCLUYENTE** ("no se
   sostiene sin Volcker"). Como exige que pasen los dos contrastes, es un contraste de intersección-unión: su tamaño no supera α y
   no necesita corrección por multiplicidad.
- **H1 solo se refuta por la regla (a).** La regla (b) del prerregistro anterior (IC al 90 % dentro de (−0,146·|β̂_U|, +∞)) se
  retira porque con esta precisión no puede activarse con ningún umbral (P = 0 en todos los escenarios, f9:899-958 y
  `audits/2026-11-08_F9_mc.md:182-187`).
- Un NO CONCLUYENTE se presenta siempre con el IC y el MDE de abajo, nunca como ausencia de efecto.
- El resultado de `s1r_liq_nov` se publica siempre, también cuando no decide.

**Potencia y MDE (escritos antes de estimar; árbol V3s completo, con la puerta H0; `aum` y NW5+HC3; ruido homocedástico /
heterocedástico `het_eps`).** Todas dependen de **[F13: equivalencia del h = 0]**.
- Con H1 cierta y β_C = β_U = β_ref (c = 1): P(confirma) = **0,037 / 0,059**; P(H0 no se confirma) = 0,824 / 0,854;
  P(no concluyente) = 0,139 / 0,087; P(refuta) = 0 (f9:727, 799). Es una **medición acotada**: el resultado más probable con un
  efecto del tamaño de β_ref es que H1 no se interprete.
- P(confirma) frente a c, con β_C = β_U = c·β_ref: c = 2: 0,171 / 0,189; c = 3: 0,364 / 0,361; c = 5: 0,745 / 0,778 (f9:886, 894).
- **MDE** (c con P(confirma) = 0,8): **[F13]**. La interpolación de F9 da c ≈ 5,5 / 5,3 (f9:886, 894) y está por encima de c = 5.
  En pp de ȳ por pp de choque, MDE = c_80 × 1,820 **[F13]**; en pp de ȳ por pp de fed funds en el impacto, c_80 × 1,92 **[F13]**.
  Cota inferior, sin la puerta H0: el contraste de H1 sin Volcker por sí solo tiene un MDE de 10,01 / 8,92 pp de ȳ por pp de choque
  (f9:691, 699).
- Tamaño con β = 0: P(confirma) = 0,004 / 0,011 (f9:719, 791).
- Bajo el rival (β_C = 0, β_U = c·β_ref): P(confirma) = 0,014 / 0,014 (c = 1), 0,025 / 0,033 (c = 2), 0,031 / 0,030 (c = 3),
  0,035 / 0,027 (c = 5) (f9:759, 767, 775, 783; 831, 839, 847, 855); c = 4: **[F13]**.

**Robustez prerregistrada** (no decide; se publica con IC sea cual sea el resultado; misma especificación `aum` y mismos errores salvo
lo que se indica):
- `r1r_bs_lin`, `r1r_bs_liq`: réplica con `mps_bs23_orth`, 1988Q1–2005Q2. Descriptiva: con `base`, F9 obtuvo P(confirma) ≈ 0 para
  todo c ≤ 10 (f9:896-897).
- `r1r_from1971q3`: `s1r_liq` sin las filas 1969Q1–1971Q2, cuyos retardos del choque son anteriores a 1969 y cuentan como 0 (F10,
  hallazgo 9).
- `r1r_state_q25`: `s1r_liq` con restringido = cuartil inferior de `s_{t−1}`.
- `r1r_state_logistic`: `s1r_liq` con D_{t−1} sustituido por F(s_{t−1}) logística, γ = 3 fijo y c en la mediana (Tenreyro-Thwaites,
  p. 10 del WP).
- `r1r_lags4`: `s1r_liq` con 4 retardos de los controles.

**Exploratorio** (lista cerrada; todo lo demás también lo es):
- la asimetría (subidas y bajadas por separado);
- las variantes V1 (muestra completa sola) y V2 (H0 y H1 sin Volcker);
- `aumi` (retardos y adelantos del choque interactuados con el estado de su propio trimestre; F10, hallazgo 2);
- β_ref con el fed funds en h = 1 (π_1 = 1,669, f9:11), que da P(confirma) ≈ 0,14–0,27 (F10, `audits/2026-11-08_F9_mc.md:103`);
- la especificación `base` (sin retardos ni adelantos del choque);
- la diferencia entre estados β_C − β_U (si la falta de liquidez amplifica o atenúa);
- la IRF por horizonte;
- la interacción exposición × restricción, la interacción triple, la coordinación y la STAR;
- otras variables de resultado;
- la etapa 1b (tiene su propio MC de puerta, F14) y la etapa 2.

Ids prerregistrados (los lee `tools/research.py`; cualquier otra especificación solo puede registrarse como exploratoria):
```prereg
# --- confirmatorias (deciden; árbol V3s) ---
s1r_lin
s1r_liq
s1r_liq_nov
# --- robustez prerregistrada (no deciden) ---
r1r_bs_lin
r1r_bs_liq
r1r_from1971q3
r1r_state_q25
r1r_state_logistic
r1r_lags4
```

prereg_commit: [sha] (aprobación de los autores, [fecha]). Lo que va de `## Prerregistro` a este bloque está congelado: cambiarlo
exige una Desviación con su huella (`tools/integrity.py`, check `prereg`).

**Replicación cruzada:** `s1r_lin`, `s1r_liq` y `s1r_liq_nov` en R (`code/replication_r/`), con NW5+HC3 en trimestres naturales y
paridad `estimates_py.csv` = `estimates_r.csv`.

**Requisito previo a estimar:**
- F13 entregado y sus cifras sustituyen a las marcas `[F13]` antes de la aprobación;
- `s1r_lp.h1_verdict` sin la rama (b) en `s1r` y los ids `r1r_*` implementados, sin mirar la inversión.

---

# Parte 2 · Por qué estos ids

- **`s1r_lin`, `s1r_liq`**: los del encargo; H0 y H1 con la muestra completa.
- **`s1r_liq_nov`** (confirmatoria): V3s decide con la estimación sin Volcker, así que tiene que estar prerregistrada. Va con id propio
  porque la paridad Python–R y `estimates_*.csv` usan la clave (`spec_id`, `term`) (`tools/integrity.py:203`): con el mismo id, las
  dos muestras chocarían. No hay `s1r_lin_nov`, porque H0 no se exige sin Volcker (decisión 5); esa estimación es parte de V2,
  que es exploratoria.
- **Robustez.** Solo entra lo que cumple dos condiciones: (i) se puede hacer con los datos de `stage1r_us.parquet` y los brutos de FRED;
  (ii) responde a una amenaza concreta de este diseño.
  - `r1r_bs_*`: la réplica posterior a 1984 que pide la Desviación del 2026-11-07 (punto 2).
  - `r1r_from1971q3`: los ceros de los retardos (F10, hallazgo 9).
  - `r1r_state_q25` y `r1r_state_logistic`: la mediana es una elección arbitraria del umbral, y estas dos ya estaban aprobadas por los
    autores el 2026-11-04.
  - `r1r_lags4`: lo poco que dejan los controles (2 retardos).
- **Fuera, por ser específicos de la muestra de 1988+ o no tener datos antes de 1985:** `r_dsr` (DSR desde 1999),
  `r_liq_narrow_assets` y `r_inv_nfc` (desde 1985 en el panel), `r_zlb_in` y `r_covid_in` (no hay ZLB ni COVID en 1969–2005),
  `r_bs25me`, `r_bs23orth_1994` y `r_bs23raw` (variantes de BS, que ya solo es réplica descriptiva).
- **Fuera por otro motivo:** `r_ctrl_interact` pasa a exploratorio junto con `aumi`, que es su versión pertinente aquí; `r_balance_ctrl`
  se sustituye por D3, que se publica siempre.

# Parte 3 · Cifras que dependen de F13

| # | Dónde (parte 1) | Qué falta | Encargo F13, punto |
|---|---|---|---|
| 1 | Muestra (choque), β_ref, potencia y MDE | Que β_ref y la potencia no cambien al agregar el choque por promedio en vez de por suma. Ojo: 1969Q1 solo tiene marzo (`DICTIONARY.md:121,129`), así que suma y promedio no difieren solo en un factor 3 en esa fila | 1 |
| 2 | Potencia y MDE | MDE simulado de V3s (c_80), en c·β_ref, en pp de ȳ por pp de choque y en pp de fed funds | 2 |
| 3 | Potencia y MDE (rival) | P(confirma) de V3s bajo el rival con c = 4 | 2 |
| 4 | Diagnósticos DL y DP | Ljung-Box(12) y predictibilidad, muestra completa y sin Volcker, en una tabla de `output/tables/` | 3 |
| 5 | Muestra (choque) | Si el punto 1 falla de forma material, decisión de los autores sobre la agregación antes de aprobar | 1 (condición de parada) |

Aviso para F13: con P(confirma) = 0,745 / 0,778 en c = 5 (f9:886, 894), el c_80 de V3s queda entre 5 y 7. Simular c = 4 no lo acota;
para el MDE hace falta simular por encima de c = 5.

---

## HANDOFF

**Hecho.** La parte 1 es el texto completo que sustituye a "## Prerregistro de la etapa 1" (`SPEC.md:49-129`): pregunta, muestra,
estado, especificación `aum`, estimando y diagnósticos, errores estándar con la excepción, hipótesis y regla V3s, β_ref con fuente y
página, potencia y MDE ex ante, robustez y exploratorio. El bloque ```prereg``` lleva 3 ids confirmatorios y 6 de robustez, y la
parte 2 los justifica. La parte 3 lista las cifras `[F13]`. No he tocado la SPEC ni el código.

**Evidencia.**
- Las 7 decisiones (`SPEC.md:187-199`) aparecen en la parte 1:
  - 1, V3s con `aum`: Especificación y Regla de decisión;
  - 2, β_ref en h = 0 y MDE también en pp por pp: β_ref, y Potencia y MDE;
  - 3, choque aislado, diagnósticos y TZ como idea: Estimando y Diagnósticos;
  - 4, NW5+HC3 con la excepción: Errores estándar;
  - 5, V3s con H0 solo en la muestra completa: Regla de decisión, pasos 1 y 3;
  - 6, refutación solo por (a): Regla de decisión;
  - 7, puerta H0: Regla de decisión, paso 1.
- Cifras: `output/tables/f9_power.md` (líneas 6-7, 10-14, 17, 30-31, 38, 44-45, 52-53, 60-61, 691, 699, 705, 719, 727, 759-783,
  791, 799, 831-855, 886, 894, 896-897); `data/clean/SAMPLE_COUNTS_S1R.md:11-19`.
- Citas con página: Tenreyro-Thwaites pp. 9, 10, 11–12, 13 y Teulings-Zubanov pp. 6, 11–13, las dos del PDF del WP (F12,
  `exploration/F12_CITAS_2026-11-08.md:16-33,47-60`); la de γ = 3 la comprobé en `kb/library/md/TenreyroThwaites2016.md` (p. 10).
- Estimador y árbol: `code/analysis/s1r_lp.py:44-54,75-88`; errores: `code/analysis/s1_lp.py:61-65`.

**Decisiones y quién las tomó.**
- Autores: las 7 de la Desviación del 2026-11-08 y las del 2026-11-07.
- Director, para escribirlas sin ambigüedad y pendientes de aprobación:
  - el id `s1r_liq_nov`;
  - los 6 ids de robustez y los que salen;
  - la regla "si los diagnósticos rechazan, no cambia nada salvo la lectura";
  - leer V3s como un contraste de intersección-unión, sin corrección;
  - conservar D1–D3 y retirar D4 (era la estabilidad de la mediana sin 1988–93, de la muestra antigua);
  - pasar `base` a exploratoria.

**Supuestos y límites.**
- Algunas cifras citadas en el texto no están en `output/tables/` sino en la réplica del Referee: el Ljung-Box y la predictibilidad
  (`audits/2026-11-08_F9_mc.md:63-65`, que rehace F13) y la potencia con h = 1 (`:103`, exploratoria). Las cito con su ruta.
- La rampa hasta h = 10 es un supuesto de la desk, no de TT.
- El horizonte del −2,5 % de TT no es verificable con el texto (F12).

**Preguntas para los autores (no las he resuelto).**
1. **Controles.** Las 7 decisiones no fijan los controles. Escribo los que se simularon y auditaron (Δlog inversión, Δlog PIB,
   Δlog deflactor y Δffr, con 2 retardos). Salen el EBP y el rendimiento a 2 años de `s1_liq`, que F9 propuso quitar
   (F9_MC_REPORT §1). ¿Lo aprobáis?
2. **Qué se hace si fallan los diagnósticos.** La decisión 3 pide declararlos, pero no dice qué pasa si rechazan, y se sabe ex ante
   que el Ljung-Box sin Volcker probablemente rechaza (p = 0,029 en F10). Propongo no cambiar ni la especificación ni el veredicto:
   solo se matiza la comparación con β_ref. ¿Lo aprobáis, o preferís otra consecuencia?
3. **Refutación en V3s.** La decisión 5 define cuándo se confirma. No dice si (a) se evalúa solo con la muestra completa. He escrito
   lo que se simuló (`s1r_lp.decide`): refuta (a) con la muestra completa. Si la completa confirma y la de sin Volcker da β̂_C > 0
   significativo, sale "no concluyente". ¿Lo confirmáis?
4. **Réplica BS con `aum`.** F9 solo simuló BS con `base`, que tiene un error de diseño del −67 % (f9:34). Con `aum` y N = 70
   quedan unos 36 g.l. y no hay MC. Como es descriptiva y no decide, la escribo con `aum` por coherencia. Alternativa: dejarla
   exploratoria.

**Descartado y por qué.**
- Un id por variante (V1/V2) en el bloque: son exploratorias.
- `s1r_lin_nov` como confirmatoria: H0 no se exige sin Volcker.
- Robustez que no tiene datos antes de 1985 o que es propia de la muestra de 1988+ (parte 2).
- Dar un MDE interpolado como definitivo: F10 pide el simulado.

**Pendiente.**
- F13: cifras 1–5 de la parte 3, y el aviso de que c = 4 no acota el c_80 de V3s.
- Coordinación, tras la aprobación:
  - pegar la parte 1 en la SPEC, sin `## ` intermedios;
  - añadir la Desviación con `prereg <hash>` y el `prereg_commit` nuevo;
  - pedir a Econometría que retire la rama (b) de `h1_verdict` para `s1r` e implemente los `r1r_*`.
