# F23 · Borrador del paper A de p01 (Redacción, 2026-11-08)

Encargo: `desks/redaccion/ENCARGO_2026-11-08_f23-borrador-paper-a.md`. Texto que obliga: `SPEC.md:49-221` (prerregistro `s1r_*`) y
las Desviaciones del 2026-11-08 (`SPEC.md:307-320`: paper A, etapas 1b y 2 cerradas). Las cifras salen todas de
`output/macros.tex` (F21, aprobadas en `audits/2026-11-08_F21_macros.md` y su adenda en 8dfa290).

## HANDOFF

**Hecho.**
- `paper/main.tex`: borrador completo en inglés, en un solo archivo, que compila con `latexmk -pdf` (12 páginas, `paper/main.pdf`).
  Secciones:
  - Introducción y literatura (`main.tex:54-110`).
  - Modelo: Prop. 1–3, Corolario 1 y Observación (`:112-219`).
  - Diseño prerregistrado: datos, estado, especificación, estimando, inferencia, diagnósticos, β_ref, regla V3s, potencia ex
    ante (Tabla 1) y robustez (`:221-368`).
  - Resultados: Tabla 2 con las 13 filas (b_lin, 6 b_C y 6 b_U), veredicto paso a paso y diagnósticos de los choques (Tabla 3)
    (`:370-469`).
  - Qué permite descartar la medición (`:471-487`), limitaciones (`:489-505`), conclusión con las etapas 1b y 2 como trabajo
    futuro condicionado a datos (`:507-521`).
  - Apéndice: mapa proposición → test SymPy (`:526-558`).
- `paper/p01.bst`: copia de `plainnat.bst` sin el campo `note`, porque en `references.bib` ese campo guarda el estado de verificación
  de Literatura y si no se imprimiría en la bibliografía.
- `uv run python tools/integrity.py --only citations,numbers` → `integridad: OK`. `uv run python tools/integrity.py` (completo,
  incluida la puerta `gate`) → `integridad: OK`. `uv run pytest -q` → 272 passed, 5 skipped. `uv run ruff check .` → limpio.
- F23 marcada en `TASKS.md`; lección candidata en `kb/lessons/writer.md`. Sin commit, como pide el encargo.

**Evidencia.**
- Veredicto y las 6 filas de b_C: `main.tex:379-416` (Tabla 2, solo macros `\bLin*`, `\bC*`, `\bU*`, `\verdictoVs`), de
  `output/tables/s1r_estimates.md:7-21`.
- H1 no se interpreta: `main.tex:418-432`. Ninguna frase dice que los datos «sugieren», «apoyan» o «son coherentes con» la
  amplificación (comprobado con grep de suggest/support/consistent/significan/drive/cause/amplif). Las seis filas se dan «whatever
  their p-values» (`:430-432`). La nota de la Tabla 2 separa el p unilateral del IC bilateral (hallazgo 3(b) de
  `audits/2026-11-08_F16_estimacion.md:76-79`).
- `h0_falla` no es evidencia de ausencia de efecto: se apoya en el IC de β_lin, que contiene 0 y β_ref (`main.tex:473-478`), y no en
  `SPEC.md:161` (hallazgo 3 de F17, `audits/2026-11-08_F16_estimacion.md:140-143`).
- MDE: «roughly 10 pp» en el texto (`main.tex:89, 323, 480`) y las macros `\MdeHomo*`/`\MdeHet*` solo en la Tabla 1, con la nota
  de que no tienen más precisión (`:342-345, 353-355`), como pide F22 (`audits/2026-11-08_F21_macros.md:37-44`).
- Teoría: cada proposición apunta a su test en `theory/check_nesting.py` y `theory/check_aggregation.py` (`main.tex:530-556`);
  su contenido es el de `theory/VERIFICACIONES_2026-11-04.md:8-59,106-111`.
- Etapas 1b y 2: solo como trabajo futuro, «did not pass its gate» (`main.tex:514-521`), según `SPEC.md:314-320`.

**Compilación (`latexmk -pdf`, `paper/main.log`).** Sin errores ni referencias o citas sin definir. Warnings:
- 2 `Underfull \hbox` en la bibliografía (entrada de Ottonello-Winberry, por el DOI y la URL largos). Cosmético.
- TinyTeX genera con METAFONT una fuente bitmap `tcrm1095` (TS1) para algún símbolo; el PDF sale bien, pero el símbolo será bitmap.
  No he localizado qué carácter la pide.
