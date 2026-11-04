# F4 · tablas del Monte Carlo de `s1_liq` (generado por `code/mc/f4_power.py`, semilla 20261104, 1000 réplicas)

## Calibración
- N = 102; k = 16 regresores; N−k = 86. Desv. típica de ε en la muestra = 0.0762; autocorrelación(1) = -0.078.
- AR(2) de 100·Δlog `inv_nonres_q` en las 102 filas (sin choques): μ = 0.258, φ1 = 0.465, φ2 = 0.271, σ_e = 1.357; κ = 1.865.
- Respuesta de los tipos a ε (MCO, ee White ×N/(N−k)), `var_{t+h} − var_{t−1}`:
  - ffr, h=0: 1.761 (ee 0.856)
  - ffr, h=1: 2.406 (ee 1.648)
  - y2_mean, h=0: 0.697 (ee 0.732)
  - y2_mean, h=1: 1.163 (ee 1.358)
- **β_ref = -2.5 × media(h=0..4)/10 × π_ffr = -0.881** pp de ȳ por 1 pp de ε (π_ffr = 1.761). Sensibilidad: pico en h=8 → -1.101; h=12 → -0.734; π_ffr ± 1,645 ee → [-1.585, -0.176].
- Efecto en ȳ de un choque de 1 desv. típica con β_ref: -0.0671 pp.

## 1. Escenarios: β_U = β_ref, β_C = m·β_ref (subidas y bajadas a la vez)

### 1a. Sesgo, RMSE y cobertura del IC al 95 % (t con N−k g.l.), ee prerregistrado y alternativas

«error de diseño» = β̂ − β sin ruido con T = N (respuesta a choques futuros reales; ver `design_error`).

