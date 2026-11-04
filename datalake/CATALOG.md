# Catálogo del datalake

Descarga: 2026-11-04 (`uv run python datalake/fetch/update_all.py`, log en `datalake/update_all.log`). Tamaño de `raw/`: ≈160 MB.
Estado: **OK** · **ROTO** · **manual** (existe, pero el script no puede bajarlo sin navegador/login). Rutas relativas a `datalake/raw/`.
Formato largo `date, series_id, value` en `.parquet` + original (`csv/<ID>.csv` en FRED). Relevancia: L1/L2 = líneas TFG1/TFG2 de p01, panel, general.

## Nivel 1 — EE. UU.

| Fuente | Series | Frec. | Cobertura | Unidades | Ruta | Rel. | Estado |
|---|---|---|---|---|---|---|---|
| FRED `actividad_precios` | GDPC1, GDP, GDPPOT (CBO), GDPDEF, PCECC96, PCE, PCEPI(LFE), CPIAUCSL, CPILFESL, GPDIC1, GPDI, PNFIC1, PRFIC1, UNRATE, PAYEMS, CIVPART, INDPRO, NROU, CLF16OV, HOUST, RSAFS, DSPIC96, PSAVERT… (25) | T/M | desde 1919–1959; GDPPOT llega a 2036 (**proyección CBO**, excluir de estimación) | unidades de FRED (ver `csv/<ID>.csv`; meta en FRED) | `fred/actividad_precios.parquet` | L1 L2 | OK |
| FRED `politica` | FEDFUNDS, DFF, EFFR, IORB, IOER, SOFR, DFEDTARU/L, DGS3MO…DGS30, TB3MS, GS1, GS10, T10Y2Y, T10Y3M, DFII10, T10YIE, T5YIFR, **WALCL, WRESBAL, RRPONTSYD/TTLD**, WSHOSHO, WSHOMCB, M1SL, M2SL, BOGMBASE, TOTRESNS, CURRCIR (36) | D/S/M | 1917–2026-11 (según serie; SOFR desde 2018, IORB 2021) | % o mill. USD | `fred/politica.parquet` | L1 L2 | OK |
| FRED `deuda` | GFDEBTN, GFDEGDQ188S, FYGFDPUN, FDHBPIN/FDHBFRBN (en manos del público/Fed), **FYOINT, A091RC1Q027SBEA** (intereses federales), BCNSDODNS, CMDEBT, HHMSDODNS, **TDSP, FODSP, CDSP, MDSP** (debt service ratios hogares), DODFS, TOTALSL, REVOLSL, MORTGAGE30US/15US, FYONET, FGEXPND, FGRECPT… (32) | T/M/A | A091RC1Q027SBEA 1947–2026Q3; TDSP desde 2005 (hogares) | mill. USD, % | `fred/deuda.parquet` | L1 L2 | OK |
| FRED `banca` | TOTBKCR, LOANS, BUSLOANS, REALLN, CONSUMER, DPSACBW027SBOG, TLAACBW027SBOG (H.8), **SLOOS** DRTSCILM/CIS/SP/CLCC, DRSDCILM, morosidad DRALACBN/DRBLACBS/DRCCLACBS/DRSFRMACBS, cargas CORALACBN/CORBLACBS/CORCCACBS, USNIM, EQTA… (27) | T/S/M | 1947–2026; SLOOS desde 1990 | % o mill. USD | `fred/banca.parquet` | L1 L2 | OK |
| FRED `condiciones_confianza` | NFCI, ANFCI, STLFSI4, BAA, AAA, BAA10Y, BAMLH0A0HYM2, BAMLC0A0CM, VIXCLS, UMCSENT, MICH, EXPINF1YR/10YR, USEPUINDXD/M, CFNAI, USSLIND, DTWEXBGS, SP500, NASDAQCOM, DCOILWTICO, USREC/USRECM… (29) | D/S/M | desde 1854 (USRECM) / 1986 (VIX) / 1978 (Michigan) | índices, % | `fred/condiciones_confianza.parquet` | L1 L2 | OK |
| FRED — **ROTAS** | SHADOWRATE, GFDEBTNQ, SUBLPDHMSNQ, GSCPI, WILL5000PR: 404 en `fredgraph.csv` (retiradas/licencia/código erróneo). TEDRATE sí baja pero está **discontinuada** (2022) | | | | | | **ROTO** |
| Fed Board — Excess Bond Premium (GZ) | gz_spread, ebp, est_prob | M | 1973-01 – 2026-09 | pp | `fed_board/ebp_csv.csv` | L1 | OK |
| Fed E.2 — Survey of Terms of Business Lending (STBL) | 2.425 series SDMX (tipo efectivo, volumen por intervalo de repreciación, % prime, intervalo medio, por riesgo/tamaño/banco); préstamos C&I **concedidos** en la semana de la encuesta | T | 1997Q2 – 2017Q2 (prime e intervalo desde 2003Q2) | %, mill. USD, días | `fed_board/e2_stbl_ddp.zip` (`E2_data.xml`) | L1 | OK — **encuesta discontinuada en 2017**; no da "% a tipo variable" |
| SPF (Philly Fed) | medianas de nivel, todas las variables | T | 1968– | var. | `spf/medianlevel.xlsx` | L1 | OK (sin parsear a largo) |
| NY Fed — ACM term premia | rendimientos y primas de plazo | M/D | 1961– | % | `nyfed/acm_term_premia_allmonth.xls` | L1 | OK |
| Fed Z.1 (Financial Accounts) | todo el release **2026-09-11** (CSV zip) | T | 1946– | mill. USD | `fed_z1/z1_csv_files_20260911.zip` | L1 L2 | OK (vintage fijado) |
| Tesoro FiscalData | `debt_to_penny` (1993–), `avg_interest_rates` (2001–, por tipo de título), `interest_expense` (2010–) | D/M | ver ruta | USD, % | `treasury/*.parquet` + `.json` | L1 L2 | OK |
| FDIC | resumen por estado y año (activos, capital, depósitos, préstamos, resultado, ingresos/gastos por intereses…); agregado EE. UU. = suma de estados | A | 1934–2025 | miles USD | `fdic/summary_state_year.json`, `fdic/us_aggregate_annual.parquet` | L1 | OK — **agregado anual; el QBP trimestral no está** |

