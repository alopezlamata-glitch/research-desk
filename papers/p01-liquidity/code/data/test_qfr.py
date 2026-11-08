"""Tests de datos del QFR (F14a): lector BIFF, particiones por industria, celdas y G."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import build_qfr_f14a as b
import qfr_read

PARQUET = b.CLEAN / "qfr_cells.parquet"
pytestmark = pytest.mark.skipif(not b.RAW.exists(), reason="descarga con datalake/fetch/qfr.py (raw no se versiona)")


@pytest.fixture(scope="module")
def cells() -> pd.DataFrame:
    if not PARQUET.exists():
        b.main()
    return pd.read_parquet(PARQUET)


def test_xls_reader_matches_xlsx_in_overlap_quarter():
    """2022Q2 sale en qfr22q2f.xls y en qfr23q2f.xlsx: mismos activos totales salvo revisión (< 5 %)."""
    x = qfr_read.long_table(b.RAW / "qfr23q2f.xlsx")
    s = qfr_read.long_table(b.RAW / "qfr22q2f.xls")
    k = ["table", "group", "quarter", "item"]
    m = x.merge(s, on=k, suffixes=("_x", "_s"))
    m = m[(m["quarter"] == "2022Q2") & (m["item"] == "Total Assets")]
    assert len(m) >= 60
    assert (m["value_x"] / m["value_s"] - 1).abs().median() < 0.02
    assert (m["value_x"] / m["value_s"] - 1).abs().max() < 0.25


def test_size_in_title_is_not_mixed_with_all_sizes():
    """En 2006–07 el tamaño va en el título de la tabla: 'Paper' (todos) y 'Paper ≥25 M' son grupos distintos."""
    t = qfr_read.long_table(b.RAW / "qfr07q2f.xls")
    g = set(t["group"])
    assert "Paper" in g and "Paper Total Assets $25 Million and Over" in g
    ta = t[(t["item"] == "Total Assets") & (t["quarter"] == "2007Q2")].set_index("group")["value"]
    assert ta["Paper Total Assets $25 Million and Over"] < ta["Paper"]


def test_leaves_partition_manufacturing(cells):
    ta = cells[(cells["size"] == "ALL")].pivot(index="quarter", columns="ind", values="total_assets")
    d = b.vintages()  # el total manufacturero no es una celda hoja: se toma de las vintages
    tot = d[(d["item"] == "Total Assets") & (d["ind"] == "All Manufacturing") & (d["size"] == "ALL") & d["bs"]]
    tot = tot.sort_values("vintage").drop_duplicates("quarter", keep="last").set_index("quarter")["value"]
    tot.index = tot.index.astype(str)
    r = (ta[b.MFG].sum(axis=1) / tot).dropna()
    assert 0.93 < r.min() and r.max() <= 1.0001  # el resto es «otro equipo de transporte», que el QFR no publica


def test_cells_unique_and_consistent(cells):
    assert not cells.duplicated(["cell", "quarter"]).any()
    ok = cells.dropna(subset=["bank_share"])
    assert ((ok["bank_share"] >= 0) & (ok["bank_share"] <= 1.0001)).all()
    assert (ok["bank_debt"] <= ok["debt"] + 1).all()
    assert (cells["total_assets"] > 0).all()


def test_manufacturing_all_sizes_complete_since_2006q3(cells):
    q = [str(p) for p in b.WINDOW]
    for ind in b.MFG:
        have = set(cells[(cells["ind"] == ind) & (cells["size"] == "ALL") & cells["total_assets"].notna()]["quarter"])
        assert set(q) <= have, ind
    assert len(q) == 80 and q[0] == "2006Q3" and q[-1] == "2026Q2"


def test_bank_share_has_no_gaps_in_window(cells):
    w = cells[(cells["size"] == "ALL") & cells["quarter"].isin([str(p) for p in b.WINDOW])]
    assert w["bank_share"].notna().all()


def test_scenario_counts_come_from_the_table(cells):
    s = pd.read_csv(b.OUT / "F14A_G_SUMMARY.csv")
    assert (s["G_sin_rupturas"] <= s["G_cobertura"]).all()
    assert s["G_sin_rupturas"].eq(s["G_mfg"] + s["G_nonmfg"]).all()
    assert s.iloc[0]["T"] == 80 and s.iloc[0]["start"] == "2006Q3"
    assert (s["G_cobertura"] > 0).all()
