"""Agregación con banco común: r_L = r_f + (psi/N) L, L = suma de I (TFG1 l. 186-189; TFG2 l. 308).

Una masa 1-s de empresas restringidas y s de holgadas. Cada empresa toma r_L como dado, así que su
curvatura propia es a_0 = b + eta v (sin psi/N); psi/N entra solo por el precio r_L. Se comprueba:
  1. la derivación a mano del abogado del diablo (§2.3), válida con restringidas RÍGIDAS (I = H, H_u = g);
  2. la fórmula general con restringidas de reserva ajustable (TFG2) y K tipos de empresa;
  3. que con una sola clase coincide con el agente representativo de TFG2 (a = a_0 + psi/N);
  4. contra el equilibrio no lineal resuelto numéricamente (diferencias finitas), con G normal exacta.
Ejecutar: uv run python papers/p01-liquidity/theory/check_aggregation.py
"""

import sys
from pathlib import Path

import pytest
import sympy as sp
from scipy.optimize import brentq
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import symcheck as sc

p_f, a0, phi, s, g, gam, B = sp.symbols("p_f a_0 phi s g gamma B", positive=True)  # phi = psi/N
BOX = {p_f: (0.5, 2), a0: (0.05, 0.5), phi: (0.01, 1), s: (0.02, 0.98), g: (0, 8), gam: (0.5, 2), B: (0.01, 3)}

# ------------------------------------------------------------ 1. restringidas rígidas (I_c = H)
L_u, Is_u = sp.symbols("L_u Is_u")
# I_s a_0 = q - phi L ; L = (1-s) H + s I_s  ->  derivar respecto de u con q_u = p_f, H_u = g
rigid = sp.solve([a0 * Is_u - (p_f - phi * L_u), L_u - ((1 - s) * g + s * Is_u)], [Is_u, L_u], dict=True)[0]
REPORT_Is_u = (p_f - phi * (1 - s) * g) / (a0 + s * phi)  # informe §2.3
REPORT_L_u = (s * p_f + a0 * (1 - s) * g) / (a0 + s * phi)  # agregado con restringidas rígidas


def test_report_slack_response_confirmed():
    sc.check_identity(rigid[Is_u], REPORT_Is_u, BOX)


def test_rigid_aggregate_formula():
    sc.check_identity(rigid[L_u], REPORT_L_u, BOX)


def test_negative_naive_individual_psi_over_N_is_rejected():
    """§5 de FIRST_PRINCIPLES: a_i = b + eta v_i + psi/N individual => holgada responde p_f/(a_0+phi)."""
    with pytest.raises(sc.ClaimFailed):
        sc.check_identity(rigid[Is_u], p_f / (a0 + phi), BOX)


def test_slack_response_falls_with_mass_and_relief_of_constrained():
    d_g = sp.diff(REPORT_Is_u, g)
    sc.check_sign(d_g, "-", BOX)  # expulsión de crédito: más alivio g de las restringidas, menos I_s
    with pytest.raises(sc.ClaimFailed):
        sc.check_sign(d_g, "+", BOX)


def test_slack_response_can_change_sign():
    """Con g > p_f/(phi (1-s)) las holgadas REDUCEN inversión ante una relajación; no ocurre en la
    calibración de TFG2 (p_f=1, phi=0.05 => umbral >= 20 > g = 5)."""
    thr = p_f / (phi * (1 - s))
    assert REPORT_Is_u.subs({p_f: 1, phi: sp.Rational(1, 20), s: sp.Rational(1, 2), g: 50, a0: sp.Rational(1, 8)}) < 0
    assert thr.subs({p_f: 1, phi: sp.Rational(1, 20), s: sp.Rational(1, 2)}) == 40
    # en la calibración de TFG2 (g<=5, phi=0.05) el umbral mínimo es 20 > 5: no ocurre
    assert thr.subs({p_f: 1, phi: sp.Rational(1, 20), s: 0}) == 20


