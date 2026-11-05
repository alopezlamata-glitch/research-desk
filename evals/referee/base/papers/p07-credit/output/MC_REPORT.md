# Monte Carlo de la LP (h = 1)

Estimador: `code/analysis/lp.py` (NW(2) sobre residuos HC3). DGP: `code/data/build_panel.py`. 1000 réplicas, semilla 7. Banda de cobertura aceptable: [0,92; 0,98].

| Parámetro | T | Verdadero | Sesgo | RMSE | Cobertura 95 % | Potencia | Fallos |
|---|---|---|---|---|---|---|---|
| shock | 120 | -1.300 | +0.045 | 0.200 | 0.945 | 1.000 | 0 |
| shock_x_credit | 120 | -1.040 | +0.038 | 0.213 | 0.934 | 0.994 | 0 |
| shock | 60 | -1.300 | +0.084 | 0.305 | 0.923 | 0.982 | 0 |
| shock_x_credit | 60 | -1.040 | +0.076 | 0.310 | 0.929 | 0.838 | 0 |

Con T = 120 la cobertura está dentro de la banda: los intervalos de NW se usan en el texto.