- `bibtex`: sin warnings.

**Defecto encontrado aguas arriba (no lo he tocado: `output/` y `code/` están fuera de mi alcance).** `output/macros.tex:114,117,121,124`
define `\PwHomoH0Falla`, `\PwHomoPowH0`, `\PwHetH0Falla` y `\PwHetPowH0`. LaTeX no admite dígitos en el nombre de una macro, y
con `\input` tal cual la compilación se para (`! LaTeX Error: Missing \begin{document}`, l. 114). F22 comparó las cadenas una a
una, pero no compiló el archivo. Solución provisional en `main.tex:18-27`: se lee `macros.tex` con el `0` como letra y se crean
cuatro alias (`\PwHomoHzeroFalla`, etc.). No cambia ningún valor. **Arreglo de verdad:** Econometría cambia los nombres en
`code/analysis/02_paper_macros.py` y regenera `macros.tex`. Eso cambia `code/` y `output/`, así que hace falta otra comprobación
corta del Referee; después se quitan las líneas 18-27 de `main.tex`.

**Decisiones y quién las tomó (todas de esta desk, de forma o de redacción).**
- Un solo `main.tex` en vez de secciones aparte. Motivo: `check_numbers` solo mira las líneas posteriores a `\begin{document}` de
  cada `.tex` (`tools/integrity.py:171-177`), así que en un archivo de sección sin `\begin{document}` no comprobaría nada.
- `% num-ok` solo en constantes de diseño o citadas, nunca en resultados: α = 0,05, la potencia objetivo 0,8 del MDE, el nivel del
  IC y el −2,5 % de Tenreyro-Thwaites (`main.tex:89,297,306-313,323,342,384,422,480`).
- El modelo se presenta desde las condiciones de primer orden de `check_nesting.py:25-31` (sin escribir un problema de optimización
  que no está verificado). G se define como el déficit esperado de una necesidad de liquidez normal, que es la G de
  `check_aggregation.py:143`.
- Proposiciones incluidas: nido y límites (`check_nesting.py`) y agregación (`check_aggregation.py`). Que la fórmula rígida «subestima»
  solo está comprobado en un ejemplo numérico (`VERIFICACIONES_2026-11-04.md:42`), así que el texto dice «does not hold», no
  «understates».
- La Observación tras el Corolario 1 (`I_u > ω_min p_f/a > 0` con g ≥ 0) combina dos resultados verificados (la ec. de I_u y ω > ω_min),
  pero no tiene un test propio. Queda marcada con `\todo` (`main.tex:558`).
- Lenguaje: el estado es predeterminado pero no exógeno; las diferencias entre estados «no son efectos de la liquidez»
  (`main.tex:252-254`). La correspondencia entre la liquidez agregada y la masa de empresas restringidas se presenta como supuesto
  (`:216-218`).
- La regla de decisión se escribe con «p < 0.05» en vez de «significant» (`main.tex:308-314`).

**Supuestos y límites.**
- Las páginas citadas son las de los WP (IOPO pp. 10–11; Perez-Orive pp. 12–13; TT pp. 11–12), como avisa
  `exploration/CITAS_DISENO_F_2026-11-04.md:6-11`; el `.bib` lleva la versión de revista. Ramey (2016) se cita sin página
  (`references.bib`, nota de `Ramey2016`).
- Ottonello-Winberry solo se cita por su resumen («firms with low default risk … most responsive»), que es lo único comprobado
  (`CITAS_DISENO_F_2026-11-04.md:74`). Cloyne et al., Grob-Züllig, Jungherr et al., Greenwald et al. y Bottero et al. aparecen
  solo en una cita de grupo por tema, sin atribuirles ningún resultado concreto.
- No atribuyo a Tenreyro-Thwaites la logística con γ = 3 ni la estandarización de z (F17 avisa de que no está verificado,
  `audits/2026-11-08_F16_estimacion.md:104-105`).
- La cobertura de NW5+HC3 (0,948–0,990, `SPEC.md:121-124`) no tiene macro. El texto la describe sin cifras («close to or above the
  nominal level … without material undercoverage»), porque el mínimo, 0,948, queda una milésima por debajo de 0,95.
