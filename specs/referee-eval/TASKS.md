# Eval del Referee — TASKS

Cada tarea es un commit atómico y se cierra con `uv run ruff check .` y `uv run pytest` en verde.

- [x] **RE1** · `grade.py` + tests con informes sintéticos (detecta / no detecta / evidencia fuera de rango /
  `any_line` / veredicto / falso positivo en C0 / informe sin formato válido). Sin sesiones de Claude.
- [x] **RE2** · Base `p07-credit`: DGP, LP, replicación R, check de SymPy, Monte Carlo, macros y `main.tex`, todo
  generado por código. Hecho: el repo temporal construido con la base pasa `integrity.py` y `pytest`.
- [x] **RE3** · `build.py` + test: construye la base y cada caso en un temporal con un commit, sin `evals/` ni
  `case.yaml` dentro; el `marker` de cada ubicación está en su rango de líneas.
- [x] **RE4** · Casos C1–C6 (overlay + `case.yaml`). Hecho: cada caso sigue pasando `integrity.py` (el error no
  lo detecta un check determinista) y el test de `marker` pasa.
- [x] **RE5** · `run.py` con `--dry-run` (un ejecutable falso en lugar de `claude`) + test del flujo completo:
  construir, lanzar, recoger informe y transcripción, puntuar y escribir `RESULTS.csv`. Respeta `desk.active()`.
- [ ] **RE6** · Línea base dev (C0, C1, C3, C4; 1 rep, Opus). Entregable: filas en `RESULTS.csv` y una nota con
  coste medido y falsos positivos para que los autores los revisen. **Requiere el visto bueno de los autores** (gasta
  cuota de la suscripción).
- [ ] **RE7** · Línea base val (C0, C2, C5, C6; 1 rep). Mismo visto bueno.
- [ ] **RE8** · Regla de uso en `CLAUDE.md` y en `.claude/agents/referee.md`: cambios al Referee se evalúan con val
  antes y después; criterio duro de la SPEC. Número de repeticiones fijado con el coste medido en RE6–RE7.

## Notas de implementación (2026-11-05, para revisión de los autores)
- **Dos commits, no uno.** El check `prereg` exige `prereg_commit: <sha>` de un commit que ya contenga el SPEC, así
  que el repo temporal tiene el commit del prerregistro (autor y fecha fijos: mismo hash en todas las construcciones)
  y el del trabajo. Los mensajes son neutros.
- **El borrador está en `draft/main.tex`, no en `paper/main.tex`.** El check `gate` impide que un `.tex` de `paper/`
  use `output/` sin un APROBADO previo: con el borrador en `paper/` la base no pasaría `integrity.py` antes de la
  auditoría. Los tests aplican igualmente al borrador los checks de cifras y citas.
- **Inferencia de la base (rehecha el 2026-11-05 con datos reales):** LP con «lag augmentation» (6 retardos de todas
  las variables, choque incluido) y errores HC3; la cobertura del Monte Carlo calibrado es 0,948/0,946 con T = 359. Con
  White (HC0) cae a 0,905/0,887 por las colas gruesas del choque: es el error de C6.
- **Salidas generadas:** `build.py regen <caso>` ejecuta el pipeline (descarga desde el datalake, Python, R y Monte
  Carlo) en un repo temporal y trae `data/raw/MANIFEST.csv`, `data/clean` y `output/` a la base o al overlay; un caso con `regen: false` (C4) conserva salidas de otro run.
- El repo temporal incluye `CLAUDE.md` y `.claude/settings.json` (el hook): el Referee se evalúa con el contexto con
  el que trabaja de verdad.
- **Casos (RE4, rehechos el 2026-11-05 sobre datos reales):** cada `case.yaml` describe el error y sus ubicaciones. Con
  datos reales la interacción no es significativa en ninguna variante razonable (estados, choques, muestras), así que
  C5 planta la exploración que sí da un resultado: otras variables de actividad, de las que solo las viviendas
  iniciadas (efecto lineal) salen significativas, presentadas como prerregistradas. En C2, el Monte Carlo del autor
  simula `fci` como exógeno (si incluyera el choque, la cobertura caería y el caso arrastraría el error de C6).
  C4 conserva un `macros.tex` del run con la muestra hasta 2016-12. El Monte Carlo usa 1000 réplicas.
- **Runner (RE5):** `run.py` lanza al Referee en `audits/` con los argumentos de `desk._start` más `--add-dir <repo>`
  (las desks lo tienen en `additionalDirectories`) y `--output-format json`, y ocupa el puesto de la desk `referee`
  (`desk.check_can_launch`) mientras dura. `--dry-run` usa `fake_claude.py`, desks y configuración temporales y escribe
  en `%TEMP%/referee-eval/RESULTS_dry-run.csv`.
- **Pendiente de comprobar en RE6** (no se puede sin una sesión real): que la sesión lanzada en `audits/` lee el repo con
  `--add-dir` sin pedir permisos, y si carga el hook `guard.js`, porque `.claude/settings.json` está en la raíz y no en
  `audits/`. Esto vale también para las auditorías reales que se lanzan desde `papers/<slug>/audits/`.
