"""Validate exact coordinator schema in CLI fixtures and both delivered populations."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pytest
from tests._paths import require_file
from greekocr.ops.data_root import input_path

from greekocr.harvest.admission import RULES, TOOL_VERSION, expected_table_sha256, run_files

ROW_TYPES = {
    'row_id': str, 'source': str, 'class': str, 'pass': bool, 'rules_failed': list,
    'expected_language': str, 'expected_scripts': list, 'letters': int,
    'nonletter_frac': float, 'scripts_seen': dict, 'mixed_script_words': list, 'foreign_chars': list,
}
RECEIPT_TYPES = {
    'tool_version': str, 'tool_sha256': str, 'input_path': str, 'input_sha256': str,
    'rows_total': int, 'rows_pass': int, 'drops_per_rule': dict,
    'drops_per_source_class': dict, 'expected_table_sha256': str, 'created': str,
    'serbian_extension_atoms': list, 'serbian_extension_sha256': str,
}
IDS = {'numeric_shape', 'short_line', 'low_confidence', 'tall_box', 'nonletter_frac',
       'unexpected_language', 'unexpected_script', 'mixed_script_word', 'foreign_char'}


def validate_schema(prefix):
    receipt = json.loads(input_path(Path(str(prefix) + '_admission_receipt.json')).read_text())
    nw1 = receipt['tool_version'].startswith(('NW1-', 'NW1b-', 'SEG-'))
    extra = {'neighbour_words_params': dict, 'neighbour_words_ownership_params_sha256': str,
             'neighbour_words_unmatched': int, 'neighbour_words_unavailable': int,
             'neighbour_words_status_counts': dict, 'neighbour_words_reason_counts': dict} if nw1 else {}
    current = receipt["tool_version"] == TOOL_VERSION
    if current:
        extra.update(lookalike_table_name=str, lookalike_table_sha256=str,
                     serbian_documents=list, serbian_documents_sha256=str)
    assert set(receipt) == set(RECEIPT_TYPES) | set(extra)
    assert all(type(receipt[k]) is t for k, t in extra.items())
    if nw1:
        from greekocr.harvest.neighbour_words import PARAMS_SHA
        assert receipt['neighbour_words_ownership_params_sha256'] == PARAMS_SHA
    current = receipt['tool_version'] == TOOL_VERSION
    ids = IDS | ({'neighbour_words'} if nw1 else set()) | ({'geometry_unavailable', 'lookalike_only_word'} if current else set())
    assert all(type(receipt[k]) is t for k, t in RECEIPT_TYPES.items())
    from greekocr.harvest.admission import SERBIAN_EXTENSION_ATOMS, serbian_extension_sha256
    assert receipt['serbian_extension_atoms'] == list(SERBIAN_EXTENSION_ATOMS)
    assert receipt['serbian_extension_sha256'] == serbian_extension_sha256()
    assert receipt['tool_version'] in {TOOL_VERSION, 'NW1b-20261018.CP2b', 'ADM5c-20261017.1'}
    assert receipt['expected_table_sha256'] == (expected_table_sha256() if current else
        'f90d7ec213d334ce334be2fee36ff3241844e8853c1ebc38617767127d380f88')
    assert datetime.fromisoformat(receipt['created']).tzinfo is not None
    for key in ('tool_sha256', 'input_sha256', 'expected_table_sha256'):
        assert len(receipt[key]) == 64 and int(receipt[key], 16) >= 0
    paths = json.loads(receipt['input_path']) if receipt['input_path'].startswith('[') else [receipt['input_path']]
    inputs = [json.loads(line) for p in paths for line in input_path(Path(p)).open() if line.strip()]
    digest = hashlib.sha256()
    for p in paths:
        digest.update(input_path(Path(p)).read_bytes())
    assert digest.hexdigest() == receipt['input_sha256']
    rules, groups, total, passed = Counter(), defaultdict(Counter), 0, 0
    with input_path(Path(str(prefix) + '_admission.jsonl')).open() as stream:
        for index, line in enumerate(stream):
            row = json.loads(line)
            row_types = dict(ROW_TYPES, class_original=str, lookalike_only_words=list) if current else ROW_TYPES
            assert set(row) == set(row_types)
            assert all(type(row[k]) is t for k, t in row_types.items())
            for key in ('rules_failed', 'expected_scripts', 'mixed_script_words', 'foreign_chars'):
                assert all(type(v) is str for v in row[key])
            assert set(row['rules_failed']) <= ids
            assert len(row['rules_failed']) == len(set(row['rules_failed']))
            assert not row['pass'] or not row['rules_failed']
            # CP2 abstains when geometry is unavailable, even if rules pass.
            assert 0.0 <= row['nonletter_frac'] <= 1.0 and row['letters'] >= 0
            assert all(type(k) is str and type(v) is int and v >= 0 for k, v in row['scripts_seen'].items())
            assert all(len(c) == 1 for c in row['foreign_chars'])
            original = inputs[index]
            expected_id = original.get('row_id', original.get('id'))
            if expected_id is not None:
                assert row['row_id'] == str(expected_id)
            assert row['source'] == original['source']
            rules.update(row['rules_failed'])
            groups[row['source'] + '|' + row['class']].update(row['rules_failed'])
            total += 1
            passed += row['pass']
    assert total == len(inputs) == receipt['rows_total']
    assert passed == receipt['rows_pass']
    assert set(receipt['drops_per_rule']) == ids
    assert set(RULES) == IDS | {'neighbour_words', 'geometry_unavailable', 'lookalike_only_word'}
    assert receipt['drops_per_rule'] == {r: rules[r] for r in ids}
    assert receipt['drops_per_source_class'] == {k: {r: v[r] for r in ids} for k, v in groups.items()}
    return receipt


@pytest.mark.parametrize('mode', ['admit', 'census'])
def test_cli_fixed_schema(mode, tmp_path):
    paths = []
    for i in range(2 if mode == 'census' else 1):
        path = tmp_path / f'input{i}.jsonl'
        rows = [dict(id=f'{i}-clean', source='anemi_round1', wave='round1', script_class='greek_poly', label='ὁ λόγος εἶναι ἑλληνικός'),
                dict(id=f'{i}-bad', source='anemi_round1', wave='round1', script_class='greek_poly', label='αa한!')]
        path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
        paths.append(path)
    prefix = tmp_path / ('census' if mode == 'census' else 'input0')
    run_files(paths, census=prefix if mode == 'census' else None, output_dir=tmp_path)
    receipt = validate_schema(prefix)
    assert receipt['rows_pass'] == 0
    assert receipt['neighbour_words_unavailable'] == 2*len(paths)
    if mode == 'census':
        assert not Path(str(prefix) + '_admitted.jsonl').exists()
        assert '| round1 |' in prefix.with_suffix('.md').read_text()


@pytest.mark.parametrize('prefix', [
    'docs/records/harvest/collect_v3_admission/w1_originals_v3',
    'docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017',
])
def test_delivered_outputs_schema(prefix):
    require_file(Path(str(prefix) + '_admission.jsonl'))
    receipt = validate_schema(Path(prefix))
    if receipt['tool_version'] == TOOL_VERSION:
        assert receipt['tool_sha256'] == hashlib.sha256(Path('greekocr/harvest/admission.py').read_bytes()).hexdigest()
    elif receipt['tool_version'] == 'ADM5c-20261017.1':
        assert receipt['tool_sha256'] == '1a01b3680030245227249288e1c47e44f302cd5d1f2109433fb12dc2a8d6d4e8'


def test_v2_codec_is_exact_frozen_training_inventory():
    from greekocr.harvest.admission import evaluate, load_codec
    codec = load_codec()
    assert codec['version'] == 'v2'
    assert codec['sha256'] == '94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9'
    row = dict(source='serbia', label='Это чистая русская строка ѣ ј')
    assert 'foreign_char' not in evaluate(row)['failed_rules']
    old = load_codec(Path('greekocr/_vendor/codec/v1.json'))
    assert 'foreign_char' in evaluate(row, codec=old)['failed_rules']
