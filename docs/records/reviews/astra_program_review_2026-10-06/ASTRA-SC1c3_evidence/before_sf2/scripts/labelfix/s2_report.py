"""Build print-based S2 tables, owner expectation receipt, fixed review selection."""
import sys,json,gzip
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from greekocr.labelfix.validate import load_three_way,DEV_BOOKS,lb95
from greekocr.labelfix.text import nfc
from greekocr.labelfix.linemetric import printed_words,score_slots,pooled
from greekocr.labelfix.spellcheck_validate import score_print
O=ROOT/'docs/labelfix/spellcheck'

def read(p):
    opener=gzip.open if str(p).endswith('.gz') else open
    with opener(p,'rt') as f:return [json.loads(x) for x in f]
def write(p,rs):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs))
def pc(x):return f'{x:.1%}' if x is not None else '—'
def units(ms):return sum(2 if k=='compound' else 1 if k!='dialytika' else 2 for k,v in ms)

def expectations(lines,notes):
    # Literal transcription of the owner's per-slot detector notes. No printed_field used.
    specs={
    '02a3a2a6-p000046-l0014':[(8,{'missed':1})],
    '177b717d-p000013-l0009':[(1,{'missed':2}),(13,{'missed':1})],
    '177b717d-p000097-l0007':[(19,{'false':'subscript_speck'})],
    '177b717d-p000097-l0010':[(2,{'missed':2}),(5,{'missed':1})],
    '2793d64c-p000048-l0010':[(6,{'false':'subscript_speck'})],
    '2793d64c-p000070-l0010':[(22,{'false':'ascender_delta'})],
    '2793d64c-p000070-l0014':[(10,{'false':'subscript_speck'}),(13,{'false':'subscript_speck'}),(12,{'false':'above_speck'})],
    '2793d64c-p000072-l0007':[(3,{'apostrophe':True})],
    '384c3f89-p000030-l0021':[(22,{'apostrophe':True})],
    '384c3f89-p000030-l0029':[(1,{'missed':1})],
    '384c3f89-p000053-l0021':[(10,{'missed':2}),(32,{'missed':1}),(22,{'apostrophe':True})],
    '384c3f89-p000053-l0028':[(25,{'missed':1})],
    '384c3f89-p000068-l0036':[(6,{'apostrophe':True}),(7,{'missed':2})],
    '384c3f89-p000121-l0024':[(18,{'apostrophe':True})],
    '384c3f89-p000205-l0005':[(1,{'missed':2}),(2,{'apostrophe':True}),(7,{'apostrophe':True})],
    '51fe7386-p000024-l0015':[(1,{'missed':1}),(2,{'missed':1}),(29,{'missed':2})],
    '51fe7386-p000024-l0020':[(k,{'missed':1}) for k in [6,8,11,20,37,39]]+[(23,{'false':'letter_part_subscript'})],
    '602cc72e-p000155-l0009':[(2,{'missed':2})]+[(k,{'missed':1}) for k in [11,12,16]],
    '602cc72e-p000167-l0027':[(k,{'missed':1}) for k in [1,6,10,14]],
    '8b6b0de9-p000004-l0028':[(2,{'missed':1}),(7,{'missed':2})],
    '8b6b0de9-p000008-l0001':[(12,{'missed':2}),(13,{'false':'ascender_delta'})],
    '8b6b0de9-p000008-l0019':[(17,{'missed':1})],
    '8b6b0de9-p000008-l0024':[(4,{'missed':1}),(18,{'missed':1})],
    '8b6b0de9-p000011-l0007':[(9,{'false':'subscript_speck'})],
    '8b6b0de9-p000011-l0014':[(13,{'missed':1})],
    '8b6b0de9-p000021-l0007':[(18,{'false':'faint_letter'})],
    '9c1dca9b-p000005-l0017':[(23,{'missed':1}),(27,{'missed':1})],
    '9c1dca9b-p000015-l0065':[(8,{'missed':1})]}
    for lid in ('02a3a2a6-p000046-l0025','8b6b0de9-p000008-l0002'):
        dots=[s for s in lines[lid]['slots'] if s['before_below']]
        slot=max(dots,key=lambda s:s['bbox'][0])['slot'] if dots else len(lines[lid]['slots'])
        specs[lid]=[(slot,{'false':'punctuation_dot'})]
    lid='8b6b0de9-p000007-l0030'
    candidates=[s for s in lines[lid]['slots'] if s['base']=='λ']
    slot=max(candidates,key=lambda s:s['before_below'])['slot']
    specs[lid]=[(slot,{'false':'subscript_speck'})]
    lid='2793d64c-p000048-l0004'
    eta=[s for s in lines[lid]['slots'] if s['base']=='η']
    specs[lid]=[(eta[-1]['slot'],{'missed':1})]
    out=[]
    for n in notes:
        lid=n['line_id']
        for slot,ex in specs.get(lid,[]):
            r=dict(line_id=lid,slot=slot,expected=ex,note=n['note'])
            if lid=='2793d64c-p000048-l0004':r['mark_kind']='subscript'
            if lid=='51fe7386-p000024-l0015' and slot in [1,2]:r.update(group_slots=[1,2],group_missed_total=3,interpretation='three marks across two slots; individual minimum one')
            if lid=='9c1dca9b-p000005-l0017':r.update(ambiguous=True,interpretation='qualitative blurry/merged note; missed count unspecified, minimum-one hypothesis only')
            if 'exclamation' in n['note']:r['slot_resolution']='rightmost slot carrying the baseline dot in the original detector; glyph pass may label the punctuation stem letter'
            s=next((s for s in lines[lid]['slots'] if s['slot']==slot),None)
            if s is None:r.update(before_fixed=False,fixed=False,status='not fixed: slot unavailable');out.append(r);continue
            def passes(ms,pre):
                if r.get('ambiguous'):return False
                if 'apostrophe' in ex:return ['apostrophe','apostrophe'] in ms
                if 'false' in ex:
                    kind=ex['false']
                    if 'subscript' in kind:return not any(k=='subscript' for k,v in ms)
                    if kind=='punctuation_dot':
                        bs=s['before_evidence' if pre else 'evidence']['below']
                        return not bs
                    return not any(k in ('accent','breathing','compound') for k,v in ms)
                if r.get('mark_kind')=='subscript':return any(k=='subscript' for k,v in ms)
                # Count is the owner's stated missing-mark minimum. Exact truth-set
                # matching additionally prevents credit for a wrong accent/breathing.
                if units(ms)<ex['missed']:return False
                if s['truth'] is not None and not set(map(tuple,s['truth']))<=set(map(tuple,ms)):return False
                if r.get('group_missed_total'):
                    return sum(units(q['before' if pre else 'detected']) for q in lines[lid]['slots'] if q['slot'] in r['group_slots'])>=r['group_missed_total']
                return True
            r.update(before_fixed=passes(s['before'],True),fixed=passes(s['detected'],False),
                     before=s['before'],after=s['detected'],truth=s['truth'],base=s['base'])
            r['status']='fixed' if r['fixed'] else 'not fixed'
            if s['truth'] is not None:
                t=s['truth'];conflict=False
                if 'missed' in ex:conflict=(not any(k=='subscript' for k,v in t)) if r.get('mark_kind')=='subscript' else units(t)<ex['missed']
                elif 'apostrophe' in ex:conflict=['apostrophe','apostrophe'] not in t
                elif 'subscript' in ex.get('false',''):conflict=any(k=='subscript' for k,v in t)
                r['note_truth_disagreement']=bool(conflict)
            else:r['note_truth_disagreement']=None
            out.append(r)
    return out


