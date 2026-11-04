"""Verificación de derivaciones en tres capas (skill sympy-check).

1. Simbólica: la expresión afirmada es idéntica a la derivada (simplify de la diferencia = 0).
2. Numérica: coincide en puntos aleatorios del dominio (atrapa simplificaciones engañosas de SymPy).
3. Signo/desigualdad: se cumple en todo el dominio muestreado **y no de forma vacía** (la afirmación
   contraria tiene que fallar; si la expresión es 0 o NaN en casi todo el dominio, el check no prueba nada).
"""

from __future__ import annotations

import numpy as np
import sympy as sp


class ClaimFailed(AssertionError):
    """La afirmación matemática no se sostiene."""


def _sample(free: list[sp.Symbol], box: dict[sp.Symbol, tuple[float, float]], n: int, seed: int):
    missing = set(free) - set(box)
    if missing:
        raise ValueError(f"faltan rangos para {sorted(map(str, missing))}")
    rng = np.random.default_rng(seed)
    return {s: rng.uniform(*box[s], size=n) for s in free}


def check_identity(derived: sp.Expr, claimed: sp.Expr, box: dict, n: int = 500, seed: int = 0,
                   rtol: float = 1e-9) -> None:
    """Capas 1 y 2: `claimed` es la misma función que `derived` en el dominio `box`."""
    if sp.simplify(derived - claimed) != 0:
        diff = sp.simplify(derived - claimed)
        raise ClaimFailed(f"simbólicamente distintas: diferencia = {diff}")
    free = sorted((derived - claimed).free_symbols | derived.free_symbols | claimed.free_symbols, key=str)
    pts = _sample(free, box, n, seed)
    f, g = (sp.lambdify(free, e, "numpy") for e in (derived, claimed))
    a, b = np.broadcast_to(f(*pts.values()), n), np.broadcast_to(g(*pts.values()), n)
    if not np.allclose(a, b, rtol=rtol, atol=rtol):
        raise ClaimFailed("coinciden simbólicamente pero no numéricamente: revisa supuestos/dominio")


def check_sign(expr: sp.Expr, sign: str, box: dict, n: int = 2000, seed: int = 0,
               min_informative: float = 0.99) -> None:
    """Capa 3: `expr` tiene signo `sign` ('+' o '-') en todo `box`, y la afirmación no es vacía."""
    if sign not in {"+", "-"}:
        raise ValueError("sign debe ser '+' o '-'")
    free = sorted(expr.free_symbols, key=str)
    vals = np.broadcast_to(sp.lambdify(free, expr, "numpy")(*_sample(free, box, n, seed).values()), n)
    informative = np.isfinite(vals) & (vals != 0)
    if informative.mean() < min_informative:
        raise ClaimFailed(f"check vacío: solo {informative.mean():.0%} de puntos finitos y no nulos")
    ok = vals[informative] > 0 if sign == "+" else vals[informative] < 0
    if not ok.all():
        bad = (~ok).mean()
        raise ClaimFailed(f"el signo '{sign}' falla en el {bad:.1%} del dominio muestreado")
