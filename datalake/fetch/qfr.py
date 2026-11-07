"""Quarterly Financial Report (Census): tablas financieras trimestrales. Prueba de disponibilidad para la etapa 1b de p01 (F7)."""

from _common import download, run

QFR = "https://www2.census.gov/econ/qfr/xls/"
FILES = ["qfr26q2f.xlsx", "qfr25q4f.xlsx", "qfr10q1f.xls"]  # último, uno reciente y uno de 2010


def main():
    for f in FILES:
        run(lambda f=f: download("census_qfr", f, QFR + f), f"QFR {f}")


if __name__ == "__main__":
    main()
