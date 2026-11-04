"""Ejecuta todos los fetch. Uso: uv run python datalake/fetch/update_all.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import fred
import narrative
import panel
import shocks
import us_misc

for m in (fred, shocks, narrative, us_misc, panel):
    print(f"=== {m.__name__} ===")
    m.main()
