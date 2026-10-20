import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import pytest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
import build_release_admission as b
import stage_crops as stage


def row(**kwargs):
    r=dict(id='test-l0001',page_id='test',source='nlg',primary_class='poly1850',
           label='ἑλληνικὸς πλήρης λόγος',candidate_usable=True,tranche='W2',
           bbox=[0,0,100,20],crop_bbox=[0,0,100,20],crop_sha256='a'*64,
           crop_source_image='/missing.png',crop_source_sha256='b'*64)
    r.update(kwargs);return r

@pytest.mark.parametrize('source,cls',[*sorted(b.C1),('gazette_modern','modern_scanned')])
def test_w2_qualified(source,cls):
    assert b.included(row(source=source,primary_class=cls,gazette_stratum='measured_1986_1990'),'W2')

@pytest.mark.parametrize('change',[dict(candidate_usable=False),dict(candidate_usable=1),
    dict(source='kosmopolis',primary_class='poly1900'),dict(source='lekythos',primary_class='poly1900'),
    dict(source='gazette_modern',primary_class='modern_scanned',gazette_stratum='unmeasured'),
    dict(source='unknown',primary_class='headings_caps')])
def test_w2_unqualified(change):
    assert not b.included(row(**change),'W2')

@pytest.mark.parametrize('source',sorted(b.W2_SOURCES))
def test_caps_carried(source):
    assert b.included(row(source=source,primary_class='headings_caps'),'W2')


def test_w1_extra_strata():
    for source,cls in b.W1_EXTRA:
        assert b.included(row(source=source,primary_class=cls),'W1')
        assert not b.included(row(source=source,primary_class=cls),'W2')


def test_all_registered_exclusions_hash_and_count():
    ids,bindings,counts=b.exclusions(b.EXCLUSIONS)
    config=json.loads(b.EXCLUSIONS.read_text())
    assert set(counts)==set(config['classes'])
    for name,meta in config['classes'].items():
        p=b.EXCLUSIONS.parent/meta['file']
        assert bindings[str(p)]==meta['sha256']
        assert set(p.read_text().split())<=ids


def test_snapshot_filters_excludes_and_medians(tmp_path):
    rows=[row(id='a'),row(id='b'),row(id='c',candidate_usable=False,bbox=[0,0,100,80])]
    p=tmp_path/'W2_features_20261018_0524.jsonl'
    p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (tmp_path/'SHA256_20261018_0524.txt').write_text(b.sha(p)+'  '+p.name+'\n')
    selected,medians,counts,inputs=b.snapshot(p,'W2',{'b'})
    assert [r['id'] for r in selected]==['a']
    assert medians[b.adm._page_key(rows[0])]==20
    assert counts==dict(snapshot_rows=3,qualified_before_exclusions=2,excluded=1)
    p.write_text(p.read_text()+'\n')
    with pytest.raises(ValueError,match='snapshot sha'):b.snapshot(p,'W2',set())


def test_no_geometry_never_keep():
    d=b.compose(row(),20,None,{},.04)
    assert d['geometry_unavailable'] is True
    assert d['pass'] is False
    assert 'geometry_unavailable' in d['rules_failed']
    assert d['orientation_status']=='not_run'


def test_no_geometry_outputs_deterministic(tmp_path):
    decision=b.compose(row(),20,None,{},.04)
    outputs=[]
    for i in range(2):
        w=b.Jsonl(tmp_path/'decisions.jsonl');w.write(decision);meta=w.finish()
        outputs.append((meta,(tmp_path/meta['path']).read_bytes()))
    assert outputs[0]==outputs[1]


def test_counts_reconcile_overlap_and_disjoint():
    counts=b.bucket()
    d=b.compose(row(label='x'),20,None,{},.04)
    b.count(counts,d);b.finish_bucket(counts)
    assert counts['pre_screen_n']==1
    assert counts['dropped_per_rule']['text_rules']==1
    assert counts['dropped_per_rule']['geometry_unavailable']==1
    assert sum(counts['first_drop'].values())==1


def test_gzip_deterministic_uncompressed_sha(tmp_path):
    value={'x':'a'*50_000_000}
    hashes=[]
    for i in range(2):
        w=b.Jsonl(tmp_path/'big.jsonl');w.write(value);meta=w.finish()
        data=(tmp_path/meta['path']).read_bytes()
        assert meta['path'].endswith('.gz')
        assert hashlib.sha256(gzip.decompress(data)).hexdigest()==meta['uncompressed_sha256']
        hashes.append(meta['sha256'])
    assert len(set(hashes))==1


