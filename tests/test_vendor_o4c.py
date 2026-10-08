"""O4c recorded-fixture replay and adversarial bounds tests. Never contacts the network."""
import hashlib,io,json,sys
from pathlib import Path
from types import SimpleNamespace
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/fetch'))
import greekocr._vendor.scripts.fetch.o4c_common as c
from greekocr._vendor.scripts.fetch.o4c_discover_archive import parse_item
from greekocr._vendor.scripts.fetch.o4c_discover_parliament import parse_record, resolve_files
from greekocr._vendor.scripts.fetch.o4c_discover_anemi import parse_oai, parse_search
from greekocr._vendor.scripts.fetch.o4c_discover_other import parse_nlg, parse_wellcome
from greekocr._vendor.scripts.fetch.o4c_discover_wikimedia import parse_file
F=Path(__file__).resolve().parent/'fixtures/o4c'
def load(name):return json.loads((F/name).read_text())

@pytest.fixture(autouse=True)
def no_live_network(monkeypatch):
    def fail(*a,**kw):pytest.fail('offline test tried network')
    monkeypatch.setattr(c.urllib.request,'build_opener',fail)
    monkeypatch.setattr(c.subprocess,'Popen',fail)

def test_recording_hashes():
    for name,r in load('recordings.json').items():assert hashlib.sha256((F/name).read_bytes()).hexdigest()==r['fixture_sha256']
    r=load('pdf_provenance.json');assert hashlib.sha256((F/'parliament_recorded_page.pdf').read_bytes()).hexdigest()==r['fixture_sha256']

def test_parliament_real_metadata_and_bundles():
    r=parse_record(load('parliament_item.json'))
    assert r['year']==1850 and r['pages']==9 and r['rights']['compatible']
    class Replay:
        def json(self,url):
            return load('parliament_bundles.json' if '/items/' in url else 'parliament_bitstreams.json')
    resolve_files(Replay(),r)
    assert r['size']==2926198 and r['download_url'].endswith('/1e324159-04b6-48b3-bf9a-45999818bc18/content')
    assert r['text_layer']['status']=='unverified'

def test_recorded_pdf_text_and_scan_geometry():
    r=c.row('parliament','fixture','fixture','fixture',rights='CC BY 4.0');r['download_url']='fixture'
    c.probe_pdf(None,r,F/'parliament_recorded_page.pdf')
    assert r['text_layer']['status']=='verified' and r['text_layer']['scan_status']=='verified-large-raster-object'
    assert r['text_layer']['measurement']['chars']==2096 and r['polytonic_ratio']>.14
    assert r['text_layer']['page_indices']==[0] and r['estimated_polytonic_lines']==33

def test_archive_real_greek_metadata_and_text():
    r=parse_item('b28038630',load('archive_greek_metadata.json'))
    assert r['pages']==1806 and r['rights']['family']=='public-domain'
    assert r['download_url'].endswith('.pdf') and r['geometry_url'].endswith('_djvu.xml')
    text=(F/'archive_greek_text.txt').read_text();expected=load('recordings.json')['archive_greek_text.txt']['measurement']
    assert c.metrics(text)==expected
    assert expected['polytonic_ratio']>.05

def test_archive_real_cyrillic_metadata_and_text():
    r=parse_item('tolstojvojnaimirtom_3_4',load('archive_cyrillic_metadata.json'))
    assert r['rights']['family']=='CC0'
    text=(F/'archive_cyrillic_text.txt').read_text();expected=load('recordings.json')['archive_cyrillic_text.txt']['measurement']
    assert c.metrics(text)==expected and expected['cyrillic_ratio']>.5

@pytest.mark.parametrize('rights,compatible',[
 ('CC BY 4.0',True),('https://creativecommons.org/licenses/by-sa/3.0/',True),
 ('https://creativecommons.org/licenses/by-nc/4.0/',False),('CC BY-ND 4.0',False),
 ('Public Domain Mark',True),('Public domain; all rights reserved',False),(None,False)])
def test_licence_filter(rights,compatible):assert c.license_info(rights)['compatible']==compatible

def test_mark_denominator_and_attached_marks():
    a=c.metrics('ἄ ὰ ᾷ α\u0313\u0342 ά ἀ\nРусский')
    assert a['greek_letters']==6 and a['polytonic_letters']==5
    assert c.metrics('ά')['polytonic_letters']==0
    assert c.metrics('\u1f71')['polytonic_letters']==1  # explicitly requested Extended-codepoint diagnostic
    assert c.metrics('᾽ \u0313 A\u0313')['polytonic_letters']==0
    assert c.metrics('α\u0313\u0342')['polytonic_letters']==1

