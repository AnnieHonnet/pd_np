# pandas drills

57 assert-checked exercises on accessing and manipulating DataFrame rows and
columns, using mock versions of your own pipeline outputs.

## Setup

    cd ~/projects/pd_np/pandas_drills   # or wherever you put these
    conda activate MISTRAL
    python pandas_drills.py

The three mock data files are written to `./drill_data/` on first run:

| file | shape | what it mimics |
|---|---|---|
| `coverage_summary.tsv` | 37 x 10 | `samtools coverage` output, one row per sample per contig |
| `kraken2_counts.tsv` | 51 x 4 | Kraken2 read counts, long format |
| `metaphlan_merged.tsv` | 4 x 19 | merged MetaPhlAn abundances, wide format |

The coverage table is messy **on purpose**: `-` as the missing-value marker
(so the column loads as text, not float), a trailing space in one sample name,
and one exact duplicate row. Exercises 1-3 and 27 deal with that.

Kraken2 is missing `Mouse3_Day5` entirely, which is what makes the merge
exercises (44, 45, 55) show you a real join gap rather than a toy one.

## Usage

    python pandas_drills.py           # run all 57
    python pandas_drills.py 23        # run just exercise 23
    python pandas_drills.py --hints   # print a hint for anything not passing
    python pandas_drills.py --regen   # rebuild the mock data files

Each exercise hands you a namespace `d`:

    d.raw   messy coverage table exactly as read from disk
    d.cov   cleaned coverage table with integer mouse/day columns
    d.k2    Kraken2 counts, long
    d.mpa   MetaPhlAn abundances, wide

`d.cov` is pre-cleaned so a mistake in exercise 2 does not cascade through the
other 55. Every exercise gets a fresh copy, so you can mutate freely.

To attempt one: assign your answer to `result` and delete the
`raise NotImplementedError` line. The asserts below tell you what was expected.

## Sections

| # | topic |
|---|---|
| 1-3 | loading, dtype traps, duplicates |
| 4-7 | column access |
| 8-15 | row access: `.iloc`, `.loc`, boolean masks, `.query`, `.at` |
| 16-22 | adding, replacing, conditional assignment, `pd.cut`, `insert`, `concat` |
| 23-26 | rename, drop, reorder |
| 27-30 | string operations and `.str.extract` |
| 31-33 | index: MultiIndex, `reset_index`, `sort_values` |
| 34-36 | missing data, group-wise fill |
| 37-42 | groupby, named agg, `transform`, `filter` |
| 43-47 | merging, join types, key mismatches, the duplicate-key blowup |
| 48-50 | melt / pivot / pivot_table |
| 51-54 | `map`, `apply`, `np.where` |
| 55-57 | end-to-end Kraken2 vs MetaPhlAn comparison |

## Suggested order

Work sections 1-8 in one sitting; those are the mechanics you use constantly.
Section 9 (groupby) and 10 (merging) are where the real leverage is for your
89-sample work, so do them slowly. Sections 11-13 build directly toward the
Kraken2/MetaPhlAn comparison you are already plotting.

Exercise 47 is worth reading even after it passes: it demonstrates the
duplicate-key row explosion that silently corrupts merges.

## Answers

`pandas_drills_solutions.py` holds worked answers for all 57 and passes its own
checks. Same commands work on it. Try first, peek second.
