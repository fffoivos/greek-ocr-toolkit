"""S7 fixed-cohort geometry qualification; offline, cached alignment only."""
import os
for k in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[k]='1'
import argparse
from collections import Counter
from copy import copy, deepcopy
import hashlib
import gzip
import json
from pathlib import Path
import socket
import time
import numpy as np
from PIL import Image
from greekocr.labelfix import ink as I, reading as R, markshape as M, toolkit_geometry as G
from greekocr.labelfix.ctc_align import Recognizer
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.linemetric import summary
from scripts.labelfix.s5_validate import read, metric
from scripts.labelfix.s6_validate import detected, physical, zones, char_truth, presence
from scripts.labelfix.owner_reading import serialize, digest
from scripts.labelfix.cn1_measure import system_coverage, page_from_saved
from scripts.labelfix.s7_owner import evaluate
from scripts.labelfix import owner_pages_build_combined as combined

O=Path('docs/labelfix/spellcheck'); E=O/'S7_evidence'


def write(path, rows):
    opener=gzip.open(path,'wt',compresslevel=1) if str(path).endswith('.gz') else open(path,'w')
    with opener as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')


def guard(*a,**kw):raise RuntimeError('S7 forbids network and recognizer inference')


def adapt(record, frozen):
    line=deepcopy(frozen); old={s['start']:s for s in frozen['recogniser_slots']}
    for s in record['slots']:
        b=old[s['start']]
        s['component_slots']=b['component_slots'];s['component_slot']=b['component_slot']
    for slot in line['slots']:
        children=[s for s in record['slots'] if s['component_slot']==slot['slot']]
        ev=deepcopy(slot['evidence'])
        for field in ('above','below','diagnostics','apostrophes'):
            ev[field]=list({tuple(b['bbox']):b for r in children for b in r['evidence'].get(field,[])}.values())
        if children:ev.update({k:v for k,v in children[0]['evidence'].items() if k not in ('above','below','diagnostics','apostrophes')})
        slot.update(detected=sorted({tuple(m) for r in children for m in detected(r)}),evidence=ev,
                    hold=any(r.get('hold') for r in children),unnamed=[x for r in children for x in r.get('unnamed',[])])
    line.update(reading=record['text'],recogniser_slots=record['slots'],opening_quotes=record['opening_quotes'],constraint_flags=record['constraint_flags'])
    return system_coverage(line)


def binary(rows,key):
    return summary(Counter(tp=sum(bool(s[key]) and s['truth'] for s in rows),
        fp=sum(bool(s[key]) and not s['truth'] for s in rows),fn=sum(not s[key] and s['truth'] for s in rows),n=len(rows)))


def box_page(line):
    page=page_from_saved(line)
    page['letter_zones']=[dict(display_slot=s['component_slot'],
        mark_zone=[s['evidence']['window'][0],s['evidence']['meanline']-1.3*s['evidence']['xh'],
                   s['evidence']['window'][1],s['evidence']['baseline']+.9*s['evidence']['xh']])
        for s in line['recogniser_slots'] if s.get('component_slot') is not None]
    for box in page['boxes']:
        slot=next((s for s in line['recogniser_slots'] if s['start']==box.get('start')),None)
        box['status']='flagged-by-constraint' if slot and slot.get('constraint_flags') else 'raw-detection'
    return page


