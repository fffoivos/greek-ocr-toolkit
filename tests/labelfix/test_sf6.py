"""SF6 deletion gate witnesses, boundary counterexamples and saved regressions."""
from copy import deepcopy
import json
import os
from pathlib import Path

import pytest
from tests._paths import evidence_params, require_file

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden import l1_common
from scripts.labelfix.clariden.r1_common import rows,write_rows
from scripts.labelfix.sf6_measure import baseline,EV,BINDING,KERAIA,CLASSES,add_census
from tests.labelfix.test_sf5 import synthetic,SF6_HELD


@pytest.fixture(scope='module')
def policy():
    if os.environ.get('SF6B_TEST_BASELINE'):
        from scripts.labelfix.sf5_measure import baseline as load
        return load(Path('artifacts/labelfix_sf6b/before'))
    return baseline() if os.environ.get('SF6_TEST_BASELINE') else (gate,l1_common)


def rich(text):
    """Explicitly scored, fully observed fixture; never production evidence."""
    rt=synthetic(text)
    rt['recognition_confidence']=.9
    rt['image_width']=1000
    for i,s in enumerate(rt['detector']['slots']):
        s.update(locator_span=[10+i*10,18+i*10],word_final=True)
        s['evidence'].update(window=[8+i*10,20+i*10],above=[],below=[],apostrophes=[],
            clipped_left=False,clipped_right=False,
            observation={z:'OBSERVED' for z in ('above','below','left','right')})
    for cov in [rt['coverage'],*rt['peer_coverage'].values()]:
        for c in cov:c['span']=[10+c['start']*10,18+c['start']*10]
    from greekocr.labelfix.ctc_align import Alignment
    rt['recognition_evidence']=Alignment(text,n_frames=250,confidence=.9,
        frame_confidences=[.9]*250).recognition_evidence(rt['detector']['slots'],1000)
    return rt


def overlay(policy,original,rt,mode='ENSEMBLE_AB'):
    return policy[1].overlay(dict(id=rt['id'],label=original,script_class='greek_poly'),rt,mode,BINDING)


def move_runtime(text):
    rt=rich(text)
    spans={s['start']:s['locator_span'] for s in rt['detector']['slots']}
    for records in [rt['coverage'],*rt['peer_coverage'].values()]:
        for c in records:c['span']=list(spans[c['start']])
    return rt


def saved_inputs(path):
    values=list(rows(path))
    if (EV/'census_inputs.jsonl.gz').exists():values+=list(rows(EV/'census_inputs.jsonl.gz'))
    return values

INPUTS=evidence_params(EV/'witness_inputs.jsonl.gz', saved_inputs,
                       ids=lambda r: r['cohort']+':'+r['id'])
CAPITAL_MOVES={
    '32aae9fec147d3b483deb96e-p000060-l0057': 'ΕΡΝΕΣΤΟΣ. -Ἀλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ',
    'a963b33d02c23d4127f5ec26-p000012-l0029': '-Ἀνεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα-',
}


