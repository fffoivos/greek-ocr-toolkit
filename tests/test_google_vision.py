"""T11 offline adapter, engine and comparison contracts; all HTTP is mocked."""
from copy import deepcopy
import base64
import json
from pathlib import Path
from types import SimpleNamespace
import unicodedata

from PIL import Image
import pytest

from greekocr.readers.services.google_vision import VisionError, VisionReader, _reading, load_google_vision
from prototypes.harvest import google_failed_lines as audit
from prototypes.harvest.vision_comparison import agreement, compare_rows, comparison_metrics

FIXTURE = Path(__file__).parent / 'data/vision_failed_lines'


def sample():
    return json.loads((FIXTURE / 'response.json').read_text())


class Credentials:
    calls = 0
    def before_request(self, *args):
        self.calls += 1


@pytest.fixture
def setup(tmp_path):
    crop = tmp_path / 'crop.png'
    Image.new('L', (100, 20), 255).save(crop)
    calls = []
    raw = sample()
    def transport(url, **kw):
        calls.append(dict(url=url, **kw))
        return SimpleNamespace(status_code=200, headers={'x-goog-request-id': 'recorded-request'},
                               json=lambda: deepcopy(raw), text='')
    reader = VisionReader('fixture-quota', responses_dir=tmp_path / 'responses',
                          credentials=Credentials(), transport=transport)
    return reader, crop, calls, raw


def test_rest_request_nfd_text_full_hierarchy_and_confidence(setup):
    reader, crop, calls, raw = setup
    r = reader.read_annotation(crop)
    assert r.text == unicodedata.normalize('NFD', raw['responses'][0]['fullTextAnnotation']['text'])
    assert r.raw_text == 'ἅλφα β\nϗ\n' and r.lines == ['ἅλφα β', 'ϗ']
    assert r.annotation == raw['responses'][0]['fullTextAnnotation']
    assert len(r.blocks) == len(r.paragraphs) == 1 and len(r.token_confidences) == 2
    assert [s['text'] for s in r.symbol_confidences] == list('ἅλφαβϗ')
    assert r.blocks[0]['text'] == r.raw_text and r.blocks[0]['bounding_box']['vertices']
    assert r.mean_symbol_conf == pytest.approx(4.1/6) and r.min_symbol_conf == .5
    assert {x['languageCode'] for x in r.detected_languages} == {'el', 'grc'}
    assert r.line_confidences == [.88, .88]
    call = calls[0]
    assert call['url'] == 'https://vision.googleapis.com/v1/images:annotate'
    request = call['json']['requests'][0]
    assert request['features'] == [{'type': 'DOCUMENT_TEXT_DETECTION'}]
    assert request['imageContext'] == {'languageHints': ['el', 'grc']}
    assert base64.b64decode(request['image']['content']) == crop.read_bytes()
    assert call['headers']['x-goog-user-project'] == 'fixture-quota'
    assert json.loads((reader.responses_dir / (r.crop_sha256 + '.json')).read_text())['language_hints'] == ['el', 'grc']


def test_read_returns_nfd_and_duplicate_sha_never_calls_again(setup, tmp_path):
    reader, crop, calls, _ = setup
    first = reader.read(crop)
    other = tmp_path / 'other.png'
    other.write_bytes(crop.read_bytes())
    assert reader.read(other) == first and len(calls) == reader._credentials.calls == 1
    assert reader.read_annotation(other).cached
    assert len(list(reader.responses_dir.glob('*.json'))) == 1
    reloaded = VisionReader('fixture-quota', responses_dir=reader.responses_dir,
                           transport=lambda *a, **k: pytest.fail('cache called HTTP'))
    assert reloaded.read(crop) == first


@pytest.mark.parametrize('changed', ['binding', 'raw', 'envelope', 'crop'])
def test_changed_cache_or_crop_rejected_without_call(setup, changed):
    reader, crop, calls, _ = setup
    r = reader.read_annotation(crop)
    if changed == 'binding':
        reader.language_hints = ('el',)
    elif changed == 'raw':
        Path(r.raw_json_path).write_text('{}')
    elif changed == 'envelope':
        path = reader.responses_dir / (r.crop_sha256 + '.json')
        data = json.loads(path.read_text()); data['response_sha256'] = 'wrong'
        path.write_text(json.dumps(data))
    else:
        with pytest.raises(ValueError, match='crop changed'):
            reader.read_annotation(crop, expected_sha256='wrong')
        assert len(calls) == 1
        return
    with pytest.raises(ValueError, match='mismatch|changed'):
        reader.read(crop)
    assert len(calls) == 1


@pytest.mark.parametrize('status,raw', [(403, {'error': {'status': 'PERMISSION_DENIED', 'message': 'billing disabled'}}),
    (200, {'responses': [{'error': {'code': 7, 'message': 'API not enabled'}}]}),
    (200, {'responses': []})])
