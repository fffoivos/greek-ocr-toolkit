"""Glyph model: font gate, rendered truth, letters vs marks, letter boxes (pieces), skew/bend, double lines, ink state.
Each CP-G1 finding (docs/reviews/CP-G1_review_1.md) has a regression here, named test_f<n>_…"""
from pathlib import Path
import json
import random

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from greekocr.glyphs.baseline import skew_line
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.evaluate import GlyphScore, score_rendered, summarise
from greekocr.glyphs.ink import ink_profile
from greekocr.glyphs.letters import letter_boxes
from greekocr.glyphs.report import document_of, line_record
from greekocr.glyphs.synthetic import (DEFECTS, LETTER, MARK, NEIGHBOUR, UnsupportedText, font_covers,
                                       font_supports_polytonic, render_truth_line)

FONTS = Path(__file__).parents[1] / 'fixtures' / 'fonts'
LINES = Path(__file__).parents[1] / 'fixtures' / 'o4d_lines'
DIDOT = FONTS / 'GFSDidot-Regular.ttf'
OWNER = LINES / 'regressions' / 's2-60f24a3d8a2d714767f2-p00003-l00024_old.png'
TEXTS = ['ἀνδρώας κύστεως, μεταξὺ τῶν τῆς ἥβης καλουμένων ὀστῶν καθήκοντα',
         'γὰρ πονηρίας ἐρρίζωκεν ἐν αὐτῷ. καρδία συνετοῦ διανοηθήσεται παραβολήν',
         'πᾶν βρῶμα φάγεται κοιλία, ἔστι δὲ βρῶμα βρώματος κάλλιον ἐν τῇ ὁδῷ',
         'ἀνατομικὰ ἔσχον· ὅθεν οὐδ’ ἐκείνων μοι μέλει. περὶ δὲ τῶν ἀνδρῶν τούτων']


def _bodies(values, *, tail=False):
    """Ten hollow 22×24 letter bodies on paper 235 (band rows 20–44), ink gray per letter; optional tail below."""
    img = np.full((80, 420), 235.0)
    for i, v in enumerate(values):
        x0 = 10 + 40 * i
        img[20:44, x0:x0 + 22] = v
        img[25:39, x0 + 6:x0 + 16] = 235
        if tail and i == 4:
            img[44:72, x0 + 8:x0 + 13] = v
    return Image.fromarray(img.astype(np.uint8))


# ---------- font gate and rendered truth (F2, F6) ----------

def test_font_gate_accepts_polytonic_and_rejects_missing_glyphs():
    assert font_supports_polytonic(DIDOT) == (True, 'ok')
    ok, why = font_supports_polytonic(FONTS / 'XCharter-Regular.otf')
    assert not ok and 'notdef' in why


def test_f6_render_refuses_text_the_font_cannot_draw():
    # CP-G1c2 F2: a supported breathing must not hide an unsupported combining macron
    assert not font_covers(DIDOT, 'ἀ\u0304')[0]
    with pytest.raises(UnsupportedText):
        render_truth_line('ἀ\u0304', DIDOT, degrade=False)
    assert not font_covers(FONTS / 'XCharter-Regular.otf', 'ἀἁ')[0]
    with pytest.raises(UnsupportedText):
        render_truth_line('ἀἁἄἅ', FONTS / 'XCharter-Regular.otf', degrade=False)
    with pytest.raises(UnsupportedText):
        render_truth_line('ἀνδρώας', DIDOT, neighbours=('abc', 'ἀἁ￾'), degrade=False)


