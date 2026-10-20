"""LQB4 offline truth extension and v2.1 scoreboard; no git or network operations."""
from __future__ import annotations
from collections import Counter, defaultdict
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unicodedata as ud
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.labelfix import lqb
import build_v2 as v2
from build_truth import Builder, deduplicate
OUT=lqb.DEFAULT
SPELL=lqb.PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck'
DEV=lqb.PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV'
SX=v2.SX

def read(p):return json.loads(_data_input(Path(p)).read_text())
def write_rows(p,rs):Path(p).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rs))
def bind(p,inputs):
    p=Path(p);inputs[str(p)]=lqb.sha256(p);return p

def verify_sx1(inputs):
    """Fail before any output mutation if extract/custody/audit checks fail."""
    r=read(bind(SX/'RECEIPT_v2.json',inputs))
    for field in ['extract','not_in_selection','truth_input','script']:
        e=r[field];p=Path(e.get('local_path',e.get('path')))
        if not p.is_absolute():p=SX.parents[1]/p
        assert lqb.sha256(bind(p,inputs))==e['sha256'],field
    xs=list(lqb.rows(SX/'sf6_release_extract_lqb_v2.jsonl'))
    missing={x['line_id'] for x in lqb.rows(SX/'not_in_selection.jsonl')}
    old=list(lqb.rows(SX/'truth_v1_input.jsonl'));ids={x['line_id'] for x in xs}
    assert len(ids)==len(xs)==r['counts']['in_selection']==101
    assert not ids&missing and ids|missing=={x['line_id'] for x in old}
    assert r['extract']['sha256']==r['remote']['extract_sha256']
    assert r['extract']['bytes']==(SX/'sf6_release_extract_lqb_v2.jsonl').stat().st_size
    assert r['validation']['passed'] and r['extract']['transfer_sha_verified']
    registry=read(OUT/'versions.json')
    prod=Path(registry['versions']['sf6_release']['receipt_local'])
    assert lqb.sha256(bind(prod,inputs))==r['remote']['receipt_sha256']
    for rel,h in r['v1_preservation']['files'].items():assert lqb.sha256(bind(SX.parents[1]/rel,inputs))==h
    v1={x['line_id']:x for x in lqb.rows(SX/'sf6_release_extract_lqb.jsonl')}
    audit={x['line_id'] for x in lqb.rows(OUT/'truth_v1.jsonl') if any(p['set']=='audit100' for p in x['provenance_all'])}
    for x in xs:
        assert x['google_text']==v1[x['line_id']]['google_text']
        for mode in ['PRESENCE','FULL']:assert x['modes'][mode]==v1[x['line_id']]['modes'][mode]
        for m in x['modes'].values():
            if m['status']=='HOLD':assert m['label'] is None and m['hold_reasons']
            else:assert m['status'] in ('released-corrected','released-unchanged') and isinstance(m['label'],str)
    released={x['line_id'] for x in xs if x['modes']['ENSEMBLE_AB']['status']!='HOLD'}
    assert len(audit)==len(audit&released)==99
    assert {x['line_id'] for x in xs if 'audit100' in x['truth_sets']}==audit
    assert r['counts_by_truth_set']['audit100']['modes']['ENSEMBLE_AB']['released']==99
    assert r['audit100_ensemble_ab_check']==dict(expected=99,released_corrected=99,held=0,passed=True)
    assert len(released)==r['counts']['modes']['ENSEMBLE_AB']['released']==99
    return xs,dict(verified=True,audit100_released=99,audit100_total=99,extract_sha256=r['extract']['sha256'],mode='ENSEMBLE_AB')

def metadata(name,p,inputs,tier,readers,typ,used=(),description=''):
    return dict(tier=tier,readers=readers,sample_type=typ,sample_description=description,
        provenance=dict(set=name,file=str(bind(p,inputs)),sha256=lqb.sha256(p),commit='33cacf520 or later; exact file SHA is authoritative'),
        used_by=list(used),exclude_from_training=True,rate_eligible=True,population_eligible=False)