def test_http_or_embedded_error_is_retained_and_never_retried(setup, status, raw):
    reader, crop, calls, _ = setup
    def failed(*a, **k):
        calls.append(k)
        return SimpleNamespace(status_code=status, headers={}, text='', json=lambda: raw)
    reader._transport = failed
    with pytest.raises(VisionError):
        reader.read(crop)
    with pytest.raises(VisionError, match='refusing automatic re-call'):
        reader.read(crop)
    assert len(calls) == 1
    ledger = [json.loads(s) for s in reader.ledger_path.read_text().splitlines()]
    assert ledger[0]['status'] == 'error' and ledger[0]['language_hints'] == ['el', 'grc']
    assert json.loads(Path(ledger[0]['raw_json_path']).read_text()) == raw


def test_transport_error_has_unknown_billing_no_retry(setup):
    reader, crop, _, _ = setup
    def failed(*a, **k):
        raise TimeoutError('fixture timeout')
    reader._transport = failed
    with pytest.raises(VisionError, match='timeout'):
        reader.read(crop)
    with pytest.raises(VisionError, match='refusing automatic re-call'):
        reader.read(crop)
    row = json.loads(reader.ledger_path.read_text())
    assert row['images_billed'] is None and row['raw_json_path'] is None


def test_empty_protojson_response_and_metrics():
    r = _reading({'responses': [{}]}, {})
    assert r.text == '' and r.lines == [] and r.mean_symbol_conf is None
    metrics = audit.crop_metrics({'responses': [{}]}, 100, 20, engine='vision')
    assert metrics['empty'] and metrics['lines_returned'] == 0 and metrics['symbol_count'] == 0


def test_vision_metric_preserves_raw_codepoints_and_reported_breaks():
    m = audit.crop_metrics(sample(), 100, 20, engine='vision')
    assert m['text'] == 'ἅλφα β\nϗ\n' and m['total_characters'] == 7
    assert m['characters_per_100px_width'] == 7 and m['lines_returned'] == 2
    assert m['paragraphs_returned'] == 1 and m['symbol_count'] == 6
    assert 'paragraph confidence' in m['line_count_source']


def test_prefix_space_hyphen_paragraph_boundaries_and_null_confidence():
    raw = sample()
    p = raw['responses'][0]['fullTextAnnotation']['pages'][0]['blocks'][0]['paragraphs'][0]
    p['words'] = [dict(symbols=[dict(text='α', property=dict(detectedBreak=dict(type='SPACE', isPrefix=True))),
        dict(text='β', property=dict(detectedBreak=dict(type='HYPHEN'))), dict(text='γ')])]
    p.pop('confidence')
    r = _reading(raw, {})
    assert r.lines == [' αβ', 'γ'] and r.line_confidences == [None, None]
    assert r.mean_symbol_conf is None


def test_factory_gate_and_lazy_adc(setup, monkeypatch):
    monkeypatch.delenv('GREEKOCR_ENABLE_GOOGLE_VISION', raising=False)
    with pytest.raises(ValueError, match='disabled'):
        load_google_vision(user_project='fixture')
    monkeypatch.setenv('GREEKOCR_ENABLE_GOOGLE_VISION', '1')
    monkeypatch.setenv('GOOGLE_CLOUD_QUOTA_PROJECT', 'fixture')
    assert load_google_vision().user_project == 'fixture'
    import google.auth
    reader, crop, _, _ = setup
    credentials, calls = Credentials(), []
    def adc(**kw):
        calls.append(kw); return credentials, None
    reader._credentials = None
    monkeypatch.setattr(google.auth, 'default', adc)
    reader.read(crop); reader.read(crop)
    assert calls == [dict(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id='fixture-quota')]


@pytest.mark.parametrize('a,b,edits,equal,rare', [('ἅ', 'α\u0314\u0301', 0, True, False),
    ('και', 'ϗ', 3, False, False), ('σ', 'ϲ', 1, False, True), ('ϗ', 'κ', 1, False, True),
    ('ϗa', 'ϗb', 1, False, False), ('', '', 0, True, False), ('', 'ϛ', 1, False, True),
    ('a\n', 'a', 1, False, False)])
def test_comparison_strict_nfd_and_rare_only_alignment(a, b, edits, equal, rare):
    m = comparison_metrics(a, b)
    assert m['nfd_edits'] == edits and m['nfd_equal'] == equal
    assert m['rare_only_disagreement'] == rare
    if not a and b:
        assert m['nfd_cer_docai_reference'] is None


