"""Generate realistic mock bioinformatics output files for the exercise set.
Formats mimic: Kraken2 --report, MetaPhlAn4 profiles, samtools coverage, sample metadata.
"""
import random
from pathlib import Path

random.seed(42)
DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)

SAMPLES = {
    "DE-14647-S2_bleu_CB_2603_S4":  {"group": "control",   "mouse": "M4",  "day": 26, "reads": 5_215_882},
    "DE-14648-S2_bleu_CB_2803_S5":  {"group": "control",   "mouse": "M5",  "day": 28, "reads": 6_094_310},
    "DE-14649-S2_bleu_CB_3103_S6":  {"group": "control",   "mouse": "M6",  "day": 31, "reads": 5_802_447},
    "DE-14650-S2_bleu_M9_CA_1703_S7": {"group": "treated", "mouse": "M9",  "day": 17, "reads": 4_251_063},
    "DE-14653-S2_bleu_M9_CA_2603_S10": {"group": "treated","mouse": "M9",  "day": 26, "reads": 4_987_120},
    "DE-14644-S2_cleaned":          {"group": "treated",   "mouse": "M2",  "day": 14, "reads": 3_918_555},
}

# taxonomy: (rank_code, depth, taxid, name) — plausible mouse gut taxa
TAXA = [
    ("R", 0, 1, "root"),
    ("D", 1, 2, "Bacteria"),
    ("P", 2, 976, "Bacteroidota"),
    ("C", 3, 200643, "Bacteroidia"),
    ("O", 4, 171549, "Bacteroidales"),
    ("F", 5, 815, "Bacteroidaceae"),
    ("G", 6, 816, "Bacteroides"),
    ("S", 7, 821, "Bacteroides vulgatus"),
    ("S", 7, 817, "Bacteroides fragilis"),
    ("F", 5, 171552, "Prevotellaceae"),
    ("G", 6, 838, "Prevotella"),
    ("S", 7, 839, "Prevotella copri"),
    ("F", 5, 2005525, "Muribaculaceae"),
    ("G", 6, 2093822, "Muribaculum"),
    ("S", 7, 1796646, "Muribaculum intestinale"),
    ("P", 2, 1239, "Bacillota"),
    ("C", 3, 186801, "Clostridia"),
    ("O", 4, 186802, "Eubacteriales"),
    ("F", 5, 186803, "Lachnospiraceae"),
    ("G", 6, 572511, "Blautia"),
    ("S", 7, 853, "Blautia producta"),
    ("G", 6, 1730, "Eubacterium"),
    ("S", 7, 39485, "Eubacterium rectale"),
    ("F", 5, 186804, "Peptostreptococcaceae"),
    ("G", 6, 1870884, "Clostridioides"),
    ("S", 7, 1496, "Clostridioides difficile"),
    ("C", 3, 91061, "Bacilli"),
    ("O", 4, 186826, "Lactobacillales"),
    ("F", 5, 33958, "Lactobacillaceae"),
    ("G", 6, 1578, "Lactobacillus"),
    ("S", 7, 1596, "Lactobacillus gasseri"),
    ("S", 7, 47770, "Lactobacillus johnsonii"),
    ("P", 2, 74201, "Verrucomicrobiota"),
    ("G", 6, 239934, "Akkermansia"),
    ("S", 7, 239935, "Akkermansia muciniphila"),
    ("P", 2, 1224, "Pseudomonadota"),
    ("G", 6, 561, "Escherichia"),
    ("S", 7, 562, "Escherichia coli"),
    ("D", 1, 10239, "Viruses"),
    ("S", 7, 1918006, "Lactobacillus phage LgaI"),
]

SPECIES = [t for t in TAXA if t[0] == "S"]

def kraken2_report(sample, meta):
    total = meta["reads"]
    unclassified = int(total * random.uniform(0.08, 0.22))
    classified = total - unclassified
    # random species weights; treated mice get more C. difficile + E. coli
    weights = {}
    for _, _, taxid, name in SPECIES:
        w = random.uniform(0.5, 10)
        if meta["group"] == "treated" and name in ("Clostridioides difficile", "Escherichia coli"):
            w *= random.uniform(4, 8)
        if meta["group"] == "control" and name == "Akkermansia muciniphila":
            w *= random.uniform(2, 4)
        weights[taxid] = w
    wsum = sum(weights.values())
    direct = {tid: int(classified * w / wsum) for tid, w in weights.items()}

    # clade reads = own direct + descendants (approximate: propagate up by name hierarchy order)
    clade = {}
    stack = []  # (depth, taxid)
    for rank, depth, taxid, name in TAXA:
        clade[taxid] = direct.get(taxid, 0)
    # propagate: iterate reversed, add child clade to nearest shallower ancestor
    arr = TAXA
    for i in range(len(arr) - 1, -1, -1):
        rank, depth, taxid, name = arr[i]
        for j in range(i - 1, -1, -1):
            if arr[j][1] < depth:
                clade[arr[j][2]] += clade[taxid]
                break
    lines = []
    pct_un = 100 * unclassified / total
    lines.append(f"{pct_un:6.2f}\t{unclassified}\t{unclassified}\tU\t0\tunclassified")
    for rank, depth, taxid, name in TAXA:
        pct = 100 * clade[taxid] / total
        indent = "  " * depth
        lines.append(f"{pct:6.2f}\t{clade[taxid]}\t{direct.get(taxid,0)}\t{rank}\t{taxid}\t{indent}{name}")
    (DATA / f"{sample}.report").write_text("\n".join(lines) + "\n")

