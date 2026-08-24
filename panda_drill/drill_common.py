"""
Shared machinery for the pandas drills: mock data generation + exercise runner.

You should not need to edit this file. It builds small, deliberately messy
bioinformatics-style tables in ./drill_data/ and provides the pass/fail runner.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "drill_data"


# --------------------------------------------------------------------------
# Mock data
# --------------------------------------------------------------------------

def make_data(force: bool = False) -> None:
    """Write three mock tables that mimic real pipeline outputs."""
    DATA_DIR.mkdir(exist_ok=True)

    cov_path = DATA_DIR / "coverage_summary.tsv"
    k2_path = DATA_DIR / "kraken2_counts.tsv"
    mpa_path = DATA_DIR / "metaphlan_merged.tsv"

    if cov_path.exists() and not force:
        return

    # ---- samtools coverage style, one row per sample per contig -----------
    # Deliberate quirks:
    #   * 'coverage' column contains "NA" -> pandas reads the column as object
    #   * one sample name carries trailing whitespace
    #   * the last row is an exact duplicate
    lines = [
        "sample\trname\tstartpos\tendpos\tnumreads\tcovbases\tcoverage\tmeandepth\tmeanbaseq\tmeanmapq"
    ]
    rows = []
    for mouse in (1, 2, 3):
        for day in (1, 2, 3, 4, 5, 6):
            sample = f"Mouse{mouse}_Day{day}"
            if mouse == 2 and day == 4:
                sample = sample + " "          # trailing space quirk
            base = mouse * 10 + day            # meandepth on the chromosome

            cov1 = f"{96.0 + mouse + day * 0.1:.2f}"
            cov2 = f"{97.0 + day * 0.1:.2f}"
            if mouse == 1 and day == 2:
                cov2 = "-"                     # missing value quirk (not auto-detected)
            if mouse == 3 and day == 3:
                cov1 = "-"

            rows.append(
                [sample, "Cdiff_CDSM_1", 1, 4152362, base * 1000, 4000000,
                 cov1, base, 36.0, 55.0]
            )
            rows.append(
                [sample, "Cdiff_CDSM_2", 1, 8000, base * 50, 7800,
                 cov2, base * 2, 36.0, 50.0]
            )

    rows.append(list(rows[-2]))                # duplicate of Mouse3_Day6 contig 1

    for r in rows:
        lines.append("\t".join(str(x) for x in r))
    cov_path.write_text("\n".join(lines) + "\n")

    # ---- Kraken2 style long counts ---------------------------------------
    # Mouse3_Day5 is absent entirely -> creates a genuine merge gap.
    taxa = [(1496, "Clostridioides difficile"),
            (1492, "Clostridium butyricum"),
            (562, "Escherichia coli")]
    blooms = {("Mouse2", 3): 446719, ("Mouse3", 4): 613962}

    k2_lines = ["sample\ttaxid\tname\treads"]
    for mouse in (1, 2, 3):
        for day in (1, 2, 3, 4, 5, 6):
            if mouse == 3 and day == 5:
                continue
            sample = f"Mouse{mouse}_Day{day}"
            for taxid, name in taxa:
                if taxid == 1496:
                    reads = blooms.get((f"Mouse{mouse}", day), 100 * day + mouse)
                elif taxid == 1492:
                    reads = 5000 + 300 * day + 50 * mouse
                else:
                    reads = 800 + 40 * day
                k2_lines.append(f"{sample}\t{taxid}\t{name}\t{reads}")
    k2_path.write_text("\n".join(k2_lines) + "\n")

    # ---- MetaPhlAn style wide relative abundances -------------------------
    clades = [
        "k__Bacteria|p__Bacillota|g__Clostridioides|s__Clostridioides_difficile",
        "k__Bacteria|p__Bacillota|g__Clostridium|s__Clostridium_butyricum",
        "k__Bacteria|p__Pseudomonadota|g__Escherichia|s__Escherichia_coli",
        "k__Bacteria|p__Bacteroidota|g__Bacteroides|s__Bacteroides_fragilis",
    ]
    samples = [f"Mouse{m}_Day{d}" for m in (1, 2, 3) for d in (1, 2, 3, 4, 5, 6)]

    mpa_lines = ["clade_name\t" + "\t".join(samples)]
    for i, clade in enumerate(clades):
        vals = []
        for s in samples:
            mouse = int(s[5])
            day = int(s.split("Day")[1])
            if i == 0:
                v = 45.0 if (mouse, day) in ((2, 3), (3, 4)) else 0.1 * day
            elif i == 1:
                v = 20.0 + day
            elif i == 2:
                v = 5.0 + 0.5 * mouse
            else:
                v = 10.0 - 0.2 * day
            vals.append(f"{v:.3f}")
        mpa_lines.append(clade + "\t" + "\t".join(vals))
    mpa_path.write_text("\n".join(mpa_lines) + "\n")


# --------------------------------------------------------------------------
# Canonical loaded frames
# --------------------------------------------------------------------------

def load_frames() -> SimpleNamespace:
    """
    Returns a namespace with:
      raw : coverage table exactly as written (messy: NA strings, dup row,
            trailing whitespace in one sample name)
      cov : cleaned coverage table with mouse/day columns  (use this in most
            exercises so an early mistake doesn't cascade)
      k2  : Kraken2 long counts
      mpa : MetaPhlAn wide relative abundances
    """
    make_data()

    raw = pd.read_csv(DATA_DIR / "coverage_summary.tsv", sep="\t")

    cov = raw.copy()
    cov["sample"] = cov["sample"].str.strip()
    cov["coverage"] = pd.to_numeric(cov["coverage"], errors="coerce")
    cov = cov.drop_duplicates().reset_index(drop=True)
    extracted = cov["sample"].str.extract(r"Mouse(\d+)_Day(\d+)")
    cov["mouse"] = extracted[0].astype(int)
    cov["day"] = extracted[1].astype(int)

    k2 = pd.read_csv(DATA_DIR / "kraken2_counts.tsv", sep="\t")
    mpa = pd.read_csv(DATA_DIR / "metaphlan_merged.tsv", sep="\t")

    return SimpleNamespace(raw=raw, cov=cov, k2=k2, mpa=mpa)


# --------------------------------------------------------------------------
# Exercise registry + runner
# --------------------------------------------------------------------------

REGISTRY: list[dict] = []


def exercise(section: str, title: str, hint: str = ""):
    def deco(fn):
        REGISTRY.append(
            {"n": len(REGISTRY) + 1, "section": section,
             "title": title, "hint": hint, "fn": fn}
        )
        return fn
    return deco


def _fresh(dfs: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(
        raw=dfs.raw.copy(), cov=dfs.cov.copy(),
        k2=dfs.k2.copy(), mpa=dfs.mpa.copy(),
    )


def run(only: int | None = None, show_hints: bool = False, quiet_pass: bool = True):
    dfs = load_frames()

    todo = [e for e in REGISTRY if only is None or e["n"] == only]
    if not todo:
        print(f"No exercise number {only}. There are {len(REGISTRY)}.")
        return 1

    passed, failed, skipped = 0, 0, 0
    current_section = None

    for ex in todo:
        if ex["section"] != current_section and only is None:
            current_section = ex["section"]
            print(f"\n\033[1m{current_section}\033[0m")

        label = f"  {ex['n']:>2}. {ex['title']}"
        try:
            ex["fn"](_fresh(dfs))
        except NotImplementedError:
            skipped += 1
            print(f"\033[90m{label}  -- not attempted\033[0m")
            if show_hints and ex["hint"]:
                print(f"        hint: {ex['hint']}")
        except AssertionError as e:
            failed += 1
            print(f"\033[91m{label}  FAIL\033[0m")
            print(f"        {e}")
            if show_hints and ex["hint"]:
                print(f"        hint: {ex['hint']}")
        except Exception:
            failed += 1
            print(f"\033[91m{label}  ERROR\033[0m")
            for line in traceback.format_exc().strip().splitlines()[-3:]:
                print(f"        {line}")
            if show_hints and ex["hint"]:
                print(f"        hint: {ex['hint']}")
        else:
            passed += 1
            if not quiet_pass or only is not None:
                print(f"\033[92m{label}  ok\033[0m")
            else:
                print(f"\033[92m{label}  ok\033[0m")

    total = len(todo)
    print(f"\n{'-' * 60}")
    print(f"passed {passed}/{total}   failed {failed}   not attempted {skipped}")
    return 0 if failed == 0 else 1


def cli(module_name: str):
    only = None
    show_hints = "--hints" in sys.argv
    for a in sys.argv[1:]:
        if a.isdigit():
            only = int(a)
    if "--regen" in sys.argv:
        make_data(force=True)
        print(f"regenerated data in {DATA_DIR}")
    sys.exit(run(only=only, show_hints=show_hints))