@pytest.mark.parametrize('w',INPUTS)
def test_saved_release_regression(policy,w):
    EXPECTED={(r['cohort'],r['id']):r for r in rows(require_file(EV/'witness_results.jsonl.gz'))}
    mode=w.get('mode','ENSEMBLE_AB');o=overlay(policy,w['record']['label'],w['runtime'],mode)
    expected=EXPECTED[w['cohort'],w['id']]
    wanted=('corrected',CAPITAL_MOVES[w['id']]) if w['id'] in CAPITAL_MOVES else (expected['after']['status'],expected['after']['label'])
    assert (o['status'],o.get('label',w['record']['label']))==wanted
    if w['id'] in CAPITAL_MOVES:
        assert len(o['deletion_checks'])==1
        assert o['deletion_checks'][0]['operation']=='MOVE'
        assert o['deletion_checks'][0]['breathing']=='psili'
        assert o['deletion_checks'][0]['allowed'] and o['deletion_checks'][0]['reason'] is None
        assert o['deletion_checks'][0]['signals']==dict(reader=False,detector=False,recogniser=False)
    if w['cohort']=='quote_probe' or (w['cohort']=='sf5' and w['id'] in SF6_HELD):
        assert o['status']=='hold' and o['changes']==[]
    oldgate,oldcommon=baseline()
    old=oldcommon.overlay(w['record'],w['runtime'],mode,BINDING)
    assert (old['status'],old.get('label',w['record']['label']))==(expected['before']['status'],expected['before']['label'])
    assert policy[0].compose_runtime(w['runtime'],mode)['slots']==oldgate.compose_runtime(w['runtime'],mode)['slots']
    if o['status']!='hold':
        assert (o['status'],o['label'])==(old['status'],old['label'])
    elif old['status']!='hold':
        assert o['changes']==[] and any(not c['allowed'] for c in o['deletion_checks'])


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('spacing','᾿᾽')
@pytest.mark.parametrize('base','ΑΕΗΙΟΥΩ')
def test_same_kind_capital_breathing_move_needs_no_absence(policy,mode,spacing,base):
    from greekocr.labelfix.text import nfc
    original='-'+spacing+base+'λλα';proposal=nfc('-'+base+'\u0313λλα')
    rt=move_runtime(proposal);rt.pop('recognition_confidence')
    o=overlay(policy,original,rt,mode)
    assert (o['status'],o['label'])==('corrected',proposal)
    assert len(o['deletion_checks'])==1
    c=o['deletion_checks'][0]
    assert c['operation']=='MOVE' and c['breathing']=='psili' and c['allowed'] and c['reason'] is None
    assert c['signals']==dict(reader=False,detector=False,recogniser=False)
    assert gate.google_deletions(original,proposal)[0]['character']==spacing


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('spacing,proposal,part',[('᾿','-Ἀλλα','psili'),('᾽','-Ἀλλα','psili'),('῾','-Ἁλλα','dasia')])
def test_breathing_move_kind_pair_in_deletion_check(policy,mode,spacing,proposal,part):
    rt=move_runtime(proposal);decision=policy[0].compose_runtime(rt,mode)
    checks=policy[0].deletion_guard('-'+spacing+'Αλλα',proposal,rt,decision)
    assert len(checks)==1 and checks[0]['allowed']
    assert checks[0]['operation']=='MOVE' and checks[0]['breathing']==part


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('defect',[
    'mismatched_kind','unnamed_a','unnamed_b','missing_b','unscored_a','unscored_b',
    'unknown','uncertain','out_of_window_a','out_of_window_b','clipped','unseen',
    'lowercase','already_attached','other_boundary','duplicate_spacing','outside_window','missing_window',
    'detector_unknown','evidence_uncertain','clipped_left','missing_top_observation','peer_unknown',
])
def test_non_move_keeps_exact_sf6_hold(policy,mode,defect):
    original='-᾿Αλλα';proposal='-Ἀλλα';rt=move_runtime(proposal)
    if defect=='mismatched_kind':
        proposal='-Ἁλλα';rt=move_runtime(proposal)
        # No second positive psili-absence signal: a different breathing
        # cannot itself bypass SF6. Valid two-absence deletions stay unchanged.
        rt.pop('recognition_confidence')
        rt['detector']['slots'][0]['evidence'].pop('observation')
    elif defect=='unnamed_a':rt['r1_predictions'][0]['parts']=[]
    elif defect=='unnamed_b':rt['peer_predictions']['B'][0]['parts']=[]
    elif defect=='missing_b':rt['peer_predictions'].pop('B');rt['peer_coverage'].pop('B')
    elif defect=='unscored_a':rt['coverage'][0]['scored']=False
    elif defect=='unscored_b':rt['peer_coverage']['B'][0]['scored']=False
    elif defect=='unknown':rt['coverage'][0]['evidence_state']='UNKNOWN'
    elif defect=='uncertain':rt['peer_coverage']['B'][0]['uncertainty']=['crop_clipped']
    elif defect=='out_of_window_a':rt['coverage'][0]['span']=[-1,10]
    elif defect=='out_of_window_b':rt['peer_coverage']['B'][0]['span']=[10,10]
    elif defect=='clipped':rt['detector']['slots'][0]['evidence']['clipped_top']=True
    elif defect=='unseen':rt['detector']['slots'][0]['evidence']['observation']['above']='UNSEEN'
    elif defect=='lowercase':original='-᾿αλλα';proposal='-ἀλλα';rt=move_runtime(proposal)
    elif defect=='already_attached':original='-᾿Ἀλλα'
    elif defect=='other_boundary':
        original='-᾿ΑΑ';proposal='-ΑἈ';rt=move_runtime(proposal)
        rt.pop('recognition_confidence');rt['detector']['slots'][0]['evidence'].pop('observation')
    elif defect=='duplicate_spacing':original='-᾿᾿Αλλα'
    elif defect=='outside_window':rt['coverage'][0]['span']=[1000,1010]
    elif defect=='missing_window':rt['detector']['slots'][0]['evidence'].pop('window')
    elif defect=='detector_unknown':rt['detector']['slots'][0]['evidence']['evidence_state']='UNKNOWN'
    elif defect=='evidence_uncertain':rt['detector']['slots'][0]['evidence']['uncertainty']=['unresolved']
    elif defect=='clipped_left':rt['detector']['slots'][0]['evidence']['clipped_left']=True
    elif defect=='missing_top_observation':rt['detector']['slots'][0]['evidence'].pop('clipped_top')
    elif defect=='peer_unknown':rt['peer_coverage']['B'][0]['evidence_state']='UNKNOWN'
    o=overlay(policy,original,rt,mode)
    assert o['status']=='hold' and o.get('label',original)==original and o['changes']==[]
    if defect in ('unnamed_a','other_boundary'):
        assert o['deletion_checks']==[]  # composer retains the spacing sign
    else:
        assert any(not c['allowed'] for c in o['deletion_checks'])
    # A direct proposal still cannot turn an unnamed/uncertain reader into
    # positive presence just because the output spells a breathing.
    checks=policy[0].deletion_guard(original,proposal,rt,policy[0].compose_runtime(rt,mode))
    assert any(not c['allowed'] for c in checks)
    assert all(c['reason']=='sf6:deletion_needs_two_positive_absences:'+c['category'] for c in checks if not c['allowed'])


