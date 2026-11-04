# p01 · Borrador del prerregistro de la etapa 1 (EE. UU.) · 2026-11-04

Autor: Director científico (sesión `desks/direccion-cientifica/`). Encargo: `desks/direccion-cientifica/ENCARGO_2026-11-04_prerreg.md` (tarea F3).
**Es una propuesta para los autores.** No se ha editado la SPEC. Cuando los autores la aprueben (o la corrijan), la Coordinación copia
§1–§6 a `SPEC.md` y el bloque ```prereg``` pasa a ser el que lee `tools/research.py`.

Convenciones:
- "p. N" es el marcador `<!-- p. N -->` de `kb/library/md/<clave>.md` (página del PDF).
- Las ecuaciones se citan como `archivo::test`, el test de `papers/p01-liquidity/theory/` que las verifica.
- **[criterio propio]** marca juicio mío, no un hecho leído.
- No he visto ningún resultado de shock → inversión. Solo he mirado las figuras de las variables de estado y del fed funds
  (`output/figures/data_*.png`) para definir los estados. No pude ejecutar Python en esta sesión (la herramienta pedía aprobación), así
  que los recuentos de observaciones de §6 son aritmética sobre las coberturas de `coverage.csv`. Econometría (F4) debe confirmarlos.

---

## 0. Resumen para los autores (una página)

1. **Qué fija la teoría verificada (F1) y qué no.** Con restricción activa, la transmisión es `I_u = ω p_f/a + (1−ω) g` con
   `ω ≥ ω_min > 0`. Por tanto, si el alivio por repreciación es no negativo (`g ≥ 0`), **la transmisión no se anula en ningún estado**:
   el signo es fijo. En cambio, **el signo de la diferencia entre estados** (poca frente a mucha liquidez) es el de `a g − p_f`, y la teoría
   lo deja libre. Va como exploratorio, como una **medición** de qué margen domina.
2. **Confirmatorio (3 especificaciones):**
   - H0, transmisión lineal (comprueba el pipeline);
   - **H1, transmisión no nula en el estado restringido**, por separado para subidas (H1⁺) y bajadas (H1⁻), con el estado de liquidez;
   - H1-DSR, la misma predicción con el DSR como estado (secundaria).
3. **Vintage:** recomiendo `mps_bs23_orth` como choque principal y `mps_bs25_me` como robustez (§5). Hay una comprobación pendiente para
   Datos: si el xlsx de BS-2023 trae también la serie con discursos del presidente de la Fed.
4. **Estado principal:** liquidez amplia sobre deuda (Z.1), **sin tendencia** y medida en t−1. El DSR queda como estado secundario,
   porque tiene ≈ 58 observaciones útiles (§6).
5. **Riesgo principal [criterio propio]:** H1 es una predicción con signo fijo, pero **poco exigente**. Solo descarta los extremos rígidos
   (TFG1; una lectura fuerte de Perez-Orive et al. para las bajadas). El valor empírico de la etapa 1 está más en E1 (la medición del signo
   de `a g − p_f`) que en H1. Los autores deciden si E1 pasa a confirmatoria con contraste bilateral (§4, opción A).

---

## 1. Pregunta e identificación (etapa 1, EE. UU.)

### Pregunta
¿Sigue transmitiéndose un choque de política monetaria a la inversión no residencial de EE. UU. cuando la liquidez de las empresas no
financieras está por debajo de su tendencia, tanto en las subidas como en las bajadas, como predice el margen interior de reservas
(`ω ≥ ω_min > 0`)? ¿Y en qué dirección cambia la transmisión con la liquidez, es decir, qué margen domina, el de precios (`p_f/a`) o el de
flujo de caja (`g`)?

