"""Double-line flag on the 44 real fixtures vs docs/records/glyphs/glyphs_fixture_labels.json (provisional, in-sample threshold)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from PIL import Image
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import skew_line
labels = json.loads((ROOT / 'docs/records/glyphs/glyphs_fixture_labels.json').read_text())
res = {}
for kind in ('double', 'single', 'unscored_partial'):
    for n in labels[kind]:
        s = skew_line(line_glyphs(Image.open(ROOT / 'tests/fixtures/o4d_lines' / f'{n}.png')))
        res[n] = (kind, s.double_line, s.second.ratio if s.second else None)
d = [v for v in res.values() if v[0] == 'double']; s1 = [v for v in res.values() if v[0] == 'single']; p = [v for v in res.values() if v[0] == 'unscored_partial']
print('double flagged %d/%d | single flagged %d/%d | partial flagged %d/%d | all flagged %d/44' % (sum(v[1] for v in d), len(d), sum(v[1] for v in s1), len(s1), sum(v[1] for v in p), len(p), sum(v[1] for v in res.values())))
print({n: v for n, v in res.items() if (v[0] == 'double') != v[1] and v[0] != 'unscored_partial'})