def test_keraia_is_held_even_with_two_r1_arms(policy):
    w=next(w for w in saved_inputs(require_file(EV/'witness_inputs.jsonl.gz')) if w['id']==KERAIA)
    o=overlay(policy,w['record']['label'],w['runtime'])
    assert o['status']=='hold' and o['changes']==[]
    c=next(c for c in o['deletion_checks'] if c['category']=='keraia')
    assert not c['signals']['reader'] and not c['signals']['detector']


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('pair',['reader_detector','reader_recogniser'])
def test_two_positive_mark_absences_release(policy,mode,pair):
    rt=rich('α' if pair=='reader_recogniser' else 'ά')
    for records in [rt['r1_predictions'],*rt['peer_predictions'].values()]:records[0]['parts']=[]
    rt['detector']['slots'][0]['parts']=[] if pair=='reader_detector' else ['acute']
    if pair=='reader_detector':rt.pop('recognition_confidence')
    # PRESENCE/FULL retain their previous detector-agreement veto.
    if mode in ('PRESENCE','FULL') and pair=='reader_recogniser':
        rt['detector']['slots'][0]['parts']=[]
    o=overlay(policy,'ά',rt,mode)
    assert o['status']=='corrected' and o['label']=='α'


@pytest.mark.parametrize('mode',gate.MODES)
def test_ab_is_one_signal_when_other_sources_keep_mark(policy,mode):
    rt=rich('ά');rt['detector']['slots'][0]['parts']=[]
    rt['detector']['slots'][0]['evidence'].pop('observation')
    for records in [rt['r1_predictions'],*rt['peer_predictions'].values()]:records[0]['parts']=[]
    o=overlay(policy,'ά',rt,mode)
    assert o['status']=='hold'


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('defect',['missing','unscored','disagrees'])
def test_reader_absence_needs_a_and_b_even_in_presence_full(policy,mode,defect):
    rt=rich('α')
    if defect=='missing':rt['peer_predictions'].pop('B');rt['peer_coverage'].pop('B')
    elif defect=='unscored':rt['peer_coverage']['B'][0]['scored']=False
    else:rt['peer_predictions']['B'][0]['parts']=['acute']
    assert overlay(policy,'ά',rt,mode)['status']=='hold'


