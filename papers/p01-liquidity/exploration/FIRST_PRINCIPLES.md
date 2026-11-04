# Primeros principios de p01 (documento vivo de discusión)

Iniciado el 2026-11-04 por la Coordinación con los autores. Aquí se piensa **qué es plausible** antes de
elegir qué reciclar o qué diseño seguir. Cada afirmación lleva su estado: **[acordado]**, **[propuesta]**
o **[abierto]**.

## 1. Principios
1. **[acordado]** El núcleo son las líneas de TFG1 y TFG2.
2. **[propuesta]** *Conservación:* todo pago es el ingreso de otro. La política no "se pierde": se
   redistribuye hacia agentes con poca propensión a gastar, se atesora (reservas precautorias), se va a
   precios o choca con una restricción. Los dos borradores ya lo incorporan (TFG1: los intereses son
   ingresos de sus tenedores; TFG2: alivio del deudor frente a ingreso del acreedor, al estilo de Auclert,
   2019). El δ de v22 lo violaba.
3. **[propuesta]** *Voluntad frente a capacidad:* la confianza y la coordinación cambian el **nivel** de
   inversión deseada (vía la varianza del proyecto, v). La capacidad (capital bancario N, pignorabilidad
   H, reservas) cambia la **pendiente**, es decir, la respuesta marginal a la política. Por eso más
   confianza puede subir la inversión y a la vez agotar la respuesta a otra bajada de tipos (TFG1).
4. **[propuesta]** *Los regímenes salen de restricciones que a veces muerden.* El régimen es qué
   restricción está activa (λ > 0), no un parámetro que se impone.
5. **[propuesta]** *Velocidades:* la repreciación y los flujos de caja actúan en el trimestre, el capital
   bancario en años y el stock de deuda en una década.

## 2. Resultado formal: TFG1 es un caso límite de TFG2
**Verificado con SymPy el 2026-11-04.** Pasa a `theory/check_*.py` cuando se formalice.

En el régimen restringido de TFG2, la respuesta de la inversión a una bajada del coste de financiación es

$$ I_u=\frac{\gamma^2 p_f + B\,g}{B+\gamma^2 a}=\omega\,\frac{p_f}{a}+(1-\omega)\,g,\qquad
\omega=\frac{\gamma^2 a}{B+\gamma^2 a}, $$

donde:
- $p_f/a$ es la respuesta sin restricción, con $a=b+\eta v+\psi/N$;
- $g=\gamma\,\mathcal E_D$ es el alivio por la deuda que se reprecia dentro del intervalo de pago;
- $B$ es la curvatura del coste de ajustar reservas: cuanto mayor, más rígidas son las reservas.

Casos límite:
- $B\to\infty$ (reservas rígidas): $I_u\to g$. Si además no hay repreciación ($g=0$), $I_u\to 0$, que es
  **exactamente el régimen restringido de TFG1**.
- $B\to 0$ (reservas perfectamente flexibles): $I_u\to p_f/a$. La restricción deja de importar en el
  margen.
- $\partial I_u/\partial g = B/(B+\gamma^2 a) > 0$: la repreciación importa **más cuanto más rígidas son las
  reservas**.

**[propuesta] Una fórmula general.** La transmisión de una economía es una media, ponderada por
régimen, de dos márgenes:
- el de precios ($1/a$, que depende del capital bancario y de la incertidumbre);
- el de flujo de caja ($g$, que depende de la estructura de repreciación de la deuda).

Los pesos dependen de la flexibilidad de las reservas. Agregando, con el multiplicador $M$ y la
redistribución deudor–acreedor:

$$ Y_u \approx M\Big[\underbrace{\textstyle\sum_r \pi_r\,(\omega_r\,\tfrac{p_f}{a}+(1-\omega_r)\,g_r)}_{\text{inversión por régimen}}
+\underbrace{(c_{b}-c_{s})\,\mathcal E}_{\text{redistribución}}\Big] $$

donde $\pi_r$ es la proporción de agentes en cada régimen (holgado / restringido).

