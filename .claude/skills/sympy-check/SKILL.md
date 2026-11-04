---
name: sympy-check
description: Verifica una derivación, una proposición, un signo o un umbral con SymPy en tres capas (simbólica, numérica y de signo con test negativo). Úsalo antes de que cualquier resultado teórico entre en un paper.
---

Regla de CLAUDE.md: una proposición sin verificación simbólica no entra en el paper.
Herramienta: `tools/symcheck.py` (con tests en `tools/test_symcheck_mc.py`).

1. **Un archivo por resultado:** `papers/<slug>/theory/check_<nombre>.py`. pytest lo recoge solo
   (`check_*.py`). Cada afirmación del paper es un `test_*`.
2. **Declara los supuestos en los símbolos** (`positive=True`, etc.) y el dominio relevante como `box`
   (p. ej., el rango muestral de la variable y el de la calibración). Un resultado sin dominio no se verifica.
3. **Tres capas obligatorias:**
   - `check_identity(derivada, forma_cerrada_afirmada, box)`: igualdad simbólica **y** numérica.
   - `check_sign(expr, "+"|"-", box)`: el signo afirmado se cumple en todo el dominio muestreado.
   - **Test negativo:** un `pytest.raises(ClaimFailed)` sobre la afirmación contraria. Si la contraria
     también "pasa", el check no prueba nada.
4. **Cifras derivadas** (umbrales, valores en la calibración): calcúlalas en el check y compáralas con la
   cifra del texto (`abs(valor - texto) < tolerancia`). Así se cazan errores como el D* ≈ 0,04 de v22, que
   en realidad es 0,43.
5. **Ecuaciones de otros papers:** cópialas del PDF (con su página) y nunca del `.md` de la biblioteca, que
   puede dañar las fórmulas.

Ejemplo completo: `tools/test_symcheck_mc.py` (convexidad de la absorción de deuda de v22).
Comprueba al final: `uv run pytest papers/<slug>/theory`.
