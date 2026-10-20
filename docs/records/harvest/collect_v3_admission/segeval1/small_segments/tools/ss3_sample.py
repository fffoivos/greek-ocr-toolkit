"""SS3: mechanical sampling and byte verification only; no reading or image review.

Run with -B. All output opens are exclusive; existing artifacts are never edited.
Stratum indices are one-based, matching the brief. Source ties sort lexically.
"""
from pathlib import Path
import collections
import hashlib
import io
import json
import random
import re
import subprocess
import sys
from fractions import Fraction

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ss1_q1 import chars, rotation, output_type, reason_category, read_rows, sha

BASE = Path(__file__).resolve().parents[2]
SMALL = BASE / 'small_segments'
OUT = SMALL / 'q3'
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.line_pipeline_native import reconstructed_crop, digest_bytes

SEED = 20261019


def write_json(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write_jsonl(path, rows):
    with path.open('x') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def allocation(pools, target, floor=0):
    """Constrained proportional Hamilton: bind minima/caps, then largest remainder.

    A source has the floor only at pool>=20. Remaining unfixed quotas are
    proportional to original pool counts. Exact fractions avoid rounding drift.
    """
    pools = dict(sorted(pools.items()))
    if target > sum(pools.values()) or target < 0:
        raise ValueError('target outside pool')
    lower = {s: min(n, floor) if n >= 20 else 0 for s, n in pools.items()}
    if sum(lower.values()) > target:
        raise ValueError('infeasible floors')
    active = {s for s, n in pools.items() if n}
    fixed = {s: 0 for s, n in pools.items() if not n}
    while active:
        remaining = target - sum(fixed.values())
        total = sum(pools[s] for s in active)
        quotas = {s: Fraction(remaining * pools[s], total) for s in active}
        below = {s for s in active if quotas[s] < lower[s]}
        above = {s for s in active if quotas[s] > pools[s]}
        if below:
            for s in below:
                fixed[s] = lower[s]
            active -= below
            continue
        if above:
            for s in above:
                fixed[s] = pools[s]
            active -= above
            continue
        result = {s: int(quotas[s]) for s in active}
        extra = remaining - sum(result.values())
        order = sorted(active, key=lambda s: (-(quotas[s] - result[s]), s))
        for s in order[:extra]:
            result[s] += 1
        fixed.update(result)
        break
    assert sum(fixed.values()) == target
    assert all(lower[s] <= fixed[s] <= pools[s] for s in pools)
    return dict(sorted(fixed.items()))


def seeded_order(rows, index):
    return random.Random(SEED + index).sample(sorted(rows, key=lambda r: r['row_id']), len(rows))


def draw(rows, target, stratum, acquire, failures, index=None, ordered=False, subgroup=None):
    """Failed acquisition advances only in this stratum's frozen permutation."""
    order = rows if ordered else seeded_order(rows, index)
    selected, pending = [], []
    for rank, row in enumerate(order, 1):
        if len(selected) == target:
            break
        try:
            obtained = acquire(row, stratum)
        except (ValueError, FileNotFoundError, OSError) as exc:
            failure = dict(stratum=stratum, subgroup=subgroup, line_id=row['row_id'],
                           seeded_rank=rank, reason=str(exc), replacement_line_id=None)
            failures.append(failure)
            pending.append(failure)
            continue
        for failure in pending:
            failure['replacement_line_id'] = row['row_id']
        pending.clear()
        selected.append(dict(obtained, seeded_rank=rank, subgroup=subgroup))
    if len(selected) != target:
        raise ValueError(f'{stratum}/{subgroup}: exhausted pool ({len(selected)}/{target})')
    return selected


def verified_write(path, png, expected, dimensions):
    if digest_bytes(png) != expected:
        raise ValueError('crop sha256 mismatch; refused before write')
    with Image.open(io.BytesIO(png)) as image:
        if image.size != dimensions:
            raise ValueError('crop dimensions mismatch; refused before write')
        image.verify()
    with path.open('xb') as f:
        f.write(png)
    assert sha(path) == expected


def sample_record(row, stratum, path, how):
    """Only census fields and acquisition enter the sample; no key input."""
    rid = row['row_id']
    geom = rotation(row['width_px'], row['height_px'])
    geom.pop('unrotated_w_over_h')
    record = {k: row.get(k) for k in ['crop_sha256', 'raw_text', 'width_px', 'height_px',
              'xheight_px', 'source', 'wave', 'primary_class', 'script_class', 'verdict_05']}
    return dict(record, line_id=rid, stratum=stratum, crop_path=str(path.resolve()), verified=True,
                how=how, chars=chars(row), output_type=output_type(row['raw_text'], row['is_numeric_output']),
                book=rid.split('--s')[0] if '--s' in rid else re.split(r'-p\d+-l\d+', rid)[0],
                reason_05=reason_category(row['verdict_05'], row['reason_05']),
                inside=chars(row) <= 8 and geom['A'] <= 6, **geom)


def write_sample(path, records):
    write_jsonl(path, records)


def contact_sheets(candidates):
    directory = OUT / 'control_sheets'
    directory.mkdir()
    font_path = Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
    font = ImageFont.truetype(str(font_path), 16)
    labels = []
    for start in range(0, len(candidates), 6):
        sheet = Image.new('RGB', (960, 6 * 330), 'white')
        pen = ImageDraw.Draw(sheet)
        for slot, candidate in enumerate(candidates[start:start + 6]):
            with Image.open(candidate['crop_path']) as crop:
                scale = min(900 / crop.width, 220 / crop.height, 4)
                dims = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale)))
                display = crop.convert('RGB').resize(dims, Image.Resampling.NEAREST)
            x, y = 30, slot * 330 + 8
            sheet.paste(display, (x, y))
            pen.rectangle((x, y, x + dims[0] - 1, y + dims[1] - 1), outline='red', width=1)
            lines = [f"{candidate['index']:02d}  {candidate['line_id']}",
                     'Google: ' + candidate['raw_text'], 'Opus type: ' + candidate['opus_type']]
            # Mechanical pixel-width wrapping only; no text interpretation.
            wrapped = []
            for line in lines:
                segment = ''
                for character in line:
                    if pen.textlength(segment + character, font=font) > 900:
                        wrapped.append(segment)
                        segment = ''
                    segment += character
                wrapped.append(segment)
            for i, line in enumerate(wrapped):
                pen.text((30, slot * 330 + 236 + i * 19), line, fill='black', font=font)
            candidate['sheet'] = str((directory / f'cc_{start // 6 + 1:02d}.png').resolve())
            labels.append(dict(index=candidate['index'], scale=scale, displayed_dimensions=dims,
                               label_lines=len(wrapped), label_fits=len(wrapped) <= 4))
        path = directory / f'cc_{start // 6 + 1:02d}.png'
        with path.open('xb') as f:
            sheet.save(f, format='PNG')
    assert all(r['label_fits'] for r in labels)
    return dict(font_path=str(font_path), font_sha256=sha(font_path), layout=labels,
                visual_review='Not performed: task forbids opening, reading or judging crops.')


