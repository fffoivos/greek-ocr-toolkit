"""Offline standard admission library and CLI, plus compatible Wave-0 contracts.

Use ``evaluate`` / ``evaluate_rows`` for standard admission. ``admit`` routes
source-bearing records through the standard policy; source-free Wave-0 callers
retain their historical contract. No OCR readers, network, or look-alike fixes.

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

from .lookalikes import HOMOGLYPHS, LOOKALIKE_TABLE_NAME, lookalike_table_sha256
from .text_primitives import codec_view, codec_letter_script, normalize_current
from .text_primitives import unicode_letter_script as letter_script
from .serbian import SERBIAN_EXTENSION_ATOMS, SERBIAN_DOCUMENTS, serbian_extension_sha256, serbian_documents_sha256
from greekocr.labelfix.text import nfd, nfc, is_unicode_mark, BREATHINGS, SUBSCRIPT, GRAVE, CIRCUMFLEX, is_delimiter

CLASSES = ("greek_poly", "greek_mono", "greek_latin_cs", "latin", "cyrillic")
REASONS = ("short_line", "low_confidence", "tall_box", "symbol_heavy",
           "foreign_script", "mixed_word", "bad_page", "label_in_holdout")
SEED = 20261015
ROMAN = frozenset("IVXLCΙΧ")
SPACING_MARKS = frozenset("\u1fbf\u1fbd\u0384")
POLY_MARKS = BREATHINGS | SUBSCRIPT | frozenset((GRAVE, CIRCUMFLEX))
# Shared sentence marks, Greek question mark/ano teleia, and quotation marks.
GREEK_PUNCTUATION = frozenset(".,;:!?·\u037e\u0387…«»'’‘\u1fbd")


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
        if is_delimiter(char, mode="admission"):
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
                letter_script(char) or is_unicode_mark(char) for char in word):
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
    return normalize_current(text)[0]


def has_spacing_mark(text: str) -> bool:
    tokens = normalize_label(text).split()
    return any(token in SPACING_MARKS and i > 0 and i + 1 < len(tokens)
               and letter_script(tokens[i - 1][-1]) is not None
               and letter_script(tokens[i + 1][0]) is not None
               for i, token in enumerate(tokens))


def _polytonic(text: str) -> bool:
    greek_base = False
    for char in nfd(nfc(text)):
        if is_unicode_mark(char):
            if greek_base and char in POLY_MARKS:
                return True
        else:
            greek_base = letter_script(char) == "greek"
    return any(letter_script(char) == "greek" and 0x1F00 <= ord(char) <= 0x1FFF
               for char in nfc(text))


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
    """Tuple API: standard policy for declared sources, legacy Wave-0 otherwise.

    New experiments should use evaluate_rows to retain checks/normalisations
    and compute page medians. Rejected tuples have no label/class.
    """
    if record.get("source"):
        result = evaluate(record)
        return (result["passed"], result["class"] if result["passed"] else None,
                result["failed_rules"], result["label"] if result["passed"] else None)
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


# ADM5 standard policy. Version changes whenever admission semantics/table change.
TABLE_VERSION = "ADM5c-CENSUS3-20261018.CP6"
TOOL_VERSION = "SEG-20261018.CP6"
NEIGHBOUR_PARAMS = dict(min_components=10, min_width_xh=3., min_height_xh=.6)
RULES = {
    "short_line": "R1: fewer than 10 Unicode letters (NFC); headings_caps requires 4",
    "numeric_shape": "numerics_tables: fewer than 4 decimal digits or less than 60% digits/separators",
    "low_confidence": "R2: available mean DocAI confidence < 0.89",
    "tall_box": "R3: height > 1.7 times page median line height",
    "nonletter_frac": "R4: more than one third of nonspace characters are nonletters",
    "unexpected_language": "R5 language branch: majority Latin without mixed class on a Greek source",
    "unexpected_script": "R5 script branch: letter script outside source expectations",
    "mixed_script_word": "R6: multiple letter scripts within one delimited word (no Roman exemption)",
    "lookalike_only_word": "R6b: secondary-script word has no distinguishing letter in the shared table",
    "foreign_char": "R7: normalized NFD atom absent from codec",
    "geometry_unavailable": "SEG-CP4c: geometry cannot be measured or bound; fail closed",
    "neighbour_words": "NW1b legacy diagnostic proxy; CP2 geometry alone remains unqualified",
}
# R8 is a normalization, not a failure: DOT ABOVE -> middle dot.
BRIEF_PROVENANCE = "docs/briefs/ADM5_standard_admission_tool.md, owner rules 5-7 (2026-10-17)"
V2_PROVENANCE = ("import_real_v2_{train,dev,test}.jsonl source/wave/script_class metadata; "
                 "ADM5 owner rule 5: expectations from wave/script_class, not observed label")


def _policy(language, scripts, latin, provenance, *, wave=None):
    return dict(language=language, expected_letters=list(scripts), latin=latin,
                provenance=provenance, wave=wave)


# Exact extension data is shared in harvest.serbian; scope stays in this table.
SERBIAN_PROVENANCE = ("../greek-ocr-toolkit-sol-collect/collect_v3/vendor/classify.py:57; "
                      "docs/briefs/ADM5c_rule_variants.md (2026-10-17)")
CLASS_RULE_VARIANTS = {
    "numerics_tables": dict(min_digits=4, min_shape_percent=60,
                            allowed_separators=".,·-/ ", replaces=["short_line", "nonletter_frac"]),
    "headings_caps": dict(min_letters=4, keep_nonletter_frac=True),
}


# One explicit row per source. No source is inferred from the recognized text.
SOURCE_POLICIES = {
    name: _policy("polytonic Greek", ["greek"], "mixed_class_or_minority", BRIEF_PROVENANCE)
    for name in ("bsb_poly1850", "ia_poly1850", "nlg", "kosmopolis", "lekythos")
}
SOURCE_POLICIES.update({
    "gazette_modern": _policy("modern Greek (monotonic)", ["greek"], "mixed_class_or_minority", BRIEF_PROVENANCE),
    "elstat": _policy("Greek", ["greek"], "mixed_class_or_minority", BRIEF_PROVENANCE + "; digits allowed subject to declared class rules and codec"),
    "serbia": _policy("Cyrillic", ["cyrillic"], "none", BRIEF_PROVENANCE),
    "ia_russian": _policy("Cyrillic", ["cyrillic"], "none", BRIEF_PROVENANCE),
    "ia_greek_latin": _policy("Greek / Latin", ["greek"], "mixed_class_or_minority",
                              BRIEF_PROVENANCE + "; source present in W1 originals, Greek policy unless explicit mixed class"),
})
SOURCE_POLICIES["serbia"].update(expected_characters=list(SERBIAN_EXTENSION_ATOMS),
                                  codec="v2 + Serbian extension", provenance=SERBIAN_PROVENANCE)
# These are the complete source identities in the requested v2 splits. The
# permitted class vocabulary is fixed below; missing/unknown classes fail closed.
_V2_SOURCES = {
    "round1": ("anemi_round1",),
    "round2": ("anemi_round2",),
    "mixed": ("anemi_mixed", "archive_b28038630") + tuple(
        "openarchives_mixed_" + s for s in (
            "apothesis", "Dione", "ktisis", "KEIED", "anaktisis", "hellanicus",
            "Pandemos", "nemertes", "kallipos", "ntua")),
    "vouli": ("vouli_parliament_1850s",),
    "parliament": ("parliament_proceedings_1975_2000",),
    "openarchives": tuple("openarchives_" + s for s in (
        "Pandemos", "kallipos", "anaktisis", "hellanicus", "Dione", "KEIED",
        "ktisis", "apothesis", "nemertes", "ntua", "IKEE_AUT")),
    "wikisource": ("wikisource_el", "wikisource_ru"),
    "cyrillic": tuple("archive_" + s for s in (
        "AA9613308335D0B014B", "sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930",
        "bub_gb_mG0mAQAAIAAJ", "bub_gb_Cmg6AQAAIAAJ", "izvestiianabul25192530bul",
        "izvestiianabulga610193138bulg", "b24878935", "izvestiianatsars1516194243tsar",
        "izvestiianatsars12192829tsar", "izvestiianatsars910193637tsar", "b29337124",
        "izvestiianatsars1112193839tsar")),
}
for _wave, _sources in _V2_SOURCES.items():
    for _source in _sources:
        SOURCE_POLICIES[_source] = _policy(
            "from script_class", ["from script_class"], "from script_class", V2_PROVENANCE, wave=_wave)

_CLASS_EXPECTATIONS = {
    "greek_poly": ("polytonic Greek", ["greek"]),
    "greek_mono": ("modern Greek (monotonic)", ["greek"]),
    "greek_latin_cs": ("Greek / Latin", ["greek", "latin"]),
    "mixed_greek_latin": ("Greek / Latin", ["greek", "latin"]),
    "latin": ("Latin", ["latin"]),
    "cyrillic": ("Cyrillic", ["cyrillic"]),
}
MIXED_CLASSES = frozenset(("greek_latin_cs", "mixed_greek_latin"))


# Secondary scripts are admitted only as whole words with distinguishing letters.
SECONDARY_SCRIPT_POLICIES = {
    "cyrillic": dict(primary="cyrillic", secondary="latin", reclassify=None),
    "latin": dict(primary="latin", secondary="greek", reclassify="mixed_greek_latin"),
}


def _has_lookalike(char, primary):
    return any(char in group and any(letter_script(c) == primary for c in group)
               for group in HOMOGLYPHS)


# CENSUS2: recorded document language, never inferred from recognized letters.
# ISO 639-2 srp / catalogue "Serbian"; multilingual srp/ger/lat is explicit.
DOCUMENT_POLICY = dict(
    wave="cyrillic", documents=list(SERBIAN_DOCUMENTS),
    expected_characters=list(SERBIAN_EXTENSION_ATOMS),
    codec="v2 + Serbian extension",
    provenance="docs/harvest/collection/v2/census2_document_language.json; CENSUS2 coordinator ruling (2026-10-18)")


def expected_policy(record: Mapping) -> dict:
    """Resolve only declared source/class metadata; unknown identities raise."""
    source = record.get("source")
    if source not in SOURCE_POLICIES:
        raise ValueError(f"unknown source {source!r}; add a provenance-bound table entry")
    result = dict(SOURCE_POLICIES[source])
    cls = record.get("script_class") or record.get("primary_class") or record.get("class")
    if result["wave"]:
        if record.get("wave") != result["wave"]:
            raise ValueError(f"source/wave mismatch: {source!r}")
        if cls not in _CLASS_EXPECTATIONS:
            raise ValueError(f"unknown script_class {cls!r} for {source!r}")
        language, scripts = _CLASS_EXPECTATIONS[cls]
        result.update(language=language, expected_letters=scripts,
                      latin="mixed_class_or_minority" if scripts == ["greek"] else
                      "allowed" if "latin" in scripts else "none")
    elif cls in MIXED_CLASSES and "greek" in result["expected_letters"]:
        result.update(expected_letters=["greek", "latin"], latin="allowed")
    if record.get("wave") == DOCUMENT_POLICY["wave"] and record.get("doc") in SERBIAN_DOCUMENTS:
        result.update(expected_characters=list(SERBIAN_EXTENSION_ATOMS),
                      codec=DOCUMENT_POLICY["codec"], provenance=DOCUMENT_POLICY["provenance"])
    result["secondary_word_policy"] = SECONDARY_SCRIPT_POLICIES.get(cls)
    if result["secondary_word_policy"]:
        result["expected_letters"] = list(dict.fromkeys(
            result["expected_letters"] + [result["secondary_word_policy"]["secondary"]]))
    result["class_rules"] = CLASS_RULE_VARIANTS.get(cls, {})
    return result


def load_codec(path=None) -> dict:
    """One validating, byte-fingerprinted codec-kind/script view."""
    return codec_view(path)


@lru_cache(maxsize=1)
def _default_codec():
    return load_codec()


def _height(record):
    box = record.get("bbox") or record.get("crop_bbox")
    if box is None:
        return None
    if len(box) != 4 or not all(math.isfinite(float(v)) for v in box):
        raise ValueError("bbox must contain four finite xyxy coordinates")
    x0, y0, x1, y1 = map(float, box)
    if x1 <= x0 or y1 <= y0:
        raise ValueError("bbox must have positive width and height")
    return y1 - y0


def _page_key(record):
    # Do not combine different sources or documents with coincident page IDs.
    return (record.get("source"), record.get("doc", record.get("document_id")), record.get("page_id"))


def page_medians(records: Iterable[Mapping]) -> dict:
    """Median of available supplied rows on each identified page, before drops."""
    import statistics
    heights = defaultdict(list)
    for record in records:
        height = _height(record)
        if height is not None and record.get("page_id") is not None:
            heights[_page_key(record)].append(height)
    return {key: statistics.median(values) for key, values in heights.items()}


def geometry_unavailable(status, reason=None):
    """Undecidable geometry is a policy loss, never a measured detection.

    CP4's unresolved letter/word evidence remains unresolved; unresolved target
    identity is unavailable geometry even when structural evidence is positive.
    """
    return status == "unavailable" or reason in {
        "ambiguous_target", "missing_target", "missing_or_ambiguous_target",
        "unsupported_target",
    }


def compose_segmentation_decision(observation):
    """Compose the fail-closed geometry rule with CP3/CP4's measured union.

    Call on freshly validated observations. This does not qualify saved evidence
    for public admission or turn an unknown into a measured positive/KEEP.
    """
    unavailable = geometry_unavailable(observation.get("status"), observation.get("reason"))
    return dict(geometry_unavailable=unavailable,
                drop=True if unavailable else observation.get("union_drop"))


# All remaining checks belong to admission eligibility. This exclusion boundary
# automatically includes new text/metadata rules instead of a diagnostic whitelist.
SEGMENTATION_CHECKS = frozenset({"geometry_unavailable", "neighbour_words",
                                "merged", "orientation", "orientation_unknown"})


def non_segmentation_eligibility(checks):
    """Admission's complete text + metadata composition, including tall_box.

    Confidence and lookalike rules are included. tall_box is a separate height
    heuristic (> 1.7 * pre-drop page median), NOT evidence of multiple lines.
    Missing height/confidence remains n/a as in admission; it is not a failure.
    This is not the CP7 sampling predicate: sampling is pre-screen candidate_usable.
    """
    rejected = [k for k, v in checks.items()
                if v == "fail" and k not in SEGMENTATION_CHECKS]
    return dict(passed=not rejected, rejections=rejected,
                height_rule="included; height > 1.7 * pre-drop page median")


def evaluate(record: Mapping, *, codec=None, page_median_height=None, neighbour_measurement=None, neighbour_params=None) -> dict:
    """Pure standard per-row result, including the ruled CENSUS3 reclassification.

    NFC counts avoid penalizing decomposed accents. Codec coverage uses NFD as
    specified by the codec. Punctuation atoms such as U+02B9 are not script
    letters. Greek policies allow standalone minority Latin tokens; majority
    Latin needs explicit mixed class. R6 has no historical Roman exception.
    """
    codec = _default_codec() if codec is None else codec
    policy = expected_policy(record)
    raw = record.get("docai_text", record.get("label"))
    if not isinstance(raw, str):
        raise ValueError("row requires string docai_text or label")
    text, normalizations = normalize_current(raw)
    inv = inventory(text)
    scripts = Counter(codec_letter_script(c, codec) for c in text
                      if codec_letter_script(c, codec) and c not in codec["nonletter_atoms"])
    allowed = set(policy["expected_letters"])
    if policy["latin"] == "mixed_class_or_minority":
        allowed.add("latin")
    unexpected = set(scripts) - allowed
    majority_latin = (policy["latin"] == "mixed_class_or_minority" and
                      scripts["latin"] > sum(v for k, v in scripts.items() if k != "latin"))
    class_original = record.get("script_class") or record.get("primary_class") or record.get("class", "unspecified")
    cls = class_original
    secondary = policy["secondary_word_policy"]
    mixed, lookalike_only = [], []
    for token in words(text):
        token_scripts = {codec_letter_script(c, codec) for c in token
                         if codec_letter_script(c, codec) and c not in codec["nonletter_atoms"]}
        if len(token_scripts) > 1:
            mixed.append(token)
        elif secondary and token_scripts == {secondary["secondary"]}:
            letters = [c for c in token if codec_letter_script(c, codec) and c not in codec["nonletter_atoms"]]
            if all(_has_lookalike(c, secondary["primary"]) for c in letters):
                lookalike_only.append(token)
            elif secondary["reclassify"]:
                cls = secondary["reclassify"]
    if cls != class_original:
        language, expected_letters = _CLASS_EXPECTATIONS[cls]
        policy.update(language=language, expected_letters=expected_letters)
    atoms = codec["atoms"]
    if policy.get("codec") == "v2 + Serbian extension":
        atoms = atoms | set(SERBIAN_EXTENSION_ATOMS)
    outside = sorted(set(nfd(text)) - atoms, key=ord)
    confidence = record.get("confidence", record.get("docai_confidence"))
    confidence = _confidence({"confidence": confidence}) if confidence is not None else None
    height = _height(record)
    median = record.get("page_median_line_height")
    if median is None:
        median = page_median_height
    if median is not None and (not math.isfinite(float(median)) or float(median) <= 0):
        raise ValueError("page median height must be positive and finite")
    tall = height is not None and median is not None and height > 1.7 * float(median)
    variant = policy["class_rules"]
    numeric = "min_digits" in variant
    numeric_bad = numeric and (
        inv["digits"] < variant["min_digits"] or
        100 * sum(ud.category(c) == "Nd" or c in variant["allowed_separators"] for c in text)
        < variant["min_shape_percent"] * len(text))
    flags = {
        "short_line": not numeric and inv["letter_count"] < variant.get("min_letters", 10),
        "numeric_shape": numeric_bad,
        "low_confidence": confidence is not None and confidence < .89,
        "tall_box": tall,
        "nonletter_frac": not numeric and 3 * (inv["nonspace_count"] - inv["letter_count"]) > inv["nonspace_count"],
        "unexpected_language": majority_latin,
        "unexpected_script": bool(unexpected),
        "mixed_script_word": bool(mixed),
        "lookalike_only_word": bool(lookalike_only),
        "foreign_char": bool(outside),
    }
    from .geometry_observations import admission_evidence_status
    geometry_status, geometry_reason = admission_evidence_status(record, neighbour_measurement)
    # No qualified word predicate exists in CP2. Never invoke the legacy F2
    # graph, including for callers claiming qualification on an old mapping.
    flags["geometry_unavailable"] = geometry_unavailable(geometry_status, geometry_reason)
    flags["neighbour_words"] = False
    checks = {rule: "fail" if fail else "pass" for rule, fail in flags.items()}
    checks["neighbour_words"] = "n/a"
    if confidence is None:
        checks["low_confidence"] = "n/a"
    if height is None or median is None:
        checks["tall_box"] = "n/a"
    failed = non_segmentation_eligibility(checks)["rejections"] + [
        rule for rule in flags if rule in SEGMENTATION_CHECKS and flags[rule]]
    return dict(passed=False, rules_passed=not failed,
                status="fail" if failed else "unresolved",
                geometry_status=geometry_status, geometry_reason=geometry_reason,
                failed_rules=failed,
                first_failure=failed[0] if failed else None, normalisations=normalizations,
                checks=checks, label=text, source=record["source"],
                **{"class": cls, "class_original": class_original},
                lookalike_only_words=lookalike_only,
                expected_language=policy["language"], expected_scripts=policy["expected_letters"],
                latin_policy=policy["latin"], confidence=confidence if confidence is not None else "n/a",
                height=height, page_median_line_height=median,
                letters=inv["letter_count"],
                nonletter_frac=float((inv["nonspace_count"] - inv["letter_count"]) / inv["nonspace_count"]) if inv["nonspace_count"] else 0.0,
                scripts_seen=dict(sorted(scripts.items())), foreign_chars=outside,
                mixed_words=mixed, unexpected_scripts=sorted(unexpected),
                outside_codec=[f"U+{ord(c):04X} {ud.name(c, 'UNNAMED')}" for c in outside],
                table_version=TABLE_VERSION, codec_sha256=codec["sha256"])


def evaluate_rows(records: Sequence[Mapping], *, codec=None, neighbour_params=None, run_root=None, neighbour_cache=None):
    """Evaluate supplied rows using pre-drop page medians; yields one result each."""
    codec = _default_codec() if codec is None else codec
    medians = page_medians(records)
    from .neighbour_words import measure_rows
    options = {}
    if run_root is not None:
        options["run_root"] = run_root
    if neighbour_cache is not None:
        options["cache"] = neighbour_cache
    measurement_rows = [dict(r, row_id=str(r.get("row_id", r["id"])))
                        if "row_id" not in r and "id" in r else r for r in records]
    measurements = measure_rows(measurement_rows, **options)
    for record in records:
        yield evaluate(record, codec=codec, page_median_height=medians.get(_page_key(record)),
                       neighbour_measurement=measurements.get(str(record.get("row_id", record.get("id")))), neighbour_params=neighbour_params)


def _bucket():
    return dict(rows=0, admitted=0, failed=0, first_failure=Counter(),
                all_failures=Counter(), not_available=Counter(), normalisations=Counter())


def _count(bucket, result):
    bucket["rows"] += 1
    bucket["admitted"] += result["passed"]
    bucket["failed"] += not result["passed"]
    bucket["all_failures"].update(result["failed_rules"])
    if result["first_failure"]:
        bucket["first_failure"].update([result["first_failure"]])
    bucket["not_available"].update(k for k, v in result["checks"].items() if v == "n/a")
    bucket["normalisations"].update(result["normalisations"])


def output_row(row, result, fallback_id):
    """Coordinator's exact public row schema; diagnostic details stay internal."""
    return dict(row_id=str(row.get("row_id", row.get("id", fallback_id))),
                source=result["source"], class_original=result["class_original"],
                lookalike_only_words=result["lookalike_only_words"],
                **{"class": result["class"], "pass": result["passed"]},
                rules_failed=result["failed_rules"], expected_language=result["expected_language"],
                expected_scripts=result["expected_scripts"], letters=result["letters"],
                nonletter_frac=result["nonletter_frac"], scripts_seen=result["scripts_seen"],
                mixed_script_words=result["mixed_words"], foreign_chars=result["foreign_chars"])


