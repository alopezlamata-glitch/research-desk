# Encargo de la Coordinación a Teoría — 2026-11-04 · Dos tests que exige el prerregistro

Modelo: sonnet

Rutas relativas a la raíz del repo (`../../`). Contexto: `papers/p01-liquidity/exploration/PREREG_DRAFT.md` §2, "Pendiente de Teoría".
Usa `tools/symcheck.py` (`check_sign`, `check_identity`) y añade los tests a los scripts existentes de `papers/p01-liquidity/theory/`.

1. En `check_aggregation.py`: `L_u > 0` siempre que g_j ≥ 0 y ω_j ≥ ω_min > 0 (con p_f, a_j, s_j, φ > 0). Incluye un test negativo:
   con algún g_j < 0 suficientemente grande, la afirmación falla.
2. En `check_nesting.py`: `∂I_u/∂g = 1 − ω` (identidad) y su signo: > 0 con B > 0 (restricción activa) y = 0 en el límite sin restricción (B → 0).

Cada test con su negativo, igual que los demás. Añade una línea por test en `theory/VERIFICACIONES_2026-11-04.md` §4, como addendum fechado.
Comprueba que `uv run pytest papers/p01-liquidity/theory` pasa. No hagas commit. Lecciones solo si aprendes algo nuevo.
