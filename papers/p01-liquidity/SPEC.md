# p01-liquidity — SPEC

Estado: **Diseño F; etapa 1 rediseñada por los autores (2026-11-07) para ganar potencia** (Romer-Romer, h = 4..12, tres
variantes de Volcker; ver Desviaciones). Datos (F7) y citas (F8) hechos; **en curso: F9**, Monte Carlo de `s1r_*`
(Econometría). Después, F10 (auditoría del Referee) y F11 (prerregistro nuevo, que aprueban los autores), **antes** de
estimar con la inversión.

## Intuición de partida (de los autores)
Hay una serie de factores que afectan a la liquidez, con **regímenes no lineales**: el mismo impulso
tiene efectos distintos según la situación de la economía. v22 fue un intento de formalizarlo
(tres canales multiplicativos), pero no funcionó por:
- pocos datos para demasiados parámetros;
- endogeneidad generalizada;
- causalidades cruzadas.

## Principio de la Fase 0
**No partimos de una estructura predefinida**, tampoco de la de v22. Partimos de todo lo disponible:
- la literatura de los autores;
- las propuestas descartadas;
- v22 y su diagnóstico.

A partir de ahí se elige el diseño con **mejor ajuste al problema, más prometedor y más ambicioso**,
con una evaluación explícita.

## Entradas
- `prior/`: v22 y su diagnóstico.
- `exploration/discarded/`: una ficha por cada propuesta descartada (idea, por qué se descartó, qué es salvable).
- `kb/topics/<topic>/papers/`: fichas de la literatura de los autores.
- `exploration/candidates/`: diseños candidatos. El candidato B ya existe y se evalúa como uno más.

## Rúbrica de evaluación (cada criterio de 1 a 5, con justificación escrita)

| Criterio | Pregunta |
|---|---|
| **Ajuste a la intuición** | ¿Captura varios factores y regímenes no lineales sin imponer la forma de antemano? |
| **Ambición / contribución** | ¿Qué sabría el campo después que hoy no sabe? ¿En qué revista encaja? |
| **Identificación** | ¿Qué variación identifica el resultado principal? ¿Resiste la endogeneidad y las causalidades cruzadas? |
| **Datos / potencia** | ¿Cuántas observaciones frente a parámetros? ¿Existen los datos gratis? Monte Carlo rápido de potencia |
| **Riesgo** | ¿Qué tiene que salir bien? ¿Hay un paper publicable aunque el resultado sea negativo? |
| **Coste** | Semanas de trabajo de las desks hasta el primer resultado |

Una puntuación alta en ambición no compensa una identificación de 1 o 2.

## Decisión
La toman **los autores**, a partir del informe de la Fase 0 (`exploration/REPORT.md`). Después, esta
SPEC se reescribe con la pregunta, las hipótesis prerregistradas y la identificación del diseño
elegido. La plantilla está en `papers/_template/SPEC.md`.

## Prerregistro de la etapa 1 rediseñada: EE. UU. (`s1r_*`; aprobado por los autores el 2026-11-08)

Sustituye al prerregistro de la etapa 1 aprobado el 2026-11-04 (`prereg_commit: af1c346`), cuyos ids `s1_*` y `r_*` no se
estiman (Desviación del 2026-11-07). Decisiones de los autores: Desviaciones del 2026-11-07 y del 2026-11-08; justificación en
`exploration/DECISIONES_AUTORES_F11_2026-11-08.md` y `exploration/PREREG_S1R_DRAFT.md`. El MC que respalda este diseño es F9
(`output/F9_MC_REPORT.md`, tablas `output/tables/f9_power.md`), auditado en F10 (`audits/2026-11-08_F9_mc.md`, APROBADO CON
CAMBIOS), con las comprobaciones de F13 (`output/F13_COMPROBACIONES.md`). Nada de esto ha usado la respuesta de la inversión.
Citas de cifras: `f9:<línea>` = `output/tables/f9_power.md`, `f13:<línea>` = `output/tables/f13_checks.md`, `f13d:<línea>` =
`output/tables/f13_shock_diagnostics.md`.

