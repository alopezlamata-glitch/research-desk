"""Proposición 1 de draft/main.tex: la inversión cae más ante una subida del tipo cuando el crédito está restringido.

Empresa: max_k A k^α − c k, con coste del capital c = r(1 + m s) + δ (prima de financiación externa proporcional al tipo
y al diferencial de crédito s ≥ 0, en pp). Capital óptimo k* = (αA / c)^{1/(1−α)}. Con una prima aditiva el signo se
invierte (último test): la Proposición depende de ese supuesto (SPEC, «Teoría»).
"""

import pytest
import sympy as sp
from symcheck import ClaimFailed, check_identity, check_sign

alpha, A, r, m, s, delta = sp.symbols("alpha A r m s delta", positive=True)
cost = r * (1 + m * s) + delta
log_k = (sp.log(alpha * A) - sp.log(cost)) / (1 - alpha)
BOX = {alpha: (0.2, 0.4), A: (0.5, 2.0), r: (0.005, 0.08), m: (0.1, 1.0), s: (0.0, 6.0), delta: (0.02, 0.1)}

d_r = sp.diff(log_k, r)
cross = sp.diff(log_k, r, s)
CLAIMED_D_R = -(1 + m * s) / ((1 - alpha) * cost)
CLAIMED_CROSS = -m * delta / ((1 - alpha) * cost**2)


def test_capital_is_the_first_order_condition_solution():
    """Condición de primer orden en logs: log(αA k^{α−1}) = log c en k = k*."""
    check_identity(sp.log(alpha * A) + (alpha - 1) * log_k, sp.log(cost), BOX)


def test_rate_semi_elasticity():
    check_identity(d_r, CLAIMED_D_R, BOX)
    check_sign(d_r, "-", BOX)


def test_proposition_1_cross_partial_is_negative():
    check_identity(cross, CLAIMED_CROSS, BOX)
    check_sign(cross, "-", BOX)


def test_proposition_1_opposite_sign_fails():
    with pytest.raises(ClaimFailed):
        check_sign(cross, "+", BOX)


def test_with_an_additive_premium_the_sign_flips():
    additive = sp.diff((sp.log(alpha * A) - sp.log(r + m * s + delta)) / (1 - alpha), r, s)
    check_identity(additive, m / ((1 - alpha) * (r + m * s + delta) ** 2), BOX)
    check_sign(additive, "+", BOX)
