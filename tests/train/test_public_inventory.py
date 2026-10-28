"""Small fixtures for public snapshot and complete bulk-receipt custody."""
import csv
import gzip
import hashlib
from pathlib import Path
import struct
import zipfile

import pytest
from scripts.release_v0_publish.inventory import inventory, candidates, index_paths, main
from scripts.release_v0_publish.receipt_manifest import receipt_manifest


def put(root, name, data=b'fixture'):
    p = root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); return p


def index(root, names, version=2):
    entries = b''; previous = b''
    for name in names:
        encoded = name.encode()
        header = struct.pack('>10I', *([0]*6), 0o100644, 0, 0, 1) + b'\0'*20 + struct.pack('>H', len(encoded))
        if version == 4:
            common = 0
            while common < min(len(previous), len(encoded)) and previous[common] == encoded[common]: common += 1
            strip = len(previous)-common
            assert strip < 128
            entries += header+bytes([strip])+encoded[common:]+b'\0'
        else:
            entry = header+encoded+b'\0'; entries += entry+b'\0'*((-len(entry))%8)
        previous = encoded
    data = struct.pack('>4sII', b'DIRC', version, len(names))+entries
    put(root, '.git/index', data+hashlib.sha1(data).digest())


@pytest.mark.parametrize('version', [2, 3, 4])
def test_worktree_candidates_keep_tracked_ignored_and_untracked(tmp_path, version):
    put(tmp_path, '.gitignore', b'ignored*\ncache/\n')
    put(tmp_path, 'ignored-tracked'); put(tmp_path, 'ignored-untracked')
    put(tmp_path, 'new.py'); put(tmp_path, 'nested/new.py'); put(tmp_path, '.hidden')
    index(tmp_path, ['ignored-tracked', 'nested/new.py'], version)
    assert index_paths(tmp_path) == {'ignored-tracked', 'nested/new.py'}
    names = candidates(tmp_path)
    assert {'ignored-tracked', 'new.py', 'nested/new.py', '.hidden'} <= set(names)
    assert 'ignored-untracked' not in names and '.git/index' not in names


def test_exclusions_and_no_secret_values_in_diagnostics(tmp_path, capsys):
    token = ('h'+'f_'+('A'*32)).encode()
    put(tmp_path, 'safe.py', b'print(1)')
    put(tmp_path, 'secrets.txt', b'header\n'+token+b'\n')
    put(tmp_path, 'key.txt', b'-----BEGIN '+b'PRIVATE KEY-----\n')
    put(tmp_path, 'pass.txt', b'password'+b' = "n4Z9fRc0Xe6Tu1Po8La3Wi7Ds2Qk5VbA"\n')
    put(tmp_path, 'big.bin', b'x'*5_000_001)
    put(tmp_path, 'google/responses/a.json', b'{"document":{"text":"fixture","pages":[{"layout":{"textAnchor":{}}}]}}')
    put(tmp_path, 'renamed.json', b'{"fullTextAnnotation": {"text": "fixture"}}')
    put(tmp_path, 'compressed.gz', gzip.compress(b'line1\n'+token))
    put(tmp_path, '__pycache__/a.pyc'); put(tmp_path, '.pytest_cache/a')
    bulk = 'out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/a.json'
    put(tmp_path, bulk)
    (tmp_path/'link').symlink_to(tmp_path/'safe.py')
    rows, locations = inventory(tmp_path, paths=[p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob('*') if p.is_file()])
    by = {r['path']: r for r in rows}
    assert by['safe.py']['decision'] == 'include'
    assert all(r['decision'] == 'exclude' for n, r in by.items() if n != 'safe.py')
    assert ('secrets.txt', 2) in locations and ('compressed.gz', 2) in locations
    out = tmp_path/'PUBLIC_INVENTORY.tsv'
    main(['--root', str(tmp_path), '--output', str(out)])
    assert token.decode() not in capsys.readouterr().out
    assert 'not-a-real-value' not in out.read_text()
    assert 'PUBLIC_INVENTORY.tsv' not in {r['path'] for r in csv.DictReader(out.open(), delimiter='\t')}


def test_manifest_covers_ignored_bulk_receipts_and_similar_trees(tmp_path):
    put(tmp_path, '.gitignore', b'out/\n')
    expected = ['out/TRAIN_FULL_v1/receipts_stage_c_smoke/a.json',
                'out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/b.log',
                'out/TRAIN_FULL_v1/receipts_stage_c_guard_smoke/nested/c.json']
    for name in expected: put(tmp_path, name, b'receipt')
    put(tmp_path, 'out/ordinary/a.json')
    rows = receipt_manifest(tmp_path)
    assert [r['path'] for r in rows] == sorted(expected)
    assert all(r['bytes'] == 7 and r['sha256'] == hashlib.sha256(b'receipt').hexdigest() for r in rows)


