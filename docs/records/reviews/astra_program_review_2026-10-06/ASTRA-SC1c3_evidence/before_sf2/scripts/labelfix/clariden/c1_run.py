"""Bounded CTC alignment only. Four independent inference workers; no training/evaluation."""
import argparse
from collections import Counter
import gzip
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import time
import traceback

from c1_common import (COMPOUND_CLASSES, agreeing_counts, crop_key, crop_path,
                       read_jsonl, sha256, write_json)


def worker(rank, args):
    import torch
    from greekocr.labelfix.ctc_align import Recognizer
    started = time.time()
    rows = read_jsonl(args.selection)[rank::args.workers]
    device = f'cuda:{rank}' if args.device == 'cuda' else 'cpu'
    if args.device == 'cuda':
        torch.cuda.set_device(rank)
    rec = Recognizer(args.checkpoint, device=device, threads=args.threads)
    counts, errors, classes = Counter(), [], Counter({c: 0 for c in COMPOUND_CLASSES})
    out = args.out / f'worker_{rank}.jsonl.gz'
    with gzip.open(out, 'xt', encoding='utf-8', compresslevel=3) as f:
        for start in range(0, len(rows), args.chunk_size):
            batch = rows[start:start + args.chunk_size]
            paths = [str(crop_path(r['crop'], args.crop_root, args.crop_layout)) for r in batch]
            try:
                aligned = rec.align_paths(paths, bs=args.batch_size)
            except Exception:
                # A malformed strip must not discard its entire chunk. Preserve the cause.
                print(f'[C1 worker {rank}] chunk exception; isolating crops\n{traceback.format_exc()}', flush=True)
                aligned = {}
                for p in paths:
                    try:
                        aligned.update(rec.align_paths([p], bs=1))
                    except Exception as e:
                        errors.append(dict(crop=batch[paths.index(p)]['crop'], error=repr(e)))
            for r, p in zip(batch, paths):
                counts['attempted'] += 1
                if p not in aligned:
                    counts['failed'] += 1
                    if not any(e['crop'] == r['crop'] for e in errors):
                        errors.append(dict(crop=r['crop'], error='align_paths skipped unreadable/missing crop'))
                    continue
                al = aligned[p]
                record = dict(crop=r['crop'], alignment=al.to_record(), prediction=al.prediction)
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                counts['aligned'] += 1
                words, cc = agreeing_counts(r['label'], al.prediction)
                counts['agreeing_words'] += words
                classes.update(cc)
            f.flush()
            print(f'[C1 worker {rank}] {counts["attempted"]}/{len(rows)}; aligned={counts["aligned"]}; '
                  f'failed={counts["failed"]}; seconds={time.time()-started:.1f}', flush=True)
    write_json(args.out / f'worker_{rank}.summary.json', dict(
        rank=rank, device=device, counts=counts, failures=errors,
        agreeing_compound_clusters_by_class=classes, elapsed_seconds=time.time()-started,
        torch=torch.__version__, cuda=torch.version.cuda,
        gpu=torch.cuda.get_device_name(rank) if args.device == 'cuda' else None,
        alignment_sha256=sha256(out)))


def compare_cache(output, reference, destination):
    ref = {crop_key(r['crop']): r['alignment'] for r in read_jsonl(reference)}
    result = dict(reference=str(reference), reference_sha256=sha256(reference), overlapping=0,
                  exact=0, mismatches=[])
    with gzip.open(output, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r['crop'] not in ref:
                continue
            result['overlapping'] += 1
            old, new = ref[r['crop']], r['alignment']
            if old == new:
                result['exact'] += 1
            else:
                differences = {k: dict(reference=old.get(k), actual=new.get(k))
                               for k in old.keys() | new.keys() if old.get(k) != new.get(k)}
                result['mismatches'].append(dict(crop=r['crop'], differences=differences))
    write_json(destination, result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection', type=Path, required=True)
    ap.add_argument('--checkpoint', type=Path, required=True)
    ap.add_argument('--crop-root', type=Path, required=True)
    ap.add_argument('--crop-layout', choices=('toolkit', 'e3'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--device', choices=('cpu', 'cuda'), required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--chunk-size', type=int, default=512)
    ap.add_argument('--mock', action='store_true')
    ap.add_argument('--compare-cache', type=Path)
    a = ap.parse_args()
    started = time.time()
    rows = read_jsonl(a.selection)
    if a.mock:
        if len(rows) > 200 or a.device != 'cpu' or a.workers != 1:
            raise ValueError('Mac mock requires <=200 rows, CPU, one worker')
    elif not os.environ.get('SLURM_JOB_ID') or a.device != 'cuda':
        raise ValueError('Full inference requires a Slurm GPU allocation')
    if len({r['crop'] for r in rows}) != len(rows):
        raise ValueError('duplicate selected crops')
    a.out.mkdir(parents=True, exist_ok=False)
    binding = dict(selection=str(a.selection), selection_sha256=sha256(a.selection),
                   checkpoint=str(a.checkpoint), checkpoint_sha256=sha256(a.checkpoint),
                   checkpoint_safetensors_sha256=sha256(a.checkpoint.with_suffix('.safetensors')),
                   lines=len(rows), job_id=os.environ.get('SLURM_JOB_ID'),
                   hostname=platform.node(), mock=a.mock,
                   arguments={k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()})
    write_json(a.out / 'binding.json', binding)
    if a.workers == 1:
        worker(0, a)
    else:
        context = mp.get_context('spawn')
        workers = [context.Process(target=worker, args=(rank, a)) for rank in range(a.workers)]
        for p in workers:
            p.start()
        for p in workers:
            p.join()
        if any(p.exitcode != 0 for p in workers):
            raise RuntimeError(f'inference workers failed: {[p.exitcode for p in workers]}')
    counts, classes, failures = Counter(), Counter({c: 0 for c in COMPOUND_CLASSES}), []
    output = a.out / 'C1_alignments.jsonl.gz'
    with gzip.open(output, 'xt', encoding='utf-8', compresslevel=3) as dest:
        for rank in range(a.workers):
            s = json.loads((a.out / f'worker_{rank}.summary.json').read_text())
            counts.update(s['counts'])
            classes.update(s['agreeing_compound_clusters_by_class'])
            failures.extend(s['failures'])
            with gzip.open(a.out / f'worker_{rank}.jsonl.gz', 'rt', encoding='utf-8') as src:
                for line in src:
                    dest.write(line)
    if counts['attempted'] != len(rows) or counts['aligned'] + counts['failed'] != len(rows):
        raise ValueError(f'incomplete accounting: {counts}')
    summary = dict(binding=binding, counts=counts, failures=failures,
                   agreeing_compound_clusters_by_class=classes,
                   agreement_definition='existing candidates.pair_tokens; exact NFD word-core equality; no ink filtering',
                   elapsed_seconds=time.time()-started, output=str(output),
                   output_bytes=output.stat().st_size, output_sha256=sha256(output))
    if a.compare_cache:
        diff = compare_cache(output, a.compare_cache, a.out / 'mock_cache_diff.json')
        summary['cache_diff'] = dict(overlapping=diff['overlapping'], exact=diff['exact'],
                                     mismatches=len(diff['mismatches']))
    write_json(a.out / 'summary.json', summary)
    print('C1_ALIGNMENT_DONE ' + json.dumps(summary, ensure_ascii=False), flush=True)
    return 1 if counts['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
