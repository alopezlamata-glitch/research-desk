# F13 · Diagnósticos del choque de Romer-Romer (generado por `code/mc/f13_checks.py`)

Sin la inversión. Choque `rr_shock` (suma de los 3 meses, F7); los dos contrastes son invariantes a reescalar el choque. Sin Volcker = la muestra completa sin 1979Q4–1982Q4, con el hueco concatenado (como R-F10). Ljung-Box con 12 retardos. Predictibilidad: MCO del choque sobre una constante y 4 retardos de 100·Δlog PIB real (`GDPC1`), 100·Δlog deflactor (`GDPDEF`) y Δ fed funds; F de Wald HC1 de las 12 pendientes = 0.

| muestra | N | ρ1 | ρ2 | ρ3 | ρ4 | Ljung-Box(12) | p | F de predictibilidad | g.l. | p |
|---|---|---|---|---|---|---|---|---|---|---|
| completa | 146 | -0.152 | -0.109 | 0.128 | -0.105 | 16.78 | 0.158 | 1.07 | (12, 133) | 0.391 |
| sin Volcker | 133 | 0.195 | -0.021 | 0.097 | 0.168 | 22.86 | 0.029 | 1.66 | (12, 120) | 0.085 |
