# F9 · Monte Carlo de la etapa 1 rediseñada (`s1r_*`) — informe de Econometría (2026-11-08)

Encargo: `desks/econometria/ENCARGO_2026-11-07_f9-mc-s1r.md`. Este informe no es una auditoría (eso es F10, del Referee).
**Todas las cifras salen de `output/tables/f9_power.md`** (§n = sección de esa tabla) y de la tabla estándar
`output/tables/mc_s1r.txt`. Las genera `code/mc/f9_power.py` (semilla 20261107; 1000 réplicas por escenario; ≈ 1,5 h), y el estimador
está en `code/analysis/s1r_lp.py`, el mismo que usará el análisis real. Tests: `code/mc/test_f9_power.py`.

**Regla dura cumplida.** No se ha estimado nada con la inversión real ni se ha mirado cómo responde a los choques. De la inversión
solo entra el AR(2) univariante de su crecimiento, sin choques, y la varianza de sus residuos en trimestres con PIB en caída (DGP
`het_rec`). La primera etapa usa el fed funds.

## 0. Conclusiones (una página)

1. **Hallazgo nuevo, que cambia la especificación: con la ventana h = 4..12, la LP con solo controles está sesgada dados los
   choques reales** (§1a). ȳ_t recoge la respuesta a todos los choques de t−10..t+12, y la serie de Romer-Romer está autocorrelada
   en la muestra (sin Volcker, ρ1 = 0,20 y ρ4 = 0,17; §0). Sin ruido, β̂/β − 1 vale:
   - +0,66 en `s1r_lin` sin Volcker y +0,83 en β_U con la muestra completa;
   - −0,67 en la réplica BS.

   Ningún error estándar lo arregla. **Propuesta: especificación `aum`**, que añade como controles los choques de t−1..t−10 (hasta el
   pico de la rampa de TT) y de t+1..t+12 (hasta el horizonte máximo), sin interactuar.
   - Con β_C = β_U, el error de diseño es exactamente 0 (§1a y test).
   - Con β_C ≠ β_U queda un resto, que tira de β̂_C hacia β_U: −0,43 frente a una desv. típ. de 2,1 cuando β_C = 0 y β_U = β_ref (§1c).
   - Interactuar los controles lo anula, pero cuesta ≈ 50 % de ee. Esa variante no está en las tablas: fue una prueba exploratoria,
     y por eso no la propongo.
   - La idea de controlar por los choques futuros es la de Teulings y Zubanov **[pendiente de Literatura]**.
   - Es una decisión de diseño para F11 (Dirección y autores).
2. **Error estándar: recomiendo NW(5) en trimestres naturales con residuos HC3, con la especificación `aum`.** Cobertura de los
   términos que deciden (b_lin, b_C) en los tres DGP:
   - con T: 0,948–0,990;
   - con T/2: 0,954–0,988 (§1b).

   **Nunca baja de la banda, pero la supera por arriba** (hasta 0,990, conservador) en varias celdas, así que `mc.validate` lanza
   `CoverageOutOfBand` (§6). Las alternativas no lo hacen mejor:
   - NW(12)+HC3 baja a 0,904–0,917 en b_C sin Volcker;
   - HC3 sin HAC llega a 0,994;
   - NW(5) simple cubre 0,64–0,95;
   - con la especificación `base`, ningún error entra en la banda (0,81–0,99).

   El fallo de NW(5)+HC3+`aum` es de **conservadurismo** (pierde potencia), no de tamaño.
   - El bootstrap por bloques no lo he probado: con 146 filas y el 70 % de Σε² del estado restringido en 4 trimestres, cada bloque
     cambia el diseño.
   - El wild bootstrap no conserva el solape MA(12).

   **Por la regla de la skill, F9 queda `[!]`**: la Dirección decide si acepta una sobrecobertura ≤ 0,99 o si pide otro error.
3. **Potencia y MDE con `aum` + NW5+HC3** (β_C = β_U = c·β_ref, árbol completo con la condición de H0; §3b; homo / het_eps):

