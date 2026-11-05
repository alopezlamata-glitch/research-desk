# Eval del Referee — TASKS

Cada tarea es un commit atómico y se cierra con `uv run ruff check .` y `uv run pytest` en verde.

- [x] **RE1** · `grade.py` + tests con informes sintéticos (detecta / no detecta / evidencia fuera de rango /
  `any_line` / veredicto / falso positivo en C0 / informe sin formato válido). Sin sesiones de Claude.
- [x] **RE2** · Base `p07-credit`: DGP, LP, replicación R, check de SymPy, Monte Carlo, macros y `main.tex`, todo
  generado por código. Hecho: el repo temporal construido con la base pasa `integrity.py` y `pytest`.
- [ ] **RE3** · `build.py` + test: construye la base y cada caso en un temporal con un commit, sin `evals/` ni
  `case.yaml` dentro; el `marker` de cada ubicación está en su rango de líneas.
- [ ] **RE4** · Casos C1–C6 (overlay + `case.yaml`). Hecho: cada caso sigue pasando `integrity.py` (el error no
  lo detecta un check determinista) y el test de `marker` pasa.
- [ ] **RE5** · `run.py` con `--dry-run` (un ejecutable falso en lugar de `claude`) + test del flujo completo:
  construir, lanzar, recoger informe y transcripción, puntuar y escribir `RESULTS.csv`. Respeta `desk.active()`.
- [ ] **RE6** · Línea base dev (C0, C1, C3, C4; 1 rep, Opus). Entregable: filas en `RESULTS.csv` y una nota con
  coste medido y falsos positivos para que los autores los revisen. **Requiere el visto bueno de los autores** (gasta
  cuota de la suscripción).
- [ ] **RE7** · Línea base val (C0, C2, C5, C6; 1 rep). Mismo visto bueno.
- [ ] **RE8** · Regla de uso en `CLAUDE.md` y en `.claude/agents/referee.md`: cambios al Referee se evalúan con val
  antes y después; criterio duro de la SPEC. Número de repeticiones fijado con el coste medido en RE6–RE7.
