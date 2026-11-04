# Diccionario de `stage1_us.parquet` (p01, etapa 1, EE. UU.)

Generado por `code/data/build_stage1_us.py` a partir de `data/raw/stage1_us/` (copiado del datalake por
`download_stage1_us.py`; filas en `data/raw/MANIFEST.csv`). Una fila por trimestre natural, **1985Q1–2026Q4** (168 filas);
`quarter` ("1988Q1") y `date` (último día del trimestre). **No se rellena ningún hueco**: donde no hay dato, hay NaN.
Cobertura exacta por variable en `coverage.csv`; verificada por `code/data/test_stage1_us.py`; figuras en `output/figures/data_<variable>.png`.

## Reglas de agregación
- **Shocks (evento → trimestre): suma** de todos los eventos FOMC del trimestre (convención de Bauer-Swanson para el
  mensual). Un trimestre con algún evento NaN no tiene suma conocida → NaN (solo 2020, ver abajo). Todos los trimestres
  del soporte tienen ≥ 1 evento (`n_ev_*`).
- **Mensual → trimestral (media simple)** solo si están los 3 meses; si no, NaN. **Diario (DGS2) → trimestral**: media de los días
  del trimestre y último dato del trimestre; el trimestre en curso (2026Q4) queda NaN.
- **Trimestrales**: se usan tal cual (FRED fecha por inicio de trimestre; BIS "YYYY-Qn"; Z.1 "YYYY:Qn").
- Vintage de las fuentes que se revisan: Z.1 release **2026-09-11**; FRED descargado **2026-11-04** (sin ALFRED: los datos
  son los de la última revisión, no de tiempo real).

## Shocks de política monetaria
| Variable | Definición | Unidad | Cobertura | Fuente / transformación |
|---|---|---|---|---|
| `mps_bs23_orth` | **BS-2023, MPS_ORTH**: 1.er componente principal de ΔED1–ED4 (ventana de 30 min), escalado a ED4=1 y **ortogonalizado** a 6 variables macro-financieras | pp | 1988Q1–2023Q4; **NaN 2020Q1–Q4** (140 válidos) | xlsx dic-2023, hoja `FOMC (update 2023)`; suma por trimestre |
| `mps_bs23_raw` | Igual sin ortogonalizar (MPS) | pp | 1988Q1–2023Q4 (144, sin huecos) | ídem |
| `n_ev_bs23`, `n_ev_bs23_unsched` | Nº de eventos y de ellos no programados | cuenta | 1988Q1–2023Q4 | ídem |
| `mps_bs25_me` | **BS-2025, ME** (monetary events: declaración + rueda de prensa) | pp, normalizado a Δ1 año GSW = 1 | 1994Q1–2026Q4 | `mps.csv` del zip ago-2025; suma por trimestre |
| `mps_bs25_stmt` | Idem solo declaración (STMT) | pp | 1994Q1–2026Q4 | ídem |
| `mps_bs25_pc` | Idem solo rueda de prensa (PC) | pp | 2011Q2–2026Q4; NaN sin rueda de prensa | ídem; NaN si no hubo ninguna en el trimestre |
| `n_ev_bs25` | Nº de eventos | cuenta | 1994Q1–2026Q4 | ídem |
| `bs25_quarter_partial` | `True` en 2026Q4: solo incluye la reunión del 28-oct-2026 (falta la de diciembre) | bool | | **excluir 2026Q4 de estimaciones con BS-2025** |

