"""CAPS1 offline, byte-exact original-crop pack builder; never starts a reader."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import sys
import unicodedata

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PROJECTS = REPO.parent
REFERENCE = PROJECTS / 'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
COLLECTOR = PROJECTS / 'greek-ocr-toolkit-sol-collect'
W1 = PROJECTS / 'collect-v3-data/run/W1'
EXCLUSIONS = COLLECTOR / 'docs/harvest/collect_v3/release_exclusions'
VERDICTS = COLLECTOR / 'docs/harvest/collect_v3/c1/verdicts'
C1 = W1 / 'c1/bsb_poly1850__poly1850'
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad')
PACK_ROOT = SCRATCH / 'sol_packs'
BED = PACK_ROOT / 'caps1'
SHEET = SCRATCH / 'caps1_controls_sheet.png'
SWAP_SHEET = SCRATCH / 'caps1_control_swap.png'

def order_seed(context):
    return SEED + ':order:' + context + (':caps1b' if context == 'c2' else '')
SEED = 'caps1:headings_caps'
FIELDS = {'card_id', 'crop', 'google_text', 'word_scripts'}
PYTHON = ['/usr/bin/arch', '-x86_64', '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', '-B']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def jsonl(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in values))


def io_guard():
    """Reject sockets and all writes outside this task's explicit output paths."""
    allowed = (HERE, BED, PACK_ROOT / 'launchers')

    def writable(path):
        if isinstance(path, int) or os.fsdecode(path) == os.devnull:
            return
        target = Path(os.fsdecode(path)).absolute().resolve()
        if target not in (SHEET, SWAP_SHEET) and not any(target == p or p in target.parents for p in allowed):
            raise PermissionError('CAPS1 write outside task outputs: ' + str(path))

    def audit(event, args):
        if event.startswith('socket.'):
            raise PermissionError('CAPS1 network OFF: ' + event)
        if event == 'open' and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            writable(args[0])
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.truncate'):
            writable(args[0])
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            writable(args[0]); writable(args[1])
    sys.addaudithook(audit)


