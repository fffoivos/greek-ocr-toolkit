"""CP6 offline text contracts; segmentation deliberately excluded from parity."""
import copy
import json
from pathlib import Path
from tests._paths import ADMISSION, run_record
import unicodedata as ud

import pytest
from greekocr.harvest import admission as a
from greekocr.harvest.text_primitives import codec_letter_script, normalize_current
from greekocr.labelfix.text import is_delimiter, tokenize

ROOT = Path(__file__).resolve().parents[1]
SEG = ADMISSION / 'seg'


def projection(record):
    result = a.evaluate(record)
    row = a.output_row(record, result, 'fixture')
    row['rules_failed'] = [r for r in row['rules_failed'] if r not in ('geometry_unavailable', 'neighbour_words')]
    row['pass'] = not row['rules_failed']
    return dict(row=row, label=result['label'], normalisations=result['normalisations'])


@pytest.mark.parametrize('case', json.loads((SEG / 'CP6_text_fixtures.json').read_text())['cases'],
                         ids=lambda c: c['input']['id'])
def test_frozen_before_after(case):
    record = copy.deepcopy(case['input'])
    assert projection(record) == case['ruled']
    assert record == case['input']
    assert case['before']['label'] == case['ruled']['label']
    assert case['before']['normalisations'] == case['ruled']['normalisations']


@pytest.mark.parametrize('text,cls,rule,new_class,bad_words', [
    ('Это чистая русская строка Paris', 'cyrillic', None, 'cyrillic', []),
    ('Это чистая русская строка coco', 'cyrillic', 'lookalike_only_word', 'cyrillic', ['coco']),
    ('Это чистая русская строка pace', 'cyrillic', 'lookalike_only_word', 'cyrillic', ['pace']),
    ('This is a Latin sentence λόγος', 'latin', None, 'mixed_greek_latin', []),
    ('This is a Latin sentence ΑΒΕ', 'latin', 'lookalike_only_word', 'latin', ['ΑΒΕ']),
    ('Это чистая русская строка Δαβій', 'cyrillic', 'mixed_script_word', 'cyrillic', []),
    ('This is a Latin sentence λόγος ΑΒΕ', 'latin', 'lookalike_only_word', 'mixed_greek_latin', ['ΑΒΕ']),
    ('Это чистая русская строка c-o/c=c', 'cyrillic', 'lookalike_only_word', 'cyrillic', ['c','o','c','c']),
    ('This is a Latin sentence λ', 'latin', None, 'mixed_greek_latin', []),
])
def test_census3_rulings(text, cls, rule, new_class, bad_words):
    result = projection(dict(label=text, script_class=cls, source='archive_b24878935', wave='cyrillic'))['row']
    assert result['pass'] == (rule is None)
    assert rule is None or rule in result['rules_failed']
    assert result['class_original'] == cls and result['class'] == new_class
    assert result['lookalike_only_words'] == bad_words


@pytest.mark.parametrize('doc,extended', [('cyrillic:7235f8d0', True), ('cyrillic:975289f3', True), ('other', False)])
def test_document_scoped_serbian(doc, extended):
    result = a.evaluate(dict(source='archive_b24878935', wave='cyrillic',
                             script_class='cyrillic', doc=doc, label='Његош пише њ и ћ'))
    assert ('foreign_char' not in result['failed_rules']) == extended
    assert 'њ' not in a.load_codec()['atoms']


@pytest.mark.parametrize('text', ['ἑλληνικὸς λόγος', 'Это чистая русская строка ёйї', 'ᾼ λόγος'])
def test_nfd_marks_never_double_count(text):
    record = dict(source='bsb_poly1850', label=text)
    before = a.evaluate(record)
    after = a.evaluate(dict(record, label=ud.normalize('NFD', text)))
    assert before['letters'] == after['letters']
    assert before['scripts_seen'] == after['scripts_seen']
    assert before['mixed_words'] == after['mixed_words']
    codec = a.load_codec()
    assert codec_letter_script('\u0301', codec) is None
    assert codec_letter_script('\u0345', codec) is None


