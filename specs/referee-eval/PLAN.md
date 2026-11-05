# Eval del Referee — PLAN

## Estructura
```
evals/referee/
  base/                  mini-paper completo (árbol del repo temporal, sin infraestructura)
    papers/p07-credit/   SPEC, data/clean, code/, theory/, output/, paper/, audits/.gitkeep
    KNOWN_ISSUES.yaml    problemas reales de la base aceptados por los autores (empieza vacío)
  cases/<Cn>/
    overlay/             archivos que sustituyen a los de la base (mismo árbol)
    case.yaml            id, set (dev|val), descripción, ubicaciones [{file, lines, marker, any_line}],
                         verdicts aceptados
  build.py               base + overlay + infraestructura → repo temporal con un commit
  grade.py               informe + transcripción + case.yaml → puntuación (función pura)
  run.py                 [--set dev|val] [--case Cn] [--reps N] [--model opus] [--dry-run]
  RESULTS.csv            fecha, commit del repo real, caso, rep, modelo, veredicto, detectado, falsos
                         positivos, protocolo, tokens, minutos, session_id
  test_*.py              tests de grade, build y casos (sin sesiones de Claude)
```

## Decisiones
| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| Repo temporal en `%TEMP%` con un único commit | Rama o carpeta dentro del repo real | La clave de respuestas y el historial quedan fuera del alcance del Referee; nada se sincroniza por OneDrive |
| Reusar de `desk.py`: `TOOLS`, `builtin_tools`, `LEAN_CONTEXT`, `active`, `session_usage` | Un lanzador propio | La eval mide al Referee tal como se lanza de verdad; si cambia `desk.py`, la eval lo sigue |
| Ejecución síncrona (`subprocess.run`, `--output-format json`) | `spawn_detached` | El runner espera al resultado para puntuarlo; una sesión de eval no tiene que sobrevivir a la sesión que la lanza |
| `UV_PROJECT_ENVIRONMENT` apuntando al `.venv` del repo real | `uv sync` en cada repo temporal | Evita crear un entorno por caso; `pyproject.toml` y `uv.lock` se copian idénticos |
| Ubicación + `marker` en `case.yaml` | Solo número de línea | Si se edita la base, un test falla en vez de puntuar contra una línea que ya no es la del error |
| Puntuación determinista | Juez LLM | Reproducible, gratis y sin un segundo modelo que también se equivoque |
| Slug `p07-credit` y tema distinto de p01 | Reusar p01 | El Referee no reconoce el material; no contamina el paper real |

## Contenido de la base (para que los errores plantados sean plausibles)
- **DGP** (`code/data/simulate.py`, semilla fija): inversión trimestral, choque monetario, estado de crédito
  observado, controles; N = 120. Genera `data/clean/panel.parquet` y su diccionario. Los datos se generan con código;
  no hay `raw/` (no hace falta `rawhash`).
- **Estimación** (`code/analysis/lp.py`): LP h = 0..4 con interacción choque × estado, NW(5), `research.log_spec`,
  `estimates_py.csv`, `macros.tex`.
- **Replicación R** (`code/replication_r/lp.R`, `fixest`): `estimates_r.csv` con paridad.
- **Teoría** (`theory/check_sign.py`): una derivada con el signo de la predicción, en tres capas (`sympy-check`).
- **Monte Carlo** (`code/mc/mc_lp.py` + `output/MC_REPORT.md`): sesgo, cobertura y potencia con `tools/mc.py`.
- **Texto** (`paper/main.tex`): ~1 página con la pregunta, la proposición, la tabla y la conclusión, todo con macros.
- Coste objetivo de una sesión: muy por debajo de una auditoría real (la base es pequeña); se medirá.

## Riesgos
- **Coste:** 4 casos × 1 rep para la línea base dev ≈ 4 sesiones de Opus. Val con 3 reps son 12. Se mide en la
  línea base y se ajusta antes de fijar la regla de uso.
- **Base con errores no intencionados:** el control C0 lo revela; se resuelven con los autores (KNOWN_ISSUES o arreglo).
- **Deriva de la infraestructura:** el repo temporal copia las versiones actuales de rol, skills y tools; la fila de
  `RESULTS.csv` guarda el commit del repo real para saber qué versión se evaluó.
- **R en la eval:** si `Rscript` no está, la replicación del Referee falla; `run.py` lo comprueba antes de lanzar.
