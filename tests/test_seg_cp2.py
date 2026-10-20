"""CP2 cache-hit, provenance and abstention contracts; no detection/reading."""
import builtins
import gzip
import hashlib
import json
from pathlib import Path
from tests._paths import ADMISSION

import numpy as np
import pytest
from PIL import Image
from scipy import ndimage as ndi
from greekocr.glyphs import foreign_ink
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.admission import evaluate, evaluate_rows
from greekocr.harvest.neighbour_words import measure_rows, page_measurements


def line(i, centre):
    r = dict(row_id=f'row-{i:05}', column_id='col-0', block_id='block-0', x0=0, x1=100,
             xheight=10., component_ids=[i+1], owned_box=[10,centre-5,18,centre+5],
             neighbours=dict(above=None, below=None))
    for key, offset in [('baseline',5),('meanline',-5),('font_top',-8),('font_bottom',8),
                        ('accent_top',-10),('accent_bottom',10),('top',-12),('bottom',12)]:
        r[key] = [centre+offset]*100
    return r


@pytest.fixture
def cached(tmp_path):
    source = tmp_path/'native.png'
    pixels=np.full((90,100),255,np.uint8)
    for centre in (20,45,70): pixels[centre-5:centre+5,10:18]=0
    Image.fromarray(pixels).save(source)
    prepared=foreign_ink.prepare_mask_page(Image.fromarray(pixels))
    cache=tmp_path/'cache'/'page';cache.mkdir(parents=True)
    rows=[line(i,c) for i,c in enumerate((20,45,70))]
    data=dict(schema=g.SCHEMA,image_size=[100,90], rows=rows,
              structure_rows=[dict(id=r['row_id'],column_id='col-0',block_id='block-0') for r in rows])
    (cache/'detector.json.gz').write_bytes(gzip.compress(json.dumps(data).encode()))
    Image.fromarray(prepared.ink).save(cache/'ink.png')
    np.savez_compressed(cache/'labels.npz',labels=prepared.labels)
    receipt=dict(schema=g.SCHEMA,source=str(source),source_sha256=g.sha(source),
                 detector_sha256=g.code_identity(g.COLLECTOR/'greekocr'), options=g.OPTIONS,
                 row_ink_source='detector_assigned_components')
    for name,key in [('detector.json.gz','geometry_sha256'),('ink.png','mask_sha256'),('labels.npz','labels_sha256')]:
        receipt[key]=g.sha(cache/name)
    (cache/'receipt.json').write_text(json.dumps(receipt))
    run=tmp_path/'run';(run/'W1/pages').mkdir(parents=True)
    (run/'W1/pages/page.json').write_text(json.dumps(dict(id='page',status='completed',image=str(source),image_sha256=g.sha(source))))
    return source,cache,rows,run


def load(cached):
    source,cache,_,_=cached
    return g.load_cached_page(source,cache,g.sha(source))


def test_cache_admission_no_detector_no_writes(cached,monkeypatch):
    import greekocr.pages
    calls=[]
    def forbidden(*a,**kw):
        calls.append(1);raise AssertionError('detector called')
    monkeypatch.setattr(greekocr.pages,'process_page',forbidden)
    before={str(p):g.sha(p) for p in cached[0].parent.rglob('*') if p.is_file()}
    original_open=builtins.open
    def readonly(file,mode='r',*a,**kw):
        assert not any(c in mode for c in 'wax+'), (file,mode)
        return original_open(file,mode,*a,**kw)
    monkeypatch.setattr(builtins,'open',readonly)
    for method in ('write_text','write_bytes','mkdir','touch','unlink','rename','replace'):
        monkeypatch.setattr(Path,method,forbidden)
    row=dict(row_id='crop', page_id='page',crop_bbox=[0,35,100,55],geometry_row_id='row-00001',
             label='ἑλληνικὸς πλήρης λόγος',source='bsb_poly1850',primary_class='poly1850',
             image_sha256=g.sha(cached[0]), crop_source_image=str(cached[0]))
    measurement=page_measurements([row],run_root=cached[3],cache=cached[1].parent)['crop']
    assert measurement['matched'] and measurement['target_row_id']=='row-00001'
    result=list(evaluate_rows([row],run_root=cached[3],neighbour_cache=cached[1].parent))[0]
    assert result['status']=='unresolved' and not result['passed'] # CP4 not qualified
    assert not calls
    assert before=={str(p):g.sha(p) for p in cached[0].parent.rglob('*') if p.is_file()}


