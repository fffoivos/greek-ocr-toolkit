"""Offline text comparison for T14b; no reader construction or network I/O."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable
import unicodedata as ud

from .montage import compare_nfd

__all__ = ["letters_marks", "compare_control", "summarise_controls"]

# Include spacing Greek coronis/psili and modifier apostrophes before selecting
# letters: U+02BC is Lm, but an apostrophe must not masquerade as a base letter.
_APOSTROPHES = "'\u2018\u2019\u02bc\u1fbd\u1fbf\u1ffe\u0060\u00b4"
_APOSTROPHE_MAP = str.maketrans({c: "'" for c in _APOSTROPHES})
_KINDS = {"L": "letter", "M": "mark", "N": "number", "P": "punctuation", "S": "symbol"}


def letters_marks(text: str) -> str:
    """NFD L/M codepoints only, after unifying spacing apostrophe variants.

    All punctuation (including edges), whitespace, numbers and symbols are
    ignored. Case, base-letter variants and every combining mark are preserved.
    This diagnostic does not test word boundaries or punctuation preservation.
    """
    return "".join(c for c in ud.normalize("NFD", text.translate(_APOSTROPHE_MAP))
                   if ud.category(c)[0] in "LM")


def _kind(char):
    return "whitespace" if char.isspace() else _KINDS.get(ud.category(char)[0], "other")


def _differences(reference, prediction):
    """One minimum-edit NFD alignment; ties: diagonal, deletion, insertion."""
    a, b = ud.normalize("NFD", reference), ud.normalize("NFD", prediction)
    matrix = [list(range(len(b) + 1))]
    for i, ca in enumerate(a, 1):
        row = [i]
        for j, cb in enumerate(b, 1):
            row.append(min(matrix[-1][j - 1] + (ca != cb), matrix[-1][j] + 1, row[-1] + 1))
        matrix.append(row)
    i, j, changes = len(a), len(b), []
    while i or j:
        if i and j and matrix[i][j] == matrix[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]:
                changes.append(dict(operation="substitute", reference=a[i - 1], prediction=b[j - 1],
                                    reference_index=i - 1, prediction_index=j - 1))
            i -= 1; j -= 1
        elif i and matrix[i][j] == matrix[i - 1][j] + 1:
            changes.append(dict(operation="delete", reference=a[i - 1], prediction="",
                                reference_index=i - 1, prediction_index=j))
            i -= 1
        else:
            changes.append(dict(operation="insert", reference="", prediction=b[j - 1],
                                reference_index=i, prediction_index=j - 1))
            j -= 1
    changes.reverse()
    kinds, operations, transitions = Counter(), Counter(), Counter()
    for change in changes:
        operations[change["operation"]] += 1
        for side in ("reference", "prediction"):
            if change[side]:
                kinds[_kind(change[side])] += 1
        transitions[( _kind(change["reference"]) if change["reference"] else "empty") + "->" +
                    (_kind(change["prediction"]) if change["prediction"] else "empty")] += 1
    return dict(changes=changes, char_kind_histogram=dict(sorted(kinds.items())),
                edit_operations=dict(sorted(operations.items())), kind_transitions=dict(sorted(transitions.items())))


def compare_control(reference: str, prediction: str) -> dict[str, Any]:
    """Exact NFD/letters+marks identity, CER, and minimum-edit kind histogram.

    Histogram counts changed codepoints on both sides: a substitution counts
    two codepoints; insertions/deletions count one. Operations count edits.
    """
    from .core import edits
    a, b = letters_marks(reference), letters_marks(prediction)
    return dict(**compare_nfd(reference, prediction), letters_marks_identical=a == b,
                letters_marks_edits=edits(a, b), **_differences(reference, prediction))


def summarise_controls(comparisons: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate crop identity percentages and changed-codepoint histograms."""
    rows = list(comparisons)
    if not rows:
        raise ValueError("control cohort must be nonempty")
    result = dict(lines=len(rows))
    for field, prefix in (("identical", "exact"), ("letters_marks_identical", "letters_marks")):
        count = sum(row[field] for row in rows)
        result[prefix + "_count"] = count
        result[prefix + "_pct"] = 100 * count / len(rows)
    for field in ("char_kind_histogram", "edit_operations", "kind_transitions"):
        counter = Counter()
        for row in rows:
            counter.update(row[field])
        result[field] = dict(sorted(counter.items()))
    return result