### Del modelo a la regresión
| Objeto del modelo | Equivalente empírico | Supuesto de medición |
|---|---|---|
| `u` (relajación del coste de financiación) | **−ε_t**, choque de Bauer-Swanson (positivo = endurecimiento) | El choque mueve `p_f` y `g` en el mismo sentido que el tipo oficial |
| `I_u` | respuesta de `100·log inv_nonres_q` (índice de cantidad BEA `A008RA3Q086SBEA`) | Inversión agregada = Σ de las empresas (`check_aggregation.py`) |
| `B = κ_F Q(z_F)`, `z_F = (m−μ_F)/σ_F` | estado `D_{t−1}`: **liquidez amplia / deuda** (Z.1) por debajo de su tendencia | **M1:** la liquidez sin tendencia es monótona en `z_F`. La tendencia secular de la caja empresarial (figura `data_liq_broad_debt.png`: de ≈0,13 en 1990 a ≈0,33 en 2026) se trata como un movimiento conjunto de `m` y de `μ_F, σ_F` que deja `z_F` sin tendencia **[criterio propio]** |
| `g = γ E_D ≥ 0` | no se mide en la etapa 1 (Z.1 no separa la deuda a tipo variable, `DICTIONARY.md` §Estado) | **A-g:** la exposición **neta** a la repreciación de las empresas que invierten es ≥ 0 (ver §2, H1) |

### Especificación base (LP de un estado, subidas y bajadas por separado)
Para `h = 0,…,H`, con `ε⁺_t = max(ε_t,0)` y `ε⁻_t = min(ε_t,0)` (la separación de Tenreyro y Thwaites, p. 13):

```
ȳ_t ≡ (1/5) Σ_{h=0}^{4} 100·[log I_{t+h} − log I_{t−1}]                       (estadístico confirmatorio)

ȳ_t = α + δ D_{t−1}
      + β⁺_C D_{t−1} ε⁺_t + β⁺_U (1−D_{t−1}) ε⁺_t
      + β⁻_C D_{t−1} ε⁻_t + β⁻_U (1−D_{t−1}) ε⁻_t
      + Σ_{ℓ=1}^{2} Γ_ℓ' x_{t−ℓ} + u_t
```
- **`D_{t−1}` = 1 (estado restringido)** si `s_{t−1} < mediana(s)` en la muestra de estimación, con `s_t = log(liq_broad_debt_t) − (1/12) Σ_{j=1}^{12} log(liq_broad_debt_{t−j})`.
  Es la desviación respecto de la media móvil hacia atrás de 3 años: solo usa información anterior a t. El umbral en la mediana de toda la
  muestra sigue a Tenreyro y Thwaites, que fijan c para que una proporción dada de la muestra quede en cada régimen (p. 10).
- **Controles `x`** (2 retardos, sin interactuar): Δlog `inv_nonres_q`, Δlog `gdp_real`, Δlog `gdp_deflator`, Δ`y2_mean` y `ebp`.
  - Interactuar los controles con el estado, como en Tenreyro y Thwaites (p. 8), es robustez: con T≈100 duplicaría los parámetros
    (de 16 a 26) **[criterio propio]**.
- **IRF completa** h = 0,…,12 con la misma ecuación y `y_{t+h} − y_{t−1}` como variable dependiente. Se presenta, pero **no decide**.
  Los horizontes > 4 son propagación (FIRST_PRINCIPLES §6.2).
- **Errores estándar:** Newey-West (Bartlett) con 5 retardos, porque ȳ_t solapa 5 trimestres. Bauer y Swanson usan Newey-West con h
  retardos en sus LP (p. 45). Valores críticos de la t con T−k grados de libertad.
  - **Condición F4:** si el Monte Carlo de F4 da una cobertura fuera de [0,92; 0,98] con el T real, se usa el método que F4 valide (p. ej.,
    bootstrap por bloques). El cambio se registra como Desviación **antes** de estimar con datos reales.
- **Forma reducida, no LP-IV:** el regresor es el choque, no el tipo instrumentado. Motivo: con FOMC solo y la serie ortogonalizada, Bauer y
  Swanson obtienen F de la primera etapa de 2,44 (p. 45, n. 47) **[mi lectura: las cifras de la nota van en el orden sin ajustar /
  ortogonalizada]**, de modo que el LP-IV sería débil. En forma reducida, la debilidad se convierte en falta de potencia, que mide F4.
  - El escalado a "25 pb en el bono a 2 años" se presenta aparte, como lectura y sin contraste.

### Identificación y amenazas
- **Exogeneidad del choque.** La serie ortogonalizada elimina la parte predecible con noticias macrofinancieras públicas previas
  (Bauer-Swanson pp. 3, 17; recomendación en §5.5, p. 51). Sin ortogonalizar, la predictibilidad tiene un R² de 10–40 % (p. 3) y sesga las
  respuestas macro hacia cero, hasta un factor 4 (p. 6).
  - **No** está ortogonalizada respecto a la liquidez empresarial. Por eso se prerregistra un **test de balance**: regresión de `ε_t` sobre
    `D_{t−1}` y `s_{t−1}` (§3, D3).
