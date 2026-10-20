"""Offline real-input admission check through the frozen R1 span gate."""
import json
from collections import Counter
from pathlib import Path
from PIL import Image
from scripts.labelfix.clariden.r1_common import rows, sha256, clusters, transfer_record
from scripts.labelfix.clariden.r1_pixels import threshold_image, font_size, plausible_span
from scripts.labelfix.clariden.r2a_prepare import ROOT


def check():
    cfg=json.loads(Path('config/r2a_job.json').read_text())
    source={r['line_id']:r for r in rows(cfg['native'])}
    aligned={r['crop']:r['alignment'] for r in rows(cfg['native_alignments'])}
    slots=list(rows(cfg['manifest'])); byline={}; results={}; failures=[]
    for r in slots:byline.setdefault(r['line_id'],[]).append(r)
    for lid,rr in byline.items():
        line=source[lid]; p=Path(line['crop']).relative_to(ROOT)
        assert sha256(p)==line['crop_sha256']
        alignment,_=transfer_record(line['recogniser_text'],aligned[line['crop']])
        spans=alignment['spans']
        letters=[(c.base,c.start,spans[c.start][3:5]) for c in clusters(line['recogniser_text']) if c.base.isalpha()]
        with Image.open(p) as im:
            binary,_=threshold_image(im);size=font_size(binary,letters)
        for r in rr:
            start=r['slot_id'][1];ok,reason=plausible_span(spans[start][3:5],size)
            if alignment.get('confidence') is None or alignment['confidence']<.5:
                ok=False;reason='line_confidence_missing_or_below_0.5'
            results[tuple(r['slot_id'])]=ok
            if not ok:failures.append(dict(slot_id=r['slot_id'],line_id=lid,reason=reason))
    assert len(results)==cfg['expected_slots']==1572 and not failures,failures
    return dict(slots=len(results),passed=sum(results.values()),failures=failures,polarity=dict(Counter(r['polarity'] for r in slots)),manifest_sha256=sha256(cfg['manifest']),frozen_gate=True,network=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
