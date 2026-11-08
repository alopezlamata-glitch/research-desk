# F13 · Comprobaciones para `s1r_*` (generado por `code/mc/f13_checks.py`, semilla 20261107, 1000 réplicas)

V3s con `aum`, ee NW5+HC3, T = N, DGP y semillas de F9 (`f9_power.py`, §2–4). Regla (b) retirada: `refuta_b` cuenta como no concluyente. β_ref = −2,5 × m_W × π(h = 0), π de ffr_t − ffr_(t−1) sobre ε_t en la muestra completa.

## 1. ¿Cambian β_ref y la potencia frente a β_ref al promediar el choque en vez de sumarlo?

| agregación | sd(ε) completa | π(h = 0) (ee) | β_ref (pp de ȳ por pp de ε) | β_ref × sd(ε) | ruido | P(confirma) V3s, c = 1 | potencia H0 | potencia H1 (completa) |
|---|---|---|---|---|---|---|---|---|
| suma | 0.6001 | 0.949 (0.248) | -1.820 | -1.092 | homo | 0.037 | 0.176 | 0.118 |
| suma | 0.6001 | 0.949 (0.248) | -1.820 | -1.092 | het_eps | 0.059 | 0.146 | 0.121 |
| media3 | 0.2000 | 2.848 (0.745) | -5.459 | -1.092 | homo | 0.037 | 0.176 | 0.118 |
| media3 | 0.2000 | 2.848 (0.745) | -5.459 | -1.092 | het_eps | 0.059 | 0.146 | 0.121 |
| media_nz | 0.2818 | 1.797 (0.491) | -3.445 | -0.971 | homo | 0.032 | 0.133 | 0.099 |
| media_nz | 0.2818 | 1.797 (0.491) | -3.445 | -0.971 | het_eps | 0.034 | 0.091 | 0.071 |

**Media de 3 meses frente a suma, en las mismas réplicas** (misma semilla): ε_media3 = ε_suma/3 en todos los trimestres, así que π, β_ref, β̂ y ee se multiplican por 3 y los estadísticos t no cambian.

| ruido | máx. \|ε_suma/3 − ε_media3\| | π_media3/π_suma | β_ref,media3/β_ref,suma | máx. \|Δt\| (b_lin, b_C, b_U; completa y sin Volcker) | máx. \|β̂_media3/β̂_suma − 3\| | veredictos V3s idénticos |
|---|---|---|---|---|---|---|
| homo | 0.0e+00 | 3.000000 | 3.000000 | 1.2e-12 | 5.5e-10 | sí |
| het_eps | 0.0e+00 | 3.000000 | 3.000000 | 1.3e-12 | 2.7e-08 | sí |

El MDE en pp de ȳ por pp de fed funds (c × 2,5 × m_W = c × 1.917) no depende de la agregación; el MDE en pp de ȳ por pp de ε sí (×3 con la media), así que el prerregistro tiene que fijar la unidad de ε.

## 2. V3s con `aum` (choque sumado, como F9): P(desenlace) frente a c, H1 cierta (m = 1) y rival (m = 0: β_C = 0, β_U = c·β_ref)

c = 4, 5,5 y 6 son celdas nuevas; las demás repiten las de F9 con su semilla. β_ref = -1.820. MDE en pp de ȳ por pp de ε = c × 1.820; por pp de fed funds = c × 1.917.

