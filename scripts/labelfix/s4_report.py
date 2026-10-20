"""Build S4 receipts and owner-note expectations; never build/publish a sheet."""
from greekocr.ops.data_root import input_path as _data_input
import gzip
import json
from pathlib import Path
from collections import Counter
from greekocr.labelfix.linemetric import score_slots, pooled
from greekocr.labelfix.owner_slots import overlap_slots
from greekocr.labelfix.markshape import load_model
from greekocr.labelfix.text import nfd, tokenize, clusters
from scripts.labelfix.s3_report import passes

O=Path('docs/records/labelfix/spellcheck')


def read(p):
    with (gzip.open if str(p).endswith('.gz') else open)(_data_input(p),'rt') as f:
        return [json.loads(x) for x in f]


def write(p,rows):
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))


def pc(x):
    return f'{x:.1%}' if x is not None else '—'


def units(ms):
    return sum(2 if k in ('compound','dialytika') else 1 for k,v in ms)


# Explicit transcription of all clauses, including unresolved qualitative ones.
# (kind, component slot, minimum printed mark count / base / word).
SPECS=[
 [('mark',1,1),('mark',17,1)], [('mark',17,1)],
 [('quote',1,None),('mark',1,2)], [('leading_sign',1,None),('named',23,None)],
 [('mark',16,1),('apostrophe',29,None)], [('no_regression',None,None)],
 [('apostrophe',27,None)], [('whole_marks',None,None)], [('no_regression',None,None)],
 [('apostrophe',14,None)], [('mark',15,2)], [('no_regression',None,None)],
 [('apostrophe',4,None)], [('apostrophe',34,None),('mark',35,2)],
 [('mark',9,1)], [('no_regression',None,None)], [('subscript',21,None)],
 [('mark',6,2),('mark',11,1),('mark',36,1)],
 [('mark',1,1),('mark',25,1),('mark',12,1)],
 [('mark',6,1),('mark',10,1),('mark',14,1)],
 [('ambiguous',None,'missed at 2 at 6: slot/count syntax unresolved')],
 [('mark',1,1),('mark',4,1),('mark',18,1)],
 [('word_slots',None,'στω'),('word_accent',None,'ω')],
 [('mark',9,1),('word_slots',None,'εις')], [('mark',17,1)],
 [('mark',9,1),('mark',11,1)], [('mark',13,1)], [('mark',17,1)],
 [('base',7,'ρ'),('base',21,'ρ')], [('mark',2,1),('union_base',[6,7],'λ')],
 [('mark',2,1)], [('mark',10,1)], [('mark',9,1)],
]


def same(a,b):
    return set(map(tuple,a))==set(map(tuple,b))


