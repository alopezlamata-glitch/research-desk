# Monte Carlo de la LP (h = 12)

Estimador: `code/analysis/lp.py` (6 retardos, HC3). DGP propio calibrado a los datos (`code/mc/mc_lp.py`): β = -0.1, γ = -0.2, ρ = 0.246. 1000 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 359 | -0.133 | +0.009 | 0.170 | 0.950 | 0.100 | 0 |
| shock_x_credit | 359 | -0.265 | +0.015 | 0.284 | 0.962 | 0.113 | 0 |
| shock | 179 | -0.133 | +0.023 | 0.283 | 0.952 | 0.056 | 0 |
| shock_x_credit | 179 | -0.265 | +0.006 | 0.561 | 0.964 | 0.046 | 0 |

Con T = 359 la cobertura está dentro de la banda: los intervalos se usan en el texto.
