"""Shocks narrativos: Ramey / Ramey-Zubairy (UCSD) y Romer-Romer (Berkeley)."""

from _common import download, run

RA = "https://econweb.ucsd.edu/~vramey/research/"
RR = "https://eml.berkeley.edu/~cromer/"
RD = "https://eml.berkeley.edu/~dromer/papers/"

RAMEY = ["Ramey_Zubairy_replication_codes.zip", "Ramey_Govt_Public_Data.xls", "govdat3908.csv",
         "Ramey_HOM_monetary.zip", "Ramey_HOM_govtspending.zip", "Ramey_HOM_tax.zip", "ORZ-Data-and-Programs.zip"]
ROMER = {
    "monetary_shocks_appendix.xls": RR + "Data/Shocks/RomerandRomerDataAppendix.xls",
    "monetary_shocks_descriptions.pdf": RR + "Data/Shocks/RomerandRomerDataDescriptions.pdf",
    "intended_rate_data.xls": RR + "Data/Rates/RomerandRomerdata.xls",
    "FOMC_data.xls": RD + "FOMC_data.xls",
    "tax_DataSet.zip": RD + "DataSet.zip",
    "transfers_AEJMacro-2014-0348_data.zip": RR + "Data/Transfers/AEJMacro-2014-0348_Data and Programs.zip",
    "crises_data_programs.zip": RR + "Data/Crises/Romer&RomerCrisesDataandPrograms.zip",
}


def main():
    for f in RAMEY:
        run(lambda f=f: download("narrative", f"ramey/{f}", RA + f), f"Ramey {f}")
    for name, url in ROMER.items():
        run(lambda n=name, u=url: download("narrative", f"romer_romer/{n}", u), f"Romer-Romer {name}")


if __name__ == "__main__":
    main()
