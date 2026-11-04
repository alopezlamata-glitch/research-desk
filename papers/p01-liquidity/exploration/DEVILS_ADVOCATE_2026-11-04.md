# Abogado del diablo sobre `FIRST_PRINCIPLES.md` (p01) · 2026-11-04

Autor: Director científico (sesión `desks/direccion-cientifica/`). Encargo: `desks/direccion-cientifica/ENCARGO_2026-11-04_abogado-del-diablo.md`.
Lo que se ataca: `exploration/FIRST_PRINCIPLES.md` (sobre todo §2, §3, §5, §6). No se ha editado.
Marco **[criterio propio]** para lo que es juicio mío y no un hecho leído.

## 0. Cómo leer este informe

**Qué he leído (texto completo, con página).** "p. N" es el marcador `<!-- p. N -->` de `kb/library/md/<clave>.md`
(página del PDF). Los borradores se citan por línea del `.tex`.

| Fuente | Qué es el archivo | Lectura |
|---|---|---|
| Perez-Orive-Timmer-van der Ghote 2026 | FEDS 2026-021 | cuerpo hasta §5 completo (pp. 2–22); modelo cuantitativo (§6) solo el inicio |
| Ippolito-Ozdagli-Perez-Orive 2018 | FEDS 2017-026 | §1–2 y §4.4–6 completos; Tablas solo por el texto |
| Auclert 2019 | NBER 23451 (2017) | §3 (Teorema 3), §3.4, §5.3–5.5 completos; §4 (medición) no |
| Jeenas 2026 | WP UPF/BSE de 2023 (**no** la versión JPE) | §1–2 completas; modelo (§3–5) no |
| Ottonello-Winberry 2020 | **Diapositivas** (seminario Chicago Booth, feb-2017), no el paper | completas; "p." = nº de diapositiva. Sin texto de apoyo, no puedo verificar definiciones |
| Jarociński-Karadi 2020 | ECB WP 2133 (2018) | resumen, §5 (zona euro) y §5.3 completos; el resto no |
| Bauer-Swanson 2023 | NBER 29939 | resumen, introducción, §5.5 y conclusión; el resto no |
| JST 2020, Jungherr et al. 2024, Tenreyro-Thwaites 2016 | WP | solo resumen e introducción |

**No leídos:** Angeletos-Lian-Wolf (ni la versión Zhang) → **no puedo evaluar la comparación del §3 de FIRST_PRINCIPLES con ellos**.
Abadi-Brunnermeier-Koby y Wang (capital bancario) tampoco.

**Datos:** `datalake/CATALOG.md` y el contenido real de `datalake/raw/ecb/csv/`. No pude ejecutar Python en esta sesión
(la herramienta pedía aprobación), así que las cuentas de §2.4 y la agregación de §2.3 son a mano y **sin verificación con SymPy**.

## 1. Veredicto por afirmación

Escala: **se sostiene** / **debilitada** / **refutada**.

### §1 Principios
| # | Afirmación | Veredicto | Razón y evidencia |
|---|---|---|---|
| 1.2 | Conservación (todo pago es ingreso de otro) | **se sostiene** | TFG1 l. 200–207 (identidad de ahorro); Auclert, Teorema 3 y eqs. (17)–(18), pp. 19–20. Matiz: vale en economía cerrada y consolidada; el propio Auclert avisa de que con bancos, firmas y resto del mundo los saldos no se netean (p. 23). |
| 1.3 | La voluntad (v) cambia el **nivel**; la capacidad (N, H) cambia la **pendiente** | **debilitada** | En ambos borradores `a = b + ηv + ψ/N`: **v entra en la pendiente** (∂T_I/∂v = −η/a², TFG1 l. 400–406) y **N entra en el nivel** (∂I/∂N = qψ/(N²a²), TFG1 l. 463). "Más confianza sube la inversión y agota la respuesta" solo ocurre cuando I llega al tope H(D) (TFG1 l. 428–440): es el tope, no una división voluntad/capacidad. |
| 1.4 | Los regímenes son restricciones que a veces muerden | **se sostiene** | Es la estructura de IOPO (pp. 10–11), Perez-Orive et al. (p. 12) y los dos borradores. No es nuevo, pero es correcto. |
| 1.5 | Velocidades: repreciación en el trimestre, capital bancario en años, deuda en una década | **no evaluada** | No hay evidencia en lo que he leído; es plausible **[criterio propio]**. |

