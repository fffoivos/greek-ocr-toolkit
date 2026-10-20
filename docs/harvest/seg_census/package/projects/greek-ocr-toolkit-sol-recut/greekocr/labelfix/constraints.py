"""Deterministic orthographic constraints of polytonic Greek (no lexicon).

`violations(core, next_core)` returns the hard constraints a word core breaks (empty list =
"possible"). A Google word that violates a constraint while the model's reading satisfies all
of them is a correction candidate that needs no lexicon: the rule `constraint` in `rules.py`
(the ink conjunction for the specific mark is still required).

Constraints (owner, 16 Oct 2026), as implemented:
  C1 initial breathing   a word-initial vowel (or initial diphthong) carries exactly one breathing,
                         on the vowel or on the second vowel of the diphthong; no breathing anywhere
                         else. Initial ρ: a breathing, if present, must be the rough one (ῥ); its
                         absence is NOT a violation (19th-c. prints often omit it) — a deliberate
                         relaxation of the brief, reported.
  C2 marks per letter    at most one breathing and one accent per letter; breathing and dialytika
                         never on the same letter; dialytika and iota subscript are separate and may
                         co-occur with one accent.
  C3 one accent          at most one accent per word, unless the next token is an enclitic (then a
                         second accent on the final syllable is possible).
  C4 accent position     an accent sits on one of the last three syllables; grave only on the final
                         syllable; perispomeni only on the last two and only on a long-capable vowel
                         (η ω, ᾳ ῃ ῳ, a diphthong, or α ι υ) — never on bare ε or ο.
  C5 dialytika           only on ι / υ, never together with a breathing on the same letter.
  C6 iota subscript      only under α η ω (adscript after capital Α Η Ω).
  C7 encoding            accent-before-breathing (or dialytika) inside one cluster is an encoding
                         slip: `normalise` reorders marks (breathing/dialytika, accent, subscript)
                         instead of rejecting. A breathing on a capital is the same codepoints in
                         NFD, so nothing to check there.
Exceptions encoded after the three-way census (47 of 75 "impossible" Google words equalled the
human text before them): medial ῤῥ carries breathings (Τυῤῥηνῶν); crasis / elision writes a
coronis (psili) on the first vowel after an initial consonant (νἄχω, ποὖναι, κἀγώ); all-caps
words carry no marks in print and are not checked; hyphenated compounds are checked part by
part; a line-final word may be followed by an enclitic on the next line, so its second accent on
the final syllable is possible when the next token is unknown. `C4:accent_before_antepenult` is
SOFT (demotic synizesis and poetic forms break it: ἀταίριαστο, θάλαμόνδε): it is reported in the
census but never used by the correction rule (`hard_only=True`).
Not implemented (vowel quantity unknown): the antepenult rule "only if the ultima is short".
"""
from __future__ import annotations

from .text import (ACCENTS, BREATHINGS, DIALYTIKA, GRAVE, CIRCUMFLEX, SUBSCRIPT, Cluster, clusters, lexicon_key,
                   nfd, strip_marks)

VOWELS_LOWER = set('αεηιουω')
VOWELS_UPPER = set('ΑΕΗΙΟΥΩ')
DIPHTHONGS = {'αι', 'ει', 'οι', 'υι', 'αυ', 'ευ', 'ηυ', 'ου', 'ωυ'}
LONG_CAPABLE = set('ηωαιυ')          # ε and ο are always short
ENCLITICS = {lexicon_key(w) for w in (
    'τις τι τινος τινι τινα τινες τινων τισι τισιν τινας τινε τινοιν '
    'μου σου του της μας σας των μοι σοι οἱ με σε ἑ σφων σφισι σφας '
    'ποτε που πως πω πη ποθεν ποι γε τε νυν περ τοι θην ρα '
    'εἰμι ἐστι ἐστιν ἐσμεν ἐστε εἰσι εἰσιν φημι φησι φησιν φασι φασιν').split()}


def _lower(c: str) -> str:
    return c.lower()


def is_vowel(base: str) -> bool:
    return base in VOWELS_LOWER or base in VOWELS_UPPER


def normalise(core: str) -> str:
    """C7: canonical mark order inside each cluster: breathing / dialytika, then accent, then subscript."""
    out = []
    for cl in clusters(nfd(core)):
        marks = cl.marks
        order = {m: (0 if m in BREATHINGS or m in DIALYTIKA else 1 if m in ACCENTS else 2 if m in SUBSCRIPT else 3)
                 for m in marks}
        out.append(cl.base + ''.join(sorted(marks, key=lambda m: order[m])))
    return ''.join(out)


def syllables(cls: list[Cluster]) -> list[list[int]]:
    """Group cluster indices into syllables: a diphthong (two vowels forming one of DIPHTHONGS,
    no dialytika on the second, no accent/breathing on the first) is one syllable."""
    out: list[list[int]] = []
    i = 0
    while i < len(cls):
        c = cls[i]
        if not is_vowel(c.base):
            i += 1
            continue
        if i + 1 < len(cls):
            d = cls[i + 1]
            pair = (_lower(c.base) + _lower(d.base))
            if (pair in DIPHTHONGS and not any(m in DIALYTIKA for m in d.marks)
                    and not any(m in ACCENTS or m in BREATHINGS for m in c.marks)):
                out.append([i, i + 1])
                i += 2
                continue
        out.append([i])
        i += 1
    return out


SOFT = frozenset({'C4:accent_before_antepenult'})
CRASIS_CONSONANTS = set('κτχθπμνδγσ')