## 3. Predicción que nos distingue de la competencia [propuesta]
- **Frente a Ippolito-Ozdagli-Perez-Orive (2018):** el canal de tipo variable importa **de forma
  condicional**. En el régimen holgado, la repreciación no cambia la inversión, solo el consumo vía
  redistribución; en el restringido, sí. Predicción: la interacción shock × exposición a la repreciación
  tiene que ser **mayor cuando las restricciones muerden**.
- **Frente a Perez-Orive-Timmer-van der Ghote (2026):** el margen de reservas precautorias hace que una
  restricción activa **no anule** la transmisión, salvo con reservas rígidas y sin repreciación. Con
  varias restricciones, el mínimo no es todo o nada. *Pendiente: leer su texto completo para confirmarlo.*
- **Frente a Angeletos-Lian-Wolf:** la coordinación actúa por la voluntad (v) y no por la capacidad, así
  que su efecto está acotado por la capacidad. "Necesaria pero no suficiente", ahora derivado y no supuesto.

## 4. Dudas sobre la plausibilidad (resueltas en la sección 6)
1. **Agregación:** desarrollada en la sección 5.
2. **Estática frente a dinámica:** los borradores son de un periodo con precios fijos, y la evidencia (LP)
   mira 4–8 trimestres. ¿Qué parte del mecanismo sobrevive cuando hay inflación y el capital bancario se
   reconstruye?
3. **Coordinación como cointegración:** la representación es elegante, pero supone una tendencia
   estocástica común en las posturas de política. ¿Es plausible en datos de EE. UU.?
4. **Magnitudes:** ¿cuánto puede pesar la incertidumbre de política (v) frente al riesgo de negocio?
   Probablemente poco, lo que acota el efecto de la coordinación. ¿Es esa la conclusión que buscáis?
5. **Medición:** hacen falta proxies de la exposición a la repreciación ($\mathcal E_D$: deuda a tipo variable
   o a corto plazo, ratios de servicio de la deuda), de la capacidad (capital bancario, colateral) y de la
   flexibilidad de reservas (activos líquidos de las empresas, en Z.1). Sin datos de empresas, ¿basta con
   agregados por sectores y países?

## 5. Agregación: de la esquina individual al régimen agregado [propuesta]

**Planteamiento.** Cada agente $i$ tiene una holgura $s_i=H_i-I_i-\gamma m_i$ hasta su restricción. Su respuesta es
$p_f/a_i$ si $s_i>0$ y $\omega_i p_f/a_i+(1-\omega_i)g_i$ si $s_i\le 0$. Integrando sobre la distribución de agentes:

$$ I_u^{agg}=\underbrace{\mathbb E\!\left[\tfrac{p_f}{a}\right]}_{\text{sin fricciones}}
\;-\;\underbrace{\pi\;\mathbb E\!\left[(1-\omega)\Big(\tfrac{p_f}{a}-g\Big)\,\Big|\,s\le 0\right]}_{\text{efecto de las restricciones}},
\qquad \pi=F_s(0). $$

**Consecuencias:**
1. **El régimen agregado no es un interruptor, es una proporción** ($\pi$, la parte de agentes restringidos).
   Se mueve de forma continua con la distribución de holguras. Su "brusquedad" depende de la **densidad de
   agentes cerca de la restricción**, $f_s(0)$: con mucha dispersión, la transición es suave; con poca, casi
   un umbral.
2. **Micro-fundamento de la smooth transition.** La función de transición logística de una LP o un VAR de
   transición suave **es** (aproximadamente) la CDF de la holgura, y su pendiente es la inversa de la
   dispersión. Elegir entre umbral y transición suave deja de ser una elección técnica: es una hipótesis
   económica sobre la dispersión, y se puede estimar.
3. **Las restricciones no siempre atenúan.** El signo del segundo término depende de
   $\mathbb E[p_f/a-g\mid s\le 0]$. Si los restringidos tienen mucha deuda que se reprecia ($g>p_f/a$), la
   restricción **amplifica** la bajada de tipos. Coincide con la ilustración de TFG2 (con repreciación
   completa, la derivada sube al entrar en el régimen restringido).
