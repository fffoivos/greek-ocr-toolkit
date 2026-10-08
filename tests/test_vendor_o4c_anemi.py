"""Recorded Anemi controls and adversarial transport tests. No live network."""
import io
import json
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/fetch'))
import greekocr._vendor.scripts.fetch.o4c_common as c
import greekocr._vendor.scripts.fetch.o4c_discover_anemi as a

F=Path(__file__).resolve().parent/'fixtures/o4c'

@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def fail(*args,**kwargs):pytest.fail('offline test attempted network')
    monkeypatch.setattr(c.urllib.request,'build_opener',fail)
    monkeypatch.setattr(c.subprocess,'Popen',fail)

def test_recorded_login_uses_resolved_url_post_and_no_persistent_login():
    url=a.BASE+'/login/?action=login'
    target,fields,user,password=a.login_form((F/'anemi_login_form.html').read_bytes(),url)
    assert target==url and user=='username' and password=='password'
    assert fields=={'action':'authorize'}
    assert 'savelogin' not in fields
    with pytest.raises(c.ProbeError,match='GET'):
        a.login_form(b'<form method="get"><input name="user" type="text"><input name="pass" type="password"></form>',url)

def test_recorded_catalogue_scope_and_stable_identity():
    data=(F/'anemi_decade_search.html').read_bytes();rows=a.parse_search(data)
    assert len(rows)==42 and a.search_positions(data)==42
    assert all(r['record_url']==a.BASE+r['document_id'] for r in rows)
    assert all(1800<=r['year']<=1809 for r in rows)
    # Duplicate displayed positions must advance the cursor independently of unique IDs.
    assert a.search_positions(data+data)==84 and len(a.parse_search(data+data))==42
    url=a.search_url(1940,1949,'gre','010')
    q=c.urllib.parse.parse_qs(c.urllib.parse.urlsplit(url).query)
    assert q['cclfield4']==['datefrom'] and q['cclterm5']==['1949']
    assert q['cclfield7']==['lang'] and q['cclterm7']==['gre']
    assert q['cclterm8']==['/hierarchy/material/010']
    assert c.robots_allowed((F/'anemi_robots.txt').read_text(),url)

def test_recorded_single_metadata_download_size_not_preservation_size():
    id='/metadata/2/e/3/metadata-36-0000007.tkl'
    r=c.row('anemi',id,'fixture',a.BASE+id)
    a.parse_detail((F/'anemi_detail.html').read_bytes(),r,terms())
    assert r['year']==1809 and r['pages']==135 and r['size']==5768787
    assert r['size']!=515228073  # The separate preservation master is NOT the offered PDF.
    assert r['scan_files'][0]['download_gate']=='CAPTCHA'
    assert not r['rights']['compatible'] and r['rights']['family']=='excluded-NC-or-ND'
    assert r['record_rights_displayed']==[] and r['in_scope']

def terms():
    return {'url':a.BASE+'/','quote':(F/'anemi_terms.txt').read_text().rstrip('\n')}

def test_recorded_bulk_bug_join_and_attribution_are_explicit():
    rows=a.parse_search((F/'anemi_decade_search.html').read_bytes())
    data=(F/'anemi_media_inventory.html').read_bytes()
    a.parse_media_inventory(data,rows,terms())
    assert sum(bool(r['download_url']) for r in rows)==31
    r=rows[1]
    assert r['document_id']=='/metadata/f/8/0/metadata-36-0000008.tkl'
    assert r['size']==55241689 and r['pages']==608
    assert '/metadata/f/8/0/attached-metadata-36-0000008/' in r['download_url']
    assert r['scan_files'][0]['source_url_displayed']!=r['download_url']
    assert c.urllib.parse.parse_qs(c.urllib.parse.urlsplit(r['viewer_urls'][0]).query)['rec']==[r['document_id']]
    assert all(not r['rights']['compatible'] for r in rows)
    with pytest.raises(c.ProbeError,match='merged'):
        a.parse_detail(data,rows[0],terms())
    with pytest.raises(c.ProbeError,match='outside bound'):
        a.parse_media_inventory(data,rows[:1],terms())

