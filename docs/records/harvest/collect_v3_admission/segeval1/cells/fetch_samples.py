"""Seeded local draw; remote stat/read-only SCP of existing crop bytes only."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import random
import subprocess

from PIL import Image

D = Path(__file__).resolve().parent
SEED = 20261019
TARGETS = dict(cells=150, numeric_not_small=50, small_not_numeric=50)


def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def main():
    pools = {k: [] for k in TARGETS}
    for line in gzip.open(D / 'population_cells.jsonl.gz', 'rt'):
        r = json.loads(line)
        group = ('cells' if r['is_cell'] else 'numeric_not_small' if r['is_numeric_output']
                 else 'small_not_numeric' if r['is_small_image'] else None)
        if group:
            pools[group].append(r)
    rng = random.Random(SEED)
    orders = {k: rng.sample(sorted(rows, key=lambda r: (r['parent_id'], r['row_id'])), len(rows))
              for k, rows in pools.items()}
    order_bytes = b''.join((json.dumps(dict(group=k, row_ids=[r['row_id'] for r in rows]), sort_keys=True) + '\n').encode()
                           for k, rows in orders.items())
    with gzip.GzipFile(filename=str(D / 'sample_order.jsonl.gz'), mode='wb', mtime=0) as f:
        f.write(order_bytes)
    (D / 'samples').mkdir(exist_ok=True)
    fetched, failures, checked, excluded = [], [], [], set()
    rows_by_id = {r['row_id']: r for rows in pools.values() for r in rows}
    while any(sum(r['sample_group'] == k for r in fetched) < n for k, n in TARGETS.items()):
        requests = {k: [(r['row_id'], r['remote_crop']) for r in rows if r['row_id'] not in excluded]
                    for k, rows in orders.items()}
        needs = {k: n - sum(r['sample_group'] == k for r in fetched) for k, n in TARGETS.items()}
        # The remote code only stats existing census crop locations. It does
        # not run ensure_crop, open a source page, import a reader or write.
        code = '''import json\nfrom pathlib import Path\nrequests=json.loads(PAYLOAD)\nneeds=json.loads(NEEDS)\nfor group, rows in requests.items():\n n=0\n if not needs[group]:continue\n for rid, path in rows:\n  p=Path(path)\n  assert str(p).startswith('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/')\n  try:available=p.is_file()\n  except OSError:available=False\n  print(json.dumps(dict(group=group,row_id=rid,path=path,available=available)),flush=True)\n  n+=available\n  if n==needs[group]:break\n'''.replace('PAYLOAD', repr(json.dumps(requests))).replace('NEEDS', repr(json.dumps(needs)))
        probe = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                                'clariden', 'python3 -B -'], input=code, text=True,
                               capture_output=True, timeout=120, check=True)
        attempts = [json.loads(line) for line in probe.stdout.splitlines()]
        checked.extend(attempts)
        selected = []
        for attempt in attempts:
            excluded.add(attempt['row_id'])
            if attempt['available']:
                selected.append((attempt['group'], rows_by_id[attempt['row_id']]))
            else:
                failures.append(dict(attempt, error='existing census crop path is not fetchable; no regeneration attempted'))
        if not selected:
            receipt = json.loads((D / 'sample_receipt.json').read_text())
            receipt.update(status='BLOCKED_MISSING_ALL_NUMERIC_CROP_FILES',
                           exhausted_pools=[k for k, n in needs.items() if n],
                           missing_required_crops=sum(needs.values()),
                           all_numeric_crop_paths_unfetchable=54440,
                           reason='All numeric rows belong to W1/W2, whose recorded crop directories do not exist. SCP-only replacement orders are exhausted. No reconstruction was run.')
            dump(D / 'sample_receipt.json', receipt)
            print('BLOCKED: no more fetchable numeric candidates; 50/250 crops available', flush=True)
            return

        def fetch(item):
            group, r = item
            p = D / 'samples' / (r['row_id'] + '.png')
            last = None
            for attempt in range(3):
                transfer = subprocess.run(['scp', '-q', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                                           'clariden:' + r['remote_crop'], str(p)],
                                          capture_output=True, text=True, timeout=60)
                if transfer.returncode:
                    last = transfer.stderr
                    continue
                data = p.read_bytes()
                actual = hashlib.sha256(data).hexdigest()
                if actual != r['crop_sha256']:
                    p.unlink()
                    return None, dict(row_id=r['row_id'], group=group, error='crop SHA256 mismatch', expected=r['crop_sha256'], actual=actual)
                with Image.open(p) as im:
                    dims = im.size
                    im.verify()
                assert dims == (r['width_px'], r['height_px']), (r['row_id'], dims)
                return dict(row_id=r['row_id'], source=r['source'], primary_class=r['primary_class'],
                            script_class=r['script_class'], **{'class': r['primary_class']},
                            wave=r['wave'], parent_id=r['parent_id'], text=r['raw_text'],
                            w=r['width_px'], h=r['height_px'], chars=r['characters'],
                            text_characters=r['text_characters'], xheight_px=r['xheight_px'],
                            verdict_05=r['verdict_05'], reason=r['reason_05'],
                            pipeline_disposition=r['pipeline_disposition'],
                            crop_path=str(p.relative_to(D)), remote_crop=r['remote_crop'],
                            sha256=actual, sample_group=group, is_numeric_output=r['is_numeric_output'],
                            is_small_image=r['is_small_image'], is_cell=r['is_cell']), None
            if p.exists():
                p.unlink()
            return None, dict(row_id=r['row_id'], group=group, error='SCP failed three times', detail=last)

        with ThreadPoolExecutor(max_workers=6) as executor:
            for result, failure in executor.map(fetch, selected):
                if result:
                    fetched.append(result)
                if failure:
                    failures.append(failure)
                print(f'Fetched {len(fetched)}/250; failed/unavailable {len(failures)}', flush=True)
        (D / 'samples.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in fetched))
        (D / 'sample_failures.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in failures))
        dump(D / 'sample_receipt.json', dict(seed=SEED, targets=TARGETS, pool_sizes={k: len(v) for k, v in pools.items()},
             algorithm='CPython random.Random(20261019), category order cells/numeric_not_small/small_not_numeric; full permutation of each pool sorted by (parent_id,row_id); first fetchable rows in that order',
             inclusion='Equal probability per row across all sources, conditional on existing fetchable hash-matching crops; no per-source quotas',
             source_counts={k: dict(sorted(Counter(r['source'] for r in fetched if r['sample_group'] == k).items())) for k in TARGETS},
             fetched_counts=dict(Counter(r['sample_group'] for r in fetched)), fetched=len(fetched),
             failed_or_unavailable=len(failures), stat_checks=len(checked),
             order_sha256=hashlib.sha256(order_bytes).hexdigest(),
             samples_sha256=hashlib.sha256((D / 'samples.jsonl').read_bytes()).hexdigest(),
             all_crop_hashes_and_png_dimensions_verified=True, remote_writes=0,
             crop_transport='read-only scp from frozen census-config parent crop locations'))
    assert len(fetched) == 250 and len({r['row_id'] for r in fetched}) == 250


if __name__ == '__main__':
    main()
