"""Tests de datalake/fetch/_common.py: volver a descargar nunca pierde la versión anterior."""

import _common as c
import integrity as ig
import pandas as pd
import pytest


@pytest.fixture
def lake(tmp_path, monkeypatch):
    monkeypatch.setattr(c, "ROOT", tmp_path)
    monkeypatch.setattr(c, "RAW", tmp_path / "raw")
    monkeypatch.setattr(c, "MANIFEST", tmp_path / "MANIFEST.csv")
    return tmp_path


def test_redownload_keeps_previous_content_as_a_verifiable_vintage(lake):
    p = c.save("fred", "a.csv", b"v1", "u")
    c.save("fred", "a.csv", b"v1", "u")  # mismo contenido: no crea vintage
    assert not (p.parent / "_vintages").exists()
    c.save("fred", "a.csv", b"v2", "u")
    (kept,) = (p.parent / "_vintages").iterdir()
    assert p.read_bytes() == b"v2" and kept.read_bytes() == b"v1"
    assert kept.name == f"a.{c.sha256(kept)[:12]}.csv"
    assert not list(p.parent.glob("*.tmp"))
    rows = ig._read_csv(lake / "MANIFEST.csv")
    assert [r["sha256"] for r in rows] == [c.sha256(kept)] * 2 + [c.sha256(p)]


def test_save_long_and_frames_are_registered_and_pass_rawhash(lake):
    df = pd.DataFrame({"date": ["2020-01-01"], "series_id": ["X"], "value": [1.0]})
    c.save_long("src", "long", df, "u", meta={"X": "serie"})
    c.save_frame("src", "wide.parquet", pd.DataFrame({"a": [1, 2]}), "u")
    c.save_frame("src", "wide.parquet", pd.DataFrame({"a": [1, 3]}), "u")
    # check_rawhash espera la estructura del repo: datalake/MANIFEST.csv y datalake/raw/
    repo = lake.parent / "repo"
    (repo / "datalake").mkdir(parents=True)
    (lake / "MANIFEST.csv").rename(repo / "datalake" / "MANIFEST.csv")
    (lake / "raw").rename(repo / "datalake" / "raw")
    assert ig.check_rawhash(repo, []) == []
