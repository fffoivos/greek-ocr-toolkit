"""T23 contracts: synthetic inputs and cached fixtures only, no network."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path

from PIL import Image
import pypdfium2 as pdfium
import pytest

from greekocr.harvest import parliament as p
from scripts.harvest import parliament as driver


def row(year=1980, ident='one', **kwargs):
    return dict(document_id=ident,year=year,title=f'ΣΥΝΕΔΡΙΑΣΗ 12 ΜΑΡΤΙΟΥ {year}',
                collection='ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ',rights={'raw':['Αναφορά Δημιουργού (CC BY 4.0)']},**kwargs)


@pytest.mark.parametrize('year',[1974,2001,None,'1980',True])
def test_selection_year_rejected(year):
    assert not p.eligible(row(year))


@pytest.mark.parametrize('year',[1975,1981,1982,2000])
def test_selection_inclusive_years(year):
    assert p.eligible(row(year))


@pytest.mark.parametrize('rights',['CC BY-NC-ND 4.0','CC BY 3.0','CC0','IN COPYRIGHT','',
    ['CC BY 4.0','CC BY-NC-ND 4.0'],['CC BY 4.0','NONCOMMERCIAL']])
def test_rights_exact_cc_by_only(rights):
    r=row();r['rights']={'raw':rights}
    assert not p.eligible(r)


def test_collection_exact_and_no_inference_from_compatible_flag():
    r=row();r['collection']='ΑΡΧΕΙΟ ΓΙΩΡΓΟΥ ΓΕΝΝΗΜΑΤΑ'
    assert not p.eligible(r)


def test_cc_by_licence_word_is_not_an_nc_token():
    r=row();r['rights']={'raw':['LICENCE CC BY 4.0']}
    assert p.eligible(r)
    r=row();r['rights']={'compatible':True,'family':'CC-BY','raw':[]}
    assert not p.eligible(r)


def test_four_chronological_strata_and_backups_are_disjoint_seeded():
    rows=[row(1980,str(i)) for i in range(24)]
    for i,r in enumerate(rows):r['title']=f'ΣΥΝΕΔΡΙΑΣΗ {i%28+1} ΙΑΝΟΥΑΡΙΟΥ 1980'
    slots=[s for s in p.candidate_slots(rows) if s['year']==1980]
    assert [len(s['candidates']) for s in slots]==[6]*4
    assert len({r['document_id'] for s in slots for r in s['candidates']})==24
    assert slots==[s for s in p.candidate_slots(rows[::-1]) if s['year']==1980]
    assert max(p.session_date(r) for r in slots[0]['candidates'])<min(p.session_date(r) for r in slots[1]['candidates'])
    assert slots != [s for s in p.candidate_slots(rows,seed=1) if s['year']==1980]


def test_missing_years_are_not_reallocated():
    slots=p.candidate_slots([row(1980,str(i)) for i in range(4)])
    assert len(slots)==104
    assert sum(bool(s['candidates']) for s in slots)==4
    assert all(not s['candidates'] for s in slots if s['year']!=1980)


def test_duplicate_catalogue_identity_fails():
    with pytest.raises(ValueError,match='duplicate'):p.candidate_slots([row(),row()])


@pytest.mark.parametrize('total',[15,20,100,731,1500])
def test_twelve_pages_spread_deterministically_with_0_2_offsets(total):
    a=p.page_spread(total,'uuid')
    assert a==p.page_spread(total,'uuid')
    assert len({r['page'] for r in a})==12
    assert all(math.ceil(.08*total)<=r['page']<=math.floor(.95*total) and 0<=r['random_offset']<=2 for r in a)
    assert min(r['anchor'] for r in a)==math.ceil(.08*total) and max(r['anchor'] for r in a)==math.floor(.95*total)


def test_short_pdf_cannot_claim_twelve_pages():
    with pytest.raises(ValueError):p.page_spread(10,'uuid')


def test_neighbours_never_expand_or_cross_boundary():
    assert p.neighbours(20,100,{21})==[20,22]
    assert p.neighbours(94,100)==[94,95]


def books(years=range(1975,2001)):
    return [dict(key=f'{y}{i:04d}',book=f'{y}-{i}',year=y,decade=y//10*10,title='Πρακτικά') for y in years for i in range(4)]


@pytest.mark.parametrize('years',[range(1975,2001),list(range(1975,1990))+[1994,1995,1996]])
def test_holdout_16_books_16_years_12_test_4_dev(years):
    b=books(years);h=p.holdout(b)
    assert h==p.holdout(b[::-1])
    assert len(h)==len({r['year'] for r in h})==16
    assert Counter(r['split'] for r in h)=={'test':12,'dev':4}
    assert min(r['year'] for r in h)<=1976 and max(r['year'] for r in h)>=1995
    assert h!=p.holdout(b,seed=1)


def test_duplicate_holdout_book_fails():
    b=books();b.append(b[0])
    with pytest.raises(ValueError,match='duplicate'):p.holdout(b)


def fixture():
    return json.loads((Path(__file__).parent/'fixtures/parliament_resolution.json').read_text())


def test_original_pdf_fixture_ignores_djvu_text_and_thumbnail():
    f=fixture();bits=p.original_pdfs(f['bundles'][2],f['bitstreams'])
    assert [b['uuid'] for b in bits]==['small','large']
    assert bits[0]['checksum']['checkSumAlgorithm']=='MD5'
    assert all(b['url'].startswith(p.BASE) for b in bits)
    assert p.original_pdfs(f['bundles'][1],f['bitstreams'])==[]


def test_resolution_fixture_pagination_and_largest_original_pdf():
    f=fixture();seen=[]
    class Client:
        def json(self,url):
            seen.append(url)
            if '/items/' in url:
                return {'_embedded':{'bundles':f['bundles']},'page':{'totalPages':1}}
            page=int(url.rsplit('=',1)[1])
            return {'_embedded':{'bitstreams':f['bitstreams'][:2] if page==0 else f['bitstreams'][2:]},'page':{'totalPages':2}}
    result=p.resolve_pdf(Client(),'item')
    assert result['uuid']=='large' and result['size']==456
    assert len(seen)==3 and not any('/text/' in s for s in seen)


def test_no_original_pdf_fails_closed():
    class Client:
        def json(self,url):return {'_embedded':{'bundles':[]}}
    with pytest.raises(ValueError,match='no ORIGINAL PDF'):p.resolve_pdf(Client(),'item')


def test_oversize_original_remains_volume_replacement_not_a_smaller_part():
    f=fixture();f['bitstreams'][-1]['sizeBytes']=p.MAX_PDF+1
    class Client:
        def json(self,url):
            if '/items/' in url:return {'_embedded':{'bundles':f['bundles']}}
            return {'_embedded':{'bitstreams':f['bitstreams']}}
    result=p.resolve_pdf(Client(),'item')
    assert result['uuid']=='large' and result['size']>250_000_000


@pytest.mark.parametrize('url',['https://evil.invalid/pdf','http://digitallibrary.parliament.gr/a'])
def test_resolution_rejects_other_hosts_and_plain_http(url):
    with pytest.raises(ValueError):p.local_url(url)


def test_render_slots_native_grey_gate_and_bounded_replacements(tmp_path,monkeypatch):
    monkeypatch.setattr(driver,'REPO',tmp_path)
    monkeypatch.setattr(driver,'BULK',tmp_path/'bulk')
    monkeypatch.setattr(driver,'OUT',tmp_path/'out')
    monkeypatch.setattr(driver,'relative',lambda p:str(p.relative_to(tmp_path)))
    doc=pdfium.PdfDocument.new()
    for i in range(100):doc.new_page(72,144).close()
    doc.save(tmp_path/'book.pdf');doc.close()
    b=dict(book='uuid',key='uuid',pdf='book.pdf',pdf_sha256='fixture',page_count=100,year=1980)
    def fake_gate(page):
        with Image.open(tmp_path/page['image']) as im:assert im.mode=='L' and im.size==(200,400)
        accepted=page['neighbour_offset']==2
        return dict(page,gate={'accepted':accepted},harvest_accepted=accepted)
    monkeypatch.setattr(driver,'gate_task',fake_gate)
    with ThreadPoolExecutor(2) as pool:manifest,slots=driver.gate_volume(b,pool)
    assert len(slots)==12 and len(manifest)<=36
    assert len({r['id'] for r in manifest})==len(manifest)
    assert all(len(s['attempts'])<=3 and all(s['original_page']<=n<=s['original_page']+2 for n in s['attempts']) for s in slots)
    assert all(r['era']=='1975_1981_polytonic_possible' for r in manifest)


def record(ident,text,book='train',year=1995):
    return dict(id=ident,page_id=ident,book_key=book,year=year,decade=year//10*10,
        confidence=.99,flags=[],bbox=[0,0,200,20],docai_text=text,licence='CC-BY-4.0',
        source_url='https://hdl.handle.net/fixture',attribution='Hellenic Parliament Library; fixture',
        era='1975_1981_polytonic_possible' if year<=1981 else '1982_2000_monotonic')


def test_o5_reserves_every_prior_wave_and_new_holdout_with_reverse_overlay():
    from scripts.harvest import parliament_outputs as o
    texts=['ἄνθρωπος καὶ λόγος','ἐλευθερία καὶ νόμος','βουλευτὴς καὶ γερουσία']
    sources=['anemi_round1','vouli_parliament_1850s','anemi_round2']
    old=[dict(id=str(i),label=t,split='test',source=s) for i,(t,s) in enumerate(zip(texts,sources))]
    newtext='Η Βουλή των Ελλήνων'
    old.append(dict(id='old-train',label=newtext,split='train',source='anemi_round2'))
    rows=[record('match-'+str(i),t) for i,t in enumerate(texts)]
    rows += [record('new-held',newtext,book='held'),record('new-match',newtext),record('unique','Παρακαλώ κύριε Πρόεδρε')]
    kept,rejected,_,_,excluded=o.admit_records(rows,[dict(book_key='held',split='dev')],old)
    assert {r['id'] for r in kept}=={'new-held','unique'}
    assert len(rejected)==4 and all(r['reasons']==['label_in_holdout'] for r in rejected)
    assert [r['id'] for r in excluded]==['old-train']


def test_era_cannot_force_polytonic_text_into_monotonic_class():
    from scripts.harvest import parliament_outputs as o
    rows=[record('poly','ἄνθρωπος καὶ λόγος',year=1995),record('mono','Η Βουλή των Ελλήνων',year=1975)]
    kept,*_=o.admit_records(rows,[],[])
    assert [r['script_class'] for r in kept]==['greek_poly','greek_mono']
    assert kept[0]['era']=='1982_2000_monotonic' and kept[1]['era']=='1975_1981_polytonic_possible'


def test_compiled_actual_year_folder_and_uuid_prefix():
    from scripts.harvest import parliament_outputs as o
    q=dict(year=1995,title='ΣΥΝΕΔΡΙΑΣΗ / Βουλή',key='abcdef12',page=42)
    path=o.compiled_path(q)
    assert path.parts[0]=='1995' and path.parts[1].endswith('_abcdef') and path.name=='p0042.jpg'


def test_docai_only_root_and_cost_ceiling_without_credentials(tmp_path):
    binding=dict(project='test',location='eu',processor='test',version='test',user_project='test',
        options=dict(ocrConfig=dict(enableSymbol=True,hints=dict(languageHints=['el']))))
    reader=driver.ParliamentReaders(dict(binding=binding,cap_usd=2.5,max_calls=2000),root=tmp_path)
    assert reader.root==tmp_path and reader.budget.max_calls==1666 and not hasattr(reader,'vision')
    with pytest.raises(ValueError,match='forbids'):reader.call('vision','unused')


def test_pdf_stream_receipt_size_checksum_and_partial_cleanup_offline(tmp_path,monkeypatch):
    import hashlib
    from greekocr.harvest.parliament_http import ParliamentHTTP
    client=ParliamentHTTP(tmp_path/'http',offline=True)
    content=b'%PDF-fixture'
    def request(url,path,limit):
        assert limit==250_000_000
        path.write_bytes(content)
        return dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
    monkeypatch.setattr(client,'_request',request)
    path=tmp_path/'book.pdf'
    receipt=client.download(p.BASE+'/fixture',path,len(content),
        {'checkSumAlgorithm':'MD5','value':hashlib.md5(content).hexdigest()})
    assert path.read_bytes()==content and receipt['bytes']==len(content)
    with pytest.raises(ValueError,match='size'):client.download(p.BASE+'/fixture',path,len(content)+1)
    assert not path.with_suffix('.part').exists()
    with pytest.raises(ValueError,match='checksum'):
        client.download(p.BASE+'/fixture',path,len(content),{'checkSumAlgorithm':'MD5','value':'wrong'})
    assert not path.with_suffix('.part').exists()


def test_http_offline_miss_cannot_make_request(tmp_path):
    from greekocr.harvest.parliament_http import ParliamentHTTP
    client=ParliamentHTTP(tmp_path,offline=True)
    with pytest.raises(RuntimeError,match='offline'):client.json(p.BASE+'/uncached')
    assert not (tmp_path/'requests.jsonl').exists()


def test_failed_size_response_is_retained_without_fabricating_lines(tmp_path,monkeypatch):
    from scripts.harvest import parliament_outputs as o
    monkeypatch.setattr(o,'OUT',tmp_path)
    error=dict(code=400,message='Input Document too large',status='INVALID_ARGUMENT')
    monkeypatch.setattr(o,'raw_read',lambda *a:(None,dict(status='error',error=error)))
    page=dict(id='oversized',width=6000,height=8000)
    rows,summary=o.read_records(dict(pages=[page]),write=True)
    assert rows==[] and summary['successful_pages']==0 and summary['failed_reads']==1
    assert summary['lost_pages']==1 and summary['empty_pages']==summary['no_line_pages']==0
    a=json.loads((tmp_path/'assignments/oversized.json').read_text())
    assert a['records']==[] and a['geometry_error']=='Input Document too large' and a['lost_page']


def test_failed_read_compilation_has_explicit_visible_heading():
    from scripts.harvest import parliament_outputs as o
    image=Image.new('L',(800,300),255)
    baseline,_=o.render_compiled(image,[],{})
    marked,layout=o.render_compiled(image,[],{'read_error':'Input Document too large'})
    assert marked.tobytes()!=baseline.tobytes() and layout['read_error']=='Input Document too large'
    assert layout['bad_page'] is False


def test_failed_read_quality_is_separate_from_frozen_admission_bad_page():
    from scripts.harvest import parliament_outputs as o
    quality={'good':{'bad_page':False}}
    reads={'pages':[dict(page_id='failed',lost_page=True,geometry_error='size'),dict(page_id='good',lost_page=False)]}
    display=o.compiled_quality(quality,reads)
    assert quality=={'good':{'bad_page':False}} and display['failed']=={'read_error':'size'}


def test_raw_gzip_roundtrip_preserves_original_bytes_custody_and_cache(tmp_path,monkeypatch):
    import gzip
    import hashlib
    from scripts.harvest import compact_parliament_raw as c,parliament_outputs as o
    root=tmp_path/'google';directory=root/'docai/fixture';directory.mkdir(parents=True)
    image=tmp_path/'page.png';Image.new('L',(20,30),255).save(image)
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    raw=directory/'raw.json';data=b'{\n  "document": {"text": "fixture"}\n}\n';raw.write_bytes(data)
    rawsha=hashlib.sha256(data).hexdigest();binding={'test':'binding'}
    (directory/'cache.json').write_text(json.dumps(dict(raw_sha256=rawsha,crop_sha256=digest,binding=binding,receipt_id='one')))
    parsed=root/'parsed/docai'/(digest+'.json');parsed.parent.mkdir(parents=True)
    parsed.write_text(json.dumps(dict(status='ok',binding=binding,image_sha256=digest,raw_json_path=str(raw),receipt_id='one')))
    assert c.compact(root)[0]==1 and not raw.exists()
    archive=raw.with_suffix('.json.gz');assert gzip.decompress(archive.read_bytes())==data
    assert c.compact(root)[0]==0
    monkeypatch.setattr(o,'REPO',tmp_path);monkeypatch.setattr(o,'GOOGLE',root)
    monkeypatch.setattr(o,'relative',lambda path:str(path.relative_to(tmp_path)))
    value,receipt=o.raw_read(dict(image='page.png',image_sha256=digest),dict(binding=binding))
    assert value==json.loads(data) and receipt['raw_sha256']==rawsha
    assert receipt['raw_gzip_sha256']==hashlib.sha256(archive.read_bytes()).hexdigest()


def test_embedded_png_dedup_reconstructs_every_original_response_byte(tmp_path,monkeypatch):
    import base64,hashlib
    from scripts.harvest import compact_parliament_raw as c
    monkeypatch.setattr(c,'REPO',tmp_path)
    root=tmp_path/'google';directory=root/'docai/fixture';directory.mkdir(parents=True)
    image=tmp_path/'page.png';Image.new('L',(20,30),180).save(image)
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    response={'document':{'text':'Ελληνικά','pages':[{'image':dict(content=base64.b64encode(image.read_bytes()).decode(),mimeType='image/png',width=20,height=30)}]}}
    data=c.canonical(response);raw=directory/'raw.json';raw.write_bytes(data);rawsha=hashlib.sha256(data).hexdigest()
    (directory/'cache.json').write_text(json.dumps(dict(raw_sha256=rawsha,crop_sha256=digest)))
    parsed=root/'parsed/docai'/(digest+'.json');parsed.parent.mkdir(parents=True)
    parsed.write_text(json.dumps(dict(status='ok',image_sha256=digest,raw_json_path=str(raw),receipt_id='fixture')))
    assert c.compact(root,image_paths={digest:image})[0]==1
    assert not raw.exists() and raw.with_suffix('.json.dedup.gz').exists()
    restored,archive=c.raw_bytes(raw)
    assert restored==data and hashlib.sha256(restored).hexdigest()==rawsha
    assert archive.name=='raw.json.dedup.gz'
    image.write_bytes(b'changed')
    with pytest.raises(ValueError,match='PNG changed'):c.raw_bytes(raw)


def test_retention_only_releases_rejected_intermediates_keeps_flag_examples(tmp_path,monkeypatch):
    from scripts.harvest import parliament_retention as r
    monkeypatch.setattr(r,'REPO',tmp_path);monkeypatch.setattr(r,'OUT',tmp_path/'out');monkeypatch.setattr(r,'BULK',tmp_path/'bulk')
    monkeypatch.setattr(r,'relative',lambda path:str(path.relative_to(tmp_path)))
    r.OUT.mkdir();r.BULK.mkdir()
    pages=[]
    for ident,accepted,flags in [('accepted',True,[]),('a-reject',False,['table']),('b-reject',False,['bend_scout']),('c-reject',False,['table'])]:
        path=tmp_path/(ident+'.png');Image.new('L',(20,30),240).save(path)
        pages.append(dict(id=ident,image=path.name,image_sha256=driver.sha(path),harvest_accepted=accepted,
            gate=dict(flags=flags),pdf_sha256='pdf',bitstream={},page=1,book='book'))
    (r.OUT/'manifest.json').write_text(json.dumps(pages));(r.OUT/'fetch_visual_qa.json').write_text(json.dumps({'samples':[]}))
    r.prepare()
    assert all((tmp_path/(ident+'.png')).exists() for ident in ('accepted','a-reject','b-reject'))
    assert not (tmp_path/'c-reject.png').exists()
    receipt=json.loads((r.OUT/'page_image_retention.json').read_text())
    assert receipt['accepted_native_kept']==1 and receipt['rejected_native_removed']==1
    assert all((tmp_path/p['preview']).exists() for p in receipt['pages'])


def test_preview_refuses_accepted_image_before_any_mutation(tmp_path,monkeypatch):
    from scripts.harvest import parliament_retention as r
    monkeypatch.setattr(r,'REPO',tmp_path)
    with pytest.raises(ValueError,match='accepted PNGs'):
        r.preview(dict(harvest_accepted=True,image='accepted.png',id='accepted'))


def geometry_response(scale=2):
    native=[1000,2000];vertices=[{'x':100,'y':200},{'x':300,'y':200},{'x':300,'y':240},{'x':100,'y':240}]
    poly=dict(vertices=[{k:v/scale for k,v in p.items()} for p in vertices],
        normalizedVertices=[dict(x=p['x']/native[0],y=p['y']/native[1]) for p in vertices])
    return dict(document=dict(text='Ελληνικά',pages=[dict(dimension=dict(width=1000,height=2000,unit='pixels'),
        image=dict(width=1000,height=2000),lines=[dict(layout=dict(boundingPoly=poly,textAnchor=dict(textSegments=[dict(endIndex=8)]),confidence=.99))])]))


def test_normalized_provider_vertices_resolve_integer_frame_without_mutating_raw():
    from greekocr.harvest.parliament_geometry import response_geometry
    raw=geometry_response();before=json.dumps(raw,sort_keys=True)
    result=response_geometry('docai',raw,(1000,2000))
    assert result['lines'][0]['bbox']==[100,200,300,240]
    assert result['coordinate_frame']['vertex_source']=='provider_normalized_vertices'
    assert json.dumps(raw,sort_keys=True)==before


def test_resolved_native_box_cuts_the_target_ink_not_the_integer_frame_background():
    from PIL import ImageDraw
    from greekocr.harvest.parliament_geometry import response_geometry
    image=Image.new('L',(1000,2000),255);ImageDraw.Draw(image).rectangle((100,200,299,239),fill=0)
    box=response_geometry('docai',geometry_response(),image.size)['lines'][0]['bbox']
    assert image.crop(tuple(box)).getextrema()==(0,0)
    assert image.crop((50,100,150,120)).getextrema()==(255,255)


def test_agreeing_integer_frame_keeps_exact_original_geometry():
    from greekocr.harvest.parliament_geometry import response_geometry
    result=response_geometry('docai',geometry_response(1),(1000,2000))
    assert result['lines'][0]['bbox']==[100,200,300,240]
    assert result['coordinate_frame']['vertex_source']=='provider_integer_vertices'


def test_recorded_transform_cases_keep_original_inverse_mapping(monkeypatch):
    from greekocr.harvest import parliament_geometry as g
    raw=geometry_response();raw['document']['pages'][0]['transforms']=[{'test':'delegate'}]
    monkeypatch.setattr(g,'original_geometry',lambda *args:args)
    result=g.response_geometry('docai',raw,(1000,2000))
    assert result==('docai',raw,(1000,2000))


def test_conflicting_frame_needs_normalized_vertices_on_every_line_and_symbol():
    from greekocr.harvest.parliament_geometry import response_geometry
    raw=geometry_response();raw['document']['pages'][0]['symbols']=[dict(layout=dict(boundingPoly=dict(vertices=[dict(x=1,y=2)])))]
    with pytest.raises(ValueError,match='without normalized'):response_geometry('docai',raw,(1000,2000))


def test_optimized_quality85_jpeg_has_identical_decoded_pixels():
    import io
    import numpy as np
    image=Image.fromarray(np.random.default_rng(20263).integers(0,256,(160,240,3),dtype='uint8'),'RGB')
    standard=io.BytesIO();optimized=io.BytesIO()
    image.save(standard,format='JPEG',quality=85)
    image.save(optimized,format='JPEG',quality=85,optimize=True)
    with Image.open(io.BytesIO(standard.getvalue())) as a,Image.open(io.BytesIO(optimized.getvalue())) as b:
        assert a.tobytes()==b.tobytes()
    assert len(optimized.getvalue())<len(standard.getvalue())


def test_compiled_source_binding_keeps_execution_sha_and_rejects_raster_changes(tmp_path):
    import hashlib
    from greekocr.harvest.parliament_provenance import verify_source
    snapshot=tmp_path/'executed.py';current=tmp_path/'current.py'
    snapshot.write_text('def render_compiled():\n    return 1\ndef publish():\n    return 2\n')
    recorded=hashlib.sha256(snapshot.read_bytes()).hexdigest()
    current.write_text('def render_compiled():\n    return 1\ndef publish():\n    return 3\n')
    binding=verify_source(recorded,current,snapshot)
    assert binding['changed_functions']==['publish'] and binding['executed_source_sha256']==recorded
    current.write_text('def render_compiled():\n    return 9\ndef publish():\n    return 3\n')
    with pytest.raises(ValueError,match='raster/admission'):verify_source(recorded,current,snapshot)
    with pytest.raises(ValueError,match='snapshot SHA'):verify_source('wrong',current,snapshot)
    current.write_bytes(snapshot.read_bytes())
    fresh=tmp_path/'new-snapshot.py'
    verify_source(recorded,current,fresh)
    assert fresh.read_bytes()==snapshot.read_bytes()
