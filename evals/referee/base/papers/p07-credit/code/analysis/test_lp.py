import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[0] / "data")]
import build_panel
import lp


def test_lp_recovers_the_dgp_response_in_a_long_sample():
    panel = build_panel.build(build_panel.simulate(20000, np.random.default_rng(0)))
    p = build_panel.PARAMS
    for h in (0, 1):
        acc = sum(p["rho"] ** k for k in range(h + 1))
        b, se = lp.fit(*lp.design(panel, h), lp.nw_lags(h))
        assert abs(b["shock"] - p["beta"] * acc) < 4 * se["shock"]
        assert abs(b["shock_x_credit"] - p["gamma"] * acc) < 4 * se["shock_x_credit"]


def test_newey_west_without_lags_is_white():
    rng = np.random.default_rng(1)
    X, u = rng.normal(size=(50, 3)), rng.normal(size=50)
    bread = np.linalg.inv(X.T @ X)
    white = bread @ (X.T * u**2) @ X @ bread
    assert np.allclose(lp.newey_west(X, u, 0), white)
