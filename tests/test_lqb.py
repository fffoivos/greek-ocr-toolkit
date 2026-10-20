"""Offline LQB contracts: statistics, coverage, contamination and assembly."""
import json
from pathlib import Path
from tests._paths import require_file
import numpy as np
import pytest
from greekocr.labelfix import lqb
from scripts.lqb.build_truth import deduplicate


def item(lid='d--s0-l0',printed='ъ',tier='B',used=(),cls='ru1_yer',slot=None,**kw):
    return dict(sample_type='uniform',truth_id=lid,line_id=lid,slot=slot or dict(kind='offset',offset=0),**{'class':cls},printed=printed,provenance=dict(set='toy',file='toy',sha256='a'*64,commit='toy'),readers=['lead'],tier=tier,used_by=list(used),exclude_from_training=True,doc_id=lid.split('--')[0],**kw)


def test_paired_delta():
    truth=[item('a--s0'),item('b--s0'),item('c--s0'),item('d--s0')]
    a={r['line_id']:'ь' for r in truth};b=dict(a);b['a--s0']='ъ';b['b--s0']='ъ'
    result=lqb.paired(truth,a,b,'A','B')['ru1_yer|A+B']
    assert result['items']==4
    assert result['delta_per_100']==-50
    assert result['ci95'][0]<=-50<=result['ci95'][1]


def test_cluster_fixed_seed():
    pairs=[('doc1',1,1,0,1),('doc1',1,1,0,1),('doc2',0,1,1,1)]
    a=lqb.bootstrap_delta(pairs,7,1000);b=lqb.bootstrap_delta(pairs,7,1000)
    assert a==b and a['documents']==2
    assert a['ci95']==[-100.,100.]
    assert a['delta_per_100']==pytest.approx(-100/3)


def test_cluster_resamples_whole_documents():
    # A single document cannot be split into independent trials.
    pairs=[('same',1,1,0,1),('same',0,1,1,1)]
    assert lqb.bootstrap_delta(pairs,3,200)['ci95']==[0.,0.]


def test_in_sample_separation():
    truth=[item('a--s0',used=['B']),item('b--s0')]
    pred={'a--s0':'ъ','b--s0':'ь'}
    r=lqb.summarize(truth,pred,'B')['ru1_yer|A+B']
    assert r['headline']['errors']==1 and r['headline']['items']==1
    assert r['in_sample']['items']==1 and r['in_sample']['errors']==0
    assert lqb.paired(truth,pred,pred,'A','B')['ru1_yer|A+B']['items']==1


def test_tier_c_never_in_headline():
    r=lqb.summarize([item(tier='C')],{'d--s0-l0':'ь'},'A')
    assert r['ru1_yer|A+B']['status']=='not measured'
    assert r['ru1_yer|C']['headline']['errors']==1


def test_not_measured_and_missing():
    r=lqb.summarize([item()],{},'absent')['ru1_yer|A+B']
    assert r['status']=='not measured' and r['headline']['errors_per_100'] is None and r['uncovered']==1
    assert lqb.bootstrap_delta([])['ci95'] is None


def test_regression_only_separate():
    r=lqb.summarize([item(rate_eligible=False)],{'d--s0-l0':'ь'},'a')['ru1_yer|A+B']
    assert r['headline']['items']==0 and r['regression_only']['items']==1


def test_dedup_conflict_excludes_entire_key():
    a=item();b=dict(a,printed='ь');c=dict(a)
    truth,conflicts=deduplicate([a,b,c])
    assert not truth and len(conflicts)==1 and len(conflicts[0]['sources'])==3


def test_dedup_unions_contamination_and_provenance():
    a=item(tier='B',used=['v1']);b=item(tier='A',used=['v2']);b['exclude_from_training']=False
    truth,conflicts=deduplicate([a,b])
    assert not conflicts and truth[0]['tier']=='A'
    assert truth[0]['used_by']==['v1','v2'] and not truth[0]['exclude_from_training']
    assert len(truth[0]['provenance_all'])==2


@pytest.mark.parametrize('g,c',[('.', 'baseline dot'),('·','raised dot'),('·','raised dot'),(' - ','hyphen'),('–','en dash'),('—','em dash'),('','nothing')])
def test_gap_glyph_classes(g,c):assert lqb.gap_class(g)==c


