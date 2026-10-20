#!/usr/bin/env python3
"""Streaming release v3 export. No network, Slurm, OCR or crop reconstruction."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unicodedata


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(x):
    return hashlib.sha256(x.encode('utf-8')).hexdigest()


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def records(p):
    opener = gzip.open if str(p).endswith('.gz') else open
    with opener(p, 'rt', encoding='utf-8') as f:
        for line in f:
            require(bool(line.strip()), 'blank JSONL line: ' + str(p))
            yield json.loads(line)


def write_json(p, x):
    Path(p).write_text(canonical(x) + '\n', encoding='utf-8')


def resolve(root, p):
    return Path(p) if Path(p).is_absolute() else root / p


def load_config(p):
    p = Path(p).resolve()
    return p.parent, json.loads(p.read_text())


def input_check(root, cfg, light=False):
    result, pending = [], []
    for item in cfg['inputs']:
        p = resolve(root, item['path'])
        if item['kind'] == 'large' and light:
            require(p.is_file(), 'missing large input: ' + str(p))
            require(p.stat().st_size == item['bytes'], 'input size mismatch: ' + str(p))
            result.append(dict(item, check='exists_and_size_only'))
        else:
            require(p.is_file() and sha(p) == item['sha256'], 'input sha mismatch: ' + str(p))
            result.append(dict(item, check='sha256', bytes=p.stat().st_size))
    byname = {i['name']: resolve(root, i['path']) for i in cfg['inputs']}
    current = json.loads(byname['CURRENT.json'].read_text())
    summary = json.loads(byname['summary.json'].read_text())
    require(current['status'] == 'completed' and summary['complete'] and summary['reconciled'], 'incomplete census')
    require(current['summary_sha256'] == sha(byname['summary.json']), 'CURRENT summary mismatch')
    for name in ('admitted_train', 'admission_records'):
        item = next(x for x in cfg['inputs'] if x['name'] == name)
        require(summary['outputs'][name]['sha256'] == item['sha256'], 'census output receipt sha mismatch')
    for crop in cfg['crops']:
        attempt = Path(crop['attempt'])
        receipt = attempt / 'upload_receipt.json'
        if not receipt.is_file():
            pending.append(crop['tranche'] + '_CROPS4_receipt')
            continue
        r = json.loads(receipt.read_text())
        require(r['status'] == 'ok' and r['mode'] == 'full' and r['sha256check_exit'] == 0
                and r['failures'] == 0 and r['mismatches'] == 0 and r['byte_exact'] == r['selected'], 'CROPS4 receipt failed')
        require(r['context']['tranche'] == crop['tranche'], 'CROPS4 tranche mismatch')
        require(Path(r['output_base']).resolve() == Path(cfg['work_root']).resolve(), 'CROPS4 wrong output base')
        require(r['context']['inputs']['CURRENT.json'] == sha(byname['CURRENT.json'])
                and r['context']['inputs']['summary.json'] == sha(byname['summary.json'])
                and r['context']['inputs']['admitted_train'] == summary['outputs']['admitted_train']['sha256'], 'CROPS4 census mismatch')
        for n in ('crops_manifest.jsonl', 'crops_sha256.txt'):
            require((attempt / n).is_file(), 'CROPS4 missing ' + n)
        result.append(dict(name=crop['tranche'] + '_CROPS4', path=str(receipt), sha256=sha(receipt), check='receipt_status'))
    return byname, result, pending


def validate_edits(row, cfg):
    """Replay recorded raw-coordinate edits, then recorded normalization only."""
    d, raw = row['decision'], row['raw_text']
    require(d['raw_text_sha256'] == digest(raw), 'raw text binding mismatch')
    require(d['final_text'] == row['final_text'] and d['final_text_sha256'] == digest(row['final_text']), 'final text binding mismatch')
    versions = {r['tool']: r for r in cfg['registry'] if r['mode'] == 'census_internal'}
    tools = {}
    for tool, route in d['routes'].items():
        if not route.get('edits'):
            continue
        require(route['status'] == 'applied' and tool in versions, 'unregistered applied tool')
        v = versions[tool]
        require(route['tool_version'] == v['version'] and route['tool_digest'] == v['tool_digest'], 'edit tool/version mismatch')
        require(route['raw_text_sha256'] == digest(raw) and route['binding'] == d['binding'], 'route binding mismatch')
        ev = route.get('evidence', {})
        require(bool(ev.get('artifact_sha256')), 'edit provenance lacks artifact sha')
        sources = {a['sha256'] for a in v['artifacts'] if a['parent_id'] == row['parent_id']}
        source_sha = ev.get('split_input_binding', {}).get('source_artifact_sha256', ev['artifact_sha256'])
        require(source_sha in sources, 'edit artifact not in frozen census registry')
        for e in route['edits']:
            tools.setdefault((e['start'], e['end'], e['before'], e['after']), set()).add(tool)
    applied = d.get('edits', [])
    require(len(applied) == len(tools), 'merged edit count mismatch')
    previous = None
    for e in applied:
        a, b = e['start'], e['end']
        require(type(a) is int and type(b) is int and 0 <= a <= b <= len(raw) and raw[a:b] == e['before'], 'invalid raw span')
        require(set(e['tools']) == tools.get((a, b, e['before'], e['after'])), 'merged edit provenance mismatch')
        if previous:
            pa, pb = previous
            require(a >= pb and a != pa and not (a == pb and a == b), 'overlapping edits')
        previous = (a, b)
    text = raw
    for e in reversed(applied):
        text = text[:e['start']] + e['after'] + text[e['end']:]
    norm = d.get('normalization')
    if norm:
        require(norm['policy'] == 'NFC-and-whitespace-only' and norm['before'] == text, 'unknown normalization provenance')
        require(norm['after'] == ' '.join(unicodedata.normalize('NFC', text).split()), 'normalization differs from recorded policy')
        text = norm['after']
    require(text == row['final_text'], 'recorded edits do not reconstruct admitted label')
    return applied, norm


def crop_index(cfg):
    crops, receipts = {}, []
    for c in cfg['crops']:
        a = Path(c['attempt'])
        r = json.loads((a / 'upload_receipt.json').read_text())
        sums = {}
        with (a / 'crops_sha256.txt').open() as f:
            for line in f:
                h, path = line.rstrip('\n').split('  ', 1)
                require(path not in sums, 'duplicate crop checksum path')
                sums[path] = h
        count = 0
        for m in records(a / 'crops_manifest.jsonl'):
            rel = Path(m['relative_path'])
            require(not rel.is_absolute() and '..' not in rel.parts, 'unsafe crop path')
            expected_prefix = 'collection_' + c['tranche'].lower() + '_originals'
            require(rel.parts[0] == expected_prefix and m['parent_id'] in cfg['parents'], 'crop tranche/parent mismatch')
            require(m['parent_id'].startswith('collect-v3-' + c['tranche'] + '-'), 'crop wrong parent tranche')
            require(sums.pop(str(rel), None) == m['sha256'], 'crop manifest/checksum mismatch')
            key = (m['parent_id'], m['row_id'])
            require(key not in crops, 'duplicate crop key')
            crops[key] = (m['sha256'], str(rel), m['bytes'])
            count += 1
        require(not sums and count == r['byte_exact'] == r['selected'], 'incomplete CROPS4 manifest')
        receipts.append(dict(tranche=c['tranche'], files={n:dict(path=str(a/n), sha256=sha(a/n), bytes=(a/n).stat().st_size)
                         for n in ('upload_receipt.json', 'crops_manifest.jsonl', 'crops_sha256.txt')}))
    return crops, receipts


def build(config, output):
    root, cfg = load_config(config)
    output = Path(output)
    require(output.is_absolute(), 'output must be absolute')
    require(not output.exists(), 'output exists; choose a new attempt')
    paths, receipts, pending = input_check(root, cfg)
    require(not pending, 'pending inputs: ' + ','.join(pending))
    crops, crop_receipts = crop_index(cfg)
    editions, books = {}, {}
    for r in records(paths['edition_map.jsonl']):
        require(r['edition_id'] not in editions, 'duplicate edition')
        editions[r['edition_id']] = r['split']
        for book in r['member_documents']:
            require(book not in books, 'duplicate edition member')
            books[book] = r['edition_id']
    candidates = set()
    for r in records(paths['candidates_v3.jsonl']):
        candidates.add((r['parent_id'], r['row_id']))
    pixels, readout_keys = set(), set()
    for r in records(paths['candidates_readout.jsonl']):
        key = (r['parent_id'], r['row_id'])
        require(key in candidates, 'readout not a benchmark candidate')
        readout_keys.add(key)
        pixels.add(r['crop_sha256'])
    require(readout_keys == candidates, 'incomplete benchmark pixel readout')
    registry = [dict(r, release_rows_touched=0, release_rows_with_record=0) for r in cfg['registry']]
    # External sparse overlays: compact IDs and changed flag only, no payload retention.
    external = {}
    for r in registry:
        if r['mode'] == 'external_registered_not_applied':
            p = resolve(root, r['file'])
            require(sha(p) == r['sha256'], 'external registry sha mismatch')
            idx = {}
            for x in records(p):
                key = (r['parent_id'], x[r['id_field']])
                require(key not in idx, 'duplicate external correction row')
                idx[key] = x[r['text_field']] != x[r['parent_text_field']]
            external[r['name']] = idx
    output.mkdir(parents=True)
    counts = Counter({n:0 for n in ('input_w1_w2_train','excluded_dev_test_edition','excluded_benchmark_key','excluded_benchmark_pixels','excluded_missing_exact_crop','released','edited_rows')})
    source_counts, edition_counts = Counter(), Counter()
    selected = {}  # compact tuple -> canonical decision digest; never retains JSON payloads
    try:
        with (output/'release_v3_admission.jsonl').open('w', encoding='utf-8') as adm, (output/'release_v3_edits.jsonl').open('w', encoding='utf-8') as edits:
            for row in records(paths['admitted_train']):
                if row['parent_id'] not in cfg['parents']:
                    continue
                counts['input_w1_w2_train'] += 1
                key = (row['parent_id'], row['id'])
                d = row['decision']
                require(row['split'] == 'train' and d['admitted'] and d['disposition'] == 'ADMIT', 'invalid admitted train row')
                require(d['binding'] == {k:row[k] for k in ('parent_id','id','split','crop_sha256')}, 'decision binding mismatch')
                ed = books.get(row['book_id'])
                require(ed is not None and ed == row['edition_id'], 'SPLIT2 edition identity mismatch')
                if editions[ed] in ('dev','test'):
                    counts['excluded_dev_test_edition'] += 1
                    continue
                require(editions[ed] == 'train', 'unknown edition split')
                if key in candidates:
                    counts['excluded_benchmark_key'] += 1
                    continue
                if row['crop_sha256'] in pixels:
                    counts['excluded_benchmark_pixels'] += 1
                    continue
                crop = crops.get(key)
                if crop is None or crop[0] != row['crop_sha256']:
                    counts['excluded_missing_exact_crop'] += 1
                    continue
                image = Path(cfg['work_root'])/crop[1]
                if not image.is_file() or image.stat().st_size != crop[2] or sha(image) != crop[0]:
                    counts['excluded_missing_exact_crop'] += 1
                    continue
                applied, norm = validate_edits(row, cfg)
                require(key not in selected, 'duplicate release key')
                selected[key] = digest(canonical(d))
                ref = dict(file=str(paths['admission_records']), file_sha256=next(x['sha256'] for x in cfg['inputs'] if x['name']=='admission_records'),
                           key=dict(parent_id=key[0],row_id=key[1]),decision_sha256=selected[key])
                admission = dict(parent_id=key[0],row_id=key[1],source=row['source'],edition_id=ed,split='train',crop_relative_path=crop[1],
                                 crop_sha256=crop[0],label=row['final_text'],raw_text_sha256=d['raw_text_sha256'],admission_decision=ref)
                adm.write(canonical(admission)+'\n')
                changed = row['final_text'] != row['raw_text']
                if changed:
                    counts['edited_rows'] += 1
                    edits.write(canonical(dict(parent_id=key[0],row_id=key[1],raw_text=row['raw_text'],raw_text_field=row['raw_text_field'],
                        label=row['final_text'],raw_text_sha256=d['raw_text_sha256'],edits=applied,normalization=norm,
                        routes=d['routes'],toolchain_versions=d['toolchain_versions'],toolchain_digest=d['toolchain_digest'],admission_decision=ref))+'\n')
                for r in registry:
                    if r['mode']=='external_registered_not_applied':
                        idx = external[r['name']]
                        r['release_rows_with_record'] += key in idx
                        r['release_rows_touched'] += bool(idx.get(key))
                    else:
                        touch = bool(norm) if r['tool']=='composer' else any(r['tool'] in e['tools'] for e in applied)
                        r['release_rows_touched'] += changed and touch
                        r['release_rows_with_record'] += bool(norm) if r['tool']=='composer' else r['tool'] in d['routes']
                counts['released'] += 1
                source_counts[row['source']] += 1
                edition_counts[ed] += 1
        require(counts['excluded_dev_test_edition'] == 0, 'assertion: dev/test edition present in admitted train')
        require(counts['excluded_benchmark_key'] == 0, 'assertion: benchmark key present in admitted train')
        require(counts['released'] > 0, 'empty release')
        found = set()
        for r in records(paths['admission_records']):
            key = (r['parent_id'], r['row_id'])
            if key in selected:
                require(key not in found and r['pass'] and r['split']=='train' and r['disposition']=='ADMIT', 'admission record invalid/duplicate')
                require(digest(canonical(r['decision'])) == selected[key] and r['label']==r['decision']['final_text'], 'admission decision differs')
                found.add(key)
        require(len(found)==len(selected), 'missing admission records')
        # Recheck small receipts/manifests after streaming; the job hashes large inputs again to detect mutation.
        input_check(root,cfg)
        for c in crop_receipts:
            for f in c['files'].values():
                require(sha(f['path'])==f['sha256'], 'CROPS4 changed during build')
        write_json(output/'corrections_registry.json',dict(schema='release-v3-corrections-registry-v1',versions=registry,sf7=cfg['sf7']))
        outputs = {n:dict(sha256=sha(output/n),bytes=(output/n).stat().st_size) for n in ('release_v3_admission.jsonl','release_v3_edits.jsonl','corrections_registry.json')}
        receipt = dict(schema='release-v3-receipt-v1',status='ok',inputs=receipts,crops=crop_receipts,counts=dict(counts),counts_per_source=dict(source_counts),
                       counts_per_edition=dict(edition_counts),outputs=outputs,config_sha256=sha(config),admission_receipt_chain={n:dict(path=str(paths[n]),sha256=sha(paths[n])) for n in ('CURRENT.json','summary.json','readout.json','candidates_readout.jsonl')})
        write_json(output/'RELEASE_V3_RECEIPT.json',receipt)
        return receipt
    except Exception as exc:
        write_json(output/'FAILED.json',dict(status='failed',reason=str(exc),counts=dict(counts)))
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path(__file__).with_name('INPUTS.json'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    require(a.output.is_absolute(),'output must be absolute')
    root,cfg=load_config(a.config)
    if cfg.get('schema')=='release-v3-package-v1':
        base=Path(cfg['work_root'])/'release_v3'
        require(a.output.parent.resolve()==base.resolve() and a.output.name!='pkg', 'production output must be new $W/release_v3/<attempt>')
    r=build(a.config,a.output)
    print(canonical(r['counts']))

if __name__=='__main__':
    main()