- No he podido ver el PDF con `pdftoppm`; lo he revisado con PyMuPDF (páginas 1, 7, 8, 9 y 11 renderizadas fuera del repo).

**Descartado y por qué.**
- Las proposiciones de coordinación (`check_coordination.py`): no las necesitan ni H0 ni H1, y ampliarían el paper más allá del A.
- La réplica con `mps_bs23_orth`, la asimetría, β_C − β_U, la IRF y cualquier exploratorio: F16 no los estimó y el paper A no los
  usa (`SPEC.md:187-199`).
- Las cifras de la etapa 1b (G = 28–32 frente a 40) y de la etapa 2: no hay macros. El texto lo dice sin cifras.
- Figuras: las de `output/figures/` son de la etapa 1 original (desde 1985), no de la muestra `s1r`.
- Contar cuántas filas de b_C tienen p < 0,05: sería el énfasis selectivo que F17 señaló (`audits/2026-11-08_F16_estimacion.md:66-74`).

**`\todo` pendientes (7).**
1. `main.tex:31`: autores y afiliaciones (autores).
2. `main.tex:100`: Jeenas (BSE WP 1409), el paper empírico más cercano; la entrada `Jeenas2026` está en DISCREPANCIA (Literatura).
3. `main.tex:109`: citar TFG1/TFG2, la base del modelo; no tienen entrada en el `.bib` (autores + Literatura).
4. `main.tex:233`: procedencia verificada de la extensión de Romer-Romer (Wieland, openICPSR 135741), que Literatura no pudo abrir
   (Literatura).
5. `main.tex:238`: citas formales de FRED, BEA y Z.1; `FRED2026` y `BEA2021` no están VERIFICADAS (Literatura).
6. `main.tex:282`: Newey-West (1987) no está VERIFICADA (Literatura). `main.tex:284`: macro del rango de cobertura de NW5+HC3, si
   los autores quieren la cifra en el texto (Econometría).
7. `main.tex:558`: test SymPy propio de la Observación (`I_u > ω_min p_f/a` con g ≥ 0), o quitarla (Teoría).

**Pendiente de decidir.**
- Coordinación: encargar a Econometría el cambio de nombre de las 4 macros con dígito, y al Referee la comprobación corta posterior.
- Coordinación: si `paper/main.pdf` se versiona (hoy git no lo ignora) o se añade a `.gitignore`.
- Autores: título y encuadre. El paper pone el peso en la teoría y presenta la medición como acotada; si prefieren otro equilibrio
  entre las dos partes, es decisión suya.
- Referee: auditoría de `paper/` en sesión nueva. Aparte de lo automático, conviene que compruebe que el texto no lee b_C como
  contraste (`exploration/F18_TRAS_H0_2026-11-08.md:119`).

## HANDOFF F29

**Hecho.** En `paper/main.tex`: (1) quitado el rodeo de macros, queda `\input{../output/macros.tex}`; (2) cobertura NW5+HC3 con
`\CovAumNwHcLo`–`\CovAumNwHcHi`; (3) `\todo` de la Observación quitado, enunciado intacto; (4) citas `Jeenas2026`,
`WielandRomerShocks2021`+`WielandYang2020`, `FRED2026`+`BEA2026NonresInv`+`FedZ12026`, `NeweyWest1987`. Quedan 2 `\todo`
(autores `main.tex:22`; TFG1/TFG2 `main.tex:99`), más la definición (`:15`).

**Evidencia.** `compile_main.py` (`audits/replication_2026-11-11_F28/`): «pdflatex rc=0; 0 errores». `latexmk -pdf`: sin
warnings en `paper/main.log`. `integrity.py --only citations,numbers`: OK. Fuentes de las citas:
`exploration/F26_CITAS_2026-11-08.md`; Observación: `theory/F27_OBSERVACION_2026-11-11.md`. Sin commit (lo pide el encargo;
entra con el informe F30 del Referee).

**Decisiones (Coordinación, en el encargo).** Citar el WP `Jeenas2026`, no `JeenasJPE2026`; sin número de tabla NIPA; autores y
TFG1/TFG2 se quedan como `\todo`.

**Supuestos y límites.**
- Wieland/Romer-Romer: solo digo que la extensión cubre hasta 2007 y la construye Wieland. F26 no verificó que la serie de los
  ficheros de Ramey (2016) sea exactamente `resid_full` (nota de `WielandRomerShocks2021` en `references.bib`).
