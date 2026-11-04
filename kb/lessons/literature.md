# Lecciones — Literatura

## 2026-11-04 · p01 · tareas 0.1b/0.2
Estado: candidata
- **Los borradores de LLM contienen citas inventadas o mal atribuidas** (Caballero-Simsek AER 2021, Reichlin-Turner-Woodford JEP, Bredemeier JME 2024). Una referencia con revista, volumen y páginas completos puede ser falsa: verificar siempre en RePEc/DOI, no por plausibilidad.
- **"Accepted/forthcoming" no es verificable por el registro bibliográfico** (Jeenas, Lakdawala-Moreland). Pedir la página del artículo en la revista; si no, citar el WP.
- **Mejores fuentes rápidas:** EconPapers/IDEAS (`RePEc:<handle>` da año, volumen y páginas), páginas NBER/FEDS, `bis.org` y `snb.ch`. Buscar con título entre comillas + revista.
- **Los resúmenes de búsqueda no equivalen a leer el paper:** las fichas son provisionales hasta leer el texto; no extraer cifras de ellos.
- **Datos de shocks cambian de versión:** la serie FRBSF de sorpresas se actualizó (ago-2025); los borradores citaban la anterior. Guardar siempre fecha y hash (ver reglas de `data/raw`).
- **Pedir al lanzar la sesión permiso para scripts:** extraer v22 requería ejecutar un script Python (aprobación); el lector de PDF no estaba (`pdftoppm`). Dejar la extracción del PDF preparada por la Coordinación.
- **Presupuesto:** ~60 citas clásicas se dejaron sin verificar para priorizar las 2025–26; conviene un segundo pase corto.

## 2026-11-04 · p01 · L1 (citas del diseño F; ver `exploration/CITAS_DISENO_F_2026-11-04.md`)
Estado: candidata
- **Las páginas citadas son las del WP, no las de la revista.** Verificar con la versión que hay en `kb/library` y decirlo en la cita; si se publica la de revista, rehacer páginas.
- **Comprobar qué contiene realmente un fichero de la biblioteca:** `OttonelloWinberry2020` es un juego de diapositivas aunque el INDEX diga "paper SED 2017". Mirar la primera página antes de fiarse de la descripción.
- **"Ambiguo" en un paper puede referirse a otra cosa:** Perez-Orive p. 8 llama ambiguo a OW sobre la asimetría, no sobre el signo restringido×choque. Leer la frase completa antes de usarla como apoyo.
- **PDFs de NBER descargados con WebFetch no se leen** sin `pdftoppm`/Python: dejar la conversión (`tools/pdf2md.py`) preparada o pedir aprobación.
