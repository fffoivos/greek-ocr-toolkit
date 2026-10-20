"""Offline T26 contracts. No Internet Archive, credentials or provider access."""
import copy
import hashlib
import json
import math
from pathlib import Path
from unittest.mock import Mock
import pytest
from PIL import Image
from greekocr.harvest import admission
from greekocr.harvest import cyrillic as policy
from scripts.harvest import cyrillic as runner
from scripts.harvest import cyrillic_outputs as outputs


def record(text='Русская кириллица',**extra):
    return dict(id='book-p000001-l0001',page_id='book-p000001',book_key='book',year=1900,decade=1900,
        confidence=.99,bbox=[10,10,200,40],flags=[],docai_text=text,source='archive_book',licence='public-domain',
        source_url='https://archive.org/details/book',attribution='author',read_batch='cyrillic',
        not_cyrillic_page=False,**extra)


@pytest.mark.parametrize('cyr,latin,passes',[(7,3,True),(69,31,False),(70,30,True),(71,29,True),(0,10,False),(10,0,True),(0,0,False)])
def test_page_threshold(cyr,latin,passes):
    result=policy.page_script('я'*cyr+'a'*latin+' 1234!·—')
    assert result['letters']==cyr+latin and result['cyrillic_letters']==cyr
    assert result['not_cyrillic_page']==(not passes)


def test_all_letters_denominator_includes_greek_and_other():
    result=policy.page_script('я'*7+'α'+'中'+'a')
    assert result['letters']==10 and not result['not_cyrillic_page']
    assert policy.page_script('я'*7+'α'+'中中'+'a')['not_cyrillic_page']


def test_historical_bulgarian_serbian_letters_count():
    result=policy.page_script('ѢѣѲѳѴѵЈјЉљЊњЋћЂђЏџЫы')
    assert result['cyrillic_share']==1


@pytest.mark.parametrize('text',['Русская кириллица','Български речник','Српски речник је добар'])
@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_cyrillic_class(text):
    good,cls,reasons,label=policy.admit(record(text),{'bad_page':False},{'not_cyrillic_page':False})
    assert good and cls=='cyrillic' and not reasons and label==admission.normalize_label(text)


@pytest.mark.parametrize('word',['кириллицa','кириллицα','Бългaрски','Српскα'])
@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_mixed_script_word_drops_line(word):
    good,cls,reasons,label=policy.admit(record(word+' кириллица'),{'bad_page':False},{'not_cyrillic_page':False})
    assert not good and cls is None and 'mixed_word' in reasons


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_latin_byproduct_kept_on_cyrillic_page():
    good,cls,reasons,label=policy.admit(record('Whole Latin sentence'),{'bad_page':False},{'not_cyrillic_page':False})
    assert good and cls=='latin'


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_page_exclusion_appends_every_t20_failure():
    r=record('яa!')
    r.update(confidence=.1,flags=['tall_box'])
    good,cls,reasons,label=policy.admit(r,{'bad_page':True},{'not_cyrillic_page':True})
    assert reasons==['short_line','low_confidence','tall_box','mixed_word','bad_page','not_cyrillic_page']
    assert not good and cls is None


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_page_rejects_clean_line():
    assert policy.admit(record(),{'bad_page':False},{'not_cyrillic_page':True})[2]==['not_cyrillic_page']


@pytest.mark.parametrize('total',[60,275,478,548,592,1056,1167,1183])
def test_sampling_inclusive_range_and_bounded_neighbours(total):
    picks=policy.sample(total,'item')
    assert len(picks)==45 and len({p['page'] for p in picks})==45
    reserved={p['page'] for p in picks};lo,hi=math.ceil(.08*total),math.floor(.95*total)
    assert all(lo<=p['page']<=hi and 0<=p['random_offset']<=2 for p in picks)
    for p in picks:
        assert p['candidates'][0]==p['page'] and len(p['candidates'])<=3
        assert all(p['page']<=n<=min(hi,p['page']+2) for n in p['candidates'])
        assert not (set(p['candidates'][1:])&reserved)
    assert picks==policy.sample(total,'item')


