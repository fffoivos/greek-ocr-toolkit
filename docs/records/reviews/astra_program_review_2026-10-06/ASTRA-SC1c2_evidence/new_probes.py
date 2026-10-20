"""Read-only cycle-2 probes: synthetic composition and saved small instruments.

No image decoding, network, CTC or neural forward passes. Run with repo PYTHONPATH.
"""
import copy
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent
from greekocr.labelfix.reading import LineReading
from scripts.labelfix.m2_run import combine
from scripts.labelfix.owner_pages_build_combined import combine as page_combine
from scripts.labelfix import owner_pages_build_combined as page
from scripts.labelfix.box_regression import diff_line

def rows(p):
    with (gzip.open(p, 'rt') if str(p).endswith('.gz') else open(p)) as f:
        return [json.loads(x) for x in f]

def raw(parts=(), **kw):
    slot = dict(start=0,end=1,base='α',parts=list(parts),unnamed=[],
        locator_span=[10,20],component=None,bbox=[10,10,20,30],
        evidence=dict(above=[],below=[],clipped_top=False,clipped_bottom=False))
    slot.update(kw)
    return LineReading('α',[slot],[])

result = {}
for label, r, coverage in [
    ('r1_unknown',raw(),[dict(start=0,scored=True,evidence_state='UNKNOWN',uncertainty=['no_pixel_evidence'],reason=None)]),
    ('r1_outside',raw(),[dict(start=0,scored=True,evidence_state='UNKNOWN',uncertainty=['out_of_image_span'],reason=None)]),
    ('segmentation_uncertain',raw(segmentation_uncertain=True),[]),
    ('clipped_detector',raw(evidence=dict(above=[],below=[],clipped_top=True,clipped_bottom=True)),[]),
]:
    pred={0:dict(parts=[],mark_probabilities={})}
    modes={m:combine('ά',copy.deepcopy(r),pred,coverage,m) for m in ('PRESENCE','FULL')}
    result[label]={m:dict(text=v['text'],holds=v['hold_slots']) for m,v in modes.items()}
    if (ROOT/'scripts/labelfix/clariden/l1_common.py').exists():
        from scripts.labelfix.clariden.l1_common import overlay
        runtime=dict(recogniser_text='ά',detector=dict(text='α'),modes=modes)
        rec=dict(id='synthetic',label='ά',script_class='greek_poly')
        binding=dict(detector='s6',r1_sha256='synthetic',policy_sha256='synthetic')
        result[label]['overlay']={m:overlay(rec,runtime,m.lower(),binding)['status'] for m in modes}

# Same physical blob, different S4 family names, fixed R1 prediction.
result['same_pixels_kind_gate']={}
for part in ('acute','psili'):
    ev=dict(above=[dict(bbox=[10,2,14,6],area=10)],below=[])
    out=combine('ά',raw([part],evidence=ev),{0:dict(parts=['acute'],mark_probabilities={'acute':.9})},[],'PRESENCE')
    result['same_pixels_kind_gate'][part]=out['hold_slots']

page.LINE_TEXT['synthetic']='α'
page.R1.clear()
page.R1[('synthetic',0)]=dict(cls='none')
r=raw();r.opening_quotes=[dict(bbox=[0,0,3,5])];r.text='“α'
out,_=page_combine('synthetic',copy.deepcopy(r))
result['page_quote_loss']=dict(before=r.text,after=out.text,opening_quote_evidence=out.opening_quotes)
r=raw();r.slots[0]['component']=object()
page.R1.clear();page.R1[('other',0)]=dict(cls='none')
out,_=page_combine('synthetic',r)
result['page_missing_prediction']=dict(parts=out.slots[0]['parts'],hold=out.slots[0].get('hold',False))

old=dict(reading='αα',boxes=[dict(kind='above',bbox=[5,2,8,5],display_slot=1)],
    letter_zones=[dict(display_slot=1,mark_zone=[0,0,10,10])])
new=copy.deepcopy(old);new['boxes'][0]['display_slot']=2;new['letter_zones'][0]['display_slot']=2
result['unchanged_box_changed_owner']=diff_line(old,new,.3)