@pytest.mark.parametrize('defect',[
    'missing_prediction','missing_coverage','unscored','unknown','uncertain','out_of_window',
    'clipped_top','unseen','unnamed','unscored_recogniser','unknown_detector','peer_unscored',
])
def test_unobserved_sources_cannot_be_absence(policy,defect):
    rt=rich('α')
    # Reader + recogniser would otherwise release; detector stays unknown.
    s=rt['detector']['slots'][0];s['evidence'].pop('observation')
    if defect=='missing_prediction':rt['r1_predictions']=[]
    elif defect=='missing_coverage':rt['coverage']=[]
    elif defect=='unscored':rt['coverage'][0]['scored']=False
    elif defect=='unknown':rt['coverage'][0]['evidence_state']='UNKNOWN'
    elif defect=='uncertain':rt['coverage'][0]['uncertainty']=['crop_clipped']
    elif defect=='out_of_window':rt['coverage'][0]['span']=[-1,10]
    elif defect=='clipped_top':s['evidence']['clipped_top']=True
    elif defect=='unseen':s['evidence']['observation']={'above':'UNSEEN'}
    elif defect=='unnamed':s['unnamed']=[0]
    elif defect=='unscored_recogniser':rt.pop('recognition_confidence')
    elif defect=='unknown_detector':
        # Keep recognised mark; A/B absence is still just one signal.
        rt=rich('ά');rt.pop('recognition_confidence');s=rt['detector']['slots'][0]
        s['parts']=[];s['evidence'].pop('observation')
        for records in [rt['r1_predictions'],*rt['peer_predictions'].values()]:records[0]['parts']=[]
    elif defect=='peer_unscored':rt['peer_coverage']['B'][0]['scored']=False
    assert overlay(policy,'ά',rt)['status']=='hold'


@pytest.mark.parametrize('mark',['\u0301','\u0300','\u0313','\u0314','\u0345','\u0308','\u0342'])
def test_replacements_delete_the_old_mark(policy,mark):
    # Direct boundary test avoids unrelated supported-mark multiplicity vetoes.
    rt=rich('α'+mark);d=policy[0].compose_runtime(rt,'ENSEMBLE_AB')
    events=policy[0].deletion_guard('α'+mark,'α',rt,d)
    assert len(events)==1 and events[0]['character']==mark
    assert not events[0]['allowed']  # every source still says present


@pytest.mark.parametrize('old,new',[('ά','ὰ'),('ά','ἁ'),('ᾳ','ά')])
def test_combining_replacement_needs_two_absences(policy,old,new):
    rt=rich(old)
    from greekocr.labelfix.text import clusters,nfd
    from greekocr.labelfix.reading import MARKS
    parts=[p for p,m in MARKS.items() if m in clusters(nfd(new))[0].marks]
    for records in [rt['r1_predictions'],*rt['peer_predictions'].values()]:records[0]['parts']=parts
    rt['detector']['slots'][0]['parts']=parts
    rt['detector']['slots'][0]['evidence'].pop('observation')
    assert overlay(policy,old,rt)['status']=='hold'


@pytest.mark.parametrize('mode',gate.MODES)
def test_punctuation_two_positive_signals_release(policy,mode):
    o=overlay(policy,"δ' α",rich('δ α'),mode)
    assert o['status']=='corrected' and o['label']=='δ α'
    if policy[0].POLICY=='sf6-release-v1':
        c=o['deletion_checks'][0]
        assert c['signals']==dict(reader=False,detector=True,recogniser=True) and c['allowed']


@pytest.mark.parametrize('defect',['unscored_text','unseen_right','unscored_head','unlocated','clipped','missing_flag'])
def test_punctuation_one_or_no_positive_signal_holds(policy,defect):
    rt=rich('δ α');original="δ' α";s=rt['detector']['slots'][0]
    if defect=='unscored_text':rt.pop('recognition_confidence')
    elif defect=='unseen_right':s['evidence']['observation']['right']='UNSEEN'
    elif defect=='unscored_head':
        rt=rich('κ α');original="κ' α"
    elif defect=='unlocated':s['localisation_unknown']=True
    elif defect=='clipped':s['evidence']['clipped_top']=True
    elif defect=='missing_flag':s.pop('apostrophe')
    assert overlay(policy,original,rt)['status']=='hold'


@pytest.mark.parametrize('mode',gate.MODES)
def test_leading_quote_two_absences_release_and_present_text_vetoes(policy,mode):
    assert overlay(policy,'“α',rich('α'),mode)['status']=='corrected'
    assert overlay(policy,'“α',rich('“α'),mode)['status']=='hold'


