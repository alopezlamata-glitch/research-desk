# Monte Carlo de la LP (h = 12)

Estimador: `code/analysis/lp.py` (6 retardos, White). DGP propio calibrado a los datos (`code/mc/mc_lp.py`): β = -0.1, γ = -0.2, ρ = 0.246. 1000 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 359 | -0.133 | +0.006 | 0.172 | 0.905 | 0.198 | 0 |
| shock_x_credit | 359 | -0.265 | +0.037 | 0.307 | 0.887 | 0.217 | 0 |
| shock | 179 | -0.133 | +0.039 | 0.275 | 0.872 | 0.169 | 0 |
| shock_x_credit | 179 | -0.265 | +0.021 | 0.532 | 0.872 | 0.163 | 0 |

Los intervalos de esta especificación son los que se usan en el texto.