# ------------------------------------------------------------ 2. fórmula general (K tipos, reserva ajustable)
# tipo j: I_j,u = w_j x/a_j + (1-w_j) g_j,  x = p_f - phi L_u,  w_j = gam_j^2 a_j/(B_j+gam_j^2 a_j); w=1 si holgada
a1, a2, w1, w2, g1, g2, s1, s2, x, Theta, Gbar = sp.symbols("a1 a2 w1 w2 g1 g2 s1 s2 x Theta Gbar")
w_in = sp.Symbol("w", positive=True)


def _general(types):
    Theta_ = sum(m * w_ / a_ for m, w_, a_, _ in types)
    Gbar_ = sum(m * (1 - w_) * g_ for m, w_, _, g_ in types)
    return Theta_, Gbar_


def _solve_L(types):
    Lu = sp.Symbol("Lu")
    xx = p_f - phi * Lu
    resp = sum(m * (w_ * xx / a_ + (1 - w_) * g_) for m, w_, a_, g_ in types)
    return sp.solve(sp.Eq(Lu, resp), Lu)[0]


TYPES = [(s1, w1, a1, g1), (s2, w2, a2, g2)]
Th, Gb = _general(TYPES)
GENERAL = (Gb + Th * p_f) / (1 + phi * Th)  # L_u = (Gbar + Theta p_f)/(1 + phi Theta)
BOX2 = {p_f: (0.5, 2), phi: (0.01, 1), a1: (0.05, 0.5), a2: (0.05, 0.5), w1: (0.05, 1), w2: (0.05, 1),
        g1: (0, 8), g2: (0, 8), s1: (0.05, 0.9), s2: (0.05, 0.9)}


def test_general_formula_any_number_of_types():
    sc.check_identity(_solve_L(TYPES), GENERAL, BOX2)


def test_general_formula_reduces_to_report_with_rigid_constrained():
    """Tipo 1 holgada (w=1, a_1=a_0, masa s), tipo 2 restringida rígida (w=0, g_2=g, masa 1-s)."""
    spec = GENERAL.subs({w1: 1, w2: 0, a1: a0, s1: s, s2: 1 - s, g2: g, g1: 0})
    sc.check_identity(spec, REPORT_L_u, BOX)


def test_negative_general_formula_without_crowding_is_rejected():
    with pytest.raises(sc.ClaimFailed):
        sc.check_identity(_solve_L(TYPES), Gb + Th * p_f, BOX2)  # omite el denominador 1 + phi Theta


def test_representative_agent_matches_tfg2():
    """s=0, todas restringidas con w_0 = gam^2 a_0/(B+gam^2 a_0): L_u = TFG2 (gam^2 p_f + B g)/(B + gam^2 (a_0+phi))."""
    w0 = gam**2 * a0 / (B + gam**2 * a0)
    one = _solve_L([(1, w0, a0, g)])
    tfg2 = (gam**2 * p_f + B * g) / (B + gam**2 * (a0 + phi))
    sc.check_identity(one, tfg2, BOX)
    with pytest.raises(sc.ClaimFailed):  # negativo: usar a_0 en vez de a_0+phi no coincide
        sc.check_identity(one, (gam**2 * p_f + B * g) / (B + gam**2 * a0), BOX)


def test_response_is_smaller_than_without_common_bank():
    """Con banco común, el efecto agregado de p_f está amortiguado por el factor 1/(1+phi Theta) < 1."""
    sc.check_sign((GENERAL.subs({g1: 0, g2: 0}) - Th * p_f).subs({s1: 0.3, s2: 0.7}), "-", BOX2)


