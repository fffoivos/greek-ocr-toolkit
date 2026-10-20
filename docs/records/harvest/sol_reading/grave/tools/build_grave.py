#!/usr/bin/env python3
"""Offline SR-G1. All output writes confined to the two grave directories.

Run with /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B.
No ink synthesis. C1's printed→Google pairs are reference labels, pending lead pixel review.
"""
import collections
import hashlib
import io
import json
import math
import random
import re
import struct
import sys
import unicodedata as U
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
RUN = Path.home()/'Projects/collect-v3-data/run/W1'
C1 = PROJECT/'docs/harvest/collect_v3/c1'
PACK_ROOT = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs')
BED = PACK_ROOT/'grave'
PACK = BED/'r1'
STRATA = ('nlg__poly1900', 'lekythos__poly1900', 'kosmopolis__poly1900')
FIELDS = {'item_id', 'word_image', 'letter_image', 'word_bare', 'anchor_index', 'anchor_base'}
sys.path.insert(0, str(ROOT.parent/'tools'))
import geometry
INPUTS = {}
CACHE = {}
REPLACEMENTS = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind(path):
    path = Path(path).resolve()
    if str(path) not in INPUTS:
        INPUTS[str(path)] = sha(path)
    return path


def read(path):
    path = bind(path)
    if str(path) not in CACHE:
        CACHE[str(path)] = json.loads(path.read_text())
    return CACHE[str(path)]


geometry.read_json = read


def rows(path):
    return [json.loads(s) for s in bind(path).read_text().splitlines() if s.strip()]


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def clusters(text):
    result = []
    for c in U.normalize('NFD', text):
        if U.category(c).startswith('M') and result:
            result[-1] += c
        else:
            result.append(c)
    return result


def letters(text):
    return [c for c in clusters(text) if c[0].isalpha()]


def bare(text):
    return U.normalize('NFC', ''.join(c[0] for c in letters(text)))


def vowel_indices(text):
    return [i for i, c in enumerate(letters(text)) if c[0].lower() in 'αεηιουω']


def positive_pairs(results):
    found = []
    for s in STRATA:
        for error in results[s]['mark_errors']:
            for a, b in re.findall(r'([^\s;→]+)\s*→\s*([^\s;→]+)', error['detail']):
                an, bn = U.normalize('NFD', a), U.normalize('NFD', b)
                diffs = [i for i, (x, y) in enumerate(zip(an, bn)) if x != y]
                if len(an) == len(bn) and len(diffs) == 1 and an[diffs[0]] == '\u0300' and bn[diffs[0]] == '\u0301':
                    anchors = [i for i, c in enumerate(letters(a)) if '\u0300' in c]
                    assert len(anchors) == 1 and anchors[0] in vowel_indices(a)
                    found.append(dict(stratum=s, card_id=error['card_id'], line_id=error['line_id'],
                                      printed=a, google=b, anchor_index=anchors[0], detail=error['detail']))
    return found


def encode(image):
    image = image.convert('RGB')
    image.info.clear()
    out = io.BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()


def save_image(image):
    data = encode(image)
    rel = 'img/'+hashlib.sha256(data).hexdigest()+'.png'
    dest = PACK/rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return rel


