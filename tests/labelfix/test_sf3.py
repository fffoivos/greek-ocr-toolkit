"""SF3 relevance and punctuation custody witnesses; saved/synthetic evidence only."""
from copy import deepcopy
import pytest
from greekocr.labelfix.release_gate import compose_runtime, edit_guard
from tests.labelfix.test_l1e import runtime


def clean(base='ε', meanline=30, xh=20):
    r=runtime();r['recogniser_text']=base
    s=r['detector']['slots'][0]
    s.update(base=base,parts=[],word_final=False)
    s['evidence'].update(meanline=meanline,xh=xh)
    for records in [r['r1_predictions'],*r['peer_predictions'].values()]:
        records[0].update(base=base,parts=[])
    for records in [r['coverage'],*r['peer_coverage'].values()]:records[0]['base']=base
    return r


@pytest.mark.parametrize('mode',['PRESENCE','FULL','ENSEMBLE_AB','ENSEMBLE_AE'])
def test_per_x_scalar_top_clearance_is_insufficient(mode):
    r=clean();s=r['detector']['slots'][0];s['evidence']['clipped_top']=True
    out=compose_runtime(r,mode)
    assert 'detector_clipped_top' in out['hold_slots'][0]['reasons']
    assert out['slots'][0]['evidence']['clipped_top']  # recorded, never erased
    s['evidence']['meanline']=18
    assert 'detector_clipped_top' in compose_runtime(r,mode)['hold_slots'][0]['reasons']


@pytest.mark.parametrize('base',['β','τ','δ','ς'])
def test_consonant_top_edge_is_not_a_greek_mark_zone(base):
    r=clean(base,0);r['detector']['slots'][0]['evidence']['clipped_top']=True
    assert not compose_runtime(r,'ENSEMBLE_AB')['hold_slots']


