# p01 — TASKS

Estado: `[ ]` pendiente · `[~]` en curso · `[x]` hecha · `[!]` bloqueada.
Cada tarea tiene desk, criterio de "hecho" y su propio commit.

## Fase 0: exploración
- [x] **0.1** · coordination · Inventario de iteraciones previas (2026-11-04): 57 archivos únicos archivados en `prior/archive/` (fuera de git); cronología, líneas, errores y lo que se salva en `exploration/INVENTORY.md`.
- [x] **0.1b** · literature · Literatura del paper buscada en repositorios a partir de las bibliografías de TFG1, TFG2, `Policy_Confidence_Coherence` y v22 (los autores indican que las líneas más relevantes son las de TFG1 y TFG2). Encargo: `desks/literatura/ENCARGO_2026-11-04.md`; sesión lanzada el 2026-11-04 (incluye también la 0.2). Resultado (2026-11-04): ~85 entradas en `paper/references.bib`; ~8 discrepancias graves, `exploration/LITERATURE_REPORT.md`. Parcial: v22 no extraída (solo refs del README) y ~25 clásicos sin comprobar.
- [x] **0.2** · literature · Fichas de la literatura + mapa en `kb/topics/`. Hecho: una ficha por paper relevante; ninguna cita sin verificar. Resultado (2026-11-04): mapa en `kb/topics/policy-transmission/README.md` y 12 fichas en `papers/` (basadas en resúmenes/registros, texto completo sin leer); las citas sin verificar quedan marcadas NO VERIFICADA en el bib, no eliminadas.
- [ ] **0.3** · scientific-director · Fichas de las iteraciones/propuestas descartadas, empezando por la más reciente (z01 "Simulate This" + `Policy_Confidence_Coherence.tex`), `modelshock` y `tc_architecture_colab_v3`. Hecho: una ficha por iteración en `exploration/discarded/`, con qué se intentó, por qué cayó y qué se salva.
- [ ] **0.3b** · referee · Auditoría del resultado de `modelshock` (LP con shocks JK, interacción significativa a h = 4–8) antes de que pese en la elección de diseño.
- [ ] **0.4** · scientific-director · 5–8 candidatos de familias distintas (ver PLAN). Hecho: cada candidato con pregunta, identificación, datos, parámetros/observaciones y riesgo.
- [ ] **0.5** · data + econometrics · Datos y potencia de los finalistas. Hecho: disponibilidad verificada + Monte Carlo rápido de potencia.
- [ ] **0.6** · referee · Pre-mortem de los 3 mejores. Hecho: informe en `audits/`.
- [ ] **0.7** · coordination · `exploration/REPORT.md` con la rúbrica y la recomendación.
- [ ] **0.8** · autores · Decisión y nueva SPEC.

## Independientes del diseño (se pueden hacer ya)
- [x] **A2** · theory · Check SymPy de la convexidad de δ en v22: 4/4 en verde, error confirmado.
- [ ] **A1** · referee · Auditoría independiente de v22 (confirma o refuta `prior/diagnosis_v22.md`). Útil para que la Fase 0 no repita errores.
