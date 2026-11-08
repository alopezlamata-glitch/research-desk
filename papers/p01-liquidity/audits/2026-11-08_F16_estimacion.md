---
verdict: APROBADO
object: "Estimación de la etapa 1 rediseñada s1r_* y robustez r1r_* con la inversión real (F16)"
date: 2026-11-08
commit: 1c98c81
reviewer: referee
session: fresh
---
## Resumen
He auditado la estimación de F16 en el commit 1c98c81 contra el prerregistro congelado (`prereg_commit: 3d6b508`, huella
`prereg 1d9476332d29`). Se ejecutó exactamente lo congelado: el código de análisis y el de R son los de bd4f7bc, los datos no han
cambiado y `spec_log.csv` registra una sola ejecución con los 7 ids. Mi réplica, escrita en Python sin importar nada de `code/`,
reproduce los 244 coeficientes y errores (los 3 `s1r_*` y los 4 `r1r_*`) con una diferencia máxima de 1,0·10⁻¹². El veredicto
`h0_falla` se sigue de la regla escrita, y la cifra que decide es β̂_lin = −1,655, con p unilateral 0,178. El informe no presenta
β̂_C como evidencia de H1 ni propone cambiar la regla. Hay tres hallazgos menores, todos de presentación en
`output/F16_RESULTADOS.md`; ninguno afecta a las estimaciones ni al veredicto.

## Comprobaciones que pasan (una línea cada una)
- **El código no cambió desde bd4f7bc.** `git diff bd4f7bc 1c98c81 --stat -- papers/p01-liquidity/code/analysis papers/p01-liquidity/code/replication_r tools`
  sale vacío. En `data/` solo cambia `DICTIONARY.md`, con 25 líneas añadidas para QFR/F14a. `git diff 1c98c81 -- code data output` también sale vacío.
- **La SPEC no se tocó después de congelarla.** `git diff 3d6b508 1c98c81 -- SPEC.md` cambia una sola línea, `prereg_commit: af1c346 → 3d6b508`,
  la que lo congela. `integrity.py` (check `prereg`) da OK.
- **Muestra.** N = 146 (1969Q1–2005Q2), 133 sin Volcker y 136 desde 1971Q3. `rr_shock` no tiene ningún dato antes de 1969Q1, y los
  NaN cuentan como 0 en los retardos y adelantos (`SPEC.md:70-79`; `01_s1r_estimate.py:70-72`; `s1r_lp.py:50`).
- **Controles, `aum` y errores estándar.** Hay 4 controles con 2 retardos (4 en `r1r_lags4`), ε_{t−1..t−10} y ε_{t+1..t+12} sin
  interactuar, y NW(5) de Bartlett en trimestres naturales con residuos HC3, sin N/(N−k), con t de N−k g.l. Todo como en `SPEC.md:85-93,119-120`.
  Los g.l. cuadran: 146−32 = 114, 146−34 = 112, 133−34 = 99, 136−34 = 102 y 146−42 = 104.
- **Los 7 ids son los del bloque ```prereg``` (`SPEC.md:202-212`).** `output/spec_log.csv:2-8` los tiene todos con
  `preregistered=True` y `exploratory=False`, una sola marca de tiempo (12:28:20–21) y la huella 1d9476332d29. `research.log_spec`
  añade filas sin borrar (`tools/research.py:59`, modo `"a"`), y el archivo solo tiene un commit (1c98c81): no hay ejecuciones escondidas.
- **Datos.** Los SHA-256 de `A008RA3Q086SBEA`, `GDPC1` y `GDPDEF` coinciden con `data/raw/MANIFEST.csv:7,8,16`. He reconstruido
  s = log(liq) − media de los 12 trimestres anteriores desde `liq_broad_debt`: diferencia máxima 4,4·10⁻¹⁶, y s_lag = s_{t−1} exacto.
- **La paridad Python–R del autor** es correcta: `integrity.py` (check `parity`) da OK.
- **El estimador está validado.** El Monte Carlo es F9, auditado en F10 (`audits/2026-11-08_F9_mc.md`), y el script es el mismo
  estimador del MC (`test_s1r_estimate.py`).

## Puntos del encargo

### 1. Se ejecutó lo congelado — sin hallazgos
Lo cubren las comprobaciones de arriba.
Evidencia: `git diff bd4f7bc 1c98c81 --stat -- papers/p01-liquidity/code/analysis papers/p01-liquidity/code/replication_r`
(vacío) y `output/spec_log.csv:2-8`.

