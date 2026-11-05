# Monte Carlo de la LP (h = 1)

Estimador: `code/analysis/lp.py` (NW(2) sobre residuos HC3). DGP: `code/data/build_panel.py`. 500 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 120 | -1.300 | +0.031 | 0.204 | 0.932 | 1.000 | 0 |
| shock_x_credit | 120 | -1.040 | +0.042 | 0.219 | 0.936 | 0.990 | 0 |
| shock | 60 | -1.300 | +0.090 | 0.300 | 0.934 | 0.984 | 0 |
| shock_x_credit | 60 | -1.040 | +0.111 | 0.352 | 0.912 | 0.780 | 0 |

Con T = 120 la cobertura está dentro de la banda: los intervalos de NW se usan en el texto.