| variante | P(confirma) con β_ref (c = 1) | c = 3 | c con P(confirma) = 0,8 | MDE en pp de ȳ por pp de fed funds (c × 1,92) |
|---|---|---|---|---|
| V1 (completa) | 0,094 / 0,097 | 0,656 / 0,540 | 3,9 / 4,4 | 7,5 / 8,4 |
| V2 (sin Volcker) | 0,048 / 0,087 | 0,372 / 0,442 | 5,5 / 4,9 | 10,6 / 9,4 |
| V3s (completa y sin Volcker, ambas p < 0,05) | 0,037 / 0,059 | 0,364 / 0,361 | 5,5 / 5,3 | 10,6 / 10,2 |
| V3l (completa, y β̂_C < 0 sin Volcker) | idéntica a V1 en las tablas | | | |
| Réplica BS (`base`) | 0,000 | 0,001 | > 10 | — |

   **La potencia frente a β_ref es 0,04–0,10, no el 0,2–0,4 que esperaba el Director** (y que aceptaron los autores en la decisión 7).
   Hay dos causas:
   - la condición de H0: H1 no se interpreta en el 82–87 % de las réplicas con c = 1 (§3);
   - el error estándar conservador (ee medio / desv. típ. ≈ 1,1–1,4; §1c).

   Sin condicionar, el contraste de H1 solo (§2) llega a 0,8 con c = 3,9 (completa) y c = 5,5 (sin Volcker).
4. **Probabilidades de veredicto** (§3, `aum`, homo):
   - **Con H1 cierta y c = 1:**
     - V1: h0_falla 0,824 · confirma 0,094 · no concluyente 0,082;
     - V2: 0,866 · 0,048 · 0,086;
     - V3s: 0,824 · 0,037 · 0,139.
   - **Bajo el rival (β_C = 0, β_U = c·β_ref)**, la falsa confirmación de V1 crece con c: 0,033 (c = 1), 0,097 (c = 3) y **0,139
     (c = 5)**. Se debe al resto del error de diseño en el estado que concentra Volcker (77 % de Σε²). V3s la mantiene en
     0,014–0,035 y V2 en 0,020–0,055 (homo y het_eps).
   - **Refuta (a) y refuta (b) tienen probabilidad 0 en todos los escenarios.**
5. **Umbral de refutación (b)** (§4).
   - Con δ = 0,146·|β̂_U|, E[δ̂] sobrestima el δ verdadero (0,266 con c = 1): ×1,7 con `aum` (0,457) y ×2,6 con `base` (0,702).
   - Con c = 5 el sesgo baja a ×1,03 (`aum`), porque la parte que es ruido pesa menos.
   - **Propongo δ fijo ex ante = 0,146·|β_ref| = 0,266 pp de ȳ por pp de ε** (con el β_ref de §0, que no usa la inversión). Así no
     depende de β̂_U ni de su ee.
   - Aun así, con ee(β̂_C) ≈ 2–3,6 frente a δ ≈ 0,27, **(b) no puede activarse con ninguna de las dos reglas** (P = 0,000 en todas
     las filas). Para que se activara, el ee tendría que bajar a ≈ 0,16.
   - El prerregistro debería decir que, en `s1r`, H1 solo puede refutarse por (a). La regla la deciden los autores en F11.
6. **Variante de Volcker más defendible: V3s** [criterio propio].
   - Tiene la misma potencia que V2 (MDE c ≈ 5,3–5,5).
   - Su falsa confirmación bajo el rival es la menor (≤ 0,035 hasta c = 5).
   - Usa la muestra completa para la condición de H0.
   - V1 gana potencia (MDE 3,9–4,4), pero bajo el rival confirma en falso hasta el 14 %, precisamente por Volcker.
   - V3l no añade nada a V1: con la muestra completa confirmada, β̂_C sin Volcker es negativo en prácticamente todas las réplicas
     (§3b: P(confirma) idéntica a la de V1).
   - La elección es de F11.

## 1. DGP (cada elección, documentada)

