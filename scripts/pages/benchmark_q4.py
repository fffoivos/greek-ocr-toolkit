"""Reproduce Q4 timings and exact fresh-API equality fingerprints.

Examples (run from the repository with the documented venv):
  python scripts/pages/benchmark_q4.py timing --reference 32e4920 --out .astra/q4-before
  python scripts/pages/benchmark_q4.py timing --workers 4 --out .astra/q4-after-w4
  python scripts/pages/benchmark_q4.py equality --reference 32e4920 --out .astra/q4-reference
  python scripts/pages/benchmark_q4.py equality --out .astra/q4-current
  python scripts/pages/benchmark_q4.py compare --left .astra/q4-reference --right .astra/q4-current --out .astra/q4-equality

Reference runs extract the commit into a TemporaryDirectory and execute its own
API in fresh interpreters. No historical detector output is read. Equality uses
all 16 Q3b option combinations; deterministic stages are memoized only within a
page, with full input keys and independent copies, as in Q3b. Timing never caches
stages. Fingerprints use canonical JSON without rounding or sorting arrays;
Parquet schema/rows and delivered crop dimensions/pixels are checked separately.
Use --details on both equality runs to retain full payloads for mismatch diagnosis.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import functools
import gzip
import hashlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import pickle
import platform
import subprocess
import sys
import tarfile
import tempfile
import time
import warnings
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
os.environ.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
STAGES = ('segmenter', 'line finding', 'ink assignment', 'guide fit', 'table delivery',
          'joining', 'statistics', 'checks', 'writing', 'other')
FILES = {'lines', 'segments', 'structure', 'cells', 'checks', 'delivery', 'statistics'}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def fingerprint(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def allowlist():
    tree = ast.parse((ROOT/'scripts/pages/check_q3b_equality.py').read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'ALLOWLIST' for t in n.targets))


def normalized(value, family, allowed, path='$'):
    paths = allowed.get(family, {})
    if not any(p.startswith(path+'.') or p.startswith(path+'[]') for p in paths):
        return value
    if isinstance(value, dict):
        return {k: normalized(v, family, allowed, path+'.'+k) for k, v in value.items()
                if path+'.'+k not in allowed.get(family, {})}
    if isinstance(value, list):
        return [normalized(v, family, allowed, path+'[]') for v in value]
    return value


def cached(fn, receipt):
    cache = {}
    @functools.wraps(fn)
    def call(*args, **kwargs):
        key = sha(pickle.dumps((args, kwargs), protocol=5))
        if key not in cache:
            cache[key] = pickle.dumps(fn(*args, **kwargs), protocol=5)
            receipt['misses'] += 1
        else:
            receipt['hits'] += 1
        return pickle.loads(cache[key])
    return call


class StageTimer:
    """Exclusive nested wall times: every measured interval is counted once."""
    def __init__(self):
        self.times = defaultdict(float)
        self.stack = []

    def wrap(self, stage, fn):
        @functools.wraps(fn)
        def call(*args, **kwargs):
            frame = [time.perf_counter(), 0.]
            self.stack.append(frame)
            try:
                return fn(*args, **kwargs)
            finally:
                duration = time.perf_counter() - frame[0]
                self.stack.pop()
                self.times[stage] += duration-frame[1]
                if self.stack:
                    self.stack[-1][1] += duration
        return call

    def install(self, stack):
        from greekocr.pages import api, lines, pixels, outputs, structure
        def bind(module, name, stage):
            stack.enter_context(patch.object(module, name, self.wrap(stage, getattr(module, name))))
        bind(lines, 'segment_page', 'line finding')
        bind(lines, 'prepare_pixels', 'segmenter')
        bind(pixels, 'prepare_pixels', 'segmenter')
        bind(lines, '_assign', 'ink assignment')
        for name in ('_pool_geometry', '_refine_bottom_contacts', 'fit_guides'):
            bind(lines, name, 'guide fit')
        bind(lines, '_diagnostics', 'checks')
        bind(structure, '_attach_structure', 'checks')
        bind(api, 'prepare_delivery', 'table delivery')
        bind(api, 'joining_result', 'joining')
        bind(api, 'page_statistics', 'statistics')
        bind(outputs, 'write_page', 'writing')


def run_page(task):
    config, path, cohort, book = task
    sys.path.insert(0, config['source_root'])
    import cv2
    import numpy as np
    from PIL import Image
    from greekocr.pages import api, process_page, PageOptions, OutputOptions
    from greekocr.pages.layout import read_layout
    from greekocr.pages.lines import extract_line_image
    import pyarrow.parquet as pq
    import greekocr
    assert Path(greekocr.__file__).resolve().is_relative_to(Path(config['source_root']).resolve()), 'Wrong implementation imported'
    cv2.setNumThreads(1)
    warnings.filterwarnings('ignore', category=np.exceptions.RankWarning)
    path = Path(path)
    with Image.open(path) as opened:
        source = opened.copy()
    layout = ROOT/'.astra/layout'/f'{path.stem}.json'
    regions = read_layout(layout, source.size) if layout.exists() else []
    frame = tuple(v/3 for v in source.size)
    report = dict(page_key=path.stem, cohort=cohort, book_id=book,
                  source_sha256=sha(path.read_bytes()), layout_sha256=sha(layout.read_bytes()) if layout.exists() else None)
    target = Path(config['out'])
    with tempfile.TemporaryDirectory(prefix='q4-page-') as temp:
        if config['mode'] == 'timing':
            timer = StageTimer()
            with ExitStack() as stack:
                timer.install(stack)
                start = time.perf_counter()
                result = process_page(source, page_key=path.stem, book_id=book, page_size=frame,
                    table_regions=regions, options=PageOptions(tables=True, join_lines=True, statistics=True,
                        outputs=OutputOptions(temp, FILES)))
                total = time.perf_counter()-start
            report.update(seconds=total, stages={s: timer.times[s] for s in STAGES},
                          lines=len(result.lines), pieces=len(result.pieces), glyphs=len(result.glyphs))
            report['stages']['other'] = total-sum(timer.times.values())
        else:
            gray = np.asarray(source.convert('L'), dtype=np.float64)
            # Every crop uses this same immutable raster. Validate it once via
            # the revision's own converter; keep the public extraction entry
            # point and the revision's unroller for every distinct crop.
            convert = api.detector._gray
            validated_gray = convert(gray)
            report['modes'] = {}
            report['counts'] = {}
            crop_cache = {}
            report['cache'] = {s: dict(hits=0, misses=0) for s in ('detection', 'delivery', 'statistics')}
            with ExitStack() as stack:
                stack.enter_context(patch.object(api.detector, '_gray',
                    lambda page: validated_gray if page is gray else convert(page)))
                for module, name, stage in ((api.detector, 'segment_page', 'detection'),
                                            (api, 'prepare_delivery', 'delivery'), (api, 'page_statistics', 'statistics')):
                    stack.enter_context(patch.object(module, name, cached(getattr(module, name), report['cache'][stage])))
                for tables in (False, True):
                    for statistics in (False, True):
                        for join in (None, 'default', 'rows', 'pieces'):
                            name = f'tables-{tables}.stats-{statistics}.join-{join}'
                            # Serialize all families with the API writer; only the
                            # rows option has a rows envelope, exactly as in Q3b.
                            files = FILES - ({'statistics'} if not statistics else set())
                            if join == 'rows':
                                files = files | {'rows'}
                            result = process_page(source, page_key=path.stem, book_id=book, page_size=frame,
                                table_regions=regions if tables else None,
                                options=PageOptions(tables=tables, statistics=statistics, join_lines=join is not None,
                                    granularity=join or 'default', outputs=OutputOptions(temp, files)))
                            report['counts'][name] = dict(lines=len(result.lines), pieces=len(result.pieces), glyphs=len(result.glyphs))
                            payload = dict(records=result.to_records(), joining=result.joining,
                                           statistics=result.statistics, pieces=[p.line.to_record() for p in result.pieces])
                            # Include internal ownership and pixel maps: discrete
                            # changes must not hide behind rounded records.
                            pixel = result.segmentation.pixels
                            payload['ownership'] = [[int(i) for i in l.component_ids] for l in result.segmentation.lines]
                            payload['pixels'] = {k: dict(shape=list(getattr(pixel,k).shape), dtype=str(getattr(pixel,k).dtype),
                                                       sha256=sha(getattr(pixel,k).tobytes())) for k in ('ink','labels','components','barriers')}
                            payload['crops'] = []
                            for piece in result.pieces:
                                line = piece.line
                                identity = sha(pickle.dumps((line.x0, line.x1, line.xheight,
                                    line.baseline, line.meanline, line.top, line.bottom), protocol=5))
                                if identity not in crop_cache:
                                    arr = np.asarray(extract_line_image(gray, line))
                                    crop_cache[identity] = dict(shape=list(arr.shape), dtype=str(arr.dtype), sha256=sha(arr.tobytes()))
                                payload['crops'].append(crop_cache[identity])
                            payload['written'] = {}
                            for family, filename in result.files.items():
                                filename = Path(filename)
                                if filename.suffix == '.json':
                                    payload['written'][family] = json.loads(filename.read_text())
                                elif filename.suffix == '.parquet':
                                    table = pq.read_table(filename)
                                    payload['parquet_schema'] = dict(display=str(table.schema), sha256=sha(table.schema.serialize().to_pybytes()))
                                    payload['parquet_rows'] = table.to_pylist()
                            for family in list(payload['records']):
                                payload['records'][family] = normalized(payload['records'][family], family, config['allowlist'])
                            for family in list(payload['written']):
                                payload['written'][family] = normalized(payload['written'][family], family, config['allowlist'])
                            if statistics:
                                payload['statistics']['stats'] = normalized(payload['statistics']['stats'], 'stats', config['allowlist'])
                            report['modes'][name] = {k: fingerprint(v) for k,v in payload.items()}
                            if config['details']:
                                with gzip.open(target/f'{path.stem}.{name}.json.gz','wt') as stream:
                                    json.dump(payload, stream, separators=(',', ':'), allow_nan=False)
                            del payload, result
            report['crop_evaluations'] = len(crop_cache)
    (target/f'{path.stem}.json').write_text(json.dumps(report, indent=2))
    print(path.stem, round(report.get('seconds', 0), 3) if config['mode']=='timing' else '16 modes', flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('timing','equality','compare'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--reference')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--details', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Equality only; requires unchanged source and input hashes')
    parser.add_argument('--left', type=Path)
    parser.add_argument('--right', type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve(); args.out.mkdir(parents=True, exist_ok=True)
    if args.reference:
        commit = subprocess.check_output(['git','rev-parse',args.reference], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory(prefix='q4-reference-') as temp:
            raw = subprocess.check_output(['git','archive',commit,'greekocr'],cwd=ROOT)
            with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
                archive.extractall(temp)
            command = [sys.executable, str(Path(__file__).resolve()), args.mode, '--source-root', temp,
                       '--out',str(args.out),'--workers',str(args.workers)]
            if args.keys: command += ['--keys', *args.keys]
            if args.details: command += ['--details']
            if args.resume: command += ['--resume']
            code = subprocess.call(command, cwd=temp)
        (args.out/'reference.json').write_text(json.dumps(dict(commit=commit, fresh_archive=True),indent=2))
        return code
    if args.mode == 'compare':
        left=json.loads((args.left/'summary.json').read_text()); right=json.loads((args.right/'summary.json').read_text())
        failures=[]; checks=0
        for a,b in zip(left['pages'],right['pages']):
            for field in ('page_key','source_sha256','layout_sha256'):
                if a[field] != b[field]: failures.append(dict(page=a['page_key'],field=field))
            if a['modes'].keys() != b['modes'].keys(): failures.append(dict(page=a['page_key'],field='modes'))
            # Coverage is part of equality: every page must carry all 16 option combinations, each with payload families
            # (an empty receipt on both sides must not compare as equal; Q4 review cycles 1-2, LOW).
            for side, report in (('left', a), ('right', b)):
                if len(report['modes']) != 16: failures.append(dict(page=report['page_key'],side=side,field='mode_count',count=len(report['modes'])))
                for mode, values in report['modes'].items():
                    if not values: failures.append(dict(page=report['page_key'],side=side,mode=mode,field='empty_mode'))
            for mode, values in a['modes'].items():
                if values.keys() != b['modes'].get(mode,{}).keys(): failures.append(dict(page=a['page_key'],mode=mode,field='families'))
                for family,value in values.items():
                    checks+=1
                    if value != b['modes'].get(mode,{}).get(family):
                        failures.append(dict(page=a['page_key'], mode=mode, family=family))
        if len(left['pages']) != len(right['pages']): failures.append(dict(field='page_count'))
        summary=dict(equal=not failures,pages=len(left['pages']),api_calls_per_revision=len(left['pages'])*16,
                     comparisons=checks, failures=failures, left=str(args.left),right=str(args.right),allowlist=allowlist())
        (args.out/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
        return int(bool(failures))
    selection=json.loads((ROOT/'.astra/book_pages/selection.json').read_text())
    identities={r['page']:r['book'] for r in selection['pages']}
    config=dict(source_root=str(args.source_root.resolve()),out=str(args.out),mode=args.mode,
                details=args.details,allowlist=allowlist())
    tasks=[]
    for cohort,directory in (('development','pages'),('book','book_pages')):
        for p in sorted((ROOT/'.astra'/directory).glob('*.png')):
            if args.keys and p.stem not in args.keys: continue
            book=identities.get(p.stem,p.stem.split('-',1)[-1].rsplit('-p',1)[0])
            tasks.append((config,str(p),cohort,book))
    manifest={str(p.relative_to(args.source_root)):sha(p.read_bytes()) for p in sorted((args.source_root/'greekocr').rglob('*.py'))}
    manifest_path=args.out/'source-manifest.json'
    previous=[]
    if args.resume:
        if args.mode != 'equality': raise ValueError('Timing must run uninterrupted, without resume')
        if json.loads(manifest_path.read_text()) != manifest: raise ValueError('Source changed: use a new output directory')
        pending=[]
        for task in tasks:
            path=Path(task[1]); receipt=args.out/f'{path.stem}.json'
            if receipt.exists():
                row=json.loads(receipt.read_text())
                if row['source_sha256'] != sha(path.read_bytes()): raise ValueError('Input changed')
                layout=ROOT/'.astra/layout'/f'{path.stem}.json'
                if row['layout_sha256'] != (sha(layout.read_bytes()) if layout.exists() else None): raise ValueError('Layout changed')
                previous.append(row)
            else: pending.append(task)
        tasks=pending
    else:
        manifest_path.write_text(json.dumps(manifest,indent=2))
    start=time.perf_counter()
    if args.workers == 1:
        pages=[run_page(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            pages=list(pool.map(run_page,tasks))
    elapsed=time.perf_counter()-start
    pages=sorted(pages+previous,key=lambda r:(r['cohort'] != 'development',r['page_key']))
    summary=dict(mode=args.mode,workers=args.workers,pages=pages,wall_seconds=elapsed,
                 pages_per_minute=len(pages)*60/elapsed,source_manifest=manifest,script_sha256=sha(Path(__file__).read_bytes()),
                 python=sys.version,platform=platform.platform(),cpu_count=os.cpu_count(),threads_per_worker=1,
                 frame='PNG/3',timing_scope='API including selected JSON and Parquet writes; decoded inputs and layout supplied')
    if args.mode=='timing':
        import numpy as np
        def distribution(values):
            return dict(median=float(np.median(values)),p95=float(np.percentile(values,95)),worst=float(max(values)),sum=float(sum(values)))
        summary['seconds']=distribution([p['seconds'] for p in pages])
        summary['stages']={s:distribution([p['stages'][s] for p in pages]) for s in STAGES}
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2))
    print('COMPLETE',len(pages),'pages',round(elapsed,3),'seconds',round(summary['pages_per_minute'],3),'pages/min',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