def test_gap_at_edited_character():
    r=item(printed='raised dot',cls='n1_separator',slot=dict(kind='gap',id='x'),context=dict(reference='12-345',start=2,end=3))
    assert lqb.error(r,'12·345')==(0,1)
    assert lqb.error(r,'12.345')==(1,1)


def test_union_marks_known_and_inserted_unknown():
    # Inserted recognizer letters have no physical truth and must not inherit it.
    assert lqb.union_errors('ἄ','ἀ')[0]==[0,1,0,0]
    assert lqb.union_errors('ἄ','ἄι')[0]==[0,0,0,0]


def test_letters_edit_distance():
    r=item(printed='αβγ',cls='letters',slot=None)
    r['slot']=None
    assert lqb.error(r,'αβ')==(1,3)
    assert lqb.error(r,'άβγ')==(0,3)


def test_remote_version_unfetched():
    assert lqb.load_version('sf6',{'versions':{'sf6':{'status':'remote_unfetched','path':'/remote'}}})=={}


def test_overlay_and_admission_populations(tmp_path):
    paths=[]
    for name,records in [('parent',[{'id':'a','label':'α'},{'id':'b','label':'β'}]),('overlay',[{'id':'a','label':'ά'}]),('adm',[{'id':'b'}])]:
        p=tmp_path/name;p.write_text(''.join(json.dumps(r)+'\n' for r in records));paths.append(p)
    def v(p,**kw):return dict(path=str(p),sha256=lqb.sha256(p),text_field='label',**kw)
    reg={'versions':dict(parent=v(paths[0]),overlay=v(paths[1],parent='parent',overlay=True),adm=v(paths[2],parent='parent',inherit_label=True))}
    assert lqb.load_version('overlay',reg)=={'a':'ά','b':'β'}
    assert lqb.load_version('adm',reg)=={'b':'β'}
    paths[0].write_text('tampered')
    with pytest.raises(ValueError,match='sha256 mismatch'):lqb.load_version('parent',reg)


def test_frozen_truth_integrity():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    manifest=json.loads((lqb.DEFAULT/'truth_v1.manifest.json').read_text());truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    assert lqb.sha256(lqb.DEFAULT/'truth_v1.jsonl')==manifest['sha256']
    assert len(truth)==manifest['items']
    assert len({(r['line_id'],json.dumps(r['slot'],sort_keys=True),r['class']) for r in truth})==len(truth)
    assert all(not r['exclude_from_training'] for r in truth if r['provenance']['set']=='T2')
    audits=[r for r in truth if r['provenance']['set']=='RU1_audit']
    assert len(audits)==40 and all('ru1_v1' not in r['used_by'] for r in audits)


def test_owner_overlay_is_applied_symmetrically():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    affected=[r for r in truth if r.get('truth_overlay')]
    assert affected
    assert all(r['printed']=='ἦ' and r['context']['printed_word']=='ἦγε' for r in affected)
    assert all(r['target']==3 for r in affected if r['slot']['head']=='accent')


def test_capital_target_is_one_letter():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    capitals=[r for r in truth if r['class']=='capitals']
    assert len(capitals)==60
    assert all(len(lqb.letters(r['printed']))==1 for r in capitals)


def test_n1_future_version_contamination():
    r=item(used=['n1_*'])
    assert lqb.sample_used(r,'N1_v2') and lqb.sample_used(r,'n1_v2') and not lqb.sample_used(r,'w1_label')


def test_mark_heads_reported_separately():
    r=item(printed='ἄ',cls='marks',slot=dict(kind='word_letter',word=0,letter=0,head='accent'),target=1,context=dict(printed_word='ἄ'))
    scores=lqb.summarize([r],{r['line_id']:'ἀ'},'v')
    assert scores['marks/accent|A+B']['headline']['errors']==1
    assert scores['marks/breathing|A+B']['status']=='not measured'


def test_partial_dash_truth_and_space():
    r=item(printed='any dash',cls='n1_separator',slot=dict(kind='gap',id='x'),context=dict(reference='12-34',start=2,end=3))
    assert lqb.error(r,'12—34')==(0,1)
    assert lqb.error(r,'12·34')==(1,1)
    assert lqb.gap_class(' ')=='space'
    assert lqb.gap_class('')=='nothing'