def test_recorded_fixture_hashes_and_no_account_or_cookie_material():
    for name in ('anemi_detail','anemi_decade_search','anemi_media_inventory'):
        p=json.loads((F/(name+'_provenance.json')).read_text())
        assert hashlib.sha256((F/(name+'.html')).read_bytes()).hexdigest()==p['fixture_sha256']
    for path in F.glob('anemi_*'):
        if path.suffix=='.pdf':continue
        text=path.read_text().lower()
        assert 'set-cookie' not in text and 'phpsessid=' not in text and 'cookie:' not in text
        assert 'username: anonymous' not in text  # Full navigation was deliberately excluded.

def test_actual_anemi_public_viewer_pdf_fixture_and_exact_measurements():
    import pypdfium2 as pdfium
    data=(F/'anemi_viewer_pages.pdf').read_bytes()
    p=json.loads((F/'anemi_viewer_pages_provenance.json').read_text())
    assert hashlib.sha256(data).hexdigest()==p['fixture_sha256']==p['response_sha256']
    assert p['original_page_indices']==[2,3,4] and p['original_pages_declared']==135
    assert p['rights']['quote']==terms()['quote']
    with pdfium.PdfDocument(data) as doc:
        assert len(doc)==3
        for i,expected in enumerate(p['measurement']):
            page=doc[i]
            try:
                tp=page.get_textpage()
                try:text=tp.get_text_range()
                finally:tp.close()
            finally:page.close()
            assert {'page_index':i+2,**c.metrics(text)}==expected
    assert not c.license_info(p['rights']['quote'])['compatible']

def test_recorded_original_download_control_requires_captcha():
    text=(F/'anemi_download_control.js').read_text()
    assert text.startswith('function showRecaptcha(filename, language)')
    assert 'grecaptcha.reset();' in text and '/php/pdf_dump.php' in text
    assert "captcha_id').style.visibility = \"visible\"" in text
    p=json.loads((F/'anemi_download_control_provenance.json').read_text())
    assert hashlib.sha256(text.encode()).hexdigest()==p['fixture_sha256']

def make_http(tmp_path,monkeypatch):
    monkeypatch.setenv('ANEMI_USER','private-runtime-id')
    monkeypatch.setenv('ANEMI_PASS','private-runtime-pass')
    monkeypatch.setattr(c.urllib.request,'build_opener',lambda *args:None)
    return a.AnemiHTTP(root=tmp_path)

def test_transport_persists_only_sanitized_receipts_and_charges_errors(tmp_path,monkeypatch):
    h=make_http(tmp_path,monkeypatch)
    class Response(io.BytesIO):
        code=403
        headers={'Set-Cookie':'session=runtime-cookie','Content-Type':'text/html',
                 'Location':'/private?token=runtime-cookie'}
    monkeypatch.setattr(a,'sys_platform_is_macos',lambda:True)
    monkeypatch.setattr(h,'native_open',lambda req,limit:Response(b'private-runtime-id private-runtime-pass runtime-cookie'))
    m,body=h.raw(a.BASE+'/login/',1000)
    assert m['status']==403 and len(body)==h.transferred
    recorded=(tmp_path/'transfer.jsonl').read_text()
    assert all(x not in recorded for x in ('private-runtime-id','private-runtime-pass','runtime-cookie','set-cookie','location'))
    assert not list(h.cache.glob('*.body')) and not list(h.cache.glob('*.json'))
    for secret in ('private-runtime-id','private-runtime-pass'):
        with pytest.raises(c.ProbeError,match='private'):h.safe({'title':secret})
    h.secrets=('private\\runtime\nvalue',)
    with pytest.raises(c.ProbeError,match='private'):h.safe({'nested':[{'title':h.secrets[0]}]})
    with pytest.raises(c.ProbeError,match='private'):h.safe({'nested':[c.urllib.parse.quote_plus(h.secrets[0])]})

