"""Offline contracts for T27; never contact Wikimedia or Google."""
import json
from pathlib import Path
import random
import unicodedata as ud

import pytest

from greekocr.harvest import wikisource as policy
from scripts.harvest.wikisource import WikimediaHTTP, index_metadata, UA
from bs4 import BeautifulSoup

FIXTURES = json.loads((Path(__file__).parent / 'data/wikisource/transcriptions.json').read_text())


@pytest.mark.parametrize('fixture', FIXTURES, ids=lambda f: f['name'])
def test_wikitext_fixtures(fixture):
    result = policy.strip_wikitext(fixture['wikitext'])
    assert [r['text'] for r in result['lines']] == fixture['lines']
    assert result['proofread_level'] == fixture['quality']
    assert not result['unknown_templates']


def test_unknown_template_never_becomes_gold():
    parsed = policy.strip_wikitext('{{mystery|this might not be printed}}\nKnown body text')
    assert parsed['unknown_templates'][0]['template'] == 'mystery'
    assert not parsed['lines'][0]['usable']
    aligned, _ = policy.align_lines(['this might not be printed', 'Known body text'], parsed['lines'])
    assert [r['alignment'] for r in aligned] == ['unaligned', 'aligned']


@pytest.mark.parametrize('wrapper', ['ВАР', 'ВАР2'])
def test_historical_variant_keeps_printed_spelling_and_line_breaks(wrapper):
    raw = '{{' + wrapper + '|<poem>Картина Міра хороша,\n{{indent|4}}Люблю я свѣтъ и тьму.</poem>'
    raw += '|<poem>Картина Мира хороша,\nЛюблю я свет и тьму.</poem>}}'
    result = policy.strip_wikitext(raw)
    assert [r['text'] for r in result['lines']] == ['Картина Міра хороша,', 'Люблю я свѣтъ и тьму.']
    assert result['variant_selections'] == [dict(template=wrapper.lower(), selected_argument=1,
        action='historical_scan_orthography', discarded_argument=2)]


def test_poem_editorial_line_counters_are_absent_from_scan_gold():
    result = policy.strip_wikitext('<poem>{{№|5}}Все, что приходитъ, то прошло,\n'
        '{{№|10}}Въ явленьи цѣльность быть должна,</poem>\n{{№|15}}')
    assert [r['text'] for r in result['lines']] == ['Все, что приходитъ, то прошло,',
        'Въ явленьи цѣльность быть должна,', '15']


def test_unknown_historical_variant_never_falls_back_to_modern_gold():
    result = policy.strip_wikitext('{{ВАР|{{mystery|old spelling}}|Modern spelling}}')
    assert not result['lines'][0]['usable']
    assert 'Modern spelling' not in result['lines'][0]['text']


def test_hyphenation_audited_without_cross_page_whole_word():
    result = policy.strip_wikitext('{{σλβα|ἀν|ἀνθρώπου}}\n{{σλβτ|θρώπου|ἀνθρώπου}}\nἀν\u00adθρώπου')
    assert [r['text'] for r in result['lines']] == ['ἀν-', 'θρώπου', 'ἀνθρώπου']
    assert [r['joined'] for r in result['hyphenation']] == [False, False, True]


@pytest.mark.parametrize('a,b,want', [('', '', 0), ('', 'я', 1), ('abc', '', 3),
    ('kitten', 'sitting', 3), ('ἄνθρωπος', 'άνθρωπος', 1), ('ѣ', 'е', 1), ('foo', 'foo', 0)])
def test_edit_distance(a, b, want):
    assert policy.distance(a, b) == want
    assert policy.distance(b, a) == want


def test_distance_matches_independent_dynamic_programming():
    rng = random.Random(27)
    for _ in range(100):
        a, b = [''.join(rng.choices('αβγѣ ', k=rng.randrange(15))) for _ in range(2)]
        row = list(range(len(b) + 1))
        for i, ch in enumerate(a, 1):
            out = [i]
            for j, other in enumerate(b, 1):
                out.append(min(out[-1] + 1, row[j] + 1, row[j-1] + (ch != other)))
            row = out
        assert policy.distance(a, b) == row[-1]


