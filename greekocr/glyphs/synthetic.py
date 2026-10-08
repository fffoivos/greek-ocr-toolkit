"""Rendered lines with exact per-pixel truth (letter / mark / punctuation / neighbour) for validating the glyph model.

The image is drawn from the real graphemes only. Truth comes from a second, aligned rendering of each grapheme without
its combining marks: pixels of the full grapheme near the stripped body are letter (or punctuation), the rest are marks.
A grapheme whose stripped body does not sit inside its full rendering (some fonts move or reshape the body when a mark
is added) is labelled IGNORE rather than given fabricated truth; so are capitals carrying spacing marks.
Every character drawn — main line and neighbours — is checked against the font first; unsupported text is refused.
All truth maps (classes, letter ids, injected defects, the baseline) go through the same rotation, bend and crop as
the image; letter boxes are taken from the final letter-id map.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import random
import unicodedata as ud
from pathlib import Path
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

from greekocr.types import PathLike

__all__ = ['DEFECTS', 'IGNORE', 'LETTER', 'MARK', 'NEIGHBOUR', 'PUNCT', 'Rendered', 'TruthGlyph', 'UnsupportedText',
           'font_covers', 'font_supports_polytonic', 'render_truth_line', 'usable_fonts']

LETTER, MARK, PUNCT, NEIGHBOUR, IGNORE = 1, 2, 3, 4, 5
DEFECTS = {'fade': 1, 'thin': 2, 'break': 3, 'thick': 4}
PROBE = 'ἀἁάὰᾶἄἅἆᾷῥὑὕῷϊΐῒ᾿῾'


class UnsupportedText(ValueError):
    """The font cannot draw every character of the requested text."""


@dataclass(frozen=True)
class TruthGlyph:
    char: str                                   # NFC grapheme as written
    kind: int                                   # LETTER or PUNCT (marks are pixel truth only)
    box: tuple[int, int, int, int] | None       # final-image bbox of its body pixels; None if none survive the crop
    reliable: bool                              # False: IGNORE truth (unaligned body, or capital with spacing marks)


@dataclass
class Rendered:
    image: Image.Image
    truth: NDArray[np.uint8]                    # per pixel: 0 paper, LETTER, MARK, PUNCT, NEIGHBOUR, IGNORE
    glyphs: list[TruthGlyph]
    glyph_ids: NDArray[np.int32]                # per pixel: 1 + index into glyphs for letter-body pixels
    xh: float
    base_truth: NDArray[np.float64]             # per column: true baseline row (after skew, bend and crop)
    skew_deg: float
    font: str
    defect_kind: NDArray[np.uint8]              # per pixel: DEFECTS code of the injected defect (0 none)
    defect_intensity: NDArray[np.float32]       # per pixel: its intensity 0..1
    second_line: bool = False                   # a full second text line was rendered inside the crop

    @property
    def ink_truth(self) -> NDArray[np.float64]:
        """Per column signed defect intensity over letter pixels (−under, +thick); 0 where no defect."""
        out = np.zeros(self.truth.shape[1])
        on = (self.truth == LETTER) & (self.defect_kind > 0)
        for c in np.nonzero(on.any(axis=0))[0]:
            k = self.defect_kind[on[:, c], c]
            v = self.defect_intensity[on[:, c], c]
            kind = np.bincount(k).argmax()
            out[c] = float(v[k == kind].mean()) * (1 if kind == DEFECTS['thick'] else -1)
        return out


def _base(grapheme: str) -> str:
    return ''.join(ch for ch in ud.normalize('NFD', grapheme) if not ud.combining(ch))


def _mask(font: ImageFont.FreeTypeFont, text: str) -> NDArray[np.bool_]:
    im = Image.new('L', (font.size * 4, font.size * 3), 0)
    ImageDraw.Draw(im).text((font.size, font.size), text, font=font, fill=255)
    return np.asarray(im) > 127


@lru_cache(maxsize=None)
def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=200_000)
def _grapheme_ok(path: str, grapheme: str) -> str:
    """'' if the font draws this grapheme properly, else the reason."""
    if grapheme.isspace():
        return ''
    font = _font(path, 48)
    notdef = _mask(font, '￿')
    full = _mask(font, grapheme)
    if not full.any():
        return f'{grapheme!r} renders empty'
    for ch in grapheme:
        if not ud.combining(ch) and np.array_equal(_mask(font, ch), notdef):
            return f'{ch!r} (U+{ord(ch):04X}) is .notdef'
    if np.array_equal(full, notdef):
        return f'{grapheme!r} is .notdef'
    if _base(grapheme) != grapheme and np.array_equal(full, _mask(font, _base(grapheme))):
        return f'{grapheme!r} drops its marks'
    return ''


def font_covers(path: PathLike, text: str) -> tuple[bool, str]:
    """Every grapheme of `text` renders, differs from .notdef, and keeps its marks."""
    for g in dict.fromkeys(_graphemes(text)):
        why = _grapheme_ok(str(path), g)
        if why:
            return False, why
    return True, 'ok'


def font_supports_polytonic(path: PathLike, size: int = 48) -> tuple[bool, str]:
    """Gate on a fixed polytonic probe (incl. spacing breathings); per-text coverage is enforced at render time."""
    return font_covers(path, PROBE)


def _graphemes(text: str) -> list[str]:
    out: list[str] = []
    for ch in ud.normalize('NFD', text):
        if ud.combining(ch) and out:
            out[-1] += ch
        else:
            out.append(ch)
    return [ud.normalize('NFC', g) for g in out]


def _shift_columns(arr: NDArray, dy: NDArray[np.int64], fill) -> NDArray:
    out = np.full_like(arr, fill)
    for c in range(arr.shape[1]):
        k = int(dy[c])
        if k == 0:
            out[:, c] = arr[:, c]
        elif k > 0:
            out[k:, c] = arr[:-k, c]
        else:
            out[:k, c] = arr[-k:, c]
    return out


def _rotate(arr: NDArray, deg: float, mode: str) -> NDArray:
    if not deg:
        return arr
    im = Image.fromarray(arr.astype(np.int32), 'I') if mode == 'I' else Image.fromarray(arr.astype(np.float32), 'F')
    return np.asarray(im.rotate(deg, resample=Image.NEAREST, fillcolor=0)).astype(arr.dtype)


def render_truth_line(text: str, font_path: PathLike, *, size: int = 40, rng: random.Random | None = None,
                      degrade: bool = True, pad: int | None = None,
                      neighbours: tuple[str, str] | None = None,
                      ink_defects: Sequence[tuple[float, float, str, float]] = (),
                      bend: tuple[str, float, float] | None = None,
                      second_line: str | None = None) -> Rendered:
    """Render `text` with per-pixel truth and an optional randomised scan model (skew ±2°, blur, ink gain, noise).

    neighbours  = (text above, text below) at a random leading; the crop keeps only their intruding tips.
    second_line = text of a full second line rendered below and kept inside the crop (a two-line box).
    ink_defects = (x0, x1 as fractions of the text width, kind, intensity 0..1), kind in fade | thin | break | thick,
                  applied to the clean ink; recorded per pixel in defect_kind / defect_intensity.
    bend        = (side 'left' | 'right', amplitude in x-heights (+ down), fraction of the text span): the line bends
                  quadratically over that end, as at a curled page edge.
    Raises UnsupportedText if the font cannot draw every character requested.
    """
    for t in (text, *(neighbours or ()), *([second_line] if second_line else [])):
        ok, why = font_covers(font_path, t)
        if not ok:
            raise UnsupportedText(f'{Path(font_path).name}: {why}')
    rng = rng or random.Random(0)
    font = _font(str(font_path), size)
    pad = pad if pad is not None else size // 2
    # width follows the main line (and a requested second line), like a box cut around it; neighbours are clipped
    width = int(max(font.getlength(text), font.getlength(second_line or ''))) + 2 * pad + size
    height = int(size * (3.4 if second_line else 1.9)) + 2 * pad
    asc, _ = font.getmetrics()
    y = pad + size * .25
    ink = np.zeros((height, width), bool)
    truth = np.zeros((height, width), np.uint8)
    gid = np.zeros((height, width), np.int32)
    glyph_meta: list[tuple[str, int, bool]] = []
    prefix = ''
    for g in _graphemes(text):
        x = pad + font.getlength(prefix)
        prefix += g
        if g.isspace():
            continue
        b = _base(g)
        full_im, base_im = Image.new('L', (width, height), 0), Image.new('L', (width, height), 0)
        ImageDraw.Draw(full_im).text((x, y), g, font=font, fill=255)
        ImageDraw.Draw(base_im).text((x, y), b, font=font, fill=255)
        full, base = np.asarray(full_im) > 127, np.asarray(base_im) > 127
        if not full.any():
            continue
        ink |= full
        is_letter = b.isalpha()
        near_base = ndi.binary_dilation(base, iterations=1) & full
        aligned = (base & ~ndi.binary_dilation(full, iterations=1)).sum() <= .02 * max(1, base.sum())
        reliable = aligned and not (b.isupper() and g != b)
        if not reliable:
            truth[full] = IGNORE
        else:
            truth[full & ~near_base & (truth == 0)] = MARK
            truth[near_base] = LETTER if is_letter else PUNCT
        if is_letter:
            gid[near_base & (gid == 0)] = len(glyph_meta) + 1
        glyph_meta.append((g, LETTER if is_letter else PUNCT, reliable))
    main = ink.copy()
    lines = list(zip(neighbours, (-1, 1))) if neighbours else []
    if second_line:
        lines.append((second_line, 0))
    for text_n, sign in lines:
        im = Image.new('L', (width, height), 0)
        lead = size * rng.uniform(1.05, 1.45) if sign else size * rng.uniform(1.15, 1.4)
        ImageDraw.Draw(im).text((pad + rng.uniform(-size, size) if sign else pad, y + (sign or 1) * lead), text_n,
                                font=font, fill=255)
        other = (np.asarray(im) > 127) & ~main
        ink |= other
        truth[other & (truth == 0)] = NEIGHBOUR
    xh_mask = _mask(font, 'ν')  # Greek x-height letter; some GFS fonts lack Latin
    ys = np.nonzero(xh_mask.any(axis=1))[0]
    xh = float(ys.max() - ys.min() + 1)
    baseline = y + asc
    # injected defects on the clean ink, recorded per pixel
    ink8 = ink.astype(np.uint8) * 255
    dkind = np.zeros((height, width), np.uint8)
    dint = np.zeros((height, width), np.float32)
    if ink_defects:
        cols = np.nonzero(main.any(axis=0))[0]
        left, span = int(cols[0]), int(cols[-1] - cols[0] + 1)
        drng = np.random.default_rng(rng.randrange(1 << 30))
        for f0, f1, kind, inten in ink_defects:
            if kind not in DEFECTS:
                raise ValueError(f'unknown ink defect {kind!r}')
            a, b = left + int(f0 * span), left + int(f1 * span)
            region = ink8[:, a:b] > 0
            if kind == 'fade':
                ink8[:, a:b] = (ink8[:, a:b] * (1 - .8 * inten)).astype(np.uint8)
            elif kind == 'thin':
                ink8[:, a:b] = ndi.binary_erosion(region, iterations=max(1, round(3 * inten))) * 255
            elif kind == 'break':
                holes = ndi.binary_dilation(drng.random(region.shape) < .04 * inten, iterations=max(1, size // 18))
                ink8[:, a:b] = (region & ~holes) * 255
            else:
                grown = ndi.binary_dilation(region, iterations=max(1, round(1 + 2.5 * inten)))
                ink8[:, a:b] = grown * 255
                region = grown
            dkind[:, a:b][region] = DEFECTS[kind]
            dint[:, a:b][region] = inten
    skew = rng.uniform(-2.0, 2.0) if degrade else 0.0
    ink_im = Image.fromarray(ink8).rotate(skew, resample=Image.BICUBIC, fillcolor=0)
    truth, gid = _rotate(truth, skew, 'I'), _rotate(gid, skew, 'I')
    dkind, dint = _rotate(dkind, skew, 'I'), _rotate(dint, skew, 'F')
    a = np.deg2rad(skew)
    cx0, cy0 = width / 2, height / 2
    dyb = baseline - cy0
    base_truth = cy0 - (np.arange(width) - cx0 - dyb * np.sin(a)) * np.tan(a) + dyb * np.cos(a)
    if degrade:
        ink_im = ink_im.filter(ImageFilter.GaussianBlur(rng.uniform(.3, 1.4)))
        arr = np.clip(np.asarray(ink_im, np.float64) * rng.uniform(.75, 1.4), 0, 255)   # gain < 1 faint, > 1 heavy
        paper, inkgray = rng.uniform(200, 245), rng.uniform(10, 70)
        gray = paper - (paper - inkgray) * arr / 255
        gray += np.random.default_rng(rng.randrange(1 << 30)).normal(0, rng.uniform(2, 9), gray.shape)
    else:
        gray = 255 - np.asarray(ink_im, np.float64)
    if bend:
        side, amp, frac = bend
        cols = np.nonzero(np.isin(truth, (LETTER, MARK, PUNCT, IGNORE)).any(axis=0))[0]
        lo, hi = int(cols[0]), int(cols[-1])
        L = max(1, int(frac * (hi - lo)))
        xs = np.arange(width)
        d = np.clip((lo + L - xs) if side == 'left' else (xs - (hi - L)), 0, None) / L
        dy = np.round(amp * xh * d ** 2).astype(np.int64)
        gray = _shift_columns(gray, dy, float(np.median(gray)))
        truth, gid = _shift_columns(truth, dy, 0), _shift_columns(gid, dy, 0)
        dkind, dint = _shift_columns(dkind, dy, 0), _shift_columns(dint, dy, 0)
        base_truth = base_truth + dy
    if neighbours or second_line:
        # cut like a page-line cutter: the main line's ink extent (plus the second line if requested) + a small margin
        keep = (LETTER, MARK, PUNCT, IGNORE)
        rows = np.nonzero(np.isin(truth, keep).any(axis=1))[0]
        r0 = max(0, int(rows[0] - rng.uniform(.1, .6) * xh))
        last = rows[-1]
        if second_line:
            last = max(last, int(np.nonzero((truth == NEIGHBOUR).any(axis=1))[0].max()))
        r1 = min(height, int(last + 1 + rng.uniform(.1, .6) * xh))
        gray, truth, gid = gray[r0:r1], truth[r0:r1], gid[r0:r1]
        dkind, dint = dkind[r0:r1], dint[r0:r1]
        base_truth = base_truth - r0
    glyphs = []
    for k, (g, kind, reliable) in enumerate(glyph_meta):
        ys_, xs_ = np.nonzero(gid == k + 1)
        box = (int(xs_.min()), int(ys_.min()), int(xs_.max()) + 1, int(ys_.max()) + 1) if xs_.size else None
        glyphs.append(TruthGlyph(g, kind, box, reliable))
    image = Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8), 'L')
    return Rendered(image=image, truth=truth, glyphs=glyphs, glyph_ids=gid, xh=xh, base_truth=base_truth,
                    skew_deg=skew, font=Path(font_path).name, defect_kind=dkind, defect_intensity=dint,
                    second_line=bool(second_line))


def usable_fonts(paths: Sequence[PathLike]) -> tuple[list[Path], dict[str, str]]:
    ok: list[Path] = []
    rejected: dict[str, str] = {}
    for p in paths:
        try:
            good, why = font_supports_polytonic(p)
        except OSError as exc:
            good, why = False, f'unreadable: {exc}'
        (ok.append(Path(p)) if good else rejected.__setitem__(Path(p).name, why))
    return ok, rejected
