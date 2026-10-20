#!/usr/bin/env python3
"""Offline T19 scope, raw receipts, exact assignment replay and image QA."""
from __future__ import annotations

from collections import Counter, defaultdict
import io
import json
from pathlib import Path
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.round1_reads import sha
from scripts.harvest.round1_reads_rest import ROOT, OUT, BULK, GOOGLE, D1, select_pages
from scripts.harvest.build_round1_reads_rest import evaluate
from scripts.harvest.compile_page_reads import render_page, relative_path, PAD, GAP


def layout_equivalence():
    baseline = json.loads((OUT / 'layout_baseline.json').read_text())
    groups = defaultdict(list)
    for row in read_jsonl(D1):
        groups[row['page_id']].append(row)
    selected = {p['page']['id'] for p in baseline['pages']}
    assert sha(OUT / 'approved_builder_reference.py.txt') == baseline['approved_builder_reference_sha256']
    reference = (OUT / 'approved_builder_reference.py.txt').read_text()
    # Independently execute the archived Python builder, restricted to the three
    # chosen pages. The shell wrapper (including its removal/open commands) was
    # excluded when extracting this immutable reference.
    reference = reference.replace("sel={b['key']", "recs={pid:rows for pid,rows in recs.items() if pid in selected}\nsel={b['key']", 1)
    reference = reference.replace('for r,txt,s in items:', 'reference_positions[pid]=[]\n    for r,txt,s in items:', 1)
    reference = reference.replace('        pd.text((x0,ty),txt,', '        reference_positions[pid].append(dict(line_number=r["line_number"],panel_xy=[x0,ty],font_size=f.size))\n        pd.text((x0,ty),txt,', 1)
    target = Path('/private/tmp/t19-approved-reference')
    target.mkdir(parents=True, exist_ok=True)
    namespace = dict(selected=selected, reference_positions={})
    old_argv = sys.argv
    try:
        sys.argv = ['approved_builder_reference.py', str(target)]
        exec(compile(reference, 'approved_builder_reference.py.txt', 'exec'), namespace)
    finally:
        sys.argv = old_argv
    pages = []
    for sample in baseline['pages']:
        page = sample['page']
        original = REPO / sample['original_path']
        independent = target / relative_path(page)
        regenerated = BULK / 'reads_d1_compiled' / relative_path(page)
        assert sha(original) == sample['original_sha256'] == sha(independent) == sha(regenerated)
        with Image.open(REPO / page['image']) as image:
            canvas, layout = render_page(image, groups[page['id']])
        buf = io.BytesIO()
        canvas.save(buf, 'JPEG', quality=85)
        assert buf.getvalue() == original.read_bytes()
        ref_positions = namespace['reference_positions'][page['id']]
        assert len(ref_positions) == len(layout['positions'])
        deltas = []
        for actual, expected in zip(layout['positions'], ref_positions):
            assert actual['line_number'] == expected['line_number'] and actual['font_size'] == expected['font_size']
            deltas.extend(abs(a-b) for a,b in zip(actual['panel_xy'], expected['panel_xy']))
        assert max(deltas, default=0) <= 1
        with Image.open(original) as image:
            assert list(image.size) == layout['canvas_size']
        pages.append(dict(page_id=page['id'], jpeg_sha256=sha(original), byte_identical=True,
                          canvas_size=layout['canvas_size'], text_positions_checked=len(ref_positions),
                          max_text_position_delta_px=max(deltas, default=0),
                          font_sizes_identical=True, tall_lines=sum(p['tall'] for p in layout['positions']),
                          low_confidence_lines=sum(p['low_confidence'] for p in layout['positions'])))
    result = dict(schema='t19-approved-layout-equivalence-1', reference_sha256=sha(OUT / 'approved_builder_reference.py.txt'),
                  pages=pages, byte_identical_pages=len(pages), pixel_position_tolerance=1)
    atomic(OUT / 'layout_equivalence.json', result)
    return result


