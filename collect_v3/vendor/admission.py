"""Offline Wave-0 admission contracts. No I/O, readers, or text correction.

Inventory counts the supplied code points (Unicode category L for letters).
The record confidence field is the previously computed mean DocAI symbol score.
Call ``page_quality`` first and add its ``bad_page`` boolean to each record.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import math
import random
import unicodedata as ud
from typing import Iterable, Mapping, Sequence

CLASSES = ("greek_poly", "greek_mono", "greek_latin_cs", "latin", "cyrillic")
REASONS = ("short_line", "low_confidence", "tall_box", "symbol_heavy",
           "foreign_script", "mixed_word", "bad_page", "label_in_holdout")
SEED = 20261015
ROMAN = frozenset("IVXLCΙΧ")
SPACING_MARKS = frozenset("\u1fbf\u1fbd\u0384")
POLY_MARKS = frozenset("\u0313\u0314\u0342\u0345\u0300")
# Shared sentence marks, Greek question mark/ano teleia, and quotation marks.
GREEK_PUNCTUATION = frozenset(".,;:!?·\u037e\u0387…«»'’‘\u1fbd")


@lru_cache(maxsize=8192)
def letter_script(char: str) -> str | None:
    """Classify letters by Unicode name; nonletters have no script vote."""
    if not ud.category(char).startswith("L"):
        return None
    name = ud.name(char, "UNNAMED")
    for script in ("GREEK", "LATIN", "CYRILLIC"):
        if script in name:
            return script.lower()
    return "other"


def _other_name(char: str) -> str:
    name = ud.name(char, "UNNAMED")
    if name.startswith(("CJK", "IDEOGRAPHIC")):
        return "CJK"
    # Full Unicode name is retained separately, so this grouping loses no detail.
    return name.split(" LETTER", 1)[0].split(" SYLLABLE", 1)[0].split(" CHARACTER", 1)[0]


def words(text: str) -> list[str]:
    """Whitespace, punctuation and = / - delimit; combining marks stay attached."""
    result, current = [], []
    for char in text:
        if char.isspace() or char in "=-/" or ud.category(char).startswith("P"):
            if current:
                result.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        result.append("".join(current))
    return result


def inventory(text: str) -> dict:
    """Return script/character counts, foreign Unicode names and mixed words.