def test_f2_rendered_ink_is_only_the_real_graphemes():
    text = TEXTS[0]
    r = render_truth_line(text, DIDOT, size=40, degrade=False)
    drawn = np.asarray(r.image) < 128
    font = ImageFont.truetype(str(DIDOT), 40)
    direct = Image.new('L', r.image.size, 0)
    ImageDraw.Draw(direct).text((20, 20 + 40 * .25), text, font=font, fill=255)
    assert (drawn & ~ndi.binary_dilation(np.asarray(direct) > 127, iterations=1)).sum() <= .01 * drawn.sum()
    assert (r.truth == MARK).sum() > 100
    letters = [g for g in r.glyphs if g.kind == LETTER]
    assert len(letters) == sum(ch.isalpha() for ch in text) and all(g.reliable for g in letters)
    for k, g in enumerate(r.glyphs):     # boxes come from the final letter-id map
        if g.kind == LETTER:
            ys, xs = np.nonzero(r.glyph_ids == k + 1)
            assert g.box == (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def test_neighbour_lines_only_intrude():
    r = render_truth_line(TEXTS[0], DIDOT, size=36, rng=random.Random(3), neighbours=(TEXTS[1], TEXTS[2]))
    assert (r.truth == NEIGHBOUR).any() and r.image.height < 2 * 36


def test_f3_defect_maps_follow_rotation_and_bend():
    r = render_truth_line(TEXTS[1], DIDOT, size=36, rng=random.Random(9), ink_defects=[(.1, .4, 'fade', .8)],
                          bend=('right', 1.0, .3))
    assert r.skew_deg != 0
    on = r.defect_kind == DEFECTS['fade']
    assert on.any() and (on & ~ndi.binary_dilation(r.truth > 0, iterations=1)).sum() == 0
    assert r.ink_truth.min() < -.5 and r.ink_truth.max() == 0


# ---------- evaluation counts truth objects (F1) ----------

def test_f1_lost_accents_count_as_misses():
    r = render_truth_line(TEXTS[0], DIDOT, size=40, degrade=False)
    assert summarise(score_rendered(r))['marks_found'] == 1.0
    lab, n = ndi.label(r.truth == MARK, structure=np.ones((3, 3)))
    arr = np.asarray(r.image).copy()
    for i in range(1, n + 1, 2):
        arr[ndi.binary_dilation(lab == i, iterations=2)] = 255
    r.image = Image.fromarray(arr)
    s = summarise(score_rendered(r))
    assert s['marks_found'] == pytest.approx(len(range(1, n + 1)[1::2]) / s['marks_total'], abs=.01)


def test_f1c2_neighbour_recall_counts_erased_neighbour_ink():
    r = render_truth_line(TEXTS[0], DIDOT, size=36, rng=random.Random(3), neighbours=(TEXTS[1], TEXTS[2]))
    full = summarise(score_rendered(r))
    lab, n = ndi.label((r.truth == NEIGHBOUR) & r.oracle_ink, structure=np.ones((3, 3)))
    arr = np.asarray(r.image).copy()
    for i in range(1, n + 1, 2):
        arr[ndi.binary_dilation(lab == i, iterations=2)] = 255
    r.image = Image.fromarray(arr)
    half = summarise(score_rendered(r))
    assert half['neighbour_recall'] < .8 * full['neighbour_recall']
    assert half['neighbour_classified_of_detected'] > .9      # the conditional rate stays high: reported separately


def test_f1c2_letter_truth_does_not_depend_on_the_detector():
    r = render_truth_line(TEXTS[1], DIDOT, size=36, rng=random.Random(4), ink_defects=[(.2, .6, 'break', 1.0)])
    g = line_glyphs(r.image)
    a = summarise(score_rendered(r, g))
    g.band = type(g.band)(g.band.top + 3 * g.band.xh, g.band.bottom + 3 * g.band.xh, g.band.xh, g.band.n_support)
    b = summarise(score_rendered(r, g, letter_boxes(line_glyphs(r.image))))
    true_states = lambda S: {k.split('->')[0]: 0 for k in S['state_confusion']} | {}
    count = lambda S: {t: sum(v for k, v in S['state_confusion'].items() if k.split('->')[0] == t) for t in true_states(S)}
    assert count(a) == count(b) and a['letters_true'] == b['letters_true']


@pytest.mark.parametrize('truth', ['print', 'visible'])
def test_c3_faded_but_visible_letters_are_not_counted_vanished_or_missed(truth):
    """CP-G1c3 probe: a fade leaving 36 % contrast is above the visible threshold and in the print."""
    r = render_truth_line(TEXTS[0], DIDOT, size=40, degrade=False, ink_defects=[(.2, .6, 'fade', .8)])
    S = summarise(score_rendered(r, state_truth=truth))
    assert S['vanished'] == 0 and S['letters_missed'] == 0


@pytest.mark.parametrize('neighbours', [False, True])
def test_marks_letters_and_neighbours_on_rendered_lines(neighbours):
    rng, total = random.Random(7), GlyphScore()
    for i in range(24):
        nb = (TEXTS[(i + 1) % 4], TEXTS[(i + 2) % 4]) if neighbours else None
        r = render_truth_line(TEXTS[i % 4], DIDOT, size=rng.randint(28, 44), rng=random.Random(i), neighbours=nb)
        total.add(score_rendered(r))
    s = summarise(total)
    # accents touching their letter (heavy ink / blur) become part of it: report, and score the separate ones
    assert s['marks_detected'] >= .99 and s['marks_found_of_separate'] >= .93 and s['mark_component_precision'] >= .93
    assert s['letter_detection']['one'] >= .75     # measured 0.78 / 0.85 on these Didot lines (all fonts: 0.93)
    if neighbours:
        assert s['neighbour_classified_of_detected'] >= .95 and s['neighbour_recall'] >= .5


# ---------- letters as pieces; ink state (F4, F5) ----------

def test_letter_boxes_split_touching_letters():
    img = np.full((60, 400), 235, np.uint8)
    starts = [10 + 30 * i for i in range(10)]
    for x0 in starts:
        img[20:44, x0:x0 + 20] = 20
        img[24:40, x0 + 6:x0 + 14] = 235
    for x0 in starts[1:3]:
        img[30:33, x0 + 20:x0 + 30] = 20
    boxes = letter_boxes(line_glyphs(Image.fromarray(img)))
    assert len(boxes) == 10 and sum(b.split for b in boxes) == 3
    states = [l.state for l in ink_profile(line_glyphs(Image.fromarray(img))).letters]
    assert states.count('merged') == 3 and states.count('intact') == 7


def test_broken_letter_pieces_are_grouped_into_one_letter():
    img = np.asarray(_bodies([20] * 10)).copy()
    img[30:33, 10 + 40 * 3:10 + 40 * 3 + 22] = 235        # letter 4: a horizontal gap → top and bottom pieces
    img[20:44, 10 + 40 * 6 + 10:10 + 40 * 6 + 13] = 235   # letter 7: a vertical gap → left and right arcs
    prof = ink_profile(line_glyphs(Image.fromarray(img)))
    assert len(prof.letters) == 10
    assert [l.state for l in prof.letters].count('broken') == 2
    assert prof.letters[3].pieces == 2 and prof.letters[6].pieces == 2


def test_f3c2_pieces_are_counted_inside_the_middle_region_only():
    img = np.asarray(_bodies([20] * 10)).copy()
    x0 = 10 + 40 * 6
    img[20:44, x0 + 10:x0 + 13] = 235      # vertical gap through letter 7's body
    img[8:20, x0 + 4:x0 + 18] = 20         # the two arcs joined above the band only
    prof = ink_profile(line_glyphs(Image.fromarray(img)))
    assert prof.letters[6].state == 'broken' and prof.letters[6].pieces == 2


def test_f4c2_faint_body_attached_to_a_dark_stroke_is_kept_and_flagged():
    img = np.asarray(_bodies([20] * 10)).astype(float)
    x0 = 10 + 40 * 3
    img[20:44, x0:x0 + 22] = 195; img[25:39, x0 + 6:x0 + 16] = 235; img[20:44, x0:x0 + 4] = 20
    g = line_glyphs(Image.fromarray(img.astype(np.uint8)))
    assert g.ink[20:44, x0:x0 + 22].sum() > .75 * 388
    assert ink_profile(g).letters[3].state in ('broken', 'faint')


def test_f5c2_fully_fused_letters_are_flagged_merged():
    img = np.full((60, 420), 235, np.uint8)
    for i in range(10):
        img[20:44, 10 + 40 * i:32 + 40 * i] = 20
    img[20:44, 10 + 40 * 3 + 22:10 + 40 * 4] = 20
    prof = ink_profile(line_glyphs(Image.fromarray(img)))
    assert len(prof.letters) == 9
    assert [l.state for l in prof.letters].count('merged') == 1 and [l.state for l in prof.letters].count('intact') == 8


def test_f4_ink_state_ignores_ink_outside_the_middle_region():
    plain = ink_profile(line_glyphs(_bodies([20] * 10)))
    tailed = ink_profile(line_glyphs(_bodies([20] * 10, tail=True)))
    assert [l.score for l in plain.letters] == [l.score for l in tailed.letters] == [0.0] * 10


def test_f5_faint_letters_are_detected_and_flagged():
    prof = ink_profile(line_glyphs(_bodies([195] * 5 + [20] * 5)))
    assert len(prof.letters) == 10
    assert [l.state for l in prof.letters] == ['faint'] * 5 + ['intact'] * 5


@pytest.mark.parametrize('kind,state,floor', [('break', 'broken', .4), ('thick', 'merged', .4)])
def test_injected_defects_change_letter_state_inside_their_region(kind, state, floor):
    """Votes use only each box's own pixels inside its bounds (CP-G1c2 F6)."""
    inside = outside = hit_in = hit_out = 0
    for i in range(4):
        r = render_truth_line(TEXTS[i], DIDOT, size=36, rng=random.Random(300 + i), ink_defects=[(.3, .7, kind, 1.0)])
        g = line_glyphs(r.image)
        for b, l in zip(letter_boxes(g), ink_profile(g).letters):
            own = np.zeros(g.labels.shape, bool)
            own[b.y0:b.y1, b.x0:b.x1] = np.isin(g.labels[b.y0:b.y1, b.x0:b.x1], b.components)
            own &= r.truth == LETTER
            d = (r.defect_kind[own] > 0).mean() if own.any() else 0
            if d > .5:
                inside += 1; hit_in += l.state == state
            elif d == 0:
                outside += 1; hit_out += l.state == state
    assert hit_in / inside >= floor and hit_in / inside > 3 * hit_out / outside


# ---------- skew, bend, cut-offs, double lines ----------

def test_skew_line_recovers_rendered_rotation():
    errors = []
    for i in range(8):
        r = render_truth_line(TEXTS[i % 4], DIDOT, size=36, rng=random.Random(100 + i))
        errors.append(abs(skew_line(line_glyphs(r.image)).angle_deg - r.skew_deg))
    assert np.median(errors) < .1 and max(errors) < .5


def test_band_follows_a_bent_line_end():
    r = render_truth_line(TEXTS[1], DIDOT, size=36, rng=random.Random(12), bend=('left', -1.2, .3))
    g = line_glyphs(r.image)
    cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]
    err = np.abs(g.band.bottom[cols[0]:cols[-1]] - r.base_truth[cols[0]:cols[-1]]) / g.band.xh
    assert np.percentile(err, 95) < .25