### §2 "TFG1 es un caso límite de TFG2" y "fórmula general"
| Afirmación | Veredicto | Razón y evidencia |
|---|---|---|
| El álgebra: `I_u = ω p_f/a + (1−ω) g`, ω = γ²a/(B+γ²a) | **se sostiene** | Es **literalmente** la Proposición `fs-transmission` de TFG2 (l. 342–356) y su eq. (`weighted-response`, l. 650–657, con ϑ_F = ω). La comprobación es álgebra de una línea. |
| "Verificado con SymPy el 2026-11-04" | **no verificable** | No hay `theory/check_*.py` que la contenga (solo existe `check_debt_absorption.py`). Regla de CLAUDE.md: sin script, la proposición no entra en el paper. |
| El resultado es **nuevo** | **refutada** | (a) Ya está en TFG2 con el mismo ω. (b) TFG2 ya dice que el cero de TFG1 solo es "un caso límite" y que no se debe asignar "transmisión cero a todo prestatario restringido" (l. 358–359, 659). (c) El caso rígido es **exactamente IOPO**: restringido ⇒ `K1 = N1 + b̄` (IOPO p. 11, eq. 7) y `N1 = f(K0) − r_c B0 − r1 L0` (p. 10, eq. 2) ⇒ ∂K1/∂r1 = −L0, es decir, I_u = g con repreciación plena. |
| TFG1 ⊂ TFG2 **importa económicamente** | **debilitada** | Como nido de modelos, sí. Como hecho económico, importa poco: el límite B→∞ es formal. En el modelo `B = κ_F·Q(z_F)` (TFG2 l. 283) está **acotado por κ_F** (=1 en la calibración); el cero de TFG2 exige "reserva con cota activa o buffer fijo" (l. 358), un **extremo**, no B→∞. Lo que se salva de TFG1 es la cota de capacidad (ver 6.4), no el min{}. |
| "Fórmula general": la transmisión es una media ponderada de un margen de precios y uno de flujo de caja | **debilitada** (novedad) | Es la dicotomía de IOPO (restringido: fondos internos; no restringido: regla neoclásica, pp. 10–11) y la descomposición de Auclert (Teorema 3, p. 20: sustitución + renta + tres canales redistributivos). Lo único nuevo es el margen interior de reservas `m`. |
| La agregación `Y_u ≈ M[Σπ_r(…) + (c_b−c_s)E]` | **debilitada** | Ver 2.3 abajo. Además `(c_b−c_s)E` trata al acreedor como hogar; en la zona euro el acreedor es un banco y la pérdida de intereses va a **N**, que entra en `a` (TFG1 l. 496: el propio borrador lo menciona y lo deja fuera). Auclert p. 23: las exposiciones indirectas por firmas y bancos son difíciles de medir. |

### §3 "Predicción que nos distingue"
| Afirmación | Veredicto | Razón y evidencia |
|---|---|---|
| Frente a IOPO: el canal de tipo variable importa **de forma condicional** (solo restringidas) | **refutada** (como diferencia) | IOPO ya lo predice y lo contrasta: el tipo flotante sube la sensibilidad de la inversión de las restringidas y **no** la de las no restringidas (Prop. 1(ii), p. 11); "las restricciones solo importan cuando la firma está expuesta al riesgo de tipos" (p. 36, Tabla VII); inversión fija y existencias (pp. 37–41). Con el aviso propio de IOPO de que lo real es "sugerente" y puede tener endogeneidad (p. 41). |
| Frente a Perez-Orive et al.: "una restricción activa **no anula** la transmisión" | **refutada** (como diferencia) | Ellos nunca dicen que la anule: con restricción activa la respuesta es `max/min |∂G_j/∂R|` (Prop. 1, p. 12), positiva en ambos sentidos; lo que predicen es que **se atenúa** la bajada y **se amplifica** la subida (resumen, p. 2; datos, p. 20). |
| Frente a Angeletos-Lian-Wolf | **no evaluable** | No leído. |
| El mismo bloque omite a **Jeenas** | **observación** | Jeenas ya tiene el margen de liquidez: "los tipos de la deuda son irrelevantes como coste de oportunidad" si la firma tiene caja (p. 4); la liquidez predice la respuesta más allá del apalancamiento (p. 4) y el canal pasa por la probabilidad de emitir deuda (p. 17); en agregado la transmisión se **amortigua ligeramente** (resumen p. 2, p. 3) y pesa la rentabilidad de la caja (pp. 5–6). Es el competidor más cercano del margen de reservas. |

