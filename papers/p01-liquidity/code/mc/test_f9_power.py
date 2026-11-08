"""Tests del estimador de s1r_* (code/analysis/s1r_lp.py) y del DGP de F9."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[0] / "analysis")]
import f9_power
import s1r_lp

PARQUET = HERE.parents[1] / "data" / "clean" / "stage1r_us.parquet"


def test_ramp_signal_gives_beta_on_ybar_for_an_isolated_shock():
    n, t0, beta, eps = 60, 20, -1.7, 0.8
    a = np.zeros(n)
    a[t0] = beta * eps / f9_power.signal_share(s1r_lp.HORIZONS)
    level = pd.Series(np.convolve(a, f9_power.ramp(n))[:n])
    assert s1r_lp.ybar(level / 100).iloc[t0] == pytest.approx(beta * eps)
    assert f9_power.signal_share(s1r_lp.HORIZONS) == pytest.approx(6.9 / 9)


def test_design_adds_shock_lags_and_leads():
    idx = pd.period_range("2000Q1", periods=30, freq="Q")
    eps = pd.Series(np.arange(30.0), index=idx)
    D = pd.Series(1.0, index=idx)
    ctrl = pd.DataFrame({c: 0.0 for c in s1r_lp.CONTROLS}, index=idx)
    X = s1r_lp.design(eps, D, ctrl, idx[12:15], "liq", shock_lags=2, shock_leads=3)
    assert X.shape == (3, 12 + 5)
    assert X.loc[idx[12], "eps_l2"] == 10 and X.loc[idx[12], "eps_f3"] == 15 and X.loc[idx[12], "b_U"] == 0


def test_h1_verdict_and_decision_tree():
    dof = 100
    assert s1r_lp.h1_verdict(-3.0, 1.0, dof, 0.1) == "confirma"
    assert s1r_lp.h1_verdict(3.0, 1.0, dof, 0.1) == "refuta_a"
    assert s1r_lp.h1_verdict(0.0, 0.01, dof, 0.1) == "refuta_b"  # IC90 = ±0,017 dentro de (−0,1, ∞)
    assert s1r_lp.h1_verdict(-0.5, 1.0, dof, 0.1) == "no_concluyente"
    assert s1r_lp.h0_confirms(-2.0, 1.0, dof) and not s1r_lp.h0_confirms(-1.0, 1.0, dof)
    d = s1r_lp.decide
    assert d("V1", False, "confirma") == "h0_falla"
    assert d("V1", True, "confirma", False, "refuta_a", 1.0) == "confirma"
    assert d("V2", True, "confirma", False, "confirma", -1.0) == "h0_falla"  # V2 usa H0 sin Volcker
    assert d("V2", False, "no_concluyente", True, "confirma", -1.0) == "confirma"
    assert d("V3s", True, "confirma", True, "no_concluyente", -1.0) == "no_concluyente"
    assert d("V3l", True, "confirma", True, "no_concluyente", -1.0) == "confirma"
    assert d("V3s", True, "refuta_a", True, "confirma", -1.0) == "refuta_a"


@pytest.mark.skipif(not PARQUET.exists(), reason="ejecuta build_stage1r_us.py (el parquet no se versiona)")
def test_dgp_samples_and_augmented_spec_has_no_design_error():
    df = f9_power.panel()
    smp = f9_power.samples(df)
    assert {k: len(v) for k, v in smp.items()} == {"RR": 146, "RR_noV": 133, "BS": 70}
    rr = {k: smp[k] for k in ("RR", "RR_noV")}
    dgp = f9_power.DGP(df, "rr_shock", rr, -2.0, -2.0, "het_eps", specs=("base", "aum"))
    assert int(dgp.D.loc[smp["RR"]].sum()) == 73  # SAMPLE_COUNTS_S1R.md: 73 restringidos
    assert (dgp.sigma[df.index.isin(smp["RR"])] ** 2).mean() == pytest.approx(1.0)
    y, X = dgp.draw(np.random.default_rng(0))
    d = dgp.data(y, X, smp["RR_noV"], "aum")
    assert d["liq"].shape == (133, 12 + 22) and np.isfinite(d["y"]).all() and d["liq"].notna().all().all()
    # Con β_C = β_U, los retardos y adelantos del choque hacen que β̂ sin ruido recupere β (la rampa dura 10 trimestres y la
    # ventana llega a h = 12). Con β_C ≠ β_U queda un resto, porque no van interactuados con el estado (ver F9_MC_REPORT.md).
    err = f9_power.design_error(df, "rr_shock", rr, -2.0, -2.0, ("aum",))["aum"]
    for s in rr:
        assert max(abs(v) for v in err[s].values()) < 1e-6, err
    # el sesgo que queda con ruido es cero dentro de 4 errores de Monte Carlo
    R = f9_power.simulate(f9_power.DGP(df, "rr_shock", rr, -2.0, -2.0, specs=("aum",)), 146, 150, 11, (f9_power.TESTED_SE,))
    for s in rr:
        A = R["aum"][s][f9_power.TESTED_SE]
        b = A[:, [0, 2]] + 2.0
        assert (np.abs(b.mean(0)) < 4 * b.std(0) / np.sqrt(len(b))).all(), b.mean(0)
