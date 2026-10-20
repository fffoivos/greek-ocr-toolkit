"""S3 print-based report, v8 owner accounting, regression list and sheet selection."""
from greekocr.ops.data_root import input_path as _data_input
import gzip, json
from collections import Counter
from pathlib import Path
from greekocr.labelfix.linemetric import pooled, score_slots
from greekocr.labelfix.owner_slots import overlap_slots
from greekocr.labelfix.validate import lb95
O=Path('docs/records/labelfix/spellcheck')


def read(p):
    with (gzip.open if str(p).endswith('.gz') else open)(_data_input(p),'rt') as f:return [json.loads(x) for x in f]


def write(p,rs):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs))
def pc(x):return f'{x:.1%}' if x is not None else '—'
def units(ms):return sum(2 if k in ('compound','dialytika') else 1 for k,v in ms)


def passes(e,s,lines,pre):
    if s is None or e.get('ambiguous'):return False
    ex=e['expected'];ms=s['before' if pre else 'detected'];ev=s['before_evidence' if pre else 'evidence']
    if 'apostrophe' in ex:return ['apostrophe','apostrophe'] in ms
    if 'false' in ex:
        if 'subscript' in ex['false']:return 'subscript' not in s.get('unknown_kinds',[]) and not any(k=='subscript' for k,v in ms)
        if ex['false']=='punctuation_dot':return not ev['below']
        return not any(k in ('accent','breathing','compound') for k,v in ms)
    if e.get('mark_kind')=='subscript':return 'subscript' not in s.get('unknown_kinds',[]) and any(k=='subscript' for k,v in ms)
    if units(ms)<ex['missed']:return False
    if s['truth'] is not None and not set(map(tuple,s['truth']))<=set(map(tuple,ms)):return False
    if e.get('group_missed_total'):
        return sum(units(q['before' if pre else 'detected']) for q in lines if q['slot'] in e['mapped_group_slots'])>=e['group_missed_total']
    return True


def owner_accounting(by):
    ee=read(O/'owner_slot_expectations.jsonl');v8=json.loads((O/'owner_v8_slots.json').read_text())['lines']
    for e in ee:
        ss=by[e['line_id']]['slots'];e['mapped_slot'],e['overlapping_slots']=overlap_slots(e['v8_x0'],e['v8_x1'],ss)
        s=next((s for s in ss if s['slot']==e['mapped_slot']),None)
        e['mapped_group_slots']=[]
        for slot in e.get('group_slots',[]):
            b=next(q['bbox'] for q in v8[e['line_id']] if q['slot']==slot)
            q,_=overlap_slots(b[0],b[2],ss);e['mapped_group_slots'].append(q)
        e['s2_fixed']=passes(e,s,ss,True);e['fixed']=passes(e,s,ss,False);e['before_fixed']=e['s2_fixed']
        e['status']='fixed' if e['fixed'] else 'not fixed'
        if s is None:e['cause']='unresolved x-overlap mapping';continue
        e.update(before=s['before'],after=s['detected'],truth=s['truth'],base=s['base'])
        b,a=s['before_evidence'],s['evidence']
        if e.get('ambiguous'):cause='qualitative blurry/merged note; no invented count'
        elif e['expected'].get('false'):cause='false '+e['expected']['false']+(' rejected' if e['fixed'] else ' remains')
        elif e['expected'].get('apostrophe'):cause='elision window/word-final eligibility'
        elif e.get('mark_kind')=='subscript':cause='below-baseline size/position or connected wedge'
        elif s['base'] not in 'αεηιουωΑΕΗΙΟΥΩρΡ':cause='non-vowel range; leading elision is not a vowel accent'
        elif a['meanline']-b['meanline']>.15*b['xh']:cause='mean-line/x-height included joined mark; body band corrected'
        elif b['diagnostics']:cause='joined vowel mark rejected by S2 ascender neck rule'
        elif any(z['faint'] for z in b['above']):cause='faint ink'
        elif not b['above'] and a['above']:cause='window/vertical eligibility or split-vowel union'
        elif b['above']:cause='classifier identity/compound support'
        else:cause='mark merged inside body or outside recoverable window'
        e['cause']=cause
        if s['truth'] is not None:
            t=s['truth'];ex=e['expected']
            conflict=units(t)<ex['missed'] if 'missed' in ex else False
            if e.get('mark_kind')=='subscript':conflict=not any(k=='subscript' for k,v in t)
            if 'apostrophe' in ex:conflict=['apostrophe','apostrophe'] not in t
            e['note_truth_disagreement']=conflict
    write(O/'owner_slot_expectations.jsonl',ee)
    return ee


