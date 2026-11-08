# p01 · Decisiones de los autores para el prerregistro nuevo (F11) — preparado por la Coordinación (2026-11-08)

Fuentes: el MC de Econometría (`output/F9_MC_REPORT.md`, commit d1a77f5) y la auditoría del Referee **F10**
(`audits/2026-11-08_F9_mc.md`, APROBADO CON CAMBIOS, réplica en R, commit 99e6d1c). Las cifras salen de esos documentos.
Nada de esto ha mirado la respuesta de la inversión: el prerregistro sigue pudiendo escribirse "antes de ver resultados".

## Dónde estamos

- **Sesgo nuevo y su corrección.** Con la ventana h = 4..12, la LP con solo controles está sesgada porque los choques de
  Romer-Romer están autocorrelados en la muestra. La especificación `aum` (choques de t−10 a t+12 como controles) lo corrige.
  El Referee lo confirma con tres formas de IRF distintas.
- **Error estándar.** NW(5) con residuos HC3 sobre `aum` cubre 0,948–0,990 en todos los DGP, también con heterocedasticidad (la
  condición de vuestra decisión 5). Nunca infracubre; se pasa por arriba en varias celdas. El Referee probó seis alternativas y
  todas son peores: la sobrecobertura es aceptable si se declara.
- **Potencia.** Con la condición de H0, la potencia frente a β_ref es **0,04–0,10 si β_ref se mide con el fed funds en h = 0, y
  0,14–0,27 si se mide en h = 1** (F10). La segunda se solapa con el 0,2–0,4 que aceptasteis; la primera no. **Esa elección no
  puede hacerse mirando cuál da más potencia**: la decide qué normalización usa Tenreyro-Thwaites para su −2,5 %, que está
  comprobando Literatura (F12).
- **La puerta H0 es el cuello de botella:** con un efecto igual a β_ref, H0 no se confirma en el 82–87 % de los casos, y entonces
  H1 no se interpreta.

## Las decisiones

| # | Decisión | Recomendación de la Coordinación | Por qué |
|---|---|---|---|
| 1 | Variante y especificación | **V3s con `aum`** | V1 con `aum` confirma en falso un 10–14 % frente al rival (β_C = 0, β_U grande), por encima de α = 0,05: el prerregistro no puede adoptarla (F10, mayor 2). V2 y V3s se mantienen ≤ 0,055. V3s usa la muestra completa y exige que se sostenga sin Volcker; F9 y F10 la recomiendan. La alternativa, V1 con `aumi`, corrige el tamaño pero pierde mucha potencia (0,63 → 0,36 con c = 3). |
| 2 | Normalización de β_ref (fed funds en h = 0 o h = 1) | **Esperar a F12 y adoptar la de Tenreyro-Thwaites**, sea cual sea | Es la única forma de que no sea una elección por resultados. El MDE se escribe además en pp de ȳ por pp de choque, que no depende de esta elección (≈ 10,0 en V2/V3s). |
| 3 | Estimando "choque aislado" | **Declararlo en la SPEC**, con el Ljung-Box y el contraste de predictibilidad de los choques | Controlar por choques futuros estima la respuesta a un choque aislado, no la total; vale si los choques no están autocorrelados en la población. RR sin Volcker da Ljung-Box p = 0,029 (F10, mayor 1). Falta la cita de Teulings-Zubanov (F12). |
| 4 | Error estándar | **NW(5) con residuos HC3 sobre `aum`, con la sobrecobertura declarada como excepción a la banda** | Es lo que mejor cubre; las alternativas infracubren o inflan el tamaño (F10). Con esto se registra la Desviación de errores estándar que dejasteis pendiente en la decisión 5. |
| 5 | Definición exacta de V3 | **V3s: H1 se confirma con la muestra completa *y* sin Volcker; H0 se exige solo con la muestra completa** | Es lo que se simuló; exigir también H0 sin Volcker obligaría a rehacer el MC y bajaría más la potencia. |
| 6 | Regla de refutación | **H1 solo se refuta por (a)**; la regla (b) se retira | Con esta precisión (b) no puede activarse con ninguna versión del umbral (F9 y F10). Mantenerla escrita sería decorativo. |
| 7 | Puerta H0 | **Mantenerla**, con la potencia escrita tal cual | Es vuestra lógica original (H1 solo tiene sentido si el choque mueve la inversión en media). Quitarla subiría la potencia, pero cambiar una regla de decisión porque el diseño no da potencia, aunque no se hayan visto datos, se parece demasiado a ajustar el contraste. Si la quitáis, que sea por un argumento económico, no de potencia. |

## La pregunta de fondo

Aun con las mejores elecciones, la H1 agregada queda como una **medición acotada**: potencia ≈ 0,14–0,27 en el mejor caso, y
"H1 no se interpreta" como resultado más probable. Hay dos caminos razonables:

- **(A) Seguir:** prerregistrar `s1r_*` con las decisiones de arriba y la potencia escrita, estimar, y presentar el resultado
  como medición con su IC. Es barato: el diseño, el código y la auditoría ya están hechos.
- **(B) Replantear el peso de la etapa 1:** prerregistrarla igual, pero mover el esfuerzo principal a la etapa 1b (panel
  QFR, gradiente de exposición), que es la que podría tener potencia. El QFR es gratuito desde 2006Q3 pero no tiene tipo
  variable; el proxy (cuota de deuda bancaria) es la parte débil y habría que validarlo antes.

La Coordinación recomienda **(A) ahora**, y abrir en paralelo un MC de puerta para la 1b (G real, proxy y potencia) antes de
invertir más en ella.

## Qué necesitamos de vosotros

Respuesta a las decisiones 1, 3–7 y al camino (A o B). La decisión 2 la cerramos con el resultado de F12; si la normalización
de TT es ambigua, os la traemos con las dos cifras.
