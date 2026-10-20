"""Lossless numeric spans and grammar proposals in Python character offsets.

Every adjacent pair of digits supplies a slot (including empty gaps), plus
left/right boundaries. Labels describe text grammar, never printed truth.
ASCII digits are intentional: these corpora/codecs use European numerals.
"""
from dataclasses import dataclass
import re

SEPARATORS = "··.,-–— "
_TOKEN = re.compile(r"[0-9]+(?:[··.,\-–— ]+[0-9]+)*")
_DASHES = "-–—"


@dataclass(frozen=True)
class Slot:
    index: int
    start: int
    end: int
    glyph: str
    position: str
    grammar_candidates: tuple[str, ...]
    boundary: str | None = None


@dataclass(frozen=True)
class NumericToken:
    start: int
    end: int
    text: str
    digit_count: int
    slots: tuple[Slot, ...]


def tokenize(text: str) -> list[NumericToken]:
    """Return maximal digit/separator runs without Unicode normalization.

    Range proposals: two ascending groups of 1..4 digits, joined by one
    dash, with optional spaces. Four-digit years 1000..2099 are included.
    Thousands: 1..3 initial digits then groups of three, optionally followed
    by a decimal suffix. Decimal: final comma/period and 1..2 digits.
    Two or more spaces, or an adjacent explicit |/tab, propose a table edge.
    A single space remains a possible thousands separator. With text alone
    cell boundaries and grouped values cannot always be distinguished.
    """
    result = []
    for match in _TOKEN.finditer(text):
        start, end = match.span()
        value = match.group()
        digits = [start + m.start() for m in re.finditer(r"[0-9]", value)]
        decimal = re.search(r"[.,]([0-9]{1,2})$", value)
        integer = value[:decimal.start()] if decimal else value
        grouped = bool(re.fullmatch(r"[0-9]{1,3}(?:[··.,\-–— ][0-9]{3})+", integer))
        range_match = re.fullmatch(r"([0-9]{1,4}) *([-–—]) *([0-9]{1,4})", value)
        is_range = bool(range_match and int(range_match[1]) <= int(range_match[3]))
        slots = []
        # Boundary glyphs are adjacent separators only; no whitespace consumed.
        left = start
        while left and text[left-1] in SEPARATORS and text[left-1] != ' ':
            left -= 1
        right = end
        while right < len(text) and text[right] in SEPARATORS and text[right] != ' ':
            right += 1
        for side, a, b, context in (("left", left, start, text[:start]),
                                    ("right", end, right, text[end:])):
            table = bool(re.search(r"[|\t] *$", context) if side == "left"
                         else re.match(r" *[|\t]", context))
            slots.append(Slot(0 if side == 'left' else len(digits), a, b,
                              text[a:b], 'table_boundary' if table else 'other',
                              ('table_boundary',) if table else ('other',), side))
        inner = []
        for i, (a, b) in enumerate(zip(digits, digits[1:]), 1):
            glyph = text[a+1:b]
            labels = []
            if len(glyph) >= 2 and glyph.isspace():
                labels.append('table_boundary')
            if glyph and is_range:
                labels.append('range')
            if decimal and a+1 == start + decimal.start():
                labels.append('decimal')
            if glyph and grouped and b <= start + len(integer):
                labels.append('thousands')
            if not labels:
                labels = ['other']
            inner.append(Slot(i, a+1, b, glyph, labels[0], tuple(labels)))
        result.append(NumericToken(start, end, value, len(digits),
                                   (slots[0], *inner, slots[1])))
    return result
