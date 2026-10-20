"""Draw the typology sample (120 short non-numeric) + owner-anchored supplement + 150 short numeric; rebuild W1 crops."""
import gzip, hashlib, io, json, random, sys
from pathlib import Path
from PIL import Image

SP = Path(sys.argv[1]); OUTD = Path(sys.argv[2]).resolve()
SEED = 20261019
SNAP = Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl')
PAGES = Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages')
rows = {}
for line in open(SP / 'small_pops.jsonl'):
    r = json.loads(line)
    rows.setdefault(r['line_id'], r)  # 150 first, then 888
with gzip.open(SP / 'census_compact.tsv.gz', 'rt') as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        if p[1] != 'W1' or int(p[7]) > 9:
            continue
        if p[0] in rows:
            continue
        rows[p[0]] = dict(population='W1', line_id=p[0], crop_path=None, text=json.loads(p[13]), width=int(p[5]), height=int(p[6]),
                          chars=int(p[7]), output_type=p[9], verdict_05=None if p[10] == 'None' else p[10], reason_05=p[11],
                          verdict_08=None, owner=None, source=p[2], primary_class=p[3], crop_sha256=p[12])
POPORDER = {'150': 0, '888': 1, 'W1': 2}
def pool(t):
    return sorted((r for r in rows.values() if r['chars'] <= 9 and r['output_type'] == t and r['height'] <= r['width']),
                  key=lambda r: (POPORDER[r['population']], r['line_id']))
nn = pool('non-numeric'); num = pool('numeric')
typ = random.Random(SEED).sample(nn, 120)
numsample = random.Random(SEED).sample(num, 150)
taken = {r['line_id'] for r in typ}
supp = [r for r in nn if r['line_id'] not in taken and (r['population'] == '150' or (r['population'] == '888' and r['owner'] is not None))]
for r in typ: r['set'] = 'typology_uniform'
for r in supp: r['set'] = 'typology_owner_supplement'
for r in numsample: r['set'] = 'numeric_sample'
chosen = typ + supp + numsample
need = {r['line_id']: r for r in chosen if r['population'] == 'W1'}
crops = OUTD / 'crops'; crops.mkdir(exist_ok=True)
found = 0
with SNAP.open() as f:
    for line in f:
        i = line.find('"id":"')
        rid = line[i + 6: line.index('"', i + 6)] if i >= 0 else None
        if rid not in need:
            r0 = json.loads(line)
            if r0['id'] not in need:
                continue
            rid = r0['id']
        r0 = json.loads(line); r = need[rid]
        assert r0['crop_sha256'] == r['crop_sha256']
        page = PAGES / (r0['crop_source_sha256'] + '.jpg')
        with Image.open(page) as im:
            c = im.convert(r0.get('crop_color_mode', 'L')).crop(r0['crop_bbox'])
            b = io.BytesIO(); c.save(b, format='PNG', compress_level=3)
        raw = b.getvalue()
        r['crop_hash_verified'] = hashlib.sha256(raw).hexdigest() == r['crop_sha256']
        out = crops / (rid + '.png'); out.write_bytes(raw)
        r['crop_path'] = str(out); r['crop_bbox'] = r0['crop_bbox']; found += 1
        assert c.size == (r['width'], r['height']), (rid, c.size)
print('pool non-numeric', len(nn), 'pool numeric', len(num), 'typology', len(typ), 'supplement', len(supp), 'numeric', len(numsample),
      'W1 crops rebuilt', found, 'of', len(need), 'hash ok', sum(r.get('crop_hash_verified', False) for r in need.values()))
with open(SP / 'chosen.jsonl', 'w') as o:
    for r in chosen:
        o.write(json.dumps(r, ensure_ascii=False) + '\n')
from collections import Counter
print(Counter((r['set'], r['population']) for r in chosen))
print(Counter(r['source'] for r in numsample))
