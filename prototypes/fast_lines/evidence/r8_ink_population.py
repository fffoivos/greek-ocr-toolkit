"""Frozen-input M35 calibration audit. No calibration or source-policy change."""
import copy
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from ..shared import ink_faintness as faint, detector
from ..shared.contracts import bbox
from ..shared.timing import dump
from ..stack import pipeline as sp
from .r8_ink_support import capture
from .r8_frame_parts import ROOT, BASE, MANIFEST

PAGE = 's2-0ce9d1025b3f23c7119e-p00001'
I1 = BASE.parent


def run():
    out=ROOT/'population';out.mkdir(parents=True,exist_ok=False)
    row=next(x for x in json.loads(MANIFEST.read_text())['pages'] if x['page']==PAGE)
    gray=cv2.imread(row['path'],0)
    detector.MODEL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
    original=sp.relative_faintness;calls=[]
    def traced(g,items,**kw):
        r=original(g,items,detail=True,**kw)
        calls.append(dict(stage='faintness',items=copy.deepcopy(items),result=copy.deepcopy(r)))
        return r
    sp.relative_faintness=traced
    try:result=sp.Stack()(row['path'])
    finally:sp.relative_faintness=original
    assert result['items']==json.loads((BASE/f'{PAGE}.json').read_text())['items']
    dump(out/'fresh-calls.json',calls)
    sources={
        'cb4d6b4':I1/'source-audit'/f'{PAGE}.json',
        '3b09d57':I1/'candidate-trace/source-audit'/f'{PAGE}.json'}
    reports=[]
    frozen=[]
    for tag,path in sources.items():
        trace=json.loads(path.read_text())
        call=next(c for c in trace['actual_calls'] if c['stage']=='faintness')
        items=call['items'];prior=call['result']
        r,loc=capture(faint.analyze,gray,items,detail=True,require_reference=True)
        assert r['reference']==prior['reference'] and r['suppress_indices']==prior['suppress_indices']
        if tag=='3b09d57':assert r['reference']==calls[0]['result']['reference']
        pool=[g for region in r['calibration'] for g in region['components'] if g['body']]
        midpoint=float(np.median([g['core'] for g in pool]));records=[];sheets=[]
        for sample_index,(index,q) in enumerate(loc['samples']):
            cs,rawloc=capture(faint.components,gray,q,r['height'],route='localized')
            assert cs==next(z['components'] for z in r['calibration'] if z['line']==index)
            a,b,c,d=[rawloc[k] for k in ('a','b','c','d')]
            native=gray[b:d,a:c];left=cv2.cvtColor(native,cv2.COLOR_GRAY2BGR);right=left.copy()
            components=[]
            for j,g in enumerate(cs):
                included=bool(g['body']);upper=bool(included and g['core']>=midpoint)
                x,y,z,w=np.rint(np.array(g['bbox'])-[a,b,a,b]).astype(int)
                color=(0,170,0) if upper else (220,0,180) if included else (0,140,255)
                cv2.rectangle(right,(x,y),(z,w),color,1)
                components.append(dict(index=j,**g,admitted_body=included,stronger_half=upper,absolute_deviation_from_core=abs(g['core']-r['reference']['core']) if included else None))
            source=items[index].get('source_ids');title=f'{tag} census {index} sources {source} strip {sample_index}'
            panel=np.hstack([left,right]);bar=np.full((32,panel.shape[1],3),255,np.uint8)
            cv2.putText(bar,title,(4,21),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            cv2.imwrite(str(out/f'{tag}.strip-{sample_index}.jpg'),np.vstack([bar,panel]))
            np.savez_compressed(out/f'{tag}.strip-{sample_index}.npz',origin=[a,b],labels=rawloc['lab'],support=rawloc['ink'],polygon_mask=rawloc['mask'],core=rawloc['core_contrast'],paper=rawloc['paper'])
            slow,sloc=capture(faint.components,gray,q,r['height'],route='slow')
            noisediff=int(np.count_nonzero(rawloc['ink']!=sloc['ink']))
            records.append(dict(sample=sample_index,index=index,source_ids=source,polygon=items[index]['polygon'],strip=q['polygon'],origin=[a,b],bounds=[a,b,c,d],operator='localized, native, scalar median paper / closing core; actual polygon intersection',scout=r['scout']['regions'][index],components=components,body_count=sum(x['body'] for x in cs),stronger_half_count=sum(x['stronger_half'] for x in components),slow_components=slow,slow_support_different_pixels=noisediff))
        # Dense comparison observes the SAME strip population. It is not a
        # substitute for the localized estimator or for the full-page census.
        slow=faint.render(gray,[q for _,q in loc['samples']],height=r['height'],route='slow')
        leave_one_out=[]
        for sample in records:
            calibration=[z for z in r['calibration'] if z['line']!=sample['index']]
            ref=faint.reference(calibration);regions=copy.deepcopy(r['regions']);faint.classify(regions,ref)
            leave_one_out.append(dict(omitted_index=sample['index'],source_ids=sample['source_ids'],reference=ref,drop_indices=[z['line'] for z in regions if z['drop']]))
        ordered=sorted(range(len(items)),key=lambda i:r['scout']['regions'][i]['core'])
        report=dict(tag=tag,input=row,trace=str(path.resolve()),trace_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),census=items,height=r['height'],scout_order=[dict(index=i,source_ids=items[i].get('source_ids'),core=r['scout']['regions'][i]['core']) for i in ordered],calibration_indices=[x['index'] for x in records],reference=r['reference'],pool_median=midpoint,samples=records,slow_same_strips_reference=slow['reference'],slow_same_strips=slow,regions=r['regions'],drop_indices=r['suppress_indices'],leave_one_strip_out=leave_one_out,source_validity='not established by photometry, body filter, or stronger-half membership')
        dump(out/f'{tag}.json',report);reports.append(dict(tag=tag,reference=r['reference'],samples=[{k:s[k] for k in ('index','source_ids','body_count','stronger_half_count','slow_support_different_pixels')} for s in records],slow_reference=slow['reference']))
        frozen.append((tag,r))
    # Pure sensitivity: frozen per-candidate components under both frozen
    # references. Neither reference is selected or passed to production.
    sensitivity=[]
    for tag,r in frozen:
        for ref_tag,rr in frozen:
            regions=copy.deepcopy(r['regions']);faint.classify(regions,rr['reference'])
            sensitivity.append(dict(census=tag,reference_population=ref_tag,drop_indices=[z['line'] for z in regions if z['drop']]))
    dump(out/'summary.json',reports);dump(out/'frozen-sensitivity.json',sensitivity)
    print(json.dumps(reports,indent=2))


if __name__=='__main__':run()