Roman-number tokens containing ONLY IVXLC and Greek Ι/Χ are exempt from
mixed-word rejection. Other-script letters vote as one script for that rule.
Digits are Unicode decimal digits (Nd); all remaining nonspace characters
are accounted for as Greek punctuation or other symbols.
"""
    counts = Counter()
    foreign, foreign_names = Counter(), Counter()
    for char in text:
        script = letter_script(char)
        if script:
            counts[script + "_letters"] += 1
            if script == "other":
                foreign[_other_name(char)] += 1
                foreign_names[ud.name(char, f"U+{ord(char):04X}")] += 1
        elif ud.category(char) == "Nd":
            counts["digits"] += 1
        elif char in GREEK_PUNCTUATION:
            counts["greek_punctuation"] += 1
        elif not char.isspace():
            counts["other_symbols"] += 1
    mixed, latin_words = [], []
    for word in words(text):
        letters = [char for char in word if letter_script(char)]
        scripts = {letter_script(char) for char in letters}
        if len(scripts) >= 2 and not (word and set(word) <= ROMAN):
            mixed.append(word)
        if len(letters) >= 2 and scripts == {"latin"} and all(
                letter_script(char) or ud.category(char).startswith("M") for char in word):
            latin_words.append(word)
    result = {key: counts[key] for key in (
        "greek_letters", "latin_letters", "cyrillic_letters", "other_letters",
        "digits", "greek_punctuation", "other_symbols")}
    result.update(other_script_letters=dict(sorted(foreign.items())),
                  other_letter_names=dict(sorted(foreign_names.items())),
                  mixed_words=mixed, latin_words=latin_words,
                  letter_count=sum(counts[s + "_letters"] for s in ("greek", "latin", "cyrillic", "other")),
                  nonspace_count=sum(not char.isspace() for char in text))
    return result


def normalize_label(text: str) -> str:
    # Replace before NFC: NFC canonically maps U+0387 ano teleia to U+00B7 too.
    return " ".join(ud.normalize("NFC", text.replace("\u02d9", "\u00b7")).split())


def has_spacing_mark(text: str) -> bool:
    tokens = normalize_label(text).split()
    return any(token in SPACING_MARKS and i > 0 and i + 1 < len(tokens)
               and letter_script(tokens[i - 1][-1]) is not None
               and letter_script(tokens[i + 1][0]) is not None
               for i, token in enumerate(tokens))


def _polytonic(text: str) -> bool:
    greek_base = False
    for char in ud.normalize("NFD", ud.normalize("NFC", text)):
        if ud.category(char).startswith("M"):
            if greek_base and char in POLY_MARKS:
                return True
        else:
            greek_base = letter_script(char) == "greek"
    return any(letter_script(char) == "greek" and 0x1F00 <= ord(char) <= 0x1FFF
               for char in ud.normalize("NFC", text))


def script_class(text: str, inv: Mapping | None = None) -> str:
    inv = inventory(text) if inv is None else inv
    # Majority means largest letter count; ties are Greek, Latin, then Cyrillic.
    majority = max(("greek", "latin", "cyrillic"), key=lambda s: inv[s + "_letters"])
    if majority == "greek":
        if inv["latin_words"]:
            return "greek_latin_cs"
        return "greek_poly" if _polytonic(text) else "greek_mono"
    return majority


def _confidence(record: Mapping) -> float:
    confidence = float(record["confidence"])
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("DocAI mean confidence must be finite and in [0, 1]")
    return confidence


def _admit(record: Mapping, inv: Mapping) -> tuple[bool, str | None, list[str], str | None]:
    reasons = []
    if inv["letter_count"] < 10:
        reasons.append("short_line")
    if _confidence(record) < .89:
        reasons.append("low_confidence")
    if "tall_box" in record.get("flags", []):
        reasons.append("tall_box")
    if 3 * (inv["nonspace_count"] - inv["letter_count"]) > inv["nonspace_count"]:
        reasons.append("symbol_heavy")
    if inv["other_letters"]:
        reasons.append("foreign_script")
    if inv["mixed_words"]:
        reasons.append("mixed_word")
    if record.get("bad_page", False):
        reasons.append("bad_page")
    if reasons:
        return False, None, reasons, None
    text = record["docai_text"]
    return True, script_class(text, inv), [], normalize_label(text)


def admit(record: Mapping) -> tuple[bool, str | None, list[str], str | None]:
    """Apply every gate in the specified order; rejected lines have no label/class."""
    return _admit(record, inventory(record["docai_text"]))


def page_quality(records: Iterable[Mapping]) -> dict[str, dict]:
    """Low-confidence denominator: >=10-letter lines; tall denominator: all lines.

Thresholds are strictly greater than 50% and 30%, respectively. An empty
eligible denominator contributes no low-confidence failure.
"""
    pages = defaultdict(lambda: Counter(lines=0, eligible_lines=0, low_confidence=0, tall_boxes=0))
    for record in records:
        page = pages[record["page_id"]]
        page["lines"] += 1
        if sum(ud.category(c).startswith("L") for c in record["docai_text"]) >= 10:
            page["eligible_lines"] += 1
            page["low_confidence"] += _confidence(record) < .89
        page["tall_boxes"] += "tall_box" in record.get("flags", [])
    result = {}
    for page_id, counts in sorted(pages.items()):
        eligible = counts["eligible_lines"]
        low = eligible > 0 and 2 * counts["low_confidence"] > eligible
        tall = 10 * counts["tall_boxes"] > 3 * counts["lines"]
        result[page_id] = dict(counts, bad_page=low or tall,
                              low_confidence_share=counts["low_confidence"] / eligible if eligible else 0.,
                              tall_box_share=counts["tall_boxes"] / counts["lines"],
                              triggers=[name for name, failed in (("low_confidence", low), ("tall_boxes", tall)) if failed])
    return result


def select_holdout_books(books: Sequence[Mapping], *, seed: int = SEED,
                         count: int = 20, dev_count: int = 5,
                         min_per_decade: int = 2, preferred_lines: int = 300) -> list[dict]:
    """Seeded decade-stratified draw, independent of input ordering.

