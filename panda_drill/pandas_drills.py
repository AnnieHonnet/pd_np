#!/usr/bin/env python3
"""
pandas_drills.py -- 57 assert-checked exercises on accessing and manipulating
rows and columns of a DataFrame.

The data mimics your own pipeline outputs: a samtools coverage table (messy on
purpose), a Kraken2 long count table, and a merged MetaPhlAn abundance table.
They are written to ./drill_data/ on first run.

    python pandas_drills.py              run everything
    python pandas_drills.py 23           run just exercise 23
    python pandas_drills.py --hints      show a hint for anything failing
    python pandas_drills.py --regen      rebuild the mock data files

Each exercise gives you three frames on `d`:
    d.raw  messy coverage table, exactly as read from disk
    d.cov  cleaned coverage table with mouse/day columns (use this by default)
    d.k2   Kraken2 counts, long format
    d.mpa  MetaPhlAn abundances, wide format

Assign your answer to `result` and delete the NotImplementedError line.
Every exercise checks itself, so a failure tells you what it expected.
Worked answers are in pandas_drills_solutions.py -- try first, peek second.
"""


import numpy as np
import pandas as pd
from drill_common import exercise, cli, DATA_DIR
import pandas.api.types 


# ==========================================================================
S = "1. Loading and inspecting"
# ==========================================================================

@exercise(S, "Load coverage_summary.tsv with '-' treated as missing",
          hint="read_csv takes na_values=")
def ex(d):
    """
    The file uses '-' for missing coverage values. Load it into `result` so
    that the 'coverage' column comes out as a proper float column.
    """
    # ---- your code here -------------------------------------------------
    
    result = pd.read_csv("/Users/nfs/annie/projects/pd_np/panda_drill/drill_data/coverage_summary.tsv", sep="\t",na_values=['-'] )

    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, pd.DataFrame), "result should be a DataFrame"
    assert result.shape == (37, 10), f"expected (37, 10), got {result.shape}"
    assert pd.api.types.is_numeric_dtype(result["coverage"]), \
        "'coverage' is still not numeric -- pandas kept it as text"
    assert result["coverage"].isna().sum() == 2, \
        "expected exactly 2 missing coverage values"


@exercise(S, "Drop the exact duplicate row",
          hint="drop_duplicates(), then reset_index(drop=True)")
def ex(d):
    """
    `d.raw` has 37 rows but one is an exact duplicate of another.
    Put the de-duplicated frame in `result`, with a clean 0..n-1 index.
    """
    # ---- your code here -------------------------------------------------
    result = d.raw.drop_duplicates().reset_index(drop=True)
    
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape[0] == 36, f"expected 36 rows, got {result.shape[0]}"
    assert list(result.index) == list(range(36)), "index was not reset"


@exercise(S, "List the non-numeric columns of d.raw",
          hint="pd.api.types.is_numeric_dtype(series) tests one column")
def ex(d):
    """
    Put the names of every column in `d.raw` that is NOT numeric into
    `result`, as a list, in the original column order.
    """
    # ---- your code here -------------------------------------------------
    result = [c for c in d.raw.columns if not pd.api.types.is_numeric_dtype(d.raw[c])]
    print(result)
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert result == ["sample", "rname", "coverage"], \
        f"expected ['sample', 'rname', 'coverage'], got {result}"


# ==========================================================================
S = "2. Column access"
# ==========================================================================

@exercise(S, "Pull out 'meandepth' as a Series",
          hint="single brackets give a Series, double give a DataFrame")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov["meandepth"]
    print(result)

    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, pd.Series), \
        "that is a DataFrame -- single brackets give a Series"
    assert result.name == "meandepth"
    assert len(result) == 36


@exercise(S, "Pull out 'sample' and 'meandepth' as a 2-column DataFrame",
          hint="pass a list of names inside the brackets")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov[["sample", "meandepth"]]
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, pd.DataFrame), "expected a DataFrame"
    assert list(result.columns) == ["sample", "meandepth"], \
        f"wrong columns: {list(result.columns)}"
    assert result.shape == (36, 2)


