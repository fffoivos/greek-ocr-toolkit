"""Offline T24 join/filter/stratification contracts; small Parquet/JSONL fixtures."""
from collections import Counter
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from greekocr.harvest import openarchives as oa


def pipe(**values):
    return dict(dict(download_success=True, ocr_success=True, filter='ok', is_empty=False,
        percentage_greek=90, mojibake_badness_score=0, greek_badness_score=1,
        page_count=100, latin_percentage=5, char_count_no_comments=120000), **values)


def external(ident='a', repo='repo', status=200, url=None):
    return dict(collection_slug=repo, edm_url=f'https://www.openarchives.gr/edm/{repo}/{ident}',
        external_link=f'https://repo.invalid/handle/{ident}', type='thesis', language_code='ELL',
        status_code=status, pdf_links_json=json.dumps([url or f'https://repo.invalid/{ident}.pdf']))


def document(ident='a', repo='repo', **values):
    return dict(source_metadata=dict(collection_slug=repo, filename=ident+'.pdf', type='thesis',
        pdf_links_json=f'https://repo.invalid/{ident}.pdf', metadata_json=json.dumps(
        {'Τίτλος':'Δοκιμή', 'Χρονολογία':'1995 (EL)', 'Δημιουργός':'Author (1850-1900)'})),
        pipeline_metadata=pipe(**values))


@pytest.fixture
def files(tmp_path):
    def write(links, docs):
        parquet=tmp_path/'links.parquet'
        pq.write_table(pa.Table.from_pylist(links), parquet)
        jsonl=tmp_path/'doc_metadata.jsonl'
        jsonl.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in docs))
        return parquet, jsonl
    return write


def test_parquet_jsonl_join_and_pool_median_after_other_filters(files):
    links=[external(i) for i in ('a','b','c','dead')]
    links[-1]['status_code']=404
    docs=[document('a',greek_badness_score=1), document('b',greek_badness_score=3),
          document('c',greek_badness_score=5), document('dead',greek_badness_score=0),
          document('unmatched',greek_badness_score=0)]
    pool,w5,r=oa.build_pool(*files(links,docs))
    assert [p['source_metadata']['filename'] for p in pool]==['a.pdf','dead.pdf','unmatched.pdf']
    assert r['median_greek_badness']==1
    assert r['counts']['external_status_200']==3
    assert r['join_coverage']==4/5 and r['external_rows_joined']==4
    assert r['pool_with_year']==3 and r['pool_year_share']==1
    assert w5==[]


def test_null_scores_pass_unchanged_and_do_not_weight_median(files):
    pool,w5,r=oa.build_pool(*files([external()], [document(mojibake_badness_score=None,greek_badness_score=None)]))
    assert len(pool)==1 and w5==[] and r['median_greek_badness'] is None
    assert pool[0]['pipeline_metadata']['mojibake_badness_score'] is None
    assert pool[0]['pipeline_metadata']['greek_badness_score'] is None
    assert r['counts']['mojibake_zero']==1
    assert r['scanned_mojibake_score_inventory']=={'null':1}


def test_median_only_measured_scores_null_passes(files):
    docs=[document('a',greek_badness_score=None),document('b',greek_badness_score=2),
          document('c',greek_badness_score=8)]
    pool,_,r=oa.build_pool(*files([external(i) for i in 'abc'],docs))
    assert r['median_greek_badness']==5 and r['measured_greek_badness_documents']==2
    assert [p['source_metadata']['filename'] for p in pool]==['a.pdf','b.pdf']


def test_empty_scanned_pool_has_defined_coverage(files):
    pool,_,r=oa.build_pool(*files([external()], [document(ocr_success=False)]))
    assert not pool and r['scanned_join_coverage']==0


def test_duplicate_document_does_not_weight_median(files):
    pool,_,r=oa.build_pool(*files([external('a'),external('b')],
        [document('a',greek_badness_score=0)]*4+[document('b',greek_badness_score=10)]))
    assert len(pool)==1 and r['median_greek_badness']==5
    assert r['counts']['duplicate_document_rows']==3


