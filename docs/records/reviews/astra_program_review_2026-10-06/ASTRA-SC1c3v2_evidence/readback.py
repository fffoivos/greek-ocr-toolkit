"""Independent readback of SF5 replay records and the declared truth scopes."""
from collections import Counter
from pathlib import Path
import json
import unicodedata as u

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows,sha256
from scripts.labelfix.sf5_measure import baseline,BINDING
from scripts.labelfix.r0_score import align

ROOT=Path.cwd();DOC=ROOT/'docs/labelfix/spellcheck';OUT=Path(__file__).parent
ALIASES="'’ʼ᾽᾿"


def letter(c):return c.isalpha() and c not in ALIASES


def all_sites(text,model):
    # Scan codepoints instead of the new punctuation_sites helper. Retain
    # initial elisions as required by R0; omit spacing breathings and marked
    # punctuation. Boundary mapping uses the frozen R0 alignment definition.
    chars=u.normalize('NFD',text);bare=''.join(c for c in chars if not u.combining(c))
    source=''.join(c for c in u.normalize('NFD',model) if letter(c))
    target=''.join(c for c in chars if letter(c));boundary=0;signs=set()
    for i,c in enumerate(bare):
        if letter(c):boundary+=1
        if c not in ALIASES:continue
        breathing=(c in '᾿᾽' and i+1<len(bare) and letter(bare[i+1]) and
            (bare[i+1].isupper() or bare[i+1] in 'αεηιουωΑΕΗΙΟΥΩ' and (i==0 or not letter(bare[i-1]))))
        if not breathing:signs.add(boundary)
    mapping={j:i for i,j in align(source,target,True) if i is not None and j is not None}
    return {mapping[k-1]+1 if k-1 in mapping else mapping[k] if k in mapping
            else 0 if k==0 else len(source) for k in signs}


