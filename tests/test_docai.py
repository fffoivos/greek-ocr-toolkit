"""Recorded, synthetic REST response and mocked ADC/transport; never live OCR."""
import base64
import ast
import copy
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
import unicodedata

from PIL import Image
import pytest

from greekocr.cli import main
from greekocr.readers.services.docai_driver import run_manifest
from greekocr.readers.services.docai_manifest import build_manifest, load_manifest
from greekocr.readers.services.google_docai import DEFAULT_VERSION, DocAIError, DocAIReader

FIXTURES = Path(__file__).parent / 'fixtures'


class Credentials:
    def __init__(self):
        self.calls = 0

    def before_request(self, request, method, url, headers):
        self.calls += 1
        assert method == 'POST'
        headers['authorization'] = 'Bearer MOCK-NOT-A-CREDENTIAL'


class Transport:
    def __init__(self, raw=None, status=200):
        self.raw = raw if raw is not None else json.loads((Path(__file__).parent / 'data/docai/response.json').read_text())
        self.status = status
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append(dict(url=url, **kwargs))
        return SimpleNamespace(headers={'x-goog-request-id': 'recorded-request-1'}, status_code=self.status,
                               json=lambda: copy.deepcopy(self.raw), text='recorded response')


@pytest.fixture
def crop(tmp_path):
    path = tmp_path / 'line.png'
    Image.new('L', (20, 8), 255).save(path)
    return path


@pytest.fixture
def reader(tmp_path):
    return DocAIReader('recorded-project', 'eu', 'processor', DEFAULT_VERSION,
                       receipts_dir=tmp_path / 'receipts', credentials=Credentials(), transport=Transport())


def ledger(reader):
    return [json.loads(line) for line in reader.ledger_path.read_text().splitlines()]


def manifest(tmp_path, crop, entries):
    path = tmp_path / 'inputs.jsonl'
    rows = [dict(dict(crop_path=str(crop), line_id=str(i), cohort='gold', gold_text=None,
                 diagnostics=dict(layer_text=None, cllg_text=None, ours_text=None)), **entry)
            for i, entry in enumerate(entries)]
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    return path


def test_recorded_response_confidences_text_and_receipt(reader, crop):
    reading = reader.read(crop)
    assert reading.text == 'ἅλφα β\n' and reading.lines == ['ἅλφα β']
    assert [r['text'] for r in reading.token_confidences] == ['ἅλφα ', 'β\n']
    assert [r['text'] for r in reading.symbol_confidences] == list('ἅλφαβ')
    assert reading.mean_symbol_conf == pytest.approx(.7) and reading.min_symbol_conf == .5
    assert reading.request_id == 'recorded-request-1' and reading.latency_s >= 0
    assert json.loads(Path(reading.raw_json_path).read_text()) == reader._transport.raw
    assert reading.crop_sha256 == hashlib.sha256(crop.read_bytes()).hexdigest()


def test_rest_payload_version_and_quota_header(reader, crop):
    reader.read(crop)
    call = reader._transport.calls[0]
    assert call['url'] == f'https://eu-documentai.googleapis.com/v1/projects/recorded-project/locations/eu/processors/processor/processorVersions/{DEFAULT_VERSION}:process'
    assert call['headers']['x-goog-user-project'] == 'recorded-project'
    assert call['json']['processOptions'] == {'ocrConfig': {'enableSymbol': True, 'hints': {'languageHints': ['el']}}}
    assert base64.b64decode(call['json']['rawDocument']['content']) == crop.read_bytes()
    assert call['json']['rawDocument']['mimeType'] == 'image/png'
    assert call['timeout'] == 60


def test_cache_avoids_auth_and_transport_and_fresh_keeps_old_receipt(reader, crop):
    first = reader.read(crop)
    second = reader.read(crop)
    assert second.cached and second.raw_json_path == first.raw_json_path
    assert len(reader._transport.calls) == reader._credentials.calls == 1
    third = reader.read(crop, fresh=True)
    assert not third.cached and third.raw_json_path != first.raw_json_path
    assert Path(first.raw_json_path).is_file()
    assert [r['pages_billed'] for r in ledger(reader)] == [1, 0, 1]
    assert [r['status'] for r in ledger(reader)] == ['ok', 'cache_hit', 'ok']
    assert ledger(reader)[1]['latency_s'] == 0
    assert all(r['version'] == DEFAULT_VERSION and r['mean_symbol_conf'] == pytest.approx(.7)
               and r['min_symbol_conf'] == .5 and r['timestamp'].endswith('+00:00') for r in ledger(reader))