### Las dos vintages de Bauer-Swanson (para que los autores elijan)
**No son dos versiones de la misma serie.** *BS-2023* (publicada oct-2024; datos hasta dic-2023) es la serie de Bauer y
Swanson (2023, NBER Macro Annual): primer componente de ED1–ED4 (futuros Eurodollar y, desde 2023, SOFR) en ventana de 30 min, escalado a ED4=1;
`MPS_ORTH` además la ortogonaliza a seis noticias macro-financieras (NFP, crecimiento del empleo, S&P 500, pendiente, materias primas, asimetría del 10 años). *BS-2025* es el paquete `monetary-policy-surprises.zip` del FRBSF (el archivo `.R` lleva fecha 09-dic-2025 y los datos llegan a
oct-2026, aunque la web lo etiqueta "ago-2025"): sorpresas construidas con la metodología de Acosta et al. (2025, FRBSF WP 2025-30)
sobre la base USMPD: PC1 *estandarizado* de MP1, MP2, ED2–ED4, **escalado para que mueva el rendimiento a 1 año (GSW) uno a uno**, calculado por separado
para declaración (STMT), rueda de prensa (PC) y evento monetario completo (ME). **No está ortogonalizado a noticias macro**; no existe `MPS_ORTH` en esta vintage. El xlsx de la web del FRBSF
sigue siendo el de dic-2023 (idéntico byte a byte, sha256 70860662…); el etiquetado `vintage2025-08.xlsx` del datalake es esa misma copia y **no se usa**.
Diferencias: cobertura 1988–2023 vs 1994–2026 (la nueva añade 2024–2026 y pierde 1988–93); construcción (ED1–ED4 vs MP1/MP2/ED2–ED4, escala ED4 vs y1, con/sin ortogonalización); tratamiento de 2020 (BS-2023 deja `MPS_ORTH` en NA mar–dic 2020, BS-2025 no); fecha de eventos (2010-05-09 y 2019-10-04 solo en BS-2025; 2019-10-11 solo en BS-2023, mismo trimestre); BS-2025 incluye 2001-09-17, BS-2023 lo excluye.
Correlación en el solape (255 eventos comunes): ME–MPS 0,88, ME–MPS_ORTH 0,81. Trimestral 1994Q1–2023Q4 (sin los NaN): ME–MPS_ORTH **0,66**, ME–MPS 0,88, STMT–MPS_ORTH 0,72; desviación típica 0,064 (ME), 0,068 (MPS_ORTH), 0,093 (MPS).
**Implicación:** `mps_bs23_orth` y `mps_bs25_me` difieren bastante (ρ≈0,66): la elección no es neutra. Para cubrir 2020 con BS-2023 solo vale `mps_bs23_raw`.
La decisión de vintage es de los autores; el panel contiene ambas con identificadores distintos.

## Estado de liquidez y servicio de la deuda
| Variable | Definición | Unidad | Cobertura | Fuente / transformación |
|---|---|---|---|---|
| `dsr_nfc` | Debt service ratio, **empresas no financieras** (EE. UU.) | % de la renta | 1999Q1–2026Q1 (109) | BIS WS_DSR, serie `Q|US|N`; sin transformar |
| `dsr_priv_nf` | DSR, **sector privado no financiero** | % | 1999Q1–2026Q1 (109) | BIS `Q|US|P` |
| `nfc_assets`, `nfc_fin_assets` | Activos totales / financieros, empresas no financieras (sociedades) | mill. USD, fin de periodo, sin AE | 1985Q1–2026Q2 | Z.1 S.11.1.b: FL102000005, FL104090005 |
| `nfc_checkable`, `nfc_timesav`, `nfc_mmf` | Depósitos a la vista y efectivo; depósitos a plazo y ahorro; participaciones en fondos monetarios | idem | idem | FL103020005, FL103030003, FL103034000 |
| `nfc_treasury`, `nfc_agency`, `nfc_muni`, `nfc_cp_asset`, `nfc_repo` | Deuda del Tesoro, agencias/GSE, municipal, papel comercial (activo), repos (activo) | idem | idem | LM103061103, LM103061703, LM103062003, FL103069100, FL102051003 |
| `nfc_debt_sec`, `nfc_loans_liab` | Pasivo: valores de deuda; préstamos totales | idem | idem | FL104122005, FL104135005 |
| `nfc_cp_liab`, `nfc_bonds`, `nfc_bank_loans` | Pasivo: papel comercial, bonos corporativos, préstamos de entidades de depósito n.e.c. | idem | idem | FL103169100, FL103163005, FL103168005 |
| `nfc_liq_narrow` | **Liquidez estrecha** = vista + plazo/ahorro + fondos monetarios | idem | idem | suma; NaN si falta un componente |
| `nfc_liq_broad` | **Liquidez amplia** = estrecha + Tesoro + agencias + municipal + papel comercial + repos | idem | idem | suma; NaN si falta un componente |
| `nfc_debt` | Deuda de mercado de crédito = valores de deuda + préstamos (pasivos) | idem | idem | suma |
| `liq_narrow_assets`, `liq_broad_assets` | Liquidez / activos totales | ratio | 1985Q1–2026Q2 | cociente |
| `liq_narrow_debt`, `liq_broad_debt` | Liquidez / deuda | ratio | idem | cociente |

