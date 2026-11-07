"""Tests de datos de stage1r_us.parquet (F7): choque de Romer-Romer, fecha de corte y recuentos por estado."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import build_stage1r_us as b
import sample_counts_s1r as sc

PARQUET = b.CLEAN / "stage1r_us.parquet"
pytestmark = pytest.mark.skipif(not PARQUET.exists(), reason="ejecuta build_stage1r_us.py (el parquet no se versiona)")


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return sc.panel()


def test_cutoff_is_2005q2_and_window_ends_before_2008q3():
    assert b.LAST_SHOCK_Q == pd.Period("2005Q2", "Q")
    assert b.LAST_SHOCK_Q + b.HORIZON < b.CRISIS <= b.LAST_SHOCK_Q + b.HORIZON + 1  # 2005Q2 es el último que cumple


def test_monthly_matches_handbook_published_values():
    s = b.rr_monthly()
    assert s.index[0] == pd.Period("1969-01", "M") and s.index[-1] == pd.Period("2007-12", "M") and len(s) == 468
    assert s["1969-03"] == pytest.approx(-0.231698, abs=1e-6) and s["2007-09"] == pytest.approx(-0.595159, abs=1e-6)
    assert s.abs().max() < 4  # pp de fed funds


def test_quarterly_is_sum_of_months_without_holes():
    s = b.rr_monthly()
    q = b.rr_quarterly(s)["rr_shock"]
    assert len(q) == 156 and q.sum() == pytest.approx(s.sum())
    assert q["1969Q1"] == pytest.approx(s["1969-03"])  # ene y feb de 1969 son 0


def test_sample_is_146_quarters_no_nan(df):
    d = df[df["in_rr_sample"]]
    assert (d.index[0], d.index[-1], len(d)) == (pd.Period("1969Q1", "Q"), pd.Period("2005Q2", "Q"), 146)
    assert d[["rr_shock", "s_lag", "ffr"]].notna().all().all()


def test_replica_sample_bs_orth_1988q1_to_cutoff(df):
    (rr, _), (bs, _) = sc.samples(df).values()
    assert (bs.index[0], bs.index[-1], len(bs)) == (pd.Period("1988Q1", "Q"), b.LAST_SHOCK_Q, 70)
    assert len(rr) == 146


def test_state_is_lagged_and_matches_stage1_definition(df):
    lg = np.log(df["liq_broad_debt"])
    s = lg - lg.shift(1).rolling(12).mean()
    both = pd.concat([df["s"], s, df["s_lag"], s.shift(1)], axis=1).dropna()  # df empieza en 1960Q1: sin los primeros 12 trim.
    assert len(both) > 150 and np.allclose(both.iloc[:, 0], both.iloc[:, 1]) and np.allclose(both.iloc[:, 2], both.iloc[:, 3])
    # coincide con la etapa 1 en el solape (Z.1 no cambia)
    import sample_counts as s1

    both = pd.concat([df["s_lag"], s1.panel()["s_lag"]], axis=1, keys=["r", "o"]).dropna()
    assert len(both) > 60 and np.allclose(both["r"], both["o"])


def test_counts_add_up_and_volcker_has_13_quarters(df):
    d = sc.with_state(sc.samples(df)["rr_shock"][0])
    t = sc.table(d, "rr_shock")
    assert t["N"].sum() == len(d) == 146 and d["volcker"].sum() == 13
    assert abs(t["Σ|ε|"].sum() - d["rr_shock"].abs().sum()) < 1e-9
    assert (t["N"] >= t["choque≠0"]).all()