def test_cache_reuse_across_reader_instances(reader, crop):
    first = reader.read(crop)
    reloaded = DocAIReader('recorded-project', 'eu', 'processor', DEFAULT_VERSION,
                          receipts_dir=reader.receipts_dir, transport=lambda *a, **k: pytest.fail('cache made HTTP call'))
    assert reloaded.read(crop).raw_json_path == first.raw_json_path


@pytest.mark.parametrize('changed', ['version', 'language_hints', 'enable_symbol', 'processor_id', 'user_project'])
def test_receipts_isolate_bindings(reader, crop, changed):
    original = reader.read(crop)
    kwargs = dict(project='recorded-project', location='eu', processor_id='processor', version=DEFAULT_VERSION,
                  receipts_dir=reader.receipts_dir, credentials=Credentials(), transport=Transport())
    kwargs[changed] = {'version': 'another-version', 'language_hints': ['el', 'en'], 'enable_symbol': False,
                       'processor_id': 'other', 'user_project': 'quota-project'}[changed]
    alternate = DocAIReader(**kwargs).read(crop)
    assert not alternate.cached and alternate.raw_json_path != original.raw_json_path


def test_binding_deterministic_defensive_and_default_unpinned(reader):
    before = reader.binding()
    assert json.dumps(before, sort_keys=True) == json.dumps(reader.binding(), sort_keys=True)
    before['options']['ocrConfig']['hints']['languageHints'].append('en')
    assert reader.binding()['options']['ocrConfig']['hints']['languageHints'] == ['el']
    unpinned = DocAIReader('project', 'eu', 'processor')
    assert unpinned.binding()['version'] is None
    assert unpinned.endpoint.endswith('/processors/processor:process')


def test_batch_order_and_single_billed_call_for_duplicate_crops(reader, crop):
    readings = reader.read_batch([crop] * 8, concurrency=4)
    assert len(readings) == 8 and sum(not r.cached for r in readings) == 1
    assert len(reader._transport.calls) == 1 and sum(r['pages_billed'] for r in ledger(reader)) == 1


def test_batch_keeps_input_order(reader, crop, tmp_path):
    second = tmp_path / 'other.png'
    Image.new('L', (10, 8), 0).save(second)
    readings = reader.read_batch([second, crop])
    assert [r.crop_sha256 for r in readings] == [hashlib.sha256(p.read_bytes()).hexdigest() for p in (second, crop)]


def test_raw_receipt_tamper_fails_without_new_charge(reader, crop):
    reading = reader.read(crop)
    Path(reading.raw_json_path).write_text('{}')
    with pytest.raises(ValueError, match='receipt changed'):
        reader.read(crop)
    assert len(reader._transport.calls) == 1


def test_http_failure_preserves_response_ledger_and_does_not_cache(reader, crop):
    reader._transport = Transport({'error': {'message': 'recorded refusal'}}, 403)
    with pytest.raises(DocAIError, match='HTTP 403'):
        reader.read(crop)
    row = ledger(reader)[0]
    assert row['status'] == 'error' and row['pages_billed'] is None
    assert json.loads(Path(row['raw_json_path']).read_text()) == reader._transport.raw
    assert not list(reader.receipts_dir.rglob('cache.json'))
    reader._transport = Transport()
    assert not reader.read(crop).cached


def test_transport_failure_is_not_retried(reader, crop):
    def failed(*a, **k):
        raise TimeoutError('recorded timeout')
    reader._transport = failed
    with pytest.raises(DocAIError, match='timeout'):
        reader.read(crop)
    assert len(ledger(reader)) == 1 and ledger(reader)[0]['page_units_reserved'] == 1


def test_non_json_error_receipt(reader, crop):
    def nonjson():
        raise ValueError('not JSON')
    reader._transport = lambda *a, **k: SimpleNamespace(status_code=503, headers={}, text='recorded gateway error', json=nonjson)
    with pytest.raises(DocAIError, match='503'):
        reader.read(crop)
    assert json.loads(Path(ledger(reader)[0]['raw_json_path']).read_text())['error']['body'] == 'recorded gateway error'


def test_missing_symbols_are_na_and_keep_neighbour_line(reader, crop):
    reader._transport.raw['document']['text'] = 'ἅλφα\nβ\n'
    reader._transport.raw['document']['pages'][0].pop('symbols')
    reading = reader.read(crop)
    assert reading.lines == ['ἅλφα', 'β'] and reading.text.endswith('\n')
    assert reading.symbol_confidences == [] and reading.mean_symbol_conf is reading.min_symbol_conf is None


