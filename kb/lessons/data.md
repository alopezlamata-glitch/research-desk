# Lecciones — Datos

## 2026-11-04 · p01 · Errores de datos en las iteraciones previas
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
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

## 2026-11-04 · p01 · Errores de datos en las iteraciones previas — puntos retirados
Estado: retirada
5. **Claves de API en el código.** Regla: FRED se descarga de `fredgraph.csv` sin clave; si hiciera falta clave, se
   lee de `FRED_API_KEY`.
   *Motivo:* ya lo cubren CLAUDE.md e integrity.py

## 2026-11-04 · datalake · Descarga masiva de fuentes públicas
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Comprobar la identidad del archivo, no solo el HTTP 200.** La URL "JSTdatasetR6.xlsx" servía un `.dta`; el xlsx de
   Bauer-Swanson de la web era byte a byte el de dic-2023 (la "actualización ago-2025" estaba en un zip con otro formato).
   Regla: hash + cabecera (PK/D0CF/`<stata_dta>`) + rango de fechas antes de etiquetar un vintage.
2. **Un `series_id` duplicado delata dimensiones mal elegidas** (WDI: agregados sin ISO3). Validar unicidad al guardar.

## 2026-11-04 · datalake · Descarga masiva de fuentes públicas — puntos retirados
Estado: retirada
2. **Wayback fija vintages** (`web.archive.org/web/<ts>id_/<url>`) pero devuelve 429 si se abusa: reintentos con espera.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
3. **imf.org, cbo.gov y la API SDMX de la OCDE devuelven 403 a scripts**: usar espejos (DBnomics, JST, WDI) o marcar "manual".
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
4. **BIS bulk (`WS_*_csv_flat.zip`)**: las dimensiones van entre `ACTION` y `TIME_PERIOD`; no hay columna `KEY`. Un CSV
   puede pesar 500 MB descomprimido (CBPOL): leer por bloques.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
6. **OneDrive bloquea el borrado de carpetas**: no regenerar borrando `raw/`; los fetch sobrescriben y el MANIFEST se reinicia aparte.
   *Motivo:* detalle de entorno o de la sesión, no una regla de método
7. FRED `GDPPOT` llega a 2036 (proyección CBO): no estimar sobre ella.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)

## 2026-11-04 · p01 · Etapa 1 (EE. UU.)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Dos vintages con el mismo nombre pueden ser series distintas.** El zip de Bauer-Swanson "ago-2025" no trae `MPS_ORTH`: es PC1 de MP1/MP2/ED2–ED4
   normalizado a la TIR a 1 año, sin ortogonalizar (ρ trimestral ≈ 0,66 con `MPS_ORTH`). Regla: antes de llamar "vintage" a un archivo, leer su script/README y
   correlacionar con el anterior en el solape; nombrar la variable por su construcción (`mps_bs23_orth`, `mps_bs25_me`), no por la fecha.
2. **Un NA de la fuente puede ser exclusión deliberada o hueco real.** 2001-09-17 (excluido por los autores) no debe anular el trimestre; mar–dic 2020 sí (los eventos
   existen pero `MPS_ORTH` no). Regla: leer la hoja `Description` y tratarlos por separado, con un test para cada caso.
3. **Agregar por trimestre con `sum()` convierte NaN en 0 sin avisar.** Regla: exigir que no haya NaN en el trimestre (o `min_count`) y llevar el nº de eventos (`n_ev_*`).
4. **Comprobar la cobertura de cada serie del datalake antes de prometerla**: `PNFIC1` (inversión no residencial real) tiene 79 observaciones desde 2007, no desde 1947. Regla: tabla de
   cobertura (`coverage.csv`) y test de primer/último dato; si la serie es corta, decirlo en el diccionario y ofrecer alternativas con otro nombre, no sustituirla en silencio.

## 2026-11-04 · p01 · Etapa 1 (EE. UU.) — puntos retirados
Estado: retirada
5. **Z.1 no tiene vencimiento ni tipo de interés de la deuda**; las partes de deuda a tipo variable/corto plazo hay que buscarlas en E.2 o en micro-datos. Los CSV de Z.1 usan `ND` y fechas `1945:Q4`.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
6. **FRED (`fredgraph.csv`) puede dar timeout**: construir desde el datalake con sha256 comprobado, no redescargar en el build.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)