Take up to two books from every decade, then draw remaining books from the
preferred pool first. A capacity-one stratum contributes its only book.
The caller must report such capacity exceptions; a too-small total raises.
"""
    if len({b["book_key"] for b in books}) != len(books):
        raise ValueError("duplicate book_key")
    if not 0 <= dev_count <= count <= len(books):
        raise ValueError("invalid holdout size")
    groups = defaultdict(list)
    for book in sorted(books, key=lambda b: b["book_key"]):
        groups[book["decade"]].append(dict(book))
    minimum = sum(min(min_per_decade, len(group)) for group in groups.values())
    if minimum > count:
        raise ValueError("holdout size cannot cover decade minima")
    rng, selected, remaining = random.Random(seed), [], []
    for decade, group in sorted(groups.items()):
        preferred = [b for b in group if b["admitted_lines"] >= preferred_lines]
        fallback = [b for b in group if b["admitted_lines"] < preferred_lines]
        rng.shuffle(preferred)
        rng.shuffle(fallback)
        ordered = preferred + fallback
        take = min(min_per_decade, len(ordered))
        selected.extend(ordered[:take])
        remaining.extend(ordered[take:])
    preferred = [b for b in remaining if b["admitted_lines"] >= preferred_lines]
    fallback = [b for b in remaining if b["admitted_lines"] < preferred_lines]
    rng.shuffle(preferred)
    rng.shuffle(fallback)
    selected.extend((preferred + fallback)[:count - len(selected)])
    rng.shuffle(selected)
    return sorted((dict(b, split="dev" if i < dev_count else "test")
                   for i, b in enumerate(selected)), key=lambda b: (b["decade"], b["book_key"]))


def apply_holdout_labels(records: Sequence[Mapping]) -> tuple[list[dict], list[dict]]:
    """O5 removes train only, using the same canonical labels as admission."""
    held = {normalize_label(r["label"]) for r in records if r["split"] in ("dev", "test")}
    kept, rejected = [], []
    for record in records:
        if record["split"] == "train" and normalize_label(record["label"]) in held:
            rejected.append(dict(id=record["id"], reasons=["label_in_holdout"],
                                 docai_text=record.get("docai_text", record["label"])))
        else:
            kept.append(dict(record))
    return kept, rejected


def spatial_neighbours(records: Sequence[Mapping]) -> dict[str, tuple[list | None, list | None]]:
    """Previous/next physical rows on ONE page, using all DocAI boxes.

    Rows must share at least half the narrower horizontal extent (same column).
    Nearest unequal vertical centres define above/below; equal-centre
    fragments/duplicate boxes are on the same row.
This avoids interpreting provider-order column jumps as vertical adjacency.
"""
    if len({r.get("page_id") for r in records}) > 1:
        raise ValueError("spatial_neighbours requires one page")
    result = {}
    for row in records:
        x0, y0, x1, y1 = row["bbox"]
        centre = (y0 + y1) / 2
        above, below = [], []
        for other in records:
            ox0, oy0, ox1, oy1 = other["bbox"]
            overlap = min(x1, ox1) - max(x0, ox0)
            if overlap <= 0 or 2 * overlap < min(x1 - x0, ox1 - ox0):
                continue
            oc = (oy0 + oy1) / 2
            if oc < centre:
                above.append((centre - oc, other["id"], other["bbox"]))
            elif oc > centre:
                below.append((oc - centre, other["id"], other["bbox"]))
        result[row["id"]] = (min(above)[2] if above else None, min(below)[2] if below else None)
    return result


def crop_geometry(bbox: Sequence[float], previous: Sequence[float] | None,
                  following: Sequence[float] | None, page_size: Sequence[int],
                  *, overlap_fraction: float = .15) -> tuple[list[int], bool]:
    """Midpoint overlap trimming, then outward rounding and in-page 4x2 padding."""
    x0, y0, x1, y1 = map(float, bbox)
    width, height = page_size
    if not (x0 < x1 and y0 < y1 and width > 0 and height > 0):
        raise ValueError("invalid bbox/page size")
    top, bottom = y0, y1
    for neighbour, side in ((previous, "top"), (following, "bottom")):
        if neighbour is None:
            continue
        a, b = max(y0, neighbour[1]), min(y1, neighbour[3])
        if b - a > overlap_fraction * (y1 - y0):
            if side == "top":
                top = max(top, (a + b) / 2)
            else:
                bottom = min(bottom, (a + b) / 2)
    if top >= bottom:
        raise ValueError("neighbour midpoint cuts leave no line extent")
    bounds = [max(0, math.floor(x0) - 4), max(0, math.floor(top) - 2),
              min(width, math.ceil(x1) + 4), min(height, math.ceil(bottom) + 2)]
    if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        raise ValueError("crop lies outside page")
    return bounds, top != y0 or bottom != y1
