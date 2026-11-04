"""FRED (fredgraph.csv, sin clave): núcleo EE. UU. de p01 + extras. Series inexistentes -> ROTO en el log."""

import io
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from _common import check, get, save, save_long

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

SERIES = {
    "actividad_precios": """GDPC1 GDP GDPPOT GDPDEF PCECC96 PCE PCEPI PCEPILFE CPIAUCSL CPILFESL GPDIC1 GPDI PNFIC1
        PRFIC1 UNRATE PAYEMS CIVPART INDPRO NROU CLF16OV HOUST RSAFS DSPIC96 PSAVERT A939RX0Q048SBEA""",
    "politica": """FEDFUNDS DFF EFFR IORB IOER SOFR DFEDTARU DFEDTARL DGS3MO DGS6MO DGS1 DGS2 DGS5 DGS7 DGS10 DGS20
        DGS30 TB3MS GS1 GS10 T10Y2Y T10Y3M DFII10 T10YIE T5YIFR WALCL WRESBAL RRPONTSYD RRPONTTLD WTREGEN
        WSHOSHO WSHOMCB M1SL M2SL BOGMBASE TOTRESNS CURRCIR SHADOWRATE""",
    "deuda": """GFDEBTN GFDEGDQ188S FYGFDPUN FYOINT A091RC1Q027SBEA FYONET MTSO133FMS FGEXPND FGRECPT
        BCNSDODNS CMDEBT HHMSDODNS TDSP FODSP CDSP MDSP DODFS TOTALSL REVOLSL MORTGAGE30US MORTGAGE15US
        GFDEBTNQ FDHBFIN FDHBFRBN FDHBPIN MVMTD027MNFRBDAL EXPGSCA FEDDT QBPBSTAS NCBDBIQ027S
        TCMDO NCBCMDPMVCE ASTLL ASTDSL""",
    "banca": """TOTBKCR LOANS BUSLOANS REALLN CONSUMER DPSACBW027SBOG TLAACBW027SBOG TOTLL
        DRTSCILM DRTSCIS DRTSSP DRTSCLCC DRSDCILM SUBLPDHMSNQ DRALACBN DRBLACBS DRCCLACBS DRSFRMACBS
        DRCLACBS CORALACBN CORBLACBS CORCCACBS USNIM TOTCI EQTA
        TLAACBM027SBOG DPSACBM027SBOG H8B1058NCBCMG""",
    "condiciones_confianza": """NFCI ANFCI STLFSI4 BAA AAA BAA10Y AAA10Y BAMLH0A0HYM2 BAMLC0A0CM VIXCLS VXOCLS
        UMCSENT MICH EXPINF1YR EXPINF10YR T10YIE USEPUINDXD USEPUINDXM TEDRATE USSLIND CFNAI GSCPI
        STLFSI2 DTWEXBGS DEXUSEU SP500 WILL5000PR NASDAQCOM DCOILWTICO USREC USRECM""",
}


def one(sid):
    try:
        r = get(URL + sid, timeout=60)
        df = pd.read_csv(io.StringIO(r.text))
        if df.shape[1] != 2:
            raise ValueError("formato inesperado")
        df.columns = ["date", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if df["value"].notna().sum() == 0:
            raise ValueError("serie vacía")
        df.insert(1, "series_id", sid)
        return sid, r.content, df, None
    except Exception as e:  # noqa: BLE001
        return sid, None, None, str(e)[:120]


def main():
    ok, bad = [], []
    for group, txt in SERIES.items():
        ids = list(dict.fromkeys(txt.split()))
        with ThreadPoolExecutor(6) as ex:
            res = list(ex.map(one, ids))
        frames = []
        for sid, content, df, err in res:
            if err:
                bad.append((sid, err))
                continue
            save("fred", f"csv/{sid}.csv", content, URL + sid, vintage=pd.Timestamp.today().date().isoformat())
            frames.append(df)
            ok.append(sid)
        if frames:
            long = pd.concat(frames)
            save_long("fred", group, long, URL + "<id>")
            print(check(long, group))
    print("OK", len(ok), "ROTAS", bad)


if __name__ == "__main__":
    sys.exit(main())
