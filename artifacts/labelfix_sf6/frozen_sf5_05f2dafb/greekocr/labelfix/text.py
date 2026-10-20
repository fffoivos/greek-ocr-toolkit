"""NFD text utilities for label correction: tokens, vowel clusters, diff classes, guards.

Everything here works on NFD codepoints (codec v1 contract). Combining marks that the
rules reason about:

    breathing   U+0313 psili, U+0314 dasia
    accent      U+0301 oxia/tonos, U+0300 varia, U+0342 perispomeni
    subscript   U+0345 ypogegrammeni
    dialytika   U+0308
    other       U+0304 macron, U+0306 vrachy (never corrected; a change there is "other")
"""
from __future__ import annotations

from dataclasses import dataclass, field
import unicodedata as ud

BREATHINGS = frozenset('̓̔')
ACCENTS = frozenset('́̀͂')
SUBSCRIPT = frozenset('ͅ')
DIALYTIKA = frozenset('̈')
OTHER_MARKS = frozenset('̄̆')
MARKS = BREATHINGS | ACCENTS | SUBSCRIPT | DIALYTIKA | OTHER_MARKS

ACUTE, GRAVE, CIRCUMFLEX = '́', '̀', '͂'

GREEK_LOWER = 'αβγδεζηθικλμνξοπρσςτυφχψω'
GREEK_UPPER = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
GREEK_LETTERS = frozenset(GREEK_LOWER + GREEK_UPPER + 'ϛϙϡϝϟϲϹ')
VOWELS = frozenset('αεηιουωΑΕΗΙΟΥΩ')
MARK_BEARERS = VOWELS | frozenset('ρΡ')   # rho carries a breathing

# Base-letter confusions the owner allows (unordered pairs; sigma/final sigma handled by position).
CONFUSIONS = frozenset({frozenset(p) for p in ('ει', 'οα', 'οσ', 'νυ', 'πτ', 'ρο', 'ιυ', '0ο')})
SIGMA_PAIR = frozenset('σς')

ELISION = "'’ʼ᾽᾿"


def is_letter(base: str) -> bool:
    """Elision aliases are punctuation even when Unicode calls them letters."""
    return base.isalpha() and base not in ELISION


def word_final_elision(cs, i):
    return (cs[i].base in ELISION and not cs[i].marks and i > 0
            and is_letter(cs[i-1].base)
            and (i+1 == len(cs) or not is_letter(cs[i+1].base)))


def spacing_breathing(cs, i):
    """A spacing psili/koronis before a capital or word-initial vowel.

    Clusters keep any combining marks with their letter, so these predicates
    also work on decomposed text without treating a combining mark as a word.
    """
    return (cs[i].base in '᾿᾽' and not cs[i].marks and i+1 < len(cs)
            and is_letter(cs[i+1].base)
            and (cs[i+1].base.isupper() or
                 (cs[i+1].base in VOWELS and (i == 0 or not is_letter(cs[i-1].base)))))


def punctuation_sites(text, predicate=word_final_elision):
    """Map punctuation to its following letter boundary (aliases are one atom).

    Boundary N is after N letters, ignoring combining marks. Callers comparing
    lines must first establish the same letter sequence; offsets stay local.
    """
    cs=clusters(nfd(text));boundary=0;out={}
    for i,c in enumerate(cs):
        if is_letter(c.base):boundary+=1
        elif predicate(cs,i):out[boundary]=c
    return out


def elision_alias_key(text):
    """Comparison only. Prefix breathings and other quotes retain their bytes."""
    cs=clusters(nfd(text))
    return ''.join(('’' if word_final_elision(cs,i) else c.base)+c.marks for i,c in enumerate(cs))


PUNCT_EDGE = '.,;:·!?"\'«»()[]{}—–-‐‑*†‡§¶"“”‘’…/\\|'
PUNCT_EDGE += ELISION
HYPHENS = ('-', '‐', '‑')


def nfd(s: str) -> str:
    return ud.normalize('NFD', s)


def nfc(s: str) -> str:
    return ud.normalize('NFC', s)


def is_mark(c: str) -> bool:
    return c in MARKS or ud.combining(c) != 0


def strip_marks(s: str) -> str:
    return ''.join(c for c in s if not is_mark(c))


def mark_category(c: str) -> str:
    if c in BREATHINGS:
        return 'breathing'
    if c in ACCENTS:
        return 'accent'
    if c in SUBSCRIPT:
        return 'subscript'
    if c in DIALYTIKA:
        return 'dialytika'
    return 'other'


@dataclass(frozen=True)
class Cluster:
    """A base codepoint with its following combining marks; `start`/`end` index the NFD word core."""
    base: str
    marks: str
    start: int
    end: int

    @property
    def categories(self) -> frozenset:
        return frozenset(mark_category(m) for m in self.marks)


def clusters(core: str) -> list[Cluster]:
    out: list[Cluster] = []
    i = 0
    n = len(core)
    while i < n:
        j = i + 1
        while j < n and is_mark(core[j]):
            j += 1
        out.append(Cluster(core[i], core[i + 1:j], i, j))
        i = j
    return out


