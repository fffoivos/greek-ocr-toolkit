"""Local, inference-free digest of receipt-verified job 3681404."""
from collections import Counter, defaultdict
from copy import deepcopy
import json
import math
from pathlib import Path
from scripts.labelfix.clariden.r1_common import HEADS, rows, sha256
from scripts.labelfix.clariden import r1_score
from scripts.labelfix import r2_score

ROOT=Path('artifacts/labelfix_r2/output_3681404')
OUT=Path('docs/labelfix/spellcheck/R2')
EVID=OUT/'evidence/job1'
FIX=Path('tests/labelfix/fixtures/r2')
DEV=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz')
ROLES=('train','validation_reserve','witness','calibration')


def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def head_check(value,choices):
    """Missing fields and invalid distributions are counted separately."""
    required=('probabilities','top','top_probability','margin')
    missing=[k for k in required if not isinstance(value,dict) or k not in value]
    if missing:return dict(missing=missing,invalid=[],p=None,margin=None)
    invalid=[];p=value['probabilities'];top=value['top'];pt=value['top_probability'];m=value['margin']
    numeric=lambda x:isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
    if not isinstance(p,dict) or set(p)!=set(choices):invalid.append('full_softmax')
    elif any(not numeric(v) or not 0<=v<=1 for v in p.values()) or abs(sum(p.values())-1)>1e-5:invalid.append('probabilities')
    if not numeric(pt) or not 0<=pt<=1:invalid.append('top_probability')
    if not numeric(m) or not 0<=m<=1:invalid.append('margin')
    if top not in choices:invalid.append('top')
    if not invalid:
        ordered=sorted(p.values(),reverse=True)
        if abs(p[top]-ordered[0])>1e-6 or abs(pt-ordered[0])>1e-6:invalid.append('top_consistency')
        if abs(m-(ordered[0]-ordered[1]))>1e-6:invalid.append('margin_consistency')
    return dict(missing=missing,invalid=invalid,p=pt if not invalid else None,margin=m if not invalid else None)


def bucket():return dict(lines=set(),slots=0,seen=Counter(),validity=Counter(),heads={h:Counter() for h in HEADS})


def add_row(b,r):
    b['lines'].add(r['line_id']);b['slots']+=1;b['seen'][str(r.get('teacher_seen_document','MISSING'))]+=1
    v=r.get('crop_validity',{});c=r.get('coverage',{})
    for k in ('clipped_top','clipped_bottom','window_outside_image'):b['validity'][k]+=bool(v.get(k))
    b['validity']['span_implausible']+=v.get('span_plausible') is False
    b['validity']['localisation_unknown']+=c.get('evidence_state')=='UNKNOWN' or bool(c.get('uncertainty'))
    b['validity']['unscored']+=not c.get('scored',True)
    b['validity']['fused']+=bool(c.get('fused'))
    for h,choices in HEADS.items():
        z=head_check((r.get('heads') or {}).get(h),choices);cnt=b['heads'][h];cnt['rows_checked']+=1
        cnt['missing_rows']+=bool(z['missing']);cnt['invalid_rows']+=bool(z['invalid'])
        for k in z['missing']:cnt['missing_'+k]+=1
        for k in z['invalid']:cnt['invalid_'+k]+=1
        if z['p'] is not None:
            cnt['valid']+=1;cnt['p_ge_099']+=z['p']>=.99;cnt['margin_ge_020']+=z['margin']>=.20
            cnt['both']+=z['p']>=.99 and z['margin']>=.20
            for lo,hi in ((0,.5),(.5,.9),(.9,.99),(.99,1.000001)):
                cnt[f'p_bin_{lo}_{hi}']+=lo<=z['p']<hi
        fs=r.get('factors');hd=(r.get('heads') or {}).get(h)
        if fs and hd and hd.get('top') in choices:cnt['factor_mismatch']+=choices[fs[list(HEADS).index(h)]]!=hd['top']


def finish(b):
    return dict(lines=len(b['lines']),slots=b['slots'],teacher_seen_document=dict(b['seen']),validity=dict(b['validity']),
        heads={h:dict(c,**{k+'_share':c[k]/b['slots'] if b['slots'] else None for k in ('p_ge_099','margin_ge_020','both')}) for h,c in b['heads'].items()})


