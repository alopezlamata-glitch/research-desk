"""F14a: celdas industria × tamaño del QFR (Census) para la puerta de la etapa 1b de p01.

Lee las 23 vintages de `datalake/raw/census_qfr/` (comprobando su sha256 contra el MANIFEST), las empalma (gana la vintage
más reciente de cada trimestre) y escribe:
  - data/clean/qfr_cells.parquet  — celda × trimestre con las variables del diccionario (QFR_DICTIONARY.md)
  - output/F14A_G_TABLE.csv       — una fila por celda candidata: cobertura 2006Q3–2026Q2, huecos, ruptura de empalme
  - output/F14A_G_SUMMARY.csv     — G por escenario de ventana
No estima nada con la inversión ni mira su respuesta a choques: solo construcción y descriptivos.
Uso: uv run python papers/p01-liquidity/code/data/build_qfr_f14a.py
"""

import csv
import glob
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd
import qfr_read

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers" / "p01-liquidity"
RAW = ROOT / "datalake" / "raw" / "census_qfr"
MANIFEST = ROOT / "datalake" / "MANIFEST.csv"
CLEAN, OUT = PAPER / "data" / "clean", PAPER / "output"
BREAK = 0.15  # |Δlog activos| entre dos vintages en el trimestre solapado a partir del cual se declara ruptura (mediana de revisión ≈ 0,01)
WINDOW = pd.period_range("2006Q3", "2026Q2", freq="Q")  # 80 trimestres: desde las primeras tablas NAICS hasta la última vintage

MFG = ["Food", "Beverage and Tobacco Products", "Textile Mills and Textile Product Mills", "Apparel and Leather Products",
       "Wood Products", "Paper", "Printing and Related Support Activities", "Petroleum and Coal Products",
       "Basic Chemicals, Resins, and Synthetics", "Pharmaceuticals and Medicines", "All Other Chemicals",
       "Plastics and Rubber Products", "Nonmetallic Mineral Products", "Iron, Steel, and Ferroalloys", "Nonferrous Metals",
       "Foundries", "Fabricated Metal Products", "Machinery", "Computer and Peripheral Equipment", "Communications Equipment",
       "All Other Electronic Products", "Electrical Equipment, Appliances, and Components", "Motor Vehicles and Parts",
       "Aerospace Products and Parts", "Furniture and Related Products", "Miscellaneous Manufacturing"]
NONMFG = ["All Mining", "Wholesale Trade, Durable Goods", "Wholesale Trade, Nondurable Goods", "Food and Beverage Stores",
          "General Merchandise and Clothing Stores", "All Other Retail Trade", "Motion Picture and Sound Recording Industries",
          "Publishing Industries", "Broadcasting and Content Providers", "Telecommunications", "All Other Information",
          "Computer Systems Design and Related Services", "Management and Technical Consulting Services",
          "Scientific Research and Development Services", "All Other Professional and Technical Services"]
# nombres que cambian con NAICS 2022 (vintage 2025Q2 en adelante): se unen y se mide la ruptura en el trimestre solapado
RENAME = {"Pharmaceuticals and Medicine": "Pharmaceuticals and Medicines",
          "Broadcasting, except Internet": "Broadcasting and Content Providers",
          "Publishing Industries, except Internet": "Publishing Industries",
          "Clothing and General Merchandise Stores": "General Merchandise and Clothing Stores"}
SIZE = {"All Total Asset Sizes": "ALL", "Total Assets Under $25 Million": "LT25", "Total Assets $25 Million and Over": "GE25",
        "Total Assets Under $50 Million": "LT50", "Total Assets $50 Million and Over": "GE50"}

# partida canónica -> (tabla 0/1, patrones de nombre). Los nombres cambian entre vintages (ver diccionario).
ITEMS = {
    "total_assets": "Total Assets", "net_ppe": "Net property, plant, and equipment", "equity": "Stockholders' equity",
    "cash_sec": "Total cash, U S [Gg]overnment and other securities", "dep": "Depreciation, depletion, and amortization of property",
    "interest_exp": "Interest expense", "sales": "Net sales, receipts, and operating revenues",
}
BANK = ["Short-term debt, original maturity of 1 year or less: a Loans from banks",
        "(?:Current portion of long-term debt, due in 1 year or less|Installments, due in 1 year or less, on long-term debt): a Loans from banks",
        "Long-term debt, due in more than 1 year: a Loans from banks"]
DEBT_NONBANK = ["Short-term debt, original maturity of 1 year or less: [bc] ",
                "(?:Current portion of long-term debt|Installments, due in 1 year or less, on long-term debt)(?:, due in 1 year or less)?: [bc] ",
                "Long-term debt, due in more than 1 year: [bc] "]