def test_resolved_present_heads_not_dropped():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    from scripts.lqb.build_truth import decode_head
    assert decode_head('subscript','present')==1
    assert decode_head('dialytika','present')==1
    assert decode_head('accent','unknown') is None
    truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    assert any(r['provenance']['set']=='T4' and r['slot'].get('head')=='subscript' and r['target']==1 for r in truth if r['class']=='marks')


def test_gap_insertion_into_empty_slot_counts_as_error():
    r=item(printed='nothing',cls='n1_separator',slot=dict(kind='gap',id='x'),context=dict(reference='1234',start=2,end=2))
    assert lqb.error(r,'1234')==(0,1)
    assert lqb.error(r,'12·34')==(1,1)


@pytest.mark.parametrize('typ', ['enriched','decision_audit'])
def test_selected_samples_never_population_rates(typ):
    r=item();r['sample_type']=typ
    row=lqb.summarize([r],{r['line_id']:'ь'},'a')['ru1_yer|A+B']
    assert row['sample_type']==typ and row['headline']['errors_per_100'] is None
    p=lqb.paired([r],{r['line_id']:'ь'},{r['line_id']:'ъ'},'a','b')['ru1_yer|A+B']
    assert p['delta_per_100'] is None and p['ci95'] is None
    assert p['delta_per_opportunity']==-1 and p['delta_ci95']==[-1,-1]
    if typ=='decision_audit':assert 'decision precision: 0/1 correct (95% CI' in lqb.measurement_text(row)
    else:assert lqb.measurement_text(row)=='1 / 1 on this sample'


def test_mixed_samples_split_and_suppress_population():
    a=item('a');b=item('b');b['sample_type']='enriched'
    row=lqb.summarize([a,b],{'a':'ь','b':'ь'},'v')['ru1_yer|A+B']
    assert row['sample_type']=='mixed' and row['headline']['errors_per_100'] is None
    assert set(row['by_sample_type'])=={'uniform','enriched'}
    assert row['by_sample_type']['uniform']['headline']['errors_per_100']==100


def test_locked_selected_scope_not_population():
    r=item();r.update(sample_type='locked_stratum',population_eligible=False)
    row=lqb.summarize([r],{r['line_id']:'ъ'},'v')['ru1_yer|A+B']
    assert row['headline']['errors_per_100'] is None


def test_ia_letters_pixel_scope_and_pending_ib():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    ia=[r for r in truth if r['provenance']['set']=='R0_ia_letters']
    assert len(ia)==24 and len({r['line_id'] for r in ia})==23
    assert sum(len(lqb.letters(r['printed'])) for r in ia)==125
    assert all(r['tier']=='A' and r['sample_type']=='locked_stratum' and not r['population_eligible'] for r in ia)
    assert not any('ib' in r['provenance']['set'] for r in truth)
    r=ia[0];ref=r['context']['reference']
    assert lqb.error(r,ref)[1]>=1
    assert lqb.error(r,ref[:r['slot']['start']]+'X'+ref[r['slot']['end']:])[0]>=1


