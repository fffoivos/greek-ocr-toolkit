"""Shared setup for the glyph evaluation scripts: fonts, text, and renders whose characters the font covers."""
import glob, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from greekocr.glyphs.synthetic import UnsupportedText, font_covers, render_truth_line, usable_fonts  # noqa: E402

FONT_DIR = Path.home() / 'Projects/greek-page-ocr/assets/fonts'


def setup(data_dir):
    fonts, rejected = usable_fonts(sorted(glob.glob(str(FONT_DIR / '*.[ot]tf'))))
    fonts = [f for f in fonts if 'Italic' not in f.name and 'Mono' not in f.name]
    texts = [json.loads(l)['text'] for l in open(Path(data_dir) / 'poly_lines.jsonl')]
    return fonts, texts


def pick_text(rng, texts, font, n=70):
    """A random line (truncated to n chars) that the font fully covers; resamples on unsupported characters."""
    for _ in range(200):
        t = rng.choice(texts)[:n]
        if font_covers(font, t)[0]:
            return t
    raise UnsupportedText(f'{font.name}: no covered text found')


def render(rng, fonts, texts, seed, *, neighbours_p=0.0, second_p=0.0, **kw):
    font = rng.choice(fonts)
    t = pick_text(rng, texts, font)
    nb = (pick_text(rng, texts, font, 80), pick_text(rng, texts, font, 80)) if rng.random() < neighbours_p else None
    second = pick_text(rng, texts, font) if rng.random() < second_p else None
    return render_truth_line(t, font, size=rng.randint(26, 46), rng=random.Random(seed), neighbours=nb,
                             second_line=second, **kw)
