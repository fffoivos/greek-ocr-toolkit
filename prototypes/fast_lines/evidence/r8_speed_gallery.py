"""Fresh native control crops and explicitly inherited pilot review links."""
import html
import json
from pathlib import Path
import cv2
import numpy as np
from r8_speed_acceptance import OUT,ROOT,BASE,PRIOR,dump,sha


def run():
    pages=json.loads((ROOT/'R8-01b/inputs-208.json').read_text())['pages']
    rows={r['page']:r for r in pages}
    controls=[('an-466cffad2cba-p000277',0,'Accepted πό and accent; trailing horizontal mark already outside.'),
        ('an-7792a3301892-p000138',40,'Terminal punctuation and left-edge support preserved.'),
        ('an-c8b96a901917-p000036',87,'Isolated right tick retained; identity remains uncertain.'),
        ('an-9ea1564fcf4f-p000202',131,'Prior-row bottoms excluded by accepted M33 narrowing.'),
        ('an-dbd045ccd84c-p000359',25,'Preceding whole row excluded by accepted M33 narrowing.'),
        ('an-d3237d690aa0-p000138',23,'Preceding letter bottoms excluded.'),
        ('s2-86865c33eef5932c013b-p00005',58,'Residual row40 retained; right curl still clipped.'),
        ('s2-86865c33eef5932c013b-p00005',57,'Residual row41 retained; right curl still clipped.'),
        ('s2-86865c33eef5932c013b-p00007',70,'Existing type-slot0 recovery, not a new row.'),
        ('s2-86865c33eef5932c013b-p00007',71,'Existing type-slot2 recovery, not a new row.')]
    target=OUT/'controls';target.mkdir(exist_ok=True);records=[];cards=[]
    for page,index,note in controls:
        r=rows[page];gray=cv2.imread(r['path'],0)
        items=json.loads((OUT/'runtime'/f'{page}.json').read_text())['items']
        old=json.loads((BASE/'runtime'/f'{page}.json').read_text())['items'];assert items==old
        q=items[index];poly=np.asarray(q['polygon']);lo=np.floor(poly.min(0)).astype(int);hi=np.ceil(poly.max(0)).astype(int)
        a,b=np.maximum(0,lo-[60,70]);c,d=np.minimum(gray.shape[::-1],hi+[60,70])
        raw=gray[b:d,a:c];draw=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR)
        cv2.polylines(draw,[np.rint(poly-[a,b]).astype(np.int32)],True,(0,150,0),1)
        mask=np.zeros(raw.shape,np.uint8);cv2.fillPoly(mask,[np.rint(poly-[a,b]).astype(np.int32)],1)
        cut=np.where(mask,raw,255).astype(np.uint8)
        stem=f'{page}-{index}'
        cv2.imwrite(str(target/f'{stem}-context.png'),np.vstack([cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR),draw]))
        cv2.imwrite(str(target/f'{stem}-native.png'),cut)
        # Display normalization only, never a claimed font-guide dewarp.
        scale=min(1,1400/cut.shape[1]);cv2.imwrite(str(target/f'{stem}-normalized.png'),cv2.resize(cut,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA))
        rec=dict(page=page,index=index,item=q,original_input_sha256=r['sha256'],bounds=[int(a),int(b),int(c),int(d)],
            output_sha256=sha(OUT/'runtime'/f'{page}.json'),items_exact=True,observation=note,
            native=f'controls/{stem}-native.png',context=f'controls/{stem}-context.png',normalized=f'controls/{stem}-normalized.png')
        records.append(rec);cards.append(f'<figure><figcaption>{page} #{index}: {html.escape(note)}</figcaption><img loading="lazy" src="{rec["context"]}"><p><a href="{rec["native"]}">Masked native</a> · <a href="{rec["normalized"]}">Display normalized</a></p></figure>')
    dump(OUT/'NATIVE_CONTROLS.json',records)
    pilot=json.loads((BASE/'pilot-review/pilot-pages.json').read_text());marks=json.loads((BASE/'pilot-review/pilot-marks.json').read_text())
    assert len(pilot)==23 and len(marks)==127
    bindings=[]
    for r in pilot:
        p=r['page'];assert json.loads((BASE/'runtime'/f'{p}.json').read_text())['items']==json.loads((OUT/'runtime'/f'{p}.json').read_text())['items']
        images=list((BASE/'pilot-review/marks').glob(p+'*.png'))+list((BASE/'pilot-review/pages').glob(p+'*.png'))
        bindings.append(dict(page=p,input_sha256=rows[p]['sha256'],candidate_sha256=sha(OUT/'runtime'/f'{p}.json'),
            prior_record=r,inherited_images={str(x):sha(x) for x in images},status='Source/input/output matched inherited physical review; no claim of fresh adjudication of every mark. All affected recorded non-clock field/ink evidence separately exact.'))
    dump(OUT/'PILOT_REUSE.json',dict(pages=bindings,marks=127,pilot_marks_sha256=sha(BASE/'pilot-review/pilot-marks.json'),
        baseline_runtime_identity='5961754 runtime equals23ee49c; this candidate changes computations, exact outputs/evidence verified afresh.'))
    links=['<li><a href="../R8-03-i2/rows/s2-86865c33eef5932c013b-p00005-row-5.png">P5 row5 remains unmatched: inherited native context</a></li>']
    for r in pilot:
        p=r['page'];links.append(f'<li>{p}: '+ ' · '.join(f'<a href="../R8-03-i1/pilot-review/{x}">native reference context {i+1}</a>' for i,x in enumerate(r['images']))+'</li>')
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R8-04 i1 speed and preservation</title><style>body{font:16px system-ui;max-width:1500px;margin:2em auto;padding:0 1em}img{max-width:100%}figure{margin:2em 0}li{margin:.5em}</style><h1>R8-04 i1 — work removed, G4 partial</h1><p>All208 retained-item exports, exclusions and recorded non-clock feature decisions match5961754. Fresh native controls below use candidate polygons. No geometry or ink-source fix is claimed. Masked/normalized images show retained output only. Old rejected material is linked only as labelled historical evidence.</p><p><a href="ACCEPTANCE.json">208 comparison</a> · <a href="TIMING.md">Timing</a> · <a href="OPERATION_DELTA.json">Work counters</a> · <a href="COMMENTS.json">104 comments</a> · <a href="ROWS.json">256 marks</a> · <a href="PILOT_REUSE.json">23/127 inherited review binding</a></p><h2>Fresh native preservation controls</h2>'+''.join(cards)+'<h2>Unchanged pilot evidence, explicitly reused</h2><ul>'+''.join(links)+'</ul><p>No changed native crop is omitted: the fresh208 comparison found none. Equality preserves known failures. Full clean-page qualification is unfinished; raw screening strips are in clean-review/.</p>')
    print('10 native controls;23pilot/127mark inherited bindings')


if __name__=='__main__':run()
