"""Fresh-directory real-slice rehearsal, with explicit failed-stage coverage."""
from copy import deepcopy
import json
import math
from pathlib import Path
import resource
import sys
import time

import pyarrow as pa
import pyarrow.parquet as pq

from .common import atomic_json, canonical, info, records
from .progress import Progress


def disk_bytes(root):
    return sum(p.stat().st_size for p in Path(root).rglob('*') if p.is_file())


def slice_file(entry, source, dest, fraction):
    path = Path(entry['path'])
    start = time.monotonic()
    if path.suffix == '.parquet':
        pf = pq.ParquetFile(path)
        wanted = max(1, math.ceil(pf.metadata.num_rows * fraction))
        batches, count = [], 0
        for batch in pf.iter_batches(batch_size=128, use_threads=False):
            batch = batch.slice(0, min(batch.num_rows, wanted - count))
            batches.append(batch)
            count += batch.num_rows
            if count >= wanted:
                break
        dest = dest.with_suffix('.parquet')
        table = pa.Table.from_batches(batches, schema=pf.schema_arrow)
        pq.write_table(table, dest, compression='zstd', use_content_defined_chunking=True)
        unit_fraction = count / max(1, pf.metadata.num_rows)
    elif path.name.endswith(('.jsonl', '.ndjson')):
        wanted = max(1, math.ceil(entry['bytes'] * fraction))
        read, count = 0, 0
        dest = dest.with_suffix('.jsonl')
        with path.open('rb') as incoming, dest.open('wb') as output:
            for line in incoming:
                output.write(line)
                read += len(line)
                count += bool(line.strip())
                if read >= wanted:
                    break
        unit_fraction = read / max(1, entry['bytes'])
    else:
        # Structured evidence must stay whole: large JSON uses its explicit streaming selector.
        if entry['bytes'] < 32_000_000:
            return entry, {'input': entry, 'fraction': 1.0, 'reason': 'small structured evidence kept whole', 'elapsed_seconds': 0}
        dest = dest.with_suffix('.jsonl')
        count = 0
        budget = max(1, math.ceil(entry['bytes'] * fraction))
        with dest.open('w') as output:
            for row in records(path, source):
                output.write(canonical(row) + '\n')
                count += 1
                if output.tell() >= budget:
                    break
        unit_fraction = fraction
    result = info(dest)
    return result, {'input': entry, 'sample': result, 'rows': count, 'fraction': unit_fraction,
                    'elapsed_seconds': time.monotonic() - start}


