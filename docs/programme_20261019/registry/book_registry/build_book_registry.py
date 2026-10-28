"""Extract RUNNER5 protections and join harvested identities; never run its builder.

Offline, read-only inputs. Conflicting holdouts use split=conflict_hold_out and
exportable=False; the CLI exits 2 after writing the diagnostic artifact.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
WAVES = ('round1', 'round2', 'mixed', 'cyrillic', 'openarchives', 'parliament', 'vouli', 'wikisource')
ROW_ROLES = {'lqb', 'release_exclusion'}
REFERENCE_NAMESPACES = {'catalogue_reference', 'page_pdf_sha256'}


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def prefix(value):
    return re.sub(r'(?:--s\d+|--p\d+|--n\d+|-p\d+).*$', '', str(value))


def provider(source, record):
    s = str(record.get('provider') or source or '').lower()
    if 'anemi' in s or s in ('round1', 'round2', 'mixed'):
        return 'anemi'
    for key in ('bsb', 'nlg', 'gazette', 'serbia', 'wikisource', 'parliament', 'vouli', 'openarchives'):
        if key in s:
            return key
    if s.startswith(('ia', 'archive')) or s in ('greek_latin', 'greek_poly', 'poly1850', 'poly1900'):
        return 'ia'
    return s or 'unknown'


def aliases(record, source='', wave=None):
    """Strong observed aliases only; no title-only or guessed identifier joins."""
    out = set()
    p = provider(source, record)

    def add(ns, value):
        if isinstance(value, (str, int)) and str(value):
            out.add((ns, str(value)))

    def identity(value):
        if not isinstance(value, (str, int)) or not str(value):
            return
        value = str(value)
        if value.startswith(('http://', 'https://', '/metadata/')):
            if value.startswith('/metadata/'):
                value = 'https://anemi.lib.uoc.gr' + value
            u = urlsplit(value)
            host = u.netloc.lower()
            path = unquote(u.path).rstrip('/')
            # URLs retain query identities; scheme and %-encoding are immaterial.
            add('source_url', host + path + ('?' + u.query if u.query else ''))
            m = re.search(r'archive.org/(?:details|download)/([^/]+)', host + path)
            if m:
                add('ia_identifier', m[1])
                add('provider_item:ia', m[1])
            if 'anemi.lib.uoc.gr' in host and path.startswith('/metadata/') and path.endswith('.tkl'):
                add('provider_item:anemi', path)
            if 'nlg.gr' in host:
                m = re.search(r'/([0-9]+)(?:/|$)', path)
                if m:
                    add('nlg_catalogue', m[1])
            m = re.search(r'bsb\d+', value)
            if m:
                add('provider_item:bsb', m[0])
            return
        if re.fullmatch(r'bsb\d+', value):
            add('provider_item:bsb', value)
        elif re.fullmatch(r'(?:round1|round2|mixed|cyrillic|openarchives|parliament|vouli|wikisource):.+', value):
            add('v2_book_id', value)
            add('line_id_prefix', value.split(':', 1)[1])
        elif '--' in value:
            add('line_id_prefix', prefix(value))
            add('edition_id', prefix(value))
        else:
            add('provider_item:' + p, value)
            if p == 'ia':
                add('ia_identifier', value)
            if p == 'nlg':
                add('nlg_catalogue', value)

    for key in ('item', 'book', 'book_id', 'identifier', 'provider_id', 'record_id', 'doc', 'document_id', 'book_key', 'key'):
        v = record.get(key)
        if key in ('key', 'book_key') and v:
            add('line_id_prefix', v)
            if wave in WAVES:
                add('v2_book_id', wave + ':' + str(v))
        else:
            identity(v)
    rid = record.get('id')
    if rid:
        if re.search(r'(?:-l\d+|--s\d+|--p\d+|-p\d+|--n\d+)', str(rid)):
            add('line_id_prefix', prefix(rid))
        else:
            identity(rid)
    for key in ('aliases', 'document_ids', 'member_documents'):
        for v in record.get(key, []) or []:
            identity(v)
    for key in ('source_url', 'item_url', 'pdf_url', 'url', 'index_url', 'scan_url', 'commons_url', 'manifest_url'):
        identity(record.get(key))
    # A catalogue landing page can describe multiple periodical issues. Retain
    # the locator, but never union books on this descriptive reference alone.
    add('catalogue_reference', record.get('catalogue_url'))
    for key in ('pdf_sha256', 'full_pdf_sha256', 'full_pdf_hash'):
        v = record.get(key)
        if isinstance(v, str) and re.fullmatch('[a-f0-9]{64}', v):
            page_pdf = key == 'pdf_sha256' and bool(re.search(r'/page-\d+', str(record.get('pdf', ''))))
            add('page_pdf_sha256' if page_pdf else 'pdf_sha256', v)
    return out


def decide(assignments):
    labels = sorted({a['split'] for a in assignments if a.get('scope', 'book') == 'book' and a['split'] not in ROW_ROLES and not a.get('superseded_by')})
    base = {s.replace('seal04_', '') for s in labels if s in ('train', 'dev', 'test', 'seal04_dev', 'seal04_test')}
    protections = set(labels) & {'hold_out'}
    conflict = len(base) > 1 or ('train' in base and bool(protections))
    if conflict:
        return ('conflict_hold_out' if 'train' in base and 'hold_out' in protections else 'unassigned'), 'conflict', False
    if base:
        b = next(iter(base))
        return ('seal04_' + b if 'seal04_' + b in labels else b), 'assigned', True
    if len(protections) == 1:
        return next(iter(protections)), 'assigned', True
    if len(protections) > 1:
        return 'unassigned', 'multiple_protection_roles', False
    return 'unassigned', 'no_recorded_split', False


def origin_reason(group):
    waves = {n['wave'] for n in group if n['wave']}
    paths = {n['evidence']['file'] for n in group}
    if waves & {'W3', 'W4'}:
        return 'w3_w4_pending'
    if any(p.endswith('/collection/import_real_all.jsonl') for p in paths):
        return 'superseded_wave'
    if any(n['page'] for n in group):
        return 'harvested_not_admitted'
    if waves:
        return 'catalogue_only'
    return 'line_instrument_only'


def instrument_records(registry, bind):
    """Consume the canonical declaration, retaining exact line IDs and list role."""
    declaration = json.loads(registry.read_text())
    result = []
    def walk(value, trail=()):
        if isinstance(value, dict):
            if str(value.get('file', '')).endswith('.txt'):
                path = registry.parent / value['file']
                ev = bind(path, 'row_instrument_list', value['sha256'])
                ids = path.read_text().splitlines()
                if len(ids) != value['n'] or len(set(ids)) != len(ids):
                    raise ValueError('instrument count/identity mismatch: ' + str(path))
                # The declaration hierarchy, not a joined producer-entry's
                # mixed-origin filename string, defines each individual role.
                kind = 'lqb' if any('lqb' in t.lower() for t in trail) else 'release_exclusion'
                for rid in ids:
                    result.append(dict(row_id=rid, kind=kind, list_name=path.name,
                        list_sha256=ev['sha256'], declaration_path='.'.join(trail)))
            for k, v in value.items():
                walk(v, trail + (k,))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, trail + (str(i),))
    walk(declaration)
    return sorted(result, key=canonical)


class Registry:
    def __init__(self):
        self.nodes = []
        self.parents = []
        self.index = {}

    def find(self, n):
        while self.parents[n] != n:
            self.parents[n] = self.parents[self.parents[n]]
            n = self.parents[n]
        return n

    def add(self, aa, evidence, assignment=None, wave=None, page=None):
        if not aa:
            raise ValueError('identity has no usable alias: ' + canonical(evidence))
        n = len(self.nodes)
        self.parents.append(n)
        self.nodes.append(dict(aliases=set(aa), evidence=evidence, assignment=assignment, wave=wave, page=page))
        for a in sorted(aa):
            if a[0] in REFERENCE_NAMESPACES:
                continue
            if a in self.index:
                self.parents[self.find(n)] = self.find(self.index[a])
            self.index[a] = n

    def materialize(self, ruling=None, ruling_provenance=None):
        groups = defaultdict(list)
        for i, n in enumerate(self.nodes):
            groups[self.find(i)].append(n)
        result = []
        for group in groups.values():
            aa = sorted(set().union(*(n['aliases'] for n in group)))
            # Deterministic for a frozen manifest. Future identity amendments get
            # a new registry version; never assume IDs survive alias expansion.
            preferred = next((a for ns in ('seal04_edition_hash', 'provider_item:bsb', 'ia_identifier', 'nlg_catalogue', 'v2_book_id', 'line_id_prefix') for a in aa if a[0] == ns), aa[0])
            bid = 'book-' + hashlib.sha256(canonical(preferred).encode()).hexdigest()[:24]
            assignments = sorted({canonical(n['assignment']) for n in group if n['assignment']})
            assignments = [json.loads(a) for a in assignments]
            resolved_ruling = None
            if ruling and (ruling['alias']['namespace'], ruling['alias']['value']) in aa:
                labels = sorted({a['split'] for a in assignments if a.get('scope', 'book') == 'book' and a['split'] not in ROW_ROLES})
                if bid != ruling['book_id'] or labels != ruling['expected_split_labels']:
                    raise ValueError('ruling identity or historical split labels changed')
                if ruling['split'] != 'train' or not ruling['harvest_protection']:
                    raise ValueError('unsupported split ruling')
                for a in assignments:
                    if a['split'] == 'hold_out' and a.get('scope', 'book') == 'book':
                        a['superseded_by'] = ruling['ruling_id']
                assignments.append(dict(split='train', scope='book', reason=ruling['reason'],
                    provenance=ruling_provenance, ruling_id=ruling['ruling_id']))
                resolved_ruling = ruling['ruling_id']
            split, state, exportable = decide(assignments)
            reason = origin_reason(group) if state == 'no_recorded_split' else None
            if reason:
                split = 'unassigned_' + reason
            protection = any(n['evidence'].get('producer_reason') for n in group)
            result.append(dict(book_id=bid, split=split, assignment_status=state, exportable=exportable,
                conflict=state == 'conflict', split_labels=sorted({a['split'] for a in assignments if a.get('scope', 'book') == 'book' and a['split'] not in ROW_ROLES}),
                harvest_protection=protection or resolved_ruling is not None, unassigned_reason=reason,
                split_resolution_ruling=resolved_ruling,
                origin_waves=sorted({n['wave'] for n in group if n['wave']}),
                row_instrument_roles=sorted({a['split'] for a in assignments if a['split'] in ROW_ROLES}),
                aliases=[dict(namespace=ns, value=v) for ns, v in aa], assignments=assignments,
                identity_provenance=[json.loads(e) for e in sorted({canonical(n['evidence']) for n in group})],
                waves=sorted({n['wave'] for n in group if n['wave']}),
                observed_pages=len({(n['wave'], n['page']) for n in group if n['page']})))
        return sorted(result, key=lambda r: r['book_id'])


def build(projects, output, repo=REPO):
    inputs = {}
    coverage = []
    reg = Registry()

    def bind(path, kind, expected=None):
        path = Path(path).resolve()
        if str(path) not in inputs:
            inputs[str(path)] = dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size, kinds=[])
        info = inputs[str(path)]
        if kind not in info['kinds']:
            info['kinds'].append(kind)
        if expected and info['sha256'] != expected:
            raise ValueError('pinned input changed: ' + str(path))
        return dict(file=str(path), sha256=info['sha256'])

    root = projects / 'greek-ocr-toolkit-sol-collect'
    pp = root / 'docs/harvest/collect_v3/w3b/receipts/protected_registry_v3.json'
    pe = bind(pp, 'canonical_RUNNER5_protections', 'a05814d9996b731cacd8fc4d986484a38fbc40d0cbb5359f130b81ab7e6a4c33')
    protected = json.loads(pp.read_text())
    if protected['unresolved'] or not protected['fail_closed']:
        raise ValueError('RUNNER5 protections unresolved')
    for item in protected['inputs']:
        bind(item['path'], 'RUNNER5:' + item['kind'], item['sha256'])
    producer_commit = 'f4795e8b0'
    producer_code = []
    for name in ('collect_v3/w3b/protected.py', 'collect_v3/exclusions.py'):
        committed = subprocess.check_output(['git', '-C', str(root), 'show', producer_commit + ':' + name])
        expected = hashlib.sha256(committed).hexdigest()
        producer_code.append(bind(root / name, 'producer_code_at_' + producer_commit, expected))
    declaration = root / 'docs/harvest/collect_v3/release_exclusions/release_exclusions.json'
    instrument_declaration = bind(declaration, 'row_instrument_declaration')
    instruments = instrument_records(declaration, bind)
    instrument_kinds = {r['list_name']: r['kind'] for r in instruments}
    for i, entry in enumerate(protected['entries']):
        reason = entry['reason']
        ev = dict(pe, locator=f'entries[{i}]', producer_reason=reason, producer_origin=canonical(entry['origin']))
        origins = entry['origin'] if isinstance(entry['origin'], list) else [entry['origin']]
        sources = []
        for origin in origins:
            # An origin can be file:line#field, file#edition or a plain file.
            path = re.sub(r':\d+(?:#.*)?$', '', str(origin).split('#')[0])
            sources.append(bind(path, 'assignment_origin'))
        if reason.startswith('seal04_'):
            label = 'seal04_dev' if 'dev' in reason else 'seal04_test'
        elif reason.startswith('v2_'):
            label = 'dev' if '_dev.' in reason else 'test'
        elif reason == 'holdout':
            label = 'hold_out'
        else:
            label = None  # Each line instrument retains its own declared role.
        aa = aliases(entry['identity'], entry['source'])
        if reason.startswith('seal04_') and not reason.endswith('_alias'):
            eid = str(entry['origin']).split('#')[-1]
            aa.update({('seal04_edition_hash', eid), ('edition_id', eid)})
        # Source-less holdouts still have local book keys/URLs; those bridge to
        # harvested catalogues instead of guessing the provider from the title.
        if label is None:
            for source in sources:
                kind = instrument_kinds[Path(source['file']).name]
                reg.add(aa, ev, dict(split=kind, scope='row', provenance=[source], runner5_entry=i, reason=reason))
        else:
            reg.add(aa, ev, dict(split=label, scope='book', provenance=sources, runner5_entry=i, reason=reason))

    # Explicit edition memberships supply RUNNER5's edition hashes and aliases.
    edpath = projects / 'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/split1/editions.jsonl'
    sppath = edpath.parent.parent / 'split2/edition_map.jsonl'
    ee = bind(edpath, 'edition_identity'); se = bind(sppath, 'edition_split')
    splitmap = {r['edition_id']: r for r in rows(sppath)}
    for e in rows(edpath):
        eid = e['edition_id']; s = splitmap[eid]['split']
        aa = {('edition_id', eid), ('seal04_edition_hash', eid)}
        aa.update(('line_id_prefix', d) for d in e['member_documents'])
        for m in e['metadata']:
            aa.update(aliases(m, m.get('source', '')))
            for r in m.get('records', []):
                aa.update(aliases(r['metadata'], m.get('source', '')))
        if s not in ('train', 'dev', 'test'):
            raise ValueError('unknown edition split ' + s)
        label = 'seal04_' + s if s in ('dev', 'test') else s
        reg.add(aa, dict(ee, locator=eid), dict(split=label, provenance=[se], reason='split2 edition_map', edition_id=eid))

    # Harvest page manifests cover failed/dropped pages before row admission.
    legacy = projects / 'greek-ocr-toolkit/docs/harvest'
    for wave in WAVES:
        p = legacy / wave / 'manifest.json'; ev = bind(p, 'legacy_harvest_pages')
        x = json.loads(p.read_text()); rr = x['pages'] if isinstance(x, dict) else x
        for r in rr:
            r = dict(r)
            image = r.get('image') or ''
            key = re.sub(r'-\d{6}$', '', Path(image).stem) if image else r.get('key')
            if key:
                r['book_key'] = key
            reg.add(aliases(r, r.get('source', wave), wave), ev, wave=wave, page=image or r.get('id') or str(r.get('page')))
        coverage.append(dict(ev, wave=wave, records=len(rr)))
        # Catalogues bind local book keys even for books with zero retained rows.
        for name in ('books.json', 'selection.json'):
            p = legacy / wave / name
            if not p.exists():
                continue
            x = json.loads(p.read_text())
            rr = x if isinstance(x, list) else x.get('books', [])
            ev = bind(p, 'legacy_book_catalogue')
            for r in rr:
                if isinstance(r, dict) and (r.get('book') or r.get('key') or r.get('id')):
                    reg.add(aliases(r, r.get('source', wave), wave), ev, wave=wave)
    # The page inventory includes rescue/auxiliary observations outside the
    # main manifests. Read locators only; never scan or re-encode raster bytes.
    inventory = repo / 'out/runner4/SOURCE_FILES_legacy_page_images.tsv'
    ev = bind(inventory, 'all_retained_legacy_page_inventory')
    n = 0
    with inventory.open() as f:
        for r in csv.DictReader(f, delimiter='\t'):
            path = Path(r['relative_path']); wave = path.parts[0]
            key = prefix(re.sub(r'-\d{6}$', '', path.stem))
            aa = {('line_id_prefix', key), ('v2_book_id', wave + ':' + key)}
            image = 'docs/harvest/harvest_big/' + r['relative_path']
            reg.add(aa, ev, wave=wave, page=image); n += 1
    coverage.append(dict(ev, wave='all_retained_legacy_images', records=n))
    # Auxiliary pilot pages have their own local namespace and retained source
    # descriptors. Follow those exact metadata pointers, not guessed hashes.
    auxpath = repo / 'docs/records/harvest/page_reads_v1/manifest.json'
    ae = bind(auxpath, 'auxiliary_page_manifest'); aux = json.loads(auxpath.read_text())
    for r in aux:
        pilot = Path(r['pilot_page_json']); ev = bind(pilot, 'auxiliary_page_identity')
        page = json.loads(pilot.read_text())['page']
        reg.add(aliases(page, page.get('source', '')), ev, wave='page_reads_v1', page=r['image'])
    coverage.append(dict(ae, wave='page_reads_v1', records=len(aux)))
    for wave, p in [(w, projects / f'collect-v3-data/run/{w}_manifest.jsonl') for w in ('W1', 'W2', 'W3')] + [('W4', projects / 'greek-ocr-toolkit-sol-w4/docs/harvest/collect_v3/w4/runtime/W4_manifest.jsonl')]:
        ev = bind(p, 'harvest_page_manifest'); n = 0
        for r in rows(p):
            aa = aliases(dict(r.get('item_record', {}), item=r['item']), r['source'])
            aa.add(('line_id_prefix', prefix(r['id'])))
            reg.add(aa, ev, wave=wave, page=r['id']); n += 1
        coverage.append(dict(ev, wave=wave, records=n))

    # Collapse repeated line observations before storing book provenance. Only
    # current v2 supplies split assignments; earlier collection splits are kept
    # as identity evidence, never silently substituted for current v2.
    testpath = legacy / 'collection/v2/import_real_v2_test.jsonl'
    testev = bind(testpath, 'reserved_to_test_membership')
    lexicon_policy = [bind(repo / name, 'lexicon_v2_policy') for name in (
        'docs/records/harvest/collection/v2/split_moves_v2.json',
        'docs/records/harvest/collection/v2/CLEAN_REPORT.md', 'scripts/harvest/apply_clean.py')]
    testids = {r['id'] for r in rows(testpath)}
    reservedids = set()
    for name, assign in [('import_real_all.jsonl', False), ('v2/import_real_v2_all.jsonl', True)]:
        p = legacy / 'collection' / name; ev = bind(p, 'collection_book_identities')
        seen = set(); n = 0
        for r in rows(p):
            n += 1
            if assign and r.get('split') == 'reserved':
                reservedids.add(r['id'])
            key = (r.get('doc'), r.get('source_url'), r.get('split'))
            if key in seen:
                continue
            seen.add(key)
            # Retain book namespace, URL and line prefix, without row text.
            aa = aliases(r, r.get('source', ''))
            s = {'val': 'dev', 'validation': 'dev', 'reserved': 'test'}.get(r.get('split'), r.get('split'))
            assignment = dict(split=s, provenance=[ev] + ([testev] if r.get('split') == 'reserved' else []), reason='collection-v2 recorded split; reserved IDs verified against v2_test', source_split=r['split']) if assign else None
            if assignment and r.get('source') == 'archive_b28038630':
                assignment['provenance'].extend(lexicon_policy)
            if assign and s not in ('train', 'dev', 'test', 'hold_out'):
                raise ValueError('unknown collection split ' + str(s))
            reg.add(aa, ev, assignment, wave=r.get('wave'))
        coverage.append(dict(ev, wave='v2' if assign else 'collection_legacy', records=n, distinct_book_records=len(seen)))
    if reservedids != testids:
        raise ValueError('v2 reserved IDs differ from the recorded v2 test population')

    ruling_path = HERE / 'SPLIT_RULING.json'
    ruling_ev = bind(ruling_path, 'coordinator_split_ruling')
    ruling = json.loads(ruling_path.read_text())
    ruling_provenance = [ruling_ev] + [bind(repo / name, 'ruling_policy') for name in ruling['policy_files']]
    records = reg.materialize(ruling, ruling_provenance)
    if sum(r['split_resolution_ruling'] == ruling['ruling_id'] for r in records) != 1:
        raise ValueError('ruling must resolve exactly one canonical book')
    # Verify every pinned file remained unchanged throughout the extraction.
    for item in inputs.values():
        if sha(item['path']) != item['sha256']:
            raise ValueError('input changed during extraction: ' + item['path'])
    output.mkdir(parents=True, exist_ok=True)
    # Arrow structs have a uniform field set, with null for absent historical
    # fields. Use exactly that representation in the JSONL transport too.
    table = pa.Table.from_pylist(records)
    records = table.to_pylist()
    raw = ''.join(canonical(r) + '\n' for r in records).encode()
    (output / 'book_registry.jsonl.gz').write_bytes(gzip.compress(raw, mtime=0))
    pq.write_table(table, output / 'book_registry.parquet', compression='zstd')
    pq.write_table(pa.Table.from_pylist(instruments), output / 'row_instruments.parquet', compression='zstd')
    assert pq.read_table(output / 'book_registry.parquet').to_pylist() == records
    conflicts = [dict(book_id=r['book_id'], split_labels=r['split_labels'], assignments=r['assignments'], aliases=r['aliases']) for r in records if r['conflict']]
    report = dict(schema='runner4-book-registry-v1', producer='RUNNER5 protected_registry_v3.json consumed read-only; not rebuilt',
        runner5_registry=pe, runner5_entries=len(protected['entries']), runner5_unresolved=protected['unresolved'],
        runner5_producer_commit=producer_commit, runner5_producer_code=producer_code,
        split_ruling=dict(ruling_ev, ruling_id=ruling['ruling_id']),
        books=len(records), counts_per_split=dict(sorted(Counter(r['split'] for r in records).items())),
        harvest_protected_books=sum(r['harvest_protection'] for r in records),
        row_instruments=dict(declaration=instrument_declaration, memberships=len(instruments), distinct_rows=len({r['row_id'] for r in instruments}),
            per_kind=dict(Counter(r['kind'] for r in instruments))),
        assignment_states=dict(Counter(r['assignment_status'] for r in records)), conflicts=conflicts,
        coverage=coverage, inputs=sorted(inputs.values(), key=lambda r:r['path']),
        code_sha256=sha(Path(__file__)), producing_head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(),
        publishable=not conflicts, network=False, uploads=False)
    (output / 'BUILD_RECEIPT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    sums = []
    for p in sorted(output.iterdir()):
        if p.is_file() and p.name != 'SHA256SUMS' and p.suffix != '.pyc':
            sums.append(f'{sha(p)}  {p.name}\n')
    (output / 'SHA256SUMS').write_text(''.join(sums))
    print(canonical({k:report[k] for k in ('books','counts_per_split','assignment_states','publishable')}))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--projects', type=Path, default=Path.home() / 'Projects')
    p.add_argument('--output', type=Path, default=HERE)
    a = p.parse_args(); report = build(a.projects, a.output)
    raise SystemExit(2 if report['conflicts'] else 0)


if __name__ == '__main__':
    main()
