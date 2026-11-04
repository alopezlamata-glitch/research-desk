"""Nivel 2: paneles internacionales. JST, BIS, BoE, ECB, Banco Mundial, OCDE, crisis (BVX, Laeven-Valencia)."""

import io
import zipfile

import pandas as pd
import requests
from _common import UA, check, download, get, run, save, save_long

BIS = "https://data.bis.org/static/bulk/WS_{}_csv_flat.zip"
BIS_SETS = ["DSR", "TC", "CBPOL", "SPP", "CREDIT_GAP", "EER", "XRU", "LONG_CPI", "CPP", "GLI"]
ECB = "https://data-api.ecb.europa.eu/service/data/"
ECB_SERIES = {
    "MRO": "FM/B.U2.EUR.4F.KR.MRR_FR.LEV", "DFR": "FM/B.U2.EUR.4F.KR.DFR.LEV", "MLF": "FM/B.U2.EUR.4F.KR.MLFR.LEV",
    "HICP_yoy": "ICP/M.U2.N.000000.4.ANR", "M3_yoy": "BSI/M.U2.Y.V.M30.X.I.U2.2300.Z01.A",
    "Eurosystem_assets": "ILM/W.U2.C.T000000.Z5.Z01", "MIR_NFC_loans_new": "MIR/M.U2.B.A2A.A.R.A.2240.EUR.N",
    "MIR_mortgages_new": "MIR/M.U2.B.A2C.A.R.A.2250.EUR.N", "yield10y_AAA": "YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",
    "yield2y_AAA": "YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y", "GDP_real": "MNA/Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N",
    "unemployment": "STS/M.I9.S.UNEH.RTT000.4.000", "CISS": "CISS/D.U2.Z0Z.4F.EC.SS_CI.IDX",
    "gov_debt_gdp": "GFS/Q.N.I9.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T",
}
WB = "https://api.worldbank.org/v2/country/all/indicator/{}?format=json&per_page=20000&date=1960:2026"
WB_IND = ["GC.DOD.TOTL.GD.ZS", "FS.AST.PRVT.GD.ZS", "GC.XPN.INTP.RV.ZS", "FR.INR.RINR", "NY.GDP.MKTP.KD.ZG"]
DV = "https://dataverse.harvard.edu/api"


def bis(code):
    r = get(BIS.format(code), timeout=300)
    save("bis", f"WS_{code}_csv_flat.zip", r.content, BIS.format(code))
    z = zipfile.ZipFile(io.BytesIO(r.content))
    parts = []
    for ch in pd.read_csv(z.open(z.namelist()[0]), low_memory=False, chunksize=500_000, dtype=str):
        cols = {c.split(":")[0]: c for c in ch.columns}
        # el formato plano de BIS pone las dimensiones entre ACTION y TIME_PERIOD, y los atributos después
        cl = list(ch.columns)
        dims = cl[cl.index(cols["ACTION"]) + 1:cl.index(cols["TIME_PERIOD"])]
        sid = ch[dims].fillna("").apply(lambda s: s.str.split(":").str[0].str.strip()).agg("|".join, axis=1)
        parts.append(pd.DataFrame({"date": ch[cols["TIME_PERIOD"]], "series_id": sid,
                                   "value": pd.to_numeric(ch[cols["OBS_VALUE"]], errors="coerce")}))
    long = pd.concat(parts, ignore_index=True)
    save_long("bis", f"WS_{code}", long, BIS.format(code), meta={f"WS_{code}": "fechas como texto SDMX (YYYY-Qn, YYYY-MM...)"})
    print("   ", code, len(long), long["date"].min(), long["date"].max())


def ecb():
    frames = []
    for name, key in ECB_SERIES.items():
        try:
            r = get(f"{ECB}{key}?format=csvdata&startPeriod=1960", timeout=120)
            d = pd.read_csv(io.StringIO(r.text))
            frames.append(pd.DataFrame({"date": d["TIME_PERIOD"].astype(str), "series_id": name,
                                        "value": pd.to_numeric(d["OBS_VALUE"], errors="coerce")}))
            save("ecb", f"csv/{name}.csv", r.content, ECB + key)
        except Exception as e:  # noqa: BLE001
            print(f"[ROTO]  ECB {name}: {str(e)[:100]}")
    long = pd.concat(frames)
    save_long("ecb", "ecb_series", long, ECB, meta={"ecb_series": {k: v for k, v in ECB_SERIES.items()}})
    print("   ", long.groupby("series_id").size().to_dict())


def worldbank():
    rows = []
    for ind in WB_IND:
        r = requests.get(WB.format(ind), headers=UA, timeout=120)
        r.raise_for_status()
        j = r.json()
        rows += [(f"{x['date']}-12-31", f"{ind}|{x['country']['id']}", x["value"]) for x in j[1] if x["value"] is not None]
    long = pd.DataFrame(rows, columns=["date", "series_id", "value"])
    save_long("worldbank", "wdi_selected", long, WB, meta={"wdi_selected": WB_IND})


def oecd():
    # la API SDMX de la OCDE devuelve 403 a scripts; se usa el espejo de DBnomics (dataset DSD_STES@DF_CLI)
    base = "https://api.db.nomics.world/v22/series/OECD/DSD_STES@DF_CLI"
    rows, off = [], 0
    while True:
        j = requests.get(base, params={"q": "confidence", "observations": 1, "limit": 1000, "offset": off},
                         headers=UA, timeout=180).json()["series"]
        for s in j["docs"]:
            rows += [(p, s["series_code"], v) for p, v in zip(s["period_start_day"], s["value"]) if v != "NA"]
        off += 1000
        if off >= j["num_found"]:
            break
    long = pd.DataFrame(rows, columns=["date", "series_id", "value"])
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    assert len(long) > 1000
    save_long("oecd", "cli_confidence", long, base)
    print("   ", check(long, "OECD confianza"))


def dataverse(doi, folder):
    j = requests.get(f"{DV}/datasets/:persistentId/", params={"persistentId": f"doi:{doi}"}, headers=UA, timeout=60).json()
    for f in j["data"]["latestVersion"]["files"]:
        fid, name = f["dataFile"]["id"], f["dataFile"]["filename"]
        if f["dataFile"]["filesize"] > 150e6:
            print(f"   omitido (>150 MB): {name}")
            continue
        download("crises", f"{folder}/{name}", f"{DV}/access/datafile/{fid}?format=original", min_bytes=10)


def main():
    run(lambda: download("jst", "JSTdatasetR6.dta", "https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.xlsx"),
        "JST R6")
    run(lambda: download("boe", "millennium_macro_data.xlsx",
                         "https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
                         "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"), "BoE millennium")
    for c in BIS_SETS:
        run(lambda c=c: bis(c), f"BIS {c}")
    run(ecb, "ECB SDMX")
    run(worldbank, "Banco Mundial WDI")
    run(oecd, "OCDE CLI (SDMX)")
    run(lambda: dataverse("10.7910/DVN/ECC9GE", "baron_verner_xiong"), "Baron-Verner-Xiong (Dataverse)")
    run(lambda: dataverse("10.7910/DVN/OCSCVL", "complex_crises"), "Complex Crises Database (Dataverse)")
    run(lambda: download("crises", "laeven_valencia/SBCD_stevedata.rda",
                         "https://github.com/svmiller/stevedata/raw/master/data/SBCD.rda", min_bytes=500),
        "Laeven-Valencia SBCD (vía paquete stevedata)")


if __name__ == "__main__":
    main()
