"""T10 offline contracts: no ADC and no live requests."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from prototypes.harvest.google_failed_lines import (
    cached_response, characters_table, crop_metrics, derive_comment_crops,
    is_anemi, load_catalogues, sha256, summarise,
)
from greekocr.readers.services.google_docai import DocAIReader, DEFAULT_VERSION

FIXTURE = Path(__file__).parent / 'data/docai_failed_lines'


def sample():
    return json.loads((FIXTURE / 'response.json').read_text())


def test_parses_both_catalogues_only_current_output_items():
    rows=load_catalogues(FIXTURE)
    assert len(rows)==3
    assert [r['catalogue_file'] for r in rows]==['controls_owner_marked.json','multi_line_segments.json','multi_line_segments.json']
    assert rows[0]['failure_type']=='control_owner_verified'
    assert rows[1]['r7_status']=='not fixed'
    assert rows[1]['expected_ocr_risk']=='two lines'
    assert rows[0]['width_px']==100 and rows[0]['height_px']==20
    assert rows[0]['crop_sha256']==sha256(Path(rows[0]['crop_path']))
    assert rows[2]['status']=='withheld_anemi'


@pytest.mark.parametrize('page,path,excluded',[
    ('an-page','crops/s2-file.png',True),
    ('s2-page','crops/an-file.png',True),
    ('ia-page','crops/ia-file.png',False),
    ('s2-page','crops/s2-file.png',False),
])
def test_anemi_exclusion_checks_both_page_and_filename(page,path,excluded):
    assert is_anemi(page,path)==excluded


def test_anemi_never_reaches_reader_even_with_cached_response(tmp_path):
    row=load_catalogues(FIXTURE)[2]
    class Forbidden:
        def binding(self):
            pytest.fail('Anemi must be rejected before reader access')
    with pytest.raises(ValueError,match='Anemi is withheld'):
        cached_response(row,tmp_path,Forbidden())


def test_metrics_from_stored_sample_response():
    result=crop_metrics(sample(),100,20)
    assert result['lines_returned']==1
    assert result['text_per_line']==['ἅλφα β']
    assert result['line_confidences']==[.88]
    assert result['total_characters']==6
    assert result['characters_per_100px_width']==6
    assert result['mean_symbol_confidence']==pytest.approx(.7)
    assert result['min_symbol_confidence']==.5
    assert result['symbol_count']==5 and not result['empty']
    assert set(result['greek_characters'])==set('ἅλφαβ')


def test_layout_line_count_is_not_newline_count():
    raw=sample()
    raw['document']['pages'][0]['lines']=[
        {'layout':{'textAnchor':{'textSegments':[{'endIndex':'5'}]}}},
        {'layout':{'textAnchor':{'textSegments':[{'startIndex':'5','endIndex':'7'}]}}},
    ]
    result=crop_metrics(raw,100,20)
    assert result['lines_returned']==2 and result['text_per_line']==['ἅλφα ','β']


def test_empty_response_metrics_preserve_absent_confidence():
    raw={'document':{'text':'','pages':[{'lines':[]}]}}
    result=crop_metrics(raw,10,4)
    assert result['empty'] and result['lines_returned']==0
    assert result['total_characters']==0 and result['mean_symbol_confidence'] is None


def test_character_tables_raw_nfd_sources_and_sha_deduplication():
    rows=[dict(status='ok',crop_sha256='a',source='Vouli',text='ἅϗϲͅ\n'),
          dict(status='ok',crop_sha256='a',source='Vouli',text='ἅϗϲͅ\n'),
          dict(status='ok',crop_sha256='b',source='Internet Archive',text='ȣά\n'),
          dict(status='withheld_anemi',crop_sha256='c',source='Anemi',text='ϛ')]
    table=characters_table(rows)
    assert table['ALL']['n_calls']==2
    assert table['ALL']['character_counts']['ϗ']==1
    assert table['ALL']['requested_characters']['ϗ']['appeared']
    assert table['ALL']['requested_characters']['ϛ']['raw_count']==0
    assert table['Vouli']['character_counts']['ϲ']==1
    assert table['Internet Archive']['character_counts']['ȣ']==1
    assert table['ALL']['nfd_marks_on_greek']['\u0314']==1
    assert table['ALL']['nfd_marks_on_greek']['\u0301']==2
    assert table['ALL']['nfd_combining_marks']['\u0345']==1
    assert 'Anemi' not in table


def test_cache_once_and_identical_bytes_reuse_no_auth(tmp_path,monkeypatch):
    class Credentials:
        calls=0
        def before_request(self,*args):
            self.calls+=1
    credentials=Credentials()
    calls=[]
    def transport(*args,**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=200,headers={},json=sample,text='')
    reader=DocAIReader('fixture','eu','processor',DEFAULT_VERSION,receipts_dir=tmp_path/'adapter',credentials=credentials,transport=transport)
    rows=load_catalogues(FIXTURE)
    a=cached_response(rows[0],tmp_path,reader)
    assert len(calls)==1
    assert calls[0]['json']['processOptions']=={'ocrConfig':{'enableSymbol':True,'hints':{'languageHints':['el']}}}
    assert cached_response(rows[0],tmp_path,reader,offline=True)==a
    b=cached_response(rows[1],tmp_path,reader,offline=True)
    assert b['receipt_id']==a['receipt_id']
    assert len(calls)==credentials.calls==1
    path=tmp_path/'responses'/f"{rows[0]['crop_id']}.json"
    data=json.loads(path.read_text()); data['crop_sha256']='changed';path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='mismatch'):
        cached_response(rows[0],tmp_path,reader)
    assert len(calls)==1


def test_billing_permission_error_stops_and_cannot_be_retried(tmp_path):
    class Credentials:
        def before_request(self,*args):pass
    calls=[]
    def transport(*args,**kwargs):
        calls.append(1)
        return SimpleNamespace(status_code=403,headers={},json=lambda:{'error':{'status':'PERMISSION_DENIED','message':'billing disabled'}},text='')
    reader=DocAIReader('fixture','eu','processor',DEFAULT_VERSION,receipts_dir=tmp_path/'adapter',credentials=Credentials(),transport=transport)
    row=load_catalogues(FIXTURE)[0]
    with pytest.raises(Exception,match='HTTP 403'):
        cached_response(row,tmp_path,reader)
    with pytest.raises(ValueError,match='refusing automatic re-call'):
        cached_response(row,tmp_path,reader)
    assert len(calls)==1


def test_response_hash_change_rejected(tmp_path):
    row=load_catalogues(FIXTURE)[0]
    reader=DocAIReader('fixture','eu','processor',DEFAULT_VERSION,receipts_dir=tmp_path/'adapter')
    path=tmp_path/'responses'/f"{row['crop_id']}.json";path.parent.mkdir()
    path.write_text(json.dumps(dict(crop_sha256=row['crop_sha256'],binding=reader.binding(),response=sample(),response_sha256='wrong')))
    with pytest.raises(ValueError,match='envelope changed'):
        cached_response(row,tmp_path,reader,offline=True)


def test_exposure_rule_uses_control_p05_and_retains_silent_candidates():
    rows=[]
    for conf,kind,n,empty in [(.9,'control_owner_verified',1,False),(.95,'control_owner_verified',1,False),(.91,'multi_line_segment',1,False),(.95,'multi_line_segment',2,False),(.7,'curl_end_cut',1,False),(None,'blob_boxed',0,True)]:
        rows.append(dict(status='ok',failure_type=kind,failure_types=[kind],crop_sha256=str(len(rows)),mean_symbol_confidence=conf,min_symbol_confidence=conf,characters_per_100px_width=4,lines_returned=n,empty=empty))
    result=summarise(rows,['multi_line_segment','curl_end_cut','blob_boxed'])
    assert result['types']['multi_line_segment']['silent_candidate_count']==1
    assert result['types']['multi_line_segment']['exposed_count']==1
    assert result['types']['curl_end_cut']['exposed_count']==1
    assert result['types']['blob_boxed']['empty_rate']==1


def comment_catalogue(tmp_path):
    import shutil
    root=tmp_path/'source'
    directory=root/'.astra/fast_lines/out/stack/r7/failed_lines'
    shutil.copytree(FIXTURE,directory)
    r7=directory.parent
    r6=r7.with_name('r6');r6.mkdir()
    page='s2-fixture-p00001'
    effect={'curl_end_cut':'last words omitted'}
    comment=dict(id='O02',page=page,failure_types=['curl_end_cut'],owner_words='last chars for 13 14 18',r7_status='not fixed',observation='synthetic curled ends')
    (directory/'page_comments.json').write_text(json.dumps(dict(effects=effect,records=[comment])))
    (r7/'comments.json').write_text(json.dumps([dict(id='O02',historical_image_source=f'.astra/fast_lines/out/stack/r6/{page}.jpg')]))
    items=[dict(polygon=[[0,0],[99,0],[99,19],[0,19]]) for _ in range(3)]
    page_data=dict(items=items)
    order=[dict(number=n,item_index=i) for i,n in enumerate([13,14,18])]
    for p in [r6,r7]:
        (p/f'{page}.json').write_text(json.dumps(page_data))
        (p/f'{page}.order.json').write_text(json.dumps(order))
    from PIL import Image
    pages=root/'.astra/pages';pages.mkdir(parents=True)
    Image.new('L',(100,20),255).save(pages/f'{page}.png')
    return directory


def test_page_regions_require_exact_historical_geometry_and_order(tmp_path):
    directory=comment_catalogue(tmp_path)
    rows=load_catalogues(directory)
    coverage=derive_comment_crops(directory,rows,tmp_path/'out')
    assert coverage[0]['status']=='exact_R6_region_intersected_with_R7'
    assert len(coverage[0]['bindings'])==3
    assert len(rows)==4  # two matching catalogue items reused, one new current crop
    assert 'curl_end_cut' in rows[0]['failure_types']
    assert rows[-1]['catalogue_file']=='page_comments.json'
    assert len(coverage[0]['bindings'][0]['sources'])==4
    assert coverage[0]['bindings'][0]['intersection'].endswith('1.0')
    p=directory.parent/f"s2-fixture-p00001.order.json"
    data=json.loads(p.read_text());data[0]['number']=99;p.write_text(json.dumps(data))
    rows=load_catalogues(directory)
    coverage=derive_comment_crops(directory,rows,tmp_path/'out')
    assert coverage[0]['status'].startswith('historical_mapping_not_exact')
    assert len(rows)==3


def test_full_run_stops_on_permission_error_and_writes_partial_receipt(tmp_path):
    from prototypes.harvest.google_failed_lines import run
    directory=comment_catalogue(tmp_path)
    class Credentials:
        def before_request(self,*args):pass
    calls=[]
    def transport(*args,**kwargs):
        calls.append(1)
        return SimpleNamespace(status_code=403,headers={},json=lambda:{'error':{'status':'PERMISSION_DENIED'}},text='')
    out=tmp_path/'report'
    reader=DocAIReader('fixture','eu','processor',DEFAULT_VERSION,receipts_dir=out/'docai_failed_lines/adapter_receipts',credentials=Credentials(),transport=transport)
    rec=run(directory,out,reader=reader)
    assert rec['status']=='stopped' and rec['calls']==1 and rec['successful_calls']==0
    assert len(calls)==1
    assert (out/'DOCAI_FAILED_LINES_v1.md').is_file()
    saved=json.loads((out/'docai_failed_lines/receipt.json').read_text())
    assert saved['error_calls']==1
    assert saved['withheld_anemi']==1


def test_recover_saved_successful_empty_parse_error_without_request(tmp_path):
    import hashlib
    from prototypes.harvest.google_failed_lines import canonical
    row=load_catalogues(FIXTURE)[0]
    reader=DocAIReader('fixture','eu','processor',DEFAULT_VERSION,receipts_dir=tmp_path/'adapter',transport=lambda *a,**k:pytest.fail('must not re-call'))
    reader.receipts_dir.mkdir()
    raw_path=reader.receipts_dir/'original.json'
    raw_path.write_text(json.dumps({'document':{'pages':[{'pageNumber':1}]}}))
    metadata=dict(crop_sha256=row['crop_sha256'],binding=reader.binding(),status='error',pages_billed=1,
        raw_json_path=str(raw_path),raw_sha256=sha256(raw_path),receipt_id='original-receipt',request_id=None,
        latency_s=1,error='Document AI response is missing document.text',cached=False)
    reader.ledger_path.write_text(json.dumps(metadata)+'\n')
    attempts=tmp_path/'attempts';attempts.mkdir()
    (attempts/f"{row['crop_sha256']}.json").write_text('{}')
    recovered=cached_response(row,tmp_path,reader)
    assert recovered['receipt_id']=='original-receipt'
    assert 'recovered_adapter_parse_error' in recovered
    assert crop_metrics(recovered['response'],100,20)['empty']
    assert len(reader.ledger_path.read_text().splitlines())==1
    assert cached_response(row,tmp_path,reader,offline=True)==recovered
