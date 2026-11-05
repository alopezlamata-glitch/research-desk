# p07 · Restricción de crédito y transmisión monetaria a la actividad industrial — SPEC

Estado: estimación hecha; pendiente de auditoría del Referee antes de pasar a Redacción.

## Pregunta
¿Reduce un endurecimiento monetario la producción industrial de EE. UU. más cuando el crédito corporativo está caro?

## Teoría
Motivación del signo de H1, no derivación de la especificación (la LP es una forma reducida). Una empresa con coste
del capital c = r(1 + m s) + δ elige k* = (αA / c)^{1/(1−α)}, donde s ≥ 0 es el diferencial de crédito y m > 0 la
sensibilidad de la prima. La prima es proporcional al tipo (acelerador financiero: la prima de financiación externa
escala con el coste de la deuda), y con ella ∂² log k* / ∂r ∂s < 0 (Proposición 1, `theory/check_sign.py`). Con una
prima aditiva (c = r + m s + δ) el signo se invierte: la elección de la prima es un supuesto, no un resultado.

## Datos
Mensuales, 1990-02 – 2019-12 (T = 359): empieza con la serie de choques y acaba antes de la COVID. Todo sale de
`data/raw/` (`code/data/download_series.py`, sha256 en `data/raw/MANIFEST.csv`) y se transforma con
`code/data/build_panel.py` (diccionario en `data/clean/DICTIONARY.md`).
- Resultado: producción industrial (FRED `INDPRO`), 100 × log.
- Choque: `MP_pm` de Jarociński-Karadi (actualización 2024-01), choque de política monetaria limpio de efecto
  información, que los autores agregan a mes sumando los anuncios FOMC (0 sin anuncio). Se divide por su desviación
  típica.
- Estado: diferencial Baa − Tesoro a 10 años (FRED `BAA` − `GS10`, medias mensuales), centrado en su media. Entra con un
  retardo: la media del mes t − 1 es anterior a cualquier anuncio del mes t.
- Controles: Δ log IPC (`CPIAUCSL`), Δ paro (`UNRATE`), el diferencial y el propio choque.

## Prerregistro
Especificación principal (LP con «lag augmentation», `code/analysis/lp.py`):

y_{t,h} = lip_{t+h} − lip_{t−1} = a_h + b_h shock_t + c_h shock_t · credit_{t−1} + Σ_{j=1..6} Γ_{h,j}' x_{t−j} + u_{t,h},
h ∈ {0, 6, 12, 18, 24}, con x = (dip, dcpi, dur, spread, shock) y errores robustos a heterocedasticidad con residuos HC3
(con los retardos del choque y de las demás variables no hace falta corregir el solape de y_{t,h}).

- **H1:** c_12 < 0 (a un año, la caída de la producción tras un endurecimiento es mayor con el crédito caro).
- **Regla de decisión:** contraste unilateral de c_12 al 5 %. Se confirma H1 si p < 0,05; si no, no se confirma.
  Los demás horizontes se informan como trayectoria, sin contraste.
- **Inferencia:** los intervalos se usan solo si el Monte Carlo (`code/mc/mc_lp.py`, skill `mc-validate`), con un DGP
  calibrado a estos datos, da una cobertura en [0,92; 0,98] con T = 359.
- Cualquier otra especificación se registra como exploratoria y se presenta como tal.

```prereg
lp_h0
lp_h6
lp_h12
lp_h18
lp_h24
```
prereg_commit: {PREREG_COMMIT}

## Desviaciones
Ninguna.
