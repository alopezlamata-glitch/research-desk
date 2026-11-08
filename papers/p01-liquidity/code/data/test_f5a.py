"""Tests de F5a: lógica de cobertura trimestral y regla de ZLB (los datos brutos no se versionan)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import f5a_coverage as f


def test_quarters_complete_needs_three_months():
    m = pd.period_range("2003-01", "2003-05", freq="M")
    assert f.quarters_complete(m) == {pd.Period("2003Q1", "Q")}
    assert f.quarters_complete(m, need=1) == {pd.Period("2003Q1", "Q")}


def test_span_reports_internal_gaps():
    qs = {pd.Period(q, "Q") for q in ("2003Q1", "2003Q2", "2003Q4")}
    assert f.span(qs) == ("2003Q1", "2003Q4", 3, 1)


@pytest.mark.skipif(not (f.LAKE / "ecb" / "csv" / "MRO.csv").exists(), reason="falta el datalake")
def test_zlb_rule_splits_regimes():
    z = f.zlb_quarters(1.0)
    assert pd.Period("2007Q1", "Q") in z
    assert pd.Period("2015Q1", "Q") not in z  # MRO = 0,05 %
    assert pd.Period("2023Q4", "Q") in z