- **El estado es predeterminado** (t−1), pero endógeno a la historia. El coeficiente β_C compara la respuesta **condicionada** al estado; no
  es el efecto causal de la liquidez **[criterio propio]**. Por eso la diferencia entre estados se interpreta como medición dentro del modelo
  (E1), no como prueba causal.
- **Agregación.** La liquidez de Z.1 está concentrada en las grandes empresas (`DICTIONARY.md`). El estado agregado puede medir mal la masa
  de restringidas (π). Es una amenaza para M1 y sesga β_C − β_U hacia cero **[criterio propio]**.
- **Persistencia del choque.** El modelo es de un periodo; los choques de BS son persistentes (el bono a 2 años vuelve a su nivel en
  varios años, p. 53). ȳ_t (h ≤ 4) se lee como respuesta de corto plazo, no como `I_u` estático.

---

## 2. Hipótesis confirmatorias (signo fijado ex ante)

Convención de signos: β < 0 significa que la inversión **cae** tras un endurecimiento (ε⁺) y **sube** tras una bajada (ε⁻ < 0 por β < 0).

| Id | Hipótesis | Signo | Ecuación de la que sale (`theory/`) | Especificación |
|---|---|---|---|---|
| **H0** | Transmisión lineal a la inversión | β_lin < 0 | Agregado `L_u = (Ḡ + Θ p_f)/(1 + φΘ)` (`check_aggregation.py::test_general_formula_any_number_of_types`), con Θ = Σ s_j ω_j/a_j > 0 y Ḡ ≥ 0 ⇒ L_u > 0 | `s1_lin` |
| **H1⁺** | En el estado restringido, una **subida** reduce la inversión | β⁺_C < 0 | `I_u = ω p_f/a + (1−ω) g` (`check_nesting.py::test_transmission_formula_from_kkt`, `::test_weighted_form`) con `ω ≥ ω_min = γ²a/(κ_F+γ²a) > 0` (`check_nesting.py::test_weight_is_bounded_below_by_w_min`). Con g ≥ 0: `I_u ≥ ω_min p_f/a > 0`. En agregado, con banco común, Θ ≥ ω_min Σ s_j/a_j > 0 ⇒ L_u > 0 | `s1_liq` |
| **H1⁻** | En el estado restringido, una **bajada** sube la inversión | β⁻_C < 0 | Lo mismo: el modelo es diferenciable con la reserva interior, así que la derivada local es la misma en los dos sentidos | `s1_liq` |
| **H1-DSR** (secundaria) | H1⁺ y H1⁻ con el DSR alto como estado restringido | β⁺_C, β⁻_C < 0 | Lo mismo. Un DSR alto sube a la vez μ_F (⇒ B) y g; con g ≥ 0 el límite inferior se mantiene | `s1_dsr` |

**Supuestos de los que dependen los signos (se declaran, no se contrastan en la etapa 1):**
- **A-g (g ≥ 0):** si las empresas tienen activos líquidos que se reprecian más que su deuda, la exposición neta `g` puede ser negativa y
  la cota `I_u ≥ ω_min p_f/a` deja de valer. Hay dos datos que lo hacen plausible, sin demostrarlo:
  - Buena parte de la liquidez de las empresas no financieras de EE. UU. rinde casi cero o es poco sensible al tipo oficial (Jeenas, p. 5, n. 8).
  - En la muestra de IOPO, la deuda a tipo variable es el 25,4 % de la deuda en 2008 (IOPO, p. 43, n.).

  **Una refutación de H1 refuta "el nido con g ≥ 0", no el nido.**
- **Resto de supuestos:** reserva interior (no esquina) y equilibrio parcial con precio fijo (advertencias de `VERIFICACIONES_2026-11-04.md` §5).

**Pendiente de Teoría antes de adoptar la SPEC [requisito]:**
- Dos tests explícitos de `check_sign`:
  - `L_u > 0` con g_j ≥ 0 y ω_j ≥ ω_min (hoy es un paso de una línea, pero no está como test);
  - `∂I_u/∂g = 1−ω` (E3).
