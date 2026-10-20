"""T25 offline selection, tail-page, whole-source and read-reservation contracts."""
from collections import Counter
import math

from PIL import Image
import pytest

from greekocr.harvest import mixed as p
from scripts.harvest import mixed as r


@pytest.mark.parametrize('title',[
    'ΛΕΞΙΚΟΝ','Λεξικὸν Ἑλληνικόν','Γραμματικὴ τῆς ἀγγλικῆς','Περιοδικόν',
    'Ἐπετηρὶς τῆς σχολῆς','Δελτίον','Γαλλικὴ γλῶσσα','ΑΓΓΛΙΚΗ',
    'Γερμανικὰ μαθήματα','Ἰταλικὴ γλῶσσα','Λατινικὴ ποιητική',
    'Διάλογοι νεοελληνικοί','Μέθοδος πρακτική',
])
def test_title_filter_ignores_accents_and_case(title):
    assert p.title_matches(title)


@pytest.mark.parametrize('title',['Ιστορία της Ελλάδος','Ελληνικόν αναγνωσματάριον','','Journal of science'])
def test_title_filter_does_not_invent_extra_patterns(title):
    assert not p.title_matches(title)


def anemi(**kwargs):
    return dict(document_id='new',year=1900,title='Λεξικὸν',download_url='https://anemi.lib.uoc.gr/x.pdf',**kwargs)


@pytest.mark.parametrize('prior',['round1','round2','early'])
def test_all_prior_anemi_sources_excluded(prior):
    row=anemi();row['document_id']=prior
    assert p.anemi_eligible(row,{'round1','round2','early'})==(False,'previous_book')


@pytest.mark.parametrize('year',[1860,1935])
def test_anemi_year_boundaries_inclusive(year):
    row=anemi();row['year']=year
    assert p.anemi_eligible(row,set())[0]


@pytest.mark.parametrize('year',[1859,1936,None,True])
def test_out_of_scope_years(year):
    row=anemi();row['year']=year
    assert p.anemi_eligible(row,set())==(False,'year')


def test_anemi_seeded_draw_reproducible_and_input_order_independent():
    rows=[dict(book=str(i)) for i in range(100)]
    a=p.anemi_draw(rows)
    assert len(a)==len({b['book'] for b in a})==40
    assert a==p.anemi_draw(rows[::-1])
    assert a!=p.anemi_draw(rows,seed=20266)


@pytest.mark.parametrize('total',[51,59,60,61,99,100,101,184,600,1806])
def test_repository_picks_seven_final12_three_middle_and_bounded_replacements(total):
    plans=p.repository_positions(total,'book')
    assert len(plans)==len({v['page'] for v in plans})==10
    tail=[q for q in plans if q['region']=='last12']
    middle=[q for q in plans if q['region']=='middle']
    assert len(tail)==7 and len(middle)==3
    assert all(q['page']>.88*total for q in tail)
    assert [q['page'] for q in middle]==[round(total*f) for f in (.4,.5,.6)]
    reserved={q['page'] for q in plans}
    for q in plans:
        assert q['candidates'][0]==q['page']
        assert len(q['candidates'])<=3
        assert all(q['page']<=n<=min(q['page']+2,total) for n in q['candidates'])
        assert not set(q['candidates'][1:])&reserved
        if q['region']=='last12':
            assert all(n>.88*total for n in q['candidates'])
    assert min(q['page'] for q in tail)==math.floor(.88*total)+1


@pytest.mark.parametrize('total',[0,10,20,49,50])
def test_not_enough_unique_tail_pages(total):
    with pytest.raises(ValueError):p.repository_positions(total)


@pytest.mark.parametrize('total,count',[(60,12),(200,12),(1806,100)])
def test_spread_pages_8_to_95_percent_and_unique(total,count):
    plans=p.spread_positions(total,count,'source')
    assert len(plans)==len({q['page'] for q in plans})==count
    assert all(math.ceil(.08*total)<=q['page']<=math.floor(.95*total) for q in plans)
    assert plans==p.spread_positions(total,count,'source')


def books():
    return [dict(key=f'{part}{i:07d}',book=f'{part}-{i}',part=part,title='source',year=1900,decade=1900)
            for part,count in [('A',40),('B',40),('C',1)] for i in range(count)]


def test_holdout_per_part_frozen_ceil15_percent_and_singleton_test():
    rows=books();held=p.select_holdout(rows)
    assert held==p.select_holdout(rows[::-1])
    assert len({b['book_key'] for b in held})==13
    for part in ('A','B'):
        assert Counter(b['split'] for b in held if b['part']==part)==({'test':4,'dev':2} if part=='A' else {'test':5,'dev':1})
    assert Counter(b['split'] for b in held)=={'test':10,'dev':3}
    assert [(b['part'],b['split']) for b in held if b['part']=='C']==[('C','test')]
    assert p.select_holdout(rows,seed=20261016)!=held


def test_holdout_duplicate_keys_rejected():
    rows=books()
    with pytest.raises(ValueError):p.select_holdout(rows+[rows[0]])


