# Encargo de los autores a Teoría — 2026-11-04 · Biblioteca de papers de p01

## Petición literal de los autores
> "Quiero que el de teoría busque todos los papers pertinentes en repos y los descargue. Si no los encuentra,
> que deje un link para descargarlo gratis, aunque debería poder."

Para Teoría es su biblioteca de trabajo: los modelos de TFG1 y TFG2 se derivarán contra estos textos completos.
Rutas relativas a la raíz del repo (`../../`).

## Qué papers
1. Todas las entradas de `papers/p01-liquidity/paper/references.bib` (≈83).
2. Los de las fichas en `kb/topics/policy-transmission/papers/` (ya deberían estar en el `.bib`).
3. Prioridad de descarga: primero los marcados [C] (competencia directa) y [F] de Línea 1 y Línea 2 en
   `kb/topics/policy-transmission/README.md`; después el resto. Omite las entradas que no son papers (series de
   datos como FRED2026, FRBSFMonetarySurprises, NFCIDocumentation, BEA2021): solo indícalas en el índice.

## Dónde buscar (solo fuentes legales y gratuitas)
- **OpenAlex** (sin clave): `https://api.openalex.org/works/doi:<DOI>` → campo `open_access.oa_url` y `best_oa_location.pdf_url`.
- arXiv; NBER (`https://www.nber.org/system/files/working_papers/w<N>/w<N>.pdf`); RePEc/IDEAS (enlaces a la versión WP);
  webs de bancos centrales (Fed Board FEDS/IFDP, FRBSF, NY Fed Staff Reports, BCE, BoE, BIS, Banca d'Italia, SNB, DNB…);
  webs personales de los autores; repositorios institucionales; CORE; versiones de acceso abierto de la revista.
- **Prohibido:** Sci-Hub, LibGen, Anna's Archive y cualquier copia pirata. No inicies sesión en ningún sitio.
  No uses SSRN si exige login.
- Si solo existe la versión de revista de pago, busca el working paper equivalente (mismo título o casi) y anótalo
  como "versión WP". Si no hay ninguna versión gratuita, no descargues nada: deja el enlace a la página oficial y
  marca **SIN VERSIÓN GRATUITA**.

## Cómo descargar y comprobar
- `curl -L -A "Mozilla/5.0" -o <destino> <url>`. Destino: `kb/library/<clave-bibtex>.pdf`.
- **Comprueba cada archivo:** que empiece por `%PDF` (no una página HTML de error) y que la primera página
  contenga el título del paper. Puedes leerla con `uv run --with pypdf python -c "..."`. Si no coincide, bórralo y
  márcalo como fallo.
- No descargues nada que no sea un PDF de un paper de la lista.

## Entregables
- `kb/library/*.pdf`: los PDFs. **No se versionan en git** (derechos de autor); la Coordinación ya lo ha excluido.
- `kb/library/INDEX.md` (sí se versiona), una fila por entrada del `.bib`:
  `clave | título | estado (DESCARGADO / ENLACE / SIN VERSIÓN GRATUITA / NO ES PAPER) | versión (revista/WP + año) | URL de origen | línea (1/2/transversal) | una línea: qué modelo o resultado le sirve a Teoría`.
- Al final del índice: recuento por estado y la lista de lo que falta, con su mejor enlace.
- `kb/lessons/theory.md`: añade lecciones del encargo (fuentes que funcionaron, trampas).

## Reglas
- No modifiques el `.bib` ni las fichas: si ves un error en una referencia, anótalo en el índice (columna de notas).
- No inventes URLs. Una URL solo va al índice si la has comprobado.