def new_expectations(by,s2,s3):
    notes=read(O/'S4_owner_notes_snapshot.jsonl')
    assert len(notes)==len(SPECS)==33
    model=load_model(Path('docs/records/labelfix/markshape_model_S3.json'))
    out=[]
    for note,spec in zip(notes,SPECS):
        lid=note['line_id'];l=by[lid];rows=[]
        for kind,target,value in spec:
            targets=target if isinstance(target,list) else [target] if target is not None else []
            resolution={}
            for version,source in [('S2',s2),('S3',s3)]:
                resolution[version]=[dict(slot=k,bbox=source[lid]['slots'][k-1]['bbox'],base=source[lid]['slots'][k-1]['base'])
                                     for k in targets if 0<k<=len(source[lid]['slots'])]
            equivalent=resolution['S2']==resolution['S3']
            e=dict(kind=kind,slots=targets,value=value,slot_lists=resolution,
                   resolution='both: identical component geometry/base' if equivalent else 'ambiguous: S2/S3 differ',
                   ambiguous=kind=='ambiguous' or not equivalent)
            chosen=[l['slots'][k-1] for k in targets if 0<k<=len(l['slots'])]
            before=False;after=False
            if kind in ('mark','subscript','apostrophe') and len(chosen)==1:
                s=chosen[0]
                truth=s['truth']
                required='subscript' if kind=='subscript' else 'apostrophe' if kind=='apostrophe' else None
                e['truth_conflict']=truth is not None and (not any(k==required for k,v in truth) if required else units(truth)<value)
                e['truth']=truth
                def good(ms):
                    if e['truth_conflict']:return False
                    if required:return any(k==required for k,v in ms)
                    return units(ms)>=value and (truth is None or set(map(tuple,truth))<=set(map(tuple,ms)))
                before,after=good(s['before']),good(s['detected'])
            elif kind in ('quote','leading_sign'):
                before=False;after=bool(l.get('opening_quotes'))
                if kind=='leading_sign':e['semantic_ambiguity']='owner says ellipsis OR quote; preserved as a leading quote-shaped sign'
            elif kind=='named' and len(chosen)==1:
                bs=s3[lid]['slots'][target-1]
                before=not bs['above'] or model.predict(bs['x'])[1]>=.5
                after=not chosen[0]['unnamed'] and not any(r.get('localisation_unknown') and r.get('component_slot')==target for r in l['recogniser_slots'])
            elif kind in ('no_regression','whole_marks'):
                known=[s for s in l['slots'] if s['truth'] is not None]
                before=all(same(s['truth'],s['before']) for s in known)
                after=all(same(s['truth'],s['detected']) for s in known)
                lost=[]
                for s in known:
                    t,b,a=(set(map(tuple,s[k])) for k in ('truth','before','detected'))
                    if (t & b)-(t & a) or (a-t)-(b-t):
                        lost.append(s['slot'])
                e['new_error_slots']=lost
                if kind=='no_regression':
                    # Empty notes impose a preservation gate, not new labels.
                    before=True;after=not lost
            elif kind in ('base','union_base'):
                before=False
                e['before_unresolved']='S3 base labels are evaluation locators; they do not certify independent letter recognition'
                rs=[r for r in l['recogniser_slots'] if r.get('component_slot') in targets]
                after=bool(rs) and all(r['base'].lower()==value for r in rs) and all(not r['localisation_unknown'] for r in rs)
                if kind=='union_base':
                    after=after and len(rs)==1 and len(rs[0].get('component_ids',[]))==len(targets)
            elif kind in ('word_slots','word_accent'):
                wanted=value
                ts=tokenize(nfd(l['recogniser_text']))
                matches=[t for t in ts if wanted in ''.join(c.base for c in clusters(t.core))]
                rs=[r for t in matches for r in l['recogniser_slots'] if t.core_start<=r['start']<t.core_end]
                after=bool(rs) and all(not r['localisation_unknown'] for r in rs)
                if kind=='word_accent':after=after and any(r['base']==value and any(p in r.get('parts',[]) for p in ('acute','grave','circumflex')) for r in rs)
                before=False
                e['before_unresolved']='S3 component-only record does not certify recogniser character segmentation'
            e.update(before_fixed=before,fixed=after and not e['ambiguous'])
            e['status']='fixed' if e['fixed'] else 'ambiguous' if e['ambiguous'] else 'not fixed'
            rows.append(e)
        out.append(dict(note,expectations=rows,before_fixed=all(e['before_fixed'] for e in rows),
                        fixed=all(e['fixed'] for e in rows)))
    write(O/'owner_examples_expectations.jsonl',out)
    return out