@exercise(S, "Select every column whose name starts with 'mean'",
          hint="df.filter(like=...) or df.filter(regex=...) or a list comprehension")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov.filter(regex="mean")
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert set(result.columns) == {"meandepth", "meanbaseq", "meanmapq"}, \
        f"got {list(result.columns)}"
    assert result.shape[0] == 36


@exercise(S, "Get the column names as a plain Python list",
          hint="list(df.columns)")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = list(d.cov.columns)
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, list), "expected a list, not an Index"
    assert result[0] == "sample" and result[-1] == "day"
    assert len(result) == 12


# ==========================================================================
S = "3. Row access: iloc, loc, boolean masks"
# ==========================================================================

@exercise(S, "First 5 rows by position",
          hint=".iloc[] takes integer positions")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov.iloc[:5]
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape == (5, 12), f"expected (5, 12), got {result.shape}"
    assert result.iloc[0]["sample"] == "Mouse1_Day1"


@exercise(S, "Rows 10-14 (positions) and only the sample/meandepth columns",
          hint=".iloc[rows, cols] -- cols can be a list of names? no: use .iloc for "
               "positions, or mix with .loc")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov.iloc[9:14, [0,7]]
    # ----------------------------------------------------------------------
    #raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape == (5, 2), f"expected (5, 2), got {result.shape}"
    assert list(result.columns) == ["sample", "meandepth"]


@exercise(S, "All rows where meandepth is above 40",
          hint="df.loc[boolean_mask]")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = d.cov.loc[d.cov["meandepth"] > 40 ]
    print(result)
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert (result["meandepth"] > 40).all(), "some rows slipped through"
    assert len(result) == 12, f"expected 12 rows, got {len(result)}"


@exercise(S, "Chromosome rows with coverage above 98",
          hint="combine with & and wrap EACH condition in parentheses")
def ex(d):
    """
    Rows where rname == 'Cdiff_CDSM_1' AND coverage > 98.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert (result["rname"] == "Cdiff_CDSM_1").all()
    assert (result["coverage"] > 98).all()
    assert len(result) == 11, f"expected 11 rows, got {len(result)}"


@exercise(S, "Rows for a specific set of samples",
          hint=".isin([...]) beats chaining == with |")
def ex(d):
    """
    Rows belonging to Mouse1_Day1, Mouse2_Day3 or Mouse3_Day4.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 6, f"3 samples x 2 contigs = 6 rows, got {len(result)}"
    assert set(result["sample"]) == {"Mouse1_Day1", "Mouse2_Day3", "Mouse3_Day4"}


@exercise(S, "Same filter using .query()",
          hint="df.query('mouse == 2 and day > 3')")
def ex(d):
    """
    Rows where mouse == 2 and day > 3, written with .query().
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 6, f"expected 6 rows, got {len(result)}"
    assert set(result["day"]) == {4, 5, 6}


@exercise(S, "Invert a mask: every row that is NOT the plasmid",
          hint="~ negates a boolean mask; != also works")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 18, f"expected 18 rows, got {len(result)}"
    assert "Cdiff_CDSM_2" not in set(result["rname"])


@exercise(S, "Read one single cell",
          hint=".at[row_label, col] is the fast scalar accessor")
def ex(d):
    """
    The meandepth in row 4 (label 4) -- as a plain number, not a Series.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert np.isscalar(result) or isinstance(result, (int, np.integer)), \
        "expected a scalar value"
    assert result == 13, f"expected 13, got {result}"


# ==========================================================================
S = "4. Adding, replacing and modifying"
# ==========================================================================

@exercise(S, "Add a computed column",
          hint="arithmetic on columns is elementwise; just assign the result")
