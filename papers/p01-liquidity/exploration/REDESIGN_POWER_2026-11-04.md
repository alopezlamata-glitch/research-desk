# p01 · Rediseño de la etapa 1 para ganar potencia — propuesta del Director científico a los autores

Encargos: `desks/direccion-cientifica/ENCARGO_2026-11-04_rediseno-potencia.md` y su continuación del 2026-11-05.
Entrada: F4 (`output/F4_MC_REPORT.md`, `output/tables/f4_power.md`). Cuentas: `exploration/redesign_power_calc.py`, que escribe
`exploration/redesign_power_tables.md` (en adelante **[T§n]**). Se reproduce con
`uv run python -I papers/p01-liquidity/exploration/redesign_power_calc.py` (segundos).

**Regla dura cumplida.** No se ha mirado la respuesta de la inversión (ni de ninguna variable de resultado) a ningún choque. De las
variables de resultado solo entra su ruido univariante (AR(2) sin choques, como en F4). De los choques solo entra su varianza y su
primera etapa sobre el **fed funds**. La muestra sigue intacta.

**Páginas.** Son las del marcador `<!-- p. N -->` de `kb/library/md/` (página del PDF del documento de trabajo; ver la advertencia de
`exploration/CITAS_DISENO_F_2026-11-04.md`). BS = Bauer-Swanson, NBER w29939. TT = Tenreyro-Thwaites (2016). Jeenas = WP UPF 1872.
Lo que no tiene página está marcado **[criterio propio]** o **[pendiente de Literatura]**.

---

## 0. Resumen (una página)

1. **La falta de potencia es de información, no de estimador.** Con el DGP de F4 conocido (un oráculo que sabe la dinámica), el
   efecto mínimo detectable de cada celda de `s1_liq` sigue siendo 21–40 veces β_ref [T§1]. La LP de F4 solo pierde ×1,2–1,4
   frente a ese oráculo. **Ningún estimador con el mismo choque y la misma muestra (VAR, proxy-SVAR, LP suavizada, bayesiano) puede
   cerrar un hueco de ×20–40**: como mucho recupera ese ×1,2–1,4.
2. **La causa es el choque.** `mps_bs23_orth` (solo FOMC) tiene una primera etapa sobre Δffr con **F = 4,2** en nuestra muestra
   [T§2]. Es el mismo problema que BS documentan para esta serie (F = 2,44 en su SVAR, "weakness of the instrument may be a serious
   concern", BS p. 41) y que resuelven añadiendo discursos (F = 10,23, BS pp. 42–43), una serie que **no está publicada** (Desviación
   2026-11-04, decisión 1). Un choque de 1 desviación típica mueve ȳ 0,067 pp, frente a un ruido de κσ_e = 2,53 pp: R² = 0,0007 [T§1].
3. **Lo único que mueve la aguja es más varianza del choque en unidades de fed funds** [T§2]: Romer-Romer 1969–2007 da ×5,1 en el
   estadístico t (×3,2 sin Volcker). Combinado con una ventana de horizontes h = 4..12 (×1,34, [T§6]), el MDE de H1 con signos
   juntos baja de c ≈ 12–14 a **c ≈ 2,6–3,0** [T§7]. **Sigue sin haber potencia 0,8 con β_ref** (0,21–0,25), pero el resultado pasa
   de inútil a informativo para efectos ≥ 3·β_ref.
4. **Separar subidas y bajadas por estado no es viable en ningún diseño agregado de EE. UU.** (potencia ≤ 0,21 con β_ref incluso con
   la innovación recursiva, que no es un choque limpio [T§7]).
5. **La vía con potencia real es transversal** (familia b): con efectos fijos de tiempo el ruido agregado desaparece. No identifica
   el nivel de H1, pero sí una predicción **con signo fijado por la teoría verificada**: el gradiente de exposición
   ∂I_u/∂g = 1 − ω > 0 (`theory/check_nesting.py::test_dI_dg_is_one_minus_w_and_its_sign`). Depende de datos que aún no tenemos.
6. **Recomendación [criterio propio]:** (i) no estimar `s1_liq` tal como está; (ii) prerregistrar de nuevo la etapa 1 con
   Romer-Romer como choque principal, ventana h = 4..12, H1 con signos juntos y la potencia esperada escrita ex ante; (iii) bajar la
   asimetría a exploratoria; (iv) abrir la etapa 1b transversal (gradiente de exposición) como la prueba confirmatoria con potencia,
   condicionada a datos y a un MC; (v) mantener la Desviación de errores estándar de F4 (NW(5) con residuos HC3), que con
   Romer-Romer es todavía más necesaria. Todo esto es decisión de los autores (§5).

