# Recuentos D1/D2 de la etapa 1 rediseñada (F7)

Generado por `code/data/sample_counts_s1r.py` sobre `data/clean/stage1r_us.parquet`. No se ha estimado nada ni se ha mirado la inversión. Estado: `s_{t−1}` frente a la mediana de la muestra (ver docstring); Volcker = 1979Q4–1982Q4 (13 trimestres).

## Choque `rr_shock`: 1969Q1–2005Q2, N = 146, mediana de s_(t−1) = -0.0101

**Con Volcker**

| estado | N | trimestres con ε≠0 | Σ\|ε\| |
|---|---|---|---|
| restringido | 73 | 72 | 31.036 |
| holgado | 73 | 73 | 21.754 |

**Sin 1979Q4–1982Q4**

| estado | N | trimestres con ε≠0 | Σ\|ε\| |
|---|---|---|---|
| restringido | 62 | 61 | 18.195 |
| holgado | 71 | 71 | 19.810 |

Trimestres de Volcker por estado: restringido 11, holgado 2 (de 13). Σ|ε| de Volcker: restringido 12.841 de 31.036; holgado 1.944 de 21.754.

## Choque `mps_bs23_orth`: 1988Q1–2005Q2, N = 70, mediana de s_(t−1) = 0.0363

**Con Volcker**

| estado | N | trimestres con ε≠0 | Σ\|ε\| |
|---|---|---|---|
| restringido | 35 | 35 | 2.229 |
| holgado | 35 | 35 | 1.721 |

**Sin 1979Q4–1982Q4**

| estado | N | trimestres con ε≠0 | Σ\|ε\| |
|---|---|---|---|
| restringido | 35 | 35 | 2.229 |
| holgado | 35 | 35 | 1.721 |

Trimestres de Volcker por estado: restringido 0, holgado 0 (de 0). Σ|ε| de Volcker: restringido 0.000 de 2.229; holgado 0.000 de 1.721.

## Aviso de concentración (Volcker en un solo estado, umbral > 75 %)

**SÍ**: rr_shock: 11 de 13 trimestres de Volcker en 'restringido'