@pytest.mark.parametrize('malformed', ['missing_document', 'bad_anchor', 'bad_confidence', 'multiple_pages', 'document_error'])
def test_malformed_response_retained_not_cached(reader, crop, malformed):
    raw = reader._transport.raw
    if malformed == 'missing_document':
        raw.clear()
    elif malformed == 'bad_anchor':
        raw['document']['pages'][0]['symbols'][0]['layout']['textAnchor']['textSegments'][0]['endIndex'] = '999'
    elif malformed == 'bad_confidence':
        raw['document']['pages'][0]['symbols'][0]['layout']['confidence'] = 2
    elif malformed == 'multiple_pages':
        raw['document']['pages'].append({})
    else:
        raw['document']['error'] = {'message': 'recorded document error'}
    with pytest.raises(DocAIError):
        reader.read(crop)
    assert Path(ledger(reader)[0]['raw_json_path']).is_file()
    assert not list(reader.receipts_dir.rglob('cache.json'))


def test_adc_is_lazy_and_scoped(reader, crop, monkeypatch):
    import google.auth
    credentials = Credentials()
    calls = []
    def default(**kwargs):
        calls.append(kwargs)
        return credentials, 'adc-project'
    monkeypatch.setattr(google.auth, 'default', default)
    reader._credentials = None
    reader.read(crop)
    assert calls == [dict(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id='recorded-project')]
    reader.read(crop)
    assert len(calls) == credentials.calls == 1


def test_reject_multipage_crop_without_calls(reader, tmp_path):
    path = tmp_path / 'multipage.tiff'
    Image.new('L', (10, 10)).save(path, save_all=True, append_images=[Image.new('L', (10, 10))])
    with pytest.raises(ValueError, match='single-page'):
        reader.read(path)
    assert not reader.ledger_path.exists() and not reader._transport.calls


def test_changed_crop_rejected_before_http(reader, crop):
    with pytest.raises(ValueError, match='crop changed'):
        reader.read(crop, expected_sha256='stale-manifest-hash')
    assert not reader._transport.calls


def test_tiny_report_gold_diagnostics_line_counts_and_cost(reader, crop, tmp_path):
    # Gold NFD: Α (1 atom) and ἅ (3 atoms); A + ά lose homoglyph and breathing.
    responses = iter(['A', 'ά', 'CLLG\nextra\n'])
    def response(*a, **k):
        text = next(responses)
        return SimpleNamespace(headers={}, status_code=200,
                               json=lambda: {'document': {'text': text, 'pages': [{}]}})
    reader._transport = response
    path = manifest(tmp_path, crop, [dict(gold_text='Α'), dict(gold_text='ἅ'),
                                  dict(cohort='owner44', diagnostics=dict(layer_text='layer', cllg_text='CLLG', ours_text=None))])
    summary = run_manifest(path, tmp_path / 'run', reader=reader, fresh=True, concurrency=1)
    metrics = summary['cohorts']['gold']['passes'][0]['gold_metrics']
    assert metrics['overall'] == dict(cer=.5, edits=2, ref_len=4, lines=2)
    assert metrics['greek_to_latin_homoglyphs'] == 1
    assert metrics['marks']['acute']['precision'] == metrics['marks']['acute']['recall'] == metrics['marks']['acute']['f1'] == 1
    assert metrics['marks']['rough_breathing']['fn'] == 1 and metrics['mark_f1'] == pytest.approx(2/3)
    owner = summary['cohorts']['owner44']['passes'][0]
    assert owner['gold_metrics'] is None and owner['gold_scored'] == 0
    assert owner['line_count_anomalies'] == [dict(line_id='2', lines=2)]
    assert owner['diagnostics']['cllg_text']['nfd_cer_agreement']['cer'] == pytest.approx(7/4)
    assert summary['cost']['pages_billed'] == 3 and summary['cost']['estimated_usd'] == pytest.approx(.0045)
    report = (tmp_path / 'run/REPORT.md').read_text()
    assert 'DIAGNOSTICS' in report and 'never accuracy' in report and 'rough_breathing' in report
    predictions = [json.loads(s) for s in (tmp_path / 'run/predictions.jsonl').read_text().splitlines()]
    assert predictions[-1]['prediction'] == 'CLLG\nextra\n' and predictions[-1]['line_count'] == 2


