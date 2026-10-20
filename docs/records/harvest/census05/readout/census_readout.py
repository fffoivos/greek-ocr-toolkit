#!/usr/bin/env python3
"""Read published census exports; never import or execute the pipeline.

JSONL is streamed. An in-memory SQLite index retains only identities, disposition
and HOLD reasons, not row payloads. Root CURRENT and immutable ledger inventory
are control/input provenance; all verdicts come from the selected generation.
A finished, quiescent ledger with no nonempty WAL is required.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time

DISPOSITIONS = ('ADMIT', 'HOLD', 'DROP')
TOOLS = ('polytonic', 'cyrillic', 'numerics', 'dashes', 'content_repair')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    h = hashlib.sha256()
    with open(str(path), 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def records(path):
    with open(str(path), encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except ValueError as exc:
                    raise ValueError('%s:%d: %s' % (path, number, exc))


def key(row):
    return (str(row['parent_id']), str(row.get('id', row.get('row_id'))))


def reason_names(reasons):
    return sorted(set(r['reason'] if isinstance(r, dict) else r for r in reasons))


def deciding_stage(d):
    if d.get('pre_dedup_disposition', d['disposition']) != d['disposition']:
        return 'deduplication'
    stages = d.get('stages', [])
    if any(s.get('excluded') for s in stages if s['stage'] == 'content_gate'):
        return 'content_gate'
    first = (d.get('reasons') or [{}])[0].get('reason')
    for stage in reversed(stages):
        if first in reason_names(stage.get('checks', [])):
            return stage['stage']
    if first == 'segmentation':
        return 'segmentation'
    # finish() does not serialize a producer for these early returns. Preserve
    # that uncertainty rather than attributing a reason to an invented stage.
    producer = {'expectations_unresolved':'expectations', 'crop_identity_unresolved':'crop_identity',
                'correction_unresolved':'correction_routing', 'conflicting_edits':'composition',
                'routing_did_not_stabilize':'correction_routing',
                'candidate_scope_requires_recheck':'composition_scope',
                'content_repair_unresolved':'content_repair',
                'split_or_edition_identity_unresolved':'split_admission',
                'infrastructure_or_invalid_evidence':'census_exception'}
    return producer.get(first, 'finish (producer not serialized)')


class Counts:
    def __init__(self):
        self.data = defaultdict(Counter)
        self.columns = {}

    def add(self, name, columns, values, n=1):
        self.columns[name] = columns
        self.data[name][tuple('' if v is None else v for v in values)] += n

    def export(self):
        return {name: [dict(list(zip(self.columns[name], values)) + [('rows', n)])
                       for values, n in sorted(counts.items())]
                for name, counts in sorted(self.data.items())}


def readout(run, out, baseline=None, expect_rows=None, expect_pipeline_version=None):
    started = time.time()
    run, out = Path(run).resolve(), Path(out).resolve()
    if out == run or run in out.parents:
        raise ValueError('output must be outside the read-only run directory')
    files = {}

    def receipt(path):
        path = Path(path).resolve()
        files[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))
        return files[str(path)]

    current = json.loads((run / 'CURRENT.json').read_text())
    receipt(run / 'CURRENT.json')
    export_id = current.get('export_id', '')
    if current.get('status') != 'completed' or not export_id or Path(export_id).name != export_id:
        raise ValueError('CURRENT.json does not publish a completed generation')
    generation = (run / 'generations' / export_id).resolve()
    if generation.parent != (run / 'generations').resolve():
        raise ValueError('generation escapes run')
    for path in sorted(generation.iterdir()):
        if path.is_file():
            if path.resolve().parent != generation:
                raise ValueError('generation file escapes generation')
            receipt(path)
    summary = json.loads((generation / 'summary.json').read_text())
    if files[str(generation / 'summary.json')]['sha256'] != current['summary_sha256']:
        raise ValueError('published summary hash mismatch')
    for name, entry in summary.get('outputs', {}).items():
        path = generation / (name + '.jsonl')
        if files[str(path)]['sha256'] != entry['sha256']:
            raise ValueError('published output hash mismatch: ' + name)
    ledger = run / 'ledger.sqlite'
    wal = Path(str(ledger) + '-wal')
    if wal.exists() and wal.stat().st_size:
        raise ValueError('nonempty ledger WAL: require a finished checkpointed run')
    receipt(ledger)
    inventory = sqlite3.connect(ledger.as_uri() + '?mode=ro&immutable=1', uri=True)
    binding = json.loads(inventory.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
    binding_hash = hashlib.sha256(canonical(binding).encode('utf-8')).hexdigest()
    if binding_hash != current['run_binding_sha256'] or binding_hash != summary['run_binding_sha256']:
        raise ValueError('run binding mismatch')
    config = binding['config']
    index = sqlite3.connect(':memory:')
    index.executescript('''CREATE TABLE seen(parent TEXT,id TEXT,disposition TEXT,split TEXT,reasons TEXT,crop TEXT,
        PRIMARY KEY(parent,id));
        CREATE TABLE eligible(parent TEXT,id TEXT,payload TEXT,PRIMARY KEY(parent,id));
        CREATE TABLE exported(parent TEXT,id TEXT,PRIMARY KEY(parent,id));
        CREATE TABLE protected_crop(value TEXT PRIMARY KEY);
        CREATE TABLE protected_edition(value TEXT PRIMARY KEY);
        CREATE TABLE leak_keys(parent TEXT,id TEXT,PRIMARY KEY(parent,id));''')
    # line_pipeline_census.py:167-171: observed non-train/non-unassigned crops
    # union configured heldout_crop_sha256; edition protection is retained below.
    for crop in config.get('final_policy', {}).get('heldout_crop_sha256', []):
        index.execute('INSERT OR IGNORE INTO protected_crop VALUES (?)', (crop,))
    for edition in config.get('final_policy', {}).get('heldout_editions', []):
        index.execute('INSERT OR IGNORE INTO protected_edition VALUES (?)', (edition,))
    input_splits = Counter()
    inventory_counts = Counter()
    for parent, split, edition, payload in inventory.execute('SELECT parent,split,edition,payload FROM observations'):
        row = json.loads(payload)
        inventory_counts[parent] += 1
        input_splits[(parent, split)] += 1
        if split not in ('train', 'unassigned'):
            index.execute('INSERT OR IGNORE INTO protected_crop VALUES (?)', (row.get('crop_sha256'),))
        if split != 'train':
            index.execute('INSERT OR IGNORE INTO protected_edition VALUES (?)', (edition,))
    counts = Counts()
    problems = defaultdict(lambda: dict(count=0, first20=[]))

    def problem(name, detail):
        if name == 'heldout_leaks':
            try:
                index.execute('INSERT INTO leak_keys VALUES (?,?)', (detail['parent'],detail['id']))
            except sqlite3.IntegrityError:
                return
        item = problems[name]
        item['count'] += 1
        if 'parent' in detail:
            counts.add('issue_counts', ('issue','parent'), (name,detail['parent']))
        if len(item['first20']) < 20:
            item['first20'].append(detail)

    totals = Counter()
    versions = Counter()
    gate = Counter()
    route_statuses = Counter()
    seg_availability = Counter()
    summary_reasons = Counter()
    v3 = Counter(dict.fromkeys(('train', 'dev', 'test', 'unassigned'), 0))
    tool_versions = Counter()
    rows = 0
    for d in records(generation / 'decisions.jsonl'):
        rows += 1
        b = d['binding']; parent, row_id = key(b); split = b.get('split', '')
        disp = d['disposition']; totals[disp] += 1
        names = reason_names(d.get('reasons', []))
        try:
            index.execute('INSERT INTO seen VALUES (?,?,?,?,?,?)',
                          (parent, row_id, disp, split, canonical(names), b.get('crop_sha256')))
        except sqlite3.IntegrityError:
            problem('duplicates', dict(parent=parent, id=row_id))
        observed = inventory.execute('SELECT source,role,script,edition,split,payload FROM observations WHERE parent=? AND id=?', (parent, row_id)).fetchone()
        if observed is None:
            problem('unexpected_rows', dict(parent=parent, id=row_id))
            observed = ('UNKNOWN', 'UNKNOWN', 'UNKNOWN', '', '', '{}')
        source, role, script, edition, inventory_split, payload = observed
        # line_pipeline_census.py:204-214: inventory split=train AND decision=ADMIT,
        # exact exported row is dict(observation, final_text=..., decision=...).
        if inventory_split == 'train' and disp == 'ADMIT':
            expected_row = dict(json.loads(payload), final_text=d.get('final_text'), decision=d)
            index.execute('INSERT OR IGNORE INTO eligible VALUES (?,?,?)',
                          (parent, row_id, hashlib.sha256(canonical(expected_row).encode()).hexdigest()))
        dims = (parent, split, disp)
        counts.add('decisions_by_parent_split', ('parent', 'split', 'disposition'), dims)
        counts.add('by_stratum', ('parent', 'split', 'source', 'role', 'script', 'disposition'),
                   (parent, split, source, role, script, disp))
        for name, columns, values in (
                ('source_class', ('source', 'role'), (source, role)),
                ('source', ('source',), (source,)), ('class', ('role',), (role,))):
            counts.add(name, columns + ('parent', 'split', 'disposition'), values + dims)
        if parent.startswith('collect-v3'):
            v3[split] += 1
        for tool, tool_version in d.get('toolchain_versions', {}).items():
            tool_versions[(tool, tool_version)] += 1
        version = d.get('pipeline_version', 'MISSING'); versions[version] += 1
        if not isinstance(version, str) or not version or version == 'MISSING' or version != (expect_pipeline_version if expect_pipeline_version is not None else next(iter(versions))):
            problem('pipeline_version_mismatch', dict(parent=parent, id=row_id, version=version))
        if disp != 'ADMIT' and not names:
            problem('no_reason', dict(parent=parent, id=row_id, disposition=disp))
        if disp != 'ADMIT' and names:
            counts.add('deciding_reasons', ('reason', 'stage', 'parent', 'split', 'disposition'),
                       (d['reasons'][0]['reason'], deciding_stage(d)) + dims)
        carried = set(names)
        for stage in d.get('stages', []):
            for field in ('checks', 'suspicious', 'profile_flags'):
                carried.update(reason_names(stage.get(field, [])))
            if stage.get('result', {}).get('reason'):
                carried.add(stage['result']['reason'])
            if stage.get('excluded'):
                carried.add(stage['excluded'])
        for route in d.get('routes', {}).values():
            if route.get('reason'):
                carried.add(route['reason'])
        for reason in sorted(carried):
            counts.add('all_reasons', ('reason', 'parent', 'split', 'disposition'), (reason,) + dims)
        for reason in names:
            counts.add('all_disposition_reasons', ('reason', 'parent', 'split', 'disposition'), (reason,) + dims)
        for r in d.get('reasons', []):
            summary_reasons[r['reason']] += 1
        excluded = any(s.get('excluded') for s in d.get('stages', []) if s['stage'] == 'content_gate')
        if excluded:
            gate[disp] += 1
            for reason in names:
                gate[reason] += 1
                counts.add('gate_reasons', ('reason', 'source', 'role', 'parent', 'split', 'disposition'),
                           (reason, source, role) + dims)
            routes = d.get('routes', {})
            if any(routes.get(t, {}).get('status') != 'not_run_due_to_prior_exclusion' for t in set(TOOLS) | set(routes)):
                problem('gate_route_violations', dict(parent=parent, id=row_id))
            if any(s['stage'] == 'segmentation' and s.get('result', {}).get('verdict') is not None for s in d.get('stages', [])):
                problem('gate_segmentation_violations', dict(parent=parent, id=row_id))
        for s in d.get('stages', []):
            if s['stage'] == 'segmentation':
                result = s.get('result', {})
                seg_availability[result.get('availability', 'measured')] += 1
                counts.add('segmentation_reasons', ('reason', 'verdict', 'parent', 'split', 'disposition'),
                           (result.get('reason', ''), result.get('verdict', '')) + dims)
        for tool, route in d.get('routes', {}).items():
            route_statuses[tool + ':' + route['status']] += 1
            if route.get('edits'):
                counts.add('correction_edits', ('tool', 'status', 'parent', 'split', 'disposition'),
                           (tool, route['status']) + dims)
        if d.get('pre_dedup_disposition', disp) != disp:
            for reason in names:
                counts.add('dedup_changes', ('reason', 'before', 'parent', 'split', 'disposition'),
                           (reason, d['pre_dedup_disposition']) + dims)
        # ADMIT dev/test are evaluation passes, not training admissions.
        if disp == 'ADMIT' and split == 'train':
            crop_hit = index.execute('SELECT 1 FROM protected_crop WHERE value=?', (b.get('crop_sha256'),)).fetchone() is not None
            edition_hit = index.execute('SELECT 1 FROM protected_edition WHERE value=?', (edition,)).fetchone() is not None
            if crop_hit or edition_hit:
                problem('heldout_leaks', dict(parent=parent, id=row_id, crop=crop_hit, edition=edition_hit))
    for parent, row_id in inventory.execute('SELECT parent,id FROM observations ORDER BY parent,id'):
        if index.execute('SELECT 1 FROM seen WHERE parent=? AND id=?', (parent, row_id)).fetchone() is None:
            problem('missing_rows', dict(parent=parent, id=row_id))
    admitted_train = 0
    for row in records(generation / 'admitted_train.jsonl'):
        admitted_train += 1
        expected_row = index.execute('SELECT payload FROM eligible WHERE parent=? AND id=?', key(row)).fetchone()
        duplicate = index.execute('SELECT 1 FROM exported WHERE parent=? AND id=?', key(row)).fetchone()
        if duplicate or expected_row is None or expected_row[0] != hashlib.sha256(canonical(row).encode()).hexdigest():
            problem('admitted_train_equals_eligible', dict(parent=key(row)[0], id=key(row)[1], kind='duplicate' if duplicate else 'row_mismatch'))
        index.execute('INSERT OR IGNORE INTO exported VALUES (?,?)', key(row))
        found = index.execute('SELECT disposition,split,crop FROM seen WHERE parent=? AND id=?', key(row)).fetchone()
        if found != ('ADMIT', 'train', row.get('crop_sha256')) or row.get('split') != 'train':
            problem('admitted_train_violations', dict(parent=key(row)[0], id=key(row)[1]))
        crop_hit = index.execute('SELECT 1 FROM protected_crop WHERE value=?', (row.get('crop_sha256'),)).fetchone() is not None
        edition_hit = index.execute('SELECT 1 FROM protected_edition WHERE value=?', (row.get('edition_id'),)).fetchone() is not None
        if crop_hit or edition_hit:
            problem('heldout_leaks', dict(parent=key(row)[0], id=key(row)[1], crop=crop_hit, edition=edition_hit, export='admitted_train.jsonl'))
    for parent, row_id in index.execute('SELECT parent,id FROM eligible EXCEPT SELECT parent,id FROM exported'):
        problem('admitted_train_equals_eligible', dict(parent=parent, id=row_id, kind='missing'))
    pending = {}
    for path in sorted(generation.glob('pending_*.jsonl')):
        tool = path.stem[len('pending_'):]; pending[tool] = 0
        for row in records(path):
            pending[tool] += 1
            found = index.execute('SELECT disposition,split,reasons FROM seen WHERE parent=? AND id=?', key(row)).fetchone()
            disp, split, reasons = found if found else ('MISSING', row.get('split', ''), '[]')
            for reason in (json.loads(reasons) if disp == 'HOLD' else ['(no HOLD reason)']):
                counts.add('pending_reasons', ('tool', 'reason', 'source', 'role', 'parent', 'split', 'disposition'),
                           (tool, reason, row.get('source', ''), row.get('primary_class', row.get('content_role', ''))) + (key(row)[0], split, disp))
            counts.add('pending_rows', ('tool', 'source', 'role', 'parent', 'split', 'disposition'),
                       (tool, row.get('source', ''), row.get('primary_class', row.get('content_role', ''))) + (key(row)[0], split, disp))
    tables = counts.export()
    # Add rates with the exact grouping used by each source/class table.
    for name in ('source', 'class', 'source_class'):
        groups = defaultdict(Counter)
        for item in tables.get(name, []):
            columns = tuple(k for k in item if k not in ('disposition', 'rows'))
            group = tuple(item[k] for k in columns)
            groups[group][item['disposition']] += item['rows']
        # Cross-parent totals also provide source/class alone and source x class x split.
        rolled = Counter()
        rolled_columns = tuple(k for k in columns if k != 'parent')
        for item in tables.get(name, []):
            rolled[tuple(item[k] for k in rolled_columns) + (item['disposition'],)] += item['rows']
        tables[name + '_totals'] = [dict(list(zip(rolled_columns + ('disposition',), group)) + [('rows', n)])
                                   for group,n in sorted(rolled.items())]
        rolled_rates = defaultdict(Counter)
        for group,n in rolled.items():
            rolled_rates[group[:-1]][group[-1]] += n
        tables[name + '_totals_rates'] = [dict(list(zip(rolled_columns, group)) + [('rows',sum(c.values())),
                                                ('admitted',c['ADMIT']),('admit_rate',c['ADMIT']/float(sum(c.values())))])
                                               for group,c in sorted(rolled_rates.items())]
        tables[name + '_rates'] = [dict(list(zip(columns, group)) + [('rows', sum(c.values())),
                                     ('admitted', c['ADMIT']), ('admit_rate', c['ADMIT'] / float(sum(c.values())))])
                                  for group, c in sorted(groups.items())]
    for source_table, target_table, columns in (
            ('gate_reasons','gate_by_parent',('reason','parent','split','disposition')),
            ('gate_reasons','gate_by_source',('reason','source','split','disposition')),
            ('gate_reasons','gate_by_class',('reason','role','split','disposition')),
            ('deciding_reasons','deciding_reasons_totals',('reason','stage','disposition')),
            ('all_reasons','all_reasons_totals',('reason','disposition')),
            ('segmentation_reasons','segmentation_reasons_totals',('reason','verdict','disposition'))):
        rolled = Counter()
        for item in tables.get(source_table, []):
            rolled[tuple(item[k] for k in columns)] += item['rows']
        tables[target_table] = [dict(list(zip(columns, group)) + [('rows', n)]) for group,n in sorted(rolled.items())]
    expected = {p['id']: p['rows'] for p in config['parents']}
    tables['input_rows'] = [dict(parent=p, rows=n, registered=inventory_counts[p]) for p, n in sorted(expected.items())]
    tables['input_splits'] = [dict(parent=p, split=s, rows=n) for (p, s), n in sorted(input_splits.items())]
    stratum_columns = ('parent', 'split', 'source', 'role', 'script', 'disposition')
    def strata(items):
        result = Counter()
        for item in items:
            result[tuple(item.get(k, '') for k in stratum_columns)] += item['rows']
        return result
    actual, reported = strata(tables.get('by_stratum', [])), strata(summary['by_stratum'])
    mismatch = sum(abs(actual[k] - reported[k]) for k in set(actual) | set(reported))
    invariants = {}
    def check(name, failures):
        invariants[name] = dict(status='PASS' if failures == 0 else 'FAIL', count=failures)
    check('dispositions_sum', abs(rows - sum(totals[d] for d in DISPOSITIONS)))
    for name in ('admitted_train_equals_eligible', 'admitted_train_violations', 'heldout_leaks', 'gate_segmentation_violations', 'gate_route_violations',
                 'duplicates', 'missing_rows', 'unexpected_rows', 'no_reason', 'pipeline_version_mismatch'):
        check(name, problems[name]['count'])
    check('summary_by_stratum', mismatch)
    check('bound_inventory_counts', sum(abs(n - inventory_counts[p]) for p, n in expected.items()) +
          sum(n for p, n in inventory_counts.items() if p not in expected))
    check('summary_dispositions', sum(abs(totals[k] - summary['dispositions'].get(k, 0)) for k in set(totals) | set(summary['dispositions'])))
    if expect_rows is not None:
        check('expect_rows', abs(rows - expect_rows))
    complete = (summary.get('complete') is True and rows == sum(expected.values()) and
                not any(n for disp,n in totals.items() if disp not in DISPOSITIONS) and
                all(invariants[n]['status'] == 'PASS' for n in ('duplicates', 'missing_rows', 'unexpected_rows', 'bound_inventory_counts', 'no_reason')))
    if expect_rows is not None:
        complete = complete and rows == expect_rows
    if baseline:
        baseline = Path(baseline).resolve(); receipt(baseline)
        old = json.loads(baseline.read_text()); before = Counter(); after = Counter()
        for r in old['by_stratum']: before[(r['parent'], r['disposition'])] += r['rows']
        for r in tables.get('by_stratum', []): after[(r['parent'], r['disposition'])] += r['rows']
        tables['baseline'] = [dict(parent=p, disposition=d, before=before[(p,d)], after=after[(p,d)], delta=after[(p,d)]-before[(p,d)])
                              for p in sorted(set(k[0] for k in before) | set(k[0] for k in after)) for d in DISPOSITIONS]
    tool_binding = dict(path=config.get('versions'), sha256=binding.get('versions_sha256'))
    # Binding pins the tool manifest by hash. Read it only when available; never
    # substitute an unverified local manifest for the bound one.
    version_path = Path(config.get('versions', ''))
    if version_path.is_file():
        version_receipt = receipt(version_path)
        if version_receipt['sha256'] != binding.get('versions_sha256'):
            raise ValueError('bound tool manifest hash mismatch')
        tool_binding['tools'] = json.loads(version_path.read_text()).get('tools', {})
    else:
        tool_binding['availability'] = 'bound manifest unavailable; values seen in decisions below'
    result = dict(schema='census-readout-v1', generation=str(generation), files=list(files.values()),
                  input_rows=sum(expected.values()), rows=rows, complete=complete, dispositions=dict(totals),
                  admitted_train=admitted_train, gate=dict(gate), pending=pending, v3_splits=dict(v3),
                  pipeline_versions=dict(versions), expected_pipeline_version=expect_pipeline_version,
                  tool_versions_binding=tool_binding,
                  toolchain_versions_seen_note='toolchain_versions tables count values serialized in decisions',
                  summary_reason_counts=dict(summary_reasons), route_status_counts=dict(route_statuses),
                  segmentation_availability=dict(seg_availability), problems=dict(problems), invariants=invariants,
                  tables=tables, baseline=str(baseline) if baseline else None, elapsed_seconds=time.time()-started)
    # Versions are recorded in each decision; avoid reopening a mutable external version file.
    tables['toolchain_versions'] = [dict(tool=t, version=v, rows=n) for (t,v),n in sorted(tool_versions.items())]
    result['elapsed_seconds'] = time.time() - started
    inventory.close(); index.close()
    if json.loads((run / 'CURRENT.json').read_text()) != current:
        raise ValueError('publication changed during readout')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'readout.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    (out / 'READOUT.md').write_text(markdown(result))
    return result


def markdown(r):
    inv = r['invariants']; passed = sum(i['status'] == 'PASS' for i in inv.values())
    g = r['gate']; d = r['dispositions']; leaks = r['problems']['heldout_leaks']['count']
    status = 'PASS' if passed == len(inv) else 'FAIL'
    lines = ['%d rows; ADMIT %d / HOLD %d / DROP %d; admitted_train %d; gate exclusions %d; invariants %s (%d/%d).'
             % (r['rows'], d.get('ADMIT',0), d.get('HOLD',0), d.get('DROP',0), r['admitted_train'],
                sum(g.get(k,0) for k in DISPOSITIONS), status, passed, len(inv)), '',
             'Published generation: `%s`. Counts use exported dispositions and reasons only. '
             'Foreign-script gate reason is `unexpected_script` (the code name). '
             'Class is the ledger role, exactly summary.by_stratum.role; script is retained in by_stratum. '
             'all_reasons includes distinct reason names/strings from decisions, stages and routes, once per row; '
             'all_disposition_reasons contains only final disposition reasons. '
             'Held-out protection checks training admissions; dev/test ADMIT rows are evaluation passes. '
             'The protected crop list is the writer’s registered dev/test crops; protected editions are policy entries '
             'plus registered non-train editions. Root ledger is immutable input provenance, never a verdict source. '
             'Only compact identity indexes are retained in memory; JSONL payloads are streamed. '
             'Stage attribution uses serialized stages first, then known finish() call sites; missing producers are explicitly labeled. Failure counts in invariants are zero on PASS.' % r['generation'], '']
    def table(title, items, source):
        lines.extend(['### ' + title, '', 'Counted from: ' + source + '.', ''])
        if not items:
            lines.extend(['(zero rows)', '']); return
        columns = list(items[0])
        lines.append('| ' + ' | '.join(columns) + ' |')
        lines.append('| ' + ' | '.join('---' for _ in columns) + ' |')
        for item in items:
            lines.append('| ' + ' | '.join(str(item.get(k, '')).replace('|', '\\|').replace('\n', ' ') for k in columns) + ' |')
        lines.append('')
    table('Totals', [dict(disposition=k, rows=v) for k,v in sorted(d.items())], '`decisions.jsonl`')
    for title, value, source in [('Disposition reason occurrences', r['summary_reason_counts'], '`decisions.jsonl`'),
                                  ('Route statuses', r['route_status_counts'], '`decisions.jsonl`'),
                                  ('Segmentation availability', r['segmentation_availability'], '`decisions.jsonl`'),
                                  ('Gate totals', g, '`decisions.jsonl`'), ('V3 splits', r['v3_splits'], '`decisions.jsonl`'),
                                  ('Pending totals', r['pending'], '`pending_<tool>.jsonl`'),
                                  ('Pipeline versions', r['pipeline_versions'], '`decisions.jsonl`')]:
        table(title, [dict(value=k, rows=v) for k,v in sorted(value.items())], source)
    table('Admission export', [dict(rows=r['admitted_train'])], '`admitted_train.jsonl`')
    table('Completeness', [dict(rows=r['rows'], input_rows=r['input_rows'], complete=r['complete'])], '`decisions.jsonl`, ledger binding')
    table('Invariants', [dict(invariant=k, **v) for k,v in sorted(inv.items())], '`decisions.jsonl`, `admitted_train.jsonl`, `summary.json`, ledger inventory')
    for title, items in sorted(r['tables'].items()):
        source = '`decisions.jsonl` + ledger inventory'
        if title.startswith('pending'): source = '`pending_<tool>.jsonl` + `decisions.jsonl`'
        if title.startswith('input'): source = '`ledger.sqlite` binding/observations'
        if title == 'baseline': source = '`%s` + `decisions.jsonl`' % r['baseline']
        table(title, items, source)
    table('Timing', [dict(elapsed_seconds=r['elapsed_seconds'])], 'readout process wall clock')
    table('Tool version binding', [r['tool_versions_binding']], '`ledger.sqlite` run binding')
    table('Diagnostics (first 20 in file order)', [dict(issue=k, count=v['count'], first20=canonical(v['first20'])) for k,v in sorted(r['problems'].items())], '`decisions.jsonl`, `admitted_train.jsonl`, ledger inventory')
    table('File provenance', r['files'], 'files named below (streamed SHA256)')
    if not r['baseline']:
        lines.extend(['No baseline supplied; no historical delta inferred. The handoff records 65,900 admissions.', ''])
    lines.append('CENSUS READOUT: rows %d (complete %s); ADMIT %d HOLD %d DROP %d; admitted_train %d; gate DROP %d HOLD %d (mixed %d foreign %d short %d cell1 %d num1 %d unresolved %d); pending %s; heldout leaks %d; invariants %d/%d PASS' %
                 (r['rows'], 'yes' if r['complete'] else 'no', d.get('ADMIT',0), d.get('HOLD',0), d.get('DROP',0), r['admitted_train'],
                  g.get('DROP',0), g.get('HOLD',0), g.get('mixed_script_word',0), g.get('unexpected_script',0), g.get('short_line',0),
                  g.get('single_character_cell',0), g.get('numeric_shape',0), g.get('cell_status_unresolved',0),
                  ', '.join('%s %d' % item for item in sorted(r['pending'].items())) or 'none', leaks, passed, len(inv)))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True); parser.add_argument('--out', required=True)
    parser.add_argument('--baseline'); parser.add_argument('--expect-rows', type=int)
    parser.add_argument('--expect-pipeline-version')
    args = parser.parse_args()
    r = readout(args.run, args.out, args.baseline, args.expect_rows, args.expect_pipeline_version)
    print(markdown(r).splitlines()[-1])
    return 0 if all(v['status'] == 'PASS' for v in r['invariants'].values()) and r['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
