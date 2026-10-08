"""Named, auditable candidate rules; these are heuristics, never certification of gold."""
from __future__ import annotations
import hashlib
import re
import unicodedata as ud
from statistics import median
import numpy as np
from greekocr._vendor.bench.common import features

# Versioned LABEL policy, applied before codec encoding and pool selection.
LABEL_POLICY = 'nfc-separators-lunate/v1'
LUNATE_FOLDS = {'ϲ': 'ς', 'Ϲ': 'Σ'}


def normalize_label(text):
    """NFC; whitespace and U+200B/U+FEFF -> trimmed single ASCII spaces.

    The two zero-width space characters are word boundaries, not deletions.
    Other format/control characters remain literal. Raw C0/C1 controls still
    reject in admit(), including whitespace controls such as TAB/LF/CR/NEL.
    Owner-requested lunate folds are LABEL policy, never codec behavior.
    """
    mapped = ''.join(' ' if c.isspace() or c in ('\u200b', '\ufeff')
                     else LUNATE_FOLDS.get(c, c) for c in text)
    # Split only on ASCII space; do not erase any other unknown characters.
    return ud.normalize('NFC', ' '.join(part for part in mapped.split(' ') if part))

RULES = ('pua', 'control', 'replacement', 'tounicode_residue', 'ligature_artifact',
         'letter_run', 'dictionary_collapse', 'crop_height', 'aspect_ratio',
         'overlapping_lines', 'rotated_text', 'ink_bbox_mismatch', 'multiline_ink',
         'near_duplicate', 'no_text', 'invalid_char_geometry', 'blank_ink', 'fragment_short', 'fragment_no_letters',
         'fragment_symbol_dominated', 'missing_baseline_neighbour', 'crop_text_mismatch', 'label_spacing_gap',
         'unexplained_ink', 'missing_ink', 'cross_column')
RESIDUE = re.compile(r'\(cid:|/(?:uni[0-9a-f]{4,6}|u[0-9a-f]{4,6}|glyph\d+|[A-Za-z]+\.(?:alt|liga|sc|ss\d{2}|cv\d{2}))\b|\b(?:uni[0-9a-f]{4,6}|glyph\d+|cid\d{3,})\b|\.notdef', re.I)


def duplicate_key(text):
    # Case/whitespace-normalized exact hash plus digit masking catches changing folios/heads.
    s = ' '.join(ud.normalize('NFC', text).casefold().split())
    s = re.sub(r'\d+', '#', s)
    return hashlib.sha256(s.encode()).hexdigest()


def dictionary_rate(text, lexicon):
    words = re.findall(r'[^\W\d_]+', text.casefold())
    return sum(w in lexicon for w in words) / max(1, len(words))


def otsu_mask(image):
    """Inclusive Otsu split (including two-tone black/white), excluding white."""
    a = np.asarray(image.convert('L'))
    hist = np.bincount(a.ravel(), minlength=256).astype(float)
    count = np.cumsum(hist); mass = np.cumsum(hist * np.arange(256))
    denom = count * (count[-1] - count)
    variance = np.divide((mass[-1]*count - mass*count[-1])**2, denom,
                         out=np.zeros(256), where=denom > 0)
    threshold = int(np.argmax(variance))
    return a <= min(254, threshold), threshold


def char_ink_diagnostics(image, boxes, margin=2, noise_area=3, containment=.90):
    """Explain 8-connected Otsu ink with the union of crop-local glyph boxes.

    At 200 dpi boxes expand by 2 pixels for rounding/accents/descenders. Every
    component >=3 pixels needs >=90% of its ink in that union. Also reject any
    >=3-pixel connected residual: a rule touching a glyph must not hide inside
    a large mostly-explained component. A second Otsu split on pixels outside
    the union (white elsewhere), capped at 245, catches faint grey rules that
    the dark-text split discards. Each expected non-space glyph needs at
    least one Otsu ink pixel in its unexpanded box (floor/ceil raster bounds).
    Empty spaces are omitted by the caller. This checks spatial agreement,
    not glyph identity or reading accuracy.
    """
    from scipy.ndimage import label
    import math
    ink, threshold = otsu_mask(image)
    explained = np.zeros_like(ink)
    missing = 0
    h,w = ink.shape
    for x0,y0,x1,y1 in boxes:
        left,top = max(0,math.floor(x0)),max(0,math.floor(y0))
        right,bottom = min(w,math.ceil(x1)),min(h,math.ceil(y1))
        if right <= left or bottom <= top or not ink[top:bottom,left:right].any():
            missing += 1
        explained[max(0,top-margin):min(h,bottom+margin),
                  max(0,left-margin):min(w,right+margin)] = True
    structure = np.ones((3,3),dtype=bool)
    components,n = label(ink, structure)
    area = np.bincount(components.ravel(), minlength=n+1)
    covered = np.bincount(components[ink & explained], minlength=n+1)
    bad = int(np.count_nonzero((area[1:] >= noise_area) &
              (covered[1:] < containment*area[1:])))
    residual,nres = label(ink & ~explained, structure)
    residual_area = np.bincount(residual.ravel(), minlength=nres+1)
    residual_count = int(np.count_nonzero(residual_area[1:] >= noise_area))
    from PIL import Image
    outside = np.asarray(image.convert('L')).copy()
    outside[explained] = 255
    faint, faint_threshold = otsu_mask(Image.fromarray(outside))
    faint &= outside <= 245
    faint_labels,nfaint = label(faint, structure)
    faint_area = np.bincount(faint_labels.ravel(), minlength=nfaint+1)
    faint_count = int(np.count_nonzero(faint_area[1:] >= noise_area))
    return dict(unexplained_ink=bool(bad or residual_count or faint_count),missing_ink=bool(missing),
                ink_component_count=int(np.count_nonzero(area[1:] >= noise_area)),
                unexplained_component_count=bad,unexplained_residual_count=residual_count,
                unexplained_faint_count=faint_count,ink_faint_otsu_threshold=faint_threshold,
                missing_ink_char_count=missing,ink_otsu_threshold=threshold)


