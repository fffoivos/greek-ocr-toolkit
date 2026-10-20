"""Mechanical, offline SPLIT1 adoption. Never writes to input worktrees.

Only the data artifacts are byte deterministic; receipt time is stamped by date.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zlib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INPUT = HERE.parent / 'split1'
MAIN = Path.home() / 'Projects/greek-ocr-toolkit-main-next'
CENSUS = MAIN / 'docs/records/harvest/seg_census'
# The recorded mock points to package/ beside itself; the actual retained package
# is under docs/harvest, in the SAME read-only main-next worktree.
PACKAGE = MAIN / 'docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut'
SPLITS = ('train', 'dev', 'test')
EXPECTED = dict(rows=320479, rows_per_split=dict(train=253402, dev=7007, test=60070),
                rows_per_tranche=dict(W1=101098, W2=219381), editions=1359,
                forced_editions=99, forced_rows=52468)
DECISION = ('Decision, owner via coordinator, 19 Oct night: SPLIT1 is adopted exactly as proposed. '
            'Every W1/W2 row takes its SPLIT1 proposed_split as its final split, with no changes. '
            'The forced editions stay test. This task converts it to the census split input '
            '(night plan step P1). It decides nothing.')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def encode(value):
    return (json.dumps(value, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


def read_lines(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def verified_inputs():
    manifest = INPUT / 'COMMIT_SHA256SUMS.txt'
    checks = dict((line.split()[1], line.split()[0]) for line in manifest.read_text().splitlines())
    inputs = {}
    for name in ('row_split_proposal.jsonl.gz', 'editions.jsonl', 'summary.json'):
        path = INPUT / name
        actual = sha(path)
        if actual != checks[str(path.relative_to(ROOT))]:
            raise ValueError('SPLIT1 SHA mismatch: ' + name)
        committed = subprocess.check_output(['git', 'show', 'd8286346:' + str(path.relative_to(ROOT))], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != actual:
            raise ValueError('Input differs from d8286346: ' + name)
        inputs[name] = actual
    inputs['COMMIT_SHA256SUMS.txt'] = sha(manifest)
    return inputs


def prepare_data():
    inputs = verified_inputs()
    proposal = read_lines(INPUT / 'row_split_proposal.jsonl.gz')
    editions = read_lines(INPUT / 'editions.jsonl')
    by_edition = {e['edition_id']: e for e in editions}
    if len(by_edition) != len(editions):
        raise ValueError('Duplicate edition')
    rows = [dict(parent_id=r['parent_id'], row_id=r['row_id'], edition_id=r['edition_id'],
                 split=r['proposed_split'], forced=r['forced']) for r in proposal]
    rows.sort(key=lambda r: (r['parent_id'], r['row_id']))
    keys = set()
    counts = Counter(); tranches = Counter(); cross = defaultdict(Counter)
    edition_rows = defaultdict(Counter); forced_rows = Counter()
    for r in rows:
        key = (r['parent_id'], r['row_id'])
        if key in keys:
            raise ValueError('Duplicate row: ' + str(key))
        keys.add(key)
        e = by_edition[r['edition_id']]
        if (r['split'], r['forced']) != (e['proposed_split'], e['forced']):
            raise ValueError('Row/edition assignment mismatch: ' + str(key))
        if r['split'] not in SPLITS or (r['forced'] and r['split'] != 'test'):
            raise ValueError('Invalid assignment: ' + str(key))
        tranche = {'collect-v3-W1-20261018-0524': 'W1', 'collect-v3-W2-20261018-0524': 'W2'}[r['parent_id']]
        document = r['row_id'].rsplit('--s', 1)[0]
        sources = {m['document_id']: m['source'] for m in e['metadata']}
        if document not in e['member_documents']:
            raise ValueError('Row outside edition documents')
        source = sources[document]
        counts[r['split']] += 1; tranches[tranche] += 1
        cross[(tranche, source)][r['split']] += 1
        edition_rows[r['edition_id']][tranche] += 1
        if r['forced']:
            forced_rows[r['split']] += 1
    observed = dict(rows=len(rows), rows_per_split=dict(counts), rows_per_tranche=dict(tranches),
                    editions=len(editions), forced_editions=sum(e['forced'] for e in editions),
                    forced_rows=sum(forced_rows.values()))
    if observed != EXPECTED:
        raise ValueError('STOP: counts differ: ' + json.dumps(observed))
    summary = json.loads((INPUT / 'summary.json').read_text())
    if (counts != summary['total_rows_by_split'] or len(rows) != summary['rows'] or
        len(editions) != summary['editions'] or observed['forced_editions'] != summary['forced'] or
        forced_rows != summary['forced_rows']):
        raise ValueError('STOP: SPLIT1 summary mismatch')
    maps = []
    for e in sorted(editions, key=lambda e: e['edition_id']):
        per_tranche = edition_rows[e['edition_id']]
        if sum(per_tranche.values()) != e['row_count'] or sum(e['rows_per_class'].values()) != e['row_count']:
            raise ValueError('STOP: edition count mismatch: ' + e['edition_id'])
        maps.append(dict(edition_id=e['edition_id'], split=e['proposed_split'], forced=e['forced'],
                         forced_reason=e['reason'] if e['forced'] else None,
                         forced_split=e['forced_split'], leakage_matches=e['leakage_matches'],
                         member_documents=e['member_documents'],
                         rows_per_tranche={w: per_tranche[w] for w in ('W1', 'W2')},
                         rows_per_class=e['rows_per_class'], gazette=e['gazette']))
    stats = dict(observed, edition_counts_per_split=dict(Counter(e['split'] for e in maps)),
                 forced_rows_per_split=dict(forced_rows),
                 forced_edition_details=[dict(edition_id=e['edition_id'], split=e['split'],
                                      rows=sum(e['rows_per_tranche'].values())) for e in maps if e['forced']],
                 rows_per_tranche_source=[dict(tranche=w, source=s,
                     **{split: c[split] for split in SPLITS}, total=sum(c.values()))
                     for (w, s), c in sorted(cross.items())])
    return rows, maps, stats, inputs


def write_data(out, rows, maps):
    out.mkdir(parents=True, exist_ok=True)
    raw_sha = hashlib.sha256()
    with (out / 'row_split.jsonl.gz').open('wb') as target:
        with gzip.GzipFile(fileobj=target, mode='wb', filename='', mtime=0, compresslevel=9) as zipped:
            for r in rows:
                line = encode(r); raw_sha.update(line); zipped.write(line)
    with (out / 'edition_map.jsonl').open('wb') as target:
        for e in maps:
            target.write(encode(e))
    return dict(compressed_sha256=sha(out / 'row_split.jsonl.gz'),
                uncompressed_sha256=raw_sha.hexdigest(), edition_map_sha256=sha(out / 'edition_map.jsonl'))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def consumer_check(path, rows):
    sys.path.insert(0, str(PACKAGE))
    from greekocr.harvest import line_pipeline_census04 as c4
    from greekocr.harvest.line_pipeline import canonical
    from greekocr.harvest import line_pipeline_sources as sources
    if not Path(c4.__file__).resolve().is_relative_to(PACKAGE):
        raise ValueError('Wrong census loader imported: ' + c4.__file__)
    prepare = load_module('split2_census_prepare', CENSUS / 'prepare_config.py')
    spec = dict(path=str(path.resolve()), sha256=sha(path))
    with tempfile.TemporaryDirectory(prefix='split2-config-') as tmp:
        base = dict(codec='unused', versions='unused', parents=[], corrections=[], metadata='unused', final_policy={})
        config = prepare.prepare(base, PACKAGE.parent, Path(tmp), split_input=spec)
        allocation = c4.load_split(config['split_input'])
        metadata = dict(row_splits={canonical(list(k)): v['split'] for k, v in allocation.items()})
        unresolved = []
        with c4.integration(config, Path(tmp), allocation, {}, c4.diagnostics):
            for r in rows:
                parent = dict(id=r['parent_id'], format='collect-v3-features')
                record = dict(id=r['row_id'], page_id=r['row_id'].rsplit('-l', 1)[0], label='')
                # Check BOTH the canonical row_splits adapter and actual census04 integration.
                adapted = sources.canonicalize(record, parent, metadata)
                bound = c4.census.canonicalize(record, parent, {})
                if (adapted['split'] != r['split'] or bound['split'] != r['split'] or
                    bound['edition_id'] != r['edition_id']):
                    unresolved.append(dict(parent_id=r['parent_id'], row_id=r['row_id']))
    return dict(rows=len(rows), resolved=len(rows)-len(unresolved), unmapped_rows=unresolved,
                allocation_rows=len(allocation), loader=str(Path(c4.__file__).resolve()),
                loader_sha256=sha(c4.__file__), prepare_config_sha256=sha(CENSUS / 'prepare_config.py'),
                sources_sha256=sha(sources.__file__),
                method='prepare_config.prepare -> census04.load_split; canonical row_splits adapter + census04.integration')


def build(out):
    rows, maps, stats, inputs = prepare_data()
    hashes = write_data(out, rows, maps)
    check = consumer_check(out / 'row_split.jsonl.gz', rows)
    if check['unmapped_rows'] or check['allocation_rows'] != len(rows):
        raise ValueError('STOP: unmapped rows: ' + json.dumps(check))
    stamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], env=dict(os.environ, TZ='Europe/Athens'), text=True).strip()
    receipt = dict(decision=DECISION, build_time_athens=stamp, input_shas=inputs,
                   consumer_schema_sha256=sha(CENSUS / 'split_input.schema.json'),
                   split1_commit='d8286346', code_sha=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                   build_script_sha256=sha(__file__), interpreter=dict(executable=sys.executable, version=sys.version,
                   implementation=platform.python_implementation(), zlib_runtime=zlib.ZLIB_RUNTIME_VERSION),
                   gzip=dict(mtime=0, filename='', compresslevel=9), output=hashes, counts=stats,
                   loader_check=check, diagnostics=dict(extra_filtering=False,
                   initial_test_correction='Initial test found receipt field-name collision between forced edition count and details; renamed details, rebuilt and reran. Allocation bytes unchanged.',
                   source_counts='Source copied from edition metadata for each member document; no snapshot or image reads.',
                   package_location='Recorded mock relative package is absent; use retained docs/harvest package in main-next.',
                   receipt_determinism='Data files are deterministic. Receipt includes live date/interpreter/code provenance.'))
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    table = '\n'.join(f"| {x['tranche']} | {x['source']} | {x['train']:,} | {x['dev']:,} | {x['test']:,} | {x['total']:,} |" for x in stats['rows_per_tranche_source'])
    (out / 'SPLIT2.md').write_text(f'''# SPLIT2 final W1/W2 row allocation

{DECISION}

Built {stamp}. `row_split.jsonl.gz` contains all 320,479 SPLIT1 rows, sorted by
(parent_id, row_id), with `split = proposed_split` and unchanged forced flags.
No admission, usability, class, source, or text filtering is applied.
`edition_map.jsonl` preserves forced reasons and leakage evidence verbatim from SPLIT1.

```json
{{"split_input": {{"path": "<deploy path>/row_split.jsonl.gz", "sha256": "{hashes['compressed_sha256']}"}}}}
```

The config hash covers compressed bytes. Gzip: mtime=0, empty filename, level=9.
Uncompressed SHA256: `{hashes['uncompressed_sha256']}`.

| Tranche | Source | Train | Dev | Test | Total |
|---|---|---:|---:|---:|---:|
{table}
| All | All | 253,402 | 7,007 | 60,070 | 320,479 |

W1: 101,098 rows; W2: 219,381 rows. Editions: 1,359
(train {stats['edition_counts_per_split']['train']}, dev {stats['edition_counts_per_split']['dev']}, test {stats['edition_counts_per_split']['test']}).
Forced: 99 editions / 52,468 rows, all test.

The 436 BSB pages read after 05:24 are not in the 05:24 snapshots, so rows
from any later snapshot have no split entry (they stay unassigned in the census).

Load-through: {check['resolved']:,}/{len(rows):,} resolved with `prepare_config.prepare`,
the census04 loader used by the mock stage, the canonical row_splits key, and
census04's integration adapter. Unmapped rows: {len(check['unmapped_rows'])}.
The retained package is in main-next's `docs/harvest/seg_census/package/`;
the mock script's relative `docs/records/.../package/` does not exist.
Imports disable bytecode writes; native segmentation is not launched.

Rebuild and test locally (no network):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/collect_v3_admission/split2/build_split2.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts= -p no:cacheprovider docs/harvest/collect_v3_admission/split2/test_split2.py
```

See `GUARDED_COMMIT_LIST.md` for the exact staging allowlist. No commit or push is performed.
''')
    print(json.dumps(dict(output=hashes, counts=EXPECTED, loader_resolved=check['resolved'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE)
    args = parser.parse_args()
    # Refuse destinations outside SPLIT2 or a temporary rebuild directory.
    destination = args.out.resolve()
    if not (destination.is_relative_to(HERE) or destination.is_relative_to(Path(tempfile.gettempdir()).resolve())):
        parser.error('output must be under split2/ or the system temporary directory')
    build(destination)
