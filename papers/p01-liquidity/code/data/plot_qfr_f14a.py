"""F14a: figura de la cuota de deuda bancaria por celda (output/figures/data_qfr_bank_share.png)."""

import matplotlib

matplotlib.use("Agg")
import build_qfr_f14a as b
import matplotlib.pyplot as plt
import pandas as pd

c = pd.read_parquet(b.PARQUET if hasattr(b, "PARQUET") else b.CLEAN / "qfr_cells.parquet")
c["q"] = pd.PeriodIndex(c["quarter"], freq="Q").to_timestamp()
fig, ax = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
m = c[(c["size"] == "ALL") & c["ind"].isin(b.MFG) & (c["quarter"] >= "2006Q3")]
for _, g in m.groupby("ind"):
    ax[0].plot(g["q"], g["bank_share"], lw=0.8, alpha=0.7)
ax[0].set(title="Manufacturas, todos los tamaños (26 industrias)", ylabel="deuda bancaria / deuda total")
for sz, col, lab in [("LT25", "tab:red", "<25 M (hasta 2019Q2)"), ("GE25", "tab:blue", "≥25 M (hasta 2019Q2)"),
                     ("LT50", "tab:orange", "<50 M (desde 2019Q2)"), ("GE50", "tab:green", "≥50 M (desde 2019Q2)")]:
    g = c[(c["size"] == sz) & c["ind"].isin(b.MFG) & (c["quarter"] >= "2006Q3")]
    g = g[g["quarter"] <= "2019Q2"] if sz.endswith("25") else g[g["quarter"] >= "2019Q2"]
    ax[1].plot(*zip(*g.groupby("q")["bank_share"].median().items()), color=col, label=lab)
ax[1].set(title="Mediana entre industrias por tamaño (cambia el corte en 2019)")
ax[1].legend()
fig.tight_layout()
out = b.OUT / "figures"
out.mkdir(exist_ok=True)
fig.savefig(out / "data_qfr_bank_share.png", dpi=110)
