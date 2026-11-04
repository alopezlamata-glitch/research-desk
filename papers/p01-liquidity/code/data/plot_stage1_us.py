"""Un gráfico por serie limpia de stage1_us.parquet → output/figures/data_<serie>.png (los errores se ven en figuras)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PAPER = Path(__file__).resolve().parents[2]
OUT = PAPER / "output" / "figures"
SKIP = {"date", "quarter", "t", "bs25_quarter_partial"}


def main() -> None:
    df = pd.read_parquet(PAPER / "data" / "clean" / "stage1_us.parquet")
    df["t"] = pd.PeriodIndex(df["quarter"], freq="Q").to_timestamp()
    OUT.mkdir(parents=True, exist_ok=True)
    for c in df.columns.difference(SKIP):
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.plot(df["t"], df[c], lw=1)  # NaN corta la línea: los huecos se ven como huecos
        ax.set_title(c, fontsize=9)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(OUT / f"data_{c}.png", dpi=90)
        plt.close(fig)


if __name__ == "__main__":
    main()