- «Closest empirical study» ya estaba en el borrador; ahora se atribuye al WP.
- El rango de cobertura 0,948–0,990 va junto a «close to or above the nominal level»; el mínimo está una milésima bajo 0,95.
- No he visto el PDF renderizado; solo el log.

**Descartado.** Escribir `a>0` explícito en la pendiente del coste marginal (opcional; no cambia nada).

**Pendiente de decidir.** Autores: lista de autores y cita de TFG1/TFG2; si se pasa de `Jeenas2026` a `JeenasJPE2026`.
Coordinación: F30 (Referee) sobre texto y `theory/`; si `main.pdf` se versiona.

## HANDOFF F31

Aplica a `paper/main.tex` (sin commit, como pide el encargo) los hallazgos de `audits/2026-11-11_F30_texto.md`. Solo texto: no
he tocado `code/`, `output/`, `theory/`, `references.bib` ni la SPEC, ni ningún enunciado de proposición.

**Hecho, por hallazgo** (líneas del `main.tex` resultante):
- **1 (mayor), aplicado.** `main.tex:84-85`, con la corrección mínima del informe. Revisados abstract (`:29-44`), §5 (`:472-488`)
  y conclusión (`:508-521`): ninguna otra frase atribuye el límite a los datos sin acotar (§5 ya dice «this design»).
- **2 (mayor), aplicado, opción (a).** `main.tex:233-236`: Ramey (2016) re-estima con Greenbook actualizados (`WielandYang2020`
  respalda solo eso); Wieland distribuye una extensión similar (`WielandRomerShocks2021`); «we have not verified that the two
  series coincide». Ya no se dice quién construyó la serie.
- **4, aplicado.** «five times» → `\MdeHetC{} to \MdeHomoC{} times` (macros, no palabras) en `:43`, `:82`, `:323` y `:493`;
  «linear point estimate is negative» `:39`; «unusually low relative to their recent trend» `:71-72`.
- **5, aplicado.** Nota de la tabla 2, `main.tex:414-415`.
- **6, aplicado.** Objetivo con penalización cuadrática del déficit `main.tex:115-119` (el Lagrangiano de
  `audits/replication_2026-11-11_F30/check_remark.py:46`); `a=b+\eta v+\psi/N>0` en `:110`. `\delta` se define ahora en
  el objetivo («costs δ per unit»), por eso salió de la frase tras (`eq:kkt`).
- **7, aplicado.** `a` de la empresa representativa que internaliza el precio del banco, con remisión a Prop. 3(ii), y curvatura
  `b+\eta v` de la empresa precio-aceptante (`:111-113`); `L=\sum_j s_jI_j` (`:171-172`); paso a H1 cita la Observación
  (ahora `\label{rem:chain}`) y la Prop. 3(iii) (`:209-212`).
- **8, aplicado.** Fila del test de F27 en el apéndice (`:549`); «verified symbolically» → «verified with SymPy (symbolic
  identities and limits; sign claims checked on sampled domains)» en abstract `:35-36` e introducción `:63-64`; apéndice `:530-531`
  («Most positive tests have a negative counterpart»).
- **3 (OK) y 9–11:** sin cambios; 9 (Jeenas) excluido por el encargo.

**Evidencia.** `uv run python papers/p01-liquidity/audits/replication_2026-11-11_F30/compile_full.py`: rc [0,0,0,0], 0 errores,
0 citas/referencias indefinidas, 0 Overfull, 13 páginas, 22 claves. `uv run python tools/integrity.py --only citations,numbers`:
«integridad: OK». `\todo` en uso: 2 (`main.tex:22`, `:101`), más la definición (`:15`). El test citado existe
(`theory/check_nesting.py:141`).

**Decisiones.** Coordinación (encargo): opción (a) en el hallazgo 2; no tocar Jeenas, autores ni TFG1/TFG2. Redacción: usar las
macros `\MdeHetC`/`\MdeHomoC` en vez de «five to five and a half» (lo sugiere el encargo; así no hay cifra tecleada); en el
hallazgo 7, la variante «empresa representativa» en vez de introducir `a_0`, para no tocar la notación de las proposiciones.