def main():
    m=json.loads((O/'S4_metrics.json').read_text())
    lines=read(O/'S4_lines.jsonl.gz');by={l['line_id']:l for l in lines}
    s2={l['line_id']:l for l in read(O/'S2_lines.jsonl.gz')}
    s3={l['line_id']:l for l in read(O/'S3_lines.jsonl.gz')}
    old=read(O/'owner_slot_expectations.jsonl');expect=[]
    for prior in old:
        e=dict(prior);l=by[e['line_id']];ss=l['slots']
        slot,hits=overlap_slots(e['v8_x0'],e['v8_x1'],ss)
        e['mapped_slot']=slot;e['overlapping_slots']=hits;e['s3_fixed']=prior['fixed']
        s=next((s for s in ss if s['slot']==slot),None)
        e['fixed']=passes(e,s,ss,False);e['after']=s['detected'] if s else None
        e['status']='fixed' if e['fixed'] else 'not fixed'
        e['s3_cause']=prior.get('cause')
        e['cause']='S4 expectation passes' if e['fixed'] else (
            'S4 naming/localisation regression; inspect retained before/after evidence' if e['s3_fixed']
            else 'S4 expectation remains unmet; S3 cause retained separately')
        expect.append(e)
    write(O/'S4_owner_expectations.jsonl',expect)
    examples=new_expectations(by,s2,s3)
    owner_ids=set(e['line_id'] for e in old)|set(n['line_id'] for n in examples)
    changed=[dict(line_id=l['line_id'],before=l['before_reading'],after=l['reading'])
             for l in lines if l['line_id'] in owner_ids and l['before_reading']!=l['reading']]
    write(O/'S4_changed_owner_lines.jsonl',changed)
    m['owner_fixed']=sum(e['fixed'] for e in expect)
    m['owner_s3_fixed']=sum(e['s3_fixed'] for e in expect)
    m['new_notes']=dict(before=sum(e['before_fixed'] for e in examples),after=sum(e['fixed'] for e in examples),n=33,
                        expectation_before=sum(e['before_fixed'] for n in examples for e in n['expectations']),
                        expectation_after=sum(e['fixed'] for n in examples for e in n['expectations']),
                        expectations=sum(len(n['expectations']) for n in examples))
    owner_lines=[l for l in lines if l['line_id'] in owner_ids]
    m['owner_metrics']={key:pooled([score_slots([dict(s,detected=s[key],unknown_kinds=[]) for s in l['slots']]) for l in owner_lines])
                        for key in ('before','detected')}
    regress=[]
    def compare(label,b,a,higher=True):
        if b is not None and a is not None and (a<b-1e-12 if higher else a>b+1e-12):regress.append(f'{label} {pc(b)}→{pc(a)}')
    for split,b,a in [('held-out',m['before'],m['after']),('DEV',m['dev_before'],m['dev_after'])]:
        for metric in ('precision','recall','f1'):compare(split+' '+metric,b['total'][metric],a['total'][metric])
        for k,c in b['by_kind'].items():
            for metric in ('precision','recall','f1'):compare(split+' '+k+' '+metric,c[metric],a['by_kind'][k][metric])
    for d,v in m['per_book'].items():
        for metric in ('precision','recall'):compare(d+' subscript '+metric,v['before']['by_kind']['subscript'][metric],v['after']['by_kind']['subscript'][metric])
    for split,v in m['ascender'].items():compare(split+' ascender false',v['before']/v['n'],v['after']/v['n'],False)
    for metric in ('precision','recall','f1'):
        compare('owner whole-line '+metric,m['owner_metrics']['before']['total'][metric],m['owner_metrics']['detected']['total'][metric])
    for cls,c in m['per_class'].items():
        for metric in ('precision','recall'):
            compare('class '+cls+' '+metric,c.get('before_'+metric),c[metric])
    for kind,c in m['atomic']['before']['by_kind'].items():
        for metric in ('precision','recall','f1'):
            compare('atomic '+kind+' '+metric,c[metric],m['atomic']['detected']['by_kind'][kind][metric])
    lost=[f"{e['line_id']}:{e['v8_slot']}" for e in expect if e['s3_fixed'] and not e['fixed']]
    if lost:regress.append('old owner expectations lost '+','.join(lost))
    empty=[n['line_id']+':'+','.join(map(str,n['expectations'][0]['new_error_slots'])) for n in examples if not n['note'] and not n['fixed']]
    if empty:regress.append('empty-note new errors '+','.join(empty))
    m['regressions']=regress
    (O/'S4_metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    train=json.loads((O/'S4_training.json').read_text())
    L=['# S4 — independent detector/reader candidate','',
       'Network off; CPU only; zero recogniser/CTC forward passes. Cached alignments only. No git writes by this run and no owner sheet build or publication. Worktree started clean at `426b9be3`. HEAD and the owner-notes input changed externally during execution (HEAD later observed `ed946b42`; notes grew from 33 to 56). `S4_owner_notes_snapshot.jsonl` preserves the original 33 records used for the requested accounting. `S4_live_notes_changes.json` records 23 added notes and one updated note, outside that frozen scope and unscored here. No concurrent input changes were overwritten.', '',
       'Detector output depends only on crop pixels, recogniser letters and cached character locations. `reading.read_line` returns NFC text; `read_line_details` provides unnamed-blob and localisation flags separately. Recogniser combining marks are discarded. Disconnected strokes covered by a single unopposed recogniser character form one body; a physical blob is credited once. Capitals use a compact upper-left mark group bounded by the previous letter; distant leading quote ink is separate. Upper neighbour components require an accepted lower mark anchor and cannot touch the crop edge. Low-confidence compound sets fall back to per-blob naming, with conflicting names left unresolved.', '',
       'Evaluation retains the frozen S2/S3 component-slot truth and unknown words. Predictions from independent recogniser slots are projected by exact primary component identity; split-body secondary components do not receive duplicate marks. All known printed positives remain in recall denominators; bottom-clipped subscript predictions abstain exactly as in the S3 report. No adjudication was changed. S3 before totals must equal the frozen S3 report. A preliminary projection bug (overlapping letter boxes) was corrected to exact component identity before final measurement. Exploratory held-out results were seen; no thresholds or class weights were fitted against held-out results.', '',
       '## Whole-line mark metrics','', '| kind | S3 P | S4 P | S3 R | S4 R | S3 F1 | S4 F1 |','|---|---:|---:|---:|---:|---:|---:|']
    for k,b,a in [('total',m['before']['total'],m['after']['total'])]+[(k,b,m['after']['by_kind'][k]) for k,b in m['before']['by_kind'].items()]:
        L.append(f"| {k} | {pc(b['precision'])} | {pc(a['precision'])} | {pc(b['recall'])} | {pc(a['recall'])} | {pc(b['f1'])} | {pc(a['f1'])} |")
    b,a=m['before']['total'],m['after']['total']
    L+=['',f"Held-out: {m['heldout_lines']} lines; {b['known_slots']} known and {b['unknown_slots']} unknown component slots. S3 TP/FP/FN {b['tp']}/{b['fp']}/{b['fn']}; S4 {a['tp']}/{a['fp']}/{a['fn']}. Fourteen books remain evaluation only.",'',
        f"Capitals with printed vowel/rho marks: {m['capital_slots']} slots; recall {pc(m['capitals']['before']['total']['recall'])} → {pc(m['capitals']['detected']['total']['recall'])}. Capital punctuation-only slots are excluded. Compound recall includes all breathing+accent sets, including stacked components. `ᾗσι` is a native stacked witness, not an independent large stacked-truth stratum.",'',
        '## Training and per-class held-out results','',
        f"Decoded {train['decoded_crops']} distinct C1 training crops (cap 10,000), selected rare compounds first with seed 20261016, plus the existing S3 DEV samples. Exact NFD Google=recogniser word agreement supplies training labels only. All C1 IDs are train split, disjoint from test IDs and all non-DEV Wikisource books. Rare compound samples are retained; ordinary classes are bounded at 1,600 C1 samples plus DEV. MLP: 96 hidden units, 100 epochs, CPU NumPy. DEV calibration uses the original S3 held-aside line IDs. Training receipt and decoded crop inventory: `S4_training.json`; fitting targets/features: `S4_training_samples.jsonl.gz`. Model SHA-256: `{train['model_sha256']}`.",'',
        'Counts below 200 are explicit when agreement/localisation yields fewer usable samples; no held-out or synthetic samples were added to fit. Zero-support classes stay explicit. Class metrics require the entire set to match, including subscript and apostrophe; they differ from the per-kind metrics above.', '',
        '| class | fit | held truth | predicted | exact TP | S3 P/R | S4 P/R |','|---|---:|---:|---:|---:|---|---|']
    for cls,c in m['per_class'].items():L.append(f"| {cls} | {c['fit']} | {c['support']} | {c['predicted']} | {c['tp']} | {pc(c.get('before_precision'))}/{pc(c.get('before_recall'))} | {pc(c['precision'])}/{pc(c['recall'])} |")
    L+=['','Atomic marks (compounds expanded into their accent and breathing; supplementary to the frozen headline metric):','',
        '| kind | S3 P/R/F1 | S4 P/R/F1 |','|---|---|---|']
    for kind,c in m['atomic']['before']['by_kind'].items():
        a=m['atomic']['detected']['by_kind'][kind]
        L.append(f"| {kind} | {pc(c['precision'])}/{pc(c['recall'])}/{pc(c['f1'])} | {pc(a['precision'])}/{pc(a['recall'])}/{pc(a['f1'])} |")
    L+=['','## Per-book subscripts','', '| book | printed positives | S3 P/R | S4 P/R |','|---|---:|---|---|']
    for d,v in m['per_book'].items():
        b,a=v['before']['by_kind']['subscript'],v['after']['by_kind']['subscript']
        L.append(f"| {d} | {b['tp']+b['fn']} | {pc(b['precision'])}/{pc(b['recall'])} | {pc(a['precision'])}/{pc(a['recall'])} |")
    L+=['','## Ascender exposure','', 'Same frozen known unmarked bases δβλθφξζ and uppercase letters; rate counts physical above blobs, including unresolved blobs. This is a geometric false-mark diagnostic, independent of classifier correctness.', '', '| split | slots | S3 false | S4 false |','|---|---:|---:|---:|']
    for split,c in m['ascender'].items():L.append(f"| {split} | {c['n']} | {c['before']} ({pc(c['before']/c['n'])}) | {c['after']} ({pc(c['after']/c['n'])}) |")
    L+=['','## Original 59 owner expectations','',f"S3 {m['owner_s3_fixed']}/59 → S4 {m['owner_fixed']}/59. Each v8 range uses unique maximum x-overlap, with ties/unavailable ranges unresolved. Machine receipt: `S4_owner_expectations.jsonl`; the original expectations file is unchanged.",'', '| line | v8 → current | expectation | S3 → S4 |','|---|---|---|---|']
    for e in expect:L.append(f"| {e['line_id']} | {e['v8_slot']} → {e['mapped_slot']} | {json.dumps(e['expected'],ensure_ascii=False)} | {e['s3_fixed']} → {e['fixed']} |")
    nn=m['new_notes']
    L+=['','## All 33 added notes','',f"Complete notes satisfied/certified: {nn['before']}/33 → {nn['after']}/33. Individual clauses: {nn['expectation_before']}/{nn['expectations']} → {nn['expectation_after']}/{nn['expectations']}. `owner_examples_expectations.jsonl` records every clause, both S2/S3 slot resolutions, conflicts, ambiguity and before/after checks. Empty notes require no new known-slot error; their owner judgment is not silently converted into new print truth. Ambiguous count syntax stays unresolved. Letter segmentation uses recogniser characters, not mark predictions. S3 has no independent letter-reading certificate, so letter-only baseline clauses remain uncertified rather than borrowing its evaluation base labels.",'', '| line | owner note | S3 → S4 | clauses / unresolved |','|---|---|---|---|']
    for n in examples:
        detail='; '.join(f"{e['kind']} {e['slots']}: {e['before_fixed']}→{e['fixed']}"+(' [truth conflict]' if e.get('truth_conflict') else '')+(' [ambiguous]' if e['ambiguous'] else '') for e in n['expectations'])
        L.append(f"| {n['line_id']} | {n['note'].replace(chr(10),' ' ) or '(empty: preserve correctness)'} | {n['before_fixed']} → {n['fixed']} | {detail} |")
    L+=['','## Requested strings versus native print','',
        'The actual supplied crops were inspected at 2× nearest-neighbour scale. `384c3f89-p000096-l0004` now reads `ᾗσι` (dasia + perispomeni + subscript) once over components 24+29. The other three requested strings conflict with the native pixels: `177b717d-p000013-l0009` prints a smooth breathing and acute (`Ἤταν`, not `Ἦταν`); `51fe7386-p000024-l0015` prints `Ὁ Ὄλυμπος … Ὄσσα` (smooth breathing over the two names); `384c3f89-p000068-l0028` has a horizontal arch above the smooth breathing (`ἆσσον`, not `ἂσσον`). The frozen print instrument may disagree and is retained. Actual-crop tests assert the visible readings; a separate per-blob regression proves a low-probability psili+grave pair composes `ἂ`. The literal requested real-crop assertions for those three strings are therefore not claimed to pass. Source crops/alignments are copied into `tests/data/labelfix_s4/` for review.', '',
        '## Owner readings changed','', 'Before strings render frozen S3 component predictions over the same recogniser letters. They are not Google text and are not a claim that S3 had a standalone reader. Full strings are in `S4_changed_owner_lines.jsonl`.', '']
    L.extend('- `'+l['line_id']+'`: '+l['before']+' → '+l['after'] for l in changed)
    verification=json.loads((O/'S4_verification.json').read_text())
    full=verification['full_suite'];focused=verification['focused']
    L+=['','## Verification and limitations','',
        f"Final full suite: {full['passed']:,} passed, {full['skipped']} skipped, {full['failed']} failures and {full['errors']} setup errors. The five setup errors in apply_clean lack `docs/records/harvest/collection/v2/admitted_all_v2.jsonl`; the sixth is the sandbox-forbidden localhost capture bind. Three collection-output failures concern missing frozen harvest budget/index inputs; the other two concern an existing uninventoried `parliament_resolution.json` and an existing four-line API example where the API test requires two lines. Those files/tests are unchanged. All {focused['passed']} runnable labelfix tests pass, including {focused['new_S4_tests']} S4 tests; one existing socket test is deselected in that focused run. Exact commands/logs, hashes and elapsed time are in `S4_verification.json`, `S4_pytest_full.txt` and `S4_inputs.json`. All-existing-tests-green is not achieved in this checkout. Unresolved connected-letter ownership remains flagged; it is not repaired by substituting Google letters. Overall held-out precision exceeds S3; smaller-stratum and owner regressions below remain open.", '',
        'This candidate is not qualified under the no-empty-note-regression requirement: `384c3f89-p000182-l0031`, slot 8, changes one false compound identity to another. Empty-note checks reject any newly introduced false identity or lost true mark, even when the old slot was already wrong against the frozen print instrument. The native-string conflicts above also leave three literal requested real-crop assertions unmet.', '',
        'Regressions: '+('; '.join(regress) or 'none')+'.','']
    b,a=m['before']['total'],m['after']['total'];cb,ca=m['capitals']['before']['total'],m['capitals']['detected']['total']
    final=f"S4 RESULT: held-out P {pc(b['precision'])}→{pc(a['precision'])} R {pc(b['recall'])}→{pc(a['recall'])}; capitals R {pc(cb['recall'])}→{pc(ca['recall'])}; stacked/compound R {pc(m['before']['by_kind']['compound']['recall'])}→{pc(m['after']['by_kind']['compound']['recall'])}; owner expectations fixed {m['owner_fixed']}/59 (S3 35/59); regressions: "+('; '.join(regress) or 'none')
    L.append(final)
    (O/'S4_REPORT.md').write_text('\n'.join(L)+'\n')
    print(final)


if __name__=='__main__':main()