def test_agreement_denominators_missing_empty_and_directions():
    pairs = [comparison_metrics('α', 'α'), comparison_metrics('αβ', 'α')]
    pairs.append(dict(nfd_equal=None))
    result = agreement(pairs)
    assert result['n_crops'] == 3 and result['n_paired'] == 2
    assert result['nfd_agreement_rate'] == .5
    assert result['pooled_nfd_cer_docai_reference'] == pytest.approx(1/3)
    assert result['pooled_nfd_cer_vision_reference'] == .5


def test_compare_rejects_different_crop_bytes(tmp_path):
    v = dict(crop_id='x', crop_sha256='a', source='Vouli', failure_type='control', failure_types=['control'], status='pending')
    with pytest.raises(ValueError, match='SHA mismatch'):
        compare_rows([v], [dict(v, crop_sha256='b')], tmp_path)


@pytest.mark.parametrize('engine', ['docai', 'vision'])
def test_cli_engine_switch_default_and_include_anemi(monkeypatch, tmp_path, engine):
    calls = []
    def run(*args, **kw):
        calls.append(kw)
        assert audit.ALLOW_ANEMI
        return dict(status='complete')
    monkeypatch.setattr(audit, 'run', run)
    monkeypatch.setattr(audit, 'ALLOW_ANEMI', False)
    argv = ['--include-anemi', '--out', str(tmp_path)]
    if engine == 'vision': argv += ['--engine', 'vision', '--language-hints', 'el', 'grc']
    assert audit.main(argv) == 0
    assert calls[0]['engine'] == engine


def test_offline_miss_cannot_reach_adc(setup, tmp_path):
    reader, crop, calls, _ = setup
    row = dict(page='s2-fixture', crop_path=str(crop), crop_id='fixture', crop_sha256=audit.sha256(crop))
    with pytest.raises(ValueError, match='offline cache miss'):
        audit.cached_response(row, tmp_path, reader, offline=True, engine='vision')
    assert calls == []


def test_engine_run_builds_both_readings_and_deduplicates_anemi(tmp_path, monkeypatch):
    import shutil
    from greekocr.readers.services.google_docai import DocAIReader, DEFAULT_VERSION
    directory = tmp_path / 'catalogue'
    shutil.copytree(Path(__file__).parent / 'data/docai_failed_lines', directory)
    (directory / 'page_comments.json').write_text(json.dumps(dict(effects={'multi_line_segment':'two lines'}, records=[])))
    out = tmp_path / 'reports'
    monkeypatch.setattr(audit, 'ALLOW_ANEMI', True)
    calls = []
    def transport(raw):
        def post(*a, **k):
            calls.append(k)
            return SimpleNamespace(status_code=200, headers={}, json=lambda: raw, text='')
        return post
    dr = DocAIReader('fixture-quota', 'eu', 'processor', DEFAULT_VERSION,
        receipts_dir=out / 'docai_failed_lines/adapter_receipts', credentials=Credentials(),
        transport=transport(json.loads((directory / 'response.json').read_text())))
    assert audit.run(directory, out, reader=dr)['status'] == 'complete'
    vr = VisionReader('fixture-quota', responses_dir=out / 'vision_failed_lines/responses',
        credentials=Credentials(), transport=transport(sample()))
    rec = audit.run(directory, out, reader=vr, engine='vision')
    assert rec['status'] == 'complete' and rec['calls'] == 1 and rec['measured_crop_ids'] == 3
    assert rec['rare_glyph_crops_vision'] == 3 and len(calls) == 2
    html = (out / 'vision_vs_docai_review.html').read_text()
    assert html.count('<article') == html.count('<h4>Document AI</h4>') == html.count('<h4>Cloud Vision</h4>') == 3
    assert 'Anemi included: **True**' in (out / 'VISION_VS_DOCAI_v1.md').read_text()
    audit.run(directory, out, reader=vr, engine='vision', offline=True)
    assert len(calls) == 2


def test_permission_error_stops_full_runner_and_writes_partial_receipt(tmp_path, monkeypatch):
    import shutil
    directory = tmp_path / 'catalogue'
    shutil.copytree(Path(__file__).parent / 'data/docai_failed_lines', directory)
    (directory / 'page_comments.json').write_text(json.dumps(dict(effects={'multi_line_segment':'two lines'}, records=[])))
    out, calls = tmp_path / 'reports', []
    def failed(*a, **k):
        calls.append(k)
        return SimpleNamespace(status_code=403, headers={}, text='', json=lambda: dict(error=dict(message='API not enabled')))
    reader = VisionReader('fixture', responses_dir=out / 'vision_failed_lines/responses',
                          credentials=Credentials(), transport=failed)
    rec = audit.run(directory, out, reader=reader, engine='vision')
    assert rec['status'] == 'stopped' and rec['calls'] == rec['error_calls'] == 1
    assert len(calls) == 1 and rec['measured_crop_ids'] == 0
    assert 'API not enabled' in (out / 'VISION_VS_DOCAI_v1.md').read_text()
