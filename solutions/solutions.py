"""Worked solutions. Run a single exercise:  python solutions.py ex07
Run everything:                              python solutions.py all
Data directory is resolved relative to this file, so it works from anywhere.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

REPORT_COLS = ["pct", "clade_reads", "direct_reads", "rank", "taxid", "name"]


# ---------------------------------------------------------------- Level 1

def ex01():
    """Load one Kraken2 report."""
    df = pd.read_csv(
        DATA / "DE-14647-S2_bleu_CB_2603_S4.report",
        sep="\t", header=None, names=REPORT_COLS,
    )
    df["name"] = df["name"].str.strip()
    print(df.head())
    print(df.dtypes)
    assert len(df) == 41 and df.loc[0, "name"] == "unclassified"
    return df


def ex02():
    """Species rows, sorted by clade_reads desc, top 5."""
    df = ex01()
    sp = (
        df[df["rank"] == "S"]
        .sort_values("clade_reads", ascending=False)
        .reset_index(drop=True)
    )
    print(sp.loc[:4, ["name", "pct"]])
    return sp


def ex03():
    """Glob all reports; extract sample names (bash ${f%.report} equivalent)."""
    samples = sorted(p.stem for p in DATA.glob("*.report"))
    print("\n".join(samples))
    assert len(samples) == 6
    return samples


def ex04():
    """MetaPhlAn profile, species level only."""
    df = pd.read_csv(
        DATA / "DE-14650-S2_bleu_M9_CA_1703_S7_profile.tsv",
        sep="\t", skiprows=4, header=None,
        names=["clade_name", "ncbi_tax_id", "relative_abundance", "additional_species"],
    )
    sp = df[df["clade_name"].str.contains("s__")].copy()
    print(sp[["clade_name", "relative_abundance"]])
    assert np.isclose(sp["relative_abundance"].sum(), 100, atol=0.01)
    return sp


# ---------------------------------------------------------------- Level 2

def ex05():
    """Extract bare species name from full clade string."""
    sp = ex04()
    sp["species"] = sp["clade_name"].str.split("|").str[-1].str[3:]  # drop 's__'
    print(sp[["species", "relative_abundance"]])
    assert not sp["species"].str.contains(r"\||s__").any()
    return sp


def ex06():
    """Three ways to bin pct into flags."""
    df = ex01()
    sp = df[df["rank"] == "S"].copy()

    sp["flag_where"] = np.where(
        sp["pct"] >= 5, "dominant", np.where(sp["pct"] >= 1, "minor", "rare")
    )
    sp["flag_select"] = np.select(
        [sp["pct"] >= 5, sp["pct"] >= 1], ["dominant", "minor"], default="rare"
    )
    sp["flag_cut"] = pd.cut(
        sp["pct"], bins=[-np.inf, 1, 5, np.inf],
        labels=["rare", "minor", "dominant"], right=False,
    )
    print(sp["flag_where"].value_counts())
    assert (sp["flag_where"] == sp["flag_select"]).all()
    assert (sp["flag_where"] == sp["flag_cut"].astype(str)).all()
    return sp


def ex07():
    """Length-weighted mean depth — the samtools coverage task."""
    cov = pd.read_csv(DATA / "DE-14644-S2_cleaned.coverage.tsv", sep="\t")
    cov = cov.rename(columns={"#rname": "rname"})
    lengths = cov["endpos"] - cov["startpos"] + 1
    lw_depth = np.average(cov["meandepth"], weights=lengths)
    print(f"length-weighted mean depth = {lw_depth:.3f}")
    assert cov["meandepth"].min() <= lw_depth <= cov["meandepth"].max()
    return lw_depth


def ex08():
    """Vectorized share-of-classified normalization."""
    sp = ex02()
    sp["share_pct"] = 100 * sp["clade_reads"] / sp["clade_reads"].sum()
    print(sp[["name", "clade_reads", "share_pct"]])
    assert np.isclose(sp["share_pct"].sum(), 100)
    return sp


# ---------------------------------------------------------------- Level 3

def load_report(path: Path) -> pd.DataFrame:
    """Ex 09: any report -> species rows + sample column."""
    df = pd.read_csv(path, sep="\t", header=None, names=REPORT_COLS)
    df["name"] = df["name"].str.strip()
    sp = df[df["rank"] == "S"].copy()
    sp.insert(0, "sample", Path(path).stem)  # the awk 'prepend sample' task
    return sp.reset_index(drop=True)


def ex09():
    a = load_report(DATA / "DE-14647-S2_bleu_CB_2603_S4.report")
    b = load_report(DATA / "DE-14644-S2_cleaned.report")
    print(a.head(3), "\n", b.head(3))
    assert list(a.columns) == list(b.columns)
    assert a["sample"].iat[0] == "DE-14647-S2_bleu_CB_2603_S4"
    return a, b


def ex10():
    """All reports -> one long table."""
    long_df = pd.concat(
        [load_report(p) for p in sorted(DATA.glob("*.report"))],
        ignore_index=True,
    )[["sample", "name", "pct", "clade_reads"]]
    print(long_df.shape)
    assert long_df["sample"].nunique() == 6
    assert len(long_df) == 6 * 12
    return long_df


def ex11():
    """Long -> wide species x sample matrix, sorted by mean abundance."""
    long_df = ex10()
    mat = (
        long_df.pivot(index="name", columns="sample", values="pct")
        .fillna(0)
    )
    mat = mat.loc[mat.mean(axis=1).sort_values(ascending=False).index]
    print(mat.round(2))
    assert mat.shape == (12, 6)
    return mat


def ex12():
    """Metadata joins and the indicator trick."""
    meta = pd.read_csv(DATA / "metadata.tsv", sep="\t")
    long_df = ex10()

    inner = long_df.merge(meta, on="sample", how="inner")
    print("inner:", inner["sample"].nunique(), "samples")

    # start from metadata to expose the sample with no results
    left = meta.merge(long_df, on="sample", how="left", indicator=True)
    missing = left.loc[left["_merge"] == "left_only", "sample"].unique()
    print("metadata samples with no result files:", missing)

    assert inner["sample"].nunique() == 6
    assert list(missing) == ["DE-14999-S2_extra_ctrl"]
    return inner


def ex13():
    """Group means and top differential species."""
    merged = ex12()
    gm = merged.groupby(["name", "group"])["pct"].agg(["mean", "std"])
    wide = gm["mean"].unstack()               # columns: control, treated
    wide["diff"] = wide["treated"] - wide["control"]
    top = wide.sort_values("diff", ascending=False).head(3)
    print(top.round(2))
    assert "Clostridioides difficile" in top.index[:2]
    return wide


# ---------------------------------------------------------------- Level 4

def load_profile(path: Path) -> pd.DataFrame:
    """Ex 14 helper: MetaPhlAn profile -> species rows + sample column."""
    df = pd.read_csv(
        path, sep="\t", skiprows=4, header=None,
        names=["clade_name", "ncbi_tax_id", "relative_abundance", "additional_species"],
    )
    sp = df[df["clade_name"].str.contains("s__")].copy()
    sp["species"] = sp["clade_name"].str.split("|").str[-1].str[3:]
    sp.insert(0, "sample", Path(path).stem.removesuffix("_profile"))
    return sp[["sample", "species", "relative_abundance"]].reset_index(drop=True)


def ex14():
    """MetaPhlAn matrix + Kraken2 vs MetaPhlAn comparison for C. difficile."""
    prof = pd.concat(
        [load_profile(p) for p in sorted(DATA.glob("*_profile.tsv"))],
        ignore_index=True,
    )
    mpa_mat = prof.pivot(index="species", columns="sample", values="relative_abundance").fillna(0)
    print(mpa_mat.round(2))

    k2 = ex10()
    k2_cd = (
        k2[k2["name"] == "Clostridioides difficile"]
        .set_index("sample")["pct"].rename("kraken2_pct")
    )
    mpa_cd = (
        prof[prof["species"] == "Clostridioides_difficile"]
        .set_index("sample")["relative_abundance"].rename("metaphlan_ab")
    )
    comp = pd.concat([k2_cd, mpa_cd], axis=1)
    print(comp.round(3))
    r = comp.corr().iloc[0, 1]
    print(f"correlation = {r:.3f}")
    assert r > 0.5
    return comp


def ex15():
    """Vectorized vs iterrows: build group means both ways and time them."""
    long_df = ex10()
    meta = pd.read_csv(DATA / "metadata.tsv", sep="\t")
    big = pd.concat([long_df] * 500, ignore_index=True).merge(meta, on="sample")

    # --- slow: iterrows accumulation (never do this) -------------------
    t0 = time.perf_counter()
    acc: dict = {}
    for _, row in big.iterrows():
        key = (row["name"], row["group"])
        acc.setdefault(key, []).append(row["pct"])
    slow = {k: sum(v) / len(v) for k, v in acc.items()}
    t_slow = time.perf_counter() - t0

    # --- fast: groupby -------------------------------------------------
    t0 = time.perf_counter()
    fast = big.groupby(["name", "group"])["pct"].mean()
    t_fast = time.perf_counter() - t0

    slow_s = pd.Series(slow).sort_index()
    slow_s.index = pd.MultiIndex.from_tuples(slow_s.index, names=["name", "group"])
    assert np.allclose(slow_s.values, fast.sort_index().values)
    print(f"iterrows: {t_slow:.3f}s   groupby: {t_fast:.4f}s   "
          f"speedup: {t_slow / t_fast:.0f}x")
    return t_slow / t_fast


ALL = {f"ex{i:02d}": globals()[f"ex{i:02d}"] for i in range(1, 16)}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = ALL.values() if which == "all" else [ALL[which]]
    for fn in targets:
        print(f"\n=== {fn.__name__} " + "=" * 50)
        fn()