def test_line04_band_covers_first_words_and_crosses_top():
    """Owner 8 Oct: the first two words of line04 had no underline; the band rises ~40 px and leaves the crop top."""
    s = skew_line(line_glyphs(Image.open(LINES / 'line04_medium.png')))
    assert s.support_x[0] < 100
    assert abs(s.baseline[120] - 42) < 4               # letters at x≈108–153 end at row 42
    assert any(c.line == 'meanline' and c.edge == 'top' and 900 < c.x < 1250 for c in s.crossings)
    assert any(c.edge == 'top' for c in s.cut_letters) and not s.double_line


@pytest.mark.parametrize('name,double', [('line08_medium', True), ('line01_large', True), ('line04_medium', False),
                                          ('line05_small', False), ('line09_small', False)])
def test_double_line_flag_on_fixtures(name, double):
    assert skew_line(line_glyphs(Image.open(LINES / f'{name}.png'))).double_line is double


def test_double_line_flag_on_rendered_crops():
    rng, hits = random.Random(5), {True: 0, False: 0}
    for i in range(8):
        two = i % 2 == 0
        r = render_truth_line(TEXTS[i % 4], DIDOT, size=34, rng=random.Random(700 + i),
                              second_line=TEXTS[(i + 1) % 4] if two else None,
                              neighbours=None if two else (TEXTS[(i + 2) % 4], TEXTS[(i + 3) % 4]))
        hits[two] += skew_line(line_glyphs(r.image)).double_line
    # recall on full second lines; rendered neighbour tips still give false alarms (precision 0.74 on 200 crops)
    assert hits[True] >= 3 and hits[False] <= 2


