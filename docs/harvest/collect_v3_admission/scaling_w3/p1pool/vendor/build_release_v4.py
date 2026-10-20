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
from rel4_contract import apply_spans, reason, sf7_index, sf7_record


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
    require(cfg['sf7']['status']=='released', 'sf7 not released')
    if cfg['schema']=='release-v4-package-v1':
        names=[x['name'] for x in cfg['inputs']]
        require(len(names)==len(set(names)) and all(n in names for n in ('CURRENT.json','summary.json','admitted_train','admission_records','readout.json','census06_config.json','census06_tool_versions.json','seal04_test','seal04_dev','seal04_suite.json','seal04_receipt.json','RELEASE_V3_RECEIPT.json','release_v3_admission')), 'incomplete production bindings')
        require(cfg['census_attempt']==str(Path(cfg['work_root'])/'census_06_20261020/attempts/full-split-002'), 'wrong census_06 root')
    for item in cfg['inputs']:
        if item.get('sha256') is None or item.get('path') is None:
            require(item.get('group') == 'census_06', 'unclassified pending input')
            pending.append('census_06')
            continue
        p = resolve(root, item['path'])
        if item['kind'] == 'large' and light:
            require(p.is_file() and p.stat().st_size == item['bytes'], 'input size mismatch: ' + str(p))
            result.append(dict(item, check='exists_and_size_only'))
        else:
            if light:
                require(p.stat().st_size < 64*1024*1024, 'small input exceeds light-check limit')
            require(p.is_file() and sha(p) == item['sha256'], 'input sha mismatch: ' + str(p))
            result.append(dict(item, check='sha256', bytes=p.stat().st_size))
    byname = {i['name']: resolve(root, i['path']) for i in cfg['inputs'] if i.get('path')}
    if 'census_06' not in pending:
        current = json.loads(byname['CURRENT.json'].read_text())
        summary = json.loads(byname['summary.json'].read_text())
        require(current['status'] == 'completed' and summary['complete'] and summary['reconciled'], 'incomplete census')
        require(current['summary_sha256'] == sha(byname['summary.json']), 'CURRENT summary mismatch')
        if cfg['schema'] == 'release-v4-package-v1':
            base = Path(cfg['census_attempt']).resolve()
            require(byname['CURRENT.json'].resolve() == base/'CURRENT.json', 'wrong census_06 attempt')
            require(Path(current['summary_path']).resolve() == byname['summary.json'].resolve(), 'wrong census generation')
            require(byname['summary.json'].resolve().is_relative_to(base/'generations'), 'summary outside census generation')
            cc = json.loads(byname['census06_config.json'].read_text())
            binding=cfg['census_run_binding']
            require(digest(canonical(binding))==current['run_binding_sha256']==summary['run_binding_sha256'], 'census run binding mismatch')
            require(binding['config']==dict(cc,routes_out_of_scope=cc.get('routes_out_of_scope',[])), 'census config differs from completed run')
            require(binding['versions_sha256']==sha(byname['census06_tool_versions.json']), 'census tool versions sha mismatch')
            require('polytonic' not in cc.get('routes_out_of_scope', []), 'polytonic out of scope')
            require([x for x in cc['corrections'] if x['tool']=='polytonic'] == cfg['sf7']['ledgers'], 'sf7 census ledger bindings differ')
            tv = json.loads(byname['census06_tool_versions.json'].read_text())['tools']['polytonic']
            require(tv['version']==cfg['sf7']['version'] and tv['digest']==cfg['sf7']['tool_digest'], 'sf7 tool binding differs')
            readout = json.loads(byname['readout.json'].read_text())
            require(readout['complete'] and not any(v['count'] for v in readout['problems'].values()) and all(v['status']=='PASS' for v in readout['invariants'].values()), 'census readout invariants failed')
            require(byname['readout.json'].resolve()==Path(str(base)+'.readout')/'readout.json', 'wrong sibling readout')
            require(Path(readout['generation']).resolve()==byname['summary.json'].resolve().parent, 'readout generation mismatch')
            require(all(any(Path(f['path']).resolve()==byname[n].resolve() and f['sha256']==sha_value for f in readout['files']) for n,sha_value in [('CURRENT.json',sha(byname['CURRENT.json'])),('summary.json',sha(byname['summary.json']))]+[(n,summary['outputs'][n]['sha256']) for n in ('admission_records','admitted_train')]), 'readout admission sha mismatch')
        for name in ('admitted_train', 'admission_records'):
            item = next(x for x in cfg['inputs'] if x['name'] == name)
            require(summary['outputs'][name]['sha256'] == item['sha256'], 'census output receipt sha mismatch')
            if cfg['schema'] == 'release-v4-package-v1':
                require(byname[name].resolve().parent == byname['summary.json'].resolve().parent, 'mixed census generations')
    if cfg['sf7']['binding_status'] != 'bound':
        pending.append('sf7')
    else:
        require(bool(cfg['sf7']['ledgers']), 'empty sf7 ledger binding')
        for ledger in cfg['sf7']['ledgers']:
            p=resolve(root,ledger['path'])
            require(ledger['status']=='released' and p.is_file(), 'sf7 ledger missing/unreleased')
            if light:
                require(p.stat().st_size==cfg['sf7'].get('ledger_sizes',{}).get(ledger['sha256'],ledger.get('bytes')), 'sf7 ledger size mismatch')
            else:
                require(sha(p)==ledger['sha256'], 'sf7 ledger sha mismatch')
        result.append(dict(name='sf7',check='ledger_sizes_only' if light else 'ledger_sha256',ledgers=cfg['sf7']['ledgers']))
    old = json.loads(byname['RELEASE_V3_RECEIPT.json'].read_text())
    old_input=next(i for i in cfg['inputs'] if i['name']=='release_v3_admission')
    require(old['status']=='ok' and old['outputs']['release_v3_admission.jsonl']['sha256']==old_input['sha256'], 'REL3 receipt mismatch')
    if cfg.get('seal04_suite_sha256'):
        require(sha(byname['seal04_suite.json'])==cfg['seal04_suite_sha256'], 'seal04 suite mismatch')
        seal=json.loads(byname['seal04_receipt.json'].read_text())
        require(seal['status']=='SEALED' and seal['suite_sha256']==cfg['seal04_suite_sha256'], 'seal04 receipt mismatch')
    for crop in cfg['crops']:
        attempt = Path(crop['attempt']); receipt = attempt/'upload_receipt.json'
        if not receipt.is_file():
            pending.append(crop['tranche']+'_CROPS4_receipt'); continue
        if crop.get('receipt_sha256'):
            require(sha(receipt)==crop['receipt_sha256'], 'CROPS4 receipt sha mismatch')
        r=json.loads(receipt.read_text())
        require(r['status']=='ok' and r['mode']=='full' and r['sha256check_exit']==0 and r['failures']==0 and r['mismatches']==0 and r['byte_exact']==r['selected'], 'CROPS4 receipt failed')
        require(r['context']['tranche']==crop['tranche'], 'CROPS4 tranche mismatch')
        require(Path(r['output_base']).resolve()==Path(cfg['work_root']).resolve(), 'CROPS4 wrong output base')
        custody=cfg.get('crop_census') or {n:sha(byname[n]) for n in ('CURRENT.json','summary.json','admitted_train')}
        require(all(r['context']['inputs'][n]==custody[n] for n in ('CURRENT.json','summary.json','admitted_train')), 'CROPS4 census mismatch')
        for n in ('crops_manifest.jsonl','crops_sha256.txt'):
            require((attempt/n).is_file(), 'CROPS4 missing '+n)
        result.append(dict(name=crop['tranche']+'_CROPS4',path=str(receipt),sha256=sha(receipt),check='receipt_status'))
    if 'crops4c' in cfg:
        if cfg['crops4c']['binding_status'] != 'bound':
            pending.append('crops4c')
        elif 'census_06' not in pending:
            from crops4c_contract import check
            result.append(check(root,cfg,byname,sha,require))
    return byname, result, sorted(set(pending))