### §5 Agregación
| Afirmación | Veredicto | Razón |
|---|---|---|
| 5.1 El régimen agregado es una proporción π, no un interruptor | **se sostiene** (algebra) | Pero el algebra supone agentes independientes; ver 2.3. |
| 5.2 La función logística de una LP/STAR **es** la CDF de la holgura; su pendiente es 1/dispersión | **debilitada** | Exige: holguras con un desplazamiento común (location shift) y forma conocida; dispersión **constante** en el tiempo; y respuestas (ω_i, g_i) independientes de s_i, lo que **contradice §5.4** (la covarianza importa). Además γ de una STAR con ~110 observaciones está casi no identificado **[criterio propio]**, el mismo mal de v22 (diagnóstico, mayor nº 1: θ débilmente identificado). |
| 5.3 Las restricciones pueden amplificar (g > p_f/a) | **se sostiene** (algebra) | **Pero es una amenaza** (ver 2.1): el signo no se predice. |
| 5.4 Importa la covarianza, no los promedios | **se sostiene** | Auclert, Teorema 3 (p. 20): los canales redistributivos son covarianzas. |
| 5.5 Asimetría: subir ≠ bajar | **se sostiene**, **no es nueva**, y el mecanismo es otro | Perez-Orive et al. (Prop. 1, p. 12; datos pp. 19–21, ASC 842 p. 22); Auclert (p. 7 y p. 40, vía prestatarios al límite de crédito); Tenreyro-Thwaites (resumen, p. 2). Con **una** restricción, Perez-Orive muestran que la derivada local es simétrica (p. 12); en el modelo de TFG1 la asimetría solo aparece para choques finitos que cruzan el codo (tope H). Es un mecanismo distinto del de ellos (varias restricciones), y FIRST_PRINCIPLES dice que "cuadra" sin mostrarlo. |
| "Predicción: la transición respecto al capital bancario es abrupta" | **debilitada** (no derivada) | En el modelo, N entra **suave**: `T_I = N/(ψ+(b+ηv)N)` (TFG1 l. 233). No hay umbral en N; los únicos codos son del tope H(D). Un umbral en N exige añadir una restricción regulatoria de capital que ningún borrador tiene. |