---

## 1. Diagnóstico: de dónde sale la falta de potencia

La potencia de un contraste sobre β depende de β·√(Σε²)/(κσ_e). Hay tres palancas: la señal (β por unidad de choque), la
información del choque (N·var(ε), medida en unidades del tipo oficial) y el ruido de la variable de resultado (κσ_e). Con
`s1_liq` se suman además el reparto en 4 celdas y el apalancamiento.

| Factor | Cifra | Fuente |
|---|---|---|
| Ruido de ȳ (h = 0..4) | κσ_e = 1,865 × 1,357 = 2,53 pp; los controles solo lo bajan ×0,909 | [T§1], F4 tabla 3 |
| Señal de 1 sd del choque con β_ref | 0,067 pp → R² poblacional 0,0007 | [T§1] |
| Relevancia del choque | π = 1,76 pp de ffr por pp de ε, **F = 4,2**; sd en unidades de ffr = 0,134 pp | [T§2] |
| Celdas | Partir en 4 celdas multiplica el ee del oráculo ×2,4–3,8 frente a β_lin (3,31 → 6,8–12,7) | [T§1] |
| Ventana h = 0..4 | Con la forma de TT (pico a 2–3 años, TT p. 11), la media de h = 0..4 recoge solo el 20 % del pico | [T§6], F4 §2 |
| Estimador | LP de F4 / oráculo = ×1,2–1,4 | [T§1] |
| Apalancamiento | 2 trimestres suman el 36–45 % de Σε² en cada celda | F4 §0.1 |

**Literatura.**
- BS p. 4: Ramey (2016) encuentra que los efectos de la política monetaria están "often poorly estimated in samples that begin after
  about 1984", porque los choques estructurales posteriores son "much smaller and less informative" [cita de segunda mano de Ramey
  (2016), vía BS; el original no está en la biblioteca].
- BS p. 41: la ortogonalización "does reduce the relevance of our instrument, to the point where weakness of the instrument may be a
  serious concern" (F = 2,44 con solo FOMC). BS p. 59: con esa serie los resultados son "very imprecise and should be treated very
  cautiously".
- BS p. 55 (ya en `CITAS_DISENO_F`): el choque exógeno "may not be very relevant".

**Conclusión del diagnóstico [criterio propio].** El prerregistro usó la versión de la serie de BS que sus propios autores declaran
débil, sin la parte (discursos) que la hacía relevante. El problema principal es la información del choque (F = 4,2), multiplicada
por las 4 celdas y por una ventana que mide antes del pico. El estimador no es el cuello de botella.

**Comprobación cruzada.** Para H1⁺ con BS, la cuenta rápida da c_LP = 33–38 sin ventana (27,1 × 1,2–1,4, [T§5]). El MC de F4 da
potencia 0,8 entre c = 30 y c = 40 (F4 tabla 2). Coinciden, así que las aproximaciones de [T§5–7] están bien calibradas.

---

## 2. Alternativas

Unidades: c = MDE / |β_ref| (potencia 0,8). F4 da c ≈ 35–40 para H1 por signo.

### (a) Más estructura: VAR / proxy-SVAR, LP suavizada o con shrinkage, VAR con umbral

- **Ganancia máxima:** ×1,2–1,4 en el ee, que es la distancia entre la LP y el oráculo con el DGP verdadero [T§1]. Un VAR bien
  especificado se acerca al oráculo, y uno mal especificado añade sesgo. El suavizado entre horizontes no puede ganar más que
  elegir bien la ventana: ×1,34 [T§6].
- **Disyuntiva sesgo-varianza entre LP y VAR [pendiente de Literatura]:** la referencia natural (Li, Plagborg-Møller y Wolf) no está
  en la biblioteca. No se cita hasta que Literatura la verifique con página. La cota del oráculo hace el argumento sin ella.
- **VAR con umbral o dependiente del estado:** TT p. 9 explican que un VAR con cambio de régimen "implicitly assumes no change in the
  state of the economy", algo difícil de defender con choques grandes. Además, añade parámetros a una muestra que ya no los soporta.
- **Hipótesis contrastable:** la misma (H0, H1). **Potencia:** con c ≈ 25–30, sigue ≈ tamaño. **Se descarta como solución**, aunque
  puede servir como robustez.

### (b) Variación transversal: panel de grupos o de empresas con efectos fijos de tiempo