def test_native_tls_uses_pipes_without_secret_argv_env_or_curlrc(tmp_path,monkeypatch):
    h=make_http(tmp_path,monkeypatch);calls=[]
    monkeypatch.setenv('SSLKEYLOGFILE','private-runtime-tls-log')
    class Input(io.BytesIO):
        def close(self):pass  # Inspect only this dummy in-memory test config.
    class Process:
        def __init__(self,args,**kwargs):
            calls.append((args,kwargs,self))
            self.stdin=Input()
            self.stdout=io.BytesIO(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
                b'Set-Cookie: session=private-runtime-cookie; Path=/\r\n\r\nok')
            self.ended=False
        def poll(self):return 0 if self.ended else None
        def terminate(self):self.ended=True
        def wait(self):return 0
    monkeypatch.setattr(c.subprocess,'Popen',Process)
    monkeypatch.setattr(a,'sys_platform_is_macos',lambda:True)
    h._post_body=b'username=private-runtime-id&password=private-runtime-pass'
    receipt,body=h.raw(a.BASE+'/login/',1000)
    args,kwargs,proc=calls[0]
    assert args[:2]==['/usr/bin/curl','-q'] and '--insecure' not in args and '-k' not in args
    assert args[-2:]==['--config','-']
    assert not any('private-runtime' in arg for arg in args)
    assert not set(('ANEMI_USER','ANEMI_PASS','SSLKEYLOGFILE')).intersection(kwargs['env'])
    assert b'password=private-runtime-pass' in proc.stdin.getvalue()
    assert body==b'ok' and receipt['status']==200
    assert [cookie.value for cookie in h.jar]==['private-runtime-cookie']
    assert 'private-runtime' not in (tmp_path/'transfer.jsonl').read_text()
    assert not list(h.cache.glob('*.body'))

def test_rate_budget_and_prohibited_paths_fail_closed(tmp_path,monkeypatch):
    h=make_http(tmp_path,monkeypatch)
    assert h.interval==2 and h.budget==1_500_000_000
    with pytest.raises(ValueError):a.AnemiHTTP(interval=1,root=tmp_path)
    for path in ('/tools/login','/tools/','/tools','/db','/db/records','/%74ools/login','/metadata/../tools/login'):
        with pytest.raises(c.ProbeError,match='prohibited'):h.check_robots(a.BASE+path)
    with pytest.raises(c.ProbeError,match='private URL'):
        h.raw(a.BASE+'/login/?session=opaque',100)
    h.transferred=h.budget
    with pytest.raises(c.ProbeError,match='budget'):h._raw(a.BASE+'/book',100)

def test_session_transport_honors_two_seconds_and_partial_caps(tmp_path,monkeypatch):
    h=make_http(tmp_path,monkeypatch);now=[100.0];sleeps=[]
    monkeypatch.setattr(c.time,'time',lambda:now[0])
    def sleep(seconds):sleeps.append(seconds);now[0]+=seconds
    monkeypatch.setattr(c.time,'sleep',sleep)
    class Response(io.BytesIO):
        code=200;headers={}
    monkeypatch.setattr(a,'sys_platform_is_macos',lambda:True)
    monkeypatch.setattr(h,'native_open',lambda req,limit:Response(b'x'))
    h.raw(a.BASE+'/one',100);h.raw(a.BASE+'/two',100)
    assert sum(sleeps)==2
    h.robots['anemi.lib.uoc.gr']={'delay':5};h.raw(a.BASE+'/three',100)
    assert sum(sleeps)==7
    monkeypatch.setattr(h,'native_open',lambda req,limit:Response(b'x'*100))
    with pytest.raises(c.ProbeError,match='limit'):h.raw(a.BASE+'/bounded',10)
    assert c.read_rows(h.ledger)[-1]['bytes']==10

