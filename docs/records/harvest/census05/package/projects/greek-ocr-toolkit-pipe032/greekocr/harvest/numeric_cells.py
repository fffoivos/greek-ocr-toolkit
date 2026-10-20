"""Descriptive numeric-cell classification; never a segmentation policy input.

The pixel/character limits below are justified by the immutable census in
docs/records/harvest/collect_v3_admission/segeval1/cells/HANDOFF.md.
"""
from __future__ import annotations

import math
import re
import unicodedata

NUMERIC_SEPARATORS = frozenset(".,:/-–—%()+'′§№")
# Proposed descriptive cut from all 592,466 rows, before the crop draw:
# numeric width P95=169 -> next 50 px; height P75=35 -> next 10 px;
# numeric saved-visible-character P90=10, used without rounding.
MAX_CELL_WIDTH_PX = 200
MAX_CELL_HEIGHT_PX = 40
MAX_CELL_CHARACTERS = 10
_ROMAN = re.compile(r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})')
_ROMAN_GLYPHS = frozenset('IVXLCDMivxlcdmΙ' + ''.join(chr(i) for i in range(0x2160, 0x2180)))


def _numeric_reason(text: str) -> str | None:
    s = text.strip()
    if not s:
        return None
    # Roman numerals may have separator/whitespace wrappers, but one numeral
    # token only. Greek capital iota is the explicit OCR alias needed for ΙΙ.
    token = s.strip(''.join(NUMERIC_SEPARATORS) + ' \t\r\n\v\f')
    roman = unicodedata.normalize('NFKC', token.replace('Ι', 'I')).upper()
    if token and all(c in _ROMAN_GLYPHS for c in token) and _ROMAN.fullmatch(roman):
        return 'numeric_output:roman'
    # Letters are forbidden in both digit branches, even if digits dominate.
    if any(unicodedata.category(c).startswith('L') for c in s):
        return None
    digits = sum(c.isdecimal() for c in s)
    if digits and all(c.isdecimal() or c in NUMERIC_SEPARATORS or c.isspace() for c in s):
        return 'numeric_output:digits_and_separators'
    if (digits * 2 > len(s) and not any(c.isspace() for c in s)
            and all(c.isdecimal() or unicodedata.category(c)[0] in 'PS' for c in s)):
        return 'numeric_output:digit_dominated_token'
    return None


def _character_count(text: str) -> int:
    """Same NFC visible-character definition as saved segmentation evidence."""
    return sum(not c.isspace() and unicodedata.category(c)[0] not in {'M', 'C'}
               for c in unicodedata.normalize('NFC', text))


def classify_cell(text, width_px, height_px, xheight_px=None) -> dict:
    """Classify a crop descriptively, with no I/O or policy/verdict changes.

    Exact numeric-output grammar, after Python ``str.strip()``:

    1. One or more Unicode decimal digits (``str.isdecimal``), interspersed
       with any Unicode whitespace or these literal separators/signs only:
       ``. , : / - – — % ( ) + ' ′ § №``. A digit is required; separator
       balance/order is not checked (so ``29)`` and ``463.503.-`` qualify).
    2. One canonical Roman numeral, case-insensitive, matching
       ``M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})``,
       nonempty, optionally wrapped by the above separators and ASCII
       whitespace. Only Latin IVXLCDM/ivxlcdm, Unicode Roman U+2160..217F
       (NFKC-expanded), and Greek capital iota Ι (mapped to I) are permitted
       inside the numeral. Internal whitespace is forbidden. Other Greek
       lookalikes are not mapped. Canonical numeral spellings that are also
       words, e.g. ``mix``, necessarily qualify by this lexical grammar.
    3. One whitespace-free token with strictly more than half its codepoints
       decimal digits; every remaining codepoint must be Unicode punctuation
       or a symbol (general-category P* or S*). This admits e.g. ``12€``.
       Letters are forbidden in both digit branches, even with many digits;
       a digit/Roman-letter mixture such as ``123IV`` does not qualify.

    ``is_small_image`` requires finite positive numeric pixel dimensions,
    width <= 200 px, height <= 40 px, and <= 10 visible characters. Visible
    characters are NFC codepoints excluding whitespace, marks (M*) and
    controls/format characters (C*), matching the saved segmentation count.
    Empty text can be a small image but cannot be numeric. Both dimensions
    are the original crop dimensions, never rotated or normalised.

    The optional xheight_px is intentionally unused: corpus curve-derived
    x-heights are reported, but tiny numeric crops have unstable font-height
    estimates. It cannot affect classification. ``is_cell`` is exactly the
    conjunction of the two booleans; reasons explain those two tests only.
    These limits describe a proposed population for review, not correctness.
    """
    numeric_reason = _numeric_reason(text)
    reasons = [numeric_reason or 'non_numeric_output']
    valid = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                and math.isfinite(v) and v > 0 for v in (width_px, height_px))
    chars = _character_count(text)
    small = bool(valid and width_px <= MAX_CELL_WIDTH_PX
                 and height_px <= MAX_CELL_HEIGHT_PX and chars <= MAX_CELL_CHARACTERS)
    if not valid:
        reasons.append('image_dimensions:missing_or_invalid')
    else:
        if width_px > MAX_CELL_WIDTH_PX:
            reasons.append('width_exceeds_limit')
        if height_px > MAX_CELL_HEIGHT_PX:
            reasons.append('height_exceeds_limit')
    if chars > MAX_CELL_CHARACTERS:
        reasons.append('characters_exceed_limit')
    if small:
        reasons.append('small_image:within_limits')
    return dict(is_numeric_output=numeric_reason is not None, is_small_image=small,
                is_cell=numeric_reason is not None and small, reasons=reasons)
