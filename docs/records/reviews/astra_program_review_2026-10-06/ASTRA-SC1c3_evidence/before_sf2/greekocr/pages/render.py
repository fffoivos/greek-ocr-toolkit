"""Q2 review images; discounted candidates are never drawn."""
import numpy as np
from PIL import Image, ImageDraw
from .lines import _extract

COLORS = [(204, 44, 58), (26, 118, 180), (25, 143, 92), (159, 65, 178)]


CURVE_SAMPLE_STEP_PX = 3  # source page pixels: limit overlay vertices while retaining the fitted curve.
RIBBON_ALPHA = 32  # 8-bit opacity: show the extraction ribbon without hiding original ink.
GUIDE_ALPHA = 220  # 8-bit opacity: keep guide strokes legible over the scan.
ACCENT_DASH_PERIOD_SAMPLES = 4  # curve samples: distinguish upper-mark guides with a repeated dash.
ACCENT_DASH_LENGTH_SAMPLES = 2  # curve samples: leave a visible gap between accent-guide dashes.
GUIDE_EMPHASIS_PX = 2  # source page pixels: emphasize baselines and dashed accent guides.
STRIP_XHEIGHT_PX = 32  # output pixels per x-height: align all strips at the same review scale.
SHEET_MIN_STRIP_WIDTH_PX = 400  # output page pixels: leave enough width for a small strip and its labels.
SHEET_COLUMN_MARGIN_PX = 70  # output page pixels: separate labels from the next column of strips.
SHEET_MAX_ROWS = 300  # output row count: keep the contact sheet below JPEG's dimension limit.
SHEET_ROW_HEIGHT_PX = 140  # output page pixels at 32 pixels/x-height: reserve a 128-pixel strip and spacing.
SHEET_STRIP_LEFT_PX = 60  # output page pixels: keep the line/column label outside the recognition strip.
SHEET_LABEL_LEFT_PX = 4  # output page pixels: inset labels from the sheet's left edge.
SHEET_LABEL_TOP_PX = 50  # output page pixels: place labels beside the strip's body band.
SHEET_RULE_TOP_PX = 134  # output page pixels: draw separators below each strip, clear of its pixels.


def render_lines(page, result):
    overlay = Image.new('RGBA', page.size)
    d = ImageDraw.Draw(overlay)
    for i, line in enumerate(result.lines):
        if line.discounted is not None:
            continue
        x = np.arange(line.x0, line.x1)
        indices = np.unique(np.r_[np.arange(0, len(x), CURVE_SAMPLE_STEP_PX), len(x) - 1])
        color = COLORS[i % len(COLORS)]
        top = [(int(x[k]), float(line.top[k])) for k in indices]
        bottom = [(int(x[k]), float(line.bottom[k])) for k in indices]
        d.polygon(top + bottom[::-1], fill=color + (RIBBON_ALPHA,))
        for curve in ('top', 'bottom', 'font_top', 'meanline', 'baseline', 'font_bottom', 'accent_bottom', 'accent_top'):
            points = [(int(x[k]), float(getattr(line, curve)[k])) for k in indices]
            if len(points) < 2:
                continue
            guide_colors = dict(baseline=(220,30,30), meanline=(0,110,235), font_top=(0,150,90),
                                font_bottom=(150,40,190), accent_bottom=(230,120,0), accent_top=(20,170,180))
            stroke = guide_colors.get(curve,(30,30,30))+(GUIDE_ALPHA,)
            if curve.startswith('accent'):
                for start in range(0,len(points)-1,ACCENT_DASH_PERIOD_SAMPLES):
                    d.line(points[start:start+ACCENT_DASH_LENGTH_SAMPLES],fill=stroke,width=GUIDE_EMPHASIS_PX)
            else:
                d.line(points,fill=stroke,width=GUIDE_EMPHASIS_PX if curve=='baseline' else 1)
        d.text((line.x0, float(line.baseline[0]) - line.xheight), str(i), fill=(0, 0, 0, 255))
    lines_image = Image.alpha_composite(page.convert('RGBA'), overlay).convert('RGB')
    active = [(i, line) for i, line in enumerate(result.lines) if line.discounted is None]
    strips = [_extract(result.pixels.gray, line, STRIP_XHEIGHT_PX) for _, line in active]
    # All strips use the same scale and baseline position. Nothing is squeezed
    # to fit the contact sheet; long strips retain their full width.
    width = max([s.width for s in strips] + [SHEET_MIN_STRIP_WIDTH_PX]) + SHEET_COLUMN_MARGIN_PX
    # JPEG has a 65500-pixel dimension limit. Wrap long tables into labelled
    # consecutive stacks, top-to-bottom then left-to-right, without rescaling.
    rows = min(SHEET_MAX_ROWS, max(1, len(strips)))
    columns = max(1, int(np.ceil(len(strips) / rows)))
    sheet = Image.new('RGB', (columns * width, rows * SHEET_ROW_HEIGHT_PX), 'white'); sd = ImageDraw.Draw(sheet)
    for position, ((i, line), strip) in enumerate(zip(active, strips)):
        x, y = (position // rows) * width, (position % rows) * SHEET_ROW_HEIGHT_PX
        sheet.paste(strip, (x + SHEET_STRIP_LEFT_PX, y))
        sd.text((x + SHEET_LABEL_LEFT_PX, y + SHEET_LABEL_TOP_PX), f'{i}\nc{line.column}', fill=COLORS[i % len(COLORS)])
        sd.line([(x, y + SHEET_RULE_TOP_PX), (x + width, y + SHEET_RULE_TOP_PX)], fill=(210, 210, 210))
    return dict(lines_image=lines_image, unrolled_image=sheet)