def test_repeat_bypasses_cache_even_first_pass_and_computes_pair_cer(reader, crop, tmp_path):
    reader.read(crop)
    texts = iter(['Α', 'A'])
    reader._transport = lambda *a, **k: SimpleNamespace(headers={}, status_code=200,
        json=lambda: {'document': {'text': next(texts), 'pages': [{}]}})
    path = manifest(tmp_path, crop, [dict(gold_text='Α')])
    summary = run_manifest(path, tmp_path / 'run', reader=reader, repeat=2, concurrency=1)
    assert summary['determinism']['fraction_identical'] == 0
    assert summary['determinism']['mean_cer_between_repeats'] == 1
    assert summary['cost']['pages_billed'] == 2 and summary['cost']['cache_hits'] == 0
    assert summary['latency']['successful_calls'] == 2


def test_repeat_raw_identity_differs_from_nfd_identity(reader, crop, tmp_path):
    texts = iter(['ἅ', unicodedata.normalize('NFD', 'ἅ'), 'ἅ'])
    reader._transport = lambda *a, **k: SimpleNamespace(headers={}, status_code=200,
        json=lambda: {'document': {'text': next(texts), 'pages': [{}]}})
    summary = run_manifest(manifest(tmp_path, crop, [dict(gold_text='ἅ')]), tmp_path / 'run',
                           reader=reader, repeat=3, concurrency=1)
    assert summary['determinism']['pairs'] == 3
    assert summary['determinism']['fraction_identical'] == pytest.approx(1/3)
    assert summary['determinism']['mean_cer_between_repeats'] == 0


def test_rerun_reuses_cache_and_run_ledger_excludes_history(reader, crop, tmp_path):
    path = manifest(tmp_path, crop, [dict(gold_text='ἅλφα β\n')])
    first = run_manifest(path, tmp_path / 'run', reader=reader)
    second = run_manifest(path, tmp_path / 'run', reader=reader)
    assert first['cost']['pages_billed'] == 1 and second['cost']['pages_billed'] == 0
    assert second['cost']['cache_hits'] == 1 and second['latency']['mean_s'] is None
    assert second['cohorts']['gold']['passes'][0]['gold_metrics']['overall']['cer'] == 0
    assert len((tmp_path / 'run/ledger.jsonl').read_text().splitlines()) == 1


def test_failure_is_visible_na_not_zero_cer(reader, crop, tmp_path):
    reader._transport = Transport({'error': {'message': 'recorded refusal'}}, 403)
    summary = run_manifest(manifest(tmp_path, crop, [dict(gold_text='Α')]), tmp_path / 'run', reader=reader)
    assert summary['complete'] is False and len(summary['failures']) == 1
    assert summary['cohorts']['gold']['passes'][0]['gold_metrics'] is None
    assert summary['cohorts']['gold']['passes'][0]['missing'] == 1
    assert summary['cost']['failed_billing_unknown'] == 1


@pytest.mark.parametrize('option', [dict(repeat=0), dict(concurrency=0), dict(max_cost_usd=.0001)])
def test_driver_invalid_or_over_budget_has_no_calls(reader, crop, tmp_path, option):
    with pytest.raises(ValueError):
        run_manifest(manifest(tmp_path, crop, [{}]), tmp_path / 'run', reader=reader, **option)
    assert not reader._transport.calls and not (tmp_path / 'run').exists()


def test_staged_manifest_builders_exact_444_and_sample_diagnostic(tmp_path):
    path = tmp_path / 'main.jsonl'
    built = build_manifest(FIXTURES, path)
    assert built['lines'] == 444 and built['cohorts'] == dict(polytondb_gold300=300, o4d_lines=44, borndigital100=100)
    rows = load_manifest(path)
    assert sum(r['gold_text'] is not None for r in rows) == 400
    assert all(r['gold_text'] is None for r in rows if r['cohort'] == 'o4d_lines')
    assert all(r['diagnostics']['cllg_text'] is not None for r in rows if r['cohort'] == 'polytondb_gold300')
    sample = build_manifest(FIXTURES, tmp_path / 'sample.jsonl', cohorts=['o4d_sample400'])
    assert sample['lines'] == 400
    assert all(r['gold_text'] is None for r in load_manifest(tmp_path / 'sample.jsonl'))