def test_join_requires_collection_and_full_url():
    index=oa.LinkIndex([external()])
    assert index.join(document())==([0],'collection_url')
    assert index.join(document(repo='different'))==([],None)
    r=document();r['source_metadata']['pdf_links_json']='https://other.invalid/a.pdf'
    assert index.join(r)==([],None)


def test_edm_fallback_only_when_explicitly_present():
    index=oa.LinkIndex([external()]);r=document('different')
    r['source_metadata']['edm_url']=external()['edm_url']
    assert index.join(r)==([0],'edm_url')


def test_multiple_matches_prefer_recorded_status_200():
    index=oa.LinkIndex([external(status=404), external(status=200)])
    assert index.join(document())==([1,0],'collection_url')


def test_html_entities_percent_encoding_and_fragment_join():
    url='https://repo.invalid/δοκιμή.pdf?sequence=1&isAllowed=y'
    index=oa.LinkIndex([external(url=url)])
    r=document();r['source_metadata']['pdf_links_json']='https://REPO.invalid/%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE.pdf?sequence=1&amp;isAllowed=y#fragment'
    assert index.join(r)==([0],'collection_url')


@pytest.mark.parametrize('a,b', [
    ('https://r.invalid/a%2Fb.pdf','https://r.invalid/a/b.pdf'),
    ('https://r.invalid/a%3Fb.pdf','https://r.invalid/a?b.pdf'),
    ('https://r.invalid/a.pdf?a=x%26b=y','https://r.invalid/a.pdf?a=x&b=y'),
    ('https://r.invalid/a.pdf?sequence=1','https://r.invalid/a.pdf?sequence=2'),
])
def test_url_components_are_not_conflated(a,b):
    assert oa.canonical_url(a)!=oa.canonical_url(b)


@pytest.mark.parametrize('value,expected', [
    ('https://r.invalid/a.pdf',['https://r.invalid/a.pdf']),
    ('["https://r.invalid/a.pdf"]',['https://r.invalid/a.pdf']),
    ('"https://r.invalid/a.pdf"',['https://r.invalid/a.pdf']),
    (None,[]), ('broken',[]), ('{}',[]), ('[1,null]',[]),
])
def test_url_shapes(value,expected):
    assert oa.urls(value)==expected


@pytest.mark.parametrize('field,value', [
    ('download_success',False), ('download_success',None), ('ocr_success',False), ('ocr_success','true'), ('filter','ocr_noise'),
    ('is_empty',True), ('is_empty',None), ('percentage_greek',79.999),
    ('percentage_greek',None),
    ('mojibake_badness_score',False), ('mojibake_badness_score',.01),
    ('page_count',19), ('page_count',601), ('page_count',None),
    ('greek_badness_score',False), ('greek_badness_score',float('nan')),
])
def test_each_filter_fails_closed(field,value):
    assert not all(ok for _,ok in oa.base_filters(pipe(**{field:value})))


@pytest.mark.parametrize('pages',[20,600])
def test_inclusive_filter_boundaries(pages):
    assert all(ok for _,ok in oa.base_filters(pipe(page_count=pages,percentage_greek=80,mojibake_badness_score=0)))


def test_wave5_keeps_mixed_scanned_with_null_scores_and_low_greek(files):
    docs=[document('a',percentage_greek=60,latin_percentage=20,mojibake_badness_score=None),
          document('b',percentage_greek=40,latin_percentage=50),
          document('c',latin_percentage=19.99), document('d',latin_percentage=50.01),
          document('e',ocr_success=False,latin_percentage=30)]
    _,w5,r=oa.build_pool(*files([external(i) for i in 'abcde'],docs))
    assert [w['source_metadata']['filename'] for w in w5]==['a.pdf','b.pdf']
    assert r['wave5_count']==2 and all(w['external_status_200'] for w in w5)


