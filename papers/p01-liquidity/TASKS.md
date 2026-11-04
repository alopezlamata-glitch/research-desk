# p01 — TASKS

Estado: `[ ]` pendiente · `[~]` en curso · `[x]` hecha · `[!]` bloqueada.
Cada tarea tiene desk, criterio de "hecho" y su propio commit.

## Fase 0: exploración
- [x] **0.1** · coordination · Inventario de iteraciones previas (2026-11-04): 57 archivos únicos archivados en `prior/archive/` (fuera de git); cronología, líneas, errores y lo que se salva en `exploration/INVENTORY.md`.
- [x] **0.1b** · literature · Literatura del paper buscada en repositorios a partir de las bibliografías de TFG1, TFG2, `Policy_Confidence_Coherence` y v22 (los autores indican que las líneas más relevantes son las de TFG1 y TFG2). Encargo: `desks/literatura/ENCARGO_2026-11-04.md`; sesión lanzada el 2026-11-04 (incluye también la 0.2). Resultado (2026-11-04): ~85 entradas en `paper/references.bib`; ~8 discrepancias graves, `exploration/LITERATURE_REPORT.md`. Parcial: v22 no extraída (solo refs del README) y ~25 clásicos sin comprobar.
- [x] **0.2** · literature · Fichas de la literatura + mapa en `kb/topics/`. Hecho: una ficha por paper relevante; ninguna cita sin verificar. Resultado (2026-11-04): mapa en `kb/topics/policy-transmission/README.md` y 12 fichas en `papers/` (basadas en resúmenes/registros, texto completo sin leer); las citas sin verificar quedan marcadas NO VERIFICADA en el bib, no eliminadas.
- [x] **0.4–0.8** · Sustituidas el 2026-11-04 por `exploration/FIRST_PRINCIPLES.md` + el abogado del diablo (`exploration/DEVILS_ADVOCATE_2026-11-04.md`, rúbrica con 6 diseños). Los autores aprueban el **diseño F** (ver Desviaciones de la SPEC). 0.3 (fichas de descartadas) no se hace: lo salvable ya está en INVENTORY y FIRST_PRINCIPLES.

## Diseño F
- [~] **F1** · theory · `check_nesting.py`, `check_aggregation.py` (banco común) y `check_coordination.py` + `theory/VERIFICACIONES_2026-11-04.md`. Encargo: `desks/teoria/ENCARGO_2026-11-04_verificaciones-p01.md` (lanzada 2026-11-04 16:43).
- [ ] **F2** · data · Etapa 1 (EE. UU.): Bauer-Swanson (la elección de la vintage es de los autores), Z.1, BIS DSR, SLOOS y EBP en `data/clean` con diccionario. Hecho: MANIFEST + comprobación de cobertura trimestral.
- [ ] **F3** · scientific-director + coordination · Borrador del bloque ```prereg``` con el signo esperado por estado, derivado de F1. Hecho: cada predicción con la ecuación de la que sale. **Lo aprueban los autores.**
- [ ] **F4** · econometrics · `mc-validate` del estimador de la etapa 1 (LP con un estado, subida/bajada) con el T real. Hecho: cobertura en [0,92; 0,98] y potencia.
- [ ] **F5** · data + econometrics · Puerta de la etapa 2 (zona euro): disponibilidad de los MIR de saldos vivos y de la inversión trimestral por país; exposición contractual × stock; MC de potencia con 10–12 clústeres. Hecho: informe de puerta (pasa / no pasa).
- [ ] **0.3b** · referee · Auditoría del resultado de `modelshock` (LP con shocks JK, interacción a h = 4–8). Útil antes de F5.

## Independientes del diseño (se pueden hacer ya)
- [x] **A2** · theory · Check SymPy de la convexidad de δ en v22: 4/4 en verde, error confirmado.
- [ ] **A1** · referee · Auditoría independiente de v22 (confirma o refuta `prior/diagnosis_v22.md`). Útil para que la Fase 0 no repita errores.
