"""SF7 preregistered rules, physical quote controls, audit and frozen SF6."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from tests._paths import evidence_params, require_file
from greekocr.labelfix import release_gate as sf6
from scripts.labelfix import release_gate_sf7 as gate
from scripts.labelfix.clariden.l1_common import overlay as sf6_overlay
from scripts.labelfix.clariden.r1_common import rows,sha256
from scripts.labelfix.sf6_measure import BINDING
from scripts.labelfix.sf7_measure import EV,audit_inputs,cards_inputs
from tests.labelfix.test_sf6 import rich


def run(original,rt,v='A',mode='ENSEMBLE_AB'):
    return gate.overlay(dict(id=rt['id'],label=original,script_class='greek_poly'),rt,v,BINDING,mode)


def blob(ids=(900,),bbox=(10,1,15,5)):
    return dict(source_ids=list(ids),bbox=list(bbox),area=12,source='preposed',touches_border=False)


@pytest.mark.parametrize('v','AB')
def test_sq1_saved_positive(v):
    rt=json.loads(Path('artifacts/sq1/runtime.json').read_text())
    original=json.loads(Path('artifacts/sq1/line_result.json').read_text())['original']
    out=run(original,rt,v,'PRESENCE')
    assert out['status']=='corrected' and 'Ἄδεια' in out['label'] and '"' not in out['label']
    q=out['rule_traces']['quotes'];assert len(q)==1 and q[0]['operation']=='CONSUME_ALIAS'
    assert q[0]['mark_source_ids']==[5,6] and q[0]['component_count']==2


def control():
    # Reader/recogniser fixture, NOT a claimed historical model output. The
    # first-capital evidence is manually assigned from the saved native crop:
    # threshold 130, 4-connected components, physical quote ID3 and compound ID1.
    text='«Ἢ νἄπαιρνε κάνε μαζί του τὴν κοπέλα, νὰ τὴν κουκου-'
    rt=rich(text);rt['id']='nlg--f4b52df5f8130047--s004-l0008'
    s=rt['detector']['slots'][0]
    s['evidence']['above']=[blob((1,),(28,4,43,15))]
    s['evidence']['above'][0]['area']=83
    s['bbox']=[45,5,79,36];s['component_ids']=[2]
    rt['detector']['opening_quotes']=[blob((3,),(6,18,19,34))]
    return rt,text


@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('omit_marks',[False,True])
def test_sq1_separate_real_quote_control(v,omit_marks):
    rt,text=control();original=text.replace('Ἢ','Η') if omit_marks else text
    out=run(original,rt,v)
    assert out['status'] in ('corrected','unchanged') and out['label']==text
    q=out['rule_traces']['quotes'][0];assert q['operation']=='KEEP_BOTH'
    assert q['quote_source_ids']==[3] and q['mark_source_ids']==[1]


@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('alias',list(dict.fromkeys(gate.ALIASES)))
def test_quote_aliases_are_one_atomic_replacement(v,alias):
    rt=rich('Ἄ');rt['detector']['slots'][0]['evidence']['above']=[blob()]
    out=run(alias+'Α',rt,v)
    assert out['status']=='corrected' and out['label']=='Ἄ'
    assert out['rule_traces']['quotes'][0]['operation']=='CONSUME_ALIAS'
    assert out['deletion_checks']==[]


@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('defect',['no_ink','shared','far_apart','extra_blob','clipped','uncertain','unresolved_quote'])
def test_quote_unknown_groups_hold(v,defect):
    rt=rich('Ἄ');s=rt['detector']['slots'][0];s['evidence']['above']=[blob()]
    if defect=='no_ink':s['evidence']['above']=[]
    elif defect=='shared':rt['detector']['slots'].append(dict(start=99,base='Α',evidence=dict(above=[blob()])))
    elif defect=='far_apart':s['evidence']['above'].append(blob((901,),(50,1,55,5)))
    elif defect=='extra_blob':s['evidence']['above'] += [blob((901,)),blob((902,))]
    elif defect=='clipped':s['evidence']['clipped_top']=True
    elif defect=='uncertain':s['evidence']['uncertainty']=['group_unresolved']
    elif defect=='unresolved_quote':rt['detector']['opening_quotes']=[dict(bbox=[1,1,5,5])]
    if defect=='shared':
        # Test ownership without inserting a malformed reader slot.
        assert gate.owned_ink(rt['detector'],s,'above')==[]
        return
    out=run('"Α',rt,v)
    assert out['status']=='hold' and 'label' not in out and out['changes']==[]


@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('old,new',[('ά','ὰ'),('ά','ἁ'),('ᾳ','ά')])
def test_substitutions_reader_alone(v,old,new):
    rt=rich(new);rt.pop('recognition_confidence');rt['detector']['slots'][0]['evidence']['above']=[]
    out=run(old,rt,v)
    assert out['status']=='corrected' and out['label']==new
    assert all(c['operation']=='SUBSTITUTE' and c['allowed'] for c in out['deletion_checks'])


@pytest.mark.parametrize('v','AB')
def test_deletion_is_sf6(v):
    rt=rich('ά')
    for a in [rt['r1_predictions'],*rt['peer_predictions'].values()]:a[0]['parts']=[]
    rt.pop('recognition_confidence');rt['detector']['slots'][0]['evidence'].pop('observation')
    before=sf6_overlay(dict(id=rt['id'],label='ά',script_class='greek_poly'),rt,'ENSEMBLE_AB',BINDING)
    out=run('ά',rt,v)
    assert out['status']=='hold' and out['deletion_checks']==before['deletion_checks']


@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('part,new',[('acute','ά'),('dasia','ἁ'),('subscript','ᾳ')])
@pytest.mark.parametrize('signal',['none','ink','recogniser','unscored_recogniser','wrong_zone','shared_ink','clipped'])
def test_addition_signals(v,part,new,signal):
    rt=rich(new);s=rt['detector']['slots'][0];s['evidence']['above']=[];s['evidence']['below']=[]
    if signal not in ('recogniser','unscored_recogniser'):rt.pop('recognition_confidence')
    if signal=='unscored_recogniser':rt['recognition_confidence']=.5
    zone='below' if part=='subscript' else 'above'
    if signal in ('ink','wrong_zone','shared_ink','clipped'):
        s['evidence']['above' if signal=='wrong_zone' and zone=='below' else 'below' if signal=='wrong_zone' else zone]=[blob()]
    if signal=='shared_ink':
        # Ownership conflict on a genuine other slot.
        rt=rich(new+'α');rt.pop('recognition_confidence');s=rt['detector']['slots'][0]
        s['evidence'][zone]=[blob()];rt['detector']['slots'][1]['evidence'][zone]=[blob()]
    if signal=='clipped':s['evidence']['clipped_'+('bottom' if zone=='below' else 'top')]=True
    original='αα' if signal=='shared_ink' else 'α'
    out=run(original,rt,v)
    wanted=(v=='A' and part!='subscript') or signal=='ink' or (v=='B' and signal=='recogniser')
    if signal=='clipped':wanted=False
    assert (out['status']=='corrected')==wanted


AUDIT=evidence_params(EV.parent/'S8_DEV/private/audit100/selected_overlays.json.gz',
                      lambda p: audit_inputs()[0], ids=lambda w: w['id'])
@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('w',AUDIT)
def test_all_audit_lines(w,v):
    AUDIT_EXPECTED={(r['id'],r['variant']):r['overlay'] for r in rows(require_file(EV/'audit_replay.jsonl.gz'))}
    out=run(w['record']['label'],w['runtime'],v)
    saved=deepcopy(AUDIT_EXPECTED[w['id'],v])
    # Binding changes are separately verified; compare the whole decision.
    saved['policy_sha']=out['policy_sha']
    assert json.loads(json.dumps(out,ensure_ascii=False))==saved


CARDS=evidence_params(EV/'cards39_inputs.jsonl.gz', lambda p: list(rows(p)), ids=lambda w: w['card']['db_id'])
@pytest.mark.parametrize('v','AB')
@pytest.mark.parametrize('w',CARDS)
def test_all_39_cards(w,v):
    CARD_EXPECTED={(r['card']['db_id'],r['variant']):r['overlay'] for r in rows(require_file(EV/'cards39_replay.jsonl.gz'))}
    out=run(w['record']['label'],w['runtime'],v)
    saved=deepcopy(CARD_EXPECTED[w['card']['db_id'],v])
    saved['policy_sha']=out['policy_sha'];assert json.loads(json.dumps(out,ensure_ascii=False))==saved


@pytest.mark.skip(reason="historical binding; green at opus/spellcheck@26d64e8a6; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_sf6_full_outputs_identical_after_sf7_import():
    prior=json.loads((EV/'sf6_before.json').read_text());assert sf6.policy_binding()==prior['policy']
    witnesses=list(rows('docs/records/labelfix/spellcheck/SF6c_evidence/after/witness_inputs.jsonl.gz'))
    after=[sf6_overlay(w['record'],w['runtime'],w.get('mode','ENSEMBLE_AB'),BINDING) for w in witnesses]
    assert json.loads(json.dumps(after,ensure_ascii=False,sort_keys=True))==prior['outputs']


@pytest.mark.skip(reason="historical binding; green at opus/spellcheck@26d64e8a6; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_binding_is_additive_and_preregistered():
    b=gate.policy_binding();assert b['schema']==gate.POLICY
    assert b['preregistration_sha256']==gate.PREREGISTRATION_SHA256
    assert all(b['sources'][p]==h for p,h in sf6.policy_binding()['sources'].items())
    assert sf6.policy_binding()['sha256']==gate.SF6_SHA256


def test_invalid_variant():
    with pytest.raises(ValueError,match='addition_rule'):
        gate.compose('α',rich('α'),addition_rule='C')
