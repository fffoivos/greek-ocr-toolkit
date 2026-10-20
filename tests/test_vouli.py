"""T21 synthetic/offline contracts; no provider request is permitted."""
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pypdfium2 as pdfium
import pytest

from scripts.harvest import vouli as v
from scripts.harvest import vouli_outputs as o


def binding():
    return dict(project='test', location='eu', processor='test', version='test',
        user_project='test', options=dict(ocrConfig=dict(enableSymbol=True,
        hints=dict(languageHints=['el']))))


def reader(tmp_path, max_calls=1126):
    return v.VouliReaders(dict(binding=binding(), cap_usd=2.5, max_calls=max_calls), root=tmp_path)


def page(ident='one', digest='a', accepted=True):
    return dict(id=ident, image_sha256=digest, gate={'accepted': accepted})


@pytest.mark.parametrize('accepted', [False, None, 1, 'true'])
def test_gate_scope_requires_literal_true(accepted):
    assert v.select_pages([page(accepted=accepted)]) == []


def test_scope_subtracts_prior_image_sha_without_decade_or_spread_filter():
    pages = [dict(page(str(i), str(i)), year=y, width=5000, height=2500)
             for i, y in enumerate((1824, 1851, 1916, None))]
    assert v.select_pages(pages, ['0']) == pages[1:]


def test_duplicate_page_identity_even_when_rejected():
    with pytest.raises(ValueError, match='duplicate page identity'):
        v.select_pages([page(accepted=False), page()])


def test_duplicate_page_image_sha_never_spends_twice():
    pages = v.select_pages([page('one'), page('two')])
    assert len(pages) == 2
    assert v.unique_call_pages(pages) == [pages[0]]


def test_holdout_exact_seeded_16_books_pre_read_and_order_independent():
    books = [dict(key=f'{i:012d}', book=f'{i:064d}', title='Βουλή', year=None,
                  decade=None) for i in range(107)]
    held = v.select_holdout(books)
    assert held == v.select_holdout(books[::-1])
    assert len(held) == 16 and len({b['book_key'] for b in held}) == 16
    assert sum(b['split'] == 'dev' for b in held) == 4
    assert sum(b['split'] == 'test' for b in held) == 12
    assert held != v.select_holdout(books, seed=20261016)


def test_holdout_duplicate_books_fail_closed():
    with pytest.raises(ValueError, match='duplicate book'):
        v.select_holdout([dict(key='same')] * 107)


def test_no_vision_instance_and_engine_guard(tmp_path):
    r = reader(tmp_path)
    assert not hasattr(r, 'vision')
    assert r.budget.path.name == 'budget.jsonl'
    assert r.docai.binding() == binding()
    with pytest.raises(ValueError, match='forbids'):
        r.call('vision', 'unused')


def test_more_than_1000_pages_allowed_but_money_cap_enforced(tmp_path):
    from greekocr.harvest.readers import BudgetExceeded
    r = reader(tmp_path, max_calls=2000)
    assert r.budget.max_calls == 1666
    for i in range(1666):
        r.budget.reserve('docai', str(i))
    assert r.budget.receipt()['cost_usd'] == pytest.approx(2.499)
    with pytest.raises(BudgetExceeded):
        r.budget.reserve('docai', 'over-cap')


def test_ambiguous_reservation_never_retried(tmp_path, monkeypatch):
    r = reader(tmp_path)
    image = tmp_path / 'page.png'
    Image.new('L', (20, 20), 255).save(image)
    r.budget.reserve('docai', v.sha(image))
    monkeypatch.setattr(r.docai, 'read', lambda *a: pytest.fail('no network'))
    first = r.call('docai', image)
    assert first['error_class'] == 'InterruptedReservedAttempt'
    assert r.call('docai', image) == first
    assert r.budget.receipt()['calls_reserved'] == 1


def test_provider_attempt_without_parsed_cache_never_retried(tmp_path, monkeypatch):
    r = reader(tmp_path)
    image = tmp_path / 'page.png'
    Image.new('L', (20, 20), 255).save(image)
    p = tmp_path / 'docai/ledger.jsonl'
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(dict(crop_sha256=v.sha(image))) + '\n')
    monkeypatch.setattr(r.docai, 'read', lambda *a: pytest.fail('no network'))
    with pytest.raises(RuntimeError, match='no re-read'):
        r.call('docai', image)
    assert r.budget.receipt()['calls_reserved'] == 0


def test_success_cache_reused_with_zero_new_requests(tmp_path, monkeypatch):
    r = reader(tmp_path)
    image = tmp_path / 'page.png'
    Image.new('L', (20, 20), 255).save(image)
    digest = v.sha(image)
    result = dict(status='ok', binding=binding(), image_sha256=digest)
    v.atomic(tmp_path / 'parsed/docai' / (digest + '.json'), result)
    monkeypatch.setattr(r.docai, 'read', lambda *a: pytest.fail('no network'))
    assert r.call('docai', image) == result
    assert r.call('docai', image) == result
    assert r.budget.receipt()['calls_reserved'] == 0


