"""Offline T28 collection close-out. Original wave files and crops are read only."""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import re
import unicodedata

from .admission import normalize_label

WAVES = ("round1", "vouli", "round2", "parliament", "openarchives", "mixed", "cyrillic", "wikisource")
CLASSES = ("greek_poly", "greek_mono", "greek_latin_cs", "latin", "cyrillic", "furniture")
SPLITS = ("train", "dev", "test")
SEED = 20261015
FIELDS = ("id", "wave", "source", "licence", "source_url", "book_key", "page_id", "year",
          "decade", "script_class", "split", "label", "human_label", "confidence", "bbox",
          "crop_path", "crop_sha256", "crop_width", "crop_height", "read_batch", "attribution",
          "human_transcription_licence")
MANIFEST_FIELDS = ("crop", "label", "script_class", "source", "licence", "wave", "year")
BRIEFS = ("T20_line_admission_crops.md", "T21_vouli_reads.md", "T22_round2_polytonic.md",
          "T23_parliament_modern.md", "T24c_openarchives_modern.md", "T25_mixed_script.md",
          "T26_cyrillic.md", "T27d_wikisource_test.md")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")


def safe_crop_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not value or path.as_posix() != value:
        raise ValueError(f"crop must be a canonical repo-relative path: {value!r}")
    return value


def normalize_row(raw: dict, wave: str, urls: dict | None = None) -> dict:
    """Keep round-1 field names; unavailable metadata is explicitly null."""
    row = {field: raw.get(field) for field in FIELDS}
    row.update(wave=wave, label=normalize_label(raw["label"]))
    row["source_url"] = raw.get("source_url") or (urls or {}).get(raw["book_key"])
    if wave != "wikisource":
        row["human_label"] = row["human_transcription_licence"] = None
    row["crop_width"] = raw.get("crop_width", raw.get("width"))
    row["crop_height"] = raw.get("crop_height", raw.get("height"))
    validate_row(row)
    return row


def validate_row(row: dict) -> None:
    if set(row) != set(FIELDS):
        raise ValueError("nonuniform collection schema")
    for key in ("id", "wave", "source", "licence", "book_key", "page_id", "label"):
        if not isinstance(row[key], str) or not row[key].strip():
            raise ValueError(f"missing/non-string {key}")
    if row["wave"] not in WAVES or row["script_class"] not in CLASSES or row["split"] not in SPLITS:
        raise ValueError("unknown wave, class or split")
    if row["wave"] == "wikisource" and row["split"] == "train":
        raise ValueError("Wikisource must remain held out")
    if row["wave"] != "wikisource" and row["human_label"] is not None:
        raise ValueError("human_label is Wikisource-only")
    safe_crop_path(row["crop_path"])
    if not re.fullmatch(r"[0-9a-f]{64}", row["crop_sha256"] or ""):
        raise ValueError("invalid crop sha256")
    for key in ("crop_width", "crop_height"):
        if type(row[key]) is not int or row[key] <= 0:
            raise ValueError(f"invalid {key}")
    for key in ("year", "decade"):
        if row[key] is not None and type(row[key]) is not int:
            raise ValueError(f"invalid {key}")
    if row["year"] is not None and row["decade"] != row["year"] // 10 * 10:
        raise ValueError("year/decade mismatch")
    confidence = row["confidence"]
    if not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("invalid confidence")
    box = row["bbox"]
    if (not isinstance(box, list) or len(box) != 4
            or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in box)
            or box[2] <= box[0] or box[3] <= box[1]):
        raise ValueError("invalid bbox")


def check_duplicates(rows: list[dict]) -> None:
    """Fail before filtering; duplicate IDs are never silently wave-prefixed."""
    for field in ("id", "crop_path"):
        seen = set()
        for row in rows:
            if row[field] in seen:
                raise ValueError(f"duplicate {field}: {row[field]}")
            seen.add(row[field])


def tallies(rows: list[dict]) -> dict:
    counts = Counter((r["script_class"], r["split"]) for r in rows)
    return {c: {s: counts[c, s] for s in SPLITS} for c in CLASSES}


