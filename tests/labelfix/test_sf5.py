"""SF5 release-only witnesses. Saved runtime; no detector/model execution."""
from copy import deepcopy
import json
import os

import pytest
from tests._paths import evidence_params

from greekocr.labelfix import reading as R, release_gate
from greekocr.labelfix.text import ELISION, clusters, is_letter, nfd, nfc
from scripts.labelfix.clariden import l1_common
from scripts.labelfix.clariden.r1_common import rows, write_rows
from scripts.labelfix.sf5_measure import baseline, BINDING, DOC


@pytest.fixture(scope='module')
def policy():
    return baseline() if os.environ.get('SF5_TEST_BASELINE') else (release_gate, l1_common)


def synthetic(text, *, detector_apostrophe=False, named=True):
    text=nfd(text);slots=[];pred=[];cov=[]
    for c in clusters(text):
        if not is_letter(c.base):continue
        parts=[p for p,m in R.MARKS.items() if m in c.marks] if named else []
        slots.append(dict(base=c.base,start=c.start,end=c.end,parts=parts,
            apostrophe=detector_apostrophe and not slots,unnamed=[],
            localisation_unknown=False,segmentation_uncertain=False,
            evidence=dict(clipped_top=False,clipped_bottom=False)))
        pred.append(dict(start=c.start,base=c.base,parts=parts))
        cov.append(dict(start=c.start,base=c.base,scored=True,
                        evidence_state='unadjudicated',uncertainty=[]))
    return dict(id='x',recogniser_text=nfc(text),
        detector=release_gate.serialize(R.LineReading(nfc(text),slots,[])),
        r1_predictions=pred,coverage=cov,peer_predictions={a:deepcopy(pred) for a in ('B','E')},
        peer_coverage={a:deepcopy(cov) for a in ('B','E')})


def overlay(policy, original, runtime, mode='ensemble_ab'):
    return policy[1].overlay(dict(id='x',label=original,script_class='greek_poly'),runtime,mode,BINDING)


WITNESSES=evidence_params(DOC/'SF5_evidence/witness_inputs.jsonl.gz',
                          lambda p: list(rows(p)), ids=lambda r: r['id'])
SF6_HELD={
    'a300f5e1c3f6a38d97201791-p000442-l0085',
    '453f156dc6352286456a08cb-p000100-l0002',
    '143e78b5de2e6e784534ee0d-p000061-l0032',
    'b518f9f9b73fe9a3257fe2f0-p000041-l0022',
    '137e9af6a0045d5746e26efa-p000008-l0008',
    '8961f6bdd6daf004b4a84dfa-p000025-l0051',
    '00c322b3ee04b419d1979f22-p000115-l0022',
    '827d2345ad77e5cdec320e80-p000028-l0019',
}


def assert_sf6_hold(result,original):
    assert result['status']=='hold' and result.get('label',original)==original
    assert result['changes']==[]
    assert any(not c['allowed'] for c in result['deletion_checks'])
    assert any(s['detail'].startswith('sf6:deletion_needs_two_positive_absences:') for s in result['hold_slots'])


@pytest.mark.parametrize('w',WITNESSES)
def test_saved_56_release_witnesses(policy,w):
    result=policy[1].overlay(w['record'],w['runtime'],'ensemble_ab',BINDING)
    # SF6 changes only release acceptance. Preserve this exact assertion even
    # for the eight still-held lines, including both known reader mistakes.
    assert policy[0].compose_runtime(w['runtime'],'ENSEMBLE_AB')['slots']==w['sf4_decisions']['slots']
    if policy[0].POLICY=='sf6-release-v1' and w['id'] in SF6_HELD:
        assert_sf6_hold(result,w['record']['label'])
        return
    assert result['status'] in ('corrected','unchanged')
    actual=result['label']
    if w['kind'].startswith('known_reader_'):
        # Precision counterexamples remain wrong; SF5 must not change them.
        assert actual==w['before'] and result['status']=='corrected'
    elif w['kind']=='capital_breathing':
        assert actual==w['before'].replace("-'Ἀ",'-Ἀ')
    else:
        from greekocr.labelfix.text import punctuation_sites
        both=punctuation_sites(w['record']['label']).keys() & punctuation_sites(w['runtime']['recogniser_text']).keys()
        if both:
            assert both<=punctuation_sites(actual).keys()
        else:
            # One seeded line has only Google's mark. Its deletion is outside
            # the consensus rule and must retain SF4 behavior, with a census.
            assert actual==w['before']
            assert result['elision_census']['google_only_deleted']==1
    # All mark sets, decision reasons and saved physical records are retained.
    assert policy[0].compose_runtime(w['runtime'],'ENSEMBLE_AB')['slots']==w['sf4_decisions']['slots']


