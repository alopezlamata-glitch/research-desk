"""F5a: cobertura de datos de la puerta de la etapa 2 (zona euro). Solo disponibilidad y recuentos: no usa la inversión
para estimar nada. Salida: output/tables/f5a_*.csv y output/tables/f5a_summary.md.

Uso: uv run python papers/p01-liquidity/code/data/f5a_coverage.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
LAKE = ROOT / "datalake" / "raw"
OUT = ROOT / "papers" / "p01-liquidity" / "output" / "tables"
COUNTRIES = ["AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"]
ZLB_THRESHOLDS = (1.0, 0.5)  # MRO mínimo del trimestre >= umbral => "sin ZLB"; 1,0 es la regla principal


def qpos(q):
    p = pd.Period(q, "Q")
    return p


def inv():
    d = pd.read_parquet(LAKE / "eurostat" / "P51G_CLV10_MEUR_SCA.parquet")
    d["country"] = d["series_id"].str.split(".").str[-1].replace({"EL": "GR"})
    d["q"] = d["date"].map(qpos)
    return d.dropna(subset=["value"])[["country", "q", "value"]]


def ecb(name):
    d = pd.read_parquet(LAKE / "ecb_country" / f"{name}.parquet")
    p = d["series_id"].str.split(".")
    d["country"] = p.str[2]
    d["m"] = pd.PeriodIndex(d["date"], freq="M")
    return d, p


def quarters_complete(months, need=3):
    """Trimestres con los 3 meses (need=3) o con el último mes (need=1)."""
    s = pd.Series(1, index=months)
    if need == 1:
        return {m.asfreq("Q") for m in months if m.month % 3 == 0}
    c = s.groupby(s.index.asfreq("Q")).size()
    return set(c[c == 3].index)


def zlb_quarters(thr):
    m = pd.read_csv(LAKE / "ecb" / "csv" / "MRO.csv", usecols=["TIME_PERIOD", "OBS_VALUE"])
    m["date"] = pd.to_datetime(m["TIME_PERIOD"])
    s = m.groupby("date")["OBS_VALUE"].last()
    daily = s.reindex(pd.date_range("1999-01-01", "2026-09-30")).ffill()
    qmin = daily.groupby(daily.index.to_period("Q")).min()
    return set(qmin[qmin >= thr].index)


def span(qs):
    qs = sorted(qs)
    if not qs:
        return "", "", 0, 0
    full = pd.period_range(qs[0], qs[-1], freq="Q")
    return str(qs[0]), str(qs[-1]), len(qs), len(full) - len(qs)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    di = inv()
    bsi, _ = ecb("BSI_nfc_loans")
    mir, p = ecb("MIR_rates_new")
    mir["maturity"], mir["dtype"], mir["amt"] = p.str[5], p.str[6], p.str[7]
    mirs, ps = ecb("MIR_rates_stock")

    sets = {
        "inversion": {c: set(g["q"]) for c, g in di.groupby("country")},
        "saldo_BSI": {c: quarters_complete(g["m"], 1) for c, g in bsi.groupby("country")},
        "MIR_tipo_nuevo_total": {c: quarters_complete(g.loc[(g.maturity == "A") & (g.dtype == "R") & (g.amt == "A"), "m"])
                                 for c, g in mir.groupby("country")},
        "MIR_volumen_nuevo_cat0": {c: quarters_complete(g.loc[(g.maturity == "A") & (g.dtype == "B") & (g.amt == "0"), "m"])
                                    for c, g in mir.groupby("country")},
        "MIR_volumen_por_fijacion": {c: quarters_complete(g.loc[(g.maturity != "A") & (g.dtype == "B"), "m"])
                                     for c, g in mir.groupby("country")},
        "MIR_tipo_saldos_total": {c: quarters_complete(g["m"][ps[g.index].str[5].eq("A") & ps[g.index].str[6].eq("R")])
                                  for c, g in mirs.groupby("country")},
    }
    cov = []
    for k, d in sets.items():
        for c in COUNTRIES:
            a, b, n, gaps = span(d.get(c, set()))
            cov.append({"serie": k, "pais": c, "primero": a, "ultimo": b, "n_trimestres": n, "huecos_internos": gaps})
    cov = pd.DataFrame(cov)
    cov.to_csv(OUT / "f5a_cobertura_por_pais.csv", index=False)

    # Número de series de volumen por periodo de fijación y país (nuevo negocio)
    fix = (mir[(mir.dtype == "B") & (mir.maturity != "A")].groupby("country")["series_id"].nunique()
           .reindex(COUNTRIES, fill_value=0).rename("series_volumen_por_fijacion"))
    fix.to_csv(OUT / "f5a_series_fijacion_por_pais.csv")

    # Clústeres por muestra sin ZLB: países con la serie completa en todos los trimestres de la muestra
    rows = []
    for thr in ZLB_THRESHOLDS:
        z = zlb_quarters(thr)
        for tag, qs in (("1999-2008 + 2022-23", {q for q in z if q.year <= 2008 or q.year >= 2022}),
                        ("2003-2008 + 2022-23 (desde el MIR)", {q for q in z if 2003 <= q.year <= 2008 or q.year >= 2022}),
                        ("2003-2008 (desde el MIR)", {q for q in z if 2003 <= q.year <= 2008}),
                        ("todo sin ZLB", z)):
            qs = {q for q in qs if q <= pd.Period("2023Q4", "Q")}
            for k, d in sets.items():
                ok = [c for c in COUNTRIES if qs and qs <= d.get(c, set())]
                rows.append({"mro_min": thr, "muestra": tag, "n_trimestres": len(qs), "serie": k,
                             "clusters_completos": len(ok), "paises": " ".join(ok)})
            # Clústeres con inversión + saldo + volumen (todo lo construible; falta la cuota por fijación)
            both = [c for c in COUNTRIES if qs and all(qs <= sets[k].get(c, set())
                                                       for k in ("inversion", "saldo_BSI", "MIR_volumen_nuevo_cat0"))]
            rows.append({"mro_min": thr, "muestra": tag, "n_trimestres": len(qs), "serie": "inversion+saldo+volumen_cat0",
                         "clusters_completos": len(both), "paises": " ".join(both)})
    cl = pd.DataFrame(rows)
    cl.to_csv(OUT / "f5a_clusters.csv", index=False)

    # Muestra mínima viable con MIR (desde 2003Q1): el MIR no existe antes
    z = zlb_quarters(1.0)
    qs_mir = {q for q in z if q >= pd.Period("2003Q1", "Q") and q <= pd.Period("2008Q4", "Q")} | \
             {q for q in z if q >= pd.Period("2022Q1", "Q") and q <= pd.Period("2023Q4", "Q")}
    # Choques JK (BCE, mensual): cobertura de trimestres sin ZLB
    jk = pd.read_csv(LAKE / "shocks" / "jarocinski_karadi" / "ecb_202310" / "shocks" / "shocks_ecb_mpd_me_m.csv")
    jk["m"] = pd.to_datetime({"year": jk.year, "month": jk.month, "day": 1}).dt.to_period("M")
    jk["q"] = jk["m"].dt.asfreq("Q")
    full = quarters_complete(jk["m"])
    jq = jk.groupby("q")[["MP_median", "CBI_median"]].agg(lambda s: (s != 0).sum())
    sh = []
    for thr in ZLB_THRESHOLDS:
        z = zlb_quarters(thr)
        zz = {q for q in z if q <= pd.Period("2023Q4", "Q")}
        sh.append({"mro_min": thr, "trimestres_sin_zlb": len(zz), "con_choque_completo": len(zz & full),
                   "con_MP_distinto_de_0": int(sum(jq.loc[q, "MP_median"] > 0 for q in zz if q in jq.index)),
                   "con_CBI_distinto_de_0": int(sum(jq.loc[q, "CBI_median"] > 0 for q in zz if q in jq.index)),
                   "primero_JK": str(jk["m"].min()), "ultimo_JK": str(jk["m"].max())})
    pd.DataFrame(sh).to_csv(OUT / "f5a_choques_jk.csv", index=False)

    lines = ["# F5a: resumen generado por `code/data/f5a_coverage.py`", "",
             f"Trimestres de la muestra sin ZLB y con MIR (2003-08 y 2022-23, MRO>=1): {len(qs_mir)}", "",
             "## Series de volumen por periodo de fijación por país (nuevo negocio, MIR)", "",
             fix.to_frame().to_markdown(), "", "## Clústeres", "", cl.drop(columns="paises").to_markdown(index=False), "",
             "## Choques JK", "", pd.DataFrame(sh).to_markdown(index=False), ""]
    (OUT / "f5a_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
