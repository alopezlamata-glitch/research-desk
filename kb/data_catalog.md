# Catálogo de datos (sin WRDS)

Estado: **probada** (descargada y validada por la desk de Datos) · **sin probar** · **rota/discontinuada**.
Los datos que existen y son gratuitos no hacen falta comprarlos; si algo requiere pago, se anota.

## Datalake (2026-11-04): fuentes **probadas**
Descargadas y validadas por Datos; detalle, rutas y avisos en [`datalake/CATALOG.md`](../datalake/CATALOG.md).
**Probadas:** FRED (151 series; 5 rotas: SHADOWRATE, GFDEBTNQ, SUBLPDHMSNQ, GSCPI, WILL5000PR) · EBP Gilchrist-Zakrajšek ·
SPF · NY Fed ACM · Fed Z.1 (2026-09-11) · Tesoro FiscalData · FDIC (anual) · Bauer-Swanson (xlsx = dic-2023; zip ago-2025
con otro formato) · USMPD · Jarociński-Karadi (Fed 2024-01, BCE 2023-10) · Ramey/Ramey-Zubairy · Romer-Romer ·
JST R6 (es `.dta`) · BIS (DSR, TC, CBPOL, SPP, CPP, credit gap, EER, XRU, LONG_CPI, GLI) · BoE millennium · BCE SDMX ·
OCDE confianza (vía DBnomics) · Banco Mundial · Baron-Verner-Xiong · Laeven-Valencia (vía `stevedata`) · Complex Crises.
**Manual / no accesibles por script (403):** FMI (WEO, HPDD, Laeven-Valencia original), Guajardo-Leigh-Pescatori, CBO,
OCDE SDMX directo, JK 2020 (AEA/openICPSR), Aruoba-Drechsel (sin URL).

## Macro y política — EE. UU.