## 2026-11-04 · p01 · F2b (inversión larga)
Estado: retirada
1. **Si una serie FRED sale corta, buscar el índice de cantidad del mismo concepto en NIPA** (`A008RA3Q086SBEA` frente a `PNFIC1`: 1947 frente a 2007). Regla: antes de declarar un hueco, probar la
   variante `A###RA3Q086SBEA` y validar con Δlog contra la serie corta en el solape (ρ ≈ 1); los niveles no son comparables (índice 2017=100 frente a USD encadenados).
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
2. **Un fetch parcial no debe rehacer todo el lago**: `fred.py` reescribe y re-hashea todas las series; para añadir una, llamar a `one()`/`save()` solo con ella y añadirla también a `SERIES` para futuras regeneraciones.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)

## 2026-11-04 · p01 · comprobaciones previas al prerregistro
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Antes de proponer una serie "mejor" (con discursos), leer la hoja `Description` y buscar la palabra "excludes"**: el xlsx de BS-2023 dice que las hojas FOMC y mensuales excluyen los discursos y que se publicarán más adelante. Regla: la comprobación de una variante de un dataset empieza por su documentación y por comparar sumas entre hojas (mensual = Σ evento), no por inferir del nombre de las columnas.
2. **Una hoja "Monthly" no es la suma de la hoja por evento si el objeto está ortogonalizado**: `Monthly MPS_ORTH` se reortogonaliza al nivel mensual. Regla: verificar la identidad de agregación antes de usar una hoja como sustituto.
3. **La encuesta E.2 no da el "% a tipo variable"** que se suponía en el diccionario: da volumen por intervalo de repreciación, cuota prime e intervalo medio, sobre préstamos *concedidos* (flujo). Regla: abrir la estructura de la fuente (`E2_struct.xml`, CodeLists) antes de prometer una variable con su nombre teórico.
4. **Los tramos de una descomposición publicada pueden no sumar el total** (E.2: 92,8–99,96 %). Regla: medir el residuo, acotarlo en un test y calcular la cuota sobre el volumen clasificado; no relajar el assert en silencio ni repartir el resto.
5. **Los recuentos por celda se hacen con el código del estimador, no a mano**: el borrador estimaba ≈ 25 por celda estado×signo; el recuento exacto da 22–29 (liquidez) y 11–18 (DSR). Regla: reutilizar `sample_counts.py` para F4.

## 2026-11-04 · p01 · comprobaciones previas al prerregistro — puntos retirados
Estado: retirada
5. **El DDP de la Fed ofrece el paquete completo en un zip** (`Output.aspx?rel=<REL>&filetype=zip`, sin clave): evita construir URLs de series. Los TIME_PERIOD son fin de trimestre natural aunque la encuesta sea de mitad de trimestre.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
6. **`print` de texto con `−`/`ε` falla en consola cp1252 de Windows**: escribir el fichero y no imprimir el contenido (o `PYTHONUTF8=1`).
   *Motivo:* detalle de entorno o de la sesión, no una regla de método

## 2026-11-07 · p01 · F7 (Romer-Romer y etapa 1b)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Antes de descargar, mirar si el lago ya lo tiene**: el catálogo decía Romer-Romer "sin probar" y el zip del Handbook de Ramey llevaba tres días en `datalake/raw/narrative/`. Regla: grep del nombre de la fuente en `datalake/MANIFEST.csv` y en `datalake/fetch/` antes de escribir un fetch.
2. **Una hoja del Handbook puede duplicar otra con distinto nombre**: `Wieland!resid_full` = `Monthly!RRSHOCK`. Regla: comprobar la identidad entre hojas con un `assert` en el build, y dejar escrito cuál de las variantes (`resid_romer`, `resid_full`) se usa.
3. **El estado de un contraste puede concentrar un episodio extremo**: Volcker (13 trimestres) cae 11/13 en "restringido" y aporta 41 % de su Σ|ε|. Regla: tabular siempre el episodio dominante por estado antes de que Econometría diseñe el MC.
4. **Un ajuste del recorte de la muestra no debe rehacer el panel anterior**: `START=1985Q1` en `build_stage1_us.py` impedía el estado desde 1969; se construyó `stage1r_us.parquet` aparte, reutilizando las funciones, para no tocar los tests ni la muestra congelada de la etapa 1.