| m | T | ee | término | verdadero | sesgo | error de diseño | RMSE | desv. típ. β̂ | ee medio | cobertura |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 102 | NW5 calendario (prerreg.) | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 8.689 | 0.872 |
| 1.0 | 102 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 13.536 | 0.900 |
| 1.0 | 102 | NW5 calendario (prerreg.) | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 6.773 | 0.887 |
| 1.0 | 102 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 11.331 | 0.891 |
| 1.0 | 102 | NW5 filas | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 8.706 | 0.876 |
| 1.0 | 102 | NW5 filas | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 13.541 | 0.900 |
| 1.0 | 102 | NW5 filas | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 6.757 | 0.888 |
| 1.0 | 102 | NW5 filas | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 11.335 | 0.892 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 9.463 | 0.912 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 14.742 | 0.919 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 7.376 | 0.921 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 12.340 | 0.913 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 9.823 | 0.917 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 16.070 | 0.951 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 8.186 | 0.946 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 13.237 | 0.928 |
| 1.0 | 102 | HC3 | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 11.781 | 0.959 |
| 1.0 | 102 | HC3 | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 18.189 | 0.977 |
| 1.0 | 102 | HC3 | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 10.247 | 0.980 |
| 1.0 | 102 | HC3 | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 15.769 | 0.963 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | b_pos_C | -0.881 | -0.439 | +0.043 | 10.901 | 10.892 | 11.186 | 0.954 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | -0.117 | +0.251 | 15.797 | 15.797 | 16.669 | 0.949 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | b_neg_C | -0.881 | -0.098 | +0.028 | 7.843 | 7.842 | 9.215 | 0.963 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.073 | +0.136 | 13.581 | 13.581 | 14.703 | 0.953 |
| 1.0 | 51 | NW5 calendario (prerreg.) | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 10.349 | 0.798 |
| 1.0 | 51 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 14.585 | 0.877 |
| 1.0 | 51 | NW5 calendario (prerreg.) | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 7.116 | 0.868 |
| 1.0 | 51 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 12.510 | 0.859 |
| 1.0 | 51 | NW5 filas | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 10.336 | 0.792 |
| 1.0 | 51 | NW5 filas | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 14.590 | 0.876 |
| 1.0 | 51 | NW5 filas | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 7.092 | 0.867 |
| 1.0 | 51 | NW5 filas | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 12.498 | 0.858 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 12.493 | 0.874 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 17.606 | 0.928 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 8.590 | 0.923 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 15.101 | 0.927 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 12.955 | 0.876 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 20.235 | 0.964 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 10.377 | 0.961 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 17.197 | 0.958 |
| 1.0 | 51 | HC3 | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 25.393 | 0.976 |
| 1.0 | 51 | HC3 | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 25.738 | 0.988 |
| 1.0 | 51 | HC3 | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 17.070 | 0.991 |
| 1.0 | 51 | HC3 | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 22.682 | 0.982 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | b_pos_C | -0.881 | +0.081 | — | 16.743 | 16.743 | 24.080 | 0.963 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | +0.997 | — | 19.041 | 19.015 | 22.665 | 0.975 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | b_neg_C | -0.881 | -0.067 | — | 9.939 | 9.938 | 14.542 | 0.983 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | -0.050 | — | 16.614 | 16.614 | 20.218 | 0.971 |
| 0.5 | 102 | NW5 calendario (prerreg.) | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 8.560 | 0.869 |
| 0.5 | 102 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 13.581 | 0.887 |
| 0.5 | 102 | NW5 calendario (prerreg.) | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 6.680 | 0.884 |
| 0.5 | 102 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 11.241 | 0.890 |
| 0.5 | 102 | NW5 filas | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 8.566 | 0.865 |
| 0.5 | 102 | NW5 filas | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 13.585 | 0.887 |
| 0.5 | 102 | NW5 filas | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 6.667 | 0.884 |
| 0.5 | 102 | NW5 filas | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 11.254 | 0.890 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 9.322 | 0.902 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 14.790 | 0.913 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 7.275 | 0.900 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 12.242 | 0.926 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 9.706 | 0.911 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 16.117 | 0.937 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 8.092 | 0.928 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 13.169 | 0.941 |
| 0.5 | 102 | HC3 | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 11.630 | 0.956 |
| 0.5 | 102 | HC3 | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 18.223 | 0.960 |
| 0.5 | 102 | HC3 | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 10.129 | 0.962 |
| 0.5 | 102 | HC3 | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 15.661 | 0.969 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | b_pos_C | -0.440 | +0.135 | +0.004 | 11.023 | 11.022 | 11.003 | 0.940 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | -0.268 | +0.244 | 16.618 | 16.616 | 16.754 | 0.941 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | b_neg_C | -0.440 | -0.360 | +0.025 | 8.373 | 8.366 | 9.090 | 0.949 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.612 | +0.215 | 13.498 | 13.484 | 14.585 | 0.958 |
| 0.5 | 51 | NW5 calendario (prerreg.) | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 10.171 | 0.784 |
| 0.5 | 51 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 14.638 | 0.880 |
| 0.5 | 51 | NW5 calendario (prerreg.) | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 6.962 | 0.849 |
| 0.5 | 51 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 12.471 | 0.866 |
| 0.5 | 51 | NW5 filas | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 10.161 | 0.784 |
| 0.5 | 51 | NW5 filas | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 14.635 | 0.880 |
| 0.5 | 51 | NW5 filas | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 6.934 | 0.848 |
| 0.5 | 51 | NW5 filas | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 12.456 | 0.864 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 12.278 | 0.850 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 17.670 | 0.936 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 8.404 | 0.907 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 15.054 | 0.916 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 12.958 | 0.868 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 20.213 | 0.972 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 10.220 | 0.958 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 17.244 | 0.960 |
| 0.5 | 51 | HC3 | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 25.098 | 0.966 |
| 0.5 | 51 | HC3 | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 25.765 | 0.988 |
| 0.5 | 51 | HC3 | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 16.959 | 0.992 |
| 0.5 | 51 | HC3 | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 22.940 | 0.983 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | b_pos_C | -0.440 | -0.039 | — | 17.110 | 17.110 | 23.382 | 0.951 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | -0.832 | — | 18.903 | 18.885 | 22.850 | 0.982 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | b_neg_C | -0.440 | -0.215 | — | 9.878 | 9.875 | 14.317 | 0.983 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.293 | — | 16.512 | 16.510 | 20.420 | 0.968 |
| 0.146 | 102 | NW5 calendario (prerreg.) | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 8.675 | 0.869 |
| 0.146 | 102 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 13.549 | 0.887 |
| 0.146 | 102 | NW5 calendario (prerreg.) | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 6.706 | 0.895 |
| 0.146 | 102 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 11.244 | 0.864 |
| 0.146 | 102 | NW5 filas | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 8.701 | 0.868 |
| 0.146 | 102 | NW5 filas | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 13.553 | 0.888 |
| 0.146 | 102 | NW5 filas | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 6.697 | 0.896 |
| 0.146 | 102 | NW5 filas | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 11.257 | 0.862 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 9.447 | 0.890 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 14.755 | 0.924 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 7.304 | 0.911 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 12.245 | 0.894 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 9.857 | 0.904 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 16.050 | 0.951 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 8.141 | 0.934 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 13.246 | 0.926 |
| 0.146 | 102 | HC3 | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 11.824 | 0.950 |
| 0.146 | 102 | HC3 | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 18.144 | 0.968 |
| 0.146 | 102 | HC3 | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 10.196 | 0.980 |
| 0.146 | 102 | HC3 | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 15.701 | 0.954 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | b_pos_C | -0.129 | -0.161 | -0.018 | 11.157 | 11.156 | 11.176 | 0.943 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | +1.161 | +0.300 | 16.070 | 16.028 | 16.694 | 0.953 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | b_neg_C | -0.129 | +0.007 | +0.018 | 8.034 | 8.034 | 9.151 | 0.955 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | -0.639 | +0.292 | 13.864 | 13.849 | 14.549 | 0.936 |
| 0.146 | 51 | NW5 calendario (prerreg.) | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 10.060 | 0.785 |
| 0.146 | 51 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 14.669 | 0.863 |
| 0.146 | 51 | NW5 calendario (prerreg.) | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 7.023 | 0.853 |
| 0.146 | 51 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 12.412 | 0.857 |
| 0.146 | 51 | NW5 filas | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 10.045 | 0.785 |
| 0.146 | 51 | NW5 filas | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 14.653 | 0.863 |
| 0.146 | 51 | NW5 filas | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 6.995 | 0.854 |
| 0.146 | 51 | NW5 filas | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 12.408 | 0.856 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 12.144 | 0.865 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 17.708 | 0.923 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 8.478 | 0.926 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 14.983 | 0.910 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 12.707 | 0.883 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 20.376 | 0.951 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 10.179 | 0.969 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 17.274 | 0.952 |
| 0.146 | 51 | HC3 | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 25.142 | 0.977 |
| 0.146 | 51 | HC3 | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 26.122 | 0.991 |
| 0.146 | 51 | HC3 | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 17.113 | 0.993 |
| 0.146 | 51 | HC3 | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 22.901 | 0.981 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | b_pos_C | -0.129 | -0.303 | — | 16.382 | 16.380 | 23.776 | 0.968 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | +0.386 | — | 19.016 | 19.012 | 22.964 | 0.975 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | b_neg_C | -0.129 | +0.393 | — | 10.093 | 10.085 | 14.577 | 0.985 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.066 | — | 16.560 | 16.559 | 20.180 | 0.969 |
| 0.0 | 102 | NW5 calendario (prerreg.) | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 8.666 | 0.861 |
| 0.0 | 102 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 13.590 | 0.893 |
| 0.0 | 102 | NW5 calendario (prerreg.) | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 6.743 | 0.879 |
| 0.0 | 102 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 11.151 | 0.895 |
| 0.0 | 102 | NW5 filas | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 8.704 | 0.865 |
| 0.0 | 102 | NW5 filas | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 13.597 | 0.894 |
| 0.0 | 102 | NW5 filas | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 6.728 | 0.879 |
| 0.0 | 102 | NW5 filas | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 11.172 | 0.895 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 9.437 | 0.889 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 14.800 | 0.922 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 7.344 | 0.908 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 12.144 | 0.917 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 9.872 | 0.899 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 16.012 | 0.945 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 8.222 | 0.938 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 13.179 | 0.936 |
| 0.0 | 102 | HC3 | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 11.861 | 0.951 |
| 0.0 | 102 | HC3 | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 18.110 | 0.971 |
| 0.0 | 102 | HC3 | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 10.310 | 0.972 |
| 0.0 | 102 | HC3 | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 15.697 | 0.961 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | b_pos_C | -0.000 | +0.104 | -0.020 | 11.414 | 11.413 | 11.196 | 0.935 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | -0.100 | +0.324 | 15.743 | 15.743 | 16.758 | 0.953 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | b_neg_C | -0.000 | +0.467 | +0.003 | 8.234 | 8.220 | 9.216 | 0.962 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.585 | +0.318 | 13.518 | 13.505 | 14.502 | 0.944 |
| 0.0 | 51 | NW5 calendario (prerreg.) | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 10.475 | 0.794 |
| 0.0 | 51 | NW5 calendario (prerreg.) | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 14.753 | 0.880 |
| 0.0 | 51 | NW5 calendario (prerreg.) | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 7.177 | 0.865 |
| 0.0 | 51 | NW5 calendario (prerreg.) | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 12.656 | 0.861 |
| 0.0 | 51 | NW5 filas | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 10.453 | 0.791 |
| 0.0 | 51 | NW5 filas | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 14.750 | 0.881 |
| 0.0 | 51 | NW5 filas | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 7.144 | 0.864 |
| 0.0 | 51 | NW5 filas | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 12.643 | 0.859 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 12.644 | 0.878 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 17.809 | 0.920 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 8.663 | 0.927 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 15.278 | 0.916 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 13.152 | 0.889 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 20.493 | 0.957 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 10.505 | 0.970 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 17.596 | 0.948 |
| 0.0 | 51 | HC3 | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 25.974 | 0.982 |
| 0.0 | 51 | HC3 | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 26.174 | 0.991 |
| 0.0 | 51 | HC3 | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 17.571 | 0.999 |
| 0.0 | 51 | HC3 | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 23.460 | 0.983 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | b_pos_C | -0.000 | +0.329 | — | 16.855 | 16.851 | 24.568 | 0.969 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | b_pos_U | -0.881 | -0.018 | — | 19.630 | 19.630 | 23.048 | 0.976 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | b_neg_C | -0.000 | -0.013 | — | 9.846 | 9.846 | 14.961 | 0.986 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | b_neg_U | -0.881 | +0.784 | — | 16.992 | 16.974 | 20.734 | 0.963 |