def main():
    OUT.mkdir(exist_ok=True)
    if any(OUT.iterdir()):
        raise SystemExit('SS3 FAILED: q3 is not empty; refusing overwrite')
    crop_dir = SMALL / 'crops'
    crop_dir.mkdir(exist_ok=True)
    receipt = dict(status='RUNNING', seed=SEED, stratum_indices='one-based 1..6', inputs=[],
                   pools={}, drawn={}, replacements=[], pages=[], reconstructed_attempts=0)
    def input_file(path):
        path = Path(path)
        receipt['inputs'].append(dict(path=str(path.resolve()), sha256=sha(path)))
        return path
    try:
        tests = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-c', '/dev/null',
                    '-p', 'no:cacheprovider', '--basetemp', str(OUT / 'test_tmp'),
                    str(SMALL / 'tests/test_ss3_sample.py'), '-q'],
                    capture_output=True, text=True)
        with (OUT / 'tests.log').open('x') as f:
            f.write(tests.stdout + tests.stderr)
        receipt['test_result'] = dict(returncode=tests.returncode, output=tests.stdout + tests.stderr)
        if tests.returncode:
            raise ValueError('tests failed')
        opus_all = list(read_rows(input_file(BASE / 'cells_opus/samples.jsonl')))
        opus = [r for r in opus_all if r.get('type')]
        opus_ids = {r['line_id'] for r in opus}
        assert len(opus_ids) == len(opus)
        receipt['opus_file_records'] = len(opus_all)
        receipt['opus_typed_sets'] = dict(collections.Counter(r['set'] for r in opus))
        owners = list(read_rows(input_file(SMALL / 'q1/owner_joined.jsonl')))
        owner_ids = {r['line_id'] for r in owners}
        census = {}
        population_count = 0
        for row in read_rows(input_file(BASE / 'cells/population_cells.jsonl.gz')):
            population_count += 1
            geom = rotation(row['width_px'], row['height_px'])
            typ = output_type(row['raw_text'], row['is_numeric_output'])
            row['_inside'] = chars(row) <= 8 and geom['A'] <= 6
            row['_type'] = typ
            row['_border1'] = typ == 'nonnumeric' and 9 <= chars(row) <= 12 and geom['A'] <= 8
            row['_border2'] = typ == 'nonnumeric' and chars(row) <= 8 and 6 < geom['A'] <= 12
            if row['row_id'] in opus_ids | owner_ids or (
                    typ in {'nonnumeric', 'mixed'} and (row['_inside'] or row['_border1'] or row['_border2'])):
                assert row['row_id'] not in census
                census[row['row_id']] = row
        receipt['census_rows'] = population_count
        assert opus_ids <= census.keys()
        receipt['opus_inside'] = sum(census[rid]['_inside'] for rid in opus_ids)
        receipt['opus_outside'] = len(opus) - receipt['opus_inside']
        # Frozen W1/W2 boxes are read and validated in full before acquisition.
        export = json.loads(input_file(BASE / 'cells/export_receipt.json').read_text())
        input_file(BASE / 'cells/materialise_1b.py')
        input_file(BASE / 'cells/HANDOFF.md')
        input_file(Path(__file__).with_name('ss1_q1.py'))
        input_file(ROOT / 'greekocr/harvest/line_pipeline_native.py')
        bindings = {}
        id_pattern = re.compile(rb'"id"\s*:\s*"([^"\\]+)"')
        for wave in ('W1', 'W2'):
            expected = next(r for r in export['metadata_inputs'] if f'/{wave}_features_' in r['path'])
            path = Path(expected['path'])
            h, count = hashlib.sha256(), 0
            with path.open('rb') as stream:
                for line in stream:
                    h.update(line)
                    count += 1
                    match = id_pattern.search(line)
                    if not match or match[1].decode() not in census:
                        continue
                    row = json.loads(line)
                    rid = row['id']
                    assert rid not in bindings
                    bindings[rid] = {k: row.get(k) for k in ['crop_source_image',
                        'crop_source_sha256', 'crop_bbox', 'crop_sha256']}
                    bindings[rid].update(crop_color_mode=row.get('crop_color_mode', 'L'), metadata_path=str(path))
            assert h.hexdigest() == expected['sha256'] and count == expected['rows']
            receipt['inputs'].append(dict(path=str(path), sha256=h.hexdigest(), rows=count))
        print('Census and frozen metadata verified; indexing existing crops', flush=True)
        existing = collections.defaultdict(list)
        for directory in [BASE / 'crops', BASE / 'cells/samples', BASE / 'cells_opus/crops',
                 Path.home() / 'Projects/ocr-review-sites-20261018/population-images', crop_dir]:
            for path in sorted(directory.rglob('*.png')):
                existing[path.stem].append(path)
        for r in opus:
            path = Path(r['crop_path'])
            if not path.is_absolute():
                path = BASE / 'cells_opus' / path
            if path not in existing[r['line_id']]:
                existing[r['line_id']].insert(0, path)
        pages = {}
        copy_refusals = []
        acquisitions = {}
        def acquire(row, stratum):
            rid, expected = row['row_id'], row['crop_sha256']
            destination = crop_dir / (rid + '.png')
            if destination.exists():
                raise ValueError('destination already exists; new-files-only')
            candidates = existing[rid]
            if stratum == 'opus':
                recorded = next(r['crop_path'] for r in opus if r['line_id'] == rid)
                recorded = Path(recorded)
                if not recorded.is_absolute():
                    recorded = BASE / 'cells_opus' / recorded
                candidates = [recorded, BASE / 'cells_opus/crops' / (rid + '.png')]
            for path in candidates:
                if not path.is_file():
                    continue
                png = path.read_bytes()
                try:
                    verified_write(destination, png, expected, (row['width_px'], row['height_px']))
                except ValueError as exc:
                    copy_refusals.append(dict(line_id=rid, path=str(path), reason=str(exc)))
                    continue
                how = dict(method='copied', from_path=str(path.resolve()), source_sha256=expected)
                acquisitions[rid] = how
                return sample_record(row, stratum, destination, how)
            if stratum == 'opus':
                raise ValueError('typed Opus PNG unavailable or mismatched; copy required')
            binding = bindings.get(rid)
            if not binding:
                raise ValueError('no local W1/W2 feature binding and no verified existing crop')
            if binding['crop_sha256'] != expected:
                raise ValueError('feature/census crop sha256 mismatch')
            page_sha = binding['crop_source_sha256']
            path = Path.home() / 'Projects/collect-v3-data/run/cache/pages' / (str(page_sha) + '.jpg')
            if not path.is_file():
                raise FileNotFoundError('recorded page missing from read-only local cache: ' + str(page_sha))
            if page_sha not in pages:
                actual = sha(path)
                if actual != page_sha:
                    raise ValueError('page sha256 mismatch: ' + str(page_sha))
                pages[page_sha] = dict(path=str(path), expected_sha256=page_sha, actual_sha256=actual,
                                       verified=True, used_for_reconstruction=False)
            if receipt['reconstructed_attempts'] >= 300:
                raise RuntimeError('300 reconstruction ceiling reached')
            receipt['reconstructed_attempts'] += 1
            with Image.open(path) as page:
                image, png = reconstructed_crop(page, binding['crop_bbox'], binding['crop_color_mode'])
            pages[page_sha]['used_for_reconstruction'] = True
            verified_write(destination, png, expected, (row['width_px'], row['height_px']))
            how = dict(method='reconstructed', page_sha256=page_sha, page_path=str(path),
                       bbox=binding['crop_bbox'], color_mode=binding['crop_color_mode'],
                       metadata_path=binding['metadata_path'])
            acquisitions[rid] = how
            return sample_record(row, stratum, destination, how)
        selected, used = [], set()
        def add(records):
            for r in records:
                assert r['line_id'] not in used
                used.add(r['line_id'])
                selected.append(r)
        # All 179 typed records are mandatory, including rows outside D_rec.
        receipt['pools']['opus'] = dict(total=len(opus))
        for row in sorted((census[rid] for rid in opus_ids), key=lambda r: r['row_id']):
            add([acquire(row, 'opus')])
        for index, name, target in [(2, 'inside_by_source', 150), (3, 'mixed', 30),
                                     (4, 'rotated', 25), (5, 'border_outside', 45)]:
            pool = [r for r in census.values() if r['row_id'] not in used and (
                r['_inside'] and r['_type'] == ('mixed' if name == 'mixed' else 'nonnumeric')
                if name != 'border_outside' else r['_border1'] or r['_border2'])]
            if name == 'rotated':
                pool = [r for r in pool if r['height_px'] > r['width_px']]
            by_source = dict(sorted(collections.Counter(r['source'] for r in pool).items()))
            info = dict(total=len(pool), by_source=by_source, excludes='all earlier drawn strata')
            receipt['pools'][name] = info
            order = seeded_order(pool, index)
            if name in {'inside_by_source', 'mixed'}:
                quotas = allocation(by_source, target, floor=4 if name == 'inside_by_source' else 0)
                info['allocation'] = quotas
                for source, quota in quotas.items():
                    add(draw([r for r in order if r['source'] == source], quota, name, acquire,
                             receipt['replacements'], ordered=True, subgroup=source))
            elif name == 'border_outside':
                for flag, count in [('_border1', 25), ('_border2', 20)]:
                    subpool = [r for r in order if r[flag]]
                    info[flag] = len(subpool)
                    add(draw(subpool, count, name, acquire, receipt['replacements'], ordered=True, subgroup=flag))
            else:
                add(draw(order, target, name, acquire, receipt['replacements'], ordered=True))
            print(name, 'drawn', target, 'pool', len(pool), flush=True)
        owner_pool = [census[rid] for rid in sorted(owner_ids) if rid in census and rid not in used
                      and census[rid]['_inside'] and census[rid]['_type'] in {'nonnumeric', 'mixed'}]
        receipt['pools']['owner'] = dict(total=len(owner_pool), excludes='all earlier drawn strata')
        # Mandatory owner census, not a replaceable random quota.
        for row in seeded_order(owner_pool, 6):
            add([acquire(row, 'owner')])
        for r in selected:
            assert sha(r['crop_path']) == r['crop_sha256']
        write_sample(OUT / 'sample.jsonl', selected)
        write_jsonl(OUT / 'key_opus.jsonl', [dict(line_id=r['line_id'], type=r['type'], note=r.get('note'))
                                          for r in sorted(opus, key=lambda r: r['line_id'])])
        # Key material is used only for this explicitly requested lead control view.
        control_rng = random.Random(SEED + 1)
        controls, control_ids, control_quotas = [], set(), {}
        by_id = {r['line_id']: r for r in selected}
        for typ in ['word_or_phrase', 'heading_caps_display', 'punctuation_only', 'noise_non_text',
                    'abbreviation_reference_label', 'multi_line_crop']:
            pool = sorted([r for r in opus if r['type'] == typ], key=lambda r: r['line_id'])
            chosen = control_rng.sample(pool, min(5, len(pool)))
            controls.extend(chosen)
            control_ids.update(r['line_id'] for r in chosen)
            control_quotas[typ] = dict(pool=len(pool), drawn=len(chosen))
        for typ in ['cut_fragment', 'text_covers_part_of_crop']:
            pool = sorted([r for r in opus if r['type'] == typ and r['line_id'] not in control_ids],
                          key=lambda r: r['line_id'])
            chosen = control_rng.sample(pool, min(30 - len(controls), len(pool)))
            controls.extend(chosen)
            control_ids.update(r['line_id'] for r in chosen)
            control_quotas[typ] = dict(pool=len(pool), drawn=len(chosen))
        assert len(controls) == 30 and len(control_ids) == 30
        candidates = [dict(index=i, line_id=r['line_id'], crop_path=by_id[r['line_id']]['crop_path'],
                           crop_sha256=by_id[r['line_id']]['crop_sha256'], verified=True,
                           raw_text=by_id[r['line_id']]['raw_text'], opus_type=r['type'],
                           stratum='opus', status='candidate_pending_lead_pixel_verification')
                      for i, r in enumerate(controls, 1)]
        receipt['control_sheets'] = contact_sheets(candidates)
        write_jsonl(OUT / 'control_candidates.jsonl', candidates)
        receipt.update(status='READY', drawn=dict(collections.Counter(r['stratum'] for r in selected)),
                       total=len(selected), verified=len(selected),
                       copied=sum(r['how']['method'] == 'copied' for r in selected),
                       reconstructed=sum(r['how']['method'] == 'reconstructed' for r in selected),
                       control_type_counts=control_quotas, copy_refusals=copy_refusals,
                       page_cache_writes=0, network_calls=0, crop_visual_review=False,
                       acquisitions=acquisitions)
        assert receipt['reconstructed'] <= receipt['reconstructed_attempts'] <= 300
        receipt['pages'] = list(pages.values())
        receipt['unique_pages_used'] = sum(p['used_for_reconstruction'] for p in pages.values())
        receipt['script_sha256'] = sha(__file__)
        receipt['test_sha256'] = sha(SMALL / 'tests/test_ss3_sample.py')
        receipt['outputs'] = [dict(path=str(p.resolve()), sha256=sha(p))
                              for p in sorted(OUT.rglob('*')) if p.is_file()]
        write_json(OUT / 'SS3_RECEIPT.json', receipt)
        print(json.dumps({k: receipt[k] for k in ['status', 'pools', 'drawn', 'total', 'copied',
                          'reconstructed', 'reconstructed_attempts', 'verified', 'unique_pages_used']}, indent=2))
        print('replacements', len(receipt['replacements']))
    except Exception as exc:
        receipt.update(status='FAILED', reason=str(exc), script_sha256=sha(__file__))
        write_json(OUT / 'SS3_RECEIPT.json', receipt)
        raise


if __name__ == '__main__':
    main()