### 2. El veredicto `h0_falla` se sigue de la regla — sin hallazgos
- Paso 1 (`SPEC.md:148-150`): β̂_lin = −1,654695, ee = 1,785946, g.l. = 114, t = −0,927, p unilateral = 0,1781 ≥ 0,05.
  **H0 no se confirma**, así que el árbol se detiene en "H0 no se confirma".
- `s1r_lp.decide` devuelve `h0_falla` en cuanto `h0_full=False` (`s1r_lp.py:85-86`), sin mirar H1.
- Mi réplica implementa el árbol desde el texto de la SPEC, sin `decide`, y da el mismo resultado.
- Contrafactual, solo para comprobar que el código no falla en silencio: aunque H0 hubiera pasado, β̂_C = −2,874 (p = 0,042) y
  β̂_C sin Volcker = −4,981 (p = 0,040) habrían dado `confirma` con V3s. Por eso importa que la puerta H0 se aplique y que
  nadie la reinterprete (punto 3).

Evidencia: `uv run python papers/p01-liquidity/audits/replication_2026-11-08b/replicate_s1r.py` ("veredicto V3s (réplica):
h0_falla"); `output/tables/s1r_estimates.md:7,21`.

### 3. Cómo se lee β̂_C — correcta, con dos matices de redacción (menor)
**Lo que está bien.**
- El informe dice que H1 «no se interpreta. Ni se confirma, ni se refuta, ni es "no concluyente"» (`F16_RESULTADOS.md:32`).
- Descarta evaluar los pasos 2 y 3 (`:106`).
- Avisa de que cualquier otro uso «sería una Desviación posterior a ver los datos» (`:116`).
- No propone ninguna especificación ni ningún cambio de regla.
- **"Medición sin veredicto" es la expresión correcta**: es literalmente la de `SPEC.md:149`, que obliga a publicar β̂_C, β̂_U y sus
  IC cuando falla H0. Un p unilateral < 0,05 de un coeficiente cuyo contraste no forma parte de ningún veredicto es una cifra
  descriptiva. No es «significativo» en el sentido del prerregistro, y el informe no usa esa palabra.

**Matiz (a): énfasis selectivo en el HANDOFF.** El «hecho que deben tener a la vista» (`F16_RESULTADOS.md:112-115`) da el p < 0,05
de β̂_C en `s1r_liq` y `s1r_liq_nov`, pero no dice que en dos de las cuatro robusteces no se mantiene:
- `r1r_from1971q3`: β̂_C = −2,035, p = 0,152. Es la que quita las filas cuyos retardos del choque son ceros imputados, y β̂_C cae
  un 29 %.
- `r1r_lags4`: β̂_C = −2,219, p = 0,082.

La tabla completa está en el §4 del mismo informe. Aun así, el resumen que se escala a la Dirección y a los autores debería darla
entera: «p < 0,05 en 2 de 2 principales y en 2 de 4 robusteces (q25, logística); p = 0,15 y 0,08 en las otras dos». Sin eso, el
lector del HANDOFF se queda con una imagen más favorable a H1 de la que dan los datos.

**Matiz (b): «pero sus IC al 95 % contienen el 0»** (`:114`). Es cierto, pero junta un contraste unilateral al 5 % con un IC
bilateral al 95 %. Lo que corresponde al contraste unilateral es el IC bilateral al 90 % (o la cota superior unilateral al 95 %),
que excluye el 0 en esas dos filas. La frase no es errónea y empuja hacia la cautela, pero conviene escribirla sin dar a entender
que hay una contradicción.

**Cómo se resuelve:** reescribir esas dos líneas del HANDOFF al escalar. No cambia ninguna cifra ni el veredicto.

Evidencia: `output/F16_RESULTADOS.md:112-116`; `output/tables/s1r_estimates.md:12,18` (from1971q3 p = 0.152; lags4 p = 0.082).

### 4. Diagnósticos de los choques — correctos, y su consecuencia es la que fija la SPEC (una nota menor)
- Mi réplica reproduce D1–D3, Ljung-Box y predictibilidad con todos los decimales publicados:
  - muestra completa: LB = 16,78 (p = 0,158), DP F(12,133) = 1,07 (p = 0,391), D3 p = 0,606;
  - sin Volcker: LB = 22,86 (p = 0,029), DP F(12,120) = 1,66 (p = 0,085), D3 p = 0,613.
- Coinciden con las cifras ex ante de `SPEC.md:106-109`.
- La consecuencia que aplica el informe (`F16_RESULTADOS.md:43-46`) es la de `SPEC.md:110-115`: no cambian ni la especificación ni
  el veredicto, y a `s1r_liq_nov` se le añade la salvedad del estimando de choque aislado frente a β_ref.
- **Nota menor:** el Ljung-Box sin Volcker concatena 1979Q3 con 1983Q1 (lo declara la cabecera de `s1r_shock_diagnostics.md:3`).
  Es la misma convención de F13, con la que se escribió la cifra ex ante, así que no hay inconsistencia. No requiere acción.

Evidencia: `output/tables/s1r_shock_diagnostics.md:7-8`; salida del script de réplica (líneas «completa:» y «sin Volcker:»).

### 5. Las dos lecturas de implementación de F15 en la robustez — razonables (menor)
**`r1r_state_logistic`: z estandarizada.**
- Sin estandarizar, con γ = 3 y sd(s_{t−1}) = 0,0883, F(s) queda en [0,353; 0,640]: casi constante e indistinguible de un modelo
  sin estado, que no es lo que pide «D_{t−1} sustituido por F(s_{t−1})» (`SPEC.md:183`).
- Estandarizada, F recorre [0,001; 0,999], con media 0,494 y corr(F, D_mediana) = 0,916: es un sustituto suave de D, que es lo que
  busca el texto.
- La lectura de F15 es la única que da sentido a «γ = 3 fijo» y está bien orientada (F → 1 con poca liquidez).
- **Límite:** no he comprobado en el PDF de Tenreyro-Thwaites que su z tenga varianza unitaria. Si el paper atribuye la
  estandarización a TT, que lo verifique Literatura.

**`r1r_from1971q3`: mediana de la muestra completa.**
- Es coherente con la regla general del estado (`SPEC.md:81-83`: «mediana … en la muestra completa de cada choque»; «no se
  recalcula en la muestra sin Volcker») y con «solo se quitan filas» (`SPEC.md:73-74`).
- Si la mediana se recalculara desde 1971Q3 (−0,00086 en vez de −0,01014), cambiarían de estado 5 de las 136 filas. La diferencia
  es pequeña, y la lectura escrita es la más fiel al texto.
- He hecho esta comprobación solo sobre el estado, sin estimar nada con la inversión.

Las dos afectan solo a la robustez, que no decide.

Evidencia: `code/analysis/01_s1r_estimate.py:75-79`; salida del script de réplica (líneas «logística:» y «r1r_from1971q3:»).

### 6. Replicación independiente — ver la sección Replicación
Evidencia: `uv run python papers/p01-liquidity/audits/replication_2026-11-08b/replicate_s1r.py`

### 7. Integridad y tests
- `uv run python tools/integrity.py` → `integridad: OK`. Ejecutado sobre HEAD 64c5450, que solo añade el encargo F17 y una línea de
  TASKS a 1c98c81.
- `uv run pytest papers/p01-liquidity -q` → `100 passed in 69.58s`.

Evidencia: `uv run python tools/integrity.py` y `uv run pytest papers/p01-liquidity -q`

## Hallazgos
### Énfasis selectivo de β̂_C en el HANDOFF que se escala — menor
El resumen que se escala da p < 0,05 de β̂_C en las dos muestras principales, pero no dice que en `r1r_from1971q3` (p = 0,152) y en
`r1r_lags4` (p = 0,082) no se mantiene. Lo resuelve reescribir las líneas 112-115 de F16_RESULTADOS con las 6 filas de b_C, o que
la Coordinación las incluya al escalar. Ver el punto 3(a).
Evidencia: `output/F16_RESULTADOS.md:112-115` frente a `output/tables/s1r_estimates.md:12,18`

### Contraste unilateral frente a IC bilateral al 95 % en la misma frase — menor
«p unilateral < 0,05 … pero sus IC al 95 % contienen el 0» compara objetos con niveles distintos. Lo resuelve citar el IC al 90 % o
la cota unilateral al 95 % junto al p unilateral. Ver el punto 3(b).
Evidencia: `output/F16_RESULTADOS.md:113-114`

### Una cita de la SPEC fuera de su rama del árbol — menor
§5 cita `SPEC.md:161` («un NO CONCLUYENTE … nunca como ausencia de efecto») para el caso `h0_falla`. La conclusión es correcta por
sí misma: el IC de β_lin, [−5,193; 1,883], contiene el 0 y β_ref = −1,820. Pero la línea citada habla de otra rama del árbol, así
que conviene apoyarse en el IC y no en esa cita.
Evidencia: `output/F16_RESULTADOS.md:63` y `SPEC.md:161`

## Replicación
- **Script propio:** `audits/replication_2026-11-08b/replicate_s1r.py`. Está escrito desde la SPEC y no importa `s1_lp`, `s1r_lp`,
  `01_s1r_estimate.py` ni la réplica en R del autor.
- **Datos:** `data/clean/stage1r_us.parquet` y los CSV de FRED en `data/raw/stage1_us`, con el hash comprobado contra el MANIFEST.
- **Estimación:** coeficientes por QR (`numpy.linalg.lstsq`), contrastados con `statsmodels.OLS` (rtol 1e-10). Palanca h_ii = Σ Q²,
  sin invertir X'X. NW(5)+HC3 y el árbol V3s escritos a mano.
- **Salidas:** `audits/replication_2026-11-08b/estimates_referee.csv` y `run.log`.
- **Comparado:** las 244 filas (spec_id, term) de `estimates_py.csv` y `estimates_py_robustness.csv`. No sobra ni falta ninguna, y
  los g.l. coinciden en todas.

| bloque | filas | máx \|Δβ̂\| | máx \|Δee\| |
|---|---|---|---|
| `s1r_*` (3 ids) | 100 | 3,0·10⁻¹³ | 2,8·10⁻¹³ |
| `r1r_*` (4 ids) | 144 | 2,3·10⁻¹³ | 1,0·10⁻¹² |

- **Resultado: coincidencia muy por debajo del 6.º decimal.** Los términos que deciden, con 6 decimales:
  - β̂_lin = −1,654695 (ee 1,785946);
  - β̂_C = −2,874478 (1,652526);
  - β̂_C sin Volcker = −4,981010 (2,814243).
- También reproduzco el veredicto (`h0_falla`) y los diagnósticos de los choques.
- Con esto, los `r1r_*`, que el autor no replicó en R (`F15_REQUISITOS.md:60-62`), quedan replicados con código independiente.

Evidencia: `uv run python papers/p01-liquidity/audits/replication_2026-11-08b/replicate_s1r.py`

## Pendiente para el Director científico y los autores (no es un hallazgo ni una propuesta de rescate)
- La SPEC escala `h0_falla` al Director científico (`SPEC.md:148-150`). Era el resultado más probable ex ante, incluso con un
  efecto del tamaño de β_ref: P = 0,824 / 0,854 (`SPEC.md:166`).
- Cualquier análisis que tome el patrón de β̂_C como punto de partida sería posterior a ver los datos y exploratorio. Eso incluye
  quitar la puerta H0, usar β_C − β_U, `aumi` o la IRF.
- Si se decide hacerlo, tiene que ir como Desviación fechada que aprueben los autores, y presentarse con las 6 filas de b_C
  (incluidas las dos robusteces que no pasan) y con el MDE de unos 10 pp de ȳ por pp de choque.

## HANDOFF
**Hecho.**
- Auditoría de F16 en 1c98c81: **APROBADO**.
- Se cubren los puntos 1–7 del encargo.
- Réplica independiente de los 7 ids, con diferencia máxima de 1,0·10⁻¹².
- F17 queda marcada en `TASKS.md` y hay una lección candidata en `kb/lessons/referee.md`.
- Sin commit, como pide el encargo.

**Evidencia.**
- Este informe.
- `audits/replication_2026-11-08b/{replicate_s1r.py, estimates_referee.csv, run.log}`.
- `integridad: OK`.
- `100 passed`.

**Decisiones y quién las tomó.** Ninguna de diseño. El veredicto del Referee se basa solo en la evidencia citada.

**Supuestos y límites.**
- No he verificado en el PDF de Tenreyro-Thwaites que su z tenga varianza unitaria (punto 5).
- Afirmo que hubo una sola ejecución por el `spec_log` de solo-añadir y su único commit. Una ejecución previa cuyo log se hubiera
  borrado a mano antes del commit no sería detectable desde git.

**Pendiente.**
- Que la Coordinación escale `h0_falla` con el resumen completo de b_C (hallazgo 1).
- Que el Director científico y los autores decidan qué sigue tras «H0 no se confirma».
- La aprobación caduca si cambian `code/`, `data/`, `output/` o `SPEC.md` del paper después de 1c98c81.