def ex(d):
    """
    Add 'reads_per_kb' = numreads / (contig length in kb), where contig
    length is endpos - startpos + 1. Put the whole frame in `result`.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "reads_per_kb" in result.columns
    assert result.shape[1] == 13
    assert abs(result.at[0, "reads_per_kb"] - 2.6491) < 0.01, \
        f"row 0 should be about 2.649, got {result.at[0, 'reads_per_kb']}"


@exercise(S, "Replace contig names with readable labels",
          hint=".replace({old: new}) or .map({...}) on the column")
def ex(d):
    """
    In `result`, rename the VALUES in 'rname':
      Cdiff_CDSM_1 -> chromosome
      Cdiff_CDSM_2 -> plasmid
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    counts = result["rname"].value_counts().to_dict()
    assert counts == {"chromosome": 18, "plasmid": 18}, \
        f"expected 18 of each, got {counts}"


@exercise(S, "Conditional assignment with .loc",
          hint="df.loc[mask, 'newcol'] = value -- NOT df[mask]['newcol'] = value")
def ex(d):
    """
    Add a boolean column 'low_depth' that is True where meandepth < 15
    and False elsewhere. Beware chained assignment: it silently does nothing.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "low_depth" in result.columns, "column was never created"
    assert result["low_depth"].sum() == 4, \
        f"expected 4 True values, got {result['low_depth'].sum()}"
    assert result.loc[result["low_depth"], "meandepth"].max() < 15


@exercise(S, "Bin a numeric column into categories",
          hint="pd.cut(series, bins=[...], labels=[...])")
def ex(d):
    """
    Add a 'depth_class' column binning meandepth as:
      0-20 -> 'low', 20-40 -> 'mid', 40-80 -> 'high'   (right-closed)
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "depth_class" in result.columns
    assert result["depth_class"].isna().sum() == 0, \
        "some values fell outside your bins"
    counts = result["depth_class"].value_counts().to_dict()
    assert counts == {"mid": 18, "high": 12, "low": 6}, \
        f"got {counts}"


@exercise(S, "Overwrite values in place for a subset of rows",
          hint="one .loc call with both the row mask and the column name")
def ex(d):
    """
    Set meanmapq to 0 for every plasmid row, leaving chromosome rows alone.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    plasmid = result.loc[result["rname"] == "Cdiff_CDSM_2", "meanmapq"]
    chrom = result.loc[result["rname"] == "Cdiff_CDSM_1", "meanmapq"]
    assert (plasmid == 0).all(), "plasmid rows were not all set to 0"
    assert (chrom == 55.0).all(), "you also modified the chromosome rows"


@exercise(S, "Insert a column at a specific position",
          hint="df.insert(loc, column, values)")
def ex(d):
    """
    Insert a column 'run' filled with the string 'HCWJHDRX7' as the FIRST
    column of the frame.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns)[0] == "run", \
        f"'run' is not first: {list(result.columns)[:3]}"
    assert (result["run"] == "HCWJHDRX7").all()
    assert result.shape[1] == 13


@exercise(S, "Append rows from another frame",
          hint="pd.concat([a, b], ignore_index=True)")
def ex(d):
    """
    Build a 2-row DataFrame for a new sample 'Mouse4_Day1' (any sensible
    values, but it must have the same columns) and append it below d.cov.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 38, f"expected 38 rows, got {len(result)}"
    assert list(result.columns) == list(d.cov.columns), \
        "column set or order changed -- check for typos in your new frame"
    assert result["sample"].nunique() == 19


# ==========================================================================
S = "5. Renaming, dropping, reordering"
# ==========================================================================

@exercise(S, "Rename two columns",
          hint="df.rename(columns={'old': 'new'})")
def ex(d):
    """
    Rename 'rname' -> 'contig' and 'numreads' -> 'n_reads'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "contig" in result.columns and "n_reads" in result.columns
    assert "rname" not in result.columns and "numreads" not in result.columns
    assert result.shape == (36, 12), "renaming should not change the shape"


@exercise(S, "Drop columns you do not need",
          hint="df.drop(columns=[...])")