def test_optional_unstaged_borndigital_reports_shortfall(tmp_path):
    result = build_manifest(tmp_path / 'fixtures', tmp_path / 'empty.jsonl', cohorts=['borndigital100'])
    assert result['lines'] == 0 and result['unavailable'] == ['borndigital100']


def test_borndigital_layer_is_never_promoted_to_gold(tmp_path, crop):
    root = tmp_path / 'fixtures/borndigital100'
    (root / 'crops').mkdir(parents=True)
    (root / 'crops/line.png').write_bytes(crop.read_bytes())
    (root / 'index.json').write_text(json.dumps([dict(line_id='line', file='line.png', layer_text='layer', text='text')]))
    build_manifest(tmp_path / 'fixtures', tmp_path / 'manifest.jsonl', cohorts=['borndigital100'])
    row = load_manifest(tmp_path / 'manifest.jsonl')[0]
    assert row['gold_text'] is None and row['diagnostics']['layer_text'] == 'layer'


def test_manifest_rejects_hash_mismatch_and_duplicate_line(tmp_path, crop):
    path = manifest(tmp_path, crop, [dict(crop_sha256='wrong')])
    with pytest.raises(ValueError, match='hash mismatch'):
        load_manifest(path)
    path = manifest(tmp_path, crop, [dict(line_id='same'), dict(line_id='same')])
    with pytest.raises(ValueError, match='duplicate'):
        load_manifest(path)


def test_cli_run_and_manifest_are_offline_with_mocked_reader(tmp_path, crop, reader, monkeypatch, capsys):
    import greekocr.readers.services.docai_driver as driver
    monkeypatch.setattr(driver, 'DocAIReader', lambda **kwargs: reader)
    path = manifest(tmp_path, crop, [dict(gold_text='ἅλφα β\n')])
    assert main(['readers', 'docai', 'run', '--manifest', str(path), '--out', str(tmp_path / 'run')]) == 0
    assert json.loads(capsys.readouterr().out)['complete']
    assert main(['readers', 'docai', 'manifest', '--fixtures-root', str(FIXTURES), '--cohorts', 'o4d_lines',
                 '--out', str(tmp_path / 'owner.jsonl')]) == 0
    assert json.loads(capsys.readouterr().out)['lines'] == 44


def test_cli_failure_returns_nonzero_and_writes_report(tmp_path, crop, reader, monkeypatch, capsys):
    import greekocr.readers.services.docai_driver as driver
    reader._transport = Transport({'error': {'message': 'recorded refusal'}}, 403)
    monkeypatch.setattr(driver, 'DocAIReader', lambda **kwargs: reader)
    path = manifest(tmp_path, crop, [dict(gold_text='Α')])
    assert main(['readers', 'docai', 'run', '--manifest', str(path), '--out', str(tmp_path / 'run')]) == 3
    assert json.loads(capsys.readouterr().out)['complete'] is False
    assert (tmp_path / 'run/REPORT.md').is_file()


def test_docai_public_api_typed_documented_and_packaged():
    from scripts.generate_api_docs import api_entries, CALLS
    from setuptools import find_namespace_packages
    root = Path(__file__).resolve().parents[1]
    docs = (root / 'docs/API.md').read_text()
    entries = [entry for entry in api_entries() if entry[0].startswith('greekocr.readers.services')]
    assert len(entries) == 31  # load_service + 13 DocAI + 7 Vision + 10 Transkribus entries
    for module, name, node, owner in entries:
        qualified = module + '.' + (owner + '.' if owner else '') + name
        assert '### `' + qualified + '`' in docs and name in CALLS
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None
            assert all(arg.annotation is not None for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                       if arg.arg not in ('self', 'cls'))
        imported = importlib.import_module(module)
        assert callable(getattr(getattr(imported, owner) if owner else imported, name))
    assert 'greekocr.readers.services' in find_namespace_packages(str(root), include=['greekocr*'])


def test_protojson_omitted_empty_text_is_cached_without_recall(reader, crop):
    reader._transport.raw={'document':{'mimeType':'image/png','pages':[{'pageNumber':1}]}}
    reading=reader.read(crop)
    assert reading.text=='' and reading.lines==[]
    assert reading.mean_symbol_conf is None and reading.min_symbol_conf is None
    assert reader.read(crop).cached
    assert len(reader._transport.calls)==1


def test_omitted_text_with_nonempty_layout_is_still_invalid(reader,crop):
    reader._transport.raw['document'].pop('text')
    with pytest.raises(DocAIError,match='missing document.text'):
        reader.read(crop)