def expected_table_sha256():
    import hashlib
    import json
    table = dict(version=TABLE_VERSION, sources=SOURCE_POLICIES,
                 classes=_CLASS_EXPECTATIONS, mixed_classes=sorted(MIXED_CLASSES),
                 class_rule_variants=CLASS_RULE_VARIANTS, document_policy=DOCUMENT_POLICY,
                 secondary_script_policies=SECONDARY_SCRIPT_POLICIES,
                 lookalike_table_name=LOOKALIKE_TABLE_NAME,
                 lookalike_table_sha256=lookalike_table_sha256())
    return hashlib.sha256(json.dumps(table, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def run_files(inputs, *, output_dir=None, census=None, codec_path=None, neighbour_params=None, run_root=None, neighbour_cache=None):
    """Write fixed-schema rows/receipt. Census preserves every input row.

    Multiple inputs: input_path is an ordered JSON path array encoded as a
    string; input_sha256 hashes their exact bytes concatenated in that order.
    The MD records individual hashes. Inputs are never rewritten.
    """
    import hashlib
    import json
    from datetime import datetime, timezone
    from pathlib import Path
    from contextlib import ExitStack
    codec = load_codec(codec_path)
    paths = [Path(p).expanduser().resolve() for p in inputs]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("empty or duplicate input paths")
    if not census and (len(paths) != 1 or output_dir is None):
        raise ValueError("admit requires one input and output_dir")
    prefix = Path(census) if census else Path(output_dir) / paths[0].stem
    decisions_path = prefix.with_name(prefix.name + "_admission.jsonl")
    receipt_path = prefix.with_name(prefix.name + "_admission_receipt.json")
    admitted_path = prefix.with_name(prefix.name + "_admitted.jsonl") if not census else None
    md_path = prefix.with_suffix(".md") if census else None
    destinations = [p for p in (decisions_path, receipt_path, admitted_path, md_path) if p]
    if any(p.resolve() in paths for p in destinations):
        raise ValueError("outputs must not overwrite inputs")
    batches, input_info, digest = [], [], hashlib.sha256()
    for path in paths:
        raw = path.read_bytes()
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
        for row in records:
            expected_policy(row)
        batches.append(records)
        digest.update(raw)
        input_info.append(dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), rows=len(records)))
    from .neighbour_words import frozen
    receipt = dict(neighbour_words_params=dict(NEIGHBOUR_PARAMS if neighbour_params is None else neighbour_params),
                   neighbour_words_ownership_params_sha256=frozen(),
                   neighbour_words_unmatched=0, neighbour_words_unavailable=0,
                   neighbour_words_status_counts={}, neighbour_words_reason_counts={},
                   tool_version=TOOL_VERSION,
                   lookalike_table_name=LOOKALIKE_TABLE_NAME,
                   lookalike_table_sha256=lookalike_table_sha256(),
                   serbian_documents=list(SERBIAN_DOCUMENTS),
                   serbian_documents_sha256=serbian_documents_sha256(),
                   serbian_extension_atoms=list(SERBIAN_EXTENSION_ATOMS),
                   serbian_extension_sha256=serbian_extension_sha256(),
                   tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   input_path=str(paths[0]) if len(paths) == 1 else json.dumps([str(p) for p in paths]),
                   input_sha256=digest.hexdigest(), rows_total=0, rows_pass=0,
                   drops_per_rule={r: 0 for r in RULES}, drops_per_source_class={},
                   expected_table_sha256=expected_table_sha256(), created=datetime.now(timezone.utc).isoformat())
    by_wave = {}
    for path in destinations:
        path.parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        admitted = stack.enter_context(admitted_path.open("w")) if admitted_path else None
        decisions = stack.enter_context(decisions_path.open("w"))
        for path, records in zip(paths, batches):
            for index, (row, result) in enumerate(zip(records, evaluate_rows(records, codec=codec, neighbour_params=neighbour_params, run_root=run_root, neighbour_cache=neighbour_cache)), 1):
                decision = output_row(row, result, f"{path.name}:{index}")
                if result["checks"]["neighbour_words"] == "n/a":
                    receipt["neighbour_words_unavailable"] += 1
                    for field, value in (("neighbour_words_status_counts", result["geometry_status"]),
                                         ("neighbour_words_reason_counts", result["geometry_reason"])):
                        counts = receipt[field]
                        counts[value] = counts.get(value, 0) + 1
                    if (row.get("crop_bbox") and row.get("row_id", row.get("id")) is not None
                            and row.get("page_id") and result["geometry_status"] == "unavailable"):
                        receipt["neighbour_words_unmatched"] += 1
                receipt["rows_total"] += 1
                receipt["rows_pass"] += decision["pass"]
                group = receipt["drops_per_source_class"].setdefault(
                    decision["source"] + "|" + decision["class"], {r: 0 for r in RULES})
                for rule in decision["rules_failed"]:
                    receipt["drops_per_rule"][rule] += 1
                    group[rule] += 1
                wave_bucket = by_wave.setdefault(row.get("wave", row["source"]), _bucket())
                _count(wave_bucket, result)
                decisions.write(json.dumps(decision, ensure_ascii=False) + "\n")
                if admitted and decision["pass"]:
                    admitted.write(json.dumps(dict(row, label=result["label"], admission=result), ensure_ascii=False) + "\n")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if census:
        lines = ["# ADM5c v2 admission census", "",
                 f"{receipt['rows_total'] - receipt['rows_pass']:,} / {receipt['rows_total']:,} rows would fail today. No v2 rows removed or rewritten.", "",
                 f"Tool: `{TOOL_VERSION}`. Expected table: `{TABLE_VERSION}` / `{receipt['expected_table_sha256']}`.",
                 f"Codec: `{codec['path']}`, version `{codec['version']}`, SHA-256 `{codec['sha256']}`.", "",
                 "Confidence and geometry are n/a when absent. Source/wave/class expectations are declared, never inferred from OCR. Rule counts overlap. DOT ABOVE is normalized before coverage checks; no look-alike correction or Roman exemption.", "",
                 "| wave | rows | fail | " + " | ".join(RULES) + " |", "|---|---:|---:|" + "---:|" * len(RULES)]
        for wave, counts in sorted(by_wave.items()):
            lines.append(f"| {wave} | {counts['rows']} | {counts['failed']} | " + " | ".join(str(counts['all_failures'].get(r, 0)) for r in RULES) + " |")
        lines += ["", "## Rule map", ""] + [f"- {rule}: {description}" for rule, description in RULES.items()]
        lines += ["- R8: DOT ABOVE → middle dot; normalization only, never a failure.", "", "## Inputs (SHA-256)", ""]
        lines += [f"- `{r['path']}`: `{r['sha256']}` ({r['rows']} rows)" for r in input_info]
        lines += ["", "For multiple inputs, receipt input_path is a JSON path array encoded as a string; input_sha256 is SHA-256 of the exact concatenated input bytes in that order.", ""]
        md_path.write_text("\n".join(lines))
    return receipt


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="ADM5 offline standard line admission; no OCR/network/spend")
    sub = parser.add_subparsers(dest="command", required=True)
    admit_parser = sub.add_parser("admit", help="write *_admitted.jsonl, *_admission.jsonl and *_admission_receipt.json")
    admit_parser.add_argument("input")
    admit_parser.add_argument("--output-dir", required=True)
    census_parser = sub.add_parser("census", help="write PREFIX_admission.jsonl, PREFIX_admission_receipt.json and PREFIX.md")
    census_parser.add_argument("inputs", nargs="+")
    census_parser.add_argument("--output-prefix", required=True)
    for command in (admit_parser, census_parser):
        command.add_argument("--codec", help="NFD codec JSON (default: vendored codec/v2.json)")
        command.add_argument("--neighbour-min-components", type=int, default=NEIGHBOUR_PARAMS["min_components"])
        command.add_argument("--neighbour-min-width-xh", type=float, default=NEIGHBOUR_PARAMS["min_width_xh"])
        command.add_argument("--neighbour-min-height-xh", type=float, default=NEIGHBOUR_PARAMS["min_height_xh"])
        command.add_argument("--run-root", type=str)
        command.add_argument("--neighbour-cache", type=str)
    args = parser.parse_args(argv)
    receipt = run_files([args.input] if args.command == "admit" else args.inputs,
                        output_dir=getattr(args, "output_dir", None),
                        census=getattr(args, "output_prefix", None), codec_path=args.codec,
                        neighbour_params=dict(min_components=args.neighbour_min_components,
                            min_width_xh=args.neighbour_min_width_xh, min_height_xh=args.neighbour_min_height_xh),
                        run_root=args.run_root, neighbour_cache=args.neighbour_cache)
    print(f"{receipt['rows_total']} rows: {receipt['rows_pass']} admitted, {receipt['rows_total'] - receipt['rows_pass']} failed; {TOOL_VERSION}")


if __name__ == "__main__":
    main()