def test_spacing_atoms_codec_metadata_and_exact_hashes():
    codec = a.load_codec()
    for c in codec['nonletter_atoms']:
        assert codec_letter_script(c, codec) is None
    assert codec['policy']['literal_override_atoms'] == '΄јѣ᾽᾿„•'
    assert a.serbian_extension_sha256() == '202a906c5f4b96d4e06d01783e9cffad20f4626db8eea4dc80a9ca3ed1105850'
    assert a.lookalike_table_sha256() == 'f5dddff62b61fca9af6b1fb115ac23ef3ece4bd50e14e9031c25ec4f51ed7acd'
    from greekocr._vendor.bench.e1_readout import HOMOGLYPHS
    assert HOMOGLYPHS is a.HOMOGLYPHS


def test_modes_preserve_internal_punctuation_and_no_corrections():
    assert a.words('αβ=ab/Яю-λέξεις,καί') == ['αβ', 'ab', 'Яю', 'λέξεις', 'καί']
    assert len(tokenize('αβ=ab/Яю-λέξεις,καί')) == 1
    assert is_delimiter('=', mode='admission') and not is_delimiter('=', mode='labelfix')
    assert not is_delimiter('\u0301', mode='admission')
    assert a.normalize_label('ϲ AАΑ\u200b') == 'ϲ AАΑ\u200b'
    assert normalize_current('  α\u0301\t˙\nβ  ') == ('ά · β', ['R8:dot_above_to_middle_dot', 'NFC', 'collapse_whitespace'])
    with pytest.raises(ValueError): normalize_current('x', mode='historical-bench')
    with pytest.raises(ValueError): is_delimiter('x', mode='unknown')


@pytest.mark.parametrize('damage', ['ids', 'cp', 'normalization'])
def test_validating_loader_not_weaker_parser(tmp_path, damage):
    obj = json.loads((ROOT / 'greekocr/_vendor/codec/v2.json').read_text())
    if damage == 'ids': obj['atoms'][1]['id'] = obj['atoms'][0]['id']
    elif damage == 'cp': obj['atoms'][1]['cp'] = 'U+FFFF'
    else: obj['policy']['normalization'] = 'NFC'
    path = tmp_path / 'codec.json'; path.write_text(json.dumps(obj))
    with pytest.raises(ValueError): a.load_codec(path)


def test_unknown_source_and_wave_raise():
    with pytest.raises(ValueError): a.evaluate(dict(source='unknown', label='λόγος'))
    with pytest.raises(ValueError): a.evaluate(dict(source='anemi_round1', wave='round2', script_class='greek_poly', label='λόγος'))


def test_legacy_spacing_mark_category_is_preserved():
    # Mc, ccc=0: broader than labelfix correction's is_mark predicate.
    assert a.inventory('ελληνικος λογος ab\u093e')['latin_words'] == ['ab\u093e']
    assert a.script_class('ελληνικος λογος ab\u093e') == 'greek_latin_cs'


@pytest.mark.parametrize('case', ['head', 'scope', 'bytes'])
def test_guard_rejects_drift(case, monkeypatch):
    import runpy
    guard = run_record(str(SEG / 'guard_cp6_commit.py'))
    monkeypatch.setattr(guard['subprocess'], 'check_output', lambda *args, **kwargs: 'current\n')
    manifest = dict(base_HEAD='old' if case == 'head' else 'current',
                    files=[], read_only_dependencies=[])
    if case == 'bytes':
        manifest['files'] = [dict(path=p, sha256='incorrect') for p in guard['FILES']]
        monkeypatch.setitem(guard['verify'].__globals__, 'sha', lambda p: 'actual')
    with pytest.raises(ValueError, match={'head': 'base HEAD moved', 'scope': 'exact review scope', 'bytes': 'bytes changed'}[case]):
        guard['verify'](manifest)
