# Diagnóstico de v22 — "Transmission Capacity and Sequential Bottlenecks" (abril 2026)

Autor del diagnóstico: director (sesión inicial), 2026-11-03. **Pendiente de auditoría
independiente del Referee** (tarea A1).

## Qué funciona (conservar)
- La **intuición** es buena y publicable: la efectividad de la política depende del estado y los
  canales pueden ser complementarios. "Coordinación necesaria pero no suficiente" es un mensaje claro.
- Hamilton filter en lugar de HP. Se reconocen los límites causales (α₁ como correlación estructural).
- Comparación fuera de muestra entre especificaciones (Tabla 2).

## Problemas, por gravedad

### Mayores
1. **Identificación: pocos datos para demasiados parámetros.** T = 135, 8 parámetros estimados y
   ≥12 calibrados o preestimados. θ admite estar débilmente identificado (ΔR² = 0.001 en θ∈[0.2,3]). Los
   parámetros de $m(\kappa)$ ($\phi_D$, Φ, $\bar s$) y de la ley de χ ($\tau_y, \phi_r, r_{min}$) no se reportan.
2. **Circularidad de los tests "model-free" (Sección 5.4).** Los tres se calculan sobre
   $\widehat{TE}_t = \hat\chi_t(1-\hat\delta_t)m(\hat\kappa_t)$, un producto por construcción. Que la varianza de
   interacción sea distinta de cero, que haya "excess collapse" y que las cross-partials difieran es
   aritmética del producto, no evidencia. Un referee lo detecta enseguida.
3. **Política endógena.** $z_t = \sigma^M + \sigma^F$ son posturas, no shocks. Los instrumentos son
   spreads y condiciones financieras rezagadas, que afectan directamente al output gap: la
   restricción de exclusión no es creíble.
4. **Solapamiento proxy/instrumento.** NFCI está en $\chi^{bank}$ y en $\kappa^{obs}$, y ANFCI es instrumento;
   BAA está en $\kappa^{obs}$ y también es instrumento.
5. **Error matemático en A.3 / Corolario 1.2.** δ es cóncava (no convexa) en toda la muestra;
   $D^*\approx0.43$, no $0.04$; la ec. 35 tiene el signo opuesto al afirmado. Detalle en `kb/lessons/theory.md`.

### Menores
6. TED spread (LIBOR) discontinuado en 2022, pero la muestra llega a 2024Q4.
7. `GFDEGDQ188S` es deuda pública **total**, no "held by the public" (esa es `FYGFGDQ188S`), a verificar.
   Sumar `NCBDBIQ027S` (en $B) a un ratio sobre el PIB requiere dividir antes por el PIB nominal; no se documenta.
8. `BAA` en FRED es un rendimiento, no un spread (el spread es `BAA10Y`).
9. Cifras distintas entre la Fig. 3 y la tabla de contrafactuales (0.158 frente a 0.155; +78.8 % frente a +82.3 %).
10. La calibración δ(1) = 0.5 ("la mitad de la liquidez la absorbe la deuda") se justifica con una
    cuenta ad hoc (intereses/PIB entre el impulso trimestral).
11. Título del PDF ("Liquidity, Debt and Institutional Coherence…") distinto del título interno.

## Implicación para la nueva versión
El mensaje puede sobrevivir, pero la evidencia tiene que venir de: (i) **shocks de política
identificados externamente**, (ii) **más datos** (panel internacional/histórico), (iii) **un único
parámetro que discipline la forma funcional** (anidamiento CES; ver `kb/methods/ces-nesting.md`) y
(iv) **tests sobre outcomes observados**, no sobre $\widehat{TE}$. Ver `../SPEC.md`.
