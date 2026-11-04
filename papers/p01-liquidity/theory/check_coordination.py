"""Efecto de quitar la varianza de política sobre la transmisión (FIRST_PRINCIPLES §6.4; abogado del diablo §2.4).

Régimen interior: pendiente p_f/a, a = b + eta (v0 + v_pol) + psi/N. Régimen restringido: Prop.
`fs-coordination` (TFG2 l. 365-385), donde sigma_F entra además de v. Se comprueba:
  1. la expresión exacta del efecto interior y su valor en la calibración de TFG2 (10 % y 65 %);
  2. que no existe cota relativa independiente de la calibración (y cuál es la única cota de nivel);
  3. la derivada del Gap de la Prop. fs-coordination, y el efecto sobre I y sobre I_u con restricción activa.
Ejecutar: uv run python papers/p01-liquidity/theory/check_coordination.py
"""

import sys
from pathlib import Path

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import symcheck as sc

b, eta, v0, vp, phi, p_f = sp.symbols("b eta v_0 v_pol phi p_f", positive=True)  # phi = psi/N
BOXI = {b: (0.05, 2), eta: (0.05, 10), v0: (0, 1), vp: (0.001, 3), phi: (0.01, 1), p_f: (0.5, 2)}

# ------------------------------------------------------------ 1. régimen interior
a_with = b + eta * (v0 + vp) + phi
a_without = b + eta * v0 + phi
slope_with, slope_without = p_f / a_with, p_f / a_without
RISE = slope_without / slope_with - 1  # subida relativa de la pendiente al quitar v_pol
CLAIM_RISE = eta * vp / (b + eta * v0 + phi)
SHARE = eta * vp / a_with  # peso de la política en a (la columna "eta v_pol / a" del informe)


def test_interior_effect_closed_form():
    sc.check_identity(RISE, CLAIM_RISE, BOXI)
    with pytest.raises(sc.ClaimFailed):  # negativo: el denominador es a SIN la política, no a con ella
        sc.check_identity(RISE, SHARE, BOXI)


def test_rise_and_share_are_related():
    sc.check_identity(RISE, SHARE / (1 - SHARE), BOXI)


def _tfg2(A_P):
    """Calibración TFG2 (l. 1690-1694): b=eta=0.1, psi/N=0.05, v = 0.05 + 3^2 rho^2 0.4^2, rho=1/(1+A_P)."""
    rho = 1 / (1 + sp.nsimplify(A_P))
    vpol = 9 * rho**2 * sp.Rational(16, 100)
    sub = {b: sp.Rational(1, 10), eta: sp.Rational(1, 10), phi: sp.Rational(1, 20), v0: sp.Rational(5, 100), vp: vpol}
    return {k: sub[k] for k in sub}


def test_tfg2_calibration_numbers():
    s2, s02 = _tfg2(2), _tfg2("0.2")
    assert sp.simplify(a_with.subs(s2) - sp.Rational(171, 1000)) == 0  # a = 0.171
    assert abs(float(slope_with.subs(s2).subs(p_f, 1)) - 5.848) < 1e-3  # TFG2 l. 767/793
    assert abs(float(slope_without.subs(s2).subs(p_f, 1)) - 6.4516) < 1e-3
    assert abs(float(RISE.subs(s2)) - 0.103) < 1e-3  # informe: 10 %
    assert abs(float(RISE.subs(s02)) - 0.645) < 1e-3  # informe: 65 %
    assert abs(float(SHARE.subs(s2)) - 0.0936) < 1e-3 and abs(float(SHARE.subs(s02)) - 0.3922) < 1e-3  # 9 %, 39 %


def test_first_principles_3_percent_is_not_the_tfg2_calibration():
    fp = {b: 1, eta: 1, phi: sp.Rational(1, 2), v0: 0, vp: sp.Rational(5, 100)}  # FIRST_PRINCIPLES §6.4
    assert abs(float(RISE.subs(fp)) - 0.0333) < 1e-3  # el ~3 % es aritméticamente correcto con ESOS parámetros
    assert float(RISE.subs(_tfg2(2))) > 3 * float(RISE.subs(fp))  # pero con los de TFG2 es >3 veces mayor
    with pytest.raises(AssertionError):  # negativo: "≈3 %" no se sostiene en la calibración de TFG2
        assert abs(float(RISE.subs(_tfg2(2))) - 0.03) < 0.005


