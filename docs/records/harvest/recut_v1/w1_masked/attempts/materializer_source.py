"""T6b offline W1 qualification: frozen masking, component audit, skip guard.

All writes are confined to this directory. W1 is read-only, including caches.
The frozen T6a2 matcher is executed from its AST without its F2 import side effects.
"""
from __future__ import annotations

import os
import sys
sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[name] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import argparse
import ast
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import random
import shutil
import subprocess
import time
import unicodedata

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
W1_ROOT = Path.home() / 'Projects/collect-v3-data/run'
W1 = W1_ROOT / 'W1'
FUNNEL = ROOT.parent / 'greek-ocr-toolkit-sol-funnel-gr/docs/harvest'
REFERENCE = FUNNEL / 'sample_v1/gr/reference/greekocr/labelfix/geometry/ownership.py'
SHARED_AUDIT = ROOT.parent / 'greek-ocr-toolkit-sol-l1emask/docs/harvest/recut_v1/masking/audit_dev.py'
PARAMS = BASE.parent / 'masking/params.json'
PROBE = BASE.parent / 'masking/probe.py'
INSTRUCTIONS = FUNNEL / 'blind_checks_v1/v2/LABEL_CHECK_v2.md'
SOURCES = ('gazette_modern', 'kosmopolis', 'lekythos')
EXPECTED = {'gazette_modern': (16691, 1392, 767, 669, 15201, 1829),
            'kosmopolis': (3864, 676, 0, 0, 3188, 70),
            'lekythos': (9113, 1124, 0, 0, 7989, 226)}
PARAM_SHA = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'
LIB_SHA = 'f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5'
START_HEAD = '45e674d28f8718555226f9fff189d985758c0f9c'
AMENDED_RULE = 'own-ink loss stated per source and judged blind'
AMENDMENT_REASON = 'Large paired CER gains, and the crop_ok-y subset improves with no source worse.'
DEV_DAMAGE = {'gazette_modern': 0, 'kosmopolis': 11, 'lekythos': 20}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write_rows(path, values):
    with Path(path).open('w') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')


def io_guard():
    """Deny network and writes outside this output, before importing the detector."""
    def writable(path):
        if isinstance(path, int) or os.fsdecode(path) == os.devnull:
            return
        if not Path(os.fsdecode(path)).absolute().resolve().is_relative_to(BASE):
            raise PermissionError('T6b write outside output: ' + str(path))
    def audit(event, args):
        if event.startswith('socket.'):
            raise PermissionError('T6b network OFF: ' + event)
        if event == 'open' and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            writable(args[0])
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.truncate'):
            writable(args[0])
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            writable(args[0]); writable(args[1])
    sys.addaudithook(audit)
    os.environ['TMPDIR'] = str(BASE / 'tmp')
    os.environ['XDG_CACHE_HOME'] = str(BASE / 'tmp')


