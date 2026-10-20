"""Draw, on a page image, every text-layer box's main line per column segment as found by the crop-level tools
(underline = the fitted baseline). Usage: draw_page_lines.py PAGE.png BOXES.json OUT.jpg [WIDTH]"""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.columns import column_segments                         # noqa: E402
from greekocr.glyphs.components import line_glyphs                          # noqa: E402
from greekocr.glyphs.report import needs_prior                              # noqa: E402

page = Image.open(sys.argv[1]).convert('L'); rows = json.load(open(sys.argv[2])); out = sys.argv[3]
width = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
crops = [page.crop(tuple(r['box'])) for r in rows]
# the page's letter height (median over its crops that measure their own) for crops too clipped to measure theirs
own = [line_glyphs(c).band.xh for c in crops if c.height > 20]
prior = float(np.median(own)) if own else None
vis = page.convert('RGB'); d = ImageDraw.Draw(vis)
COL = [(214, 39, 40), (31, 119, 180), (44, 160, 44), (148, 103, 189)]
n = 0
for k, (r, crop) in enumerate(zip(rows, crops)):
    x0, y0 = r['box'][:2]
    kw = {'xh_prior': prior} if prior and needs_prior(line_glyphs(crop)) else {}
    for s in column_segments(crop, **kw):
        if s.glyphs is None:
            continue
        b = s.glyphs.band.bottom
        d.line([(x0 + s.x0 + x, y0 + float(b[x]) + 3) for x in range(0, len(b), 4)], fill=COL[k % 4], width=max(3, page.width // 650))
        n += 1
vis.resize((width, round(vis.height * width / vis.width)), Image.LANCZOS).save(out, quality=72)
print(Path(sys.argv[1]).stem, len(rows), 'boxes →', n, 'lines drawn')
