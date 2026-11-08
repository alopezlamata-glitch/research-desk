"""Quarterly Financial Report (Census): tablas financieras trimestrales. Prueba de disponibilidad para la etapa 1b de p01 (F7)."""

from _common import download, run

QFR = "https://www2.census.gov/econ/qfr/xls/"

def _name(y, q):
    ext = "xlsx" if (y, q) >= (22, 3) else "xls"  # el Census cambió de formato en 2022Q3
    return f"qfr{y:02d}q{q}f.{ext}"


# Cada archivo trae 5 trimestres: uno de cada 4 (2Q de cada año, hacia atrás desde 26q2) cubre 2005Q2–2026Q2 con solape de 1.
# F14a añade 06q3 (el primero con tablas NAICS) y 25q4/10q1 (los de F7).
FILES = [_name(y, 2) for y in range(26, 6, -1)] + [_name(6, 3), _name(25, 4), _name(10, 1)]


def main():
    for f in FILES:
        run(lambda f=f: download("census_qfr", f, QFR + f), f"QFR {f}")


if __name__ == "__main__":
    main()
