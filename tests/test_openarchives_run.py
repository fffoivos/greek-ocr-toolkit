"""T24c offline operational boundaries: disk, scale, stream, holdout and O5."""
from collections import Counter
import json
from types import SimpleNamespace
from pathlib import Path
import pytest
from PIL import Image
import pypdfium2 as pdfium
from greekocr.harvest import openarchives as policy
from scripts.harvest import openarchives as run
from scripts.harvest import openarchives_outputs as output


def books(repos=20,each=20):
    return [dict(book=f'{r:03}-{n:03}',key=f'{r:03}-{n:03}',collection_slug=f'r{r:03}',type=('thesis','article')[n%2],
        title='test',year=1990+n%3*10,decade=1990+n%3*10) for r in range(repos) for n in range(each)]


@pytest.mark.parametrize('repos,cap',[(20,10),(10,20),(5,30)])
def test_cap_escalation_only_when_130_cannot_fit(repos,cap):
    rows=books(repos,40);draw,used=policy.capped_draw(rows)
    assert used==cap and len(draw)==min(173,repos*cap)
    assert max(Counter(r['collection_slug'] for r in draw).values())<=cap
    assert draw==policy.capped_draw(rows[::-1])[0]


def test_nulls_and_unmatched_url_do_not_need_external_success(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    ext=tmp_path/'links.parquet';docs=tmp_path/'doc_metadata.jsonl'
    pq.write_table(pa.Table.from_pylist([dict(collection_slug='elsewhere',pdf_links_json='https://x.invalid/old.pdf',edm_url='',status_code=404)]),ext)
    row=dict(source_metadata=dict(collection_slug='r',filename='x',pdf_links_json='https://x.invalid/new.pdf'),
        pipeline_metadata=dict(download_success=True,ocr_success=True,filter='ok',is_empty=False,percentage_greek=80,page_count=20,
            greek_badness_score=None,mojibake_badness_score=None))
    docs.write_text(json.dumps(row)+'\n');pool,_,receipt=policy.build_pool(ext,docs)
    assert len(pool)==1 and pool[0]['earlier_status_code'] is None and receipt['join_coverage']==0


def test_disk_abort_writes_report_without_deleting_data(monkeypatch,tmp_path):
    monkeypatch.setattr(run,'OUT',tmp_path)
    monkeypatch.setattr(run.shutil,'disk_usage',lambda p:SimpleNamespace(free=4*2**30-1))
    with pytest.raises(run.LowDisk):run.disk_check()
    assert json.loads((tmp_path/'disk_abort.json').read_text())['status']=='aborted_low_disk'
    monkeypatch.setattr(run.shutil,'disk_usage',lambda p:SimpleNamespace(free=4*2**30))
    assert run.disk_check()==4*2**30


@pytest.mark.parametrize('size',[(612,792),(1440,2160),(720,300)])
def test_render_caps_native_pixels_and_keeps_frame(tmp_path,size):
    doc=pdfium.PdfDocument.new();page=doc.new_page(*size)
    try:
        image,receipt=run.render_page(page,tmp_path/'page.png')
        assert image.mode=='L' and max(image.size)<=3500
        assert receipt['native_page_points']==list(size)
        assert receipt['render_scale_factor']==pytest.approx(receipt['effective_dpi']/200)
        assert receipt['coordinate_frame']=='rendered PNG' and receipt['png_compress_level']==6
        if max(size)*200/72>3500:assert receipt['render_scale_factor']<1
        else:assert receipt['render_scale_factor']==1
    finally:page.close();doc.close()


def test_strip_every_image_before_persisting_without_touching_geometry():
    raw=dict(document=dict(text='abc',pages=[dict(image=dict(content='BIG',width=10,height=20),lines=[1]),dict(image=dict(content='BIG2'))]))
    stripped=run.strip_response_images(raw)
    assert all('content' not in p['image'] for p in stripped['document']['pages'])
    assert stripped['document']['pages'][0]['image']==dict(width=10,height=20)
    assert stripped['document']['pages'][0]['lines']==[1]
    assert stripped['content_stripped']['page_images_removed']==2


class Response:
    def __init__(self,data,code=200,headers=None):self.data=data;self.status_code=code;self.headers=headers or {};self.is_redirect=code in (301,302)
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def raise_for_status(self):pass
    def iter_content(self,n):yield self.data


def fake_http(monkeypatch,tmp_path,responses):
    monkeypatch.setattr(run,'BULK',tmp_path);monkeypatch.setattr(run,'disk_check',lambda:10*2**30)
    http=run.DirectHTTP();calls=[]
    def get(url,**kwargs):calls.append(url);return responses.pop(0)
    monkeypatch.setattr(http.session,'get',get)
    return http,calls


def test_stream_rejects_size_from_header_and_removes_partial(monkeypatch,tmp_path):
    http,calls=fake_http(monkeypatch,tmp_path,[Response(b'',headers={'Content-Length':str(policy.MAX_PDF+1)})])
    with pytest.raises(ValueError,match='pdf_size_limit'):http.download('https://r.invalid/a.pdf',tmp_path/'a.pdf')
    assert len(calls)==1 and not (tmp_path/'a.part').exists() and not (tmp_path/'a.pdf').exists()


def test_stream_rejects_size_while_reading(monkeypatch,tmp_path):
    monkeypatch.setattr(policy,'MAX_PDF',8)
    http,_=fake_http(monkeypatch,tmp_path,[Response(b'%PDF-123456')])
    with pytest.raises(ValueError,match='pdf_size_limit'):http.download('https://r.invalid/a.pdf',tmp_path/'a.pdf')
    assert not (tmp_path/'a.part').exists()


def test_stream_records_redirect_and_pdf_digest(monkeypatch,tmp_path):
    http,calls=fake_http(monkeypatch,tmp_path,[Response(b'',302,{'Location':'https://other.invalid/b.pdf'}),Response(b'%PDF-small')])
    receipt=http.download('https://r.invalid/a.pdf',tmp_path/'a.pdf')
    assert len(calls)==2 and receipt['sha256']==run.sha(tmp_path/'a.pdf') and receipt['bytes']==10
    rows=run.read_jsonl(tmp_path/'http/requests.jsonl');assert [r['status'] for r in rows]==[302,200]


def test_stream_refuses_html_and_never_leaves_pdf(monkeypatch,tmp_path):
    http,_=fake_http(monkeypatch,tmp_path,[Response(b'<html>not a pdf')])
    with pytest.raises(ValueError,match='not_pdf'):http.download('https://r.invalid/a.pdf',tmp_path/'a.pdf')
    assert not (tmp_path/'a.pdf').exists() and not (tmp_path/'a.part').exists()


def test_holdout_uses_acquired_documents_and_is_repository_disjoint():
    selected,_=policy.capped_draw(books());downloaded=selected[20:150]
    held=policy.holdout(downloaded)
    assert len(held)==20 and Counter(r['split'] for r in held)=={'test':15,'dev':5}
    assert {r['book_key'] for r in held}<={r['key'] for r in downloaded}
    assert len({r['collection_slug'] for r in held})==20


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0e9016f70; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_admission_checks_prior_holdouts_and_retains_metadata_repository():
    def row(ident,text):
        return dict(id=ident,page_id='p',book_key='b',year=2000,decade=2000,confidence=.99,bbox=[0,0,500,30],source='openarchives_r',licence=policy.LICENCE,
            source_url='https://r.invalid/x',attribution='r',read_batch='openarchives',collection_slug='r',docai_text=text,flags=[])
    prior=[dict(id='old',label='Αυτή είναι δοκιμή',split='test',source='old')]
    kept,rejected,_,_,_=output.admit_records([row('a','Αυτή είναι δοκιμή'),row('b','Εδώ γράφουμε άλλο κείμενο')],[],prior)
    assert [r['id'] for r in kept]==['b'] and kept[0]['collection_slug']=='r'
    assert rejected[0]['id']=='a' and rejected[0]['reasons']==['label_in_holdout']


def test_compiled_path_uses_metadata_repository_and_unknown_year():
    assert str(output.compiled_path(dict(collection_slug='r',year=None,title='A/B',key='12345678',page=6)))=='r/unknown_A B_123456/p0006.jpg'


def test_docai_strips_before_raw_cache_and_reuses_sha_once(monkeypatch,tmp_path):
    from tests.test_docai import Credentials
    binding=dict(project='test',location='eu',processor='test',version='test',user_project='test',
        options=dict(ocrConfig=dict(enableSymbol=True,hints=dict(languageHints=['el']))))
    reader=run.OpenArchivesReaders(dict(binding=binding,cap_usd=3,max_calls=1560),root=tmp_path/'google')
    assert reader.budget.max_calls==1560 and not hasattr(reader,'vision')
    reader.docai._credentials=Credentials();calls=[]
    def post(*args,**kwargs):
        calls.append(1)
        return SimpleNamespace(status_code=200,headers={},json=lambda:dict(document=dict(text='',pages=[dict(image=dict(content='BIG',width=20,height=20))])))
    monkeypatch.setattr(run.requests,'post',post);monkeypatch.setattr(run,'disk_check',lambda:10*2**30)
    path=tmp_path/'page.png';Image.new('L',(20,20),255).save(path)
    first=reader.call('docai',path);second=reader.call('docai',path)
    assert first==second and first['status']=='ok' and len(calls)==1
    raw=json.loads(Path(first['raw_json_path']).read_text())
    assert raw['document']['pages'][0]['image']==dict(width=20,height=20) and raw['content_stripped']['page_images_removed']==1
    assert len(run.read_jsonl(tmp_path/'google/budget.jsonl'))==1
    with pytest.raises(ValueError,match='forbids'):reader.call('vision',path)
