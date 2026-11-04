# Candidato B — LP dependiente de estado con agregación CES

Estado: **candidato** (propuesto por el director en la sesión inicial, 2026-11-03). Se evalúa en la Fase 0 junto al resto.
Versión previa: `../../prior/v22_transmission_capacity.pdf` · Diagnóstico: `../../prior/diagnosis_v22.md`

## Pregunta
¿Depende la potencia de los impulsos de política fiscal y monetaria del estado estructural de la
economía (deuda, salud bancaria, confianza)? Y, si depende, **¿se combinan esos estados como
sustitutos (aditivo) o como complementos/cuellos de botella (multiplicativo/Leontief)?**

## Contribución (frente a v22 y la literatura)
- La literatura de multiplicadores dependientes de estado (Auerbach-Gorodnichenko; Ramey-Zubairy;
  Ilzetzki-Mendoza-Végh) estudia **un estado cada vez**. Aquí se estudia **cómo se agregan varios**.
- La forma de agregación se resume en **un único parámetro estimable** (ρ de un agregador CES que anida
  el caso aditivo, el multiplicativo y el Leontief), en lugar de comparar especificaciones ad hoc.
- La identificación descansa en **shocks de política identificados externamente** y en **más datos**
  (panel), no en un sistema estructural con muchos parámetros calibrados.

## Modelo empírico (núcleo)
Local projection dependiente de estado con agregación CES de los estados (rezagados, predeterminados):

$$ y_{i,t+h}-y_{i,t-1} = \alpha_{i,h} + \beta_h\,T(s_{i,t-1};\rho,w,\nu)\,\varepsilon_{i,t} + \gamma_h' s_{i,t-1} + \Gamma_h' x_{i,t-1} + u_{i,t+h} $$
$$ T(s) = \Big[\textstyle\sum_j w_j s_{j}^{\rho}\Big]^{\nu/\rho} $$

- $\varepsilon_{i,t}$: shock de política identificado externamente (monetario y fiscal, por separado).
- $s_{j}\in(0,1]$: estados normalizados (fiscal space, banking health, confidence).
- ρ = 1: aditivo · ρ → 0: multiplicativo · ρ → −∞: cuello de botella (Leontief).
- Parámetros de forma: ρ, ν y 2 pesos libres, compartidos entre horizontes (frente a ≥ 20 en v22).

**Paso previo (sin forma funcional):** LP con interacciones $\varepsilon\times s_j$, $\varepsilon\times s_j s_k$ y
$\varepsilon\times s_1s_2s_3$ sobre el **output observado**. Este es el test genuinamente "model-free" de complementariedad.

## Hipótesis prerregistradas — BORRADOR (decisión de los autores)

| Id | Hipótesis | Especificación | Regla de decisión |
|---|---|---|---|
| H1 | La respuesta acumulada del output a un shock expansivo cae con la deuda | LP con interacción ε×(1−fiscal space), h = 0…8 | Coeficiente medio en h = 4…8 < 0, test unilateral al 5 % con inferencia robusta |
| H2 | Los estados son complementarios (no aditivos) | CES-LP | IC al 90 % de ρ excluye 1 |
| H3 | La agregación es al menos tan complementaria como el producto | CES-LP | IC al 90 % de ρ por debajo de 0 o incluyéndolo; se reporta la elasticidad 1/(1−ρ) |
| H4 | Los resultados de H1–H3 se mantienen en el panel internacional | Panel CES-LP con FE de país | Mismo signo y solapamiento de IC con EE. UU. |

Horizontes, muestras y estados exactos se fijan en `PLAN.md` antes de la tarea C3.

## Identificación
- **Shocks de política:** monetarios (Romer-Romer extendidos; Bauer-Swanson; en panel, el instrumento
  trilema de JST) y fiscales (noticias militares de Ramey; consolidaciones narrativas de
  Guajardo-Leigh-Pescatori).
- **Estados:** rezagados un periodo y medidos con series **distintas** de cualquier instrumento.
  Amenaza: los estados son endógenos al ciclo. Mitigación: controles de ciclo, rezagos más profundos
  y estados medidos con variación lenta (deuda) o prederminada (crisis bancarias de BVX).
- **Tests sobre outcomes observados**, nunca sobre un $\widehat{TE}$ construido.

## Datos
- EE. UU. trimestral (FRED + shocks): ~1960–2024, T ≈ 250 si los shocks lo permiten.
- Panel JST (18 países, 1870–2020, anual) + crisis/retornos bancarios BVX + consolidaciones de GLP.
- Ratio parámetros/observaciones reportado en cada tabla.

## Replicación de calibración
1. Reproducir la estimación de v22 con su propio pipeline (FRED) para tener la línea base.
2. Replicar un resultado publicado de dependencia de estado (candidato: Ramey-Zubairy 2018, multiplicador
   con holgura frente a sin holgura) para validar el pipeline de LP.

## Fuera de alcance (v1)
- Estimación estructural completa del modelo DSGE de la Sección 2 de v22.
- El canal de coherencia institucional Γ como efecto causal (se mantiene como correlación, con su identificación como trabajo futuro).

## Desviaciones
_(ninguna todavía)_