- Regla de CLAUDE.md: sin script, la proposición no entra. Hasta que existan, H0/H1 se apoyan en `test_general_formula…` + `test_weight_is_bounded…`.

**Qué distingue H1 de los rivales:**
- **TFG1 y el límite rígido** (`B→∞`, g = 0 ⇒ `I_u → 0`; `check_nesting.py::test_rigid_limit_B_to_infinity_is_g`) predicen β_C ≈ 0.
- **Perez-Orive et al.:** con varias restricciones, la política expansiva tiene efectos "débiles" porque siempre queda una restricción
  activa (p. 3; Prop. 1–2, p. 12). No predicen cero. H1⁻ solo los contradice si β⁻_C resulta **mayor** que lo que su atenuación permite,
  y eso no es un contraste prerregistrable sin su calibración **[criterio propio]**.
- **Lo que es poco exigente:** casi cualquier modelo con transmisión positiva predice β_C < 0 (ver §0.5).

---

## 3. Reglas de decisión

Estadístico: los coeficientes sobre ȳ_t (media de h = 0–4). α = 0,05 unilateral. **Holm** sobre {H1⁺, H1⁻} dentro de `s1_liq`. H1-DSR
tiene su propio Holm y **no puede revocar** la conclusión de `s1_liq`, solo replicarla o no.

| Resultado | Condición |
|---|---|
| **Confirma H1^d** (d = +, −) | β^d_C < 0 con p ajustado por Holm < 0,05 |
| **Refuta H1^d** | (a) β^d_C > 0 con p unilateral < 0,05 (signo contrario); **o** (b) equivalencia: el IC al 90 % de β^d_C cae entero en (−δ^d, +∞), con δ^d = ω_min^{TFG2}·\|β̂^d_U\| = 0,146·\|β̂^d_U\|. Es decir, la respuesta restringida es significativamente menor que la cota del modelo con g = 0, evaluada en la calibración de TFG2 (`check_nesting.py::test_minimum_transmission_with_g0_at_tfg2_calibration`). **[criterio propio]:** ω_min depende de κ_F y a. Si los autores prefieren no usar una cifra calibrada, la regla (b) se sustituye por "IC al 90 % dentro de (−0,1·\|β̂^d_U\|, +∞)" |
| **No concluyente** | Ninguna de las anteriores. **Además, siempre que la potencia (F4) contra la alternativa de referencia sea < 0,8, un β_C no significativo se declara "no concluyente por potencia", nunca refutación** |
| **H0** | Confirma si β_lin < 0 con p < 0,05. Si H0 no se confirma, el pipeline o la relevancia del choque fallan: **H1 no se interpreta** y se escala al director antes de seguir |

**Alternativas de referencia para la potencia (encargo a F4):**
- `β_U = β_ref` y `β_C ∈ {β_ref, 0,5·β_ref, 0,146·β_ref}`, con T, la proporción por celda (estado × signo) y la varianza del choque reales.
- **β_ref:** el gasto duradero de hogares y la inversión empresarial caen ≈ 2,5 % por 1 pp del fed funds en el modelo lineal de Tenreyro y
  Thwaites (pp. 11–12, choques de Romer). Hay que traducirlo a unidades de ȳ con la respuesta del fed funds al choque BS. Es tarea de F4, que lo documenta.
- **[criterio propio]:** es una referencia de otra serie de choques y de otra muestra (1969–2003, TT p. 9). Si F4 considera mejor otra
  fuente con página, se cambia antes de estimar.

**Diagnósticos prerregistrados (no deciden, se publican siempre):**
- **D1:** número de observaciones por celda (estado × signo).
- **D2:** suma de \|ε\| por celda.
- **D3:** test de balance ε_t ~ D_{t−1} + s_{t−1}. Si p < 0,05, se añade s_{t−1}·ε_t como control en una robustez, sin cambiar la principal.
- **D4:** estabilidad de la mediana del estado al quitar 1988–93.

---

## 4. Exploratorio (lista cerrada; todo lo demás también lo es)

Se registra con `log_spec(..., exploratory=True)` y se presenta como exploratorio.