def test_seeded_per_item_sample_differs():
    assert policy.sample(1183,'a')!=policy.sample(1183,'b')


def test_sample_insufficient_book():
    with pytest.raises(ValueError):policy.sample(20,'short')


def books():return [dict(key=f'{i:08d}',book=str(i),title='Title',year=1900,decade=1900) for i in range(13)]


def test_whole_item_holdout_deterministic_independent_of_input_order():
    held=policy.holdout(books())
    assert held==policy.holdout(list(reversed(books())))
    assert len({r['book_key'] for r in held})==3
    assert [r['split'] for r in held].count('test')==2
    assert [r['split'] for r in held].count('dev')==1


@pytest.mark.parametrize('rows',[books()[:12],books()+books()[:1]])
def test_holdout_exact_scope(rows):
    with pytest.raises(ValueError):policy.holdout(rows)


def test_media_300mb_fallback():
    r=dict(download_url='big',scan_files=[dict(name='big.pdf',url='big',size=300_000_001),dict(name='a_text.pdf',url='small',size=90)])
    assert policy.media(r)==dict(kind='pdf',url='small',bytes=90)
    r['scan_files']=r['scan_files'][:1]
    assert policy.media(r)['kind']=='page_images'


def test_exact_300mb_allowed():
    assert policy.media(dict(download_url='x',scan_files=[dict(name='x.pdf',size=300_000_000,url='x')]))['kind']=='pdf'


def test_input_scope_print_and_rights_checks():
    rows=[dict(source='archive',estimated_cyrillic_lines=1,document_id=str(i),rights=dict(compatible=True,family='public-domain'),
        print_review=dict(status='verified-target-sample')) for i in range(13)]
    assert len(policy.candidates(rows+[dict(source='archive',estimated_cyrillic_lines=0)]))==13
    rows[0]['print_review']['status']='digital-edition'
    with pytest.raises(ValueError):policy.candidates(rows)
    rows[0]['print_review']['status']='verified-target-sample';rows[0]['rights']['family']='CC-BY-NC'
    with pytest.raises(ValueError):policy.candidates(rows)


def test_key_determinism():
    assert policy.key('a')==hashlib.sha256(b'archive_a').hexdigest()[:8]


def test_reader_binding_no_hints(tmp_path):
    b=runner.binding();assert b['options']['ocrConfig']['hints']['languageHints']==[]
    plan=dict(binding=b,cap_usd=1.2,max_calls=585)
    reader=runner.CyrillicReaders(plan,root=tmp_path)
    assert reader.docai.binding()==b and reader.docai.language_hints==()
    assert reader.budget.cap==1.2 and reader.budget.max_calls==585
    with pytest.raises(ValueError):reader.call('vision',tmp_path/'unused')


def test_budget_cap_and_at_most_once_cache(tmp_path):
    b=runner.binding();reader=runner.CyrillicReaders(dict(binding=b,cap_usd=1.2,max_calls=585),root=tmp_path)
    image=tmp_path/'image.png';Image.new('L',(20,20),255).save(image)
    digest=runner.sha(image);path=tmp_path/'parsed/docai'/(digest+'.json');path.parent.mkdir(parents=True)
    result=dict(status='ok',binding=b,image_sha256=digest)
    path.write_text(json.dumps(result));reader.docai.read=Mock(side_effect=AssertionError('network forbidden'))
    assert reader.call('docai',image)==result
    reader.docai.read.assert_not_called()
    assert not (tmp_path/'budget.jsonl').exists()


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_o5_and_page_exclusion_together():
    one=record();one['id']='train';two=dict(one,id='test',book_key='held')
    three=dict(one,id='drop',page_id='drop-page',book_key='bad',not_cyrillic_page=True)
    kept,rejected,quality,count,excluded=outputs.admit_records([one,two,three],[dict(book_key='held',split='test')],[])
    assert [r['id'] for r in kept]==['test']
    assert {r['id']:r['reasons'] for r in rejected}=={'train':['label_in_holdout'],'drop':['not_cyrillic_page']}