@dataclass(frozen=True)
class Token:
    text: str      # the whitespace-delimited token, NFD
    lead: str      # leading punctuation
    core: str      # letters (+ marks) between the punctuation
    trail: str     # trailing punctuation
    start: int     # index of `text` in the NFD line
    end: int
    index: int     # word index in the line

    @property
    def core_start(self) -> int:
        return self.start + len(self.lead)

    @property
    def core_end(self) -> int:
        return self.end - len(self.trail)


def split_token(text: str) -> tuple[str, str, str]:
    i, j = 0, len(text)
    while i < j and text[i] in PUNCT_EDGE:
        i += 1
    while j > i and text[j - 1] in PUNCT_EDGE and not is_mark(text[j - 1]):
        j -= 1
    return text[:i], text[i:j], text[j:]


def tokenize(line: str) -> list[Token]:
    """Whitespace tokens of an NFD line with punctuation split off the core."""
    line = nfd(line)
    out: list[Token] = []
    i = 0
    n = len(line)
    k = 0
    while i < n:
        if line[i].isspace():
            i += 1
            continue
        j = i
        while j < n and not line[j].isspace():
            j += 1
        text = line[i:j]
        lead, core, trail = split_token(text)
        out.append(Token(text, lead, core, trail, i, j, k))
        k += 1
        i = j
    return out


def lexicon_key(core: str) -> str:
    """Mark-stripped, lower-cased key that groups orthographic variants of a word."""
    return lower_word(strip_marks(core))


def lower_word(core: str) -> str:
    """Lower-case a word core; a capital sigma at word end becomes final sigma."""
    low = core.lower()
    if low.endswith('σ') and core.endswith('Σ'):
        low = low[:-1] + 'ς'
    return low


def has_greek(core: str) -> bool:
    return any(c in GREEK_LETTERS for c in core)


def has_latin_or_digit(core: str) -> bool:
    for c in core:
        if c.isdigit():
            return True
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            return True
    return False


def is_capitalised(core: str) -> bool:
    """Initial capital followed by at least one lower-case letter (proper-name shape)."""
    letters = [c for c in core if not is_mark(c)]
    return len(letters) >= 2 and letters[0].isupper() and any(c.islower() for c in letters[1:])


def is_all_caps(core: str) -> bool:
    letters = [c for c in core if not is_mark(c) and c.isalpha()]
    return len(letters) >= 1 and all(c.isupper() for c in letters)


def is_abbreviation(tok: Token) -> bool:
    letters = strip_marks(tok.core)
    return tok.trail.startswith('.') and 0 < len(letters) <= 3


def hyphenated_line_end(tok: Token, is_last: bool) -> bool:
    return is_last and tok.text.endswith(HYPHENS)


@dataclass(frozen=True)
class Diff:
    """How the model's word core differs from Google's; None elsewhere means 'not a candidate'."""
    kind: str                   # 'marks' | 'base'
    cluster_index: int          # index into clusters(google_core) == clusters(model_core)
    google: str                 # the differing cluster/letter in Google's reading
    model: str                  # ... in the model's reading
    categories: frozenset = field(default_factory=frozenset)  # mark categories that changed
    final_position: bool = False  # the cluster is the last mark-bearing cluster of the word

    @property
    def base_pair(self) -> frozenset:
        return frozenset((strip_marks(self.google), strip_marks(self.model)))


def classify_diff(google_core: str, model_core: str) -> Diff | None:
    """Return the single allowed difference between two word cores, else None.

    (i) marks on exactly one cluster, or (ii) exactly one base-letter substitution from the
    confusion list with identical marks. Insertions, deletions and multi-position changes
    are never candidates.
    """
    g, m = nfd(google_core), nfd(model_core)
    if g == m or not g or not m:
        return None
    cg, cm = clusters(g), clusters(m)
    if len(cg) != len(cm):
        return None
    diffs = [i for i, (a, b) in enumerate(zip(cg, cm)) if (a.base, a.marks) != (b.base, b.marks)]
    if len(diffs) != 1:
        return None
    i = diffs[0]
    a, b = cg[i], cm[i]
    bearers = [k for k, c in enumerate(cg) if c.base in MARK_BEARERS]
    final = bool(bearers) and i == bearers[-1]
    if a.base == b.base:
        if a.base not in MARK_BEARERS:
            return None
        ga, mb = set(a.marks), set(b.marks)
        changed = (ga ^ mb)
        cats = frozenset(mark_category(c) for c in changed)
        if 'other' in cats:
            return None
        if sorted(a.marks) == sorted(b.marks):   # same marks, different order: ordering only
            return None
        return Diff('marks', i, a.base + a.marks, b.base + b.marks, cats, final)
    if a.marks != b.marks:
        return None
    pair = frozenset((a.base, b.base))
    if pair == SIGMA_PAIR:
        if i != len(cg) - 1:
            return None   # sigma shape is only a candidate at the word end
        return Diff('base', i, a.base, b.base, frozenset({'final_sigma'}), final)
    if pair in CONFUSIONS:
        return Diff('base', i, a.base, b.base, frozenset({'base_sub'}), final)
    return None


def accent_of(marks: str) -> str | None:
    found = [c for c in marks if c in ACCENTS]
    return found[0] if len(found) == 1 else None
