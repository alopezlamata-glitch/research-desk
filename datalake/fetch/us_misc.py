"""EE. UU. fuera de FRED: EBP (Fed), SPF (Philly), ACM (NY Fed), Z.1, Tesoro (FiscalData), FDIC."""

import json

import pandas as pd
import requests
from _common import UA, download, run, save, save_long

FD = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
FDIC = "https://api.fdic.gov/banks/summary"


def fiscaldata(name, path):
    rows, page = [], 1
    while True:
        r = requests.get(FD + path, params={"page[size]": 10000, "page[number]": page}, headers=UA, timeout=120)
        r.raise_for_status()
        j = r.json()
        rows += j["data"]
        if page >= j["meta"]["total-pages"]:
            break
        page += 1
    assert rows, name
    save("treasury", f"{name}.json", json.dumps(rows).encode(), FD + path, vintage="descarga completa")
    pd.DataFrame(rows).to_parquet(save_path(name))


def save_path(name):
    from _common import RAW
    p = RAW / "treasury" / f"{name}.parquet"
    return p


def fdic():
    r = requests.get(FDIC, params={"limit": 10000}, headers=UA, timeout=120)
    r.raise_for_status()
    j = r.json()
    df = pd.DataFrame([x["data"] for x in j["data"]])
    assert len(df) == j["meta"]["total"] > 1000
    save("fdic", "summary_state_year.json", json.dumps(j["data"]).encode(), FDIC)
    cols = [c for c in ["ASSET", "EQ", "DEP", "LNLSNET", "NETINC", "INTINC", "EINTEXP", "NCLNLS"] if c in df]
    us = df.groupby("YEAR")[cols].sum(min_count=1).reset_index()
    long = us.melt("YEAR", var_name="series_id", value_name="value")
    long["date"] = pd.to_datetime(long.pop("YEAR").astype(str) + "-12-31")
    save_long("fdic", "us_aggregate_annual", long[["date", "series_id", "value"]], FDIC,
              meta={"us_aggregate_annual": "suma de estados por año (miles USD); revisar cobertura antes de usar"})


def main():
    run(lambda: download("fed_board", "ebp_csv.csv",
                         "https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv"), "EBP Gilchrist-Zakrajsek")
    base = "https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/"
    run(lambda: download("spf", "medianlevel.xlsx", base + "historical-data/medianlevel.xlsx"), "SPF medianlevel")
    run(lambda: download("nyfed", "acm_term_premia_allmonth.xls",
                         "https://www.newyorkfed.org/medialibrary/media/research/capital_markets/allmonth.xls"),
        "NY Fed ACM term premia")
    run(lambda: download("fed_z1", "z1_csv_files_20260911.zip",
                         "https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip", "2026-09-11"),
        "Fed Z.1 (20260911)")
    for name, path in {"debt_to_penny": "v2/accounting/od/debt_to_penny",
                       "avg_interest_rates": "v2/accounting/od/avg_interest_rates",
                       "interest_expense": "v2/accounting/od/interest_expense"}.items():
        run(lambda n=name, p=path: fiscaldata(n, p), f"Tesoro {name}")
    run(fdic, "FDIC summary")


if __name__ == "__main__":
    main()
