"""Sustituto de `claude` para `run.py --dry-run`: hace lo que el runner espera de una sesión del Referee, sin modelo.

Escribe en la carpeta de trabajo (audits/) un informe con un hallazgo mayor sobre draft/main.tex:34 y un script en
replication_<fecha>/, y en $CLAUDE_CONFIG_DIR/projects/ una transcripción con las ejecuciones de integrity.py y pytest
y el consumo de tokens. Guarda sus argumentos en $CLAUDE_CONFIG_DIR/last_args.json para los tests.
"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPORT = """---
verdict: RECHAZADO
object: LP h = 1 del borrador
date: 2026-11-05
commit: {commit}
reviewer: referee
session: fresh
---
## Resumen
Ensayo en seco del runner.

## Hallazgos
### La cifra principal del texto no sale de estimates_py.csv — mayor
Evidencia: ../draft/main.tex:34 y `uv run python ../../../tools/integrity.py`

### Estilo de la tabla — menor
Evidencia: ../draft/main.tex:45

## Replicación
Script propio en audits/replication_2026-11-05/.
"""


def main(argv: list[str]) -> int:
    sid = argv[argv.index("--session-id") + 1]
    config = Path(os.environ["CLAUDE_CONFIG_DIR"])
    config.mkdir(parents=True, exist_ok=True)
    (config / "last_args.json").write_text(json.dumps(argv), encoding="utf-8")
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                            check=True).stdout.strip()
    audits = Path.cwd()
    (audits / "2026-11-05_lp-h1.md").write_text(REPORT.format(commit=commit), encoding="utf-8")
    (audits / "replication_2026-11-05").mkdir(exist_ok=True)
    (audits / "replication_2026-11-05" / "rep.py").write_text("print('replica')\n", encoding="utf-8")
    t0 = datetime(2026, 11, 5, 10, 0, tzinfo=UTC)
    usage = {"input_tokens": 10, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 5000,
             "output_tokens": 200}
    entries = [{"type": "assistant", "timestamp": (t0 + timedelta(minutes=i)).isoformat(),
                "message": {"id": f"m{i}", "usage": usage,
                            "content": [{"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}
               for i, cmd in enumerate(["uv run python ../../../tools/integrity.py", "uv run pytest -q"])]
    transcript = config / "projects" / "fake-project" / f"{sid}.jsonl"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text("\n".join(map(json.dumps, entries)) + "\n", encoding="utf-8")
    print(json.dumps({"type": "result", "subtype": "success", "session_id": sid, "result": "Informe escrito."}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