def test_withdrawn_record_positions_do_not_erase_subsequent_pages():
    withdrawn=b'<tr class="resultsnorm"><td colspan="3">Document is invalid after 2019-01-01</td></tr>'
    assert a.search_positions(withdrawn)==1 and not a.parse_search(withdrawn)
    with pytest.raises(c.ProbeError,match='cursor not advanced'):
        a.search_positions(b'<tr class="resultsnorm"><td>unknown layout</td></tr>')

def test_authentication_requires_signed_in_navigation_not_cookie(monkeypatch):
    monkeypatch.setenv('ANEMI_USER','private-runtime-id');monkeypatch.setenv('ANEMI_PASS','private-runtime-pass')
    class Replay:
        def __init__(self,success):self.success=success;self.events=[]
        def get(self,url,limit):return {'url':a.BASE+'/login/?action=login'},(F/'anemi_login_form.html').read_bytes()
        def post(self,url,fields):
            assert url.startswith(a.BASE+'/login/') and fields['action']=='authorize'
            assert 'savelogin' not in fields
            return {},b'<a href="/login/?action=logout">Sign Out</a>' if self.success else b'<p>Sign In</p>'
        def event(self,**kwargs):self.events.append(kwargs)
    assert a.authenticate(Replay(True))
    with pytest.raises(c.ProbeError,match='not verified'):a.authenticate(Replay(False))

def test_bounded_viewer_probe_replays_existing_recorded_pdf():
    id='/metadata/test/metadata-test.tkl'
    r=c.row('anemi',id,'fixture',a.BASE+id,pages=10,rights=terms()['quote'])
    r['download_url']=a.BASE+'/metadata/test/attached-metadata-test/test.pdf'
    r['viewer_urls']=[a.BASE+'/php/pdf_pager.php?rec='+id+'&do=test.pdf']
    class Replay:
        transferred=0
        def get(self,url,limit):
            if 'pdf_pager' in url:
                return {'url':url,'sha256':'viewer'},b'<iframe src="pdf_split.php?filename=/var/www/anemi-portal/metadata/test/attached-metadata-test/test.pdf&amp;pageno=3&amp;pagenum=1">'
            data=(F/'parliament_recorded_page.pdf').read_bytes();self.transferred+=len(data)
            return {'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)},data
    a.probe_viewer_page(Replay(),r,1)
    assert r['pages']==10 and r['text_layer']['page_indices']==[2]
    assert r['text_layer']['measurement']['chars']==2096
    assert r['text_layer']['page_measurements'][0]['chars_per_page']==2096
    assert not r['rights']['compatible'] and r['status']=='excluded-site-terms'
    with pytest.raises(ValueError):a.probe_viewer_page(Replay(),r,4)

def test_three_page_bound_preserves_full_file_count_and_page_metrics():
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(F/'parliament_recorded_page.pdf') as source:
        with pdfium.PdfDocument.new() as doc:
            doc.import_pages(source,pages=[0,0,0]);stream=io.BytesIO();doc.save(stream);data=stream.getvalue()
    r=c.row('anemi','fixture','fixture','fixture',pages=10,rights=terms()['quote'])
    r['download_url']=a.BASE+'/metadata/test/attached-metadata-test/test.pdf'
    r['viewer_urls']=[a.BASE+'/php/pdf_pager.php?rec=/metadata/test/metadata-test.tkl&do=test.pdf']
    class Replay:
        transferred=0
        viewer_template={'endpoint':a.BASE+'/php/pdf_split.php','filename_prefix':'/var/www/anemi-portal',
            'verified_viewer_url':'recorded-control','viewer_sha256':'control'}
        def get(self,url,limit):
            assert c.urllib.parse.parse_qs(c.urllib.parse.urlsplit(url).query)['pagenum']==['3']
            self.transferred+=len(data)
            return {'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)},data
    a.probe_viewer_page(Replay(),r,3)
    assert r['pages']==10 and r['text_layer']['page_indices']==[2,3,4]
    assert r['text_layer']['sample_pages']==3
    assert [m['chars'] for m in r['text_layer']['page_measurements']]==[2096]*3
    assert r['text_layer']['measurement']['polytonic_ratio']==pytest.approx(r['polytonic_ratio'])