| Fuente | Qué | Acceso | Estado | Notas |
|---|---|---|---|---|
| FRED | Casi todas las series de v22 | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>` (sin API key) | sin probar | Las series se revisan: guardar el vintage. ALFRED para tiempo real |
| FRED `TEDRATE` | TED spread | — | **discontinuada** (LIBOR, 2022) | Sustituto: spread SOFR/T-bill o el EBP de Gilchrist-Zakrajšek |
| Fed Board — Excess Bond Premium (Gilchrist-Zakrajšek) | Estrés financiero/crediticio, mensual desde 1973 | Web de la Fed (FEDS Notes, csv) | sin probar | Candidato a proxy exógeno de salud bancaria |
| Chicago Fed NFCI/ANFCI | Condiciones financieras | FRED | sin probar | v22 lo usa a la vez como proxy y como instrumento → solapamiento |

## Shocks identificados externamente (clave para p01)

| Fuente | Qué | Estado | Notas |
|---|---|---|---|
| Romer-Romer (extendidos, p. ej., Wieland-Yang) | Shocks monetarios narrativos, EE. UU. | sin probar | Verificar URL y cobertura |
| Bauer-Swanson (2023) | Shocks monetarios de alta frecuencia, EE. UU. | sin probar | Web de los autores |
| Ramey (2011), Ramey-Zubairy (2018) | Shocks fiscales: noticias de gasto militar, EE. UU. 1889– | sin probar | Web de Valerie Ramey |
| Romer-Romer (2010) | Shocks narrativos de impuestos, EE. UU. | sin probar | |
| Guajardo-Leigh-Pescatori (2014) | Consolidaciones fiscales narrativas, 17 países OCDE | sin probar | Panel: fiscal |
| Jordà-Schularick-Taylor (2020) | Instrumento "trilema" para shocks monetarios en panel histórico | sin probar | Panel: monetario |
| Jarociński-Karadi (2020) | Shocks monetarios BCE/Fed (alta frecuencia + bolsa) | sin probar | Zona euro |

## Usadas en iteraciones previas de p01 (ver `papers/p01-liquidity/exploration/INVENTORY.md`)

| Fuente | Qué | Estado | Notas |
|---|---|---|---|
| DBnomics (`pip install dbnomics`) | ONS, OCDE (MEI/KEI), BIS para Reino Unido y otros países, sin clave | usada en LDC_UK | Los códigos de serie cambian (MEI → DP_LIVE): `fetch_multi` con alternativas |
| Shock de Jarociński-Karadi (2020) | Shock monetario puro (alta frecuencia + restricciones de signo) | usada en `modelshock` | Verificar la versión y la URL |
| Monetary policy surprises (xlsx + chart1 csv) | Sorpresas de política monetaria | usada en z01 (oct-2026) | Identificar la fuente exacta (¿Bauer-Swanson, SF Fed?) en la tarea 0.3 |

## Paneles internacionales

| Fuente | Qué | Estado | Notas |
|---|---|---|---|
| JST Macrohistory Database | 18 países, 1870–2020, anual: PIB, deuda, crédito, tipos, crisis | sin probar | macrohistory.net, xlsx/dta. La principal vía para tener más datos |
| Baron-Verner-Xiong (2021) | Crisis bancarias y retornos de acciones bancarias, 46 países | sin probar | Proxy de salud bancaria en panel |
| BIS statistics | Crédito, deuda por sector, tipos de política, trimestral | sin probar | API SDMX |
| IMF WEO / Historical Public Debt Database | Deuda pública larga | sin probar | |
| OECD | Confianza del consumidor y de las empresas | sin probar | Proxy de confianza en panel |
| ECB Data Portal | Zona euro: tipos, balance, crédito | sin probar | API SDMX |

## Microestructura / liquidez de mercado (para futuros papers)

| Fuente | Qué | Estado |
|---|---|---|
| LOBSTER (muestras) | Libro de órdenes NASDAQ | sin probar |
| data.binance.vision, Bybit, Hyperliquid | Libro de órdenes y trades de cripto | sin probar |
| Open Source Asset Pricing (Chen-Zimmermann) | Señales de sección cruzada, incluidas de liquidez | sin probar |
| SEC MIDAS | Métricas de estructura de mercado | sin probar |

## Paquetes de replicación y series de shocks localizados por Literatura (2026-11-04, p01)

Todos **sin probar**. Licencia: "no consultada" = no se abrió la página del repositorio.

| Fuente | Qué contiene | URL | Estado | Notas |
|---|---|---|---|---|
| Bauer-Swanson (FRBSF) | Sorpresas FOMC brutas y ortogonalizadas (xlsx ≈295 kb) | https://www.frbsf.org/?p=133218 | sin probar | Última actualización 25-ago-2025; los borradores usan la de dic-2023 (publicada oct-2024). Fijar versión. Licencia no consultada |
| USMPD (Acosta et al., FRBSF WP 2025-30) | Base de eventos FOMC (declaraciones, ruedas de prensa, actas): futuros, OIS, Treasuries/TIPS, bolsa, USD; código R | sffed.us/usmpd (según la página del FRBSF: https://www.frbsf.org/research-and-insights/data-and-indicators/us-monetary-policy-event-study-database/) | sin probar | Alternativa/ampliación de la serie anterior |
| Jarociński-Karadi (2020) | Paquete AEA del artículo (datos + apéndice) | Vía DOI 10.1257/mac.20180090 (AEA data archive) | sin probar | No se abrió; no se confirmó openICPSR |
| Jarociński (GitHub) | Shocks de política y de información del BCE actualizados (por reunión del Consejo); MATLAB | https://github.com/marekjarocinski/jkshocks_update_ecb_202310 | sin probar | Requiere `Dataset_EA-MPD.xlsx` del BCE. Licencia no consultada |
| Abadi-Brunnermeier-Koby (2023) | Datos y código de "The Reversal Interest Rate" | https://www.openicpsr.org/openicpsr/project/188611/version/V1/view | sin probar | |
| Auclert (2019) | Datos y código (Italia/EE. UU.) | https://www.openicpsr.org/openicpsr/project/113120/version/V1/view | sin probar | También ICPSR 38144 |
| Ottonello-Winberry (2020) | Ficheros suplementarios: empírico y modelo | https://www.econometricsociety.org/publications/econometrica/2020/11/01/financial-heterogeneity-and-investment-channel-monetary-policy | sin probar | Sección "Supplemental Material" |
| Bernanke-Blanchard (2023) | Datos y código | https://www.openicpsr.org/openicpsr/project/195423/version/V1/view | sin probar | Solo si se usa |
| Jeenas (BSE WP 1409) | No localizado paquete de replicación | — | no encontrado | Pedir al autor |
| Perez-Orive et al. (FEDS 2026-021) | No localizado | — | no encontrado | No se abrió el PDF; mirar apéndice de datos |
| Lakdawala-Moreland | No localizado (ni para su paper de Economics Letters 2023) | — | no encontrado | Mirar sitio de los autores |

## Repositorios de replicación
openICPSR (AEA), Zenodo, Harvard Dataverse: buscar ahí el paquete de replicación del paper de
referencia **antes** de construir los datos desde cero.