def ex(d):
    """
    Drop 'meanbaseq', 'meanmapq' and 'covbases'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape[1] == 9, f"expected 9 columns, got {result.shape[1]}"
    for gone in ("meanbaseq", "meanmapq", "covbases"):
        assert gone not in result.columns


@exercise(S, "Reorder columns explicitly",
          hint="select with a list in the order you want")
def ex(d):
    """
    Return a frame whose columns are exactly, in this order:
      sample, mouse, day, rname, meandepth, coverage
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns) == \
        ["sample", "mouse", "day", "rname", "meandepth", "coverage"], \
        f"got {list(result.columns)}"


@exercise(S, "Drop rows by label",
          hint="df.drop(index=[...])")
def ex(d):
    """
    Drop the rows with index labels 0 and 1.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 34, f"expected 34 rows, got {len(result)}"
    assert 0 not in result.index and 1 not in result.index


# ==========================================================================
S = "6. String operations"
# ==========================================================================

@exercise(S, "Clean whitespace and extract mouse/day from sample names",
          hint=".str.strip() then .str.extract(r'Mouse(\\d+)_Day(\\d+)')")
def ex(d):
    """
    Starting from the RAW frame (one sample name has a trailing space),
    produce `result` with clean 'sample' plus integer 'mouse' and 'day'
    columns.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result["mouse"].dtype.kind == "i", "'mouse' is not an integer column"
    assert result["day"].dtype.kind == "i", "'day' is not an integer column"
    assert result["mouse"].isna().sum() == 0, \
        "some names failed to parse -- did you strip the whitespace first?"
    assert set(result["mouse"]) == {1, 2, 3}
    assert not result["sample"].str.endswith(" ").any()


@exercise(S, "Filter rows by substring",
          hint=".str.contains() returns a boolean mask")
def ex(d):
    """
    Every row whose sample name contains 'Day3'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 6, f"3 mice x 2 contigs = 6, got {len(result)}"
    assert (result["day"] == 3).all()


@exercise(S, "Shorten MetaPhlAn clade names to species",
          hint=".str.split('|').str[-1] then .str.replace('s__', '')")
def ex(d):
    """
    Add a 'species' column to the MetaPhlAn frame holding just the species
    name, e.g. 'Clostridioides_difficile'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "species" in result.columns
    assert result.at[0, "species"] == "Clostridioides_difficile", \
        f"got {result.at[0, 'species']!r}"
    assert not result["species"].str.contains("__").any()


@exercise(S, "Build a new label by concatenating columns",
          hint="string columns concatenate with +, but cast numbers first")
def ex(d):
    """
    Add a column 'label' of the form 'M<mouse>D<day>', e.g. 'M1D1'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.at[0, "label"] == "M1D1", f"got {result.at[0, 'label']!r}"
    assert result["label"].nunique() == 18


# ==========================================================================
S = "7. The index"
# ==========================================================================

@exercise(S, "Set a two-level index and look up a row",
          hint="set_index(['sample', 'rname']) then .loc[('Mouse2_Day3', 'Cdiff_CDSM_1')]")
def ex(d):
    """
    Index by sample AND contig, then put the meandepth of
    ('Mouse2_Day3', 'Cdiff_CDSM_1') into `result`.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert np.isscalar(result) or isinstance(result, (int, np.integer)), \
        f"expected a single number, got {type(result)}"
    assert result == 23, f"expected 23, got {result}"


@exercise(S, "Go back to a plain integer index",
          hint="reset_index() turns index levels back into columns")
def ex(d):
    """
    Take d.cov, set the index to 'sample', then undo it so that 'sample'
    is a normal column again and the index is 0..n-1.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "sample" in result.columns, "'sample' did not come back as a column"
    assert list(result.index) == list(range(36))
    assert list(result.columns)[0] == "sample"


@exercise(S, "Sort rows by two keys",
          hint="sort_values(['a', 'b'], ascending=[True, False])")
def ex(d):
    """
    Sort by mouse ascending, then meandepth DESCENDING within each mouse.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.iloc[0]["mouse"] == 1
    first_mouse = result.loc[result["mouse"] == 1, "meandepth"].tolist()
    assert first_mouse == sorted(first_mouse, reverse=True), \
        "meandepth is not descending within mouse 1"
    assert result.iloc[-1]["mouse"] == 3