def render(line, wb, lb):
    # owner39 E2 formulas, including its integer half-width padding.
    word_box = (max(0, wb[0]-6), 0, min(line.width, wb[2]+6), line.height)
    pad = max(6, (lb[2]-lb[0])//2)
    letter_box = (max(0, lb[0]-pad), 0, min(line.width, lb[2]+pad), line.height)
    w, l = line.crop(word_box), line.crop(letter_box)
    return (w.resize((w.width*3, line.height*3), Image.Resampling.LANCZOS),
            l.resize((l.width*8, line.height*8), Image.Resampling.NEAREST),
            list(word_box), list(letter_box))


def png_clean(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('PNG signature')
    pos = 8
    chunks = []
    while pos < len(data):
        n = struct.unpack('>I', data[pos:pos+4])[0]
        tag = data[pos+4:pos+8]
        if tag not in (b'IHDR', b'IDAT', b'IEND'):
            raise ValueError('PNG ancillary/non-RGB chunk')
        chunks.append(tag)
        pos += n+12
    if pos != len(data) or chunks[0] != b'IHDR' or chunks[-1] != b'IEND':
        raise ValueError('PNG closure')
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        if image.format != 'PNG' or image.mode != 'RGB' or image.info:
            raise ValueError('PNG mode/metadata')


def scan(directory, key):
    """Exact public closure; no estimates, source ids, answers, extra files or links."""
    directory = Path(directory)
    if directory.is_symlink() or {p.name for p in directory.iterdir()} != {'items.jsonl', 'img'}:
        raise ValueError('Reader root closure')
    data = [json.loads(s) for s in (directory/'items.jsonl').read_text().splitlines()]
    if [r.get('item_id') for r in data] != list(key) or len(data) != len(key):
        raise ValueError('Private/public order mismatch')
    expected = {'items.jsonl'}
    for r in data:
        if set(r) != FIELDS or not re.fullmatch(r'k[0-9a-f]{10}', r['item_id']):
            raise ValueError('Fields/opaque id')
        if not isinstance(r['word_bare'], str) or not r['word_bare'] or bare(r['word_bare']) != r['word_bare']:
            raise ValueError('Bare letters')
        i = r['anchor_index']
        if type(i) is not int or not 0 <= i < len(r['word_bare']) or r['anchor_base'] != r['word_bare'][i]:
            raise ValueError('Anchor')
        for field in ('word_image', 'letter_image'):
            rel = r[field]
            if not isinstance(rel, str) or not re.fullmatch(r'img/[0-9a-f]{64}\.png', rel):
                raise ValueError('Image reference')
            expected.add(rel)
    text = (directory/'items.jsonl').read_text()
    if re.search(r'(?i)(truth|verdict|source_id|line_id|stratum|acute|grave|circumflex|unreadable|\bnone\b|(?<!\w)[ca]\d{3}(?!\w))', text):
        raise ValueError('Private field/label/source id leak')
    for m in key.values():
        if m['line_id'] in text or m['stratum'] in text:
            raise ValueError('Source leak')
    files = {}
    for path in sorted(directory.rglob('*')):
        rel = str(path.relative_to(directory))
        if path.is_symlink():
            raise ValueError('Symlink')
        if path.is_dir():
            if rel != 'img':
                raise ValueError('Unexpected directory')
            continue
        if not path.is_file() or path.stat().st_nlink != 1 or rel not in expected:
            raise ValueError('Unexpected/nonregular/linked file')
        files[rel] = sha(path)
        if rel.startswith('img/'):
            if path.name != files[rel]+'.png':
                raise ValueError('Content hash mismatch')
            png_clean(path)
    if set(files) != expected:
        raise ValueError('Missing referenced file')
    return dict(ok=True, items=len(data), files=files)


def review(key, public):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
    for cls, name in (('positive', 'positives'), ('negative', 'negatives'), ('control', 'controls')):
        selected = [(p, key[p['item_id']]) for p in public if key[p['item_id']]['class'] == cls]
        for part, start in enumerate(range(0, len(selected), 18)):
            group = selected[start:start+18]
            sheet = Image.new('RGB', (1600, math.ceil(len(group)/6)*490), 'white')
            draw = ImageDraw.Draw(sheet)
            for i, (p, m) in enumerate(group):
                x, y = (i % 6)*266+5, (i//6)*490
                draw.text((x, y+5), p['item_id'], fill='black', font=font)
                draw.text((x, y+28), 'Expected: '+m['truth_accent'], fill='black', font=font)
                with Image.open(PACK/p['letter_image']) as image:
                    image = image.convert('RGB')
                    image.thumbnail((256, 300), Image.Resampling.NEAREST)
                    sheet.paste(image, (x, y+55))
                with Image.open(PACK/p['word_image']) as image:
                    image = image.convert('RGB')
                    image.thumbnail((256, 120), Image.Resampling.LANCZOS)
                    sheet.paste(image, (x, y+365))
            out = ROOT/'keys/control_review'/(name+('' if part == 0 else f'_{part+1}')+'.png')
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(encode(sheet))


def build():
    for path in (Path(__file__), ROOT/'tools/score_grave.py', ROOT/'tools/test_grave.py',
                 ROOT.parent/'tools/geometry.py', ROOT.parent/'tools/scan_packs.py',
                 ROOT.parent/'tools/common.py', ROOT.parent/'tools/build_packs.py',
                 C1/'efficiency/build.py', C1/'efficiency/build_owner39.py'):
        bind(path)
    results = read(C1/'c1_results.json')
    positives = positive_pairs(results)
    counts = collections.Counter(p['stratum'] for p in positives)
    assert dict(counts) == dict(zip(STRATA, (9, 11, 6))), counts
    cards = {s: {c['card_id']: c for c in rows(RUN/'c1'/s/'cards.jsonl')} for s in STRATA}
    keys = {s: read(RUN/'c1'/f'{s}_key.json') for s in STRATA}
    verdicts = {s: [v for arm in ('a', 'b') for v in rows(C1/'verdicts'/f'{s}__{arm}.jsonl')] for s in STRATA}
    good = {}
    for s in STRATA:
        bycard = collections.defaultdict(list)
        for v in verdicts[s]:
            bycard[v['card_id']].append(v)
        # Both available readers must agree marks=y and letters=y; no conflicting verdict admitted.
        good[s] = {cid for cid, vv in bycard.items() if all(v.get('marks') == v.get('letters') == 'y' for v in vv)}
    wanted = {m['line_id'] for k in keys.values() for m in k.values() if isinstance(m, dict) and 'line_id' in m}
    features = {}
    with bind(RUN/'features.jsonl').open() as f:
        for line in f:
            r = json.loads(line)
            if r['id'] in wanted:
                if r['id'] in features:
                    raise ValueError('Duplicate source feature')
                features[r['id']] = r
    geo_cache = {}

    def exact(candidate):
        s, cid = candidate['stratum'], candidate['card_id']
        card = cards[s][cid]
        line = keys[s][cid]['line_id']
        assert line == candidate['line_id']
        if (s, cid) not in geo_cache:
            r = features[line]
            page = read(RUN/'pages'/f'{r["page_id"]}.json')
            source = bind(RUN/'c1'/s/card['crop'])
            meta = dict(row=r, source_crop=source, response=page['response'],
                        native_size=[page['analysis_page']['width'], page['analysis_page']['height']])
            words, reason = geometry.word_geometry(meta, card['google_text'])
            geo_cache[s, cid] = (words, reason, meta)
        words, reason, meta = geo_cache[s, cid]
        if reason:
            return None, reason
        matches = [w for w in words if w['word_index'] == candidate['word_index']]
        if len(matches) != 1:
            return None, 'word_not_uniquely_aligned'
        word = matches[0]
        if U.normalize('NFC', word['text']) != U.normalize('NFC', candidate['label_token']):
            return None, 'label_word_mismatch'
        letter_boxes = [l for l in word['letters'] if any(c.isalpha() for c in l['text'])]
        if len(letter_boxes) != len(letters(candidate['printed_word'])):
            return None, 'letter_count_mismatch'
        anchor = letter_boxes[candidate['anchor_index']]
        if anchor['approx_letter_box'] or bare(anchor['text']) != candidate['anchor_base']:
            return None, 'no_exact_anchor_symbol'
        return dict(word=word, anchor=anchor, source_crop=str(meta['source_crop']),
                    crop_bbox=meta['row']['crop_bbox'], response=str(meta['response']),
                    native_size=meta['native_size'], approx_word_box=False, approx_letter_box=False), None

    selected = []
    used = {p['line_id'] for p in positives}
    for p in positives:
        s, cid = p['stratum'], p['card_id']
        words = cards[s][cid]['google_text'].split()
        matches = [(i, w) for i, w in enumerate(words, 1) if U.normalize('NFC', ''.join(c for c in clusters(w) if c[0].isalpha())) == U.normalize('NFC', p['google'])]
        if len(matches) != 1:
            raise ValueError('Positive pair not uniquely located: '+str(p))
        i, token = matches[0]
        m = dict(stratum=s, line_id=p['line_id'], card_id=cid, printed_word=p['printed'],
                 class_='positive', truth_accent='grave', anchor_index=p['anchor_index'],
                 anchor_base=bare(p['printed'])[p['anchor_index']], word_index=i, label_token=token,
                 pair=dict(printed=p['printed'], google=p['google']), c1_detail=p['detail'])
        g, reason = exact(m)
        if reason:
            raise ValueError('Mandatory positive lacks exact geometry: '+str((p, reason)))
        m['geometry'] = g
        selected.append(m)

    def candidates(s, kind):
        out = []
        for cid in sorted(good[s]):
            for wi, token in enumerate(cards[s][cid]['google_text'].split(), 1):
                ll = letters(token)
                vv = vowel_indices(token)
                if not vv or not all('GREEK' in U.name(l[0], '') for l in ll):
                    continue
                anchor = None
                if kind == 'negative' and '\u0301' in ll[vv[-1]]:
                    anchor = vv[-1]
                elif kind == 'circumflex':
                    aa = [i for i in vv[-2:] if '\u0342' in ll[i]]
                    if len(aa) == 1:
                        anchor = aa[0]
                elif kind == 'none' and len(ll) >= 4 and not any(c in ll[vv[-1]] for c in '\u0300\u0301\u0342'):
                    anchor = vv[-1]
                if anchor is None:
                    continue
                # Preserve all letter diacritics and remove surrounding punctuation.
                printed = U.normalize('NFC', ''.join(ll))
                out.append(dict(stratum=s, card_id=cid, line_id=keys[s][cid]['line_id'],
                                printed_word=printed, label_token=token, word_index=wi,
                                class_='negative' if kind == 'negative' else 'control',
                                control_kind=None if kind == 'negative' else kind,
                                truth_accent='acute' if kind == 'negative' else kind,
                                anchor_index=anchor, anchor_base=ll[anchor][0],
                                c1_verdicts=[v for v in verdicts[s] if v['card_id'] == cid]))
        rng = random.Random('sol-grave:neg:'+s if kind == 'negative' else 'sol-grave:ctrl:'+kind+':'+s)
        rng.shuffle(out)
        if kind == 'negative':
            out.sort(key=lambda m: len(letters(m['printed_word'])) < 4)
        return out

    def pick(s, kind, n):
        pending = []
        chosen = 0
        for m in candidates(s, kind):
            if m['line_id'] in used:
                continue
            g, reason = exact(m)
            if reason:
                record = dict(stratum=s, class_='negative' if kind == 'negative' else 'control',
                              control_kind=None if kind == 'negative' else kind,
                              rejected=dict(card_id=m['card_id'], line_id=m['line_id'], word=m['printed_word']),
                              reason=reason, replacement=None)
                REPLACEMENTS.append(record)
                pending.append(record)
                continue
            for record in pending:
                record['replacement'] = dict(card_id=m['card_id'], line_id=m['line_id'], word=m['printed_word'])
            pending.clear()
            m['geometry'] = g
            selected.append(m)
            used.add(m['line_id'])
            chosen += 1
            if chosen == n:
                return
        raise ValueError(f'Insufficient exact candidates for {s} {kind}: {chosen}/{n}')

    for s in STRATA:
        pick(s, 'negative', counts[s])
    # One circumflex and one unaccented control per stratum, independently seeded.
    for s in STRATA:
        for kind in ('circumflex', 'none'):
            pick(s, kind, 1)
    random.Random('sol-grave:r1').shuffle(selected)
    public, key = [], {}
    for m in selected:
        m['class'] = m.pop('class_')
        source_identity = json.dumps([m['stratum'], m['card_id'], m['word_index'], m['anchor_index']], separators=(',', ':'))
        iid = 'k'+hashlib.sha256(('sol-grave:id:'+source_identity).encode()).hexdigest()[:10]
        assert iid not in key
        g = m['geometry']
        with Image.open(g['source_crop']) as line:
            line = line.convert('RGB')
            word, letter, wb, lb = render(line, g['word']['box'], g['anchor']['box'])
        g.update(render_word_box=wb, render_letter_box=lb, word_scale=3, letter_scale=8,
                 word_resampling='LANCZOS', letter_resampling='NEAREST', source_crop_sha256=sha(g['source_crop']))
        pub = dict(item_id=iid, word_image=save_image(word), letter_image=save_image(letter),
                   word_bare=bare(m['printed_word']), anchor_index=m['anchor_index'], anchor_base=m['anchor_base'])
        key[iid] = m
        public.append(pub)
    PACK.mkdir(parents=True, exist_ok=True)
    (PACK/'items.jsonl').write_text(''.join(json.dumps(p, ensure_ascii=False)+'\n' for p in public))
    dump(ROOT/'keys/key.json', key)
    review(key, public)
    result = scan(PACK, key)
    if {p.name for p in BED.iterdir()} - {'r1', 'MANIFEST.r1.json'}:
        raise ValueError('Bed closure')
    manifest = BED/'MANIFEST.r1.json'
    dump(manifest, dict(bed='grave', reader='r1', files=result['files']))
    count_table = {s: dict(collections.Counter(m['class'] for m in key.values() if m['stratum'] == s)) for s in STRATA}
    receipt = dict(task='SR-G1', inputs=INPUTS, counts=dict(total=len(key), positive=len(positives), negative=len(positives), control=6, per_stratum=count_table),
                   positive_pairs=positives, replacements=REPLACEMENTS,
                   seeds=dict(order='sol-grave:r1', negative='sol-grave:neg:<stratum>', control='sol-grave:ctrl:<kind>:<stratum>'),
                   sampling_policy='Stable card/word enumeration; shuffle; >=4-letter negative tier first; one selected word per line. Both available C1 readers must have letters=y and marks=y. Controls: one per kind per stratum. No crop_ok restriction.',
                   geometry_policy='E2 response transform/token containment/exact machine-text alignment and exact symbol boxes; no estimated boxes accepted. Mandatory positives cannot be silently substituted.',
                   rendering_policy='owner39 E2: word x ±6, full crop height, 3x LANCZOS; anchor x ±max(6,width//2), full crop height, 8x NEAREST. E2 mapped boxes include existing local_box padding.',
                   review_status='Contact sheets generated for lead pixel check; no new ink adjudication claimed.',
                   pack=str(PACK), key_sha256=sha(ROOT/'keys/key.json'), manifest_sha256=sha(manifest), closure=result)
    dump(ROOT/'BUILD_RECEIPT.json', receipt)
    print(json.dumps(dict(counts=receipt['counts'], replacements=len(REPLACEMENTS), manifest_sha256=sha(manifest)), indent=2))


if __name__ == '__main__':
    build()
