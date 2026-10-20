"""Text-only N1-L artifact builder; refuses to overwrite any deliverable.

Run with PYTHONDONTWRITEBYTECODE=1 from the worktree root, after the tests.
The pytest record below is the observed N1-L run, not rerun by this builder.
"""
import hashlib
import importlib.util
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.numerics.locks import load_locks
from greekocr.numerics.tokens import tokenize

OUT = ROOT / 'artifacts/n1'
PROJECTS = Path.home() / 'Projects'
RELEASE = PROJECTS / 'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3'
INPUTS = {}
OUTPUTS = {}


def read(path):
    data = path.read_bytes()
    INPUTS[str(path)] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                             line_count=len(data.splitlines()))
    return data


def write(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    data = path.read_bytes()
    OUTPUTS[str(path.relative_to(ROOT))] = dict(sha256=hashlib.sha256(data).hexdigest(),
        bytes=len(data), line_count=len(data.splitlines()))


def write_ids(name, ids):
    write(OUT / name, ''.join(x + '\n' for x in sorted(set(ids))))


def json_rows(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


receipt0 = json.loads(read(OUT / 'validation.json'))
census = json.loads(read(OUT / 'census.json'))
frame = json_rows(read(OUT / 'frame_step1.jsonl'))
docs_meta = json.loads(read(OUT / 'locked_eval_docs.json'))
for name in ('frame_step1.jsonl', 'locked_eval_docs.json'):
    assert INPUTS[str(OUT / name)]['sha256'] == receipt0['sha256']['artifacts/n1/' + name]
reserved_docs = set(docs_meta['locked_documents'])
assert reserved_docs == set(census['sampling']['locked_documents'])
locked = [r for r in frame if r['partition'] == 'locked_eval']
step1 = [r for r in frame if r['partition'] == 'step1']
locked_ids = {r['line_id'] for r in locked}
step1_ids = {r['line_id'] for r in step1}
step1_docs = {r['document'] for r in step1}
assert {r['slot_id'] for r in locked} == set(docs_meta['locked_slot_ids'])
c1 = set(docs_meta['excluded_c1_line_ids'])
frozen_c1 = set(c1)
for path in sorted((PROJECTS / 'collect-v3-data/run/W1/c1').glob('*_key.json')):
    key = json.loads(read(path))
    c1.update(v['line_id'] for v in key.values() if isinstance(v, dict) and 'line_id' in v)
assert c1 == frozen_c1, 'C1 inputs changed since step 0'
wave_path = RELEASE / 'release_admissions/w1_masked_1d.jsonl'
wave_rows = json_rows(read(wave_path))
assert all('row_id' in r for r in wave_rows)
wave_ids = {r['row_id'] for r in wave_rows if r.get('tranche') == 'W1'}
assert len(wave_ids) == len(wave_rows), 'Unexpected tranche or duplicate wave-1d id'
exclusion_root = RELEASE / 'release_exclusions'
read(exclusion_root / 'release_exclusions.json')
exclusions = {p.name: set(read(p).decode().splitlines())
              for p in sorted(exclusion_root.glob('*.txt'))}

# A single read-only pass over W1, hashing the exact bytes parsed. No collector imports.
w1path = PROJECTS / 'collect-v3-data/run/W1/features.jsonl'
h = hashlib.sha256()
reserved_ids = set()
reserved_rows = []
locked_meta = {}
seen = set()
row_count = 0
before = w1path.stat()
with w1path.open('rb') as f:
    for line in f:
        h.update(line)
        r = json.loads(line)
        id = r['id']
        assert id not in seen, 'Duplicate W1 id'
        seen.add(id)
        row_count += 1
        doc = f"{r['source']}:{r['item']}"
        if doc in reserved_docs:
            reserved_ids.add(id)
            reserved_rows.append(r)
        if id in locked_ids:
            locked_meta[id] = r
        # Check frame metadata against W1, below, without retaining full W1.
after = w1path.stat()
assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
INPUTS[str(w1path)] = dict(sha256=h.hexdigest(), bytes=after.st_size, line_count=row_count)
assert h.hexdigest() == census['inputs'][str(w1path)]['sha256'], 'W1 changed since step 0'
assert locked_ids <= seen
assert wave_ids <= seen
assert {r['source'] for r in locked_meta.values()} <= {'elstat', 'gazette_modern'}
for r in locked:
    w = locked_meta[r['line_id']]
    assert r['document'] == f"{w['source']}:{w['item']}"
    assert r['source'] == w['source'] and r['year'] == w['year']
    assert r['crop_sha256'] == w['crop_sha256']
    assert w['text'][r['start']:r['end']] == r['glyph']
counts = dict(Counter(r['source_era'] for r in locked))
assert counts == {'elstat': 100, 'gazette_1982_1985': 100, 'gazette_1986_1990': 100}
assert not locked_ids & step1_ids
assert not reserved_ids & step1_ids
assert not reserved_docs & step1_docs
assert not locked_ids & c1
assert locked_ids <= reserved_ids
assert {f"{r['source']}:{r['item']}" for r in reserved_rows} == reserved_docs
write_ids('n1_locked_eval_line_ids.txt', locked_ids)
write_ids('n1_reserved_docs.txt', reserved_docs)
write_ids('n1_reserved_doc_line_ids.txt', reserved_ids)
load_locks(OUT).assert_fit_rows(step1_ids)

overlaps = {'wave_1d': dict(count=len(locked_ids & wave_ids), ids=sorted(locked_ids & wave_ids))}
for name, ids in exclusions.items():
    overlaps[name] = dict(count=len(locked_ids & ids), ids=sorted(locked_ids & ids))
other_union = set().union(*exclusions.values())
other_count = len(locked_ids & other_union)
alt_info = dict(status='not needed')
if overlaps['wave_1d']['count']:
    # Reuse the step-0 round-robin sampler and exact row construction. Importing
    # this module does not call main(), read images, or write its old artifacts.
    spec = importlib.util.spec_from_file_location('n1_step0', ROOT / 'scripts/numerics/n1_step0.py')
    s0 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s0)
    read(ROOT / 'scripts/numerics/n1_step0.py')
    read(ROOT / 'greekocr/numerics/tokens.py')
    candidates = []
    for r in reserved_rows:
        if r['id'] in c1 or r['id'] in wave_ids:
            continue
        for ti, t in enumerate(tokenize(r['text'])):
            for s in t.slots:
                candidates.append(dict(line_id=r['id'], document=f"{r['source']}:{r['item']}",
                    source=r['source'], source_era=s0.bucket(r), year=r['year'], page=r['page'],
                    crop=r['crop'], crop_sha256=r['crop_sha256'], token_index=ti,
                    token_start=t.start, token_end=t.end, digit_count=t.digit_count, **asdict(s),
                    slot_id=f"{r['id']}:t{ti}:s{s.index}",
                    suspected_hyphen=(s.boundary is None and '-' in s.glyph and t.digit_count >= 4)))
    seed = '20261017:N1L:alt'
    def draw():
        rng = random.Random(seed)
        selected = []
        quotas = {}
        for era in ('elstat', 'gazette_1982_1985', 'gazette_1986_1990'):
            pool = [r for r in candidates if r['source_era'] == era]
            marks = [r for r in pool if r['glyph'] or r['position'] == 'table_boundary']
            chosen = s0.balanced_sample(marks, 90, rng)
            assert len(chosen) == 90, f'Insufficient observed candidates: {era}'
            used = {r['slot_id'] for r in chosen}
            remaining = s0.balanced_sample([r for r in pool if r['slot_id'] not in used], 10, rng)
            assert len(remaining) == 10
            selected.extend(chosen + remaining)
            quotas[era] = dict(observed_draw=90, remaining_draw=10,
                remaining_observed=sum(bool(r['glyph'] or r['position']=='table_boundary') for r in remaining),
                eligible_slots=len(pool), observed_eligible_slots=len(marks))
        return [dict(r, partition='locked_eval', seed=seed, truth=None, rendered=False) for r in selected], quotas
    alt, quotas = draw()
    alt_bytes = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in alt)
    assert alt_bytes == ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in draw()[0])
    alt_ids = {r['line_id'] for r in alt}
    assert len(alt) == len({r['slot_id'] for r in alt}) == 300
    assert not alt_ids & (wave_ids | c1 | step1_ids)
    assert alt_ids <= reserved_ids
    assert all(set(r) == set(locked[0]) and r['document'] in reserved_docs for r in alt)
    assert Counter(r['source_era'] for r in alt) == Counter(counts)
    write(OUT / 'frame_locked_alt.jsonl', alt_bytes)
    write_ids('n1_locked_eval_line_ids_alt.txt', alt_ids)
    alt_info = dict(status='written', seed=seed, slots=300, lines=len(alt_ids), quotas=quotas,
                    per_source_line_counts=dict(Counter(r['source_era'] for r in reserved_rows
                        if False)),
                    deterministic_replay=True, schema_matches=True, wave_1d_overlap=0,
                    c1_overlap=0, step1_line_overlap=0, outside_reserved_lines=0,
                    exclusions={name: len(alt_ids & ids) for name, ids in exclusions.items()})
    alt_info['per_source_line_counts'] = dict(Counter(s0.bucket(r) for r in reserved_rows if r['id'] in alt_ids))