def test_no_calibration_free_relative_bound():
    """RISE = x/c con x = eta v_pol > 0 y c = b + eta v0 + psi/N > 0 libres: su cota superior es infinita."""
    x, c = sp.symbols("x c", positive=True)
    assert sp.limit(x / c, x, sp.oo) == sp.oo
    target = sp.Symbol("target", positive=True)
    x_star = sp.solve(sp.Eq(x / c, target), x)[0]  # para cada objetivo hay una calibración que lo alcanza
    sc.check_identity((x / c).subs(x, x_star), target, {target: (0.01, 100), c: (0.01, 5)})
    with pytest.raises(sc.ClaimFailed):  # negativo: ninguna cota fija (p. ej. 0,5) vale en todo el dominio
        sc.check_sign(0.5 - RISE, "+", BOXI)
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(0.03 - RISE, "+", BOXI)


def test_only_bound_is_in_level_and_depends_on_b_and_psi_over_N():
    """Ganancia en nivel de la pendiente < p_f/(b + psi/N), para cualquier (eta, v0, v_pol)."""
    gain = slope_without - slope_with
    sc.check_sign(p_f / (b + phi) - gain, "+", BOXI)
    sc.check_sign(gain, "+", BOXI)
    with pytest.raises(sc.ClaimFailed):  # negativo: no es calibration-free en b, psi/N
        sc.check_sign(p_f / (b + phi) / 100 - gain, "+", BOXI)


# ------------------------------------------------------------ 3. régimen restringido
m, mu, sig, kap, gam, dl = sp.symbols("m mu sigma kappa gamma delta", positive=True)
z_ = (m - mu) / sig
pdf = lambda t: sp.exp(-t**2 / 2) / sp.sqrt(2 * sp.pi)
Qf = lambda t: sp.erfc(t / sp.sqrt(2)) / 2
G = sig * (pdf(z_) - z_ * Qf(z_))  # E[(X - m)_+], X ~ N(mu, sig^2)  (TFG2 fs-liquidity-derivatives)


def test_vega_and_slope_of_shortfall():
    assert sp.simplify(sp.diff(G, m) + Qf(z_)) == 0  # G_m = -Q
    assert sp.simplify(sp.diff(G, sig) - pdf(z_)) == 0  # G_sigma = phi(z): el canal sigma_F


def test_gap_derivative_proposition_fs_coordination():
    """Gap = H - gam m0(sigma) - q/a, con kappa G(m0, sigma) = delta. Derivada afirmada (l. 385):
    Gap_theta = -gam kappa phi(z0)/B0 sigma_theta + (q/a^2) a_theta,  B0 = kappa Q(z0)."""
    q, a, a_th, s_th = sp.symbols("q a a_theta sigma_theta")
    m0_sig = -sp.diff(kap * G, sig) / sp.diff(kap * G, m)  # teorema de la función implícita
    gap_th = -gam * m0_sig * s_th + (q / a**2) * a_th
    claimed = -gam * kap * pdf(z_) / (kap * Qf(z_)) * s_th + (q / a**2) * a_th
    assert sp.simplify(gap_th - claimed) == 0
    wrong = gam * kap * pdf(z_) / (kap * Qf(z_)) * s_th + (q / a**2) * a_th  # signo del canal sigma cambiado
    assert sp.simplify(gap_th - wrong) != 0


