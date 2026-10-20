"""Independently re-hash every selected original and every produced crop."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import run


def verify(out):
    binding = json.loads((out / 'binding.json').read_text())
    source = Path(binding['source'])
    pages, inputs = run.make_selection(source, binding['mode'] == 'mock')
    digest = hashlib.sha256(json.dumps(pages, sort_keys=True).encode()).hexdigest()
    if inputs != binding['inputs'] or digest != binding['selection_sha256']:
        raise ValueError('live import/admitted/page population differs from run bindings')
    if json.loads((out / 'selection.json').read_text()) != pages:
        raise ValueError('stored selection drift')
    for name, expected in binding['code'].items():
        if run.sha(run.contained(out / 'code', name)) != expected:
            raise ValueError('frozen code snapshot changed: ' + name)
    if binding['adapter_sha256'] != run.sha(run.PHASE / 'phase0_mask.py'):
        raise ValueError('phase0 adapter changed')
    if binding['runner_sha256'] != run.sha(run.__file__):
        raise ValueError('runner changed')
    def record_digest(record):
        return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).digest()
    aggregate = {}
    for r in run.rows(out / 'records.jsonl'):
        if r['id'] in aggregate:
            raise ValueError('duplicate aggregate id: ' + r['id'])
        aggregate[r['id']] = record_digest(r)
    counts, seen, missing_outputs, failed, expected_outputs = {}, set(), [], 0, set()
    expected_page_files = set()
    for page in pages:
        record_file = out / 'pages' / (run.page_name(page) + '.records.jsonl')
        expected_page_files.add(record_file)
        records = list(run.rows(record_file))
        # Rehash both original and output, including byte-exact skip/fallbacks.
        run.validate_records(page, records, out, source, rehash=True)
        for record in records:
            if record['id'] in seen or aggregate.get(record['id']) != record_digest(record):
                raise ValueError('page/aggregate record disagreement: ' + record['id'])
            seen.add(record['id'])
            failed += record['guard_status'] == 'failed_page'
            if record['output_sha256'] is None:
                missing_outputs.append(record['id'])
            else:
                expected_outputs.add(record['output_path'])
        run.add_counts(counts, records)
    if set(aggregate) != seen:
        raise ValueError('aggregate population mismatch')
    if set((out / 'pages').glob('*.records.jsonl')) != expected_page_files:
        raise ValueError('unexpected page records')
    actual_outputs = {str(p.relative_to(out)) for p in (out / 'crops').rglob('*') if p.is_file()}
    if actual_outputs != expected_outputs:
        raise ValueError('output file population differs from records')
    summary = json.loads((out / 'summary.json').read_text())
    if (summary['pages_complete'] != len(pages) or summary['per_wave_split'] != counts
            or summary['state'] not in ('completed', 'completed_with_failures')):
        raise ValueError('summary is incomplete or disagrees with re-counted records')
    return dict(ok=not failed and not missing_outputs, pages=len(pages), records=len(seen),
                outputs_hashed=len(seen) - len(missing_outputs), originals_hashed=len(seen),
                failed_crops=failed, missing_outputs=missing_outputs, per_wave_split=counts,
                host=run.socket.gethostname(), tree_sha=run.TREE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=run.HERE / 'out')
    args = parser.parse_args()
    run.offline()
    try:
        result = verify(args.out.resolve())
    except Exception as error:
        print(json.dumps(dict(ok=False, error=str(error))), flush=True)
        sys.exit(1)
    print(json.dumps(result), flush=True)
    sys.exit(0 if result['ok'] else 1)