## Shocks identificados

| Fuente | Contenido | Ruta | Estado / notas |
|---|---|---|---|
| Bauer-Swanson (FRBSF) | **Vintage dic-2023**: `FOMC (update 2023)` 1988-02-04…2023-12-13 + `Monthly (update 2023)` y las hojas originales (hasta 2019/2020). El xlsx de la web es **idéntico byte a byte** a la copia de Wayback (2025-01-21) | `shocks/bauer_swanson/monetary-policy-surprises-data_vintage2023-12.xlsx` (+ `_wayback20250121.xlsx` de control) | OK |
| Bauer-Swanson **ago-2025** | zip con `mps.csv` (columnas `Date, STMT, PC, ME`; 280 eventos, **1994-02-04 – 2026-10-28**), `mps_minutes.csv`, `y1.csv`, `mps.R`, `gss.R` | `shocks/bauer_swanson/monetary-policy-surprises_vintage2025-08.zip` | OK. **Aviso:** el xlsx *no* se actualizó y su formato es otro: el zip trae sorpresas por declaración/rueda de prensa/actas (estructura tipo USMPD/GSS), no `MPS_ORTH`. **Decisión para los autores:** si p01 necesita "el vintage ago-2025" de la serie ortogonalizada, hay que leer `mps.R` y la web del FRBSF antes de asumir que es la misma serie |
| USMPD (FRBSF) | base de eventos FOMC + series de los gráficos | `shocks/usmpd/` | OK |
| Jarociński-Karadi, Fed (actualización ene-2024) | `shocks_fed_jk_m.csv` (1990–2024, mensual), `_t.csv` (por evento), `fomc_surprises_jk.csv` | `shocks/jarocinski_karadi/fed_202401/` | OK |
| Jarociński-Karadi, BCE (actualización oct-2023) | `shocks_ecb_mpd_me_{d,m}.csv`, `Dataset_EA-MPD.xlsx` | `shocks/jarocinski_karadi/ecb_202310/` | OK |
| JK (2020) paquete AEA original | — | — | **manual** (openICPSR/AEA exigen login); la actualización de GitHub lo sustituye |
| Ramey / Ramey-Zubairy | `Ramey_Zubairy_replication_codes.zip` (noticias militares 1889–2015), `Ramey_Govt_Public_Data.xls` (2011), `govdat3908.csv` (SPF gasto), `Ramey_HOM_{monetary,govtspending,tax}.zip` (Handbook of Macro), `ORZ-Data-and-Programs.zip` | `narrative/ramey/` | OK |
| Romer-Romer | monetarios (`monetary_shocks_appendix.xls`, `intended_rate_data.xls`, `FOMC_data.xls`), impuestos (`tax_DataSet.zip`: bases RATS del artículo de impuestos de 2010), transferencias (AEJ:Macro 2014), crisis financieras | `narrative/romer_romer/` | OK |
| Aruoba-Drechsel | no localizado URL pública | — | **manual** |