cn=ROOT/'docs/labelfix/spellcheck/CN1_evidence'
if cn.exists():
    a=json.loads((cn/'s6_control_boxes.json').read_text())['lines']
    b=json.loads((cn/'combined_boxes.json').read_text())['lines']
    quote_diffs=[]
    for lid in a:
        ar,br=a[lid]['line_reading'],b[lid]['line_reading']
        if ar['opening_quotes'] and not br['text'].startswith('“'):
            quote_diffs.append(dict(line_id=lid,control=ar['text'],combined=br['text'],quote_evidence=br['opening_quotes']))
    result['saved_CN1_quotes_missing_from_text']=quote_diffs

se=ROOT/'docs/labelfix/spellcheck/S7_evidence'
if se.exists():
    ds=[r for r in rows(se/'kind_disagreements.jsonl') if r['variant']=='baseline']
    def zone(parts):
        return set(('below' if p=='subscript' else 'above') for p in parts)
    result['80_disagreements_zone_strata']=dict(Counter('same_named_zone' if zone(r['detector_parts'])==zone(r['r1_parts']) else 'different_named_zone' for r in ds))
    result['80_disagreements_known']=dict(Counter('unknown' if r['truth'] is None else 'R1' if r['r1_right'] else 'detector' if r['detector_right'] else 'neither' for r in ds))

if (ROOT/'artifacts/labelfix_l1/mock_checked_192').exists():
    base=ROOT/'artifacts/labelfix_l1/mock_checked_192'
    runtimes={r['id']:r for p in sorted((base/'combined').glob('*-combined.jsonl.gz')) for r in rows(p)}
    out={}
    for v in ('presence','full'):
        overlays=rows(base/'release'/f'overlay_{v}.jsonl.gz')
        ctrl=rows(base/'release'/f'ctrl_subset_{v}.jsonl.gz')
        kept={r['line_id'] for r in overlays if r['status'] in ('corrected','unchanged')}
        tally=Counter();detail=[]
        for lid in kept:
            r=runtimes[lid]
            unknown=[c for c in r['coverage'] if c.get('evidence_state')=='UNKNOWN']
            ambiguous=[s['start'] for s in r['detector']['slots'] if s.get('segmentation_uncertain')]
            clipped=[s['start'] for s in r['detector']['slots'] if s['evidence'].get('clipped_top') or s['evidence'].get('clipped_bottom')]
            for k,vs in [('r1_UNKNOWN',unknown),('segmentation_uncertain',ambiguous),('detector_clipped',clipped)]:
                tally[k+'_slots']+=len(vs);tally[k+'_lines']+=bool(vs)
            if unknown or ambiguous or clipped:detail.append(dict(id=lid,unknown=unknown,segmentation_uncertain=ambiguous,clipped=clipped))
        out[v]=dict(statuses=dict(Counter(r['status'] for r in overlays)),kept=len(kept),paired_ids=kept=={r['line_id'] for r in ctrl},uncertainty=dict(tally),details=detail)
    result['L1_mock_saved_readback']=out

if (ROOT/'scripts/labelfix/clariden/l1_common.py').exists():
    from scripts.labelfix.clariden.l1_common import overlay
    result['unsupported_original_mark_deletion']={}
    for original,base in [('ᾱ','α'),('é','e'),('α\u0301\u0300','α')]:
        rd=raw();rd.text=base;rd.slots[0]['base']=base
        predictions={0:dict(parts=[],mark_probabilities={})} if base=='α' else {}
        modes={m:combine(original,copy.deepcopy(rd),predictions,[],m) for m in ('PRESENCE','FULL')}
        runtime=dict(recogniser_text=original,detector=dict(text=base),modes=modes)
        rec=dict(id='synthetic',label=original,script_class='greek_poly')
        binding=dict(detector='s6',r1_sha256='synthetic',policy_sha256='synthetic')
        result['unsupported_original_mark_deletion'][original]={m:{k:v for k,v in overlay(rec,runtime,m.lower(),binding).items() if k in ('status','label','hold_slots')} for m in modes}

dest=OUT/('new_probes_l1.json' if ROOT.name.endswith('-l1') else 'new_probes_main.json')
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for k,v in result.items():
    if k=='saved_CN1_quotes_missing_from_text':print(k,len(v),[r['line_id'] for r in v])
    elif k=='L1_mock_saved_readback':print(k,{name:{kk:vv for kk,vv in value.items() if kk!='details'} for name,value in v.items()})
    else:print(k,json.dumps(v,ensure_ascii=False))