# ------------------------------------------------------------ 4. equilibrio no lineal (diferencias finitas)
def _equilibrium(u, par):
    """Resuelve L con r_L = r_f + phi L. Holgadas: I = (q-phi L)/a0. Restringidas: I + gam m = H,
    kappa G(m) = delta + gam (q - phi L - a0 I), G exacta normal."""
    q = par["q0"] + par["p_f"] * u
    H = par["H0"] + par["g"] * u

    def invest(L):
        Is = (q - par["phi"] * L) / par["a0"]

        def foc(m):
            I = H - par["gam"] * m
            G = par["sig"] * (norm.pdf((m - par["mu"]) / par["sig"]) - (m - par["mu"]) / par["sig"] * norm.sf((m - par["mu"]) / par["sig"]))
            return par["kap"] * G - par["delta"] - par["gam"] * (q - par["phi"] * L - par["a0"] * I)

        m = brentq(foc, -5, 5, xtol=1e-14)
        return Is, H - par["gam"] * m, m

    def excess(L):
        Is, Ic, _ = invest(L)
        return par["s"] * Is + (1 - par["s"]) * Ic - L

    L = brentq(excess, -1, 3, xtol=1e-14)
    return L, *invest(L)


PAR = {"q0": 0.06, "p_f": 1.0, "H0": 0.25, "g": 0.5, "a0": 0.12, "phi": 0.05, "gam": 1.0,
       "kap": 1.0, "delta": 0.015, "mu": 0.1, "sig": 0.3, "s": 0.4}


def test_general_formula_against_nonlinear_equilibrium():
    h = 1e-6
    Lp, _, _, _ = _equilibrium(h, PAR)
    Lm, _, _, _ = _equilibrium(-h, PAR)
    L0, Is, Ic, m = _equilibrium(0.0, PAR)
    num = (Lp - Lm) / (2 * h)
    # régimen: la restringida tiene lambda>0 (capacidad vinculante) y reserva interior; la holgada es interior
    lam = PAR["q0"] - PAR["phi"] * L0 - PAR["a0"] * Ic
    assert lam > 0 and 0 < m < 1 and Is > 0 and Ic > 0
    z0 = (m - PAR["mu"]) / PAR["sig"]
    B0 = PAR["kap"] * norm.sf(z0)
    w0 = PAR["gam"] ** 2 * PAR["a0"] / (B0 + PAR["gam"] ** 2 * PAR["a0"])
    f = sp.lambdify((p_f, phi, a1, a2, w1, w2, g1, g2, s1, s2), GENERAL)
    pred = f(PAR["p_f"], PAR["phi"], PAR["a0"], PAR["a0"], 1.0, w0, 0.0, PAR["g"], PAR["s"], 1 - PAR["s"])
    assert abs(num - pred) < 1e-6, (num, pred)
    # negativo: la fórmula de rígidas del informe NO vale con reserva ajustable
    report = float(REPORT_L_u.subs({p_f: PAR["p_f"], a0: PAR["a0"], phi: PAR["phi"], s: PAR["s"], g: PAR["g"]}))
    assert abs(num - report) > 1e-3, (num, report)


def test_report_slack_formula_holds_when_constrained_are_rigid_numerically():
    """Con restringidas rígidas (I=H) la diferencia finita reproduce la fórmula del informe."""
    h, par = 1e-6, PAR

    def L_of(u):
        q, H = par["q0"] + par["p_f"] * u, par["H0"] + par["g"] * u
        # L = (1-s) H + s (q - phi L)/a0  -> lineal
        return ((1 - par["s"]) * H + par["s"] * q / par["a0"]) / (1 + par["s"] * par["phi"] / par["a0"])

    def Is_of(u):
        return (par["q0"] + par["p_f"] * u - par["phi"] * L_of(u)) / par["a0"]

    num = (Is_of(h) - Is_of(-h)) / (2 * h)
    rep = float(REPORT_Is_u.subs({p_f: par["p_f"], a0: par["a0"], phi: par["phi"], s: par["s"], g: par["g"]}))
    assert abs(num - rep) < 1e-8


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
