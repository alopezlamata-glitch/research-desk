# Cuentas de REDESIGN_POWER_2026-11-04 (generado por `exploration/redesign_power_calc.py`)

## 1. Cota de información con el DGP de F4 conocido (ee del impulso, en unidades de ȳ)

σ_e = 1.357, κ = 1.865, β_ref = -0.881 (F4). Con controles, multiplicar los ee por 0.909.

| término | ee oráculo | ee LP de F4 (NW5+HC3, desv. típ. de β̂) | pérdida LP/oráculo | potencia oráculo con β_ref (α=0,025) | c = MDE/|β_ref| oráculo |
|---|---|---|---|---|---|
| b_pos_C | 8.07 | 10.89 | 1.4 | 0.032 | 25.6 |
| b_pos_U | 12.67 | 15.80 | 1.2 | 0.029 | 40.3 |
| b_neg_C | 6.77 | 7.84 | 1.2 | 0.034 | 21.5 |
| b_neg_U | 10.67 | 13.58 | 1.3 | 0.030 | 33.9 |
| β_lin (s1_lin, sin celdas) | 3.31 | — (F4 no lo simuló) | — | 0.084 (α=0,05) | 9.3 |

R² poblacional del choque en ȳ con β_ref: 0.00070 (β_ref·sd(ε) = -0.067 pp frente a κσ_e = 2.53 pp).

## 2. Choques: varianza en unidades de fed funds (primera etapa sobre Δffr_t; no usa ninguna variable de resultado)

Ganancia = √(N·π²·var(ε)) relativa a la fila 1: factor en el estadístico t con el mismo ruido de la variable de resultado.

| choque | N | sd(ε) | π (Δffr_t) | F primera etapa | sd ffr-equiv. = π·sd(ε) | % de Σε² en los 4 mayores | ganancia t |
|---|---|---|---|---|---|---|---|
| BS-2023 orth (FOMC), muestra prerreg. | 102 | 0.076 | 1.76 | 4.2 | 0.134 | 29% | 1.0 |
| BS-2023 raw (FOMC), misma muestra | 102 | 0.107 | 3.22 | 66.7 | 0.345 | 30% | 2.6 |
| BS-2025 ME, 1994–2023 filtrada | 79 | 0.071 | 4.15 | 22.3 | 0.296 | 50% | 1.9 |
| JK MP_pm, 1990–2023 filtrada | 95 | 0.114 | 2.92 | 57.1 | 0.334 | 56% | 2.4 |
| Romer-Romer (Coibion), 1969–2007 | 156 | 0.586 | 0.95 | 15.3 | 0.557 | 53% | 5.1 |
| Romer-Romer, 1969–2007 sin 1979Q4–1982Q4 | 143 | 0.389 | 0.94 | 32.8 | 0.367 | 26% | 3.2 |
| Romer-Romer, 1988–2007 filtrada | 79 | 0.284 | 1.07 | 52.1 | 0.303 | 25% | 2.0 |
| Innovación de Δffr (4 retardos), 1969–2007 | 156 | 1.001 | 1 (def.) | — | 1.001 | 43% | 9.2 |
| Innovación de Δffr (4 retardos), 1988–2023 filtrada | 102 | 0.360 | 1 (def.) | — | 0.360 | 33% | 2.7 |

## 3. Panel con efectos fijos de tiempo: t_panel / t_agregado = √G · (σ_agg/σ_idio) · (Δβ·sd_X / |β|)

G = grupos con ruido idiosincrásico independiente; Δβ·sd_X/|β| = diferencia de respuesta entre grupos a 1 sd de X, relativa a la respuesta media.

| G | σ_idio/σ_agg | Δβ·sd_X/|β| | factor en t | c necesario (≈35/factor) |
|---|---|---|---|---|
| 2 | 1 | 0,5 | 0.71 | 49 |
| 2 | 2 | 0,5 | 0.35 | 99 |
| 2 | 4 | 0,5 | 0.18 | 198 |
| 8 | 1 | 0,5 | 1.41 | 25 |
| 8 | 2 | 0,5 | 0.71 | 49 |
| 8 | 4 | 0,5 | 0.35 | 99 |
| 40 | 1 | 0,5 | 3.16 | 11 |
| 40 | 2 | 0,5 | 1.58 | 22 |
| 40 | 4 | 0,5 | 0.79 | 44 |
| 200 | 1 | 0,5 | 7.07 | 5 |
| 200 | 2 | 0,5 | 3.54 | 10 |
| 200 | 4 | 0,5 | 1.77 | 20 |

## 4. Efecto mínimo detectable (potencia 0,8, α = 0,05 unilateral, oráculo lineal, choque BS orth, N = 102)

ȳ = media h=0..4 del cambio acumulado. Ruido = AR(2) univariante en las 102 filas, **sin choques**. MDE por 1 pp de fed funds = MDE por 1 pp de ε / π_ffr.

