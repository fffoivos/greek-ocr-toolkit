"""LQB5 offline build: admitted weighted DEV, frozen truth, explicit release gaps."""
from __future__ import annotations
from collections import defaultdict
import copy
import html
import json
import sys
import unicodedata as ud
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import build_v2_1 as prior
import build_v2 as v2
from greekocr.labelfix import lqb
OUT=lqb.DEFAULT
POPULATION='v2 train greek_poly, training wave; S8 600-line DEV connected-word census (4,942 groups)'
READERS=['two blind Opus readers; third-reader majority tiebreak; lead LQB5 admission ruling']
ORIGINAL_DEV=prior.dev_records

def dev_records(inputs,tier):
    rs,google,ids,n=ORIGINAL_DEV(inputs,tier)
    for r in rs:
        r.update(sample_type='weighted_stratified',readers=READERS,
                 sample_description='S8 DEV weighted_stratified; unweighted counts on the sample',
                 population=POPULATION,weighted_population_eligible=True)
        # Generic unweighted scorer must never promote these to a population rate.
        r['population_eligible']=False
        r['context']['weight_applied']=False
        r['context']['weight_source']='saved S8a6 dev_truth.jsonl.gz weight; applied only in weighted_dev ledger'
    return rs,google,ids,n


def weighted(entries, seed=20261017, replicates=4000):
    """Hájek ratios; independently resample documents inside each wave.

    entries: wave, document, fixed saved card weight, errors, opportunities.
    No inclusion probabilities or wave weights are calculated here.
    """
    groups=defaultdict(lambda:defaultdict(lambda:np.zeros(2)))
    raw_e=raw_n=0
    for wave,doc,w,e,n in entries:
        assert np.isfinite(w) and w>0
        groups[wave][doc]+=np.array([e,n])*w;raw_e+=e;raw_n+=n
    total=sum((v for ds in groups.values() for v in ds.values()),np.zeros(2))
    result=dict(status='measured' if total[1] else 'not measured',errors_on_sample=raw_e,opportunities_on_sample=raw_n,
                weighted_errors=float(total[0]),weighted_opportunities=float(total[1]),rate=float(total[0]/total[1]) if total[1] else None,
                ci95=None,ci_method='percentile document bootstrap within waves; fixed saved S8a6 weights',
                seed=seed,replicates=replicates,valid_replicates=0,documents_by_wave={w:len(ds) for w,ds in groups.items()},population=POPULATION)
    if not total[1]:return result
    rng=np.random.default_rng(seed);boot=np.zeros((replicates,2))
    for wave,ds in sorted(groups.items()):
        m=np.array([ds[d] for d in sorted(ds)])
        for start in range(0,replicates,128):
            take=rng.integers(len(m),size=(min(128,replicates-start),len(m)))
            boot[start:start+len(take)]+=m[take].sum(1)
    ratios=boot[boot[:,1]>0,0]/boot[boot[:,1]>0,1]
    result.update(ci95=np.quantile(ratios,[.025,.975]).tolist(),valid_replicates=len(ratios))
    return result


def dev_entries(rs,predictions,numerator=None):
    entries=[]
    for r in rs:
        if r['line_id'] not in predictions:continue
        value=lqb.error(r,predictions[r['line_id']])
        if value is None:continue
        e,n=value
        if numerator:e=numerator(r,predictions[r['line_id']])
        entries.append((r['context']['wave'],r['doc_id'],r['context']['card_weight'],e,n))
    return entries


def direction_error(r,text,direction):
    err=lqb.error(r,text)
    if err is None or not err[0]:return 0
    zero=dict(r,target=0)
    if r['slot']['kind'] in ('scoped_mark','word_letter'):
        # Scoped scorer reads printed_word, so change the actual tested head,
        # preserving the alignment bases and every other truth head.
        ctx=dict(r['context']);cs=lqb.clusters(ctx['printed_word']);letter=-1
        marks={'breathing':'\u0313\u0314','accent':'\u0301\u0300\u0342','dialytika':'\u0308','subscript':'\u0345'}
        for i,c in enumerate(cs):
            if c[0].isalpha():letter+=1
            if c[0].isalpha() and letter==r['slot']['letter']:
                cs[i]=''.join(x for x in ud.normalize('NFD',c) if x not in marks[r['slot']['head']]);break
        ctx['printed_word']=''.join(cs);zero['context']=ctx
    positive=bool(lqb.error(zero,text)[0])
    actual='extra' if not r['target'] else 'wrong mark' if positive else 'missing'
    return int(actual==direction)