def test_large_review_inventory_has_git_sized_parts(tmp_path, monkeypatch):
    import scripts.release_v0_publish.inventory as module
    monkeypatch.setattr(module, 'MAX_BYTES', 200)
    rows = [dict(path=f'fixture/{i}.txt', bytes=1, sha256='a'*64, decision='include', reason='fixture')
            for i in range(12)]
    out = tmp_path/'PUBLIC_INVENTORY.tsv'
    module.write_inventory_outputs(out, rows, part_bytes=240)
    import json
    receipt = json.loads(out.with_suffix('.receipt.json').read_text())
    combined = []
    for item in receipt['parts']:
        p = tmp_path/item['path']
        assert p.stat().st_size == item['bytes'] <= 240
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256']
        combined.extend(csv.DictReader(p.open(), delimiter='\t'))
    assert [r['path'] for r in combined] == [r['path'] for r in rows]
    assert receipt['full_local_review']['sha256'] == hashlib.sha256(out.read_bytes()).hexdigest()


def test_archive_member_raw_google_content_is_excluded(tmp_path):
    archive = tmp_path/'renamed.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('renamed.json', '{"fullTextAnnotation": {"text": "fixture"}}')
    rows, matches = inventory(tmp_path, paths=['renamed.zip'])
    assert rows[0]['decision'] == 'exclude'
    assert 'Google' in rows[0]['reason']
    assert matches == []


def test_source_literals_and_empty_response_path_are_included(tmp_path):
    files = {'parse.py': b'return response["fullTextAnnotation"]',
             'google/responses/README.md': b'"pages" "text" "textAnchor"',
             'google/raw/empty.json': b'{}',
             'credentials.py': b'password = os.environ.get("PASSWORD")\ntoken = credentials.access_token\n',
             'example.py': b'password = "ordinary-example"\n',
             'short.txt': b'hf_12345678901234567890123456789',
             'pins.json': b'{"tokenizer_sha256":"a9e5b31f40c8d278bef906ab43d17fe501ecb9a08"}'}
    for name, data in files.items(): put(tmp_path, name, data)
    rows, matches = inventory(tmp_path, paths=files)
    assert all(r['decision'] == 'include' for r in rows)
    assert matches == []


@pytest.mark.parametrize('name', ['audit/opus_keys/deck/key.jsonl', 'x/private/a.txt',
    'x/R0_adjudication_private/ia/a.json', 'x/items_key012.json', 'audit/cards/key.jsonl'])
def test_private_answer_material_is_excluded(tmp_path, name):
    put(tmp_path, name)
    rows, _ = inventory(tmp_path, paths=[name])
    assert rows[0]['decision'] == 'exclude'


def test_output_evidence_is_exact_allowlist(tmp_path):
    from scripts.release_v0_publish.inventory import output_rule
    assert output_rule('out/runner1/a.json')
    assert output_rule('out/TRAIN_FULL_v1/pytest_release/a.py')
    assert output_rule('artifacts/sf7_rc1_test/output_12/receipt.json')
    assert not output_rule('out/lane/CLAIM.json', {'out/lane/CLAIM.json'})
    assert not output_rule('artifacts/method/receipt.json')


def test_review_deck_key_tree_exclusion_and_ignored_discovery(tmp_path):
    from scripts.release_v0_publish.inventory import private_rule, write_review_outputs
    put(tmp_path, '.gitignore', b'artifacts/\n')
    excluded = ['artifacts/lf1/keys/deck.json', 'artifacts/cq4/keys/nested/cards.tsv',
                'artifacts/keys/deck.json.gz']
    excluded += ['docs/keys/deck.json', 'keys/deck.json',
                 'other/artifacts/lf1/keys/deck.json']
    included = ['artifacts/lf1/keyset/deck.json', 'artifacts/cq1/keys',
                'greekocr/keys/parser.py', 'scripts/keys/build.py', 'tests/keys/test_keys.py']
    for name in excluded + included:
        put(tmp_path, name)
    assert set(excluded) <= set(candidates(tmp_path))
    rows, _ = inventory(tmp_path, paths=excluded + included)
    by = {r['path']: r for r in rows}
    for name in excluded:
        assert private_rule(name) == 'review deck key tree'
        assert by[name]['decision'] == 'exclude'
        assert by[name]['reason'] == 'review deck key tree'
    assert all(by[name]['decision'] == 'include' for name in included)
    write_review_outputs(tmp_path, rows)
    private = list(csv.DictReader((tmp_path/'PRIVATE_REVIEW.tsv').open(), delimiter='\t'))
    assert {r['path'] for r in private} == set(excluded)
    assert all(r['rule'] == 'review deck key tree' for r in private)
    names = {r['path'] for r in csv.DictReader((tmp_path/'INCLUDED_NAME_REVIEW.tsv').open(), delimiter='\t')}
    assert not names.intersection(excluded)


