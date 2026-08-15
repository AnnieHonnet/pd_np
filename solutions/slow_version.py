"""Ex 15 starting point: a deliberately slow, row-by-row implementation.
Your task: produce the identical result fully vectorized (pivot / groupby),
time both on the data repeated 500x, and report the speedup.
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
REPORT_COLS = ["pct", "clade_reads", "direct_reads", "rank", "taxid", "name"]


def build_long() -> pd.DataFrame:
    frames = []
    for p in sorted(DATA.glob("*.report")):
        df = pd.read_csv(p, sep="\t", header=None, names=REPORT_COLS)
        df["name"] = df["name"].str.strip()
        df = df[df["rank"] == "S"].copy()
        df.insert(0, "sample", p.stem)
        frames.append(df)
    long_df = pd.concat(frames, ignore_index=True)
    meta = pd.read_csv(DATA / "metadata.tsv", sep="\t")
    return long_df.merge(meta, on="sample")


def group_means_slow(df: pd.DataFrame) -> pd.Series:
    """Mean pct per (species, group) — the WRONG way. Do not imitate."""
    sums: dict = {}
    counts: dict = {}
    for _, row in df.iterrows():                     # row-by-row: slow
        key = (row["name"], row["group"])
        sums[key] = sums.get(key, 0.0) + row["pct"]
        counts[key] = counts.get(key, 0) + 1
    means = {k: sums[k] / counts[k] for k in sums}
    s = pd.Series(means).sort_index()
    s.index = pd.MultiIndex.from_tuples(s.index, names=["name", "group"])
    return s


if __name__ == "__main__":
    df = build_long()
    big = pd.concat([df] * 500, ignore_index=True)
    print(group_means_slow(big).round(3))