**No existe en Z.1**: la parte de la deuda a tipo variable o a corto plazo (Z.1 no desglosa por vencimiento ni tipo de interés). No se ha
construido un sustituto con otro nombre. Candidatos fuera del lago (no probados): Survey of Terms of Business Lending (E.2, % de préstamos C&I a tipo
variable), Call Reports/SLOOS, datos de empresa (Compustat, no disponible). Las partidas Z.1 (activos/pasivos) usan valoración de mercado en bonos y acciones; la liquidez de una "sociedad no financiera"
agregada incluye a las grandes empresas, que concentran los saldos.

## Controles y resultados
| Variable | Definición | Unidad | Cobertura | Fuente / transformación |
|---|---|---|---|---|
| `inv_nonres_q` | **Inversión fija privada no residencial real (variable principal de inversión)** | índice de cantidad, 2017=100 | **1985Q1–2026Q3 (167)** en el panel; la serie FRED va de 1947Q1 | FRED `A008RA3Q086SBEA` (BEA, índice de cantidad); sin rellenar huecos |
| `inv_nonres_real` | Inversión fija privada no residencial real, en niveles | mil mill. USD 2017 encadenados, tasa anual | 2007Q1–2026Q3 (79) | FRED `PNFIC1`. **Solo comprobación** desde 2007: la tasa de crecimiento (Δlog) correlaciona 0,99999998 con `inv_nonres_q` |
| `inv_priv_real` | Inversión privada interior bruta real (incluye vivienda y existencias) | idem | 1985Q1–2026Q3 | FRED `GPDIC1`; **alternativa de muestra larga, otro concepto** |
| `inv_nfc_nominal` | Formación bruta de capital fijo, sociedades no financieras | mill. USD, flujo anualizado, AE | 1985Q1–2026Q2 | Z.1 S.11.1.t FA105019005 |
| `inv_nfc_real` | `inv_nfc_nominal / gdp_deflator × 100` | mill. USD 2017 | idem | **derivada**: se deflacta con el deflactor del PIB, no con uno de inversión |
| `gdp_real`, `gdp_deflator` | PIB real (miles mill. USD 2017) y deflactor (2017=100) | | 1985Q1–2026Q3 | FRED `GDPC1`, `GDPDEF` |
| `ffr` | Fed funds efectivo, media trimestral de la media mensual | % | 1985Q1–2026Q3 | FRED `FEDFUNDS` |
| `y2_mean`, `y2_eoq` | Rendimiento Tesoro 2 años (CMT), media del trimestre y último dato | % | 1985Q1–2026Q3 | FRED `DGS2` (diario; sin días festivos) |
| `sloos_ci_large`, `sloos_ci_small` | SLOOS: % neto de bancos que **endurecen** estándares C&I (grandes y medianas / pequeñas) | % neto | 1990Q2–2026Q4 | FRED `DRTSCILM`, `DRTSCIS` (trimestre de la encuesta) |
| `sloos_ci_demand` | SLOOS: % neto de demanda de préstamos C&I más fuerte (grandes y medianas) | % neto | 1991Q4–2026Q4 | FRED `DRSDCILM` |
| `ebp`, `gz_spread` | Excess bond premium y spread GZ, media trimestral | pp | 1985Q1–2026Q3 | Fed Board (Gilchrist-Zakrajšek), mensual → media de 3 meses |

## Huecos y avisos
1. La inversión no residencial principal es `inv_nonres_q` (1985Q1+ en el panel, 1947+ en FRED). `inv_nonres_real` (PNFIC1) solo existe desde 2007Q1: úsese como comprobación, no como resultado. Otros conceptos: `inv_nfc_real` (sociedades, deflactor del PIB) e `inv_priv_real` (incluye vivienda y existencias).
2. `mps_bs23_orth` NaN en 2020Q1–Q4 (decisión de los autores de BS-2023, no de la desk).
3. Z.1 termina en 2026Q2 y DSR en 2026Q1: las ecuaciones con estado de liquidez o DSR acaban ahí; los shocks BS-2025 llegan a 2026Q3 completos.
4. 2026Q4 incompleto en shocks BS-2025 (`bs25_quarter_partial`); SLOOS 2026Q4 ya publicada pero PIB, tipos y EBP no.
5. Datos en **última revisión** (Z.1 2026-09-11, FRED 2026-11-04): no son de tiempo real; Z.1 y NIPA se revisan.
6. SLOOS se publica con retraso dentro del trimestre de la encuesta; el dato de un trimestre usa información posterior al FOMC de ese trimestre: alinear en la estimación (tarea de Econometría).
