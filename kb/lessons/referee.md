# Lecciones — Referee

## 2026-11-03 · p01 · Diagnóstico de v22 (Transmission Capacity)
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