### §6 Resoluciones
| Afirmación | Veredicto | Razón y evidencia |
|---|---|---|
| 6.1 Transición suave estimada; Markov descartado | **debilitada** | Ver 5.2. El descarte del Markov es razonable. |
| 6.2 El modelo de un periodo da "la respuesta de impacto condicionada a estados" que estima una LP en t−1 | **debilitada** | Los choques identificados son **persistentes** (en BS el rendimiento a 2 años salta y tarda varios años en volver a su nivel, BS p. 53); IOPO supone r2 sin cambiar y lo flexibiliza solo en el modelo dinámico (p. 10, nota 8); Auclert (pp. 40–41) muestra que con persistencia el reparto entre sustitución y redistribución **cambia**, y que los estadísticos "no son objetos estructurales". Además OW (diap. 14): las diferencias entre firmas son de corta vida. |
| 6.3 En los dos borradores la coordinación actúa **solo** por v | **refutada** | TFG2, Prop. `fs-coordination` y eq. (`fs-gap-derivative`, l. 365–385): la compatibilidad reduce **también σ_F** y libera reservas, lo que amplía capacidad (`−γ κφ(z0)/B0 · (σ_F)_θ`). TFG1, eq. `totalI` (l. 480–483) y l. 451–468: también hay canal por μ (dμ), τ, D y N. |
| 6.4 Cota ≈ 3 % con "la calibración de TFG2 (b=η=1, v=0,05, ψ=0,5, N=1; a=1,55)" | **refutada** | Esa calibración **no es la de TFG2** (ni la encuentro en TFG1). La de TFG2 (Tabla `calibration`, l. 1690–1694): b=0,1, η=0,1, ψ=0,05, N=1, v=0,05+9ρ²(0,4)². Con ella, ver 2.4: la parte de política de v mueve la pendiente **un 10 % (A_P=2) a un 65 % (A_P=0,2)**. El 3 % es un artefacto de elegir v=0,05 con η=1; con η=5 sale 14 %. |
| 6.5 BCE exógeno; más variación; E_D = pass-through al tipo del stock; datos | **debilitada / refutada en datos** | Ver 2.5. |
| 6.6 (1) interacción triple shock × exposición × restricción | **debilitada** | La versión doble es de IOPO (pp. 11, 36–41) y su sentido en el agregado EE. UU. de TFG2 no se detecta: los nueve gradientes tienen IC que incluyen 0 con n=107–115 (TFG2 Tabla `evidence-interactions`, l. 1831–1864). La triple añade una restricción medida a nivel país: ver 2.5.4. |
| 6.6 (2) menos capacidad bancaria ⇒ menos respuesta, transición más abrupta en N | **debilitada** | La primera mitad es el canal de capital bancario (no leí ABK/Wang). La segunda no se deriva (ver 5.5). |
| 6.6 (3) asimetría y más cerca de las restricciones | **se sostiene**, **ya mostrada** | Perez-Orive pp. 12–13, 19–22 (la asimetría crece con el nº de restricciones: Prop. 2, pp. 12–13; Figura 6, pp. 20–21); Auclert p. 40; Tenreyro-Thwaites p. 2. |
| 6.6 (4) la coordinación mueve el nivel; su efecto marginal está acotado por la capacidad | **refutada** como está escrita | Ver 6.3 y 6.4. Solo es cierta en el régimen interior y con el σ_F fijo. |

## 2. Detalle de los ataques

### 2.1 Falsabilidad: el signo de la interacción principal no está predicho
- La literatura que he leído **discrepa en el signo** de "estar restringido × choque":
  - OW (diap. 4, 12–13): las firmas **más endeudadas responden menos**; el 50 % menos endeudado explica casi toda la respuesta agregada.
  - IOPO (p. 5, pp. 36–41), Perez-Orive (pp. 19–21), Jeenas (p. 4) y Jungherr (resumen, p. 2; p. 4): restringidas, con más liquidez escasa o más deuda que vence responden **más** (a la subida).
- La propia Perez-Orive lo señala como controversia (p. 8: predicciones "ambiguas" de OW) y que el desacuerdo se aclara separando subida y bajada (p. 9).
- FIRST_PRINCIPLES §5.3 admite que el signo de la restricción depende de `p_f/a − g` y no lo fija. Con el signo libre, casi cualquier estimación encaja **[criterio propio]**.
- Lo que sí es una predicción firme es `∂I_u/∂g = 1−ω > 0` solo en el régimen restringido: es lo mismo que IOPO Prop. 1(ii) (p. 11).

### 2.2 La novedad que queda
Descontando IOPO, Perez-Orive, Jeenas, Jungherr y Auclert, lo único que el planteamiento aporta de verdad:
1. El **margen interior de reservas** `m` junto con la repreciación, en forma cerrada (TFG2). Jeenas lo tiene dinámico y sin forma cerrada para el tipo flotante.
2. El **cierre bancario** `ψ/N` dentro de la misma fórmula.
3. Una aplicación con panel de países.

Eso es un paper de teoría **incremental** más una aplicación empírica, no una "fórmula general" **[criterio propio]**.

