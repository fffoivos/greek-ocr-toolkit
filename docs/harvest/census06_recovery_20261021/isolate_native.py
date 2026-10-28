"""Read-only matched error/control measurement outside the sealed code and ledger."""
import argparse, collections, concurrent.futures, hashlib, importlib, json, pathlib, statistics, struct, sys, threading, time


def matched_items(snapshot):
    errors, controls = snapshot['errors'], snapshot['succeeded_controls']
    assert errors and len(errors) == len(controls), 'equal nonempty control set required'
    parent_counts = lambda rows: collections.Counter(r['observation']['parent_id'] for r in rows)
    assert parent_counts(errors) == parent_counts(controls), 'parent mix differs'
    keys = [(r['observation']['parent_id'], r['observation']['id']) for r in errors + controls]
    assert len(keys) == len(set(keys)), 'duplicate/overlapping observations'
    assert all(r['decision']['disposition'] == 'INFRA_ERROR' for r in errors)
    assert all(r['decision']['disposition'] != 'INFRA_ERROR' and any(s['stage'] == 'segmentation' and 'result' in s for s in r['decision']['stages']) for r in controls), 'controls must have succeeded native results'
    by_parent = collections.defaultdict(list)
    for row in reversed(controls): by_parent[row['observation']['parent_id']].append(row)
    items = []
    for i, error in enumerate(errors):
        pair = [('former_error', error), ('succeeded_control', by_parent[error['observation']['parent_id']].pop())]
        if i % 2: pair.reverse()
        items.extend(pair)
    return items


def measure_row(item, worker, call, clock=time.monotonic):
    cohort, item = item; row = item['observation']
    record = dict(cohort=cohort, parent=row['parent_id'], id=row['id'], position=item['decision_insertion_position'], cold=worker.process is None, worker_thread=threading.current_thread().name, worker_call=call, text_length=len(row['raw_text']), primary_class=row.get('primary_class'), book=row['book_id'])
    # Both cohorts receive exactly the same pre-read. This is timed separately;
    # native_seconds includes worker startup/internal I/O, not pure CPU time.
    started = clock()
    try:
        raw = pathlib.Path(row['crop_path']).read_bytes()
        record['crop_read_seconds'] = clock() - started
        record['crop_bytes'] = len(raw)
        record['crop_sha256'] = hashlib.sha256(raw).hexdigest()
        assert record['crop_sha256'] == row['crop_sha256'], 'crop hash mismatch'
        record['crop_pixels'] = list(struct.unpack('>II', raw[16:24])) if raw.startswith(b'\x89PNG\r\n\x1a\n') else None
    except Exception as exc:
        record.update(crop_read_seconds=record.get('crop_read_seconds', clock()-started), crop_read_error=repr(exc))
    started = clock()
    try:
        result = worker(row)
        record.update(status='PASS', native_result=result)
    except Exception as exc:
        record.update(status='ERROR', error_type=type(exc).__name__, detail=str(exc))
    record['native_seconds'] = clock() - started
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=pathlib.Path, required=True)
    p.add_argument('--out', type=pathlib.Path, required=True)
    a = p.parse_args(); v = json.loads(a.snapshot.read_text()); items = matched_items(v); config = v['binding']['config']
    root = pathlib.Path(config['component_roots']['greek-ocr-toolkit-pipe032'])
    assert not a.out.resolve().is_relative_to(root.resolve())
    a.out.mkdir(exist_ok=False, parents=True)
    sys.path.insert(0, str(root)); native = importlib.import_module('greekocr.harvest.line_pipeline_native')
    assert pathlib.Path(native.__file__).resolve().is_relative_to(root.resolve())
    from greekocr.harvest.line_pipeline_census import code_binding, file_sha
    assert code_binding() == v['binding']['code']
    assert file_sha(config['versions']) == v['binding']['versions_sha256']
    local = threading.local(); workers = []; lock = threading.Lock()
    def measure(item):
        if not hasattr(local, 'worker'):
            local.worker = native.NativeWorker(config['versions'], config['predictor'], config.get('row_timeout_seconds',120), config['runtime_manifest']); local.calls = 0
            with lock: workers.append(local.worker)
        record = measure_row(item, local.worker, local.calls+1); local.calls += 1
        with lock:
            with (a.out/'rows.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
        return record
    started = time.monotonic()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=16, thread_name_prefix='isolation') as pool:
            records = list(pool.map(measure, items))
    finally:
        cleanup = []
        for worker in workers:
            try: worker.close()
            except Exception as exc: cleanup.append(repr(exc))
    cohorts = {}
    for cohort in ['former_error', 'succeeded_control']:
        group = [r for r in records if r['cohort'] == cohort]
        cohorts[cohort] = dict(rows=len(group), parents=dict(collections.Counter(r['parent'] for r in group)), pass_rows=sum(r['status']=='PASS' for r in group), error_rows=sum(r['status']!='PASS' for r in group), crop_read_errors=sum('crop_read_error' in r for r in group), max_native_seconds=max(r['native_seconds'] for r in group), median_native_seconds=statistics.median(r['native_seconds'] for r in group), max_crop_read_seconds=max(r['crop_read_seconds'] for r in group), median_crop_read_seconds=statistics.median(r['crop_read_seconds'] for r in group))
    report = dict(status='PASS' if all(r['status']=='PASS' and 'crop_read_error' not in r for r in records) and not cleanup else 'HOLD', rows=len(records), workers=16, cohorts=cohorts, binding_sha256=v['progress']['run_binding_sha256'], timeout_seconds=config.get('row_timeout_seconds',120), same_native_worker=True, same_versions=True, attempt_access='none; captured read-only observations only', timing_note='plain crop read before native in both cohorts; native wall includes startup/internal I/O and is not pure CPU time; pre-read may warm cache', wall_seconds=time.monotonic()-started, cleanup_errors=cleanup, cold_requests=sum(r['cold'] for r in records), warm_requests=sum(not r['cold'] for r in records))
    (a.out/'report.json').write_text(json.dumps(report, indent=2)+'\n'); print(json.dumps(report, indent=2))
    if report['status'] != 'PASS': raise SystemExit(2)

if __name__ == '__main__': main()
