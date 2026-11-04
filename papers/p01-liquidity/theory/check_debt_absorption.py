"""Verifica la curvatura de la absorción de deuda de v22: delta(d) = 1 - exp(-theta * d**gamma).

v22 (ec. 34-35, Corolario 1.2) afirma que delta es convexa por encima de D* y que D* ~ 0.04.
Ejecutar: uv run pytest papers/p01-liquidity/theory/check_debt_absorption.py
"""

import sympy as sp

d, theta, gamma = sp.symbols("d theta gamma", positive=True)
delta = 1 - sp.exp(-theta * d**gamma)
d_star = ((gamma - 1) / (theta * gamma)) ** (1 / gamma)
calib = {theta: sp.log(2), gamma: sp.Rational(13, 10)}


def test_second_derivative_closed_form():
    claimed_by_us = (
        theta * gamma * sp.exp(-theta * d**gamma) * d ** (gamma - 2)
        * ((gamma - 1) - theta * gamma * d**gamma)
    )
    assert sp.simplify(sp.diff(delta, d, 2) - claimed_by_us) == 0


def test_threshold_value_at_calibration():
    value = float(d_star.subs(calib))
    assert abs(value - 0.429) < 1e-3  # v22 reporta ~0.04


def test_delta_concave_on_v22_sample_range():
    # Muestra de v22: d en [0.72, 1.56], toda por encima de D*.
    d2 = sp.lambdify(d, sp.diff(delta, d, 2).subs(calib))
    assert all(d2(x) < 0 for x in (0.72, 1.0, 1.56))


def test_te_convex_in_debt_on_sample_range():
    # TE es proporcional a (1 - delta); v22 (Corolario 1.2) afirma d2TE/dd2 < 0.
    te2 = sp.lambdify(d, sp.diff(1 - delta, d, 2).subs(calib))
    assert all(te2(x) > 0 for x in (0.72, 1.0, 1.56))
