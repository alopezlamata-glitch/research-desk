# Diccionario de data/clean/panel.parquet

Trimestral, 1994T1–2023T4 (T = 120). Generado por `code/data/build_panel.py` (semilla 20261105).

| Columna | Descripción | Unidad |
|---|---|---|
| date | Trimestre | AAAAQn |
| loginv | 100 × log de la inversión no residencial real | log × 100 |
| dinv | Crecimiento trimestral de la inversión (Δ loginv) | pp |
| dgdp | Crecimiento trimestral del PIB real | pp |
| infl | Inflación trimestral del deflactor | pp |
| term_spread | Diferencial 10 años − 3 meses | pp |
| baa_spread | Diferencial Baa − bono a 10 años | pp |
| vix | Índice de volatilidad implícita VIX (media trimestral) | puntos |
| ted_spread | Diferencial Libor 3 meses − letra a 3 meses | pp |
| sloos | % neto de bancos que endurecen el crédito a empresas | % |
| ff4 | Sorpresa monetaria de alta frecuencia (futuro de fed funds, ventana de 30 min) | pp |
| shock | ff4 estandarizada en la muestra | desv. típ. |
| credit | sloos estandarizada en la muestra (estado del crédito; > 0 = restringido) | desv. típ. |
| fci | Índice de condiciones financieras: media de term_spread, baa_spread, vix, ted_spread estandarizados | desv. típ. |
