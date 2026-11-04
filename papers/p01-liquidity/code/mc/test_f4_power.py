"""Tests del estimador de s1_liq (code/analysis/s1_lp.py) y del DGP de F4."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[0] / "analysis")]
import f4_power
import s1_lp

PARQUET = HERE.parents[1] / "data" / "clean" / "stage1_us.parquet"


def test_nw_without_gaps_matches_statsmodels():
    rng = np.random.default_rng(0)
    X = sm.add_constant(rng.normal(size=(80, 3)))
    y = X @ [1, 2, 0, -1] + np.convolve(rng.normal(size=84), np.ones(5), "valid")
    _, se, dof = s1_lp.fit(y, X, s1_lp.hac_weights(np.arange(80), 5))
    ref = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5, "use_correction": False})
    np.testing.assert_allclose(se, ref.bse, rtol=1e-10)
    assert dof == 76


def test_leverage_option_is_hc3():
    rng = np.random.default_rng(1)
    X = sm.add_constant(rng.standard_t(3, size=(60, 2)))
    y = X @ [0, 1, -1] + rng.normal(size=60)
    _, se, _ = s1_lp.fit(y, X, np.eye(60), leverage=True)
    np.testing.assert_allclose(se, sm.OLS(y, X).fit(cov_type="HC3").bse, rtol=1e-10)


def test_calendar_weights_with_gaps_are_psd_and_cut_across_gaps():
    q = np.r_[np.arange(30), np.arange(60, 90)]
    W = s1_lp.hac_weights(q, 5)
    assert np.linalg.eigvalsh(W).min() > -1e-10
    assert W[29, 30] == 0 and W[0, 1] == pytest.approx(5 / 6)


def test_kappa_is_the_ybar_response_to_a_unit_impulse():
    phi1, phi2 = 0.4, 0.2
    g = pd.Series(np.r_[np.zeros(5), f4_power.lfilter([1.0], [1.0, -phi1, -phi2], np.r_[1.0, np.zeros(14)])])
    assert s1_lp.ybar((g / 100).cumsum()).iloc[5] == pytest.approx(f4_power.kappa(phi1, phi2))


def test_holm_and_verdicts():
    np.testing.assert_allclose(s1_lp.holm(np.array([0.04, 0.01])), [0.04, 0.02])
    dof = 86
    se = {t: 1.0 for t in s1_lp.TERMS}
    b = {"b_pos_C": -3.0, "b_pos_U": -1.0, "b_neg_C": 2.0, "b_neg_U": -1.0}
    assert s1_lp.verdicts(b, se, dof) == {"pos": "confirma", "neg": "refuta_a"}
    se_small = {t: 0.01 for t in s1_lp.TERMS}
    b = {"b_pos_C": 0.0, "b_pos_U": -1.0, "b_neg_C": -0.5, "b_neg_U": -10.0}
    # (b): IC90 de 0 ± 0,017 ⊂ (−0,146, ∞) → refuta; −0,5 con ee 0,01 → confirma aunque (b) también se cumpla
    assert s1_lp.verdicts(b, se_small, dof) == {"pos": "refuta_b", "neg": "confirma"}
    assert s1_lp.refute_b_also(b, se_small, dof, "neg")


@pytest.mark.skipif(not PARQUET.exists(), reason="ejecuta build_stage1_us.py (el parquet no se versiona)")
def test_dgp_reproduces_sample_and_estimator_recovers_large_effects():
    df = f4_power.sample_counts.panel()
    rows = f4_power.sample_counts.sample(df)[0].index
    assert len(rows) == 102
    betas = f4_power.scenario_betas(-40.0, 0.5)
    dgp = f4_power.DGP(df, rows, betas)
    y, X, _ = dgp(102, np.random.default_rng(1))
    assert X.shape == (102, 16) and np.isfinite(y).all() and X.notna().all().all()
    assert int((X["D"] == 1).sum()) == 51  # celdas de SAMPLE_COUNTS.md: 51 restringidas
    # Con choques reales fijos, sesgo total = error de diseño (determinista, sin ruido) + parte del ruido (media cero)
    r = f4_power.simulate(dgp, betas, 102, 200, 7, kinds=(f4_power.MAIN_SE,))[f4_power.MAIN_SE]
    mcse = r["sd"] / np.sqrt(200)
    noise_bias = r["bias"] - f4_power.design_error(df, rows, betas)
    assert (np.abs(noise_bias) < 4 * mcse).all(), noise_bias
    # el error de diseño es casi lineal en β (no exacto: el control Δlog inversión, un regresor, también depende de β)
    double = {t: 2 * v for t, v in betas.items()}
    np.testing.assert_allclose(f4_power.design_error(df, rows, double), 2 * f4_power.design_error(df, rows, betas), rtol=1e-4)