@pytest.mark.parametrize('lang,text', [('el', 'Ἄνθρωπος καὶ ἄνθρωποι'), ('ru', 'Наслѣдственность организмовъ')])
def test_alignment_nfc_and_spaces(lang, text):
    result, _ = policy.align_lines([ud.normalize('NFD', text)], [{'text': text.replace(' ', '  ')}])
    assert result[0]['human_label'] == text
    assert result[0]['cer_docai_vs_human'] == 0


@pytest.mark.parametrize('docai,human', [(['alpha beta gamma delta'], ['alpha beta', 'gamma delta']),
    (['alpha beta', 'gamma delta'], ['alpha beta gamma delta'])])
def test_split_merge_is_unaligned(docai, human):
    result, blocks = policy.align_lines(docai, [{'text': x} for x in human])
    assert all(r['alignment'] == 'unaligned' for r in result)
    assert all(r['human_label'] is None for r in result)
    assert any(r['alignment_reason'] == 'split_or_merged_lines' for r in result)


def test_missing_and_inserted_lines_preserve_matching_context():
    human = [{'text': x} for x in ['ἄνθρωποι καὶ πράγματα', 'Lost human line', 'Наслѣдственность организмовъ']]
    result, _ = policy.align_lines(['Header 17', 'ἄνθρωποι καὶ πράγματα', 'Наслѣдственность организмовъ'], human)
    assert [r['human_line_indices'] for r in result] == [[], [0], [2]]
    assert [r['alignment'] for r in result] == ['unaligned', 'aligned', 'aligned']


def test_cer_reports_errors_before_admission():
    result, _ = policy.align_lines(['ανθρώπων καὶ ἀνθρώποις'], [{'text': 'ἀνθρώπων καὶ ἀνθρώποις'}])
    row = dict(result[0], lang='el')
    summary = policy.cer_summary([row])
    assert summary['el']['edit_distance'] == 1
    assert summary['el']['mark_classes']['breathings']['aligned'] == 1
    assert summary['el']['mark_classes']['iota_subscript']['cer'] is None
    assert summary['ru']['cer'] is None


