"""Prepare, but DO NOT execute, the optional source-page crop fallback."""
import gzip
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[4]


def main():
    orders = [json.loads(line) for line in gzip.open(D / 'sample_order.jsonl.gz', 'rt')]
    wanted = {r['group']: r['row_ids'][:150 if r['group'] == 'cells' else 50]
              for r in orders if r['group'] in ('cells', 'numeric_not_small')}
    selected_ids = {rid for ids in wanted.values() for rid in ids}
    population = {}
    for line in gzip.open(D / 'population_cells.jsonl.gz', 'rt'):
        r = json.loads(line)
        if r['row_id'] in selected_ids:
            population[r['row_id']] = r
    config = json.loads((ROOT / 'docs/harvest/line_pipeline/clariden/full-run-config.json').read_text())
    bindings = {}
    for wave in ('W1', 'W2'):
        p = ROOT.parent / f'collect-v3-data/snapshots/{wave}_features_20261018_0524.jsonl'
        parent = next(p for p in config['parents'] if p['id'] == f'collect-v3-{wave}-20261018-0524')
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for line in stream:
                h.update(line)
                r = json.loads(line)
                if r['id'] not in selected_ids:
                    continue
                source = r['crop_source_image']
                for old, new in parent['path_map'].items():
                    if source.startswith(old + '/'):
                        source = new + source[len(old):]
                assert r['crop_sha256'] == population[r['id']]['crop_sha256']
                bindings[r['id']] = dict(source_page=source, source_sha256=r['crop_source_sha256'],
                                          bbox=r['crop_bbox'], color_mode=r.get('crop_color_mode', 'L'))
        assert h.hexdigest() == parent['sha256']
    assert len(bindings) == 200
    records = [dict(population[rid], sample_group=group, **bindings[rid]) for group, ids in wanted.items() for rid in ids]
    p = D / 'pending_reconstruction.jsonl'
    p.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in records))
    (D / 'pending_reconstruction_receipt.json').write_text(json.dumps(dict(
        status='PREPARED_NOT_EXECUTED_REQUIRES_OWNER_SCOPE_CHANGE', rows=200,
        groups={k: len(v) for k, v in wanted.items()}, source_pages=len({r['source_page'] for r in records}),
        manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(), remote_writes=0,
        proposed_action='Read frozen source pages, verify page hashes, reproduce the existing L-mode bbox PNG compress_level=3 contract in memory, verify exact census crop hashes, stream 200 PNGs to this Mac. No pipeline, reader, detector, Slurm or remote output file.'), indent=2) + '\n')


if __name__ == '__main__':
    main()