def test_secret_shapes_and_structured_google_formats(tmp_path):
    import io, json, tarfile
    from scripts.release_v0_publish.inventory import scan_bytes, content_checks
    assert scan_bytes(b'token'+b' = "'+b'p9J4zW8mN2rT7vQ1'+b'xL6aD3sF0cH5kB9y"') == [1]
    assert scan_bytes(b'AWS_KEY = "AK'+b'IA1234567890ABCDEF"') == [1]
    assert not scan_bytes(b'token = os.environ["ACCESS_TOKEN"]')
    obj = {'document': {'text': 'fixture', 'pages': [{'layout': {'textAnchor': {}}}]}}
    data = json.dumps(obj).encode()
    for name, payload in [('a.json', data), ('a.jsonl', b'{}\n'+data),
                          ('a.json.gz', gzip.compress(data))]:
        assert content_checks(name, payload)[1]
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode='w') as t:
        member = tarfile.TarInfo('renamed.json'); member.size = len(data)
        t.addfile(member, io.BytesIO(data))
    assert content_checks('a.tar.gz', gzip.compress(archive.getvalue()))[1]
    assert not content_checks('source.py', data)[1]


@pytest.mark.parametrize('prefix', ['', 'docs/history/', 'greekocr/', 'scripts/', 'tests/'])
@pytest.mark.parametrize('name', ['deck_key.json', 'deck_key.jsonl', 'key_SEALED.json',
                                 'blind_key.json', 'blind_pages_key.json', 'wl_key.json'])
@pytest.mark.parametrize('suffix', ['', '.gz'])
def test_review_key_file_patterns(tmp_path, prefix, name, suffix):
    from scripts.release_v0_publish.inventory import private_rule, write_review_outputs
    path = prefix + name + suffix
    put(tmp_path, path, gzip.compress(b'{}') if suffix else b'{}')
    rows, _ = inventory(tmp_path, paths=[path])
    assert private_rule(path) == 'review deck key file'
    assert rows[0]['decision'] == 'exclude'
    assert rows[0]['reason'] == 'review deck key file'
    write_review_outputs(tmp_path, rows)
    with (tmp_path/'PRIVATE_REVIEW.tsv').open() as f:
        assert next(csv.DictReader(f, delimiter='\t'))['rule'] == 'review deck key file'


@pytest.mark.parametrize('path', ['answers/deck.mapped.jsonl',
                                 'docs/history/answers/nested/deck.mapped.jsonl',
                                 'scripts/review/answers/deck.mapped.jsonl'])
def test_review_answer_join(tmp_path, path):
    from scripts.release_v0_publish.inventory import private_rule
    put(tmp_path, path, b'{}')
    rows, _ = inventory(tmp_path, paths=[path])
    assert private_rule(path) == 'review answer join'
    assert rows[0]['decision'] == 'exclude'
    assert rows[0]['reason'] == 'review answer join'


@pytest.mark.parametrize('path', ['greekocr/keys/parser.py', 'scripts/keys/build.py',
                                 'tests/keys/test_keys.py', 'docs/keys/example.py',
                                 'deck.mapped.jsonl', 'answer/deck.mapped.jsonl',
                                 'answers/deck.jsonl', 'keyset/deck.json',
                                 'key.json', 'key.jsonl', 'deck_key.json.backup',
                                 'greekocr/parser.py', 'scripts/build.py', 'tests/test_keys.py'])
def test_review_rule_keeps_code_and_nonmatching_paths(tmp_path, path):
    from scripts.release_v0_publish.inventory import private_rule
    # Card/source co-occurrence alone must not apply the path policy.
    put(tmp_path, path, b'{"card_id": "opaque", "line_id": "source"}')
    rows, _ = inventory(tmp_path, paths=[path])
    assert private_rule(path) == ''
    assert rows[0]['decision'] == 'include'


def test_ignored_review_key_files_and_answer_joins_are_discovered(tmp_path):
    put(tmp_path, '.gitignore', b'history/\n')
    paths = ['history/deck_key.json', 'history/deck_key.json.gz',
             'history/answers/deck.mapped.jsonl', 'history/keys/deck.tsv']
    for path in paths:
        put(tmp_path, path)
    assert set(paths) <= set(candidates(tmp_path))