- **Ganancia:** t_panel / t_agregado = √G · (σ_agg/σ_idio) · (Δβ·sd_X/|β|) [T§3].
  - Con G = 40 grupos y σ_idio ≈ 2σ_agg: ×1,6.
  - Con G = 200: ×3,5.
  - Con G = 2 (Z.1 solo separa empresas societarias y no societarias): ×0,7 o menos, **inútil**.
- **Lo que deja de ser contrastable:** con efectos fijos de tiempo, el choque común se absorbe y **el nivel de H1 (β_C < 0) no se
  identifica**. Solo se identifican diferencias entre grupos.
- **Lo que pasa a ser contrastable:**
  - **H2 (nueva, con signo fijado por la teoría):** dentro del estado restringido, los grupos con más exposición neta a la
    repreciación (g) transmiten más, porque ∂I_u/∂g = 1 − ω > 0 si ω < 1. Está verificado en
    `check_nesting.py::test_dI_dg_is_one_minus_w_and_its_sign`. Es la predicción más cercana al mecanismo que tenemos con signo fijo.
  - **E1** (la diferencia entre estados de liquidez) se vuelve medible con mucha más potencia, **pero sigue sin signo teórico**
    (signo de a g − p_f, decisión 2 de los autores): seguiría siendo exploratoria.
- **Evidencia de que hay señal en esta dirección:** Jeenas (WP, p. 9) usa Compustat trimestral y el ratio de caja sobre activos. En
  p. 13 informa de que la heterogeneidad explicada por la liquidez es "substantial in comparison to the 'level' effects" sobre la
  inversión agregada de esas empresas (−0,34 % a dos años).
- **Datos [criterio propio; los tiene que comprobar Datos]:**
  - Compustat: G de miles, pero no es gratis (la rúbrica pide datos gratis). **Pregunta a los autores:** ¿tenéis acceso a WRDS?
  - Quarterly Financial Report del Census (por tamaño de activo e industria): gratis, pero **no está en `datalake/CATALOG.md`**. Falta
    comprobar si da inversión (o PP&E para construirla), caja y deuda bancaria a corto con continuidad trimestral, y desde qué año.
  - Exposición g: E.2 STBL solo cubre 1997–2017 (decisión 2 de los autores). Habría que medirla por grupo con otra fuente o con un
    proxy (el tamaño) que tendría que justificarse con literatura [pendiente de Literatura].
- **Potencia:** no se puede calcular hasta saber G y σ_idio. **Es la única familia con potencial de llegar a 0,8 con efectos
  plausibles.**

### (c) Choque con más varianza o instrumento más fuerte

[T§2], ganancia en el t respecto al prerregistro, a igual ruido:

| choque | N | F primera etapa | % de Σε² en los 4 mayores | ganancia t |
|---|---|---|---|---|
| BS-2023 orth (prerreg.) | 102 | 4,2 | 29 % | 1,0 |
| BS-2023 raw | 102 | 66,7 | 30 % | 2,6 |
| BS-2025 ME (1994–) | 79 | 22,3 | 50 % | 1,9 |
| JK MP_pm | 95 | 57,1 | 56 % | 2,4 |
| **Romer-Romer 1969–2007** | 156 | 15,3 | 53 % | **5,1** |
| Romer-Romer sin 1979Q4–1982Q4 | 143 | 32,8 | 26 % | 3,2 |
| Innovación recursiva de Δffr 1969–2007 | 156 | — | 43 % | 9,2 |

- **BS raw y JK:** ganan ×2,4–2,6, pero BS p. 3 documentan que las sorpresas sin ortogonalizar son predecibles (R² del 10–40 %). Se
  recupera relevancia perdiendo exogeneidad, y el sesgo va hacia cero (BS p. 41). Sirven como robustez, no como choque principal.
- **Romer-Romer** (la serie de Coibion en los datos del Handbook de Ramey, en `datalake/raw/narrative/ramey/`):
  - Es el choque que usa la propia fuente de β_ref: TT p. 9 lo usan para 1969Q1–2003Q2, y TT p. 2 encuentran con él diferencias por
    estado "particularly large in … business investment".
  - **Riesgos:** (1) el periodo de Volcker concentra la varianza (TT p. 10: "the period of greatest variability in the shocks"; 53 %
    de Σε² en 4 trimestres [T§2]), así que el apalancamiento de F4 empeora; (2) posible cambio estructural entre los años 70 y hoy
    [criterio propio]; (3) **solapamiento con la crisis:** TT cortan los choques en 2003Q2 para que la respuesta no entre en la
    crisis (TT p. 9). Con h = 12 habría que cortar en ≈ 2005Q2. Las cifras de [T§5, §7] usan 1969–2007 y son algo optimistas.