**Pregunta.** ¿Se transmite un choque monetario a la inversión no residencial de EE. UU. cuando la liquidez de las empresas no
financieras está por debajo de su tendencia, como predice el margen interior de reservas (ω ≥ ω_min > 0)? Se mide como la
respuesta media en h = 4..12 trimestres, con subidas y bajadas juntas (la asimetría es exploratoria).

**Muestra y datos.**
- Choque principal: `rr_shock` (Romer-Romer, extensión de Coibion reestimada por Wieland, `resid_full`). **ε_t es la suma de los
  choques mensuales de los 3 meses del trimestre** (`data/clean/DICTIONARY.md:121,128`); su unidad es el pp de fed funds sumado
  en el trimestre, y en esa unidad se dan β_ref y el MDE "por pp de choque". Todos los trimestres tienen sus 3 meses, así que el
  promedio de Tenreyro y Thwaites sería ε/3: β_ref y la potencia frente a β_ref **no dependen de sumar o promediar** (los t
  difieren como mucho en 1,3·10⁻¹² y los veredictos de V3s son idénticos; f13:16-21). Solo el MDE por pp de choque se
  multiplicaría por 3 con el promedio; el MDE por pp de fed funds no cambia (f13:23).
- t ∈ 1969Q1–2005Q2 (`in_rr_sample`; el último t con t + 12 ≤ 2008Q2): N = 146, 73 trimestres en el estado restringido y 73 en el
  holgado (f9:6; `data/clean/SAMPLE_COUNTS_S1R.md:11-12`).
- Muestra sin Volcker: la anterior sin las filas t ∈ 1979Q4–1982Q4 (13 trimestres). N = 133, con 62 y 71 por estado (f9:7;
  `SAMPLE_COUNTS_S1R.md:18-19`). Solo se quitan filas: el estado, los adelantos y retardos del choque y ȳ_t de las demás filas
  se calculan con la serie completa, como en el MC (`code/analysis/s1r_lp.py:44-54`).
- Réplica con `mps_bs23_orth`: t ∈ 1988Q1–2005Q2, N = 70 (f9:17). Exploratoria: no decide ni es robustez prerregistrada (ver abajo).
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

**Diagnósticos de los choques** (sin la inversión; se publican siempre; tabla `output/tables/f13_shock_diagnostics.md`, generada por
`code/mc/f13_checks.py`):
- DL: Ljung-Box(12) de ε. Muestra completa: 16,78, p = 0,158; sin Volcker: 22,86, p = 0,029 (f13d:7-8).
- DP: predictibilidad, F de Wald (HC1) de las 12 pendientes de ε_t sobre una constante y 4 retardos de 100·Δlog PIB real,
  100·Δlog deflactor y Δffr (f13d:3). Muestra completa: F(12, 133) = 1,07, p = 0,391; sin Volcker: F(12, 120) = 1,66, p = 0,085
  (f13d:7-8).
- Qué se hace si rechazan (p < 0,05): **no cambia la especificación ni la regla de decisión**, porque cambiarlas por un diagnóstico
  sería elegir la especificación con los datos. El veredicto se refiere al estimando de choque aislado; el paper declara que, en
  esa muestra, no es comparable uno a uno con β_ref (respuesta total) y que la lectura en múltiplos c de β_ref es aproximada; la
  que vale es el MDE en pp de ȳ por pp de choque. Se sabe antes de estimar, y sin mirar la inversión, que la muestra sin Volcker
  rechaza el Ljung-Box (p = 0,029) y que la predictibilidad no rechaza al 5 % en ninguna muestra (f13d:7-8): la salvedad se
  aplica a `s1r_liq_nov`.
- Además se publican, como en el prerregistro anterior: D1, trimestres por estado; D2, Σ|ε| por estado (con y sin Volcker,
  `SAMPLE_COUNTS_S1R.md`); D3, contraste de balance ε_t ~ D_{t−1} + s_{t−1}.

