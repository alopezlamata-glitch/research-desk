"""Etapa 1 rediseñada (F7): panel trimestral `data/clean/stage1r_us.parquet` con el choque de Romer-Romer y el estado.

Choque: hoja `Wieland` (resid_full) de Monetarydat.xlsx del Handbook de Ramey (Romer-Romer reestimado hasta 2007m12 por
Wieland a partir de la extensión de Coibion), idéntica a `RRSHOCK` de la hoja `Monthly`. Trimestre = suma de los 3 meses
(el shock mensual ya suma las reuniones del mes; ene–feb de 1969 son 0: la primera reunión de RR es marzo de 1969).
Estado: igual que la etapa 1 (`s` de sample_counts.py), pero con Z.1 desde 1945, sin el recorte START de stage1_us.
Uso: uv run python papers/p01-liquidity/code/data/build_stage1r_us.py
"""

import io
import zipfile

import build_stage1_us as b
import numpy as np
import pandas as pd

CLEAN = b.CLEAN
HANDBOOK = b.RAW / "Ramey_HOM_monetary.zip"
HORIZON = 12  # h máximo de la ventana
CRISIS = pd.Period("2008Q3", "Q")  # la ventana t+12 debe terminar antes
FIRST_SHOCK_Q = pd.Period("1969Q1", "Q")
LAST_SHOCK_Q = CRISIS - HORIZON - 1  # 2005Q2


def rr_monthly() -> pd.Series:
    with zipfile.ZipFile(HANDBOOK) as z:
        raw = z.read("Monetarydat.xlsx")
    w = pd.read_excel(io.BytesIO(raw), "Wieland", usecols="A:C").dropna(subset=["date"])
    w.index = pd.PeriodIndex(w["date"].str.replace("m", "-"), freq="M")
    s = w["resid_full"].astype(float)
    m = pd.read_excel(io.BytesIO(raw), "Monthly", usecols="A,J").dropna(subset=["RRSHOCK"])
    k = ((m["DATES"] - 1959) * 12).round().astype(int)  # DATES = año + (mes−1)/12
    m = pd.Series(m["RRSHOCK"].to_numpy(), index=pd.Period("1959-01", "M") + k.to_numpy())
    assert np.allclose(s.reindex(m.index), m), "hoja Wieland y RRSHOCK de Monthly difieren"
    assert (s.loc[:"1969-02"] == 0).all() and s.index.is_monotonic_increasing and s.index.is_unique
    return s


def rr_quarterly(s: pd.Series) -> pd.DataFrame:
    g = s.groupby(s.index.asfreq("Q"))
    assert (g.count() == 3).all()  # trimestres completos
    return pd.DataFrame({"rr_shock": g.sum(), "rr_months_nonzero": g.apply(lambda x: int((x != 0).sum()))})


def main() -> None:
    idx = pd.period_range("1960Q1", "2008Q4", freq="Q")
    z = b.z1()["liq_broad_debt"]
    lg = np.log(z)
    st = pd.DataFrame({"liq_broad_debt": z, "s": lg - lg.shift(1).rolling(12).mean()})
    st["s_lag"] = st["s"].shift(1)
    bs = pd.read_parquet(CLEAN / "stage1_us.parquet").set_index("quarter")
    bs.index = pd.PeriodIndex(bs.index, freq="Q")
    parts = [rr_quarterly(rr_monthly()), st, b.complete_quarters(b.fred("FEDFUNDS"), 3).rename("ffr"), bs["mps_bs23_orth"]]
    df = pd.concat([p.reindex(idx) for p in parts], axis=1)
    df["in_rr_sample"] = (df.index >= FIRST_SHOCK_Q) & (df.index <= LAST_SHOCK_Q)
    df.index.name = "quarter"
    df.reset_index().assign(quarter=lambda x: x["quarter"].astype(str)).to_parquet(CLEAN / "stage1r_us.parquet", index=False)
    print(df[df.in_rr_sample].describe().T)


if __name__ == "__main__":
    main()