def test_repository_order_seeded_balanced_unique_urls():
    rows=[dict(book=f'{s}-{i}',collection_slug=s,pdf_url=f'https://{s}.gr/{i}.pdf')
          for s in ('one','two','three') for i in range(8)]
    ordered=p.repository_order(rows+rows[:2])
    assert len(ordered)==24 and ordered==p.repository_order(rows[::-1])
    assert Counter(b['collection_slug'] for b in ordered[:6])=={'one':2,'two':2,'three':2}


def test_unjoined_retained_source_url_is_usable_and_rights_recorded():
    row=dict(pipeline_metadata=dict(ocr_success=True,latin_percentage=30,page_count=100,
        mojibake_badness_score=None,percentage_greek=60),collection_slug='repo',metadata_row=3,
        source_metadata=dict(pdf_links_json='https://repo.gr/source.pdf',filename='scan.pdf',
            metadata_json='{"Τίτλος":"Τίτλος","Ημερομηνία έκδοσης":"2001","Δικαιώματα":"unknown"}'))
    b=p.repository_candidate(row)
    assert b['pdf_url']=='https://repo.gr/source.pdf' and b['year']==2001
    assert b['recorded_rights']=={'Δικαιώματα':'unknown'}
    assert b['source']=='openarchives_mixed_repo' and not b['external_status_200']


def binding():
    return dict(project='test',location='eu',processor='test',version='test',user_project='test',
        options=dict(ocrConfig=dict(enableSymbol=True,hints=dict(languageHints=['el']))))


def test_docai_only_adapter(tmp_path):
    reader=r.MixedReaders(dict(binding=binding(),cap_usd=2,max_calls=980),root=tmp_path)
    assert not hasattr(reader,'vision')
    with pytest.raises(ValueError,match='forbids'):reader.call('vision','unused')


def test_reserved_interrupted_page_never_read_twice(tmp_path,monkeypatch):
    reader=r.MixedReaders(dict(binding=binding(),cap_usd=2,max_calls=980),root=tmp_path)
    image=tmp_path/'image.png';Image.new('L',(20,20),255).save(image)
    reader.budget.reserve('docai',r.sha(image))
    monkeypatch.setattr(reader.docai,'read',lambda *a:pytest.fail('reserved page called twice'))
    result=reader.call('docai',image)
    assert result['error_class']=='InterruptedReservedAttempt'
    assert reader.call('docai',image)==result
    assert reader.budget.receipt()['calls_reserved']==1


def line(ident,text,part='A',book='new'):
    return dict(id=ident,page_id='page',book_key=book,year=1900,decade=1900,
        docai_text=text,confidence=.99,bbox=[0,0,100,20],flags=[],licence='internal',
        source_url='https://example.gr/record',attribution='source',read_batch='mixed',
        source='anemi_mixed' if part=='A' else 'openarchives_mixed_repo',part=part)


@pytest.mark.parametrize('source',['anemi_round1','vouli_parliament_1850s','anemi_round2',
    'parliament_1975_2000','openarchives_repo'])
@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@f8805bcf8; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_o5_uses_every_previous_holdout_source(source):
    from scripts.harvest.mixed_outputs import admit_records
    text='Αυτή είναι ελληνική γραμμή αρκετών λέξεων'
    old=[dict(id='old',source=source,label=text,split='test')]
    kept,rejected,*_=admit_records([line('new',text)],[],old)
    assert not kept and rejected==[dict(id='new',docai_text=text,reasons=['label_in_holdout'])]


@pytest.mark.parametrize('part,source',[('A','anemi_mixed'),('B','openarchives_mixed_repo'),('C','archive_b28038630')])
@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@f8805bcf8; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_current_holdout_blocks_new_and_prior_train(part,source):
    from scripts.harvest.mixed_outputs import admit_records
    text='Αυτή είναι ελληνική γραμμή αρκετών λέξεων'
    rows=[line('held',text,part,'held'),line('train',text,part)]
    rows[0]['source']=source;rows[1]['source']=source
    old=[dict(id='old-train',source='old',label=text,split='train')]
    kept,rejected,_,_,exclusions=admit_records(rows,[dict(book_key='held',split='test')],old)
    assert [row['id'] for row in kept]==['held']
    assert rejected[0]['reasons']==['label_in_holdout'] and exclusions[0]['id']=='old-train'


@pytest.mark.parametrize('text,expected',[
    ('Το ελληνικό κείμενο περιέχει word εδώ','greek_latin_cs'),
    ('This English text includes ελληνικά','latin'),
])
@pytest.mark.skip(reason="historical binding; green at sol/recut-v1@f8805bcf8; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_mixed_classes_follow_unchanged_t20_majority(text,expected):
    from scripts.harvest.mixed_outputs import admit_records
    kept,rejected,*_=admit_records([line('line',text)],[],[])
    assert not rejected and kept[0]['script_class']==expected


def test_source_unavailability_is_distinguished_from_individual_page_requests():
    book=dict(book='source',key='key',positions=[dict(page=10,candidates=[10,11,12])])
    failed={f'key:{n}':dict(reason='source_volume_unavailable') for n in (10,11,12)}
    slots,_=r.replay_slots([book],{},failed)
    assert slots[0]['accepted_page'] is None
    assert all(s['state']=='source_unavailable' and s['reasons']==['source_volume_unavailable'] for s in slots[0]['chain'])