def measure(lock, out, fraction=.02):
    """No reuse of production work. No extrapolation is reported as a measured full build."""
    from .build_dataset import Builder
    from .accept_dataset import Acceptance
    out = Path(out).resolve()
    if out.exists() or not 0 < fraction <= 1:
        raise ValueError('measure requires a fresh directory and a fraction in (0,1]')
    out.mkdir(parents=True)
    slices = out / 'slices'; slices.mkdir()
    sample = deepcopy(lock)
    sample['_measure'] = True
    sample['frozen_trained'] = {}
    measurements = []
    started = time.monotonic()
    with Progress('measure:slicing'):
        bridge = sample.get('book_bridge', {})
        whole_inputs = {bridge.get('registry_input'), bridge.get('instruments_input'), bridge.get('sources_input')}
        i = 0
        for source in sample['inputs']:
            for selection in (source, source.get('original_crops_source')):
                if not selection:
                    continue
                values = []
                for entry in selection['files']:
                    # Every large selected file, including prepared and original crop shards.
                    if selection is not source:
                        # Independent payload prefixes do not close the selected
                        # native tuples. Keep the pinned dependency and let the
                        # ordinary smoke loader select exact tuples and hashes.
                        value, measurement = entry, dict(input=entry, fraction=1.0, elapsed_seconds=0,
                            reason='SHA-locked original payload dependency kept whole; exact selected tuple closure')
                    elif (source['name'] in whole_inputs or source.get('table') == 'book_sources'
                          or source.get('book_bridge_metadata') or source.get('validation_original_metadata')):
                        value, measurement = entry, dict(input=entry, fraction=1.0, elapsed_seconds=0,
                            reason='SHA-locked book bridge evidence kept whole')
                    else:
                        value, measurement = slice_file(entry, selection, slices / str(i), fraction)
                    measurements.append(measurement)
                    values.append(value)
                    i += 1
                selection['files'] = values
    # Raw recovery itself is outside P2a; adapters are nevertheless real-sliced if supplied.
    for source in sample.get('label_variant_adapters', []):
        values = []
        for entry in source['files']:
            value, measurement = slice_file(entry, source, slices / str(i), fraction)
            values.append(value); measurements.append(measurement); i += 1
        source['files'] = values
    if sample.get('label_variant_adapters'):
        # The independent prefixes need not preserve raw-parent locator closure.
        # Never silently qualify that missing cost as an all-stage production projection.
        sample['label_variant_adapters'] = []
    result = {'fraction': fraction, 'inputs': measurements, 'stages': [], 'complete': False,
              'parallelism': {'sqlite_writers': 1, 'arrow_threads': 1, 'omp_threads': 1, 'readback_file_workers': 8,
                              'allocated_cpus_recommended': 8},
              'qualification': 'sample projection; run on Clariden, not a production timing promise'}
    builder = None
    try:
        with Progress('index') as progress:
            builder = Builder(sample, out / 'dataset', out / 'work', smoke=2**30)
        result['stages'].append({**progress.result, 'scale': 1.0})
        from .common import sha
        hash_projection = 0.0
        with Progress('input-hash') as progress:
            for measurement in measurements:
                hash_started = time.monotonic()
                sha(measurement.get('sample', measurement['input'])['path'])
                hash_projection += (time.monotonic() - hash_started) / measurement['fraction']
            import hashlib
            for entry in lock.get('assets', []):
                hash_started = time.monotonic()
                wanted = max(1, math.ceil(entry['bytes'] * fraction))
                h = hashlib.sha256()
                read = 0
                with Path(entry['path']).open('rb') as stream:
                    while read < wanted:
                        chunk = stream.read(min(4 << 20, wanted - read))
                        if not chunk: break
                        h.update(chunk); read += len(chunk); progress.bytes += len(chunk)
                measurements.append({'input': entry, 'fraction': read / max(1, entry['bytes']), 'unit': 'asset hash bytes', 'sample_sha256': h.hexdigest()})
                hash_projection += (time.monotonic() - hash_started) / max(read / max(1, entry['bytes']), 1e-9)
        result['stages'].append({**progress.result, 'projected_full_seconds': hash_projection,
            'projection_basis': 'sum of per-input hash seconds / actual input fraction; whole dependencies x1'})
        with Progress('original-payload-input') as progress:
            for source in sample['inputs']:
                override = source.get('original_crops_source')
                if override:
                    with builder.store.db:
                        builder.original_inputs.load(sample, source, builder.smoke, builder.store_original_payload)
                    # Keep the binding for ingest AND independent source replay.
                    # Loaded bytes alone are not a native row custody binding.
        result['stages'].append({**progress.result, **({'projected_full_seconds': None,
            'projection_basis': 'whole dependency scan plus selected tuple byte verification; full verification unmeasured'}
            if any(s.get('original_crops_source') for s in sample['inputs']) else {})})
        # Timers also wrap every phase inside run; all errors are retained, never hidden.
        try:
            builder.run()
        finally:
            result['stages'].extend(builder.timings)
        try:
            with Progress('independent-readback') as progress:
                scratch = out / 'accept'; scratch.mkdir()
                verifier = Acceptance(builder.out, scratch, validation_mode='external-cache',
                                      input_lock=builder.out / 'manifests/INPUT_LOCK.json', allow_smoke=True)
                try:
                    atomic_json(out / 'READBACK.json', verifier.run())
                finally:
                    verifier.db.close()
        finally:
            result['stages'].append({'stage': 'independent-readback', **progress.result})
        result['readback_report'] = info(out / 'READBACK.json')
        result['complete'] = True
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        if builder is not None:
            builder.store.db.close()
    scale = 1 / fraction
    for stage in result['stages']:
        stage.setdefault('projected_full_seconds', stage['elapsed_seconds'] * stage.get('scale', scale))
    result['sample_elapsed_seconds'] = time.monotonic() - started
    result['sample_scratch_bytes'] = disk_bytes(out)
    result['projected_scratch_bytes_build_plus_readback'] = result['sample_scratch_bytes'] * scale + 2 * sum(f['bytes'] for s in lock['inputs'] for f in s['files'])
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result['peak_rss_bytes'] = rss if sys.platform == 'darwin' else rss * 1024
    required = {'ingest', 'derive', 'export', 'summaries', 'manifest-hash', 'independent-readback', 'index', 'evidence-reconciliation', 'input-hash'}
    covered = {s['stage'] for s in result['stages']}
    result['unmeasured_stages'] = sorted(required - covered)
    if any(s.get('original_crops_source') for s in sample['inputs']):
        result['unmeasured_stages'].append('full original payload verification (whole dependency scan with selected tuple bytes)')
    if lock.get('label_variant_adapters'):
        result['unmeasured_stages'].append('P1 adapter closure and feature work (raw integration outside P2a)')
    result['projected_full_hours'] = (sum(s['projected_full_seconds'] for s in result['stages'] if not s.get('diagnostic_only')) / 3600
                                      if result['complete'] and not result['unmeasured_stages'] else None)
    result['within_12_hours'] = (result['projected_full_hours'] <= 12
                                 if result['projected_full_hours'] is not None else None)
    result['derive_rate_qualification'] = 'derive rows count store writes, not completed input lines; use subphase timings'
    atomic_json(out / 'MEASURE.json', result)
    print(canonical(result), flush=True)
    return result