@pytest.mark.parametrize('original,proposal,classes',[
    ('ά','α',['mark']),('ά','ὰ',['mark']),("Ι'.",'Ι.',['keraia']),
    ('Ι\u0374.','Ι.',['keraia']),('Ι\u02b9.','Ι.',['keraia']),
    ('Ι\u0384.','Ι.',['keraia']),("12'.",'12.',['keraia']),("Ⅻ'.",'Ⅻ.',['keraia']),
    ('“α','α',['quote']),('κ\u1fbf α','κ α',['apostrophe']),('α  β','α β',['other']),
    ('᾿ποὺ',"'ποὺ",['apostrophe']),
    ("κ' α",'κ’ α',[]),('α\u0301','ά',[]),('α','ά',[]),
    ("κ'' α","κ' α",['apostrophe']),('άα','αά',['mark']),('-᾿Α','-Ἀ',['mark']),
])
def test_deletion_inventory_counts_replacements_and_multiplicity(policy,original,proposal,classes):
    assert [r['category'] for r in policy[0].google_deletions(original,proposal)]==classes


def test_insertions_and_sf5_alias_atom_unchanged(policy):
    assert overlay(policy,'α',rich('ά'))['label']=='ά'
    assert overlay(policy,"κ' α",rich('κ’ α'))['label']=="κ' α"


def test_recogniser_score_is_bound_to_release_evidence(policy):
    rt=rich('α');bound=policy[0].bind_runtime(rt)
    rt['recognition_confidence']=.8
    assert policy[0].bind_runtime(rt)['evidence_sha256']!=bound['evidence_sha256']
    bound['recognition_confidence']=.8
    with pytest.raises(ValueError,match='binding mismatch'):policy[0].bind_runtime(bound)


def test_census_is_seeded_thirty_distinct_release_deletions(tmp_path,monkeypatch):
    from scripts.labelfix import sf6_measure as measure
    monkeypatch.setattr(measure,'EV',tmp_path)
    path=tmp_path/'census.jsonl.gz'
    records=[dict(id=f'census-{i:03}',record=dict(id=f'census-{i:03}',label='“α',script_class='greek_poly'),
                  runtime=rich('“α')) for i in range(40)]
    write_rows(path,records);add_census(path)
    first=list(rows(tmp_path/'census_inputs.jsonl.gz'))
    add_census(path);second=list(rows(tmp_path/'census_inputs.jsonl.gz'))
    assert first==second and len(first)==len({r['id'] for r in first})==30


def test_census_missing_evidence_fails_loudly(tmp_path,monkeypatch):
    from scripts.labelfix import sf6_measure as measure
    monkeypatch.setattr(measure,'EV',tmp_path);path=tmp_path/'census.jsonl'
    write_rows(path,[dict(id='missing',google='“α')])
    with pytest.raises(ValueError,match='saved runtime'):add_census(path)


def test_l1r2_aggregate_census_uses_saved_sidecar(tmp_path,monkeypatch):
    from scripts.labelfix import sf6_measure as measure
    monkeypatch.setattr(measure,'EV',tmp_path)
    records=[dict(id=f'census-{i:03}',record=dict(id=f'census-{i:03}',label='“α',script_class='greek_poly'),
                  runtime=rich('“α')) for i in range(40)]
    path=tmp_path/'CHANGES.json'
    path.write_text(json.dumps(dict(modes={'ENSEMBLE_AB':{'overall':{'deletions_by_class':{
        'quote':dict(example_ids=[r['id'] for r in records])}}}})))
    with pytest.raises(ValueError,match='census witnesses pending'):add_census(path)
    assert json.loads((tmp_path/'census_pending.json').read_text())['available_saved_inputs']==[]
    write_rows(tmp_path/'deletion_witness_inputs.jsonl.gz',records)
    add_census(path)
    assert len(list(rows(tmp_path/'census_inputs.jsonl.gz')))==30


def test_every_released_measured_deletion_has_two_certified_absences():
    require_file('docs/records/labelfix/spellcheck/SF6_evidence/heldout/release_labels.jsonl.gz')
    for instrument in ('heldout','m2_dev'):
        for r in rows(EV/instrument/'release_labels.jsonl.gz'):
            if r['after']['status']=='hold':continue
            for c in r['checks']:
                assert c['allowed']
                s=c['signals']
                assert (s['detector'] and s['recogniser'] if c['category'] in ('apostrophe','quote','keraia')
                        else s['reader'] and (s['detector'] or s['recogniser']))