@pytest.mark.parametrize('field,value', [('source_sha256','bad'),('source','/tmp/other/native.png'),
    ('detector_sha256','bad'),('options',{}),('row_ink_source','ribbon')])
def test_stale_receipt(cached,field,value):
    p=cached[1]/'receipt.json';r=json.loads(p.read_text());r[field]=value;p.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='stale'):load(cached)


@pytest.mark.parametrize('name',['detector.json.gz','ink.png','labels.npz'])
def test_corrupt_payload(cached,name):
    p=cached[1]/name;p.write_bytes(p.read_bytes()+b'corrupt')
    with pytest.raises(ValueError,match='corrupt'):load(cached)


@pytest.mark.parametrize('change',['frame','fields','structure','components','duplicate'])
def test_invalid_geometry(cached,change):
    p=cached[1]/'detector.json.gz';d=json.loads(gzip.decompress(p.read_bytes()))
    if change=='frame':d['image_size']=[90,100]
    if change=='fields':del d['rows'][0]['neighbours']
    if change=='structure':d['rows'][0]['column_id']='wrong'
    if change=='components':d['rows'][0]['component_ids']=[999]
    if change=='duplicate':d['structure_rows'].append(d['structure_rows'][0])
    p.write_bytes(gzip.compress(json.dumps(d).encode()))
    rp=cached[1]/'receipt.json';r=json.loads(rp.read_text());r['geometry_sha256']=g.sha(p);rp.write_text(json.dumps(r))
    with pytest.raises(ValueError):load(cached)


def test_row_stability_ambiguity_missing_neighbour(cached):
    page=load(cached)
    assert [r['row_id'] for r in page['rows']]==[r['row_id'] for r in cached[2]]
    assert page['rows'][1]['component_ids']==[2]
    assert g.observe_crop(page,[0,0,100,90])['reason']=='ambiguous_target'
    assert g.observe_crop(page,[50,0,100,90])['reason']=='missing_target'
    m=g.observe_crop(page,[0,0,100,90],target_row_id='row-00001')
    assert m['native_foreign_component_ids']==[1,3]
    assert [r['xheight'] for r in m['neighbours']]==[10,10]
    page['rows']=page['rows'][1:2]
    assert g.observe_crop(page,[0,35,100,55])['reason']=='missing_neighbour'


@pytest.mark.parametrize('box',[[0,0,100,90],[0,20,100,60],[0,10,100,70]])
def test_exact_frozen_masks_and_immutable_inputs(cached,box):
    source,cache,rows,_=cached
    image=Image.open(source);prepared=foreign_ink.prepare_mask_page(image)
    original=image.tobytes();labels=prepared.labels.copy();before=g.sha(source)
    expected=foreign_ink._foreign_mask(prepared.ink,foreign_ink._centre_fit(rows[1]),
                                      [foreign_ink._centre_fit(r) for r in (rows[0],rows[2])],tuple(box))
    actual=g.measure_foreign(prepared,rows[1],[rows[0],rows[2]],box)
    assert np.array_equal(expected,actual['mask'])
    assert image.tobytes()==original and g.sha(source)==before
    assert np.array_equal(labels,prepared.labels) and prepared.fills=={}


@pytest.mark.parametrize('measurement',[None,dict(matched=False),dict(matched=True),
    dict(matched=True,xheight=10),dict(status='unavailable',matched=True),
    dict(matched=True,decision_status='unqualified_cp2',components=[],xheight=10)])
def test_unavailable_never_verified_keep(measurement):
    result=evaluate(dict(label='ἑλληνικὸς πλήρης λόγος',source='bsb_poly1850',primary_class='poly1850'),neighbour_measurement=measurement)
    assert not result['passed'] and result['status']=='fail'
    assert result['checks']['neighbour_words']=='n/a'


def test_missing_fields_not_skipped():
    result=measure_rows([dict(row_id='missing')])
    assert result['missing']['reason']=='missing_record_fields'


