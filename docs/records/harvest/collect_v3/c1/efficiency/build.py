#!/usr/bin/env python3
"""Offline, serial pack builder. Never imports the live collect_v3 package."""
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import socket
import struct
import subprocess
import time
import unicodedata as ud

ROOT = Path(__file__).resolve().parent
C1 = ROOT.parent
PROJECTS = Path.home() / 'Projects'
RUN = PROJECTS / 'collect-v3-data/run'
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad')
ARMS = {'E0a': 'control; original protocol', 'E0b': 'control repeat; original protocol',
        'E1': 'one context for the whole bed; original protocol',
        'E2': 'word crops 3x and glyph close-ups 8x; no full-line crop',
        'E3': 'compact protocol and minimal item lines',
        'E4': 'one context plus compact protocol and minimal item lines'}
SOURCES = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    path = Path(path)
    SOURCES[str(path.resolve())] = sha(path)
    return json.loads(path.read_text())


def rows(path, bind=True):
    path = Path(path)
    if bind:
        SOURCES[str(path.resolve())] = sha(path)
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_json(path, obj):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def png_size(path):
    data = Path(path).read_bytes()[:24]
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    return struct.unpack('>II', data[16:24])


def normal(text):
    return ''.join(ud.normalize('NFC', text).split())


def spans(node):
    return [(int(s.get('startIndex', 0)), int(s['endIndex']))
            for s in node.get('layout', {}).get('textAnchor', {}).get('textSegments', [])]


def anchor_text(doc, node):
    return ''.join(doc['text'][a:b] for a, b in spans(node))