def metrics(rows,capital_truth):
    out={}
    for split,dev in [('heldout',False),('dev',True)]:
        ls=[l for l in rows if l['dev']==dev];cs=[s for l in ls for s in l['character_checks']]
        groups=dict(all=cs,fused=[s for s in cs if s['fused']],merged_accent=[s for s in cs if s['merged_accent']])
        out[split]=dict(lines=len(ls),atomic_slots=metric(ls,'detected'),presence={k:dict(n=len(ss),**presence(ss,'S7','above' if k=='merged_accent' else None)) for k,ss in groups.items()},
            below_shared_meanline=sum(s['below_shared_meanline'] for s in cs),
            below_shared_meanline_pixels=sum(s['below_shared_meanline_pixels'] for s in cs),
            ascender_false_marks=sum(bool(s['evidence']['above']) for l in ls for s in l['slots'] if s['truth']==[] and (s['base'] in 'δβλθφξζ' or s['base'].isupper())),
            ambiguous_slots=sum(bool(s.get('localisation_unknown')) for l in ls for s in l['recogniser_slots']),
            unseen_slots=sum(bool(s.get('unseen_zones')) for l in ls for s in l['recogniser_slots']))
    by={l['line_id']:l for l in rows};caps=[]
    for old in capital_truth:
        rs=next((s for s in by[old['line_id']]['recogniser_slots'] if s['component_slot']==old['slot']),{})
        caps.append(dict(old,pixel=rs.get('pixel_class')=='capital',combined=rs.get('case_class')=='capital'))
    out['capitals']={k:binary(caps,k) for k in ('pixel','combined')}
    out['capital_disagreement']={k:binary([s for s in caps if s['case_disagreement']],k) for k in ('pixel','combined')}
    out['guide_winners']=dict(Counter(l['shared_guides']['decision']['winner'] for l in rows))
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--variants',nargs='+',default=['baseline','S1','S2','S3','accepted']);a=ap.parse_args()
    socket.socket.connect=guard;socket.create_connection=guard;Recognizer.__init__=guard;Recognizer.align_batch=guard
    start=time.monotonic();E.mkdir(parents=True,exist_ok=True)
    from scripts.labelfix.owner_reading import SOURCES
    files=[Path(p) for p in SOURCES]+[Path(__file__),Path('scripts/labelfix/s7_owner.py'),
        Path('scripts/labelfix/cn1_measure.py'),Path('scripts/labelfix/s6_validate.py'),Path('scripts/labelfix/s6_notes.py'),
        Path('scripts/labelfix/s5_notes.py'),Path('scripts/labelfix/clariden/r1_owner.py'),
        O/'S4_lines.jsonl.gz',O/'S6_lines.jsonl.gz',O/'S5_capital_truth.jsonl',O/'print_truth_s0.json',
        Path('.cache/labelfix/align_s0.jsonl'),Path('docs/labelfix/markshape_model_S4.json'),Path('docs/labelfix/case_model_S5.json')]
    before={str(p):digest(p) for p in files}
    saved=read(O/'S6_lines.jsonl.gz');s4={l['line_id']:l for l in read(O/'S4_lines.jsonl.gz')}
    frozen={'S4':s4,'S6':{l['line_id']:l for l in saved}}
    source={l['line_id']:l for l in load_three_way(0)}
    truth=json.loads((O/'print_truth_s0.json').read_text())
    owner_ids=set(json.loads((O/'CN1_evidence/combined_boxes.json').read_text())['lines'])
    (E/'saved_S6_boxes.json').write_text(json.dumps(dict(lines={l['line_id']:box_page(l) for l in saved if l['line_id'] in owner_ids}),ensure_ascii=False)+'\n')
    cfg=json.loads((O/'CN1_evidence/combined_config.json').read_text())
    for p,d in cfg['r1_predictions'].items():
        assert digest(p)==d
        for r in read(Path(p)):combined.R1[(r['line_id'],r['start'])]=r
    als=load_alignments(Path('.cache/labelfix/align_s0.jsonl'));model=M.load_model(Path('docs/labelfix/markshape_model_S4.json'))
    variants={k:[] for k in a.variants};combined_lines={k:{} for k in a.variants}
    oldholds=[r for r in read(O/'CN1_checks.jsonl') if r['type']=='hold_slot' and r['kind_disagreement']]
    disagreement_records=[]
    for n,old in enumerate(saved):
        lid=old['line_id'];text=old['recogniser_text'];combined.LINE_TEXT[lid]=text
        with Image.open(old['crop']) as im: base=I.analyse(im)
        reasons={};ct=char_truth(source[lid],truth,reasons=reasons)
        for variant in a.variants:
            subs=[] if variant=='baseline' else R.QUALIFIED_GEOMETRY if variant=='accepted' else variant.split('+')
            ci=copy(base);ci.case_info={};ci.word_bands={}
            rd=R.read_ink(ci,text,als[crop_key(old['crop'])],model,filtered=False,substitutions=subs)
            guides=getattr(ci,'shared_guides',None) or G.shared_guides(ci)
            serial=serialize(rd)
            line=adapt(serial,old)
            line['shared_guides']=guides.record()
            if hasattr(ci,'physical_letters'):line['physical_letters']=ci.physical_letters
            by={s['start']:s for s in line['recogniser_slots']}
            checks=[]
            for b in old['character_checks']:
                s=by[b['start']];cs=deepcopy(b);ev=s['evidence']
                cs.update(truth=ct.get(b['start']),truth_zones=zones(ct.get(b['start'])),truth_reason=reasons.get(b['start']),
                          presence={'S7':physical(s)})
                bad=0;bad_blobs=0
                for blob in ev.get('above',[]):
                    if blob['source']=='preposed':continue
                    x0,y0,x1,y1=blob['bbox']
                    blob_bad=sum(int(np.count_nonzero(y+y0>=np.floor(guides.mean[x0+a0:x0+b0]))) for y,a0,b0 in blob.get('pixel_runs') or [])
                    bad+=blob_bad;bad_blobs+=bool(blob_bad)
                cs['below_shared_meanline']=bad_blobs;cs['below_shared_meanline_pixels']=bad;checks.append(cs)
            line['character_checks']=checks
            variants[variant].append(line)
            if lid in owner_ids:
                rawparts={s['start']:list(s['parts']) for s in rd.slots}
                rawline=adapt(serialize(R.apply_constraints(deepcopy(rd))[0]),old)
                cr,_=combined.combine(lid,deepcopy(rd))
                cl=adapt(serialize(cr),old);combined_lines[variant][lid]=cl
                line['owner_detector_control']=rawline
                for h in (h for h in oldholds if h['line_id']==lid):
                    p=combined.R1[(lid,h['start'])];rparts=[p for p in p['cls'].split('+') if p!='none']
                    dparts=rawparts[h['start']];t=ct.get(h['start']);ts=set(zones(t) or []) if t is not None else None
                    from greekocr.labelfix.linemetric import mark_set
                    def kinds(parts):return combined._kinds(parts)
                    tk=kinds([x for k,v in t for x in (v.split('+') if k=='compound' else [v])]) if t is not None else None
                    disagreement_records.append(dict(variant=variant,line_id=lid,start=h['start'],detector_parts=dparts,r1_parts=rparts,
                        remains=kinds(dparts)!=kinds(rparts),truth=t,truth_kinds=sorted(tk) if tk is not None else None,
                        detector_right=kinds(dparts)==tk if tk is not None else None,r1_right=kinds(rparts)==tk if tk is not None else None))
        if n%100==0:print('S7',n,len(saved),round(time.monotonic()-start,1),flush=True)
    cap=read(O/'S5_capital_truth.jsonl');result={};allnotes=[]
    for variant,rows in variants.items():
        # Auxiliary detector-control copy is limited to owner lines.
        controls={l['line_id']:l.pop('owner_detector_control') for l in rows if 'owner_detector_control' in l}
        write(E/f'{variant}_lines.jsonl.gz',rows)
        write(E/f'{variant}_combined_lines.jsonl',list(combined_lines[variant].values()))
        (E/f'{variant}_boxes.json').write_text(json.dumps(dict(lines={l['line_id']:box_page(l) for l in rows if l['line_id'] in owner_ids}),ensure_ascii=False)+'\n')
        systems={'S6':{lid:system_coverage(frozen['S6'][lid]) for lid in owner_ids},
                 'combined':combined_lines[variant],'SF1_detector_control':controls}
        notes,ns=evaluate(systems,frozen);allnotes.extend(dict(r,variant=variant) for r in notes)
        rawnotes,_=evaluate(dict(systems,combined=controls),frozen)
        result[variant]=metrics(rows,cap)
        result[variant]['owner']=ns
        result[variant]['strict_detector']={g:dict(n=sum(r['note_set']==g for r in rawnotes),fixed=sum(r['note_set']==g and r['systems']['combined']['raw_fixed'] for r in rawnotes)) for g in ns}
        ds=[r for r in disagreement_records if r['variant']==variant]
        result[variant]['kind_disagreements']=dict(original=len(ds),remaining=sum(r['remains'] for r in ds),resolved=sum(not r['remains'] for r in ds),
            remaining_known=sum(r['remains'] and r['truth'] is not None for r in ds),remaining_detector_right=sum(r['remains'] and r['detector_right'] is True for r in ds),remaining_r1_right=sum(r['remains'] and r['r1_right'] is True for r in ds))
        all_disagreements=sum(combined._kinds(r.get('parts',[]))!=combined._kinds([x for x in combined.R1[(l['line_id'],r['start'])]['cls'].split('+') if x!='none']) for l in rows if l['line_id'] in owner_ids for r in l['recogniser_slots'] if (l['line_id'],r['start']) in combined.R1)
        result[variant]['kind_disagreements']['all_owner_slots']=all_disagreements
        hold_records=[dict(line_id=lid,start=s['start'],base=s['base'],parts=s.get('parts'),
            unseen_zones=s.get('unseen_zones',[]),localisation_unknown=s.get('localisation_unknown',False),
            constraint_flags=s.get('constraint_flags',[])) for lid,l in combined_lines[variant].items() for s in l['recogniser_slots'] if s.get('hold')]
        write(E/f'{variant}_hold_slots.jsonl',hold_records)
        result[variant]['hold_slots']=dict(slots=len(hold_records),lines=len({s['line_id'] for s in hold_records}),
            unseen_slots=sum(bool(s['unseen_zones']) for s in hold_records),
            localisation_unknown=sum(s['localisation_unknown'] for s in hold_records))
        result[variant]['physical_mapping']=dict(letters=sum(len(l.get('physical_letters',[])) for l in rows),
            unmatched_physical=sum(not p['recognizer_starts'] for l in rows for p in l.get('physical_letters',[])),
            unresolved_physical=sum(not p['resolved'] for l in rows for p in l.get('physical_letters',[])))
        print(variant,json.dumps({k:result[variant][k] for k in ('kind_disagreements','capitals','strict_detector')},ensure_ascii=False),flush=True)
    write(E/'owner_checks.jsonl',allnotes);write(E/'kind_disagreements.jsonl',disagreement_records)
    (E/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    assert before=={str(p):digest(p) for p in files},'source changed during qualification'
    (E/'receipt.json').write_text(json.dumps(dict(network=False,ctc_forward_passes=0,r1_forward_passes=0,retraining=False,
        elapsed_seconds=time.monotonic()-start,lines=len(saved),variants=a.variants,source_sha256=before),indent=2)+'\n')


if __name__=='__main__':main()