| ruido | m | c | MDE pp/pp ε | MDE pp/pp ffr | h0_falla | confirma | refuta_a | no_concluyente | potencia H0 | potencia H1 (completa) |
|---|---|---|---|---|---|---|---|---|---|---|
| homo | 1 | 1 | 1.82 | 1.92 | 0.824 | 0.037 | 0.000 | 0.139 | 0.176 | 0.118 |
| homo | 1 | 2 | 3.64 | 3.83 | 0.506 | 0.171 | 0.000 | 0.323 | 0.494 | 0.381 |
| homo | 1 | 3 | 5.46 | 5.75 | 0.183 | 0.364 | 0.000 | 0.453 | 0.817 | 0.678 |
| homo | 1 | 4 | 7.28 | 7.67 | 0.045 | 0.590 | 0.000 | 0.365 | 0.955 | 0.861 |
| homo | 1 | 5 | 9.10 | 9.58 | 0.003 | 0.745 | 0.000 | 0.252 | 0.997 | 0.960 |
| homo | 1 | 5.5 | 10.01 | 10.54 | 0.003 | 0.797 | 0.000 | 0.200 | 0.997 | 0.982 |
| homo | 1 | 6 | 10.92 | 11.50 | 0.000 | 0.871 | 0.000 | 0.129 | 1.000 | 0.994 |
| homo | 1 | 7 | 12.74 | 13.42 | 0.000 | 0.946 | 0.000 | 0.054 | 1.000 | 0.994 |
| homo | 0 | 1 | 1.82 | 1.92 | 0.925 | 0.014 | 0.000 | 0.061 | 0.075 | 0.044 |
| homo | 0 | 2 | 3.64 | 3.83 | 0.849 | 0.025 | 0.000 | 0.126 | 0.151 | 0.071 |
| homo | 0 | 3 | 5.46 | 5.75 | 0.742 | 0.031 | 0.000 | 0.227 | 0.258 | 0.101 |
| homo | 0 | 4 | 7.28 | 7.67 | 0.615 | 0.032 | 0.000 | 0.353 | 0.385 | 0.122 |
| homo | 0 | 5 | 9.10 | 9.58 | 0.517 | 0.035 | 0.000 | 0.448 | 0.483 | 0.141 |
| homo | 0 | 5.5 | 10.01 | 10.54 | 0.468 | 0.020 | 0.000 | 0.512 | 0.532 | 0.112 |
| homo | 0 | 6 | 10.92 | 11.50 | 0.451 | 0.017 | 0.000 | 0.532 | 0.549 | 0.093 |
| homo | 0 | 7 | 12.74 | 13.42 | 0.350 | 0.014 | 0.000 | 0.636 | 0.650 | 0.114 |
| het_eps | 1 | 1 | 1.82 | 1.92 | 0.854 | 0.059 | 0.000 | 0.087 | 0.146 | 0.121 |
| het_eps | 1 | 2 | 3.64 | 3.83 | 0.563 | 0.189 | 0.000 | 0.248 | 0.437 | 0.337 |
| het_eps | 1 | 3 | 5.46 | 5.75 | 0.282 | 0.361 | 0.000 | 0.357 | 0.718 | 0.564 |
| het_eps | 1 | 4 | 7.28 | 7.67 | 0.101 | 0.600 | 0.000 | 0.299 | 0.899 | 0.782 |
| het_eps | 1 | 5 | 9.10 | 9.58 | 0.033 | 0.778 | 0.000 | 0.189 | 0.967 | 0.902 |
| het_eps | 1 | 5.5 | 10.01 | 10.54 | 0.015 | 0.840 | 0.000 | 0.145 | 0.985 | 0.937 |
| het_eps | 1 | 6 | 10.92 | 11.50 | 0.008 | 0.882 | 0.000 | 0.110 | 0.992 | 0.964 |
| het_eps | 1 | 7 | 12.74 | 13.42 | 0.002 | 0.933 | 0.000 | 0.065 | 0.998 | 0.994 |
| het_eps | 0 | 1 | 1.82 | 1.92 | 0.945 | 0.014 | 0.000 | 0.041 | 0.055 | 0.037 |
| het_eps | 0 | 2 | 3.64 | 3.83 | 0.853 | 0.033 | 0.000 | 0.114 | 0.147 | 0.073 |
| het_eps | 0 | 3 | 5.46 | 5.75 | 0.760 | 0.030 | 0.000 | 0.210 | 0.240 | 0.089 |
| het_eps | 0 | 4 | 7.28 | 7.67 | 0.679 | 0.021 | 0.000 | 0.300 | 0.321 | 0.086 |
| het_eps | 0 | 5 | 9.10 | 9.58 | 0.584 | 0.027 | 0.000 | 0.389 | 0.416 | 0.109 |
| het_eps | 0 | 5.5 | 10.01 | 10.54 | 0.562 | 0.029 | 0.000 | 0.409 | 0.438 | 0.105 |
| het_eps | 0 | 6 | 10.92 | 11.50 | 0.484 | 0.015 | 0.000 | 0.501 | 0.516 | 0.106 |
| het_eps | 0 | 7 | 12.74 | 13.42 | 0.414 | 0.010 | 0.000 | 0.576 | 0.586 | 0.098 |

### 2b. c con P(confirma) = 0,8 (interpolación lineal en la rejilla de arriba)

| ruido | c con 0,8 | MDE pp de ȳ por pp de ε | MDE pp de ȳ por pp de fed funds | máx. P(confirma) del rival, c ≤ 5 |
|---|---|---|---|---|
| homo | 5.5 | 10.01 | 10.54 | 0.035 |
| het_eps | 5.2 | 9.46 | 9.97 | 0.033 |
