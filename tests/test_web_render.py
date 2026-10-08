"""No live HTTP: browser fixtures are local; source transport tests use recorded responses."""
from __future__ import annotations

import hashlib
import ctypes
import json
import os
from pathlib import Path
import unicodedata
import struct

from PIL import Image
import pytest

from greekocr.cli import main
from greekocr.real.sources.web_render import (degrade_twins, page_records, records_from_dom,
                                             records_from_pdf, render_pages)
from greekocr.real.sources.web_sources import (_PoliteHTTP, mastodon_post_html,
                                              source_catalog, source_pages)

FIXTURES = Path(__file__).parent / 'web_fixtures'
ROOT = Path(__file__).resolve().parents[1]
NAMES = ('polytonic', 'government', 'news')


@pytest.fixture(scope='module')
def chromium():
    playwright = pytest.importorskip('playwright.sync_api', reason='optional playwright is absent')
    if 'PLAYWRIGHT_BROWSERS_PATH' not in os.environ and (ROOT / '.playwright').exists():
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(ROOT / '.playwright')
    with playwright.sync_playwright() as driver:
        try:
            browser = driver.chromium.launch(headless=True)
        except playwright.Error as error:
            pytest.skip('Chromium absent or unable to launch in sandbox: ' + str(error).splitlines()[0])
        browser.close()


@pytest.fixture(scope='module')
def rendered(chromium, tmp_path_factory):
    root = tmp_path_factory.mktemp('web-render')
    inputs = [dict(url=str(FIXTURES / (name + '.html')), licence='CC0-1.0; authored test fixture') for name in NAMES]
    return (render_pages(inputs, root / 'first', offline=True),
            render_pages(inputs, root / 'second', offline=True))


@pytest.mark.parametrize('index', range(3), ids=NAMES)
def test_dom_nodes_and_scaled_geometry(rendered, index):
    page = rendered[0][index]
    dom = json.loads(Path(page.dom_path).read_text())
    assert len(dom['lines']) >= 10
    for node in dom['nodes']:
        if node['text_raw'].strip() and not node.get('excluded'):
            assert node['line_ids'], node
            fragments = [dom['lines'][i] for i in node['line_ids']]
            assert all(line['node_id'] == node['node_id'] for line in fragments)
            actual = ''.join(line['text'] for line in fragments)
            # Range may suppress collapsed spaces at line boundaries.
            assert ''.join(actual.split()) == ''.join(unicodedata.normalize('NFC', node['text_raw']).split())
    for line in dom['lines']:
        assert line['text'] and line['bbox_css'][2] > line['bbox_css'][0]
        assert line['bbox_css'][3] > line['bbox_css'][1]
        assert line['bbox_pixel'] == [v * 2 for v in line['bbox_css']]
    records = records_from_dom(page.png_path, page.dom_path)
    assert len(records) == len(dom['lines'])
    assert all(r['tier'] == 'exact-rendered' and r['provenance'] == 'web_render' for r in records)
    assert all(r['source_url'] == page.receipt['final_url'] and r['licence'].startswith('CC0') for r in records)


@pytest.mark.parametrize('index', range(3), ids=NAMES)
def test_receipts_and_embedded_fonts(rendered, index):
    page = rendered[0][index]
    receipt = json.loads(Path(page.receipt_path).read_text())
    for key in ('url', 'fetched_at', 'final_url', 'status', 'title', 'lang', 'sha256',
                'fonts', 'computed_font_families', 'licence', 'user_agent', 'chromium_version'):
        assert key in receipt
    assert receipt['lang'] == 'el'
    assert receipt['title'] and receipt['computed_font_families']
    assert receipt['status'] in (0, None)  # file navigation has no HTTP status
    assert receipt['determinism']['fonts_awaited']
    assert receipt['determinism']['javascript'] is False
    for key, filename in receipt['files'].items():
        assert receipt['sha256'][key] == hashlib.sha256((Path(page.receipt_path).parent / filename).read_bytes()).hexdigest()
    assert b'/FontFile' in Path(page.pdf_path).read_bytes()
    with Image.open(page.png_path) as image:
        assert image.width == 794 * 2 and image.height >= 1123 * 2