@pytest.mark.parametrize('file,url,allowed',[
 ('commons_robots.txt','https://commons.wikimedia.org/w/api.php?action=query',False),
 ('commons_robots.txt','https://commons.wikimedia.org/wiki/File:Example.pdf',True),
 ('gallica_robots.txt','https://gallica.bnf.fr/services/engine/search/sru?query=gre',False),
 ('gallica_robots.txt','https://gallica.bnf.fr/ark:/12148/xyz/texteBrut',True),
 ('anemi_robots.txt','https://anemi.lib.uoc.gr/search?cclterm1=Greek',True),
 ('anemi_robots.txt','https://anemi.lib.uoc.gr/search?ccl=Greek',False),
 ('anemi_robots.txt','https://anemi.lib.uoc.gr/tools/oai',False)])
def test_recorded_robots(file,url,allowed):assert c.robots_allowed((F/file).read_text(),url)==allowed

def test_robots_longest_allow_and_specific_agent():
    text='User-agent: *\nDisallow: /w/\nAllow: /w/api.php?action=mobileview&\nUser-agent: GreekPageOCR\nDisallow: /private\n'
    assert c.robots_allowed(text,'https://example.org/w/api.php?action=query')
    assert not c.robots_allowed(text,'https://example.org/private')
    assert c.robots_allowed('User-agent: *\nDisallow: /a\nAllow: /ab','https://example.org/abc')

def cache_put(h,url,body,status=200,headers=None,range_header=None):
    key=hashlib.sha256((url+'\n'+str(range_header)).encode()).hexdigest()
    (h.cache/(key+'.body')).write_bytes(body)
    c.write_json(h.cache/(key+'.json'),dict(url=url,status=status,headers=headers or {},sha256=hashlib.sha256(body).hexdigest()))

def test_offline_cache_integrity_and_miss(tmp_path):
    h=c.HTTP('test',offline=True,root=tmp_path)
    cache_put(h,'https://example.org/robots.txt',b'User-agent: *\nDisallow: /private')
    cache_put(h,'https://example.org/test',b'data')
    assert h.get('https://example.org/test')[1]==b'data' and h.requests==0
    with pytest.raises(c.ProbeError,match='robots disallows'):h.get('https://example.org/private')
    with pytest.raises(c.ProbeError,match='offline cache miss'):h.get('https://example.org/missing')
    key=hashlib.sha256(('https://example.org/test\nNone').encode()).hexdigest();(h.cache/(key+'.body')).write_bytes(b'changed')
    with pytest.raises(c.ProbeError,match='cache hash mismatch'):h.get('https://example.org/test')

class RecordedRanges:
    def __init__(self,data):self.data=data;self.requests=[]
    def get(self,url,limit,range_header):
        a,b=map(int,range_header[6:].split('-'));b=min(b,len(self.data)-1);self.requests.append((a,b));data=self.data[a:b+1]
        return {'status':206,'headers':{'content-range':f'bytes {a}-{b}/{len(self.data)}'}},data

def test_pdf_custom_range_callback_replays_recorded_page():
    data=(F/'parliament_recorded_page.pdf').read_bytes();h=RecordedRanges(data)
    r=c.row('parliament','range-fixture','fixture','fixture',rights='CC BY 4.0');r['download_url']='https://example.org/fixture.pdf'
    c.probe_pdf(h,r)
    assert r['text_layer']['status']=='verified' and r['text_layer']['measurement']['chars']==2096
    assert len(h.requests)<=2 and r['text_layer']['probe_bytes']<=len(data)

def test_range_cap_never_falls_back_to_full_file():
    h=RecordedRanges(b'x'*1000);f=c.RangeFile(h,'fixture',max_bytes=128,block=64)
    f.seek(300)
    assert f.read(10)==b'x'*10
    f.seek(900)
    with pytest.raises(c.ProbeError,match='per-document'):f.read(10)
    assert h.requests==[(0,63),(256,319)]

def test_range_ignored_fails_closed():
    class Ignored:
        def get(self,*a,**k):return {'status':200,'headers':{}},b'%PDF'
    with pytest.raises(c.ProbeError,match='support'):c.RangeFile(Ignored(),'fixture')

