# Pandas / NumPy / pathlib Training — Bioinformatics Result Files

15 graded exercises using realistic mock versions of files you work with daily:
Kraken2 `--report` output, MetaPhlAn4 profiles, `samtools coverage` tables, and a
sample metadata sheet. Everything lives in `data/`.

Work in a Python session or notebook inside your MISTRAL env (pandas, numpy are there).
Solutions are in `solutions/solutions.py` — one function per exercise, so you can
check yourself with `python solutions/solutions.py ex01` etc. Try each exercise
properly before peeking. Expected outputs are shown so you can self-verify.

**The data:** 6 samples (matching your real naming style), each with:
- `<sample>.report` — Kraken2 report: `pct  clade_reads  direct_reads  rank  taxid  name` (tab-separated, name indented by 2 spaces per level)
- `<sample>_profile.tsv` — MetaPhlAn4 profile (4 comment lines starting with `#`, then `clade_name  NCBI_tax_id  relative_abundance  additional_species`)
- `<sample>.coverage.tsv` — samtools coverage output
- `data/metadata.tsv` — sample → group/mouse/day/total_reads. **Deliberately contains one sample with no result files** (you'll meet it in the join exercises).

---

## Level 1 — Loading and inspecting (pathlib + read_csv basics)

### Ex 01 — Load one Kraken2 report
Load `DE-14647-S2_bleu_CB_2603_S4.report` into a DataFrame with columns
`pct, clade_reads, direct_reads, rank, taxid, name`. The file has no header.
Strip leading whitespace from `name`.
*Check: 41 rows; first row is `unclassified`; dtypes of clade_reads/direct_reads are int64.*

Hints: `pd.read_csv(..., sep="\t", header=None, names=[...])`, `.str.strip()`.

### Ex 02 — Species table, sorted
From Ex 01's DataFrame, keep only species rows (`rank == "S"`), sort by
`clade_reads` descending, and show the top 5 with just `name` and `pct`.
*Check: the top species should be a Muribaculum/Bacteroides-type gut taxon, not E. coli (this is a control mouse).*

### Ex 03 — Glob all reports with pathlib
Using `pathlib.Path.glob`, list all `*.report` files in `data/` and extract the
sample name from each filename (equivalent of your bash `${f%.report}`).
Print sample names sorted.
*Check: 6 samples; names contain no `.report` suffix and no directory part.*

Hints: `Path("data").glob("*.report")`, `p.stem`.

### Ex 04 — Load a MetaPhlAn profile, skipping comments
Load `DE-14650-S2_bleu_M9_CA_1703_S7_profile.tsv` keeping only **species-level**
rows (clade_name contains `s__`), with columns `clade_name` and
`relative_abundance`. The `#clade_name...` line is the real header but starts with `#`.
*Check: 5 rows; relative_abundance sums to ≈100.*

Hints: either `comment="#"` + manual names, or `skiprows=4` + `names=[...]`.
`.str.contains("s__")`.

---

## Level 2 — Transforming single tables (masking, string ops, numpy)

### Ex 05 — Extract just the species name
Add a column `species` to Ex 04's table containing only the final taxon
(e.g. `Clostridioides_difficile`), stripped of the `s__` prefix.
*Check: no `|` and no `s__` anywhere in the column.*

Hints: `.str.split("|").str[-1]`, `.str.removeprefix("s__")` (pandas ≥2.0) or `.str[3:]`.

### Ex 06 — Boolean masks & np.where
On the Ex 01 report DataFrame: create a column `flag` that is `"dominant"` when
`pct >= 5`, `"minor"` when `1 <= pct < 5`, and `"rare"` otherwise — species rows only.
Do it once with `np.where` (nested) and once with `pd.cut` or `np.select`. Compare.
*Check: value_counts over flag; sum of counts == number of species rows.*

### Ex 07 — Length-weighted mean depth (your samtools task, in pandas)
Load `DE-14644-S2_cleaned.coverage.tsv` and compute the **length-weighted mean
depth** across contigs: `sum(meandepth * contig_length) / sum(contig_length)`
where length = `endpos - startpos + 1`. Pure numpy arithmetic, no loops.
*Check: a single float, plausibly between the min and max meandepth.*

Hints: `np.average(df.meandepth, weights=lengths)` is the one-liner.

### Ex 08 — Vectorized normalization
From Ex 02's species table, compute each species' share of **classified species
reads** (clade_reads / clade_reads.sum() × 100) as a new column, without any loop.
Verify it sums to 100 with `np.isclose`.

---

## Level 3 — Many files → one table (the core skill)

### Ex 09 — Parse-all-reports function
Write `load_report(path) -> DataFrame` that loads any report, keeps species rows,
and adds a `sample` column derived from the filename (your awk
"prepend sample name" task, in pandas). Test on 2 different files.
*Check: both results have identical columns; sample column matches filename.*

### Ex 10 — Concat into long format
Use Ex 09 + a comprehension over `Path.glob` to build one **long** DataFrame of
all 6 samples: columns `sample, name, pct, clade_reads`.
*Check: 6 samples × 12 species = 72 rows (some species may be 0-count but present).*

Hints: `pd.concat([load_report(p) for p in paths], ignore_index=True)`.

### Ex 11 — Pivot to a species × sample abundance matrix
Pivot Ex 10 into a wide matrix: rows = species name, columns = sample, values = pct.
Fill missing with 0. Sort rows by row mean, descending.
*Check: shape (12, 6); `Clostridioides difficile` mean is visibly higher in the 3 treated samples than the 3 controls.*

Hints: `df.pivot(index=..., columns=..., values=...)`, `.fillna(0)`,
`.loc[matrix.mean(axis=1).sort_values(ascending=False).index]`.

### Ex 12 — The metadata join (and its trap)
Merge the matrix (or the long table) with `metadata.tsv`. Metadata has **7**
samples; you have results for 6. Do a merge that (a) keeps only samples with
results, then (b) a merge that reveals which metadata sample has no results.
*Check: (a) 6 samples; (b) `DE-14999-S2_extra_ctrl` shows NaN for abundance columns.*

Hints: `how="inner"` vs `how="left"` starting from metadata; `indicator=True` is
the professional trick — look at the `_merge` column.

---

## Level 4 — Groupby, integration, speed

### Ex 13 — Groupby: treated vs control
From the merged long table: mean and std of `pct` per species per group. Then
extract the 3 species with the biggest treated-minus-control difference.
*Check: C. difficile and E. coli should top the list (that's how the data was built).*

Hints: `groupby(["name","group"])["pct"].mean().unstack()`, then subtract columns.

### Ex 14 — MetaPhlAn merged table + validation vs Kraken2
Build the same species × sample matrix from the 6 `_profile.tsv` files (reusing
your Ex 04/05/09 machinery — write `load_profile(path)`). Then, for
`Clostridioides difficile` only, make a 2-column comparison table:
Kraken2 pct vs MetaPhlAn relative_abundance per sample. They won't match
numerically (different denominators!) — but the treated/control *pattern* should agree.
*Check: correlation between the two columns is strongly positive (`df.corr()`).*

### Ex 15 — Speed: vectorize a slow loop
`solutions/slow_version.py` contains a deliberately slow row-by-row `iterrows`
implementation of Ex 11+13 (build matrix, compute group means). Rewrite it fully
vectorized and time both with `time.perf_counter` on the data repeated 500×
(`pd.concat([long_df]*500)`). Report the speedup.
*Check: the vectorized version should be at least ~50× faster and give identical numbers (`np.allclose`).*

---

## After these
- Redo Ex 10–13 in **polars** for comparison (same logic, different API) — optional.
- Point the same code at your **real** merge1 reports on SuperDome. The only change
  should be the glob path. If more than the path changes, your functions weren't general enough — refactor.
