"""Offline execution model for the Clariden plan; NOT a production source adapter.

Real one-book metadata + explicitly mock crop/trainer/synthetic/reference payloads.
No Hub, network, scheduler or rendering API is used. All input files are pinned.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import time

import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
HELPER = REPO / 'docs/programme_20261019/registry/evidence/hf_one_book_probe.py'
spec = importlib.util.spec_from_file_location('registry_features', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
AUTH_VARS = ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'HUGGINGFACEHUB_API_TOKEN', 'HUGGINGFACE_API_KEY')
TABLES = ('pages', 'boxes', 'rows', 'row_features')
KEYS = dict(pages=['page_id'], boxes=['box_id'], rows=['row_key'],
            row_features=['row_key', 'label_variant', 'feature_version'])


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def info(p, root):
    return dict(path=str(p.relative_to(root)), bytes=p.stat().st_size, sha256=sha(p))


def write_json(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(canonical(value) + '\n')
    tmp.replace(p)


def credential_free():
    if any(os.environ.get(v) for v in AUTH_VARS):
        raise ValueError('CPU builder requires authentication variables absent')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'


def shards(table, dest, name, cap):
    """Check the actual closed size; split recursively, preserving binary values."""
    if not 0 < cap <= 1_000_000_000:
        raise ValueError('invalid shard cap')
    outputs = []
    def emit(t):
        p = dest / f'{name}-{len(outputs):05d}.parquet'
        pq.write_table(t, p, compression='zstd')
        if p.stat().st_size > cap:
            p.unlink()
            if t.num_rows <= 1:
                raise ValueError('single record exceeds shard cap')
            n = t.num_rows // 2
            emit(t.slice(0, n)); emit(t.slice(n))
        else:
            outputs.append(p)
    emit(table)
    return outputs


def database_transport(db, dest, cap):
    full = sha(db)
    if db.stat().st_size <= cap:
        return [db], dict(sha256=full, bytes=db.stat().st_size, parts=[db.name])
    parts = []; directory = dest / 'registry.sqlite.parts'; directory.mkdir()
    with db.open('rb') as f:
        while b := f.read(cap):
            p = directory / f'part-{len(parts):05d}'
            p.write_bytes(b); parts.append(p)
    h = hashlib.sha256()
    for p in parts:
        h.update(p.read_bytes())
    if h.hexdigest() != full:
        raise ValueError('database transport reassembly SHA mismatch')
    return parts, dict(sha256=full, bytes=db.stat().st_size,
                      parts=[str(p.relative_to(dest)) for p in parts])


def verify_artifacts(root, records):
    for r in records:
        p = root / r['path']
        if p.stat().st_size != r['bytes'] or sha(p) != r['sha256']:
            raise ValueError('artifact hash mismatch: ' + r['path'])


def validate(tables):
    rr = {k: t.to_pylist() for k, t in tables.items()}
    for name, records in rr.items():
        keys = [tuple(r[k] for k in KEYS[name]) for r in records]
        if len(keys) != len(set(keys)):
            raise ValueError('duplicate ' + name + ' key')
    pages = {r['page_id']: r for r in rr['pages']}
    boxes = {r['box_id']: r for r in rr['boxes']}
    rows = {r['row_key']: r for r in rr['rows']}
    if len({(r['parent_id'],r['row_id']) for r in rows.values()}) != len(rows):
        raise ValueError('duplicate original training row identity')
    for b in boxes.values():
        if b['page_id'] not in pages:
            raise ValueError('orphan box')
    for r in rows.values():
        b = boxes.get(r['box_id']); p = pages.get(r['page_id'])
        if not b or not p or b['page_id'] != r['page_id']:
            raise ValueError('row -> box -> page join failed')
        if r['book_id'] != p['book_id'] or r['split'] != p['split']:
            raise ValueError('book/split join failed')
        if r['split'] == 'conflict_hold_out' and r['book_split_exportable']:
            raise ValueError('conflict exported')
    for f in rr['row_features']:
        if f['row_key'] not in rows:
            raise ValueError('orphan feature')
    if {(f['row_key'],f['label_variant']) for f in rr['row_features']} != {(k,v) for k in rows for v in ('raw','census_corrected')}:
        raise ValueError('raw/corrected feature coverage differs')
    return dict(counts={k: len(v) for k, v in rr.items()},
                row_box_page_book_joins=len(rows), used_joins=sum(r['status']=='used' for r in rows.values()),
                statuses=dict(Counter(r['status'] for r in rows.values())))


def run(config_path, output, stop_after=None):
    credential_free()
    started = time.perf_counter()
    config_path = config_path.resolve(); root = config_path.parent
    config = json.loads(config_path.read_text())
    if config['mode'] != 'mock_one_book_not_publishable':
        raise ValueError('production source adapters are not implemented by this mock')
    output = output.resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError('output must be separate from immutable inputs')
    verify_artifacts(root, config['inputs'])
    binding = hashlib.sha256(canonical(dict(config_sha256=sha(config_path), code=sha(Path(__file__)),
        helper=sha(HELPER), codec=sha(helper.REPO/'greekocr/_vendor/codec/v2.json'),
        pyarrow=pa.__version__, unicode=helper.ud.unidata_version)).encode()).hexdigest()
    output.mkdir(parents=True, exist_ok=True)
    bp = output / 'BINDING.json'
    if bp.exists() and json.loads(bp.read_text())['binding'] != binding:
        raise ValueError('resume binding changed; choose a new output root')
    write_json(bp, dict(binding=binding))
    tables = {n: pq.read_table(root / (n+'.parquet')) for n in TABLES}
    checks = validate(tables)
    books = {b['book_id']: b for b in pq.read_table(root/'book_registry.parquet').to_pylist()}
    instruments = {}
    for m in pq.read_table(root/'row_instruments.parquet').to_pylist():
        instruments.setdefault(m['row_id'], []).append(m)
    for r in tables['pages'].to_pylist() + tables['rows'].to_pylist():
        b = books[r['book_id']]
        if r['split'] != b['split'] or r['harvest_protection'] != b['harvest_protection'] or r['book_registry_sha256'] != sha(root/'book_registry.parquet'):
            raise ValueError('canonical registry binding differs')
    for r in tables['rows'].to_pylist():
        m = instruments.get(r['row_id'], [])
        if r['lqb_row'] != any(x['kind']=='lqb' for x in m) or r['release_excluded_row'] != any(x['kind']=='release_exclusion' for x in m):
            raise ValueError('line instrument membership differs')
    scripts = root / 'Scripts-14.0.0.txt'
    feature = helper.Features(scripts)
    page_ids = sorted(tables['pages']['page_id'].to_pylist())
    records = {k: t.to_pylist() for k, t in tables.items()}
    row_map = {r['row_key']: r for r in records['rows']}
    box_map = {b['box_id']: b for b in records['boxes']}
    page_map = {p['page_id']: p for p in records['pages']}
    feature_checks = 0
    sample = set(sorted(row_map, key=lambda k: hashlib.sha256(('runner4-verify:'+k).encode()).digest())[:1000])
    # Recompute every available text feature and geometry on 1,000 real rows.
    # Same implementation: this is replay agreement, not independent semantics QA.
    for f in records['row_features']:
        r = row_map[f['row_key']]; b = box_map[r['box_id']]; p = page_map[r['page_id']]
        anchor = box_map[b['source_box_ids'][0]]
        raw = json.loads(anchor['raw_segmenter_json'])
        langs = json.loads(anchor['effective_detected_languages_json'])
        recomputed = feature.compute(r['label_raw' if f['label_variant']=='raw' else 'label_corrected'], langs)
        for k, v in recomputed.items():
            if f['row_key'] in sample and f[k] != v:
                raise ValueError('feature replay mismatch: '+k)
        f.update(recomputed)
        bbox = b['bbox_px']
        if abs(f['x_center_norm']-(bbox[0]+bbox[2])/2/p['width_px']) > 1e-9 or abs(f['y_center_norm']-(bbox[1]+bbox[3])/2/p['height_px']) > 1e-9:
            raise ValueError('position replay mismatch')
        feature_checks += f['row_key'] in sample
    tables['row_features'] = pa.Table.from_pylist(records['row_features'], schema=tables['row_features'].schema)
    cap = config['shard_cap_bytes']; batch_size = config['page_batch_size']
    artifacts = []; reused = 0; built = 0
    for batch, start in enumerate(range(0, len(page_ids), batch_size)):
        ids = set(page_ids[start:start+batch_size]); batch_dir = output / f'batches/{batch:05d}'
        receipt_path = batch_dir / 'DONE.json'
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt['binding'] != binding:
                raise ValueError('batch binding mismatch')
            verify_artifacts(output, receipt['artifacts']); reused += 1
        else:
            # Only this output-owned unfinished batch is discarded on restart.
            if batch_dir.exists():
                shutil.rmtree(batch_dir)
            batch_dir.mkdir(parents=True)
            row_ids = {r['row_key'] for r in records['rows'] if r['page_id'] in ids}
            batch_records = dict(pages=[r for r in records['pages'] if r['page_id'] in ids],
                boxes=[r for r in records['boxes'] if r['page_id'] in ids],
                rows=[r for r in records['rows'] if r['row_key'] in row_ids],
                row_features=[r for r in records['row_features'] if r['row_key'] in row_ids])
            paths = []
            for name, rr in batch_records.items():
                rr.sort(key=lambda r: tuple(r[k] for k in KEYS[name]))
                table = pa.Table.from_pylist(rr, schema=tables[name].schema)
                paths.extend(shards(table, batch_dir, name, cap))
            receipt = dict(binding=binding, page_ids=sorted(ids), artifacts=[info(p, output) for p in paths])
            write_json(receipt_path, receipt); built += 1
        artifacts.extend(receipt['artifacts'])
        if stop_after and built >= stop_after:
            return dict(interrupted=True, batches_built=built, batches_reused=reused)
    # Payload lanes are fixtures only. Whole-row archive preserves all unknown
    # historical provenance and exact binary image_png values and label fields.
    payload_checks = {}
    for lane in ('crops', 'training', 'synthetic', 'references'):
        table = pq.read_table(root / f'{lane}.parquet')
        dest = output / lane; dest.mkdir(exist_ok=True)
        for old in dest.glob('part-*.parquet'):
            old.unlink()
        paths = shards(table, dest, 'part', cap)
        reread = pa.concat_tables([pq.read_table(p) for p in paths])
        if reread.to_pylist() != table.to_pylist():
            raise ValueError('payload/label/provenance changed')
        for r in reread.to_pylist():
            if hashlib.sha256(r['image_png']).hexdigest() != r['image_sha256']:
                raise ValueError('embedded payload hash mismatch')
        payload_checks[lane] = table.num_rows
        artifacts.extend(info(p, output) for p in paths)
    md = output / 'metadata'; md.mkdir(exist_ok=True)
    for name in ('book_registry.parquet', 'row_instruments.parquet'):
        shutil.copyfile(root/name, md/name); artifacts.append(info(md/name, output))
    analysis = output / 'analysis'
    if analysis.exists():
        shutil.rmtree(analysis)
    analysis.mkdir()
    dbpath = analysis / 'registry.sqlite'; db = sqlite3.connect(dbpath)
    for name, table in tables.items():
        helper.sql_store(db, name, table)
    db.executescript('CREATE UNIQUE INDEX page_pk ON pages(page_id);CREATE UNIQUE INDEX box_pk ON boxes(box_id);CREATE UNIQUE INDEX row_pk ON rows(row_key);CREATE UNIQUE INDEX feature_pk ON row_features(row_key,label_variant,feature_version);')
    db.commit()
    if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise ValueError('SQLite integrity failure')
    count = db.execute('SELECT count(*) FROM rows r JOIN boxes b USING(box_id) JOIN pages p ON p.page_id=b.page_id').fetchone()[0]
    if count != tables['rows'].num_rows:
        raise ValueError('SQLite join failed')
    db.close()
    transport, db_info = database_transport(dbpath, analysis, cap)
    artifacts.extend(info(p, output) for p in transport)
    if transport != [dbpath]:
        dbpath.unlink()  # transported representation only; recorded full SHA
    # Re-read complete Parquet outputs, not just the in-memory source tables.
    readback = {n: pa.concat_tables([pq.read_table(output/a['path']) for a in artifacts
        if a['path'].startswith('batches/') and Path(a['path']).name.startswith(n+'-')]) for n in TABLES}
    if validate(readback) != checks:
        raise ValueError('final output reconciliation failed')
    verify_artifacts(output, artifacts)
    final = dict(mode=config['mode'], publishable=False, binding=binding, checks=checks,
        feature_replay=dict(rows=len(sample), variants=feature_checks, independent=False),
        payload_fixture_rows=payload_checks, database=db_info, artifacts=sorted(artifacts,key=lambda a:a['path']))
    write_json(output / 'MOCK_COMPLETE.json', final)
    (output/'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {a['path']}\n" for a in final['artifacts']) +
        f"{sha(output/'MOCK_COMPLETE.json')}  MOCK_COMPLETE.json\n")
    metrics = dict(seconds=time.perf_counter()-started, batches_built=built, batches_reused=reused,
                   input_bytes=sum(r['bytes'] for r in config['inputs']), output_bytes=sum(r['bytes'] for r in artifacts))
    write_json(output / 'RUN_METRICS.json', metrics)
    return dict(**metrics, checks=checks, feature_replay=final['feature_replay'], payload_fixture_rows=payload_checks,
                publishable=False, manifest_sha256=sha(output/'MOCK_COMPLETE.json'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--stop-after-batches', type=int)
    a = p.parse_args()
    print(canonical(run(a.config, a.output, a.stop_after_batches)))