# ==========================================================================
S = "8. Missing data"
# ==========================================================================

@exercise(S, "Count missing values per column",
          hint="df.isna().sum() gives a Series indexed by column name")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, pd.Series), "expected a Series"
    assert result["coverage"] == 2, f"coverage should have 2 NaN, got {result['coverage']}"
    assert result["meandepth"] == 0


@exercise(S, "Drop rows with a missing coverage value",
          hint="dropna(subset=[...]) limits the check to those columns")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 34, f"expected 34 rows, got {len(result)}"
    assert result["coverage"].isna().sum() == 0


@exercise(S, "Fill missing coverage with the mean of its own contig",
          hint="groupby(...)['coverage'].transform('mean') gives a per-row fill value")
def ex(d):
    """
    Replace each NaN in 'coverage' with the mean coverage of the same
    contig (rname), not the global mean.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result["coverage"].isna().sum() == 0, "still some NaN left"
    filled = result.at[3, "coverage"]          # was NaN, plasmid row
    plasmid_mean = d.cov.loc[d.cov["rname"] == "Cdiff_CDSM_2", "coverage"].mean()
    assert abs(filled - plasmid_mean) < 1e-9, \
        f"row 3 filled with {filled}, expected the plasmid mean {plasmid_mean}"


# ==========================================================================
S = "9. groupby and aggregation"
# ==========================================================================

@exercise(S, "Mean meandepth per mouse",
          hint="groupby('mouse')['meandepth'].mean()")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert isinstance(result, pd.Series), "expected a Series"
    assert result.loc[1] == 20.25, f"mouse 1 should be 20.25, got {result.loc[1]}"
    assert result.loc[3] == 50.25


@exercise(S, "Total reads per mouse per day",
          hint="group by a LIST of two columns")
def ex(d):
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 18, f"expected 18 groups, got {len(result)}"
    assert result.loc[(1, 1)] == 11550, \
        f"Mouse1 Day1 should total 11550, got {result.loc[(1, 1)]}"


@exercise(S, "Several statistics at once, with clean column names",
          hint="df.groupby(k).agg(newname=('col', 'func'), ...)")
def ex(d):
    """
    Per mouse, compute:
      mean_depth = mean of meandepth
      max_depth  = max of meandepth
      total_reads = sum of numreads
      n = number of rows
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns) == \
        ["mean_depth", "max_depth", "total_reads", "n"], \
        f"got {list(result.columns)}"
    assert result.loc[1, "n"] == 12
    assert result.loc[3, "max_depth"] == 72


@exercise(S, "Broadcast a group statistic back onto every row",
          hint=".transform() returns something the same length as the frame")
def ex(d):
    """
    Add a column 'mouse_mean_depth' holding, for each row, the mean
    meandepth of that row's mouse. The frame must stay 36 rows.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 36, "transform should not collapse rows -- did you use agg?"
    assert result.loc[result["mouse"] == 1, "mouse_mean_depth"].eq(20.25).all()


@exercise(S, "Keep only groups that meet a condition",
          hint="groupby(...).filter(lambda g: ...) keeps whole groups")
def ex(d):
    """
    Keep only the rows belonging to mice whose mean meandepth exceeds 30.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert set(result["mouse"]) == {2, 3}, f"got mice {sorted(set(result['mouse']))}"
    assert len(result) == 24


@exercise(S, "Count rows per group",
          hint="value_counts() on a column, or groupby().size()")
def ex(d):
    """
    Number of rows per contig, as a Series indexed by contig name.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.loc["Cdiff_CDSM_1"] == 18
    assert result.loc["Cdiff_CDSM_2"] == 18


# ==========================================================================
S = "10. Merging"
# ==========================================================================

@exercise(S, "Pivot the Kraken2 long table to one row per sample",
          hint="pivot_table(index=..., columns=..., values=...)")
def ex(d):
    """
    Turn d.k2 into a wide frame: one row per sample, one column per taxon
    name, values = reads. 'sample' should be a normal column, not the index.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "sample" in result.columns, "'sample' must be a column"
    assert result.shape[0] == 17, \
        f"17 samples were classified, got {result.shape[0]}"
    assert "Clostridioides difficile" in result.columns


