# Lecciones — Econometría

## 2026-11-04 · p01 · F4: Monte Carlo de una LP con choques de alta frecuencia y N ≈ 100
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Con choques HF agregados por trimestre, unos pocos trimestres dominan cada celda** (en p01, dos trimestres suman el 36–45 %
   de Σε² por celda estado × signo). Newey-West estándar infracubre (0,86–0,90) por **apalancamiento**, no por el solape: HC1
   cubre bien los términos U, pero no el más apalancado. Regla: antes de fijar los ee, mira el apalancamiento máximo y el peso de
   los dos choques mayores por celda; si es alto, usa residuos HC3 (u/(1−h_ii)) dentro del HAC y valídalo con MC.
2. **Si el MC fija los choques reales, el error de los choques futuros ε_{t+1..t+h} dentro de ȳ_t no se promedia**: aparece como un
   sesgo determinista proporcional a β. Regla: sepáralo con una corrida sin ruido (`design_error`) y no lo confundas con sesgo del
   estimador; el test de recuperación compara el sesgo con ese error, no con cero.
3. **Muestra con huecos (ZLB, COVID) y errores solapados:** el HAC debe medir los retardos en trimestres naturales; los pesos de
   Bartlett sobre la rejilla completa restringidos a las filas siguen siendo SDP. En p01 la diferencia con el HAC por filas es
   mínima, pero la versión de calendario es la correcta y cuesta lo mismo.
4. **Traducir una β de referencia de otra serie de choques exige dos supuestos que hay que escribir:** la respuesta del tipo al
   choque (aquí π_ffr, muy imprecisa: ee ≈ 50 %) y la forma de la IRF (pico frente a media de h=0..4). Repórtalos con sensibilidad.
5. **Calcula el efecto mínimo detectable antes de discutir escenarios.** Con β_ref, un choque de 1 desv. típica mueve ȳ ≈ 0,07 pp
   frente a un ee de 9–17 pp: la potencia es ≈ el tamaño (hace falta ≈ 40·β_ref para 0,8), y todo veredicto distinto de "no
   concluyente" es ruido. Haz esta cuenta en la fase de diseño, no después del prerregistro.

## 2026-11-08 · p01 · F9: Monte Carlo de una LP con ventana larga (h = 4..12) y choques narrativos
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Con una ventana larga y una IRF persistente, ȳ_t contiene la respuesta a los choques reales de t−10..t+12.** Si la serie de
   choques está autocorrelada en la muestra (Romer-Romer sin Volcker: ρ1 = 0,20, ρ4 = 0,17), la LP sesga β̂ de forma proporcional a
   β (en p01, +66 % en `s1r_lin` sin Volcker y −67 % en la réplica BS). No es un problema del error estándar: ningún HAC lo arregla.
   Regla: mide el error de diseño sin ruido para cada muestra y, si es grande, añade retardos (hasta el pico de la IRF supuesta) y
   adelantos (hasta el horizonte máximo) del choque como controles. Con β igual en los dos estados lo anula; con β distinto queda un
   resto, porque no van interactuados (interactuarlos lo anula, pero cuesta un ≈ 50 % de ee en p01).
2. **La regla de parada debe mirar también la cobertura centrada en β + error de diseño** («pseudo»): separa lo que es culpa del
   error estándar de lo que es sesgo condicional a los choques. En F4 la diferencia era despreciable; en F9 no.
3. **Más retardos de Bartlett no arreglan una cobertura baja con N ≈ 140 y un error muy persistente:** NW(12)+HC3 dio ee *menores*
   que NW(5)+HC3 en b_C sin Volcker y cubrió 0,90–0,92 (el sesgo a la baja del HAC con residuos MCO domina). Pruébalo con MC antes
   de suponer que «más ancho de banda = más conservador».
4. **Con la condición de H0 y un ee conservador, la potencia del árbol completo cae muy por debajo de la del contraste aislado**
   (en p01, 0,04–0,10 frente a la cota del Director de 0,2–0,4). Da siempre el MDE del árbol completo, no el de la desv. típ. de β̂.
