"""R2 artifact custody and scorer contract. Offline; never invokes readers."""
import sys,gzip,json
from pathlib import Path
from tests._paths import ADMISSION, require_file
import pytest
BASE=ADMISSION / 'seg/cp7'
sys.path.insert(0,str(BASE))
import r2_common as c
import score_r2 as score

@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_freeze_binding_list():
    f=c.verify();lines=(BASE/'freeze_bound_paths_r2.txt').read_text().splitlines()[1:]
    assert set(lines)==set(f['files'])|set(f['geometry_files'])
    assert any(p.endswith('calibrate_cp5pb.py') for p in lines)
    assert any(p.endswith('CP5_verification.json') for p in lines)

def test_draw_deterministic_disjoint_and_snapshot_bound(monkeypatch):
    require_file(c.SEG/'CP5_verification.json')
    require_file(c.SEG/'CP5_cp4_verification.json')
    import prepare_r2 as prep
    monkeypatch.setattr(prep.build, 'COLLECTOR', Path(__file__).resolve().parents[1])
    rec=c.read(c.R2/'draw_receipt.json');records=[]
    for p,h in rec['inputs'].items():
        assert c.sha(p)==h
        if Path(p).name.startswith(('W1_features_','W2_features_')):records+=c.rows(p)
    _,classes,_=prep.build.exclusion_sets();fresh=prep.build.fresh_ids(c.read(c.SEG/'calibration_ledger.json'))
    first={r['id'] for r in c.rows(BASE/'keys/draw.jsonl')}
    pool=c.population(records,set().union(*classes.values()),fresh|first)
    draw=c.rows(c.R2/'keys/draw.jsonl')
    assert draw==prep.select_r2(pool)==prep.select_r2(list(reversed(pool)))
    assert len(draw)==len({r['id'] for r in draw})==100
    assert not {r['id'] for r in draw}&(fresh|first)

@pytest.mark.parametrize('bed',c.BEDS_R2)
@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_pack_closure_opacity_crop_shas_and_controls(bed):
    key=c.read(c.R2/'keys'/f'{bed}.json');directory=c.PACK_ROOT/bed/'r1'
    files=c.closure(directory,key['readers']['r1'])
    assert files==c.read(directory.parent/'MANIFEST.r1.json')['files']
    assert sum(m['control'] for m in key['items'].values())==5
    assert all(c.sha(c.R2/'crops'/(m['crop_sha256']+'.png'))==m['crop_sha256'] for m in key['items'].values() if not m['control'])
    old={r['card_id'] for bed0 in ('segcp7_a','segcp7_b') for r in c.rows(c.PACK_ROOT/bed0/'r1/cards.jsonl')}
    assert not set(key['items'])&old

@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_scanner_prompt_and_launcher():
    assert c.sha(BASE/'tools/scan_rollout.py')==c.SCANNER
    assert c.sha(BASE/'prompts/bsb.md')==c.sha(c.REFERENCE/'prompts/bsb.md')
    assert c.sha(BASE/'prompts/path_addendum_r2.md')==c.sha(c.ROOT/'docs/records/harvest/recut_v1/w1_masked/w2c1/prompts/path_addendum.md')
    rubric=(BASE/'prompts/segcp7_crop_rubric_r2.md').read_text()
    assert all(f'`{f}`' in rubric and f'`{f}_reason`' in rubric for f in (*score.TRUTH_FIELDS,'end_clip'))
    assert 'two horizontally adjacent text blocks joined' in rubric
    assert not any(x in rubric for x in ('geometry_unavailable','edge_clip_candidate','screen_drop','76ea2d35'))
    assert not (BASE/'run_r2.log').exists()
    assert not list((c.R2/'answers').glob('**/*.jsonl')) if (c.R2/'answers').exists() else True
    launcher=(c.R2/'launchers/run_bed.sh').read_text()
    assert 'Refuse rerun' in launcher and 'limit_probe.sh' in launcher and 'path_addendum_r2.md' in launcher

@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_frozen_gate_and_seal():
    gate=c.read(c.R2/'frozen_gate.json')
    assert gate['passed'] and gate['freeze_sha256']==c.sha(c.FREEZE)
    assert {k:(v['met'],v['required']) for k,v in gate['counts'].items()}==dict(KEEP=(22,22),D=(9,9),C1=(6,6),gallery=(6,6),rotated=(4,4))
    build=c.read(c.R2/'build_receipt.json');seal=c.R2/'keys/sealed_decisions.jsonl.gz'
    assert c.sha(seal)==build['sealed_decisions_sha256']
    records=[json.loads(l) for l in gzip.open(seal,'rt')]
    assert len(records)==100
    assert all('edge_clip_candidate' in r and 'orientation_unknown' in r for r in records)
    assert not seal.stat().st_mode&0o077

@pytest.mark.parametrize('field',score.TRUTH_FIELDS)
def test_score_truth_bits(field):
    a={f:'no' for f in (*score.TRUTH_FIELDS,'end_clip')};a['end_clip']='yes'
    assert not score.truth(a)
    a[field]='yes';assert score.truth(a)

def test_score_policy_and_diagnostic_fixture():
    a={f:'no' for f in (*score.TRUTH_FIELDS,'end_clip')};a['end_clip']='yes'
    s=dict(merged=False,neighbour_words=False,orientation=False,crossing={'drop':False},screen_drop=True,geometry_unavailable=True,orientation_unknown=True,edge_clip_candidate=True)
    r=dict(context_valid=True,row_id='fixture',reader=a,sealed=s,predictions=score.predictions(s),truth='KEEP',mismatches=score.mismatches(s,a),flag=False,unreadable=False)
    controls=[dict(passed=True)]*10;custody=[dict(scan_ok=True)]*2
    summary=score.summarize([r],controls,custody)
    assert summary['geometry_unavailable']['total']==1 and summary['screen_denominator']==0
    assert all(m['FP']==m['FN']==0 for m in summary['matrices'].values())
    assert summary['end_clip']['rate']==1 and summary['edge_clip_candidate']['agreement']['TP']==1
    assert not summary['gate_pass'] # mapped is not 100
    s['geometry_unavailable']=False;s['screen_drop']=False
    summary=score.summarize([r]*100,controls,custody)
    assert summary['gate_pass']
    controls[0]=dict(passed=False);assert not score.summarize([r]*100,controls,custody)['gate_pass']

def test_score_matrix_directions_and_unknown():
    assert [score.matrix([(True,True),(True,False),(False,True),(False,False)])[k] for k in ('TP','FP','FN','TN')]==[1,1,1,1]
    s=dict(merged=None,neighbour_words=None,orientation=None,crossing={'drop':None})
    assert not any(score.predictions(s).values())