| Elemento | Elección | Por qué |
|---|---|---|
| Muestras | RR 1969Q1–2005Q2 (146; 73/73 por estado); sin Volcker (133; 62/71); BS 1988Q1–2005Q2 (70) | Encargo y `SAMPLE_COUNTS_S1R.md` |
| Estado | D_{t−1} con la mediana de la muestra completa de cada choque, también sin Volcker y con T/2 | SPEC, Desviación 2026-11-07 |
| Señal | Rampa de TT hasta el pico en h = 10, luego plana; β = coeficiente de ȳ (test) | La misma forma con la que se fijaron β_ref y la ventana (TT p. 11); no sale de los datos |
| Ruido | AR(2) univariante de 100·Δlog `A008RA3Q086SBEA` en cada muestra, sin choques (φ1 = 0,435, φ2 = 0,187, σ_e = 1,724 en RR); residuos remuestreados | Como en F4 |
| het_eps | Var(e_t) ∝ 1 + media_{k=0..12}(ε_{t−k}/sd)², con σ_t entre 0,71 y 2,00 | El error de ȳ_t contiene e_t..e_{t+12}: así las filas de alto apalancamiento son las más ruidosas. Generaliza la prueba de R-F4 a la ventana |
| het_rec | Var ×1,53 en trimestres con Δlog PIB < 0, calibrado en 1969–2005 (18 trimestres) | Segunda forma que pide R-F4. En BS solo hay 4 trimestres así (ρ = 0,2 si se calibrara ahí, puro ruido) |
| Controles | Δlog inversión (simulada), Δlog PIB, Δlog deflactor y Δffr, con 2 retardos | Los de `s1_liq` (EBP, rendimiento a 2 años) no existen antes de 1973–76. **Propuesta para F11** |
| T/2 | Bloque contiguo de 73 filas de la muestra completa; sin Volcker = el bloque menos 1979Q4–1982Q4 | V3 combina las dos muestras con los mismos datos |

## 2. β_ref con Romer-Romer (§0)

- **π_ffr (h = 0)** = 0,949 (ee 0,248), así que **β_ref = −2,5 × 0,767 × 0,949 = −1,820** pp de ȳ por pp de ε. El factor 0,767 es la
  media de la rampa en h = 4..12.
- **Con h = 1**: π = 1,669 y β_ref = −3,198, es decir, ×1,76. R-F4 vio ×1,36 con BS.
- Sin Volcker, π(h=0) = 0,943, prácticamente igual.
- Elijo h = 0 por continuidad con F4 [criterio propio]. **Con h = 1, todos los c de este informe se dividen por 1,76** (MDE de V3s:
  c ≈ 3,1). El MDE en unidades absolutas no cambia: ≈ 10 pp de ȳ por pp de fed funds en V2/V3s, frente a 1,92 en la referencia.

## 3. La composición de pérdidas del Director (§5)

| contraste | c predicho [T§7] | c MC con `base` | c MC con `aum` | pérdida LP/oráculo medida (0..4) | ganancia de ventana medida |
|---|---|---|---|---|---|
| H0 lineal | 1,91–2,23 | 1,98 | 2,31 | 1,30 | 1,40 |
| H1, estado C | 2,70–3,15 | 1,81 | 2,78 | 0,98 | 1,63 |

- **Con `aum`, la predicción se sostiene en H1 y queda ligeramente corta en H0** (2,31 frente a 1,91–2,23).
- Los factores no son los supuestos:
  - la pérdida en H1 es ≈ 1, porque el estado C concentra la varianza del choque, que el oráculo con "mitad de la muestra
    independiente de ε" no recoge;
  - la ganancia de ventana es 1,40–1,63, no 1,34.
- Ojo: estos c usan la desviación típica de β̂ con aproximación normal. **El MDE del árbol completo es 3,9–5,5**, porque añade la
  condición de H0 y el ee conservador. Esa es la cifra que tiene que ir al prerregistro.

## 4. Qué falta y riesgos

- **Decisiones para F11 (Dirección y autores):**
  1. especificación `aum` (o aceptar el sesgo de `base`);
  2. NW(5)+HC3 pese a la sobrecobertura;
  3. V1, V2 o V3;
  4. δ fijo (y decir que (b) no puede activarse);
  5. controles nuevos;
  6. reescribir la expectativa de potencia (0,04–0,10 con β_ref, no 0,2–0,4).
- **La réplica BS no informa:** P(confirma) ≈ 0 para c ≤ 10 y un error de diseño de −67 %. Propongo presentarla como descriptiva.
- **Riesgos:**
  - el error de diseño depende de la forma supuesta (rampa hasta h = 10, permanente); con una IRF que revierte sería menor;
  - el DGP con β_C ≠ β_U deja un sesgo residual en `aum`;
  - los choques sin dato (2008) cuentan como 0 en los adelantos de las dos últimas filas;
  - con 34 regresores y N = 133, la especificación sin Volcker deja 99 g.l.;
  - la cita de Teulings-Zubanov (y la de Montiel Olea–Plagborg-Møller sobre LP aumentadas) está pendiente de Literatura.
- **F10:** el Referee debería auditar sobre todo el error de diseño (§1a), la elección `aum` y la lectura de la sobrecobertura.
