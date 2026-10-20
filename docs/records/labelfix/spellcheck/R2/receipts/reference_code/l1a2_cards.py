"""L1A2 offline word-card preparation, reviewed-control planting and validation.

Uses saved overlay evidence only; never imports or runs gates, detectors or readers.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import random
import re
import unicodedata as ud

from PIL import Image, ImageDraw, ImageFont
from scripts.labelfix.clariden.l1r2_changes import tokens, letter

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/labelfix/spellcheck/S8_DEV'
PRIVATE = BASE / 'private/audit100'
BLIND = BASE / 'audit100'
SELECTION = ROOT / 'docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl'
ORIGINAL = ROOT / 'docs/harvest/collection/v2/import_real_v2_train.jsonl'
HARVEST_ROOT = ROOT.parent / 'greek-ocr-toolkit'
SEED = 'L1A2-cards-20261017'
WAVES = ('round1', 'round2', 'mixed', 'vouli', 'openarchives', 'parliament')


def load(p):
    return json.loads(Path(p).read_text())


def dump(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def canon(text):
    # NFD first; contextual elision aliases become one atom, using the release census.
    return ud.normalize('NFC', tokens(text)[2])


def skeleton(text):
    return ''.join(c for c in ud.normalize('NFD', text) if letter(c))


def code_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'greekocr').rglob('*.py'))}


def inputs():
    selection = [json.loads(s) for s in SELECTION.read_text().splitlines()]
    receipt = load(SELECTION.with_name('audit100_receipt.json'))
    assert sha(SELECTION) == receipt['sha256']
    wanted = {r['line_id']: r for r in selection}
    assert len(selection) == len(wanted) == 100
    originals = {}
    with ORIGINAL.open() as f:
        for s in f:
            r = json.loads(s)
            if r['id'] in wanted:
                assert r['id'] not in originals
                originals[r['id']] = r
    saved = json.loads(gzip.decompress((PRIVATE/'selected_overlays.json.gz').read_bytes()))
    overlays = {r['line_id']: r for r in saved['records']}
    assert set(originals) == set(overlays) == set(wanted)
    return wanted, originals, overlays


def word_box(slots, start, end, size):
    """Saved recogniser spans + saved physical ink bounds, full crop height."""
    w, h = size
    selected = [s for s in slots if start <= s['start'] < end]
    assert selected and all(s['locator_span'] for s in selected)
    bounds = [x for s in selected for x in s['locator_span']]
    for s in selected:
        e = s.get('evidence') or {}
        bounds.extend(e.get('body') or [])
        for k in ('above', 'below', 'apostrophes'):
            for component in e.get(k, []):
                if component.get('bbox'):
                    bounds.extend([component['bbox'][0], component['bbox'][2]])
    # Retain punctuation / overhang context on both sides, without vertical trimming.
    return [max(0, math.floor(min(bounds)-.4*h)), 0,
            min(w, math.ceil(max(bounds)+.4*h)), h]


def crop_image(it):
    with Image.open(it['source_crop']) as im:
        crop = im.convert('RGB').crop(it['crop_box'])
    scale = min(3., 1200/crop.width)
    # Integer uniform magnification where possible, never upsample above 3x.
    size = (max(1, round(crop.width*scale)), max(1, round(crop.height*scale)))
    return crop.resize(size, Image.Resampling.LANCZOS), scale


def review_sheets(items, tag, n=6):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 23)
    for page in range(math.ceil(len(items)/n)):
        selected = items[page*n:(page+1)*n]
        rows = []
        for i, it in enumerate(selected, page*n):
            crop, _ = crop_image(it)
            with Image.open(it['source_crop']) as im:
                full = im.convert('RGB')
            sc = min(1., 1560/full.width)
            full = full.resize((round(full.width*sc), round(full.height*sc)), Image.Resampling.LANCZOS)
            row = Image.new('RGB', (1600, 55+crop.height+full.height+25), 'white')
            draw = ImageDraw.Draw(row)
            desc = it.get('proposed_correct') or ' / '.join(dict.fromkeys(it['forms'].values()))
            draw.text((12, 8), f'{i:03d}  {it["wave"]}  {desc}', font=font, fill='black')
            row.paste(crop, (12, 48))
            y = 55+crop.height
            row.paste(full, (12, y))
            x0, _, x1, h = it['crop_box']
            draw.rectangle((12+x0*sc, y, 12+x1*sc-1, y+h*sc-1), outline='#c00000', width=1)
            rows.append(row)
        sheet = Image.new('RGB', (1600, sum(r.height for r in rows)+8*(len(rows)-1)), '#ddd')
        y = 0
        for row in rows:
            sheet.paste(row, (0, y)); y += row.height+8
        name = f'{tag}_{page:02d}.png'
        sheet.save(PRIVATE/name)
        for it in selected:
            it['review_sheet'] = name
            it['review_sheet_sha256'] = sha(PRIVATE/name)


def prepare():
    wanted, originals, overlays = inputs()
    binding = dict(selection_sha256=sha(SELECTION), original_labels_sha256=sha(ORIGINAL),
        selected_overlays_sha256=sha(PRIVATE/'selected_overlays.json.gz'), code_hashes=code_hashes())
    if (PRIVATE/'input_binding.json').exists():
        assert load(PRIVATE/'input_binding.json') == binding
    else:
        dump(PRIVATE/'input_binding.json', binding)
    data, control_pool, aliases, line_records = [], [], [], []
    for ident in sorted(wanted):
        meta, src, ov = wanted[ident], originals[ident], overlays[ident]
        assert meta['wave'] == src['wave'] and meta['weight'] > 0
        assert ov['status'] == 'corrected' and ov['release_policy'] == 'sf6-release-v1'
        assert hashlib.sha256(src['label'].encode()).hexdigest() == ov['original_label_sha256']
        evidence = ov['changes'][0]['evidence']
        assert all(c['evidence']['recogniser_text'] == evidence['recogniser_text'] for c in ov['changes'])
        path = HARVEST_ROOT/src['crop']
        assert path.is_file()
        with Image.open(path) as im:
            size = im.size
        raw_lines = dict(google=src['label'], released=ov['label'], recogniser=evidence['recogniser_text'])
        words = {k: list(re.finditer(r'\S+', ud.normalize('NFD', s))) for k, s in raw_lines.items()}
        assert len({len(v) for v in words.values()}) == 1
        changed_indices = []
        for wi, (g, r, rec) in enumerate(zip(words['google'], words['released'], words['recogniser'])):
            assert skeleton(g.group()) == skeleton(r.group()) == skeleton(rec.group())
            raw_forms = dict(google=ud.normalize('NFC', g.group()), released=ud.normalize('NFC', r.group()),
                             recogniser=ud.normalize('NFC', rec.group()))
            forms = {k: canon(v) for k, v in raw_forms.items()}
            if not skeleton(g.group()):
                assert forms['google'] == forms['released'], ('changed standalone punctuation', ident, wi)
                continue
            it = dict(line_id=ident, wave=meta['wave'], weight=meta['weight'], word_index=wi,
                start=g.start(), end=g.end(), recogniser_start=rec.start(), recogniser_end=rec.end(),
                raw_forms=raw_forms, forms=forms, control=False, uid=digest([ident, wi, 'word'])[:24],
                source_crop=str(path), source_crop_sha256=sha(path), source_size=list(size),
                crop_box=word_box(evidence['slots'], rec.start(), rec.end(), size),
                original_label_sha256=ov['original_label_sha256'], overlay_evidence_sha256=ov['evidence_sha256'])
            if forms['google'] != forms['released']:
                data.append(it); changed_indices.append(wi)
            elif ud.normalize('NFD', raw_forms['google']) != ud.normalize('NFD', raw_forms['released']):
                aliases.append(dict(line_id=ident, word_index=wi, forms=raw_forms))
            if len(set(forms.values())) == 1:
                correct = forms['google']
                if 2 <= len(correct) <= 9 and all(c.isalpha() for c in correct) and any(ud.combining(c) for c in ud.normalize('NFD', correct)):
                    control_pool.append(dict(it, proposed_correct=correct))
        assert changed_indices, ident
        line_records.append(dict(line_id=ident, wave=meta['wave'], weight=meta['weight'],
            source_crop=str(path), source_crop_sha256=sha(path), source_size=list(size),
            original_label=src['label'], released_label=ov['label'], recogniser_text=evidence['recogniser_text'],
            changed_word_indices=changed_indices))
    required = math.ceil(len(data)*.08/.92)
    queues = {}
    for wave in WAVES:
        pool = sorted([it for it in control_pool if it['wave'] == wave], key=lambda x:x['uid'])
        random.Random(SEED+'controls'+wave).shuffle(pool)
        queues[wave] = pool
    # Round-robin candidates, spread across different lines wherever possible.
    review = []; used_lines = set()
    while len(review) < max(required*2, 30) and any(queues.values()):
        for wave in WAVES:
            pool = queues[wave]
            if not pool:
                continue
            at = next((i for i, it in enumerate(pool) if it['line_id'] not in used_lines), 0)
            it = pool.pop(at); review.append(it); used_lines.add(it['line_id'])
    review_sheets(review, 'control_review')
    review_sheets(data, 'word_review')
    dump(PRIVATE/'word_plan.json', data)
    dump(PRIVATE/'control_review_queue.json', review)
    dump(PRIVATE/'line_inventory.json', line_records)
    dump(PRIVATE/'alias_only_words_excluded.json', aliases)
    summary = dict(lines=len(wanted), word_cards=len(data), controls_required=required,
        aliases_only_words_excluded=len(aliases), per_wave={w:dict(lines=sum(r['wave']==w for r in line_records),
            word_cards=sum(it['wave']==w for it in data)) for w in WAVES}, seed=SEED)
    dump(PRIVATE/'plan_receipt.json', summary)
    print(json.dumps(summary))


def build():
    data = load(PRIVATE/'word_plan.json')
    queue = load(PRIVATE/'control_review_queue.json')
    verified = load(PRIVATE/'controls_pixel_review.json')
    required = math.ceil(len(data)*.08/.92)
    controls = []
    for review in verified:
        it = queue[review['queue_index']]
        assert review['pixel_verified'] is True and review['notes']
        assert review['correct'] == it['proposed_correct']
        assert review['source_crop_sha256'] == it['source_crop_sha256'] == sha(it['source_crop'])
        assert review['review_sheet_sha256'] == it['review_sheet_sha256'] == sha(PRIVATE/it['review_sheet'])
        nfd = ud.normalize('NFD', review['correct'])
        # A deliberately missing diacritic, never a letter substitution.
        marks = [i for i, c in enumerate(nfd) if ud.combining(c)]
        at = marks[-1]
        wrong = ud.normalize('NFC', nfd[:at]+nfd[at+1:])
        assert canon(wrong) != canon(review['correct'])
        controls.append(dict(it, control=True, uid=digest([it['uid'], 'control'])[:24],
            forms=dict(pixel_verified=review['correct'], planted_wrong=wrong),
            raw_forms=dict(pixel_verified=review['correct'], planted_wrong=wrong),
            known_answer=review['correct'], pixel_review=review))
    assert len(controls) >= required
    pool = data+controls
    random.Random(SEED+'deck').shuffle(pool)
    (BLIND/'img').mkdir(parents=True, exist_ok=True)
    blind, key, lines = [], [], {}
    for it in pool:
        ident = 'item_'+digest([SEED, it['uid']])[:16]
        line_id = it['line_id']
        if line_id not in lines:
            name = 'img/line_'+digest([SEED, line_id])[:16]+'.png'
            with Image.open(it['source_crop']) as im:
                im.convert('RGB').save(BLIND/name)
            lines[line_id] = name
        crop, scale = crop_image(it)
        name = 'img/'+ident+'.png'; crop.save(BLIND/name)
        candidates = list(dict.fromkeys(it['forms'].values()))
        random.Random(SEED+ident).shuffle(candidates)
        options = {chr(65+i):s for i, s in enumerate(candidates)}
        b = dict(id=ident, img=name, line_img=lines[line_id], options=options,
                 other_options=['none of these', 'unreadable'])
        blind.append(b)
        key.append(dict(b, **it, zoom_scale=scale,
            candidate_sources={k:[source for source,s in it['forms'].items() if s==v] for k,v in options.items()},
            expected_choice=next((k for k,v in options.items() if v==it.get('known_answer')), None)))
    dump(BLIND/'items_blind.json', blind)
    dump(PRIVATE/'items_key.json', key)
    dump(BLIND/'answers_blank.json', [dict(id=b['id'], choice=None, transcription=None, uncertain=None, note=None) for b in blind])
    (BLIND/'README.md').write_text('Read the printed ink literally, including misprints. Inspect the word zoom and full line. Choose a candidate, "none of these" (and transcribe), or "unreadable". Elision apostrophe aliases are displayed as U+2019. Do not regularise spelling or marks. Word zooms use uniform scaling at most 3x; full-line files preserve the source pixels. Record clipping or ambiguous word boundaries. Read independently. Distribute only this directory.\n')
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Print audit</title><style>body{font:18px Georgia;max-width:1600px;margin:24px auto;padding:12px;background:#eee}section{background:white;padding:20px;margin:24px 0;break-inside:avoid}img{max-width:100%;height:auto;display:block;margin:16px 0}.line{overflow:auto}li{font-size:28px;margin:10px}</style><p>Read the print literally, including misprints. Inspect the word and full line. Choose a candidate, none of these (transcribe), or unreadable. U+2019 represents elision apostrophe aliases.</p>'
    for b in blind:
        page += '<section><h2>'+b['id']+'</h2><img alt="Word zoom" src="'+b['img']+'"><div class="line"><img alt="Full line" src="'+b['line_img']+'"></div><ul>'+''.join('<li>'+k+': '+html.escape(v)+'</li>' for k,v in b['options'].items())+'</ul><p>none of these / unreadable</p></section>'
    (BLIND/'index.html').write_text(page+'</html>\n')
    print(json.dumps(dict(word_cards=len(data), controls=len(controls), total=len(blind))))


def validate():
    import numpy as np
    wanted, originals, overlays = inputs()
    binding = load(PRIVATE/'input_binding.json')
    production = SELECTION.parent
    manifest_path = production/'release/release/release_ensemble_ab.json'
    manifest = load(manifest_path)
    assert manifest['release_policy'] == 'sf6-release-v1' and manifest['variant'] == 'ensemble_ab'
    assert manifest['source_sha256'] == binding['original_labels_sha256']
    census = [json.loads(s) for s in (production/'census/changes/real_mark_correction_lines.jsonl').read_text().splitlines()]
    population = {r['line_id']:r for r in census if r['mode']=='ENSEMBLE_AB'}
    selection_receipt = load(SELECTION.with_name('audit100_receipt.json'))
    assert len(population) == selection_receipt['population_size'] == 155
    assert dict(Counter(r['wave'] for r in population.values())) == selection_receipt['per_wave_population']
    for ident, r in wanted.items():
        assert population[ident]['wave'] == r['wave']
        assert r['weight'] == selection_receipt['per_wave_population'][r['wave']]/sum(x['wave']==r['wave'] for x in wanted.values())
    assert binding['code_hashes'] == code_hashes()
    assert binding['selection_sha256'] == sha(SELECTION)
    assert binding['original_labels_sha256'] == sha(ORIGINAL)
    assert binding['selected_overlays_sha256'] == sha(PRIVATE/'selected_overlays.json.gz')
    blind, key = load(BLIND/'items_blind.json'), load(PRIVATE/'items_key.json')
    data = [k for k in key if not k['control']]
    controls = [k for k in key if k['control']]
    assert len({k['id'] for k in key}) == len(key) == len(blind)
    assert len({k['uid'] for k in data}) == len(data)
    control_by_index = {it['pixel_review']['queue_index']:it for it in controls}
    expected_order = load(PRIVATE/'word_plan.json') + [control_by_index[r['queue_index']]
        for r in load(PRIVATE/'controls_pixel_review.json')]
    random.Random(SEED+'deck').shuffle(expected_order)
    assert [it['uid'] for it in expected_order] == [it['uid'] for it in key]
    assert {k['line_id'] for k in data} == set(wanted)
    assert len(controls)/len(key) >= .08
    assert len({(k['line_id'],k['word_index']) for k in key}) == len(key)
    expected = set(); aliases = 0
    for ident in wanted:
        old = originals[ident]['label'].split(); new = overlays[ident]['label'].split()
        assert len(old) == len(new)
        for wi, (a,b) in enumerate(zip(old,new)):
            if canon(a) != canon(b):
                expected.add((ident,wi))
            elif ud.normalize('NFD',a) != ud.normalize('NFD',b):
                aliases += 1
    assert {(it['line_id'],it['word_index']) for it in data} == expected
    assert {(it['line_id'],it['word_index']) for it in load(PRIVATE/'word_plan.json')} == expected
    checked_lines = set()
    for b,k in zip(blind,key):
        assert set(b) == {'id','img','line_img','options','other_options'}
        assert b == {field:k[field] for field in b}
        assert b['other_options'] == ['none of these','unreadable']
        assert set(b['options'].values()) == set(k['forms'].values())
        expected_options = list(dict.fromkeys(k['forms'].values()))
        random.Random(SEED+k['id']).shuffle(expected_options)
        assert list(b['options'].values()) == expected_options
        assert k['wave'] == wanted[k['line_id']]['wave'] and k['weight'] == wanted[k['line_id']]['weight']
        assert sha(k['source_crop']) == k['source_crop_sha256']
        assert all(k['candidate_sources'][c] == [s for s,f in k['forms'].items() if f==v] for c,v in b['options'].items())
        expected_img,scale = crop_image(k)
        with Image.open(BLIND/b['img']) as im:
            assert np.array_equal(np.asarray(im),np.asarray(expected_img))
            w,h = k['crop_box'][2]-k['crop_box'][0],k['crop_box'][3]-k['crop_box'][1]
            assert 0 < scale <= 3 and im.width <= 3*w and im.height <= 3*h
            assert abs(im.width/w-im.height/h) <= 1/w+1/h
        if k['line_id'] not in checked_lines:
            with Image.open(k['source_crop']) as src,Image.open(BLIND/b['line_img']) as dst:
                assert src.size == dst.size and np.array_equal(np.asarray(src.convert('RGB')),np.asarray(dst))
                assert not dst.info
            checked_lines.add(k['line_id'])
        if k['control']:
            assert k['pixel_review']['pixel_verified'] and k['expected_choice']
            assert k['pixel_review']['correct'] == k['known_answer']
            assert b['options'][k['expected_choice']] == k['known_answer']
            assert sha(PRIVATE/k['review_sheet']) == k['pixel_review']['review_sheet_sha256']
        else:
            assert k['expected_choice'] is None and k['forms']['google'] != k['forms']['released']
            wi=k['word_index'];rec=overlays[k['line_id']]['changes'][0]['evidence']['recogniser_text']
            assert k['forms'] == dict(google=canon(originals[k['line_id']]['label'].split()[wi]),
                released=canon(overlays[k['line_id']]['label'].split()[wi]),recogniser=canon(rec.split()[wi]))
    assert not list(BLIND.rglob('*key*'))
    assert len(list((BLIND/'img').glob('*.png'))) == len(blind)+100
    for p in BLIND.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.html','.md'):
            assert not any(s in p.read_text() for s in ('candidate_sources','known_answer','pixel_verified','source_crop','recogniser','google','released','private/','control=True'))
    summary = dict(lines=100,word_cards=len(data),controls=len(controls),total=len(blind),
        control_fraction=len(controls)/len(blind),all_controls_pixel_verified=True,
        all_changed_words_covered=True,alias_only_words_excluded=aliases,full_lines_pixel_identical=100,
        all_word_images_reconstructed=True,max_zoom=3,source_code_unchanged=True,seed=SEED,
        per_wave={w:dict(lines=sum(r['wave']==w for r in wanted.values()),word_cards=sum(k['wave']==w for k in data),
            controls=sum(k['wave']==w for k in controls)) for w in WAVES},
        blind_sha256=sha(BLIND/'items_blind.json'),key_sha256=sha(PRIVATE/'items_key.json'),
        builder_sha256=sha(Path(__file__)),validation='PASS; data-card print truth remains pending independent readers')
    summary.update(production_manifest_sha256=sha(manifest_path),production_original_label_file_match=True,
        production_audit_population_match=True,seeded_deck_and_options_verified=True)
    dump(PRIVATE/'validation_receipt.json',summary)
    manifest={str(p.relative_to(BASE)):sha(p) for p in sorted(BLIND.rglob('*')) if p.is_file()}
    dump(PRIVATE/'blind_manifest.json',manifest)
    print(json.dumps(summary))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','build','validate'])
    args=parser.parse_args()
    globals()[args.action]()
