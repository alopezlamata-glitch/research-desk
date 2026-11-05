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
- [ ] **RE5** · `run.py` con `--dry-run` (un ejecutable falso en lugar de `claude`) + test del flujo completo:
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
- **Inferencia de la base:** NW con h + 1 retardos sobre residuos HC3 y H1 en h = 1. Con NW(5) y residuos MCO la
  cobertura del Monte Carlo (T = 120) caía a 0,86–0,90 en h = 4, y la base ya contenía el error de C6.
- **Salidas generadas:** `build.py regen <caso>` ejecuta el pipeline (Python, R y Monte Carlo) en un repo temporal y
  trae `data/clean` y `output/` a la base o al overlay; un caso con `regen: false` (C4) conserva salidas de otro run.
- El repo temporal incluye `CLAUDE.md` y `.claude/settings.json` (el hook): el Referee se evalúa con el contexto con
  el que trabaja de verdad.
- **Casos (RE4):** cada `case.yaml` describe el error y sus ubicaciones. Para que cada caso tenga un único error, el DGP
  de la base no hace depender la inversión de los diferenciales (si lo hiciera, el control contaminado de C2 sesga b y
  el Monte Carlo de C2 falla, que es el error de C6) y `fci` promedia cuatro componentes. C5 vive en su propio mundo
  (γ = −0,15, semilla 20261165, elegida para que el cuantil 0,75 sea la única de cuatro variantes significativa: es el
  jardín de senderos que el caso planta). C4 conserva un `macros.tex` del run con la muestra hasta 2019T4.
  El Monte Carlo usa 1000 réplicas (500 dejaba la cobertura de la base en el borde de la banda por puro ruido).