4. **Importa la covarianza, no los promedios.** La respuesta agregada depende de la exposición a la
   repreciación **de los restringidos**, no de la media. Si las empresas que dependen de los bancos
   (restringidas) son también las que tienen deuda a tipo variable, cosa plausible, el canal de flujo de
   caja agregado es mayor que "proporción restringida × repreciación media". Es la misma lección que el
   error de v22: multiplicar índices agregados ignora la covarianza de los productos micro.
5. **Asimetría.** Una subida de tipos aumenta $\pi$ (empuja agentes hacia la restricción) y una bajada lo
   reduce, así que subir y bajar no son simétricos. Cuadra con el resultado de Perez-Orive et al. (subir pesa
   más que bajar).

**¿Cuándo hay cambios agregados bruscos de verdad?** Solo si la distribución se concentra o se
sincroniza:
- **Restricciones que son agregadas por naturaleza:** el capital del sistema bancario (pocos bancos grandes
  e interconectados) o el suelo de tipos. Una sola restricción común produce una esquina agregada nítida.
- **Realimentación de equilibrio general:** cuando unos se restringen, cae el precio del colateral y se
  restringen otros (tipo Kiyotaki-Moore, ventas forzadas). Eso sincroniza holguras y crea saltos, quizá
  equilibrios múltiples. Es la economía de las crisis.

**Predicción contrastable [propuesta]:** la transición respecto al **capital bancario** debería ser
abrupta (casi un umbral) y la transición respecto al **apalancamiento de empresas y hogares**, suave. En
tiempos normales los regímenes cambian de forma gradual; los saltos solo aparecen con realimentación sistémica.

**Medición sin datos de empresas [abierto]:** $\pi$ se puede aproximar con medidas que ya son
proporciones:
- la proporción neta de bancos que endurecen el crédito (SLOOS);
- la distribución de los ratios de servicio de la deuda entre países (BIS);
- los activos líquidos de empresas por sector (Z.1).

En el panel internacional, cada país aporta su propio $\pi$.

## 6. Resolución de las dudas (Coordinación, 2026-11-04) [propuesta firme]

Criterio: entre las alternativas, la más defendible ante un referee de una revista de macro. Cada punto
indica qué se descarta y por qué.

**6.1 Agregación → régimen como proporción, con transición suave estimada.**
- *Alternativas:* umbral (TVAR o LP con umbral), Markov-switching, transición suave.
- *Elección:* transición suave cuya función de transición se interpreta como la CDF de la holgura (§5),
  con su pendiente **estimada**. El umbral queda como caso límite (pendiente → ∞), así que se contrasta en
  lugar de imponerse.
- *Descartado:* Markov-switching como especificación principal. Sus regímenes son latentes, y con T
  pequeño se identifican mal: es el mismo problema que v22, regímenes inferidos del propio output.

**6.2 Estática frente a dinámica → dos escalas de tiempo.**
- El modelo de un periodo (TFG1/TFG2) da la respuesta **de impacto, condicionada a estados
  predeterminados**. Eso es justo lo que estima una LP condicionada a estados en t−1.
- Las predicciones del mecanismo se contrastan en horizontes cortos (h = 0–4 trimestres). Los horizontes
  largos mezclan la propagación de los propios estados (capital bancario, deuda) y se presentan como
  propagación, no como prueba del mecanismo.
- *Descartado:* construir un DSGE dinámico completo. Vuelve al problema de v22: muchos parámetros y poca
  identificación.

**6.3 Coordinación → incertidumbre de política medida directamente, no la brecha cointegrada.**
- En los dos borradores, la coordinación actúa sobre la inversión **solo** a través de la varianza del
  proyecto, v. Entonces el objeto relevante es la incertidumbre de política, y se puede **medir**:
  - índices EPU de Baker-Bloom-Davis, con su componente fiscal y monetario;
  - incertidumbre de política monetaria implícita en mercados.
- La representación por cointegración queda como resultado teórico, no como estrategia empírica: la
  tendencia estocástica común de las posturas de política es una hipótesis frágil y depende de cómo se
  construyan esas posturas (lección de v22).

