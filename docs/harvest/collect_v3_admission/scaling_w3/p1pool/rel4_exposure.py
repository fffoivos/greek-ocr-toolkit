"""Exact REL4 exclusion setup body; see REL4_EXPOSURE_COPY.json."""
from build_release_v4 import records, require

def union(paths):
    editions, books = {}, {}
    for r in records(paths['edition_map.jsonl']):
        require(r['edition_id'] not in editions, 'duplicate edition')
        editions[r['edition_id']] = r['split']
        for book in r['member_documents']:
            require(book not in books, 'duplicate edition member')
            books[book] = r['edition_id']
    candidates = set()
    for r in records(paths['candidates_v3.jsonl']):
        candidates.add((r['parent_id'], r['row_id']))
    pixels, readout_keys = set(), set()
    for r in records(paths['candidates_readout.jsonl']):
        key = (r['parent_id'], r['row_id'])
        require(key in candidates, 'readout not a benchmark candidate')
        readout_keys.add(key)
        pixels.add(r['crop_sha256'])
    require(readout_keys == candidates, 'incomplete benchmark pixel readout')
    for name in ('seal04_test','seal04_dev'):
        for r in records(paths[name]):
            require(r['split']==name.split('_')[1], 'seal04 split mismatch')
            candidates.add((r['parent_id'],r['row_id']))
            pixels.add(r['crop_sha256'])
    return editions, books, candidates, pixels