def engine(rows,col,stage='all',dev=None,policy='strict'):
    dk='decision' if policy=='strict' else 'ratio_decision';ok='print_outcome' if policy=='strict' else 'ratio_print_outcome';sk='stage' if policy=='strict' else 'ratio_stage'
    ss=[r for r in rows if r[dk]['column']==col and (stage=='all' or r[sk]==stage) and (dev is None or r['dev']==dev)]
    c=Counter(r[ok] for r in ss);n=len(ss)-c['unknown'];correct=c['correct']
    return dict(n=len(ss),known=n,correct=correct,wrong=c['google_right']+c['both_wrong'],unknown=c['unknown'],precision=correct/n if n else None,lb95=lb95(correct,n))


def main():
    m=json.loads((O/'S3_metrics.json').read_text());ls=read(O/'S3_lines.jsonl.gz');by={l['line_id']:l for l in ls};held=[l for l in ls if not l['dev']]
    # Headline recall includes abstentions on known printed positives. Removing
    # cut-off positives would inflate subscript recall by changing its support.
    m['observable_scope']=dict(before=pooled([score_slots([dict(s,detected=s['before']) for s in l['slots']]) for l in held]),after=pooled([score_slots(l['slots']) for l in held]))
    for l in ls:
        l['before_metric']=score_slots([dict(s,detected=s['before'],unknown_kinds=[]) for s in l['slots']])
        l['metric']=score_slots([dict(s,detected=[x for x in s['detected'] if x[0] not in s.get('unknown_kinds',[])],unknown_kinds=[]) for s in l['slots']])
    m['before']=pooled([l['before_metric'] for l in held]);m['after']=pooled([l['metric'] for l in held])
    m['per_book']={d:dict(before=pooled([l['before_metric'] for l in held if l['doc']==d]),after=pooled([l['metric'] for l in held if l['doc']==d])) for d in sorted({l['doc'] for l in held})}
    # Match S2's agreement-only ascender population exactly.
    from greekocr.labelfix.validate import load_three_way
    from greekocr.labelfix.candidates import pair_tokens
    from greekocr.labelfix.text import tokenize
    sources={l['line_id']:l for l in load_three_way(0)}
    eligible=[]
    for l in ls:
        source=sources[l['line_id']];gs=tokenize(source['google']);gm={g.index:q for g,q in pair_tokens(source['google'],source['model'])};gh={g.index:q for g,q in pair_tokens(source['google'],source['human'])}
        for s in l['slots']:
            wi=s['word']
            if wi is None or not gm.get(wi) or not gh.get(wi) or not(gs[wi].core==gm[wi].core==gh[wi].core):continue
            if s['truth']==[] and (s['base'] in 'δβλθφξζ' or s['base'].isupper()):eligible.append((l,s))
    m['ascender']={split:dict(n=len(ss),before=sum(bool(s['before_above']) for s in ss),after=sum(bool(s['above']) for s in ss)) for split,ss in [('all',[s for l,s in eligible]),('held-out',[s for l,s in eligible if not l['dev']])]}
    ee=owner_accounting(by);notes=read(O/'owner_notes_db_20261016.jsonl');owner_ids=[n['line_id'] for n in notes];owner=[by[x] for x in owner_ids]
    erows={it:[r for seed in (0,1) for r in read(O/d/f'words_s{seed}.jsonl')] for it,d in [('S2','S2_engine'),('S3','S3_engine')]}
    original=[r for seed in (0,1) for r in read(O/f'words_s{seed}.jsonl')]
    # Re-score S1 outputs with the same authoritative print words, retaining rows.
    from greekocr.labelfix.validate import load_three_way
    from greekocr.labelfix.linemetric import printed_words
    from greekocr.labelfix.spellcheck_validate import score_print
    truth=json.loads((O/'print_truth_s0.json').read_text());pw={seed:{l['line_id']:printed_words(l,truth) for l in load_three_way(seed)} for seed in (0,1)}
    for r in original:score_print(r,pw[r['seed']][r['line_id']].get(r['word_index']))
    erows={'S1 original':original,**erows}
    m['engine']={it:{col:engine(rs,col) for col in ('ACCEPT','HOLD')} for it,rs in erows.items()}
    m['owner_before']=pooled([l['before_metric'] for l in owner]);m['owner_after']=pooled([l['metric'] for l in owner]);m['owner_fixed']=sum(e['fixed'] for e in ee);m['owner_s2_fixed']=sum(e['s2_fixed'] for e in ee)
    changed=[]
    for l in held:
        if any(s['before']!=s['detected'] or s['before_evidence']['above']!=s['evidence']['above'] or s['before_evidence']['below']!=s['evidence']['below'] for s in l['slots']):changed.append(l['line_id'])
    sample=(O/'heldout_sample60.txt').read_text().splitlines();eligible=list(dict.fromkeys(sample+sorted(changed)))
    section2=[x for x in eligible if x not in owner_ids]
    write(O/'S3_sheet_lines.jsonl',[dict(line_id=x) for x in owner_ids+section2[:140]])
    (O/'S3_sheet_overflow.txt').write_text('\n'.join(section2[140:])+('\n' if section2[140:] else ''))
    write(O/'S3_changed_lines.jsonl',[dict(line_id=x) for x in changed])
    regress=[]
    def compare(label,b,a,higher=True):
        if b is not None and a is not None and (a<b-1e-12 if higher else a>b+1e-12):regress.append(f'{label} {pc(b)}→{pc(a)}')
    for k in ('total',):
        for metric in ('precision','recall','f1'):compare('held-out '+metric,m['before'][k][metric],m['after'][k][metric])
    for kind,b in m['before']['by_kind'].items():
        for metric in ('precision','recall','f1'):compare(kind+' '+metric,b[metric],m['after']['by_kind'][kind][metric])
    for metric in ('precision','recall','f1'):compare('owner whole-line '+metric,m['owner_before']['total'][metric],m['owner_after']['total'][metric])
    for book,b in m['per_book'].items():
        for metric in ('precision','recall'):compare(book+' subscript '+metric,b['before']['by_kind']['subscript'][metric],b['after']['by_kind']['subscript'][metric])
    sp=m['speck'];compare('speck rejection',sp['before_rejected']/sp['n'] if sp['n'] else None,sp['after_rejected']/sp['n'] if sp['n'] else None)
    for split,c in m['ascender'].items():compare(split+' ascender false',c['before']/c['n'],c['after']/c['n'],False)
    for col in ('ACCEPT','HOLD'):
        compare('engine '+col+' precision',m['engine']['S2'][col]['precision'],m['engine']['S3'][col]['precision'])
    m['regressions']=regress;m['regression_header']='Regressions: '+('; '.join(regress) if regress else 'none in the reported S2 comparisons')+'.'
    m['engine_header']=f"Owner expectations fixed {m['owner_s2_fixed']}/59 → {m['owner_fixed']}/59 (v8 mapping). Subscript recall {pc(m['before']['by_kind']['subscript']['recall'])} → {pc(m['after']['by_kind']['subscript']['recall'])}."
    (O/'S3_metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    L=['# S3 — recall candidate; precision goal not met','',
       f"CPU only, network off, zero CTC forward passes. {m['dev_lines']} DEV lines fit/calibrate; {m['heldout_lines']} lines from 14 frozen held-out books evaluate only. HEAD observed `{m['head'][:8]}` (two brief-only commits beyond requested 4a3ace67). No git writes; all changes remain in this worktree.",'',
       'Print truth is unchanged: `print_truth_s0.json` plus three-way agreement words. The recogniser locates base letters only. Whole visible lines are scored; unknown words and competing character owners stay unknown. S2 outputs/model/artifacts are preserved. The first candidate failed DEV precision (83.98%); DEV-only inspection rejected right-hand eta descenders and whole unmarked bodies. Final classifier and geometric rules were frozen before reading final held-out results. No held-out thresholds or samples were fitted.', '',
       'Changes: vowel-relative subscripts use 0.25–0.9 x-height, ink-band darkness, under-body position with 0.3 x-height slack; touching wedges must leave the left half. Thin punctuation runs, neighbouring descenders, specks and border ink are rejected. Bottom-edge ink is UNKNOWN for subscript presence, not an absent subscript. Joined vowel top lobes do not need a consonant-style neck; complete short bodies cannot supply a lobe. A short-body height mode repairs overestimated bands. Non-vowel ink remains diagnostic (rho may carry breathing). A CTC span crossing two components of at most 1.6 x-height uses their union; whole-line scoring refuses a union with another known character owner. Twelve compound classes remain explicit; no samples were invented.', '',
       '## Whole-line metrics','',
       'Headline recall retains ALL known printed positives, including abstained cut-off subscripts. An UNKNOWN prediction is not an assertion of absence, but cannot earn a recall hit. Conditional recall on fully observable slots is shown separately; it must not replace the 94-positive subscript denominator. Mark identities are exact; nonempty unclassified blobs count as errors. Classifier argmax is diagnostic; engine decisions retain calibrated tau.', '',
       '| population | detector | known / unknown slots | TP / FP / FN | P | R | F1 |','|---|---|---:|---:|---:|---:|---:|']
    raw=json.loads((O/'S2_metrics.json').read_text())['after']['total']
    for pop,it,c in [('held-out (original scope)','S2 frozen',raw),('held-out (all known print)','S2',m['before']['total']),('held-out (all known print)','S3',m['after']['total']),('owner 33','S2',m['owner_before']['total']),('owner 33','S3',m['owner_after']['total'])]:
        L.append(f"| {pop} | {it} | {c.get('known_slots',0)} / {c.get('unknown_slots',0)} | {c['tp']} / {c['fp']} / {c['fn']} | {pc(c['precision'])} | {pc(c['recall'])} | {pc(c['f1'])} |")
    obs=m['observable_scope'];L+=['',f"Bottom-clipped subscript slots: {obs['after']['total'].get('unknown_subscript_slots',0)} held-out, counted separately from unknown word/slot ownership. Fully observable subscript recall (47 known positives): {pc(obs['before']['by_kind']['subscript']['recall'])} → {pc(obs['after']['by_kind']['subscript']['recall'])}. This conditional result excludes 47 of 94 printed positives; headline recall does not.", '', '| kind | S2 P | S3 P | S2 R | S3 R | S2 F1 | S3 F1 |','|---|---:|---:|---:|---:|---:|---:|']
    for k,b in m['before']['by_kind'].items():
        a=m['after']['by_kind'][k];L.append(f"| {k} | {pc(b['precision'])} | {pc(a['precision'])} | {pc(b['recall'])} | {pc(a['recall'])} | {pc(b['f1'])} | {pc(a['f1'])} |")
    L+=['','## Subscripts and specks side by side','', '| population | S2 subscript recall | S3 subscript recall | S2 speck rejection | S3 speck rejection |','|---|---:|---:|---:|---:|',f"| held-out | {pc(m['before']['by_kind']['subscript']['recall'])} | {pc(m['after']['by_kind']['subscript']['recall'])} | {sp['before_rejected']}/{sp['n']} = {pc(sp['before_rejected']/sp['n'])} | {sp['after_rejected']}/{sp['n']} = {pc(sp['after_rejected']/sp['n'])} |",'',
       'Speck exposure is the S2 operational stratum: known non-subscript slots with an S1 below blob, excluding cut-off evidence. It includes descenders/noise; it is not a newly adjudicated pure-speck population.', '',
       '| held-out book | true subscripts | S2 P / R | S3 P / R |','|---|---:|---|---|']
    for book,b in m['per_book'].items():
        z,a=b['before']['by_kind']['subscript'],b['after']['by_kind']['subscript'];L.append(f"| {book} | {z['tp']+z['fn']} | {pc(z['precision'])} / {pc(z['recall'])} | {pc(a['precision'])} / {pc(a['recall'])} |")
    L+=['','## Ascender false marks','', '| population | eligible unmarked slots | S2 false | S3 false |','|---|---:|---:|---:|']
    for split,c in m['ascender'].items():L.append(f"| {split} | {c['n']} | {c['before']} ({pc(c['before']/c['n'])}) | {c['after']} ({pc(c['after']/c['n'])}) |")
    L+=['','## Owner slots and missed-mark causes','',
       'Both old modules were recovered with `git show 153ff82e:...` and imported from a temporary `owner_v8` package outside greekocr. `owner_v8_slots.json` stores every old letter box; `owner_slot_expectations.jsonl` pins v8_x0/v8_x1 and maps by unique maximum overlap (ties/unavailable ranges abstain). The modules yield identical letter-component boxes to S2 on all 33 supplied crops: **zero actual renumberings**. The requested example cannot honestly be relabelled 8→9: old slot 8 is x=362–403, mapped to current slot 8, whose input base is β. The crop has a leading elision sign before β; that is an unresolved punctuation/expectation mismatch, not a fabricated vowel accent. A fixture with an inserted slot verifies renumbering by overlap.', '',
       f"S2 corrected accounting: {m['owner_s2_fixed']}/59; S3: {m['owner_fixed']}/59. Qualitative blurry notes remain unresolved. Every expectation is shown below, and every owner card has the fixed count and both slot identities. No-note card remains 0/0.", '',
       '| line | v8 slot [x0,x1) → current | expectation | S2 → S3 | physical cause / remaining limitation |','|---|---|---|---|---|']
    for e in ee:L.append(f"| {e['line_id']} | {e['v8_slot']} [{e['v8_x0']},{e['v8_x1']}) → {e['mapped_slot']} | {json.dumps(e['expected'],ensure_ascii=False)} | {'fixed' if e['s2_fixed'] else 'not fixed'} → {'fixed' if e['fixed'] else 'not fixed'} | {e['cause']} |")
    L+=['','Owner whole-line metrics (all visible slots):','', '| line | S2 P/R/F1 | S3 P/R/F1 |','|---|---|---|']
    for l in owner:
        b,a=l['before_metric']['total'],l['metric']['total'];L.append(f"| {l['line_id']} | {pc(b['precision'])}/{pc(b['recall'])}/{pc(b['f1'])} | {pc(a['precision'])}/{pc(a['recall'])}/{pc(a['f1'])} |")
    L+=['','## Compound support','', 'No recogniser passes or agreement harvesting were performed. Counts describe existing DEV fitting/calibration examples and known held-out component-slot truths, not independent newly labelled samples.', '', '| compound class | fit | DEV calibration | held-out slots | exact recovered |','|---|---:|---:|---:|---:|']
    for cls,c in m['per_class'].items():
        if ('psili' in cls or 'dasia' in cls) and any(a in cls for a in ('acute','grave','circumflex')):L.append(f"| {cls} | {c['fit']} | {c['dev_calibration']} | {c['held_slots']} | {c['held_exact']} |")
    L+=['','## S1 engine re-scored against print','', 'The original S1 outputs are re-scored; the same S1 engine is also run with S2 and S3 extraction/classifiers. Both seeds reuse crops and are not independent image observations. Strict and ratio policies retain separate columns. Full rows/receipts are in S3_engine/.', '', '| detector | policy | split | stage | column | decided | correct | wrong | unknown | print P | LB95 |','|---|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for it,rs in erows.items():
        for policy in ('strict','ratio'):
            for split,dv in [('all',None),('held-out',False),('DEV',True)]:
                for stage in ('all','L2'):
                    for col in ('ACCEPT','HOLD'):
                        c=engine(rs,col,stage,dv,policy);L.append(f"| {it} | {policy} | {split} | {stage} | {col} | {c['n']} | {c['correct']} | {c['wrong']} | {c['unknown']} | {pc(c['precision'])} | {pc(c['lb95'])} |")
    L+=['','## Sheet and validation','',f"`sheets/owner_iter_S3.html` uses sheet_build.py; CSS and notes JavaScript are unchanged. Section 1: 33 owner lines. Section 2: fixed sample60 plus changed held-out lines, unique line IDs, capped at 140 non-owner cards. {len(changed)} held-out detections changed; {len(section2[:140])} section-2 cards; {len(section2[140:])} overflow IDs in S3_sheet_overflow.txt. Some fixed-sample lines may already appear in section 1, never twice.",'',
       'New regression tests cover subscript stroke/speck/darkness/connected/cutoff, split-eta union and v8 overlap mapping. The existing capture test cannot bind a localhost socket in this sandbox, as in S2. Exact test results and artifact/notes-script checks are in S3_verification.json. This environmental test remains unverified; no all-tests-green claim is made.', '',m['regression_header'],'']
    b,a=m['before']['total'],m['after']['total'];asc=m['ascender']['all'];en=m['engine']['S3']['ACCEPT']
    final=f"S3 RESULT: held-out P {pc(b['precision'])}→{pc(a['precision'])} R {pc(b['recall'])}→{pc(a['recall'])}; subscript R {pc(m['before']['by_kind']['subscript']['recall'])}→{pc(m['after']['by_kind']['subscript']['recall'])}; owner expectations fixed {m['owner_fixed']}/59 (v8 mapping; S2 was {m['owner_s2_fixed']}/59); ascender false {pc(asc['before']/asc['n'])}→{pc(asc['after']/asc['n'])}; S1 ACCEPT vs print p={pc(en['precision'])}; regressions: {'; '.join(regress) if regress else 'none'}"
    (O/'S3_REPORT.md').write_text('\n'.join(L+[final])+'\n');print(final)


if __name__=='__main__':main()
