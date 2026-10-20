"""Percentile rank of each owner-judged short 150/888 row's ratio within the census distribution of the same output type and chars."""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
SP = Path(sys.argv[1])
dist = defaultdict(list)
with gzip.open(SP / 'census_compact.tsv.gz', 'rt') as f:
    next(f)
    for line in f:
        p = line.split('\t'); w, h, c = int(p[5]), int(p[6]), int(p[7])
        if c <= 9 and h <= w:
            dist[(p[9], c)].append(w / h)
dist = {k: np.sort(v) for k, v in dist.items()}
print('| population | line_id | text | w×h | ratio | chars | type | census n (type, chars) | percentile of ratio | owner | 0.5 | 0.8 |')
print('|---|---|---|---|---:|---:|---|---:|---:|---|---|---|')
for l in open(SP / 'small_pops.jsonl'):
    r = json.loads(l)
    if r['chars'] > 9 or r['height'] > r['width'] or r['owner'] is None:
        continue
    d = dist[(r['output_type'], r['chars'])]; x = r['width'] / r['height']
    pct = 100 * np.searchsorted(d, x, side='right') / len(d)
    print(f'| {r["population"]} | {r["line_id"]} | `{r["text"]}` | {r["width"]}×{r["height"]} | {x:.2f} | {r["chars"]} | {r["output_type"]} | {len(d):,} | {pct:.1f} | {r["owner"]} | {r["verdict_05"]} | {r["verdict_08"]} |')
