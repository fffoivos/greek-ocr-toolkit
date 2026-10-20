"""T4c: fresh blind cards from post-fix usable lines; 30 screen-pass + up to 10 screen-reject per stratum, excluding already-carded lines."""
import json, random, os, glob, hashlib
from PIL import Image
OUT = '/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/t4c'
F = os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/features.jsonl')
carded = set(json.loads(l)['id'] for l in open(os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/card_eval.jsonl')))
STRATA = {'gazette_modern': ('government-gazette', ['modern_scanned']), 'gazette_poly1900': ('government-gazette', ['poly1900']),
          'lekythos_poly1900': ('lekythos', ['poly1900']), 'bsb_poly1850': ('bsb', ['poly1850']), 'bsb_mixed': ('bsb', ['mixed_greek_latin']),
          'oa_poly1900': ('openarchives', ['poly1900']), 'pleias_poly1850': ('pleias', ['poly1850']), 'anemi_poly1850': ('anemi', ['poly1850'])}
rows = [json.loads(l) for l in open(F)]
print('carded', len(carded))
for name, (src, cls) in STRATA.items():
    pool = [r for r in rows if r['source'] == src and r['primary_class'] in cls and r.get('fixed_usable') and r['id'] not in carded]
    rng = random.Random('t4c:' + name)
    passes = sorted([r for r in pool if r.get('usable_final')], key=lambda r: r['id'])
    rejects = sorted([r for r in pool if r.get('screen_reject')], key=lambda r: r['id'])
    pick = [(r, 'pass') for r in rng.sample(passes, min(30, len(passes)))] + [(r, 'reject') for r in rng.sample(rejects, min(10, len(rejects)))]
    rng.shuffle(pick)
    d = f'{OUT}/{name}'; os.makedirs(d + '/crops', exist_ok=True)
    cards, key = [], {}
    for i, (r, arm) in enumerate(pick, 1):
        cid = f'c{i:03d}'; x0, y0, x1, y1 = r['crop_bbox']
        Image.open(r['crop_page_path']).crop((x0, y0, x1, y1)).save(f'{d}/crops/{cid}.png')
        label = r['label_after_conventions'] if r.get('usable_final') else r['fixed_label']
        cards.append(dict(card_id=cid, crop=f'crops/{cid}.png', google_text=label))
        key[cid] = dict(line_id=r['id'], arm=arm, pool_pass=len(passes), pool_reject=len(rejects), assembly_changed=r['assembly_changed'], tags=r.get('tags'))
    open(d + '/cards.jsonl', 'w').write(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cards))
    json.dump(key, open(f'{OUT}/{name}_key.json', 'w'), indent=1)
    print(name, 'pool pass/reject', len(passes), len(rejects), '-> cards', len(cards))
