# Encargo de la Coordinación a Datos — 2026-11-04 · Comprobaciones previas al prerregistro

Modelo: sonnet

Rutas relativas a la raíz del repo (`../../`). Contexto: `papers/p01-liquidity/exploration/PREREG_DRAFT.md` (§5, §4 "Opción A", §6).
De estas tres comprobaciones dependen decisiones de los autores. No estimes nada y no mires respuestas de la inversión a los choques.

1. **Serie de Bauer-Swanson con discursos.** Abre el xlsx de BS-2023 que ya está en el lago y lista **todas** sus hojas y columnas.
   - ¿Hay una serie ortogonalizada que incluya los discursos del presidente de la Fed (además de las reuniones del FOMC)?
   - Si la hay, añádela al panel como `mps_bs23_orth_sp`, con su agregación trimestral, su cobertura y su correlación con `mps_bs23_orth`.
2. **Una medida de la exposición a la repreciación (g)** para EE. UU., trimestral y gratuita. Por ejemplo, la cuota de préstamos C&I a
   tipo variable del Survey of Terms of Business Lending (Fed, E.2, hasta 2017), o el plazo de revisión de los tipos de los préstamos C&I.
   Si existe, descárgala con script y MANIFEST y documéntala. Si no, explica qué probaste y por qué no vale. No fabriques un sustituto.
3. **Recuentos exactos, por código,** de la muestra de §6 del borrador:
   - muestra 1988Q2–2023Q4 sin ZLB (`ffr` < 0,25) ni 2019Q1–2021Q4;
   - observaciones por celda (estado = liquidez amplia/deuda sin tendencia de 12 trimestres < mediana) × (signo del choque);
   - lo mismo con el DSR.
   Escríbelos en `papers/p01-liquidity/data/clean/SAMPLE_COUNTS.md` con el script que los genera.

Entregable: actualiza `DICTIONARY.md`, `MANIFEST.csv`, los scripts y los tests. No hagas commit. Lecciones en `kb/lessons/data.md` (`Estado: candidata`).