def test_capital_and_lowercase_scalar_clearance_cannot_drop_top_cut():
    r=clean('Α',8,20);s=r['detector']['slots'][0];s['evidence']['clipped_top']=True
    assert 'detector_clipped_top' in compose_runtime(r,'ENSEMBLE_AB')['hold_slots'][0]['reasons']
    s['evidence']['meanline']=7
    assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']
    # Same local xh, different saved per-x meanline: the second is uncut.
    r=clean('ρ',18,20);s=r['detector']['slots'][0];s['evidence']['clipped_top']=True
    assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']
    s['evidence']['meanline']=30
    assert 'detector_clipped_top' in compose_runtime(r,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('value',[None,float('nan'),float('inf'),'invalid'])
def test_missing_invalid_geometry_never_proves_observation(value):
    r=clean();s=r['detector']['slots'][0];s['evidence'].update(clipped_top=True,meanline=value)
    assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']


def test_explicit_unseen_is_not_overridden_by_clear_crop_edge():
    r=clean();s=r['detector']['slots'][0]
    s['evidence'].update(clipped_top=True,observation={'above':'UNSEEN'})
    assert 'crop_UNSEEN:above' in compose_runtime(r,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('base',list('αηωΑΗΩ'))
def test_bottom_cut_still_holds_every_subscript_bearer(base):
    r=clean(base);r['detector']['slots'][0]['evidence']['clipped_bottom']=True
    assert 'detector_clipped_bottom' in compose_runtime(r,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('signal',['detector','A','B','E','original','adscript'])
def test_below_prediction_from_any_signal_is_relevant(signal):
    r=clean('ι');s=r['detector']['slots'][0];s['evidence']['clipped_bottom']=True
    assert not compose_runtime(r,'PRESENCE')['hold_slots']
    if signal=='detector':s['parts']=['subscript']
    elif signal=='original':r['recogniser_text']='ι\u0345'
    elif signal=='adscript':s['iota_adscript']=True
    else:(r['r1_predictions'] if signal=='A' else r['peer_predictions'][signal])[0]['parts']=['subscript']
    assert 'detector_clipped_bottom' in compose_runtime(r,'PRESENCE')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('level',['line','slot','external','saved_reasons'])
@pytest.mark.parametrize('reason',['clipped_bottom','clipped_top'])
def test_K1_observation_retains_top_and_only_relaxes_irrelevant_bottom(level,reason):
    r=clean();s=r['detector']['slots'][0];s['evidence'][reason]=True
    flag=dict(start=0,rule='observation',reason=reason)
    extra=[]
    if level=='line':r['detector']['constraint_flags']=[flag]
    elif level in ('slot','saved_reasons'):
        s.update(hold=True,constraint_flags=[flag])
        if level=='saved_reasons':s['hold_reasons']=['K1:flag','K1:observation:'+reason,'detector_'+reason]
    else:extra=[flag]
    if reason=='clipped_bottom':assert not compose_runtime(r,'ENSEMBLE_AB',extra)['hold_slots']
    else:assert 'detector_clipped_top' in compose_runtime(r,'ENSEMBLE_AB',extra)['hold_slots'][0]['reasons']
    if reason=='clipped_bottom':s['base']='η';r['recogniser_text']='η'
    else:s['evidence']['meanline']=0
    # For eta, reader base mismatch also holds, but the clipping flag must survive.
    reasons=compose_runtime(r,'ENSEMBLE_AB',extra)['hold_slots'][0]['reasons']
    assert 'detector_'+reason in reasons


def test_adscript_context_keeps_below_zone_conservative():
    r=clean('Α');s=deepcopy(r['detector']['slots'][0]);s.update(start=1,end=2,base='ι')
    s['evidence']['clipped_bottom']=True
    r['recogniser_text']='Αι';r['detector']['slots'].append(s)
    for records in [r['r1_predictions'],*r['peer_predictions'].values()]:records.append(dict(start=1,base='ι',parts=[]))
    for records in [r['coverage'],*r['peer_coverage'].values()]:records.append(dict(start=1,base='ι',scored=True,evidence_state='unadjudicated',uncertainty=[]))
    assert 'detector_clipped_bottom' in compose_runtime(r,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('reason',['unnamed','localisation_unknown','new_unknown_observation'])
def test_other_K1_observation_flags_remain_decisive(reason):
    r=clean();r['detector']['constraint_flags']=[dict(start=0,reason=reason)]
    assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']


@pytest.mark.parametrize('original,proposal',[
    ('δ\u0314\u0301','δ'),('α\u0342\u0300','α\u0342'),('δ\u0300','δ'),
    ('ι\u0313\u0314\u0342','ι\u0313\u0342'),('ξ\u0300','ξ'),('η\u0301\u0342','η\u0342'),
    ('ι\u0314\u0301\u0342','ι\u0314\u0301'),('υ\u0313\u0314\u0342','υ\u0313\u0342'),
    ('ρ\u0314\u0345','ρ\u0314'),('υ\u0342\u0345','υ\u0342'),('ᾱ','α'),('é','e'),
    (' \u0301Α',' Α')])
def test_every_audited_unsupported_cluster_still_holds(original,proposal):
    assert edit_guard(original,proposal)


@pytest.mark.parametrize('alias',list("'᾽᾿’ʼ"))
def test_elision_codepoint_variants_share_only_word_final_policy(alias):
    assert not edit_guard('δ'+alias,'δ’')
    assert not edit_guard('δ'+alias,'δ')
    assert edit_guard(alias+'ς','ς')  # prefix custody is not a deletion licence


@pytest.mark.parametrize('original,proposal',[
    ('α «β»','ά “β”'),('α "β"','ά “β”'),("'ς",'᾿ς'),('α\u00a0β','ά β'),('α\u202fβ','ά β')])
def test_representation_only_quotes_and_space_codepoints(original,proposal):
    assert not edit_guard(original,proposal)


@pytest.mark.parametrize('original,proposal',[('α,','ά.'),('α β','άβ'),('α  β','ά β'),('α.\'','ά.'),('α…','ά.')])
def test_punctuation_content_and_space_count_are_preserved(original,proposal):
    assert edit_guard(original,proposal)


@pytest.mark.parametrize('text',["'ς", "α.'", "'φελᾷ"])
def test_composer_retains_prefix_elisions_and_closing_quotes(text):
    from greekocr.labelfix.reading import LineReading
    from greekocr.labelfix.release_gate import compose
    from greekocr.labelfix.text import clusters,nfd
    slots=[dict(start=c.start,end=c.end,base=c.base,parts=[],evidence={})
           for c in clusters(nfd(text)) if c.base.isalpha()]
    cov=[dict(start=s['start'],scored=True,evidence_state='unadjudicated',uncertainty=[]) for s in slots]
    pred={s['start']:dict(parts=[]) for s in slots}
    out=compose(text,LineReading(text,slots,[]),pred,cov,'FULL')
    assert not out['hold_slots']
    assert out['text'].startswith("'") if text.startswith("'") else out['text'].endswith(".'")


def test_DEV_allowlist_filters_cache_before_decoding_locked_payload(tmp_path):
    import json
    from scripts.labelfix.sf3_measure import dev_runtime,dev_inventory
    cache=tmp_path/'cache.jsonl'
    cache.write_text('{"id":"locked", deliberately invalid payload}\n'+json.dumps(dict(id='dev',status='ok'))+'\n')
    assert dev_runtime(cache,{'dev'})==[dict(id='dev',status='ok')]
    manifest=tmp_path/'manifest.jsonl'
    manifest.write_text(json.dumps(dict(selection_role='locked',card_id='locked'))+'\n')
    with pytest.raises(ValueError,match='non-DEV'):dev_inventory(manifest)