**Errores estándar.** Newey-West con núcleo de Bartlett y 5 retardos en trimestres naturales, con los residuos HC3 (u_i/(1−h_ii));
t de Student con N − k grados de libertad (`s1_lp.fit(..., hac_weights(q, 5), small_sample=False, leverage=True)`). Cierra la
decisión 5 del 2026-11-07. **Excepción declarada a la banda de `mc.validate`** ([0,92; 0,98], f9:38): con `aum`, la cobertura del
IC al 95 % de los términos que deciden (b_lin, b_C) es 0,948–0,990 en los tres DGP con T (f9:44-45, 52-53, 60-61). Se acepta la
sobrecobertura hasta 0,99 porque es conservadora (cuesta potencia, no tamaño); ninguna de las 7 alternativas probadas por F10 lo
hace mejor (`audits/2026-11-08_F9_mc.md:118-159`). La infracobertura no se aceptaría.

**β_ref (alternativa de referencia).** β_ref = −2,5 × m_W × π_0 = **−1,820 pp de ȳ por pp de ε** (ε sumado; f9:14, f13:9). Con
el choque promediado sería −5,459, exactamente ×3, con el mismo efecto de 1 desv. típ. de ε (−1,092 pp; f13:9-12).
- −2,5 %: respuesta del modelo lineal de Tenreyro y Thwaites (2016) para los índices de gasto duradero de los hogares y de inversión
  empresarial, ante una subida de 1 pp del fed funds (pp. 11–12 del PDF del WP). Es una sola cifra para los dos agregados y **el
  texto no dice en qué horizonte se lee** (`F12_CITAS_2026-11-08.md:26-33`): esa parte de la comparación no es verificable.
- π_0 = 0,949 (ee 0,248): respuesta del fed funds en h = 0 (ffr_t − ffr_{t−1}) al choque, en la muestra completa (f9:10); sin
  Volcker, 0,943 (f9:12). **La normalización al impacto es la de Tenreyro y Thwaites** («initial 1pp rise», p. 10; «scaled so that
  the shock results in a 1pp increase», p. 11; «on impact», p. 13; choques trimestrales promediados, p. 9).
- m_W = 0,7667: media de min(h/10, 1) en h = 4..12, es decir, una rampa lineal hasta el pico en h = 10 (f9:14). La forma es un
  supuesto de la desk (F4, `output/F4_MC_REPORT.md:67`), centrado en el mínimo del PIB «two to three years after the shock» de
  Tenreyro y Thwaites (p. 10); no es una cifra de su texto.
- c = 1 equivale a 2,5 × m_W = 1,917 pp de ȳ por pp de fed funds en el impacto (f13:23).

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
heterocedástico `het_eps`; 1000 réplicas, error MC de P ≈ ±0,013).** No dependen de sumar o promediar el choque (f13:9-21).
- Con H1 cierta y β_C = β_U = β_ref (c = 1): P(confirma) = **0,037 / 0,059**; P(H0 no se confirma) = 0,824 / 0,854;
  P(no concluyente) = 0,139 / 0,087; P(refuta) = 0 (f13:31, 47). Es una **medición acotada**: el resultado más probable con un
  efecto del tamaño de β_ref es que H1 no se interprete.
- P(confirma) frente a c, con β_C = β_U = c·β_ref: c = 2: 0,171 / 0,189; c = 3: 0,364 / 0,361; c = 4: 0,590 / 0,600;
  c = 5: 0,745 / 0,778; c = 5,5: 0,797 / 0,840; c = 6: 0,871 / 0,882 (f13:32-37, 48-53).
- **MDE** (c con P(confirma) = 0,8, interpolación lineal en la rejilla simulada): **c = 5,5 / 5,2**, es decir, **10,01 / 9,46 pp de
  ȳ por pp de choque** (ε sumado) y 10,54 / 9,97 pp de ȳ por pp de fed funds en el impacto (f13:68-69). Unos 10 pp de ȳ por pp de
  choque en los dos DGP. Con el choque promediado, el MDE por pp de choque sería ×3; el de pp de fed funds no cambia (f13:23).
- Tamaño con β = 0: P(confirma) = 0,004 / 0,011 (f9:719, 791).
- Bajo el rival (β_C = 0, β_U = c·β_ref): P(confirma) **≤ 0,035 en toda la rejilla hasta c = 7** (máximo 0,035 / 0,033; f13:39-46,
  55-62), por debajo de α.

