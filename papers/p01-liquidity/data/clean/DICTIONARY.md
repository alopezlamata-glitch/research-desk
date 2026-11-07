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

### ¿Hay una serie de BS con discursos del presidente de la Fed? (comprobado 2026-11-04) — **No; `mps_bs23_orth_sp` no se crea**
Hojas del xlsx BS-2023: `Description`, `FOMC (update 2023)` (361×23), `Monthly (update 2023)` (431×10), `FOMC (original)` (323×23), `Monthly (original)` (566×15).
Columnas de las hojas FOMC: `Date, Time, Unscheduled, FF1, FF2, ED1–ED4, SP500, SP500 emini, TNOTE02/05/10, TBOND, MPS, MPS_ORTH, NFP_SURP, NFP_12M, SP500_3M, SLOPE_3M, BCOM_3M, TR_SKEW`;
las mensuales, `Year, Month, MPS, MPS_ORTH` y las 6 noticias (la original añade IP, desempleo, CRB, CPI, EBP y el 2 años).
- La hoja `Description` lo dice expresamente: la hoja FOMC "contains data only for the FOMC announcements, and **excludes** data for the Fed Chair speeches and other types of
  monetary policy announcements […]. These other data will be released at some point in the future". Las hojas mensuales son "using FOMC announcements only".
- Comprobado en los datos: la suma mensual de `MPS` de la hoja FOMC reproduce `Monthly MPS` (error máx. 1,4e-5), es decir, sin discursos. `Monthly MPS_ORTH` **no** es la suma de
  `MPS_ORTH` por evento (se reortogonaliza al nivel mensual con las noticias del primer evento del mes): otro objeto, también solo FOMC, que no se añade.
- El zip BS-2025 (`mps.csv`, `mps_minutes.csv`, `y1.csv`) y `USMPD.xlsx` (hojas Statements, Press Conferences, Monetary Events, Minutes) tampoco traen discursos; BS-2025 incluye ruedas de prensa, no discursos.
- Los discursos del presidente están en Swanson-Jayawickrema (2021, citado en BS-2023 como fuente de 880 discursos 1988–2019) y no están publicados con el xlsx; **no se ha localizado una versión pública**. Alternativa: pedirla a los autores del
  dataset (michael.bauer@sf.frb.org según la hoja `Description`). Sin ella, la recomendación de §5 del borrador (serie con discursos como principal) no se puede ejecutar y queda `mps_bs23_orth` (solo FOMC, con la F baja que BS señalan).

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
construido un sustituto con otro nombre.

### Exposición a la repreciación `g` (E.2, Survey of Terms of Business Lending; probada 2026-11-04)
Fuente: Fed DDP `rel=E2` (zip, publicación 2017-08-02; `datalake/raw/fed_board/e2_stbl_ddp.zip`), todos los bancos comerciales, todos los riesgos.
**E.2 no publica "% a tipo variable"**: publica el volumen por intervalo de repreciación, la cuota basada en el prime y el intervalo medio ponderado.
| Variable | Definición | Unidad | Cobertura | Fuente / transformación |
|---|---|---|---|---|
| `stbl_short_share` | % del volumen de préstamos C&I **con intervalo de vencimiento/repreciación ≤ 30 días** (cero + diario + 2–30 días) | % | 1997Q2–2017Q2 (81, sin huecos) | tramos `BCABLCCEV{Z,O,S}` / suma de los 5 tramos. Los 5 tramos suman 92,8–99,96 % del total publicado (mediana 99,6 %): se divide por el **volumen clasificado**, sin repartir el resto |
| `stbl_prime_pct` | % del valor de los préstamos con tipo basado en el **prime** (tipo variable de hecho) | % | 2003Q2–2017Q2 (57) | `BCABLCCEQA_N.Q` |
| `stbl_interval_days` | Intervalo medio ponderado de vencimiento/repreciación, todos los préstamos | días | 2003Q2–2017Q2 (57) | `BCABLCCEIT_N.Q`; muy ruidosa (47–430) |

