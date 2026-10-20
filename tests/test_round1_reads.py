"""Offline T17 tier, Vision attachment, confidence and review contracts."""
import base64
import io
import json
import re

from PIL import Image
import pytest

from greekocr.harvest.round1_reads import (line_tier, letter_count, attach_vision, symbol_confidences,
    cohort_summary, median_page, book_folder, numbered_image, page_text, review_html)
from scripts.harvest.round1_reads import select_pages
from greekocr.harvest.readers import Readers


def line(text, bbox):
    return dict(text=text, bbox=bbox)


@pytest.mark.parametrize('docai,vision,tier', [
    ('ἅλφα', 'ἅλφα', 1), ('λόγος.', 'λόγος,', 2), ('λ όγος', 'λόγος', 2),
    ('λόγος 2', 'λόγος 3', 2), ("ἀλλ᾽", "ἀλλʼ", 2), ('λόγος', 'λογος', 3),
    ('Λόγος', 'λόγος', 3), ('σ', 'ς', 3), ('καὶ', 'κὶ', 3),
    ('', '', 3), ('λόγος', '', 3), ('123', '123', 3), ('λόγος', 'λόγος', 1),
])
def test_strict_tiers_docai_label(docai, vision, tier):
    result = line_tier(docai, vision)
    assert result == dict(tier=tier, label=docai if tier < 3 else None)


def test_rejected_reading_cannot_earn_label():
    assert line_tier('λόγος', 'λόγος', usable=False) == dict(tier=3, label=None)


def test_apostrophe_marks_letter_count():
    assert letter_count('ἅλφαʼ 123') == 4
    assert letter_count('ἀβ') == 2


def test_exact_accepted_scope_only():
    selection = dict(books=[dict(book=str(d), decade=d, key=str(d), title='x', year=d) for d in range(1860, 1940, 10)])
    manifest = dict(pages=[dict(book=str(d), page=i, harvest_accepted=accepted) for d in range(1860,1940,10) for i,accepted in ((1,True),(2,False),(3,None))])
    assert [(p['book'],p['page']) for p in select_pages(selection, manifest)] == [('1860',1),('1870',1),('1880',1)]


def test_overlap_single_and_missing():
    docai = [line('λόγος', [10,10,90,20]), line('άλλος', [10,40,90,50])]
    result = attach_vision(docai, [line('λογος', [10,10,90,20])])
    assert result['results'][0]['method'] == 'box_overlap'
    assert result['results'][1]['method'] == 'unresolved'
    assert not result['results'][1]['usable']


def test_overlap_boundaries_70_50():
    result = attach_vision([line('αλφα', [10,10,90,20])], [line('βητα', [50,13,130,23])])
    assert result['results'][0]['method'] == 'box_overlap'


def test_side_by_side_pieces_join_in_x_order():
    result = attach_vision([line('αλφα βητα', [0,10,100,20])],
                           [line('βητα',[60,10,100,20]), line('αλφα',[0,10,45,20])])
    a = result['results'][0]
    assert a['text'] == 'αλφα βητα' and a['method'] == 'box_overlap'
    assert 'horizontal_pieces_joined' in a['flags']


def test_stacked_pieces_retained_but_rejected():
    result = attach_vision([line('αλφα βητα', [0,0,100,40])],
                           [line('αλφα',[0,0,80,10]), line('βητα',[0,30,80,40])])
    assert not result['results'][0]['usable']
    assert 'stacked_bands' in result['results'][0]['flags']
    assert 'αλφα' in result['results'][0]['text']


def test_ambiguous_touch_resolved_by_mutual_text():
    docai = [line('αλφα', [0,10,90,20]), line('βητα',[0,21,90,31])]
    result = attach_vision(docai, [line('αλφα',[0,10,90,22])])
    a,b = result['results']
    assert a['method'] == 'text_alignment' and a['vision_indices'] == [0]
    assert a['alignment']['score'] == 1
    assert b['method'] == 'unresolved' and not b['usable']


def test_repeated_text_tie_never_guessed_or_shared():
    docai = [line('αλφα',[0,10,90,20]), line('αλφα',[0,21,90,31])]
    result = attach_vision(docai,[line('αλφα',[0,10,90,22])])
    assert all(a['method']=='unresolved' for a in result['results'])
    assert result['unassigned_vision_indices'] == [0]


def test_two_equal_vision_candidates_remain_unresolved():
    result = attach_vision([line('αλφα',[0,0,100,40])],
                           [line('αλφα',[0,0,80,10]), line('αλφα',[0,30,80,40])])
    assert result['results'][0]['method']=='unresolved'


def test_text_match_without_overlap_not_attached():
    result = attach_vision([line('αλφα',[0,0,80,10])], [line('αλφα',[0,100,80,110])])
    assert result['results'][0]['method'] == 'unresolved'


