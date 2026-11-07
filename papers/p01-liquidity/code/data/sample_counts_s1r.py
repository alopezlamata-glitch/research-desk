"""F7: D1/D2 de la etapa 1 rediseñada → data/clean/SAMPLE_COUNTS_S1R.md.

No estima nada ni mira la inversión: solo cuenta trimestres de choque por estado de D_{t−1}.
Estado = el de la etapa 1: restringido si `s_{t−1}` < mediana de `s_{t−1}` en la muestra (con N impar la mediana va a "holgado").
La mediana se fija en la muestra completa de cada choque; la fila "sin Volcker" solo quita trimestres, no redefine el estado.
Uso: uv run python papers/p01-liquidity/code/data/sample_counts_s1r.py
"""

from pathlib import Path

import pandas as pd

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"
VOLCKER = ("1979Q4", "1982Q4")
CONCENTRATION = 0.75  # aviso si Volcker cae con más de esta fracción en un solo estado


def panel() -> pd.DataFrame:
    df = pd.read_parquet(CLEAN / "stage1r_us.parquet").set_index("quarter")
    df.index = pd.PeriodIndex(df.index, freq="Q")
    return df


def samples(df: pd.DataFrame) -> dict[str, tuple[pd.DataFrame, str]]:
    """Muestra de cada choque: (datos con estado, columna de choque)."""
    rr = df[df["in_rr_sample"] & df["s_lag"].notna() & df["rr_shock"].notna()]
    last = rr.index.max()
    bs = df.loc["1988Q1":last]
    bs = bs[bs["mps_bs23_orth"].notna() & bs["s_lag"].notna()]
    return {"rr_shock": (rr, "rr_shock"), "mps_bs23_orth": (bs, "mps_bs23_orth")}


def with_state(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["estado"] = (d["s_lag"] < d["s_lag"].median()).map({True: "restringido", False: "holgado"})
    d["volcker"] = (d.index >= pd.Period(VOLCKER[0], "Q")) & (d.index <= pd.Period(VOLCKER[1], "Q"))
    return d


def table(d: pd.DataFrame, col: str) -> pd.DataFrame:
    g = d.groupby("estado")[col]
    t = pd.DataFrame({"N": g.size(), "choque≠0": g.apply(lambda x: int((x != 0).sum())), "Σ|ε|": g.apply(lambda x: x.abs().sum())})
    return t.reindex(["restringido", "holgado"]).fillna(0)


def md(t: pd.DataFrame) -> str:
    rows = [f"| {i} | {int(r['N'])} | {int(r['choque≠0'])} | {r['Σ|ε|']:.3f} |" for i, r in t.iterrows()]
    return "| estado | N | trimestres con ε≠0 | Σ\\|ε\\| |\n|---|---|---|---|\n" + "\n".join(rows) + "\n"


def volcker_split(d: pd.DataFrame, col: str) -> tuple[pd.Series, pd.Series]:
    v = d[d["volcker"]]
    return v["estado"].value_counts().reindex(["restringido", "holgado"]).fillna(0).astype(int), v.groupby("estado")[col].apply(lambda x: x.abs().sum())


def main() -> None:
    df = panel()
    out = ["# Recuentos D1/D2 de la etapa 1 rediseñada (F7)\n",
           ("Generado por `code/data/sample_counts_s1r.py` sobre `data/clean/stage1r_us.parquet`. No se ha estimado nada ni se ha mirado la "
            "inversión. Estado: `s_{t−1}` frente a la mediana de la muestra (ver docstring); Volcker = 1979Q4–1982Q4 (13 trimestres).\n")]
    flags = []
    for d, col in samples(df).values():
        d = with_state(d)
        out.append(f"## Choque `{col}`: {d.index.min()}–{d.index.max()}, N = {len(d)}, mediana de s_(t−1) = {d['s_lag'].median():.4f}\n")
        out.append("**Con Volcker**\n\n" + md(table(d, col)))
        out.append("**Sin 1979Q4–1982Q4**\n\n" + md(table(d[~d["volcker"]], col)))
        n, a = volcker_split(d, col)
        tot = table(d, col)["Σ|ε|"]
        out.append(f"Trimestres de Volcker por estado: restringido {n['restringido']}, holgado {n['holgado']} (de {int(n.sum())}). "
                   f"Σ|ε| de Volcker: restringido {a.get('restringido', 0):.3f} de {tot['restringido']:.3f}; "
                   f"holgado {a.get('holgado', 0):.3f} de {tot['holgado']:.3f}.\n")
        if n.sum() and n.max() / n.sum() > CONCENTRATION:
            flags.append(f"{col}: {n.max()} de {n.sum()} trimestres de Volcker en '{n.idxmax()}'")
    out.append("## Aviso de concentración (Volcker en un solo estado, umbral > 75 %)\n\n" + ("**SÍ**: " + "; ".join(flags) if flags else "No.") + "\n")
    (CLEAN / "SAMPLE_COUNTS_S1R.md").write_text("\n".join(out), encoding="utf-8")
    print(f"escrito {CLEAN / 'SAMPLE_COUNTS_S1R.md'}")


if __name__ == "__main__":
    main()