**Límites que condicionan su uso como `g`:**
1. Mide los préstamos **concedidos en la semana de la encuesta** (primera semana completa de feb/may/ago/nov), un flujo de bancos, no el stock de deuda de las empresas
   ni sus bonos. El trimestre natural es el de la fecha de publicación (feb→T1…). El "intervalo ≤ 30 días" incluye préstamos a tipo fijo a muy corto plazo (que no reprecian *dentro* de la vida del préstamo): es un indicador de repreciación rápida, no de tipo variable.
2. **Termina en 2017Q2** (la encuesta se discontinuó; E.2 pasó a no publicarse) y empieza en 1997Q2. Con la muestra principal de `SAMPLE_COUNTS.md` solo se solapan **53 de 102** trimestres (45 de 58 con DSR); los años ZLB 2009–2015 quedan fuera por construcción.
3. Es una serie agregada de series temporales: varía en el tiempo, no entre empresas. Sirve como estado/interacción en E3/E4 con esa cobertura, no como medida de la exposición neta de las empresas que invierten (supuesto A-g).
4. Correlación con `ffr` en 1997Q2–2017Q2: `stbl_short_share` 0,06, `stbl_prime_pct` 0,42 (la cuota prime cae con el tipo oficial bajo).
Otros candidatos descartados sin descargar: Call Reports (vencimiento residual, trimestral desde 1997 pero requiere construcción con micro-datos), Compustat (no disponible). Las partidas Z.1 (activos/pasivos) usan valoración de mercado en bonos y acciones; la liquidez de una "sociedad no financiera"
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

## Etapa 1 rediseñada (F7): `stage1r_us.parquet`
Generado por `code/data/build_stage1r_us.py` (tests en `test_stage1r_us.py`). Una fila por trimestre, **1960Q1–2008Q4** (196 filas); no
rellena huecos. No reemplaza a `stage1_us.parquet` (la etapa 1 original sigue intacta). Recuentos por estado en `SAMPLE_COUNTS_S1R.md`.

| Variable | Definición | Unidad | Cobertura | Fuente / transformación |
|---|---|---|---|---|
| `rr_shock` | **Romer-Romer** (extensión Coibion, reestimada por Wieland, `resid_full`), **suma de los 3 meses** del trimestre | pp de fed funds | 1969Q1–2007Q4 (156); 1969Q1 = marzo de 1969 | `Ramey_HOM_monetary.zip` → `Monetarydat.xlsx`, hoja `Wieland` (= `Monthly` `RRSHOCK`, comprobado) |
| `rr_months_nonzero` | Meses del trimestre con choque ≠ 0 | cuenta (0–3) | ídem | ídem |
| `liq_broad_debt`, `s`, `s_lag` | Como en la etapa 1, con Z.1 desde 1945 (sin el recorte START); `s_lag` = `s_{t−1}` | ratio / log | 1960Q1– (la media usa 12 trimestres previos de Z.1) | Z.1 2026-09-11 |
| `ffr` | Fed funds, media trimestral (3 meses completos) | % | 1960Q1– | FRED `FEDFUNDS` |
| `mps_bs23_orth` | Bauer-Swanson ortogonalizado (réplica), como en `stage1_us` | pp | 1988Q1–2008Q4 | `stage1_us.parquet` |
| `in_rr_sample` | `True` en 1969Q1–**2005Q2** | bool | 146 trimestres | último t con t + 12 < 2008Q3 |

**Regla de agregación del choque:** suma de los choques mensuales del trimestre (la fuente construye el mensual sumando las reuniones del
mes y no indica otra regla). Todos los trimestres tienen sus 3 meses; ene–feb de 1969 son 0 en la fuente (la primera reunión de RR es marzo de 1969).
Muestra de la réplica con `mps_bs23_orth`: 1988Q1–2005Q2 (70 trimestres). Aviso: 11 de los 13 trimestres de Volcker caen en el estado «restringido».
