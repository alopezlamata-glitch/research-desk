"""Zona euro por país (F5a de p01): inversión trimestral (Eurostat) y préstamos a SNF (BCE: MIR y BSI).

Por país: FBCF (P51G, Eurostat namq_10_gdp), saldo de préstamos de las IFM a SNF (BSI), tipos del MIR de nuevo negocio
(total y por periodo de fijación) y volúmenes del MIR de nuevo negocio. Los volúmenes por periodo de fijación solo existen
para el agregado U2; por país el MIR da solo el total (y por tramo de importe): ver `datalake/CATALOG.md`.
"""

import csv
import io

import pandas as pd
from _common import get, run, save_long

COUNTRIES = ["AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"]
ECB = "https://data-api.ecb.europa.eu/service/data/"
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"


def _ecb(flow, key):
    url = f"{ECB}{flow}/{key}?startPeriod=1999-01&format=csvdata"
    rows = list(csv.DictReader(io.StringIO(get(url).text)))
    return url, pd.DataFrame({"date": [r["TIME_PERIOD"] for r in rows], "series_id": [r["KEY"] for r in rows],
                              "value": [pd.to_numeric(r["OBS_VALUE"], errors="coerce") for r in rows]})


def _eurostat(unit, sadj):
    parts = []
    for c in COUNTRIES:
        geo = "EL" if c == "GR" else c  # Eurostat usa EL para Grecia
        url = f"{EUROSTAT}namq_10_gdp/Q.{unit}.{sadj}.P51G.{geo}?startPeriod=1999-Q1&format=SDMX-CSV"
        try:
            df = pd.read_csv(io.StringIO(get(url).text))
        except Exception as e:  # noqa: BLE001
            print(f"[SIN DATOS] P51G {unit} {sadj} {c}: {str(e)[:60]}")
            continue
        parts.append(pd.DataFrame({"date": df["TIME_PERIOD"], "series_id": f"P51G.{unit}.{sadj}.{c}",
                                   "value": df["OBS_VALUE"]}))
    return f"{EUROSTAT}namq_10_gdp/Q.{unit}.{sadj}.P51G.<geo>", pd.concat(parts)


def main():
    for unit, sadj in (("CLV10_MEUR", "SCA"), ("CLV10_MEUR", "NSA"), ("CP_MEUR", "SCA")):
        run(lambda u=unit, s=sadj: _save_es(u, s), f"Eurostat P51G {unit} {sadj}")
    keys = {"MIR_rates_new": "M.{c}.B.A2A....2240.EUR.N", "MIR_rates_stock": "M.{c}.B.A20....2240.EUR.O",
            "BSI_nfc_loans": "M.{c}.N.A.A20.A.1.U2.2240.Z01.E"}
    for name, k in keys.items():
        flow = "BSI" if name.startswith("BSI") else "MIR"
        parts, url = [], ""
        for c in COUNTRIES:
            try:
                url, d = _ecb(flow, k.format(c=c))
                parts.append(d)
            except Exception as e:  # noqa: BLE001
                print(f"[ROTO]  {name} {c}: {str(e)[:100]}")
        run(lambda n=name, p=parts, u=url: save_long("ecb_country", n, pd.concat(p), u.replace("AT", "<c>", 1)),
            f"BCE por país {name}")


def _save_es(unit, sadj):
    url, d = _eurostat(unit, sadj)
    save_long("eurostat", f"P51G_{unit}_{sadj}", d, url)


if __name__ == "__main__":
    main()