def test_anemi_standards_is_not_document_rights():
    assert 'OAI-PMH' in (F/'anemi_standards.html').read_text()
    assert parse_search((F/'anemi_standards.html').read_bytes())==[]
    # Protocol resumption edge case is synthetic, clearly separate from real recordings.
    rows,token=parse_oai(b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><ListRecords><resumptionToken>next</resumptionToken></ListRecords></OAI-PMH>')
    assert rows==[] and token=='next'

def test_other_recorded_catalogue_does_not_infer_rights_or_language():
    rows=[parse_wellcome(x) for x in load('wellcome_results.json')['results']]
    assert rows and all(not r['rights']['compatible'] and r['download_url'] is None for r in rows)
    assert parse_nlg(b'<a href="/browse/23">Greek print</a><a href="/browse/23">duplicate</a>','https://example.org') [0]['document_id']=='nlg:23'

def test_wikimedia_parser_is_conservative_without_license():
    # No live imageinfo recording was taken: robots blocks it. Negative schema fixture only.
    r=parse_file({'title':'File:Unverified.djvu','imageinfo':[{'url':'https://example.org/file.djvu','size':50}]},'el')
    assert not r['rights']['compatible'] and r['text_layer']['status']=='unverified'

def test_http_task_budget_and_rate_accounting(tmp_path,monkeypatch):
    now=[100.0];sleeps=[];calls=[]
    monkeypatch.setattr(c.time,'time',lambda:now[0])
    def pause(seconds):sleeps.append(seconds);now[0]+=seconds
    monkeypatch.setattr(c.time,'sleep',pause)
    class Response(io.BytesIO):
        code=200;headers={}
    class Opener:
        def open(self,request,timeout):
            calls.append(request);response=Response(b'abcdefghij')
            response.headers={'Content-Length':'10'} if len(calls)==1 else {}
            return response
    monkeypatch.setattr(c.urllib.request,'build_opener',lambda *a:Opener())
    h=c.HTTP('test',budget=15,interval=.6,root=tmp_path)
    assert h.raw('https://example.org/one',10)[1]==b'abcdefghij'
    with pytest.raises(c.ProbeError,match='limit'):h.raw('https://example.org/two',10)
    assert sum(r['bytes'] for r in c.read_rows(h.ledger))==15
    with pytest.raises(c.ProbeError,match='budget'):h.raw('https://example.org/three',10)
    assert len(calls)==2 and sum(sleeps)>=.6
    assert all(request.get_header('User-agent')==c.UA for request in calls)

def test_http_rejects_large_ignored_range_before_body_read(tmp_path,monkeypatch):
    class Response(io.BytesIO):
        code=200;headers={'Content-Length':'999999999'}
        def read(self,*a):pytest.fail('ignored Range caused a large media read')
    class Opener:
        def open(self,*a,**kw):return Response(b'data')
    monkeypatch.setattr(c.urllib.request,'build_opener',lambda *a:Opener())
    h=c.HTTP('test',root=tmp_path)
    with pytest.raises(c.ProbeError,match='limit'):h.raw('https://example.org/big.pdf',64,'bytes=0-63')
    assert c.read_rows(h.ledger)[0]['bytes']==0

def test_persisted_rate_clock_survives_reboot_and_clock_backwards(tmp_path,monkeypatch):
    now=[500.0];sleeps=[]
    monkeypatch.setattr(c.time,'time',lambda:now[0])
    def pause(seconds):sleeps.append(seconds);now[0]+=seconds
    monkeypatch.setattr(c.time,'sleep',pause)
    class Response(io.BytesIO):
        code=200;headers={'Content-Length':'1'}
    class Opener:
        def open(self,*a,**kw):return Response(b'x')
    monkeypatch.setattr(c.urllib.request,'build_opener',lambda *a:Opener())
    # Legacy monotonic timestamps must not cause a multi-day sleep after reboot.
    c.write_json(tmp_path/'rate_state.json',{'example.org':999999999.0})
    h=c.HTTP('test',root=tmp_path);h.raw('https://example.org/one',1)
    assert sum(sleeps)==0
    saved=json.loads((tmp_path/'rate_state.json').read_text())
    assert saved=={'clock':'unix-seconds-v1','hosts':{'example.org':500.0}}
    h2=c.HTTP('test',root=tmp_path);h2.raw('https://example.org/two',1)
    assert sum(sleeps)==pytest.approx(.6)
    now[0]-=1000
    h3=c.HTTP('test',root=tmp_path);h3.raw('https://example.org/three',1)
    assert sum(sleeps)==pytest.approx(1.2)

def test_http_partial_read_is_charged_and_not_reused(tmp_path,monkeypatch):
    class Response(io.BytesIO):
        code=200;headers={}
        def read(self,*a):raise c.http.client.IncompleteRead(b'partial',100)
    class Opener:
        def open(self,*a,**kw):return Response()
    monkeypatch.setattr(c.urllib.request,'build_opener',lambda *a:Opener())
    h=c.HTTP('test',root=tmp_path)
    with pytest.raises(c.ProbeError,match='IncompleteRead'):h.raw('https://example.org/partial',100)
    assert c.read_rows(h.ledger)[0]['bytes']==7
    with pytest.raises(c.ProbeError,match='recorded response'):h.raw('https://example.org/partial',100)

def test_anemi_recorded_search_recovers_actual_tkl_ids():
    rows=parse_search((F/'anemi_search.html').read_bytes())
    assert len(rows)==10 and len({r['document_id'] for r in rows})==10
    assert rows[0]['year']==1908 and rows[1]['year']==1934
    assert all(r['document_id'].startswith('/metadata/') and not r['rights']['compatible'] for r in rows)

def test_recorded_parliament_page_size_lie_cannot_skip_records():
    from greekocr._vendor.scripts.fetch.o4c_discover_parliament import validate_page
    data=load('parliament_truncated_page.json')
    assert data['page']['size']==1000 and len(data['_embedded']['objects'])==100
    with pytest.raises(c.ProbeError,match='pagination mismatch'):validate_page(data)
    validate_page({'page':{'size':100,'number':7,'totalElements':734},'_embedded':{'objects':[{}]*34}})

def test_ranking_excludes_unverified_scan_and_s17_baseline():
    from greekocr._vendor.scripts.fetch.o4c_finalize import qualify
    r=c.row('parliament','test','test','test',rights='CC BY 4.0');r['download_url']='https://example.org/test.pdf'
    c.apply_text(r,'Ἀνθρωπος '*30,'test',1)
    assert not qualify(r)
    r['text_layer']['scan_status']='verified-large-raster-object'
    assert qualify(r)
    r['existing_s17']=True
    assert not qualify(r)

def test_excluded_rights_still_preserve_exact_license_version():
    assert c.license_info('Αναφορά (CC BY-NC-ND 4.0)')['identifier']=='CC-BY-NC-ND-4.0'
    assert c.license_info('https://creativecommons.org/licenses/by-nc-sa/3.0/')['identifier']=='CC-BY-NC-SA-3.0'

def test_misleading_cyrillic_ocr_is_excluded_by_recorded_print_review():
    from greekocr._vendor.scripts.fetch.o4c_finalize import qualify
    reviews=c.read_rows(F/'print_reviews.jsonl')
    conflicts=[r for r in reviews if r['status']=='unverified-conflict']
    assert len(conflicts)==4
    for review in conflicts:
        for probe in review['page_probes']:
            data=(F/'review_pages'/Path(probe['local_path']).name).read_bytes()
            assert hashlib.sha256(data).hexdigest()==probe['sha256']
        r=c.row('archive',review['document_id'],'wrong language metadata','test',rights='public domain')
        r['download_url']='https://example.org/test.pdf'
        c.apply_text(r,'Кириллица '*30,'misleading layer',1)
        r['text_layer']['scan_status']='source-declared'
        assert not qualify(r)  # Ratios alone no longer admit Archive records.
        r['print_review']={'status':'verified-target-sample'}
        assert not qualify(r)  # A metadata-only media URL is insufficient.
        r['media_probe']={'status':'verified-file-prefix','probe_url':r['download_url']}
        assert qualify(r)
        r['print_review']=review
        assert not qualify(r)
    r['print_review']={'status':'unverified-scan-origin'}
    assert not qualify(r)

def test_baseline_alias_scan_md5_is_excluded():
    from greekocr._vendor.scripts.fetch.o4c_finalize import mark_baseline
    r={'document_id':'different-UUID','download_url':'scan','scan_files':[{'url':'scan','checksum':{'checkSumAlgorithm':'MD5','value':'ABCD'}}]}
    mark_baseline(r,[{'item_id':'original-UUID','content_md5':'abcd'}])
    assert r['existing_s17'] and r['baseline_match_basis']=='scan-MD5'

def test_print_probe_honours_existing_three_page_cap(tmp_path):
    from greekocr._vendor.scripts.fetch.o4c_probe_print import existing_pages, page_url
    directory=tmp_path/'print_probes';directory.mkdir()
    for page in (5,15,20):(directory/f'item_n{page}.json').write_text('{}')
    assert existing_pages('item',tmp_path)=={5,15,20}
    assert page_url('an item',20)=='https://archive.org/download/an%20item/page/n20.jpg'

def test_recorded_archive_media_prefix_is_bounded_and_pdf():
    from greekocr._vendor.scripts.fetch.o4c_probe_media import classify_prefix
    data=(F/'archive_pdf_prefix.bin').read_bytes();receipt=load('recordings.json')['archive_pdf_prefix.bin']
    assert len(data)==512 and receipt['range']=='bytes=0-511'
    assert hashlib.sha256(data).hexdigest()==receipt['fixture_sha256']
    assert classify_prefix(data)=='PDF'
    assert classify_prefix(b'<html>access denied</html>') is None
    # Synthetic DjVu signature edge case, separate from the recorded PDF.
    assert classify_prefix(b'AT&TFORM'+b'\0'*4+b'DJVM')=='DjVu'