### 2.3 Agregación: supuestos escondidos
1. **El banco es común.** En TFG1/TFG2 `r_L = r_f + ψ L/N` y `L = ΣI` (TFG1 l. 186–189; TFG2 l. 308). La `a_i = b+ηv_i+ψ/N` de §5 trata `ψ/N` como un parámetro individual. Con una masa 1−s de restringidas (inversión fija H) y s de holgadas:
   `I_s·(a_0 + sψ/N) = q − (ψ/N)(1−s)H`, de modo que
   `dI_s/du = [p_f − (ψ/N)(1−s) g] / (a_0 + sψ/N)`
   (a_0 = b+ηv). La respuesta de las holgadas **depende de la masa de restringidas** y de su alivio g (efecto expulsión de crédito). La fórmula del §5 no lo tiene. *Derivación a mano, sin SymPy (ver §0).* Esto es sincronización de holguras **dentro del modelo**, sin hacer falta Kiyotaki-Moore.
2. **Equilibrio parcial.** TFG1 es precio fijo con capacidad ociosa (l. 218, 476); Auclert (pp. 23–24) avisa de que su Teorema 3 es parcial y para choques transitorios, y de que no admite inversión de capital (nota 28, p. 24).
3. **Heterogeneidad independiente de s.** §5.4 la rechaza, pero §5.2 la usa para leer la STAR como CDF.

### 2.4 Cota de la coordinación: depende de la calibración
Cuentas a mano, con la tabla de TFG2 (b=0,1, η=0,1, ψ/N=0,05, v=0,05+1,44ρ², ρ=1/(1+A_P)):

| A_P | v | a | 1/a (= p_f/a) | η·v_pol/a |
|---|---|---|---|---|
| 2 | 0,21 | 0,171 | 5,85 (coincide con TFG2 l. 793) | 9 % |
| 0,2 | 1,05 | 0,255 | 3,92 | 39 % |
| v_pol → 0 | 0,05 | 0,155 | 6,45 | — |

- Quitar **toda** la varianza de política sube la pendiente un **10 %** desde A_P=2 y un **65 %** desde A_P=0,2. FIRST_PRINCIPLES dice ≈3 %.
- Con los parámetros de FIRST_PRINCIPLES, η·v/a = 0,05/1,55 = 3,2 %; con η=5 pasa a 14 % (0,25/1,75), con η=10 y v=0,2 a 57 % **[cuentas mías]**. La "cota" no sale de un teorema; sale de elegir ηv pequeño frente a b+ψ/N (unidades arbitrarias).
- **Canales que no pasan por v** (todos en los borradores): σ_F y la liberación de reservas (TFG2 l. 365–385), μ, τ, D, Ā y N (TFG1 l. 451–468), respaldo fiscal (TFG2 l. 622), curva de tipos a dos vencimientos (TFG2 l. 710–716), y el capital bancario por beneficios (TFG1 l. 496). En el régimen restringido la inversión es `H − γ m_0(σ_F)` y su respuesta a σ_F **no** está acotada por `ηv/a`.

