"""Apply the compiled anomaly decisions to the collection pool: manifest v2.

    .venv/bin/python -m scripts.harvest.apply_clean [--variant strict|spec] [--keep-lexicon-split]

Reads (never modifies): docs/harvest/collection/admitted_all.jsonl (pool v1), the compiler outputs under
docs/harvest/analysis/ (clean_preview/*.jsonl.gz, rules.json, impact.json), split_repairs.json and the
Wikisource human transcriptions (reserved labels). Writes only under docs/harvest/collection/v2/.

Decisions applied (owner, 15 Oct 2026, "OK apply this"):
  * drop every line whose rule set is non-empty under the chosen variant (default = strict: R3 needs the
    low characters-per-pixel signal or two of its three signals; the R13 bad-page share is recomputed on it);
  * replace the label by the compiled label_v2 (R6 breathing-on-capital, R8 στ ligature, R15 book fixes);
  * move the Liddell-Scott lexicon (mixed/archive_b28038630, book 4c207e1e) wholly to train so every
    book sits in one split;
  * re-run the global label hold-out on the new labels (a train label equal to any dev/test or reserved
    Wikisource label is rejected, exactly as T28 did).
Bulk outputs (admitted_all_v2.jsonl, manifest_v2_*.json, import_real_v2_*.jsonl) are reproducible and
git-ignored; the small delta files (dropped_v2.jsonl, relabels_v2.jsonl, split_moves_v2.json,
rejected_global_v2.jsonl), validation_v2.json and CLEAN_REPORT.md are tracked.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import subprocess

from greekocr.harvest.collection import (
    CLASSES, SPLITS, digest, importer_row, normalize_label, read_jsonl, trainer_manifest, write_json,
    write_jsonl,
)
from scripts.harvest.collection import class_table, markdown_table, reserved_wikisource

LEXICON = ("mixed", "archive_b28038630")
RULE_ORDER = ["DROP_BOOK"] + [f"R{i}" for i in range(1, 16)]


def read_gz_jsonl(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def git_head(root: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def book_split_map(rows):
    books = defaultdict(set)
    for r in rows:
        books[r["source"], r["book_key"]].add(r["split"])
    return books


def run(root: Path, variant: str = "strict", lexicon_to_train: bool = True) -> str:
    root = root.resolve()
    coll = root / "docs/harvest/collection"
    analysis = root / "docs/harvest/analysis"
    out = coll / "v2"
    out.mkdir(parents=True, exist_ok=True)
    inputs = [coll / "admitted_all.jsonl", coll / "split_repairs.json",
              analysis / "clean_preview/admitted_all_clean_preview.jsonl.gz",
              analysis / "clean_preview/dropped_preview.jsonl.gz",
              analysis / "rules.json", analysis / "impact.json", analysis / "compile_decisions.py",
              analysis / "DECISIONS.md"]
    input_digests = {p.relative_to(root).as_posix(): digest(p) for p in inputs}

    # 1. compiler verdicts, keyed by id
    rule_key = "rules_strict" if variant == "strict" else "rules"
    dropped = {}      # id -> rules under the variant (non-empty)
    rescued = {}      # id -> (label_v2, relabel_rules) for lines the spec variant dropped but this one keeps
    spec_dropped = 0
    for d in read_gz_jsonl(analysis / "clean_preview/dropped_preview.jsonl.gz"):
        spec_dropped += 1
        if d[rule_key]:
            dropped[d["id"]] = d[rule_key]
        else:
            rescued[d["id"]] = (d["label_v2"], d["relabel_rules"])
    relabels = {}     # id -> (label_v2, relabel_rules without R11)
    for r in read_gz_jsonl(analysis / "clean_preview/admitted_all_clean_preview.jsonl.gz"):
        rules = [x for x in r["rules_applied"] if x != "R11"]
        if r["label_v2"] != r["label"]:
            relabels[r["id"]] = (r["label_v2"], rules)
    for i, (label2, rules) in rescued.items():
        if rules:
            relabels[i] = (label2, rules)

    # 2. walk the pool
    pool = read_jsonl(coll / "admitted_all.jsonl")
    before = Counter((r["script_class"], r["split"]) for r in pool)
    kept, drop_rows, relabel_rows, moves = [], [], [], []
    drop_by_rule = Counter()
    drop_by = defaultdict(Counter)
    seen = set()
    for r in pool:
        assert r["id"] not in seen, r["id"]
        seen.add(r["id"])
        if r["id"] in dropped:
            rules = dropped[r["id"]]
            drop_rows.append(dict(id=r["id"], wave=r["wave"], source=r["source"], book_key=r["book_key"],
                                  script_class=r["script_class"], split=r["split"], rules=rules, label=r["label"]))
            for rule in rules:
                drop_by_rule[rule] += 1
                drop_by["class"][rule, r["script_class"]] += 1
            continue
        row = dict(r)
        if r["id"] in relabels:
            label2, rules = relabels[r["id"]]
            row["label"] = label2
            row["label_v1"] = r["label"]
            row["rules_applied"] = rules
            relabel_rows.append(dict(id=r["id"], rules=rules, label_v1=r["label"], label=label2))
        else:
            row["rules_applied"] = []
        if lexicon_to_train and (r["wave"], r["source"]) == LEXICON and r["split"] != "train":
            moves.append(dict(id=r["id"], before=r["split"], after="train"))
            row["split_v1"] = r["split"]
            row["split"] = "train"
        kept.append(row)
    assert len(kept) + len(drop_rows) == len(pool)
    assert len(dropped) == len(drop_rows), "compiler drop ids missing from the pool"

    # 3. global label hold-out on the new labels (same policy as T28)
    reserved = reserved_wikisource(root, True)
    held = {normalize_label(r["label"]) for r in kept if r["split"] != "train"} | set(reserved)
    rows, rejected = [], []
    for r in kept:
        if r["split"] == "train" and normalize_label(r["label"]) in held:
            rejected.append(dict(id=r["id"], label=r["label"], reason="train label equals a dev/test or reserved label after relabel"))
        else:
            rows.append(r)
    assert all(r["book_key"] != "4c207e1e" or r["split"] == "train" for r in rows) or not lexicon_to_train

    # 4. document disjointness
    books = book_split_map(rows)
    multi = {f"{s}|{b}": sorted(v) for (s, b), v in books.items() if len(v) > 1}
    repairs = json.loads((coll / "split_repairs.json").read_text())["repairs"]
    repaired_sources = {(x["wave"], x["source"]) for x in repairs}
    if lexicon_to_train:
        repaired_sources.discard(LEXICON)   # the lexicon is one document again: doc id = book, not page

    # 5. outputs
    write_jsonl(out / "admitted_all_v2.jsonl", rows)
    write_jsonl(out / "dropped_v2.jsonl", drop_rows)
    write_jsonl(out / "relabels_v2.jsonl", relabel_rows)
    write_jsonl(out / "rejected_global_v2.jsonl", rejected)
    write_json(out / "split_moves_v2.json", dict(lexicon=LEXICON, policy="whole book to train" if lexicon_to_train else "unchanged",
                                                 moved=len(moves), by_split=dict(Counter(m["before"] for m in moves)), rows=moves))
    for split in SPLITS:
        group = [r for r in rows if r["split"] == split]
        with (out / f"manifest_v2_{split}.json").open("w") as stream:
            stream.write("[\n")
            for i, row in enumerate(group):
                stream.write((",\n" if i else "") + json.dumps(trainer_manifest(row), ensure_ascii=False))
            stream.write("\n]\n")
        write_jsonl(out / f"import_real_v2_{split}.jsonl", (importer_row(r, repaired_sources) for r in group))
    write_jsonl(out / "import_real_v2_all.jsonl", (importer_row(r, repaired_sources) for r in rows))

    after = Counter((r["script_class"], r["split"]) for r in rows)
    tall = lambda c: {cls: {s: c[cls, s] for s in SPLITS} for cls in CLASSES}  # noqa: E731
    relabel_by_rule = Counter(rule for x in relabel_rows for rule in x["rules"])
    sample = {}
    for p in sorted(out.glob("*")):
        if p.is_file() and p.name not in ("validation_v2.json", "CLEAN_REPORT.md"):
            sample[p.name] = dict(bytes=p.stat().st_size, sha256=digest(p))
    crop_missing = sum(not (root / r["crop_path"]).is_file() for r in rows[::97])
    validation = dict(schema="clean-v2-validation-1", variant=variant, lexicon_to_train=lexicon_to_train,
                      git_head=git_head(root), inputs=input_digests,
                      pool_v1=len(pool), spec_dropped=spec_dropped, dropped=len(drop_rows), rescued_by_variant=len(rescued),
                      relabelled=len(relabel_rows), relabel_by_rule=dict(relabel_by_rule), moved_to_train=len(moves),
                      rejected_global=len(rejected), admitted_v2=len(rows),
                      drop_by_rule={k: drop_by_rule[k] for k in RULE_ORDER if drop_by_rule[k]},
                      drop_by_rule_class={f"{k}|{c}": v for (k, c), v in sorted(drop_by["class"].items())},
                      per_class_split_before=tall(before), per_class_split_after=tall(after),
                      per_wave_class_split={w: tall(Counter((r["script_class"], r["split"]) for r in rows if r["wave"] == w))
                                            for w in sorted({r["wave"] for r in rows})},
                      books_in_several_splits=multi, crop_sample_checked=len(rows[::97]), crop_sample_missing=crop_missing,
                      outputs=sample, network_calls=0, google_calls=0)
    write_json(out / "validation_v2.json", validation)

    # 6. report
    splits = Counter(r["split"] for r in rows)
    classes = Counter(r["script_class"] for r in rows)
    lines = ["# Collection v2 (cleaned pool)", "",
             f"Built by `scripts/harvest/apply_clean.py` from pool v1 ({len(pool):,} lines) and the compiled analysis "
             f"decisions ([DECISIONS.md](../../analysis/DECISIONS.md), rules.json, impact.json) at git `{validation['git_head']}`. "
             f"Variant **{variant}**; lexicon {'moved wholly to train' if lexicon_to_train else 'split unchanged'}.", "",
             "## Totals", "",
             markdown_table(["Step", "Lines"], [
                 ["Pool v1", f"{len(pool):,}"],
                 [f"Dropped by rules ({variant})", f"{len(drop_rows):,}"],
                 ["Kept back vs the spec variant (weak R3/R13 hits)", f"{len(rescued):,}"],
                 ["Relabelled (label_v1 kept on the row)", f"{len(relabel_rows):,}"],
                 ["Lexicon lines moved dev/test → train", f"{len(moves):,}"],
                 ["Rejected by global label hold-out after relabel", f"{len(rejected):,}"],
                 ["**Admitted v2**", f"**{len(rows):,}**"]]),
             "## Drops by rule (a line may carry several)", "",
             markdown_table(["Rule", "Lines"], [[k, f"{drop_by_rule[k]:,}"] for k in RULE_ORDER if drop_by_rule[k]]),
             "## Relabels by rule", "",
             markdown_table(["Rule", "Lines"], [[k, f"{v:,}"] for k, v in sorted(relabel_by_rule.items())]),
             "## Class × split before", "", class_table(tall(before)),
             "## Class × split after", "", class_table(tall(after)),
             "## Checks", "",
             f"- Books present in more than one split: {len(multi)}" + (f" ({', '.join(sorted(multi))})" if multi else ""),
             f"- Crop sample checked: {len(rows[::97]):,} rows, missing files: {crop_missing}",
             f"- Reserved Wikisource human labels honoured: {len(reserved):,}",
             "- Pool v1, wave files and crops unchanged; no network or Google calls.", "",
             "Files: admitted_all_v2.jsonl (git-ignored, reproducible), manifest_v2_{train,dev,test}.json, "
             "import_real_v2_{all,train,dev,test}.jsonl (git-ignored), dropped_v2.jsonl, relabels_v2.jsonl, "
             "rejected_global_v2.jsonl, split_moves_v2.json, validation_v2.json (tracked).", ""]
    status = (f"CLEAN_V2: done | variant: {variant} | pool_v1: {len(pool)} | dropped: {len(drop_rows)} | relabelled: {len(relabel_rows)} | "
              f"moved: {len(moves)} | rejected: {len(rejected)} | admitted_v2: {len(rows)} | train: {splits['train']} | dev: {splits['dev']} | "
              f"test: {splits['test']} | poly: {classes['greek_poly']} | mono: {classes['greek_mono']} | cs: {classes['greek_latin_cs']} | "
              f"latin: {classes['latin']} | cyr: {classes['cyrillic']}")
    (out / "CLEAN_REPORT.md").write_text("\n".join(lines) + status + "\n")
    print(status, flush=True)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--variant", choices=("strict", "spec"), default="strict")
    parser.add_argument("--keep-lexicon-split", action="store_true")
    args = parser.parse_args()
    run(args.root, args.variant, not args.keep_lexicon_split)


if __name__ == "__main__":
    main()