def verify_manifest(files):
    """rawhash local: cada archivo leído tiene fila en el MANIFEST del datalake y coincide su sha256."""
    with MANIFEST.open(encoding="utf-8") as f:
        rows = {(r["path"], r["sha256"]) for r in csv.DictReader(f)}
    for p in files:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert (f"raw/census_qfr/{p.name}", h) in rows, f"{p.name} sin fila coincidente en datalake/MANIFEST.csv"


def parse_group(g):
    g = re.sub(r"\s+\d$", "", g)
    m = re.search(r"(All Total Asset Sizes|Total Assets .*)$", g)
    ind, size = (g[:m.start()], m[1]) if m else (g, "All Total Asset Sizes")
    ind = re.sub(r"\s+\d$", "", ind.strip())
    return RENAME.get(ind, ind), SIZE.get(re.sub(r"\s+\d$", "", size.strip()), "OTHER:" + size)


def vintages():
    files = sorted(Path(p) for p in glob.glob(str(RAW / "qfr*f.xls*")))
    verify_manifest(files)
    out = []
    for p in files:
        d = qfr_read.long_table(p)
        yq = re.search(r"qfr(\d\d)q(\d)", p.name)
        d["vintage"] = pd.Period(f"20{yq[1]}Q{yq[2]}", "Q")
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    gm = d[["group"]].drop_duplicates()
    gm[["ind", "size"]] = [parse_group(g) for g in gm["group"]]
    d = d.merge(gm, on="group")
    d["quarter"] = pd.PeriodIndex(d["quarter"], freq="Q")
    d["bs"] = d["table"].str.endswith("_1")
    return d


def pick(d, pattern, bs):
    x = d[(d.bs == bs) & d["item"].str.contains(pattern, regex=True)]
    # una partida por (celda, trimestre, vintage): si el patrón casa varias (a/b/c), se suman
    return x.groupby(["ind", "size", "vintage", "quarter"], as_index=False)["value"].sum()


def variables(d):
    """Celda × trimestre × vintage con las variables canónicas."""
    cols = {k: pick(d, "^" + v, k != "dep" and k != "interest_exp" and k != "sales").rename(columns={"value": k})
            for k, v in ITEMS.items()}
    bank = sum(pick(d, "^" + b, True).set_index(["ind", "size", "vintage", "quarter"])["value"] for b in BANK)
    nonbank = sum(pick(d, "^" + b, True).set_index(["ind", "size", "vintage", "quarter"])["value"] for b in DEBT_NONBANK)
    v = None
    for df in cols.values():
        v = df if v is None else v.merge(df, on=["ind", "size", "vintage", "quarter"], how="outer")
    v = v.set_index(["ind", "size", "vintage", "quarter"])
    v["bank_debt"] = bank
    v["debt"] = bank + nonbank
    v = v.reset_index().sort_values(["ind", "size", "vintage", "quarter"])
    v["bank_share"] = v["bank_debt"] / v["debt"]
    # proxy de inversión (el QFR no trae capex): ΔPPE neto + depreciación, sobre PPE neto rezagado. Se calcula DENTRO de cada
    # vintage para no mezclar niveles revisados; solo con trimestres consecutivos.
    g = v.groupby(["ind", "size", "vintage"])
    lag = g["net_ppe"].shift(1)
    consecutive = (v["quarter"] - g["quarter"].shift(1)).map(lambda x: x.n if pd.notna(x) else 0) == 1
    v["inv_proxy"] = ((v["net_ppe"] - lag + v["dep"]) / lag).where(consecutive)
    return v


def stitch(v):
    """Gana la vintage más reciente de cada (celda, trimestre); devuelve también la ruptura en cada empalme."""
    v = v.sort_values("vintage")
    cur = v.groupby(["ind", "size", "quarter"], as_index=False).last()  # último valor NO nulo de cada variable
    first = v.drop_duplicates(["ind", "size", "quarter"], keep="first")
    both = cur.merge(first, on=["ind", "size", "quarter"], suffixes=("_new", "_old"))
    both = both[both["vintage_new"] != both["vintage_old"]]
    seam = both.assign(jump=np.log(both["total_assets_new"] / both["total_assets_old"]))[["ind", "size", "quarter", "jump"]]
    return cur.drop(columns="vintage"), seam