@pytest.mark.parametrize('mode',release_gate.MODES)
@pytest.mark.parametrize('google_alias',ELISION)
@pytest.mark.parametrize('recogniser_alias',ELISION)
def test_both_sources_override_detector_absence(policy,mode,google_alias,recogniser_alias):
    original='κ'+google_alias+' ἡ'
    result=overlay(policy,original,synthetic('κ'+recogniser_alias+' ἡ'),mode)
    assert result['status']=='unchanged' and result['label']==original
    assert result['elision_census']['both_kept']==1
    assert result['elision_census']['both_deleted']==0


@pytest.mark.parametrize('alias',ELISION)
def test_elision_after_combining_marks(policy,alias):
    original='α\u0301'+alias+' ἡ'
    result=overlay(policy,original,synthetic("ά' ἡ"))
    assert result['status']=='unchanged' and result['label']==original


@pytest.mark.parametrize('mode',release_gate.MODES)
@pytest.mark.parametrize('spacing','᾿᾽')
@pytest.mark.parametrize('base',['Α','Ε','Ρ','α','ε'])
def test_spacing_breathing_consumed_in_same_edit(policy,mode,spacing,base):
    original='-'+spacing+base+'λα'
    breathing='\u0314' if base=='Ρ' else '\u0313'
    runtime=synthetic("-'"+base+breathing+'λα')
    result=overlay(policy,original,runtime,mode)
    if policy[0].POLICY=='sf6-release-v1':
        assert_sf6_hold(result,original)
        assert any(c['character']==spacing and c['category']=='mark' for c in result['deletion_checks'])
        # The SF5 proposal is still atomic; only release becomes HOLD.
        proposal,_=policy[0].release_text(original,runtime['recogniser_text'],policy[0].compose_runtime(runtime,mode)['text'])
        assert proposal==nfc('-'+base+breathing+'λα')
        return
    assert result['status']=='corrected' and result['label']==nfc('-'+base+breathing+'λα')
    assert len(result['changes'])>=1 and not result['hold_slots']


@pytest.mark.parametrize('spacing','᾿᾽')
def test_spacing_breathing_unattached_stays_verbatim(policy,spacing):
    original='-'+spacing+'Αλλά'
    result=overlay(policy,original,synthetic(original,named=False))
    if policy[0].POLICY=='sf6-release-v1':
        assert_sf6_hold(result,original)
        assert spacing in result.get('label',original)
        assert [c['character'] for c in result['deletion_checks']]==['\u0301']
        return
    assert result['label']==nfc(original.replace('ά','α'))  # real accent edit is still allowed
    assert spacing in result['label'] and '’' not in result['label']


@pytest.mark.parametrize('spacing','᾿᾽')
def test_uncertain_attachment_keeps_google(policy,spacing):
    original='-'+spacing+'Αλλά';runtime=synthetic("-'Ἀλλά")
    runtime['coverage'][0]['scored']=False
    result=overlay(policy,original,runtime)
    assert result['status']=='hold' and result.get('label',original)==original


@pytest.mark.parametrize('alias',"'ʼ᾽᾿")
def test_alias_only_is_unchanged_with_original_bytes(policy,alias):
    original='κ'+alias+' α'
    result=overlay(policy,original,synthetic(original,detector_apostrophe=True))
    assert result['status']=='unchanged' and result['label']==original
    assert result['alias_only'] is True and result['changes']==[]


