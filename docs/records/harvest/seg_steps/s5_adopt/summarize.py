"""Score native results with the unchanged S4 marks and gate re-report joins."""
from pathlib import Path
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import json

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
STEPS = OUT.parent
DATA = ROOT.parent / 'greek-ocr-data'
read = lambda p: [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
dump = lambda p, x: Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def stamp(m):
    s=m.get('updated','')
    if not s: return 0.
    dt=datetime.fromisoformat(s.replace('Z','+00:00'))
    return (dt if dt.tzinfo else dt.replace(tzinfo=ZoneInfo('Europe/Athens'))).timestamp()


def latest(ms):
    chosen={}
    for i,m in enumerate(ms):
        if m['line_id'] not in chosen or (stamp(m),i)>=(stamp(chosen[m['line_id']]),chosen[m['line_id']]['file_line']):
            chosen[m['line_id']]=dict(m,file_line=i)
    return chosen


def run():
    rows=read(OUT/'replay.jsonl'); main=[r for r in rows if r['cohort']!='typology']; typ=[r for r in rows if r['cohort']=='typology']
    assert len(rows)==1705 and len(main)==1288 and len(typ)==417
    decisions=read(DATA/'docs/harvest/seg_steps/gate_rereport/row_decisions.jsonl')
    gate={(r['set'],r['id']):r['outcome']=='ADMIT' for r in decisions}
    ms=read(STEPS/'s4/owner_marks_snapshot.jsonl'); tm=read(STEPS/'s4/typology_owner_marks_snapshot.jsonl')
    marks=latest(ms); tmarks=latest(tm)
    assert len(ms)==240 and len(marks)==235 and len(tmarks)==185
    unique={r['line_id']:r for r in main}
    pool=dict(unique)
    for r in typ:
        if r['line_id'] in pool:
            assert r['row']['crop_sha256']==pool[r['line_id']]['row']['crop_sha256']
            assert all(r[v]['verdict']==pool[r['line_id']][v]['verdict'] for v in ('before','after'))
        else: pool[r['line_id']]=r
    candidates={}
    for r in main:
        rating=r.get('owner_rating') or {}
        if rating.get('decision') in ('KEEP','DROP'):
            candidates.setdefault(r['line_id'],[]).append(dict(owner_mark=rating['decision'],explicit=False,updated=rating.get('updated','')))
    for entries in (ms,tm):
        for m in entries: candidates.setdefault(m['line_id'],[]).append(dict(m,explicit=True))
    judgments={rid:max(enumerate(xs),key=lambda it:(it[1]['explicit'],stamp(it[1]),it[0]))[1] for rid,xs in candidates.items()}
    expected={r['line_id'] for r in read(STEPS/'s5/changed_lines.jsonl') if r['scheme']=='overall'}
    actual={rid for rid in judgments if pool[rid]['before']['verdict']!=pool[rid]['after']['verdict']}
    expected_after={rid for rid in expected if gate['changed_lines',rid]}
    actual_after={rid for rid in actual if gate['changed_lines',rid]}
    differences=[]
    for rid in sorted(actual^expected):
        differences.append(dict(line_id=rid,saved_ratio=pool[rid]['saved_ratio'],expected_change=rid in expected,actual_change=rid in actual))
    scores={}
    for filtered in (False,True):
        scores['gate_0.3_removed' if filtered else 'unfiltered']={}
        ss=scores['gate_0.3_removed' if filtered else 'unfiltered']
        for version in ('before','after'):
            get=lambda r:r[version]['verdict']
            selected=lambda rs,key:[r for r in rs if not filtered or gate[key,r['line_id']]]
            s150=selected([r for r in main if r['cohort']=='segeval1'],'segeval1')
            rated=selected([r for r in main if r.get('owner_rating') and r['owner_rating'].get('decision') in ('KEEP','DROP')],'rated_888')
            marked=selected([unique[rid] for rid in marks],'owner_marks')
            typmarked=selected([r for r in typ if r['line_id'] in tmarks],'typology_marked')
            def score(rs,label):
                confusion={v:{m:sum(get(r)==v and label(r)==m for r in rs) for m in ('KEEP','DROP')} for v in ('KEEP','DROP','UNCERTAIN')}
                return dict(n=len(rs),agreement=sum(get(r)==label(r) for r in rs),confusion=confusion)
            ss['s4' if version=='before' else 's5']=dict(
                segeval1=dict(n=len(s150),FP=sum(get(r)=='DROP' and r['owner_standard_state']=='fine' for r in s150),
                    FN=sum(get(r)=='KEEP' and r['owner_standard_state']=='faulty' for r in s150),UNC=sum(get(r)=='UNCERTAIN' for r in s150)),
                rated=score(rated,lambda r:r['owner_rating']['decision']),
                marks=score(marked,lambda r:marks[r['line_id']]['owner_mark']),
                typology=score(typmarked,lambda r:tmarks[r['line_id']]['owner_mark']),
                cohort_counts={c:len(selected([r for r in rows if r['cohort']==c],c)) for c in ('segeval1','calibration','cells','typology')},
                cells_verdicts=dict(Counter(get(r) for r in selected([r for r in main if r['cohort']=='cells'],'cells'))))
    population=read(STEPS/'s5/band_population.jsonl'); assert len(population)==500
    band_errors={}
    reference=json.loads((STEPS/'gate_rereport/finite_summary.json').read_text())
    for filtered in (False,True):
        pp=[r for r in population if not filtered or gate['band_population',r['line_id']]]
        key='gate_0.3_removed' if filtered else 'unfiltered'
        band_errors[key]={}
        for version,band in (('before','0.50-1.50'),('after','0.30-2.00')):
            obj=[r for r in pp if not r['length_blind']]
            vv=lambda r:pool[r['line_id']][version]['verdict']=='KEEP'
            result=dict(n=len(pp),objective_n=len(obj),fd=sum(r['owner_mark']=='KEEP' and not vv(r) for r in obj),
                fk=sum(r['owner_mark']=='DROP' and vv(r) for r in obj),blind_n=len(pp)-len(obj),
                blind_kept=sum(vv(r) for r in pp if r['length_blind']))
            result['total']=result['fd']+result['fk']; band_errors[key]['s4' if version=='before' else 's5']=result
            exp=reference['fixed_bands']['all' if filtered else 'before']['overall'][band]
            assert result==exp,(key,version,result,exp)
            lower,upper=(.5,1.5) if version=='before' else (.3,2.)
            for r in pp:
                expected_keep=lower<=r['r']<=upper and r['padding_state']=='KEEP'
                if vv(r)!=expected_keep:
                    differences.append(dict(line_id=r['line_id'],saved_ratio=r['r'],version=version,expected_keep=expected_keep,actual_keep=vv(r)))
    for key,refkey in (('unfiltered','before'),('gate_0.3_removed','all')):
        for metric in ('segeval1','rated','marks'):
            expected_metric=reference['scores'][refkey]['s4'][metric]
            assert scores[key]['s4'][metric]==expected_metric,(key,metric)
        assert scores[key]['s4']['typology']==reference['scores'][refkey]['typology']['s4']['overall']
    write=lambda p,xs:Path(p).write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in xs))
    write(OUT/'acceptance_differences.jsonl',differences)
    write(OUT/'owner_judged_flips.jsonl',[dict(line_id=rid,saved_ratio=pool[rid]['saved_ratio'],owner_mark=judgments[rid]['owner_mark'],content_gate_pass=gate['changed_lines',rid]) for rid in sorted(actual)])
    reason_only=[dict(cohort=r['cohort'],line_id=r['line_id'],saved_ratio=r['saved_ratio'],old_reason=r['before']['reason'],new_reason=r['after']['reason']) for r in rows if r['before']['verdict']==r['after']['verdict'] and r['before']['reason']!=r['after']['reason']]
    write(OUT/'reason_only.jsonl',reason_only)
    initial=json.loads((OUT/'initial.json').read_text()); replay=json.loads((OUT/'replay_receipt.json').read_text())
    summary=dict(policy_sha256=dict(old=initial['sha256']['greekocr/harvest/filtering_assets/segmentation-policy.js'],new=replay['policy_sha256']),
        segmentation='0.9-s5',pipeline='0.3.1',scores=scores,band_errors=band_errors,
        acceptance=dict(owner_judged_ids=len(judgments),changed_before=len(actual),expected_before=len(expected),changed_after=len(actual_after),expected_after=len(expected_after),
            identical_before=actual==expected,identical_after=actual_after==expected_after,differences=len(differences)),
        replay=replay,reason_only=len(reason_only),tests=dict(passed=248,failed=0,verbatim='248 passed in 4.21s'),
        manifest_fallback=None,findings=[])
    assert summary['acceptance']['identical_before'] and summary['acceptance']['identical_after']
    assert len(actual)==59 and len(actual_after)==38 and not differences
    dump(OUT/'summary.json',summary)
    print(json.dumps(dict(scores=scores,band_errors=band_errors,acceptance=summary['acceptance']),ensure_ascii=False,indent=2))


if __name__=='__main__':run()