def validate_edits(row, cfg):
    """Replay recorded raw-coordinate edits, then recorded normalization only."""
    d, raw = row['decision'], row['raw_text']
    require(d.get('pipeline_version') == '0.3.3', 'pipeline_version must equal 0.3.3')
    route=d.get('routes',{}).get('polytonic',{})
    if route.get('status') == 'kept_unverified':
        ev=route.get('evidence',{})
        require(not route.get('edits') and ev.get('kept_unverified') is True and isinstance(ev.get('reason'),str) and ev['reason'].strip(), 'invalid kept_unverified')
    require(d['raw_text_sha256'] == digest(raw), 'raw text binding mismatch')
    require(d['final_text'] == row['final_text'] and d['final_text_sha256'] == digest(row['final_text']), 'final text binding mismatch')
    versions = {r['tool']: r for r in cfg['registry'] if r['mode'] == 'census_internal' or r['name'] == 'sf7'}
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
    specs=list(cfg['crops'])
    if cfg.get('crops4c',{}).get('binding_status')=='bound':
        specs.append(dict(tranche='all',attempt=cfg['crops4c']['attempt']))
    for c in specs:
        a = Path(c['attempt'])
        r = json.loads((a / 'upload_receipt.json').read_text())
        sums = {}
        with (a / 'crops_sha256.txt').open() as f:
            for line in f:
                h, path = line.rstrip('\n').split('  ', 1)
                require(path not in sums, 'duplicate crop checksum path')
                sums[path] = h
        count = 0; local_keys=set(); splits=Counter(); tranches=Counter(); tranche_bytes=Counter(); total_bytes=0
        for m in records(a / 'crops_manifest.jsonl'):
            rel = Path(m['relative_path'])
            require(not rel.is_absolute() and '..' not in rel.parts, 'unsafe crop path')
            tranche = 'W1' if m['parent_id'].startswith('collect-v3-W1-') else 'W2'
            require(c['tranche'] in (tranche,'all'), 'crop wrong tranche')
            expected_prefix = 'collection_' + tranche.lower() + '_originals'
            require(rel.parts[0] == expected_prefix and m['parent_id'] in cfg['parents'], 'crop tranche/parent mismatch')
            require(m['parent_id'].startswith('collect-v3-' + tranche + '-'), 'crop wrong parent tranche')
            require(str(rel)==str(Path(expected_prefix)/m['source']/(m['row_id']+'.png')), 'crop identity/path mismatch')
            require(m['split'] in ('train','dev','test'), 'crop split mismatch')
            require(sums.pop(str(rel), None) == m['sha256'], 'crop manifest/checksum mismatch')
            key = (m['parent_id'], m['row_id'])
            value=(m['sha256'], str(rel), m['bytes'])
            require(key not in local_keys, 'duplicate crop key')
            local_keys.add(key)
            require(key not in crops or crops[key]==value, 'conflicting crop union')
            crops[key] = value
            count += 1
            splits[m['split']]+=1; tranches[tranche]+=1; tranche_bytes[tranche]+=m['bytes']; total_bytes+=m['bytes']
        if c['tranche']=='all':
            require(splits['train']==r['train_selected'] and splits['dev']+splits['test']==r['heldout_selected'] and total_bytes==r['bytes'], 'CROPS4C manifest totals')
            require(all(tranches[t]==r['per_tranche'][t]['selected'] and tranche_bytes[t]==r['per_tranche'][t]['bytes'] for t in ('W1','W2')), 'CROPS4C manifest tranches')
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
    if 'decisions' in paths:
        for decision in records(paths['decisions']):
            require(decision.get('pipeline_version')=='0.3.3', 'pipeline_version must equal 0.3.3')
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
    for name in ('seal04_test','seal04_dev'):
        for r in records(paths[name]):
            require(r['split']==name.split('_')[1], 'seal04 split mismatch')
            candidates.add((r['parent_id'],r['row_id']))
            pixels.add(r['crop_sha256'])
    old_rows = {}
    for r in records(paths['release_v3_admission']):
        key=(r['parent_id'],r['row_id'])
        require(key not in old_rows, 'duplicate REL3 key')
        old_rows[key]=r['source']
    ledger_index=sf7_index(root,cfg,records,sha,require,digest,canonical)
    registry = [dict(r, release_rows_touched=0, release_rows_with_record=0) for r in cfg['registry']]
    # External sparse overlays: compact IDs and changed flag only, no payload retention.
    external = {}
    for r in registry:
        if r['mode'] == 'external_registered_not_applied' and r['name'] != 'sf7':
            p = resolve(root, r['file'])
            require(sha(p) == r['sha256'], 'external registry sha mismatch')
            idx = {}
            for x in records(p):
                key = (r['parent_id'], x[r['id_field']])
                require(key not in idx, 'duplicate external correction row')
                idx[key] = x[r['text_field']] != x[r['parent_text_field']]
            external[r['name']] = idx
    output.mkdir(parents=True)
    counts = Counter({n:0 for n in ('input_w1_w2_train','excluded_dev_test_edition','excluded_benchmark_key','excluded_benchmark_pixels','excluded_missing_exact_crop','released','edited_rows','sf7_edited_rows','missing_crop_new_admits')})
    source_counts, edition_counts = Counter(), Counter()
    missing_new = Counter({p:0 for p in cfg['parents']})
    added_reasons, removed_reasons = {}, {}
    released_ids=set()
    flip_counts=Counter()
    poly_counts=Counter()
    def flip(direction, key, source, decision):
        why=reason(decision)
        flip_counts[(direction,key[0],source,why)]+=1
        return dict(direction=direction,parent_id=key[0],row_id=key[1],source=source,reason=why,decision=decision)
    selected = {}  # compact tuple -> canonical decision digest; never retains JSON payloads
    try:
        with (output/'release_v4_admission.jsonl').open('w', encoding='utf-8') as adm, (output/'release_v4_edits.jsonl').open('w', encoding='utf-8') as edits, (output/'release_v4_sf7_edits.jsonl').open('w', encoding='utf-8') as sf7, (output/'release_v4_flips.jsonl').open('w', encoding='utf-8') as flips:
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
                    if key not in old_rows:
                        counts['missing_crop_new_admits'] += 1; missing_new[key[0]] += 1
                    continue
                image = Path(cfg['work_root'])/crop[1]
                if not image.is_file() or image.stat().st_size != crop[2] or sha(image) != crop[0]:
                    counts['excluded_missing_exact_crop'] += 1
                    if key not in old_rows:
                        counts['missing_crop_new_admits'] += 1; missing_new[key[0]] += 1
                    continue
                applied, norm = validate_edits(row, cfg)
                require(row['id'] not in released_ids, 'overlay cannot express cross-parent row ID collision')
                released_ids.add(row['id'])
                overlay=sf7_record(row,ledger_index,require,digest,canonical)
                if overlay:
                    sf7.write(canonical(overlay)+'\n'); counts['sf7_edited_rows']+=1
                if key not in old_rows:
                    flips.write(canonical(flip('added',key,row['source'],d))+'\n')
                require(key not in selected, 'duplicate release key')
                selected[key] = digest(canonical(d))
                ref = dict(file=str(paths['admission_records']), file_sha256=next(x['sha256'] for x in cfg['inputs'] if x['name']=='admission_records'),
                           key=dict(parent_id=key[0],row_id=key[1]),decision_sha256=selected[key])
                admission = dict(parent_id=key[0],row_id=key[1],source=row['source'],edition_id=ed,split='train',crop_relative_path=crop[1],
                                 crop_sha256=crop[0],label=row['raw_text'],raw_text_sha256=d['raw_text_sha256'],admission_decision=ref)
                require(admission['label']==row['raw_text'] and digest(admission['label'])==admission['raw_text_sha256'], 'release label is not raw')
                status=d['routes'].get('polytonic',{}).get('status')
                if status in ('kept_unverified','applied','verified_no_change'):
                    poly_counts[(key[0],row.get('primary_class',row.get('content_role','unknown')),status)]+=1
                if status=='kept_unverified':
                    require(admission['label']==row['raw_text'], 'kept_unverified label is not raw')
                adm.write(canonical(admission)+'\n')
                other_edits=[dict(e,tools=[t for t in e['tools'] if t!='polytonic']) for e in applied if any(t!='polytonic' for t in e['tools'])]
                other_text=apply_spans(row['raw_text'],other_edits)
                other_norm=None
                if norm and norm['before']!=norm['after']:
                    other_norm=dict(before=other_text,after=' '.join(unicodedata.normalize('NFC',other_text).split()),policy=norm['policy'])
                    other_text=other_norm['after']
                changed = other_text != row['raw_text'] or bool(other_edits) or bool(other_norm)
                if changed:
                    counts['edited_rows'] += 1
                    edits.write(canonical(dict(parent_id=key[0],row_id=key[1],raw_text=row['raw_text'],raw_text_field=row['raw_text_field'],
                        label=other_text,raw_text_sha256=d['raw_text_sha256'],edits=other_edits,normalization=other_norm,census_normalization=norm,
                        routes={k:v for k,v in d['routes'].items() if k!='polytonic'},normalization_context='recorded after all census edits; not applied to release or sf7',toolchain_versions=d['toolchain_versions'],toolchain_digest=d['toolchain_digest'],admission_decision=ref))+'\n')
                for r in registry:
                    if r['name']=='sf7':
                        r['release_rows_with_record'] += key in ledger_index
                        if key in ledger_index:
                            spec,record,reference=ledger_index[key]
                            route=d['routes'].get('polytonic',{})
                            r['release_rows_touched'] += bool(overlay)
                    elif r['mode']=='external_registered_not_applied':
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
        require(not counts['missing_crop_new_admits'], 'missing_crop_new_admits must be zero')
        require(counts['released'] > 0, 'empty release')
        found = set(); removed_found=set()
        for r in records(paths['admission_records']):
            require(r['decision'].get('pipeline_version')=='0.3.3', 'pipeline_version must equal 0.3.3')
            key = (r['parent_id'], r['row_id'])
            if key in old_rows and key not in selected:
                require(key not in removed_found, 'duplicate removed decision')
                require(r['source']==old_rows[key], 'removed source mismatch')
                with (output/'release_v4_flips.jsonl').open('a',encoding='utf-8') as flips:
                    flips.write(canonical(flip('removed',key,r['source'],r['decision']))+'\n')
                removed_found.add(key)
            if key in selected:
                require(key not in found and r['pass'] and r['split']=='train' and r['disposition']=='ADMIT', 'admission record invalid/duplicate')
                require(digest(canonical(r['decision'])) == selected[key] and r['label']==r['decision']['final_text'], 'admission decision differs')
                found.add(key)
        require(len(found)==len(selected), 'missing admission records')
        require(removed_found == set(old_rows)-set(selected), 'missing removed census decision')
        # Recheck small receipts/manifests after streaming; the job hashes large inputs again to detect mutation.
        input_check(root,cfg)
        for c in crop_receipts:
            for f in c['files'].values():
                require(sha(f['path'])==f['sha256'], 'CROPS4 changed during build')
        sfreg=next(r for r in registry if r['name']=='sf7')
        sfreg.update(sha256=sha(output/'release_v4_sf7_edits.jsonl'),ledger_shas=[x['sha256'] for x in cfg['sf7']['ledgers']],binding_status='bound')
        write_json(output/'corrections_registry.json',dict(schema='release-v4-corrections-registry-v1',versions=registry,sf7=cfg['sf7']))
        outputs = {n:dict(sha256=sha(output/n),bytes=(output/n).stat().st_size) for n in ('release_v4_admission.jsonl','release_v4_edits.jsonl','release_v4_sf7_edits.jsonl','release_v4_flips.jsonl','corrections_registry.json')}
        receipt = dict(schema='release-v4-receipt-v1',status='ok',inputs=receipts,crops=crop_receipts,counts=dict(counts),counts_per_source=dict(source_counts),
                       counts_per_edition=dict(edition_counts),polytonic_released_per_parent_class=[dict(parent_id=p,line_class=c,status=s,rows=n) for (p,c,s),n in sorted(poly_counts.items())],
                       polytonic_released_per_parent={p:{s:sum(n for (pp,c,ss),n in poly_counts.items() if pp==p and ss==s) for s in ('kept_unverified','applied','verified_no_change')} for p in cfg['parents']},
                       polytonic_released_per_class={c:{s:sum(n for (pp,cc,ss),n in poly_counts.items() if cc==c and ss==s) for s in ('kept_unverified','applied','verified_no_change')} for c in sorted({c for p,c,s in poly_counts})},missing_crop_new_admits_per_parent=dict(missing_new),
                       requires_crops4_top_up=bool(counts['missing_crop_new_admits']),labels='raw_text asserted per row',
                       flips=[dict(direction=d,parent_id=p,source=s,reason=r,rows=n) for (d,p,s,r),n in sorted(flip_counts.items())],outputs=outputs,config_sha256=sha(config),admission_receipt_chain={n:dict(path=str(paths[n]),sha256=sha(paths[n])) for n in ('CURRENT.json','summary.json','admission_records','admitted_train','readout.json','candidates_readout.jsonl','release_v3_admission','RELEASE_V3_RECEIPT.json')})
        write_json(output/'RELEASE_V4_RECEIPT.json',receipt)
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
    require(cfg.get('schema')=='release-v4-package-v1', 'CLI requires production schema')
    if cfg.get('schema')=='release-v4-package-v1':
        base=Path(cfg['work_root'])/'release_v4'
        require(a.output.parent.resolve()==base.resolve() and a.output.name!='pkg', 'production output must be new $W/release_v4/<attempt>')
    r=build(a.config,a.output)
    print(canonical(r['counts']))

if __name__=='__main__':
    main()
