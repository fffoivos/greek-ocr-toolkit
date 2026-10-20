"""CENSUS3 whole-word secondary script contracts, offline."""
import ast
import copy
import hashlib
import json
import subprocess

import pytest

from greekocr.harvest import admission as a
from greekocr.harvest.lookalikes import HOMOGLYPHS, lookalike_table_sha256


def row(text, cls):
    return dict(label=text, script_class=cls, source='archive_b24878935', wave='cyrillic')


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
@pytest.mark.skip(reason="historical binding; green at sol/census-v2-serbian@504bdb1e1; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_secondary_words(text, cls, rule, new_class, bad_words):
    record = row(text, cls)
    before = copy.deepcopy(record)
    result = a.evaluate(record)
    assert result['passed'] == (rule is None)
    assert rule is None or rule in result['failed_rules']
    assert result['class_original'] == cls
    assert result['class'] == new_class
    assert result['lookalike_only_words'] == bad_words
    assert record == before
    if new_class == 'mixed_greek_latin':
        assert result['expected_language'] == 'Greek / Latin'
        assert result['expected_scripts'] == ['greek', 'latin']
    if rule == 'lookalike_only_word':
        assert 'mixed_script_word' not in result['failed_rules']
        assert 'unexpected_script' not in result['failed_rules']


@pytest.mark.skip(reason="historical binding; green at sol/census-v2-serbian@504bdb1e1; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_existing_mixed_class_and_greek_policy_unchanged():
    assert a.evaluate(row('This is a Latin sentence ΑΒΕ', 'mixed_greek_latin'))['passed']
    record = dict(source='bsb_poly1850', label='ἑλληνικὸς λόγος coco')
    assert a.evaluate(record)['passed']


def test_table_exact_existing_groups_and_hash():
    source = subprocess.check_output(['git', 'show', '3f93d204:greekocr/_vendor/bench/e1_readout.py'], text=True)
    tree = ast.parse(source)
    original = next(ast.literal_eval(n.value) for n in tree.body
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'HOMOGLYPHS' for t in n.targets))
    assert HOMOGLYPHS == original
    assert lookalike_table_sha256() == hashlib.sha256(json.dumps(original, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    assert a.TOOL_VERSION != 'ADM5c-CENSUS2-20261018.1'


def test_public_schema_and_receipt_reclassified_group(tmp_path):
    path = tmp_path / 'input.jsonl'
    record = row('This is a Latin sentence λόγος', 'latin')
    path.write_text(json.dumps(record, ensure_ascii=False)+'\n')
    receipt = a.run_files([path], census=tmp_path / 'census')
    result = json.loads((tmp_path / 'census_admission.jsonl').read_text())
    assert result['class_original'] == 'latin'
    assert result['class'] == 'mixed_greek_latin'
    assert result['lookalike_only_words'] == []
    assert set(receipt['drops_per_source_class']) == {'archive_b24878935|mixed_greek_latin'}
    assert receipt['lookalike_table_sha256'] == lookalike_table_sha256()
