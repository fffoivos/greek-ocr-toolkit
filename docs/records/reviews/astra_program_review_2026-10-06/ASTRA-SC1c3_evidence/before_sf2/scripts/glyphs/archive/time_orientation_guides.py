"""Time production orientation, including table confirmation, on upright sources.

The main detector fit is reused only after checking its source hash. Orientation
and all local fits execute normally; timing excludes loading and serialization.
This isolates OrientedPage.orientation_seconds from total delivery time.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys
from time import perf_counter

from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from greekocr.glyphs.oriented_page import oriented_page
from scripts.glyphs.archive.render_orientation_round4 import load_baseline
from scripts.glyphs.archive.evaluate_orientation_guides import save,time_summary
from scripts.glyphs.archive.audit_orientation_guides import compact_word

OUT=ROOT/'.astra/out/orientation_eval'
BASE=ROOT/'.astra/previous_round4_part2'


def main():
    rows=[]
    for path in sorted((ROOT/'.astra/pages').glob('*.png')):
        image=Image.open(path).convert('L');key=path.stem
        expected=json.loads((BASE/f'{key}.checks.json').read_text())['source_sha256']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        segmentation,pieces=load_baseline(BASE,key)
        layout=json.loads((ROOT/'.astra/layout'/f'{key}.json').read_text())
        tables=[(str(c['id']),[v*3 for v in c['box']]) for c in layout['retained']]
        started=perf_counter()
        result=oriented_page(image,tables,use_osd=False,segmentation=segmentation,pieces=pieces)
        elapsed=perf_counter()-started
        # A table-fit memoization must not change any delivered label, frame,
        # box or ownership field from the completed four-turn delivery audit.
        observed=[compact_word(word,image) for word in result.words]
        observed=json.loads(json.dumps(observed,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
        expected_words=json.loads((OUT/'delivery'/f'{key}.json').read_text())['word_records']
        assert observed==expected_words, f'delivery changed after table-fit memoization: {key}'
        rows.append(dict(key=key,orientation_seconds=result.orientation_seconds,
                         delivery_seconds=elapsed,orientation_cw=result.dominant.orientation_cw,
                         delivery_identical_to_full_audit=True))
        print(key,round(result.orientation_seconds,3),round(elapsed,3),flush=True)
        save(OUT/'production-orientation-time.json',dict(
            scope='54 original source rasters, actual oriented_page orientation including table confirmation; no OCR, no fit cache beyond same-frame verified part-2 main segmentation',
            environment=dict(system=platform.system(),release=platform.release(),machine=platform.machine(),python=platform.python_version()),
            source_sha256=hashlib.sha256((ROOT/'greekocr/glyphs/oriented_page.py').read_bytes()).hexdigest(),
            rows=rows,orientation=time_summary([r['orientation_seconds'] for r in rows]),
            delivery=time_summary([r['delivery_seconds'] for r in rows])))


if __name__=='__main__':main()
