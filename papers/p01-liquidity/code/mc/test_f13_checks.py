"""Tests de las comprobaciones de F13 (code/mc/f13_checks.py)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import f13_checks


def test_aggregations_mean_of_three_months_is_sum_over_three_and_nonzero_mean_skips_empty_months():
    s = pd.Series([0.3, 0.0, -0.6, 0.0, 0.0, 0.0], index=pd.period_range("1990-01", periods=6, freq="M"))
    a = f13_checks.aggregations(s)
    assert a["media3"].to_numpy() == pytest.approx(a["suma"].to_numpy() / 3)
    assert a["media_nz"].to_numpy() == pytest.approx([-0.15, 0.0])


def test_seeds_reuse_f9_cells_and_new_cells_do_not_collide():
    assert f13_checks.seed("homo", 1, 3) == f13_checks.SEED + 10_000 + 100 + 3
    assert f13_checks.seed("het_eps", 0, 5) == f13_checks.SEED + 11_000 + 4
    seeds = [f13_checks.seed(n, m, c) for n in f13_checks.NOISES for m in (0, 1) for c in f13_checks.CS_F9 + list(f13_checks.CS_NEW)]
    assert len(set(seeds)) == len(seeds)


def test_ljung_box_and_predictability_detect_dependence_and_accept_white_noise():
    rng = np.random.default_rng(0)
    idx = pd.period_range("1960Q1", periods=200, freq="Q")
    e = rng.standard_normal(200)
    ar = pd.Series(np.convolve(e, 0.6 ** np.arange(20))[:200], index=idx)
    assert f13_checks.ljung_box(ar)[1] < 0.01
    ffr = pd.Series(np.cumsum(rng.standard_normal(200)), index=idx)
    df = pd.DataFrame({"gdp": np.exp(np.cumsum(rng.normal(0.01, 0.01, 200))), "defl": np.exp(np.cumsum(rng.normal(0.01, 0.002, 200))),
                       "ffr": ffr, "noise": rng.standard_normal(200), "pred": ffr.diff().shift(1).fillna(0) + 0.1 * rng.standard_normal(200)},
                      index=idx)
    rows = idx[10:]
    assert f13_checks.predictability(df, "pred", rows)[3] < 0.001
    _F, d1, d2, p = f13_checks.predictability(df, "noise", rows)
    assert (d1, d2) == (12, len(rows) - 13) and p > 0.01
