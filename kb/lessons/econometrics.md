# Lecciones — Econometría

## 2026-11-04 · p01 · F4: Monte Carlo de una LP con choques de alta frecuencia y N ≈ 100
Estado: candidata
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