def repair_splits(rows: list[dict], holdouts: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Repair entire sources by page, only for the explicit lexicon or proven starvation."""
    result = [dict(r) for r in rows]
    groups = defaultdict(list)
    for row in result:
        groups[row["wave"], row["source"]].append(row)
    candidates = {}
    lexicon = ("mixed", "archive_b28038630")
    if lexicon in groups:
        candidates[lexicon] = "explicit T28 wave-5 part-C lexicon repair"
    scan = []
    for wave in WAVES:
        wave_rows = [r for r in result if r["wave"] == wave]
        for cls, splits in tallies(wave_rows).items():
            if splits["train"] or not splits["test"]:
                continue
            sources = {r["source"] for r in wave_rows if r["script_class"] == cls}
            eligible = False
            if wave != "wikisource" and len(sources) == 1:
                key = (wave, next(iter(sources)))
                group = groups[key]
                held_keys = {h["book_key"] for h in holdouts.get(wave, [])}
                eligible = (all(r["split"] != "train" for r in group)
                            and {r["book_key"] for r in group} <= held_keys)
                if eligible:
                    candidates.setdefault(key, f"{cls} has train=0/test>0; single held-out source")
            scan.append(dict(wave=wave, script_class=cls, sources=sorted(sources), repair_eligible=eligible))
    repairs = []
    for (wave, source), reason in sorted(candidates.items()):
        group = groups[wave, source]
        pages = sorted({r["page_id"] for r in group})
        if len(pages) < 3:
            raise ValueError(f"cannot repair {wave}/{source}: fewer than three pages")
        random.Random(SEED).shuffle(pages)
        ntrain, ndev = int(len(pages) * .7), int(len(pages) * .1)
        assignments = {p: "train" if i < ntrain else "dev" if i < ntrain + ndev else "test"
                       for i, p in enumerate(pages)}
        before = tallies(group)
        changes = []
        for row in group:
            if row["split"] != assignments[row["page_id"]]:
                changes.append(dict(id=row["id"], before=row["split"], after=assignments[row["page_id"]]))
            row["split"] = assignments[row["page_id"]]
        repairs.append(dict(wave=wave, source=source, reason=reason, seed=SEED,
                            pages=len(pages), page_splits=dict(Counter(assignments.values())),
                            page_assignments=dict(sorted(assignments.items())),
                            before=before, after_page_repair=tallies(group), changed_rows=changes))
    return result, repairs, scan


def global_holdout(rows: list[dict], reserved: dict[str, list[str]] | None = None) -> tuple[list[dict], list[dict]]:
    held = defaultdict(list)
    for label, evidence in (reserved or {}).items():
        held[normalize_label(label)].extend(evidence)
    for row in rows:
        if row["split"] in ("dev", "test"):
            held[normalize_label(row["label"])].append(f'{row["wave"]}:{row["id"]}')
            if row.get("human_label"):
                held[normalize_label(row["human_label"])].append(f'human:{row["wave"]}:{row["id"]}')
    kept, rejected = [], []
    for row in rows:
        matches = held.get(normalize_label(row["label"]), [])
        if row["split"] == "train" and matches:
            rejected.append(dict(row, reason="label_in_holdout", reasons=["label_in_holdout"],
                                 matching_holdout_labels=sorted(set(matches))))
        else:
            kept.append(row)
    return kept, rejected


def cap_source(source: str) -> str:
    # Shared institutions/repositories must not gain a separate cap allowance per wave.
    if source in ("vouli_parliament_1850s", "parliament_proceedings_1975_2000"):
        return "hellenic_parliament"
    return source.replace("openarchives_mixed_", "openarchives_", 1)


def source_caps(rows: list[dict]) -> list[dict]:
    counts = Counter((r["script_class"], cap_source(r["source"])) for r in rows if r["split"] == "train")
    totals = Counter(r["script_class"] for r in rows if r["split"] == "train")
    return [dict(script_class=c, source=s, train=n, class_train=totals[c], share=n / totals[c],
                 over_40_percent=n * 5 > totals[c] * 2)
            for (c, s), n in sorted(counts.items())]


def check_crops(root: Path, rows: list[dict], sample: int = 2000) -> dict:
    """Stat EVERY crop, hash/decode the deterministic sample independently of row order."""
    from PIL import Image
    root = root.resolve()
    output = {}
    for wave in WAVES:
        group = [r for r in rows if r["wave"] == wave]
        for row in group:
            path = root / safe_crop_path(row["crop_path"])
            if not path.is_file() or not path.resolve().is_relative_to(root):
                raise ValueError(f"missing/outside crop: {path}")
        selected = sorted(group, key=lambda r: sha256(f'{SEED}:{wave}:{r["id"]}'.encode()).digest())[:sample]
        for row in selected:
            path = root / row["crop_path"]
            if digest(path) != row["crop_sha256"]:
                raise ValueError(f"crop hash mismatch: {path}")
            with Image.open(path) as img:
                if img.size != (row["crop_width"], row["crop_height"]):
                    raise ValueError(f"crop dimension mismatch: {path}")
                img.verify()
        output[wave] = dict(existence_checked=len(group), sha256_and_dimensions_checked=len(selected),
                            sampled_ids=[r["id"] for r in selected], errors=0)
    return output


def trainer_manifest(row: dict) -> dict:
    return {key: row["crop_path"] if key == "crop" else row[key] for key in MANIFEST_FIELDS}


def importer_row(row: dict, page_repaired_sources: set[tuple[str, str]]) -> dict:
    repaired = (row["wave"], row["source"]) in page_repaired_sources
    return dict(trainer_manifest(row), id=row["id"],
                doc=f'{row["wave"]}:{row["page_id"] if repaired else row["book_key"]}',
                split={"train": "train", "dev": "val", "test": "reserved"}[row["split"]],
                source_dataset=row["source"], license=row["licence"], source_url=row["source_url"],
                attribution=row["attribution"], label_tier="silver", admitted=True)


def read_wave(root: Path, wave: str) -> dict:
    directory = root / "docs/harvest" / wave
    summary_path = directory / "admission_summary.json"
    reports = {name: (directory / name).read_text() for name in ("READS.md", "ADMISSION.md")
               if (directory / name).is_file()}
    if not directory.exists() or not summary_path.exists():
        return dict(status="not delivered", why="wave folder missing" if not directory.exists()
                    else "admission_summary.json absent", summary={}, rows=[], holdouts=[], reports=reports)
    summary = json.loads(summary_path.read_text())
    for name in ("admitted.jsonl", "rejected.jsonl", "holdout_books.json"):
        if not (directory / name).is_file():
            raise ValueError(f"delivered wave {wave} missing {name}")
    rows = read_jsonl(directory / "admitted.jsonl")
    if len(rows) != summary["admitted"]:
        raise ValueError(f"{wave}: admitted count differs from summary")
    rejections = read_jsonl(directory / "rejected.jsonl")
    if len(rejections) != summary["rejected"]:
        raise ValueError(f"{wave}: rejected count differs from summary")
    reasons = Counter(reason for row in rejections
                      for reason in row.get("reasons", [row["reason"]] if "reason" in row else []))
    if dict(reasons) != {k: v for k, v in summary["per_reason"].items() if v}:
        raise ValueError(f"{wave}: rejection reasons differ from summary")
    return dict(status="delivered", why=summary.get("status", "admission artifacts present"),
                summary=summary, rows=rows, holdouts=json.loads((directory / "holdout_books.json").read_text()),
                reports=reports, rejection_reasons=dict(sorted(reasons.items())))


def ledger_cost(root: Path, wave: str) -> dict:
    directory = root / "docs/harvest/harvest_big" / wave / "google"
    paths = sorted(directory.glob("budget*.jsonl"))
    totals, seen, entries = Counter(), set(), []
    for path in paths:
        rows = read_jsonl(path)
        for row in rows:
            key = (row["engine"], row["key"])
            if key in seen:
                raise ValueError(f"duplicate budget reservation: {wave}/{key}")
            seen.add(key)
            if row["state"] != "reserved" or type(row["micro_usd"]) is not int or row["micro_usd"] < 0:
                raise ValueError(f"unexpected budget entry in {path}")
            totals[row["engine"]] += row["micro_usd"]
        entries.append(dict(path=path.relative_to(root).as_posix(), sha256=digest(path),
                            reservations=len(rows), micro_usd=sum(r["micro_usd"] for r in rows)))
    receipt = root / "docs/harvest" / wave / "cost_receipt.json"
    micro_usd = sum(totals.values())
    if receipt.exists():
        cost = json.loads(receipt.read_text())["cost_usd"]
        if round(cost * 1_000_000) != micro_usd:
            raise ValueError(f"{wave} budget/receipt cost mismatch")
    return dict(ledger_usd=micro_usd / 1_000_000, ledger_micro_usd=micro_usd,
                ledger_by_engine_usd={k: v / 1_000_000 for k, v in sorted(totals.items())},
                budget_ledgers=entries, cost_known=bool(paths) or receipt.exists())


def mix_marginals(rows: list[dict]) -> dict:
    decades, lengths, classes = Counter(), Counter(), Counter()
    digits = caps = 0
    for row in rows:
        text = row["label"]
        n = len(text)
        bucket = "0-19" if n < 20 else "20-39" if n < 40 else "40-79" if n < 80 else "80-139" if n < 140 else "140+"
        lengths[bucket] += 1
        decades[str(row["decade"]) if row["decade"] is not None else "unknown"] += 1
        classes[row["script_class"]] += 1
        digits += any(unicodedata.category(c) == "Nd" for c in text)
        caps += text.isupper()
    return dict(total=len(rows), script_class={c: classes[c] for c in CLASSES},
                decade=dict(sorted(decades.items())),
                length_buckets={k: lengths[k] for k in ("0-19", "20-39", "40-79", "80-139", "140+")},
                digit_bearing=digits, all_caps=caps,
                digit_bearing_share=digits / len(rows) if rows else 0,
                all_caps_share=caps / len(rows) if rows else 0)
