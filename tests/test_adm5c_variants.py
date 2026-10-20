"""ADM5c source-scoped codec and class-rule contracts, entirely offline."""
import ast
import hashlib
from pathlib import Path

import pytest

from greekocr.harvest.admission import (
    CLASS_RULE_VARIANTS, SERBIAN_EXTENSION_ATOMS, SOURCE_POLICIES, non_segmentation_eligibility,
    evaluate, load_codec, serbian_extension_sha256,
)


def row(text, cls='poly1850', source='bsb_poly1850', **extra):
    return dict(label=text, primary_class=cls, source=source, **extra)


def test_serbian_extension_exact_collector_inventory():
    path = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect/collect_v3/vendor/classify.py'
    tree = ast.parse(path.read_text())
    candidates = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
                  and isinstance(node.value, str) and 'њ' in node.value]
    assert candidates == [''.join(SERBIAN_EXTENSION_ATOMS)]
    assert len(SERBIAN_EXTENSION_ATOMS) == len(set(SERBIAN_EXTENSION_ATOMS)) == 12
    assert serbian_extension_sha256() == hashlib.sha256(candidates[0].encode()).hexdigest()
    assert SOURCE_POLICIES['serbia']['expected_characters'] == list(SERBIAN_EXTENSION_ATOMS)
    assert CLASS_RULE_VARIANTS['numerics_tables']['replaces'] == ['short_line', 'nonletter_frac']


def test_serbian_atoms_admitted_only_for_serbia_and_base_codec_unchanged():
    codec = load_codec()
    before = codec['atoms']
    assert evaluate(row('Његош пише њ и ћ', source='serbia'), codec=codec)['failed_rules'] == ['geometry_unavailable']
    result = evaluate(row('ἑλληνικὸς λόγος њ ћ'), codec=codec)
    assert {'unexpected_script', 'foreign_char'} <= set(result['failed_rules'])
    assert codec['atoms'] == before and 'њ' not in before
    result = evaluate(row('Это чистая русская строка њ ћ', source='ia_russian'))
    assert 'foreign_char' in result['failed_rules']


@pytest.mark.parametrize('text,passed', [
    ('4.547.331', True), ('p. 12', False), ('123', False), ('1234', True),
    ('1234 αααααα', False), ('1234. αααα', True), # exact 60% including space
    ('1234 . , · - /', True),
])
def test_numeric_shape(text, passed):
    result = evaluate(row(text, 'numerics_tables', 'elstat'))
    assert ('numeric_shape' not in result['failed_rules']) == passed
    assert not {'short_line', 'nonletter_frac'} & set(result['failed_rules'])
    if text in ('4.547.331', '1234', '1234 . , · - /'):
        assert result['failed_rules'] == ['geometry_unavailable']


@pytest.mark.parametrize('text,failed', [('ΚΕΦΑΛΑΙΟΝ', []), ('ΑΒΓ', ['short_line']),
                                        ('ΑΒΓΔ', []), ('ΑΒΓΔ!!!', ['nonletter_frac'])])
def test_heading_shape(text, failed):
    assert evaluate(row(text, 'headings_caps'))['failed_rules'] == failed + ['geometry_unavailable']


@pytest.mark.parametrize('cls,prefix', [('numerics_tables', '1234567890 '),
                                       ('headings_caps', 'ΚΕΦΑΛΑΙΟΝ ')])
@pytest.mark.parametrize('suffix,rule', [('한', 'unexpected_script'), ('🚀', 'foreign_char'),
                                        ('ΚΕΦΑΛΑΙΟN', 'mixed_script_word'),
                                        ('This is an entirely Latin sentence', 'unexpected_language')])
def test_variant_retains_language_script_mixed_and_codec_checks(cls, prefix, suffix, rule):
    assert rule in evaluate(row(prefix + suffix, cls))['failed_rules']


@pytest.mark.parametrize('cls,text', [('numerics_tables', '4.547.331'),
                                    ('headings_caps', 'ΚΕΦΑΛΑΙΟΝ')])
def test_variants_keep_confidence_and_geometry(cls, text):
    result = evaluate(row(text, cls, confidence=.88, bbox=[0, 0, 100, 18], page_median_line_height=10))
    assert result['failed_rules'] == ['low_confidence', 'tall_box', 'geometry_unavailable']


@pytest.mark.parametrize('doc,source,passed', [
    ('cyrillic:7235f8d0', 'archive_bub_gb_Cmg6AQAAIAAJ', True),
    ('cyrillic:975289f3', 'archive_b29337124', True),
    ('cyrillic:9a32fb66', 'archive_AA9613308335D0B014B', False),
    ('cyrillic:252fd568', 'archive_izvestiianabul25192530bul', False),
    ('unknown-language', 'archive_bub_gb_Cmg6AQAAIAAJ', False),
])
def test_census2_document_language_controls_extension(doc, source, passed):
    result = evaluate(row('Његош пише њ и ћ', 'cyrillic', source,
                          doc=doc, wave='cyrillic'))
    # SEG-CP6 separates text eligibility from unqualified physical admission.
    assert non_segmentation_eligibility(result['checks'])['passed'] is passed
    assert result['passed'] is False
    assert result['checks']['geometry_unavailable'] == 'fail'
    assert ('foreign_char' in result['failed_rules']) is not passed


def test_census2_extension_preserves_class_rules_and_rejects_letter_inference():
    result = evaluate(row('Његош пише њ и ћ', 'latin',
                          'archive_bub_gb_Cmg6AQAAIAAJ',
                          doc='cyrillic:7235f8d0', wave='cyrillic'))
    assert result['failed_rules'] == ['unexpected_script', 'geometry_unavailable']
    assert evaluate(row('Његош пише њ и ћ', source='ia_russian',
                        doc='cyrillic:7235f8d0'))['failed_rules'] == ['foreign_char', 'geometry_unavailable']
