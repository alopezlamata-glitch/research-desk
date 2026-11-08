# Estimaciones de `s1r_*` y `r1r_*` (generado por `code/analysis/01_s1r_estimate.py`)

`aum`, NW(5)+HC3, t de N − k g.l.; p unilateral de β < 0. Pp de ȳ (h = 4..12) por pp de choque (ε sumado en el trimestre).

| id | término | β̂ | ee | g.l. | p (β < 0) | IC al 95 % |
|---|---|---|---|---|---|---|
| s1r_lin | b_lin | -1.655 | 1.786 | 114 | 0.178 | [-5.193, 1.883] |
| s1r_liq | b_C | -2.874 | 1.653 | 112 | 0.042 | [-6.149, 0.400] |
| s1r_liq | b_U | 0.841 | 4.341 | 112 | 0.577 | [-7.760, 9.441] |
| s1r_liq_nov | b_C | -4.981 | 2.814 | 99 | 0.040 | [-10.565, 0.603] |
| s1r_liq_nov | b_U | 1.024 | 4.687 | 99 | 0.586 | [-8.276, 10.324] |
| r1r_from1971q3 | b_C | -2.035 | 1.974 | 102 | 0.152 | [-5.950, 1.879] |
| r1r_from1971q3 | b_U | 0.059 | 4.097 | 102 | 0.506 | [-8.067, 8.184] |
| r1r_state_q25 | b_C | -6.085 | 3.045 | 112 | 0.024 | [-12.118, -0.052] |
| r1r_state_q25 | b_U | -0.840 | 2.488 | 112 | 0.368 | [-5.769, 4.089] |
| r1r_state_logistic | b_C | -4.576 | 2.196 | 112 | 0.020 | [-8.928, -0.225] |
| r1r_state_logistic | b_U | 1.890 | 5.289 | 112 | 0.639 | [-8.589, 12.369] |
| r1r_lags4 | b_C | -2.219 | 1.582 | 104 | 0.082 | [-5.356, 0.917] |
| r1r_lags4 | b_U | 3.034 | 4.028 | 104 | 0.773 | [-4.953, 11.021] |

**Veredicto V3s** (`s1r_lp.decide`): `h0_falla`. Se presenta con el IC y el MDE de la SPEC; `s1r_liq_nov` lleva la salvedad del Ljung-Box sin Volcker (SPEC, «Diagnósticos de los choques»).
