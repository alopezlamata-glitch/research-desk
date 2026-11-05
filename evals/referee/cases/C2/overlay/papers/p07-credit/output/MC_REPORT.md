# Monte Carlo de la LP (h = 1)

Estimador: `code/analysis/lp.py` (NW(2) sobre residuos HC3). DGP: `code/data/build_panel.py`. 1000 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 120 | -1.300 | +0.048 | 0.235 | 0.936 | 1.000 | 0 |
| shock_x_credit | 120 | -1.040 | +0.038 | 0.213 | 0.935 | 0.995 | 0 |
| shock | 60 | -1.300 | +0.088 | 0.357 | 0.925 | 0.921 | 0 |
| shock_x_credit | 60 | -1.040 | +0.078 | 0.312 | 0.923 | 0.843 | 0 |

Con T = 120 la cobertura está dentro de la banda: los intervalos de NW se usan en el texto.
