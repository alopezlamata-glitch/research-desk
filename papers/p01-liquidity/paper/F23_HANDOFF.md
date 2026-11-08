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
