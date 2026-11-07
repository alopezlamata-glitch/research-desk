import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[0] / "analysis")]
import lp
import mc_lp

PANEL = HERE.parents[1] / "data" / "clean" / "panel.parquet"


def test_lp_recovers_the_mc_dgp_response_in_a_long_sample():
    cal = mc_lp.calibrate(pd.read_parquet(PANEL))
    sim = mc_lp.simulate(20000, np.random.default_rng(0), cal)
    for h in (0, lp.H_MAIN):
        b, se = lp.fit(*lp.design(sim, h))
        true = mc_lp.true_values(cal, h)
        for term in lp.TERMS:
            assert abs(b[term] - true[term]) < 4 * se[term]


def test_white_matches_its_closed_form():
    rng = np.random.default_rng(1)
    X = pd.DataFrame(rng.normal(size=(60, 3)), columns=list("abc"))
    y = X.to_numpy() @ [1.0, -1.0, 0.5] + rng.normal(size=60)
    _, se = lp.fit(y, X)
    Xa = X.to_numpy()
    bread = np.linalg.inv(Xa.T @ Xa)
    u = y - Xa @ bread @ Xa.T @ y
    assert np.allclose(se, np.sqrt(np.diag(bread @ (Xa.T * u**2) @ Xa @ bread)))