def inventory():
    role={r:bucket() for r in ROLES};source=defaultdict(bucket)
    for n,p in enumerate(sorted((ROOT/'B').glob('chunk-*.jsonl.gz'))):
        if p.name.endswith('-alignments.jsonl.gz'):continue
        for r in rows(p):
            add_row(role[r['role']],r);add_row(source[r['role']+' / '+r['source']],r)
        if n%1800==0:print('inventory files',n,flush=True)
    return bind_population(dict(roles={k:finish(b) for k,b in role.items()},role_source={k:finish(b) for k,b in sorted(source.items())}))


def bind_population(inv):
    path=Path('artifacts/labelfix_r2/population/population.jsonl')
    binding=json.loads((ROOT/'B/teacher_receipt.json').read_text())['binding']
    assert sha256(path)==binding['line_list_sha256']
    population=list(rows(path));rr=defaultdict(list);ss=defaultdict(list)
    for r in population:
        rr[r['role']].append(r);ss[r['role']+' / '+r['source']].append(r)
    for groups,source in ((inv['roles'],rr),(inv['role_source'],ss)):
        for key,ll in source.items():
            if key not in groups:groups[key]=finish(bucket())
            b=groups[key];b.setdefault('lines_with_exported_slots',b['lines']);b['lines']=len(ll)
            b['zero_slot_lines']=b['lines']-b['lines_with_exported_slots']
            b['teacher_seen_document_lines']=dict(Counter(str(r.get('teacher_seen_document',False)) for r in ll))
    inv['population_binding']=dict(path=str(path),sha256=sha256(path),lines=len(population))
    return inv


def physical_ledger(old,new):
    oo={(l['line_id'],s['slot']):(l,s) for l in old for s in l['slots']};nn={(l['line_id'],s['slot']):(l,s) for l in new for s in l['slots']};out=[]
    for key,(l,a) in oo.items():
        b=nn[key][1]
        if a['truth'] is None:continue
        y=set(map(tuple,a['truth']));aa=set(map(tuple,a['detected']));bb=set(map(tuple,b['detected']))
        if aa!=bb:
            out.append(dict(line_id=key[0],slot=key[1],doc=l['doc'],base=a['base'],truth=sorted(y),old=sorted(aa),new=sorted(bb),
                old_right=aa==y,new_right=bb==y,direction='old_right_new_wrong' if aa==y else 'old_wrong_new_right' if bb==y else 'both_wrong_changed'))
    return dict(counts=dict(Counter(r['direction'] for r in out)),ledger=out)