@exercise(S, "Left-join coverage onto the Kraken2 counts",
          hint="merge(..., on='sample', how='left') keeps every left row")
def ex(d):
    """
    Take the chromosome rows of d.cov (18 samples) and left-join the
    Kraken2 C. difficile read counts onto them. Result: 18 rows, with a
    'reads' column that is NaN for the sample Kraken2 never saw.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 18, \
        f"expected 18 rows -- more means duplicate keys, got {len(result)}"
    assert result["reads"].isna().sum() == 1, \
        "exactly one sample should be missing from Kraken2"
    missing = result.loc[result["reads"].isna(), "sample"].iloc[0]
    assert missing == "Mouse3_Day5", f"the missing sample is {missing}"


@exercise(S, "Inner vs outer join",
          hint="how='inner' keeps only shared keys; how='outer' keeps everything")
def ex(d):
    """
    Inner-join the same two tables. `result` should contain only the 17
    samples present in BOTH.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 17, f"expected 17 rows, got {len(result)}"
    assert result["reads"].isna().sum() == 0
    assert "Mouse3_Day5" not in set(result["sample"])


@exercise(S, "Merge on differently-named keys",
          hint="left_on= and right_on=")
def ex(d):
    """
    The lookup table below uses 'sample_id' instead of 'sample'.
    Merge it onto the chromosome rows anyway.
    """
    lookup = pd.DataFrame({
        "sample_id": [f"Mouse{m}_Day{dd}" for m in (1, 2, 3) for dd in range(1, 7)],
        "cage": ["A"] * 6 + ["B"] * 6 + ["C"] * 6,
    })
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 18
    assert result["cage"].isna().sum() == 0, "some rows failed to match"
    assert set(result.loc[result["mouse"] == 2, "cage"]) == {"B"}


@exercise(S, "Spot the duplicate-key blowup",
          hint="merging on 'sample' when the right side has 2 rows per sample "
               "doubles your rows")
def ex(d):
    """
    Merge the FULL d.cov (36 rows, two per sample) onto itself on 'sample'.
    Put the resulting row count in `result` -- and note what happened.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result == 72, \
        f"18 samples x 2 x 2 = 72 rows; got {result}. This is why you always " \
        "check .shape after a merge."


# ==========================================================================
S = "11. Reshaping: wide <-> long"
# ==========================================================================

@exercise(S, "Melt the MetaPhlAn table to long format",
          hint="melt(id_vars=..., var_name=..., value_name=...)")
def ex(d):
    """
    Convert d.mpa (4 clades x 18 sample columns) to long format with
    columns: clade_name, sample, abundance.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns) == ["clade_name", "sample", "abundance"], \
        f"got {list(result.columns)}"
    assert len(result) == 72, f"4 x 18 = 72 rows, got {len(result)}"
    assert result["abundance"].dtype.kind == "f"


@exercise(S, "Pivot the long table back to wide",
          hint="pivot(index=..., columns=..., values=...)")
def ex(d):
    """
    Melt d.mpa to long, then pivot back so that samples are ROWS and
    clades are COLUMNS (the transpose of the original layout).
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape == (18, 4), f"expected (18, 4), got {result.shape}"
    assert result.index.name == "sample"


@exercise(S, "Cross-tabulate with pivot_table and an aggregation",
          hint="pivot_table takes aggfunc= and fill_value=")
def ex(d):
    """
    From d.cov build a table with mouse as rows, rname as columns and the
    SUM of numreads as values.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.shape == (3, 2), f"expected (3, 2), got {result.shape}"
    assert result.loc[1, "Cdiff_CDSM_1"] == 81000, \
        f"got {result.loc[1, 'Cdiff_CDSM_1']}"


# ==========================================================================
S = "12. apply, map and friends"
# ==========================================================================