def metaphlan_profile(sample, meta):
    hdr = [
        "#mpa_vJan25_CHOCOPhlAnSGB_202503",
        f"#/usr/bin/metaphlan {sample}.fastq.gz --nproc 8",
        f"#{meta['reads']} reads processed",
        "#clade_name\tNCBI_tax_id\trelative_abundance\tadditional_species",
    ]
    k = "k__Bacteria"
    rows = [(k, "2", 100.0)]
    sp = [
        ("k__Bacteria|p__Bacteroidota|c__Bacteroidia|o__Bacteroidales|f__Muribaculaceae|g__Muribaculum|s__Muribaculum_intestinale", "2|976|200643|171549|2005525|2093822|1796646"),
        ("k__Bacteria|p__Bacteroidota|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides|s__Bacteroides_vulgatus", "2|976|200643|171549|815|816|821"),
        ("k__Bacteria|p__Verrucomicrobiota|c__Verrucomicrobiae|o__Verrucomicrobiales|f__Akkermansiaceae|g__Akkermansia|s__Akkermansia_muciniphila", "2|74201|203494|48461|1647988|239934|239935"),
        ("k__Bacteria|p__Bacillota|c__Clostridia|o__Eubacteriales|f__Peptostreptococcaceae|g__Clostridioides|s__Clostridioides_difficile", "2|1239|186801|186802|186804|1870884|1496"),
        ("k__Bacteria|p__Bacillota|c__Bacilli|o__Lactobacillales|f__Lactobacillaceae|g__Lactobacillus|s__Lactobacillus_johnsonii", "2|1239|91061|186826|33958|1578|47770"),
    ]
    ab = [random.uniform(1, 40) for _ in sp]
    if meta["group"] == "treated":
        ab[3] *= 3  # C. difficile up in treated
    s = sum(ab)
    ab = [100 * a / s for a in ab]
    for (clade_name, tid), a in zip(sp, ab):
        rows.append((clade_name, tid, a))
    lines = hdr + [f"{c}\t{t}\t{a:.5f}\t" for c, t, a in rows]
    (DATA / f"{sample}_profile.tsv").write_text("\n".join(lines) + "\n")

def samtools_coverage(sample, meta):
    hdr = "#rname\tstartpos\tendpos\tnumreads\tcovbases\tcoverage\tmeandepth\tmeanbaseq\tmeanmapq"
    contigs = []
    for i in range(1, 13):
        ln = random.randint(5_000, 480_000)
        nr = random.randint(100, 90_000)
        covb = int(ln * random.uniform(0.55, 1.0))
        cov = 100 * covb / ln
        md = nr * 150 / ln
        contigs.append(f"contig_{i:03d}\t1\t{ln}\t{nr}\t{covb}\t{cov:.4f}\t{md:.4f}\t{random.uniform(33,37):.1f}\t{random.uniform(38,60):.1f}")
    (DATA / f"{sample}.coverage.tsv").write_text(hdr + "\n" + "\n".join(contigs) + "\n")

meta_lines = ["sample\tgroup\tmouse\tday\ttotal_reads"]
for sample, meta in SAMPLES.items():
    kraken2_report(sample, meta)
    metaphlan_profile(sample, meta)
    samtools_coverage(sample, meta)
    meta_lines.append(f"{sample}\t{meta['group']}\t{meta['mouse']}\t{meta['day']}\t{meta['reads']}")

# metadata: deliberately include one extra sample with no files (for merge/join exercises)
meta_lines.append("DE-14999-S2_extra_ctrl\tcontrol\tM12\t31\t5100000")
(DATA / "metadata.tsv").write_text("\n".join(meta_lines) + "\n")

print("Files written:")
for p in sorted(DATA.iterdir()):
    print(" ", p.name, p.stat().st_size, "bytes")