### 2.5 Identificación del diseño de la zona euro (§6.5)
1. **Los datos no están.** `datalake/raw/ecb/csv/` solo tiene agregados del área (`U2`/`I9`): `MIR_NFC_loans_new` y `MIR_mortgages_new` son **nuevos préstamos** del área; PIB y deuda/PIB, del área. No hay tipos sobre saldos vivos, ni inversión, ni PIB trimestral **por país**. FIRST_PRINCIPLES dice que "se comprobó" que el BCE no da volúmenes por país; no está en el repo y no lo puedo confirmar. Que existan los tipos MIR de saldos vivos por país es algo que sé del conocimiento general, no de la biblioteca **[criterio propio, a verificar]**. BIS DSR existe 1999Q1–2026Q1 (CATALOG); no he comprobado qué países y sectores.
2. **Efecto información.** JK, zona euro: los choques de información explican ~50 % de la variación de alta frecuencia frente a 33 % en EE. UU. (p. 4); el 46 % de las sorpresas tienen respuesta bursátil "de signo equivocado" (p. 29); con la identificación estándar, las bolsas **suben** tras la "contracción" (p. 29). Si la exposición se correlaciona con la sensibilidad al ciclo del área (el periférico es más cíclico) **[criterio propio]**, `choque × E_i` mide sensibilidad a **noticias** y no repreciación. Haría falta usar el choque de política de JK y un placebo con el de información. El dato está en el lago (ecb_202310, 1999–2023). El agosto de 2011 es uno de los mayores choques de información (p. 30).
3. **E_D como pass-through estimado.** (a) `E_D = −∂J_F/∂u` está en **unidades de flujo** y "no es la deuda total" (TFG2 l. 247–252); un pass-through en puntos porcentuales **omite el stock**. País con 100 % de pass-through y poca deuda tiene E_D bajo. (b) Un pass-through estimado con el propio choque es una variable **posterior al tratamiento**: incluye la respuesta de los diferenciales por riesgo (Jeenas p. 5, nota 9: los costes de endeudamiento suben más que los tipos oficiales por primas de crédito y de plazo) y la "historia del país". Debe medirse con la **estructura contractual predeterminada** (cuota de reset, vencimientos) × stock (BIS TC está en el lago).
4. **Confusión en la triple interacción.** Mucha deuda variable (hipotecas ES/PT/IT/FI) coincide con banca débil y con la crisis soberana **[criterio propio, conocimiento general; sin cita de la biblioteca]**. Con efectos fijos de tiempo (que absorben el choque común), β se identifica solo con variación **entre países**: un contraste núcleo–periferia con ~10–12 clústeres y 2–3 grupos efectivos. Con `exposición` y `capital bancario` casi colineales por país, la triple no está identificada separadamente. JK p. 30: las subidas de abril y julio de 2011 coinciden con la crisis soberana; esa observación domina.
5. **El límite inferior cero (ZLB/NIRP).** IOPO muestra que el canal flotante **desaparece** en el límite inferior (p. 6; Tabla XIII, pp. 44–45). Con 2012–2022 a tipos ~0 o negativos, casi la mitad de 1999–2023 no tiene canal; con suelos contractuales, tampoco bajadas. La muestra útil queda ~1999–2008 + 2022–23 **[criterio propio]**.
6. **El BCE no es exógeno para cada país grande** (DE, FR, IT, ES ≈ la mayor parte del PIB). La exogeneidad del choque es condicional a datos del área (BS p. 3: R² 10–40 % de predecibilidad en EE. UU.), no por país. Y el choque no tiene "más variación de regímenes" si 3 de las 4 grandes están en el mismo régimen casi todo el tiempo.
7. **Antecedente.** El contraste "estructura hipotecaria por país × choque" ya existe (Calza-Monacelli-Stracca 2013, citado por Auclert p. 38; **segunda mano**, no leído). La novedad del panel es, otra vez, modesta.

**Contraste EE. UU. (BS):** BS p. 4 dice que tras 1984 los choques de alta frecuencia son poco relevantes para Ramey (2016); BS p. 55 asume el mismo riesgo para los suyos ortogonalizados. TFG2 ya muestra n=107–115 y ningún gradiente significativo (l. 1864). El EE. UU. agregado no tiene potencia para estados de régimen.

## 3. Las tres amenazas más graves

| # | Amenaza | Qué la resolvería |
|---|---|---|
| **1** | **Contribución:** el resultado central (§2), la predicción 1 y la 3 ya están en TFG2/IOPO/Perez-Orive/Auclert; el signo de la interacción no está predicho (2.1). El diferenciador real (margen de reservas + cierre bancario) es pequeño y Jeenas lo ocupa en parte. | (a) Reescribir la contribución como "margen de reservas bajo repreciación y cierre bancario común" y diferenciarla de IOPO y de Jeenas con **una** tabla de casos límite verificada con SymPy (`theory/check_*.py`). (b) **Prerregistrar el signo**: fijar con la calibración medida de `p_f/a` y `g` qué grupos de países deben tener `g > p_f/a` y cuáles no, **antes** de ver resultados. |
| **2** | **Identificación y datos de la zona euro:** datos por país no están; E_D mal definida y endógena; info-efecto; clústeres; triple colineal; ZLB (2.5). | (a) Descargar y registrar en `MANIFEST.csv` los MIR de saldos vivos y la inversión trimestral por país; (b) definir E_D por estructura contractual × stock; (c) `mc-validate` de **potencia** con G=10–12 clústeres, colinealidad realista exposición–banca y T efectivo sin ZLB; **no lanzar el panel si la potencia es < 0,8 para el efecto de IOPO**; (d) placebo con el choque de información de JK; (e) excluir la observación 2011 como robustez; (f) la triple interacción pasa a **exploratoria**. |
| **3** | **Errores en la teoría que sostienen afirmaciones del paper:** cota del 3 % con parámetros que no son los del borrador; "coordinación solo por v"; agregación sin banco común; "transición abrupta en N" no derivada (1.3, 2.3, 2.4). | Recalcular la cota con la calibración correcta y derivarla **también** en régimen restringido (σ_F); rederivar la agregación con `r_L = r_f + ψL/N`; sacar del prerregistro 6.6(2) segunda mitad y 6.6(4) o derivarlas; guardar todo en `theory/check_*.py` + `mc-validate` del estimador de la STAR. |

