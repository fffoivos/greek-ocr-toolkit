"""SF1 truth/policy replay of saved S6 evidence, without detector or CTC inference."""
import json
import hashlib
from copy import deepcopy
from collections import Counter
from pathlib import Path
from scripts.labelfix.k1_validate import read,write,reading_of,filtered_line,score,classify
from scripts.labelfix.s6_validate import char_truth,aggregate
from greekocr.labelfix.reading import apply_constraints,APPLIED_CONSTRAINT_RULES
from greekocr.labelfix.validate import load_three_way

O=Path('docs/labelfix/spellcheck')

def main():
    saved=read(O/'S6_lines.jsonl.gz');raw=deepcopy(saved)
    truth=json.loads((O/'print_truth_s0.json').read_text());sources={l['line_id']:l for l in load_three_way(0)}
    changes=[]
    for l in raw:
        reasons={};ct=char_truth(sources[l['line_id']],truth,reasons=reasons)
        for c in l['character_checks']:
            old=c['truth'];new=ct.get(c['start'])
            new=[list(m) for m in new] if new is not None else None
            if new!=old:
                changes.append(dict(line_id=l['line_id'],start=c['start'],dev=l['dev'],before=old,after=new,reason=reasons.get(c['start'])))
            c.update(truth=new,truth_zones=None if new is None else c['truth_zones'],truth_reason=reasons.get(c['start']))
    support={l['line_id']:l['naming'] for l in read(O/'K1_support.jsonl.gz')}
    for l in raw:
        names=support[l['line_id']]
        assert len(names)==len(l['recogniser_slots'])
        l['recogniser_slots']=[dict(s,naming=n) for s,n in zip(l['recogniser_slots'],names)]
    normalised=[];printed=[];deletions=[];flags=[]
    for l in raw:
        r,removed=apply_constraints(reading_of(l),output='normalised')
        normalised.append(filtered_line(l,r))
        p,none=apply_constraints(reading_of(l));assert not none and p.text==l['reading']
        printed.append(filtered_line(l,p))
        for receipt in removed:
            deletions.append(dict(receipt,line_id=l['line_id'],dev=l['dev'],print_status=classify(l,receipt)))
        flags.extend(dict(f,line_id=l['line_id'],dev=l['dev']) for f in p.constraint_flags)
    def split_scores(ls):return {name:score([l for l in ls if l['dev']==dev]) for name,dev in [('heldout',False),('dev',True)]}
    old_k1=json.loads((O/'K1_metrics.json').read_text())
    result=dict(schema='sf1-saved-evidence-rescore-v1',ctc_forward_passes=0,network=False,detector_inference=False,
        truths_now_unknown=len([c for c in changes if c['before'] is not None and c['after'] is None]),truth_changes=changes,
        S6_before=split_scores(saved),S6_after=split_scores(raw),K1_print=split_scores(printed),K1_normalised=split_scores(normalised),
        K1_before={split:old_k1[split]['after'] for split in ('heldout','dev')},
        old_deletions_now_flags={split:dict(Counter(d['print_status'] for d in deletions if d['dev']==dev),total=sum(d['dev']==dev for d in deletions)) for split,dev in [('heldout',False),('dev',True)]},
        held_labels=sum(s.get('hold',False) for l in printed for s in l['recogniser_slots']),
        applied_rules=sorted(APPLIED_CONSTRAINT_RULES),
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [O/'S6_lines.jsonl.gz',O/'K1_support.jsonl.gz',O/'K1_support_receipt.json',O/'print_truth_s0.json',Path('greekocr/labelfix/reading.py'),Path('scripts/labelfix/s6_validate.py'),Path(__file__)]},
        source_text_sha256=hashlib.sha256(json.dumps([{k:l[k] for k in ('line_id','google','model','human')} for _,l in sorted(sources.items())],sort_keys=True).encode()).hexdigest(),
        support_policy='historical K1 classifier support replay; not new detector qualification')
    (O/'SF1_truth_K1_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    write(O/'SF1_constraint_flags.jsonl.gz',flags)
    write(O/'SF1_truth_changes.jsonl',changes)
    print(json.dumps({k:result[k] for k in ('truths_now_unknown','old_deletions_now_flags','held_labels')},indent=2))
    for split in ('heldout','dev'):
        print(split,'S6',result['S6_before'][split]['character_atomic'],'->',result['S6_after'][split]['character_atomic'])
        print(split,'K1 old',result['K1_before'][split]['character_atomic'],'normalised',result['K1_normalised'][split]['character_atomic'],'print',result['K1_print'][split]['character_atomic'])

if __name__=='__main__':main()