def main():
    result={};oldgate,oldcommon=baseline()
    for cohort in ('heldout','m2_dev'):
        fresh=json.loads((OUT/cohort/'metrics.json').read_text())
        assert fresh==json.loads((DOC/'SF5_evidence'/cohort/'metrics.json').read_text())
    result['metrics_match_report_artifacts']=True
    # Check actual slot records, not the boolean proof rows.
    old={r['id']:r for r in rows(DOC/'SF4_evidence/heldout/decisions.jsonl.gz')}
    new={r['id']:r for r in rows(OUT/'heldout/decisions.jsonl.gz')}
    count=0
    assert old.keys()==new.keys() and len(old)==666
    for lid,a in old.items():
        for mode in gate.MODES:
            x=a['decisions'][mode];y=new[lid]['decisions'][mode]
            assert x['slots']==y['slots'] and x['hold_slots']==y['hold_slots']
            count+=len(x['slots'])
    result['heldout']=dict(lines=666,slot_mode_records_identical=count,
        full_runtime_recomposition=False,method='Saved decisions plus current render/guard replay')
    before={};after={}
    for r in rows(OUT/'m2_dev/decisions.jsonl.gz'):(before if r['phase']=='before' else after)[r['id']]=r
    count=0
    assert len(before)==len(after)==273 and before.keys()==after.keys()
    for lid,a in before.items():
        for mode in gate.MODES:
            x=a['modes'][mode];y=after[lid]['modes'][mode]
            assert x['slots']==y['slots'] and x['hold_slots']==y['hold_slots']
            count+=len(x['slots'])
    result['m2_dev']=dict(cards=273,slot_mode_records_identical=count,full_saved_runtime_recomposition=True)
    witnesses=[];count=0
    for r in rows(OUT/'witness_inputs.jsonl.gz'):
        oldvalue=oldcommon.overlay(r['record'],r['runtime'],'ENSEMBLE_AB',BINDING)
        assert (oldvalue['status'],oldvalue.get('label'))==(r['before_status'],r['before'])
        x=oldgate.compose_runtime(r['runtime'],'ENSEMBLE_AB');y=gate.compose_runtime(r['runtime'],'ENSEMBLE_AB')
        assert x['slots']==y['slots']==r['sf4_decisions']['slots'] and x['hold_slots']==y['hold_slots']
        count+=len(y['slots'])
    witnesses=list(rows(OUT/'witness_results.jsonl.gz'))
    assert witnesses==list(rows(DOC/'SF5_evidence/witness_results.jsonl.gz'))
    result['witnesses']=dict(lines=len(witnesses),slot_records_identical=count,
        consensus_atoms=sum(r['consensus'] for r in witnesses),consensus_kept=sum(r['consensus_kept'] for r in witnesses),
        capital_breathings=sum(r['kind']=='capital_breathing' for r in witnesses),
        known_errors_unchanged=sum(r['kind'].startswith('known_reader_') and r['before']==r['after'] for r in witnesses),
        single_source_deletion_rows=[{k:r[k] for k in ('id','google','recogniser','after','elision_census')} for r in witnesses if r['elision_census'].get('google_only_deleted')],
        retained_initial_prefix_edits=[{k:r[k] for k in ('id','google','recogniser','after')} for r in witnesses if r['id'] in (
            '453f156dc6352286456a08cb-p000100-l0002','b518f9f9b73fe9a3257fe2f0-p000041-l0022')])
    sources={r['line_id']:r for r in rows(DOC/'R0_evidence/continuity_666.jsonl')}
    sites=[]
    for line in (DOC/'R0_evidence/scoring/punctuation_sites.jsonl').open():
        if '"stratum": "continuity_666"' in line:sites.append(json.loads(line))
    assert len({(s['line_id'],s['letter_boundary'],s['rank']) for s in sites})==len(sites)
    known=[s for s in sites if s['status']=='KNOWN' and s['printed_role']!='quote']
    positives=[s for s in known if s['printed_role']=='apostrophe_elision']
    negatives=[s for s in known if s['printed_role']=='absent']
    assert len(known)==len(positives)+len(negatives)
    human_pos=sum(s['emitted']['human'] in set("'’ʼ᾽᾿`´") for s in positives)
    human_neg=sum(s['emitted']['human']=='' for s in negatives)
    result['truth']=dict(positive_sites=len(positives),negative_sites=len(negatives),lines=len({s['line_id'] for s in known}),
        quote_sites=sum(s['status']=='KNOWN' and s['printed_role']=='quote' for s in sites),unknown_sites=sum(s['status']!='KNOWN' for s in sites),
        human_positive=human_pos,r0_fallback_positive=len(positives)-human_pos,
        human_total=human_pos+human_neg,r0_fallback_total=len(known)-human_pos-human_neg,full_lines_certified=0)
    assert result['truth']==dict(positive_sites=213,negative_sites=5,lines=180,
        quote_sites=10,unknown_sites=1,human_positive=212,r0_fallback_positive=1,
        human_total=214,r0_fallback_total=4,full_lines_certified=0)
    releases={(r['phase'],r['mode'],r['id']):r for r in rows(OUT/'heldout/release_labels.jsonl.gz')}
    event_counts={};trace=[]
    for phase in ('before','after'):
        for mode in gate.MODES:
            counts=Counter();maps={}
            for s in known:
                lid=s['line_id'];record=releases[phase,mode,lid]
                if lid not in maps:maps[lid]=all_sites(record['label'],sources[lid]['model'])
                present=s['letter_boundary'] in maps[lid]
                positive=s['printed_role']=='apostrophe_elision'
                outcome=('kept' if present else 'deleted') if positive else ('added' if present else 'absent')
                counts[outcome]+=1
                if mode=='ENSEMBLE_AB' and outcome in ('deleted','added'):
                    trace.append(dict(phase=phase,id=lid,boundary=s['letter_boundary'],outcome=outcome,
                        source_status=record['status'],google=sources[lid]['google'],effective_label=record['label'],
                        r0_emitted=s['emitted'],card_ids=s['card_ids']))
            expected=json.loads((OUT/'heldout/metrics.json').read_text())['elision'][phase][mode]['effective_release']
            assert all(counts[k]==expected[k] for k in ('kept','deleted','added','absent'))
            event_counts[phase+':'+mode]=dict(counts)
    result['independent_elision_counts']=event_counts;result['AB_omission_and_addition_trace']=trace
    m2=json.loads((OUT/'m2_dev/metrics.json').read_text());result['m2_source_census_after']=m2['after']['elision_census']
    result['heldout_source_census_after']=json.loads((OUT/'heldout/metrics.json').read_text())['elision_census']['after']
    # The source-bound receipts are checked against original bytes too.
    verified=0
    for receipt_path in [DOC/'SF5_evidence/witness_inputs_receipt.json',OUT/'heldout/receipt.json',OUT/'m2_dev/receipt.json']:
        for path,digest in json.loads(receipt_path.read_text())['inputs'].items():
            assert sha256(path)==digest,path
            verified+=1
    result['input_hashes_verified']=verified
    (OUT/'readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('AB_omission_and_addition_trace','heldout_source_census_after','m2_source_census_after','witnesses')},indent=2))
    print('witnesses:',{k:v for k,v in result['witnesses'].items() if not isinstance(v,list)})


if __name__=='__main__':main()