def substitution_records(inputs):
    p=SPELL/'R2_evidence/substitution_sample_60.json';sample=read(bind(p,inputs))['sample']
    notes={r['db_id']:r['note'] for r in lqb.rows(bind(SPELL/'R2_evidence/owner_sheet_notes_20261017.jsonl',inputs)) if r['sheet']=='Accent Substitutions'}
    bind(SPELL/'R2_evidence/OWNER_REMARKS_20261017.md',inputs)
    bind(SPELL/'R2_evidence/page_builders/build_subst_page.py',inputs)
    meta=metadata('substitution60',p,inputs,'A',['owner; no note = shown substitution right, per saved sheet protocol'],'decision_audit',description='60 owner-reviewed sf6 substitution-proposal lines (20 per detector group); certified changed heads only')
    b=Builder();unknown=[];google=[];allids=set()
    names={'none':0,'psili':1,'dasia':2,'acute':1,'grave':2,'circumflex':3}
    for group,rs in sample.items():
        assert len(rs)==20
        for r in rs:
            lid=r['line_id'];assert lid not in allids;allids.add(lid)
            google.append(dict(line_id=lid,google_text=r['label']))
            note=notes.get(lid,'');ls=lqb.letters(r['label'])
            if note in ('dubious','probably wrong') or 'cut off' in note:
                unknown.append(dict(line_id=lid,note=note,heads=len(r['con']),reason='no exact printed head certified'));continue
            for c in r['con']:
                i=c['letter'];head=c['fam'];assert lqb.factors(ls[i])[lqb.HEADS.index(head)]==names[c['google']]
                target=names[c['ours']]
                if 'dialytika with tonos' in note:
                    assert len(r['con'])==1 and head=='accent';target=1
                # Certify the reviewed head only; the rest of the line remains unknown.
                marks={ 'breathing':{1:'\u0313',2:'\u0314'},'accent':{1:'\u0301',2:'\u0300',3:'\u0342'},'dialytika':{1:'\u0308'}}
                printed=ud.normalize('NFC',ls[i][0]+marks[head].get(target,''))
                b.add(meta,lid,dict(kind='letter_index',index=i,head=head),'marks',printed,target=target,
                    context=dict(owner_note=note,substitution_group=group,reviewed_head_only=True,google_head=c['google'],proposal_head=c['ours']))
                if 'dialytika with tonos' in note:
                    b.add(meta,lid,dict(kind='letter_index',index=i,head='dialytika'),'marks',ud.normalize('NFC',ls[i][0]+'\u0308'),target=1,context=dict(owner_note=note,reviewed_head_only=True))
    assert len(allids)==60
    return b.records,google,unknown,allids

def dev_records(inputs,tier):
    p=DEV/'evidence/dev_truth.jsonl.gz'
    meta=metadata('S8_DEV',p,inputs,tier,['r1 and r2; saved two-reader adjudication, r3 majority tiebreak; model identities unspecified'],
        'enriched',used=['S8b'],description='S8 training-wave DEV: disagreement census + 5% all-agree words, further wave reading cut; unweighted certified heads only')
    for rel in ['S8_DEV_ids.txt','S8_DEV_receipt.json','private/cards/items_key.json','evidence/word_census.jsonl','evidence/sources.json','cards/cut_receipt.json']:
        bind(DEV/rel,inputs)
    bind(DEV.parent/'S8a6_DEV_TRUTH.md',inputs);bind(DEV.parent/'S8a_REPORT.md',inputs)
    sources=read(DEV/'evidence/sources.json');ids=set((DEV/'S8_DEV_ids.txt').read_text().splitlines());assert len(ids)==600
    keys={r['id']:r for r in read(DEV/'private/cards/items_key.json')};groups=defaultdict(list)
    for r in lqb.rows(DEV/'evidence/word_census.jsonl'):groups[r['line_id']].append(r)
    positions={}
    for lid,rs in groups.items():
        offset=0;joined=''
        for r in sorted(rs,key=lambda r:r['start']):
            value=''.join(c[0] for c in lqb.letters(r['raw_forms']['google']))
            positions[r['uid']]=(offset,offset+len(value));offset+=len(value);joined+=value
        assert joined==''.join(c[0] for c in lqb.letters(sources[lid]['label'])),lid
    b=Builder();n=0
    for r in lqb.rows(p):
        if r.get('type')!='item' or r.get('control') or r.get('status')!='resolved' or not r.get('truth'):continue
        n+=1;lid=r['line_id'];assert lid in ids
        k=keys[r['id']];assert k['uid']==r['uid'];a,z=positions[r['uid']]
        reference=''.join(c[0] for c in lqb.letters(sources[lid]['label']))
        for i,ch in enumerate(lqb.letters(r['truth'])):
            for head,target in zip(lqb.HEADS,lqb.factors(ch)):
                b.add(meta,lid,dict(kind='scoped_mark',start=a,end=z,letter=i,head=head),'marks',ch,sources[lid]['doc'],target=target,
                    context=dict(reference=reference,printed_word=ud.normalize('NFC',r['truth']),card_id=r['id'],wave=r['wave'],card_selection=r['selection'],card_weight=r['weight'],weight_applied=False))
    assert n==976
    return b.records,[dict(line_id=lid,google_text=sources[lid]['label']) for lid in sorted(ids)],ids,n