def extract(path, names, namespace):
    tree = ast.parse(Path(path).read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in functions} != set(names):
        raise RuntimeError('missing frozen functions: ' + str(path))
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def frozen():
    p = json.loads(PARAMS.read_text())
    actual = hashlib.sha256(json.dumps(p['params'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert actual == p['params_sha256'] == PARAM_SHA
    for name, digest in p['source_hashes'].items():
        assert sha(ROOT / name) == digest, 'frozen source changed: ' + name
    assert sha(ROOT / 'greekocr/glyphs/foreign_ink.py') == LIB_SHA
    original = subprocess.check_output(['git', 'show', 'eacb5c39:docs/harvest/recut_v1/masking/probe.py'], cwd=ROOT)
    assert hashlib.sha256(original).hexdigest() == sha(PROBE), 'matcher changed'
    return dict(params_sha256=actual, library_sha256=LIB_SHA, source_hashes=p['source_hashes'],
                params_file_sha256=sha(PARAMS), matcher_sha256=sha(PROBE),
                ownership_sha256=sha(REFERENCE), component_audit_source_sha256=sha(SHARED_AUDIT),
                component_audit_copy_sha256=sha(BASE / 'component_audit.py'), runner_sha256=sha(__file__))


def rotated(row):
    x0, y0, x1, y1 = row['crop_bbox']
    return y1-y0 > x1-x0 and sum(c.isalpha() for c in row['label']) >= 4


def caps_heading(row):
    return bool((set(row.get('tags', [])) | set(row.get('line_tags', []))) & {'caps', 'heading'})


def guard_measure(original_ink, changed_pixels):
    """Original-crop dark-ink fraction, independent of inferred component owners."""
    total = int(original_ink.sum())
    changed = int((original_ink & changed_pixels).sum())
    return dict(original_dark_ink_pixels=total, would_be_dark_ink_pixels_changed=changed,
                own_ink_masked_fraction=changed/total if total else 0., original_dark_ink_empty=total == 0)


def population():
    if not (W1_ROOT / 'collector.exit').exists() or json.loads((W1 / 'state.json').read_text())['status'] != 'completed_selected_sources':
        raise RuntimeError('W1 precondition failed; stop')
    source_rows = rows(W1 / 'crop_tight_page.jsonl')
    eligible, excluded, summary = [], [], {}
    for source in SOURCES:
        candidates = [r for r in source_rows if r['source'] == source and r.get('candidate_usable') is True and r.get('crop_tight_page') is True]
        merged = [r for r in candidates if r.get('screen_merged') is True]
        rotation = [r for r in candidates if rotated(r)]
        overlap = sum(r.get('screen_merged') is True for r in rotation)
        left = [r for r in candidates if not r.get('screen_merged') and not rotated(r)]
        caps = [r for r in left if caps_heading(r)]
        assert (len(candidates), len(merged), len(rotation), overlap, len(left), len(caps)) == EXPECTED[source]
        pool = [r for r in left if not caps_heading(r)]
        assert all(r['usable_final'] is False and r['label'] == r['label_after_conventions'] for r in candidates)
        summary[source] = dict(candidate_rows=len(candidates), screen_merged_removed=len(merged),
            rotated_crop_total=len(rotation), rotated_crop_already_screen_merged=overlap,
            rotated_crop_additional_removed=len(rotation)-overlap, after_merged_rotation=len(left),
            caps_heading_excluded=len(caps), eligible_rows=len(pool))
        eligible.extend(pool)
        for r in candidates:
            reason = 'screen_merged' if r.get('screen_merged') else 'rotated_crop' if rotated(r) else 'caps_heading' if caps_heading(r) else None
            if reason:
                excluded.append(dict(id=r['id'], source=source, reason=reason,
                    screen_merged=bool(r.get('screen_merged')), rotated_crop=rotated(r),
                    caps_heading=caps_heading(r), crop_sha256=r['crop_sha256']))
    return eligible, excluded, summary


def prep_owners(analysis, own):
    """Same joined detector components as T6a2's G1b cache, without writing W1."""
    pixels = analysis.segmentation.pixels
    metadata = {r['id']: r for r in analysis.rows}
    prepared, invalid = {}, []
    for r in analysis.delivery:
        record = {k: v for k, v in r.items() if k != 'pieces'}
        ids = sorted({int(k) for i in metadata[r['row_id']]['line_indices']
                      for k in analysis.segmentation.lines[i].component_ids})
        cc = pixels.components[__import__('numpy').isin(pixels.components[:, 5], ids)]
        record.update(component_ids=ids, owned_box=(
            [int(cc[:, 0].min()), int(cc[:, 1].min()), int(cc[:, 2].max()), int(cc[:, 3].max())]
            if len(cc) else [r['x0'], int(min(r['top'])), r['x1'], int(max(r['bottom']))]))
        try:
            prepared[r['row_id']] = own['prepare_row'](record, pixels.ink, pixels.labels)
        except ValueError as exc:
            # Match W1's existing detector adapter. A selected row must still
            # have its saved measured owner below, or the prerequisite fails.
            invalid.append(dict(row_id=r['row_id'], reason=str(exc)))
    return prepared, invalid


def worker(index):
    io_guard()
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(BASE))
    import numpy as np
    import cv2
    cv2.setNumThreads(0)
    from PIL import Image
    from greekocr.pages import process_page, PageOptions
    from greekocr.glyphs.foreign_ink import PARAMETERS, prepare_mask_page, mask_foreign_ink
    from greekocr.glyphs.recut import LineFit
    from greekocr.harvest.page_reads import _response_geometry
    from component_audit import component_audit
    binding = frozen()
    assert PARAMETERS == json.loads(PARAMS.read_text())['params']
    matching = extract(PROBE, ('match', 'runtime_fit'), dict(np=np, LineFit=LineFit))
    own = extract(REFERENCE, ('prepare_row', 'box_hits', 'ownership'), dict(np=np,
        CURVES=('baseline', 'meanline', 'font_top', 'font_bottom', 'accent_top', 'accent_bottom', 'top', 'bottom')))
    page = json.loads((BASE / 'selection.json').read_text())[index]
    source, page_id = page['source'], page['page_id']
    started = time.monotonic()
    metadata_path = W1 / 'pages' / (page_id + '.json')
    metadata = json.loads(metadata_path.read_text())
    raster, response = Path(metadata['image']), Path(metadata['response'])
    assert raster.resolve().is_relative_to(W1_ROOT) and response.resolve().is_relative_to(W1_ROOT)
    assert sha(raster) == metadata['image_sha256'] == page['raster_sha256']
    assert sha(response) == metadata['response_sha256']
    with Image.open(raster) as image:
        native = image.copy()
    assert native.mode == 'L', 'W1 crop-source must be native L, no conversion'
    raw = json.loads(response.read_text())
    google = [r for r in _response_geometry('docai', raw, native.size)['lines'] if r['source'] == 'lines']
    before = time.monotonic()
    analysis = process_page(native, options=PageOptions(join_lines=True, granularity='rows'))
    detector_seconds = time.monotonic()-before
    lines = [line for line in analysis.segmentation.lines if line.discounted is None]
    fits = [matching['runtime_fit'](line) for line in lines]
    owners, invalid_audit_rows = prep_owners(analysis, own)
    prepared = prepare_mask_page(native)
    curves = dict(runtime_lines=[dict(x0=l.x0, x1=l.x1, xheight=l.xheight,
        baseline=l.baseline.tolist(), meanline=l.meanline.tolist()) for l in lines],
        audit_rows=[{k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items() if not k.startswith('_')} for r in owners.values()])
    curve_path = BASE / source / 'curves' / (page_id + '.json.gz')
    curve_path.write_bytes(gzip.compress(json.dumps(curves, allow_nan=False, separators=(',', ':')).encode(), mtime=0))
    records, audits = [], []
    for r in page['rows']:
        box = r['crop_bbox']; x0, y0, x1, y1 = box
        assert np.allclose(google[r['docai_line_index']]['bbox'], r['bbox'], atol=1e-8), 'Google box custody'
        stored = Path(r['crop'])
        assert stored.resolve().is_relative_to(W1_ROOT)
        original = native.crop(tuple(box)); a = np.asarray(original)
        buffer = io.BytesIO(); original.save(buffer, format='PNG', compress_level=3)
        original_bytes = buffer.getvalue()
        assert hashlib.sha256(original_bytes).hexdigest() == r['crop_sha256'], 'crop encoding custody'
        stored_crop_available = stored.exists()
        if stored_crop_available:
            assert stored.read_bytes() == original_bytes, 'retained crop custody'
        idx = matching['match'](box, fits)
        if idx is None:
            result_image = original
            would_mask = np.zeros(a.shape, dtype=bool)
            proposal = dict(crop_box=box, masked_pixel_count=0, proposed_masked_pixel_count=0,
                masked_component_count=0, ring_median=None, ring_spread=None, fills=[], empty_ring_abstentions=0,
                mask_sha256=hashlib.sha256(would_mask.tobytes()).hexdigest(), changed=False, native_changed_pixels=0)
        else:
            result = mask_foreign_ink(prepared, lines[idx], lines, box)
            result_image, proposal = result.image, result.record
            would_mask = a != np.asarray(result.image)
        # Independent G1b owner anchored to the original Google box, never to the matched mask curve.
        owner_id = r['measured_row_id']
        assert owner_id in owners, 'own-ink audit prerequisite: missing measured owner'
        counts, _ = component_audit(owners, analysis.segmentation.pixels.labels, box,
                                    would_mask, owner_id, own['box_hits'])
        assert counts['own_pixels'] is not None, 'own-ink audit prerequisite: unknown owner'
        assert counts['own_pixels'] or counts['own_component_pixels_lost'] == 0
        guard_counts = guard_measure(prepared.ink[y0:y1, x0:x1], would_mask)
        fraction = guard_counts['own_ink_masked_fraction']
        guard = fraction > .30
        applied_mask = np.zeros_like(would_mask) if guard else would_mask
        actual, _ = component_audit(owners, analysis.segmentation.pixels.labels, box,
                                   applied_mask, owner_id, own['box_hits'])
        dest = BASE / source / 'crops' / (r['id'] + '.png')
        if guard or not proposal['changed']:
            dest.write_bytes(original_bytes)
        else:
            result_image.save(dest, format='PNG', compress_level=3)
        masked_sha = sha(dest)
        if guard:
            assert masked_sha == r['crop_sha256']
            # Small native witness, full original plus exact would-change pixels in red.
            if page['guard_witness_budget']:
                overlay = np.asarray(original.convert('RGB')).copy(); overlay[would_mask] = (255, 0, 0)
                Image.fromarray(overlay).save(BASE / source / 'guard_witnesses' / (r['id'] + '.png'))
        audit = dict(id=r['id'], source=source, page_id=page_id, owner_row_id=owner_id,
            runtime_index=idx, own_ink_masked_fraction=fraction, wrong_line_risk=guard,
            guard_measurement=guard_counts,
            assigned_own_ink_masked_fraction=counts['own_component_pixels_lost']/counts['own_pixels'] if counts['own_pixels'] else None,
            own_ink_empty=counts['own_pixels'] == 0,
            would_be=counts, applied=actual, audit_status='measured',
            original_crop_sha256=r['crop_sha256'], masked_crop_sha256=masked_sha)
        audits.append(audit)
        applied = dict(proposal)
        if guard:
            applied.update(masked_pixel_count=0, masked_component_count=0, ring_median=None,
                ring_spread=None, fills=[], empty_ring_abstentions=0, changed=False,
                native_changed_pixels=0, mask_sha256=hashlib.sha256(applied_mask.tobytes()).hexdigest())
        record = dict(applied, id=r['id'], row_id=r['id'], source=source, page_id=page_id,
            original_crop_sha256=r['crop_sha256'], masked_crop_sha256=masked_sha,
            original_crop=str(stored), masked_crop=str(dest.relative_to(BASE)),
            stored_crop_available=stored_crop_available, crop_source_image=str(raster),
            params_sha256=PARAM_SHA, library_sha256=LIB_SHA, runtime_index=idx,
            matched=idx is not None, wrong_line_risk=guard, own_ink_masked_fraction=fraction,
            guard_measurement=guard_counts,
            assigned_own_ink_masked_fraction=counts['own_component_pixels_lost']/counts['own_pixels'] if counts['own_pixels'] else None,
            own_ink_empty=counts['own_pixels'] == 0,
            mask_applied=idx is not None and not guard, output_kind='guarded_original' if guard else 'unmatched_original' if idx is None else 'masked',
            component_audit=actual, would_be=proposal, would_be_component_audit=counts,
            google_text=r['label'], crop_bbox=box, screen_merged=False, rotated_crop=False,
            admitted=False, usable_final=False)
        records.append(record)
        if stored_crop_available:
            assert sha(stored) == r['crop_sha256']
    directory = BASE / source / 'pages'
    write_rows(directory / (page_id + '.jsonl'), records)
    write_rows(directory / (page_id + '_audit.jsonl'), audits)
    provenance = dict(page_id=page_id, source=source, rows=len(records), raster=str(raster),
        raster_sha256=sha(raster), response=str(response), response_sha256=sha(response),
        metadata_sha256=sha(metadata_path), curve_path=str(curve_path.relative_to(BASE)), curves_sha256=sha(curve_path),
        audit_ink_sha256=hashlib.sha256(analysis.segmentation.pixels.ink.tobytes()).hexdigest(),
        audit_labels_sha256=hashlib.sha256(analysis.segmentation.pixels.labels.tobytes()).hexdigest(),
        invalid_audit_rows=invalid_audit_rows,
        detector_seconds=detector_seconds, seconds=time.monotonic()-started, frozen=binding)
    write_json(directory / (page_id + '_provenance.json'), provenance)
    print(json.dumps(dict(page_id=page_id, rows=len(records), changed=sum(r['changed'] for r in records),
        guarded=sum(r['wrong_line_risk'] for r in records), seconds=round(provenance['seconds'], 2))), flush=True)


def word_scripts(text):
    result = []
    for word in text.split():
        scripts = {next((s for s in ('Greek', 'Latin', 'Cyrillic') if s.upper() in unicodedata.name(c, '')), 'Other')
                   for c in word if c.isalpha()}
        result.append([word, next(iter(scripts)) if len(scripts) == 1 else 'Mixed' if scripts else 'none'])
    return result


def draw_cards(source, records):
    pool = sorted(records, key=lambda r: r['id'])
    picked = random.Random('t6b:' + source).sample(pool, 100)
    directory = BASE / 'cards' / source
    (directory / 'crops').mkdir(parents=True, exist_ok=True)
    cards, key = [], dict(_seed='t6b:' + source, _pool=len(pool), _draw='uniform without replacement over line-id ordered pool; no length sorting', _admitted=False)
    for i, row in enumerate(picked, 1):
        cid = f'c{i:03d}'; dest = directory / 'crops' / (cid + '.png')
        shutil.copyfile(BASE / row['masked_crop'], dest)
        cards.append(dict(card_id=cid, crop='crops/' + dest.name, google_text=row['google_text'], word_scripts=word_scripts(row['google_text'])))
        key[cid] = dict(line_id=row['id'], page_id=row['page_id'], original_crop_sha256=row['original_crop_sha256'],
            masked_crop_sha256=row['masked_crop_sha256'], card_crop_sha256=sha(dest),
            wrong_line_risk=row['wrong_line_risk'], own_ink_masked_fraction=row['own_ink_masked_fraction'],
            output_kind=row['output_kind'], mask_applied=row['mask_applied'], changed=row['changed'], screen_merged=False,
            params_sha256=PARAM_SHA)
    write_rows(directory / 'cards.jsonl', cards)
    key_path = BASE / 'cards' / (source + '_key.json'); write_json(key_path, key)
    return dict(cards=str((directory / 'cards.jsonl').relative_to(BASE)), cards_sha256=sha(directory / 'cards.jsonl'),
        key=str(key_path.relative_to(BASE)), key_sha256=sha(key_path), count=len(cards),
        guarded_cards=sum(key[c['card_id']]['wrong_line_risk'] for c in cards),
        crops=[dict(path=str((directory / c['crop']).relative_to(BASE)), sha256=sha(directory / c['crop'])) for c in cards])


def contact_sheet(source, records):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    chosen = sorted((r for r in records if r['wrong_line_risk']), key=lambda r: r['id'])[:20]
    font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 14)
    sheets = []
    for offset in range(0, len(chosen), 5):
        sheet = Image.new('RGB', (1800, 5*220), '#e5e5e5'); draw = ImageDraw.Draw(sheet)
        for j, row in enumerate(chosen[offset:offset+5]):
            y = j*220
            draw.text((8, y+2), row['id'] + f"  own ink would change {row['own_ink_masked_fraction']:.3%}", font=font, fill='black')
            # Label wraps without rewriting; the JSONL retains the exact original string.
            label = row['google_text']
            for line_index in range(0, min(len(label), 220), 110):
                draw.text((8, y+22+(line_index//110)*18), label[line_index:line_index+110], font=font, fill='black')
            for path, top in ((BASE / row['masked_crop'], y+65),
                              (BASE / source / 'guard_witnesses' / (row['id'] + '.png'), y+140)):
                with Image.open(path) as image:
                    image = image.convert('RGB'); scale = min(2, 1750/image.width, 70/image.height)
                    image = image.resize((max(1, round(image.width*scale)), max(1, round(image.height*scale))), Image.Resampling.NEAREST)
                    sheet.paste(image, (20, top))
        path = BASE / source / f'guarded_contact_{offset//5+1:02d}.png'; sheet.save(path)
        sheets.append(dict(path=str(path.relative_to(BASE)), sha256=sha(path), rows=[r['id'] for r in chosen[offset:offset+5]]))
    return dict(rows_shown=len(chosen), order='line_id', panels='original above; exact would-be changed pixels in red below; output remains original', sheets=sheets)


def finish():
    import numpy as np
    binding = frozen(); selection = json.loads((BASE / 'selection.json').read_text())
    counts = json.loads((BASE / 'population.json').read_text())
    shutil.copyfile(INSTRUCTIONS, BASE / 'cards/LABEL_CHECK_v2.md')
    assert sha(INSTRUCTIONS) == sha(BASE / 'cards/LABEL_CHECK_v2.md')
    receipts = {}
    for source in SOURCES:
        pages = [p for p in selection if p['source'] == source]
        records, audits, provenance = [], [], []
        for p in pages:
            stem = BASE / source / 'pages' / p['page_id']
            records.extend(rows(stem.with_suffix('.jsonl')))
            audits.extend(rows(stem.parent / (stem.name + '_audit.jsonl')))
            provenance.append(json.loads((stem.parent / (stem.name + '_provenance.json')).read_text()))
        assert len(records) == len(audits) == counts[source]['eligible_rows']
        assert len({r['id'] for r in records}) == len(records)
        write_rows(BASE / source / 'records.jsonl', records)
        write_rows(BASE / source / 'component_audit.jsonl', audits)
        write_rows(BASE / source / 'provenance.jsonl', provenance)
        guard = [r for r in records if r['wrong_line_risk']]
        applied = [r for r in records if r['mask_applied']]
        fills = [f for r in applied for f in r['fills'] if f['fill'] is not None]
        def quantile(values):
            return dict(zip(('min', 'p50', 'p90', 'max'), np.quantile(values, (0, .5, .9, 1)).items())) if values else None
        card = draw_cards(source, records)
        receipt = dict(schema='t6b-w1-masked-qualification-1', source=source, status='qualification_pending_blind_check',
            admitted=False, arm_if_pass='wave-1d only', precondition=dict(collector_exit=(W1_ROOT / 'collector.exit').read_text().strip(), status='completed_selected_sources'),
            population=counts[source], rows_processed=len(records), rows_masked=len(applied),
            rows_guarded=len(guard), guarded_pages=len({r['page_id'] for r in guard}),
            guarded_page_ids=sorted({r['page_id'] for r in guard}), rows_unmatched=sum(not r['matched'] for r in records),
            rows_excluded_caps_heading=counts[source]['caps_heading_excluded'],
            changed_crops=sum(r['changed'] for r in records), share_crops_changed=sum(r['changed'] for r in records)/len(records),
            changed_denominator='all eligible outputs, including byte-exact guarded and unmatched originals',
            masked_pixel_count=sum(r['masked_pixel_count'] for r in records),
            masked_component_count=sum(r['masked_component_count'] for r in records),
            fill_statistics=dict(components=len(fills), ring_median=quantile([float(np.mean(f['ring_median'])) for f in fills]),
                ring_spread_p90_p10=quantile([float(np.mean(f['ring_spread'])) for f in fills]),
                ring_pixels=quantile([f['ring_pixels'] for f in fills]),
                empty_ring_abstentions=sum(r['empty_ring_abstentions'] for r in records)),
            own_ink_audit=dict(rows=len(audits), unknown=0, own_pixels=sum(a['applied']['own_pixels'] for a in audits),
                zero_assigned_own_ink_rows=sum(a['own_ink_empty'] for a in audits),
                empty_assigned_own_ink='component audit remains 0 pixels/0 loss; assigned-own fraction is null; original dark-ink guard remains computable',
                own_pixels_changed=sum(a['applied']['own_component_pixels_lost'] for a in audits),
                own_components_touched=sum(a['applied']['own_components_touched'] for a in audits),
                guard_numerator='actual native pixels the frozen mask would change in original crop dark ink',
                guard_denominator='original native page binarise foreground clipped to original crop, before masking; independent of detector component ownership',
                method='T6a2/T6d component_audit, joined G1b assigned components and original OWN.prepare_row/box_hits',
                guard='strictly greater than 0.30; byte-exact original; remains in card population',
                midpoint_matching_variant_applied=False),
            dev_own_ink_damage_pixels=DEV_DAMAGE[source], dev_damage_scope='T6a2 dev crop_ok-y cached own-component pixels; judged blind here',
            amended_rule=AMENDED_RULE, amendment_reason=AMENDMENT_REASON,
            cards=card, checker_instructions=dict(path='cards/LABEL_CHECK_v2.md', sha256=sha(INSTRUCTIONS), unchanged=True),
            contact_sheet=contact_sheet(source, records),
            gate=dict(applied_here=False, crop_ok_y_at_least=90, letters_y_at_least=90, cards=100,
                statistic='point estimate on same 100 cards; guard originals included', own_ink_clipping='crop_clipped',
                gazette_also_W2_probe=source == 'gazette_modern', C1_original_gazette=dict(letters=86, crop_ok=70) if source == 'gazette_modern' else None),
            merged_screen_recall=dict(status='pending T6b blind verdicts', C1_gazette_caught=4, C1_gazette_merged=7,
                C1_gazette_recall=4/7, note='All screen_merged rows excluded before draw. T6b cards estimate residual merged_two_lines frequency, not unconditional recall without excluded-row truth.'),
            records_sha256=sha(BASE / source / 'records.jsonl'), component_audit_sha256=sha(BASE / source / 'component_audit.jsonl'),
            provenance_sha256=sha(BASE / source / 'provenance.jsonl'), frozen=binding,
            network='OFF', W1_read_only=True, W1_locks_taken=False, created_utc=utc())
        write_json(BASE / (source + '_receipt.json'), receipt); receipts[source] = receipt
    total = sum(r['rows_processed'] for r in receipts.values()); changed = sum(r['changed_crops'] for r in receipts.values())
    write_json(BASE / 'summary.json', dict(status='qualification_pending_blind_check', admitted=False,
        sources={s: {k:r[k] for k in ('rows_processed','rows_masked','rows_guarded','guarded_pages','rows_unmatched','changed_crops','share_crops_changed')} for s,r in receipts.items()},
        rows_processed=total, changed_crops=changed, share_crops_changed=changed/total,
        params_sha256=PARAM_SHA, IA_greek_latin='hold-tagged, masking off, not processed', network='OFF'))
    print(json.dumps(json.loads((BASE / 'summary.json').read_text()), indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--worker', type=int); parser.add_argument('--finish', action='store_true')
    parser.add_argument('--restart-incomplete', action='store_true', help='explicitly rebuild an incomplete attempt, preserving its binding')
    args = parser.parse_args()
    if args.worker is not None:
        worker(args.worker); return
    if args.finish:
        io_guard(); finish(); return
    start = time.monotonic(); binding = frozen()
    eligible, excluded, summary = population()
    if (BASE / 'selection.json').exists():
        if not args.restart_incomplete or (BASE / 'execution.json').exists():
            raise RuntimeError('existing selection: do not overwrite or silently resume')
        attempts = BASE / 'attempts'; attempts.mkdir(exist_ok=True)
        attempt = len(list(attempts.glob('binding_*.json'))) + 1
        shutil.copyfile(BASE / 'binding.json', attempts / f'binding_{attempt}.json')
        write_json(attempts / f'restart_{attempt}.json', dict(utc=utc(), reason='input adapter correction; all pages rebuilt; no masking/matching changes',
            previous_runner_sha256=json.loads((BASE / 'binding.json').read_text())['frozen']['runner_sha256'], runner_sha256=sha(__file__)))
    for source in SOURCES:
        for sub in ('crops', 'pages', 'curves', 'guard_witnesses'):
            (BASE / source / sub).mkdir(parents=True, exist_ok=True)
    for sub in ('logs', 'tmp', 'cards'):
        (BASE / sub).mkdir(exist_ok=True)
    io_guard()
    groups = defaultdict(list)
    for row in eligible: groups[row['page_id']].append(row)
    selection = []
    for page_id, rr in sorted(groups.items()):
        first = rr[0]
        assert len({(r['crop_source_image'], r['crop_source_sha256']) for r in rr}) == 1
        selection.append(dict(page_id=page_id, source=first['source'], raster_sha256=first['crop_source_sha256'],
            guard_witness_budget=True, rows=[{k:r[k] for k in ('id','page_id','source','crop','crop_sha256','crop_bbox','bbox','docai_line_index','label','measured_row_id')} for r in rr]))
    write_json(BASE / 'selection.json', selection); write_json(BASE / 'population.json', summary)
    write_rows(BASE / 'excluded.jsonl', excluded)
    write_json(BASE / 'binding.json', dict(frozen=binding, start_head=START_HEAD,
        inputs={str(p):sha(p) for p in (W1_ROOT/'collector.exit', W1/'state.json', W1/'crop_tight_page.jsonl', INSTRUCTIONS)},
        selection_sha256=sha(BASE/'selection.json'), created_utc=utc(), network='OFF', W1_read_only=True))
    def launch(i):
        if time.monotonic()-start > 70*60: raise RuntimeError('T6b processing budget exhausted')
        log = BASE / 'logs' / (selection[i]['page_id'] + '.log')
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--worker', str(i)], cwd=ROOT,
                stdout=stream, stderr=subprocess.STDOUT, timeout=300)
        if result.returncode:
            raise RuntimeError('page failed: ' + str(log) + '\n' + log.read_text()[-5000:])
        return log.read_text().splitlines()[-1]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(launch, i) for i in range(len(selection))]
        for i, future in enumerate(as_completed(futures), 1):
            try: result = future.result()
            except Exception:
                for pending in futures: pending.cancel()
                raise
            print(f'{i}/{len(selection)} ' + result, flush=True)
    finish()
    write_json(BASE / 'execution.json', dict(status='completed', seconds=time.monotonic()-start,
        pages=len(selection), concurrency=3, numerical_threads_per_worker=1, network='OFF', W1_read_only=True))


if __name__ == '__main__':
    main()
