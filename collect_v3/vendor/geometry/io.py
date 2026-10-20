"""Read-only harvest adapters, deterministic sampling, source-bound caches."""
from __future__ import annotations

from collections import defaultdict, Counter
import gzip
import hashlib
import json
from pathlib import Path
import random
import time
import warnings

import numpy as np
from PIL import Image
from greekocr.ops.receipts import file_sha256, write_receipt

SCHEMA = 'greekocr-labelfix-geometry-1'


def jsonl(path):
    with Path(path).open(encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    with temp.open('w', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
    temp.replace(path)


def identity(paths) -> dict:
    return {str(p):file_sha256(p) for p in paths}


def detector_identity() -> str:
    root = Path(__file__).resolve().parents[3]/'greekocr'
    files = sorted([*(root/'pages').glob('*.py'), *(root/'glyphs').glob('*.py')])
    h = hashlib.sha256()
    for p in files:
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def page_key(record):
    # IDs retain full book IDs even when crop directories use six/eight chars.
    return record['wave'], record['id'].rsplit('-l', 1)[0]


def sample_pages(keys, n, seed):
    """Equal-wave, round-robin-book selection; deterministic without replacement."""
    rng = random.Random(seed)
    waves = defaultdict(lambda: defaultdict(list))
    for wave, page in sorted(set(keys)):
        waves[wave][page.rsplit('-p',1)[0]].append((wave,page))
    pools = {}
    for wave, books in sorted(waves.items()):
        order = sorted(books)
        rng.shuffle(order)
        for values in books.values():
            rng.shuffle(values)
        pool=[]
        while any(books.values()):
            for book in order:
                if books[book]:
                    pool.append(books[book].pop())
        pools[wave] = pool
    result=[]
    while len(result) < min(n, len(set(keys))):
        for wave in sorted(pools):
            if pools[wave] and len(result)<n:
                result.append(pools[wave].pop(0))
    return result


def build_plan(source_root: Path, predictions: list[Path], train_pages=200, seed=20261016,
               wave=None, scope='study') -> tuple[list[dict], dict]:
    harvest = source_root/'docs/harvest'
    test_file = harvest/'collection/v2/import_real_v2_test.jsonl'
    train_file = harvest/'collection/v2/import_real_v2_train.jsonl'
    prediction_keys=[]
    for pred in predictions:
        prediction_keys.append({(r['source_doc_id'].split(':',1)[0],r['line_id']) for r in jsonl(pred)})
    if scope=='study' and (len(prediction_keys) != 2 or prediction_keys[0] != prediction_keys[1]):
        raise ValueError('two_seed_test_id_sets_must_match')
    prediction_ids=prediction_keys[0] if prediction_keys else set()
    test = list(jsonl(test_file))
    evaluation_pages = {page_key(r) for r in test if (r['wave'],r['id']) in prediction_ids}
    train_keys = {page_key(r) for r in jsonl(train_file)}
    # A page-uniform draw within each wave makes a training line-rate ratio
    # estimable with N_wave/n_wave page weights; do not silently balance books.
    rng = random.Random(seed)
    train_pools = {w:sorted(k for k in train_keys if k[0]==w) for w in sorted({k[0] for k in train_keys})}
    for pool in train_pools.values():
        rng.shuffle(pool)
    chosen_train=set()
    while len(chosen_train)<min(train_pages,len(train_keys)):
        for pool in train_pools.values():
            if pool and len(chosen_train)<train_pages:
                chosen_train.add(pool.pop())
    selected = {**{k:'test' for k in evaluation_pages}, **{k:'train' for k in chosen_train}}
    dev_file=harvest/'collection/v2/import_real_v2_dev.jsonl'
    if scope=='all-admitted':
        selected={}
        for split,path in [('test',test_file),('train',train_file),('dev',dev_file)]:
            for r in jsonl(path):
                key=page_key(r)
                if key in selected and selected[key]!=split:
                    raise ValueError('page_crosses_collection_splits')
                selected[key]=split
    if wave:
        selected = {k:v for k,v in selected.items() if k[0] == wave}
    by_page = defaultdict(list)
    for r in test:
        if page_key(r) in selected:
            by_page[page_key(r)].append(r)
    for r in jsonl(train_file):
        if page_key(r) in selected:
            by_page[page_key(r)].append(r)
    if scope=='all-admitted':
        for r in jsonl(dev_file):
            if page_key(r) in selected:
                by_page[page_key(r)].append(r)
    inputs = [test_file,train_file,*predictions]
    if scope=='all-admitted':
        inputs.append(dev_file)
    plan=[]
    for w in sorted({k[0] for k in selected}):
        admitted_file = harvest/w/'admitted.jsonl'
        records_file = harvest/w/('records_all.jsonl' if w=='round1' else 'records.jsonl')
        inputs.extend([admitted_file,records_file])
        admitted = {r['id']:r for r in jsonl(admitted_file) if (w,r['page_id']) in selected}
        raw = defaultdict(dict)
        for r in jsonl(records_file):
            if (w,r['page_id']) in selected:
                raw[r['page_id']][r['id']] = {k:r.get(k) for k in
                    ('id','page_id','image','image_sha256','bbox','docai_text','docai_raw_text','docai_index')}
        for (ww,key), split in sorted(selected.items()):
            if ww!=w:
                continue
            fragments=[]
            for r in by_page[(w,key)]:
                a, original = admitted[r['id']], raw[key][r['id']]
                if a['crop_path'] != r['crop'] or a['bbox'] != original['bbox']:
                    raise ValueError('admitted_source_geometry_changed:'+r['id'])
                fragments.append(dict(id=r['id'],old_label=r['label'],
                    fragment_text=r['label'],docai_fragment_text=original['docai_text'],
                    fragment_text_source='v2_admitted_google_label_preserving_existing_cleaning',
                    bbox=a['bbox'],crop_bbox=a['crop_bbox'],
                    old_crop=r['crop'],crop_sha256=a['crop_sha256'],docai_index=original['docai_index'],
                    provenance={k:r.get(k) for k in ('source','source_url','licence','script_class','year')}))
            first=next(iter(raw[key].values()))
            plan.append(dict(wave=w,page_id=key,split=split,book=key.rsplit('-p',1)[0],
                             image=first['image'],image_sha256=first['image_sha256'],fragments=fragments))
    receipt=dict(schema=SCHEMA,seed=seed,scope=scope,
                 selection=('all admitted train/dev/test pages' if scope=='all-admitted' else
                            'all seed-predicted test pages; equal-wave uniform-without-replacement training pages'),
                 input_sha256=identity(inputs),test_prediction_lines=len(prediction_ids),
                 manifest_test_pages=len({page_key(r) for r in test}),
                 excluded_test_pages=sorted(set(page_key(r) for r in test)-
                     {k for k,split in selected.items() if split=='test'}),
                 train_population_pages=dict(Counter(k[0] for k in train_keys)),
                 requested_train_pages=train_pages,pages=len(plan))
    return plan,receipt


def cache_page(source: Path, cache: Path, expected_sha: str, detector_sha: str):
    """Gzipped JSON geometry + lossless detector mask, beside page reference.

    The cache lives in the caller's output tree, NEVER beside source harvest
    pixels. Cache hits verify the source, detector, mask, and geometry binding.
    """
    from greekocr.pages import process_page, PageOptions
    if file_sha256(source) != expected_sha:
        raise ValueError('page_source_hash_changed:'+str(source))
    geometry, mask_path, receipt_path = cache/'detector.json.gz',cache/'ink.png',cache/'receipt.json'
    labels_path=cache/'labels.npz'
    if receipt_path.exists():
        receipt=json.loads(receipt_path.read_text())
        if (receipt['source_sha256'] != expected_sha or receipt['detector_sha256'] != detector_sha or
                receipt.get('row_ink_source')!='detector_assigned_components'):
            raise ValueError('stale_detector_cache:'+str(cache))
        if (file_sha256(geometry)!=receipt['geometry_sha256'] or file_sha256(mask_path)!=receipt['mask_sha256'] or
                file_sha256(labels_path)!=receipt['labels_sha256']):
            raise ValueError('corrupt_detector_cache:'+str(cache))
        data=json.loads(gzip.decompress(geometry.read_bytes()))
        with Image.open(mask_path) as mask:
            ink=np.asarray(mask).astype(bool)
        with np.load(labels_path) as archive:
            labels=archive['labels']
        return data,ink,labels,dict(receipt,cache_hit=True)
    start=time.perf_counter()
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter('always')
        result=process_page(source,options=PageOptions(join_lines=True,granularity='rows'))
    detector_s=time.perf_counter()-start
    # Joined records can contain full duplicate singleton pieces: the original
    # addressed row geometry is already retained in each record's curves.
    rows=[{k:v for k,v in r.items() if k!='pieces'} for r in result.delivery]
    metadata={r['id']:r for r in result.rows}
    for row in rows:
        row['component_ids']=sorted({int(k) for i in metadata[row['row_id']]['line_indices']
                                    for k in result.segmentation.lines[i].component_ids})
        owned=result.segmentation.pixels.components[
            np.isin(result.segmentation.pixels.components[:,5],row['component_ids'])]
        row['owned_box']=([int(owned[:,0].min()),int(owned[:,1].min()),
                           int(owned[:,2].max()),int(owned[:,3].max())] if len(owned) else
                          [row['x0'],int(min(row['top'])),row['x1'],int(max(row['bottom']))])
    data=dict(schema=SCHEMA,image_size=result.image_size,rows=rows,
              structure_rows=result.rows,blocked_rows=result.blocked_rows,
              warnings=dict(__import__('collections').Counter(str(w.message) for w in notices)))
    cache.mkdir(parents=True,exist_ok=True)
    geometry.write_bytes(gzip.compress(json.dumps(data,allow_nan=False,separators=(',',':')).encode(),compresslevel=3,mtime=0))
    ink=result.segmentation.pixels.ink.astype(bool)
    Image.fromarray(ink).save(mask_path)
    labels=result.segmentation.pixels.labels
    np.savez_compressed(labels_path,labels=labels)
    receipt=dict(schema=SCHEMA,source=str(source),source_sha256=expected_sha,detector_sha256=detector_sha,
                 detector_s=detector_s,geometry_sha256=file_sha256(geometry),mask_sha256=file_sha256(mask_path),
                 row_ink_source='detector_assigned_components',labels_sha256=file_sha256(labels_path),
                 options=dict(join_lines=True,granularity='rows',tables=False,statistics=False,orientation=False))
    write_receipt(receipt_path,receipt)
    return data,ink,labels,dict(receipt,cache_hit=False)