def exclusions(candidates,dev_ids,inputs):
    p=v2.COLLECT/'release_exclusions/release_exclusions.json';registry=read(bind(p,inputs));registered=set();classes={}
    for name,e in registry['classes'].items():
        path=bind(p.parent/e['file'],inputs);assert lqb.sha256(path)==e['sha256']
        ids=set(path.read_text().splitlines());assert len(ids)==e['n'];registered|=ids;classes[name]=len(ids)
    # LQB4 explicitly assigns DEV to eval_only_dev. Record the discrepancy rather
    # than rewriting the sourcing registry, which remains read-only.
    dev_disk=set((p.parent/registry['classes']['eval_only_dev']['file']).read_text().splitlines())
    new=sorted(candidates-registered-dev_ids)
    return new,dict(registered_classes=classes,dev_class='eval_only_dev',dev_class_authority='LQB4 user instruction',dev_ids=600,dev_in_current_class=len(dev_ids&dev_disk),dev_registry_sync_pending=len(dev_ids-dev_disk))

def build_truth(inputs,dev_tier):
    old=list(lqb.rows(bind(_data_input(OUT/'truth_v1.jsonl'),inputs)))
    dev,dgoogle,dids,cards=dev_records(inputs,dev_tier);sub,sgoogle,unknown,sids=substitution_records(inputs)
    truth,conflicts=deduplicate(old+dev+sub)
    # Apply the frozen line-level training flags to the new snapshot only.
    flags=list(lqb.rows(bind(OUT/'truth_v1_flags.jsonl',inputs)));byline={r['line_id']:r['in_training'] for r in flags}
    for r in truth:
        if r['line_id'] in byline:r['in_training']=byline[r['line_id']]
        if 'sf6_release' in r['used_by']:
            r['used_by']=sorted(set(r['used_by'])|{'sf6_presence_full'})
    new,exinfo=exclusions(sids|dids,dids,inputs)
    p=OUT/'truth_v1_1.jsonl';write_rows(p,truth);write_rows(OUT/'truth_v1_1_conflicts.jsonl',conflicts)
    (OUT/'truth_v1_1_exclusion_ids_new.txt').write_text(''.join(x+'\n' for x in new))
    # Flags also have a new immutable name; v1 bytes are untouched.
    write_rows(OUT/'truth_v1_1_flags.jsonl',flags)
    membership=Counter(p['set'] for r in truth for p in {p['set']:p for p in r['provenance_all']}.values())
    manifest=dict(schema='lqb-truth-v1.1',parent_sha256=lqb.sha256(OUT/'truth_v1.jsonl'),sha256=lqb.sha256(p),items=len(truth),
        tiers=dict(Counter(r['tier'] for r in truth)),classes=dict(Counter(r['class'] for r in truth)),
        added=dict(S8_DEV=len(dev),substitution60=len(sub)),source_membership_counts=dict(membership),conflicts=len(conflicts),
        dev=dict(lines=600,resolved_cards=cards,sample_type='enriched',used_by=['S8b'],out_of_sample_for=['sf6_release'],tier=dev_tier,reader_model_identity='unspecified; requires explicit LQB4 owner tier ruling',population_rate=False),
        substitution60=dict(lines=60,known_heads=len(sub),unknown_lines=unknown,sample_type='decision_audit',scope='reviewed substitution heads only; no whole-line truth claim'),
        exclusion_new=len(new),exclusion_registration=exinfo,inputs=dict(inputs))
    lqb.dump(OUT/'truth_v1_1.manifest.json',manifest)
    (OUT/'truth_v1_1.sha256').write_text(lqb.sha256(p)+'  truth_v1_1.jsonl\n')
    return truth,manifest,dgoogle+sgoogle