| Id | Qué | Por qué no es confirmatorio | Ecuación |
|---|---|---|---|
| **E1** | **Diferencia entre estados** β^d_C − β^d_U: mide el signo de `a g − p_f`, es decir, si la restricción amplifica (g > p_f/a) o atenúa | La teoría no fija el signo; la literatura discrepa (OW diap. 4, 12–13 frente a IOPO pp. 36–41; ver DEVILS_ADVOCATE §2.1) | `∂I_u/∂B = γ²(a g − p_f)/(B+γ²a)²` (`check_coordination.py::test_slope_depends_on_B_with_sign_of_a_g_minus_p_f`), con B decreciente en la liquidez (`check_nesting.py::test_Q_is_strictly_decreasing_onto_open_unit_interval`) |
| E2 | **Asimetría** β⁺ frente a β⁻ (lineal y por estado) | En el nido, con una restricción y reserva interior, la derivada local es simétrica. Perez-Orive et al. obtienen asimetría solo con varias restricciones (Prop. 1, p. 12), y nuestro modelo no la tiene derivada | — (no derivada; FIRST_PRINCIPLES 6.6(3) queda exploratoria) |
| E3 | `∂I_u/∂g = 1−ω > 0` **solo** con restricción activa: interacción exposición × restricción | Signo fijo en la teoría (dirección prerregistrada: mayor respuesta con más exposición en el estado restringido), pero exige medir g aparte del estado. Son dos estados, y la SPEC limita la etapa 1 a uno | `check_nesting.py::test_weighted_form` (falta test explícito, ver §2) |
| E4 | **Interacción triple** choque × exposición × restricción | Exploratoria por decisión de los autores (SPEC, Desviaciones 2026-11-04) | — |
| E5 | Coordinación / incertidumbre de política (EPU) sobre la **pendiente** | Signo libre con restricción activa | `check_coordination.py::test_coordination_effect_on_slope_has_no_fixed_sign_when_constrained` |
| E6 | Transición suave con pendiente **estimada** (STAR-LP) | θ casi no identificado con ~100 observaciones (DEVILS_ADVOCATE §1, 5.2) **[criterio propio]** | — |
| E7 | Amortiguamiento por banco común 1/(1+φΘ) y expulsión de crédito de las holgadas | No se contrasta con datos agregados: exige una sección cruzada | `check_aggregation.py::test_response_is_smaller_than_without_common_bank`, `::test_slope_response_falls_with_mass_and_relief_of_constrained` |
| E8 | Otras variables de resultado: liquidez (m_u, signo libre: `check_nesting.py::test_buffer_and_multiplier_formulas`), préstamos bancarios, EBP, `inv_nfc_real` | No hay hipótesis con signo | — |
| E9 | Horizontes h > 4 | Propagación, no mecanismo (FIRST_PRINCIPLES §6.2) | — |
| E10 | Extensión 2024–2026 con `mps_bs25_me` | Fuera de la muestra del choque principal | — |
| E11 | **Etapa 2** (panel de la zona euro) | Solo si pasa la puerta F5 (SPEC, Desviaciones) | — |
| — | FIRST_PRINCIPLES 6.6(2, segunda mitad) y 6.6(4) | **Fuera** hasta que se deriven (SPEC) | — |

**Opción A para los autores [criterio propio]:** pasar E1 a confirmatoria como **contraste bilateral de existencia** (H2: β_C ≠ β_U).
- **Ventaja:** la teoría predice ∂I_u/∂B ≠ 0 salvo en el caso no genérico `a g = p_f`, y la medición del signo es la contribución empírica
  diferencial de la etapa 1.