**Robustez prerregistrada** (no decide; se publica con IC sea cual sea el resultado; misma especificación `aum` y mismos errores salvo
lo que se indica):
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
- la réplica con `mps_bs23_orth` (1988Q1–2005Q2, con `aum`): sin MC que la valide con N = 70 y ≈ 36 g.l. (con `base`, F9 obtuvo
  P(confirma) ≈ 0 para todo c ≤ 10, f9:896-897), así que se publica como descriptiva y exploratoria;
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
r1r_from1971q3
r1r_state_q25
r1r_state_logistic
r1r_lags4
```

prereg_commit: 3d6b508 (aprobación de los autores, 2026-11-08). Lo que va de `## Prerregistro` a este bloque está congelado: cambiarlo
exige una Desviación con su huella (`tools/integrity.py`, check `prereg`).

**Replicación cruzada:** `s1r_lin`, `s1r_liq` y `s1r_liq_nov` en R (`code/replication_r/`), con NW5+HC3 en trimestres naturales y
paridad `estimates_py.csv` = `estimates_r.csv`.

**Requisito previo a estimar:** `s1r_lp.h1_verdict` sin la rama (b) en `s1r` y los ids `r1r_*` implementados, sin mirar la
inversión.

## Desviaciones
- 2026-11-04 · El borrador inicial (candidato B) se retira como SPEC y pasa a `exploration/candidates/`
  por decisión de los autores: primero se revisa todo el material.
- 2026-11-04 · **Los autores aprueban el diseño F** (`exploration/DEVILS_ADVOCATE_2026-11-04.md` §4–5), propuesto
  en común por el Director científico y la Coordinación. La Fase 0 se cierra sin el `REPORT.md` previsto: el informe
  del abogado del diablo puntúa con la rúbrica el planteamiento de `FIRST_PRINCIPLES.md` y 5 alternativas.
  - **Contribución:** el margen interior de reservas y el cierre bancario común entre los extremos de IOPO
    (2018) y Perez-Orive et al. (2026).
  - **Empírica en dos etapas:**
    1. EE. UU. con Bauer-Swanson, un solo estado (liquidez o servicio de la deuda) y subidas y bajadas separadas.
    2. Panel de la zona euro, solo si pasa la puerta: datos por país en el MANIFEST, exposición contractual × stock,
       potencia ≥ 0,8 por Monte Carlo con 10–12 clústeres y sin ZLB, y placebo con el choque de información de JK.
  - La interacción triple es exploratoria.
  - **Prerregistro:** el signo esperado se fija ex ante. Las predicciones 6.6(2, segunda mitad) y 6.6(4) de
    `FIRST_PRINCIPLES.md` quedan fuera hasta que se deriven.
  - **Motivo:** el planteamiento anterior tenía identificación 2 y afirmaciones refutadas (cota del 3 %, novedad
    de TFG1 ⊂ TFG2, diferencias con IOPO y Perez-Orive).
- 2026-11-04 · **Los autores aprueban el prerregistro de la etapa 1** sobre el borrador `exploration/PREREG_DRAFT.md`, con cuatro decisiones:
  1. **Choque principal `mps_bs23_orth`**, con `mps_bs25_me` como robustez desde 1994. La serie con discursos no está publicada (Datos lo comprobó).
  2. **E1** (amplifica o atenúa) **queda exploratoria**: la teoría no fija su signo, y la medida de exposición disponible (E.2 STBL,
     préstamos nuevos 1997–2017) cubre solo 53 de las 102 observaciones.
  3. **Umbral de refutación: 0,146 = ω_min de TFG2**, no un 10 % fijo.
  4. **El estado DSR pasa de secundario confirmatorio a robustez (`r_dsr`)**, porque sus celdas tienen 11–18 observaciones. Por eso
     desaparece `s1_dsr` del borrador.
