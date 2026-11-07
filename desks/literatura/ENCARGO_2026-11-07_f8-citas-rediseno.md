# Encargo de la Coordinación a Literatura — 2026-11-07 · F8: citas del rediseño de la etapa 1 de p01

Modelo: sonnet

Rutas relativas a la raíz del repo (`../../`). Contexto: los autores han decidido rediseñar la etapa 1 con Romer-Romer
como choque principal y la media de h = 4..12 (Desviación del 2026-11-07 en `papers/p01-liquidity/SPEC.md`; propuesta del
Director en `exploration/REDESIGN_POWER_2026-11-04.md`, §4, con las citas que marcó **[pendiente de Literatura]**).

Usa la skill `../../.claude/skills/verify-citation/SKILL.md` para cada referencia: que existe, que dice lo que se le
atribuye y en qué página. Nada se marca VERIFICADA sin haberlo comprobado en la fuente (DOI, NBER, SSRN o la web del autor).

## Qué verificar y añadir a `papers/p01-liquidity/paper/references.bib`
1. **Romer y Romer (2004)**, la serie narrativa de choques monetarios: dónde se definen y qué muestra cubren.
2. **Coibion (2012)**, la extensión de Romer-Romer que usa el Handbook de Ramey: muestra y construcción.
3. **Ramey (2016)**, *Macroeconomic Shocks and Their Propagation* (Handbook of Macroeconomics), **en el original**: la parte
   sobre choques monetarios narrativos y la debilidad de los choques de alta frecuencia como instrumento.
4. **Li, Plagborg-Møller y Wolf**, LP frente a VAR (sesgo y varianza): la página que respalda que una LP pierde poco frente
   a un estimador eficiente con el mismo choque, que es el argumento del §1 de la propuesta.
5. **Una fuente para usar el tamaño de la empresa como proxy de la exposición a tipo variable** (etapa 1b). Si la lleva
   alguna referencia que ya está en el `.bib` (p. ej., IOPO 2018), indica la página.
6. **Una extensión de Romer-Romer más allá de 2007** (p. ej., Wieland-Yang), si existe y es pública: cobertura y dónde se
   descarga. Pásale el enlace a Datos anotándolo en `kb/data_catalog.md`.

## Reglas
- Si una cita del borrador del Director no dice lo que se le atribuye, márcala `DISCREPANCIA:` con el motivo, como en el
  `.bib` actual. No la corrijas en su documento; anótalo en tu informe.
- Si guardas un PDF, va a `kb/library/` con su fila en `kb/library/INDEX.md`.

## Entregable
Las entradas en `references.bib` con `note = {VERIFICADA. <página y qué respalda>}` (o `DISCREPANCIA:`), y un informe breve
en `papers/p01-liquidity/exploration/F8_CITAS_2026-11-07.md`: cada cita, lo que respalda y su página.
`uv run python tools/integrity.py --only citations` en verde. Marca **F8** en `TASKS.md`. Lecciones en
`kb/lessons/literature.md` (`Estado: candidata`). No hagas commit.