- **Innovación recursiva:** es una cota de varianza, no un diseño. Contiene la respuesta sistemática a las noticias del trimestre y
  sesga hacia cero. Solo vale como robustez (TT p. 16 la usan así, con un VAR de Cholesky).
- **LP-IV con el tipo:** en el caso exactamente identificado no añade información respecto a la forma reducida. Solo cambia la
  escala, y con F = 4,2 sus intervalos no son fiables [criterio propio]. No es una vía.
- **Frecuencia mensual:** sumar a trimestres conserva Σε², así que no se gana información del choque. Solo habría ganancia si una
  variable de resultado mensual tuviera menos ruido en relación con la señal. No lo he calculado [criterio propio].
- **Potencia con Romer-Romer y ventana h = 4..12** [T§7] (c_LP con una pérdida LP de ×1,2–1,4):

| contraste | c_LP | potencia con β_ref |
|---|---|---|
| H0 lineal | 1,8–2,1 | 0,31–0,39 |
| H1, estado C, signos juntos | 2,6–3,0 | 0,21–0,25 |
| H1⁺, estado C, solo subidas (Holm) | 5,0–5,8 | 0,07–0,08 |

### (d) Variable de resultado más sensible o más cercana al mecanismo

[T§4]: MDE por 1 pp de fed funds, en la media de h = 0..4, en las 102 filas.

| variable | MDE (pp por 1 pp de ffr) |
|---|---|
| inversión no residencial | 4,7 |
| deuda NFC | 2,7 |
| PIB real | 1,6 |
| EBP | 0,8 |
| préstamos bancarios NFC | 7,1 |
| liquidez amplia NFC | 6,3 |

- Las variables cercanas al mecanismo (liquidez m_u y préstamos) son **más ruidosas** que la inversión. Las menos ruidosas (PIB,
  EBP) no contrastan el mecanismo.
- Sin un β_ref con página para cada variable no se puede convertir el MDE en c. Además, cambiar la variable de resultado cambia la
  hipótesis, porque la teoría habla de I_u.
- **Inversión de las empresas pequeñas:** solo tiene sentido dentro de (b).
- **No es una solución por sí sola.**

### (e) Aceptar "no concluyente por potencia" y llevar la contribución a la teoría y a la etapa 2

- Es el resultado modal del diseño actual: P(no concluyente) = 0,89–0,93 (F4 §0.3).
- Es honesto y barato, pero la etapa 1 no aportaría nada: un IC de ±20 pp sobre ȳ no acota ningún modelo.
- La contribución quedaría en la teoría (el margen interior y el cierre común entre IOPO y Perez-Orive) y en la etapa 2, cuya puerta
  de potencia (≥ 0,8 con 10–12 clústeres) tampoco está garantizada [criterio propio].

---

## 3. Comparación con la rúbrica de la SPEC [criterio propio]

Puntuación de 1 a 5. **Diseño actual** = `s1_liq` con BS-orth.

| Criterio | Actual | (a) | (b) panel | (c) RR + ventana | (d) | (e) |
|---|---|---|---|---|---|---|
| Ajuste a la intuición | 4 | 4 | 4 (estados × exposición) | 4 | 3 | 3 |
| Ambición / contribución | 3 | 3 | 4 (H2 contrasta el canal) | 3 | 2 | 2 |
| Identificación | 4 | 3 (más supuestos) | 4 (FE de tiempo; exposición endógena) | 3 (narrativo; Volcker; cambio estructural) | 4 | — |
| Datos / potencia | **1** (c ≈ 35–40) | 1 | 3–5 según los datos (sin calcular) | 2–3 (c ≈ 2,6–3 en H1 con signos juntos) | 1 | — |
| Riesgo | 2 | 2 | 3 (falta de datos gratis) | 3 | 2 | 4 |
| Coste (semanas de desks hasta el primer resultado; no es una puntuación) | 0 | 2 | 4–6 | 1–2 | 1 | 0 |

Una ambición alta no compensa una identificación de 2: ninguna opción cae por debajo de 3 en identificación.

---

## 4. Recomendación [criterio propio]