def prepare_versions(xs,inputs,extra_google=()):
    registry=read(OUT/'versions.json');versions=registry['versions']
    old=copy.deepcopy(versions.get('sf6_presence_full',versions['sf6_release']))
    # Preserve the v1 FULL/PRESENCE view under its historical name.
    old.update(path=str(OUT/'sf6_release_labels.jsonl'),sha256=lqb.sha256(OUT/'sf6_release_labels.jsonl'),mode='FULL (identical to PRESENCE on this extract)')
    versions['sf6_presence_full']=old
    labels=[]
    for r in xs:
        m=r['modes']['ENSEMBLE_AB']
        if m['status']!='HOLD':labels.append(dict(line_id=r['line_id'],label=m['label']))
    p=OUT/'sf6_release_labels_v2.jsonl';write_rows(p,labels)
    sf=copy.deepcopy(old);sf.update(path=str(p),sha256=lqb.sha256(p),local_label_copy=str(p),mode='ENSEMBLE_AB',
        sx1_receipt=str(SX/'RECEIPT_v2.json'),sx1_receipt_sha256=lqb.sha256(SX/'RECEIPT_v2.json'),
        population=dict(rows=len(labels),definition='SX1 v2 ENSEMBLE_AB released labels on original truth IDs; new DEV/sub60 and HOLD IDs uncovered'),
        read='Audited ENSEMBLE_AB released label only; no HOLD/proposal fallback')
    versions['sf6_release']=sf
    supplemental=versions['google_raw']['supplemental_sources']
    supplemental=[x for x in supplemental if 'sf6_release_extract_lqb' not in x['path'] and 'google_truth_v1_1' not in x['path']]
    p=SX/'sf6_release_extract_lqb_v2.jsonl'
    supplemental.append(dict(path=str(p),sha256=lqb.sha256(p),id_field='line_id',text_field='google_text'))
    if extra_google:
        p=OUT/'google_truth_v1_1.jsonl';write_rows(p,extra_google)
        supplemental.append(dict(path=str(p),sha256=lqb.sha256(p),id_field='line_id',text_field='google_text'))
    versions['google_raw']['supplemental_sources']=supplemental
    lqb.dump(OUT/'versions.json',registry)
    return registry

def headline(truth,predictions,registry):
    breakdown={};parts=[]
    sources={p['set'] for r in truth if r['class']=='marks' for p in r['provenance_all']}
    # Uniform OOS marks precede the two named decision audits; remaining
    # enriched sets stay explicit, even when SX1 has no coverage.
    order=sorted(sources,key=lambda s:(0 if any(r['sample_type']=='uniform' and any(p['set']==s for p in r['provenance_all']) for r in truth) else 1 if s=='audit100' else 2 if s=='substitution60' else 3,s))
    for source in order:
        rs=[r for r in truth if r['class']=='marks' and any(p['set']==source for p in r['provenance_all'])]
        for typ in sorted({r['sample_type'] for r in rs}):
            selected=[r for r in rs if r['sample_type']==typ]
            pair=lqb.paired(selected,predictions['google_raw'],predictions['sf6_release'],'google_raw','sf6_release')['marks|A+B']
            pair['truth_items']=len(selected);pair['truth_lines']=len({r['line_id'] for r in selected})
            pair['sf6_covered_lines']=len({r['line_id'] for r in selected}&predictions['sf6_release'].keys())
            pair['sample_type']=typ
            breakdown[source+'/'+typ]=pair
            if pair['items']:
                parts.append(f"{source} ({typ}): {pair['a_errors']} → {pair['b_errors']} errors / {pair['items']} known mark-head opportunities; delta {pair['b_errors']-pair['a_errors']:+d}")
            elif source in ('S8_DEV','audit100','substitution60'):
                parts.append(f"{source} ({typ}): not measured (sf6 coverage {pair['sf6_covered_lines']}/{pair['truth_lines']} certified lines)")
    # Never imply an enriched DEV sample established a uniform population effect.
    line='; '.join(parts)
    bottom='No out-of-sample uniform mark-head set is measured. DEV is enriched and the v2 extract has no DEV or substitution60 labels. Audit100 is a decision audit; its covered-sample delta does not establish a population improvement.'
    return dict(line=line,bottom_line=bottom,by_source=breakdown)