@pytest.mark.parametrize('pilot_accept,photometric_accept', [(True, True), (False, True), (True, False), (False, False)])
def test_frozen_gate_and_photometry_both_wired(tmp_path, monkeypatch, pilot_accept, photometric_accept):
    path = tmp_path / 'spread.png'
    Image.new('L', (200, 100), 255).save(path)
    polygon = [[10, 10], [190, 10], [190, 30], [10, 30]]
    item = dict(polygon=polygon)
    calls = []
    def page_gate(gray, items, *, bend_fired):
        calls.append((gray.shape, items, bend_fired))
        return dict(accepted=pilot_accept, flags=[] if pilot_accept else ['rotated'], column_bands=[[10, 190]])
    def crop_gate(box, boxes, pg, size, row, *, long_complete):
        assert box == boxes[0] == [10, 10, 190, 30]
        assert long_complete and size == (200, 100) and row == item
        return dict(accepted=True)
    gate = SimpleNamespace(page_gate=page_gate, crop_gate=crop_gate,
                           bbox=lambda polygon: [10, 10, 190, 30])
    stack = SimpleNamespace(source_sha256='stack', model_sha256='model',
        run=lambda path, gray: dict(items=[item], harvest_bend=[dict(side=1)], removed=[]))
    feature = dict(darkest_percentile_contrast=100 if photometric_accept else 69,
                   faintness_proxy=100, ink_fraction=.2, component_contrast_p10=100)
    monkeypatch.setattr(v, 'crop_features', lambda image: feature)
    limits = dict(ink_min=.08, ink_max=.85, component_min=37.333, faint_suppression_max=.125)
    result = v.gate_image(path, stack, gate, limits)
    assert result['accepted'] == (pilot_accept and photometric_accept)
    assert result['gate_source_sha256'] == v.round1.GATE_SHA
    assert result['image_sha256'] == v.sha(path)
    assert result['flags'] == ([] if pilot_accept else ['rotated']) + ([] if photometric_accept else ['bad_darkest_percentile_contrast'])
    assert calls == [((100, 200), [item], True)]


def test_renderer_covers_all_pages_of_multipage_pdf_and_resumes(tmp_path, monkeypatch):
    bulk, out = tmp_path / 'bulk', tmp_path / 'out'
    bulk.mkdir()
    path = tmp_path / 'book.pdf'
    doc = pdfium.PdfDocument.new()
    for _ in range(3):
        doc.new_page(72, 144).close()
    doc.save(path)
    doc.close()
    monkeypatch.setattr(v, 'REPO', tmp_path)
    monkeypatch.setattr(v, 'BULK', bulk)
    monkeypatch.setattr(v, 'OUT', out)
    seen = []
    def gate_image(path, *args):
        with Image.open(path) as image:
            assert image.mode == 'L' and image.size == (200, 400)
        seen.append(path.name)
        return dict(accepted=True)
    monkeypatch.setattr(v, 'gate_image', gate_image)
    for name in ('WORKER_STACK', 'WORKER_GATE', 'WORKER_LIMITS'):
        monkeypatch.setattr(v, name, None, raising=False)
    b = dict(pdf='book.pdf', pdf_sha256=v.sha(path), key='abcdef123456')
    pages = v.gate_book(b)
    assert [p['page'] for p in pages] == [1, 2, 3]
    assert seen == ['abcdef123456-000001.png', 'abcdef123456-000002.png', 'abcdef123456-000003.png']
    assert v.gate_book(b) == pages and len(seen) == 3


def record(ident, text, book='train'):
    return dict(id=ident, page_id=ident, book_key=book, year=1850, decade=1850,
                confidence=.99, flags=[], bbox=[0, 0, 200, 20], docai_text=text,
                licence='CC-BY-4.0', source_url='https://example.invalid', attribution='Library')


def test_o5_against_both_wave_and_round1_holdouts_and_reverse_overlay():
    a, b, c = 'ἄνθρωπος καὶ λόγος', 'ἐλευθερία καὶ νόμος', 'βουλευτὴς καὶ γερουσία'
    rows = [record('new-train-old-match', a), record('new-test', b, 'held'),
            record('new-train-new-match', b), record('new-unique', c)]
    old = [dict(id='old-test', label=a, split='test', source='anemi_round1'),
           dict(id='old-train', label=b, split='train', source='anemi_round1')]
    kept, rejected, _, _, overlay = o.admit_records(rows, [dict(book_key='held', split='test')], old)
    assert [r['id'] for r in kept] == ['new-test', 'new-unique']
    assert {r['id'] for r in rejected} == {'new-train-old-match', 'new-train-new-match'}
    assert all(r['reasons'] == ['label_in_holdout'] for r in rejected)
    assert [r['id'] for r in overlay] == ['old-train']


