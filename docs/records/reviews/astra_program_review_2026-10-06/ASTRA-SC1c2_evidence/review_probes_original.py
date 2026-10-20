"""Read-only ASTRA-SC1 probes. No crop decoding, network, CTC or model forward passes."""
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageDraw

R = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
O = Path(__file__).resolve().parent
sys.path.insert(0, str(R))
sys.path.insert(0, str(R/'scripts/labelfix'))
from greekocr.labelfix import ink as I, case
from greekocr.labelfix.reading import LineReading, apply_constraints
from greekocr.labelfix.segmentation import _region
from scripts.labelfix.clariden.r1_extract import window, extract_line
from scripts.labelfix.box_regression import diff_line
from s6_notes import clause
from s6_validate import char_truth

results = {}
# A print transcription may be orthographically impossible. Support does not veto deletion.
s = dict(base='ε', start=0, parts=['circumflex'], naming={'probability':1.0},
         evidence=dict(xh=20, body=[10,25], above=[dict(bbox=[12,4,22,10],area=50)]))
rd, removed = apply_constraints(LineReading('ε\u0342', [s], []))
results['k1_supported_misprint'] = dict(before='ε\u0342', after=rd.text, removed=removed)

# Clipping an original blob must not switch to a foreign component in its bounding box.
lab = np.zeros((20,20), int)
lab[2:12,2]=1; lab[2,2:14]=1; lab[11,2:14]=1
lab[4:10,4:12]=2
ci = I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,np.full(20,12.),np.full(20,18.),[],255.,20,20,20.)
b = I._blob(lab==1,0,0,'attached',ci)
q = I.zone_blob(ci,b,upper=10)
results['blob_parent_switch'] = dict(source_bbox=b.to_record()['bbox'],source_area=b.area,
    clipped_bbox=q.to_record()['bbox'], clipped_area=q.area,
    result_parent_ids=np.unique(lab[q.y0:q.y1,q.x0:q.x1]).tolist())

# A union region retains both labels, but case features read only the first label.
lab = np.zeros((30,40),int); lab[5:25,5:10]=1; lab[5:25,15:20]=2
ci = I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,np.full(40,5.),np.full(40,25.),[],255.,40,30,20.)
c = _region(ci,[SimpleNamespace(index=1),SimpleNamespace(index=2)],5,20)
results['union_case_occupancy'] = dict(measured=case.features(ci,c)[5],
    actual_union=float((lab[c.y0:c.y1,c.x0:c.x1]>0).mean()), region_index=c.index)

# Entire-crop vertical resizing changes font scale when only blank padding changes.
a=Image.new('L',(80,40),255); b=Image.new('L',(80,80),255)
for im in (a,b):ImageDraw.Draw(im).rectangle((20,10,29,29),fill=0)
wa,_=window(a,[20,30],20); wb,_=window(b,[20,30],20)
results['r1_vertical_padding'] = dict(dark_rows_40=int((wa<128).any(axis=1).sum()),
    dark_rows_80=int((wb<128).any(axis=1).sum()), equal=bool(np.array_equal(wa,wb)))
al=dict(prediction='α',spans=[['α',0,1,20.,30.]],confidence=.9)
ss,_,_,losses,coverage,size=extract_line(dict(_line=0,recogniser_text='α'),al,Image.new('L',(80,40),255),evaluation=True)
results['r1_blank_admission']=dict(samples=len(ss),size=size,coverage=coverage)

# Same boxes, different ordering -> different lost/added conclusions.
old=dict(reading='',letters=[[0,10],[5,15]],boxes=[dict(kind='above',bbox=[0,0,10,10]),dict(kind='above',bbox=[5,0,15,10])])
new=dict(reading='',letters=old['letters'],boxes=[dict(kind='above',bbox=[2,0,12,10]),dict(kind='above',bbox=[-3,0,7,10])])
rev=copy.deepcopy(old);rev['boxes'].reverse()
results['box_matching_order']={key:{k:len(v) for k,v in diff_line(value,new,.3).items() if k in ('lost','added','moved')}
    for key,value in [('original',old),('reversed',rev)]}

# A physical-presence check can pass when a previously approved name disappears.
old=dict(slots=[dict(slot=1,truth=None,detected=[])],recogniser_slots=[dict(start=0,component_slot=1,parts=['acute'],evidence={'above':[{'bbox':[0,0,3,3]}]})])
new=copy.deepcopy(old);new['recogniser_slots'][0]['parts']=[]
results['unknown_approved_name_removed']=dict(zip(('passes','details'),clause(new,old,'no_regression',None,None)))
results['missing_owner_target_no_top']=dict(zip(('passes','details'),clause(new,old,'no_top',999,None)))
results['unsupported_print_truth']=char_truth(dict(line_id='probe',google='α',model='α',human='α'),
    {'probe|0':{'printed':'α\u0301\u0300'}})

root=R/'docs/labelfix/spellcheck'
metrics=json.loads((root/'clariden/R1_result_3678928/metrics.json').read_text())
results['r1_metrics']={k:metrics[k] for k in ('heldout_lines','scoring_contract','source_sha256')}
results['r1_metrics']['A']={k:metrics['arms']['A'][k] for k in ('mapping','all_unscored_none','scored','fused_all_unscored_none','fused_scored','capital_detection','capital_naming','owner_counts')}
results['r1_metrics']['coverage']={k:v for k,v in metrics['coverage'].items() if k in ('counts','samples','coverage','font_rule','font_size_summary')}
results['model_assets']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'docs/labelfix').glob('*model*.json')}
results['s5_s6_baselines']={n:json.loads((root/f'{n}_metrics.json').read_text()).get('after') for n in ('S4','S5')}
results['s5_s6_baselines']['S6']=json.loads((root/'S6_metrics.json').read_text())['heldout']['detected']
results['r1_reference_S5']=metrics['reference']['S5']['all_unscored_none']
results['r1_disjointness']=json.loads((R/'artifacts/labelfix_r1/binding/disjointness.json').read_text())

(O/'review_probe_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
for k,v in results.items():
    if k not in ('r1_metrics','s5_s6_baselines','r1_reference_S5'):print(k,json.dumps(v,ensure_ascii=False))
for k in ('mapping','capital_detection','owner_counts'):
    print('R1 A',k,json.dumps(results['r1_metrics']['A'][k]))
print('R1 A totals', {k:results['r1_metrics']['A'][k]['total'] for k in ('all_unscored_none','scored','fused_all_unscored_none','fused_scored')})
print('reference total identity', {k:v['total'] for k,v in results['s5_s6_baselines'].items()},results['r1_reference_S5']['total'])
