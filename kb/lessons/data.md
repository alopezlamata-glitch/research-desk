# Lecciones — Datos

## 2026-11-04 · p01 · Errores de datos en las iteraciones previas
Estado: candidata
1. **Extrapolar con AR(1) hasta el final de la muestra y luego estimar sobre esos trimestres** (LDC_UK) mete datos
   inventados en la estimación. Regla: la muestra de estimación termina en el último dato observado; si una
   serie se extiende, la extensión se marca y se excluye.
2. **`ffill().bfill()` e `interpolate()` sobre todo el índice** rellenan huecos con datos futuros (look-ahead).
   Regla: nunca `bfill` en series que entran en una estimación; los NaN se documentan.
3. **Renombrar una serie como si fuera otra** (paro → "delinquency", −confianza empresarial → "VIX") esconde que
   el instrumento no es lo que dice el paper. Regla: el nombre de la variable describe la serie real; el papel
   (proxy de X) va en el diccionario de datos.
4. **Marcadores de posición que se quedan** (`UNRATE` como encuesta de confianza). Regla: los marcadores se
   escriben `TODO_SERIE_REAL` para que fallen y no se estimen en silencio.
5. **Claves de API en el código.** Regla: FRED se descarga de `fredgraph.csv` sin clave; si hiciera falta clave, se
   lee de `FRED_API_KEY`.

## 2026-11-04 · datalake · Descarga masiva de fuentes públicas
Estado: candidata
1. **Comprobar la identidad del archivo, no solo el HTTP 200.** La URL "JSTdatasetR6.xlsx" servía un `.dta`; el xlsx de
   Bauer-Swanson de la web era byte a byte el de dic-2023 (la "actualización ago-2025" estaba en un zip con otro formato).
   Regla: hash + cabecera (PK/D0CF/`<stata_dta>`) + rango de fechas antes de etiquetar un vintage.
2. **Wayback fija vintages** (`web.archive.org/web/<ts>id_/<url>`) pero devuelve 429 si se abusa: reintentos con espera.
3. **imf.org, cbo.gov y la API SDMX de la OCDE devuelven 403 a scripts**: usar espejos (DBnomics, JST, WDI) o marcar "manual".
4. **BIS bulk (`WS_*_csv_flat.zip`)**: las dimensiones van entre `ACTION` y `TIME_PERIOD`; no hay columna `KEY`. Un CSV
   puede pesar 500 MB descomprimido (CBPOL): leer por bloques.
5. **Un `series_id` duplicado delata dimensiones mal elegidas** (WDI: agregados sin ISO3). Validar unicidad al guardar.
6. **OneDrive bloquea el borrado de carpetas**: no regenerar borrando `raw/`; los fetch sobrescriben y el MANIFEST se reinicia aparte.
7. FRED `GDPPOT` llega a 2036 (proyección CBO): no estimar sobre ella.

## 2026-11-04 · p01 · Etapa 1 (EE. UU.)
Estado: candidata
1. **Dos vintages con el mismo nombre pueden ser series distintas.** El zip de Bauer-Swanson "ago-2025" no trae `MPS_ORTH`: es PC1 de MP1/MP2/ED2–ED4
   normalizado a la TIR a 1 año, sin ortogonalizar (ρ trimestral ≈ 0,66 con `MPS_ORTH`). Regla: antes de llamar "vintage" a un archivo, leer su script/README y
   correlacionar con el anterior en el solape; nombrar la variable por su construcción (`mps_bs23_orth`, `mps_bs25_me`), no por la fecha.
2. **Un NA de la fuente puede ser exclusión deliberada o hueco real.** 2001-09-17 (excluido por los autores) no debe anular el trimestre; mar–dic 2020 sí (los eventos
   existen pero `MPS_ORTH` no). Regla: leer la hoja `Description` y tratarlos por separado, con un test para cada caso.
3. **Agregar por trimestre con `sum()` convierte NaN en 0 sin avisar.** Regla: exigir que no haya NaN en el trimestre (o `min_count`) y llevar el nº de eventos (`n_ev_*`).
4. **Comprobar la cobertura de cada serie del datalake antes de prometerla**: `PNFIC1` (inversión no residencial real) tiene 79 observaciones desde 2007, no desde 1947. Regla: tabla de
   cobertura (`coverage.csv`) y test de primer/último dato; si la serie es corta, decirlo en el diccionario y ofrecer alternativas con otro nombre, no sustituirla en silencio.
5. **Z.1 no tiene vencimiento ni tipo de interés de la deuda**; las partes de deuda a tipo variable/corto plazo hay que buscarlas en E.2 o en micro-datos. Los CSV de Z.1 usan `ND` y fechas `1945:Q4`.
6. **FRED (`fredgraph.csv`) puede dar timeout**: construir desde el datalake con sha256 comprobado, no redescargar en el build.

## 2026-11-04 · p01 · F2b (inversión larga)
Estado: candidata
1. **Si una serie FRED sale corta, buscar el índice de cantidad del mismo concepto en NIPA** (`A008RA3Q086SBEA` frente a `PNFIC1`: 1947 frente a 2007). Regla: antes de declarar un hueco, probar la
   variante `A###RA3Q086SBEA` y validar con Δlog contra la serie corta en el solape (ρ ≈ 1); los niveles no son comparables (índice 2017=100 frente a USD encadenados).
2. **Un fetch parcial no debe rehacer todo el lago**: `fred.py` reescribe y re-hashea todas las series; para añadir una, llamar a `one()`/`save()` solo con ella y añadirla también a `SERIES` para futuras regeneraciones.

## 2026-11-04 · p01 · comprobaciones previas al prerregistro
Estado: candidata
1. **Antes de proponer una serie "mejor" (con discursos), leer la hoja `Description` y buscar la palabra "excludes"**: el xlsx de BS-2023 dice que las hojas FOMC y mensuales excluyen los discursos y que se publicarán más adelante. Regla: la comprobación de una variante de un dataset empieza por su documentación y por comparar sumas entre hojas (mensual = Σ evento), no por inferir del nombre de las columnas.
2. **Una hoja "Monthly" no es la suma de la hoja por evento si el objeto está ortogonalizado**: `Monthly MPS_ORTH` se reortogonaliza al nivel mensual. Regla: verificar la identidad de agregación antes de usar una hoja como sustituto.
3. **La encuesta E.2 no da el "% a tipo variable"** que se suponía en el diccionario: da volumen por intervalo de repreciación, cuota prime e intervalo medio, sobre préstamos *concedidos* (flujo). Regla: abrir la estructura de la fuente (`E2_struct.xml`, CodeLists) antes de prometer una variable con su nombre teórico.
4. **Los tramos de una descomposición publicada pueden no sumar el total** (E.2: 92,8–99,96 %). Regla: medir el residuo, acotarlo en un test y calcular la cuota sobre el volumen clasificado; no relajar el assert en silencio ni repartir el resto.
5. **El DDP de la Fed ofrece el paquete completo en un zip** (`Output.aspx?rel=<REL>&filetype=zip`, sin clave): evita construir URLs de series. Los TIME_PERIOD son fin de trimestre natural aunque la encuesta sea de mitad de trimestre.
6. **`print` de texto con `−`/`ε` falla en consola cp1252 de Windows**: escribir el fichero y no imprimir el contenido (o `PYTHONUTF8=1`).
7. **Los recuentos por celda se hacen con el código del estimador, no a mano**: el borrador estimaba ≈ 25 por celda estado×signo; el recuento exacto da 22–29 (liquidez) y 11–18 (DSR). Regla: reutilizar `sample_counts.py` para F4.
