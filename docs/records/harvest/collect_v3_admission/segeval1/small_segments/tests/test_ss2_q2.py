"""Hand-computable SS2 grouping, concentration, density and page-proxy checks."""
import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ss2_q2 as q


@pytest.mark.parametrize('row_id,expected',[
 ('gazette_modern--aeb6--s012-l0001',('gazette_modern--aeb6','gazette_modern--aeb6--s012','double_dash_s')),
 ('129cff40-p000009-l0107',('129cff40','129cff40-p000009','collection_v2')),
 ('other--l123',('other','other','fallback')),
 ('other-l99',('other','other','fallback')),
 ('odd_identifier',('odd_identifier','odd_identifier','fallback')),
])
def test_ids(row_id,expected):
    assert q.book_page(row_id)==expected


def test_page_grouping():
    a=q.book_page('b--s001-l0001')
    b=q.book_page('b--s001-l0002')
    c=q.book_page('b--s002-l0001')
    assert a[:2]==b[:2]
    assert a[0]==c[0] and a[1]!=c[1]
    assert q.book_page('x-p01-l01')[:2]==q.book_page('x-p01-l02')[:2]


def test_concentration_with_ties():
    r=q.concentration([4,3,3,0])
    assert [r[f'books_for_{p}pct'] for p in [50,80,95]]==[2,3,3]
    assert r['books_with_rows']==3
    assert r['top_1_share_pct']==40
    assert q.concentration([5,5])['books_for_50pct']==1
    assert q.concentration([])['books_for_95pct']==0
    assert q.concentration([])['top_1_share_pct'] is None


def test_density_excludes_under_50_and_tie_order():
    books=pd.DataFrame([dict(book='tiny',rows=49,small_rows=49,density_pct=100),
        dict(book='b',rows=50,small_rows=25,density_pct=50),
        dict(book='a',rows=100,small_rows=50,density_pct=50)])
    assert [r['book'] for r in q.ranked_books(books,density=True)]==['a','b']
    assert q.ranked_books(books)[1]['book']=='tiny'


def test_proxies_are_distinct_and_inclusive():
    pages=pd.DataFrame([dict(rows=4,small_rows=1,numeric_rows=2,numeric=0,mixed=1,nonnumeric=0),
        dict(rows=4,small_rows=2,numeric_rows=1,numeric=1,mixed=0,nonnumeric=1),
        dict(rows=4,small_rows=3,numeric_rows=3,numeric=2,mixed=0,nonnumeric=1),
        dict(rows=4,small_rows=0,numeric_rows=0,numeric=0,mixed=0,nonnumeric=0)])
    masks=q.page_proxies(pages)
    assert list(masks['numeric_ge_50pct'])==[True,False,True,False]
    assert list(masks['small_ge_50pct'])==[False,True,True,False]
    result=q.page_summary(pages)
    a,b=result['table_like_proxies']
    assert a['small_rows']==4 and a['share_of_all_small_pct']==pytest.approx(100*4/6)
    assert b['small_rows']==5 and b['numeric']==3
    assert result['isolated']==dict(pages=1,small_rows=1,numeric=0,mixed=1,nonnumeric=0)
    assert q.ratio_bucket(2,4,[10,25,50,75,90,100])==2


def test_page_counts_use_all_rows_for_numeric_share():
    df=pd.DataFrame([dict(book='b',page='p',output_type=t) for t in ['numeric','numeric','mixed','nonnumeric']])
    small=df.iloc[[2]]
    page=q.page_table(df,small).iloc[0]
    assert (page.rows,page.small_rows,page.numeric_rows,page.mixed)==(4,1,2,1)