def evaluate():
    lines=[l for l in r2_score.truth_lines('docs/labelfix/spellcheck/S4_lines.jsonl.gz') if not l['dev']]
    assert len(lines)==666
    binding=json.loads((FIX/'binding.json').read_text())['sha256']
    for name in ('heldout_lines.jsonl.gz','A_predictions.jsonl.gz'):assert sha256(FIX/name)==binding[name]
    md=list(rows(FIX/'heldout_lines.jsonl.gz'));meta={l['id']:dict(l,coverage_by_start={c['start']:c for c in l['coverage']}) for l in md}
    ex=json.loads(Path('artifacts/labelfix_r1/heldout_font/extraction_receipt.json').read_text())
    native_metadata=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/labelfix_r1/heldout_font/lines.jsonl.gz')
    assert sha256(native_metadata)==ex['sha256']['lines.jsonl.gz']
    assert list(rows(native_metadata))==md  # fixture gzip envelope differs; parsed metadata is exact
    pred={'A16':list(rows(FIX/'A_predictions.jsonl.gz'))}
    for seed in (17,18):
        p=ROOT/'C'/str(20261000+seed);rr=json.loads((p/'heldout_predictions.receipt.json').read_text())
        assert rr['checkpoint_sha256']==sha256(p/'best.pt')
        assert rr['prediction_sha256']==sha256(p/'heldout_predictions.jsonl')
        assert rr['extraction_receipt_sha256']==sha256(Path('artifacts/labelfix_r1/heldout_font/extraction_receipt.json'))
        assert rr['input_index_sha256']==ex['sha256']['index.npy']
        pred['s'+str(seed)]=list(rows(p/'heldout_predictions.jsonl'))
        assert len(pred['s'+str(seed)])==rr['samples']
    expected={(lid,c['start']) for lid,l in meta.items() for c in l['coverage'] if c['scored']}
    for pp in pred.values():
        assert len(pp)==len(expected) and {(p['line_id'],p['start']) for p in pp}==expected
        for p in pp:
            assert p['base']==meta[p['line_id']]['coverage_by_start'][p['start']]['base']
            p['coverage']=meta[p['line_id']]['coverage_by_start'][p['start']]
    variants={'without_overlay':lines}
    for v in ('v0','v1','v1_1'):
        ll,ov=r2_score.apply_overlay(lines,json.loads((OUT/f'truth_overlay_{v}.json').read_text()));variants[v]=ll
    result={}
    for name,ll in variants.items():
        result[name]={};records={};mapped={}
        for model,pp in pred.items():
            print('scoring',name,model,flush=True)
            raw,records[model]=r2_score.score(ll,pp)
            cc=r2_score.continuity(ll,meta,pp)
            mapped[model],_=r1_score.map_lines(ll,meta,{(p['line_id'],p['start']):p for p in pp},filtered=False)
            result[name][model]=dict(continuity=cc,raw=raw)
        if name=='without_overlay':
            published=json.loads(Path('docs/labelfix/spellcheck/clariden/R1_result_3678928/metrics.json').read_text())['policies']['raw']['arms']['A']
            for k in ('all_unscored_none','scored','fused_all_unscored_none','fused_scored','per_class','per_book'):
                assert result[name]['A16']['continuity']['summary'][k]==published[k],k
        for model in ('s17','s18'):
            result[name][model]['paired_union_vs_A']=r2_score.paired(records['A16'],records[model])
            result[name][model]['paired_physical_vs_A']=physical_ledger(mapped['A16'],mapped[model])
        result[name]['seed_pair']=dict(physical=physical_ledger(mapped['s17'],mapped['s18']),union=r2_score.paired(records['s17'],records['s18']))
    churn=[]
    for a,b in zip(sorted(pred['s17'],key=lambda p:(p['line_id'],p['start'])),sorted(pred['s18'],key=lambda p:(p['line_id'],p['start']))):
        if a['factors']!=b['factors']:churn.append(dict(line_id=a['line_id'],start=a['start'],base=a['base'],s17=a['factors'],s18=b['factors']))
    dump(EVID/'base_seed_churn.json',dict(count=len(churn),definition='different four-head argmax tuple on identical scored extraction slot; before truth/overlay filtering',slots=churn))
    return result,len(churn)


def dev_pending():
    data=list(rows(DEV));items=[r for r in data if r.get('type')=='item']
    sources=json.loads((DEV.parent/'sources.json').read_text());ids=sorted({r['id'] for r in rows(DEV.parent/'baseline_per_line.jsonl')})
    assert len(ids)==600 and {r['line_id'] for r in items}<=set(ids)
    (EVID/'DEV_selection.jsonl').write_text(''.join(json.dumps(dict(id=lid,doc=sources[lid]['doc'],crop=sources[lid]['crop'],google=sources[lid]['label'],wave=sources[lid]['wave']),ensure_ascii=False)+'\n' for lid in ids))
    (EVID/'DEV_required_lines.txt').write_text('\n'.join(ids)+'\n')
    dump(EVID/'DEV_pending.json',dict(truth=str(DEV),sha256=sha256(DEV),items=len(items),line_count=len(ids),truth_card_lines=len({r['line_id'] for r in items}),noncontrol_truth_card_lines=len({r['line_id'] for r in items if not r.get('control')}),line_ids=ids,
        waves=dict(Counter(r['wave'] for r in items)),status='pending',reason='No BASE DEV windows or BASE DEV predictions in readback or inspected local extraction inventories; saved A word forms do not provide BASE predictions.',
        proposed_job=dict(name='R2RB_DEV_extract_score',submitted=False,stages=1,training=False,
            inputs=['exact DEV_required_lines.txt and DEV_selection.jsonl (600 census lines, 542 with cards, 527 with noncontrol cards)','S8 saved line crops, recogniser text and CTC alignments (hash bind before execution)','R1-A 719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636','both BASE best.pt with READBACK_RECEIPT hashes','S8 DEV truth and inclusion weights'],
            checkpoints={name:dict(path=('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/'+str(seed)+'/best.pt'),sha256=sha256(ROOT/'C'/str(seed)/'best.pt')) for name,seed in [('s17',20261017),('s18',20261018)]} if (ROOT/'C/20261017/best.pt').exists() else {},
            teacher_checkpoint=dict(sha256='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636',path='frozen R1-A teacher path in config/r2_job.json'),
            resources=dict(nodes=1,gpus=1,cpus=8,wall_minutes=20,wall_basis='provisional cap, no DEV measurement'),
            steps=['Fail closed on absent crop/alignment or recogniser-text mismatch; no new CTC forward required for saved alignments.',
                'Extract exact listed full-height R1 windows (1.5 left / 0.75 right font heights, 64x128), same extraction for all three checkpoints.',
                'Export predictions and receipts for A16/s17/s18, no gradient updates.',
                'Join by line_id and recogniser NFD start to DEV word ranges; preserve UNKNOWN, controls, alias policy and inclusion weights; report by wave and paired errors.'],
            outputs=['extraction_receipt.json','three prediction JSONL + SHA receipts','weighted DEV metrics by wave','paired regressions'],
            prerequisite='bind exact native crop and saved alignment paths and hashes before coordinator submission')))
    return len(ids)