@pytest.mark.parametrize('index', range(3), ids=NAMES)
def test_pdf_independently_matches_dom(rendered, index):
    page = rendered[0][index]
    rows = records_from_pdf(page.pdf_path)
    agreement = json.loads((Path(page.pdf_path).parent / 'page_records/agreement.json').read_text())
    assert len(rows) >= 10
    assert agreement['pdf_text_agreement'] >= .95, agreement
    assert agreement['dom_text_coverage'] >= .95, agreement
    assert agreement['mean_iou'] > .4, agreement
    assert all(r['bbox_pdf'] and r['bbox_pixel'] and Path(r['crop_path']).exists() for r in rows)
    assert all(r['text'] == unicodedata.normalize('NFC', r['text']) for r in rows)
    assert all(r['tier'] == 'exact-rendered' and r['provenance'] == 'web_render' for r in rows)


@pytest.mark.parametrize('index', range(3), ids=NAMES)
def test_deterministic_boxes(rendered, index):
    first, second = (json.loads(Path(group[index].dom_path).read_text()) for group in rendered)
    assert first['lines'] == second['lines']
    assert first['nodes'] == second['nodes']
    assert rendered[0][index].receipt['sha256']['png'] == rendered[1][index].receipt['sha256']['png']


def test_browser_cli_and_checksum_guard(chromium, tmp_path, capsys):
    destination = tmp_path / 'cli'
    assert main(['web', 'render', '--sources', str(FIXTURES / 'polytonic.html'),
                 '--max-pages', '1', '--dest', str(destination), '--offline', '--licence', 'CC0-1.0']) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result['pages']) == 1
    assert main(['web', 'records', str(destination)]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary['pages'][0]['dom_records'] > 0 and summary['pages'][0]['pdf_records'] > 0
    Path(result['pages'][0]['html_path']).write_text('changed')
    assert main(['web', 'records', str(destination)]) == 3
    assert 'checksum mismatch' in capsys.readouterr().err


def test_offline_blocks_browser_network_and_media(chromium, tmp_path):
    page = render_pages([dict(url='https://recorded.invalid/page', html='''
        <html lang="el"><link rel="stylesheet" href="https://forbidden.invalid/style.css">
        <body><p>Τοπικό κείμενο</p><img src="https://forbidden.invalid/image.png"></body></html>''')],
                        tmp_path, offline=True, print_to_pdf=False)[0]
    assert page.pdf_path is None and page.print_dom_path is None
    assert page.receipt['sha256']['pdf'] is None
    assert {r['reason'] for r in page.receipt['blocked_requests']} == {'offline', 'block_media'}


def test_print_reflow_and_pdf_only(chromium, tmp_path):
    page = render_pages([FIXTURES / 'government.html'], tmp_path, viewport=(480, 700),
                        scale=1.5, screenshot=False, offline=True)[0]
    assert page.png_path is None and page.receipt['sha256']['png'] is None
    screen = json.loads(Path(page.dom_path).read_text())
    printed = json.loads(Path(page.print_dom_path).read_text())
    assert screen['scale'] == 1.5 and printed['scale'] == 1
    assert screen['width'] != printed['width']
    assert page_records(tmp_path)['pages'][0]['pdf_records'] > 0


def test_catalog_seeds_no_network_and_news_round_robin():
    catalog = source_catalog()
    assert all(r['interval'] >= 1 and r['robots'] and r['licence'] for r in catalog.values())
    assert {'wikipedia-random', 'wikipedia-featured', 'wikisource', 'gov', 'eur-lex', 'mastodon', 'gutenberg'} <= catalog.keys()
    for name in catalog.keys() - {'mastodon'}:
        assert len(list(source_pages([name], 1))) == 1
    news = list(source_pages(['news'], 3))
    assert {r['source'] for r in news} == {'news-kathimerini', 'news-naftemporiki', 'news-efsyn'}
    assert len(list(source_pages(['wikipedia-random'], 3))) == 3
    category = list(source_pages(['wikisource'], 1, category='Αρχαία ελληνική ποίηση'))[0]
    assert '%CE' in category['url']


def test_article_discovery_uses_polite_transport():
    class Client:
        def get(self, url):
            return dict(status=200, url=url, body=b'<a href="/article/123">story</a><a href="https://other.invalid/x">offsite</a>')
    rows = list(source_pages(['news-efsyn'], 3, client=Client()))
    assert [r['url'] for r in rows] == ['https://www.efsyn.gr/', 'https://www.efsyn.gr/article/123']


def test_mastodon_json_public_only_and_inert_html():
    public = dict(visibility='public', url='https://social.invalid/@user/1',
                  content='<p>Ἀλήθεια &amp; λέξεις<br>δεύτερη γραμμή</p><script>bad()</script>',
                  account=dict(display_name='Δοκιμή <test>'))
    class Client:
        def get(self, url):
            return dict(status=200, url=url, body=json.dumps([public, dict(public, visibility='unlisted')]).encode())
    rows = list(source_pages(['mastodon'], 2, client=Client(), mastodon_instance='https://social.invalid'))
    assert len(rows) == 1 and rows[0]['source_json'] == public
    rendered = mastodon_post_html(public)
    assert '<script' not in rendered and 'bad()' not in rendered and '&lt;test&gt;' in rendered
    assert 'Ἀλήθεια &amp; λέξεις\nδεύτερη γραμμή' in rendered


def test_robots_redirect_and_rate_gate(monkeypatch):
    clock = [0.0]
    pauses = []
    def sleep(seconds):
        pauses.append(seconds)
        clock[0] += seconds
    monkeypatch.setattr('greekocr.real.sources.web_sources.time.monotonic', lambda: clock[0])
    monkeypatch.setattr('greekocr.real.sources.web_sources.time.sleep', sleep)
    client = _PoliteHTTP()
    visited = []
    def request(url):
        visited.append(url)
        if url.endswith('/robots.txt'):
            body = b'User-agent: *\nDisallow: /private\nCrawl-delay: 2\n'
            return dict(url=url, status=200, body=body, headers={})
        if url.endswith('/redirect'):
            return dict(url=url, status=302, body=b'', headers={'Location': 'https://b.invalid/private'})
        return dict(url=url, status=200, body=b'page', headers={})
    monkeypatch.setattr(client, '_request', request)
    assert client.get('https://a.invalid/page')['body'] == b'page'
    with pytest.raises(ValueError, match='robots disallows'):
        client.get('https://a.invalid/redirect')
    assert 'https://b.invalid/robots.txt' in visited and 'https://b.invalid/private' not in visited
    assert pauses == [2.0, 2.0]
    with pytest.raises(ValueError, match='>=1'):
        _PoliteHTTP(interval=.1)


def test_robots_missing_and_unavailable(monkeypatch):
    monkeypatch.setattr('greekocr.real.sources.web_sources.time.sleep', lambda _: None)
    allowed = _PoliteHTTP()
    monkeypatch.setattr(allowed, '_request', lambda url: dict(url=url, status=404, body=b'', headers={}) if url.endswith('robots.txt') else dict(url=url, status=200, body=b'OK', headers={}))
    assert allowed.get('https://missing.invalid/page')['body'] == b'OK'
    blocked = _PoliteHTTP()
    monkeypatch.setattr(blocked, '_request', lambda url: dict(url=url, status=503, body=b'', headers={}))
    with pytest.raises(ValueError, match='robots unavailable'):
        blocked.get('https://blocked.invalid/page')


def test_dom_direct_records_and_validation(tmp_path):
    image = tmp_path / 'page.png'
    Image.new('RGB', (100, 50), 'white').save(image)
    lines = [dict(text='α\u0313', bbox_pixel=[2, 3, 80, 30])]
    receipt = dict(page_id='test', final_url='https://recorded.invalid', licence='CC0-1.0')
    rows = records_from_dom(image, lines, receipt=receipt)
    assert rows[0]['text'] == 'ἀ' and rows[0]['bbox_pixel'] == [2, 3, 80, 30]
    assert rows[0]['source_url'] == receipt['final_url']
    with pytest.raises(ValueError, match='invalid DOM'):
        records_from_dom(image, [dict(text='bad', bbox_pixel=[0, 0, 0, 1])])


def test_degradation_stub_preserves_labels(tmp_path):
    labels = [dict(text='Ἀλήθεια', bbox_pixel=[1, 2, 3, 4])]
    result = degrade_twins(tmp_path / 'page.png', labels)
    assert result['status'] == 'unavailable' and result['labels'] == labels
    assert 'not vendored' in result['reason']
    assert result['labels'] is not labels


def test_cli_validation_without_browser(tmp_path, capsys):
    assert main(['web', 'records', str(tmp_path)]) == 3
    assert 'no web render receipts' in capsys.readouterr().err
    assert main(['web', 'render', '--sources', 'gov', '--dest', str(tmp_path), '--offline']) == 3
    assert 'offline render requires' in capsys.readouterr().err
    assert main(['web', 'render', '--sources', 'gov', '--dest', str(tmp_path), '--max-pages', '0']) == 3
    assert 'positive' in capsys.readouterr().err


def test_recorded_wikisource_capture_if_available():
    receipt_path = FIXTURES / 'wikisource_capture/capture_receipt.json'
    if not receipt_path.exists():
        pytest.skip('optional Wikisource fixture was not captured')
    receipt = json.loads(receipt_path.read_text())
    if receipt['capture_status'] != 'captured':
        pytest.skip('Wikisource fixture capture unavailable: ' + receipt.get('reason', 'unknown'))
    body = (receipt_path.parent / 'source.html').read_bytes()
    assert hashlib.sha256(body).hexdigest() == receipt['html_sha256']
    assert receipt['status'] == 200 and receipt['robots_respected'] and receipt['interval'] >= 1


def test_pdf_wrapper_does_not_replace_failed_labels(monkeypatch, tmp_path):
    pdf = tmp_path / 'empty.pdf'
    pdf.write_bytes(b'local fake; extractor mocked')
    image = Image.new('L', (200, 200), 255)
    candidates = [dict(text='different', bbox_pixel=[10, 10, 100, 30],
                       char_bbox_pixel=[12, 12, 98, 28], bbox_pdf=[1, 2, 3, 4])]
    monkeypatch.setattr('greekocr._vendor.bench.o4b_textlayer_lines.pdf_pages',
                        lambda _: iter([(1, image, candidates, None), (2, None, [], 'no_text_layer')]))
    dom = dict(lines=[dict(text='Ἀλήθεια', bbox_css=[1, 2, 3, 4])])
    rows = records_from_pdf(pdf, dom_lines=dom)
    assert rows[0]['text'] == 'different' and rows[0]['dom_agreement']['text_match'] is False
    agreement = json.loads((tmp_path / 'empty_records/agreement.json').read_text())
    assert agreement['pdf_text_agreement'] == 0 and agreement['dom_text_coverage'] == 0
    assert agreement['failures'] == [dict(page=2, error='no_text_layer')]


def test_real_born_digital_pdf_extraction_without_browser(tmp_path):
    """Exercise the actual vendored extractor even when Chromium cannot launch."""
    import pypdfium2 as pdfium
    font_path = next((path for path in (Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
                                        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
                      if path.exists()), None)
    if font_path is None:
        pytest.skip('no local Greek-capable TrueType font for PDFium fixture')
    raw = pdfium.raw
    font_data = font_path.read_bytes()
    font_buffer = (ctypes.c_ubyte * len(font_data)).from_buffer_copy(font_data)
    texts = ['Ἀλήθεια\u00a0καὶ\u00a0λέξεις', 'Ελληνικά\u00a0και\u00a0English\u00a0123']
    path = tmp_path / 'native.pdf'
    with pdfium.PdfDocument.new() as document:
        font = raw.FPDFText_LoadFont(document, font_buffer, len(font_data), raw.FPDF_FONT_TRUETYPE, 1)
        assert font
        page = document.new_page(300, 300)
        try:
            for index, text in enumerate(texts):
                obj = raw.FPDFPageObj_CreateTextObj(document, font, 18)
                encoded = text.encode('utf-16-le') + b'\0\0'
                words = struct.unpack('<' + 'H' * (len(encoded) // 2), encoded)
                buffer = (ctypes.c_ushort * len(words))(*words)
                assert raw.FPDFText_SetText(obj, buffer)
                raw.FPDFPageObj_Transform(obj, 1, 0, 0, 1, 20, 250 - index * 40)
                raw.FPDFPage_InsertObject(page, obj)
            page.gen_content()
            document.save(path)
        finally:
            page.close()
            raw.FPDFFont_Close(font)
    receipt = dict(final_url='fixture:native-pdf', licence='CC0-1.0; authored fixture text')
    rows = records_from_pdf(path, receipt=receipt)
    assert [row['text'] for row in rows] == texts
    assert all(row['font_names'] and row['source_url'] == 'fixture:native-pdf' for row in rows)
    assert all(row['bbox_pdf'][2] > row['bbox_pdf'][0] and Path(row['crop_path']).exists() for row in rows)
    report = json.loads((tmp_path / 'native_records/agreement.json').read_text())
    assert report['pdf_text_agreement'] is None and report['pdf_lines'] == 2


@pytest.mark.parametrize('options', [dict(viewport=(0, 100)), dict(scale=0), dict(scale=float('nan')),
                                    dict(viewport=(1, 2, 3)), dict(timeout=0), dict(interval=.5),
                                    dict(interval=float('nan')), dict(timeout=float('inf'))])
def test_invalid_render_options_fail_before_browser(options, tmp_path):
    with pytest.raises(ValueError):
        render_pages([], tmp_path, **options)
    assert not list(tmp_path.iterdir())


def test_cli_named_seeds_and_render_arguments_without_browser(monkeypatch, tmp_path, capsys):
    captured = {}
    def render(inputs, destination, **kwargs):
        captured.update(inputs=list(inputs), destination=destination, **kwargs)
        return []
    monkeypatch.setattr('greekocr.real.sources.web_render.render_pages', render)
    assert main(['web', 'render', '--sources', 'news-kathimerini', 'news-naftemporiki', 'news-efsyn',
                 '--dest', str(tmp_path), '--max-pages', '3', '--viewport', '900x600', '--scale', '1.5',
                 '--no-pdf', '--allow-media', '--interval', '2', '--timeout', '60']) == 0
    assert {r['source'] for r in captured['inputs']} == {'news-kathimerini', 'news-naftemporiki', 'news-efsyn'}
    assert captured['viewport'] == (900, 600) and captured['scale'] == 1.5
    assert captured['print_to_pdf'] is False and captured['block_media'] is False
    assert captured['interval'] == 2 and captured['timeout'] == 60
    assert json.loads(capsys.readouterr().out) == {'pages': []}


def test_cli_manifest_resolves_relative_paths(monkeypatch, tmp_path, capsys):
    captured = []
    def render(inputs, destination, **kwargs):
        captured.extend(inputs)
        assert kwargs['offline']
        return []
    monkeypatch.setattr('greekocr.real.sources.web_render.render_pages', render)
    manifest = tmp_path / 'sources.json'
    manifest.write_text(json.dumps(dict(pages=[dict(path='fixture.html', licence='CC0-1.0'),
                                                dict(url='https://recorded.invalid', html='<p>Recorded</p>', licence='caller')])))
    assert main(['web', 'render', '--sources', str(manifest), '--dest', str(tmp_path / 'out'), '--offline']) == 0
    assert captured[0]['url'] == str(tmp_path / 'fixture.html') and captured[0]['licence'] == 'CC0-1.0'
    assert captured[1]['url'] == 'https://recorded.invalid' and captured[1]['licence'] == 'caller'
    capsys.readouterr()


def test_receipt_verification_and_dom_export_without_browser(tmp_path):
    work = tmp_path / 'page'
    work.mkdir()
    Image.new('RGB', (100, 60), 'white').save(work / 'page.png')
    (work / 'source.html').write_text('<p>Ἀλήθεια</p>')
    (work / 'dom.json').write_text(json.dumps(dict(lines=[dict(text='Ἀλήθεια', bbox_pixel=[1, 2, 80, 25])]), ensure_ascii=False))
    files = dict(html='source.html', png='page.png', dom='dom.json', pdf=None)
    hashes = {key: hashlib.sha256((work / filename).read_bytes()).hexdigest() if filename else None
              for key, filename in files.items()}
    receipt = dict(page_id='fixture', files=files, sha256=hashes, final_url='fixture:html', licence='CC0-1.0')
    (work / 'receipt.json').write_text(json.dumps(receipt))
    summary = page_records(tmp_path)
    assert summary['pages'][0]['dom_records'] == 1
    row = json.loads((work / 'dom_records.jsonl').read_text())
    assert row['source_url'] == 'fixture:html' and row['text'] == 'Ἀλήθεια'
    (work / 'source.html').write_text('changed')
    with pytest.raises(ValueError, match='checksum mismatch'):
        page_records(tmp_path)