def build_page(score,truth,summary_renderer=None):
    sys.path.insert(0,str(lqb.PROJECTS/'greek-ocr-toolkit-cleanup'))
    import greekocr
    greekocr.__path__.append(str(lqb.PROJECTS/'greek-ocr-toolkit-cleanup/greekocr'))
    spec=importlib.util.spec_from_file_location('_lqb4_board',ROOT/'scripts/lqb/build_scoreboard.py')
    board=importlib.util.module_from_spec(spec);spec.loader.exec_module(board)
    def summary(data):
        if summary_renderer is not None:return summary_renderer(data)
        return v2.summary_html(data).replace('LQB3_RECEIPT.json','LQB4_RECEIPT.json').replace('Witness cards below retain frozen adjudicated slots.',
            'Truth v1.1 retains frozen adjudicated slots. DEV is enriched (disagreement selection plus reading cut), used_by S8b, out-of-sample for sf6. Substitution60 certifies changed heads only; uncertain notes remain UNKNOWN. The SX1 extract covers neither new set; no proposal is substituted for a release.')
    board.summary_html=summary
    crop_sources={r['line_id']:dict(crop=r['source_crop'],crop_sha256=r['source_crop_sha256']) for r in read(SPELL/'S8_DEV/private/audit100/items_key.json') if not r['control']}
    board.main(score_path=OUT/'score_v2.json',truth_path=OUT/'truth_v1_1.jsonl',crop_sources=crop_sources)

def report(manifest,h):
    base=read(OUT/'baseline_v2.json')
    md=['# Label Quality Scoreboard v2.1','','## Marks delta — google_raw → sf6_release','',h['line'],'',h['bottom_line'],'',
        '## Truth v1.1','',f"{manifest['items']:,} items; SHA256 `{manifest['sha256']}`. Frozen v1 is unchanged. Added DEV {manifest['added']['S8_DEV']:,} heads from 976 resolved word groups in the 600-line draw; substitution60 {manifest['added']['substitution60']} certified heads. Controls, unread cards and UNKNOWN are excluded; no unreviewed heads are inferred absent.",'',
        'DEV is **enriched**, because word disagreements were exhaustively selected, only 5% of all-agree groups were drawn, and a further wave cut was adjudicated. This unweighted scoreboard makes no population-rate claim, even if the earlier capped line draw were described as uniform. It is out-of-sample for sf6 and marked `used_by=["S8b"]`. Reader model identities remain unspecified in the available peer record; its admission tier requires the explicit LQB4 owner ruling recorded in the receipt. No new readers ran.','',
        'Substitution60 is tier A owner truth and `decision_audit`: the saved sheet and lead notes explicitly say “no note = our line is right.” Only reviewed substitution heads enter truth. The dialytika-with-tonos correction certifies acute plus dialytika at the reviewed letter. “Dubious”, “probably wrong”, and clipped-off accents do not bind an exact printed head and remain UNKNOWN. Notes about a missed breathing do not locate that extra head, so it is not invented. These are reviewed sf6 substitution proposals; their historical HOLD proposals are never treated as released labels.','',
        'The new exclusion list contains only new candidate IDs outside every registered sourcing class. Per the LQB4 instruction, all 600 DEV IDs belong to `eval_only_dev` and are omitted. The current on-disk sourcing class still contains the older 273 IDs; the manifest records the exact overlap and pending registry synchronization. This work does not write that registry or send the list. The lead hands [the new IDs](truth_v1_1_exclusion_ids_new.txt) to the sourcing lead.','',
        '## SX1 v2 verification','',
        'The extract SHA, byte size, source-script SHA, earlier truth input, disjoint coverage partition, production receipt SHA, preserved v1 files and identical PRESENCE/FULL contents were verified locally. Actual audit100 membership is 99/99 ENSEMBLE_AB released; the receipt agrees. `sf6_release` now uses ENSEMBLE_AB. Historical FULL/PRESENCE is retained as `sf6_presence_full`; null HOLD labels stay uncovered. The v2 extract predates DEV/substitution60 truth, so both new sets have zero sf6 coverage. No network fetch was attempted.','',
        '## BASELINE — Google against truth','',
        'LQB3 strata, denominators and its C1 tier ruling remain unchanged. No pooled population rate. C1 verdicts do not supply complete head-resolved truth. The baseline remains first on the HTML page, followed by the marks headline, version scores and native witness cards.','',
        '| Class / scope | Stratum | Google errors/n, rate, 95% Wilson CI | sample_type | Tier | Source |','|---|---|---|---|---|---|']
    for r in base:md.append('| '+' | '.join(str(x).replace('|','/') for x in [r['class_name']+' / '+r['metric'],r['stratum'],v2.rate_text(r),r['sample_type'],r['tier'],r['source_set']])+' |')
    md+=['','## Scores and reproduction','',
        '[Every registered version](score_v2.json) is rescored on truth v1.1, with A/B/C, sample type, construction exposure, regression-only and uncovered counts separated. The [headline ledger](headline_v2.json) records source-specific paired document bootstrap intervals (4,000 replicates, seed 20261017). Scoped DEV groups use the saved census to locate Google letter spans, then mark-blind line alignment and the existing union scorer. No recogniser word indices are substituted for Google word indices. Changed audit100 cards compare Google directly to sf6; they do not require W1/RU1 coverage.','',
        '```sh',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/build_v2_1.py --dev-tier-a-owner-ruling',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest tests/test_lqb.py tests/test_lqb3.py tests/test_lqb4.py -q -p no:cacheprovider --basetemp=docs/records/labelfix/lqb/validation/lqb4/pytest_tmp',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/validate_scoreboard.py',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/finalize_v2_1.py',
        '```','',
        'Network OFF; no .git writes, peer writes, inference, readers, publication, browser or computer-use tools. The browser layout remains unverified by instruction. Offline structural validation and PNG decoding are recorded separately. [Receipt](LQB4_RECEIPT.json), [truth manifest](truth_v1_1.manifest.json), [tests](tests_lqb4.txt).']
    (OUT/'SCORE_v2.md').write_text('\n'.join(md)+'\n')