def make_baseline(truth,google,inputs,weighted_google):
    old=v2.baseline(truth,google,inputs)
    for r in old:
        if r['source_set'].startswith('C1/') and r['n']:
            field='marks' if r['metric'].startswith('marks (') else 'letters' if r['metric'].startswith('letters /') else 'crop' if r['metric'].startswith('crop (') else None
            if field:r.update({field+'_y':r['n']-r['errors'],field+'_n':r['errors']})
    dev=[r for r in truth if r['provenance']['set']=='S8_DEV']
    def wr(metric,rs,fn=None):
        x=weighted_google if metric=='all known mark heads' else weighted(dev_entries(rs,google,fn))
        return dict(class_name='polytonic marks',stratum='S8 DEV / all five waves',source_set='S8_DEV',metric=metric,
                    errors=x['errors_on_sample'],n=x['opportunities_on_sample'],rate=x['rate'],ci95=x['ci95'],
                    sample_type='weighted_stratified',tier='A',status=x['status'],truth_needed=None,weighted=x)
    old.append(wr('all known mark heads',dev))
    for source in ['S8_DEV','audit100','substitution60']:
        rs=[r for r in truth if r['class']=='marks' and any(p['set']==source for p in r['provenance_all'])]
        for head in lqb.HEADS:
            hs=[r for r in rs if r['slot']['head']==head and r['line_id'] in google]
            if not hs:continue
            for direction in ['missing','extra','wrong mark']:
                fn=lambda r,t,d=direction:direction_error(r,t,d)
                if source=='S8_DEV':row=wr(head+' / '+direction,hs,fn)
                else:
                    vals=[r for r in hs if lqb.error(r,google[r['line_id']]) is not None]
                    row=v2.measurement('polytonic marks',source+' / certified heads only',source,head+' / '+direction,
                        sum(fn(r,google[r['line_id']]) for r in vals),len(vals),typ='decision_audit')
                old.append(row)
    result=[]
    for cls in dict.fromkeys(r['class_name'] for r in old):
        rows=[r for r in old if r['class_name']==cls]
        result.extend(r for r in rows if r['status']=='measured')
        gaps=[r for r in rows if r['status']!='measured']
        # One collapsed gap line per class, preserving every original scope.
        if not gaps:
            gaps=[v2.measurement(cls,'outside named strata','registered source inventory','class-wide population',need='Certified probability-sample truth beyond the named measured strata; no class-wide extrapolation.')]
        if gaps:
            result.append(dict(class_name=cls,stratum='remaining scopes',source_set='; '.join(dict.fromkeys(r['source_set'] for r in gaps)),
                metric='not measured (collapsed)',n=None,errors=None,rate=None,ci95=None,sample_type='not measured',tier='not assigned',status='not measured',
                truth_needed='; '.join(r['stratum']+' / '+r['metric']+': '+str(r['truth_needed']) for r in gaps),unmeasured_scopes=gaps))
    return result


def rate_text(r):
    if r.get('weighted'):
        x=r['weighted'];lo,hi=x['ci95']
        return f"weighted estimate {100*x['rate']:.3f}%; 95% document-within-wave bootstrap CI {100*lo:.3f}–{100*hi:.3f}%; {x['errors_on_sample']}/{x['opportunities_on_sample']} on the sample"
    s=v2.rate_text(r)
    for field in ['marks','letters','crop']:
        if field+'_y' in r:s+=f"; {field}_y/n {r[field+'_y']}/{r[field+'_n']}"
    if r['n']:s+=' on the sample' if r['sample_type']=='decision_audit' else ''
    return s


def summary_html(score):
    h=prior.read(OUT/'headline_v2.json');base=prior.read(OUT/'baseline_v2.json')
    # Reuse the established score/version table, replace only the baseline body.
    old=v2.summary_html(score)
    a=old.index('<tbody>');b=old.index('</tbody>',a)
    rows=[]
    for r in base:
        vals=[r['class_name']+' / '+r['metric'],r['stratum'],rate_text(r),r['sample_type'],r['tier'],r['source_set']]
        if r['status']=='not measured':
            rows.append('<tr class="not-measured"><td>'+html.escape(r['class_name'])+'</td><td colspan="5"><details><summary>Not measured — remaining scopes</summary>'+html.escape(r['truth_needed'])+'</details></td></tr>')
        else:rows.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in vals)+'</tr>')
    old=old[:a+7]+''.join(rows)+old[b:]
    old=old.replace('<section class="lqb-intro">','<section class="lqb-intro"><p id="bottom-line">'+html.escape(h['bottom_line'])+'</p>',1)
    old=old.replace('Uniform and locked sources only.','Measured strata first, then one collapsed gap line per class. DEV is a weighted_stratified estimate using saved S8a6 weights.')
    old=old.replace('LQB3_RECEIPT.json','LQB5_RECEIPT.json').replace('on this sample','on the sample').replace('Google errors/n; rate; 95% Wilson CI','Google errors/n; rate; 95% interval')
    return old