def test_full_detector_identity_matches_vendor():
    import importlib.util
    path=g.COLLECTOR/'collect_v3/vendor/geometry/io.py'
    spec=importlib.util.spec_from_file_location('_cp2_vendor_io',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.detector_identity()==g.code_identity(g.COLLECTOR/'greekocr')


def test_code_change_rejects_cache(cached,monkeypatch):
    original=g.code_identity
    monkeypatch.setattr(g,'code_identity',lambda root: '0'*64 if Path(root)==g.COLLECTOR/'greekocr' else original(root))
    with pytest.raises(ValueError,match='stale'):load(cached)


def test_source_bytes_change_rejected(cached):
    expected=g.sha(cached[0])
    cached[0].write_bytes(cached[0].read_bytes()+b'changed')
    with pytest.raises(ValueError,match='stale'):
        g.load_cached_page(cached[0],cached[1],expected)


def test_missing_cache_abstains_without_preparation(cached):
    (cached[1]/'receipt.json').unlink()
    rows=[dict(row_id='crop',page_id='page',crop_bbox=[0,35,100,55])]
    observed=measure_rows(rows,run_root=cached[3],cache=cached[1].parent)['crop']
    assert observed['status']=='unavailable' and not observed['matched']
    assert not (cached[1]/'receipt.json').exists()


def test_missing_neighbour_never_verified_clean(cached):
    page=load(cached);page['rows']=page['rows'][1:2]
    m=g.observe_crop(page,[0,35,100,55])
    r=evaluate(dict(label='ἑλληνικὸς πλήρης λόγος',source='bsb_poly1850',primary_class='poly1850'),neighbour_measurement=m)
    assert m['reason']=='missing_neighbour' and not r['passed']


def test_multiframe_source_is_ambiguous(cached):
    source=cached[0].with_suffix('.tiff')
    im=Image.new('L',(100,90),255)
    im.save(source,save_all=True,append_images=[im])
    rp=cached[1]/'receipt.json';r=json.loads(rp.read_text())
    r.update(source=str(source),source_sha256=g.sha(source));rp.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='ambiguous_source_frame'):
        g.load_cached_page(source,cached[1],g.sha(source))