def main():
    inputs={};xs,sx=verify_sx1(inputs)
    if '--verify-only' in sys.argv:
        print(json.dumps(sx));return
    if '--register-only' in sys.argv:
        prepare_versions(xs,inputs);print('Registered verified sf6 v2 and historical sf6_presence_full');return
    if '--dev-tier-a-owner-ruling' not in sys.argv:
        raise SystemExit('DEV model identities are unspecified: explicit owner tier-A ruling required before truth v1.1 build')
    for p in [Path(__file__),ROOT/'scripts/lqb/build_truth.py',ROOT/'scripts/lqb/build_scoreboard.py',ROOT/'scripts/lqb/build_v2.py',ROOT/'greekocr/labelfix/lqb.py',SPELL/'LQB_MARKS_INPUTS.md']:bind(p,inputs)
    # Preserve the previous report/score/registry for historical receipt checks.
    archive=OUT/'validation/lqb3/frozen';archive.mkdir(parents=True,exist_ok=True)
    previous=read(OUT/'LQB3_RECEIPT.json')
    for name,h in previous['outputs'].items():
        target=archive/name
        if target.exists():assert lqb.sha256(target)==h;continue
        source=OUT/name
        if lqb.sha256(source)!=h:raise ValueError('LQB3 output changed before archive: '+name)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
    truth,manifest,google=build_truth(inputs,'A')
    registry=prepare_versions(xs,inputs,google);names=list(registry['versions'])
    items,_=lqb.load_truth(OUT/'truth_v1_1.jsonl');wanted={r['line_id'] for r in items};cache={}
    predictions={n:lqb.load_version(n,registry,wanted,cache) for n in names}
    score=lqb.run(OUT/'truth_v1_1.jsonl',registry,names)
    score['paired']['google_raw→sf6_release']=lqb.paired(items,predictions['google_raw'],predictions['sf6_release'],'google_raw','sf6_release')
    lqb.dump(OUT/'score_v2.json',score)
    h=headline(items,predictions,registry);lqb.dump(OUT/'headline_v2.json',h)
    build_page(score,truth);report(manifest,h)
    outputs=['versions.json','truth_v1_1.jsonl','truth_v1_1_flags.jsonl','truth_v1_1.manifest.json','truth_v1_1.sha256','truth_v1_1_conflicts.jsonl','truth_v1_1_exclusion_ids_new.txt','score_v2.json','baseline_v2.json','headline_v2.json','scoreboard.html','scoreboard_cards.json','scoreboard_build.json','SCORE_v2.md','sf6_release_labels_v2.jsonl','google_truth_v1_1.jsonl']
    receipt=dict(schema='lqb4-v2.1',network=False,git_writes=False,peer_writes=False,browser_launched=False,new_readers=0,inputs=inputs,sx1=sx,
        dev_tier_ruling='explicit owner acceptance of tier A; model identities unspecified',truth=dict(items=manifest['items'],sha256=manifest['sha256'],added=manifest['added'],exclusion_new=manifest['exclusion_new']),
        headline=h['line'],versions=len(names),outputs={name:lqb.sha256(OUT/name) for name in outputs})
    lqb.dump(OUT/'LQB4_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('inputs','outputs')},ensure_ascii=False))

if __name__=='__main__':main()
