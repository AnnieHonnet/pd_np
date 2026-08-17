import pandas as pd
import numpy as np
import os
import sys
import time
from pathlib import Path
import re




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
    
    
#TABLE_METAPHLAN
COL = ["cladenames", "ncbi_taxid",  "relative_abund",  
       "coverage" , "n_reads"]

def table_metaphlan():
    frames = []
    for f in sorted(DATA.glob("*_metaphlan.txt")): 
        df = pd.read_csv(f, sep="\t", names=COL, skiprows=7)
        df["samples"] = f.stem.replace("_metaphlan", "")
        frames.append(df)
    df_all = pd.concat(frames, ignore_index=True,)
    #print(df_all)
    is_species = (df_all["cladenames"].str.contains(r"\|s__")) 
    
    species_table = df_all[is_species].copy()
   

    
    species_table["species"] = species_table["cladenames"].str.extract(r"(s__[^|]+)")
    species_table_3 = species_table[[ 'n_reads', 'samples', 'species']] 
    species_table_3.to_csv(DATA.parent / "species_table_3.tsv", sep="\t", index=False)
    
    
 
def air():
    COL = ["city","country" ,"date.utc","location","parameter","value","unit"]

    df_air = pd.read_csv(DATA / "air_qual.csv", sep=",", names=COL)
    no2 = df_air[df_air["parameter"] == "no2"]
    no2_subset = no2.sort_index().groupby(["location"]).all()


    no2.to_csv("no2.csv")
    
    print(no2_subset)
   


# main
if __name__ == "__main__": 
    #ex1()
    #ex2()
    #ex3()
    #table_metaphlan()
    air()