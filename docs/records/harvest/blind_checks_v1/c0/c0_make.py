"""C0: fresh uniform blind cards (seeded, never length-sorted) from post-fix usable lines; excludes all prior card lines."""
import json, random, os, sys
from PIL import Image
OUT = sys.argv[1]; SPEC = json.loads(sys.argv[2])  # {name: [track, source, [classes], n]}
F = os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/features.jsonl')
seen = set(json.loads(l)['id'] for l in open(os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/card_eval.jsonl')))
for k in os.listdir(os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/t4c')):
    if k.endswith('_key.json'):
        seen |= {v['line_id'] for v in json.load(open(os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/t4c/' + k))).values()}
rows = [json.loads(l) for l in open(F)]
for name, (track, src, cls, n) in SPEC.items():
    pool = sorted([r for r in rows if r['track'] == track and r['source'] == src and r['primary_class'] in cls and r['fixed_usable'] and not r['text_exclusions'] and r['id'] not in seen], key=lambda r: r['id'])
    seed = f'c0:{name}'; pick = random.Random(seed).sample(pool, min(n, len(pool)))
    d = f'{OUT}/{name}'; os.makedirs(d + '/crops', exist_ok=True); cards = []; key = {'_seed': seed, '_pool': len(pool)}
    for i, r in enumerate(pick, 1):
        cid = f'c{i:03d}'; Image.open(r['crop_page_path']).crop(tuple(r['crop_bbox'])).save(f'{d}/crops/{cid}.png')
        cards.append(dict(card_id=cid, crop=f'crops/{cid}.png', google_text=r['label_after_conventions']))
        key[cid] = dict(line_id=r['id'], primary_class=r['primary_class'], screen_merged=r['screen_reject'], tags=r['tags'])
    open(d + '/cards.jsonl', 'w').write(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cards))
    json.dump(key, open(f'{OUT}/{name}_key.json', 'w'), indent=1); print(name, 'pool', len(pool), 'cards', len(cards))