def test_wave5_preserves_unmatched_scanned_candidate_for_next_wave(files):
    _,w5,_=oa.build_pool(*files([external()], [document('missing',latin_percentage=30)]))
    assert len(w5)==1 and w5[0]['external_status_200'] is False and w5[0]['join_method'] is None


def test_partial_metadata_is_never_consumed(files):
    args=files([external()],[document()])
    args[1].with_suffix('.jsonl.partial').write_text('partial')
    with pytest.raises(RuntimeError,match='not ready'):oa.build_pool(*args)


@pytest.mark.parametrize('meta,year', [
    ({'Χρονολογία':'1995 (EL)','Ημερομηνία έκδοσης':'2010-03-29T00:00:00Z'},1995),
    ({'dc.date.issued':'1983','dc.date.accessioned':'2026'},1983),
    ({'Ημερομηνία':'2007'},2007),
    ({'Τίτλος':'Athens 1995','Δημιουργός':'Author (1850-1900)'},None),
    ({'date.available':'2026'},None), ({},None),
])
def test_year_only_from_date_fields(meta,year):
    assert oa.extract_year(meta)[0]==year


@pytest.mark.parametrize('value,expected', [
    ('thesis','thesis'), ('PhD Thesis / Διδακτορική Διατριβή','thesis'),
    ('άρθρο','article'), ('Article','article'), ('βιβλίο','book'), ('book','book'),
    ('text','other'), (None,'other'),
])
def test_type_mapping(value,expected):
    assert oa.document_type(value)==expected


def books(repos=20, each=20):
    return [dict(book=f'{repo:03d}-{i:04d}',key=f'{repo:03d}-{i:04d}',
        title='Δοκιμή',collection_slug=f'repo_{repo:03d}',year=1980+(i%4)*10,
        decade=1980+(i%4)*10,type=('thesis','article','book','other')[i%4])
        for repo in range(repos) for i in range(each)]


def test_overdraw_is_seeded_order_invariant_and_caps_every_prefix():
    rows=books();draw=oa.stratified_draw(rows)
    assert len(draw)==173 and len({r['book'] for r in draw})==173
    assert draw==oa.stratified_draw(rows[::-1])
    assert draw!=oa.stratified_draw(rows,seed=1)
    for n in (130,173):
        assert max(Counter(r['collection_slug'] for r in draw[:n]).values())<=10
    assert len({r['collection_slug'] for r in draw[:130]})==20
    assert {r['type'] for r in draw}=={'thesis','article','book','other'}
    assert {r['decade'] for r in draw}=={1980,1990,2000,2010}


def test_unknown_decade_is_explicit_and_not_discarded():
    rows=books(1,4);rows[0].update(year=None,decade=None)
    assert any(r['decade'] is None for r in oa.stratified_draw(rows,4))


def test_repository_capacity_shortfall_is_not_relaxed():
    draw=oa.stratified_draw(books(12),173)
    assert len(draw)==120 and max(Counter(r['collection_slug'] for r in draw).values())==10
    assert oa.stratified_draw([])==[]


def test_duplicate_draw_identity_fails():
    rows=books();rows.append(rows[0])
    with pytest.raises(ValueError,match='duplicate'):oa.stratified_draw(rows)


def test_holdout_is_20_documents_15_test_5_dev_and_repository_stratified():
    rows=oa.stratified_draw(books(),130)
    held=oa.holdout(rows)
    assert held==oa.holdout(rows[::-1]) and held!=oa.holdout(rows,seed=1)
    assert len(held)==len({r['book_key'] for r in held})==20
    assert Counter(r['split'] for r in held)=={'test':15,'dev':5}
    assert len({r['collection_slug'] for r in held})==20
    assert {r['book_key'] for r in held}<={r['key'] for r in rows}


def test_holdout_capacity_shortfall_and_key_collision_fail():
    with pytest.raises(ValueError,match='insufficient'):oa.holdout(books(1,19))
    rows=books();rows[1]['key']=rows[0]['key']
    with pytest.raises(ValueError,match='duplicate'):oa.holdout(rows)