- 2026-11-07 · **Los autores deciden rediseñar la etapa 1** sobre la propuesta del Director científico
  (`exploration/REDESIGN_POWER_2026-11-04.md`) y la auditoría R-F4 (`audits/2026-11-05_F4_mc.md`, APROBADO CON CAMBIOS).
  Resumen de la decisión en `exploration/DECISIONES_AUTORES_2026-11-07.md`. Aceptan las 7 recomendaciones:
  1. **`s1_liq` no se estima tal como está**: frente a β_ref su potencia ≈ tamaño (F4), y con la condición de H0 el 92 % de
     los resultados serían "H1 no se interpreta" (R-F4).
  2. **Romer-Romer pasa a ser el choque principal** (sustituye a la decisión 1 del 2026-11-04); `mps_bs23_orth` queda como
     réplica posterior a 1984. La robustez sin 1979Q4–1982Q4 es obligatoria.
  3. **H1 con subidas y bajadas juntas**; la asimetría pasa a exploratoria. Revierte en parte el diseño F ("subidas y bajadas
     separadas") porque separarlas no tiene potencia en ningún diseño agregado de EE. UU.
  4. **Estadístico: media de h = 4..12**, en vez de h = 0..4.
  5. **Errores estándar: la Desviación de F4 (NW(5) con residuos HC3) no se registra todavía.** Primero el MC nuevo la valida
     también con ruido heterocedástico ligado a los trimestres de alto apalancamiento; se registra con ese resultado, y si no
     pasa se elige otro error antes de estimar. (Postura de la Coordinación; el Director proponía registrarla ya.)
  6. **Se abre la etapa 1b transversal** (gradiente de exposición ∂I_u/∂g = 1 − ω > 0, panel con efectos fijos de tiempo),
     condicionada a datos (G ≥ 40) y a un MC con potencia ≥ 0,8. **Los autores no tienen acceso a WRDS** (confirmado el
     2026-11-07): la etapa 1b depende de una fuente gratuita (QFR del Census u otra), que busca Datos en F7.
  7. **Se acepta prerregistrar una H1 con potencia esperada ≈ 0,2–0,4**, como medición acotada, con el MDE escrito ex ante,
     las probabilidades de veredicto calculadas con la condición de H0 y el umbral de refutación (b) revisado para que no
     dependa de un β̂_U ruidoso.
  - **Qué no cambia todavía:** el bloque ```prereg``` y su texto congelado (`prereg_commit: af1c346`). El prerregistro nuevo
    (`s1r_*`) se escribe con los resultados del MC nuevo y antes de ver la respuesta de la inversión; al cambiar el texto
    congelado, su Desviación llevará la huella `prereg <hash>` y un `prereg_commit` nuevo cuando lo aprueben los autores.
- 2026-11-07 · **Volcker en la etapa 1 rediseñada (aviso de F7).** 11 de los 13 trimestres de 1979Q4–1982Q4 caen en el estado
  restringido (59 % de Σ|ε| con Volcker; equilibrado sin él, `data/clean/SAMPLE_COUNTS_S1R.md`). Los autores deciden que el
  MC de F9 compare tres variantes y que la principal se elija en el prerregistro nuevo (F11), antes de ver la respuesta de la
  inversión: (V1) muestra completa con la robustez sin Volcker como comprobación; (V2) principal sin Volcker; (V3) muestra
  completa, y H1 solo se confirma si también se sostiene sin Volcker. El estado sigue definido como en el prerregistro
  (mediana de `s_{t−1}` en la muestra completa de cada choque); quitar Volcker no lo redefine.
- 2026-11-08 · **Los autores fijan el diseño del prerregistro nuevo de la etapa 1 (`s1r_*`)** sobre el MC de F9
  (`output/F9_MC_REPORT.md`), su auditoría F10 (`audits/2026-11-08_F9_mc.md`, APROBADO CON CAMBIOS) y F12
  (`exploration/F12_CITAS_2026-11-08.md`). Resumen en `exploration/DECISIONES_AUTORES_F11_2026-11-08.md`. Camino **A**: se
  prerregistra la H1 agregada como medición acotada y se abre en paralelo un MC de puerta para la etapa 1b. Decisiones:
  1. **Variante V3s con la especificación `aum`** (choques de t−10 a t+12 como controles). V1 con `aum` queda descartada:
     confirma en falso un 10–14 % frente al rival (F10).
  2. **β_ref con la respuesta del fed funds al impacto (h = 0)**, como normalizan Tenreyro-Thwaites (pp. 10–11, 13; F12). La
     potencia que se escribe ex ante es la de h = 0 (≈ 0,04–0,10 frente a β_ref); el MDE se escribe también en pp de ȳ por pp
     de choque.
  3. **El estimando es la respuesta a un choque aislado**; la SPEC declara el supuesto de choques sin autocorrelación en la
     población y los diagnósticos (Ljung-Box y predictibilidad de los choques). Teulings-Zubanov se cita como idea, no como
     prueba de insesgadez.
  4. **Errores estándar: NW(5) con residuos HC3 sobre `aum`**, con la sobrecobertura declarada como excepción a la banda. Cierra
     la decisión 5 del 2026-11-07, que esperaba a esta validación (cubre 0,948–0,990 también con heterocedasticidad).
  5. **V3s:** H1 se confirma con la muestra completa y también sin 1979Q4–1982Q4; H0 se exige solo con la muestra completa.
  6. **H1 solo se refuta por la regla (a)**; la (b) se retira porque no puede activarse con esta precisión.
  7. **Se mantiene la puerta H0.**
  - El bloque ```prereg``` y su texto congelado no cambian hasta que los autores aprueben el borrador de F11; entonces la
    Desviación llevará la huella `prereg <hash>` y un `prereg_commit` nuevo.
- 2026-11-08 · **Los autores aprueban el prerregistro nuevo de la etapa 1 (`s1r_*`)**, sobre el borrador del Director científico
  (`exploration/PREREG_S1R_DRAFT.md`, F11) con las cifras de F13, y sustituye a la sección "Prerregistro de la etapa 1" del
  2026-11-04. Aplica las decisiones del 2026-11-07 y del 2026-11-08 y responde a las cuatro preguntas abiertas del borrador:
  1. **Controles:** los que se simularon y auditaron (Δlog inversión, Δlog PIB, Δlog deflactor y Δffr, con 2 retardos); salen el
     EBP y el rendimiento a 2 años de `s1_liq`.
  2. **Si los diagnósticos de los choques rechazan** (se sabe ex ante que el Ljung-Box sin Volcker da p = 0,029): no cambian la
     especificación ni el veredicto; solo se matiza la comparación con β_ref.
  3. **La refutación (a) se evalúa solo con la muestra completa**; si la completa confirma y sin Volcker β̂_C > 0 es
     significativo, el resultado es "no concluyente".
  4. **La réplica con `mps_bs23_orth` pasa a exploratoria** (sin MC que la valide con N = 70); `r1r_bs_lin` y `r1r_bs_liq` salen
     del bloque.
  - Los ids `s1_*` y `r_*` de la etapa 1 anterior salen del bloque: no se estimarán.
  - Huella del texto congelado nuevo: prereg 1d9476332d29. El `prereg_commit` pasa al commit de esta aprobación.
- 2026-11-08 · **Los autores deciden cómo sigue p01 tras `h0_falla`** (F16, auditada en F17: APROBADO), sobre las opciones del
  Director científico (`exploration/F18_TRAS_H0_2026-11-08.md`):
  1. **El paper es la opción A:** la teoría verificada más la medición prerregistrada y auditada de la etapa 1, presentada como
     medición acotada con la potencia declarada ex ante. H1 no se interpreta; las 6 filas de b_C se muestran todas, con su p
     unilateral y su IC, como "medición sin veredicto" (las dos que no pasan incluidas).
  2. **Se abre en paralelo solo la puerta de la etapa 2** (zona euro, F5), tal como se aprobó el 2026-11-04 y sin mirar
     resultados. Si pasa, la etapa 2 se prerregistra y entra en una versión 2 del paper; si no, el paper A queda como está.
  3. **La etapa 1b se cierra como "no pasa la puerta"** (F14a: G = 28–32 frente a 40, proxy sin cita verificada, sin capex). La
     puerta no se relaja: hacerlo sabiendo el resultado sería elegirla con el resultado delante.
  4. La opción B (repetir H1 en otros países) se descarta: se plantearía después de ver β̂_C. Se retiran F14b, F19 y F20.