def validate_compiled(records_file, folder, pages):
    receipt = json.loads((folder / 'compile_receipt.json').read_text())
    assert receipt['records_sha256'] == sha(records_file)
    assert receipt['builder_sha256'] == sha(REPO / 'scripts/harvest/compile_page_reads.py')
    assert receipt['pad'] == receipt['gap'] == 40 and receipt['jpeg_quality'] == 85
    assert receipt['page_count'] == len(pages) == len(receipt['pages'])
    assert set(p['page_id'] for p in receipt['pages']) == {p['id'] for p in pages}
    by_page = {p['id']: p for p in pages}
    groups = defaultdict(list)
    for row in read_jsonl(records_file):
        groups[row['page_id']].append(row)
    for item in receipt['pages']:
        page = by_page[item['page_id']]
        path = folder / item['path']
        assert item['path'] == str(relative_path(page))
        assert sha(path) == item['jpeg_sha256']
        with Image.open(path) as image:
            assert image.format == 'JPEG' and list(image.size) == item['canvas_size']
            assert image.size == (2*page['width']+120, page['height']+80)
        rows = {r['line_number']: r for r in groups[item['page_id']]}
        positions = item['positions']
        assert len(positions) == sum(bool(r['docai_text'].strip()) for r in rows.values())
        fitted = sorted(p['fitted_size'] for p in positions if rows[p['line_number']]['counted']) or sorted(p['fitted_size'] for p in positions)
        if fitted:
            assert item['page_font_size'] == fitted[len(fitted)//4]
        for pos in positions:
            row = rows[pos['line_number']]
            x0,y0,x1,y1 = row['bbox']
            median = item['median_counted_height']
            tall = y1-y0 > 1.7*median
            assert pos['tall'] == tall
            assert pos['text'] == ' '.join(row['docai_text'].split())
            assert pos['font_size'] == min(item['page_font_size'], pos['fitted_size'])
            assert pos['low_confidence'] == (row['confidence'] is not None and row['confidence'] < .89)
            ty = y0+2 if tall else y0+((y1-y0)-pos['font_size'])/2-pos['font_size']*.15
            assert pos['panel_xy'] == [x0,ty]
            assert pos['canvas_xy'] == [PAD+page['width']+GAP+x0,PAD+ty]
    assert len(list(folder.rglob('*.jpg'))) == len(pages)
    return dict(pages=len(pages), text_positions=sum(len(p['positions']) for p in receipt['pages']),
                receipt_sha256=sha(folder / 'compile_receipt.json'), all_jpeg_hashes_and_dimensions_verified=True)


def validate(plan):
    for path, expected in plan['inputs'].items():
        assert sha(REPO / path) == expected
    baseline = json.loads((OUT / 'layout_baseline.json').read_text())
    for path, expected in baseline['d1_inputs'].items():
        assert sha(REPO / path) == expected, 'd1 input/ledger changed: '+path
    resume = json.loads((OUT / 'resume_check.json').read_text())
    assert resume['pages'] == plan['page_count'] and resume['new_calls'] == resume['new_vision_calls'] == 0
    assert resume['ledgers_byte_identical']
    for path, expected in resume['ledger_hashes'].items():
        assert sha(Path(path)) == expected
    books = {}
    for path in (ROOT / 'selection.json', ROOT / 'rescue/selection.json'):
        books.update({b['book']: b for b in json.loads(path.read_text())['books']})
    selected = select_pages(json.loads((_data_input(ROOT / 'manifest_all.json')).read_text()), books, read_jsonl(D1))
    assert [p['id'] for p in selected] == [p['id'] for p in plan['pages']]
    reservations = read_jsonl(GOOGLE / 'budget_rest.jsonl')
    keys = {p['image_sha256'] for p in plan['pages']}
    assert len(reservations) == len(keys) == plan['page_count']
    assert Counter(r['key'] for r in reservations) == Counter(keys)
    assert all(r['engine'] == 'docai' and r['micro_usd'] == 1500 for r in reservations)
    assert json.loads((GOOGLE / 'budget_rest.state.json').read_text())['calls'] == len(keys)
    historical = read_jsonl(GOOGLE / 'budget.jsonl')
    assert not keys & {r['key'] for r in historical if r['engine'] == 'docai'}
    ledger = [r for r in read_jsonl(GOOGLE / 'docai/ledger.jsonl') if r['crop_sha256'] in keys]
    assert len(ledger) == len(keys) and Counter(r['crop_sha256'] for r in ledger) == Counter(keys)
    assert all(r['status'] == 'ok' and r['cached'] is False and r['pages_billed'] == 1 and r['binding'] == plan['binding'] for r in ledger)
    receipt_ids = {r['receipt_id'] for r in ledger}
    assert len(receipt_ids) == len(keys)
    records, summary = evaluate(plan, write=False)
    assert records == read_jsonl(OUT / 'records.jsonl')
    assert summary == json.loads((OUT / 'summary.json').read_text())
    assert len(list((OUT / 'assignments').glob('*.json'))) == len(keys)
    for p in plan['pages']:
        assignment = json.loads((OUT / 'assignments' / (p['id']+'.json')).read_text())
        assert assignment['readers']['docai']['receipt_id'] in receipt_ids
    combined = read_jsonl(ROOT / 'records_all.jsonl')
    d1 = read_jsonl(D1)
    rest_ids = {p['id'] for p in plan['pages']}
    assert len(combined) == len(d1)+len(records)
    for expected, actual in zip(d1+records, combined):
        actual = dict(actual)
        batch = actual.pop('read_batch')
        assert actual == expected
        assert batch == ('rest' if expected['page_id'] in rest_ids else 'd1')
    cost = json.loads((OUT / 'cost_receipt.json').read_text())
    assert cost['calls_reserved'] == len(keys) and cost['calls_by_engine'] == {'vision': 0, 'docai': len(keys)}
    assert cost['cost_usd'] == len(keys)*.0015 <= 3
    d1_plan = json.loads((ROOT / 'reads_d1/plan.json').read_text())
    compiled = dict(rest=validate_compiled(OUT / 'records.jsonl', BULK / 'reads_rest_compiled', plan['pages']),
                    d1=validate_compiled(D1, BULK / 'reads_d1_compiled', d1_plan['pages']))
    equivalence = layout_equivalence()
    result = dict(schema='t19-offline-validation-1', page_count=len(keys),
                  assignments_replayed=len(keys), record_count=len(records), d1_records_preserved=len(d1),
                  combined_records=len(combined), calls_reserved=len(reservations), unique_uncached_docai_receipts=len(ledger),
                  vision_calls=0, cost_usd=cost['cost_usd'], compiled=compiled,
                  completed_cached_resume_new_calls=0,
                  approved_layout_byte_identical_pages=equivalence['byte_identical_pages'],
                  frozen_inputs_and_shared_t17_ledgers_unchanged=True, success=True)
    atomic(OUT / 'validation.json', result)
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    validate(json.loads((OUT / 'plan.json').read_text()))
