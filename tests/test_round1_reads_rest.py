"""T19 contracts; all reader transports in this suite are mocked/offline."""
import json
from pathlib import Path

import pytest
from PIL import Image

from greekocr.harvest.readers import BudgetExceeded, atomic
from scripts.harvest.round1_reads_rest import select_pages, DocAIOnlyReaders


def book(decade):
    return dict(key=str(decade), title='Λόγος', year=decade, decade=decade)


def test_scope_subtracts_d1_and_includes_all_rescue_decades():
    books = {str(d): book(d) for d in range(1860, 1940, 10)}
    manifest = [dict(book=str(d), page=n, origin=origin, harvest_accepted=True)
                for d in books for n, origin in ((1, 't16'), (2, 'rescue'))]
    old = [dict(page_id=f'{d}-p000001') for d in (1860, 1870, 1880)]
    selected = select_pages(manifest, books, old)
    assert len(selected) == 13
    assert not {p['id'] for p in selected} & {r['page_id'] for r in old}
    assert len([p for p in selected if p['origin'] == 'rescue']) == 8


@pytest.mark.parametrize('accepted', [False, None, 1])
def test_scope_requires_literal_acceptance(accepted):
    assert select_pages([dict(book='1890', page=1, origin='t16', harvest_accepted=accepted)],
                        {'1890': book(1890)}, []) == []


def test_duplicate_identity_is_rejected_even_if_already_read():
    p = dict(book='1890', page=1, origin='t16', harvest_accepted=True)
    with pytest.raises(ValueError, match='duplicate'):
        select_pages([p, p], {'1890': book(1890)}, [dict(page_id='1890-p000001')])


def test_unread_early_t16_page_fails_closed():
    with pytest.raises(ValueError, match='outside authorized'):
        select_pages([dict(book='1860', page=1, origin='t16', harvest_accepted=True)], {'1860': book(1860)}, [])


def reader(tmp_path):
    binding = dict(project='test', location='eu', processor='test', version='test', user_project='test',
                   options={'ocrConfig': {'enableSymbol': True, 'hints': {'languageHints': ['el']}}})
    return DocAIOnlyReaders(dict(cap_usd=3, max_calls=1189, binding=binding), root=tmp_path)


def test_docai_only_budget_and_no_vision_instance(tmp_path):
    r = reader(tmp_path)
    assert not hasattr(r, 'vision')
    assert r.budget.max_calls == 1189
    with pytest.raises(ValueError, match='forbids'):
        r.call('vision', 'unused')
    for i in range(1189):
        r.budget.reserve('docai', str(i))
    assert r.budget.receipt()['cost_usd'] == pytest.approx(1.7835)
    with pytest.raises(BudgetExceeded):
        r.budget.reserve('docai', 'extra')


def test_ambiguous_reserved_request_never_retries(tmp_path, monkeypatch):
    r = reader(tmp_path)
    path = tmp_path / 'page.png'
    Image.new('L', (20, 20), 255).save(path)
    from scripts.harvest.round1_reads import sha
    r.budget.reserve('docai', sha(path))
    monkeypatch.setattr(r.docai, 'read', lambda *a: pytest.fail('network must not run'))
    first = r.call('docai', path)
    assert first['error_class'] == 'InterruptedReservedAttempt'
    assert r.call('docai', path) == first
    assert r.budget.receipt()['calls_reserved'] == 1


def test_prior_batch_attempt_without_cache_never_retries(tmp_path, monkeypatch):
    r = reader(tmp_path)
    path = tmp_path / 'page.png'
    Image.new('L', (20, 20), 255).save(path)
    from scripts.harvest.round1_reads import sha
    (tmp_path / 'budget.jsonl').write_text(json.dumps(dict(engine='docai', key=sha(path)))+'\n')
    monkeypatch.setattr(r.docai, 'read', lambda *a: pytest.fail('network must not run'))
    with pytest.raises(RuntimeError, match='no re-read'):
        r.call('docai', path)
    assert r.budget.receipt()['calls_reserved'] == 0


@pytest.mark.parametrize('height,confidence,expected', [
    (17, .89, []), (17.001, .889, ['low_confidence', 'tall_box']),
    (10, 0, ['low_confidence']), (10, None, []),
])
def test_flag_strict_boundaries(height, confidence, expected):
    from scripts.harvest.build_round1_reads_rest import flag_rows
    rows = [dict(bbox=[0, 0, 100, 10], counted=True, confidence=.99) for _ in range(3)]
    rows.append(dict(bbox=[0, 0, 100, height], counted=True, confidence=confidence))
    flagged, median = flag_rows(rows)
    assert median == 10
    assert flagged[-1]['flags'] == expected
    assert 'flags' not in rows[-1]


def test_short_line_does_not_shift_counted_median():
    from scripts.harvest.build_round1_reads_rest import flag_rows
    rows = [dict(bbox=[0, 0, 100, 10], counted=True, confidence=.95),
            dict(bbox=[0, 0, 100, 100], counted=False, confidence=.8)]
    result, median = flag_rows(rows)
    assert median == 10
    assert result[1]['flags'] == ['low_confidence', 'short_line', 'tall_box']


def test_no_counted_lines_has_no_invented_tall_denominator():
    from scripts.harvest.build_round1_reads_rest import flag_rows
    rows, median = flag_rows([dict(bbox=[0, 0, 10, 100], counted=False, confidence=None)])
    assert median is None
    assert rows[0]['flags'] == ['short_line']


def test_docai_provider_order_labels_and_missing_symbol_confidence():
    from scripts.harvest.build_round1_reads_rest import make_rows
    page = dict(id='test-p1', page=1, book='test', key='test', year=1900, decade=1900,
                origin='rescue', image='page.png', image_sha256='a')
    def layout(start, end, confidence=None):
        return dict(textAnchor={'textSegments': [dict(startIndex=start, endIndex=end)]}, confidence=confidence)
    document = dict(text='λόγος12', pages=[dict(lines=[dict(layout=layout(0, 5)), dict(layout=layout(5, 7))],
                   symbols=[dict(layout=layout(0, 1, .8)), dict(layout=layout(1, 2)), dict(layout=layout(5, 6, .9))])])
    geometry = dict(coordinate_frame=dict(converted=True), lines=[
        dict(source='lines', text='λόγος', bbox=[20, 80, 80, 90]),
        dict(source='lines', text='12', bbox=[20, 10, 40, 20])])
    rows, _, _, _ = make_rows(page, document, geometry)
    assert [r['docai_index'] for r in rows] == [0, 1]
    assert [r['bbox'][1] for r in rows] == [80, 10]
    assert rows[0]['label'] == 'λόγος'
    assert rows[1]['label'] is None
    assert rows[0]['vision_text'] is rows[0]['tier'] is None
    assert rows[0]['symbol_count'] == 2
    assert rows[0]['confidence'] == rows[0]['min_confidence'] == .8
    assert rows[0]['flags'] == ['docai_transform_inverse', 'low_confidence']