def main():
    inputs={};xs,sx=prior.verify_sx1(inputs)
    for p in [Path(__file__),lqb.ROOT/'docs/records/briefs/LQB5_finish_v2.md',lqb.ROOT/'scripts/lqb/build_v2_1.py',lqb.ROOT/'scripts/lqb/build_v2.py',lqb.ROOT/'scripts/lqb/build_truth.py',lqb.ROOT/'scripts/lqb/build_scoreboard.py',lqb.ROOT/'greekocr/labelfix/lqb.py']:prior.bind(p,inputs)
    prior.dev_records=dev_records
    truth,manifest,google=prior.build_truth(inputs,'A')
    manifest['dev'].update(sample_type='weighted_stratified',reader_model_identity='two blind Opus readers + third-reader tiebreak; lead LQB5 ruling',
        controls=dict(r1='82/84',r2='82/84',shared_misses=0),population_rate='weighted estimates only',population=POPULATION,
        excluded_unadjudicated=671,excluded_unknown=2,weight_source=str(prior.DEV/'evidence/dev_truth.jsonl.gz'),weight_policy='read saved weight verbatim; no re-derivation')
    cards=[]
    for r in lqb.rows(prior.DEV/'evidence/dev_truth.jsonl.gz'):
        if r.get('type')=='item' and not r.get('control') and r.get('status')=='resolved':
            cards.append({k:r[k] for k in ['id','line_id','wave','truth','weight','selection']})
            cards[-1]['known_heads']=4*len(lqb.letters(r['truth']))
    assert len(cards)==976
    prior.write_rows(OUT/'truth_v1_1_dev_cards.jsonl',cards)
    manifest['dev'].update(cards_with_mark_heads=sum(bool(r['known_heads']) for r in cards),
        resolved_cards_without_letters=sum(not r['known_heads'] for r in cards),
        card_ledger_sha256=lqb.sha256(OUT/'truth_v1_1_dev_cards.jsonl'))
    lqb.dump(OUT/'truth_v1_1.manifest.json',manifest)
    registry=prior.prepare_versions(xs,inputs,google);names=list(registry['versions'])
    items,_=lqb.load_truth(OUT/'truth_v1_1.jsonl');wanted={r['line_id'] for r in items};cache={}
    pred={n:lqb.load_version(n,registry,wanted,cache) for n in names}
    score=lqb.run(OUT/'truth_v1_1.jsonl',registry,names)
    score['paired']['google_raw→sf6_release']=lqb.paired(items,pred['google_raw'],pred['sf6_release'],'google_raw','sf6_release')
    dev=[r for r in items if r['provenance']['set']=='S8_DEV']
    score['weighted_dev']={n:weighted(dev_entries([r for r in dev if not lqb.sample_used(r,n,lqb.training_arms(n,registry))],pred[n])) for n in names}
    for n,x in score['weighted_dev'].items():
        x.update(population_estimate_eligible=x['opportunities_on_sample']==len(dev),
                 scope='all certified DEV heads' if x['opportunities_on_sample']==len(dev) else 'covered out-of-sample DEV subset only; not a population estimate')
    wg=score['weighted_dev']['google_raw']
    base=make_baseline(items,lqb.load_version('google_raw',registry),inputs,wg);lqb.dump(OUT/'baseline_v2.json',base)
    h=prior.headline(items,pred,registry)
    # Bind actual coverage. A sparse release subset cannot estimate full DEV.
    covered=[r for r in dev if r['line_id'] in pred['sf6_release'] and r['line_id'] in pred['google_raw']
             and lqb.error(r,pred['sf6_release'][r['line_id']]) is not None and lqb.error(r,pred['google_raw'][r['line_id']]) is not None]
    diff=[]
    for r in covered:
        ae,n=lqb.error(r,pred['google_raw'][r['line_id']]);be,_=lqb.error(r,pred['sf6_release'][r['line_id']])
        diff.append((r['context']['wave'],r['doc_id'],r['context']['card_weight'],be-ae,n))
    change=weighted(diff)
    covered_pair=dict(status='covered_subset_only',population_estimate_eligible=False,heads=len(covered),
        google=weighted(dev_entries(covered,pred['google_raw'])),sf6=weighted(dev_entries(covered,pred['sf6_release'])),
        weighted_delta=change['rate'],weighted_delta_ci95=change['ci95'],bootstrap=change,
        limitation='Two documents in two waves only, one document per wave: degenerate document bootstrap; not evidence of full-DEV uncertainty')
    pair=dict(status='not measured',sample_type='weighted_stratified',
        reason='Full DEV population delta unavailable: saved sf6 release labels cover only 2/391 certified lines; frozen_AB includes HOLD proposals',
        delta=None,ci95=None,google_weighted=wg,covered_subset=covered_pair,
        sf6_covered_lines=len({r['line_id'] for r in covered}),resolved_cards=976,excluded_unadjudicated=671,excluded_unknown=2)
    assert pair['sf6_covered_lines']==2 and len(covered)==76
    h['by_source']['S8_DEV/weighted_stratified']=pair
    audit=h['by_source']['audit100/decision_audit']
    h['line']=f"DEV (weighted_stratified): population delta not measured (2/391 certified lines covered; covered subset weighted delta {100*change['rate']:+.3f} pp, degenerate document-within-wave bootstrap); audit100 (decision_audit): {audit['a_errors']} → {audit['b_errors']} errors / {audit['items']} heads on the sample; substitution60 (decision_audit): release delta not measured (0/57 certified lines covered)"
    h['bottom_line']=f"Marks change: Google → sf6 release falls from {audit['a_errors']} to {audit['b_errors']} errors on audit100's {audit['items']} known heads on the sample. DEV release coverage is only 2/391 certified lines, so its weighted population change is not measured; substitution60 has no saved release coverage. The DEV Google baseline is {100*wg['rate']:.3f}% weighted head errors, using the 976 resolved cards and excluding 671 unread cards and 2 UNKNOWN. DEV is out-of-sample for frozen sf6 and in-sample for S8b; audit results describe sampled decisions."
    lqb.dump(OUT/'headline_v2.json',h);lqb.dump(OUT/'score_v2.json',score)
    prior.build_page(score,truth,summary_renderer=summary_html)
    report(manifest,h,base,score)
    outputs=['truth_v1_1_dev_cards.jsonl','versions.json','truth_v1_1.jsonl','truth_v1_1_flags.jsonl','truth_v1_1.manifest.json','truth_v1_1.sha256','truth_v1_1_conflicts.jsonl','truth_v1_1_exclusion_ids_new.txt','score_v2.json','baseline_v2.json','headline_v2.json','scoreboard.html','scoreboard_cards.json','scoreboard_build.json','SCORE_v2.md','sf6_release_labels_v2.jsonl','google_truth_v1_1.jsonl']
    receipt=dict(schema='lqb5-v2.2',network=False,git_writes=False,peer_writes=False,browser_launched=False,new_readers=0,inputs=inputs,sx1=sx,
        dev_tier_ruling=READERS[0],truth=dict(items=manifest['items'],sha256=manifest['sha256'],added=manifest['added'],exclusion_new=manifest['exclusion_new']),
        headline=h['line'],baseline_measured_rows=sum(r['status']=='measured' for r in base),versions=len(names),
        unresolved=['Full-DEV sf6 release coverage unavailable offline (only 2/391 certified lines); substitution60 absent; full-DEV population delta undefined'],outputs={n:lqb.sha256(OUT/n) for n in outputs})
    lqb.dump(OUT/'LQB5_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('inputs','outputs')},ensure_ascii=False))


def report(m,h,base,score):
    md=['# Label Quality Scoreboard v2.2','',h['bottom_line'],'','## Marks headline','',h['line'],'','## Truth v1.1','',
        f"{m['items']:,} items; SHA256 `{m['sha256']}`. Added DEV {m['added']['S8_DEV']:,} heads and substitution60 {m['added']['substitution60']} heads. Frozen v1 and flags are unchanged. Tier A DEV admission: two blind Opus readers plus third-reader tiebreak, controls 82/84 each with zero shared misses, per lead ruling and [S8a6 source](../.. /spellcheck/S8a6_DEV_TRUTH.md). No new readers ran.",'',
        'DEV is `weighted_stratified`, in-sample for S8b and out-of-sample for frozen sf6. The 600 lines were stratified by wave; cards include all disagreement word groups and 5% all-agree words per wave. Only 976 resolved cards enter the card ledger: 671 unadjudicated data cards and 2 UNKNOWN are excluded, as are controls. Eight resolved cards contain no letters and contribute zero mark heads; 968 cards contribute the 21,892 DEV mark heads. All 976 resolved card IDs, printed forms and saved weights are retained in truth_v1_1_dev_cards.jsonl. Substitution60 is a decision audit: 63 certified heads on 57 lines; 3 lines remain UNKNOWN. Only the reviewed heads are certified.','',
        '## Weights, population and uncertainty','',
        'Population: '+POPULATION+'. The estimate is limited to the documented DEV draw; it does not establish performance outside these DEV lines. Every slot inherits its saved S8a6 card weight from `S8_DEV/evidence/dev_truth.jsonl.gz` (inverse card-inclusion × wave-cut weight). Weights are read verbatim, never re-derived, rescaled or redistributed after exclusions. Hájek error ratios use weighted error sums divided by weighted known head opportunities. Unweighted counts are labelled "on the sample".','',
        'The weighted Google baseline and every covered version use 4,000 percentile bootstrap replicates, seed 20261017, independently resampling documents with replacement within each wave, retaining fixed card weights and all contributing slots per document. The machine ledger retains weighted numerators, denominators, documents per wave and valid replicates. Reader error and extrapolation beyond the source draw are not included. Generic version tables retain unweighted sample counts and cannot promote weighted_stratified to an unweighted population rate.','',
        '**Limited release comparison:** verified SX1 v2 covers only 2/391 certified DEV lines (76 heads in two documents, one per contributing wave) and no substitution60 lines. A weighted paired difference with 4,000 document-within-wave bootstrap replicates is retained for that covered subset; its interval is degenerate because each contributing wave has only one document. It is explicitly not a DEV population estimate. Full-DEV and substitution60 release deltas remain not measured. The saved S8a6 `frozen_AB` values include HOLD proposals and cannot be substituted for released labels. Full-DEV coverage is required to compute the requested population headline offline. Audit100 has 99/99 actual ENSEMBLE_AB releases; its selected decision-audit delta is descriptive, with document-bootstrap intervals in the headline ledger.','',
        '## BASELINE — Google against truth','',
        'Within each class, measured rows come first: C1 card verdicts (explicit marks_y/n, letters_y/n and crop_y/n), locked strata where certified, other admitted strata and DEV weighted. One collapsed line then lists every unmeasured scope. C1 aggregate verdicts do not imply per-head truth. Head/direction rows are shown only for DEV, audit100 and substitution60, using each known head as the denominator; absent, extra and wrong-positive marks are mutually exclusive errors. Unknown and unavailable heads are excluded. Partial substitution truth does not certify other heads.','',
        '| Class / metric | Stratum | Measurement | sample_type | Tier | Source |','|---|---|---|---|---|---|']
    for r in base:
        md.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in [r['class_name']+' / '+r['metric'],r['stratum'],rate_text(r),r['sample_type'],r['tier'],r['source_set']])+' |')
    md+=['','## Custody and reproduction','',
        f"All {len(score['versions'])} registered versions were rescored. SX1 v2 SHA, byte size, production receipt, v1 preservation and audit100 membership verified; sf6_release reads only ENSEMBLE_AB release labels. Historical PRESENCE/FULL remains sf6_presence_full. N1 remains UNADOPTED. [Machine scores](score_v2.json), [headline ledger](headline_v2.json), [manifest](truth_v1_1.manifest.json), [receipt](LQB5_RECEIPT.json).",'',
        'The 60 new exclusion IDs omit registered classes and all 600 DEV IDs under the lead eval_only_dev instruction. The old on-disk DEV class has zero overlap; 600 IDs still require sourcing synchronization. No peer registry was written and nothing was sent.','',
        '```sh','PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/build_v2_2.py','PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest tests/test_lqb.py tests/test_lqb3.py tests/test_lqb4.py tests/test_lqb5.py -q -p no:cacheprovider --basetemp=/private/tmp/lqb5-pytest','PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/validate_scoreboard.py','PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/finalize_v2_2.py','```','',
        'Network OFF; no .git writes, peer writes, inference, publication, browser or computer-use tools. HTML structural checks and native PNG decoding are performed; rendered desktop/narrow layout is unverified by instruction. Historical LQB3 artifacts remain in validation/lqb3/frozen/.']
    text='\n'.join(md).replace('../.. /spellcheck/S8a6_DEV_TRUTH.md',str(prior.DEV.parent/'S8a6_DEV_TRUTH.md'))
    (OUT/'SCORE_v2.md').write_text(text+'\n')

if __name__=='__main__':main()