- **Coste:** un contraste bilateral sin signo es justo lo que el informe del abogado del diablo critica (§2.1: "con el signo libre, casi
  cualquier estimación encaja").
- **Recomendación:** dejarlo **exploratorio** y presentar el signo como medición, salvo que Datos encuentre antes de estimar una medida de
  g (p. ej., la cuota a tipo variable del Survey of Terms of Business Lending, `DICTIONARY.md`, no probada). Esa medida permitiría fijar ex
  ante el signo esperado de `a g − p_f`.

---

## 5. Vintage de Bauer-Swanson: recomendación

**Recomiendo `mps_bs23_orth` como choque principal**, y `mps_bs25_me` y `mps_bs23_raw` como robustez. La decisión es de los autores.

| Criterio | `mps_bs23_orth` | `mps_bs25_me` |
|---|---|---|
| Exogeneidad para efectos macro | **Ortogonalizada** respecto de 6 noticias previas, la práctica que BS recomiendan para LP/VAR (pp. 17, 51). Sin ortogonalizar, las respuestas macro salen atenuadas o con el signo cambiado (p. 6, p. 54) | **No ortogonalizada** (`DICTIONARY.md`). Repetiría el sesgo que BS documentan |
| Muestra | 1988Q1–2023Q4; 1988–93 añade años de política más variable (BS p. 4). La datación de 1988–93 es menos nítida (operaciones de mercado abierto, p. 18) | 1994Q1–2026Q4; pierde 1988–93 y añade 2024–26 (≈ 10 trimestres útiles: Z.1 acaba en 2026Q2, `DICTIONARY.md`) |
| 2020 | NaN (decisión de BS-2023) | Disponible, pero 2020 se excluye igualmente (§6) |
| Relevancia | Solo FOMC: con la serie ortogonalizada y sin discursos, la F de la primera etapa es baja (p. 45, n. 47); BS recomiendan añadir los discursos del presidente de la Fed (p. 51) | Incluye las ruedas de prensa (ME). Construcción de Acosta et al. (2025): **no está en `kb/library/`, sin página** |
| Correlación | ρ trimestral con ME ≈ 0,66 (`DICTIONARY.md`): la elección no es neutra | |

**Argumento:**
1. La regla científica de la desk exige que el resultado no dependa de un instrumento con sesgo documentado. BS muestran que la
   predictibilidad sesga precisamente el objeto que estimamos, las respuestas macro (pp. 6, 54).
2. Los 10 trimestres extra de BS-2025 no compensan, y 2024–26 quedaría además en el final de muestra más revisado.
3. **Robustez obligatoria:** `mps_bs23_orth` con muestra 1994+ frente a `mps_bs25_me` con 1994+. Así se separa el efecto de la
   construcción del efecto de la muestra.

**Comprobación previa (Datos, antes de aprobar):**
- ¿El xlsx de BS-2023 tiene una hoja con FOMC + discursos ortogonalizada? (La desk solo usó la hoja `FOMC (update 2023)`.)
- Si existe, recomiendo esa serie como principal, por la relevancia (p. 45, n. 47; p. 51), y la de solo FOMC como robustez.

---

## 6. Muestra y robustez

**Muestra principal** (fechas t del choque):
- **Rango:** 1988Q2–2023Q4. 1988Q1 se pierde porque `s_{t−1}` necesita 12 trimestres de Z.1, que empieza en 1985Q1.
- **Se excluye:**
  - **ZLB:** trimestres con `ffr_t` < 0,25 (calculado por código a partir de `ffr`; según la figura, ≈ 2009Q1–2015Q4 y 2020Q2–2022Q1).
    El canal de tipo variable desaparece en el límite inferior (IOPO, resumen p. 2; §6.3, pp. 43–44), y el modelo asume que `g` se mueve
    con el tipo oficial.
  - **Pandemia:** t ∈ [2019Q1, 2021Q4]. Son los choques cuya ventana [t−2, t+4] toca 2020, más 2020, que es NaN en el choque
    **[criterio propio]**.
- **Tamaño:** T ≈ 143 − 28 − 13 ≈ **102** (aritmética sobre `coverage.csv` y la figura del fed funds; la cifra exacta, F4).
  Son ≈ 25 observaciones por celda estado × signo.

**Datos: última revisión, congelada.** Z.1 release 2026-09-11 y FRED 2026-11-04, con los hashes de `data/raw/MANIFEST.csv`.
- El estado es la liquidez de las propias empresas, que estas conocen sin error; la revisión es mejor estimación que el dato en tiempo
  real **[criterio propio]**.
- El tiempo real solo importaría si el estado midiera lo que sabía la Fed, y la ortogonalización de BS ya usa noticias publicadas antes del
  anuncio (p. 19).
- Con t ≤ 2023Q4 y h ≤ 4, la última inversión que se usa es 2024Q4, ya revisada en la actualización anual de la BEA.
- **Refrescar los datos es una Desviación fechada.**

**Estado: liquidez (principal) frente a DSR (secundario).**
- **Liquidez/deuda:**
  - Es el análogo directo de `m` frente a `μ_F`, que escala con las obligaciones (B = κQ(z_F)).
  - Cubre todo el choque (1985+).
  - Exige quitar la tendencia (§1).
- **DSR (`dsr_nfc`):**
  - Mezcla restricción (μ_F ↑) y exposición (g ↑). H1 sigue valiendo, pero E1 sería ininterpretable.
  - Empieza en 1999 ⇒ t ∈ 1999Q2–2023Q4 ⇒ ≈ 99 − 28 − 13 ≈ **58** observaciones.
  - Es muy persistente: ≈ 3 ciclos en la figura `data_dsr_nfc.png`, es decir, pocas "rachas" de estado independientes **[criterio propio]**.
  - Se usa en nivel, con el umbral en la mediana, sin quitar tendencia (no se ve tendencia en 1999–2026).

**Robustez prerregistrada** (ids en el bloque ```prereg```; **no deciden**):

| Id | Cambio frente a `s1_liq` |
|---|---|
| `r_bs25me` | Choque `mps_bs25_me`, muestra 1994+ |
| `r_bs23orth_1994` | Choque principal, muestra 1994+ (pareja de la anterior) |
| `r_bs23raw` | Choque `mps_bs23_raw` (sin ortogonalizar) |
| `r_zlb_in` | Incluye los trimestres ZLB |
| `r_covid_in` | Incluye 2019Q1–2021Q4 (excepto 2020, NaN) con variables ficticias por trimestre en 2020Q1–2021Q2 |
| `r_liq_narrow_assets` | Estado: `liq_narrow_assets` sin tendencia |
| `r_state_q25` | Restringido = cuartil inferior de s |
| `r_state_logistic` | Transición logística F(s) con θ = 3 **fijo** y c en la mediana (Tenreyro-Thwaites, p. 10) |
| `r_ctrl_interact` | Controles interactuados con el estado (Tenreyro-Thwaites, p. 8) |
| `r_lags4` | 4 retardos de los controles |
| `r_balance_ctrl` | Añade s_{t−1}·ε_t (solo si D3 rechaza) |
| `r_inv_nfc` | Resultado: `inv_nfc_real` (sociedades; deflactor del PIB) |

**Replicación cruzada:** `s1_lin` y `s1_liq` se replican en R (`code/replication_r/`, `fixest`), con `estimates_py.csv` = `estimates_r.csv`.

---

## 7. Bloque ```prereg``` propuesto (para copiar a la SPEC si los autores lo aprueban)

```prereg
# --- confirmatorias (deciden; reglas en SPEC §Hipótesis) ---
s1_lin        # H0: LP lineal, ȳ(h=0..4) sobre ε (choque principal), controles x (2 ret.), NW(5); muestra §6
s1_liq        # H1+ / H1-: LP con D(liquidez amplia/deuda sin tendencia, t-1) × {ε+, ε-}; Holm sobre {H1+, H1-}
s1_dsr        # H1-DSR (secundaria): igual que s1_liq con D = DSR (BIS, empresas no fin.) > mediana; 1999Q2+
# --- robustez prerregistrada (no deciden) ---
r_bs25me
r_bs23orth_1994
r_bs23raw
r_zlb_in
r_covid_in
r_liq_narrow_assets
r_state_q25
r_state_logistic
r_ctrl_interact
r_lags4
r_balance_ctrl
r_inv_nfc
```

**Antes de copiarlo a la SPEC** hay que resolver:
- la vintage (y si hay serie con discursos);
- la opción A de §4;
- la regla (b) de refutación, con la cifra de TFG2 o el 10 %;
- los dos tests de Teoría de §2.

**Y después:** F4 corre `mc-validate` con esta especificación exacta y el T real **antes** de tocar los datos de inversión.

---

## 8. Qué no he podido hacer
- Ejecutar Python: los recuentos de T de §6 son aritmética, sin código.
- Abrir el xlsx de BS-2023 para ver si trae la serie con discursos.
- Leer Acosta et al. (2025): no está en la biblioteca, así que no hay afirmaciones con página sobre BS-2025 salvo lo que dice `DICTIONARY.md`.
- Las páginas de BS son del NBER WP 29939 (abril de 2022), no de la versión publicada en NBER Macro Annual. La serie del xlsx se actualizó
  hasta 2023; la descripción del paper (muestra 1988–2019, pp. 18, 45) puede no coincidir exactamente con el xlsx.
- La versión de IOPO en la biblioteca es la de septiembre de 2016 (p. 2), no la publicada en 2018: las páginas pueden diferir.
