"""Shocks identificados: Bauer-Swanson (ago-2025 y dic-2023), USMPD, Jarociński-Karadi (Fed y BCE)."""

from _common import download, run

SF = "https://www.frbsf.org/wp-content/uploads/"
GH = "https://raw.githubusercontent.com/marekjarocinski/"
WB = "http://web.archive.org/web/20250121051008id_/https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx"


def main():
    # Verificado: el xlsx de la web (datos hasta 2023-12-13) es idéntico byte a byte a la copia de Wayback
    # del 2025-01-21, es decir, es el vintage dic-2023. La actualización de ago-2025 está en el zip (mps.csv...).
    run(lambda: download("shocks", "bauer_swanson/monetary-policy-surprises-data_vintage2023-12.xlsx",
                         SF + "monetary-policy-surprises-data.xlsx", "2023-12 (xlsx web, descargado 2026-11)"),
        "Bauer-Swanson xlsx dic-2023")
    run(lambda: download("shocks", "bauer_swanson/monetary-policy-surprises_vintage2025-08.zip",
                         SF + "monetary-policy-surprises.zip", "2025-08 (según la web del FRBSF)"),
        "Bauer-Swanson zip ago-2025")
    run(lambda: download("shocks", "bauer_swanson/monetary-policy-surprises-data_wayback20250121.xlsx",
                         WB, "2023-12 (Wayback 2025-01-21, control)"), "Bauer-Swanson Wayback (control)")
    run(lambda: download("shocks", "usmpd/USMPD.xlsx", SF + "USMPD.xlsx"), "USMPD xlsx")
    run(lambda: download("shocks", "usmpd/usmpd-chart1-fomc.csv", SF + "usmpd-chart1-fomc.csv", min_bytes=100),
        "USMPD chart1")
    run(lambda: download("shocks", "usmpd/usmpd-chart2-time-series.csv", SF + "usmpd-chart2-time-series.csv",
                         min_bytes=100), "USMPD chart2")
    fed = GH + "jkshocks_update_fed_202401/main/"
    for f in ["shocks_fed_jk_m.csv", "shocks_fed_jk_t.csv", "fomc_surprises_jk.csv", "readme.txt"]:
        run(lambda f=f: download("shocks", f"jarocinski_karadi/fed_202401/{f}", fed + f, min_bytes=100),
            f"JK Fed {f}")
    ecb = GH + "jkshocks_update_ecb_202310/main/"
    for f in ["shocks/shocks_ecb_mpd_me_d.csv", "shocks/shocks_ecb_mpd_me_m.csv",
              "source_data/Dataset_EA-MPD.xlsx", "readme.txt"]:
        run(lambda f=f: download("shocks", f"jarocinski_karadi/ecb_202310/{f}", ecb + f, min_bytes=100),
            f"JK BCE {f}")


if __name__ == "__main__":
    main()
