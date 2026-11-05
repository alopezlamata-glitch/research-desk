# Monte Carlo de la LP (h = 1)

Estimador: `code/analysis/lp.py` (NW(2) sobre residuos HC3). DGP: `code/data/build_panel.py`. 1000 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 120 | -1.300 | +0.044 | 0.186 | 0.945 | 1.000 | 0 |
| shock_x_credit | 120 | -0.195 | +0.004 | 0.182 | 0.943 | 0.166 | 0 |
| shock | 60 | -1.300 | +0.085 | 0.287 | 0.922 | 0.994 | 0 |
| shock_x_credit | 60 | -0.195 | +0.011 | 0.266 | 0.952 | 0.096 | 0 |

Con T = 120 la cobertura está dentro de la banda: los intervalos de NW se usan en el texto.
