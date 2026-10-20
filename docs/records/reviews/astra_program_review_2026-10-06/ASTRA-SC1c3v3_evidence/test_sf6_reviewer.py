"""SF6/SF6b-only release witnesses. Synthetic saved records; no inference."""
from copy import deepcopy

import pytest
from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.ctc_align import Alignment
from scripts.labelfix.clariden import l1_common
from tests.labelfix.test_sf6 import rich,move_runtime,overlay

POLICY=(gate,l1_common)


def legacy_unscored_punctuation():
    # Real legacy loader: omitted confidence becomes 0.0; infer_line subsequently
    # serializes alignment.confidence as recognition_confidence.
    legacy=dict(prediction='δ',spans=[['δ',1,2,10.,18.]],n_frames=10,scale=1.,strip_width=40)
    alignment=Alignment.from_record(legacy)
    assert 'confidence' not in legacy and alignment.confidence==0.
    rt=rich('δ');rt['recognition_confidence']=alignment.confidence
    # Delta has no R1 mark head. Those inputs cannot certify punctuation.
    rt['r1_predictions']=[];rt['coverage']=[];rt['peer_predictions']={};rt['peer_coverage']={}
    return legacy,rt


def ordinary_absence_outside_window(source):
    if source=='reader':
        rt=rich('ά');rt.pop('recognition_confidence')
        rt['detector']['slots'][0]['parts']=[]
        for preds in [rt['r1_predictions'],*rt['peer_predictions'].values()]:preds[0]['parts']=[]
        for cov in [rt['coverage'],*rt['peer_coverage'].values()]:cov[0]['span']=[100000,100010]
    else:
        rt=rich('α')
        # No detector absence observation: only the reader and alleged
        # recogniser observation can authorize this deletion.
        rt['detector']['slots'][0]['evidence'].pop('observation')
        rt['detector']['slots'][0]['locator_span']=[100000,100010]
    assert rt['detector']['slots'][0]['evidence']['window']==[8,20]
    return rt


@pytest.mark.parametrize('mode',gate.MODES)
def test_missing_score_default_is_not_positive_recogniser_absence(mode):
    _,rt=legacy_unscored_punctuation()
    result=overlay(POLICY,"δ'",rt,mode)
    assert result['status']=='hold' and 'label' not in result,result


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('source',['reader','recogniser'])
def test_deletion_source_must_cover_the_target_window(mode,source):
    result=overlay(POLICY,'ά',ordinary_absence_outside_window(source),mode)
    assert result['status']=='hold' and 'label' not in result,result


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('defect',['missing_score','unscored_A','missing_B','clipped_top','uncertainty','missing_span'])
def test_existing_negative_controls_hold(mode,defect):
    rt=rich('α');rt['detector']['slots'][0]['evidence'].pop('observation')
    if defect=='missing_score':rt.pop('recognition_confidence')
    elif defect=='unscored_A':rt['coverage'][0]['scored']=False
    elif defect=='missing_B':rt['peer_predictions'].pop('B');rt['peer_coverage'].pop('B')
    elif defect=='clipped_top':rt['detector']['slots'][0]['evidence']['clipped_top']=True
    elif defect=='uncertainty':rt['peer_coverage']['B'][0]['uncertainty']=['no_pixel_evidence']
    elif defect=='missing_span':rt['detector']['slots'][0].pop('locator_span')
    result=overlay(POLICY,'ά',rt,mode)
    assert result['status']=='hold' and 'label' not in result


@pytest.mark.parametrize('mode',gate.MODES)
def test_positive_reader_detector_control(mode):
    rt=rich('ά');rt.pop('recognition_confidence');rt['detector']['slots'][0]['parts']=[]
    for preds in [rt['r1_predictions'],*rt['peer_predictions'].values()]:preds[0]['parts']=[]
    result=overlay(POLICY,'ά',rt,mode)
    assert (result['status'],result['label'])==('corrected','α')
    assert result['deletion_checks'][0]['signals']==dict(reader=True,detector=True,recogniser=False)


@pytest.mark.parametrize('mode',gate.MODES)
@pytest.mark.parametrize('defect',['none','kind','unnamed','noncapital','extra_sign','other_deletion','outside_window'])
def test_move_exception_is_confined_to_one_matching_spacing_sign(mode,defect):
    original='-᾿Αλλα';proposal='-Ἀλλα'
    if defect=='kind':proposal='-Ἁλλα'
    if defect=='noncapital':original='-᾿αλλα';proposal='-ἀλλα'
    if defect=='extra_sign':original='-᾿᾿Αλλα'
    if defect=='other_deletion':original='“-᾿Αλλα'
    rt=move_runtime(proposal);rt.pop('recognition_confidence')
    if defect=='kind':rt['detector']['slots'][0]['evidence'].pop('observation')
    if defect=='unnamed':rt['peer_predictions']['B'][0]['parts']=[]
    if defect=='outside_window':rt['peer_coverage']['B'][0]['span']=[100000,100010]
    result=overlay(POLICY,original,rt,mode)
    if defect=='none':
        assert (result['status'],result['label'])==('corrected',proposal)
        assert len(result['deletion_checks'])==1
        assert result['deletion_checks'][0]['operation']=='MOVE'
        assert result['deletion_checks'][0]['signals']==dict(reader=False,detector=False,recogniser=False)
    else:
        assert result['status']=='hold' and 'label' not in result,result
        assert any(not c['allowed'] for c in result['deletion_checks'])


@pytest.mark.parametrize('old,new,n',[
    ('άἀ','ὰἁ',2),("δ''",'δ',2),('“ά','α',2),('άα','αά',1),
    ("δ'",'δ’',0),('α','ά',0),('-᾿Α','-Ἀ',1),
])
def test_replacements_multiple_edits_and_alias_inventory(old,new,n):
    assert len(gate.google_deletions(old,new))==n