checks = dict(frozen_frame_sha256_match=True, frozen_documents_sha256_match=True,
    w1_matches_step0_sha256=True, w1_stable_during_read=True, w1_ids_unique=True,
    locked_ids_exist=True, locked_sources_valid=True, locked_metadata_offsets_valid=True,
    locked_slots_match_document_receipt=True, slot_counts=counts, locked_slot_count=300,
    locked_line_count=len(locked_ids), reserved_document_count=len(reserved_docs),
    reserved_line_count=len(reserved_ids), locked_line_counts=dict(Counter(
        ('elstat' if r['source']=='elstat' else 'gazette_1982_1985' if r['year'] <=1985 else 'gazette_1986_1990')
        for r in locked_meta.values())),
    locked_step1_line_overlap=0, reserved_step1_line_overlap=0, reserved_step1_document_overlap=0,
    c1_locked_overlap=0, c1_ids_match_step0=True, all_reserved_documents_found=True,
    fitting_guard_accepts_step1=True, all_locked_lines_reserved=True)
pytest = dict(command='PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --noconftest -q -p no:cacheprovider tests/test_numeric_locks.py tests/test_numeric_tokens.py',
              exit_code=0, passed=29, summary='29 passed in 0.06s')
locked_sha = OUTPUTS['artifacts/n1/n1_locked_eval_line_ids.txt']['sha256']
report = f'''# N1-L evaluation lock

Frozen frame and document-lock SHA256s match step-0 validation. W1 also matches the step-0 SHA256. All checks pass: 300 slots (100 each ELSTAT, Gazette 1982–85, Gazette 1986–90), {len(locked_ids)} unique locked W1 lines, {len(reserved_docs)} reserved documents and {len(reserved_ids)} fitting-excluded lines across all pages. No locked or reserved line or document enters step1; no C1 card line enters the lock.

Original locked-line SHA256: `{locked_sha}`.

| Overlap with original lock | Lines |
|---|---:|
''' + ''.join(f'| {name} | {value["count"]} |\n' for name, value in overlaps.items()) + f'''
Other exclusions contain {other_count} distinct locked lines (union; file counts may overlap). Alternative: {alt_info['status']}. When written, it uses seed `20261017:N1L:alt`, the same reserved documents, row schema and 100-slot quotas, draws 90 observed separator/table candidates plus 10 remaining per source, and excludes wave-1d and C1 lines. Remaining slots follow step-0 semantics and may themselves contain observed marks. The receipt records deterministic replay, pool sizes and alternative overlaps.

The original files remain unchanged. The sourcing lead must choose the original or alternative evaluation lock and register it; registration and step1 have not been performed. `load_locks` reads the original named lock and all reserved lines; the document-wide fitting exclusion covers both draws. Call `assert_fit_rows(ids)` before reading fitting data.

Tests: **29 passed**, using `python3 -m pytest --noconftest -q -p no:cacheprovider tests/test_numeric_locks.py tests/test_numeric_tokens.py` with bytecode disabled. Includes nonselected reserved lines, generators, allowed batches, missing/malformed files, inconsistent locks and immutability.

Local CPU and text metadata only. No network, image opening/decoding/rendering, collector writes, `run.lock` access, `.git` writes or exclusion registration. Live usage probe was not run under network OFF.

Full input/output hashes, counts, overlap IDs and check results: `artifacts/n1/N1L_RECEIPT.json`. Receipt SHA256 is not included in itself. `artifacts/n1/build_n1l.py` records the deterministic build and refuses to overwrite deliverables.
'''
write(ROOT / 'docs/labelfix/secondary/N1L_REPORT.md', report)
for name in ('greekocr/numerics/locks.py', 'tests/test_numeric_locks.py', 'artifacts/n1/build_n1l.py'):
    data = (ROOT / name).read_bytes()
    OUTPUTS[name] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), line_count=len(data.splitlines()))
# Confirm all small inputs remain byte-identical at completion. W1 was hashed
# during the read and stat-checked, rather than taking a live collector lock.
for name, meta in INPUTS.items():
    path = Path(name)
    if path != w1path:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == meta['sha256'], f'Input changed: {name}'
assert (w1path.stat().st_size, w1path.stat().st_mtime_ns) == (after.st_size, after.st_mtime_ns)
receipt = dict(schema='N1L-1', status='READY_FOR_LEAD_SELECTION_AND_REGISTRATION',
    inputs=INPUTS, outputs=OUTPUTS, checks=checks, overlaps=overlaps,
    other_exclusions_union_overlap=other_count, alternative=alt_info, pytest=pytest,
    constraints=dict(network_used=False, images_opened_decoded_rendered=False,
        git_writes=False, collector_writes=False, run_lock_accessed=False, cpu_only=True),
    registration='Not performed; sourcing lead must choose and register before step1',
    receipt_self_hash='Omitted to avoid a circular hash')
write(OUT / 'N1L_RECEIPT.json', json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(checks=checks, overlaps={k:v['count'] for k,v in overlaps.items()},
                     alternative=alt_info, locked_sha256=locked_sha), indent=2))
