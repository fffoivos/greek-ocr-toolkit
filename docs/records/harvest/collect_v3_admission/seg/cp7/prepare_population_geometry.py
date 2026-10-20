"""Offline, source-bound CP2 fallback preparation. Population execution is opt-in.

No OCR, OSD, reading, live feature reads, or live-root writes. Dry runs use
synthetic payloads and a separate identity; they never count as real caches.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cp7_common import ROOT, SEG, COLLECTOR, LIVE, sha, read, rows, dump
from freeze import verify_freeze

DEFAULT_OUT = Path.home()/'Projects/collect-v3-data/geometry_prep'
_GUARDED_OUT = None
OPTIONS = dict(join_lines=True, granularity='rows', tables=False, statistics=False, orientation=False)


def guard(out):
    global _GUARDED_OUT
    out = Path(out).resolve()
    if _GUARDED_OUT is not None:
        assert _GUARDED_OUT == out, 'cannot change guarded output in one process'
        return
    assert not out.is_relative_to(LIVE.resolve()), 'live run root is read-only'
    def audit(event, args):
        if event.startswith('socket.') or event == 'subprocess.Popen':
            raise AssertionError('network/subprocess OFF')
        if event == 'open':
            path, mode, flags = args
            if isinstance(path, int): return
            p = Path(path).resolve()
            if p.is_relative_to(LIVE) and p.name == 'features.jsonl':
                raise AssertionError('live features forbidden')
            if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND) and not p.is_relative_to(out):
                raise AssertionError('write outside output: '+str(p))
        if event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate','os.rename','os.link','os.symlink'):
            for value in (args[:2] if event in ('os.rename','os.link','os.symlink') else args[:1]):
                p = Path(value).resolve()
                if event == 'os.mkdir' and p.is_dir(): continue
                if not p.is_relative_to(out): raise AssertionError('mutation outside output: '+str(p))
    sys.addaudithook(audit)
    _GUARDED_OUT = out


def io_module():
    path = COLLECTOR/'collect_v3/vendor/geometry/io.py'
    spec = importlib.util.spec_from_file_location('_cp7_existing_io', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest_from_snapshots():
    """Use the exact CP7a2 snapshot bindings and population; never discover newer inputs."""
    receipt = read(HERE/'build_receipt.json')
    paths = [Path(p) for p in receipt['inputs'] if Path(p).name.startswith(('W1_features_', 'W2_features_'))]
    assert len(paths) == 2
    ids = {r['id'] for r in rows(HERE/'keys/population_ids.jsonl')}
    assert sha(HERE/'keys/population_ids.jsonl') == receipt['population_ids_sha256']
    records = []
    for p in paths:
        assert sha(p) == receipt['inputs'][str(p)]
        records.extend(r for r in rows(p) if r['id'] in ids)
    assert len(records) == len(ids)
    return page_manifest(records)


def page_manifest(records):
    pages = {}
    for r in records:
        pid = r['id'].rsplit('-l', 1)[0]
        value = dict(page_id=pid, source=str(Path(r['crop_source_image']).resolve()),
                     source_sha256=r['crop_source_sha256'], frame=0)
        if pid in pages: assert pages[pid] == value, 'page identity conflict'
        pages[pid] = value
    # Once per source-bound page even when multiple page IDs alias it.
    unique = {}
    for p in sorted(pages.values(), key=lambda p:p['page_id']):
        key = (p['source'], p['source_sha256'], p['frame'])
        if key not in unique: unique[key] = dict(p, page_ids=[])
        unique[key]['page_ids'].append(p['page_id'])
    return list(unique.values())


def identity(page, dry_run=False):
    return dict(page=page, options=OPTIONS, freeze_sha256=sha(SEG/'CP7_FREEZE.json'),
                implementation=read(SEG/'CP7_FREEZE.json')['geometry_implementation'],
                dry_run=dry_run)


def valid(out, page, dry_run=False):
    directory = Path(out)/'cache'/page['page_id']
    try:
        receipt = read(directory/'preparation.json')
        if receipt['identity'] != identity(page, dry_run): return False
        if sha(page['source']) != page['source_sha256']: return False
        if not all(sha(directory/p) == h for p,h in receipt['payloads'].items()): return False
        if not dry_run:
            native = read(directory/'receipt.json')
            if (native['source_sha256'] != page['source_sha256'] or
                Path(native['source']).resolve() != Path(page['source']).resolve() or
                native['detector_sha256'] != receipt['identity']['implementation']['detector_sha256'] or
                native['options'] != OPTIONS): return False
            for name, field in [('detector.json.gz','geometry_sha256'),('ink.png','mask_sha256'),('labels.npz','labels_sha256')]:
                if sha(directory/name) != native[field]: return False
        return True
    except (OSError, ValueError, KeyError): return False


def enough_disk(out, minimum=10_000_000_000):
    p = Path(out)
    while not p.exists(): p = p.parent
    return shutil.disk_usage(p).free >= minimum


def prepare_one(out, page, dry_run=False):
    guard(out)
    start = time.perf_counter()
    directory = Path(out)/'cache'/page['page_id']
    if valid(out, page, dry_run): return dict(page_id=page['page_id'], status='skip_valid')
    directory.mkdir(parents=True, exist_ok=True)
    claim = directory/'attempt.json'
    if claim.exists(): return dict(page_id=page['page_id'], status='failed', reason='already_attempted_invalid_or_failed; no implicit redetection')
    with claim.open('x') as f: json.dump(identity(page, dry_run), f)
    try:
        assert sha(page['source']) == page['source_sha256'], 'source hash changed'
        if dry_run:
            (directory/'dry_payload.json').write_text(json.dumps(page, sort_keys=True))
            names = ['dry_payload.json']
        else:
            from PIL import Image
            with Image.open(page['source']) as image: assert getattr(image,'n_frames',1) == 1
            # Match CP3/CP4: detector imports resolve wholly to the collector,
            # whereas the coordinator verifies/observes with frozen recut code.
            for name in list(sys.modules):
                if name == 'greekocr' or name.startswith('greekocr.'):
                    del sys.modules[name]
            sys.path.insert(0, str(COLLECTOR))
            import greekocr.pages
            from greekocr.glyphs import orientation
            assert Path(greekocr.pages.__file__).resolve().is_relative_to(COLLECTOR.resolve())
            def forbidden(*args, **kwargs): raise AssertionError('OCR/OSD/reading OFF')
            orientation._osd = orientation.recognizer_polarity = forbidden
            module = io_module()
            assert module.detector_identity() == identity(page)['implementation']['detector_sha256']
            module.cache_page(Path(page['source']), directory, page['source_sha256'], module.detector_identity())
            names = ['detector.json.gz','ink.png','labels.npz','receipt.json']
        result = dict(page_id=page['page_id'], status='prepared', seconds=time.perf_counter()-start,
                      identity=identity(page,dry_run), payloads={n:sha(directory/n) for n in names},
                      bytes=sum((directory/n).stat().st_size for n in names), preparation_calls=0 if dry_run else 1)
        dump(directory/'preparation.json', result)
        return result
    except Exception as e:
        result = dict(page_id=page['page_id'],status='failed',seconds=time.perf_counter()-start,reason=f'{type(e).__name__}: {e}')
        dump(directory/'failure.json',result)
        return result


def run(pages, out, workers=4, dry_run=False, minimum=10_000_000_000):
    out = Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    guard(out)
    results = []; stopped = False; stop_requested = False
    def request_stop(signum, frame):
        nonlocal stop_requested
        stop_requested = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    def progress():
        dump(out/'progress.json.tmp',dict(total=len(pages),completed=len(results),
            prepared=sum(r['status']=='prepared' for r in results),
            skipped=sum(r['status']=='skip_valid' for r in results),
            failures=sum(r['status']=='failed' for r in results), stopped_disk=stopped, stop_requested=stop_requested,
            dry_run=dry_run, workers=workers, results=results))
        (out/'progress.json.tmp').replace(out/'progress.json')
    iterator = iter(pages)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {}
        def submit():
            nonlocal stopped
            if stop_requested: return False
            if not enough_disk(out,minimum): stopped=True; return False
            page = next(iterator,None)
            if page is None: return False
            pending[pool.submit(prepare_one,out,page,dry_run)] = page
            return True
        for _ in range(workers):
            if not submit(): break
        progress()
        while pending:
            done,_ = wait(pending,return_when=FIRST_COMPLETED,timeout=1)
            if not enough_disk(out,minimum): stopped=True
            for future in done:
                page=pending.pop(future)
                try: result=future.result()
                except Exception as e: result=dict(page_id=page['page_id'],status='failed',reason=f'{type(e).__name__}: {e}')
                results.append(result)
                progress()
                print(json.dumps({k:v for k,v in results[-1].items() if k not in ('identity','payloads')}),flush=True)
                if not stopped: submit()
        progress()
    return 2 if stopped or stop_requested else 1 if any(r['status']=='failed' for r in results) else 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT_OUT)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--manifest',type=Path,default=HERE/'population_geometry_pages.jsonl')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    verify_freeze()
    assert args.workers > 0
    plan=read(HERE/'population_geometry_plan.json')
    if args.manifest.resolve() == (HERE/'population_geometry_pages.jsonl').resolve():
        assert sha(args.manifest) == plan['manifest_sha256'], 'population manifest drift'
        assert plan['freeze_sha256'] == sha(SEG/'CP7_FREEZE.json')
        for p,digest in plan['snapshot_bindings'].items(): assert sha(p) == digest
    pages=rows(args.manifest)
    if args.limit: pages=pages[:args.limit]
    if not args.dry_run and args.output.resolve() != DEFAULT_OUT.resolve():
        assert args.output.resolve() == (SEG/'CP7_geometry').resolve(), 'unexpected output'
        gate=page_manifest(rows(HERE/'keys/draw.jsonl'))
        assert pages == gate, 'gate scope must match unchanged draw exactly'
    if not args.dry_run and args.output.resolve() == DEFAULT_OUT.resolve():
        assert args.manifest.resolve() == (HERE/'population_geometry_pages.jsonl').resolve() and args.limit is None
        assert len(pages) == plan['pages']
        assert not DEFAULT_OUT.resolve().is_relative_to(ROOT.resolve())
        assert not any((p/'.git').exists() for p in [DEFAULT_OUT.resolve(), *DEFAULT_OUT.resolve().parents]), 'output is inside a repository'
    if args.dry_run: assert args.output.resolve() != DEFAULT_OUT.resolve(), 'dry run needs isolated output'
    minimum = 0 if args.output.resolve() == (SEG/'CP7_geometry').resolve() else 10_000_000_000
    return run(pages,args.output,args.workers,args.dry_run,minimum)

if __name__=='__main__': sys.exit(main())
