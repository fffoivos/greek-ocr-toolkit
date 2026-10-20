"""CP1 truth/provenance and fail-closed saved-union regressions; no live writes."""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from tests._paths import ADMISSION, relocated, require_file

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ADMISSION / 'nw1b'
sys.path.insert(0,str(BASE))
import calibrate

FOUR = [
    'gazette_modern--54876940c2de96c3--s000-l0062',
    'gazette_modern--836a4d5d06d0f16d--s000-l0045',
    'ia_poly1850--36dcee7ce4c29f8b--s004-l0062',
    'kosmopolis--109d033afd51aea6--s000-l0019',
]
LEDGER = json.loads(calibrate.LEDGER.read_text())


def load(name):
    spec=importlib.util.spec_from_file_location('cp1_'+name,BASE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.fixture
def current_ledger(tmp_path):
    # Gate mechanics need a current, temporary source binding: CLEAN4L rebased
    # links inside the briefs. Keep the saved ledger and its hashes untouched.
    ledger = copy.deepcopy(LEDGER)
    sources = {}
    for name, digest in ledger['sources'].items():
        path = relocated(name)
        if str(path) != name:
            path = require_file(path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        sources[str(path)] = digest
    ledger['sources'] = sources
    path = tmp_path/'current-ledger.json'
    path.write_text(json.dumps(ledger))
    return path


def test_partition_and_provenance():
    cards,_=calibrate.truth()
    keep={c['row_id'] for c in cards if c['truth']=='keep'}
    drop={c['row_id'] for c in cards if c['truth']=='drop'}
    assert len(keep)==22 and len(drop)==9 and not keep & drop
    assert all(c['provenance'] for c in cards)
    assert LEDGER['eighth_owner_issue']['status']=='unidentified'
    assert LEDGER['eighth_owner_issue']['row_id'] is None
    assert sum(c['truth']=='borderline' for c in cards)==1
    assert len(LEDGER['c1_witnesses'])==6
    gallery={g['row_id'] for g in LEDGER['gallery_witnesses'] if g['type']=='merged_multi_line'}
    c1={c['row_id'] for c in LEDGER['c1_witnesses']}
    assert len(gallery)==6 and len(gallery & c1)==5
    outside='gazette_modern--2e613d9290dd13d4--s000-l0209'
    assert outside not in c1
    witness = next(c for c in LEDGER['non_gating_witnesses'] if c['row_id']==outside)
    assert witness['classification']=='label-error witness, non-gating' and witness['gating'] is False
    assert next(c for c in cards if c['row_id']==outside)['truth']=='label-error witness, non-gating'
    builder = load_builder()
    assert witness['reason']==builder.C068_RULING
    overrun=LEDGER['drop_adjudication']['removed_id']
    assert overrun not in keep|drop
    assert next(c for c in cards if c['row_id']==overrun)['truth']=='diagnostic'
    assert 'halves' in LEDGER['drop_adjudication']['evidence']['detail']


@pytest.mark.parametrize('rid',FOUR)
def test_current_four_false_drops_survive_denominator(rid):
    cards,_=calibrate.truth()
    card=next(c for c in cards if c['row_id']==rid)
    assert card['truth']=='keep' and card['screen_merged'] is True
    pred=calibrate.predictions(card,card['measurement'],calibrate.CANDIDATE_PARAMS)
    assert pred['neighbour_words'] is False and pred['union'] is True
    assert rid in calibrate.build_report()['candidate']['combined']['false_drop_ids']


def test_standalone_pass_union_fail_stops_qualification(tmp_path,current_ledger):
    report=calibrate.build_report(current_ledger)
    assert report['candidate']['standalone']['gate']
    assert report['candidate']['combined']['confusion']==dict(tp=9,fp=4,fn=0,tn=18)
    assert set(report['candidate']['combined']['false_drop_ids'])==set(FOUR)
    assert not report['gate'] and report['selected'] is None
    path=tmp_path/'current-calibration.json'
    path.write_text(json.dumps(report))
    with pytest.raises(calibrate.QualificationError,match='actual segmentation union'):
        calibrate.require_qualification(path, ledger_path=current_ledger)


@pytest.mark.parametrize('script',['prepare_w1','reissue'])
def test_preparation_and_reissue_stop_before_side_effects(script,monkeypatch,tmp_path,current_ledger):
    module=load(script)
    touched=[]
    def forbidden(*args,**kwargs):
        touched.append(True)
        raise AssertionError('preparation/publication reached on failing gate')
    path=tmp_path/'current-calibration.json'
    path.write_text(json.dumps(calibrate.build_report(current_ledger)))
    monkeypatch.setattr(module,'require_qualification',lambda *a, **kw: calibrate.require_qualification(path, ledger_path=current_ledger))
    if script=='prepare_w1':
        monkeypatch.setattr(module,'page_measurements',forbidden)
        monkeypatch.setattr(module,'ProcessPoolExecutor',forbidden)
    else:
        monkeypatch.setattr(module,'run_files',forbidden)
        monkeypatch.setattr(module.os,'replace',forbidden)
    with pytest.raises(calibrate.QualificationError,match='GATE_FAIL'):
        module.main()
    assert not touched


def test_planted_standalone_pass_union_fail():
    # Mechanical observations, not semantic word annotations.
    measurement=dict(matched=True,xheight=10.,components=[])
    card=dict(row_id='planted-keep',truth='keep',screen_merged=True,rotated_crop=False,measurement=measurement)
    standalone=calibrate.score([card],{'planted-keep':measurement},calibrate.CANDIDATE_PARAMS)
    union=calibrate.score([card],{'planted-keep':measurement},calibrate.CANDIDATE_PARAMS,True)
    assert standalone['gate'] and not union['gate']
    assert union['confusion']==dict(tp=0,fp=1,fn=0,tn=0)
    assert standalone['recall']['value'] is None  # no positive denominator


def test_orientation_is_in_the_actual_union():
    m=dict(matched=True,xheight=10.,components=[])
    c=dict(row_id='upright-truth',truth='keep',screen_merged=False,rotated_crop=True)
    assert calibrate.predictions(c,m,calibrate.CANDIDATE_PARAMS)['union'] is True
    assert not calibrate.score([c],{c['row_id']:m},calibrate.CANDIDATE_PARAMS,True)['gate']


def test_missing_observation_is_unknown_not_verified_keep():
    c=dict(row_id='unknown',truth='keep',screen_merged=False,rotated_crop=False)
    result=calibrate.score([c],{},calibrate.CANDIDATE_PARAMS,True)
    assert not result['gate'] and result['unknown_count']==1
    assert result['confusion']==dict(tp=0,fp=0,fn=0,tn=0)
    assert result['keep_false_drop_rate']['value'] is None


def test_no_overlap_by_duplicate_id():
    c=dict(row_id='same',truth='keep')
    with pytest.raises(calibrate.QualificationError,match='duplicate'):
        calibrate.score([c,dict(c,truth='drop')],{},calibrate.CANDIDATE_PARAMS)


@pytest.mark.parametrize('mutation',['forged_pass','wrong_hash','standalone_only'])
def test_stale_or_standalone_report_cannot_authorize(tmp_path,mutation):
    report=calibrate.build_report()
    if mutation=='forged_pass': report['gate']=True
    if mutation=='wrong_hash': report['bindings']['ledger_sha256']='0'*64
    if mutation=='standalone_only': report['selected']=report['candidate']; report['gate']=report['candidate']['standalone']['gate']
    path=tmp_path/'report.json';path.write_text(json.dumps(report))
    with pytest.raises(calibrate.QualificationError,match='stale/inconsistent'):
        calibrate.require_qualification(path)


def test_pre_collector_screen_population_is_bound():
    pop=LEDGER['pre_screen_population']
    assert pop['feature_rows']==101098 and pop['eligible_rows']==33301
    assert pop['feature_source'] in LEDGER['sources']
    for rid in FOUR:
        c=next(c for c in LEDGER['cases'] if c['row_id']==rid)
        # All observations come from pre-screen features, including any strata
        # outside the current content allowlist; none are excused downstream.
        assert c['screen_merged'] is True
    assert len(calibrate.build_report()['witnesses']['c1']['detected'])==6
    assert len(calibrate.build_report()['witnesses']['gallery_merges']['detected'])==6


def test_calibration_never_calls_detector_or_measurement(monkeypatch):
    from greekocr.harvest import neighbour_words
    import greekocr.pages as detector
    def forbidden(*args,**kwargs): raise AssertionError('CP1 must use saved observations')
    monkeypatch.setattr(neighbour_words,'page_measurements',forbidden)
    # process_page is imported only by the NW draft's measurement entrypoint.
    if hasattr(detector,'process_page'): monkeypatch.setattr(detector,'process_page',forbidden)
    assert not calibrate.build_report()['gate']


@pytest.mark.parametrize('mutation',['invented_keep','invented_drop','invented_count','eighth_issue'])
def test_no_invented_truth_or_counts(tmp_path,mutation):
    ledger=copy.deepcopy(LEDGER)
    if mutation=='invented_keep':
        next(c for c in ledger['cases'] if c['truth']=='keep')['row_id']='invented-owner-keep'
    if mutation=='invented_drop':
        next(c for c in ledger['cases'] if c['truth']=='drop')['row_id']='invented-owner-drop'
    if mutation=='invented_count': ledger['counts']['named_owner_issues']=8
    if mutation=='eighth_issue': ledger['eighth_owner_issue']['row_id']='c068-is-not-eighth'
    path=tmp_path/'ledger.json';path.write_text(json.dumps(ledger))
    with pytest.raises(calibrate.QualificationError): calibrate.truth(path)


def load_builder():
    path = BASE.parent/'seg/freeze_truth.py'
    spec = importlib.util.spec_from_file_location('freeze_truth_cp4c', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
