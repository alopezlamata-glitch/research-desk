---
name: verify-citation
description: Verifica que una referencia existe y dice lo que se le atribuye antes de citarla o de marcarla VERIFICADA en el .bib. Úsalo siempre que vayas a añadir o cambiar una entrada de references.bib o a citar algo en un .tex.
---

Una cita solo pasa el check `citations` de `tools/integrity.py` si su `note` empieza por `VERIFICADA`.
Este es el único procedimiento para llegar a ese estado.

1. **Identificador persistente.** Busca DOI, número NBER/SSRN/arXiv o la página oficial del working paper.
   Comprueba en la fuente (no en un resumen de búsqueda) título, autores **en orden**, año, revista,
   volumen y páginas. OpenAlex (`https://api.openalex.org/works/doi:<DOI>`) sirve para contrastar metadatos.
2. **Estado publicado.** "Forthcoming", "R&R" o "accepted" solo cuentan si lo dice la revista o la web
   del autor, con fecha. Si no, se cita como working paper.
3. **Lo que se le atribuye.** Si la cita apoya una afirmación concreta (un resultado, una cifra), léela en
   el texto completo: `kb/library/md/<clave>.md` (o descárgalo legalmente, ver `kb/README.md`) y anota la
   página. Una afirmación verificada solo con el resumen se marca `(solo resumen)`.
4. **Escribe el estado en `note`**, en este formato:
   - `VERIFICADA. <fuente comprobada>. <p. N si respalda una afirmación concreta>`
   - `DISCREPANCIA: <qué no coincide y con qué fuente>` → no se puede citar hasta corregirlo.
   - `NO VERIFICADA: <qué se intentó>` → no se puede citar.
5. **Nunca** se escribe VERIFICADA a partir de memoria del modelo, de otro `.bib` o de una bibliografía ajena.

Comprueba al final: `uv run python tools/integrity.py --only citations`.