def pct(v):return '—' if v is None else f'{100*v:.3f}%'
def prf(m):
    m=m.get('total',m)
    return ' / '.join(pct(m.get(k)) for k in ('precision','recall','f1'))
def table(headers,data):return ['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in data]


def report(inv,ev,churn,ndev):
    rb=json.loads((ROOT/'READBACK_RECEIPT.json').read_text());stages={s:json.loads((ROOT/f'stage_{s}.json').read_text()) for s in 'ABC'};teacher=json.loads((ROOT/'B/teacher_receipt.json').read_text())
    t=teacher['timing_seconds'];elapsed=stages['B']['elapsed_seconds'];runs=stages['C']['result']['runs']
    L=['# R2 job 3681404: first readback and BASE digest','',
       'Job completed with exit 0:0 (coordinator report), 34:46 Slurm elapsed. This is BASE seed spread and teacher-export accounting; it does not establish a repair benefit or authorize another run. No submission, certificate refresh, new extraction or cohort inference was performed. All scoring below uses saved job predictions and frozen R1-A predictions.','',
       '## Readback','',f"Pulled {rb['file_count']:,} files / {rb['total_bytes']:,} bytes, {rb['pull_start_time']} to {rb['pull_end_time']} (11:52–11:53 Athens, before 18:30). {rb['sha256_verified']:,}/{rb['file_count']:,} SHA256 verified; {rb['receipt_matched']:,} against stage/chunk receipts. The remaining seven root envelopes/log have no parent receipt and were verified against remotely captured SHA256 values. Their `receipt_match=no` means no parent receipt; there are zero mismatches or missing stage payloads. BASE checkpoints only; no windows, crops or training shards pulled.",
       '', '[Readback receipt](../../../../artifacts/labelfix_r2/output_3681404/READBACK_RECEIPT.json), [remote envelope hashes](../../../../artifacts/labelfix_r2/readback_3681404_root_sha256.txt).','',
       '## Stage timing and measured throughput','']
    L+=table(['Stage','Receipt min','Reference min'],[[s,f"{stages[s]['elapsed_seconds']/60:.6f}",{'A':'I/O unforecast','B':'18.902','C':'30 (training planning allowance)'}[s]] for s in 'ABC'])
    L+=['',f"A–C receipt sum {sum(s['elapsed_seconds'] for s in stages.values())/60:.3f} min; Slurm wall 34.767 min vs requested forecast 74 min (forecast unpadded 48.902 min). Stage A reports only result recording: input validation precedes its timer, so this is **not** measured input verification time. Stage B includes startup and receipt/export costs; chunk alignment/windows/teacher totals are {t['alignment']:.3f}/{t['windows']:.3f}/{t['teacher']:.3f} s. Stage C includes parallel seed execution, validation and export; training-only times must not be added to parallel wall.",
          '',f"Teacher end-to-end Stage B: {teacher['lines']/elapsed:.3f} lines/s, {teacher['slots']/elapsed:.3f} slots/s ({teacher['lines']:,} lines / {teacher['slots']:,} slots). Export internal elapsed {teacher['elapsed_seconds']:.3f} s gives {teacher['lines']/teacher['elapsed_seconds']:.3f} lines/s and {teacher['slots']/teacher['elapsed_seconds']:.3f} slots/s. Teacher forward-only: {teacher['slots']/t['teacher']:.3f} slots/s; alignment-only: {teacher['lines']/t['alignment']:.3f} lines/s.",'']
    L+=table(['Seed','Draws','Train s','Train draws/s','Best val loss'],[[r['seed'],r['total_training_samples'],f"{r['training_seconds']:.3f}",f"{r['forward_backward_samples_per_second']:.3f}",f"{r['best_validation_loss']:.8f}"] for r in runs])
    L+=['','## Teacher-export inventory','', 'Every exported row was parsed and every head checked for the full named softmax, finite [0,1] values, sum=1 (1e-5 tolerance), argmax/top probability, margin consistency (1e-6 tolerance), and factor/top agreement. Confidence shares below use all role/source slots as denominator, including flagged windows; confidence is uncalibrated and does not admit a pseudo-label. Localisation unknown means coverage evidence_state=UNKNOWN or nonempty uncertainty. Clipping means edge ink, with ownership unadjudicated.','']
    L+=table(['Role','Lines','Slots','Teacher-seen lines / slots','Top clip','Bottom clip','Outside','Bad span','Locator unknown'],[[role,b['lines'],b['slots'],str(b.get('teacher_seen_document_lines',{}).get('True',0))+' / '+str(b['teacher_seen_document'].get('True',0)),*[b['validity'].get(k,0) for k in ('clipped_top','clipped_bottom','window_outside_image','span_implausible','localisation_unknown')]] for role,b in inv['roles'].items()])
    L+=['','### Probability integrity','']
    L+=table(['Role','Head','Checked','Missing rows','Invalid rows','Factor mismatch'],[[role,h,c['rows_checked'],c['missing_rows'],c['invalid_rows'],c.get('factor_mismatch',0)] for role,b in inv['roles'].items() for h,c in b['heads'].items()])
    L+=['','### Confidence by role and source family','', 'Each cell is p(top)≥0.99 share / margin≥0.20 share / both share. `source` is the exported source-family label. Population line counts (including zero-slot lines), teacher-seen true/false line and slot counts, detailed missing-field counts and probability bins [0,.5), [.5,.9), [.9,.99), [.99,1] are in [teacher inventory JSON](evidence/job1/teacher_inventory.json).','']
    for title,groups in [('Role',inv['roles']),('Role / source',inv['role_source'])]:
        L+=table([title,'Slots',*HEADS],[[k,b['slots'],*[' / '.join(pct(b['heads'][h][v+'_share']) for v in ('p_ge_099','margin_ge_020','both')) for h in HEADS]] for k,b in groups.items()])+['']
    L+=['## BASE vs saved A on the 666','', 'The R2 `continuity()` column calls the unchanged R1 physical-slot scorer. Frozen metadata gzip envelopes differ from the original extraction, but the original receipt-bound file was hash-verified and its parsed contents match the fixture exactly. Saved A reproduces every published raw/scored/fused/per-class/per-book value exactly (asserted). Predictions cover the identical 11,329 scored extraction slots. The without-overlay instrument includes 206 apostrophe FN outside the four model heads. Overlays v0, v1 and v1.1 were each applied independently to the frozen truth, symmetrically to all models. v1 excludes the unresolved full tuple; v1.1 resolves it. No key was overwritten.','']
    L+=table(['Overlay','Model','Physical mark P / R / F1','Four-head P','Four-head R','Tuple all','Tuple marked'],[[v,m,prf(z['continuity']['summary']['all_unscored_none']),pct(z['raw']['micro']['atomic']['precision']),pct(z['raw']['micro']['atomic']['recall']),pct(z['raw']['micro']['composed_tuple']['accuracy_all']),pct(z['raw']['micro']['composed_tuple']['accuracy_marked'])] for v,res in ev.items() for m,z in res.items() if m!='seed_pair'])
    metrics=[ev['v1_1'][m]['continuity']['summary']['all_unscored_none']['total'] for m in ('A16','s17','s18')]
    L += ['', 'With v1.1, the three-seed continuity range (max minus min) is '+', '.join(f'{k} {100*(max(z[k] for z in metrics)-min(z[k] for z in metrics)):.3f} pp' for k in ('precision','recall','f1'))+'. These are observed seed ranges, not calibrated statistical acceptance margins. Stage D was skipped because no hash-bound R2a manifest was supplied.']
    for v in ('without_overlay','v1_1'):
        L+=['',f'### {v}: exact composed classes','']
        classes=ev[v]['A16']['continuity']['summary']['per_class']
        L+=table(['Class','Support','A16 P / R','s17 P / R','s18 P / R'],[[c,z['support'],*[' / '.join(pct(ev[v][m]['continuity']['summary']['per_class'][c][k]) for k in ('precision','recall')) for m in ('A16','s17','s18')]] for c,z in classes.items() if z['support'] or any(ev[v][m]['continuity']['summary']['per_class'][c]['predicted'] for m in ('A16','s17','s18'))])
        L+=['',f'### {v}: capitals, compounds and paired churn','']
        L+=table(['Model','Capital detection P / R','Capital naming P / R / F1','Marked capitals','Subscript P / R','Dialytika P / R'],[[m,' / '.join(pct(z['continuity']['summary']['capital_detection'][k]) for k in ('precision','recall')),prf(z['continuity']['summary']['capital_naming']),z['continuity']['summary']['capital_marked_slots'],*[' / '.join(pct(z['raw']['micro']['heads'][h]['values'][h][k]) for k in ('precision','recall')) for h in ('subscript','dialytika')]] for m,z in ev[v].items() if m!='seed_pair'])
        L+=['','Physical ledger exact-set changes versus A (all known physical slots, apostrophes retained):','']
        L+=table(['Pair','Old right → new wrong','Old wrong → new right','Both wrong, changed'],[[m,*[ev[v][m]['paired_physical_vs_A']['counts'].get(k,0) for k in ('old_right_new_wrong','old_wrong_new_right','both_wrong_changed')]] for m in ('s17','s18')])
        for m in ('s17','s18'):
            dump(EVID/f'{v}_{m}_physical_vs_A.json',ev[v][m]['paired_physical_vs_A'])
        L+=['',f"Seed17→18 physical changes: {ev[v]['seed_pair']['physical']['counts']}. Complete slot ledgers carry line, physical slot, base, truth, old/new marks and direction; union/head paired ledgers with document bootstrap intervals are in [full scores](evidence/job1/scores.json).",'',f'### {v}: raw exact named head confusion','', 'Rows are printed truth, columns predicted. Alphabetic union, mark-blind and case-preserving alignment; unmatched print positives are FN, inserted predicted positives FP. This uses the frozen physical-truth adapter, not newly adjudicated complete line truth. UNKNOWN and coverage counts are preserved in the machine-readable result. Compounds are separate exact tuples.','']
        L += table(['Model','Union slots','Covered','UNKNOWN','Unmatched print','Inserted prediction'],[[m,*[ev[v][m]['raw']['micro']['states'][k] for k in ('union_slots','coverage','UNKNOWN','unmatched_print','inserted_prediction')]] for m in ('A16','s17','s18')])+['', 'The union adapter has 1,334 inserted prediction slots against the physical alphabetic base sequence; this changes the denominator and contributes false positives compared with the continuity mapping. These are instrument results, not a certification of complete independently printed line truth. Held-out exports lack crop-validity flags, so absent clipped/localisation flags must not be interpreted as verified clean crops.','']
        for h,choices in HEADS.items():
            for m in ('A16','s17','s18'):
                matrix=ev[v][m]['raw']['micro']['heads'][h]['confusion']
                L += [f'**{m}, {h}**','']+table(['Truth / prediction',*choices],[[a,*[int(matrix[a][b]) for b in choices]] for a in choices])+['']
        for m in ('A16','s17','s18'):
            matrix=ev[v][m]['raw']['micro']['dialytika_compound_confusion'];choices=list(matrix)
            L += [f'**{m}, dialytika compounds**','']+table(['Truth / prediction',*choices],[[a,*[int(matrix[a][b]) for b in choices]] for a in choices])+['']
    L += [f"BASE seed churn: **{churn} / 11,329 extraction slots** have different four-head tuples between seeds 17 and 18, independent of overlays. This observed spread is the BASE noise-floor instrument for future paired non-target comparisons; no criterion is declared passed. Full per-book results and UNKNOWN counts remain in scores.json.",'','## DEV','',f'**DEV pending: needs window extraction on Clariden for {ndev} lines** in the S8 DEV census (600 total; supplied truth has cards on 542 lines, including 527 with noncontrol cards). [Exact line list](evidence/job1/DEV_required_lines.txt), [one-stage job specification](evidence/job1/DEV_pending.json). S8 truth is a sampled word/card instrument, not complete line truth; keep its original inclusion weights, waves, controls and UNKNOWN policy. The exact crop/label/wave selection is in [DEV selection](evidence/job1/DEV_selection.jsonl). Saved A forms alone cannot establish paired BASE metrics. Inspected this worktree and the S8/original spellcheck extraction inventories; no matching BASE DEV predictions or complete DEV reader windows were available. No new cohort extraction/inference or submission was performed. The 20-min job cap is provisional; native crop/alignment paths and hashes must be bound before any coordinator submission.','', '## Validation','', 'All **1,477 labelfix tests passed**, including 10 new readback/digest regressions; see [test log](evidence/job1/tests.log). The R2 physical-truth adapter now expands compound atoms before factorisation; a real frozen-witness regression verifies all overlay versions. The historical continuity scorer and frozen runtime remain unchanged.','']
    f1=[ev['v1_1'][m]['continuity']['summary']['all_unscored_none']['total']['f1'] for m in ('s17','s18','A16')]
    final=f"R2RB READY: readback {rb['file_count']}/{rb['total_bytes']} sha ok {rb['sha256_verified']}/{rb['file_count']}; stages A {stages['A']['elapsed_seconds']/60:.6f} B {stages['B']['elapsed_seconds']/60:.3f} C {stages['C']['elapsed_seconds']/60:.3f} min vs forecast 74; teacher rows {teacher['slots']} ({'/'.join(str(inv['roles'][r]['slots']) for r in ROLES)}); BASE F1 s17 {100*f1[0]:.3f}% s18 {100*f1[1]:.3f}% vs A {100*f1[2]:.3f}%; seed churn {churn} slots; DEV pending"
    L += ['Final F1 below uses the symmetric v1.1 continuity column; without-overlay values are tabulated above.','',final]
    (OUT/'R2_JOB1_DIGEST.md').write_text('\n'.join(L)+'\n');print(final,flush=True)


def main():
    EVID.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((ROOT/'READBACK_RECEIPT.json').read_text());assert not receipt['failures']
    inv=inventory();dump(EVID/'teacher_inventory.json',inv)
    assert sum(b['lines'] for b in inv['roles'].values())==47129
    assert sum(b['slots'] for b in inv['roles'].values())==1232387
    ev,churn=evaluate();dump(EVID/'scores.json',ev);ndev=dev_pending();report(inv,ev,churn,ndev)
    finalize()


def finalize():
    dump(EVID/'digest_receipt.json',dict(inference_runs=0,network='none after verified readback',inputs={str(p):sha256(p) for p in [ROOT/'READBACK_RECEIPT.json',DEV,DEV.parent/'sources.json',DEV.parent/'baseline_per_line.jsonl',FIX/'binding.json',Path('artifacts/labelfix_r2/population/population.jsonl'),Path('scripts/labelfix/r2_readback_verify.py'),Path('scripts/labelfix/r2_score.py'),Path('tests/labelfix/test_r2_readback_digest.py'),Path(__file__),*[OUT/f'truth_overlay_{v}.json' for v in ('v0','v1','v1_1')]]},outputs={str(p):sha256(p) for p in [OUT/'R2_JOB1_DIGEST.md',EVID/'tests.log',*EVID.glob('*.json'),EVID/'DEV_required_lines.txt',EVID/'DEV_selection.jsonl'] if p.name!='digest_receipt.json'}))


if __name__=='__main__':main()