## 4. Rúbrica (SPEC de p01): planteamiento actual frente a rivales

Escala 1–5, **mayor = mejor**; en *Coste*, 5 = barato y rápido. "Total" suma sin ponderar. Regla de la SPEC: una ambición alta no compensa una identificación de 1–2.

| Criterio | **A. Actual** (FP: teoría + panel euro + EE. UU.) | **B. Solo EE. UU.** (BS-orth × exposición sectorial Z.1, SLOOS, EBP) | **C. Panel histórico JST** (instrumento trilema, estado = crédito/deuda, signo) | **D. Teoría pura** (reservas + varias restricciones + repreciación, SymPy) | **E. Estadísticos suficientes** (Auclert; momentos sectoriales vs. LP) | **F. Actual modificado** (ver §5) |
|---|---|---|---|---|---|---|
| Ajuste a la intuición | 3 | 3 | 3 | 4 | 4 | 4 |
| Ambición / contribución | 3 | 2 | 3 | 2 | 4 | 3 |
| Identificación | **2** | 3 | 4 | 3 | 3 | 3 |
| Datos / potencia | **2** | 2 | 4 | 5 | 2 | 3 |
| Riesgo | 3 | 2 | 3 | 3 | 2 | 4 |
| Coste | 2 | 5 | 3 | 4 | 3 | 3 |
| **Total** | **15** | **17** | **20** | **21** | **18** | **20** |
| ¿Alerta (ident. ≤ 2)? | **sí** | no | no | no | no | no |

Justificación **[criterio propio salvo cita]**:

- **A.** *Ajuste 3:* los regímenes salen de restricciones, pero la forma (CARA-normal, cuadrática, min) se impone. *Ambición 3:* encaja en revistas de macro-banca de segundo nivel; el núcleo está en IOPO/Perez-Orive/Jeenas (2.2). *Ident. 2:* 2.5. *Datos 2:* por país no existen; EE. UU. n≈110 sin gradientes (TFG2 l. 1864). *Riesgo 3:* TFG2 es publicable aunque el panel salga nulo. *Coste 2:* descarga nueva, MC, réplica en R, derivaciones.
- **B.** *Ajuste 3:* contrasta regímenes pero solo con estados agregados. *Ambición 2:* repite el diseño de TFG2 con otro estado. *Ident. 3:* BS ortogonalizada mejora exogeneidad (BS pp. 4–5) y los choques de política son identificados. *Datos 2:* Z.1 no separa tipo variable de fijo; n≈115. *Riesgo 2:* un nulo no es publicable. *Coste 5:* todo en el lago.
- **C.** *Ajuste 3:* mide no linealidad por crédito, no el flujo de caja por repreciación (JST no tiene cuota de deuda flotante; `[no verificado]`). *Ambición 3:* JST2020 ya hace dependencia de estado por burbuja hipotecaria y ciclo (JST p. 3, p. 5); y halló **poca** asimetría por crédito de empresas (p. 5): un nulo ya publicado frena la novedad. *Ident. 4:* experimento cuasi-natural con discusión de spillovers (pp. 3–5). *Datos 4:* 18 países desde 1870, `jst/JSTdatasetR6.dta` en el lago, pero anual. *Riesgo 3.* *Coste 3.*
- **D.** *Ajuste 4:* los regímenes son endógenos y se derivan. *Ambición 2:* el aporte incremental ante Perez-Orive 2026 y Jeenas es pequeño y la teoría pura es difícil de colocar. *Ident. 3:* no hay causal que identificar; se disciplina con momentos de Perez-Orive/Jeenas. *Datos 5:* ninguno necesario. *Riesgo 3:* publicable, pero con novedad dudosa. *Coste 4.*
- **E.** *Ajuste 4*, *Ambición 4*: reconciliar covarianzas medidas con LP sería nuevo (Auclert p. 20: los estadísticos son medibles). *Ident. 3.* *Datos 2:* hacen falta covarianzas micro (MPC, exposición); con agregados por sector se pierde lo central (Auclert p. 23). *Riesgo 2*, *Coste 3.*
- **F.** Ver §5.