def frame(page, native_size):
    matrix = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
    returned = (page['dimension']['width'], page['dimension']['height'])
    for m in page.get('transforms', []):
        if m['type'] not in (5, 6):
            raise ValueError('Unsupported response transform')
        raw = base64.b64decode(m['data'])
        values = struct.unpack('<' + ('f' if m['type'] == 5 else 'd')*(m['rows']*m['cols']), raw)
        a = [list(values[i*m['cols']:(i+1)*m['cols']]) for i in range(m['rows'])]
        if m['rows'] == 2:
            a.append([0., 0., 1.])
        matrix = [[sum(a[i][k]*matrix[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    if not page.get('transforms') and tuple(returned) != tuple(native_size):
        raise ValueError(f'Unmapped response frame: {returned} vs {native_size}')
    augmented = [matrix[i] + [float(i == j) for j in range(3)] for i in range(3)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(augmented[i][col]))
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        if abs(divisor) < 1e-15:
            raise ValueError('Singular response transform')
        augmented[col] = [v/divisor for v in augmented[col]]
        for i in range(3):
            if i != col:
                factor = augmented[i][col]
                augmented[i] = [a-factor*b for a,b in zip(augmented[i], augmented[col])]
    return [row[3:] for row in augmented], returned


def box(node, inverse, returned):
    poly = node.get('layout', {}).get('boundingPoly', {})
    points = poly.get('vertices') or [dict(x=v.get('x', 0)*returned[0], y=v.get('y', 0)*returned[1]) for v in poly.get('normalizedVertices', [])]
    if not points:
        return None
    a = [[sum(inverse[i][j]*[v.get('x', 0), v.get('y', 0), 1][j] for j in range(3)) for i in range(3)] for v in points]
    a = [[p[0]/p[2], p[1]/p[2]] for p in a]
    if not all(math.isfinite(v) for p in a for v in p):
        raise ValueError('Nonfinite response geometry')
    return [min(p[0] for p in a), min(p[1] for p in a), max(p[0] for p in a), max(p[1] for p in a)]


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


def inside(b, row_box):
    return b is not None and all([b[0] >= row_box[0], b[1] >= row_box[1], b[2] <= row_box[2], b[3] <= row_box[3]])


def local_box(b, crop_box, size, padding=1):
    sx, sy = size[0]/(crop_box[2]-crop_box[0]), size[1]/(crop_box[3]-crop_box[1])
    out = [max(0, math.floor((b[0]-crop_box[0])*sx)-padding),
           max(0, math.floor((b[1]-crop_box[1])*sy)-padding),
           min(size[0], math.ceil((b[2]-crop_box[0])*sx)+padding),
           min(size[1], math.ceil((b[3]-crop_box[1])*sy)+padding)]
    if out[2] <= out[0] or out[3] <= out[1]:
        raise ValueError(f'Empty mapped box: {out}')
    return out


def graphemes(text):
    out = []
    for i, c in enumerate(text):
        if ud.combining(c) and out:
            out[-1][1] = i+1
        elif not c.isspace():
            out.append([i, i+1])
    return out


def compact_protocol(bed):
    if bed == 'bsb':
        return '''You are a blind OCR label checker. Each cards.jsonl line gives card_id, crop (relative to this file), google_text, and word_scripts ([word, Unicode script]). Compare the printed pixels with the literal transcription; do not guess the reader or source.

Open every crop with Read. For small crops make enlarged copies with ImageMagick in your zoom folder: magick in.png -resize 300% out.png. Do not use sips or Pillow.

Compare character by character: accents, breathings, iota subscript, grave/acute, circumflex, diaeresis, final/medial sigma, punctuation, line-end hyphens, digits, and old Cyrillic ѣ і ѳ ѵ ъ. Check every word against word_scripts; a wrong script or mixed-script word is an error.

Record letters=y only if all base letters, digits and words are present and correct, in the correct script, ignoring diacritics; n otherwise; u if pixels prevent deciding. Record marks=y if all diacritics are correct, n if any are wrong/missing/extra, na if no diacritic-bearing script. Judge marks even when letters=n whenever marks can be compared. Record crop_ok=y only for exactly one complete printed line, first through last character, with other-line/column ink limited to thin ascender/descender slivers without readable characters or whole letter bodies; n for readable foreign characters/bodies or clipping at either end or through letters.

errors is a list (empty if none), limited to wrong_letter, lookalike_script_letter, missing_word_or_span, extra_text, wrong_mark, missing_mark, extra_mark, punctuation, hyphen, digits, merged_two_lines, crop_clipped, crop_overrun. detail gives exact wrong parts as printed → google pairs, or an empty string.

Use Write to overwrite OUT with one JSON object per card: card_id, letters, marks, crop_ok, errors, detail. Rewrite all lines so far every few cards. Exactly one line per card. Then report card count; letters y/n/u, marks y/n/na, crop_ok y/n counts; three most common error types; one sentence on any systematic pattern. Open only cards.jsonl and crop images; never keys or anything else.
'''
    return '''You are a blind glyph adjudicator. Each items.jsonl line has item_id, crop (relative to this file), masked_text and slots (possibly 0). Each ⟦1⟧, ⟦2⟧, … hides a transcription word-final ъ or ь; determine the printed glyph from ink alone.

Open every crop with Read. Zoom EVERY hidden letter, never judge it at normal size: use ImageMagick in ZOOM, magick in.png -resize 400% out.png, optionally -crop WxH+X+Y first. Do not use sips or Pillow.

For each slot inspect the word's final glyph: ъ has a bowl/stem with a top horizontal flag/bar extending LEFT, often to x-height or above; ь has the same bowl/stem without the flag; other means another glyph or none printed; u means worn, blurred or cut ink prevents deciding. Do not use spelling, grammar or what should be printed; another reader handles that.

For every item list OTHER printed word-final ъ omitted by the transcription, excluding hidden slots, as whole words as printed. Say whether pre-1918 orthography (word-final ъ, ѣ, і, ѳ) is visible: yes/no/unclear.

Use Write to overwrite OUT with one JSON object per item containing item_id, slots (slot-number strings to ъ/ь/other/u; {} for zero slots), confidence (high/low per slot), unmarked_final_hard_signs (word list), pre1918, note. Rewrite all lines so far every few items. Report items done, ъ/ь/other/u slot counts, number of items with unmarked hard signs, and one sentence on glyph distinctness in these faces. Open only items.jsonl and crop images; never keys or anything else in the folder.
'''


def protocol(bed, arm):
    source = C1 / ('LABEL_CHECK_v2.md' if bed == 'bsb' else 'yer_adjudication/INK.md')
    SOURCES[str(source.resolve())] = sha(source)
    text = source.read_text()
    if arm in ('E3', 'E4'):
        return compact_protocol(bed)
    if arm != 'E2':
        return text
    if bed == 'bsb':
        old = 'Each card is one printed text line, cropped from a scanned page (`crop`), plus a machine transcription of it (`google_text`).'
        new = ('Each card supplies `crop` as an ordered list of 3x word-crop paths covering every transcribed word and 8x close-up paths for every nonspace glyph, plus `google_text`; the paths are relative to cards.jsonl, and you no longer get the full-line crop, its complete line boundaries, or surrounding line/column context.')
    else:
        old = 'Each item is one printed line of Russian text, cropped from a scanned page (`crop`), and a transcription of it (`masked_text`) in which some word-final letters are hidden as ⟦1⟧, ⟦2⟧, …'
        new = ('Each item supplies `crop` as an ordered list of 3x crops of words holding hidden slots and 8x close-ups of their final letters (word then final letter in slot order; empty for zero slots), with paths relative to items.jsonl, and `masked_text` with hidden word-final letters ⟦1⟧, ⟦2⟧, …; you no longer get the full-line crop, non-slot words, or surrounding line context.')
    assert text.count(old) == 1
    return text.replace(old, new)


def load_inputs():
    bsb_path = RUN/'W1/c1/bsb_poly1850__poly1850/cards.jsonl'
    bsb = list(rows(bsb_path))
    yer = list(rows(C1/'yer_adjudication/items_a.jsonl')) + list(rows(C1/'yer_adjudication/items_b.jsonl'))
    assert len(bsb) == 100 and len(yer) == 59 and sum(r['slots'] for r in yer) == 65
    data = {'bsb': bsb, 'yer': yer}
    input_key = {'bsb': {}, 'yer': {}}
    # BSB's original key is deliberately never opened. Match copies by SHA256.
    wanted_hashes = {}
    for c in bsb:
        src = bsb_path.parent/c['crop']
        wanted_hashes.setdefault(sha(src), []).append(c['card_id'])
        input_key['bsb'][c['card_id']] = {'source_crop': str(src), 'source_crop_sha256': sha(src)}
    yer_key = read_json(C1/'yer_adjudication/key.json')
    v2_key = read_json(SCRATCH/'v2/ia_russian_key.json')
    c1_key = read_json(RUN/'W1/c1/ia_russian__cyrillic_key.json')
    wanted_ids = {}
    for item in yer:
        iid = item['item_id']; meta = yer_key[iid]
        original = (v2_key if meta['set'] == 'v2' else c1_key)[meta['card_id']]['line_id']
        wanted_ids[original] = iid
        input_key['yer'][iid] = {'source_crop': item['crop'], 'source_crop_sha256': sha(item['crop']),
                                 'source_set': meta['set'], 'original_card_id': meta['card_id'], 'line_id': original}
    # Only read source rows. No source locks, writes, imports, or cache population.
    w1path = RUN/'W1/features.jsonl'
    for r in rows(w1path):
        h = r.get('crop_sha256')
        if h in wanted_hashes:
            for cid in wanted_hashes[h]:
                meta = input_key['bsb'][cid]
                if 'row' in meta and meta['row']['id'] != r['id']:
                    raise ValueError('Ambiguous BSB crop hash')
                meta['row'] = r
        if r['id'] in wanted_ids:
            input_key['yer'][wanted_ids[r['id']]]['row'] = r
    # Earlier v2 rows and responses, when not present in W1.
    old_features = PROJECTS/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/features.jsonl'
    needed = {m['line_id']: iid for iid, m in input_key['yer'].items() if 'row' not in m}
    for r in rows(old_features):
        if r['id'] in needed:
            input_key['yer'][needed[r['id']]]['row'] = r
    old_base = PROJECTS/'greek-ocr-toolkit-sol-funnel-ia/docs/harvest/sample_v1/ia'
    old_pages = {r['id']: r for r in rows(old_base/'pages.jsonl')}
    for bed, metas in input_key.items():
        for iid, m in metas.items():
            if 'row' not in m:
                raise ValueError(f'Cannot locate source row {bed}/{iid}')
            r = m['row']; m['line_id'] = r['id']
            if 'crop_source_image' in r:
                page = read_json(RUN/'W1/pages'/f'{r["page_id"]}.json')
                m['response'] = page['response']; m['native_size'] = [page['analysis_page']['width'], page['analysis_page']['height']]
            else:
                page = old_pages[r['page_id']]
                parsed = old_base/'google/parsed/docai'/f'{page["image_sha256"]}.json'
                if parsed.exists():
                    raw = Path(read_json(parsed)['raw_json_path'])
                    if not raw.exists():
                        hits = list((old_base/'google/docai').rglob(raw.name))
                        raw = hits[0] if len(hits) == 1 else raw
                    m['response'] = str(raw) if raw.exists() else None
                else:
                    m['response'] = None
                m['native_size'] = [page['width'], page['height']]
    # Keep answers only under keys; cross-check both independent ink sources.
    btruth = {}
    for name in ('a', 'b'):
        for r in rows(C1/f'verdicts/bsb_poly1850__poly1850__{name}.jsonl'):
            if r['card_id'] in btruth:
                raise ValueError('Duplicate BSB reference')
            btruth[r['card_id']] = r
    ytruth = {}
    for name in ('a', 'b'):
        for r in rows(C1/f'yer_adjudication/ink_{name}.jsonl'):
            if r['item_id'] in ytruth:
                raise ValueError('Duplicate yer reference')
            ytruth[r['item_id']] = r
    table = read_json(C1/'yer_adjudication/table.json')
    assert {r['item_id'] for r in table} == set(ytruth)
    for r in table:
        t = {m[1]: m[2] for slot in r['slots'] if (m := re.fullmatch(r'(\d+):g=. ink=(ъ|ь|other|u) prior=.+', slot))}
        assert t == ytruth[r['item_id']]['slots'], (r, t)
    assert set(btruth) == {r['card_id'] for r in bsb}
    assert set(ytruth) == {r['item_id'] for r in yer}
    write_json(ROOT/'keys/truth.json', {'bsb': btruth, 'yer': ytruth})
    return data, input_key


def word_geometry(meta, text):
    """Align exact OCR nonspace characters to the supplied (unmasked) text."""
    r = meta['row']; cb = r['crop_bbox']; size = png_size(meta['source_crop'])
    words = list(re.finditer(r'\S+', text))
    response = meta.get('response')
    selected = []; symbols = []; reason = None
    if response:
        doc = read_json(response)['document']; page = doc['pages'][0]
        inverse, returned = frame(page, meta['native_size'])
        for i, token in enumerate(page.get('tokens', [])):
            b = box(token, inverse, returned)
            if inside(b, cb) and i not in r.get('dropped_token_ids', []):
                selected.append({'token_id': i, 'text': anchor_text(doc, token), 'box': b, 'spans': spans(token)})
        selected.sort(key=lambda t: t['spans'][0][0] if t['spans'] else -1)
        owned = [s for t in selected for s in t['spans']]
        for symbol in page.get('symbols', []):
            ss = spans(symbol); b = box(symbol, inverse, returned)
            if b and ss and all(any(a <= x < y <= z for a, z in owned) for x, y in ss):
                symbols.append({'text': anchor_text(doc, symbol), 'box': b, 'spans': ss})
        symbols.sort(key=lambda s: s['spans'][0][0])
        if not selected:
            reason = 'no_token_boxes_inside_crop'
        elif normal(''.join(t['text'] for t in selected)) != normal(text):
            reason = 'token_text_does_not_align_with_supplied_line'
    else:
        reason = 'earlier_v2_response_or_token_boxes_missing'
    geometry = []
    # NFC character offsets excluding whitespace, preserving all word punctuation.
    offset = 0; token_chars = []
    for token in selected:
        token_chars += [(c, token['box'], token['token_id']) for c in normal(token['text'])]
    symbol_chars = []
    for symbol in symbols:
        symbol_chars += [(c, symbol['box']) for c in normal(symbol['text'])]
    symbols_exact = normal(''.join(s['text'] for s in symbols)) == normal(text)
    n = max(1, len(text))
    for widx, match in enumerate(words, 1):
        word = match.group(); chars = normal(word); length = len(chars)
        if reason:
            b = [cb[0]+(cb[2]-cb[0])*match.start()/n, cb[1], cb[0]+(cb[2]-cb[0])*match.end()/n, cb[3]]
            token_ids = []
        else:
            b = union([t[1] for t in token_chars[offset:offset+length]])
            token_ids = sorted({t[2] for t in token_chars[offset:offset+length]})
        word_box = local_box(b, cb, size)
        letters = []
        # Symbol close-ups, otherwise character-count subdivisions of this word.
        for j, (start, end) in enumerate(graphemes(ud.normalize('NFC', word))):
            if not reason and symbols_exact:
                lb = union([s[1] for s in symbol_chars[offset+start:offset+end]])
                approx_letter = False
            else:
                lb = [b[0]+(b[2]-b[0])*start/max(1,length), b[1], b[0]+(b[2]-b[0])*end/max(1,length), b[3]]
                approx_letter = True
            letters.append({'glyph_index': j+1, 'text': ud.normalize('NFC', word)[start:end],
                            'box': local_box(lb, cb, size, padding=2), 'approx_letter_box': approx_letter})
        geometry.append({'word_index': widx, 'text': word, 'box': word_box, 'token_ids': token_ids, 'letters': letters})
        offset += length
    return geometry, reason


def render_crops(source, requests):
    """One ImageMagick invocation per item, serial; fresh pixels, never links."""
    if not requests:
        return
    cmd = ['magick', '-limit', 'thread', '1', str(source)]
    for box_, scale, dest in requests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        x0, y0, x1, y1 = box_
        cmd += ['(', '+clone', '-crop', f'{x1-x0}x{y1-y0}+{x0}+{y0}', '+repage',
                '-resize', f'{scale*100}%', '-strip', '-write', str(dest), '+delete', ')']
    cmd += ['null:']
    env = dict(os.environ, MAGICK_TEMPORARY_PATH=str(ROOT/'.work'))
    subprocess.run(cmd, check=True, env=env, capture_output=True)


def e2_items(bed, items, metadata):
    result = {}; evidence = {}
    for item in items:
        iid = item['card_id' if bed == 'bsb' else 'item_id']; m = metadata[iid]
        text = item.get('google_text', item.get('masked_text'))
        # Use the original machine transcription to restore hidden characters for
        # geometric alignment only; never include this restoration in a pack.
        if bed == 'yer':
            original = read_json(C1/'yer_adjudication/key.json')[iid]
            text = original['google_text']
        geometry, reason = word_geometry(m, text)
        requests = []; images = []; output_geometry = []
        masked_words = item.get('masked_text', '').split()
        for word in geometry:
            if bed == 'yer' and not re.search(r'⟦\d+⟧', masked_words[word['word_index']-1]):
                continue
            name = f'{iid}_w{word["word_index"]:03d}'
            rel = f'crops/{name}.png'
            requests.append((word['box'], 3, ROOT/'.work'/bed/iid/rel)); images.append(rel)
            if bed == 'bsb':
                letters = word['letters']
            else:
                # Final alphabetic glyph, allowing punctuation after the slot.
                candidates = [l for l in word['letters'] if any(c.isalpha() for c in l['text'])]
                letters = candidates[-1:] if candidates else word['letters'][-1:]
            for letter in letters:
                rel = f'crops/{name}_g{letter["glyph_index"]:03d}.png'
                requests.append((letter['box'], 8, ROOT/'.work'/bed/iid/rel)); images.append(rel)
            output_geometry.append({**word, 'letters': letters})
        render_crops(m['source_crop'], requests)
        result[iid] = {**item, 'crop': images}
        evidence[iid] = {'approx_box': bool(reason), 'approx_reason': reason,
                         'approx_letter_box': any(l['approx_letter_box'] for w in output_geometry for l in w['letters']),
                         'source_crop_sha256': m['source_crop_sha256'], 'crop_bbox': m['row']['crop_bbox'],
                         'response': m['response'], 'line_id': m['line_id'], 'words': output_geometry,
                         'images': [{'path': str(dest.relative_to(ROOT/'.work'/bed/iid)), 'native_box': b, 'scale': s} for b,s,dest in requests]}
    return result, evidence


def build():
    start = time.monotonic()
    if (ROOT/'MANIFEST.json').exists():
        raise SystemExit('Manifest already exists. Use a fresh output directory; no implicit overwrites.')
    # Deny accidental Python networking, including future changes to this file.
    def deny(*a, **kw):
        raise RuntimeError('E-build network OFF')
    socket.create_connection = deny; socket.socket.connect = deny; socket.getaddrinfo = deny
    (ROOT/'.work').mkdir(exist_ok=True)
    data, keys = load_inputs()
    e2 = {}; e2key = {}
    for bed in data:
        e2[bed], e2key[bed] = e2_items(bed, data[bed], keys[bed])
        print(f'{bed}: E2 geometry built; approximated {sum(r["approx_box"] for r in e2key[bed].values())}/{len(data[bed])}', flush=True)
    packs = []
    for bed, items in data.items():
        field = 'card_id' if bed == 'bsb' else 'item_id'
        name = 'cards.jsonl' if bed == 'bsb' else 'items.jsonl'
        by_id = {r[field]: r for r in items}
        ids = sorted(by_id)
        for arm, factor in ARMS.items():
            order = ids[:]; seed = f'eff:{bed}:{arm}'; random.Random(seed).shuffle(order)
            groups = [order] if arm in ('E1', 'E4') else [order[:(len(order)+1)//2], order[(len(order)+1)//2:]]
            assignments = {}
            for n, group in enumerate(groups, 1):
                reader = f'r{n}'; d = ROOT/'packs'/bed/arm/reader; d.mkdir(parents=True)
                out = []; copied = []
                for iid in group:
                    src = by_id[iid]; m = keys[bed][iid]
                    if arm == 'E2':
                        item = e2[bed][iid]
                        for rel in item['crop']:
                            source = ROOT/'.work'/bed/iid/rel; dest = d/rel; dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(source, dest)
                            copied.append({'path': rel, 'sha256': sha(dest), 'derived_from_sha256': m['source_crop_sha256']})
                    else:
                        rel = f'crops/{iid}.png'; dest = d/rel; dest.parent.mkdir(exist_ok=True)
                        shutil.copyfile(m['source_crop'], dest)
                        item = {**src, 'crop': rel}
                        copied.append({'path': rel, 'sha256': sha(dest), 'source_sha256': m['source_crop_sha256']})
                    out.append(item)
                separators = (',', ':') if arm in ('E3', 'E4') else None
                (d/name).write_text(''.join(json.dumps(i, ensure_ascii=False, separators=separators)+'\n' for i in out))
                (d/'PROTOCOL.md').write_text(protocol(bed, arm))
                files = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(d.rglob('*')) if p.is_file()]
                packs.append({'bed': bed, 'arm': arm, 'reader': reader, 'path': str(d.relative_to(ROOT)),
                              'factor': factor, 'items_file': name, 'items_per_reader': len(group),
                              'item_ids': group, 'files': files, 'copied_crops': copied})
                assignments[reader] = group
            write_json(ROOT/'keys'/bed/f'{arm}.json', {'seed': seed, 'random_algorithm': 'random.Random(seed).shuffle(sorted(original_ids))',
                       'order': order, 'readers': assignments, 'factor': factor,
                       'e2_mapping': e2key[bed] if arm == 'E2' else None})
    summary = {}
    for bed in data:
        approximate = [i for i, r in e2key[bed].items() if r['approx_box']]
        letters = [i for i, r in e2key[bed].items() if r['approx_letter_box']]
        summary[bed] = {'items': len(data[bed]), 'approx_items': len(approximate), 'approx_item_ids': approximate,
                        'approx_share_percent': 100*len(approximate)/len(data[bed]),
                        'approx_letter_items': len(letters), 'approx_letter_item_ids': letters}
    summary['combined'] = {'items': 159, 'approx_items': sum(summary[b]['approx_items'] for b in data),
                           'approx_share_percent': 100*sum(summary[b]['approx_items'] for b in data)/159}
    # Strip large row payloads from the private provenance index.
    write_json(ROOT/'keys/input_mapping.json', {b: {i: {k:v for k,v in m.items() if k != 'row'} for i,m in ms.items()} for b,ms in keys.items()})
    write_json(ROOT/'keys/source_hashes.json', SOURCES)
    write_json(ROOT/'keys/e2_approximation.json', summary)
    write_json(ROOT/'MANIFEST.json', {'schema_version': 1, 'network': False, 'readers_run': False,
               'nice_priority': os.getpriority(os.PRIO_PROCESS, 0), 'arms': ARMS, 'packs': packs,
               'e2_approximation': summary, 'reader_counts': {b: sum(p['bed']==b for p in packs) for b in data},
               'per_item_reads_per_arm': 1, 'elapsed_build_seconds': time.monotonic()-start})
    shutil.rmtree(ROOT/'.work')
    print(json.dumps({'reader_counts': {b: sum(p['bed']==b for p in packs) for b in data}, 'E2': summary, 'seconds': time.monotonic()-start}, indent=2))


if __name__ == '__main__':
    build()
