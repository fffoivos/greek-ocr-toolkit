"""Offline two-read N1 candidates; raised dots always await lead pixel review.

VOID reads are retained as secondary evidence only. Two gate-passing reads are
required: one valid plus one VOID is still only one valid read. No labels change.
Re-run after r2: python -B scripts/numerics/n1_decide.py
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from n1_score import decode_and_gate, MEANINGS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/n1'

def rows(path): return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
def dump(path,value): Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def edit_rule(glyph, position, truth_candidate):
    if glyph in ('-','.') and position=='thousands' and truth_candidate=='raised dot':
        return dict(original=glyph,replacement='\u00b7')
    return None

def decide(slot, reads):
    if len({r['reader'] for r in reads}) != len(reads): raise ValueError('duplicate reader vote')
    valid=[r for r in reads if r['context_status']=='VALID' and r.get('read_status')=='ok']
    meanings=[r.get('meaning') for r in reads if r.get('meaning') is not None]
    uncertain=any(m in ('other','unreadable') for m in meanings)
    disagree=len(set(meanings))>1
    candidate=None
    reason='two_agreeing_valid_reads'
    if uncertain: reason='unreadable_or_other'
    elif disagree: reason='disagreement'
    elif len(valid)!=2: reason='fewer_than_two_valid_reads'
    elif len(set(r['meaning'] for r in valid))==1: candidate=valid[0]['meaning']
    else: reason='disagreement'
    raised=any(m=='raised dot' for m in meanings)
    edit=edit_rule(slot['glyph'],slot['position'],candidate)
    review=candidate is None or raised
    if candidate is not None and raised: reason='raised_dot_requires_lead_pixel_check'
    return dict(slot_id=slot['slot_id'],line_id=slot['line_id'],document=slot['document'],
                google_glyph=slot['glyph'],position=slot['position'],grammar_candidates=slot['grammar_candidates'],
                start=slot['start'],end=slot['end'],reads=reads,valid_reads=len(valid),
                truth_candidate=candidate,status='lead_review' if review else 'no_edit',reason=reason,
                edit_candidate=edit,edit=None,apply_edit=False,lead_pixel_check_required=raised)

def load_reads(out=OUT):
    byslot={}; gates={}
    for i in range(1,8):
        ctx=f'ctx{i:02}'
        for reader in ('r1','r2'):
            suffix='' if reader=='r1' else '.r2'
            keypath=out/'keys'/f'{ctx}{suffix}.json'
            key=json.loads(keypath.read_text())
            answerpath=out/'answers'/f'{ctx}.{reader}.jsonl'
            gate=dict(status='MISSING',wrong=None,abstentions=None)
            answers=[]; error=None
            if answerpath.exists():
                try:
                    answers=rows(answerpath)
                    gate,_=decode_and_gate(key,answers)
                    # A gate is usable only with the successful isolated run and v4 leak scan.
                    scan=json.loads((out/'answers'/f'{ctx}.{reader}.scan.json').read_text())
                    run=json.loads((out/'answers'/f'{ctx}.{reader}.run.json').read_text())
                    if not scan['ok'] or scan['scanner_version'] not in (4, 'v4.4-canonical') or run['rc']!=0 or run['model']!='gpt-6.1-sol':
                        raise ValueError('run/leak provenance failed')
                except (ValueError,KeyError,OSError,TypeError,AssertionError) as exc:
                    gate=dict(status='INVALID',wrong=None,abstentions=None); error=str(exc)
            gates[f'{ctx}.{reader}']=dict(gate,error=error)
            grouped={}
            for a in answers: grouped.setdefault(a.get('item_id'),[]).append(a)
            for iid in key['readers'][reader]:
                item=key['items'][iid]
                if item['control_truth'] is not None: continue
                found=grouped.get(iid,[]); a=found[0] if len(found)==1 else {}
                meaning=item['option_map'].get(a.get('answer')) if isinstance(a.get('answer'),str) else None
                status='missing' if not found else 'duplicate' if len(found)>1 else 'invalid' if meaning not in MEANINGS else 'ok'
                r=dict(context=ctx,reader=reader,item_id=iid,meaning=meaning,confidence=a.get('confidence'),note=a.get('note',''),
                       context_status=gate['status'],read_status=status,
                       vote_role='primary_eligible' if gate['status']=='VALID' else 'secondary_only' if gate['status']=='VOID' else 'unusable')
                byslot.setdefault(item['slot_id'],[]).append(r)
    return byslot,gates

def build(out=OUT):
    frame={r['slot_id']:r for r in rows(out/'frame_step1.jsonl') if r['partition']=='step1'}
    bed=rows(out/'step1_rendered_v3.jsonl')
    reads,gates=load_reads(out)
    assert set(reads)=={r['slot_id'] for r in bed}
    decisions=[decide(frame[r['slot_id']],reads[r['slot_id']]) for r in bed]
    assert all(len(r['reads'])==2 for r in decisions)
    (out/'decisions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in decisions))
    summary=dict(bed_slots=len(decisions),status=dict(Counter(r['status'] for r in decisions)),
                 truth_candidates=sum(r['truth_candidate'] is not None for r in decisions),
                 edit_candidates=sum(r['edit_candidate'] is not None for r in decisions),applied_edits=0,
                 reasons=dict(Counter(r['reason'] for r in decisions)),gates=gates,
                 policy='Two VALID reads required; VOID is secondary-only. Exact primary position thousands. Every raised call requires lead pixels. Edits are proposals only.',
                 rerun='Run n1_decide.py then n1_raised_sheets.py after r2; no reader is launched by either command.')
    dump(out/'decisions_summary.json',summary)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=OUT);p.add_argument('--v2',action='store_true')
    args=p.parse_args()
    if args.v2:
        from n1ts import phase1
        phase1()
    else: print(json.dumps(build(args.out),ensure_ascii=False,indent=2))