## 5. Recomendación: **MODIFICAR** (no mantener ni sustituir)

El planteamiento resiste en lo esencial (la teoría de TFG2 es correcta y publicable), pero **no en lo que dice
que aporta ni en cómo propone contrastarlo**. Sustituir por B o C pierde lo único que tiene de propio (reservas + repreciación).
Concretamente:

1. **Reposicionar la contribución** (SPEC): el resultado no es "TFG1 ⊂ TFG2" ni "fórmula general", sino *"el margen interior de
   reservas y el cierre bancario común entre los extremos de IOPO y Perez-Orive"*. Citar IOPO p. 11 y Perez-Orive p. 12 como casos límite.
2. **Corregir antes de prerregistrar:** (a) §6.4: recalcular con la calibración real y sustituir "≈3 %" por una función de (η, v_pol, b, ψ/N, σ_F); (b) §5: agregación con banco común; (c) quitar "transición abrupta en N" y "solo por v".
3. **Dos tareas de teoría** (`theory/check_*.py` + SymPy): (i) `check_nesting.py`: casos límite IOPO/TFG1/TFG2; (ii) `check_aggregation.py`: la fórmula de 2.3.
4. **Empírica en dos etapas con puerta:**
   - *Etapa 1 (barata, ya con datos):* EE. UU. con BS-orth, **un único estado** (liquidez/servicio de la deuda, Z.1 + BIS DSR) y **separación subida/bajada**. Es el contraste con más potencia para el signo y la asimetría, y no hace falta más datos.
   - *Etapa 2 (condicionada):* panel euro **solo si** (a) los datos por país están en el MANIFEST, (b) E_D contractual × stock, (c) `mc-validate` de potencia ≥ 0,8 con 10–12 clústeres y sin ZLB, (d) placebo con el choque de información. La triple interacción es exploratoria.
5. **Prerregistro (para los autores):** fijar el **signo esperado** por grupo (2.1) y sacar del prerregistro 6.6(2, segunda mitad) y 6.6(4) hasta que se deriven.
6. **Qué hay que aprobar:** si los autores aceptan que el paper sea **teoría + una prueba empírica acotada** (rúbrica F) y no una "prueba del mecanismo" con la triple interacción.

**Si hay que elegir un rival:** D (teoría) tiene la mejor puntuación bruta (21) pero la ambición es 2; C es el más limpio en identificación pero no contrasta el canal. **Mi preferencia es F** [criterio propio]: mantiene lo propio, retira las afirmaciones refutadas y pone una puerta de potencia antes de gastar semanas en datos.

## 6. Qué no he podido hacer
- Leer Angeletos-Lian-Wolf (§3 de FIRST_PRINCIPLES) ni los trabajos sobre capital bancario (ABK, Wang).
- Ejecutar Python: los cálculos de 2.3 y 2.4 son a mano; deben pasar a `theory/check_*.py`.
- Verificar los datos por país del BCE/Eurostat (solo he comprobado el contenido del lago).
- Leer de OW otra cosa que las diapositivas; de JST, Jungherr, Tenreyro-Thwaites y JK/BS, más que lo indicado en §0.
- Los pocos datos que uso de conocimiento general (estructura hipotecaria por país, existencia de MIR de saldos vivos) están marcados y no están en la biblioteca.
