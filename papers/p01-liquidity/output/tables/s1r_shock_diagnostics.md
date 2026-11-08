# Diagnósticos de los choques de `s1r_*` (generado por `code/analysis/01_s1r_estimate.py`)

Sin la inversión (SPEC, «Diagnósticos de los choques»). D1/D2: trimestres y Σ|ε| por estado de D_{t−1} (mediana de la muestra completa). D3: MCO de ε_t sobre (1, D_{t−1}, s_{t−1}), ee HC1, F de Wald de las 2 pendientes. Ljung-Box con 12 retardos. Predictibilidad: MCO de ε_t sobre una constante y 4 retardos de 100·Δlog PIB real, 100·Δlog deflactor y Δffr, F de Wald HC1 de las 12 pendientes. Sin Volcker = sin 1979Q4–1982Q4, con el hueco concatenado.

| muestra | N | D1 restr. | D1 holg. | D2 Σ\|ε\| restr. | D2 Σ\|ε\| holg. | D3 F | D3 p | Ljung-Box(12) | p | F predict. | g.l. | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| completa | 146 | 73 | 73 | 31.036 | 21.754 | 0.50 | 0.606 | 16.78 | 0.158 | 1.07 | (12, 133) | 0.391 |
| sin Volcker | 133 | 62 | 71 | 18.195 | 19.810 | 0.49 | 0.613 | 22.86 | 0.029 | 1.66 | (12, 120) | 0.085 |