def coverage(cur, seam):
    rows = []
    for (ind, size), g in cur[cur["size"].isin(SIZE.values())].groupby(["ind", "size"]):
        qs = set(g.loc[g["total_assets"].notna(), "quarter"]) & set(WINDOW)
        have = sorted(qs)
        # tramo continuo más largo dentro de la ventana
        best = run = 0
        for q in WINDOW:
            run = run + 1 if q in qs else 0
            best = max(best, run)
        sj_q = seam[(seam["ind"] == ind) & (seam["size"] == size)]
        sj = sj_q["jump"].abs()
        br = sorted(str(q) for q in sj_q[sj_q["jump"].abs() > BREAK]["quarter"]) if len(sj_q) else []
        rows.append({"industry": ind, "size": size, "breaks": ";".join(br), "sector": "mfg" if ind in MFG else "nonmfg" if ind in NONMFG else "aggregate",
                     "first_q": str(have[0]) if have else "", "last_q": str(have[-1]) if have else "", "n_quarters": len(qs),
                     "longest_run": best, "gaps_in_window": len(WINDOW) - len(qs) if have else len(WINDOW),
                     "max_seam_abs_log": sj.max() if len(sj) else np.nan})
    return pd.DataFrame(rows)


SCENARIOS = [  # (nombre, inicio, fin, tamaños admitidos para manufacturas, tamaño de no manufacturas)
    ("S1 literal: continuas 2006Q3–2026Q2 (cualquier tamaño fijo)", "2006Q3", "2026Q2", ["ALL", "LT25", "GE25", "LT50", "GE50"], ["GE50"]),
    ("S2 manuf. todos los tamaños + no manuf. ≥50 M", "2007Q2", "2026Q2", ["ALL"], ["GE50"]),
    ("S3 igual que S2, desde 2010Q2 (entran información y servicios profesionales)", "2010Q2", "2026Q2", ["ALL"], ["GE50"]),
    ("S4a manuf. por tamaño <25/≥25 M + no manuf. ≥50 M", "2006Q3", "2019Q2", ["LT25", "GE25"], ["GE50"]),
    ("S4b igual que S4a, desde 2010Q2 (entran información y servicios profesionales)", "2010Q2", "2019Q2", ["LT25", "GE25"], ["GE50"]),
    ("S5 manuf. por tamaño <50/≥50 M + no manuf. ≥50 M", "2019Q2", "2026Q2", ["LT50", "GE50"], ["GE50"]),
]


def scenarios(cur, seam):
    """G = celdas hoja sin solape con TODOS los trimestres de la ventana (sin huecos). Cada celda es industria × UNA definición de tamaño."""
    qs = {k: set(g.loc[g["total_assets"].notna(), "quarter"]) for k, g in cur.groupby(["ind", "size"])}
    brk = {k: set(g.loc[g["jump"].abs() > BREAK, "quarter"]) for k, g in seam.groupby(["ind", "size"])}
    out = []
    for name, s, e, msz, nsz in SCENARIOS:
        win = set(pd.period_range(s, e, freq="Q"))
        first = min(win)

        def cov(i, z, win=win):
            return win <= qs.get((i, z), set())

        def ok(i, z, win=win, first=first):  # cobertura completa y ninguna ruptura (|Δlog| > BREAK) en la ventana
            return cov(i, z, win) and not {q for q in brk.get((i, z), set()) if q in win and q != first}

        cand = [(i, z) for i in MFG for z in msz] + [(i, z) for i in NONMFG for z in nsz]
        sin = [c for c in cand if cov(*c)]
        cells = [c for c in cand if ok(*c)]
        out.append({"scenario": name, "start": s, "end": e, "T": len(win),
                    "G_cobertura": len(sin), "G_sin_rupturas": len(cells),
                    "G_mfg": sum(c[0] in MFG for c in cells), "G_nonmfg": sum(c[0] in NONMFG for c in cells)})
    return pd.DataFrame(out)


def main():
    d = vintages()
    v = variables(d)
    cur, seam = stitch(v)
    cov = coverage(cur, seam)
    cov.to_csv(OUT / "F14A_G_TABLE.csv", index=False)
    summ = scenarios(cur, seam)
    summ.to_csv(OUT / "F14A_G_SUMMARY.csv", index=False)
    cells = cur[cur["size"].isin(SIZE.values()) & cur["ind"].isin(MFG + NONMFG)].copy()
    cells["quarter"] = cells["quarter"].astype(str)
    cells["cell"] = cells["ind"] + " | " + cells["size"]
    cells.to_parquet(CLEAN / "qfr_cells.parquet", index=False)
    seam.assign(quarter=seam["quarter"].astype(str)).to_csv(OUT / "F14A_SEAMS.csv", index=False)
    print(summ.to_string())
    print(cov.groupby(["sector", "size"]).size())


if __name__ == "__main__":
    main()