# I, m, lambda con capacidad vinculante: lambda = q - aI; kappa G(m, sigma) = delta + gam lambda; I + gam m = H
I_th, m_th, lam_th = sp.symbols("I_th m_th lam_th")
a_, A, S, I_, B_, phz, gm, kp, pf_, g_, zz, sg = sp.symbols("a A S I B phz gamma_ kappa_ p_f g z sigma", positive=True)
# a_theta = -A (<0), sigma_theta = -S (<0); G_m = -Q => kappa G_m = -B; kappa G_sigma = kappa phi(z)
lam_eq = lam_th - (A * I_ - a_ * I_th)  # lambda_theta = -a_theta I - a I_theta
foc_eq = -B_ * m_th + kp * phz * (-S) - gm * lam_th
cap_eq = I_th + gm * m_th
SOL = sp.solve([lam_eq, foc_eq, cap_eq], [I_th, m_th, lam_th], dict=True)[0]
I_THETA = (gm**2 * A * I_ + gm * kp * phz * S) / (B_ + gm**2 * a_)
BOXR = {a_: (0.1, 0.5), A: (0, 0.1), S: (0, 0.2), I_: (0.05, 1), B_: (0.01, 1), phz: (0.01, 0.4), gm: (0.5, 2), kp: (0.2, 2)}


def test_investment_response_with_binding_capacity():
    sc.check_identity(SOL[I_th], I_THETA, {**BOXR, A: (0.001, 0.1), S: (0.001, 0.2)})


def test_investment_rises_and_reserve_falls():
    box = {**BOXR, A: (0.001, 0.1), S: (0.001, 0.2)}
    sc.check_sign(SOL[I_th], "+", box)  # "inversión no decreciente" (Prop. fs-coordination)
    sc.check_sign(SOL[m_th], "-", box)  # "reserva no creciente"
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(SOL[I_th], "-", box)


def test_sigma_channel_works_without_any_change_in_v():
    """a_theta = 0 (A=0): en el régimen interior I no cambia; con restricción activa I sube por sigma_F.
    La cota eta v_pol/a (que solo mira v) no acota esa respuesta."""
    only_sigma = I_THETA.subs(A, 0)
    sc.check_sign(only_sigma, "+", {**BOXR, S: (0.001, 0.2)})
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(only_sigma, "-", {**BOXR, S: (0.001, 0.2)})


def test_sigma_channel_share_is_free():
    """El peso del canal sigma en I_theta recorre (0,1) según S/A: no hay proporción fija entre v y sigma_F."""
    share = (gm * kp * phz * S) / (gm**2 * A * I_ + gm * kp * phz * S)
    sc.check_sign(share, "+", {**BOXR, A: (0.001, 0.1), S: (0.001, 0.2)})
    sc.check_sign(1 - share, "+", {**BOXR, A: (0.001, 0.1), S: (0.001, 0.2)})
    assert sp.limit(share, S, sp.oo) == 1 and sp.limit(share, S, 0) == 0


# ---- efecto sobre la pendiente I_u con restricción activa: I_u = (gam^2 p_f + B g)/(B + gam^2 a), B = kappa Q(z)
I_U = (gm**2 * pf_ + B_ * g_) / (B_ + gm**2 * a_)
dIu_dB = sp.diff(I_U, B_)
dIu_da = sp.diff(I_U, a_)


def test_slope_depends_on_B_with_sign_of_a_g_minus_p_f():
    sc.check_identity(dIu_dB, gm**2 * (a_ * g_ - pf_) / (B_ + gm**2 * a_) ** 2, {**BOXR, pf_: (0.5, 2), g_: (0, 8)})
    sc.check_sign(dIu_da, "-", {**BOXR, pf_: (0.5, 2), g_: (0, 8)})  # a baja => I_u sube


def test_coordination_effect_on_slope_has_no_fixed_sign_when_constrained():
    """dI_u/dtheta = I_u,a a_theta + I_u,B B_theta; B_theta = -kappa phi(z) z_theta, z_theta = (m_theta - z sigma_theta)/sigma,
    m_theta = -I_theta/gam. El canal a es siempre positivo; el canal B (sigma_F) tiene signo libre."""
    z_th = (-I_THETA / gm + zz * S) / sg
    B_th = -kp * phz * z_th
    total = dIu_da * (-A) + dIu_dB * B_th
    a_part = dIu_da * (-A)
    box = {**BOXR, A: (0.001, 0.1), S: (0.001, 0.2), pf_: (0.5, 2), g_: (0, 8), zz: (-2, 2), sg: (0.1, 0.5)}
    sc.check_sign(a_part, "+", box)
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(total, "+", box, min_informative=0.0)
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(total, "-", box, min_informative=0.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