def ink_diagnostics(image, expected):
    """Expected bbox is crop-local char union; compare edge offsets / union W,H.

    Search the entire padded crop, so adjacent-line intrusion is measurable. Threshold 200
    is deliberately conservative on clean native renders; scan use is diagnostic only.
    """
    a = np.asarray(image.convert('L'))
    mask = a < 200
    yy, xx = np.nonzero(mask)
    if not len(xx):
        return {'ink_bbox': None, 'ink_bbox_error': None, 'multiline_ink': False, 'blank_ink': True}
    box = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
    error = None
    if expected is not None:
        x0, y0, x1, y1 = expected
        error = max(abs(box[0]-x0)/max(1,x1-x0), abs(box[2]-x1)/max(1,x1-x0),
                    abs(box[1]-y0)/max(1,y1-y0), abs(box[3]-y1)/max(1,y1-y0))
    # Two substantial ink bands separated by a gap; small accent bands are preserved.
    on = mask.sum(axis=1) >= max(2, .005 * a.shape[1])
    bands, start = [], None
    for i, v in enumerate(list(on) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            bands.append((start, i)); start = None
    big = [(x,y) for x,y in bands if y-x >= max(5, .22 * (box[3]-box[1]))]
    multi = any(big[i+1][0]-big[i][1] >= 3 for i in range(len(big)-1))
    return {'ink_bbox': box, 'ink_bbox_error': error, 'multiline_ink': multi, 'blank_ink': False}


def admit(row, seen=None, lexicon=None, neighbours=()):
    # Replays preserve the original even when called on an already-admitted row.
    raw = row.setdefault('text_raw', row['text'])
    text = row['text'] = normalize_label(raw)
    row['label_policy'] = LABEL_POLICY
    if 'features' in row:
        row['features'] = features(text)
    reasons = []
    def fail(name, condition):
        if condition:
            reasons.append(name)
    fail('pua', any(0xE000 <= ord(c) <= 0xF8FF for c in text))
    fail('control', any(ord(c) < 32 or 0x7F <= ord(c) <= 0x9F for c in raw))
    fail('replacement', '\ufffd' in text)
    fail('tounicode_residue', bool(RESIDUE.search(text)))
    fail('ligature_artifact', any(0xFB00 <= ord(c) <= 0xFB06 for c in text))
    fail('letter_run', any(len(s) > 40 for s in re.findall(r'[^\W\d_]+', text)))
    rate = dictionary_rate(text, lexicon) if lexicon else None
    neighbour_rates = [dictionary_rate(normalize_label(t), lexicon) for t in neighbours
                       if len(normalize_label(t).split()) >= 3] if lexicon else []
    fail('dictionary_collapse', rate is not None and len(text) >= 25 and rate < .15
         and bool(neighbour_rates) and median(neighbour_rates) >= .6)
    x0, y0, x1, y1 = row['bbox_pixel']
    h, w = y1-y0, x1-x0
    fail('crop_height', not 8 <= h <= 120)
    fail('aspect_ratio', w / max(1, h) < 2)
    for name in ('overlapping_lines', 'rotated_text', 'multiline_ink', 'invalid_char_geometry', 'blank_ink',
                 'unexplained_ink', 'missing_ink'):
        fail(name, row.get(name, False))
    # Replay the geometric guard as well as the assembler's flag. Candidate
    # gutters lack enough support to split lines, but cannot permit a merge.
    # Only explicitly glyph-continuous full-width baselines receive an exemption.
    box = row.get('bbox_pdf')
    gutters = row.get('column_candidate_gutters_pdf', []) + row.get('column_gutters_pdf', [])
    spans = row.get('spanning_gutters_pdf', [])
    fail('cross_column', row.get('cross_column', False) or bool(box and any(
        box[0] < g[0] and box[2] > g[1] and g not in spans for g in gutters)))
    fail('ink_bbox_mismatch', row.get('ink_bbox_error') is not None and row['ink_bbox_error'] > .25)
    fail('no_text', not text.strip())
    visible = [c for c in text if not c.isspace()]
    letters = sum(ud.category(c).startswith('L') for c in visible)
    fail('fragment_short', bool(visible) and len(visible) < 5)
    fail('fragment_no_letters', bool(visible) and letters == 0)
    fail('fragment_symbol_dominated', bool(visible) and letters/max(1,len(visible)) < .3)
    fail('missing_baseline_neighbour', row.get('missing_baseline_neighbour', False))
    fail('label_spacing_gap', row.get('label_spacing_gap', False))
    # Spatial character membership is a raw-source check. LABEL normalization
    # must not hide an omitted character or make a matching crop fail spuriously.
    fail('crop_text_mismatch', 'crop_text' in row and row['crop_text'] != raw)
    key = duplicate_key(text) if text.strip() else None
    fail('near_duplicate', seen is not None and key is not None and key in seen)
    # Rejected first occurrences do not suppress later geometrically usable occurrences.
    if seen is not None and key is not None and not reasons:
        seen.add(key)
    row.update(admitted=not reasons, reject_reasons=reasons, text_hash=key,
               short_line=len(text.split()) < 3, dictionary_word_rate=rate)
    return row
