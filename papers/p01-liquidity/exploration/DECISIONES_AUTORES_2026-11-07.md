# p01 · Decisiones de los autores sobre la etapa 1 — preparado por la Coordinación (2026-11-07)

Para decidir sin releer todo. Fuentes: la propuesta del Director científico
(`exploration/REDESIGN_POWER_2026-11-04.md`, §4–5, commit c30cdae), el Monte Carlo de F4 (`output/F4_MC_REPORT.md`) y la
auditoría del Referee **R-F4** (`audits/2026-11-05_F4_mc.md`, APROBADO CON CAMBIOS, replicación en Python y en R). Las cifras
salen de esos documentos; aquí no se calcula nada nuevo.

## Dónde estamos

- **`s1_liq` tal como está no tiene potencia.** Frente a β_ref, la potencia de "confirma" es ≈ 0,03, igual que el tamaño del
  test, y hace falta un efecto ≈ 40·β_ref para llegar a 0,8 (F4, confirmado por R-F4).
- **La causa es el choque, no el estimador.** `mps_bs23_orth` tiene F = 4,2 en la primera etapa sobre el fed funds; ningún
  estimador alternativo cierra un hueco de ×20–40 (Director, §0).
- **R-F4 añade dos cosas que cambian el contexto de cualquier opción:**
  1. *La condición de H0.* La SPEC dice que H1 solo se interpreta si se confirma H0 (`s1_lin`). F4 dio las probabilidades de
     veredicto sin esa condición. Con ella, H0 se confirma con P ≈ 0,077 y en ≈ 92 % de los casos el resultado es "H0 no se
     confirma, H1 no se interpreta".
  2. *El error estándar recomendado (NW(5) con residuos HC3) no está validado con heterocedasticidad.* Si la varianza del
     error crece con el tamaño del choque, cubre 0,920 ± 0,005: justo en el borde de la banda [0,92; 0,98], sin margen.
  - Menores con efecto en el rediseño: el umbral de refutación (b), δ = 0,146·|β̂_U|, es ruido cuando ee(β̂_U) ≫ |β_U| (de media
    sale ≈ 2 veces el β verdadero) y daría falsas refutaciones en cuanto mejore la precisión de β_C; y β_ref se calculó con la
    respuesta del fed funds en h = 0 (con h = 1 sería −1,20 en vez de −0,88).

## Las 7 decisiones

| # | Decisión | Director científico | Lo que añade R-F4 / Coordinación |
|---|---|---|---|
| 1 | ¿Se para `s1_liq` tal como está? | **Sí.** | De acuerdo. R-F4 lo refuerza: con la condición de H0, el 92 % de los resultados serían "H1 no se interpreta". |
| 2 | ¿Romer-Romer pasa a choque principal, con BS-orth como réplica posterior a 1984? (Desviación sobre la decisión 1 del 2026-11-04) | **Sí.** Es lo único que da varianza del choque en unidades de fed funds (×5,1 en t; ×3,2 sin Volcker). | De acuerdo, con un riesgo que hay que vigilar: 4 trimestres de Volcker concentran el 53 % de Σε². La robustez sin 1979Q4–1982Q4 tiene que ser obligatoria, y Datos debe publicar antes D1/D2 por estado en la muestra nueva. |
| 3 | ¿Se juntan subidas y bajadas en H1 y la asimetría pasa a exploratoria? (Desviación sobre el diseño F) | **Sí.** Separarlas no tiene potencia en ningún diseño agregado de EE. UU. (≤ 0,21). | Es la decisión que más cambia el paper: revierte una parte del diseño F que aprobasteis. Técnicamente está justificada. |
| 4 | ¿Ventana h = 4..12 en vez de h = 0..4? | **Sí** (×1,34; la forma sale de TT p. 11, no de nuestros datos). | De acuerdo. La fecha de corte de los choques (≈ 2005Q2, para no entrar en 2008 con h = 12) la fija Datos antes de estimar. |
| 5 | ¿Se registra ya la Desviación de errores estándar de F4 (NW(5) con residuos HC3)? | **Sí, se mantiene**, y con Romer-Romer hace todavía más falta. | **Discrepamos en el momento.** R-F4 muestra que con heterocedasticidad queda en el borde (0,920) y con Romer-Romer el apalancamiento es mayor. Proponemos **no registrarla todavía**: que el MC nuevo la valide con un DGP heterocedástico ligado a los trimestres de alto apalancamiento, y registrar la Desviación con el resultado. Si no pasa, se elige otro error antes de estimar. |
| 6 | ¿Se abre la etapa 1b transversal (gradiente de exposición ∂I_u/∂g = 1 − ω > 0, panel con efectos fijos de tiempo)? ¿Hay acceso a Compustat/WRDS? | **Sí, condicionada** a datos (G ≥ 40 grupos) y a un MC con potencia ≥ 0,8; si pasa la puerta, es la prueba confirmatoria principal. | De acuerdo. **Necesitamos que nos digáis si tenéis acceso a WRDS**; si no, Datos busca una fuente gratuita (QFR del Census). |
| 7 | ¿Se acepta prerregistrar una H1 con potencia esperada ≈ 0,2–0,4, presentada como medición acotada? | **Sí**, con el MDE ≈ 2–3·β_ref escrito ex ante y la regla (b) inactiva mientras la potencia sea < 0,8. | De acuerdo, con dos condiciones de R-F4: las probabilidades de veredicto del MC nuevo se calculan **con la condición de H0** incluida, y el umbral (b) se revisa (no puede depender de β̂_U ruidoso). |

## Si aceptáis las recomendaciones, lo que pondría en marcha la Coordinación

1. **Desviación fechada en la SPEC** con vuestras decisiones. Cambia el texto congelado del prerregistro, así que la entrada
   llevará la huella `prereg <hash>` que da `tools/integrity.py`. El prerregistro nuevo (`s1r_*`) se escribe **antes** de ver
   datos y se congela con un `prereg_commit` nuevo cuando lo aprobéis.
2. **Datos:** serie de Romer-Romer (Coibion/Ramey) en el datalake con su MANIFEST; fecha de corte exacta; D1/D2 (observaciones
   y Σ|ε| por estado) en la muestra nueva, con aviso si los trimestres de Volcker caen casi todos en un estado; disponibilidad
   del QFR.
3. **Econometría, MC nuevo con `mc-validate`** antes de estimar: DGP con Romer-Romer y D reales; estadístico h = 4..12 con signos
   juntos; cobertura de NW(5)+HC3 **también con ruido heterocedástico**, con T y T/2; curva de potencia c ∈ {1, 2, 3, 5};
   probabilidades de veredicto **con la condición de H0**; la misma tabla sin Volcker.
4. **Literatura:** Li, Plagborg-Møller y Wolf (LP frente a VAR), Ramey (2016) en el original, una fuente para el tamaño como
   proxy de exposición a tipo variable, y la extensión de Romer-Romer más allá de 2007 si existe.
5. **Referee:** auditoría del MC nuevo en sesión nueva antes de que se estime nada, como con F4.

Datos y Literatura pueden trabajar en paralelo (máximo 2 desks); Econometría empieza cuando Datos entregue.

## Qué necesitamos de vosotros

Una respuesta a cada una de las 7 decisiones (vale "sí a todo lo recomendado", indicando qué postura tomáis en la 5) y si
tenéis acceso a WRDS.
