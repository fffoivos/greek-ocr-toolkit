import ast
import hashlib
import io
from pathlib import Path
import sys

from PIL import Image
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import ss3_sample as ss3


def test_largest_remainder_floor_and_caps():
    assert ss3.allocation({'a': 200, 'b': 20, 'c': 3, 'd': 0}, 20, 4) == {
        'a': 16, 'b': 4, 'c': 0, 'd': 0}
    assert ss3.allocation({'a': 2, 'b': 20, 'c': 50}, 72, 4) == {'a': 2, 'b': 20, 'c': 50}
    assert ss3.allocation({'a': 1, 'b': 1, 'c': 1}, 2) == {'a': 1, 'b': 1, 'c': 0}
    for target in range(8, 74):
        pools = {'a': 2, 'b': 20, 'c': 51}
        result = ss3.allocation(pools, target, 4)
        assert sum(result.values()) == target
        assert all(0 <= result[k] <= pools[k] for k in pools)
        assert result['b'] >= 4 and result['c'] >= 4


def test_seeded_draw_reproducible_and_input_order_independent():
    rows = [dict(row_id=str(i)) for i in range(20)]
    first = ss3.seeded_order(rows, 2)
    assert first == ss3.seeded_order(list(reversed(rows)), 2)
    assert first != ss3.seeded_order(rows, 3)


def test_replacement_keeps_stratum():
    failures = []
    def acquire(row, stratum):
        if row['row_id'] == 'bad':
            raise ValueError('sha mismatch')
        return dict(line_id=row['row_id'], stratum=stratum)
    result = ss3.draw([dict(row_id='bad'), dict(row_id='good')], 1, 'rotated',
                      acquire, failures, ordered=True)
    assert result[0]['stratum'] == failures[0]['stratum'] == 'rotated'
    assert failures[0]['replacement_line_id'] == 'good'


def test_sha_mismatch_never_written(tmp_path):
    raw = io.BytesIO()
    Image.new('L', (2, 3)).save(raw, format='PNG')
    path = tmp_path / 'crop.png'
    with pytest.raises(ValueError, match='sha256 mismatch'):
        ss3.verified_write(path, raw.getvalue(), '0' * 64, (2, 3))
    assert not path.exists()
    ss3.verified_write(path, raw.getvalue(), hashlib.sha256(raw.getvalue()).hexdigest(), (2, 3))
    assert path.read_bytes() == raw.getvalue()


def test_key_never_referenced_by_sample_writer(tmp_path):
    tree = ast.parse(Path(ss3.__file__).read_text())
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for name in ['sample_record', 'write_sample', 'write_jsonl']:
        source = ast.unparse(functions[name]).lower()
        assert all(word not in source for word in ['key_opus', 'opus_type', "['note']", "['type']"])
    # Writer works with no key file or Opus record available.
    path = tmp_path / 'sample.jsonl'
    ss3.write_sample(path, [dict(line_id='row', verified=True)])
    assert 'opus' not in path.read_text() and 'note' not in path.read_text()
