"""Offline custody and frozen-observation qualification. No new reading or geometry."""
import gzip,hashlib,json,sys,statistics
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
SEG=HERE.parent;BASE=SEG.parent;ROOT=BASE.parents[2];CP7=SEG/'cp7'
sys.path[:0]=[str(ROOT),str(CP7)]
from greekocr.harvest.qualified_admission import evaluate_evidence
from restore_cp5 import restore

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def rows(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else Path(p).open()) as f:return [json.loads(l) for l in f if l.strip()]
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def matrix(pairs):
    out=dict(TP=0,FP=0,FN=0,TN=0)
    for p,t in pairs:out[('T' if p==t else 'F')+('P' if p else 'N')]+=1
    return out

def reproduce_matrices(lead):
    overrides={r['row_id']:r for r in lead['rows']}
    for draw,path,summary in [('r1',CP7/'scored_cp7b.jsonl.gz',CP7/'score_summary_cp7b.json'),('r2',CP7/'r2/scored.jsonl.gz',CP7/'r2/score_summary.json')]:
        rr=rows(path);summ=load(summary);flagged=set(summ['adjudication_ids']);account=[]
        for r in rr:
            actual=any(r['reader'][f]=='yes' for f in ('neighbour_whole_word','multi_line','rotated','horizontally_missegmented'))
            assert actual==(r['truth']=='DROP')
            sealed=r['sealed']
            pred={f:sealed[f] is True for f in ('merged','neighbour_words','orientation')}
            pred['crossing']=sealed['crossing']['drop'] is True
            pred['union']=sealed['screen_drop'] if draw=='r1' else any(pred.values())
            if draw=='r1':pred['geometry_unavailable']=sealed['geometry_unavailable']
            assert pred==r['predictions']
        raw_population=rr if draw=='r1' else [r for r in rr if not r['sealed']['geometry_unavailable']]
        raw_recomputed={f:matrix([(r['predictions'][f],r['truth']=='DROP') for r in raw_population]) for f in summ['matrices']}
        assert all(all(value[k]==summ['matrices'][f][k] for k in ('TP','FP','FN','TN')) for f,value in raw_recomputed.items())
        for r in rr:
            if r['row_id'] not in flagged:continue
            o=overrides.get(r['row_id']) if draw=='r2' else next((x for x in lead['first_draw_r1'] if x['row_id']==r['row_id']),None)
            if o:assert o['crop_sha256']==r['crop_sha256']
            account.append(dict(row_id=r['row_id'],crop_sha256=r['crop_sha256'],reader=r['reader'],
                disposition='lead record bound' if o else ('coordinator class-wide end-clip ruling' if draw=='r1' and r['mismatches'].get('union')=='FN' else 'original reader verdict retained; diagnostic flag accounted without a new pixel claim'),
                lead=o,mismatches=r['mismatches'],flag=r['flag'],unreadable=r['unreadable']))
        assert len(account)==len(flagged)
        final=[];standalone=[]
        for r in rr:
            if r['sealed']['geometry_unavailable']:continue
            truth=r['truth']=='DROP'
            if draw=='r1' and r['mismatches'].get('union')=='FN':
                # Review section 2 explicitly adjudicates all four apparent FN
                # as admitted end-clips. This is a class ruling, no new reading.
                truth=False
            o=overrides.get(r['row_id']) if draw=='r2' else None
            if o:truth=not o['lead_verdict'].startswith('KEEP')
            standalone.append((r,truth))
            if draw=='r2' and r['sealed']['text_rules'] and not r['sealed']['text_rules']['passed']:continue
            final.append((r,truth))
        screens=('union','merged','neighbour_words','orientation','crossing')
        dump(HERE/(draw+'_matrices.json'),dict(raw_reader=summ['matrices'],raw_recomputed=raw_recomputed,
            adjudicated_standalone={s:matrix([(r['predictions'][s],t) for r,t in standalone]) for s in screens},
            text_eligible_composition={s:matrix([(r['predictions'][s],t) for r,t in final]) for s in screens},
            text_eligible_denominator=len(final),flagged_count=len(account),accounting=account,
            coordinator_ruling=lead['coordinator_ruling'],
            without_individual_lead_override=sum(x['lead'] is None for x in account),
            disposition_authority='Original reader labels retained except the committed lead overrides and review section 2 class-wide ruling on all four r1 apparent FN. Flags alone do not change admission truth.',
            unreadable_entries=sum(x['unreadable'] for x in account)))
        if draw=='r2':
            result=matrix([(r['predictions']['union'],t) for r,t in final])
            assert result['FP']==2 and result['FN']==0

