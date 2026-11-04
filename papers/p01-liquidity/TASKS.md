# p01 — TASKS

Estado: `[ ]` pendiente · `[~]` en curso · `[x]` hecha · `[!]` bloqueada.
Cada tarea tiene desk, criterio de "hecho" y su propio commit.

## Fase 0: exploración
- [x] **0.1** · coordination · Inventario de iteraciones previas (2026-11-04): 57 archivos únicos archivados en `prior/archive/` (fuera de git); cronología, líneas, errores y lo que se salva en `exploration/INVENTORY.md`.
- [x] **0.1b** · literature · Literatura del paper buscada en repositorios a partir de las bibliografías de TFG1, TFG2, `Policy_Confidence_Coherence` y v22 (los autores indican que las líneas más relevantes son las de TFG1 y TFG2). Encargo: `desks/literatura/ENCARGO_2026-11-04.md`; sesión lanzada el 2026-11-04 (incluye también la 0.2). Resultado (2026-11-04): ~85 entradas en `paper/references.bib`; ~8 discrepancias graves, `exploration/LITERATURE_REPORT.md`. Parcial: v22 no extraída (solo refs del README) y ~25 clásicos sin comprobar.
- [x] **0.2** · literature · Fichas de la literatura + mapa en `kb/topics/`. Hecho: una ficha por paper relevante; ninguna cita sin verificar. Resultado (2026-11-04): mapa en `kb/topics/policy-transmission/README.md` y 12 fichas en `papers/` (basadas en resúmenes/registros, texto completo sin leer); las citas sin verificar quedan marcadas NO VERIFICADA en el bib, no eliminadas.
- [x] **0.4–0.8** · Sustituidas el 2026-11-04 por `exploration/FIRST_PRINCIPLES.md` + el abogado del diablo (`exploration/DEVILS_ADVOCATE_2026-11-04.md`, rúbrica con 6 diseños). Los autores aprueban el **diseño F** (ver Desviaciones de la SPEC). 0.3 (fichas de descartadas) no se hace: lo salvable ya está en INVENTORY y FIRST_PRINCIPLES.

## Diseño F
- [x] **F1** · theory · `check_nesting.py`, `check_aggregation.py` (banco común) y `check_coordination.py` + `theory/VERIFICACIONES_2026-11-04.md`. Resultado (2026-11-04): 43 tests en verde. Confirma el informe salvo la agregación con reserva ajustable, que corrige: `L_u = (Ḡ+Θp_f)/(1+φΘ)`. Resultados nuevos: ω ≥ ω_min = γ²a/(κ_F+γ²a), y no hay cota de la coordinación independiente de la calibración. Pendiente: que Literatura confirme IOPO pp. 10–11 con el PDF.
- [x] **F2** · data · Etapa 1 (EE. UU.): Bauer-Swanson (la elección de la vintage es de los autores), Z.1, BIS DSR, SLOOS y EBP en `data/clean` con diccionario. Hecho: MANIFEST + comprobación de cobertura trimestral. Resultado (2026-11-04): `data/clean/stage1_us.parquet` (1985Q1–2026Q4, 46 variables) + `DICTIONARY.md` + `coverage.csv`; scripts `code/data/{download,build,plot}_stage1_us.py`, 10 tests en verde; ambas vintages de Bauer-Swanson con identificador propio (ρ trimestral ME–MPS_ORTH ≈ 0,66: decisión de los autores). **Avisos:** `inv_nonres_real` (PNFIC1) solo desde 2007Q1 en el lago; Z.1 no trae deuda a tipo variable/corto plazo; Z.1 acaba en 2026Q2, DSR en 2026Q1; `mps_bs23_orth` NaN en 2020.
- [ ] **F2b** · data · Sustituir `PNFIC1` (desde 2007 en FRED) por el índice de cantidad `A008RA3Q086SBEA` (inversión no residencial real, 1947–2026Q3, comprobado en FRED el 2026-11-04) como variable principal de inversión.
- [ ] **F3** · scientific-director + coordination · Borrador del bloque ```prereg``` con el signo esperado por estado, derivado de F1. Hecho: cada predicción con la ecuación de la que sale. **Lo aprueban los autores.**
- [ ] **F4** · econometrics · `mc-validate` del estimador de la etapa 1 (LP con un estado, subida/bajada) con el T real. Hecho: cobertura en [0,92; 0,98] y potencia.
- [ ] **F5** · data + econometrics · Puerta de la etapa 2 (zona euro): disponibilidad de los MIR de saldos vivos y de la inversión trimestral por país; exposición contractual × stock; MC de potencia con 10–12 clústeres. Hecho: informe de puerta (pasa / no pasa).
- [ ] **0.3b** · referee · Auditoría del resultado de `modelshock` (LP con shocks JK, interacción a h = 4–8). Útil antes de F5.

## Independientes del diseño (se pueden hacer ya)
- [x] **A2** · theory · Check SymPy de la convexidad de δ en v22: 4/4 en verde, error confirmado.
- [ ] **A1** · referee · Auditoría independiente de v22 (confirma o refuta `prior/diagnosis_v22.md`). Útil para que la Fase 0 no repita errores.
