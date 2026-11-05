# p07 · Restricción de crédito y transmisión monetaria a la inversión — SPEC

Estado: estimación hecha; pendiente de auditoría del Referee antes de pasar a Redacción.

## Pregunta
¿Reduce un endurecimiento monetario la inversión no residencial más cuando el crédito bancario está restringido?

## Teoría
Una empresa con coste del capital c = r(1 + m s) + δ (prima de financiación externa proporcional al tipo y al
endurecimiento del crédito s) elige k* = (αA / c)^{1/(1−α)}. La semielasticidad de la inversión al tipo es más
negativa cuanto más restringido está el crédito: ∂² log k* / ∂r ∂s < 0 (Proposición 1, `theory/check_sign.py`).

## Datos
Panel trimestral 1994T1–2023T4 (T = 120), `data/clean/panel.parquet` (`code/data/build_panel.py`, diccionario en
`data/clean/DICTIONARY.md`). Choque: sorpresa de alta frecuencia `ff4`, estandarizada. Estado: `sloos`
estandarizada (`credit`, > 0 = restringido), con un retardo.

## Prerregistro
Especificación principal (LP, `code/analysis/lp.py`):

y_{t,h} = loginv_{t+h} − loginv_{t−1} = a_h + b_h shock_t + d_h credit_{t−1} + c_h shock_t · credit_{t−1}
+ Γ_h' x_{t−1} + u_{t,h}, h = 0..4,

con x_{t−1} = (dinv, dgdp, infl, fci) retardados un trimestre y errores de Newey-West (Bartlett, h + 1 retardos).

- **H1:** c_1 < 0 (la caída acumulada de la inversión en dos trimestres es mayor con el crédito restringido).
- **Regla de decisión:** contraste unilateral de c_1 al 5 %. Se confirma H1 si p < 0,05; si no, no se confirma.
  h = 0, 2, 3, 4 se informan como trayectoria, sin contraste.
- **Inferencia:** los intervalos de NW se usan solo si el Monte Carlo (`code/mc/mc_lp.py`, skill `mc-validate`) da
  una cobertura en [0,92; 0,98] con T = 120.
- Cualquier otra especificación se registra como exploratoria y se presenta como tal.

```prereg
lp_h0
lp_h1
lp_h2
lp_h3
lp_h4
```
prereg_commit: {PREREG_COMMIT}

## Desviaciones
Ninguna.