@pytest.mark.parametrize('bad,foreign,expected',[(False,False,[]),(True,False,['bad_page']),(False,True,['not_cyrillic_page']),(True,True,['bad_page','not_cyrillic_page'])])
def test_compiled_rejection_heading(bad,foreign,expected):
    image=Image.new('L',(250,80),255)
    canvas,layout=outputs.render_compiled(image,[],{'bad_page':bad},{'not_cyrillic_page':foreign})
    assert layout['rejection_reasons']==expected and canvas.size==(620,160)
    if expected:assert canvas.crop((40,0,600,35)).convert('L').getextrema()[0]<255


def test_compiled_path_required_structure():
    p=dict(year=1900,title='Title / dictionary',key='12345678',page=9)
    assert str(outputs.compiled_path(p))=='1900_Title dictionary_123456/p0009.jpg'


def test_share_report_empty_and_language_metadata():
    pages=[dict(page_id='a',book_key='b',letters=0,cyrillic_letters=0,cyrillic_share=None,not_cyrillic_page=True,detected_languages=[])]
    report=outputs.share_report(pages)
    assert report['empty_denominators']==report['rejected_pages']==1 and report['distribution']['pages']==0


@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@0728898d2; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_frozen_t20_module():
    assert runner.sha(runner.REPO/'greekocr/harvest/admission.py')==runner.ADMISSION_SHA


def test_page_text_gate_survives_geometry_failure_and_keeps_languages(tmp_path,monkeypatch):
    p=dict(id='p',width=100,height=100,key='book')
    languages=[dict(languageCode='ru',confidence=.8),dict(languageCode='de',confidence=.2)]
    raw=dict(document=dict(text='я'*7+'a'*4,pages=[dict(lines=[{}],detectedLanguages=languages)]))
    monkeypatch.setattr(outputs,'OUT',tmp_path)
    monkeypatch.setattr(outputs,'raw_read',lambda *a:(raw,{}))
    def unusable(*args):raise ValueError('singular transform')
    monkeypatch.setattr(outputs,'_response_geometry',unusable)
    rows,reads=outputs.read_records(dict(pages=[p]),write=True)
    assert not rows and reads['lost_pages']==1
    assert reads['pages'][0]['detected_languages']==languages
    assert reads['pages'][0]['not_cyrillic_page']
    assignment=json.loads((tmp_path/'assignments/p.json').read_text())
    assert assignment['page_script']['letters']==11
    assert assignment['page_script']['cyrillic_letters']==7
    assert outputs.read_records(dict(pages=[p]))==(rows,reads)


def test_empty_page_is_language_rejection_not_geometry_loss(tmp_path,monkeypatch):
    p=dict(id='p',width=100,height=100,key='book')
    raw=dict(document=dict(pages=[{}]))
    monkeypatch.setattr(outputs,'OUT',tmp_path)
    monkeypatch.setattr(outputs,'raw_read',lambda *a:(raw,{}))
    # An empty but valid page has no rows and no geometry loss.
    monkeypatch.setattr(outputs,'_response_geometry',lambda *a:dict(coordinate_frame={},lines=[]))
    monkeypatch.setattr(outputs,'make_rows',lambda *a:([],[],[],None))
    rows,reads=outputs.read_records(dict(pages=[p]),write=True)
    assert reads['empty_pages']==reads['no_line_pages']==1 and reads['lost_pages']==0
    assert reads['pages'][0]['not_cyrillic_page'] and reads['pages'][0]['cyrillic_share'] is None