def main():
    metrics=json.loads((O/'S2_metrics.json').read_text());ll=read(O/'S2_lines.jsonl.gz');by={l['line_id']:l for l in ll}
    notes=read(O/'owner_notes_db_20261016.jsonl');ee=expectations(by,notes);write(O/'owner_slot_expectations.jsonl',ee)
    truth=json.loads((O/'print_truth_s0.json').read_text())
    old=[];new=[]
    for seed in (0,1):
        lines={l['line_id']:l for l in load_three_way(seed)}
        for dest,path in [(old,O/f'words_s{seed}.jsonl'),(new,O/'S2_engine'/f'words_s{seed}.jsonl')]:
            for r in read(path):
                score_print(r,printed_words(lines[r['line_id']],truth).get(r['word_index']));dest.append(r)
    # All decision-verdict flips for each iteration and both policies.
    flips=[]
    for iteration,rows in [('S1',old),('S2',new)]:
        for r in rows:
            for policy,dk,hk,pk in [('strict','decision','outcome','print_outcome'),('ratio','ratio_decision','ratio_outcome','ratio_print_outcome')]:
                if r[dk]['column'] and r[hk]!=r[pk]:flips.append(dict(iteration=iteration,policy=policy,seed=r['seed'],line_id=r['line_id'],word_index=r['word_index'],column=r[dk]['column'],google=r['google_nfc'],proposal=r[dk]['proposal'],human=r.get('human_nfc'),printed=r.get('printed_core'),human_verdict=r[hk],print_verdict=r[pk]))
    write(O/'S2_verdict_flips.jsonl',flips)
    changed=set()
    oldmap={(r['seed'],r['line_id'],r['word_index']):r for r in old}
    decision_changes=[]
    for r in new:
        b=oldmap.get((r['seed'],r['line_id'],r['word_index']))
        if b and b['decision']!=r['decision']:
            decision_changes.append(dict(seed=r['seed'],line_id=r['line_id'],word_index=r['word_index'],before=b['decision'],after=r['decision']))
            if r['seed']==0 and not r['dev']:changed.add(r['line_id'])
    write(O/'S2_decision_changes.jsonl',decision_changes)
    changed|={l['line_id'] for l in ll if not l['dev'] and any(s['before']!=s['detected'] or s['before_evidence']['above']!=s['evidence']['above'] or s['before_evidence']['below']!=s['evidence']['below'] for s in l['slots'])}
    sample=(O/'heldout_sample60.txt').read_text().splitlines();selected=sample+sorted(changed-set(sample))
    write(O/'S2_sheet_lines.jsonl',[dict(line_id=x) for x in selected[:140]])
    (O/'S2_sheet_overflow.txt').write_text('\n'.join(selected[140:])+'\n')
    def engine(rows,col,reference='print',stage='all',split='all',policy='strict'):
        dk='decision' if policy=='strict' else 'ratio_decision';ok=('print_outcome' if reference=='print' else 'outcome')
        if policy=='ratio':ok='ratio_'+ok
        rs=[r for r in rows if r[dk]['column']==col and (stage=='all' or r['stage' if policy=='strict' else 'ratio_stage']==stage) and (split=='all' or r['dev']==(split=='dev'))]
        cc=Counter(r[ok] for r in rs);n=sum(v for k,v in cc.items() if k!='unknown')
        return dict(n=len(rs),correct=cc['correct'],wrong=cc['google_right']+cc['both_wrong'],unknown=cc['unknown'],precision=cc['correct']/n if n else None,lb=lb95(cc['correct'],n))
    ma,mh=engine(new,'ACCEPT'),engine(new,'HOLD');counts=Counter(r['decision']['column'] for r in new)
    metrics['engine_header']=f"ACCEPT {counts['ACCEPT']} / HOLD {counts['HOLD']} / L2 ACCEPT {sum(r['stage']=='L2' and r['decision']['column']=='ACCEPT' for r in new)} (both seeds); false corrections vs known print {ma['wrong']}; HOLD contradicts known print {mh['wrong']}/{mh['n']-mh['unknown']}."
    (O/'S2_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    L=['# S2 — mark detector and PRINT truth','',f"Iteration `{metrics['iteration']}`. CPU; network off; **0 CTC forward passes**. 1,264 seed-0 lines, frozen 666 held-out lines from 14 non-DEV books. Classifier choices and second-pass detector adjustments used DEV only. Old model, input labels, truth, alignment caches and S1 artifacts preserved.",'',
    'The recogniser only locates input characters. Google = human = recogniser cores establish agreement truth; the 189 adjudications override those words; null/other disagreements are UNKNOWN. No owner `printed_field` is used. Unmatched/competing letter-component ownership is UNKNOWN. The two seeds reuse the same images; pooled engine confidence bounds describe observations, not independent images. S1 baseline classifier originally used these held-out books for calibration, so before/after is a frozen-book comparison, not a newly untouched baseline.', '',
    '## Whole-line metrics','', 'Each letter component sorted by x is a slot. Exact accent/breathing identities are compared; fused breathing+accent is one compound kind, subscript separate, apostrophe separate. A physical blob classified none is retained as an unclassified false mark. The class prediction is diagnostic argmax (no confidence filtering); engine decisions use tau. UNKNOWN slots are counted and excluded.', '', '| set | iteration | known slots | unknown slots | TP | FP | FN | precision | recall | F1 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for label,sub in [('held-out',[l for l in ll if not l['dev']]),('owner 33',[by[n['line_id']] for n in notes])]:
        for name,key in [('before','before_metric'),('after','metric')]:
            m=pooled([l[key] for l in sub])['total'];L.append(f"| {label} | {name} | {m.get('known_slots',0)} | {m.get('unknown_slots',0)} | {m.get('tp',0)} | {m.get('fp',0)} | {m.get('fn',0)} | {pc(m['precision'])} | {pc(m['recall'])} | {pc(m['f1'])} |")
    L+=['','| mark kind | before P | after P | before R | after R |','|---|---:|---:|---:|---:|']
    for k,b in metrics['before']['by_kind'].items():
        a=metrics['after']['by_kind'][k];L.append(f"| {k} | {pc(b['precision'])} | {pc(a['precision'])} | {pc(b['recall'])} | {pc(a['recall'])} |")
    L+=['','## Failure-class strata','', 'Operational, overlapping strata below describe observable exposure, not a claim that every error has a proven physical cause. Full per-slot evidence and per-line P/R/F1: `S2_lines.jsonl.gz`.', '', '| failure class / slot exposure | slots | before P/R | after P/R |','|---|---:|---|---|']
    checks={
      '(a) ascender/capital':lambda s:s['base'] in 'δβλθφξζ' or s['base'].isupper(),
      '(b) old below blob, no printed subscript':lambda s:s['before_below'] and not any(k=='subscript' for k,v in (s['truth'] or [])),
      '(c) printed apostrophe':lambda s:any(k=='apostrophe' for k,v in (s['truth'] or [])),
      '(c2) descender with old below blob':lambda s:s['base'] in 'ρφψχγμζξς' and s['before_below'],
      '(d) faint candidate':lambda s:any(b.get('faint') for b in s['before_evidence']['above']+s['before_evidence']['below']),
      '(e) printed compound':lambda s:any(k=='compound' for k,v in (s['truth'] or []))}
    for label,test in checks.items():
        ss=[s for l in ll if not l['dev'] for s in l['slots'] if test(s)];b=score_slots([dict(s,detected=s['before']) for s in ss])['total'];a=score_slots(ss)['total']
        L.append(f"| {label} | {len(ss)} | {pc(b['precision'])}/{pc(b['recall'])} | {pc(a['precision'])}/{pc(a['recall'])} |")
    L+=['','## Agreement-set false marks by unmarked letter','', 'Rate = slots with any above blob / agreement slots with no printed marks. This table includes all books for reporting; held-out did not set thresholds.', '', '| letter | slots | before | after | before rate | after rate |','|---|---:|---:|---:|---:|---:|']
    for k,c in sorted(metrics['ascender'].items()):L.append(f"| {k} | {c['n']} | {c['before']} | {c['after']} | {pc(c['before']/c['n'])} | {pc(c['after']/c['n'])} |")
    aa=[c for k,c in metrics['ascender'].items() if k in 'δβλθφξζ' or k=='capitals'];an=sum(c['n'] for c in aa);ab=sum(c['before'] for c in aa)/an;az=sum(c['after'] for c in aa)/an
    L+=['','## Classifier','',metrics['training_policy']+f". tau={metrics['tau']}. {metrics['samples']} new agreement samples; old file {metrics['old_samples']}; matched {metrics['paired']}, changed feature vectors {metrics['changed_features']}, changed blob composition {metrics['changed_composition']} on the new sample population, labels changed {metrics['labels_changed']}. Sample IDs include word index and cluster for future exact matching; old samples lack these IDs so old/new matching uses occurrence order within (line, word, base, class).",'',
    f"Training collection inspected: {metrics['train_dev_lines']} DEV-book lines, {metrics['train_cached']} cached. No extra training samples admitted: no eligible cached training alignments/recorded recogniser agreement. Single-vowel Google-only labels would not meet the agreement requirement. Twelve compound classes are represented in the model schema, but several have **zero independent fitting examples**. This requirement remains incomplete; absent classes cannot be claimed learned.",'',
    '| class | fit | DEV calibration | held-out | held-out recall | precision at tau | prediction coverage |','|---|---:|---:|---:|---:|---:|---:|']
    for k,c in metrics['per_class'].items():L.append(f"| {k} | {c['fit']} | {c['dev_calibration']} | {c['held']} | {pc(c['recall'])} | {pc(c['precision_at_tau'])} | {pc(c['coverage'])} |")
    L+=['','## Owner expectations','', 'Literal notes are retained below and in `owner_slot_expectations.jsonl`. `missed` counts are minimum missing units; compounds carry two units. Fixed also requires all known printed marks at that slot. Qualitative blurry notes stay unresolved. The three marks across slots 1/2 are checked as a group. No-note card has no invented expectation. A note/truth conflict is reported without adjudicating it; alignment/slot mismatch is also a possible cause.', '', '| line | slot | expectation | before → after | truth conflict | owner note |','|---|---:|---|---|---|---|']
    for n in notes:
        es=[e for e in ee if e['line_id']==n['line_id']]
        if not es:L.append(f"| {n['line_id']} | — | no expectation | — | — | {n['note']} |")
        for e in es:L.append(f"| {e['line_id']} | {e['slot']} | {json.dumps(e['expected'])} | {'fixed' if e['before_fixed'] else 'not fixed'} → {e['status']} | {e.get('note_truth_disagreement')} | {e['note']} |")
    L+=['','Owner per-line exact metrics (including all visible slots):','','| line | before P/R/F1 | after P/R/F1 | known/unknown slots |','|---|---|---|---|']
    for n in notes:
        l=by[n['line_id']];b=l['before_metric']['total'];a=l['metric']['total'];L.append(f"| {l['line_id']} | {pc(b['precision'])}/{pc(b['recall'])}/{pc(b['f1'])} | {pc(a['precision'])}/{pc(a['recall'])}/{pc(a['f1'])} | {a.get('known_slots',0)}/{a.get('unknown_slots',0)} |")
    L+=['','## S1 engine rescoring','', 'S1 policy/proposal code is retained except the compound-compatible count check, new extractor and new classifier. ACCEPT and HOLD remain separate. Both seeds re-run by `spellcheck_validate`; raw rows and receipt in `S2_engine/`. Original S1 rows are scored both ways without rewriting them. Unknown print words remain excluded. HOLD contradicts print whenever its proposal differs from known print; this includes Google-right and both-wrong.', '', '| iteration | seed | policy | split | stage | column | reference | decided | correct | wrong | unknown | precision | LB95 |','|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for iteration,rows in [('S1',old),('S2',new)]:
      for seed in (0,1,'both'):
       rr=rows if seed=='both' else [r for r in rows if r['seed']==seed]
       for policy in ('strict','ratio'):
        for split in ('dev','held-out','all'):
         for stage in ('D1','D2','L1','L2','all'):
          for col in ('ACCEPT','HOLD'):
           for ref in ('human','print'):
            m=engine(rr,col,ref,stage,split,policy);L.append(f"| {iteration} | {seed} | {policy} | {split} | {stage} | {col} | {ref} | {m['n']} | {m['correct']} | {m['wrong']} | {m['unknown']} | {pc(m['precision'])} | {pc(m['lb'])} |")
    L+=['','## Every human → print decision verdict flip','','| iteration | policy | seed | line / word | column | Google → proposal | human → print verdict | printed |','|---|---|---:|---|---|---|---|---|']
    for f in flips:L.append(f"| {f['iteration']} | {f['policy']} | {f['seed']} | {f['line_id']} / {f['word_index']} | {f['column']} | {f['google']} → {f['proposal']} | {f['human_verdict']} → {f['print_verdict']} | {nfc(f['printed']) if f['printed'] else 'UNKNOWN'} |")
    L+=['','## Crops and review selection','',f"Fixed seed-20261016 sample: `heldout_sample60.txt`; 60 cards plus changed held-out detection/decisions, total eligible {len(selected)}, capped at 140. Remaining {max(0,len(selected)-140)} IDs in `S2_sheet_overflow.txt`. Only HTML is built; no db collection/document was touched. Existing 33 notes are displayed. The save script now writes printed text only after a real input event (`printed_edited: true`) and merges note-only updates.",'',
    'Before/after crop witnesses (same native pixels; old/new detector evidence and bounding boxes in `S2_lines.jsonl.gz`; embedded annotated images in the owner sheet for selected lines):','']
    for n in notes:L.append(f"- `{n['line_id']}`: [paired before/after crop](crops_S2/{n['line_id']}.png); native `{by[n['line_id']]['crop']}`")
    compound=metrics['after']['by_kind']['compound']['recall'];b=metrics['before']['total'];a=metrics['after']['total']
    final=f"S2 RESULT: held-out line mark P {pc(b['precision'])}→{pc(a['precision'])} R {pc(b['recall'])}→{pc(a['recall'])} (owner 33-line expectations fixed {sum(e['fixed'] for e in ee)}/{len(ee)}); ascender false-mark rate {pc(ab)}→{pc(az)}; compound recall {pc(compound)}; S1 ACCEPT vs print p={pc(ma['precision'])} (LB95 {pc(ma['lb'])}), HOLD vs print p={pc(mh['precision'])}"
    L+=['','## Validation and open work','',
    'Synthetic detector/compound/two-line metric cases pass. Existing labelfix tests: all runnable tests pass; one localhost capture test cannot bind under the sandbox (PermissionError). Test evidence: `S2_verification.json`; 109 tests passed, the existing socket test was separately observed to fail at bind and then deselected. The actual notes JavaScript was exercised with an in-memory db stub: a note-only save omits printed/printed_edited, an edited printed field sets printed_edited=true, and updates merge without replacing existing fields. Rare compound sample support is insufficient; zero-sample classes are explicit. The owner case `384c3f89-p000096-l0004` (ᾗσι) remains unrecovered: its dasia+circumflex+subscript class has zero fitting examples. Two note/truth conflicts are retained (slot 8 on 02a3a2a6-p000046-l0014; slot 13 on 177b717d-p000013-l0009). Physical masks are unchanged; the stricter subscript rule can lose attached or borderline genuine subscripts by design. Owner slot-truth conflicts and unmapped slots remain open. This iteration is a measured candidate, not an accepted replacement.', '',final]
    (O/'S2_REPORT.md').write_text('\n'.join(L)+'\n');print(final)
if __name__=='__main__':main()