def test_stage_floor_and_extension(tmp_path):
    from PIL import Image
    root=tmp_path/'output';root.mkdir();features=tmp_path/'input/features.jsonl';features.parent.mkdir()
    source=tmp_path/'source.png';Image.new('L',(100,20),255).save(source)
    buffer=io.BytesIO();Image.new('L',(100,20),255).save(buffer,format='PNG',compress_level=3)
    digest=hashlib.sha256(buffer.getvalue()).hexdigest()
    r=row(crop_source_image=str(source),crop_source_sha256=stage.sha(source),crop_sha256=digest)
    features.write_text(json.dumps(r)+'\n');admitted=tmp_path/'admitted.jsonl';admitted.write_text(json.dumps(dict(r,row_id=r['id']))+'\n')
    # No new crop may be generated below the requested disk floor.
    with patch.object(stage.shutil,'disk_usage',return_value=type('Disk',(),{'free':9_000_000_000})()):
        result=stage.stage(admitted,features,root/'crops',extend=True,minimum_free_gb=10)
    assert result['disk_deferred']==1 and result['new_count']==0
    assert not list(root.rglob('*.png'))
    result=stage.stage(admitted,features,root/'crops',extend=True,minimum_free_gb=0)
    target=root/'crops/nlg/test-l0001.png'
    assert stage.sha(target)==digest
    assert result['new_count']==1
    other=tmp_path/'empty.jsonl';other.write_text('')
    stage.stage(other,features,root/'crops',extend=True,minimum_free_gb=10)
    manifest=[json.loads(l) for l in (root/'crops_manifest.jsonl').read_text().splitlines()]
    assert len(manifest)==1 and manifest[0]['admitted'] is True
    assert stage.sha(target)==digest


def test_whole_builder_repeat_and_gazette_subset(tmp_path):
    snapshots=tmp_path/'snapshots';snapshots.mkdir();out=tmp_path/'out';out.mkdir()
    values=[row(id='nlg-l0001'),row(id='gaz-l0001',source='gazette_modern',primary_class='modern_scanned',gazette_stratum='measured_1986_1990')]
    p=snapshots/'W2_features_20261018_0524.jsonl'
    p.write_text(''.join(json.dumps(r)+'\n' for r in values))
    (snapshots/'SHA256_20261018_0524.txt').write_text(b.sha(p)+'  '+p.name+'\n')
    b.run('W2',[],out=out,snapshots=snapshots)
    before={p.name:p.read_bytes() for p in out.iterdir()}
    b.run('W2',[],out=out,snapshots=snapshots)
    assert before=={p.name:p.read_bytes() for p in out.iterdir()}
    whole=[json.loads(l) for l in (out/'w2_originals_v3_admission.jsonl').read_text().splitlines()]
    gaz=[json.loads(l) for l in (out/'gazette_w2_originals_v3_admission.jsonl').read_text().splitlines()]
    assert gaz==[r for r in whole if r['source']=='gazette_modern']
    assert all(not r['pass'] and r['geometry_unavailable'] for r in whole)
    assert (out/'w2_originals_v3_admitted.jsonl').read_bytes()==b''


def test_unknown_orientation_only_admits():
    d=b.orient.compose_cp5(dict(status='orientation_unknown',rotated=None),
        dict(status='measured',reason=None,union_drop=False),dict(status='measured',drop=False))
    assert d['drop'] is False and not d['geometry_unavailable']
    assert d['verified_keep'] is False


def test_edge_candidate_non_gating_with_unknown_orientation():
    from PIL import Image
    image=Image.new('L',(100,20),255)
    raw=io.BytesIO();image.save(raw,format='PNG',compress_level=3)
    r=row(crop_sha256=hashlib.sha256(raw.getvalue()).hexdigest())
    axis=dict(status='orientation_unknown',rotated=None)
    structural=dict(status='measured',reason=None,merged=False,neighbour_drop=False,union_drop=False)
    context=dict(image=image,regions=[],separators=dict(boundaries=[]))
    with patch.object(__import__('greekocr.harvest.qualified_admission',fromlist=['x']),'neighbour_word_evidence',return_value=structural), \
         patch.object(b.orient,'observe_orientation',return_value=axis), \
         patch.object(b.orient,'inherit_regional_axis',return_value=axis), \
         patch.object(b.orient,'column_crossings',return_value=dict(status='measured',drop=False)), \
         patch.object(__import__('greekocr.harvest.qualified_admission',fromlist=['x']),'edge_diagnostic',return_value=dict(status='measured',candidate=True)):
        d=b.compose(r,20,dict(binding={}),context,.04)
    assert d['edge_clip_candidate'] is True and d['orientation_unknown'] is True
    assert d['pass'] is True and d['rules_failed']==[]