**6.4 Magnitud de la coordinación → acotada, y es un resultado.**
- Con la inversión deseada $q/a$ y $a=b+\eta v+\psi/N$, la elasticidad respecto a $v$ es $\eta v/a$. Eliminar
  **toda** la incertidumbre de política mueve la inversión deseada como mucho en una fracción
  $\eta v_{pol}/a$.
- Con la calibración de TFG2 ($b=\eta=1$, $v=0.05$, $\psi=0.5$, $N=1$; $a=1.55$), la cota es ≈ 3 %
  **aunque toda la varianza fuera de política**.
- La coordinación es un efecto de segundo orden **acotado por la capacidad**. "Necesaria pero no
  suficiente" pasa a ser un resultado cuantitativo derivable. Se contrastará con la EPU.

**6.5 Medición e identificación → panel de la zona euro con shock común, más EE. UU.**
- **Diseño más defendible:** un shock monetario común (Jarociński-Karadi para el BCE, ya en el datalake)
  que llega a países con **distinta** exposición a la repreciación y distinta capacidad.
  - Es exógeno para cada país (el BCE no fija su política por un país pequeño).
  - Hay mucha más variación de regímenes que en una sola serie de EE. UU.
  - Permite comparar efectos dentro del mismo shock, tipo diferencias en diferencias.
- **Exposición a la repreciación ($\mathcal E_D$):** se mide como la **transmisión empírica del tipo
  oficial al tipo medio pagado sobre el stock de deuda** (tipos MIR sobre saldos vivos, por país y sector).
  Es el objeto exacto de TFG2: la parte de la deuda que se reprecia dentro del intervalo. Es mejor que la
  cuota de préstamos variables, que la API del BCE no da por país en volúmenes (comprobado: solo hay tipos
  por fijación). Los ratios de servicio de la deuda del BIS sirven de contraste.
- **Capacidad:**
  - capital bancario por país (BCE/BIS);
  - pignorabilidad: precios de la vivienda y endeudamiento (BIS);
  - flexibilidad de las reservas: activos líquidos de empresas (cuentas financieras).
- **EE. UU.** (Bauer-Swanson, Z.1, SLOOS, EBP) aporta la variación temporal y la mejor identificación del
  shock.
- *Descartado:* datos de empresas (no hay sin WRDS) y depender solo de EE. UU. (repite el problema de
  pocos datos de v22).

**6.6 Predicciones centrales que salen de esto (candidatas al prerregistro; deciden los autores):**
1. La respuesta del output y la inversión a un shock monetario común es mayor en países y periodos con más
   exposición a la repreciación, **pero sobre todo cuando las restricciones muerden** (interacción triple
   shock × exposición × restricción).
2. Con capacidad bancaria baja, la respuesta cae, con una transición más abrupta respecto al capital
   bancario que respecto al endeudamiento.
3. Subir y bajar tipos son asimétricos, y la asimetría es mayor cuanto más cerca está la economía de las
   restricciones.
4. La incertidumbre de política mueve el nivel de la inversión, pero su efecto sobre la respuesta marginal
   está acotado por la capacidad.

## 7. Registro de la discusión
- 2026-11-04 · Los autores piden filosofar antes de elegir. Acordado: el núcleo son TFG1 y TFG2. La
  Coordinación propone la conservación, voluntad frente a capacidad, los regímenes como restricciones
  activas y la unificación TFG1 ⊂ TFG2 (verificada).
- 2026-11-04 · Agregación (sección 5): el régimen agregado es una proporción de agentes restringidos; los
  saltos requieren concentración o realimentación sistémica.
- 2026-11-04 · Los autores piden que la Coordinación no pregunte pasos intermedios. Se resuelven las dudas (sección 6): transición suave estimada, dos escalas de tiempo, coordinación medida por incertidumbre de política (acotada ≈3 %% con la calibración de TFG2), panel de la zona euro con shock común del BCE y exposición medida por la transmisión al tipo del stock de deuda.