def test_all_frozen_sources_and_rows_have_sample_types():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    m=json.loads((lqb.DEFAULT/'truth_v1.manifest.json').read_text())
    allowed={'uniform','enriched','decision_audit','locked_stratum'}
    assert all(s['sample_type'] in allowed for s in m['sources'].values())
    assert all(r['sample_type'] in allowed for r in lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    assert m['sources']['yer_adjudication']['sample_type']=='uniform'
    assert m['sources']['RU1_audit']['sample_type']=='decision_audit'
    assert m['sources']['N1_controls']['sample_type']=='enriched'


def test_intro_has_every_measured_class_and_sf6_status():
    score=json.loads((lqb.DEFAULT/'score_v1.json').read_text())
    text=' '.join(lqb.intro_sentences(score))
    for cls in lqb.CLASSES:
        if score['paired']['google_raw→ru1_v1'][cls+'|A+B']['items']:
            assert 'Google vs ours on '+score['paired']['google_raw→ru1_v1'][cls+'|A+B']['sample_description'] in text
    assert 'sf6 release (accents): not scored yet; its labels on the truth lines are being fetched' in text
    assert 'Not measured:' in text


@pytest.mark.parametrize('typ',['uniform','locked_stratum'])
def test_population_types_allow_rates(typ):
    r=item();r['sample_type']=typ
    row=lqb.summarize([r],{r['line_id']:'ь'},'v')['ru1_yer|A+B']
    assert row['headline']['errors_per_100']==100
    assert lqb.measurement_text(row).startswith('POPULATION:')


def test_ru1_audit_precision_and_selected_n1():
    score=json.loads((lqb.DEFAULT/'score_v1.json').read_text())
    row=score['versions']['ru1_v1']['ru1_yer|A+B']['by_sample_type']['decision_audit']
    assert row['headline']['items']==40 and row['headline']['errors']==0
    assert lqb.measurement_text(row).startswith('decision precision: 40/40 correct (95% CI')
    for v in score['versions'].values():
        assert v['n1_separator|A+B']['headline']['errors_per_100'] is None


def test_base_span_ignores_outside_errors_and_maps_prefix_change():
    r=item(printed='βγ',cls='letters',context=dict(reference='αβγδ'))
    r['slot']=dict(kind='base_span',start=1,end=3)
    assert lqb.error(r,'Χβγδ')==(0,2)
    assert lqb.error(r,'αβΧδ')==(1,2)
    assert lqb.error(r,'ααβγδ')==(0,2)


def test_scoreboard_sample_displays_and_pending_truth():
    require_file('docs/records/labelfix/lqb/scoreboard.html')
    page=require_file(lqb.DEFAULT/'scoreboard.html').read_text()
    assert 'decision precision: 40/40 correct (95% CI' in page
    assert '33 / 103 on the sample' in page
    assert 'sample_type' in page
    assert '75 fewer errors per 100' not in page
    assert 'reference transcription, not pixel truth' in page
    assert 'Marks delta' in page and 'sf6_release' in page
    assert 'id="baseline"' in page


def test_lqb2_alt_and_flags_integrity():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    receipt=json.loads((lqb.DEFAULT/'LQB2_RECEIPT.json').read_text())
    original=(lqb.DEFAULT/'truth_v1_exclusion_ids.txt').read_text().splitlines()
    alt=(lqb.DEFAULT/'truth_v1_exclusion_ids_alt.txt').read_text().splitlines()
    flags=list(lqb.rows(lqb.DEFAULT/'truth_v1_flags.jsonl'))
    removed={r['line_id'] for r in flags};dropped={r['line_id'] for r in receipt['unmatched']}
    assert len(removed)==len(flags)==11 and all(r['in_training']=='wave-1d' for r in flags)
    assert removed==set(receipt['removed_wave_1d']) and len(dropped)==12
    assert alt==[x for x in original if x not in removed|dropped]
    assert len(alt)==len(set(alt))==receipt['alt_count']==1476
    assert lqb.sha256(lqb.DEFAULT/'truth_v1_exclusion_ids_alt.txt')==receipt['alt_sha256']
    assert lqb.sha256(lqb.DEFAULT/'truth_v1_flags.jsonl')==receipt['flags_sha256']
    assert lqb.sha256(lqb.DEFAULT/'truth_v1.jsonl')==receipt['truth_sha256']
    inventory={r['source_id']:r for r in json.loads((lqb.ROOT/'artifacts/ru1/keys/control_inventory.json').read_text())}
    for r in receipt['unmatched']:
        assert inventory[r['line_id']]['source_set']=='v2'
        assert inventory[r['line_id']]['w1_id'] is None
        assert r['registered_space_matches']==[] and r['action']=='dropped'
    truth=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    assert {r['line_id'] for r in truth} >= removed|dropped
    assert len([r for r in truth if r['line_id'] in removed])==11


def test_lqb2_real_training_split_and_label_parity():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    items,flagsha=lqb.load_truth(lqb.DEFAULT/'truth_v1.jsonl')
    frozen=list(lqb.rows(lqb.DEFAULT/'truth_v1.jsonl'))
    flagged=[r for r in items if r.get('in_training')=='wave-1d']
    assert len(flagged)==11 and flagsha
    predictions={r['line_id']:r['context']['reference'] for r in flagged}
    for name in json.loads((lqb.DEFAULT/'versions.json').read_text())['versions']:
        assert lqb.summarize(items,predictions,name)==lqb.summarize(frozen,predictions,name)
    scores=lqb.summarize(items,predictions,'trained_model',trained_on={'wave-1d'})
    row=scores['n1_separator|A+B']
    assert row['headline']['items']==0 and row['in_sample']['items']==11
    assert row['by_sample_type']['enriched']['in_sample']['items']==11
    assert lqb.paired(items,predictions,predictions,'label','trained_model',b_trained_on={'wave-1d'})['n1_separator|A+B']['items']==0


def test_lqb2_run_autoloads_flags_and_inherits_training(tmp_path):
    truth=tmp_path/'truth.jsonl';flags=tmp_path/'truth_flags.jsonl';labels=tmp_path/'labels.jsonl'
    truth.write_text(json.dumps(item())+'\n')
    flags.write_text(json.dumps(dict(line_id='d--s0-l0',in_training='wave-1d'))+'\n')
    labels.write_text(json.dumps(dict(id='d--s0-l0',label='ъ'))+'\n')
    v=dict(path=str(labels),sha256=lqb.sha256(labels),text_field='label')
    reg={'versions':dict(label=v,model=dict(v,trained_on=['wave-1d']),child=dict(v,parent='model'))}
    score=lqb.run(truth,reg,['label','model','child'])
    assert score['truth_flags_sha256']==lqb.sha256(flags)
    assert score['trained_on']==dict(label=[],model=['wave-1d'],child=['wave-1d'])
    assert score['versions']['label']['ru1_yer|A+B']['headline']['items']==1
    for name in ('model','child'):
        assert score['versions'][name]['ru1_yer|A+B']['in_sample']['items']==1
        assert score['versions'][name]['ru1_yer|A+B']['headline']['items']==0
    assert score['paired']['label→model']['ru1_yer|A+B']['items']==0
    assert lqb.sha256(truth)==score['truth_sha256']


@pytest.mark.parametrize('records',[
    [dict(line_id='absent',in_training='wave-1d')],
    [dict(line_id='d--s0-l0',in_training='')],
    [dict(line_id='d--s0-l0',in_training=['wave-1d'])],
    [dict(line_id='d--s0-l0',in_training='wave-1d',used_by=['v'])],
    [dict(line_id='d--s0-l0',in_training='wave-1d')]*2,
])
def test_lqb2_invalid_flags_fail_closed(tmp_path,records):
    truth=tmp_path/'truth.jsonl';flags=tmp_path/'flags.jsonl'
    truth.write_text(json.dumps(item())+'\n')
    flags.write_text(''.join(json.dumps(r)+'\n' for r in records))
    with pytest.raises(ValueError,match='truth flag'):lqb.load_truth(truth,flags)


def test_lqb2_explicit_missing_flags_fail_and_custom_truth_without_flags_works(tmp_path):
    truth=tmp_path/'truth.jsonl';truth.write_text(json.dumps(item())+'\n')
    assert lqb.load_truth(truth)==([item()],None)
    with pytest.raises(FileNotFoundError):lqb.load_truth(truth,tmp_path/'missing.jsonl')


def test_lqb2_conflicting_inline_flags_rejected(tmp_path):
    truth=tmp_path/'truth.jsonl';flags=tmp_path/'truth_flags.jsonl'
    truth.write_text(json.dumps(item(in_training='other'))+'\n')
    flags.write_text(json.dumps(dict(line_id='d--s0-l0',in_training='wave-1d'))+'\n')
    with pytest.raises(ValueError,match='conflicting truth flag'):lqb.load_truth(truth)


@pytest.mark.parametrize('declared',['wave-1d',[None]])
def test_lqb2_invalid_training_metadata_rejected(declared):
    with pytest.raises(ValueError,match='trained_on'):
        lqb.training_arms('v',{'versions':{'v':{'trained_on':declared}}})


def test_lqb2_training_lineage_cycle_rejected():
    with pytest.raises(ValueError,match='cyclic'):
        lqb.training_arms('v',{'versions':{'v':{'parent':'v'}}})