@pytest.mark.parametrize('problem', ['changed_bytes', 'duplicate', 'missing', 'wrong_page'])
def test_local_coordinator_receipts_fail_closed(tmp_path, monkeypatch, problem):
    import hashlib
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'BULK', tmp_path)
    page = dict(id='abcdef01-p000008', page=8, scan_file='Fixture.djvu')
    directory = tmp_path / 'thumbs'; directory.mkdir()
    data = b'coordinator scan bytes'
    (directory / (page['id'] + '.jpg')).write_bytes(data)
    receipt = dict(page_id=page['id'], width=3840, bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest(), url=collector.thumbnail_url(page))
    rows = [receipt]
    if problem == 'changed_bytes':
        (directory / (page['id'] + '.jpg')).write_bytes(b'different scan')
    elif problem == 'duplicate':
        rows.append(receipt)
    elif problem == 'missing':
        rows = []
    elif problem == 'wrong_page':
        receipt['url'] = collector.thumbnail_url(dict(page, page=9))
    (directory / 'receipts.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    monkeypatch.setattr(collector, 'WikimediaHTTP', lambda *a, **kw: pytest.fail('network forbidden'))
    with pytest.raises(ValueError):
        collector.local_receipts([page])


def test_failed_local_receipt_is_unavailable_without_network_or_file(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'BULK', tmp_path)
    (tmp_path / 'thumbs').mkdir()
    receipt = dict(page_id='abcdef01-p000008', failed=True)
    (tmp_path / 'thumbs/receipts.jsonl').write_text(json.dumps(receipt) + '\n')
    monkeypatch.setattr(collector, 'WikimediaHTTP', lambda *a, **kw: pytest.fail('network forbidden'))
    assert collector.local_receipts([dict(id=receipt['page_id'])]) == {receipt['page_id']: receipt}


def test_local_gate_preserves_flagged_page_scale_and_scan_custody(tmp_path, monkeypatch):
    import hashlib
    import io
    from PIL import Image
    from scripts.harvest import wikisource as collector, vouli
    monkeypatch.setattr(collector, 'ROOT', tmp_path)
    monkeypatch.setattr(collector, 'BULK', tmp_path / 'bulk')
    monkeypatch.setattr(collector, 'OUT', tmp_path / 'out')
    monkeypatch.setattr(collector, 'WikimediaHTTP', lambda *a, **kw: pytest.fail('network forbidden'))
    for name in ('WORKER_STACK', 'WORKER_GATE', 'WORKER_LIMITS'):
        monkeypatch.setattr(vouli, name, None, raising=False)
    monkeypatch.setattr(vouli, 'gate_image', lambda *a: dict(accepted=False, flags=['fixture_failure']))
    page = dict(id='abcdef01-p000008', key='abcdef01', page=8)
    path = collector.BULK / 'thumbs' / (page['id'] + '.jpg'); path.parent.mkdir(parents=True)
    Image.new('RGB', (2100, 4200), (220, 210, 200)).save(path)
    receipt = dict(page_id=page['id'], width=3840, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    result = collector.gate_local_page((page, receipt, 'receipt-sha'))
    assert result['served_size'] == [2100, 4200]
    assert (result['width'], result['height']) == (1750, 3500)
    assert result['scale_x'] == result['scale_y'] == 3500 / 4200
    assert result['harvest_accepted'] is False and result['gate']['flags'] == ['fixture_failure']
    with Image.open(tmp_path / result['image']) as image:
        assert image.mode == 'L'
    assert collector.gate_local_page((page, receipt, 'receipt-sha')) == result
    path.write_bytes(b'changed')
    with pytest.raises(ValueError):
        # A full import always checks JPEG hashes before reusing a gate.
        collector.gate_local_page((page, dict(receipt, sha256='changed'), 'receipt-sha'))


def test_whole_work_splits_never_train():
    books = [dict(key=f'{lang}{i}', title='fixture', year=1900, lang=lang)
             for lang, n in [('el', 20), ('ru', 10)] for i in range(n)]
    splits = policy.splits(books)
    assert splits == policy.splits(list(reversed(books)))[::-1]
    assert sum(b['split'] == 'dev' and b['lang'] == 'el' for b in splits) == 3
    assert sum(b['split'] == 'dev' and b['lang'] == 'ru' for b in splits) == 1
    assert {b['split'] for b in splits} == {'test', 'dev'}


def test_index_requires_quality_and_explicit_edition_year():
    soup = BeautifulSoup('<div id="mw-content-text"><table><tr><th>Έτος</th><td>1927</td></tr>'
        '<tr><th>Τίτλος</th><td>Έργο</td></tr></table><div class="prp-index-pagelist">'
        '<a class="quality3" href="/wiki/Σελίδα:Book.djvu/8">8</a>'
        '<a class="quality4" href="/wiki/Σελίδα:Book.djvu/9">9</a>'
        '<a class="quality1" href="/wiki/Σελίδα:Book.djvu/10">10</a></div></div>', 'html.parser')
    el = index_metadata(soup, 'https://el.wikisource.org/wiki/Μεταγραφή:Book.djvu', 'el')
    ru = index_metadata(soup, 'https://ru.wikisource.org/wiki/Индекс:Book.djvu', 'ru')
    assert el['year'] == 1927 and [p['page'] for p in el['eligible_pages']] == [8, 9]
    assert [p['page'] for p in ru['eligible_pages']] == [9]


def test_robots_denial_and_external_host_never_request(tmp_path):
    class Session:
        headers = {}
        def get(self, *args, **kwargs):
            pytest.fail('network forbidden in offline tests')
    (tmp_path / 'el.wikisource.org.robots.txt').write_text('User-agent: *\nDisallow: /w/\n')
    http = WikimediaHTTP(tmp_path, session=Session(), sleep=lambda _: None)
    with pytest.raises(PermissionError):
        http.get('https://el.wikisource.org/w/api.php?action=query')
    with pytest.raises(ValueError):
        http.get('https://example.org/test')
    assert http.allowed('https://el.wikisource.org/wiki/Σελίδα:Book/8?action=raw')
    assert http.session.headers['User-Agent'] == UA


def test_rate_spacing_survives_independent_clients_and_cache_is_free(tmp_path):
    class Clock:
        now = 0.
        def time(self): return self.now
        def sleep(self, seconds): self.now += seconds
    clock = Clock(); starts = []
    class Response:
        status_code, content, headers = 200, b'frozen body', {}
    class Session:
        headers = {}
        def get(self, url, **kwargs):
            assert kwargs['allow_redirects'] is False
            starts.append(clock.time())
            return Response()
    (tmp_path / 'el.wikisource.org.robots.txt').write_text('User-agent: *\nAllow: /\n')
    a = WikimediaHTTP(tmp_path, Session(), clock.time, clock.sleep)
    b = WikimediaHTTP(tmp_path, Session(), clock.time, clock.sleep)
    a.get('https://el.wikisource.org/wiki/A')
    b.get('https://el.wikisource.org/wiki/B')
    a.get('https://el.wikisource.org/wiki/A')
    assert len(starts) == 2 and starts[1] - starts[0] >= 1


def test_russian_printed_fragments_and_typo():
    result = policy.strip_wikitext('{{перенос|наслѣд|ственность}}\n{{перенос2|наслѣд|ственность}}\n'
        '{{Опечатка2|нашестві|нашествія}} {{lang|la|Varia}} {{№|15}}')
    assert [x['text'] for x in result['lines']] == ['наслѣд-', 'ственность', 'нашестві Varia 15']
    assert not result['unknown_templates']


def test_train_collision_audit_uses_human_and_docai_and_never_edits_prior(tmp_path, monkeypatch):
    from scripts.harvest import wikisource_outputs as outputs
    root = tmp_path; out = root / 'docs/records/harvest/wikisource'; out.mkdir(parents=True)
    prior = root / 'docs/records/harvest/prior'; prior.mkdir()
    rows = [dict(id='human-hit', split='train', source='prior', label=ud.normalize('NFD', 'ἄνθρωποι')),
        dict(id='google-hit', split='train', source='prior', label='Google reading'),
        dict(id='test-only', split='test', source='prior', label='ἄνθρωποι'),
        dict(id='clean', split='train', source='prior', label='Different label')]
    file = prior / 'train_pool.jsonl'
    file.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    before = file.read_bytes()
    monkeypatch.setattr(outputs, 'ROOT', root); monkeypatch.setattr(outputs, 'OUT', out)
    monkeypatch.setattr(outputs, 'BULK', root / 'docs/harvest/harvest_big/wikisource')
    report = outputs.train_collision_audit({'page': {'lines': [{'text': 'ἄνθρωποι', 'usable': True}]}},
        [dict(docai_label='Google reading', page_id='page')])
    assert report['collision_occurrences'] == 2
    assert report['train_pools'][0]['train_rows'] == 3
    assert file.read_bytes() == before


def test_train_collision_audit_includes_implicit_json_train_manifest(tmp_path, monkeypatch):
    from scripts.harvest import wikisource_outputs as outputs
    out = tmp_path / 'docs/records/harvest/wikisource'; out.mkdir(parents=True)
    prior = tmp_path / 'docs/records/harvest/collection'; prior.mkdir()
    train = prior / 'import_real_train.jsonl'
    crop = 'docs/harvest/harvest_big/prior/crops/work/p000001-l0001.png'
    train.write_text(json.dumps(dict(id='known-id', source='prior', crop=crop,
        label='ἄνθρωποι', split='train')) + '\n')
    manifest = prior / 'manifest_train.json'
    manifest.write_text(json.dumps([dict(source='prior', crop=str(tmp_path / crop), label='ἄνθρωποι')]))
    original = {p: p.read_bytes() for p in (train, manifest)}
    monkeypatch.setattr(outputs, 'ROOT', tmp_path); monkeypatch.setattr(outputs, 'OUT', out)
    monkeypatch.setattr(outputs, 'BULK', tmp_path / 'docs/harvest/harvest_big/wikisource')
    report = outputs.train_collision_audit({'page': {'lines': [dict(text='ἄνθρωποι', usable=True)]}}, [])
    assert report['collision_occurrences'] == 2 and report['unique_colliding_ids'] == 1
    assert len(report['train_pools']) == 2
    assert all(p.read_bytes() == data for p, data in original.items())


def test_thumbnail_uses_selected_page_requested_width_and_scope():
    import hashlib
    from scripts.harvest.wikisource import thumbnail_url
    page = dict(page=8, scan_file='File:Book.djvu')
    digest = hashlib.md5(b'Book.djvu').hexdigest()
    assert thumbnail_url(page) == f'https://upload.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/Book.djvu/page8-3840px-Book.djvu.jpg'
    assert thumbnail_url(page, host='thumb.wikimedia.org').startswith('https://thumb.wikimedia.org/')
    with pytest.raises(ValueError):
        thumbnail_url(page, host='example.org')


@pytest.mark.parametrize('header,attempt,expected', [({}, 1, 10), ({'Retry-After': '75'}, 2, 75),
    ({'retry-after': '10'}, 5, 160), ({'Retry-After': 'invalid'}, 8, 300),
    ({'Retry-After': 'Thu, 01 Jan 1970 00:02:00 GMT'}, 1, 120)])
def test_backoff_honors_retry_after(header, attempt, expected):
    from scripts.harvest.wikisource import retry_delay
    assert retry_delay(header, attempt, now=0) == expected


def test_image_request_gap_and_retry_bypasses_cached_429(tmp_path):
    class Clock:
        now = 0.
        def time(self): return self.now
        def sleep(self, seconds): self.now += seconds
    clock = Clock(); starts = []
    class Session:
        headers = {}
        def get(self, url, **kwargs):
            from types import SimpleNamespace
            starts.append(clock.time())
            return SimpleNamespace(status_code=429 if len(starts) == 1 else 200,
                                   content=b'body', headers={})
    (tmp_path / 'upload.wikimedia.org.robots.txt').write_text('User-agent: *\nAllow: /\n')
    http = WikimediaHTTP(tmp_path, Session(), clock.time, clock.sleep)
    url = 'https://upload.wikimedia.org/test.jpg'
    assert http.get(url, image=True)[1]['status'] == 429
    assert http.get(url, refresh=True, image=True)[1]['status'] == 200
    assert starts[1] - starts[0] >= 3
    assert len(list(tmp_path.glob('*.html'))) == 2


def test_six_image_attempts_persist_and_only_one_fallback_width(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []; times = []
    class HTTP:
        now = 0.
        def clock(self): return self.now
        def sleep(self, seconds): self.now += seconds
        def get(self, url, **kwargs):
            assert kwargs == dict(refresh=True, image=True)
            times.append(self.now)
            return b'429', dict(status=429, headers={'Retry-After': '10'})
    def resolve(http, page, width, **kwargs):
        widths.append(width)
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    http = HTTP()
    assert collector.fetch_scan(http, dict(id='p1'), standard_width=False)[0] is None
    assert widths == [2500, 2500, 1600, 1600, 1600, 1600]
    assert times == [0, 10, 30, 70, 150, 310]
    assert collector.fetch_scan(http, dict(id='p1'), standard_width=False)[1]['status'] == 'retry_exhausted'
    assert len(widths) == 6


def test_direct_resolution_never_checks_or_calls_api(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    class HTTP:
        def allowed(self, url): pytest.fail('direct resolution requires no network')
        def get(self, *args, **kwargs): pytest.fail('direct resolution requires no network')
    page = dict(id='p1', page=3, scan_file='Book.djvu', thumbnail='/commons/thumb/saved')
    result = collector.resolve_thumbnail(HTTP(), page, 2500)
    assert result['status'] == 'resolved' and result['method'] == 'deterministic_commons_md5'
    assert result['network_request_sent'] is False
    assert collector.resolve_thumbnail(HTTP(), dict(page, thumbnail='/local/images/'), 2500)['status'] == 'hosting_unavailable'


def test_direct_url_unicode_spaces_and_saved_page_number():
    import hashlib
    from urllib.parse import quote
    from scripts.harvest.wikisource import thumbnail_url
    name = 'Έργο_ѣ.pdf'; digest = hashlib.md5(name.encode()).hexdigest()
    page = dict(scan_file='File:Έργο ѣ.pdf', page=17, url='https://el.wikisource.org/wiki/Σελίδα:Έργο_ѣ.pdf/17')
    encoded = quote(name, safe='')
    assert thumbnail_url(page, width=1600) == f'https://upload.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/{encoded}/page17-1600px-{encoded}.jpg'
    with pytest.raises(ValueError, match='saved Page'):
        thumbnail_url(dict(page, page=18))


def test_404_gets_one_1600_fallback_then_stops(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []
    class HTTP:
        def clock(self): return 0
        def sleep(self, seconds): pass
        def get(self, url, **kwargs): return b'404', dict(status=404, headers={})
    def resolve(http, page, width):
        widths.append(width)
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    assert collector.fetch_scan(HTTP(), dict(id='p1'), standard_width=False)[1]['status'] == 'http_permanent_failure'
    assert widths == [2500, 1600]
    collector.fetch_scan(HTTP(), dict(id='p1'), standard_width=False)
    assert widths == [2500, 1600]


def test_width_policy_400_stops_without_unapproved_size_or_retry(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []
    class HTTP:
        def clock(self): return 0
        def get(self, url, **kwargs):
            return b'Use thumbnail sizes listed on https://w.wiki/GHai', dict(status=400, headers={})
    def resolve(http, page, width):
        widths.append(width)
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    http = HTTP()
    assert collector.fetch_scan(http, dict(id='p1'), standard_width=False)[1]['status'] == 'unsupported_thumbnail_width'
    assert collector.fetch_scan(http, dict(id='p1'), standard_width=False)[1]['status'] == 'unsupported_thumbnail_width'
    assert widths == [2500]
    # A later explicit override preserves the first attempt and uses one
    # standard width even when the server still returns the policy error.
    result = collector.fetch_scan(http, dict(id='p1'), standard_width=True)[1]
    assert widths == [2500, 3840, 1920, 1280] and len(result['attempts']) == 4


def test_approved_standard_width_never_downgrades_after_429(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []
    class HTTP:
        now = 0.
        def clock(self): return self.now
        def sleep(self, seconds): self.now += seconds
        def get(self, url, **kwargs): return b'429', dict(status=429, headers={})
    def resolve(http, page, width):
        widths.append(width)
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    assert collector.fetch_scan(HTTP(), dict(id='p1'), standard_width=True)[1]['status'] == 'retry_exhausted'
    assert widths == [3840] * 6


@pytest.mark.parametrize('status', [400, 404])
def test_supported_widths_only_fall_back_after_permanent_size_failure(tmp_path, monkeypatch, status):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []
    class HTTP:
        def clock(self): return 0
        def get(self, url, **kwargs): return b'failure', dict(status=status, headers={})
    def resolve(http, page, width):
        widths.append(width)
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    state = collector.fetch_scan(HTTP(), dict(id='p1'))[1]
    assert widths == [3840, 1920, 1280]
    assert state['status'] == 'http_permanent_failure'
    collector.fetch_scan(HTTP(), dict(id='p1'))
    assert len(widths) == 3


def test_supported_width_fallback_survives_interruption_and_429(tmp_path, monkeypatch):
    from scripts.harvest import wikisource as collector
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    widths = []; statuses = iter([404, 429, 200])
    class HTTP:
        now = 0.
        def clock(self): return self.now
        def sleep(self, seconds): self.now += seconds
        def get(self, url, **kwargs): return b'body', dict(status=next(statuses), headers={})
    def resolve(http, page, width):
        widths.append(width)
        if len(widths) == 2:
            raise KeyboardInterrupt
        return dict(status='resolved', url='https://upload.wikimedia.org/test')
    monkeypatch.setattr(collector, 'resolve_thumbnail', resolve)
    with pytest.raises(KeyboardInterrupt):
        collector.fetch_scan(HTTP(), dict(id='p1'))
    data, state = collector.fetch_scan(HTTP(), dict(id='p1'))
    assert data == b'body' and state['status'] == 'obtained'
    assert widths == [3840, 1920, 1920, 1920]


@pytest.mark.parametrize('finish_on_shortfall,expected_calls', [(True, 1), (False, 2)])
def test_acquisition_shortfall_retains_unattempted_scope(tmp_path, monkeypatch, finish_on_shortfall, expected_calls):
    from scripts.harvest import wikisource as collector, vouli
    monkeypatch.setattr(collector, 'OUT', tmp_path)
    monkeypatch.setattr(vouli, 'check_frozen', lambda: None)
    monkeypatch.setattr(collector, 'WikimediaHTTP', lambda: object())
    (tmp_path / 'selection.json').write_text('{}')
    (tmp_path / 'selected_pages.json').write_text(json.dumps([dict(id='p1'), dict(id='p2')]))
    calls = []
    def fetch(http, page, **kwargs):
        calls.append(page['id'])
        return None, dict(status='retry_exhausted')
    monkeypatch.setattr(collector, 'fetch_scan', fetch)
    collector.acquire(finish_on_shortfall=finish_on_shortfall)
    summary = json.loads((tmp_path / 'acquisition_summary.json').read_text())
    assert len(calls) == expected_calls
    assert summary['finished'] and summary['obtained'] == 0
    assert summary['shortfall_exception_applied'] is finish_on_shortfall
    assert summary['supported_width_attempted_pages'] == 0  # no fabricated receipts


def test_delivery_long_side_cap_without_upsampling():
    import io
    from PIL import Image
    from scripts.harvest.wikisource import delivery_image
    raw = io.BytesIO(); Image.new('RGB', (2500, 4200), 'white').save(raw, format='JPEG')
    image, _, served = delivery_image(raw.getvalue())
    assert image.mode == 'L' and max(image.size) == 3500 and served == (2500, 4200)
    raw = io.BytesIO(); Image.new('L', (1600, 2400), 255).save(raw, format='JPEG')
    assert delivery_image(raw.getvalue(), fallback=True)[0].size == (1600, 2400)
    with pytest.raises(ValueError):
        delivery_image(raw.getvalue())


def test_docai_transport_removes_only_embedded_image_before_persistence(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from scripts.harvest import wikisource as collector
    raw = dict(document=dict(text='ἀνθρώπων', pages=[dict(image=dict(content='large base64', width=2500),
               lines=[dict(layout=dict(confidence=.98))])]))
    monkeypatch.setattr(collector.requests, 'post', lambda *a, **kw:
        SimpleNamespace(status_code=200, headers={'x-request-id': 'fixture'}, json=lambda: raw))
    response = collector.compact_docai_transport('unused')
    compact = response.json()
    assert compact['document']['pages'][0]['image'] == dict(width=2500)
    assert compact['document']['text'] == 'ἀνθρώπων'
    assert compact['document']['pages'][0]['lines'][0]['layout']['confidence'] == .98
    from PIL import Image
    from greekocr.readers.services.google_docai import DocAIReader
    image = tmp_path / 'input.png'; Image.new('L', (20, 20), 255).save(image)
    class Credentials:
        def before_request(self, *args): pass
    reader = DocAIReader('test', 'eu', 'test', receipts_dir=tmp_path / 'receipts',
                         transport=collector.compact_docai_transport, credentials=Credentials())
    reading = reader.read(image)
    saved = json.loads(Path(reading.raw_json_path).read_text())
    assert 'content' not in saved['document']['pages'][0]['image']


@pytest.mark.parametrize('count,finished,allowed', [(0, True, False), (1, False, False), (1, True, True)])
def test_partial_read_plan_requires_finished_acquisition_and_at_least_one_image(tmp_path, monkeypatch, count, finished, allowed):
    from scripts.harvest import wikisource as collector, vouli, round1
    out = tmp_path / 'out'; out.mkdir()
    monkeypatch.setattr(collector, 'ROOT', tmp_path)
    monkeypatch.setattr(collector, 'OUT', out)
    monkeypatch.setattr(collector, 'BULK', tmp_path / 'bulk')
    monkeypatch.setattr(vouli, 'check_frozen', lambda: None)
    monkeypatch.setattr(round1, 'OUT', tmp_path / 'prior')
    previous = round1.OUT / 'reads_d1'; previous.mkdir(parents=True)
    binding = dict(options=dict(ocrConfig=dict(hints=dict(languageHints=['el']), enableSymbol=True)))
    (previous / 'plan.json').write_text(json.dumps(dict(bindings=dict(docai=binding))))
    image = tmp_path / 'page.png'; image.write_bytes(b'fixture image identity')
    pages = [dict(id='p1', image='page.png', image_sha256=vouli.sha(image), harvest_accepted=False)] * count
    (out / 'manifest.json').write_text(json.dumps(pages))
    (out / 'acquisition_summary.json').write_text(json.dumps(dict(finished=finished)))
    (out / 'transcriptions').mkdir(); (out / 'transcriptions/p1.json').write_text('{}')
    for name in ('source_books.json', 'selected_pages.json', 'holdout_books.json', 'selection.json'):
        (out / name).write_text('[]')
    if allowed:
        plan = collector.prepare_plan()
        assert plan['page_count'] == 1 and plan['pages_accepted'] == 0
        assert plan['max_cost_usd'] == .0015 and plan['vision_calls'] == 0
        assert plan['binding']['options']['ocrConfig']['hints']['languageHints'] == []
    else:
        with pytest.raises(ValueError, match='at least one image'):
            collector.prepare_plan()
