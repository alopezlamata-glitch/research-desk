# Recuentos de la muestra de PREREG_DRAFT §6

Generado por `code/data/sample_counts.py` sobre `data/clean/stage1_us.parquet` (Z.1 2026-09-11, FRED 2026-11-04). No se ha
estimado nada. Fecha t = trimestre del choque; el estado se mide en t−1.

**Definiciones.** `s_t = log(liq_broad_debt_t) − media(log(liq_broad_debt_{t−1…t−12}))`.
Restringido (liquidez) = `s_{t−1}` < mediana de `s_{t−1}` **en la muestra**; (DSR) = `dsr_nfc_{t−1}` > mediana de `dsr_nfc_{t−1}`
en la muestra con DSR. Con N impar, la observación mediana queda en "holgado". Choque = `mps_bs23_orth` (suma trimestral).
**No** se imponen aquí las condiciones del resultado ȳ_t ni de los controles: están definidos en toda la muestra (inversión desde 1947,
PIB, deflactor, `y2_mean`, `ebp` desde 1985), de modo que no recortan.

## Cascada (muestra principal)
| paso | N |
|---|---|
| 1988Q2–2023Q4 | 143 |
| sin ZLB (`ffr` < 0.25) | 107 |
| sin 2019Q1–2021Q4 | 102 |
| con `mps_bs23_orth` no NaN | 102 |
| con `s_{t-1}` definido | 102 |

Trimestres excluidos por ZLB dentro de 1988Q2–2023Q4: 2009Q1, 2009Q2, 2009Q3, 2009Q4, 2010Q1, 2010Q2, 2010Q3, 2010Q4, 2011Q1, 2011Q2, 2011Q3, 2011Q4, 2012Q1, 2012Q2, 2012Q3, 2012Q4, 2013Q1, 2013Q2, 2013Q3, 2013Q4, 2014Q1, 2014Q2, 2014Q3, 2014Q4, 2015Q1, 2015Q2, 2015Q3, 2015Q4, 2020Q2, 2020Q3, 2020Q4, 2021Q1, 2021Q2, 2021Q3, 2021Q4, 2022Q1.

## Estado de liquidez (`s1_liq`): N = 102, mediana de s_{t−1} = 0.0103
| estado | ε<0 (bajada) | ε>0 (subida) | total |
|---|---|---|---|
| restringido | 22 | 29 | 51 |
| holgado | 28 | 23 | 51 |
| total | 50 | 52 | 102 |

## Estado DSR (`s1_dsr`, desde 1999Q2): N = 58, mediana de dsr_{t−1} = 41.400
| estado | ε<0 (bajada) | ε>0 (subida) | total |
|---|---|---|---|
| restringido | 11 | 16 | 27 |
| holgado | 13 | 18 | 31 |
| total | 24 | 34 | 58 |

## Cobertura de la medida de g (E.2, `stbl_short_share`, 1997Q2–2017Q2)
Observaciones de la muestra principal con `stbl_short_share` disponible: **53** (de 102); en la muestra DSR: **45**.