def test_real_mark_edit_preserves_google_elision_spelling(policy):
    result=overlay(policy,'κ᾿ α',synthetic("κ' ά",detector_apostrophe=True))
    assert result['status']=='corrected' and result['label']=='κ᾿ ά'
    assert result['alias_only'] is False


@pytest.mark.parametrize('source',['google','recogniser'])
@pytest.mark.parametrize('detected',[False,True])
def test_single_source_presence_behavior_unchanged_and_counted(policy,source,detected):
    original='κ᾿ α' if source=='google' else 'κ α'
    text='κ α' if source=='google' else "κ' α"
    result=overlay(policy,original,synthetic(text,detector_apostrophe=detected))
    expected=('κ᾿ α' if source=='google' else 'κ’ α') if detected else 'κ α'
    if policy[0].POLICY=='sf6-release-v1' and source=='google' and not detected:
        assert_sf6_hold(result,original)
        assert result['deletion_checks'][0]['category']=='apostrophe'
    else:assert result['label']==expected
    c=result['elision_census']
    assert c['both']==0 and c[source+'_only']==1
    assert c[source+'_only_kept' if detected else source+'_only_deleted']==1


@pytest.mark.parametrize('original,proposal',[("-᾿Α","-Ἀ"),("-᾽α","-ἀ")])
def test_guard_accepts_only_atomic_spacing_breathing_attachment(policy,original,proposal):
    assert policy[0].edit_guard(original,proposal)==[]
    assert policy[0].edit_guard(original,proposal.replace('Ἀ','Α').replace('ἀ','α'))
    assert policy[0].edit_guard(original,proposal.replace('-','!'))


def test_alias_manifest_accounting_has_no_status_double_count(policy,tmp_path):
    source=tmp_path/'source';source.write_text('source bytes')
    selection=tmp_path/'selection';runtime=tmp_path/'runtime'
    write_rows(selection,[dict(id='x',label='κ᾿ α',wave='wave',source='source',script_class='greek_poly')])
    write_rows(runtime,[synthetic("κ' α",detector_apostrophe=True)])
    binding=dict(BINDING,code_commit='test',detector_commit='test')
    receipt=dict(exclusions={},out_of_scope={},r0_policy='test',input_documents_sha256={})
    out=tmp_path/'release'
    counts=policy[1].release(selection,[runtime],out,binding,source,receipt)
    for mode in ('presence','full'):
        m=json.loads((out/f'release_{mode}.json').read_text())
        assert counts[mode]==dict(corrected=0,unchanged=1,hold=0,out_of_scope=0)
        assert m['alias_only']==1 and m['coverage_per_wave']['wave']['alias_only']==1
        assert m['coverage_per_source']['source']['total']==1
        assert list(rows(out/f'overlay_{mode}.jsonl.gz'))[0]['alias_only'] is True
        assert list(rows(out/f'ctrl_subset_{mode}.jsonl.gz'))[0]['label']=='κ᾿ α'


def test_composer_consumes_its_own_spacing_breathing(policy):
    r=synthetic('-᾿Ἀλλα')
    result=policy[0].compose_runtime(r,'ENSEMBLE_AB')
    assert result['text']=='-Ἀλλα' and not result['hold_slots']


def test_elision_instrument_counts_printed_initial_sign_and_excludes_breathing():
    from scripts.labelfix.sf5_measure import mapped_elisions,score_elisions
    assert mapped_elisions("δὲ 'φελα", "δὲ 'φελα")=={2}
    assert mapped_elisions('-᾿Αλλα','-Αλλα')==set()
    site=dict(line_id='x',letter_boundary=2,status='KNOWN',printed_role='apostrophe_elision',
              truth_source='R0_adjudication',card_ids=['synthetic'])
    counts,_=score_elisions([site],{'x':"δὲ 'φελα"},{'x':"δὲ 'φελα"})
    assert counts['kept']==1 and counts['deleted']==0
    quote=dict(site,printed_role='quote')
    counts,_=score_elisions([quote],{'x':"δε’"},{'x':"δε’"})
    assert counts['added']==0 and counts['excluded_quote_sites']==1


def test_word_final_elision_is_after_a_letter_including_combining_marks(policy):
    assert policy[0]._word_final_elision(clusters(nfd("x\u0301' α")),1)
