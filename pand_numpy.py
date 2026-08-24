#!/Users/nfs/annie/.conda/envs/MISTRAL/bin/python

import pandas as pd
import numpy as np
import os
import sys
import time
from pathlib import Path
import re
import matplotlib.pyplot as plt 
import seaborn as sns




#--- LEVEL 1 

DATA = Path("/home/anh/Desktop/pandas_bioinfo_training/data")

K2_REPORT_PATH = Path("/Users/nfs/annie/projects/yousra/fastq_mouse/filter_mapping2")
Metaphaln_table = Path("")
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



def k2_report_tab():
    COL_K2 = ["percent" , "clade_reads", "taxon_reads", "rank_code", "ncbi_id" , "scientific_name"]
    dfs=[]
    dfs_all=[]
    all_samples=[]

    for report in sorted(K2_REPORT_PATH.glob("*.report")): 
        df = pd.read_csv(report, sep="\t", names=COL_K2, skipinitialspace=True )
        df["sample"] = report.stem
        all_samples.append(report.stem)
        
        Clostridium = df["scientific_name"].str.contains("Clostridioides difficile|Clostridium butyricum")
        dfs.append(df[Clostridium])
        
        Species_specific = df["rank_code"].str.contains("S")
        dfs_all.append(df[Species_specific])
    k2_report_all = pd.concat(dfs_all, ignore_index=True)
    k2_report = pd.concat(dfs, ignore_index=True)
    #print(k2_report)
    #return k2_report
    
    table_all = k2_report_all.pivot_table(index="scientific_name", columns="sample", values="taxon_reads", fill_value=0)
    table = k2_report.pivot_table(index="scientific_name", columns="sample", values="taxon_reads", fill_value=0) 
    
    table = table.reindex(columns=all_samples, fill_value=0) #force to have all samples inside table even if there are no C.diff or C.but inside


    #print(table)
    #table.plot()
    table.to_csv("k2_report_table_clean.tsv",sep="\t")
    table_all.to_csv("k2_report_table_all_clean.tsv",sep="\t")
 
metaphlan_tab= Path("/Users/nfs/annie/projects/yousra/fastq_mouse/metaphlan3/metaphlan_clostridium.csv")
k2_tab = Path("/Users/nfs/annie/projects/yousra/fastq_mouse/metaphlan3/k2_repor_table.csv")
plot_out = Path("/Users/nfs/annie/projects/yousra/fastq_mouse/metaphlan3/plots")
species   = ["Clostridioides difficile", "Clostridium butyricum"]

def load_table(path, sep="\t"):
    df = pd.read_csv(path, sep=sep, index_col=0, thousands=",")
    df.index = df.index.str.replace("_", " ").str.strip()
    df.columns = [re.match(r"(DE-\d+-S\d+)", c).group(1) for c in df.columns]

    return df 

table_k2  = load_table(k2_tab, sep=",")
table_mpa = load_table(metaphlan_tab, sep=",")

samples = [s for s in table_k2.columns if s in table_mpa.columns]
table_k2  = table_k2[samples]
table_mpa = table_mpa[samples]

plot_out.mkdir(parents=True, exist_ok=True)


fig, axes = plt.subplots(2, 1, figsize=(22, 8), sharex=True)
for ax, sp in zip(axes, species):
    ax.plot(samples, table_k2.loc[sp],  marker="o", ms=3, label="Kraken2")
    ax.plot(samples, table_mpa.loc[sp], marker="s", ms=3, label="MetaPhlAn4")
    ax.set_yscale("symlog")
    ax.set_ylabel("reads")
    ax.set_title(sp, style="italic")
    ax.legend()
axes[-1].set_xticks(range(len(samples)))
axes[-1].set_xticklabels(samples, rotation=90, fontsize=5)
plt.tight_layout()
plt.savefig(plot_out / "k2_vs_mpa_lines.png", dpi=200)
plt.close()

Cdiff_3toxin = Path("/Users/nfs/annie/projects/yousra/fastq_mouse/metaphlan3/Mice_vs_Cdiff3toxin.csv")
Cbut_4_plasmid_4gene = Path("/Users/nfs/annie/projects/yousra/fastq_mouse/metaphlan3/Cbut_megaplasmid_4gene.csv") 
def combine_line():
    Cdiff_3toxin_COL = ["samples" ,"#rname" , "startpos" , "endpos"  ,"numreads" , "covbases",  "coverage",  "meandepth" ,  "meanbaseq",  "meanmapq"]
    Cdiff_3toxin_df = pd.read_csv(Cdiff_3toxin , sep = "\t", names=Cdiff_3toxin_COL, skiprows=1)
    Cbut_4gene = pd.read_csv(Cbut_4_plasmid_4gene , sep = "\t", names=Cdiff_3toxin_COL,  skiprows=1)
    sum_Cdiff_df = Cdiff_3toxin_df.groupby("samples", as_index=False, )["numreads"].sum()
    summ_Cbut_4gene = Cbut_4gene.groupby("samples", as_index=False, )["numreads"].sum()


    print(summ_Cbut_4gene)
    summ_Cbut_4gene.to_csv("Cbut_4gene_sum.tsv")

    sum_Cdiff_df.to_csv("C.diff_3toxin_summ.tsv")

def ex05(): 
    

def main(): 
    #ex1()
    #ex2()
    #ex3()
    #table_metaphlan()
    #air()
    #k2_report_tab()
    #table_k2  = load_table(k2_tab)
    #table_mpa = load_table(metaphlan_tab)
    #combine_line()

# main
if __name__ == "__main__": 
    main()
