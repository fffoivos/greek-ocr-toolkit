"""Rejected M55 caller migration: complete observed support, no centre authority.

Executed only by this evidence command. Revives approved pure frames whose
joined/fragmented units M54 does not assign, so it is NOT the default adapter.
"""
import json
from pathlib import Path
import cv2,numpy as np
from ..stack import pipeline as sp
from ..shared import detector
from ..shared.timing import dump
from .r8_ink_support import BASE,OUT,frame_support,support


def exclude(gray,items,field,height,observation):
    observed_gray,observed_field,h,owned,observed,sampled=observation
    if observed_gray is not gray or field is not observed_field or h!=height:
        raise ValueError('native frame observation does not belong to this call')
    kept=[];removed=[];decisions=[]
    for i,q in enumerate(items):
        p=np.asarray(q['polygon']);x,y=np.maximum(0,np.floor(p.min(0))).astype(int);z,w=np.minimum(gray.shape[::-1],np.ceil(p.max(0)+1)).astype(int)
        if not owned[y:w,x:z].any():kept.append(q);continue
        _,l=support(gray,q,height);a,b,c,d=l['a'],l['b'],l['c'],l['d'];pm=l['mask']>0
        ink=(l['ink']>0)|(observed[b:d,a:c]&pm)
        residual=ink&~owned[b:d,a:c];outside=pm&~sampled[b:d,a:c]
        # The full current support is consumed, including all small and clipped
        # components omitted by M35's record filters. Unobserved domain abstains.
        drop=bool(ink.any() and not residual.any() and not outside.any())
        decisions.append(dict(line=i,source_ids=q.get('source_ids'),support=int(ink.sum()),unresolved=int(residual.sum()),unobserved_domain=int(outside.sum()),drop=drop))
        if drop:removed.append(i)
        else:kept.append(q)
    return dict(items=kept,removed=removed,exclusions=[dict(items[i],removal='recurrent frame') for i in removed],decisions=decisions)


def run():
    out=OUT/'frame-migration-attempt';out.mkdir(parents=True,exist_ok=False)
    detector.MODEL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx');stack=sp.Stack();state=[];records=[]
    render=sp.frame_render;oldexclude=sp.frame_exclude;decision=[]
    def rendering(gray,polygons,h):
        field,owned,observed,sampled,_=frame_support(gray,polygons,h);state[:]=[gray,field,h,owned,observed,sampled];return field
    def excluding(gray,items,field,h):
        result=exclude(gray,items,field,h,state);decision[:]=result['decisions'];return result
    sp.frame_render=rendering;sp.frame_exclude=excluding
    try:
        for row in json.loads((BASE.parent/'R8-01b/inputs-208.json').read_text())['pages']:
            if not row['page'].startswith('an-7792a3301892-'):continue
            p=row['page'];r=stack(row['path']);base=json.loads((BASE/'runtime'/f'{p}.json').read_text())['items'];e=json.loads((BASE/'runtime'/f'{p}.evidence.json').read_text());dump(out/f'{p}.json',r)
            records.append(dict(page=p,before=len(base),after=len(r['items']),frames_before=e['counts']['frames'],frames_after=r['counts']['frames'],decisions=list(decision)));print(p,records[-1]['frames_before'],records[-1]['frames_after'],flush=True)
    finally:sp.frame_render=render;sp.frame_exclude=oldexclude
    dump(out/'results.json',records)
if __name__=='__main__':run()