@exercise(S, "map a Series through a dictionary",
          hint=".map({...}) -- values not in the dict become NaN")
def ex(d):
    """
    Add a 'phase' column: days 1-2 -> 'pre', 3-4 -> 'peak', 5-6 -> 'post'.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result["phase"].isna().sum() == 0, "some days were not mapped"
    counts = result["phase"].value_counts().to_dict()
    assert counts == {"pre": 12, "peak": 12, "post": 12}, f"got {counts}"


@exercise(S, "apply a function down a column",
          hint=".apply(func) on a Series calls func once per value")
def ex(d):
    """
    Add 'depth_log10' = log10 of meandepth, using .apply with np.log10.
    (In real code you would just call np.log10 on the column -- this is
    to practise the mechanics.)
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert "depth_log10" in result.columns
    assert abs(result.at[0, "depth_log10"] - np.log10(11)) < 1e-9


@exercise(S, "apply a function across each row",
          hint="axis=1 passes each ROW to the function as a Series")
def ex(d):
    """
    Add a 'tag' column of the form '<sample>:<rname>' built with a
    row-wise apply.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert result.at[0, "tag"] == "Mouse1_Day1:Cdiff_CDSM_1", \
        f"got {result.at[0, 'tag']!r}"
    assert result["tag"].nunique() == 36


@exercise(S, "Vectorised two-way choice with np.where",
          hint="np.where(condition, value_if_true, value_if_false)")
def ex(d):
    """
    Add a 'molecule' column: 'plasmid' where endpos < 100000, else
    'chromosome'. Use np.where, not a loop.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    counts = pd.Series(result["molecule"]).value_counts().to_dict()
    assert counts == {"plasmid": 18, "chromosome": 18}, f"got {counts}"


# ==========================================================================
S = "13. Putting it together"
# ==========================================================================

@exercise(S, "Kraken2 vs MetaPhlAn, end to end",
          hint="melt the MetaPhlAn table, filter to C. difficile, merge on sample")
def ex(d):
    """
    Build a per-sample comparison of C. difficile signal:
      columns: sample, reads (Kraken2), abundance (MetaPhlAn)
      one row per sample, all 18 samples kept, NaN where Kraken2 is missing.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert len(result) == 18, f"expected 18 rows, got {len(result)}"
    assert set(result.columns) == {"sample", "reads", "abundance"}
    assert result["reads"].isna().sum() == 1
    peak = result.loc[result["sample"] == "Mouse3_Day4"].iloc[0]
    assert peak["reads"] == 613962 and peak["abundance"] == 45.0


@exercise(S, "Find the samples where the two tools disagree most",
          hint="compute a ratio, then sort_values(ascending=False).head()")
def ex(d):
    """
    Using the merged comparison, add reads_per_abundance = reads/abundance
    and return the 3 samples with the HIGHEST value, as a DataFrame with
    columns sample and reads_per_abundance, sorted descending.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns) == ["sample", "reads_per_abundance"]
    assert len(result) == 3
    vals = result["reads_per_abundance"].tolist()
    assert vals == sorted(vals, reverse=True), "not sorted descending"


@exercise(S, "Write a tidy summary table to disk and read it back",
          hint="to_csv(sep='\\t', index=False), then read it again and compare")
def ex(d):
    """
    Build a per-sample chromosome summary (sample, mouse, day, numreads,
    meandepth, coverage), write it to drill_data/summary.tsv as TSV
    WITHOUT the index, read it back into `result`, and confirm it survived
    the round trip.
    """
    # ---- your code here -------------------------------------------------
    result = None
    # ----------------------------------------------------------------------
    raise NotImplementedError  # delete this line once you have written your answer
    assert list(result.columns) == \
        ["sample", "mouse", "day", "numreads", "meandepth", "coverage"], \
        f"unexpected columns {list(result.columns)} -- did index=False get used?"
    assert len(result) == 18
    assert result.at[0, "sample"] == "Mouse1_Day1"


if __name__ == "__main__":
    cli(__name__)
