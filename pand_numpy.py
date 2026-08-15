import pandas as pd
import numpy as np
import os
import sys
import time
from pathlib import Path




#--- LEVEL 1 

DATA = Path("/home/anh/Desktop/pandas_bioinfo_training/data")

REPORT_COLS = ["pct", "clade_reads", "direct_reads", "rank", "taxid", "name"]

#EX1
def ex1():
    """Load one Kraken2 report."""
    df = pd.read_csv(
        DATA / "DE-14647-S2_bleu_CB_2603_S4.report",sep="\t", header=None, names=REPORT_COLS,)
    
    df["name"] = df["name"].str.strip()
    print(df.head())
    print(df.dtypes)
    assert len(df) == 41 and df.loc[0, "name"] == "unclassified"
    return df

def ex2():
    df = ex1()
    df_rank = df[df["rank"] == "S"].sort_values("clade_reads", ascending=False).reset_index(drop=True) 
    print(df_rank.loc[:4, ["name", "pct"]] )

#Glob all reports with pathlib
def ex3():
    report = sorted(r.stem for r in DATA.glob("*.report"))
    print("\n".join(report))
    assert len(report) == 6 
    
    

def ex4():
    metaphlan_profile =  DATA.glob("*_profile.tsv")

    print(metaphlan_profile)
    metaphlan_profile_read = pd.read_csv(metaphlan_profile)
    print(metaphlan_profile_read)
# main
if __name__ == "__main__": 
    #ex1()
    #ex2()
    #ex3()
    ex4()