### 1b. Probabilidad de cada veredicto (reglas de la SPEC; Holm unilateral; δ = 0,146·|β̂_U|)

| m | T | ee | sentido | confirma | refuta_a | refuta_b | no_concluyente | confirma y (b) a la vez |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 102 | NW5 calendario (prerreg.) | subida | 0.085 | 0.082 | 0.032 | 0.801 | 0.000 |
| 1.0 | 102 | NW5 calendario (prerreg.) | bajada | 0.073 | 0.070 | 0.017 | 0.840 | 0.000 |
| 1.0 | 102 | NW5 filas | subida | 0.081 | 0.082 | 0.032 | 0.805 | 0.000 |
| 1.0 | 102 | NW5 filas | bajada | 0.074 | 0.068 | 0.020 | 0.838 | 0.000 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | subida | 0.062 | 0.063 | 0.036 | 0.839 | 0.000 |
| 1.0 | 102 | NW5 calendario ×N/(N−k) | bajada | 0.055 | 0.057 | 0.020 | 0.868 | 0.000 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | subida | 0.053 | 0.060 | 0.023 | 0.864 | 0.000 |
| 1.0 | 102 | HC1 (White ×N/(N−k)) | bajada | 0.043 | 0.039 | 0.025 | 0.893 | 0.000 |
| 1.0 | 102 | HC3 | subida | 0.024 | 0.034 | 0.013 | 0.929 | 0.000 |
| 1.0 | 102 | HC3 | bajada | 0.016 | 0.019 | 0.011 | 0.954 | 0.000 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | subida | 0.033 | 0.033 | 0.017 | 0.917 | 0.000 |
| 1.0 | 102 | NW5 calendario con residuos HC3 | bajada | 0.025 | 0.027 | 0.022 | 0.926 | 0.000 |
| 1.0 | 51 | NW5 calendario (prerreg.) | subida | 0.117 | 0.142 | 0.031 | 0.710 | 0.000 |
| 1.0 | 51 | NW5 calendario (prerreg.) | bajada | 0.091 | 0.080 | 0.056 | 0.773 | 0.000 |
| 1.0 | 51 | NW5 filas | subida | 0.116 | 0.143 | 0.030 | 0.711 | 0.000 |
| 1.0 | 51 | NW5 filas | bajada | 0.089 | 0.081 | 0.057 | 0.773 | 0.000 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | subida | 0.065 | 0.095 | 0.027 | 0.813 | 0.000 |
| 1.0 | 51 | NW5 calendario ×N/(N−k) | bajada | 0.053 | 0.047 | 0.032 | 0.868 | 0.000 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | subida | 0.068 | 0.092 | 0.019 | 0.821 | 0.000 |
| 1.0 | 51 | HC1 (White ×N/(N−k)) | bajada | 0.028 | 0.028 | 0.013 | 0.931 | 0.000 |
| 1.0 | 51 | HC3 | subida | 0.016 | 0.023 | 0.009 | 0.952 | 0.000 |
| 1.0 | 51 | HC3 | bajada | 0.007 | 0.006 | 0.004 | 0.983 | 0.000 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | subida | 0.020 | 0.034 | 0.011 | 0.935 | 0.000 |
| 1.0 | 51 | NW5 calendario con residuos HC3 | bajada | 0.011 | 0.015 | 0.004 | 0.970 | 0.000 |
| 0.5 | 102 | NW5 calendario (prerreg.) | subida | 0.077 | 0.096 | 0.035 | 0.792 | 0.000 |
| 0.5 | 102 | NW5 calendario (prerreg.) | bajada | 0.071 | 0.074 | 0.039 | 0.816 | 0.000 |
| 0.5 | 102 | NW5 filas | subida | 0.073 | 0.097 | 0.028 | 0.802 | 0.000 |
| 0.5 | 102 | NW5 filas | bajada | 0.069 | 0.076 | 0.039 | 0.816 | 0.000 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | subida | 0.059 | 0.072 | 0.037 | 0.832 | 0.000 |
| 0.5 | 102 | NW5 calendario ×N/(N−k) | bajada | 0.057 | 0.060 | 0.033 | 0.850 | 0.000 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | subida | 0.049 | 0.069 | 0.031 | 0.851 | 0.000 |
| 0.5 | 102 | HC1 (White ×N/(N−k)) | bajada | 0.050 | 0.053 | 0.017 | 0.880 | 0.000 |
| 0.5 | 102 | HC3 | subida | 0.023 | 0.043 | 0.016 | 0.918 | 0.000 |
| 0.5 | 102 | HC3 | bajada | 0.028 | 0.023 | 0.014 | 0.935 | 0.000 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | subida | 0.034 | 0.043 | 0.026 | 0.897 | 0.000 |
| 0.5 | 102 | NW5 calendario con residuos HC3 | bajada | 0.037 | 0.036 | 0.021 | 0.906 | 0.000 |
| 0.5 | 51 | NW5 calendario (prerreg.) | subida | 0.108 | 0.151 | 0.037 | 0.704 | 0.000 |
| 0.5 | 51 | NW5 calendario (prerreg.) | bajada | 0.086 | 0.098 | 0.052 | 0.764 | 0.000 |
| 0.5 | 51 | NW5 filas | subida | 0.109 | 0.152 | 0.037 | 0.702 | 0.000 |
| 0.5 | 51 | NW5 filas | bajada | 0.086 | 0.098 | 0.053 | 0.763 | 0.000 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | subida | 0.080 | 0.106 | 0.027 | 0.787 | 0.000 |
| 0.5 | 51 | NW5 calendario ×N/(N−k) | bajada | 0.050 | 0.068 | 0.033 | 0.849 | 0.000 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | subida | 0.069 | 0.104 | 0.024 | 0.803 | 0.000 |
| 0.5 | 51 | HC1 (White ×N/(N−k)) | bajada | 0.026 | 0.039 | 0.033 | 0.902 | 0.000 |
| 0.5 | 51 | HC3 | subida | 0.015 | 0.029 | 0.005 | 0.951 | 0.000 |
| 0.5 | 51 | HC3 | bajada | 0.005 | 0.009 | 0.006 | 0.980 | 0.000 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | subida | 0.024 | 0.035 | 0.015 | 0.926 | 0.000 |
| 0.5 | 51 | NW5 calendario con residuos HC3 | bajada | 0.007 | 0.016 | 0.016 | 0.961 | 0.000 |
| 0.146 | 102 | NW5 calendario (prerreg.) | subida | 0.062 | 0.102 | 0.044 | 0.792 | 0.000 |
| 0.146 | 102 | NW5 calendario (prerreg.) | bajada | 0.044 | 0.080 | 0.034 | 0.842 | 0.000 |
| 0.146 | 102 | NW5 filas | subida | 0.064 | 0.102 | 0.042 | 0.792 | 0.000 |
| 0.146 | 102 | NW5 filas | bajada | 0.045 | 0.081 | 0.035 | 0.839 | 0.000 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | subida | 0.055 | 0.084 | 0.043 | 0.818 | 0.000 |
| 0.146 | 102 | NW5 calendario ×N/(N−k) | bajada | 0.040 | 0.073 | 0.027 | 0.860 | 0.000 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | subida | 0.046 | 0.082 | 0.027 | 0.845 | 0.000 |
| 0.146 | 102 | HC1 (White ×N/(N−k)) | bajada | 0.032 | 0.058 | 0.021 | 0.889 | 0.000 |
| 0.146 | 102 | HC3 | subida | 0.027 | 0.052 | 0.018 | 0.903 | 0.000 |
| 0.146 | 102 | HC3 | bajada | 0.007 | 0.033 | 0.012 | 0.948 | 0.000 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | subida | 0.030 | 0.059 | 0.017 | 0.894 | 0.000 |
| 0.146 | 102 | NW5 calendario con residuos HC3 | bajada | 0.023 | 0.041 | 0.020 | 0.916 | 0.000 |
| 0.146 | 51 | NW5 calendario (prerreg.) | subida | 0.121 | 0.139 | 0.035 | 0.705 | 0.000 |
| 0.146 | 51 | NW5 calendario (prerreg.) | bajada | 0.070 | 0.124 | 0.056 | 0.750 | 0.000 |
| 0.146 | 51 | NW5 filas | subida | 0.120 | 0.141 | 0.033 | 0.706 | 0.000 |
| 0.146 | 51 | NW5 filas | bajada | 0.070 | 0.123 | 0.055 | 0.752 | 0.000 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | subida | 0.070 | 0.097 | 0.028 | 0.805 | 0.000 |
| 0.146 | 51 | NW5 calendario ×N/(N−k) | bajada | 0.037 | 0.073 | 0.046 | 0.844 | 0.000 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | subida | 0.061 | 0.092 | 0.027 | 0.820 | 0.000 |
| 0.146 | 51 | HC1 (White ×N/(N−k)) | bajada | 0.019 | 0.036 | 0.043 | 0.902 | 0.000 |
| 0.146 | 51 | HC3 | subida | 0.014 | 0.021 | 0.012 | 0.953 | 0.000 |
| 0.146 | 51 | HC3 | bajada | 0.002 | 0.007 | 0.002 | 0.989 | 0.000 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | subida | 0.016 | 0.030 | 0.017 | 0.937 | 0.000 |
| 0.146 | 51 | NW5 calendario con residuos HC3 | bajada | 0.005 | 0.015 | 0.014 | 0.966 | 0.000 |
| 0.0 | 102 | NW5 calendario (prerreg.) | subida | 0.073 | 0.102 | 0.050 | 0.775 | 0.000 |
| 0.0 | 102 | NW5 calendario (prerreg.) | bajada | 0.063 | 0.099 | 0.033 | 0.805 | 0.000 |
| 0.0 | 102 | NW5 filas | subida | 0.071 | 0.106 | 0.043 | 0.780 | 0.000 |
| 0.0 | 102 | NW5 filas | bajada | 0.063 | 0.101 | 0.033 | 0.803 | 0.000 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | subida | 0.057 | 0.085 | 0.037 | 0.821 | 0.000 |
| 0.0 | 102 | NW5 calendario ×N/(N−k) | bajada | 0.044 | 0.080 | 0.029 | 0.847 | 0.000 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | subida | 0.051 | 0.073 | 0.034 | 0.842 | 0.000 |
| 0.0 | 102 | HC1 (White ×N/(N−k)) | bajada | 0.032 | 0.059 | 0.025 | 0.884 | 0.000 |
| 0.0 | 102 | HC3 | subida | 0.025 | 0.049 | 0.022 | 0.904 | 0.000 |
| 0.0 | 102 | HC3 | bajada | 0.013 | 0.025 | 0.016 | 0.946 | 0.000 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | subida | 0.034 | 0.055 | 0.019 | 0.892 | 0.000 |
| 0.0 | 102 | NW5 calendario con residuos HC3 | bajada | 0.016 | 0.042 | 0.016 | 0.926 | 0.000 |
| 0.0 | 51 | NW5 calendario (prerreg.) | subida | 0.111 | 0.148 | 0.044 | 0.697 | 0.000 |
| 0.0 | 51 | NW5 calendario (prerreg.) | bajada | 0.062 | 0.099 | 0.053 | 0.786 | 0.000 |
| 0.0 | 51 | NW5 filas | subida | 0.112 | 0.148 | 0.046 | 0.694 | 0.000 |
| 0.0 | 51 | NW5 filas | bajada | 0.064 | 0.101 | 0.052 | 0.783 | 0.000 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | subida | 0.062 | 0.096 | 0.038 | 0.804 | 0.000 |
| 0.0 | 51 | NW5 calendario ×N/(N−k) | bajada | 0.032 | 0.073 | 0.031 | 0.864 | 0.000 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | subida | 0.053 | 0.098 | 0.037 | 0.812 | 0.000 |
| 0.0 | 51 | HC1 (White ×N/(N−k)) | bajada | 0.014 | 0.035 | 0.024 | 0.927 | 0.000 |
| 0.0 | 51 | HC3 | subida | 0.007 | 0.030 | 0.008 | 0.955 | 0.000 |
| 0.0 | 51 | HC3 | bajada | 0.001 | 0.003 | 0.005 | 0.991 | 0.000 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | subida | 0.011 | 0.031 | 0.014 | 0.944 | 0.000 |
| 0.0 | 51 | NW5 calendario con residuos HC3 | bajada | 0.008 | 0.015 | 0.017 | 0.960 | 0.000 |