def release_exclusions():
    manifest = EXCLUSIONS / 'release_exclusions.json'
    config = json.loads(manifest.read_text())
    excluded, bindings = set(), {str(manifest): sha(manifest)}
    classes = {}
    for name, meta in config['classes'].items():
        path = EXCLUSIONS / meta['file']
        assert sha(path) == meta['sha256'], 'release exclusion hash: ' + name
        ids = {s.strip() for s in path.read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')}
        assert len(ids) == meta['n'], 'release exclusion count: ' + name
        classes[name] = ids
        excluded |= ids
        bindings[str(path)] = sha(path)
        if 'spellcheck_subset' in meta:
            sub = meta['spellcheck_subset']
            path = EXCLUSIONS / sub['file']
            assert sha(path) == sub['sha256']
            subset = {s.strip() for s in path.read_text().splitlines() if s.strip() and not s.startswith('#')}
            assert len(subset) == sub['n'] and subset <= ids
            bindings[str(path)] = sha(path)
    assert 'rotated_crop' in classes
    return excluded, classes, bindings


def filter_pool(values, excluded):
    """No source, length, usable_final, or crop_tight_page selection gate."""
    return sorted((r for r in values if r.get('primary_class') == 'headings_caps'
                   and r.get('candidate_usable') is True and r['id'] not in excluded), key=lambda r: r['id'])


def load_inputs():
    excluded, classes, bindings = release_exclusions()
    ckey_path = W1 / 'c1/bsb_poly1850__poly1850_key.json'
    ckey = json.loads(ckey_path.read_text())
    control_ids = {r['line_id'] for r in ckey.values() if isinstance(r, dict) and 'line_id' in r}
    candidates, control_rows, seen = [], {}, set()
    before = Counter()
    removed = Counter()
    for row in rows_stream(W1 / 'features.jsonl'):
        rid = row['id']
        if rid in control_ids:
            assert rid not in control_rows, 'duplicate control feature id'
            control_rows[rid] = row
        if row.get('primary_class') == 'headings_caps' and row.get('candidate_usable') is True:
            assert rid not in seen, 'duplicate pool id'
            seen.add(rid)
            before[row['source']] += 1
            if rid in excluded:
                removed.update(name for name, ids in classes.items() if rid in ids)
            candidates.append(row)
    pool = filter_pool(candidates, excluded)
    assert len(pool) >= 100 and len(control_rows) == len(control_ids)
    for path in (W1 / 'features.jsonl', ckey_path, C1 / 'cards.jsonl',
                 REFERENCE / 'HANDOVER.md', REFERENCE / 'prompts/bsb.md',
                 COLLECTOR / 'collect_v3/storage.py', COLLECTOR / 'collect_v3/common.py'):
        bindings[str(path)] = sha(path)
    return pool, control_rows, ckey, bindings, dict(before), dict(removed)


def rows_stream(path):
    with Path(path).open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def draw(pool):
    return random.Random(SEED).sample(sorted(pool, key=lambda r: r['id']), 100)


def choose_controls(control_rows, ckey, bindings):
    cards = rows(C1 / 'cards.jsonl')
    verdicts = {}
    for path in sorted(VERDICTS.glob('bsb_poly1850__poly1850__*.jsonl')):
        bindings[str(path)] = sha(path)
        for verdict in rows(path):
            assert verdict['card_id'] not in verdicts, 'duplicate reference verdict'
            verdicts[verdict['card_id']] = verdict
    assert len(cards) == len(verdicts) == 100
    good, bad = [], []
    excluded, _, _ = release_exclusions()
    for card in sorted(cards, key=lambda r: r['card_id']):
        cid = card['card_id']
        feature = control_rows[ckey[cid]['line_id']]
        assert feature['primary_class'] != 'headings_caps'
        if feature['id'] in excluded:
            continue
        v = verdicts[cid]
        record = dict(card=card, feature=feature, verdict=v)
        if v['letters'] == v['crop_ok'] == 'y':
            good.append(record)
        elif (v['letters'] == 'n' or v['crop_ok'] == 'n') and v['detail'].strip():
            bad.append(record)
    rng = random.Random(SEED + ':controls')
    positives = rng.sample(good, 7)
    # Continue the original positive-draw RNG before its negative draw/shuffle.
    continuation = random.Random()
    continuation.setstate(rng.getstate())
    while True:
        replacement = continuation.choice(good)
        if replacement not in positives and replacement['verdict']['detail'] == '':
            break
    assert replacement['card']['card_id'] == 'c066'
    selected = positives + rng.sample(bad, 3)
    rng.shuffle(selected)
    slot = next(i for i, c in enumerate(selected) if c['card']['card_id'] == 'c058')
    assert slot == 5
    selected[slot] = replacement
    return selected, dict(good=len(good), clear_bad=len(bad), seed=SEED + ':controls',
        swap=dict(from_card='c058', to_card=replacement['card']['card_id'],
                  selection='continue positive-draw RNG; reject selected cards or nonempty detail'))


def word_scripts(text):
    result = []
    for word in text.split():
        scripts = {next((s for s in ('Greek', 'Latin', 'Cyrillic')
                         if s.upper() in unicodedata.name(c, '')), 'Other') for c in word if c.isalpha()}
        result.append([word, next(iter(scripts)) if len(scripts) == 1 else 'Mixed' if scripts else 'none'])
    return result


def original_crop(row):
    """Use byte-exact T6b originals, existing collector crops, or ensure_crop.

    Only the destination 'crop' field is redirected when ensure_crop runs;
    its source page, source hash, crop box and expected hash stay untouched.
    """
    t6b = HERE.parent / row['source'] / 'crops' / (row['id'] + '.png')
    native = Path(row['crop'])
    if t6b.is_file() and sha(t6b) == row['crop_sha256']:
        source, method = t6b, 'T6b byte-exact original'
    elif native.is_file():
        assert sha(native) == row['crop_sha256'], 'existing collector crop hash mismatch'
        source, method = native, 'existing collector original'
    else:
        sys.path.insert(0, str(COLLECTOR))
        from collect_v3.storage import ensure_crop
        source = HERE / 'cache' / (row['crop_sha256'] + '.png')
        try:
            result = ensure_crop(dict(row, crop=str(source)))
        except ValueError as exc:
            raise ValueError(row['id'] + ': ' + str(exc)) from exc
        assert result == source
        method = 'collector ensure_crop (redirected output only)'
    assert not source.is_symlink() and sha(source) == row['crop_sha256']
    return source, method


def pool_record(row):
    return {k: row[k] for k in ('id', 'source', 'primary_class', 'candidate_usable',
                               'usable_final', 'crop_tight_page', 'crop_sha256')}


def control_sheet(controls, path=SHEET):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 22)
    width = 1900
    tiles = []
    for control in controls:
        card, verdict = control['card'], control['verdict']
        with Image.open(C1 / card['crop']) as image:
            image = image.convert('RGB')
        scale = min(3, (width - 40) / image.width, 180 / image.height)
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.NEAREST)
        probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))

        def wrap(text):
            result, line = [], ''
            for word in text.split(' '):
                trial = (line + ' ' + word).lstrip()
                if line and probe.textlength(trial, font=font) > width - 40:
                    result.append(line); line = word
                else:
                    line = trial
            return result + [line]

        texts = ['Google: ' + card['google_text'],
                 'Reference: letters=' + verdict['letters'] + '  crop_ok=' + verdict['crop_ok'] + '  marks=' + verdict['marks'],
                 'Detail: ' + (verdict['detail'] or '(empty reference detail)'),
                 'Errors: ' + ', '.join(verdict['errors'])]
        lines = [s for text in texts for s in wrap(text)]
        tile = Image.new('RGB', (width, 65 + image.height + len(lines) * 31 + 20), 'white')
        pen = ImageDraw.Draw(tile)
        pen.text((20, 8), ('REPLACEMENT c058 -> c066 | ' if card['card_id'] == 'c066' else '') + control['context'] + '  ' + control['opaque_id'] + '  C1 ' + card['card_id'], font=font, fill='black')
        tile.paste(image, (20, 50))
        for i, line in enumerate(lines):
            pen.text((20, 65 + image.height + i * 31), line, font=font, fill='black')
        pen.line((0, tile.height - 2, width, tile.height - 2), fill='gray', width=2)
        tiles.append(tile)
    sheet = Image.new('RGB', (width, sum(t.height for t in tiles)), 'white')
    top = 0
    for tile in tiles:
        sheet.paste(tile, (0, top)); top += tile.height
    sheet.save(path)
    return dict(path=str(path), sha256=sha(path), size=list(sheet.size), controls=len(controls), lead_pixel_review='9 approved; c066 pending')


