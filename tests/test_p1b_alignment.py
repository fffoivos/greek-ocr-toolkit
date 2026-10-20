"""Printed-edge and margin release invariants; no network or provider calls."""
import sys
from pathlib import Path
import unicodedata as ud
import pytest

PILOT = Path(__file__).resolve().parents[1]/'docs/records/harvest/pilots_v2'
sys.path.insert(0,str(PILOT))
from p1b_align import repair_tei_node, margin_numerals
from align import align_page, normal


def run(prooftext, texts, pilot='wikisource', body_start=0):
    # A literal XML-like owner for every NFD source atom, with stable raw offsets.
    source=normal(prooftext)
    proof=dict(text=source, owners=[dict(xpath='/p',field='text',nfd_offset=i) for i in range(len(source))],
               raw_path='fixture.xml',status='test',transformations=[],body_start=body_start)
    page=dict(id='p',pilot=pilot,item='test',height=1000,page=1,text_revision='r',text_sha256='t',image_sha256='i')
    lines=[dict(id=f'l{i}',docai_raw_text=s,text=s,bbox=[10,300+i*40,900,330+i*40],geometry_positive=False,
                crop_path='fixture.png',crop_sha256='c',script_class='greek_poly',mixed_line=False,line_tags=[]) for i,s in enumerate(texts)]
    return align_page(page,lines,proof)[0]


@pytest.mark.parametrize('glyph',['-','‐','‑'])
def test_joined_word_requires_and_keeps_printed_hyphen(glyph):
    rows=run('τοὺς στρατιώτας καὶ τοὺς ἄλλους',['τοὺς στρα'+glyph,'τιώτας καὶ τοὺς ἄλλους'])
    assert all(r['accepted'] for r in rows)
    assert rows[0]['human_label']=='τοὺς στρα'+glyph
    assert rows[1]['human_label'].startswith('τιώτας')
    assert rows[0]['source_span_nfd'][1]==rows[1]['source_span_nfd'][0]
    assert 'carried_word_fragment' in rows[1]['flags']
    assert rows[0]['edge_glyph_ownership'][-1]['text']==glyph


def test_inside_word_without_printed_edge_is_withheld():
    rows=run('τοὺς στρατιώτας καὶ τοὺς ἄλλους',['τοὺς στρα','τιώτας καὶ τοὺς ἄλλους'])
    assert not rows[0]['accepted']
    assert 'ends_inside_proofread_word_without_printed_edge' in rows[0]['reasons']


@pytest.mark.parametrize('glyph',['’','ʼ','᾿',"'"])
def test_elision_edge_is_kept(glyph):
    r=run('καὶ τοὺς ὑπ αὐτὸν στρατιώτας',['καὶ τοὺς ὑπ'+glyph,'αὐτὸν στρατιώτας'])[0]
    assert r['accepted'] and r['human_label'].endswith(glyph)


@pytest.mark.parametrize('glyph',['— ','– ','«','“','"'])
def test_left_dialogue_or_quote_is_kept(glyph):
    r=run('Καλημέρα πάτερ Ἄνθιμε',[glyph+'Καλημέρα πάτερ Ἄνθιμε'])[0]
    assert r['accepted'] and r['human_label'].startswith(glyph)


@pytest.mark.parametrize('glyph',['”','»','—'])
def test_right_quote_or_dash_is_kept(glyph):
    r=run('Καλημέρα πάτερ Ἄνθιμε',['Καλημέρα πάτερ Ἄνθιμε'+glyph])[0]
    assert r['accepted'] and r['human_label'].endswith(glyph)


def test_page_carry_owns_only_printed_tail():
    source=normal('ἐκέλευσε, τήν τε ἔξοδον ἐπήγγειλε')
    r=run(source,['λευσε, τήν τε ἔξοδον ἐπήγγειλε'],body_start=len(normal('ἐκέλευσε, '))+1)[0]
    assert r['accepted'] and r['human_label'].startswith('λευσε,')
    assert 'cross_page_tei_fragment' in r['flags']
    assert r['source_span_nfd'][0]>0


