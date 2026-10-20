#!/usr/bin/env python3
"""T20: locally admit already-read lines, freeze held-out books, cut native crops.

Run from the repo: .venv/bin/python -m scripts.harvest.admit_round1
No provider adapter, HTTP client, model, or Git command is used.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import random
import statistics
import time

from PIL import Image, ImageDraw, ImageFont

from greekocr.harvest.admission import (
    CLASSES, REASONS, SEED, admit, apply_holdout_labels, crop_geometry,
    has_spacing_mark, inventory, page_quality, select_holdout_books, spatial_neighbours,
)

REPO = Path(__file__).resolve().parents[2]
OUT = Path("docs/harvest/round1")
BULK = Path("docs/harvest/harvest_big/round1")
SOURCES = ["greekocr/harvest/admission.py", "scripts/harvest/admit_round1.py",
           "scripts/harvest/validate_round1_admission.py", "tests/test_harvest_admission.py",
           "tests/test_round1_admission_outputs.py"]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def write_jsonl(path: Path, rows) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp.replace(path)


def stats(values: list[int]) -> dict:
    if not values:
        return dict(count=0)
    values = sorted(values)
    return dict(count=len(values), min=values[0], p05=values[int(.05 * (len(values) - 1))],
                median=statistics.median(values), mean=statistics.mean(values),
                p95=values[int(.95 * (len(values) - 1))], max=values[-1])


def choose_font(path: str | None = None):
    paths = [Path(path)] if path else [
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in paths:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), 20), candidate
    raise ValueError("pass --font pointing to a local Greek/Cyrillic-capable font")


def wrap_label(draw, text: str, font, width: int) -> list[str]:
    # Character wrapping also handles OCR tokens longer than a whole cell.
    lines, current = [], ""
    for char in text:
        trial = current + char
        if current and draw.textlength(trial, font=font) > width:
            lines.append(current)
            current = char
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [""]


def contact_sheets(repo: Path, admitted: list[dict], sheet_dir: Path, *, font_path=None) -> dict:
    font, font_file = choose_font(font_path)
    sheet_dir.mkdir(parents=True, exist_ok=True)
    metadata = {}
    for index, cls in enumerate(CLASSES):
        pool = [r for r in admitted if r["script_class"] == cls]
        chosen = random.Random(SEED + index).sample(sorted(pool, key=lambda r: r["id"]), min(60, len(pool)))
        cell_width, gap, margin, header = 820, 20, 24, 80
        tiles, max_height = [], 200
        probe = ImageDraw.Draw(Image.new("L", (1, 1)))
        for row in chosen:
            with Image.open(repo / row["crop_path"]) as source:
                thumb = source.copy()
            thumb.thumbnail((cell_width - 24, 180), Image.Resampling.LANCZOS)
            lines = wrap_label(probe, row["label"], font, cell_width - 24)
            height = thumb.height + 16 + 28 * len(lines) + 42
            max_height = max(max_height, height)
            tiles.append((row, thumb, lines))
        rows = max(1, (len(tiles) + 2) // 3)
        sheet = Image.new("L", (margin*2 + cell_width*3 + gap*2,
                                header + margin + rows*(max_height + gap)), 255)
        draw = ImageDraw.Draw(sheet)
        title = f"{cls} | {len(chosen)} unique crops / {len(pool)} admitted | seed {SEED + index} | labels below crops"
        draw.text((margin, 20), title, font=font, fill=0)
        if len(pool) < 60:
            draw.text((margin, 48), "All available crops shown; this class has fewer than 60 admitted lines.", font=font, fill=0)
        for i, (row, thumb, lines) in enumerate(tiles):
            left = margin + (i % 3)*(cell_width + gap)
            top = header + (i // 3)*(max_height + gap)
            draw.rectangle((left, top, left + cell_width, top + max_height), outline=180)
            sheet.paste(thumb, (left + 12, top + 12))
            y = top + 12 + thumb.height + 12
            for line in lines:
                draw.text((left + 12, y), line, font=font, fill=0)
                y += 28
            draw.text((left + 12, top + max_height - 30), f"{row['id']} | {row['split']}", font=font, fill=90)
        destination = sheet_dir / (cls + ".jpg")
        sheet.save(destination, quality=92)
        metadata[cls] = dict(path=str(destination.relative_to(repo)), sha256=sha(destination),
                             width=sheet.width, height=sheet.height, count=len(chosen),
                             ids=[r["id"] for r in chosen], seed=SEED + index,
                             font=str(font_file), font_size=20)
    return metadata


def escaped(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ↵ ").replace("\r", "").replace("\t", " ⇥ ")


def report(summary: dict, rejected: list[dict], mixed_examples: list[dict], held: list[dict]) -> str:
    s = summary
    lines = ["# T20 — Wave 0 line admission", "",
             f"{s['input_lines']:,} DocAI lines on {s['pages']:,} pages from {s['books']} books. "
             f"**{s['admitted']:,} admitted, {s['rejected']:,} rejected, {s['crops']:,} native grey crops.** "
             "Local, offline; no new Google calls or Git writes.", "",
             "Admission evaluates every failing rule in order. Confidence is the stored mean of anchored DocAI symbols; "
             "the legacy `tier`, Vision reading and `counted` flag do not decide admission. "
             "Inventory uses the supplied Unicode code points; label normalization occurs after the gates.", "",
             "The low-confidence page denominator is all lines with at least 10 letters; the tall-box denominator is "
             "all provider lines. Thresholds are strictly greater than 50% and 30%. "
             "Greek-majority lines with a whole Latin word of at least two letters take the code-switch class first; "
             "letter-count ties resolve Greek, Latin, Cyrillic. Roman tokens using only IVXLC and Greek Ι/Χ are exempt "
             "from mixed-word rejection. Unicode decimal digits are counted as digits; shared Greek sentence punctuation "
             "is `. , ; : ! ? · ; · … « » ' ’ ‘ ᾽`; other nonspace nonletters are other symbols.", "",
             "Crop neighbours are the nearest distinct-centre rows above/below sharing at least half the narrower horizontal extent, "
             "computed from **all** DocAI lines on the page. Provider-order column jumps and equal-centre fragments "
             "are not vertical neighbours. Trimming uses overlap greater than 15% of the original line height, "
             "then midpoint cuts, outward pixel rounding, and 2 px vertical / 4 px horizontal padding inside the page. "
             "Original `bbox` and actual `crop_bbox` are both retained. No crop is resized. Duplicate DocAI boxes are "
             "retained when the stated text gates admit their lines; physical label accuracy remains for owner review.", "",
             "## Class × split", "", "| Class | Train | Dev | Test | Total |", "|---|---:|---:|---:|---:|"]
    for cls in CLASSES:
        c = s["per_class_split"][cls]
        lines.append(f"| {cls} | {c['train']} | {c['dev']} | {c['test']} | {sum(c.values())} |")
    lines += ["", "## Rejection reasons", "", "A rejected line may occur in several rows.", "",
              "| Reason | Lines |", "|---|---:|"]
    lines += [f"| {reason} | {s['per_reason'][reason]} |" for reason in REASONS]
    lines += ["", "## Decades", "", "| Decade | Books | Held-out books | Train | Dev | Test | Rejected |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for decade, c in s["per_decade"].items():
        lines.append(f"| {decade}s | {c['books']} | {c['holdout_books']} | {c['train']} | {c['dev']} | {c['test']} | {c['rejected']} |")
    lines += ["", "## Held-out books", "",
              "Seed 20261015; two per decade where capacity allows, then seeded draws from remaining books with ≥300 "
              "admitted lines before fallback books. A seeded shuffle assigns five dev and fifteen test books. "
              "Counts in this table are after admission and before O5 (O5 drops train only).", ""]
    lines += ["**Capacity exception:** " + message for message in s["holdout_policy"]["capacity_exceptions"]]
    lines += ["", "| Book key | Title | Year | Decade | Split | Admitted lines |", "|---|---|---:|---:|---|---:|"]
    for b in held:
        lines.append(f"| {b['book_key']} | {escaped(b['title'])} | {b['year']} | {b['decade']} | {b['split']} | {b['admitted_lines']} |")
    lines += ["", f"O5 removed **{s['label_in_holdout']:,} train lines** equal to an admitted dev/test label. "
              "Equality is NFC and whitespace-collapsed, with DOT ABOVE already converted to middle dot; case and other marks are preserved.", "",
              "## Native crop sizes", "", "| Measure | Min | p05 | Median | Mean | p95 | Max |", "|---|---:|---:|---:|---:|---:|---:|"]
    for measure in ("width", "height"):
        c = s["crop_size_stats"][measure]
        if c["count"]:
            lines.append(f"| {measure} px | {c['min']} | {c['p05']} | {c['median']} | {c['mean']:.2f} | {c['p95']} | {c['max']} |")
    lines += ["", f"Trimmed: {s['trimmed']:,}. Labels with standalone spacing marks: {s['has_spacing_mark']:,}. "
              "Spacing U+1FBF/U+1FBD/U+0384 marks between letters remain unchanged; the flag records them for a later label decision.", "",
              "## Contact sheets", "", "The sheets are seeded after admission and O5, with one 20 px label type size. "
              "Crops may be reduced for the sheet only. Owner accuracy review is pending.", "",
              "| Class | Unique examples | Sheet |", "|---|---:|---|"]
    for cls, c in s["contact_sheets"].items():
        lines.append(f"| {cls} | {c['count']} | `{c['path']}` |")
    lines += ["", "## Bad pages", "", "| Page | Eligible lines | Low-confidence lines | Tall / all | Triggers |", "|---|---:|---:|---|---|"]
    for p in s["bad_pages"]:
        lines.append(f"| {p['page_id']} | {p['eligible_lines']} | {p['low_confidence']} | {p['tall_boxes']} / {p['lines']} | {', '.join(p['triggers'])} |")
    lines += ["", "## Ten example mixed words", "", "| Word | Line |", "|---|---|"]
    lines += [f"| {escaped(x['word'])} | {x['id']} |" for x in mixed_examples]
    lines += ["", "## Rejected examples", "", "Up to 30 actual lines per reason; all available are shown when fewer exist. "
              "Text is the original DocAI text, with Markdown delimiters escaped and whitespace displayed."]
    for reason in REASONS:
        examples = random.Random(SEED + REASONS.index(reason)).sample(
            [r for r in rejected if reason in r["reasons"]], min(30, s["per_reason"][reason]))
        lines += ["", f"### {reason} ({len(examples)} examples)", "", "| Line | All reasons | DocAI text |", "|---|---|---|"]
        lines += [f"| {r['id']} | {', '.join(r['reasons'])} | {escaped(r['docai_text'])} |" for r in examples]
    lines += ["", "## Reproduce and validate", "", "```sh",
              ".venv/bin/python -m pytest tests/test_harvest_admission.py tests/test_round1_admission_outputs.py",
              ".venv/bin/python -m scripts.harvest.admit_round1",
              ".venv/bin/python -m scripts.harvest.validate_round1_admission", "```", "",
              "Input and source hashes, contact-sheet selections and output hashes are in `admission_inventory.json`; "
              "full corpus/crop validation is in `admission_validation.json`.", ""]
    return "\n".join(lines)


def build(repo: Path = REPO, *, records_path: Path = OUT / "records_all.jsonl",
          manifest_path: Path = OUT / "manifest_all.json", selection_path: Path = OUT / "selection.json",
          output_dir: Path = OUT, bulk_dir: Path = BULK, holdout_count=20, dev_count=5,
          make_sheets=True, font_path=None, emit=print) -> dict:
    started = time.monotonic()
    inputs = [records_path, manifest_path, selection_path]
    input_hashes = {str(p): sha(repo / p) for p in inputs}
    records = read_jsonl(repo / records_path)
    manifest = json.loads((repo / manifest_path).read_text())
    catalogue = {b["key"]: b for b in json.loads((repo / selection_path).read_text())["books"]}
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("duplicate input line id")
    manifest_by_image = {p["image"]: p for p in manifest}
    if len(manifest_by_image) != len(manifest):
        raise ValueError("duplicate manifest image")
    pages = defaultdict(list)
    for row in records:
        pages[row["page_id"]].append(row)
        if row["image"] not in manifest_by_image:
            raise ValueError("record image absent from manifest")
        if row["book_key"] not in catalogue:
            raise ValueError("missing book title metadata")
    quality = page_quality(records)
    eligible, rejected, inventories, mixed_examples, seen_words = [], [], Counter(), [], set()
    foreign_scripts, foreign_names = Counter(), Counter()
    for row in records:
        inv = inventory(row["docai_text"])
        inventories.update({k: inv[k] for k in ("greek_letters", "latin_letters", "cyrillic_letters",
                                               "other_letters", "digits", "greek_punctuation", "other_symbols")})
        foreign_scripts.update(inv["other_script_letters"])
        foreign_names.update(inv["other_letter_names"])
        for word in inv["mixed_words"]:
            if word not in seen_words and len(mixed_examples) < 10:
                seen_words.add(word)
                mixed_examples.append(dict(word=word, id=row["id"]))
        good, cls, reasons, label = admit(dict(row, bad_page=quality[row["page_id"]]["bad_page"]))
        if good:
            eligible.append(dict(id=row["id"], page_id=row["page_id"], book_key=row["book_key"],
                year=row["year"], decade=row["decade"], script_class=cls, label=label,
                has_spacing_mark=has_spacing_mark(label), confidence=row["confidence"], bbox=row["bbox"],
                source="anemi_round1", licence="anemi-research-internal", read_batch=row["read_batch"],
                docai_text=row["docai_text"]))
        else:
            rejected.append(dict(id=row["id"], reasons=reasons, docai_text=row["docai_text"]))
    book_counts = Counter(r["book_key"] for r in eligible)
    book_input = {r["book_key"]: r for r in records}
    books = [dict(book_key=key, title=catalogue[key]["title"], year=row["year"],
                  decade=row["decade"], admitted_lines=book_counts[key]) for key, row in sorted(book_input.items())]
    held = select_holdout_books(books, count=holdout_count, dev_count=dev_count)
    splits = {b["book_key"]: b["split"] for b in held}
    for row in eligible:
        row["split"] = splits.get(row["book_key"], "train")
    admitted, o5_rejected = apply_holdout_labels(eligible)
    rejected.extend(o5_rejected)
    rejected.sort(key=lambda r: r["id"])
    emit(f"admission: {len(eligible)} before O5; {len(o5_rejected)} train duplicates removed; {len(admitted)} final", flush=True)
    admitted_by_id = {r["id"]: r for r in admitted}
    crop_root = repo / bulk_dir / "crops"
    crop_widths, crop_heights, page_inventory = [], [], []
    for page_index, (page_id, rows) in enumerate(sorted(pages.items()), 1):
        page_rows = [r for r in rows if r["id"] in admitted_by_id]
        if not page_rows:
            continue
        page_path = repo / rows[0]["image"]
        payload = page_path.read_bytes()
        page_sha = hashlib.sha256(payload).hexdigest()
        manifest_sha = manifest_by_image[rows[0]["image"]]["gate"]["image_sha256"]
        if any(r["image"] != rows[0]["image"] or r["image_sha256"] != page_sha for r in rows) or page_sha != manifest_sha:
            raise ValueError("page pixels differ from record/manifest custody: " + page_id)
        neighbours = spatial_neighbours(rows)
        with Image.open(io.BytesIO(payload)) as image:
            if image.mode != "L":
                raise ValueError("expected native grey page: " + page_id)
            image.load()
            page_inventory.append(dict(page_id=page_id, path=rows[0]["image"], sha256=page_sha,
                                       width=image.width, height=image.height))
            for input_row in page_rows:
                row = admitted_by_id[input_row["id"]]
                bounds, trimmed = crop_geometry(row["bbox"], *neighbours[row["id"]], image.size)
                crop = image.crop(tuple(bounds))
                path = crop_root / row["book_key"] / f"p{input_row['page']:06d}-l{input_row['line_number']:04d}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                stream = io.BytesIO()
                crop.save(stream, format="PNG", compress_level=3)
                crop_bytes = stream.getvalue()
                # Exact deterministic crops support safe repeat runs without needless rewrites.
                digest = hashlib.sha256(crop_bytes).hexdigest()
                if not path.is_file() or sha(path) != digest:
                    path.write_bytes(crop_bytes)
                row.update(crop_path=str(path.relative_to(repo)), crop_sha256=digest,
                           crop_width=crop.width, crop_height=crop.height,
                           crop_bbox=bounds, trimmed=trimmed)
                row.pop("docai_text")
                crop_widths.append(crop.width)
                crop_heights.append(crop.height)
        if page_index % 100 == 0:
            emit(f"crops: page {page_index}/{len(pages)}, {len(crop_widths)} written, {time.monotonic()-started:.1f}s", flush=True)
    output = repo / output_dir
    output.mkdir(parents=True, exist_ok=True)
    sheets = contact_sheets(repo, admitted, repo / bulk_dir / "admission_sheet", font_path=font_path) if make_sheets else {}
    per_reason = Counter(reason for row in rejected for reason in row["reasons"])
    per_split = Counter(row["split"] for row in admitted)
    per_class = Counter(row["script_class"] for row in admitted)
    decade_capacity = Counter(b["decade"] for b in books)
    held_decades = Counter(b["decade"] for b in held)
    admitted_decades = Counter((r["decade"], r["split"]) for r in admitted)
    rejected_ids = {r["id"] for r in rejected}
    rejected_decades = Counter(r["decade"] for r in records if r["id"] in rejected_ids)
    bad_pages = [dict(page_id=p, book_key=pages[p][0]["book_key"], page=pages[p][0]["page"],
                      **q) for p, q in quality.items() if q["bad_page"]]
    summary = dict(schema="t20-admission-1", generated_at=datetime.now(timezone.utc).isoformat(),
        seed=SEED, input_lines=len(records), pages=len(pages), books=len(books),
        admitted_before_o5=len(eligible), admitted=len(admitted), rejected=len(rejected),
        crops=len(crop_widths), trimmed=sum(r["trimmed"] for r in admitted),
        has_spacing_mark=sum(r["has_spacing_mark"] for r in admitted),
        per_reason={reason: per_reason[reason] for reason in REASONS},
        per_split={split: per_split[split] for split in ("train", "dev", "test")},
        per_class={cls: per_class[cls] for cls in CLASSES},
        per_class_split={cls: {split: sum(r["script_class"] == cls and r["split"] == split for r in admitted)
                              for split in ("train", "dev", "test")} for cls in CLASSES},
        per_decade={str(d): dict(books=decade_capacity[d], holdout_books=held_decades[d],
                                train=admitted_decades[d, "train"], dev=admitted_decades[d, "dev"],
                                test=admitted_decades[d, "test"], rejected=rejected_decades[d]) for d in sorted(decade_capacity)},
        crop_size_stats=dict(width=stats(crop_widths), height=stats(crop_heights)),
        label_in_holdout=len(o5_rejected), bad_pages=bad_pages, contact_sheets=sheets,
        character_inventory=dict(counts=dict(inventories), other_script_letters=dict(foreign_scripts),
                                 other_letter_names=dict(foreign_names)),
        holdout_policy=dict(count=holdout_count, dev=dev_count, test=holdout_count-dev_count,
                            preferred_admitted_lines=300, minimum_per_decade=2,
                            capacity_exceptions=[f"{d}s has only {n} round-1 book; selected all {n}, so the requested two cannot be supplied."
                                                 for d, n in sorted(decade_capacity.items()) if n < 2]),
        crop_neighbour_policy="nearest distinct vertical centre sharing >=50% of narrower horizontal extent; all provider boxes",
        crop_rounding="floor left/top, ceil right/bottom after trim; then 4 px horizontal and 2 px vertical in-page padding",
        seconds=time.monotonic()-started)
    if len(admitted) + len(rejected) != len(records) or len(crop_widths) != len(admitted):
        raise AssertionError("line/crop reconciliation failed")
    if {str(p): sha(repo / p) for p in inputs} != input_hashes:
        raise ValueError("input changed during run")
    write_json(output / "holdout_books.json", held)
    write_jsonl(output / "admitted.jsonl", admitted)
    write_jsonl(output / "rejected.jsonl", rejected)
    write_json(output / "admission_summary.json", summary)
    (output / "ADMISSION.md").write_text(report(summary, rejected, mixed_examples, held))
    outputs = ["holdout_books.json", "admitted.jsonl", "rejected.jsonl", "admission_summary.json", "ADMISSION.md"]
    write_json(output / "admission_inventory.json", dict(schema="t20-inventory-1", inputs=input_hashes,
        sources={p: sha(repo / p) for p in SOURCES if (repo / p).is_file()},
        outputs={str(output_dir / p): sha(output / p) for p in outputs},
        page_images=page_inventory,
        crops="Every crop path/hash/dimension is recorded in admitted.jsonl",
        contact_sheets=sheets, network_calls=0, google_calls=0, git_writes=0))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="local Greek/Cyrillic font for contact sheets")
    args = parser.parse_args()
    result = build(font_path=args.font)
    print(json.dumps({k: result[k] for k in ("admitted", "rejected", "per_split", "per_class", "crops", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