## 2. Potencia de «confirma» (T = N) con β_U = β_C = c·β_ref

| c | β_C | ee | P(confirma) subida | P(confirma) bajada | P(refuta) subida | P(refuta) bajada |
|---|---|---|---|---|---|---|
| 1 | -0.88 | NW5 calendario (prerreg.) | 0.076 | 0.044 | 0.140 | 0.090 |
| 1 | -0.88 | NW5 calendario con residuos HC3 | 0.034 | 0.016 | 0.076 | 0.040 |
| 2 | -1.76 | NW5 calendario (prerreg.) | 0.116 | 0.084 | 0.130 | 0.072 |
| 2 | -1.76 | NW5 calendario con residuos HC3 | 0.058 | 0.038 | 0.076 | 0.032 |
| 5 | -4.40 | NW5 calendario (prerreg.) | 0.172 | 0.116 | 0.060 | 0.062 |
| 5 | -4.40 | NW5 calendario con residuos HC3 | 0.084 | 0.058 | 0.032 | 0.034 |
| 10 | -8.81 | NW5 calendario (prerreg.) | 0.238 | 0.256 | 0.036 | 0.016 |
| 10 | -8.81 | NW5 calendario con residuos HC3 | 0.122 | 0.144 | 0.018 | 0.006 |
| 15 | -13.21 | NW5 calendario (prerreg.) | 0.348 | 0.460 | 0.008 | 0.004 |
| 15 | -13.21 | NW5 calendario con residuos HC3 | 0.208 | 0.262 | 0.006 | 0.000 |
| 20 | -17.61 | NW5 calendario (prerreg.) | 0.566 | 0.646 | 0.004 | 0.000 |
| 20 | -17.61 | NW5 calendario con residuos HC3 | 0.394 | 0.392 | 0.004 | 0.000 |
| 30 | -26.42 | NW5 calendario (prerreg.) | 0.828 | 0.884 | 0.002 | 0.000 |
| 30 | -26.42 | NW5 calendario con residuos HC3 | 0.652 | 0.720 | 0.000 | 0.000 |
| 40 | -35.22 | NW5 calendario (prerreg.) | 0.934 | 0.994 | 0.000 | 0.000 |
| 40 | -35.22 | NW5 calendario con residuos HC3 | 0.840 | 0.930 | 0.000 | 0.000 |

