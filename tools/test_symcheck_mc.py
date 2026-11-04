import mc
import numpy as np
import pytest
import symcheck as sc
import sympy as sp

d, th, g = sp.symbols("d theta gamma", positive=True)
DELTA = 1 - sp.exp(-th * d**g)
BOX = {d: (0.72, 1.56), th: (0.6, 0.8), g: (1.2, 1.4)}


# ---------------------------------------------------------------- symcheck
def test_identity_accepts_correct_second_derivative():
    claimed = th * g * sp.exp(-th * d**g) * d ** (g - 2) * ((g - 1) - th * g * d**g)
    sc.check_identity(sp.diff(DELTA, d, 2), claimed, BOX)


def test_identity_rejects_v22_sign_error():
    v22 = th * g * sp.exp(-th * d**g) * d ** (g - 2) * (th * g * d**g - (g - 1))
    with pytest.raises(sc.ClaimFailed):
        sc.check_identity(sp.diff(DELTA, d, 2), v22, BOX)


def test_sign_check_and_its_negative_test():
    second = sp.diff(DELTA, d, 2)
    sc.check_sign(second, "-", BOX)  # cóncava en la muestra de v22
    with pytest.raises(sc.ClaimFailed, match="falla"):
        sc.check_sign(second, "+", BOX)  # la afirmación de v22 (convexa) falla


def test_sign_check_refuses_vacuous_claims():
    with pytest.raises(sc.ClaimFailed, match="vacío"):
        sc.check_sign(d - d, "+", {d: (0, 1)})


# ---------------------------------------------------------------- mc
def ols_dgp(T, rng):
    x = rng.normal(size=T)
    return x, 0.5 * x + rng.normal(size=T)


def ols(data):
    x, y = data
    X = np.column_stack([np.ones_like(x), x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    cov = resid @ resid / (len(y) - 2) * np.linalg.inv(X.T @ X)
    return b[1:], np.sqrt(np.diag(cov))[1:]


def test_mc_valid_estimator_passes_with_t_and_half_t():
    res = mc.validate(ols_dgp, ols, {"beta": 0.5}, T=200, reps=400)
    assert {r.T for r in res} == {200, 100}
    assert abs(res[0].bias) < 0.02 and res[0].power > 0.99


def test_mc_flags_estimator_with_wrong_standard_errors():
    def overconfident(data):
        b, s = ols(data)
        return b, s / 3
    with pytest.raises(mc.CoverageOutOfBand):
        mc.validate(ols_dgp, overconfident, {"beta": 0.5}, T=200, reps=400)
