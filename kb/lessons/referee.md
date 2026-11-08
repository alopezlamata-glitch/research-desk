# Lecciones — Referee

## 2026-11-03 · p01 · Diagnóstico de v22 (Transmission Capacity)
Estado: candidata
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
Estado: candidata
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
Estado: candidata
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
