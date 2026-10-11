"""T10: licensed, at-most-once Document AI audit of R7 crop failures.

No harvest or training dataset is created. The raw response envelopes are bound to
both image bytes and processor options. An attempted request without a durable
response is deliberately not retried (its billing outcome may be unknown).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import csv
import fcntl
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import statistics
import unicodedata

from PIL import Image, ImageDraw
from greekocr.readers.services.google_docai import DEFAULT_VERSION, DocAIReader, _reading

CATALOGUES = ('controls_owner_marked.json', 'multi_line_segments.json')
SPECIAL = 'ϗȣϛϲϹϝϙϡͅʹ͵'
PRICE_URL = 'https://cloud.google.com/products/document-ai/pricing'
PRICE_PER_PAGE = 1.50 / 1000
DEFAULT_CATALOGUE = Path(__file__).resolve().parents[2].with_name(
    'greek-ocr-toolkit-ff-merged') / '.astra/fast_lines/out/stack/r7/failed_lines'
DEFAULT_OUT = Path(__file__).resolve().parents[2] / 'docs/harvest'
# These explicit selections quote the current owner's words, not inferred numbers
# from a free-text regex. Their R6 numbering is accepted only after exact R7 binding.
NUMBER_SELECTIONS = {
    'O02': {'curl_end_cut': [13, 14, 18]},
    'O04': {'line_start_missed': [75, 90]},
    'O05': {'curl_end_cut': [42, 59, 118, 127]},
    'O06': {'multi_line_segment': [116, 117]},
    'O07': {'misaligned_crop': [123]},
    'O11': {'faint_ghost_kept': [1, 89, 117, 126, 127], 'crop_extends_over_faint': [5]},
    'O12': {'crop_extends_over_faint': [9, 40]},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(canonical(value) + '\n', encoding='utf-8')
    tmp.replace(path)


def is_anemi(page: str, crop: str | Path) -> bool:
    return page.startswith('an-') or Path(crop).name.startswith('an-')


def source_of(page: str) -> str:
    if page.startswith('s2-'):
        return 'Vouli'
    if page.startswith('an-'):
        return 'Anemi'
    if page.startswith(('ia-', 'archive-')):
        return 'Internet Archive'
    return 'Unknown'


def load_catalogues(directory: str | Path) -> list[dict]:
    """Flatten only current_output_items; retain owner provenance and excluded rows."""
    directory = Path(directory).resolve()
    rows = []
    ids = set()
    for filename in CATALOGUES:
        records = json.loads((directory / filename).read_text())
        if not isinstance(records, list):
            raise ValueError(f'{filename}: expected a list')
        for record in records:
            for item in record['current_output_items']:
                path = (directory / item['crop']).resolve()
                if not path.is_relative_to(directory / 'crops'):
                    raise ValueError('crop path escapes catalogue crops directory')
                crop_id = path.stem
                if crop_id in ids:
                    raise ValueError(f'duplicate crop ID: {crop_id}')
                ids.add(crop_id)
                with Image.open(path) as image:
                    width, height = image.size
                rows.append(dict(crop_id=crop_id, catalogue_file=filename,
                    page=record['page'], source=source_of(record['page']),
                    failure_type=record['failure_type'], failure_types=[record['failure_type']],
                    r7_status=record['r7_status'], expected_ocr_risk=record['expected_ocr_risk'],
                    observation=record['observation'], owner_words=record.get('owner_words', ''),
                    owner_mark=record.get('owner_mark'), item_index=item['item_index'],
                    polygon=item['polygon'], crop_path=str(path), crop_sha256=sha256(path),
                    width_px=width, height_px=height, comment_associations=[],
                    status='withheld_anemi' if is_anemi(record['page'], path) else 'pending'))
    return rows


def polygon_crop(page_path: Path, polygon: list, destination: Path) -> None:
    """Native grayscale polygon crop, white outside; no straightening or padding."""
    with Image.open(page_path) as image:
        image = image.convert('L')
        x0 = max(0, math.floor(min(p[0] for p in polygon)))
        y0 = max(0, math.floor(min(p[1] for p in polygon)))
        x1 = min(image.width, math.ceil(max(p[0] for p in polygon)) + 1)
        y1 = min(image.height, math.ceil(max(p[1] for p in polygon)) + 1)
        if x1 <= x0 or y1 <= y0:
            raise ValueError('empty polygon crop')
        crop = image.crop((x0, y0, x1, y1))
        mask = Image.new('L', crop.size, 0)
        ImageDraw.Draw(mask).polygon([(round(x-x0), round(y-y0)) for x,y in polygon], fill=255)
        result = Image.new('L', crop.size, 255)
        result.paste(crop, mask=mask)
        destination.parent.mkdir(parents=True, exist_ok=True)
        result.save(destination)


def derive_comment_crops(directory: Path, rows: list[dict], output: Path) -> list[dict]:
    """Bind named current-owner boxes via unchanged R6 polygons and number maps.

    An exact historical polygon is a region; its exact R7 counterpart is the
    intersection. No whole-page labels, missing-line pseudo-crops, or old R4
    numbers are substituted for an absent region.
    """
    comments = json.loads((directory / 'page_comments.json').read_text())
    r7 = directory.parent
    root = r7.parents[4]
    supplemental_path = r7 / 'comments.json'
    supplemental = {r['id']: r for r in json.loads(supplemental_path.read_text())} if supplemental_path.exists() else {}
    page_images = {}
    page_directories = {root / '.astra/pages'}
    for filename in CATALOGUES:
        for record in json.loads((directory / filename).read_text()):
            if record.get('page_image'):
                page_images[record['page']] = Path(record['page_image'])
                page_directories.add(Path(record['page_image']).parent)
    by_item = defaultdict(list)
    for row in rows:
        by_item[(row['page'], row['item_index'])].append(row)
    coverage = []
    for comment in comments['records']:
        base = dict(comment_id=comment['id'], page=comment['page'],
                    failure_types=comment['failure_types'], owner_words=comment['owner_words'],
                    observation=comment['observation'], r7_status=comment['r7_status'],
                    crop_ids=[], bindings=[])
        if is_anemi(comment['page'], ''):
            base['status'] = 'withheld_anemi_page'
            coverage.append(base)
            continue
        selections = NUMBER_SELECTIONS.get(comment['id'])
        meta = supplemental.get(comment['id'], {})
        historical = root / meta.get('historical_image_source', '__absent__')
        paths = [historical.with_suffix('.json'), historical.with_suffix('.order.json'),
                 r7 / (comment['page'] + '.json'), r7 / (comment['page'] + '.order.json')]
        if not selections or not all(p.is_file() for p in paths):
            base['status'] = 'no_unambiguous_region; two-catalogue evidence only'
            coverage.append(base)
            continue
        old, old_order, new, new_order = [json.loads(p.read_text()) for p in paths]
        if old['items'] != new['items'] or old_order != new_order:
            base['status'] = 'historical_mapping_not_exact; two-catalogue evidence only'
            coverage.append(base)
            continue
        number_map = {r['number']: r['item_index'] for r in old_order}
        candidates = [page_images.get(comment['page'])] + [p/(comment['page']+'.png') for p in sorted(page_directories)]
        page_path = next((p for p in candidates if p is not None and p.is_file()), root/'__missing_page__')
        if not page_path.is_file():
            base['status'] = 'page_image_missing; two-catalogue evidence only'
            coverage.append(base)
            continue
        for failure_type, numbers in selections.items():
            for number in numbers:
                index = number_map[number]
                polygon = new['items'][index]['polygon']
                matches = [r for r in by_item[(comment['page'], index)] if r['polygon'] == polygon]
                if matches:
                    row = matches[0]  # Associate once, rather than relabel every duplicated mark.
                else:
                    crop_id = f"{comment['page']}.comment.r7item{index}"
                    destination = output / 'derived_crops' / (crop_id + '.png')
                    if not destination.exists():
                        polygon_crop(page_path, polygon, destination)
                    with Image.open(destination) as image:
                        width, height = image.size
                    row = dict(crop_id=crop_id, catalogue_file='page_comments.json',
                        page=comment['page'], source=source_of(comment['page']),
                        failure_type=failure_type, failure_types=[failure_type],
                        r7_status=comment['r7_status'], expected_ocr_risk=comments['effects'][failure_type],
                        observation=comment['observation'], owner_words=comment['owner_words'],
                        owner_mark=None, item_index=index, polygon=polygon,
                        crop_path=str(destination), crop_sha256=sha256(destination),
                        width_px=width, height_px=height, comment_associations=[], status='pending')
                    rows.append(row)
                    by_item[(comment['page'], index)].append(row)
                if failure_type not in row['failure_types']:
                    row['failure_types'].append(failure_type)
                association = dict(comment_id=comment['id'], failure_type=failure_type,
                    owner_words=comment['owner_words'], observation=comment['observation'],
                    r7_status=comment['r7_status'], expected_ocr_risk=comments['effects'][failure_type], number=number)
                row['comment_associations'].append(association)
                base['crop_ids'].append(row['crop_id'])
                base['bindings'].append(dict(number=number, item_index=index,
                    failure_type=failure_type, crop_id=row['crop_id'],
                    intersection='exact polygon equality, intersection share 1.0',
                    sources=[dict(path=str(p), sha256=sha256(p)) for p in paths],
                    page_image_sha256=sha256(page_path)))
        base['status'] = 'exact_R6_region_intersected_with_R7'
        coverage.append(base)
    return coverage


def anchored_text(layout: dict, text: str) -> str:
    result = []
    for segment in layout.get('textAnchor', {}).get('textSegments', []):
        start, end = int(segment.get('startIndex', 0)), int(segment['endIndex'])
        if not 0 <= start <= end <= len(text):
            raise ValueError('line anchor outside document text')
        result.append(text[start:end])
    return ''.join(result).rstrip('\r\n')


def crop_metrics(raw: dict, width: int, height: int) -> dict:
    """Measure actual page.lines, with explicitly labelled splitlines fallback."""
    if width <= 0 or height <= 0:
        raise ValueError('crop dimensions must be positive')
    reading = _reading(raw, dict(raw_json_path='', request_id=None, latency_s=0,
                                crop_sha256='', receipt_id=''))
    page = raw['document']['pages'][0]
    if 'lines' in page:
        lines = [anchored_text(r.get('layout', {}), reading.text) for r in page['lines']]
        line_confidences = [r.get('layout', {}).get('confidence') for r in page['lines']]
        line_count_source = 'document.pages[0].lines'
    elif not reading.text:
        lines, line_confidences = [], []
        line_count_source = 'document.pages[0].lines (empty ProtoJSON default omitted)'
    else:
        lines = reading.lines
        line_confidences = [None] * len(lines)
        line_count_source = 'document.text.splitlines fallback (no layout lines)'
    characters = reading.text.replace('\r', '').replace('\n', '')
    greek = sorted({c for c in reading.text if 'GREEK' in unicodedata.name(c, '')}, key=ord)
    return dict(width_px=width, height_px=height, lines_returned=len(lines),
        text_per_line=lines, line_confidences=line_confidences, line_count_source=line_count_source,
        text=reading.text, total_characters=len(characters),
        characters_per_100px_width=100 * len(characters) / width,
        mean_symbol_confidence=reading.mean_symbol_conf, min_symbol_confidence=reading.min_symbol_conf,
        symbol_count=len(reading.symbol_confidences),
        empty=not reading.text.strip(), greek_characters=greek)


def characters_table(rows: list[dict]) -> dict:
    """Count raw emitted code points and NFD marks, once per successful image SHA."""
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        if row['status'] != 'ok' or row['crop_sha256'] in seen:
            continue
        seen.add(row['crop_sha256'])
        grouped['ALL'].append(row['text'])
        grouped[row['source']].append(row['text'])
    table = {}
    for source, texts in sorted(grouped.items()):
        counts = Counter(''.join(texts))
        nfd = Counter(unicodedata.normalize('NFD', ''.join(texts)))
        marks = {c: n for c,n in nfd.items() if unicodedata.category(c).startswith('M')}
        greek_marks = Counter()
        for text in texts:
            greek_base = False
            for c in unicodedata.normalize('NFD', text):
                if unicodedata.category(c).startswith('M'):
                    if greek_base:
                        greek_marks[c] += 1
                else:
                    greek_base = 'GREEK' in unicodedata.name(c, '') and unicodedata.category(c).startswith('L')
        table[source] = dict(n_calls=len(texts), character_counts=dict(sorted(counts.items(), key=lambda r: ord(r[0]))),
            greek_character_counts={c:n for c,n in sorted(counts.items(), key=lambda r: ord(r[0])) if 'GREEK' in unicodedata.name(c, '')},
            requested_characters={c:dict(raw_count=counts[c], nfd_count=nfd[c], appeared=counts[c] > 0) for c in SPECIAL},
            nfd_combining_marks=dict(sorted(marks.items(), key=lambda r: ord(r[0]))),
            nfd_marks_on_greek=dict(sorted(greek_marks.items(), key=lambda r: ord(r[0]))))
    return table


def distribution(values: list) -> dict:
    values = sorted(v for v in values if v is not None)
    if not values:
        return dict(n=0, min=None, p05=None, p25=None, median=None, p75=None, p95=None, max=None, mean=None)
    def q(f):
        position = (len(values)-1) * f
        lo, hi = math.floor(position), math.ceil(position)
        return values[lo] + (values[hi]-values[lo]) * (position-lo)
    return dict(n=len(values), min=values[0], p05=q(.05), p25=q(.25), median=q(.5),
                p75=q(.75), p95=q(.95), max=values[-1], mean=statistics.mean(values))


def summarise(rows: list[dict], failure_types: list[str]) -> dict:
    controls = [r for r in rows if r['status']=='ok' and r['failure_type']=='control_owner_verified']
    baseline = distribution([r['mean_symbol_confidence'] for r in controls])
    threshold = baseline['p05']
    min_threshold = distribution([r['min_symbol_confidence'] for r in controls])['p05']
    density_baseline = distribution([r['characters_per_100px_width'] for r in controls])
    for row in rows:
        if row['status'] != 'ok':
            continue
        low = threshold is not None and row['mean_symbol_confidence'] is not None and row['mean_symbol_confidence'] < threshold
        low_min = min_threshold is not None and row['min_symbol_confidence'] is not None and row['min_symbol_confidence'] < min_threshold
        row['exposure_signals'] = (['multiple_layout_lines'] if row['lines_returned'] > 1 else []) + (['empty'] if row['empty'] else []) + (['low_mean_symbol_confidence'] if low else []) + (['low_min_symbol_confidence'] if low_min else [])
        row['treatment'] = 'Google exposes it' if row['exposure_signals'] else 'Google absorbs it silently (candidate; visual confirmation needed)'
    summaries = {}
    for kind in ['control_owner_verified'] + failure_types:
        members = [r for r in rows if kind in r['failure_types']]
        measured = [r for r in members if r['status']=='ok']
        summaries[kind] = dict(n_crops=len(members), n_measured=len(measured),
            n_unique_images=len({r['crop_sha256'] for r in measured}),
            withheld_anemi=sum(r['status']=='withheld_anemi' for r in members),
            lines_returned_distribution=dict(sorted(Counter(r['lines_returned'] for r in measured).items())),
            empty_count=sum(r['empty'] for r in measured),
            empty_rate=sum(r['empty'] for r in measured)/len(measured) if measured else None,
            mean_symbol_confidence=distribution([r['mean_symbol_confidence'] for r in measured]),
            min_symbol_confidence=distribution([r['min_symbol_confidence'] for r in measured]),
            characters_per_100px_width=distribution([r['characters_per_100px_width'] for r in measured]),
            exposed_count=sum(bool(r['exposure_signals']) for r in measured),
            silent_candidate_count=sum(not r['exposure_signals'] for r in measured),
            density_below_controls_p05=sum(r['characters_per_100px_width'] < density_baseline['p05'] for r in measured) if controls else None,
            density_above_controls_p95=sum(r['characters_per_100px_width'] > density_baseline['p95'] for r in measured) if controls else None,
            density_median_ratio_to_controls=(statistics.median(r['characters_per_100px_width'] for r in measured)/density_baseline['median']) if measured and density_baseline['median'] else None)
    return dict(low_confidence_threshold=threshold, low_min_confidence_threshold=min_threshold, types=summaries)


@contextmanager
def run_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def cached_response(row: dict, output: Path, reader: DocAIReader, *, offline=False) -> dict:
    """No Anemi bytes reach the adapter. Validate cache before every reuse."""
    if is_anemi(row['page'], row['crop_path']):
        raise ValueError('Anemi is withheld: no adapter call allowed')
    crop_sha = row['crop_sha256']
    if sha256(Path(row['crop_path'])) != crop_sha:
        raise ValueError('crop changed since inventory; no call made')
    path = output / 'responses' / (row['crop_id'] + '.json')
    binding = reader.binding()
    if path.exists():
        value = json.loads(path.read_text())
        if value['crop_sha256'] != crop_sha or value['binding'] != binding:
            raise ValueError('crop cache SHA/options mismatch; refusing re-call')
        raw_sha = hashlib.sha256(canonical(value['response']).encode()).hexdigest()
        if raw_sha != value['response_sha256']:
            raise ValueError('raw response envelope changed; refusing re-call')
        return value
    # Reuse a differently named, byte-identical image without even acquiring ADC.
    for sibling in sorted((output / 'responses').glob('*.json')):
        value = json.loads(sibling.read_text())
        if value['crop_sha256'] == crop_sha:
            if value['binding'] != binding or hashlib.sha256(canonical(value['response']).encode()).hexdigest() != value['response_sha256']:
                raise ValueError('shared image cache binding/hash mismatch')
            value = dict(value, crop_id=row['crop_id'], reused_from_crop=value['crop_id'])
            atomic_json(path, value)
            return value
    if offline:
        raise ValueError(f"offline cache miss: {row['crop_id']}")
    attempt_path = output / 'attempts' / (crop_sha + '.json')
    if attempt_path.exists():
        # The adapter may have persisted its receipt just before an interruption.
        binding_sha = hashlib.sha256(canonical(binding).encode()).hexdigest()
        adapter_cache = reader.receipts_dir / binding_sha / (crop_sha + '-' + (reader.version or 'default')) / 'cache.json'
        if not adapter_cache.exists():
            # Recover a durable HTTP-success receipt rejected by an older parser.
            # Preserve its original raw bytes and error ledger; never send again.
            ledger = [json.loads(s) for s in reader.ledger_path.read_text().splitlines()] if reader.ledger_path.exists() else []
            candidates = [r for r in ledger if r['crop_sha256']==crop_sha and r['binding']==binding and r['status']=='error' and r.get('pages_billed')==1 and r.get('raw_json_path')]
            if not candidates:
                raise ValueError('prior attempt has no durable response; refusing automatic re-call')
            metadata = candidates[-1]
            raw_path = Path(metadata['raw_json_path'])
            if sha256(raw_path) != metadata['raw_sha256']:
                raise ValueError('saved error receipt changed; no re-call')
            raw = json.loads(raw_path.read_text())
            _reading(raw, metadata, cached=True)
            value = dict(schema_version=1, crop_id=row['crop_id'], crop_sha256=crop_sha, binding=binding,
                receipt_id=metadata['receipt_id'], request_id=metadata['request_id'],
                raw_json_path=str(raw_path), latency_s=metadata['latency_s'], response=raw,
                response_sha256=hashlib.sha256(canonical(raw).encode()).hexdigest(),
                recovered_adapter_parse_error=metadata['error'])
            atomic_json(path, value)
            atomic_json(attempt_path, dict(status='ok', crop_id=row['crop_id'], crop_sha256=crop_sha,
                receipt_id=metadata['receipt_id'], recovered_without_call=True))
            return value
    else:
        atomic_json(attempt_path, dict(status='attempted', crop_id=row['crop_id'], crop_sha256=crop_sha,
                                      started_at=datetime.now(timezone.utc).isoformat()))
    try:
        reading = reader.read(row['crop_path'], expected_sha256=crop_sha, fresh=False)
        raw = json.loads(Path(reading.raw_json_path).read_text())
        value = dict(schema_version=1, crop_id=row['crop_id'], crop_sha256=crop_sha, binding=binding,
            receipt_id=reading.receipt_id, request_id=reading.request_id,
            raw_json_path=reading.raw_json_path, latency_s=reading.latency_s,
            response=raw, response_sha256=hashlib.sha256(canonical(raw).encode()).hexdigest())
        atomic_json(path, value)
        atomic_json(attempt_path, dict(status='ok', crop_id=row['crop_id'], crop_sha256=crop_sha,
                                      receipt_id=reading.receipt_id, cached=reading.cached))
        return value
    except Exception as error:
        atomic_json(attempt_path, dict(status='error', crop_id=row['crop_id'], crop_sha256=crop_sha, error=str(error)))
        raise


def receipt(rows, directory, output, reader, status, error=None) -> dict:
    ledger = [json.loads(s) for s in reader.ledger_path.read_text().splitlines()] if reader.ledger_path.exists() else []
    calls = [r for r in ledger if not r['cached']]
    billed = sum(r.get('pages_billed') or 0 for r in calls)
    recovered = {json.loads(p.read_text())['receipt_id'] for p in (output/'responses').glob('*.json') if 'recovered_adapter_parse_error' in json.loads(p.read_text())}
    files = list((directory / 'crops').glob('*.png'))
    return dict(schema_version=1, status=status, error=error, timestamp=datetime.now(timezone.utc).isoformat(),
        catalogue_directory=str(directory), binding=reader.binding(),
        input_hashes={f:sha256(directory/f) for f in ['README.md', *CATALOGUES, 'page_comments.json'] if (directory/f).exists()},
        calls=len(calls), successful_calls=sum(r['status']=='ok' or r['receipt_id'] in recovered for r in calls),
        adapter_parse_error_recoveries=len(recovered),
        error_calls=sum(r['status']=='error' and r['receipt_id'] not in recovered for r in calls), pages_billed_known=billed,
        pages_billing_unknown=sum(r.get('pages_billed') is None for r in calls),
        estimated_cost_usd=round(billed*PRICE_PER_PAGE, 6), price_per_1000_pages_usd=1.50,
        price_source=PRICE_URL, price_checked_date='2026-10-11',
        cost_basis='Enterprise Document OCR base list price; excludes free allowance, credits, taxes and account-specific discounts; not an invoice',
        catalogue_crop_files=len(files), withheld_anemi=sum(p.name.startswith('an-') for p in files),
        withheld_anemi_current_output_crops=sum(r['status']=='withheld_anemi' for r in rows),
        catalogued_current_output_crops=sum(r['catalogue_file'] in CATALOGUES for r in rows),
        derived_comment_crops=sum(r['catalogue_file']=='page_comments.json' for r in rows),
        measured_crop_ids=sum(r['status']=='ok' for r in rows),
        unique_measured_crop_sha256=len({r['crop_sha256'] for r in rows if r['status']=='ok'}),
        request_policy='sequential; no retries; SHA cache; stop on first error; el hints; symbols enabled')


def fmt(value):
    return '—' if value is None else f'{value:.3f}'


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k:canonical(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def build_artifacts(rows, comments, directory, out, rec):
    output = out / 'docai_failed_lines'
    effects = json.loads((directory/'page_comments.json').read_text())['effects']
    findings_path = output/'visual_findings.json'
    findings = json.loads(findings_path.read_text()) if findings_path.exists() else []
    by_id = {r['crop_id']:r for r in rows}
    reviewed = []
    for finding in findings:
        row = by_id.get(finding['crop_id'])
        if row is None or row['status']!='ok':
            continue
        envelope = json.loads((output/'responses'/(row['crop_id']+'.json')).read_text())
        if row['crop_sha256'] != finding['crop_sha256'] or envelope['response_sha256'] != finding['response_sha256']:
            raise ValueError('visual finding source hash changed')
        row['visual_observation'] = finding['observation']
        reviewed.append(row)
    summary = summarise(rows, list(effects))
    for kind, stats in summary['types'].items():
        associated = [c for c in comments if kind in c['failure_types']]
        stats['n_page_comments'] = len(associated)
        stats['n_withheld_anemi_page_comments'] = sum(c['status']=='withheld_anemi_page' for c in associated)
        stats['n_bound_page_comments'] = sum(any(b['failure_type']==kind for b in c['bindings']) for c in associated)
    chars = characters_table(rows)
    atomic_json(output/'metrics.json', rows)
    atomic_json(output/'summary.json', summary)
    atomic_json(output/'characters.json', chars)
    atomic_json(output/'page_comment_coverage.json', comments)
    atomic_json(output/'receipt.json', rec)
    write_csv(output/'crops.csv', rows)
    char_rows = []
    for source, table in chars.items():
        for character, count in table['character_counts'].items():
            char_rows.append(dict(source=source, character=character, codepoint=f'U+{ord(character):04X}',
                unicode_name=unicodedata.name(character,'CONTROL'), count=count, representation=repr(character)))
    write_csv(output/'characters.csv', char_rows)
    baseline = summary['types']['control_owner_verified']
    control_sha = {r['crop_sha256'] for r in rows if r['catalogue_file']==CATALOGUES[0] and r['status']=='ok'}
    multi_sha = {r['crop_sha256'] for r in rows if r['catalogue_file']==CATALOGUES[1] and r['status']=='ok'}
    lines = ['# Document AI treatment of known R7 line-finder failures — v1', '',
        '## Controls baseline (first)', '',
        f"{baseline['n_measured']} permitted control crop IDs ({baseline['n_unique_images']} distinct images); {baseline['withheld_anemi']} Anemi current-output controls withheld. These are owner-verified marks, not gold OCR transcripts.", '',
        f"Returned layout lines: `{baseline['lines_returned_distribution']}`. Empty rate: {fmt(baseline['empty_rate'])}. Mean symbol confidence: median {fmt(baseline['mean_symbol_confidence']['median'])}, p05 {fmt(baseline['mean_symbol_confidence']['p05'])}, p95 {fmt(baseline['mean_symbol_confidence']['p95'])}. Minimum symbol confidence: median {fmt(baseline['min_symbol_confidence']['median'])}.", '',
        f"Characters/100 px: min {fmt(baseline['characters_per_100px_width']['min'])}, p05 {fmt(baseline['characters_per_100px_width']['p05'])}, p25 {fmt(baseline['characters_per_100px_width']['p25'])}, median {fmt(baseline['characters_per_100px_width']['median'])}, p75 {fmt(baseline['characters_per_100px_width']['p75'])}, p95 {fmt(baseline['characters_per_100px_width']['p95'])}, max {fmt(baseline['characters_per_100px_width']['max'])}.", '',
        '## Scope, cache and measurement contract', '',
        f"Status: **{rec['status']}**. The two catalogues contain {rec['catalogued_current_output_crops']} current-output crop IDs; {rec['withheld_anemi_current_output_crops']} are withheld. The whole supplied crop directory contains {rec['catalogue_crop_files']} files, including **{rec['withheld_anemi']} withheld Anemi files** (marked crops included). Marked-region images are not harvest inputs and were not sent. {rec['derived_comment_crops']} additional current-output crops were derived from exact historical-number mappings. No Anemi file or page was submitted.", '',
        f"{rec['measured_crop_ids']} crop IDs measured from {rec['unique_measured_crop_sha256']} distinct image SHA-256 values. Byte-identical crops share one request. Crop statistics are crop-ID weighted; character counts are unique-call weighted. Controls and multi-line catalogues share {len(control_sha & multi_sha)} distinct image hashes. An overlapping neighbour can be a clean crop even within a partly fixed multi-line mark; mark-level labels do not establish that every current-output crop is defective. These samples are development pages, not the held-out set. No harvest was made.", '',
        f"Processor binding: `{canonical(rec['binding'])}`. Crop bytes, processor/options, response hash, request/receipt IDs and raw responses are retained in `docai_failed_lines/responses/<crop_id>.json`; the adapter's original receipts and ledger are also retained. A changed cache binding or an unresolved prior attempt stops the run; there is no fresh/retry switch.", '',
        f"Adapter parsing recoveries: {rec['adapter_parse_error_recoveries']}. A successful empty page can omit default `document.text` and repeated line/symbol fields under [ProtoJSON default-value rules](https://protobuf.dev/programming-guides/json/#presence-and-default-values). The adapter now accepts that empty form. The original rejected receipt/error ledger remains intact; recovery reads its saved raw bytes and makes no API call.", '',
        'Line count uses the API layout `document.pages[0].lines`, not the adapter\'s text-newline heuristic. A missing lines field uses an explicitly labelled fallback. Total characters excludes CR/LF but includes spaces, punctuation and combining code points. Density is that count / image width × 100. Confidence is over symbols with reported confidence; absence is null, not zero. Greek-character sets use Unicode names; exact raw characters and NFD marks are counted separately.', '',
        f"Operational exposure rule: multiple returned layout lines, empty text, or mean/minimum symbol confidence below the corresponding controls' p05 ({fmt(summary['low_confidence_threshold'])} mean; {fmt(summary['low_min_confidence_threshold'])} minimum). These thresholds are diagnostics, not validated filters. A layout-line return can split a single curved printed row into spatial pieces; it is not proof of two printed rows. Single-line outputs without these signals are **silent candidates**, not proof of correct or incorrect transcription. Truncation/appending cannot be established from confidence or density alone: compare crop, owner observation and text in the review page. Baseline false alarms are {baseline['exposed_count']}/{baseline['n_measured']} controls; owner controls sometimes include complete neighbours.", '',
        '## Treatment by failure type', '',
        '| Catalogue type | n measured / withheld crops | Page comments (Anemi withheld) | Layout-line distribution | Empty rate | Mean conf median (p05) | Min conf median | Chars/100px median (p05–p95) | Density below/above controls p05–p95 | Exposed / silent candidates | Verdict |',
        '| --- | ---: | ---: | --- | ---: | --- | ---: | --- | --- | --- | --- |']
    for kind in effects:
        s = summary['types'][kind]
        if s['n_measured']:
            verdict = ('Google exposes it' if not s['silent_candidate_count'] else
                f"Google absorbs it silently — candidates: {s['silent_candidate_count']}; exposed: {s['exposed_count']}")
        elif kind in ('missed_line','missed_words_in_row'):
            verdict = 'No crop for missing ink: no Google signal; line-finder-side recovery required'
        else:
            verdict = 'Not measured: withheld or no reliably located crop; no Google verdict inferred'
        lines.append(f"| `{kind}` | {s['n_measured']} / {s['withheld_anemi']} | {s['n_page_comments']} ({s['n_withheld_anemi_page_comments']}) | `{s['lines_returned_distribution']}` | {fmt(s['empty_rate'])} | {fmt(s['mean_symbol_confidence']['median'])} ({fmt(s['mean_symbol_confidence']['p05'])}) | {fmt(s['min_symbol_confidence']['median'])} | {fmt(s['characters_per_100px_width']['median'])} ({fmt(s['characters_per_100px_width']['p05'])}–{fmt(s['characters_per_100px_width']['p95'])}) | {s['density_below_controls_p05']} / {s['density_above_controls_p95']} | {s['exposed_count']} / {s['silent_candidate_count']} | {verdict} |")
    lines += ['', 'Density outside the controls’ p05–p95 is descriptive, not an exposure signal: fonts, crop scales and short fragments differ. Types with silent candidates need line-finder-side geometry/ink filters or exclusions; Google confidence is not a crop-completeness check. Missing input is invisible to OCR. Counts for associated page-comment types overlap other types and must not be summed. Withheld-crop counts apply only to labelled crops in the two catalogues; unlocated page-comment regions have unknown crop counts, even when their whole Anemi page is withheld. Full distribution quantiles, unique-image counts and per-crop evidence are in the linked JSON/CSV.', '',
        '## Page-comment coverage', '',
        'Named current-owner regions are accepted only when saved R6 item geometry **and** display-number order match R7 exactly. The historical polygon is intersected with its exact R7 counterpart (share 1.0); the full output polygon is cropped from native grayscale pixels. Existing matching catalogue crops are reused. No old R4 number is guessed from today\'s order. Broad comments and types without a region remain page-level; their coverage is reported below, with Google evidence restricted to the two crop catalogues.', '',
        '| Comment | Page | Types | Binding / scope | Crop IDs measured |', '| --- | --- | --- | --- | ---: |']
    for c in comments:
        lines.append(f"| {c['comment_id']} | `{c['page']}` | {', '.join(c['failure_types'])} | {c['status']} | {len(c['crop_ids'])} |")
    if reviewed:
        lines += ['', '## Visual checks of the returned-line signal', '']
        for row in reviewed:
            text = ' / '.join(row['text_per_line']).replace('|', '\\|')
            lines.append(f"- [{row['crop_id']}](docai_failed_lines_review.html#{row['crop_id']}): {row['visual_observation']} Returned text: `{text}`; mean symbol confidence {fmt(row['mean_symbol_confidence'])}. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).")
        lines += ['', 'These samples calibrate the signal; the complete crop review remains available to the owner.', '']
    lines += ['', '## Representative returned outputs', '',
        'These are signal-only examples, selected deterministically from measured crop IDs. They show what Google returned, not gold-text correctness. View the linked crop against its owner observation.', '',
        '| Type | Crop / Google signal | Returned lines | Mean / minimum symbol confidence |',
        '| --- | --- | --- | --- |']
    for kind in effects:
        members = [r for r in rows if r['status']=='ok' and kind in r['failure_types']]
        for exposed in [True, False]:
            match = next((r for r in members if bool(r['exposure_signals'])==exposed), None)
            if match:
                text = ' / '.join(match['text_per_line']).replace('|', '\\|')
                lines.append(f"| `{kind}` | [{match['crop_id']}](docai_failed_lines_review.html#{match['crop_id']}) · {'exposed' if exposed else 'silent candidate'} | {text or '(empty)'} | {fmt(match['mean_symbol_confidence'])} / {fmt(match['min_symbol_confidence'])} |")
    lines += ['', '## Characters actually emitted', '',
        'The [complete characters table](docai_failed_lines/characters.csv) includes every raw emitted code point and its count for ALL calls and each present source. Counts include whitespace. [characters.json](docai_failed_lines/characters.json) also stores Greek-only sets and NFD counts. Absence here is not proof that the processor cannot recognise a glyph: no glyph-level ground truth or exposure count is supplied.', '']
    for source, table in chars.items():
        greek = ''.join(table['greek_character_counts'])
        lines += [f"### {source} — {table['n_calls']} unique calls", '', f'Raw emitted Greek set: `{greek}`.', '',
            '| Requested character | Code point | Raw count / appeared | NFD count |', '| --- | --- | ---: | ---: |']
        for c, count in table['requested_characters'].items():
            lines.append(f"| {c} | U+{ord(c):04X} | {count['raw_count']} / {'yes' if count['appeared'] else 'no'} | {count['nfd_count']} |")
        lines += ['', 'NFD combining marks attached to Greek letters:', '', '| Mark | Code point / name | Count |', '| --- | --- | ---: |']
        for c, count in table['nfd_marks_on_greek'].items():
            lines.append(f"| ◌{c} | U+{ord(c):04X} {unicodedata.name(c)} | {count} |")
        if not table['nfd_marks_on_greek']:
            lines.append('| — | None observed | 0 |')
        lines += ['']
    if 'Internet Archive' not in chars:
        lines += ['Internet Archive: **no current-output crop in this catalogue**, so no per-source measurement. Anemi is withheld.', '']
    lines += ['## Cost receipt', '',
        f"**{rec['calls']} API calls**: {rec['successful_calls']} successful, {rec['error_calls']} errors; {rec['pages_billed_known']} known successful one-page units, {rec['pages_billing_unknown']} units with unknown billing outcome. Estimated base list-price cost: **US${rec['estimated_cost_usd']:.4f}** at US$1.50/1,000 pages. [Google Enterprise Document OCR pricing]({PRICE_URL}) checked 11 October 2026. The pricing page also shows a free allowance; this conservative list-price estimate does not assume its remaining balance, credits, discounts or taxes and is not an invoice.", '',
        '[Machine-readable receipt](docai_failed_lines/receipt.json) · [Raw per-crop CSV](docai_failed_lines/crops.csv) · [Metrics](docai_failed_lines/metrics.json) · [Summary](docai_failed_lines/summary.json) · [Comment-region provenance](docai_failed_lines/page_comment_coverage.json) · [Visual review](docai_failed_lines_review.html)', '']
    if rec['error']:
        lines += ['## Stopped request', '', f"`{rec['error']}`", '', 'No later crop was submitted. Resume does not automatically retry this attempted image.', '']
    validation_path = output/'validation.json'
    if validation_path.exists():
        validation = json.loads(validation_path.read_text())
        lines += ['## Verification and visual-review limit', '',
            f"{validation['tests']['passed']} offline tests passed. The [artifact validator](../../scripts/harvest/validate_google_failed_lines.py) recomputes every crop metric and the character table from raw responses, checks all image hashes/cards/links/CSV IDs, and confirms at most one API call per SHA. Offline regeneration added no calls. [Verification receipt](docai_failed_lines/validation.json).", '',
            'The responsive CSS constrains images and long text to the available width. Actual desktop and phone viewport rendering remains unverified: the local headless browser could not launch in this sandbox, and automatic approval review rejected Firefox access because computer use was not approved for that app. Sixteen native crop/response samples were inspected visually; this is not a browser layout check.', '']
    (out/'DOCAI_FAILED_LINES_v1.md').write_text('\n'.join(lines), encoding='utf-8')
    build_review(rows, summary, comments, out, rec)


def build_review(rows, summary, comments, out, rec):
    """Continuous strip/card format and palette from scripts/glyphs/pages_review.html."""
    esc = lambda s: html.escape(str(s), quote=True)
    images = out/'docai_failed_lines/images'
    images.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for row in rows:
        destination = images/(row['crop_id']+'.png')
        if not destination.exists() or sha256(destination) != row['crop_sha256']:
            shutil.copyfile(row['crop_path'], destination)
        groups[row['failure_type']].append(row)
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Document AI · Known failed lines · T10</title>',
        '''<style>:root{--bg:#f3f5f6;--surface:#fff;--fg:#1a1f25;--muted:#5a6470;--rule:#d6dce1;--accent:#0d6e72;--cut:#b42318;--feature:#fff4d6}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Arial,sans-serif}.wrap{max-width:1640px;margin:auto;padding:28px 20px 64px;display:grid;gap:28px;min-width:0}h1,h2{font-family:Georgia,serif;font-weight:500;overflow-wrap:anywhere}h1{font-size:1.9rem;margin:0}h2{font-size:1.35rem;border-top:2px solid var(--accent);padding-top:12px}.intro,section{display:grid;gap:12px;min-width:0}.line{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:16px;display:grid;gap:10px;min-width:0}.line.silent{box-shadow:inset 4px 0 var(--cut)}.id{font-family:ui-monospace,Menlo,monospace;font-size:.85rem;overflow-wrap:anywhere}.note{background:var(--feature);padding:10px 12px;border-radius:4px;white-space:pre-wrap;overflow-wrap:anywhere}.muted{color:var(--muted)}.events{font-size:.85rem;display:flex;flex-wrap:wrap;gap:4px 18px}.ocr{font:1.1rem/1.7 Georgia,serif;white-space:pre-wrap;overflow-wrap:anywhere;margin:0;padding-left:24px}.crop{display:block;width:auto;max-width:100%;height:auto;background:#fff}a{color:var(--accent);overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:8px 16px}p{margin:0;overflow-wrap:anywhere}code{overflow-wrap:anywhere;white-space:normal}@media(max-width:600px){.wrap{padding:16px 10px 40px;gap:18px}.line{padding:12px}h1{font-size:1.5rem}.ocr{font-size:1rem}}@media print{.line{break-inside:avoid;box-shadow:none}body{background:#fff}}</style>''',
        '<main class="wrap"><header class="intro"><h1>How Google treats the line finder’s failures</h1>',
        f"<p>{rec['measured_crop_ids']} crop IDs measured · {rec['calls']} calls · {rec['withheld_anemi']} Anemi files withheld · estimated US${rec['estimated_cost_usd']:.4f}</p>",
        '<p>Read each native crop against the owner’s observation and Google’s layout lines. A single confident line can still omit or append text. Red inset: silent candidate under the operational rule; it needs visual confirmation.</p>',
        '<p class="muted">One card per crop ID, including local-only withheld crops. Primary groups follow catalogue types; secondary comment types appear on the same card. Identical crop bytes share a response. Tap a crop to open its native-resolution image. Images are local files.</p>',
        '<p><a href="DOCAI_FAILED_LINES_v1.md">Report and coverage limits</a> · <a href="docai_failed_lines/crops.csv">Per-crop CSV</a> · <a href="docai_failed_lines/characters.csv">Emitted characters</a> · <a href="docai_failed_lines/receipt.json">Receipt</a></p>',
        '<nav aria-label="Failure groups">']
    order = ['control_owner_verified'] + sorted(k for k in groups if k!='control_owner_verified')
    for kind in order:
        parts.append(f'<a href="#{esc(kind)}">{esc(kind)} ({len(groups[kind])})</a>')
    parts.append('</nav></header>')
    for kind in order:
        parts.append(f'<section id="{esc(kind)}"><h2>{esc(kind)}</h2>')
        for row in groups[kind]:
            silent = row['status']=='ok' and not row['exposure_signals']
            parts += [f'<article class="line {"silent" if silent else ""}" id="{esc(row["crop_id"])}">',
                f'<h3 class="id">{esc(row["crop_id"])}</h3>',
                f'<p class="muted">{esc(row["catalogue_file"])} · {esc(", ".join(row["failure_types"]))} · R7: {esc(row["r7_status"])}</p>',
                f'<a href="docai_failed_lines/images/{esc(row["crop_id"])}.png"><img class="crop" loading="lazy" width="{row["width_px"]}" height="{row["height_px"]}" src="docai_failed_lines/images/{esc(row["crop_id"])}.png" alt="Native grayscale crop {esc(row["crop_id"])}"></a>',
                f'<div class="note"><b>Owner / catalogue observation</b>\n{esc(row["owner_words"])}\n{esc(row["observation"])}</div>',
                f'<p class="muted">Expected risk: {esc(row["expected_ocr_risk"])}</p>']
            if row.get('visual_observation'):
                parts.append(f'<div class="note"><b>T10 visual observation</b>\n{esc(row["visual_observation"])}</div>')
            for c in row['comment_associations']:
                parts.append(f'<div class="note"><b>{esc(c["comment_id"])} · {esc(c["failure_type"])} · #{c["number"]}</b>\n{esc(c["owner_words"])}\n{esc(c["observation"])}</div>')
            if row['status']=='ok':
                parts += [f'<div class="events"><span>{row["width_px"]} × {row["height_px"]} px</span><span>{row["lines_returned"]} layout lines</span><span>Mean symbol confidence {fmt(row["mean_symbol_confidence"])}</span><span>Minimum {fmt(row["min_symbol_confidence"])}</span><span>{row["total_characters"]} characters · {fmt(row["characters_per_100px_width"])} / 100 px</span></div>',
                    f'<p><b>{esc(row["treatment"])}</b> · {esc(", ".join(row["exposure_signals"]) or "no exposure signal")}</p>', '<ol class="ocr" lang="el">']
                for text, conf in zip(row['text_per_line'],row['line_confidences']):
                    parts.append(f'<li>{esc(text)} <small class="muted">[line confidence {fmt(conf)}]</small></li>')
                parts += ['</ol>', f'<p class="muted">Empty: {str(row["empty"]).lower()} · Greek set: {esc("".join(row["greek_characters"]))}</p>',
                    f'<a href="docai_failed_lines/responses/{esc(row["crop_id"])}.json">Raw response and SHA receipt</a>']
            else:
                parts.append(f'<p><b>{esc(row["status"])}</b> · No Google output.</p>')
            parts.append('</article>')
        parts.append('</section>')
    parts += ['<section><h2>Types without a crop measurement</h2>']
    for kind, s in summary['types'].items():
        if not s['n_measured']:
            parts.append(f'<p><b>{esc(kind)}</b>: withheld, absent crop, or no unambiguous region. See report for page comments; no treatment is inferred.</p>')
    parts.append('</section></main></html>')
    (out/'docai_failed_lines_review.html').write_text('\n'.join(parts), encoding='utf-8')


def run(directory: Path, out: Path, *, offline=False, reader=None):
    directory, out = directory.resolve(), out.resolve()
    output = out/'docai_failed_lines'
    reader = reader or DocAIReader('ocr-ground-truth-20261008', 'eu', '9a98b7aca3c19561',
        DEFAULT_VERSION, language_hints=('el',), enable_symbol=True, receipts_dir=output/'adapter_receipts')
    out.mkdir(parents=True, exist_ok=True)
    with run_lock(output/'run.lock'):
        rows = load_catalogues(directory)
        comments = derive_comment_crops(directory, rows, output)
        atomic_json(output/'inventory.json', rows)
        permitted = [r for r in rows if r['status']!='withheld_anemi']
        print(f'inventory: {len(rows)} crop IDs, {len(permitted)} permitted, {len(rows)-len(permitted)} withheld input crops', flush=True)
        try:
            for i, row in enumerate(permitted, 1):
                value = cached_response(row, output, reader, offline=offline)
                row.update(crop_metrics(value['response'],row['width_px'],row['height_px']))
                row.update(status='ok', request_id=value['request_id'], receipt_id=value['receipt_id'])
                if i % 10 == 0 or i == len(permitted):
                    print(f'completed {i}/{len(permitted)} crop IDs', flush=True)
                    atomic_json(output/'receipt.json', receipt(rows,directory,output,reader,'running'))
        except Exception as error:
            row['status']='error'
            row['error']=str(error)
            rec=receipt(rows,directory,output,reader,'stopped',str(error))
            build_artifacts(rows,comments,directory,out,rec)
            print(f'STOPPED: {error}', flush=True)
            return rec
        rec=receipt(rows,directory,output,reader,'complete')
        build_artifacts(rows,comments,directory,out,rec)
        print(f"complete: {rec['calls']} calls; US${rec['estimated_cost_usd']:.4f}; {rec['withheld_anemi']} Anemi files withheld", flush=True)
        return rec


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--offline', action='store_true', help='rebuild from saved responses; no ADC or API calls')
    args=parser.parse_args(argv)
    result=run(args.catalogue,args.out,offline=args.offline)
    return 0 if result['status']=='complete' else 1


if __name__=='__main__':
    raise SystemExit(main())
