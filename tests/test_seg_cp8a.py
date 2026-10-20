"""CP8 closure and fail-closed policy regressions; temporary artifacts only."""
import importlib.util,json
from pathlib import Path
from tests._paths import ADMISSION
import pytest
from greekocr.harvest.qualified_admission import evaluate_evidence
from greekocr.harvest.application_identity import identity
ROOT=Path(__file__).resolve().parents[1]
HERE=ADMISSION / 'seg/cp8a'

def test_closure_drift_fails_closed(tmp_path):
    p=tmp_path/'manifest.json';p.write_text(json.dumps(dict(files={'greekocr/harvest/qualified_admission.py':'0'*64})))
    with pytest.raises(ValueError,match='application closure drift'):identity(p)

@pytest.mark.parametrize('candidate',[None,False,True])
def test_end_clip_never_gates(candidate):
    d=evaluate_evidence({},screen_only=True,structural=dict(status='measured',merged=False,neighbour_drop=False,union_drop=False),
        axis=dict(status='orientation_unknown',rotated=None),crossing=dict(status='measured',drop=False),edge=dict(candidate=candidate))
    assert d['pass'] and d['screen_drop'] is False and d['orientation_unknown']
    assert d['edge_clip_candidate'] is candidate

def test_unavailable_geometry_never_admits():
    d=evaluate_evidence({},screen_only=True,structural=dict(status='unavailable',merged=None,neighbour_drop=None,union_drop=None),
        axis=dict(status='orientation_unknown',rotated=None),crossing=dict(status='unavailable',drop=None))
    assert not d['pass'] and d['hits']['geometry_unavailable']

@pytest.mark.parametrize('draw,n',[('r1',28),('r2',43)])
def test_flagged_entries_exhaustively_accounted(draw,n):
    data=json.loads((HERE/(draw+'_matrices.json')).read_text())
    assert len({r['row_id'] for r in data['accounting']})==n
    assert all(len(r['crop_sha256'])==64 and r['disposition'] for r in data['accounting'])

def test_accepted_fp_are_preserved():
    data=json.loads((HERE/'r2_matrices.json').read_text())
    assert data['adjudicated_standalone']['union']['FP']==3
    assert data['text_eligible_composition']['union']['FP']==2
    assert data['text_eligible_composition']['union']['FN']==0


from test_neighbour_words import staged_pair

def test_corrupt_active_crop_preserves_manifest(staged_pair):
    module,admitted,features,out,rows=staged_pair
    previous=(out.parent/'crops_manifest.jsonl').read_bytes()
    target=out/'bsb_poly1850/test-0.png';target.write_bytes(b'corrupt active witness')
    with pytest.raises(ValueError,match='crop hash mismatch'):
        module.stage(admitted,features,out)
    assert (out.parent/'crops_manifest.jsonl').read_bytes()==previous
    assert target.read_bytes()==b'corrupt active witness'

def test_retained_size_corruption_preserves_manifest(staged_pair):
    module,admitted,features,out,rows=staged_pair
    path=out.parent/'crops_manifest.jsonl'
    data=[json.loads(l) for l in path.read_text().splitlines()]
    data[1]['bytes']+=1
    path.write_text(''.join(json.dumps(r)+'\n' for r in data));previous=path.read_bytes()
    admitted.write_text(json.dumps(rows[0])+'\n')
    with pytest.raises(ValueError,match='hash/size mismatch'):
        module.stage(admitted,features,out)
    assert path.read_bytes()==previous


def test_replay_cannot_silently_skip_text_metadata():
    with pytest.raises((ValueError,KeyError)):
        evaluate_evidence({},structural=dict(status='measured',merged=False,neighbour_drop=False,union_drop=False),
            axis=dict(status='orientation_unknown',rotated=None),crossing=dict(status='measured',drop=False))
