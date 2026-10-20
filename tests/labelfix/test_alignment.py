"""Token pairing, CTC frame -> span mapping and alignment transfer (pure functions)."""
import unicodedata as ud

import numpy as np

from greekocr.labelfix.candidates import align_chars, pair_tokens
from greekocr.labelfix.ctc_align import Alignment, CharSpan, frames_to_spans, transfer_alignment


def N(s):
    return ud.normalize('NFD', s)


def test_pair_tokens_equal_counts_pairs_by_index():
    pairs = pair_tokens(N('ὁ νέος ἐλυπήθη'), N('ὀ νέος ἐλυπήθη'))
    assert [(g.core, m.core) for g, m in pairs] == [(N('ὁ'), N('ὀ')), (N('νέος'), N('νέος')), (N('ἐλυπήθη'), N('ἐλυπήθη'))]


def test_pair_tokens_unequal_counts_uses_char_alignment():
    pairs = pair_tokens(N('χρόνος τότητα'), N('χρόνος'))
    assert pairs[0][1] is not None and pairs[0][1].core == N('χρόνος')
    assert pairs[1][1] is None
    pairs = pair_tokens(N('καὶ τὸ βῆμα'), N('καὶτὸ βήμα'))
    # 'καὶ' and 'τὸ' both align into one model token: neither is a one-to-one pair
    assert pairs[0][1] is None and pairs[1][1] is None and pairs[2][1].core == N('βήμα')


def test_align_chars_is_a_valid_path():
    path = align_chars('abcd', 'abxd')
    assert [p for p in path if p[0] is not None and p[1] is not None and 'abcd'[p[0]] != 'abxd'[p[1]]] == [(2, 2)]


def test_frames_to_spans_places_characters_between_spikes():
    ids = np.array([0, 5, 5, 0, 0, 7, 0, 9, 9, 0])
    spans = frames_to_spans(ids, lambda v: {5: 'a', 7: 'b', 9: 'c'}[v], scale=2.0)
    assert ''.join(s.char for s in spans) == 'abc'
    assert (spans[0].frame0, spans[0].frame1) == (1, 3) and (spans[1].frame0, spans[1].frame1) == (5, 6)
    # STRIDE 4 px per frame, scale 2: 'a' spans from frame 0 to the midpoint (3+5)/2 = 4 -> 32 px
    assert spans[0].x0 == 0.0 and spans[0].x1 == 4 * 4 * 2.0
    assert spans[1].x0 == spans[0].x1 and spans[2].x1 == (9 + 1) * 4 * 2.0


def test_transfer_alignment_keeps_matched_spans():
    al = Alignment('abc', [CharSpan('a', 0, 0, 1, 0.0, 10.0), CharSpan('b', 1, 1, 2, 10.0, 20.0), CharSpan('c', 2, 2, 3, 20.0, 30.0)], 3, 1.0, 12)
    t = transfer_alignment('abxc', al)
    assert [c.char for c in t.spans] == list('abxc')
    assert (t.spans[0].x0, t.spans[0].x1) == (0.0, 10.0) and (t.spans[3].x0, t.spans[3].x1) == (20.0, 30.0)
    assert (t.spans[2].x0, t.spans[2].x1) == (10.0, 20.0)   # unmatched 'x' borrows its neighbour's span
    assert transfer_alignment('abc', al) is al