def test_foreign_script_kept_rejected():
    result = attach_vision([line('αλφα',[0,0,80,10])],[line('漢字',[0,0,80,10])])
    assert not result['results'][0]['usable'] and 'garbage' in result['results'][0]['flags']


def test_confidence_anchor_custody_and_missing_confidence():
    def layout(a,b,c=None):
        return dict(layout=dict(textAnchor=dict(textSegments=[dict(startIndex=a,endIndex=b)]), confidence=c))
    document = dict(pages=[dict(lines=[layout(0,4),layout(4,8)], symbols=[layout(0,1,.9),layout(2,3,None),layout(3,5,.2),layout(5,6,.7)])])
    a,b=symbol_confidences(document)
    assert a['symbol_indices']==[0,1] and a['symbol_confidences']==[.9] and a['mean']==.9
    assert b['symbol_indices']==[3] and b['mean']==.7


def row(i=1, tier=1, counted=True, page_id='a'):
    return dict(id=str(i),page_id=page_id,line_number=i,tier=tier,counted=counted,bbox=[20,20+i*20,180,35+i*20],
                docai_text='<script>αλφα &',vision_text='βητα >',confidence=.9,symbol_confidences=[.8,1.],
                flags=[],attachment_method='box_overlap')


def page(ident='a', number=1):
    return dict(id=ident,page=number,year=1860,title='τίτλος < & / :',book='book',key='abc',decade=1860,width=200,height=200)


def test_short_line_denominator_and_symbol_weighting():
    c=cohort_summary([page()], [row(1),row(2,2),row(3,3),row(4,1,False)])
    assert (c['lines'],c['records'],c['short_lines'],c['labels'])==(3,4,1,2)
    assert c['label_yield_pct']==pytest.approx(200/3) and c['mean_confidence']==.9 and c['symbol_count']==6


def test_empty_cohort_pages_stay_counted():
    c=cohort_summary([page()],[])
    assert c['pages']==1 and c['lines']==0 and c['label_yield_pct']==0 and c['mean_confidence'] is None


def test_median_yield_lower_middle_ties():
    pages=[page(c,i+1) for i,c in enumerate('abcd')]
    rows=[row(1,3,page_id='a'),row(1,2,page_id='b'),row(2,3,page_id='b'),row(1,1,page_id='c'),row(1,1,page_id='d')]
    assert median_page(pages,rows)['id']=='b'
    assert median_page([pages[2],pages[3]],rows)['id']=='c'


def test_finder_utf8_safe_folder_and_text():
    p=page();p['title']='ἅλφα/βητα:'*200
    folder=book_folder(p)
    assert len(folder.encode())<255 and '/' not in folder and ':' not in folder
    text=page_text(p,[row(1,2),row(2,3,False)])
    assert '001 | tier 2' in text and '002 | tier 3' in text and 'short: excluded' in text


def test_review_builder_escape_fold_images_and_numbers(tmp_path):
    path=tmp_path/'page.png';Image.new('L',(200,200),255).save(path)
    rows=[row(1),row(2,2),row(3,3)]
    result=review_html(1860,[(page(),rows,path)])
    assert '<script>' not in result and '&lt;script&gt;' in result and 'τίτλος &lt; &amp;' in result
    assert result.count('data-line=')==3 and result.count('<details>')==1
    assert all(f'class="tier{i}"' in result for i in (1,2,3))
    encoded=re.findall('data:image/webp;base64,([A-Za-z0-9+/=]+)',result)
    assert len(encoded)==1
    with Image.open(io.BytesIO(base64.b64decode(encoded[0]))) as im:
        assert im.size==(200,200) and im.format=='WEBP'
    image=numbered_image(path,rows)
    assert image.size==(200,200) and image.getpixel((20,40))==(0,141,66)


def test_review_downscale_preserves_aspect_ratio(tmp_path):
    path=tmp_path/'page.png';Image.new('L',(2400,4000),255).save(path)
    image=numbered_image(path,[],max_size=(1200,1600))
    assert image.size==(960,1600)


def test_at_most_once_cache_and_interrupted_attempt_no_network(tmp_path):
    path=tmp_path/'page.png';Image.new('L',(20,20),255).save(path)
    readers=Readers(tmp_path/'google',cap=2)
    import hashlib
    key=hashlib.sha256(path.read_bytes()).hexdigest()
    readers.budget.reserve('vision',key)
    def forbidden(*args,**kwargs): raise AssertionError('network forbidden')
    readers.vision.read_annotation=forbidden
    first=readers.call('vision',path)
    assert first['error_class']=='InterruptedReservedAttempt'
    assert readers.call('vision',path)==first
    assert readers.budget.receipt()['calls_reserved']==1