@pytest.mark.parametrize('other,wave,excluded', [(3, 2, 0), (3, 3, 1), (0, 2, 2), (100, 100, 34)])
def test_poly_source_cap_in_combined_training_pool(other, wave, excluded):
    old = [dict(id=f'old{i}', split='train', script_class='greek_poly') for i in range(other)]
    new = [dict(id=f'new{i}', split='train', script_class='greek_poly', label=str(i)) for i in range(wave)]
    exclusions, cap = o.apply_source_cap(new, old, [])
    assert len(exclusions) == excluded and cap['passed'] and cap['pool_share'] <= .4
    assert exclusions == o.apply_source_cap(new[::-1], old, [])[0][::-1]


def test_vouli_compiled_paths_use_flat_book_folders_and_actual_year():
    p = dict(title='ΣΥΝΕΔΡΙΑΣΗ / Λόγος' * 5, year=1875, key='abcdef123456', page=2)
    path = o.compiled_path(p)
    assert len(path.parts) == 2 and path.parts[0].startswith('1875_')
    assert path.parts[0].endswith('_abcdef') and path.name == 'p0002.jpg'
    assert o.compiled_path(dict(p, year=None)).parts[0].startswith('unknown_')


@pytest.mark.parametrize('workers', [1, 2])
def test_compile_builder_path_callback_preserves_approved_raster(tmp_path, workers):
    image = tmp_path / 'page.png'
    Image.new('L', (200, 300), 255).save(image)
    records = tmp_path / 'records.jsonl'
    records.write_text('')
    p = dict(id='empty', image=str(image), image_sha256=v.sha(image),
             year=1850, key='abcdef123456', title='Βουλή', page=1)
    receipt = v.compiler.compile_records(records, tmp_path / 'compiled', pages=[p], books={}, path_builder=o.compiled_path, workers=workers)
    target = tmp_path / 'compiled' / o.compiled_path(p)
    assert target.is_file() and receipt['page_count'] == 1
    with Image.open(target) as im:
        assert im.size == (520, 380)


def test_parallel_compile_has_identical_approved_jpeg_and_layout(tmp_path):
    image = tmp_path / 'page.png'
    Image.new('L', (200, 300), 240).save(image)
    p = dict(id='page', image=str(image), image_sha256=v.sha(image),
             year=1850, key='abcdef123456', title='Βουλή', page=1)
    rows = [dict(page_id='page', docai_index=i, line_number=i + 1,
                 image_sha256=p['image_sha256'], bbox=[30, 30 + i * 40, 180, 50 + i * 40],
                 docai_text='ἄνθρωπος καὶ νόμος', confidence=.85 if i else .99, counted=True)
            for i in range(2)]
    records = tmp_path / 'records.jsonl'
    records.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    serial = v.compiler.compile_records(records, tmp_path / 'serial', pages=[p], books={}, path_builder=o.compiled_path)
    parallel = v.compiler.compile_records(records, tmp_path / 'parallel', pages=[p], books={}, path_builder=o.compiled_path, workers=2)
    assert serial == parallel
    assert (tmp_path / 'serial' / o.compiled_path(p)).read_bytes() == (tmp_path / 'parallel' / o.compiled_path(p)).read_bytes()


def test_unusable_geometry_is_reported_as_lost_page_without_inventing_boxes(tmp_path, monkeypatch):
    monkeypatch.setattr(o, 'OUT', tmp_path)
    raw = dict(document=dict(text='ἄνθρωπος', pages=[dict(lines=[{}])]))
    monkeypatch.setattr(o, 'raw_read', lambda *a: (raw, {'status': 'ok'}))
    def invalid(*args):
        raise ValueError('singular transform')
    monkeypatch.setattr(o, '_response_geometry', invalid)
    records, summary = o.read_records(dict(pages=[dict(id='page', width=200, height=300)]), write=True)
    assert records == [] and summary['lost_pages'] == 1
    assert summary['empty_pages'] == 0 and summary['no_line_pages'] == 0
    assignment = json.loads((tmp_path / 'assignments/page.json').read_text())
    assert assignment['lost_page'] and assignment['geometry_error'] == 'singular transform'
    assert assignment['records'] == [] and assignment['coordinate_frame'] is None


def test_uncuttable_neighbour_midpoints_are_extraction_failures_without_rule_repair():
    target = dict(record('target', 'ἄνθρωπος καὶ λόγος'), page_id='page', bbox=[0, 10, 100, 20])
    previous = dict(target, id='previous', bbox=[0, -2, 100, 30])
    following = dict(target, id='following', bbox=[0, 0, 100, 32])
    valid = dict(target, id='valid', bbox=[200, 10, 300, 20])
    kept, rejected, failures, geometry = o.plan_crops(
        [target, previous, following, valid], [target, valid], {'page': (500, 100)})
    assert kept == [valid] and set(geometry) == {'valid'}
    assert rejected == [dict(id='target', reasons=['crop_geometry'], docai_text=target['docai_text'])]
    assert failures[0]['error'] == 'neighbour midpoint cuts leave no line extent'
    assert target['bbox'] == [0, 10, 100, 20]
