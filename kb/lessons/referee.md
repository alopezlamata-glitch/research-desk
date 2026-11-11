# Lecciones — Referee

## 2026-11-03 · p01 · Diagnóstico de v22 (Transmission Capacity)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
Patrones de error encontrados en la versión previa, que conviene buscar en cualquier paper:
1. **Tests "model-free" calculados sobre objetos construidos con el modelo.** La varianza de
   interacción, el "excess collapse" y las cross-partials se calculan sobre $\widehat{TE}_t$, que se
   construye como un producto. Una interacción distinta de cero es mecánica. Regla: los tests de
   forma funcional se hacen sobre outcomes observados (output) y estados observados.
2. **El mismo dato como proxy y como instrumento.** NFCI entra en $\chi^{bank}$ y en $\kappa^{obs}$,
   y ANFCI es instrumento; BAA entra en la PCA de confianza y también es instrumento. Regla: tabla de
   "qué serie entra dónde" antes de estimar.
3. **Muchos parámetros calibrados con T pequeño.** ≥12 valores calibrados o preestimados ($\theta, \gamma,
   \phi_k, \phi_m, \psi, \rho_\Gamma, \mu_\Gamma, \sigma_{cb}$, la pendiente 1.5 del logístico, $\bar\chi$, $\tau_y, \phi_r,
   r_{min}$, los parámetros de $m(\kappa)$) frente a 8 estimados con T = 135. Regla: contar y reportar.
4. **Errores de signo en derivaciones.** Ver `kb/lessons/theory.md`. Regla: SymPy en todas.
5. **Cifras incoherentes entre figura y tabla** (Fig. 3: 0.158 y +78.8 %; tabla: 0.155 y +82.3 %).
   Regla: todas las cifras salen del mismo run de código.

## 2026-11-05 · p01 · R-F4, Monte Carlo de `s1_liq`
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Las probabilidades de veredicto se calculan con el árbol de decisión completo.** F4 dio las de H1 sin la puerta H0 de la
   SPEC. Con ella, el resultado modal pasa de "no concluyente por potencia" a "H1 no se interpreta" (P ≈ 0,92). Regla:
   simular todas las especificaciones que condicionan el veredicto (puertas, gating) y dar la probabilidad conjunta.
2. **Un error estándar "validado" solo vale para el DGP con el que se validó.** Con apalancamiento alto, HC3 es conservador
   con innovaciones homocedásticas, pero cae al borde de la banda si la varianza va ligada a |ε|. Regla: validar una alternativa
   de ee con al menos un DGP heterocedástico ligado a las observaciones de alto apalancamiento (aquí, recesiones).
3. **Umbrales relativos a otro coeficiente estimado.** Con δ = 0,146·|β̂_U| y ee(β̂_U) ≫ |β_U|, el umbral es ruido y genera
   falsas refutaciones en cuanto la precisión de β_C mejora. Regla: comprobar E[δ̂] frente al valor verdadero en el MC.
4. **Diagnósticos triviales.** La media del apalancamiento siempre es k/N; no es evidencia. Mirar el máximo y qué fechas lo producen.
5. **Antes de atribuir una discrepancia de MC al ruido, comparar un objeto determinista.** Las ee sobre ȳ sin ruido (σ = 0)
   permitieron comparar F4, Python y R al 9.º decimal. Después, una discrepancia de ≈ 3 errores se repite con otra semilla y
   más réplicas: aquí, dos casos de 1 sobre ~40 comparaciones, y los dos desaparecieron. Una corrida de 1000 réplicas sola puede
   mover una probabilidad del 7 % en 0,02.

## 2026-11-08 · p01 · R-F10, Monte Carlo de `s1r_*` (F9)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Un sesgo "corregido exactamente" en el MC puede ser una tautología del DGP.** Con β_C = β_U, ȳ_t es lineal exacta en
   ε_{t−9..t+12} y `aum` controla justo por esos choques: error 0 por construcción. Regla: probar la corrección con otra forma de
   IRF (más corta, con joroba que revierte) y con efectos heterogéneos (β_C ≠ β_U), que es donde queda el resto.
2. **Tamaño del contraste frente a la hipótesis rival, no solo frente a β = 0.** El contraste de H1 tenía tamaño 0,01–0,04 con
   β_C = β_U = 0, pero confirmaba en falso un 10–14 % con β_C = 0 y β_U grande. Regla: simular siempre el rival relevante de la
   SPEC y dar P(confirma) en una rejilla de su parámetro.
3. **Las cifras en "múltiplos de β_ref" heredan la normalización de β_ref.** Con π del fed funds en h = 0 o en h = 1, la
   potencia frente a β_ref pasa de 0,04–0,10 a ≈ 0,1–0,3. Regla: dar el MDE en unidades del choque (invariante) y la potencia con
   cada normalización defendible; no comparar con una expectativa fijada con otra normalización.
4. **Una sobrecobertura no se juzga sola: hay que ver qué hacen las alternativas en la celda difícil.** Las ee que cubren bien
   en la muestra completa (NW con corrección de g.l., EWC) caen a 0,79–0,85 en b_C sin Volcker; solo las que usan residuos HC3
   aguantan. La que se acerca más a 0,95 (EWC+HC3) infla el tamaño sin Volcker. Regla: tabular las alternativas por celda y medir
   también el tamaño (β = 0) y la potencia del árbol completo, no solo la cobertura.
