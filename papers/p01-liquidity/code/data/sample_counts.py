"""Recuentos exactos de la muestra de PREREG_DRAFT §6 → data/clean/SAMPLE_COUNTS.md.

No estima nada ni mira la inversión como resultado: solo cuenta observaciones de choque y estado.
Uso: uv run python papers/p01-liquidity/code/data/sample_counts.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"
ZLB = 0.25  # ffr_t < ZLB se excluye
COVID = ("2019Q1", "2021Q4")  # se excluye
FIRST, LAST = "1988Q2", "2023Q4"  # 1988Q2: s_{t-1} necesita 12 trimestres de Z.1 (empieza en 1985Q1)


def panel() -> pd.DataFrame:
    df = pd.read_parquet(CLEAN / "stage1_us.parquet").set_index("quarter")
    df.index = pd.PeriodIndex(df.index, freq="Q")
    lg = np.log(df["liq_broad_debt"])
    # s_t = log(liq/deuda)_t − media de los 12 trimestres anteriores (hacia atrás, sin t); NaN si falta alguno
    df["s"] = lg - lg.shift(1).rolling(12).mean()
    df["s_lag"], df["dsr_lag"] = df["s"].shift(1), df["dsr_nfc"].shift(1)
    return df


def sample(df: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    """Muestra principal y cascada de exclusiones (el orden solo afecta a la tabla de cascada)."""
    steps = []
    d = df.loc[FIRST:LAST]
    steps.append((f"{FIRST}–{LAST}", len(d)))
    d = d[d["ffr"] >= ZLB]
    steps.append((f"sin ZLB (`ffr` < {ZLB})", len(d)))
    d = d[(d.index < pd.Period(COVID[0], "Q")) | (d.index > pd.Period(COVID[1], "Q"))]
    steps.append((f"sin {COVID[0]}–{COVID[1]}", len(d)))
    d = d[d["mps_bs23_orth"].notna()]
    steps.append(("con `mps_bs23_orth` no NaN", len(d)))
    d = d[d["s_lag"].notna()]
    steps.append(("con `s_{t-1}` definido", len(d)))
    return d, steps


def cells(d: pd.DataFrame, state: pd.Series, restricted: pd.Series) -> pd.DataFrame:
    eps = d["mps_bs23_orth"]
    sign = pd.Series(np.select([eps > 0, eps < 0], ["ε>0 (subida)", "ε<0 (bajada)"], "ε=0"), index=d.index)
    est = pd.Series(np.where(restricted, "restringido", "holgado"), index=d.index)
    t = pd.crosstab(est, sign).reindex(["restringido", "holgado"])
    t["total"] = t.sum(axis=1)
    t.loc["total"] = t.sum()
    return t


def md(t: pd.DataFrame) -> str:
    head = "| estado | " + " | ".join(map(str, t.columns)) + " |\n|---|" + "---|" * len(t.columns) + "\n"
    return head + "\n".join(f"| {i} | " + " | ".join(str(int(v)) for v in r) + " |" for i, r in t.iterrows()) + "\n"


def main() -> None:
    df = panel()
    d, steps = sample(df)
    med_s = d["s_lag"].median()
    liq = cells(d, d["s_lag"], d["s_lag"] < med_s)

    dd = d[d["dsr_lag"].notna()]
    med_d = dd["dsr_lag"].median()
    dsr = cells(dd, dd["dsr_lag"], dd["dsr_lag"] > med_d)

    n_g = int(d["stbl_short_share"].notna().sum())
    n_g_dsr = int(dd["stbl_short_share"].notna().sum())
    out = """# Recuentos de la muestra de PREREG_DRAFT §6

Generado por `code/data/sample_counts.py` sobre `data/clean/stage1_us.parquet` (Z.1 2026-09-11, FRED 2026-11-04). No se ha
estimado nada. Fecha t = trimestre del choque; el estado se mide en t−1.

**Definiciones.** `s_t = log(liq_broad_debt_t) − media(log(liq_broad_debt_{t−1…t−12}))`.
Restringido (liquidez) = `s_{t−1}` < mediana de `s_{t−1}` **en la muestra**; (DSR) = `dsr_nfc_{t−1}` > mediana de `dsr_nfc_{t−1}`
en la muestra con DSR. Con N impar, la observación mediana queda en "holgado". Choque = `mps_bs23_orth` (suma trimestral).
**No** se imponen aquí las condiciones del resultado ȳ_t ni de los controles: están definidos en toda la muestra (inversión desde 1947,
PIB, deflactor, `y2_mean`, `ebp` desde 1985), de modo que no recortan.

## Cascada (muestra principal)
| paso | N |
|---|---|
""" + "\n".join(f"| {k} | {v} |" for k, v in steps) + f"""

Trimestres excluidos por ZLB dentro de {FIRST}–{LAST}: {", ".join(map(str, sorted(set(df.loc[FIRST:LAST].index[df.loc[FIRST:LAST, "ffr"] < ZLB]))))}.

## Estado de liquidez (`s1_liq`): N = {len(d)}, mediana de s_{{t−1}} = {med_s:.4f}
{md(liq)}
## Estado DSR (`s1_dsr`, desde 1999Q2): N = {len(dd)}, mediana de dsr_{{t−1}} = {med_d:.3f}
{md(dsr)}
## Cobertura de la medida de g (E.2, `stbl_short_share`, 1997Q2–2017Q2)
Observaciones de la muestra principal con `stbl_short_share` disponible: **{n_g}** (de {len(d)}); en la muestra DSR: **{n_g_dsr}**.
"""
    (CLEAN / "SAMPLE_COUNTS.md").write_text(out, encoding="utf-8")
    print(f"escrito {CLEAN / 'SAMPLE_COUNTS.md'}")


if __name__ == "__main__":
    main()