@pytest.mark.parametrize('raw,want',[('Σἑ??ʼῆρος','Σεȣῆρος'),('Ῥἁ??ʼέννης','Ῥαȣέννης'),('Ἀδ̔??ʼέντον','Ἀδȣέντον'),('Σεȣῆρος','Σεȣῆρος')])
def test_ou_preserved_or_explicitly_repaired(raw,want):
    text,mapping,repairs=repair_tei_node(raw)
    assert ud.normalize('NFC',text)==want
    assert len(mapping)==len(text)
    assert not repairs or repairs[0]['emitted']=='ȣ'


def test_unadjudicated_corruption_is_not_guessed():
    text,_,changes=repair_tei_node('μ̔??ʼστηρίων')
    assert '??' in text and not changes


def line():return dict(bbox=[0,0,1000,80],crop_bbox=[0,0,1000,80],row_xheight=30)
def token(text,x0,x1):return dict(text=text,bbox=[x0,10,x1,65])


@pytest.mark.parametrize('tokens',[[token('15',10,35),token('λόγος',100,900)],[token('λόγος',100,900),token('5',960,980)],[token('2',10,25),token('λόγος',100,900),token('15',960,995)]])
def test_separate_margin_numeral_is_identified(tokens):
    assert len(margin_numerals(line(),tokens))==sum(t['text'].isdigit() for t in tokens)


def test_internal_prose_numeral_is_not_margin():
    assert not margin_numerals(line(),[token('ἔτους',20,300),token('15',320,360),token('λόγος',380,950)])


def test_numeral_outside_crop_is_not_contamination():
    assert not margin_numerals(dict(line(),crop_bbox=[80,0,950,80]),[token('15',10,35),token('λόγος',100,900)])


def test_neighbour_line_number_does_not_contaminate():
    assert not margin_numerals(line(),[dict(token('15',10,35),bbox=[10,100,35,150]),token('λόγος',100,900)])


def test_margin_is_a_release_veto_even_with_perfect_alignment():
    # Exercise the admission path, not just its geometric predicate.
    # Use full align API with a precomputed geometric witness.
    source=normal('οὗτος ἦν ὁ λόγος')
    proof=dict(text=source,owners=[dict(xpath='/p',field='text',nfd_offset=i) for i in range(len(source))],raw_path='fixture.xml',status='test',transformations=[])
    page=dict(id='p',pilot='wikisource',item='x',page=1,height=1000,text_revision='r',text_sha256='t',image_sha256='i')
    r=dict(id='l',docai_raw_text=source,text=source,bbox=[0,200,1000,280],geometry_positive=False,crop_path='c',crop_sha256='s',script_class='greek_poly',mixed_line=False,line_tags=[],margin_numerals=[dict(text='15',bbox=[0,210,30,270])])
    result=align_page(page,[r],proof)[0][0]
    assert not result['accepted'] and result['human_label'] is None
    assert 'margin_numeral_in_crop' in result['reasons']


def test_proofreader_disagreement_is_flag_not_veto():
    r=run('ΣΠΥΡΟΣ ΧΑΡΑΛΑΜΠΑΚΗΣ',['ΣΠΥΡΟΣ ΧΑΡΑΛΑΜΠΗΣ'])[0]
    assert r['accepted'] and r['disagrees_with_page_read']
    assert r['human_label']=='ΣΠΥΡΟΣ ΧΑΡΑΛΑΜΠΑΚΗΣ'


def test_printed_ano_teleia():
    r=run('τὴν ἔξοδον ἐπήγγειλε: νομάς',['τὴν ἔξοδον ἐπήγγειλε· νομάς'])[0]
    assert r['accepted'] and '·' in r['human_label'] and ':' not in r['human_label']
    assert r['printed_corrections'][0]['rule']=='printed_ano_teleia'
