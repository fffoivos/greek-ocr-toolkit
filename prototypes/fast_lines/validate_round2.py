"""Validate published Q8 artifacts without running any detector or experiment."""
import json
from collections import Counter

import cv2
import numpy as np

from .round2 import DEST, COMMON, ROOT, active_study, get_baseline
from .shared.manifest import digest
from .shared.timing import dump


def main():
    rows=json.loads((COMMON/'manifest.json').read_text())['pages']
    directory,source=active_study()
    benchmark=json.loads((DEST/'benchmark.json').read_text())
    review=json.loads((ROOT/'docs/research/FAST_LINES_ROUND2_REVIEW.json').read_text())
    assert review['source']==source==benchmark['source']
    assert {r['page'] for r in review['pages']}=={r['page'] for r in rows}
    assert len(benchmark['records'])==3*len(rows)==585
    assert Counter(r['page'] for r in benchmark['records'])==Counter({r['page']:3 for r in rows})
    assert len({(r['page'],r['repetition']) for r in benchmark['records']})==585
    counts=Counter(); artifacts=[]
    for row in rows:
        p=row['page']; before=get_baseline(row)
        data=json.loads((DEST/(p+'.json')).read_text())
        ev=json.loads((DEST/(p+'.evidence.json')).read_text())
        comparison=json.loads((DEST/(p+'.comparison.json')).read_text())
        visual=next(r for r in review['pages'] if r['page']==p)
        assert visual['overview_checked'] and visual['input_sha256']==row['sha256']
        assert visual['changed_line_ids']==[r['line'] for r in ev['changes']]
        assert data['page']==p and data['image_size']==row['image_size'] and data['unit']=='line'
        assert data['items']==json.loads((directory/(p+'.json')).read_text())['items']
        assert data['seconds']>0 and np.isfinite(data['seconds'])
        assert len(comparison['lines'])==len(before)
        changed={c['line']:c for c in ev['changes']}
        expected=[]
        for i,item in enumerate(before):
            if i not in changed:
                expected.append(item)
            else:
                change=changed[i]
                old=np.asarray(item['polygon'],np.float32)
                assert change['old']==item['polygon'] and len(change['new'])==2
                for polygon in change['new']:
                    assert all(cv2.pointPolygonTest(old,tuple(map(float,xy)),True)>=-1e-3 for xy in polygon)
                    expected.append(dict(item,polygon=polygon,source_ids=[i],provenance='verified separator clip'))
        assert expected==data['items'], f'unexplained mutation: {p}'
        for item in data['items']:
            q=np.asarray(item['polygon'],float)
            assert q.ndim==2 and q.shape[1]==2 and len(q)>=3 and np.isfinite(q).all()
            assert (q>=0).all() and (q<=row['image_size']).all()
            assert cv2.contourArea(q.astype(np.float32))>0
            assert item['baseline'] is None and np.isfinite(item['score'])
            assert not item.get('discounted')
        assert digest(DEST/(p+'.jpg'))==visual['output_image_sha256']
        for r in [x for x in benchmark['records'] if x['page']==p]:
            assert r['changes']==len(changed)
            assert r['added_s']>=r['correction_s'] and r['total_s']>=r['baseline_s']
            assert r['added_s']<1
            if not r['candidates']:
                assert r['correction_s']==0
            if row['group']=='agreement':
                assert not r['candidates'] and not changed and before==data['items']
        counts['pages']+=1; counts['source_lines']+=len(before)
        counts['changed_pages']+=bool(changed); counts['changed_lines']+=len(changed)
        counts['agreement_pages']+=row['group']=='agreement'
        artifacts.append(dict(page=p,json_sha256=digest(DEST/(p+'.json')),
                              image_sha256=digest(DEST/(p+'.jpg')),
                              evidence_sha256=digest(DEST/(p+'.evidence.json'))))
    assert counts['pages']==195 and counts['changed_pages']==18 and counts['changed_lines']==308
    assert counts['agreement_pages']==40
    dump(DEST/'validation.json',dict(status='passed',source=source,counts=dict(counts),
         benchmark_sha256=digest(DEST/'benchmark.json'),review_sha256=digest(ROOT/'docs/research/FAST_LINES_ROUND2_REVIEW.json'),
         scope='format, timing completeness, source lineage, exact unchanged items, polygon containment, visual ledger coverage',
         artifacts=artifacts))
    print('PASS:',dict(counts))


if __name__=='__main__':
    main()
