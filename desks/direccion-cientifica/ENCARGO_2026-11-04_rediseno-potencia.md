# Encargo de la Coordinación al Director científico — 2026-11-04 · Rediseño de la etapa 1 para ganar potencia

Modelo: opus

Rutas relativas a la raíz del repo (`../../`). Ahora puedes ejecutar `uv run python` para comprobar cuentas (no para implementar).

## Situación
El Monte Carlo F4 (`papers/p01-liquidity/output/F4_MC_REPORT.md` y `output/tables/f4_power.md`) muestra que `s1_liq`, tal como está
prerregistrada (`SPEC.md`), **no tiene potencia**. Con β_ref la potencia es ≈ tamaño, y la de 0,8 exige un efecto ≈ 40·β_ref, lo que es
implausible. Un choque de 1 desviación típica mueve ȳ 0,067 pp, frente a errores estándar de 9–17 pp. **Nadie ha estimado con la inversión
real: la muestra está intacta.** Lo que se cambie ahora es una Desviación legítima, previa a ver los datos.

## Qué hacer
Escribir `papers/p01-liquidity/exploration/REDESIGN_POWER_2026-11-04.md`, una propuesta para los autores.
1. **Diagnóstico:** ¿de dónde sale la falta de potencia? Varianza de los choques HF frente a la del ruido de la inversión, celdas, número
   de parámetros. Cita con página lo que diga la literatura (p. ej., BS p. 4 sobre los choques HF y la potencia).
2. **Alternativas de familias distintas**, con el orden de magnitud de la ganancia de potencia, argumentado o con una cuenta rápida en
   Python. Al menos:
   - **(a) Más estructura:** VAR/proxy-SVAR o LP con suavizado o shrinkage (sesgo frente a varianza de LP y VAR); un VAR con umbral o
     dependiente del estado.
   - **(b) Variación transversal:** un panel de sectores o de clases de tamaño con datos públicos, como el Quarterly Financial Report del
     Census (liquidez e inversión por tamaño de empresa e industria). El Z.1 por sectores se puede comprobar con `datalake/CATALOG.md`.
     Con efectos fijos de tiempo el ruido agregado desaparece. **Ojo:** eso identifica diferencias entre estados (E1), no el nivel de H1.
     Di qué hipótesis se vuelven contrastables.
   - **(c) Choque con más varianza o con un instrumento más fuerte:** Romer-Romer, LP-IV con el tipo, frecuencia mensual.
   - **(d) Variable de resultado más sensible o más cercana al mecanismo:** préstamos C&I, emisión, liquidez de las empresas (m_u),
     inversión de las empresas pequeñas.
   - **(e) Aceptar "no concluyente por potencia"** y desplazar la contribución a la teoría y a la etapa 2.
3. **Hipótesis contrastable y potencia esperada** para cada alternativa, comparada con la rúbrica de la SPEC. Ninguna alternativa vale si
   exige mirar la respuesta de la inversión real.
4. **Recomendación:** qué diseño, qué se prerregistra de nuevo y qué tiene que validar Econometría con un nuevo Monte Carlo antes de estimar.
   Incluye la Desviación de errores estándar de F4 (NW(5) con residuos HC3) si sigue aplicando.

Ninguna afirmación sobre la literatura sin página. Marca **[criterio propio]**. Lecciones en `kb/lessons/scientific-director.md`
(`Estado: candidata`). No edites la SPEC ni ningún otro archivo.