## 3. Sensibilidad: ruido con σ_e condicionado a los 10 controles (×0.909), m = 1, T = N

| ee | sentido | confirma | refuta_a | refuta_b | no_concluyente | cobertura (b_pos_C, b_pos_U, b_neg_C, b_neg_U) |
|---|---|---|---|---|---|---|
| NW5 calendario (prerreg.) | pos | 0.086 | 0.087 | 0.025 | 0.802 | 0.862, 0.904, 0.905, 0.907 |
| NW5 calendario (prerreg.) | neg | 0.060 | 0.070 | 0.032 | 0.838 | 0.862, 0.904, 0.905, 0.907 |
| NW5 calendario con residuos HC3 | pos | 0.032 | 0.050 | 0.017 | 0.901 | 0.943, 0.959, 0.966, 0.953 |
| NW5 calendario con residuos HC3 | neg | 0.023 | 0.025 | 0.015 | 0.937 | 0.943, 0.959, 0.966, 0.953 |

## 4. Tabla estándar de `tools/mc.py` (IC con z normal; potencia bilateral), m = 1

```
[NW5 calendario (prerreg.)] **CoverageOutOfBand** con T
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.864 potencia=0.129 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.893 potencia=0.107 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.875 potencia=0.130 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.876 potencia=0.126 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.775 potencia=0.231 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.844 potencia=0.157 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.829 potencia=0.166 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.836 potencia=0.169 fallos=0
[NW5 filas] **CoverageOutOfBand** con T
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.863 potencia=0.132 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.891 potencia=0.109 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.874 potencia=0.128 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.877 potencia=0.123 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.776 potencia=0.231 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.842 potencia=0.156 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.830 potencia=0.169 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.834 potencia=0.170 fallos=0
[NW5 calendario ×N/(N−k)] **CoverageOutOfBand** con T
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.898 potencia=0.103 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.905 potencia=0.094 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.903 potencia=0.100 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.906 potencia=0.100 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.851 potencia=0.145 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.910 potencia=0.095 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.892 potencia=0.115 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.901 potencia=0.101 fallos=0
[HC1 (White ×N/(N−k))] **CoverageOutOfBand** con T
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.904 potencia=0.093 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.934 potencia=0.065 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.939 potencia=0.067 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.936 potencia=0.065 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.867 potencia=0.131 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.943 potencia=0.056 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.941 potencia=0.057 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.937 potencia=0.066 fallos=0
[HC3] dentro de [0,92; 0,98]
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.949 potencia=0.059 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.960 potencia=0.039 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.969 potencia=0.032 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.962 potencia=0.037 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.971 potencia=0.031 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.983 potencia=0.017 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.991 potencia=0.012 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.974 potencia=0.021 fallos=0
[NW5 calendario con residuos HC3] dentro de [0,92; 0,98]
   b_pos_C T=102   sesgo=-0.5186 RMSE=11.0736 cobertura=0.940 potencia=0.062 fallos=0
   b_pos_U T=102   sesgo=-0.3369 RMSE=15.9105 cobertura=0.938 potencia=0.066 fallos=0
   b_neg_C T=102   sesgo=+0.2155 RMSE=7.9800 cobertura=0.953 potencia=0.051 fallos=0
   b_neg_U T=102   sesgo=+0.3186 RMSE=13.8116 cobertura=0.951 potencia=0.054 fallos=0
   b_pos_C T=51    sesgo=-0.0428 RMSE=17.6378 cobertura=0.962 potencia=0.038 fallos=0
   b_pos_U T=51    sesgo=+2.0400 RMSE=19.9431 cobertura=0.960 potencia=0.041 fallos=0
   b_neg_C T=51    sesgo=+0.4951 RMSE=9.8803 cobertura=0.977 potencia=0.027 fallos=0
   b_neg_U T=51    sesgo=+0.2131 RMSE=17.5943 cobertura=0.960 potencia=0.039 fallos=0
```