5. **Calibra la heterocedasticidad del DGP en una muestra con suficientes episodios** (ρ de recesiones con 4 trimestres sale 0,2:
   ruido). Y liga la varianza a la ventana del error (e_t..e_{t+h}), no solo al choque contemporáneo, si quieres estresar las filas
   de alto apalancamiento.

## 2026-11-08 · p01 · F13: comprobaciones del prerregistro `s1r_*`
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Antes de discutir si una normalización «cambia la potencia», comprueba si es un reescalado del regresor.** La potencia de una
   MCO no cambia al reescalar ε, y β_ref escala con π. Que la media de 3 meses sea la suma/3 lo demuestran los t idénticos en
   las mismas réplicas (|Δt| ≈ 1e-12). Lo que sí cambia es la unidad del MDE «por pp de ε»: fija esa unidad por escrito.
2. **Para reproducir las celdas de un MC anterior, haz que la semilla sea una función pura de la celda** (ruido, m, índice de c) y
   da a las celdas nuevas índices libres. Así F13 reprodujo F9 exactamente sin volver a correrlo entero.

## 2026-11-08 · p01 · F13: comprobaciones del prerregistro `s1r_*` — puntos retirados
Estado: retirada
2. **Cuando te piden el MDE «en c = k», mira primero dónde cruza 0,8 la variante que importa.** En F9 el intervalo 3–5 era el de
   V1; en V3s el cruce estaba entre 5 y 7. Simula también en el punto del MDE, no solo en el que se pidió.
   *Motivo:* demasiado ligado a F9/F13

## 2026-11-08 · p01 · F15: requisitos previos a estimar `s1r_*`
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Al retirar una regla de decisión, no la borres del MC que la estudió: muévela allí.** `s1r_lp.h1_verdict` pierde la (b), pero
   F9 y F13 la necesitan para reproducir sus tablas; vive como `f9_power.h1_verdict_b`, y el test antiguo se reapunta a ella en vez
   de borrarse.
2. **El test de paridad Python–R debe correr sobre la misma inversión simulada que el MC, no sobre la real.** Se sustituye `inv` en
   el panel real por exp(nivel simulado / 100) y se pasa a los dos scripts. Además se comprueba que el script de análisis da lo mismo
   que el estimador del MC (rel. 1e-10): así lo que se va a estimar es exactamente lo que validó el MC.
3. **En R, `pmax(0, M)` devuelve un vector: toma los atributos del primer argumento y se pierde la dimensión.** Para recortar una
   matriz de pesos HAC, `pmax(M, 0)`.

## 2026-11-08 · p01 · F15: requisitos previos a estimar `s1r_*` — puntos retirados
Estado: retirada
4. **Un script de análisis no debe depender de columnas que no usa.** `sample_counts_s1r.samples` necesita `mps_bs23_orth`; el panel
   simulado para R no la tiene. Define la muestra con lo mínimo y comprueba en un test que coincide con los recuentos publicados.
   *Motivo:* regla genérica de higiene de código, poco específica

## 2026-11-08 · p01 · F16: estimación de `s1r_*` con la inversión real
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Antes de ejecutar un análisis prerregistrado, comprueba con `git diff <commit> -- code/` que el código es el revisado.** Así el
   informe puede afirmar «tal como en bd4f7bc» con evidencia, no de memoria.
2. **Cuando la puerta H0 falla, el informe no debe leer la medición de H1 como si fuera un veredicto, aunque sus p pasen de 0,05.**
   Se publica como medición y se deja anotado en «pendiente de decidir», para que lo vea quien decide. Así no se esconde, pero tampoco
   se interpreta.

## 2026-11-08 · p01 · F16: estimación de `s1r_*` con la inversión real — puntos retirados
Estado: retirada
3. **Si los tests de paridad y de equivalencia con el MC se dejan escritos antes de ver los datos (F15), la estimación real es un
   solo comando, sin nada que ajustar.** La paridad con los datos reales salió a 1e-12 a la primera.
   *Motivo:* constatación, no regla