5. **Controlar por adelantos del choque cambia el estimando si el choque está autocorrelado en la población.** Regla: con
   adelantos como controles, contrastar la autocorrelación del choque (Ljung-Box) y escribir en la SPEC que se estima la respuesta a
   un choque aislado.

## 2026-11-08 · p01 · R-F17, estimación de `s1r_*` (F16)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Cuando la puerta falla, se audita el resumen que se escala, no solo las cifras.** Las estimaciones y el veredicto eran
   exactos, pero el HANDOFF daba el p < 0,05 de β̂_C en las dos muestras principales y se callaba las dos robusteces en las que no
   pasa (p = 0,15 y 0,08). Regla: si un coeficiente sin veredicto "llama la atención", exigir que el resumen lleve todas sus filas
   prerregistradas (principales y robustez), no solo las favorables.
2. **No juntes en una frase un p unilateral y un IC bilateral al 95 %.** «p unilateral < 0,05 pero el IC al 95 % contiene el 0»
   suena a contradicción y no lo es: al contraste unilateral al 5 % le corresponde el IC al 90 %. Regla: dar el IC del mismo nivel
   que el contraste.
3. **Las lecturas de implementación se juzgan sin la variable de resultado.** Para decidir si z debía estandarizarse en la logística
   o si la mediana se recalculaba al recortar la muestra, bastó mirar el estado: rango de F (sin estandarizar, [0,35; 0,64], casi
   sin estado) y número de filas que cambian de estado (5 de 136). Regla: comprobar el efecto de la lectura sobre el regresor, no
   sobre β̂, para no elegir la lectura con los datos.
4. **Comprobar que no hay ejecuciones escondidas con el historial del spec_log.** Un log de solo-añadir con una sola marca de
   tiempo y un único commit es la prueba disponible; no detecta un log borrado a mano antes del commit. Regla: citar ese límite en
   el informe.

## 2026-11-08 · p01 · R-F22, macros del paper A (F21)
Estado: candidata
1. **Las macros se auditan con una correspondencia macro → celda escrita a mano, sin importar el script del autor.** Si se reutilizan
   su parser y sus diccionarios, el mismo error de mapeo aparece en los dos lados. Con archivo:línea:columna fijos se detectan a la vez
   las macros sin fuente, las ausentes y las distintas. Regla: comparar cadenas exactas, no floats.
2. **Que una macro sea fiel a su tabla no basta: mira también cómo se calculó la celda de origen.** El MDE de f13 multiplica un c
   redondeado a un decimal (10,01 frente a ≈ 10,05). Es irrelevante aquí, pero solo se ve leyendo la línea que escribe la tabla. Regla:
   para las cifras derivadas (MDE, umbrales), leer la línea que las genera.
3. **Comprobar que la fuente "auditada" tiene de verdad un informe en `audits/`.** F13 no lo tenía; su respaldo era el prerregistro
   aprobado. Regla: citar la cadena de aprobación real en el informe.

## 2026-11-11 · p01 · R-F28, renombrado de macros (F25)
Estado: candidata
1. **Un renombrado se audita compilando también al consumidor, no solo el archivo renombrado.** `macros.tex` compilaba, pero el
   rodeo `\let\Nuevo\Viejo` de `main.tex` pasó a dejar `\Nuevo` indefinida al desaparecer `\Viejo`. Regla: al renombrar macros,
   compilar el `.tex` que las usa en un directorio temporal, sin tocarlo.
2. **Cuando una celda tiene dos rangos (todos los términos y, entre paréntesis, los que deciden), mira cuál toma el parser.** Aquí
   coincidían, pero la SPEC describe uno y el código lee el otro. Regla: recalcular los dos y pedir que el código lea el que cita la SPEC.

## 2026-11-11 · p01 · R-F30, texto del paper A y test de F27
Estado: candidata
1. **En el texto, busca la frase que convierte un límite del diseño en un límite de los datos.** La sección de resultados decía «what
   this design can detect», pero la introducción decía «what aggregate U.S. data can say», y el propio paper cita que las LP tienen más
   varianza que los VAR. Regla: comparar cada afirmación de alcance de la introducción y del abstract con su versión acotada del cuerpo.
2. **Una cita de procedencia de datos se contrasta con las notas de todas las entradas implicadas, no solo con la citada.** La frase
   sobre la serie de Romer-Romer citaba dos entradas cuyas notas decían «no verificado» y «solo metadatos», y la de Ramey contaba otra
   historia. Regla: para cada «X construye/distribuye la serie», leer las notas del `.bib` de X, de la fuente de los ficheros y del
   DICTIONARY.
3. **Las KKT que se dan sin objetivo son una derivación sin verificar.** Los tests partían de `κ G(m) = δ + γλ`, que solo sale con una
   penalización cuadrática del déficit; con la lineal, la cota cambia de fórmula. Regla: derivar las KKT desde el objetivo en SymPy
   y pedir que el texto lo escriba.
4. **Un test negativo se valida mutando en memoria lo que el test usa (peso, signo, dominio) y viendo que falla.** Es barato, no toca
   `theory/` y distingue un negativo real de uno vacío.
