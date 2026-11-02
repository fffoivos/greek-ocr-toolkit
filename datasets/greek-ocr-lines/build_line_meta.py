"""One row per published real line (public greek-ocr-lines @859fa987): book source + position on page, from the sealed build's rows table."""
import pyarrow.parquet as pq, pyarrow as pa, glob, json, hashlib, collections
O = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/builds/hfd-e1-001'
order, split = [], {}
for f in sorted(glob.glob(O + '/frozen-859fa987/data/real/*/*.parquet')):
    sp = f.split('/')[-2]  # the published split (directory under data/real/)
    for lid in pq.read_table(f, columns=['line_id'])['line_id'].to_pylist(): order.append(lid); split[lid] = sp
src = {'canonical_book_id': 'book_id', 'provider': 'provider', 'source': 'source', 'item': 'item', 'volume': 'volume',
       'source_title': 'title', 'year': 'year', 'page': 'page', 'catalogue_url': 'catalogue_url', 'source_url': 'source_url',
       'crop_bbox': 'bbox', 'source_missing_reasons_json': 'missing_reasons'}
meta = {}
for f in sorted(glob.glob(O + '/Cprime/tables/rows/*.parquet')):
    t = pq.read_table(f, columns=['trainer_line_id'] + list(src))
    for r in t.to_pylist():
        lid = r.pop('trainer_line_id')
        if lid in split:
            assert lid not in meta, 'duplicate ' + lid
            meta[lid] = r
assert len(meta) == len(split) == len(order) == 878202, (len(meta), len(split))
cols = collections.defaultdict(list)
for lid in order:
    r = meta[lid]
    cols['line_id'].append(lid); cols['split'].append(split[lid])
    for k, v in src.items():
        x = r[k]
        if v == 'bbox': x = json.loads(x) if x else None
        if v == 'missing_reasons': x = x if x not in (None, '{}', 'null') else None
        if v in ('year', 'page', 'volume') and x is not None: x = str(x)
        cols[v].append(x)
schema = pa.schema([('line_id', pa.string()), ('split', pa.string())] + [(v, pa.list_(pa.int32()) if v == 'bbox' else pa.string()) for v in src.values()])
tab = pa.table({n: cols[n] for n in schema.names}, schema=schema)
import os; os.makedirs(O + '/lines-meta/metadata', exist_ok=True)
out = O + '/lines-meta/metadata/real_lines.parquet'
pq.write_table(tab, out, compression='zstd', row_group_size=100000)
h = hashlib.sha256(open(out, 'rb').read()).hexdigest()
nn = {n: tab.num_rows - tab[n].null_count for n in schema.names}
print(json.dumps({'rows': tab.num_rows, 'bytes': os.path.getsize(out), 'sha256': h, 'nonnull': nn}))
print(json.dumps(tab.slice(0, 1).to_pylist()[0], ensure_ascii=False)[:800])
print(json.dumps(tab.slice(500000, 1).to_pylist()[0], ensure_ascii=False)[:800])
