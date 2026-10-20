import pytest
from greekocr.numerics.tokens import tokenize


@pytest.mark.parametrize('text,position,glyphs', [
    ('4·547·331', 'thousands', ['·', '·']),
    ('4·547·331', 'thousands', ['·', '·']),
    ('555,6', 'decimal', [',']),
    ('0-499', 'range', ['-']),
    ('1985-1990', 'range', ['-']),
    ('3.652.450', 'thousands', ['.', '.']),
    ('12 345', 'thousands', [' ']),
    ('4-547-331', 'thousands', ['-', '-']),
    ('1.234,56', 'decimal', [',']),
    ('1985–1990', 'range', ['–']),
    ('1985—1990', 'range', ['—']),
])
def test_grammar(text, position, glyphs):
    token, = tokenize(text)
    assert len(token.slots) == token.digit_count + 1
    assert [s.glyph for s in token.slots if s.position == position] == glyphs
    assert all(text[s.start:s.end] == s.glyph for s in token.slots)


def test_table():
    a, b = tokenize('97.400 | 3.652.450')
    assert a.slots[-1].position == b.slots[0].position == 'table_boundary'
    assert sum(s.position == 'thousands' for t in (a, b) for s in t.slots) == 3


def test_boundaries_and_empty_slots():
    token, = tokenize('x -123, text')
    assert token.slots[0].glyph == '-'
    assert token.slots[-1].glyph == ','
    assert [s.glyph for s in token.slots[1:-1]] == ['', '']


def test_maximal_and_table_space():
    token, = tokenize('12  345')
    assert token.text == '12  345'
    assert any(s.position == 'table_boundary' for s in token.slots)


def test_offsets_and_ambiguity():
    token, = tokenize('α 123-456 β')
    slot = next(s for s in token.slots if s.glyph == '-')
    assert slot.grammar_candidates == ('range', 'thousands')
    assert (token.start, token.end) == (2, 9)
    assert tokenize('abc') == []


def test_decimal_and_none_are_text_observations():
    token, = tokenize('555.6')
    assert [s.position for s in token.slots if s.glyph == '.'] == ['decimal']
    assert all(s.position == 'other' for s in tokenize('12345')[0].slots)
    assert tokenize('9,123')[0].slots[1].position == 'thousands'
    gap = next(s for s in tokenize('185· 95')[0].slots if s.glyph)
    assert gap.glyph == '· ' and gap.position == 'other'


def test_empty_and_mixed_separator_spans():
    assert tokenize('') == []
    token, = tokenize('12 - 34')
    gap = next(s for s in token.slots if s.glyph)
    assert gap.glyph == ' - ' and gap.position == 'range'
    assert tokenize('123456-789012')[0].slots[6].position == 'other'
