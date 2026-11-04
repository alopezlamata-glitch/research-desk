"""Tests de datos de stage1_us.parquet: cobertura, unicidad, huecos esperados y unidades."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"
PARQUET = CLEAN / "stage1_us.parquet"

pytestmark = pytest.mark.skipif(not PARQUET.exists(), reason="ejecuta build_stage1_us.py (el parquet no se versiona)")


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return pd.read_parquet(PARQUET).set_index("quarter")


def span(s: pd.Series) -> tuple[str, str]:
    return s.first_valid_index(), s.last_valid_index()


def test_index_unique_and_contiguous(df):
    q = pd.PeriodIndex(df.index, freq="Q")
    assert q.is_unique and q.is_monotonic_increasing
    assert (np.diff(q.asi8) == 1).all()


def test_coverage(df):
    assert span(df["mps_bs23_orth"]) == ("1988Q1", "2023Q4")
    assert span(df["mps_bs25_me"]) == ("1994Q1", "2026Q4")
    assert span(df["dsr_nfc"]) == ("1999Q1", "2026Q1")
    assert span(df["liq_narrow_assets"])[0] == "1985Q1"
    assert span(df["inv_nonres_real"])[0] == "2007Q1"  # límite de PNFIC1 en el datalake
    assert span(df["sloos_ci_large"])[0] == "1990Q2"
    assert span(df["ebp"])[1] == "2026Q3"


def test_no_internal_gaps(df):
    """Las series con soporte continuo no tienen NaN entre su primer y su último dato."""
    for c in ["dsr_nfc", "dsr_priv_nf", "liq_narrow_assets", "liq_broad_debt", "gdp_real", "ffr", "y2_mean",
              "ebp", "sloos_ci_large", "sloos_ci_small", "sloos_ci_demand", "mps_bs25_me", "mps_bs25_stmt"]:
        s = df[c].loc[df[c].first_valid_index():df[c].last_valid_index()]
        assert s.notna().all(), c


def test_covid_gap_in_orth_only(df):
    """MPS_ORTH no existe de mar a dic de 2020 (los autores): NaN en 2020Q1–Q4; la serie cruda sí existe."""
    q = ["2020Q1", "2020Q2", "2020Q3", "2020Q4"]
    assert df.loc[q, "mps_bs23_orth"].isna().all()
    assert df.loc[q, "mps_bs23_raw"].notna().all()
    assert df["mps_bs23_orth"].loc["1988Q1":"2023Q4"].isna().sum() == 4


def test_2001_09_17_excluded_not_a_gap(df):
    assert pd.notna(df.loc["2001Q3", "mps_bs23_orth"])
    assert df.loc["2001Q3", "n_ev_bs23"] == 1  # 2001-09-17 fuera; queda 2001-08-21


def test_every_quarter_has_an_event(df):
    assert (df.loc["1988Q1":"2023Q4", "n_ev_bs23"] >= 1).all()
    assert (df.loc["1994Q1":"2026Q4", "n_ev_bs25"] >= 1).all()


def test_partial_quarter_flag(df):
    assert df["bs25_quarter_partial"].sum() == 1 and df.loc["2026Q4", "bs25_quarter_partial"]
    assert df.loc["2026Q4", "n_ev_bs25"] == 1


def test_units(df):
    assert df["mps_bs23_raw"].abs().max() < 1.0  # puntos porcentuales
    assert df["mps_bs25_me"].abs().max() < 1.0
    assert df["dsr_nfc"].dropna().between(10, 60).all() and df["dsr_priv_nf"].dropna().between(5, 30).all()
    assert df["liq_narrow_assets"].dropna().between(0.005, 0.2).all()
    assert (df["liq_broad_assets"].dropna() >= df["liq_narrow_assets"].dropna()).all()
    assert df["gdp_real"].dropna().between(5_000, 40_000).all()  # miles de millones de USD de 2017
    assert df["ffr"].dropna().between(0, 20).all()


def test_no_jumps(df):
    for c in ["liq_narrow_assets", "dsr_nfc", "dsr_priv_nf"]:
        assert df[c].pct_change(fill_method=None).abs().max() < 0.35, c


def test_inv_nfc_real_is_derived_not_filled(df):
    ok = df["inv_nfc_nominal"].notna() & df["gdp_deflator"].notna()
    assert np.allclose(df.loc[ok, "inv_nfc_real"], df.loc[ok, "inv_nfc_nominal"] / df.loc[ok, "gdp_deflator"] * 100)
    assert df.loc[~ok, "inv_nfc_real"].isna().all()
