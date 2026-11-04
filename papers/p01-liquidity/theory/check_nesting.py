"""Casos límite de la respuesta ponderada de TFG2 (Prop. fs-transmission, l. 342-356 y 650-657).

    I_u = w p_f/a + (1-w) g,   w = gamma^2 a / (B + gamma^2 a),   B = kappa_F Q(z_F)

Se deriva de las condiciones KKT (TFG2 ec. fs-kkt) y se comprueba qué casos límite recupera:
sin restricción (B->0), TFG1 (min{}: B->inf con g=0), IOPO 2018 p. 11 eq. 7 (B->inf, g = L0) y qué
parte de ese rango es alcanzable con B = kappa_F Q(z_F) (TFG2 l. 283).
Ejecutar: uv run python papers/p01-liquidity/theory/check_nesting.py
"""

import sys
from pathlib import Path

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import symcheck as sc

p_f, gam, a, B, g, kap, z = sp.symbols("p_f gamma a B g kappa z", positive=True)
I_u, m_u, lam_u = sp.symbols("I_u m_u lambda_u")
Q = sp.erfc(z / sp.sqrt(2)) / 2  # cola superior de la normal estándar


def _derive():
    """Diferencia las KKT (lambda=q-aI; kappa G(m)=delta+gamma lambda; I+gamma m=H) respecto de u.

    G' = -Q, así que kappa G' = -B. Con q_u = p_f, H_u = g y a, sigma_F, delta fijos:
    """
    eqs = [lam_u - (p_f - a * I_u), -B * m_u - gam * lam_u, I_u + gam * m_u - g]
    return sp.solve(eqs, [I_u, m_u, lam_u], dict=True)[0]


SOL = _derive()
W = gam**2 * a / (B + gam**2 * a)
CLAIMED = (gam**2 * p_f + B * g) / (B + gam**2 * a)  # TFG2 ec. fs-transmission
BOX = {p_f: (0.5, 2), gam: (0.5, 2), a: (0.1, 0.5), B: (0.01, 3), g: (0, 6)}


def test_transmission_formula_from_kkt():
    sc.check_identity(SOL[I_u], CLAIMED, BOX)


def test_weighted_form():
    sc.check_identity(SOL[I_u], W * p_f / a + (1 - W) * g, BOX)


def test_buffer_and_multiplier_formulas():
    sc.check_identity(SOL[m_u], gam * (a * g - p_f) / (B + gam**2 * a), BOX)  # fs-buffer-transmission
    sc.check_identity(SOL[lam_u], B * (p_f - a * g) / (B + gam**2 * a), BOX)


def test_negative_wrong_weight_is_rejected():
    wrong = (gam * p_f + B * g) / (B + gam * a)  # sin el cuadrado de gamma
    with pytest.raises(sc.ClaimFailed):
        sc.check_identity(SOL[I_u], wrong, BOX)


def test_unconstrained_limit():
    """B->0 (reserva sin coste marginal): I_u = p_f/a, el caso sin restricción."""
    assert sp.simplify(sp.limit(SOL[I_u], B, 0, "+") - p_f / a) == 0


def test_rigid_limit_B_to_infinity_is_g():
    """B->inf: I_u = g. Con g=0 es el cero de TFG1; con g=gamma*E_D es IOPO."""
    assert sp.simplify(sp.limit(SOL[I_u], B, sp.oo) - g) == 0


def test_tfg1_minimum_branches():
    """TFG1: I* = min{H, q/a}. Rama holgada: derivada p_f/a (= B->0). Rama con tope H(D): derivada
    H_u = g, que TFG1 fija en 0 (H no depende de u). El kink separa las dos."""
    u, q0, H0, aa = sp.symbols("u q0 H0 aa", positive=True)
    slack, bind = (q0 + p_f * u) / aa, H0 + g * u
    assert sp.diff(slack, u) == p_f / aa and sp.diff(bind, u) == g
    assert sp.limit(SOL[I_u], B, sp.oo).subs(g, 0) == 0  # el min{} de TFG1 es B->inf con g=0
    assert SOL[I_u].subs({g: 0, B: 1, gam: 1, p_f: 1, a: sp.Rational(171, 1000)}) != 0  # negativo: B finito