def violations(core: str, next_core: str | None = None, hard_only: bool = False) -> list[str]:
    """Constraint violations of a word core (NFD, edge punctuation already stripped).
    Hyphenated compounds are checked part by part; all-caps words are not checked."""
    core = nfd(core)
    if '-' in core.strip('-'):
        parts = [p for p in core.split('-') if p]
        out = []
        for k, part in enumerate(parts):
            out += violations(part, next_core if k == len(parts) - 1 else None, hard_only)
        return sorted(set(out))
    v = _violations(normalise(core), next_core)
    return [x for x in v if not (hard_only and x in SOFT)]


def _violations(core: str, next_core: str | None) -> list[str]:
    cls = clusters(core)
    letters = [c for c in cls if c.base.isalpha()]
    if not letters or not any(is_vowel(c.base) for c in letters):
        return []
    if all(c.base.isupper() for c in letters):
        return []
    v: list[str] = []
    # C2 / C5 / C6 per letter
    for c in cls:
        nb = sum(1 for m in c.marks if m in BREATHINGS)
        na = sum(1 for m in c.marks if m in ACCENTS)
        nd = sum(1 for m in c.marks if m in DIALYTIKA)
        ns = sum(1 for m in c.marks if m in SUBSCRIPT)
        if nb > 1:
            v.append('C2:two_breathings')
        if na > 1:
            v.append('C2:two_accents_one_letter')
        if nb and nd:
            v.append('C2:breathing_with_dialytika')
        if nd and _lower(c.base) not in ('ι', 'υ'):
            v.append('C5:dialytika_not_on_iota_upsilon')
        if ns and _lower(c.base) not in ('α', 'η', 'ω'):
            v.append('C6:subscript_not_under_alpha_eta_omega')
        if (nb or na or nd or ns) and not is_vowel(c.base) and not (_lower(c.base) == 'ρ' and nb and not (na or nd or ns)):
            v.append('C2:mark_on_consonant')
    # medial double rho may carry breathings (ῤῥ): drop those from the breathing census
    rho_pair = set()
    for i in range(len(cls) - 1):
        if _lower(cls[i].base) == 'ρ' and _lower(cls[i + 1].base) == 'ρ' and i > 0:
            rho_pair |= {i, i + 1}
    # C1 breathings
    breathing_positions = [i for i, c in enumerate(cls) if any(m in BREATHINGS for m in c.marks) and i not in rho_pair]
    first = letters[0]
    first_i = cls.index(first)
    # crasis / elision: a coronis (psili) on the first vowel after initial consonant(s) is possible
    syl = syllables(cls)
    first_syl = set(syl[0]) if syl else set()
    coronis_at = [i for i in breathing_positions if i in first_syl and '\u0313' in cls[i].marks]
    if not is_vowel(first.base) and _lower(first.base) in CRASIS_CONSONANTS and len(coronis_at) == 1:
        breathing_positions = [i for i in breathing_positions if i != coronis_at[0]]
    if is_vowel(first.base):
        allowed = {first_i}
        if syl and syl[0][0] == first_i and len(syl[0]) == 2:
            allowed = {syl[0][1]}          # breathing on the second vowel of an initial diphthong
            if first_i in breathing_positions and syl[0][1] not in breathing_positions:
                # a breathing on the first vowel of what looks like a diphthong: then it is not a
                # diphthong (ἄυλος); syllables() already treated the pair as two syllables in that
                # case, so this branch only sees a true diphthong
                pass
        if not breathing_positions:
            v.append('C1:missing_initial_breathing')
        elif len(breathing_positions) > 1:
            v.append('C1:several_breathings')
        elif breathing_positions[0] not in allowed:
            v.append('C1:breathing_not_initial')
    elif _lower(first.base) == 'ρ':
        others = [i for i in breathing_positions if i != first_i]
        if others:
            v.append('C1:breathing_not_initial')
        if first_i in breathing_positions and '̔' not in first.marks:
            v.append('C1:smooth_breathing_on_rho')
    else:
        if breathing_positions:
            v.append('C1:breathing_after_consonant_start')
    # C3 / C4 accents
    accented = [(i, [m for m in c.marks if m in ACCENTS][0]) for i, c in enumerate(cls) if any(m in ACCENTS for m in c.marks)]
    syl_of = {}
    for k, s in enumerate(syl):
        for i in s:
            syl_of[i] = k
    n_syl = len(syl)
    if len(accented) > 1:
        enclitic_next = next_core is None or lexicon_key(strip_marks(nfd(next_core))) in ENCLITICS
        last_syl_accents = [a for a in accented if syl_of.get(a[0], -1) == n_syl - 1]
        if not (enclitic_next and len(accented) == 2 and last_syl_accents):
            v.append('C3:two_accents')
    for i, acc in accented:
        k = syl_of.get(i)
        if k is None:
            continue
        from_end = n_syl - 1 - k
        if from_end > 2:
            v.append('C4:accent_before_antepenult')
        if acc == GRAVE and from_end != 0:
            v.append('C4:grave_not_final')
        if acc == CIRCUMFLEX:
            if from_end > 1:
                v.append('C4:circumflex_before_penult')
            s = syl[k]
            base = _lower(cls[i].base)
            long_ok = len(s) == 2 or base in LONG_CAPABLE or any(m in SUBSCRIPT for m in cls[i].marks)
            if not long_ok:
                v.append('C4:circumflex_on_short_vowel')
    return sorted(set(v))


def possible(core: str, next_core: str | None = None, hard_only: bool = False) -> bool:
    return not violations(core, next_core, hard_only)