## Nivel 2 — panel internacional

| Fuente | Contenido | Frec. | Cobertura | Ruta | Estado |
|---|---|---|---|---|---|
| JST Macrohistory R6 | 18 países, 59 variables (debtgdp, stir, tloans, crisisJST…) | A | 1870–2020 | `jst/JSTdatasetR6.dta` (**es Stata**, la URL decía xlsx) | OK |
| BIS DSR | debt service ratios por sector | T | 1999Q1–2026Q1 | `bis/WS_DSR.parquet` (+ zip) | OK |
| BIS TC | crédito total por sector | T | 1940Q2–2026Q1 | `bis/WS_TC.parquet` | OK |
| BIS CBPOL | tipos oficiales | D/M | 1945– | `bis/WS_CBPOL.parquet` | OK |
| BIS SPP, CPP | precios de vivienda / inmuebles comerciales | T | 1927Q1– | `bis/WS_SPP`, `WS_CPP` | OK |
| BIS credit gap, EER, XRU, LONG_CPI, GLI | brecha de crédito, tipos de cambio efectivos/bilaterales, IPC largo (1661–), liquidez global | varias | ver parquet | `bis/WS_*.parquet` | OK |
| BoE millennium dataset | "A millennium of macroeconomic data" (27 MB) | A/T/M | desde 1086 (hojas históricas) | `boe/millennium_macro_data.xlsx` | OK |
| BCE (SDMX) | MRO, DFR, MLF, HICP, M3, activos Eurosistema, tipos MIR (empresas/hipotecas), curva AAA 2a/10a, PIB, CISS, deuda/PIB | varias | 1999– | `ecb/ecb_series.parquet` + `ecb/csv/` | OK; `unemployment` **ROTO** (clave STS 404) |
| OCDE confianza (CLI/BCI/CCI) | 113 series | M | 1950–2026-05 | `oecd/cli_confidence.parquet` | OK vía espejo DBnomics (la API SDMX de la OCDE da 403 a scripts) |
| Banco Mundial WDI | deuda gob. central/PIB, crédito privado/PIB, intereses/ingresos, tipo real, crecimiento | A | 1960– | `worldbank/wdi_selected.parquet` | OK |
| Baron-Verner-Xiong (QJE 2021) | replication kit (zip) + README | — | — | `crises/baron_verner_xiong/` | OK (Dataverse DOI 10.7910/DVN/ECC9GE; contenido sin inspeccionar) |
| Laeven-Valencia SBCD | tabla de crisis 1970–2017 | — | — | `crises/laeven_valencia/SBCD_stevedata.rda` | OK **vía paquete R `stevedata`** (copia de terceros; el original IMF devuelve 403). Contrastar con el IMF WP 18/206 |
| Complex Crises Database | crisis bancarias/cambiarias/deuda, 70 años | — | — | `crises/complex_crises/` | OK |
| Guajardo-Leigh-Pescatori | — | — | — | — | **manual**: imf.org devuelve 403 a scripts; no hay réplica pública localizada |
| FMI (WEO, HPDD, GDD), CBO históricos | — | — | — | — | **manual**: imf.org y cbo.gov devuelven 403 a scripts. Sustitutos ya en el lago: JST (deuda), BIS TC, WDI, FRED GFDEGDQ188S |

## Lo que falta de la lista del encargo
- Vencimiento medio de la deuda del Tesoro y peso de ARM/préstamos C&I a tipo variable: no hay serie FRED/API sencilla; `treasury/avg_interest_rates` da tipos por título pero no vencimiento. Candidatos: Treasury Bulletin (PDF), MSPD `mspd_table_3_market`, SLOOS/Call Reports.
- QBP trimestral de la FDIC (la API `summary` es anual).
- Nivel 3 hecho con criterio propio: Z.1, ACM, CISS, BIS credit gap/GLI/EER/LONG_CPI, Complex Crises, EPU, CFNAI, GDPNow no incluido.
