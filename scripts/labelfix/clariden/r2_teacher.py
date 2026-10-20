"""Frozen R1-A full-head export. New lines are aligned by the unchanged L1 Recognizer."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image
import torch
from scripts.labelfix.clariden.r1_common import HEADS, LETTERS, rows, sha256, write_json, write_rows, compose
from scripts.labelfix.clariden.r1_extract import extract_line, window_geometry, window
from scripts.labelfix.clariden.r1_pixels import plausible_span
from scripts.labelfix.clariden.l1_infer import load_reader
from greekocr.labelfix.ctc_align import Recognizer, VENDOR_CODEC

ROLES=('train','validation_reserve','witness','calibration')

TEACHER_SHA='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636'

from scripts.labelfix.clariden.r2_util import atomic_json as write_json

def code_binding():
    paths=[*Path('greekocr/labelfix').glob('*.py'),*Path('greekocr/_vendor/train').glob('*.py'),
           *Path('scripts/labelfix/clariden').glob('r[12]_*.py'),Path('scripts/labelfix/clariden/l1_infer.py')]
    return {str(p):sha256(p) for p in sorted(paths)}


def full_predictions(model,samples,windows,device,batch_size=512):
    result=[]
    with torch.inference_mode():
        for i in range(0,len(samples),batch_size):
            ss=samples[i:i+batch_size]
            grey=torch.from_numpy(np.asarray(windows[i:i+batch_size])).to(device=device,dtype=torch.float32).div_(255)
            masks=torch.as_tensor(np.asarray([s[7][0] for s in ss]),device=device,dtype=torch.float32)
            xx=torch.arange(128,device=device,dtype=torch.float32)[None,:]+.5
            span=((xx>=masks[:,0,None]) & (xx<masks[:,1,None])).float()[:,None,:].expand(-1,64,-1)
            x=torch.stack((grey,span),1).contiguous(memory_format=torch.channels_last)
            pp=[p.float().softmax(1).cpu().numpy() for p in model(x,torch.tensor([s[4] for s in ss],device=device))]
            for j,s in enumerate(ss):
                heads={}; values=[]
                for (h,choices),p in zip(HEADS.items(),pp):
                    order=np.argsort(p[j]);top=int(order[-1]);values.append(top)
                    heads[h]=dict(probabilities={v:float(p[j,k]) for k,v in enumerate(choices)},top=choices[top],
                        top_probability=float(p[j,top]),margin=float(p[j,top]-p[j,order[-2]]))
                result.append(dict(start=int(s[3]),base=LETTERS[s[4]],heads=heads,factors=values,cls=compose(values)))
    return result


def export(line_list,checkpoint,recognizer_checkpoint,out,device='cuda:0',mock=False,slots=None,recognizer_sha256=None):
    torch.set_num_threads(4 if mock else 8)
    if sha256(checkpoint)!=TEACHER_SHA: raise ValueError('teacher is not frozen 3678928-A')
    if recognizer_sha256 is None or sha256(recognizer_checkpoint)!=recognizer_sha256: raise ValueError('recognizer checkpoint binding mismatch')
    lines=list(rows(line_list))
    if not lines: raise ValueError('empty population')
    if mock and len(lines)>64: raise ValueError('Mac limit: 64 lines')
    if not mock and not __import__('os').environ.get('SLURM_JOB_ID'): raise ValueError('new-line pipeline requires Clariden allocation')
    if len({r['line_id'] for r in lines})!=len(lines): raise ValueError('duplicate population line')
    for r in lines:
        if r['role'] not in ROLES: raise ValueError('invalid population role')
        if not r.get('source') or not r.get('doc'): raise ValueError('missing document/source')
        if sha256(r['image'])!=r['crop_sha256']: raise ValueError('crop hash mismatch')
    wanted={tuple(r['slot_id']) for r in rows(slots)} if slots else None
    code=code_binding();binding=dict(teacher_sha256=TEACHER_SHA,recognizer_sha256=recognizer_sha256,
        codec_sha256=sha256(VENDOR_CODEC),code_sha256=code,line_list_sha256=sha256(line_list),
        slot_list_sha256=sha256(slots) if slots else None,mock=mock,calibration_version='uncalibrated-R1-A')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    recognizer=Recognizer(recognizer_checkpoint,device=device,threads=4 if mock else 8)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    model=load_reader(checkpoint,device)
    started=time.monotonic();receipts=[]
    for number in range(0,len(lines),16):
        batch=lines[number:number+16];name=f'chunk-{number//16:06d}';rp=out/(name+'.receipt.json')
        if rp.exists():
            rr=json.loads(rp.read_text())
            if rr['binding']!=binding or any(sha256(out/p)!=v for p,v in rr['sha256'].items()): raise ValueError('stale teacher resume receipt')
            receipts.append(rr);continue
        timing=dict(alignment=0.,windows=0.,teacher=0.);records={r:[] for r in ROLES};alignments=[]
        images=[Image.open(r['image']).convert('L') for r in batch]
        tick=time.monotonic();als=recognizer.align_batch(images);timing['alignment']+=time.monotonic()-tick
        for r,image,al in zip(batch,images,als):
            ar=al.to_record();alignments.append(dict(line_id=r['line_id'],crop_sha256=r['crop_sha256'],alignment=ar))
            tick=time.monotonic()
            ss,wide,_,_,coverage,size=extract_line(dict(_line=0,recogniser_text=ar['prediction']),ar,image,evaluation=True)
            # Export probabilities even for quarantined locator/crop states.
            # Training eligibility remains the original extraction's scored flag.
            have={int(s[3]) for s in ss}
            for c in coverage:
                if c['start'] not in have:
                    x,m=window(image,c['span'],size['pixel_height'])
                    ss.append((0,len(ss),0,c['start'],LETTERS.index(c['base']),0,[-1]*4,[m,m]));wide.append(x)
            timing['windows']+=time.monotonic()-tick
            tick=time.monotonic();pred=full_predictions(model,ss,wide,device,64 if mock else 512);timing['teacher']+=time.monotonic()-tick
            bystart={p['start']:p for p in pred}
            binary=np.asarray(image)<size['threshold']
            for c in coverage:
                sid=(r['crop_sha256'],c['start'])
                if wanted is not None and sid not in wanted: continue
                x0,x1,_=window_geometry(c['span'],size['pixel_height'])
                lo,hi=max(0,x0),min(image.width,x1)
                validity=dict(clipped_top=bool(binary[0,lo:hi].any()),clipped_bottom=bool(binary[-1,lo:hi].any()),
                    clipping_basis='ink touches native crop edge; ownership unadjudicated',window_outside_image=x0<0 or x1>image.width,
                    span_plausible=plausible_span(c['span'],size)[0],reason=c['reason'],fused=c['fused'],evidence_state=c['evidence_state'])
                records[r['role']].append(dict(slot_id=list(sid),line_id=r['line_id'],doc=r['doc'],source=r['source'],
                    role=r['role'],teacher_seen_document=r.get('teacher_seen_document',False),crop_validity=validity,coverage=c,**bystart.get(c['start'],dict(start=c['start'],base=c['base'],heads=None)),
                    teacher_checkpoint_sha256=TEACHER_SHA,code_sha256=code,
                    input_hashes=dict(crop=r['crop_sha256'],line_list=binding['line_list_sha256'],recognizer=recognizer_sha256,codec=binding['codec_sha256']),
                    calibration_version=binding['calibration_version']))
        files=[]
        for role,rs in records.items():
            p=out/f'{name}-{role}.jsonl.gz';write_rows(p,rs);files.append(p)
        ap=out/f'{name}-alignments.jsonl.gz';write_rows(ap,alignments);files.append(ap)
        rr=dict(binding=binding,lines=len(batch),slots=sum(map(len,records.values())),timing_seconds=timing,
                sha256={p.name:sha256(p) for p in files},complete=True)
        write_json(rp,rr);receipts.append(rr)
    result=dict(binding=binding,complete=True,lines=len(lines),slots=sum(r['slots'] for r in receipts),
        elapsed_seconds=time.monotonic()-started,timing_seconds={k:sum(r['timing_seconds'][k] for r in receipts) for k in ('alignment','windows','teacher')},
        chunks={p.name:sha256(p) for p in out.glob('chunk-*.receipt.json')})
    write_json(out/'teacher_receipt.json',result);return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('line-list','checkpoint','recognizer-checkpoint','out'): ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--recognizer-sha256',required=True);ap.add_argument('--slots',type=Path)
    ap.add_argument('--device',default='cuda:0');ap.add_argument('--mock',action='store_true')
    print(json.dumps(export(**vars(ap.parse_args()))))

if __name__=='__main__': main()