**Supuestos y límites.**
- El ω_min de la Prop. 3(iii) sigue sin decir con qué `a` se evalúa: aclararlo exigiría tocar el enunciado (fuera del encargo).
  Como 3(iii) es una hipótesis «ω_j ≥ ω_min > 0», la afirmación vale con cualquiera de las dos.
- La frase de H1 dice que la Prop. 3(iii) vale «whatever the mass of constrained types»: es mi lectura de su enunciado (slack ⇒
  ω_j = 1 ≥ ω_min); el Referee debería confirmarla.
- No he visto el PDF renderizado; solo la salida de `compile_full.py`.

**Descartado.** Añadir aserciones simbólicas de signo o el test de las KKT desde ℓ(m) (es `theory/`, para Teoría). Corregir el
docstring de `check_nesting.py` (idem; haría caducar la aprobación).

**Decisiones de los autores (2026-11-11), aplicadas después:**
- **TFG1/TFG2:** son borradores propios y no se citan. Quitado el `\todo` de la literatura (antes `main.tex:101-102`) sin cita
  sustituta; la contribución teórica (`main.tex:55-64`) queda como estaba. Resuelve la dependencia «\todo» del informe F30.
- **Jeenas (hallazgo 9):** fuente principal `JeenasJPE2026`, con el WP entre paréntesis (`\citealt{Jeenas2026}`) y sin «in a
  working paper» (`main.tex:93-94`).
- Tras ambas: `compile_full.py` rc [0,0,0,0], 0 errores, 0 indefinidas, 0 Overfull, 13 páginas; `integrity.py --only
  citations,numbers` OK; queda solo el `\todo` de autores (`main.tex:22`). La lista de claves de `compile_full.py` no muestra
  `Jeenas2026` porque su regex no reconoce `\citealt` (`compile_full.py:42`); LaTeX no da la cita por indefinida y el check
  `citations` sí reconoce `\citealt` (`tools/integrity.py:132`).
- Límite: el apéndice sigue nombrando `test_tfg1_minimum_branches` y `test_representative_agent_matches_tfg2` (`main.tex:542`,
  `:553`), que remiten a obras no citadas. Renombrarlos es `theory/` (Teoría) y haría caducar la aprobación.

**Pendiente de decidir.** ~~Autores: Jeenas WP/JPE (hallazgo 9), autores y TFG1/TFG2.~~ Resuelto el 2026-11-11, salvo la lista de autores.
Coordinación: si los cambios de §2 (objetivo, `a`, `L`, paso a H1) merecen una lectura breve del Referee antes del commit, o si basta
el informe F30 (lo exige la puerta solo para `code/`, `data/`, `output/`, `theory/`, SPEC); opción (b) del hallazgo 2 (Datos +
Literatura) si se quiere volver a afirmar quién construye la serie.

## HANDOFF F33

Encargo de la Coordinación (2026-11-11): hallazgos 3 y 7 de `audits/2026-11-11_F32_relectura.md`. Solo `paper/main.tex`, sin commit.
- **Hallazgo 3:** «internalizes the bank's pricing» sustituido por la corrección mínima del informe, palabra por palabra (`main.tex:110-113`).
- **Hallazgo 3, relacionado:** «(with $a_j$ in place of $a$)» en la frase de la Observación «at a given lending rate» (`main.tex:209`).
- **Hallazgo 7, apéndice:** «Every result in Section 2, from the optimality conditions (1) on, is verified with SymPy…» (`main.tex:529`).
- **Hallazgo 7, abstract:** «All results, from the firm's optimality conditions on, are verified…» (`main.tex:35`); sin `\eqref`, porque el abstract
  no remite a ecuaciones.
- **Hallazgo 7, introducción:** «Every result, from the optimality conditions~(1) on, is verified…» (`main.tex:63`), con una referencia hacia
  delante a `eq:kkt`.
- **Evidencia:** `compile_full.py` (F30) rc [0,0,0,0], 0 errores, 0 indefinidas, 0 Overfull, 13 páginas; `integrity.py --only
  citations,numbers` OK; queda solo el `\todo` de autores (`main.tex:22`).
- **Sin tocar (encargo):** nombres de tests con `tfg` (`main.tex:543`, `:554`); el test que derive las KKT desde el objetivo sigue pendiente
  para Teoría (F30 hallazgo 6, F32 hallazgo 7).