## 2026-11-07 · p01 · F7 (Romer-Romer y etapa 1b) — puntos retirados
Estado: retirada
5. **El Excel del QFR no trae clases de tamaño por industria**: las 8 clases solo existen en agregados; por industria solo hay <50 M y ≥50 M. Regla: contar celdas hoja sin solape (no etiquetas) antes de declarar G, y verificar el recuento con el diccionario de tablas.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
6. **`.xls` antiguos no se leen sin `xlrd`** (pandas de este entorno usa calamine): anotar el archivo como "descargado, no abierto" en vez de añadir una dependencia sin pedirla.
   *Motivo:* incorrecto: lo desmiente F14a (no hay python-calamine)

## 2026-11-08 · p01 · F14a (QFR: G y proxy de exposición)
Estado: validada
Validada por: Adrián López Lamata (2026-11-08)
1. **Una definición de grupo que cambia a mitad de la serie no da un panel continuo**: el QFR pasó de <25/≥25 M a <50/≥50 M en 2019Q2. Regla: antes de contar G, listar para cada (industria, tamaño) los trimestres con datos *y su etiqueta* en cada vintage; contar solo celdas con la misma definición en toda la ventana.
2. **El tamaño o la muestra pueden ir en el título de la tabla y no en la cabecera de columna** (QFR 2006–07): se mezclaban «Paper ≥25 M» y «Paper todos los tamaños» y se duplicaban sumas. Regla: parsear título y cabecera, y comprobar con un test que un subgrupo no supera a su total.
3. **Una partida cambia de nombre entre vintages** («Installments…» frente a «Current portion…»): una suma con un componente NaN da NaN en silencio. Regla: tras unir partidas, comprobar que la variable derivada no tiene NaN en la ventana (test).
4. **Medir las rupturas de empalme en el trimestre solapado entre vintages** (|Δlog| mediana 0,01; las reclasificaciones NAICS dan 0,3–0,5) y declarar el umbral. El umbral es una decisión: dar G con y sin excluir rupturas.

## 2026-11-08 · p01 · F14a (QFR: G y proxy de exposición) — puntos retirados
Estado: retirada
5. **`.xls` sin `xlrd`**: la lección de F7 decía que pandas usaba calamine; no es cierto en este entorno (`python-calamine` no está). Un lector BIFF8 mínimo (OLE2 + SST + NUMBER/RK/MULRK) basta para estas tablas; validarlo contra un trimestre que salga también en un `.xlsx`.
   *Motivo:* añadir una dependencia o escribir un lector propio lo deciden los autores
6. **Los descargables de un mismo año de la Census no son el mismo diseño**: antes de fijar la ventana, abrir una vintage de cada régimen (2006, 2008, 2011, 2019, 2023, 2025).
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)
7. **El QFR no trae capex**: la proxy ΔPPE neto + depreciación mezcla fusiones y ventas de activos; calcularla dentro de cada vintage para no mezclar niveles revisados.
   *Motivo:* trasladado a kb/data_catalog.md («Trucos de acceso por fuente»)

## 2026-11-08 · p01 · F5a (zona euro: datos de la puerta de la etapa 2)
Estado: candidata
1. **Antes de comprometer una exposición por país en un diseño, comprobar que la fuente publica el desglose por país.** El MIR del BCE da los volúmenes por periodo de fijación solo para `U2`; por país hay tipos por fijación, pero no cuotas. Regla: listar las series con comodines (`M.<c>.B.A2A....2240.EUR.N`) y contar las de volumen por país antes de prerregistrar la puerta.
2. **Una muestra "sin ZLB" que empieza en 1999 no sirve para datos de préstamos por país**: el MIR y el BSI por país empiezan en 2003Q1 (muchos países, después y con huecos). Regla: calcular la ventana efectiva como la intersección de las series, no la del ejemplo del encargo.
3. **Códigos de país distintos entre fuentes** (Eurostat usa `EL`, el BCE `GR`): una petición con la lista entera devuelve 400 sin decir cuál falla. Regla: pedir país a país y registrar los que fallan.
4. **`_common.save` añade fila al MANIFEST en cada ejecución**, aunque el contenido no cambie: repetir un fetch al depurar duplica filas (mismo hash). Regla: depurar con una sola fuente o dedupicar el MANIFEST antes de cerrar.
