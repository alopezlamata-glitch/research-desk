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
   SPEC. Con ella, el resultado modal pasa de "no concluyente por potencia" a "H1 no se interpreta" (P ≈ 0,94). Regla:
   simular todas las especificaciones que condicionan el veredicto (puertas, gating) y dar la probabilidad conjunta.
2. **Un error estándar "validado" solo vale para el DGP con el que se validó.** Con apalancamiento alto, HC3 es conservador
   con innovaciones homocedásticas, pero cae al borde de la banda si la varianza va ligada a |ε|. Regla: validar una alternativa
   de ee con al menos un DGP heterocedástico ligado a las observaciones de alto apalancamiento (aquí, recesiones).
3. **Umbrales relativos a otro coeficiente estimado.** Con δ = 0,146·|β̂_U| y ee(β̂_U) ≫ |β_U|, el umbral es ruido y genera
   falsas refutaciones en cuanto la precisión de β_C mejora. Regla: comprobar E[δ̂] frente al valor verdadero en el MC.
4. **Diagnósticos triviales.** La media del apalancamiento siempre es k/N; no es evidencia. Mirar el máximo y qué fechas lo producen.