def main():
    restore()
    from custody import validate
    records,controls,custody=validate()
    assert len(records)==100 and sum(c['passed'] for c in controls)==10
    dump(HERE/'custody.json',dict(mapped=100,controls=10,canonical_scan_violations=0,contexts=custody))
    lead=load(CP7/'r2/LEAD_ADJUDICATION_r2.json'); overrides={r['row_id']:r for r in lead['rows']}
    from greekocr.harvest import admission as adm
    heights=defaultdict(list)
    for path,digest in load(CP7/'build_receipt.json')['inputs'].items():
        if not Path(path).name.startswith(('W1_features_','W2_features_')):continue
        assert sha(path)==digest
        with Path(path).open() as f:
            for line in f:
                r=json.loads(line);h=adm._height(r)
                if h is not None:heights[adm._page_key(r)].append(h)
    medians={k:statistics.median(v) for k,v in heights.items()}
    parity={}
    for name,seals,inputs in [
        ('witness_r1',CP7/'keys/frozen_witness_measurements.jsonl.gz',CP7/'keys/witness_inputs.jsonl'),
        ('witness_r2',CP7/'r2/keys/frozen_witness_measurements.jsonl.gz',CP7/'keys/witness_inputs.jsonl'),
        ('r1',CP7/'keys/sealed_decisions_cp7a2.jsonl.gz',CP7/'keys/draw.jsonl'),
        ('r2',CP7/'r2/keys/sealed_decisions.jsonl.gz',CP7/'r2/keys/draw.jsonl')]:
        by={r['id']:r for r in rows(inputs)};count=0
        for s in rows(seals):
            r=by[s['row_id']]
            d=evaluate_evidence(r,screen_only='label' not in r,page_median_height=medians.get(adm._page_key(r)),structural=s['structural'],
                axis=s['orientation_observation'],crossing=s['crossing'],edge=dict(s.get('edge_clip_diagnostic') or {},candidate=s.get('edge_clip_candidate')))
            if s['text_rules']:
                text=d['text'];checks={k:v for k,v in text['checks'].items() if k not in ('geometry_unavailable','neighbour_words')}
                assert dict(checks=checks,**adm.non_segmentation_eligibility(text['checks']))==s['text_rules'],s['row_id']
                assert d['admission_drop']==s['admission_drop']
            assert d['composed']==s['composed'] and d['screen_drop']==s['screen_drop'],s['row_id']
            assert d['hits']['merged']==(s['merged'] is True)
            assert d['hits']['neighbour_words']==(s['neighbour_words'] is True)
            assert d['hits']['orientation']==(s['orientation'] is True)
            if 'edge_clip_candidate' in s:assert d['edge_clip_candidate']==s['edge_clip_candidate']
            count+=1
        parity[name]=dict(matched=count,total=count,scope='frozen geometry observations; complete composition; text re-evaluated with original snapshot pre-drop medians')
    dump(HERE/'parity.json',parity)
    reproduce_matrices(lead)
    print(json.dumps(parity))
if __name__=='__main__':
    if '--evidence-only' in sys.argv:
        restore()
        from custody import validate
        r,c,s=validate()
        assert len(r)==100 and sum(x['passed'] for x in c)==10
        reproduce_matrices(load(CP7/'r2/LEAD_ADJUDICATION_r2.json'))
        print('portable evidence: mapping 100/100; controls 10/10; scans 0 violations; final FP2 FN0')
    else:main()