| variable | transformación | σ innov. | κ | MDE por 1 pp ε | MDE por 1 pp de fed funds |
|---|---|---|---|---|---|
| inversión no residencial (F4) | 100·Δlog | 1.357 | 1.86 | 8.2 | 4.7 |
| liquidez amplia NFC (Z.1) | 100·Δlog | 4.298 | 0.80 | 11.2 | 6.3 |
| préstamos bancarios NFC (Z.1) | 100·Δlog | 2.267 | 1.70 | 12.5 | 7.1 |
| deuda NFC (Z.1) | 100·Δlog | 0.869 | 1.72 | 4.8 | 2.7 |
| PIB real | 100·Δlog | 0.526 | 1.61 | 2.8 | 1.6 |
| EBP | Δ (pp) | 0.313 | 1.31 | 1.3 | 0.8 |

## 5. Diseños combinados: c = MDE/|β_ref| con el oráculo (potencia 0,8)

β_ref = −0,5 pp de ȳ por 1 pp de fed funds (F4: −2,5 % en el pico, TT pp. 11–12, rampa a h=10) × π del choque. Ruido: AR(2) univariante de 100·Δlog A008RA3Q086SBEA **en la muestra de cada fila**, sin choques. Estado: mitad de la muestra, independiente de ε (supuesto). La LP real pierde ×1,2–1,4 frente al oráculo (§1).

| diseño | N | σ_e | κ | c lineal (α=0,05) | c estado C, signos juntos (α=0,05) | c estado C por signo, subida (α=0,025) | potencia lineal con β_ref |
|---|---|---|---|---|---|---|---|
| BS-2023 orth, 1988–2023 (prerreg.) | 102 | 1.36 | 1.86 | 9.3 | 13.2 | 27.1 | 0.08 |
| Romer-Romer, 1969–2007 | 156 | 1.68 | 1.70 | 2.1 | 2.9 | 5.6 | 0.33 |
| Romer-Romer, 1969–2007 sin Volcker | 143 | 1.60 | 1.70 | 3.1 | 4.4 | 8.7 | 0.20 |
| Innovación recursiva de Δffr, 1969–2007 | 156 | 1.68 | 1.70 | 1.1 | 1.6 | 2.7 | 0.71 |

## 6. Ventana de horizontes del estadístico: señal/ruido relativa a ȳ (h = 0..4)

Señal: rampa de F4 hasta el pico en h = 10 (TT p. 11: mínimo a 2–3 años). Ruido: innovaciones futuras e_{t..t+h} propagadas por el AR(2) de F4 (φ1 = 0,465, φ2 = 0,271). No usa datos.

| ventana | señal media / pico | ratio señal/ruido relativo a h=0..4 |
|---|---|---|
| h = 0..4 | 0.20 | 1.00 |
| h = 0..8 | 0.40 | 1.24 |
| h = 4..12 | 0.77 | 1.34 |
| h = 8..12 | 0.94 | 1.34 |
| h = 0..12 | 0.58 | 1.33 |

## 7. Diseños de §5 con la ventana h = 4..12 (§6) y la pérdida de la LP (§1: ×1,2 a ×1,4)

c_LP = c_oráculo(§5) / 1.34 × pérdida. Potencia con β_ref = Φ((z_α + z_0,8)/c_LP − z_α). Aproximación: supone que la pérdida de §1 y la ganancia de §6 se componen.

| diseño | contraste | α | c_LP (pérdida 1,2–1,4) | potencia con β_ref |
|---|---|---|---|---|
| BS-2023 orth, 1988–2023 (prerreg.) | lineal (H0) | 0.05 | 8.4–9.7 | 0.08–0.09 |
| BS-2023 orth, 1988–2023 (prerreg.) | estado C, signos juntos | 0.05 | 11.8–13.8 | 0.07–0.08 |
| BS-2023 orth, 1988–2023 (prerreg.) | estado C, subida (Holm) | 0.025 | 24.3–28.3 | 0.03–0.03 |
| Romer-Romer, 1969–2007 | lineal (H0) | 0.05 | 1.8–2.1 | 0.31–0.39 |
| Romer-Romer, 1969–2007 | estado C, signos juntos | 0.05 | 2.6–3.0 | 0.21–0.25 |
| Romer-Romer, 1969–2007 | estado C, subida (Holm) | 0.025 | 5.0–5.8 | 0.07–0.08 |
| Romer-Romer, 1969–2007 sin Volcker | lineal (H0) | 0.05 | 2.8–3.2 | 0.19–0.23 |
| Romer-Romer, 1969–2007 sin Volcker | estado C, signos juntos | 0.05 | 3.9–4.6 | 0.14–0.16 |
| Romer-Romer, 1969–2007 sin Volcker | estado C, subida (Holm) | 0.025 | 7.8–9.1 | 0.05–0.05 |
| Innovación recursiva de Δffr, 1969–2007 | lineal (H0) | 0.05 | 1.0–1.2 | 0.67–0.79 |
| Innovación recursiva de Δffr, 1969–2007 | estado C, signos juntos | 0.05 | 1.4–1.7 | 0.44–0.53 |
| Innovación recursiva de Δffr, 1969–2007 | estado C, subida (Holm) | 0.025 | 2.4–2.8 | 0.16–0.21 |