# ---------- report (F8) ----------

def test_f8_records_are_strict_json_even_for_a_blank_crop(tmp_path):
    p = tmp_path / 'blank.png'
    Image.fromarray(np.full((60, 320), 235, np.uint8)).save(p)
    rec = line_record(p)
    json.dumps(rec, allow_nan=False)
    assert rec['residual_px'] is None and rec['confidence'] == 'low'


def test_line_record_uses_document_prior_for_the_owner_example():
    assert document_of(OWNER.name) == 's2-60f24a3d8a2d714767f2'
    rec = line_record(OWNER, priors={'s2-60f24a3d8a2d714767f2': {'xh': 21.0, 'n': 1}})
    json.dumps(rec, allow_nan=False)
    assert rec['prior'] == {'xh': 21.0, 'n': 1} and rec['xh'] == 21.0
    assert rec['cut_spans'] and rec['letters'] and len(rec['visible']) > 300
    assert max(rec['visible'][:30]) < .5 and max(rec['visible']) > .9   # unreadable at the start, readable later


def test_four_guide_lines_for_main_and_neighbour_lines():
    """Neighbours borrow the main line's shape; the renderer's true neighbour baselines check the placement."""
    from greekocr.glyphs.baseline import text_lines
    errs = []
    for i in range(6):
        r = render_truth_line(TEXTS[i % 4], DIDOT, size=36, rng=random.Random(900 + i), neighbours=(TEXTS[(i + 1) % 4], TEXTS[(i + 2) % 4]))
        L = text_lines(line_glyphs(r.image))
        main = L[0]
        assert main.side == 'main' and np.all(main.ascender < main.mean) and np.all(main.base < main.descender)
        cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]
        for side, tb in r.other_base_truth:
            pred = [l for l in L if l.side == ('below' if side > 0 else 'above')]
            if pred:
                errs.append(min(float(np.median(np.abs(l.base[cols] - tb[cols]))) for l in pred) / r.xh)
    assert len(errs) >= 8 and np.median(errs) < .2


def test_owner_b1ce_four_lines_in_one_crop():
    """Owner 8 Oct: b1ce…l00068 holds four lines; above, main, and tips above and below are all placed."""
    from greekocr.glyphs.baseline import text_lines
    L = text_lines(line_glyphs(Image.open(Path(__file__).parents[1] / 'fixtures' / 'o4d_sample400' / 'crops' / 's2-b1ce8959da62cc55c839-p00009-l00068.png')))
    sides = sorted(round(l.shift_xh) for l in L)
    assert sides == [-5, -3, 0, 2]