def build():
    import PIL
    from PIL import Image, features
    import platform
    pool, control_rows, ckey, bindings, before, removed = load_inputs()
    selected = draw(pool)
    controls, control_inventory = choose_controls(control_rows, ckey, bindings)
    key = dict(bed='caps1', protocol='bsb', seed=SEED, readers={}, items={})
    custody = []
    for index, context in enumerate(('c1', 'c2')):
        records = [(row, None) for row in selected[index * 50:(index + 1) * 50]]
        context_controls = controls[index * 5:(index + 1) * 5]
        records += [(c['feature'], c) for c in context_controls]
        random.Random(order_seed(context)).shuffle(records)
        public = []
        directory = BED / context
        (directory / 'crops').mkdir(parents=True, exist_ok=True)
        for row, control in records:
            iid = 'k' + hashlib.sha256((SEED + ':' + context + ':' + row['id']).encode()).hexdigest()[:10]
            assert iid not in key['items'], 'opaque id collision'
            source, method = original_crop(row)
            if control:
                csource = C1 / control['card']['crop']
                assert sha(csource) == row['crop_sha256'], 'C1 crop differs from collector original'
                bindings[str(csource)] = sha(csource)
                assert control['card']['google_text'] == row['label'], 'C1 text differs from W1 label'
                assert control['card']['word_scripts'] == word_scripts(row['label'])
                control.update(context=context, opaque_id=iid)
            dest = directory / 'crops' / (row['crop_sha256'] + '.png')
            if dest.exists():
                assert sha(dest) == row['crop_sha256']
            else:
                shutil.copyfile(source, dest)
            assert sha(dest) == row['crop_sha256'] and not os.path.samefile(source, dest)
            with Image.open(dest) as image:
                image.load()
                assert image.mode == 'L' and not image.info and image.format == 'PNG'
            pub = dict(card_id=iid, crop='crops/' + dest.name, google_text=row['label'], word_scripts=word_scripts(row['label']))
            assert set(pub) == FIELDS
            public.append(pub)
            meta = dict(control=control is not None, source_id=row['id'], line_id=row['id'],
                        source=row['source'], primary_class=row['primary_class'], crop_sha256=row['crop_sha256'],
                        usable_final=row['usable_final'], crop_tight_page=row['crop_tight_page'])
            if control:
                meta.update(source_public_id=control['card']['card_id'],
                            expected={k: control['verdict'][k] for k in ('letters', 'crop_ok')},
                            reference_verdict=control['verdict'])
            key['items'][iid] = meta
            custody.append(dict(opaque_id=iid, context=context, line_id=row['id'], method=method,
                                source=str(source), destination=str(dest), expected_sha256=row['crop_sha256'],
                                actual_sha256=sha(dest)))
        key['readers'][context] = [r['card_id'] for r in public]
        if context == 'c1':
            baseline = json.loads((HERE / 'control_swap.json').read_text())['c1_original_files']
            assert rows(directory / 'cards.jsonl') == public
            assert {str(p.relative_to(directory)): sha(p) for p in directory.rglob('*') if p.is_file()} == baseline
        else:
            expected_crops = {r['crop'] for r in public}
            previous = json.loads((HERE / 'control_swap.json').read_text())['previous_controls']
            retired = next(c for c in previous if c['source_card']['card_id'] == 'c058')
            retired_crop = sha(C1 / retired['source_card']['crop']) + '.png'
            for stale in (directory / 'crops').iterdir():
                if 'crops/' + stale.name not in expected_crops:
                    assert stale.name == retired_crop and sha(stale) + '.png' == stale.name
                    stale.unlink()
            jsonl(directory / 'cards.jsonl', public)
        jsonl(HERE / 'pack_inventory' / (context + '.cards.jsonl'), public)
    dump(HERE / 'keys/caps1.json', key)
    jsonl(HERE / 'keys/pool.jsonl', [pool_record(r) for r in pool])
    jsonl(HERE / 'keys/draw.jsonl', [pool_record(r) for r in selected])
    dump(HERE / 'keys/control_truth.json', [dict(context=c['context'], opaque_id=c['opaque_id'],
         source_card=c['card'], line_id=c['feature']['id'], primary_class=c['feature']['primary_class'],
         reference_verdict=c['verdict']) for c in controls])
    dump(HERE / 'keys/crop_custody.json', custody)
    prompt = HERE / 'prompts/caps1.md'
    prompt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REFERENCE / 'prompts/bsb.md', prompt)
    assert prompt.read_bytes() == (REFERENCE / 'prompts/bsb.md').read_bytes()
    report = dict(seed=SEED, population_order='id', sampling='random.Random(seed).sample(id_ordered_pool, 100)',
                  candidates_before_exclusions=sum(before.values()), candidates_per_source=before,
                  excluded_by_class=removed, pool=len(pool),
                  pool_per_source=dict(sorted(Counter(r['source'] for r in pool).items())),
                  pool_states=dict(Counter('usable_final' if r['usable_final'] else 'crop_tight_page' for r in pool)),
                  draw=100, draw_per_source=dict(sorted(Counter(r['source'] for r in selected).items())),
                  draw_states=dict(Counter('usable_final' if r['usable_final'] else 'crop_tight_page' for r in selected)),
                  contexts={c: dict(items=55, bed=50, controls=5, order_seed=order_seed(c)) for c in ('c1', 'c2')},
                  control_selection=control_inventory, control_sheet=control_sheet(controls),
                  control_swap_sheet=control_sheet([c for c in controls if c['card']['card_id'] == 'c066'], SWAP_SHEET),
                  prompt_sha256=sha(prompt), crop_methods=dict(Counter(r['method'] for r in custody)),
                  decisions=dict(letters='Sol final', crop_ok='Sol final', marks='pending Opus; ignored for decisions and control scoring'),
                  weekly_used_percent=None, budget_status='not probed: offline preparation; no Codex call made',
                  reader_runs_started=0, sources_read_only=True, network='OFF', inputs=bindings)
    report['materializer_environment'] = dict(python=sys.executable, architecture=platform.machine(),
        pillow=PIL.__version__, zlib=features.version('zlib'),
        note='Collector venv required for byte-exact ensure_crop; handover Python 3.11 remains the scanner interpreter')
    dump(HERE / 'build_receipt.json', report)
    print(json.dumps({k: report[k] for k in ('pool', 'pool_per_source', 'draw_per_source', 'crop_methods', 'prompt_sha256')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', required=True)
    parser.parse_args()
    io_guard()
    build()