def test_stale_saved_cp1_report_still_blocks():
    import importlib.util
    path=ADMISSION / 'nw1b/calibrate.py'
    spec=importlib.util.spec_from_file_location('_cp2_calibration',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    with pytest.raises(m.QualificationError,match='stale/inconsistent'):
        m.require_qualification()


# Review H1's exact independently reproduced boundary bypasses.
H1_MEASUREMENTS = [
    dict(matched=True, xheight=10., components=[]),
    dict(matched=True, xheight=10., components=[], status='stale',
         binding={'source_sha256': 'wrong'}),
    dict(matched=True, xheight=10., components=[], decision_status='unresolved'),
]


def eligible(**fields):
    return dict(label='ἑλληνικὸς πλήρης λόγος', source='bsb_poly1850',
                primary_class='poly1850', **fields)


@pytest.mark.parametrize('measurement', H1_MEASUREMENTS)
def test_h1_review_inputs_abstain_and_never_call_f2(measurement, monkeypatch):
    from greekocr.harvest import neighbour_words
    def forbidden(*args, **kwargs):
        raise AssertionError('legacy F2 must never be an admission predicate')
    monkeypatch.setattr(neighbour_words, 'runs', forbidden)
    r = evaluate(eligible(), neighbour_measurement=measurement)
    assert not r['passed'] and not r['rules_passed']
    assert r['status'] == 'fail' and r['geometry_status'] == 'unavailable'
    assert r['checks']['neighbour_words'] == 'n/a' and r['failed_rules'] == ['geometry_unavailable']


@pytest.mark.parametrize('status', [None, 'stale', 'unavailable', 'unresolved', 'available', 'pass', 'legacy'])
@pytest.mark.parametrize('decision', [None, 'unresolved', 'unqualified_cp2', 'qualified'])
def test_positive_tag_cannot_rescue_unavailable_or_legacy(status, decision):
    r = evaluate(eligible(), neighbour_measurement=dict(matched=True, xheight=10.,
                 components=[], status=status, decision_status=decision, binding={}))
    assert r['status'] == 'fail' and not r['passed']
    assert r['geometry_status'] == 'unavailable'


@pytest.mark.parametrize('decision', [None, 'unresolved', 'stale', 'unqualified_cp2', 'unknown'])
def test_measured_requires_positive_qualification(cached, decision):
    row, m = bound_case(cached)
    m['decision_status'] = decision
    r = evaluate(row, neighbour_measurement=m)
    assert not r['passed'] and r['geometry_status'] == 'unresolved'
    assert r['geometry_reason'] == 'unqualified_measurement'


def bound_case(cached):
    m = g.observe_crop(load(cached), [0,35,100,55], target_row_id='row-00001')
    m['decision_status'] = 'qualified'  # Caller claim, never a CP2 certificate.
    row = eligible(row_id='crop', page_id='page', image_sha256=g.sha(cached[0]),
                   crop_source_image=str(cached[0]), crop_bbox=[0,35,100,55],
                   geometry_row_id='row-00001')
    return row, m


@pytest.mark.parametrize('change', ['missing', 'empty', 'source', 'code', 'geometry',
    'receipt', 'source_bytes', 'payload_bytes', 'crop', 'target', 'record_source',
    'record_sha', 'page', 'foreign_pixels'])
def test_claimed_qualification_requires_current_full_binding(cached, change):
    row, m = bound_case(cached)
    if change == 'missing': del m['binding']
    elif change == 'empty': m['binding'] = {}
    elif change == 'source': m['binding']['source_sha256'] = '0'*64
    elif change == 'code': m['binding']['admission_adapter_sha256'] = '0'*64
    elif change == 'geometry': m['binding']['cache_receipt']['geometry_sha256'] = '0'*64
    elif change == 'receipt': m['binding']['receipt_sha256'] = '0'*64
    elif change == 'source_bytes': cached[0].write_bytes(cached[0].read_bytes()+b'stale')
    elif change == 'payload_bytes': (cached[1]/'labels.npz').write_bytes(b'corrupt')
    elif change == 'crop': row['crop_bbox'] = [0,34,100,55]
    elif change == 'target': row['geometry_row_id'] = 'row-00002'
    elif change == 'record_source': row['crop_source_image'] = str(cached[0].with_name('other.png'))
    elif change == 'record_sha': row['image_sha256'] = '0'*64
    elif change == 'page': row['page_id'] = 'other-page'
    elif change == 'foreign_pixels': m['foreign_pixels'] += 1
    r = evaluate(row, neighbour_measurement=m)
    assert not r['passed'] and r['status'] == 'fail'
    assert r['geometry_status'] == 'unavailable'


def test_valid_geometry_and_claimed_qualification_still_not_cp2_authority(cached, monkeypatch):
    from greekocr.harvest import neighbour_words
    row, m = bound_case(cached)
    def forbidden(*args, **kwargs):
        raise AssertionError('F2 called')
    monkeypatch.setattr(neighbour_words, 'runs', forbidden)
    r = evaluate(row, neighbour_measurement=m)
    assert not r['passed'] and r['rules_passed']
    assert r['geometry_status'] == 'unresolved'
    assert r['geometry_reason'] == 'qualification_not_supported_cp2'


def test_h1_receipt_counts_all_boundary_abstentions(tmp_path, monkeypatch, cached):
    from greekocr.harvest import neighbour_words
    from greekocr.harvest.admission import run_files
    row, m = bound_case(cached)
    observations = H1_MEASUREMENTS + [dict(m, decision_status='unqualified_cp2'), m]
    rows = [dict(row, row_id=f'r{i}') for i in range(len(observations))]
    monkeypatch.setattr(neighbour_words, 'measure_rows',
                        lambda records, **kw: {r['row_id']: m for r,m in zip(records, observations)})
    p = tmp_path/'h1.jsonl'
    p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt = run_files([p], output_dir=tmp_path/'out')
    assert receipt['rows_pass'] == 0 and receipt['rows_total'] == 5
    assert receipt['neighbour_words_unavailable'] == 5
    assert receipt['neighbour_words_unmatched'] == 3
    assert receipt['neighbour_words_status_counts'] == {'unavailable':3, 'unresolved':2}
    # CP7 counting hook: overlapping rule losses by source x class. No real
    # admission file is evaluated here; only this five-row temporary fixture.
    assert receipt['drops_per_rule']['geometry_unavailable'] == 3
    assert receipt['drops_per_source_class']['bsb_poly1850|poly1850']['geometry_unavailable'] == 3
    assert sum(receipt['neighbour_words_reason_counts'].values()) == 5
    assert all(not json.loads(l)['pass'] for l in (tmp_path/'out/h1_admission.jsonl').read_text().splitlines())
    assert (tmp_path/'out/h1_admitted.jsonl').read_bytes() == b''
