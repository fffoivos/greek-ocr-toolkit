"""Unicode diagnostics for Greek readings; language plausibility belongs to the judge."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import re
import unicodedata as ud

__all__ = ['TextChecks', 'text_checks']

ACCENTS = frozenset('\u0300\u0301\u0342')
BREATHINGS = frozenset('\u0313\u0314')
VOWELS = frozenset('αεηιουω')
POLYTONIC = BREATHINGS | frozenset('\u0342\u0345')
ORDINARY_PUNCTUATION = frozenset('.,;:··!?…–—-\'’‘"“”«»()[]/')


@dataclass(frozen=True)
class TextChecks:
    """All ratios/scores are 0..1; None means unavailable, not a negative result."""
    is_greek_script: float
    lexicon_validity: float | None
    polytonic_consistency: dict
    garbage_score: float
    consonant_run_ratio: float
    mixed_script_word_ratio: float
    symbol_density: float
    n_letters: int
    n_words: int
    problems: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _script(char: str) -> str:
    name = ud.name(char, '')
    return 'Greek' if 'GREEK' in name else 'Latin' if 'LATIN' in name else 'Cyrillic' if 'CYRILLIC' in name else 'Other'


def _clusters(text: str) -> list[tuple[str, list[str]]]:
    result: list[tuple[str, list[str]]] = []
    for char in ud.normalize('NFD', text):
        if ud.category(char).startswith('M'):
            if result:
                result[-1][1].append(char)
            else:
                result.append(('', [char]))
        else:
            result.append((char, []))
    return result


def text_checks(text: str) -> TextChecks:
    """Check normalized graphemes, not NFC-vs-NFD representation differences.

    Breathing absence is advisory only in demonstrably polytonic input. Monotonic
    Greek, capitals, diphthong placement, enclitic double accents and line fragments
    are tolerated. No vocabulary is derived from the sample readings; no bundled
    frequency lexicon is present in this vendor tree, hence lexicon_validity=None.
    """
    if not isinstance(text, str):
        raise TypeError('text must be str')
    nfd = ud.normalize('NFD', text)
    nfc = ud.normalize('NFC', text)
    letters = [c for c in nfd if c.isalpha()]
    greek = [c for c in letters if _script(c) == 'Greek']
    words = re.findall(r'[^\W\d_]+(?:[\u0300-\u036f]+[^\W\d_]*)*', nfd)
    polytonic = any(c in POLYTONIC for c in nfd)
    initial_vowels = breathing_missing = accented = unaccented = impossible = 0
    mixed = consonant_runs = 0
    details = []
    for number, word in enumerate(words):
        clusters = _clusters(word)
        bases = ''.join(base for base, _ in clusters)
        scripts = {_script(c) for c in bases if c.isalpha()}
        if len(scripts) > 1:
            mixed += 1
            details.append(f'mixed scripts in word {number+1}: {ud.normalize("NFC", word)}')
        folded = bases.casefold()
        if re.search(r'[βγδζθκλμνξπρσςτφχψ]{5,}', folded):
            consonant_runs += 1
        accents = sum(sum(m in ACCENTS for m in marks) for _, marks in clusters)
        accented += accents > 0
        unaccented += accents == 0 and len(bases) > 1 and not bases.isupper()
        if polytonic and clusters and clusters[0][0].casefold() in VOWELS and not bases.isupper():
            initial_vowels += 1
            # Initial diphthongs may carry breathing on the second vowel.
            head = clusters[:2] if len(clusters)>1 and clusters[1][0].casefold() in 'ιυ' else clusters[:1]
            breathing_missing += not any(m in BREATHINGS for _, marks in head for m in marks)
        for base, marks in clusters:
            if not marks:
                continue
            low = base.casefold()
            greek_base = _script(base) == 'Greek'
            invalid = (not base.isalpha()
                       or len(set(marks)) != len(marks)
                       or sum(m in ACCENTS for m in marks) > 1
                       or sum(m in BREATHINGS for m in marks) > 1
                       or greek_base and any(m in ACCENTS for m in marks) and low not in VOWELS
                       or any(m in BREATHINGS for m in marks) and low not in VOWELS | {'ρ'}
                       or '\u0345' in marks and low not in 'αηω'
                       or greek_base and '\u0308' in marks and low not in 'ιυ'
                       or '\u0342' in marks and low in 'εο'
                       or '\u0304' in marks and '\u0306' in marks
                       or '\u0342' in marks and '\u0306' in marks
                       or greek_base and '\u0304' in marks and low in 'εο'
                       or greek_base and '\u0306' in marks and low in 'ηω'
                       or '\u0308' in marks and any(m in BREATHINGS for m in marks))
            if invalid:
                impossible += 1
                details.append(f'impossible mark stack in word {number+1}: {base}{"".join(marks)}')
        # Two word accents can be grammatical with enclitics. Three are suspicious.
        if accents > 2:
            details.append(f'more than two accents in word {number+1}')
    # Standalone/control/replacement marks and symbol-heavy corruption are counted
    # separately from ordinary punctuation, numerals and Greek middle dots.
    visible = [c for c in nfc if not c.isspace()]
    symbols = sum(ud.category(c).startswith(('S', 'C')) or c == '\ufffd'
                  or ud.category(c).startswith('P') and c not in ORDINARY_PUNCTUATION
                  for c in visible)
    orphan_marks = sum(not b.isalpha() and bool(m) for b, m in _clusters(text))
    impossible += orphan_marks
    if orphan_marks:
        details.append('orphan combining marks')
    if not letters:
        details.append('no letters')
    density = symbols/max(1, len(visible))
    nwords = len(words)
    runs_ratio = consonant_runs/max(1, nwords)
    mixed_ratio = mixed/max(1, nwords)
    stack_ratio = impossible/max(1, len(letters))
    script_ratio = len(greek)/max(1, len(letters))
    garbage = min(1., .35*runs_ratio + .45*mixed_ratio + .70*density + .60*stack_ratio + .30*(1-script_ratio))
    if not text.strip():
        garbage = 1.
    consistency = {'polytonic_detected': polytonic,
                   'initial_vowel_words': initial_vowels,
                   'missing_breathing_words': breathing_missing,
                   'missing_breathing_ratio': breathing_missing/max(1, initial_vowels) if polytonic else None,
                   'accented_word_ratio': accented/max(1, nwords),
                   'unaccented_noncapital_words': unaccented,
                   'impossible_mark_stacks': impossible,
                   'score': max(0., 1-.5*breathing_missing/max(1, initial_vowels)-min(1., stack_ratio*5)) if polytonic else None}
    return TextChecks(script_ratio, None, consistency, garbage, runs_ratio, mixed_ratio,
                      density, len(letters), nwords, tuple(dict.fromkeys(details)))