**Etapa 1 rediseñada (`s1r_*`), antes de ver datos:**
1. **Choque principal:** Romer-Romer (serie de Coibion, Handbook de Ramey), con los choques entre 1969Q1 y el último trimestre en
   que la ventana h = 12 acaba antes de 2008Q3 (≈ 2005Q2; Datos fija la fecha exacta).
   - BS-2023 orth 1988–2023 pasa a **réplica posterior a 1984** (robustez, no decide), con sus potencias escritas.
   - Romer-Romer sin 1979Q4–1982Q4 es robustez obligatoria.
2. **Estadístico:** media de h = 4..12 del cambio acumulado, en vez de h = 0..4. La ventana sale de la forma de TT (p. 11), no de
   nuestros datos.
3. **Hipótesis confirmatorias:**
   - H0 lineal;
   - **H1 con signos juntos** (β_C < 0 en el estado restringido).
   - La **asimetría pasa a exploratoria**. Esto **revierte en parte el diseño F aprobado** ("subidas y bajadas separadas"), así que
     es una decisión de los autores.
4. **Potencia escrita ex ante en la SPEC:** "con β_ref, potencia ≈ 0,2–0,4; el MDE es ≈ 2–3·β_ref".
   - La regla (b) de refutación sigue inactiva mientras la potencia sea < 0,8.
   - Se publica el IC como medición.
5. **Errores estándar:** se mantiene la Desviación de F4: NW(5) en trimestres naturales con residuos HC3. Con Romer-Romer el
   apalancamiento es mayor (53 % de Σε² en 4 trimestres), así que hace todavía más falta, pero **hay que validarla de nuevo**.
6. **Estado:** el mismo `D_{t−1}` (liquidez de Z.1 frente a su media móvil de 12 trimestres), disponible desde 1946.
   - Datos publica antes D1 y D2 (observaciones y Σ|ε| por celda) en la muestra nueva. **Si los trimestres de Volcker caen casi todos
     en un estado, se escala antes de estimar.**

**Etapa 1b (nueva, condicionada):** H2, el gradiente de exposición ∂I_u/∂g = 1 − ω > 0 en un panel con efectos fijos de tiempo.
- **Puerta:** que Datos encuentre una fuente gratis con G ≥ 40 grupos (o que los autores aporten Compustat) y una medida de g por
  grupo, y que el MC dé una potencia ≥ 0,8.
- Si pasa la puerta, **H2 es la prueba confirmatoria principal del paper**: es la que contrasta el canal y la que tiene potencia.

**Qué tiene que validar Econometría con un MC nuevo (`mc-validate`) antes de estimar:**
- (i) el DGP de F4 con Romer-Romer y D reales y fijos en la muestra nueva, y el ruido de un AR(2) univariante de la inversión **en
  esa muestra** (sin choques);
- (ii) el estadístico h = 4..12 con signos juntos: sesgo, cobertura de NW(5)+HC3 con T y T/2, y la curva de potencia
  c ∈ {1, 2, 3, 5};
- (iii) si la pérdida LP/oráculo (×1,2–1,4) y la ganancia de ventana (×1,34) se componen como supone [T§7];
- (iv) la misma tabla sin Volcker;
- (v) para la etapa 1b, un MC aparte cuando existan los datos (G, σ_idio/σ_agg y la correlación de g con el estado).

**Peticiones a otras desks** (el encargo prohíbe editar otros archivos, así que no las he añadido a `TASKS.md`; propongo que la
Coordinación las añada y las asigne):
- **Datos:** QFR (disponibilidad y variables), fecha de corte, y D1/D2 en la muestra de Romer-Romer.
- **Literatura:** Li, Plagborg-Møller y Wolf (LP frente a VAR) con página; Ramey (2016), en el original; una fuente para usar el
  tamaño como proxy de la exposición a tipo variable; la extensión de Romer-Romer más allá de 2007 (p. ej., Wieland-Yang), si existe.

## 5. Decisiones que tienen que tomar los autores

1. ¿Se para `s1_liq` tal como está? Recomiendo que sí, coincidiendo con F4.
2. ¿Pasa Romer-Romer a ser el choque principal, con BS-orth como réplica? Es una Desviación sobre la decisión 1.
3. ¿Se juntan los signos en H1 y la asimetría pasa a exploratoria? Es una Desviación sobre el diseño F.
4. ¿Se cambia la ventana a h = 4..12?
5. ¿Se registra ya la Desviación de errores estándar de F4?
6. ¿Se abre la etapa 1b transversal? ¿Hay acceso a Compustat/WRDS?
7. ¿Se acepta prerregistrar una H1 con una potencia esperada de ≈ 0,2–0,4, presentada como medición acotada?