def test_iopo_2018_eq7_is_rigid_limit_with_full_repricing():
    """IOPO p. 11 eq. 7: restringida => K1 = N1 + b; N1 = f(K0) - r_c B0 - r1 L0 (p. 10 eq. 2).
    Con u = -dr1 (relajación), dK1/du = L0. En TFG2: g = gamma E_D con E_D = -dJ_F/du; con deuda
    toda flotante a r1, J_F = r1 L0 y E_D = L0; gamma = 1 (TFG2 l. 1690-1694)."""
    r1, L0, r_c, B0, b_bar, f_K0, u = sp.symbols("r1 L0 r_c B0 b_bar f_K0 u")
    N1 = f_K0 - r_c * B0 - (r1 - u) * L0  # r1 baja u
    K1 = N1 + b_bar
    iopo = sp.diff(K1, u)
    E_D = -sp.diff((r1 - u) * L0, u)  # J_F = (r1-u) L0 -> E_D = -dJ_F/du = L0
    assert sp.simplify(iopo - L0) == 0 and sp.simplify(E_D - L0) == 0
    rigid = sp.limit(SOL[I_u].subs(g, gam * E_D), B, sp.oo)
    sc.check_identity(rigid.subs(gam, 1), iopo, {L0: (0.1, 5)})
    with pytest.raises(sc.ClaimFailed):  # negativo: con reserva ajustable IOPO ya no es exacto
        sc.check_identity(SOL[I_u].subs({gam: 1, g: L0}), iopo, {**BOX, L0: (0.1, 5)})


def test_fixed_buffer_corner_gives_g_exactly():
    """Con m fijo (cota m=0 o buffer fijo), I = H - gamma m_bar => I_u = H_u = g, sin pasar por B->inf."""
    H0, m_bar, u = sp.symbols("H0 m_bar u")
    assert sp.diff(H0 + g * u - gam * m_bar, u) == g


# ---------------------------------------------------------------- alcanzabilidad con B = kappa_F Q(z_F)
q = sp.Symbol("q", positive=True)  # q = Q(z_F) en (0,1): Q es estrictamente decreciente con límites 1 y 0
B_REACH = kap * q
BOX_Z = {kap: (0.2, 5), q: (1e-6, 1 - 1e-6), a: (0.1, 0.5), gam: (0.5, 2), p_f: (0.5, 2), g: (0, 6)}


def test_Q_is_strictly_decreasing_onto_open_unit_interval():
    assert sp.limit(Q, z, -sp.oo) == 1 and sp.limit(Q, z, sp.oo) == 0
    sc.check_sign(sp.diff(Q, z) * sp.exp(z**2 / 2), "-", {z: (-8, 8)})  # Q' = -phi(z) < 0


def test_B_is_in_open_interval_zero_kappa():
    sc.check_sign(B_REACH, "+", BOX_Z)
    sc.check_sign(kap - B_REACH, "+", BOX_Z)  # Q<1: B nunca llega a kappa_F, y menos a infinito
    with pytest.raises(sc.ClaimFailed):  # negativo: B no supera kappa_F
        sc.check_sign(B_REACH - kap, "+", BOX_Z)


def test_weight_is_bounded_below_by_w_min():
    """w >= w_min = gamma^2 a/(kappa_F + gamma^2 a) > 0: el rígido (w=0) no se alcanza con kappa_F finito."""
    w_min = gam**2 * a / (kap + gam**2 * a)
    sc.check_sign((W - w_min).subs(B, B_REACH), "+", BOX_Z)
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign((W - w_min / 2).subs(B, B_REACH) * -1, "+", BOX_Z)


def test_minimum_transmission_with_g0_at_tfg2_calibration():
    """Calibración TFG2 (l. 1690-1694): b=eta=0.1, psi/N=0.05, kappa_F=gamma=1, v=0.21 (A_P=2)
    => a=0.171, p_f=1. Con g=0, I_u >= w_min p_f/a = 0.146 * 5.848 = 0.854, no 0."""
    aval = sp.Rational(1, 10) + sp.Rational(1, 10) * sp.Rational(21, 100) + sp.Rational(5, 100)
    assert aval == sp.Rational(171, 1000)
    w_min = float((gam**2 * a / (kap + gam**2 * a)).subs({gam: 1, kap: 1, a: aval}))
    assert abs(w_min - 0.146) < 1e-3
    assert abs(w_min / float(aval) - 0.854) < 1e-3
    # TFG2 l. 793 reporta I_u = 1.769 con g=0 (A_P=2): implica B = 1/1.769 - a ~ 0.394 en (0, kappa_F).
    B_impl = 1 / 1.769 - float(aval)
    assert 0 < B_impl < 1 and abs(B_impl - 0.394) < 1e-3
    assert abs(float(W.subs({gam: 1, a: aval, B: B_impl})) * 5.848 - 1.769) < 5e-3  # coherente con w p_f/a


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
