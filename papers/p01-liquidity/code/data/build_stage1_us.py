"""Etapa 1 (EE. UU.) de p01: panel trimestral `data/clean/stage1_us.parquet` a partir de `data/raw/stage1_us/`.

Reglas: sin rellenar huecos (los NaN se quedan); una media mensual/diaria solo se calcula si el trimestre está
completo; los shocks se suman por trimestre (convención de Bauer-Swanson). Las definiciones están en
data/clean/DICTIONARY.md. Uso: uv run python papers/p01-liquidity/code/data/build_stage1_us.py
"""

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[2]
RAW = PAPER / "data" / "raw" / "stage1_us"
CLEAN = PAPER / "data" / "clean"
START = "1985Q1"  # un colchón de 3 años antes de la primera sorpresa (1988) para rezagos de controles


def q(dates) -> pd.PeriodIndex:
    return pd.DatetimeIndex(dates).to_period("Q")


# ---------------------------------------------------------------- agregación
def complete_quarters(s: pd.Series, per_q: int) -> pd.Series:
    """Media trimestral solo donde hay `per_q` observaciones (3 meses)."""
    g = s.dropna().groupby(q(s.dropna().index))
    return g.mean()[g.count() >= per_q]


def daily_mean_and_last(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Media diaria del trimestre y último dato del trimestre; NaN en el trimestre en curso (el último)."""
    s = s.dropna()
    g = s.groupby(q(s.index))
    last_q = q([s.index.max()])[0]
    mean, last = g.mean(), g.last()
    return mean[mean.index < last_q], last[last.index < last_q]


def fred(name: str) -> pd.Series:
    d = pd.read_csv(RAW / f"{name}.csv", parse_dates=["observation_date"], index_col="observation_date")
    return pd.to_numeric(d[name], errors="coerce")


# ---------------------------------------------------------------- Bauer-Swanson
def bs23() -> pd.DataFrame:
    """Vintage dic-2023: hoja 'FOMC (update 2023)', todos los anuncios (incluye no programados)."""
    f = pd.read_excel(RAW / "monetary-policy-surprises-data_vintage2023-12.xlsx", "FOMC (update 2023)")
    f = f[["Date", "Unscheduled", "MPS", "MPS_ORTH"]]
    # 2001-09-17: los autores lo excluyen (mercados cerrados desde el 11-S); la hoja lo deja en NA. No es un hueco.
    f = f[f["Date"] != "2001-09-17"].copy()
    f["qtr"] = q(f["Date"])
    g = f.groupby("qtr")
    out = pd.DataFrame({
        # min_count: un trimestre con algún evento NA (covid, mar–dic 2020) no tiene suma conocida → NaN
        "mps_bs23_orth": g["MPS_ORTH"].apply(lambda x: x.sum() if x.notna().all() else np.nan),
        "mps_bs23_raw": g["MPS"].sum(),
        "n_ev_bs23": g.size(),
    })
    out["n_ev_bs23_unsched"] = g["Unscheduled"].sum()
    return out


def bs25() -> pd.DataFrame:
    """Vintage ago-2025: mps.csv del zip (STMT, PC, ME por evento). PC es NaN donde no hubo rueda de prensa."""
    with zipfile.ZipFile(RAW / "monetary-policy-surprises_vintage2025-08.zip") as z:
        m = pd.read_csv(io.BytesIO(z.read("mps.csv")), parse_dates=["Date"], na_values=["NA"])
    m["qtr"] = q(m["Date"])
    g = m.groupby("qtr")
    out = pd.DataFrame({
        "mps_bs25_me": g["ME"].apply(lambda x: x.sum() if x.notna().all() else np.nan),
        "mps_bs25_stmt": g["STMT"].apply(lambda x: x.sum() if x.notna().all() else np.nan),
        "mps_bs25_pc": g["PC"].sum(min_count=1),  # NaN si el trimestre no tuvo ninguna rueda de prensa
        "n_ev_bs25": g.size(),
    })
    return out


# ---------------------------------------------------------------- BIS, Z.1, EBP
def bis_dsr() -> pd.DataFrame:
    d = pd.read_parquet(RAW / "WS_DSR.parquet")
    d = d[d.series_id.isin(["Q|US|P", "Q|US|N"])]
    d = d.assign(qtr=pd.PeriodIndex(d["date"].str.replace("-", ""), freq="Q"))
    w = d.pivot(index="qtr", columns="series_id", values="value")
    return w.rename(columns={"Q|US|P": "dsr_priv_nf", "Q|US|N": "dsr_nfc"})


Z1 = {  # nombre → código Z.1 (S11.1.b, niveles de fin de periodo, millones de USD, sin ajuste estacional)
    "nfc_assets": "FL102000005", "nfc_fin_assets": "FL104090005",
    "nfc_checkable": "FL103020005", "nfc_timesav": "FL103030003", "nfc_mmf": "FL103034000",
    "nfc_treasury": "LM103061103", "nfc_agency": "LM103061703", "nfc_muni": "LM103062003",
    "nfc_cp_asset": "FL103069100", "nfc_repo": "FL102051003",
    "nfc_debt_sec": "FL104122005", "nfc_loans_liab": "FL104135005",
    "nfc_cp_liab": "FL103169100", "nfc_bonds": "FL103163005", "nfc_bank_loans": "FL103168005",
}
Z1_FLOW = {"inv_nfc_nominal": "FA105019005"}  # S11.1.t, flujo anualizado, ajustado estacionalmente


def z1_table(name: str, codes: dict[str, str]) -> pd.DataFrame:
    with zipfile.ZipFile(RAW / "z1_csv_files_20260911.zip") as z:
        d = pd.read_csv(io.BytesIO(z.read(f"csv/{name}.csv")), encoding="latin1", na_values=["ND", "NA"])
    d.index = pd.PeriodIndex(d["date"].str.replace(":", ""), freq="Q")
    cols = {v + ".Q": k for k, v in codes.items()}
    missing = set(cols) - set(d.columns)
    assert not missing, f"códigos Z.1 ausentes en {name}: {missing}"
    return d[list(cols)].rename(columns=cols).apply(pd.to_numeric, errors="coerce")


def z1() -> pd.DataFrame:
    b = z1_table("S11_1_b", Z1)
    t = z1_table("S11_1_t", Z1_FLOW)
    d = b.join(t)
    liq_n = d[["nfc_checkable", "nfc_timesav", "nfc_mmf"]].sum(axis=1, min_count=3)
    liq_b = liq_n + d[["nfc_treasury", "nfc_agency", "nfc_muni", "nfc_cp_asset", "nfc_repo"]].sum(axis=1, min_count=5)
    debt = d[["nfc_debt_sec", "nfc_loans_liab"]].sum(axis=1, min_count=2)
    d["nfc_liq_narrow"], d["nfc_liq_broad"], d["nfc_debt"] = liq_n, liq_b, debt
    d["liq_narrow_assets"], d["liq_broad_assets"] = liq_n / d["nfc_assets"], liq_b / d["nfc_assets"]
    d["liq_narrow_debt"], d["liq_broad_debt"] = liq_n / debt, liq_b / debt
    return d


def ebp() -> pd.DataFrame:
    e = pd.read_csv(RAW / "ebp_csv.csv", parse_dates=["date"], index_col="date")
    return pd.DataFrame({"ebp": complete_quarters(e["ebp"], 3), "gz_spread": complete_quarters(e["gz_spread"], 3)})


# ---------------------------------------------------------------- ensamblaje
def main() -> None:
    idx = pd.period_range(START, "2026Q4", freq="Q")
    gdp, defl = fred("GDPC1"), fred("GDPDEF")
    y2_mean, y2_last = daily_mean_and_last(fred("DGS2"))
    parts = [
        bs23(), bs25(), bis_dsr(), z1(), ebp(),
        pd.DataFrame({
            "gdp_real": gdp.set_axis(q(gdp.index)), "gdp_deflator": defl.set_axis(q(defl.index)),
            "inv_nonres_real": fred("PNFIC1").pipe(lambda s: s.set_axis(q(s.index))),
            "inv_priv_real": fred("GPDIC1").pipe(lambda s: s.set_axis(q(s.index))),
            "ffr": complete_quarters(fred("FEDFUNDS"), 3),
            "y2_mean": y2_mean, "y2_eoq": y2_last,
            "sloos_ci_large": fred("DRTSCILM").pipe(lambda s: s.set_axis(q(s.index))),
            "sloos_ci_small": fred("DRTSCIS").pipe(lambda s: s.set_axis(q(s.index))),
            "sloos_ci_demand": fred("DRSDCILM").pipe(lambda s: s.set_axis(q(s.index))),
        }),
    ]
    df = pd.concat([p.reindex(idx) for p in parts], axis=1)
    # derivadas (sin rellenar: NaN en, NaN out)
    df["inv_nfc_real"] = df["inv_nfc_nominal"] / df["gdp_deflator"] * 100
    # el trimestre solo tiene shocks completos si ya pasó; el 2026Q4 solo tiene la reunión de octubre
    df["bs25_quarter_partial"] = df.index == pd.Period("2026Q4")
    df.index.name = "quarter"
    df.insert(0, "date", df.index.to_timestamp(how="end").normalize())
    # las sorpresas suman cero en trimestres sin evento solo dentro del soporte de cada vintage
    s23 = df.index <= pd.Period("2023Q4")
    s25 = df.index >= pd.Period("1994Q1")
    for col, ok in [("mps_bs23_orth", s23), ("mps_bs23_raw", s23), ("mps_bs25_me", s25), ("mps_bs25_stmt", s25)]:
        assert df.loc[~ok, col].isna().all(), col
    CLEAN.mkdir(parents=True, exist_ok=True)
    out = df.reset_index().assign(quarter=lambda x: x["quarter"].astype(str))
    out.to_parquet(CLEAN / "stage1_us.parquet", index=False)
    cov = pd.DataFrame({"first": df.apply(lambda s: s.first_valid_index()), "last": df.apply(lambda s: s.last_valid_index()),
                        "n_valid": df.notna().sum()}).drop(index="date")
    cov["first"], cov["last"] = cov["first"].astype(str), cov["last"].astype(str)
    cov.to_csv(CLEAN / "coverage.csv", index_label="variable")
    print(cov.to_string())


if __name__ == "__main__":
    main()
