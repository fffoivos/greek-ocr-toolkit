"""T27 offline dual-label records, unchanged T20 admission, O5 audit and reports."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

from greekocr.harvest import admission, wikisource as policy
from greekocr.harvest.readers import atomic, read_jsonl
from greekocr.harvest.page_reads import _response_geometry
from scripts.harvest import vouli, vouli_outputs, round1, compact_parliament_raw as archive
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest.admit_round1 import write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows
from scripts.harvest.wikisource import ROOT, OUT, BULK, UA

GOOGLE = BULK / 'google'


def sha(path):
    return vouli.sha(path)


def relative(path):
    return str(Path(path).relative_to(ROOT))


def transcriptions():
    """Derive cleaned text from frozen raw bytes; retain all original saved files."""
    result = {}
    for path in sorted((OUT / 'transcriptions').glob('*.json')):
        saved = json.loads(path.read_text()); raw = ROOT / saved['raw_path']
        if sha(raw) != saved['receipt']['sha256']:
            raise ValueError('frozen wikitext changed')
        parsed = policy.strip_wikitext(raw.read_text())
        result[saved['page']['id']] = dict(saved, **parsed,
            parent_transcription_path=relative(path),
            stripping_policy_sha256=sha(ROOT / 'greekocr/harvest/wikisource.py'))
        atomic(OUT / 'cleaned_transcriptions' / path.name, result[saved['page']['id']])
    return result


def read_records(plan, gold):
    records, audits = [], []
    for index, p in enumerate(plan['pages'], 1):
        parsed_path = GOOGLE / 'parsed/docai' / (p['image_sha256'] + '.json')
        parsed = json.loads(parsed_path.read_text())
        if parsed['status'] != 'ok' or parsed['binding'] != plan['binding'] or sha(ROOT / p['image']) != p['image_sha256']:
            raise ValueError('reader/image binding mismatch')
        raw_path = Path(parsed['raw_json_path']); cache = json.loads((raw_path.parent / 'cache.json').read_text())
        data, packed = archive.raw_bytes(raw_path)
        if hashlib.sha256(data).hexdigest() != cache['raw_sha256'] or cache['crop_sha256'] != p['image_sha256']:
            raise ValueError('raw response custody mismatch')
        raw = json.loads(data)
        rows, error = [], None
        try:
            geometry = _response_geometry('docai', raw, (p['width'], p['height']))
            rows, _, _, _ = make_rows(p, raw['document'], geometry)
        except ValueError as exc:
            error = str(exc)
        alignment, blocks = policy.align_lines([r['docai_text'] for r in rows], gold[p['id']]['lines'])
        for r, aligned in zip(rows, alignment):
            r.update(**aligned, lang=p['lang'], source=p['source'], licence=p['licence'],
                source_url=p['source_url'], index_url=p['index_url'], attribution=p['attribution'],
                human_transcription_licence=p['human_transcription_licence'],
                docai_label=policy.nfc(r['docai_text']), read_batch='wikisource',
                page_gate_failed=not p['gate']['accepted'], page_gate_flags=p['gate']['flags'],
                transcription_path=relative(OUT / 'cleaned_transcriptions' / (p['id'] + '.json')),
                transcription_sha256=gold[p['id']]['receipt']['sha256'], train_pool_eligible=False)
            if r['page_gate_failed']:
                r['flags'].append('page_gate_failed')
        receipt = dict(receipt_id=parsed['receipt_id'], raw_sha256=cache['raw_sha256'],
            parsed_path=relative(parsed_path), parsed_sha256=sha(parsed_path),
            storage_path=relative(packed or raw_path), storage_sha256=sha(packed or raw_path))
        atomic(OUT / 'assignments' / (p['id'] + '.json'), dict(page=p, reader=receipt,
            records=rows, alignment_blocks=blocks, geometry_error=error))
        records.extend(rows)
        audits.append(dict(page_id=p['id'], lang=p['lang'], lines=len(rows), geometry_error=error,
            gate_accepted=p['gate']['accepted'], aligned=sum(r['alignment'] == 'aligned' for r in rows), reader=receipt))
        if index % 25 == 0 or index == len(plan['pages']):
            print(f"aligned pages {index}/{len(plan['pages'])}; lines {len(records)}", flush=True)
    atomic(OUT / 'read_summary.json', dict(pages=audits, pages_read=len(audits), lines=len(records)))
    return records


def admit_records(records, held):
    quality = admission.page_quality(records)
    splits = {b['book_key']: b['split'] for b in held}
    kept, rejected = [], []
    for r in records:
        good, cls, reasons, label = admission.admit(dict(r, bad_page=quality[r['page_id']]['bad_page']))
        extra = {k: r[k] for k in ('human_label', 'docai_label', 'cer_docai_vs_human', 'alignment', 'human_line_indices')}
        if good:
            fields = ('id', 'page_id', 'book_key', 'year', 'decade', 'confidence', 'bbox', 'source', 'licence',
                'source_url', 'attribution', 'read_batch', 'lang', 'page_gate_failed', 'page_gate_flags',
                'transcription_path', 'transcription_sha256', 'human_transcription_licence')
            kept.append(dict({k: r[k] for k in fields}, **extra, label=label, split=splits[r['book_key']],
                script_class=cls, has_spacing_mark=admission.has_spacing_mark(label), train_pool_eligible=False))
        else:
            rejected.append(dict(id=r['id'], reasons=reasons, docai_text=r['docai_text'], **extra))
    if any(r['split'] not in ('test', 'dev') for r in kept):
        raise ValueError('T27 can never enter train')
    return kept, rejected, quality


def train_collision_audit(gold, records):
    """Scan every existing repo docs JSONL for train rows; keep prior files intact.

    Both human and Google labels are reserved, including labels whose crops or
    OCR quality are rejected. This is stricter than an admitted-only O5 check.
    """
    labels = defaultdict(set)
    for pid, g in gold.items():
        for line in g['lines']:
            if line['usable']:
                labels[admission.normalize_label(line['text'])].add('human:' + pid)
    for r in records:
        labels[admission.normalize_label(r['docai_label'])].add('docai:' + r['page_id'])
    audits, collisions, crop_ids = [], [], {}
    files = sorted((ROOT / 'docs').rglob('*.jsonl'))
    files += sorted(p for p in (ROOT / 'docs').rglob('*.json')
                    if p.name in ('manifest_train.json', 'train_pool.json') or p.stem.endswith('_train'))
    for path in files:
        if BULK in path.parents or OUT in path.parents or 'harvest_big' in path.parts:
            continue
        count = matches = 0
        with path.open() as stream:
            if path.suffix == '.jsonl':
                rows = ((number, json.loads(line)) for number, line in enumerate(stream, 1) if line.strip())
            else:
                value = json.load(stream)
                if not isinstance(value, list):
                    raise ValueError('train JSON manifest must be a list: ' + relative(path))
                rows = enumerate(value, 1)
            for number, row in rows:
                implicit_train = path.suffix == '.json'
                if (not isinstance(row, dict) or row.get('split', 'train' if implicit_train else None) != 'train'
                        or not isinstance(row.get('label'), str)):
                    continue
                count += 1
                label = admission.normalize_label(row['label'])
                if label in labels:
                    crop = row.get('crop_path', row.get('crop'))
                    crop_key = (row.get('source'), str((ROOT / crop).resolve())) if crop else None
                    if crop_key and row.get('id'):
                        crop_ids[crop_key] = row['id']
                    matches += 1
                    ident = row.get('id') or crop_ids.get(crop_key) or ('crop:' + crop if crop else f'{relative(path)}:{number}')
                    collisions.append(dict(id=ident, source=row.get('source'), record_file=relative(path),
                        row_number=number, crop_path=crop, label=row['label'], normalized_label=label, reason='label_in_holdout',
                        matching_holdout_labels=sorted(labels[label])))
        audits.append(dict(path=relative(path), sha256=sha(path), train_rows=count, collisions=matches))
    write_jsonl(OUT / 'prior_train_exclusions.jsonl', collisions)
    report = dict(schema='t27e-o5-1', scope='all docs JSONL with split=train plus JSON train manifests/pools (implicit train); bulk provider caches and this wave excluded',
        human_labels=sum(any(k.startswith('human:') for k in refs) for refs in labels.values()),
        reserved_labels=len(labels), files_checked=len(audits), train_pools=[a for a in audits if a['train_rows']],
        collision_occurrences=len(collisions), unique_colliding_ids=len({(r['source'], r['id']) for r in collisions}),
        prior_files_modified=False, exclusions_file=relative(OUT / 'prior_train_exclusions.jsonl'), files=audits)
    atomic(OUT / 'label_in_holdout.json', report)
    return report


def compiled_path(p):
    return Path(p['lang']) / f"{p['year']}_{compiler.slug(p['title'])}" / f"p{p['page']:04d}.jpg"


def compiled_canvas(image, rows, page):
    base, layout = compiler.render_page(image, rows)
    width, height = image.size
    human = Image.new('RGB', (width, height), 'white'); draw = ImageDraw.Draw(human)
    for r in rows:
        text = r['human_label'] if r['alignment'] == 'aligned' else '[unaligned]'
        x0, y0, x1, y1 = r['bbox']
        size = compiler.fit(draw, text, x1 - x0, layout['page_font_size'])
        draw.text((x0, y0), text, font=compiler.font(size), fill=(0, 0, 0) if r['human_label'] else (140, 50, 140))
    canvas = Image.new('RGB', (base.width + width + compiler.GAP, base.height + 56), 'white')
    canvas.paste(base, (0, 56)); canvas.paste(human, (base.width + compiler.GAP, compiler.PAD + 56))
    draw = ImageDraw.Draw(canvas)
    title = 'SCAN | GOOGLE DOCUMENT AI | WIKISOURCE HUMAN (one-to-one only)'
    if not page['gate']['accepted']:
        title += ' | PAGE GATE FAILED: ' + ', '.join(page['gate']['flags'])
    draw.text((compiler.PAD, 8), title, font=compiler.font(24), fill=(180, 0, 0) if not page['gate']['accepted'] else (0, 0, 0))
    return canvas, layout


def build():
    vouli.check_frozen()
    gold = transcriptions()
    plan = json.loads((OUT / 'plan.json').read_text()) if (OUT / 'plan.json').exists() else None
    records = read_records(plan, gold) if plan else []
    held = json.loads((OUT / 'holdout_books.json').read_text())
    kept, rejected, quality = admit_records(records, held)
    manifest = plan['pages'] if plan else []
    kept, crop_rejected, failures, geometry = vouli_outputs.plan_crops(records, kept,
        {p['id']: (p['width'], p['height']) for p in manifest})
    rejected.extend(crop_rejected)
    by_page = defaultdict(list)
    for row in records:
        by_page[row['page_id']].append(row)
    kept_by_id = {r['id']: r for r in kept}; compiled = []
    for index, p in enumerate(manifest, 1):
        with Image.open(ROOT / p['image']) as image:
            image.load()
            for r in by_page[p['id']]:
                if r['id'] not in kept_by_id:
                    continue
                a = kept_by_id[r['id']]; bounds, trimmed = geometry[r['id']]
                crop = image.crop(tuple(bounds))
                path = BULK / 'crops' / p['key'] / f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                path.parent.mkdir(parents=True, exist_ok=True); crop.save(path, compress_level=3)
                a.update(crop_path=relative(path), crop_sha256=sha(path), crop_width=crop.width,
                    crop_height=crop.height, crop_bbox=bounds, trimmed=trimmed)
            canvas, layout = compiled_canvas(image, by_page[p['id']], p)
            path = BULK / 'compiled' / compiled_path(p); path.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(path, quality=90, subsampling=0)
            compiled.append(dict(page_id=p['id'], path=relative(path), sha256=sha(path),
                raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(), layout=layout))
        if index % 25 == 0 or index == len(manifest):
            print(f"crops/compiled pages {index}/{len(manifest)}", flush=True)
    for name, rows in [('records', records), ('admitted', kept), ('rejected', rejected)]:
        write_jsonl(OUT / (name + '.jsonl'), rows)
    atomic(OUT / 'crop_failures.json', failures)
    atomic(BULK / 'compiled/compile_receipt.json', dict(pages=compiled, builder_sha256=sha(__file__)))
    o5 = train_collision_audit(gold, records)
    cer = policy.cer_summary(records)
    per_work = []
    for book in json.loads((OUT / 'source_books.json').read_text()):
        rows = [r for r in records if r['book_key'] == book['key']]
        cohort = policy.cer_summary(rows)[book['lang']]
        per_work.append(dict(book_key=book['key'], title=book['title'], lang=book['lang'],
            year=book['year'], pages=sum(p['key'] == book['key'] for p in manifest),
            admitted=sum(r['book_key'] == book['key'] for r in kept), **cohort))
    reasons = Counter(reason for r in rejected for reason in r['reasons'])
    acquisition = json.loads((OUT / 'acquisition_summary.json').read_text()) if (OUT / 'acquisition_summary.json').exists() else {}
    blocked = acquisition.get('blocked_by_size_policy', False)
    status = ('complete' if len(manifest) == 400 else
              'blocked_thumbnail_width' if blocked else
              'complete_with_source_shortfall' if manifest and acquisition.get('finished') else
              'closed_source_shortfall_no_images' if acquisition.get('finished') else
              'incomplete_source_images')
    summary = dict(schema='t27e-admission-1', status=status, acquisition=acquisition,
        selected_works={'el': 20, 'ru': 10}, selected_pages={'el': 300, 'ru': 100},
        transcriptions={lang: sum(g['page']['lang'] == lang for g in gold.values()) for lang in ('el', 'ru')},
        human_lines=sum(len(g['lines']) for g in gold.values()), pages_read=len(manifest),
        pages_by_language={lang: sum(p['lang'] == lang for p in manifest) for lang in ('el', 'ru')},
        input_lines=len(records), aligned=sum(r['alignment'] == 'aligned' for r in records),
        admitted=len(kept), rejected=len(rejected), crops=len(kept),
        per_class_split={c: {s: sum(r['script_class'] == c and r['split'] == s for r in kept)
                            for s in ('dev', 'test')} for c in admission.CLASSES},
        per_split={s: sum(r['split'] == s for r in kept) for s in ('train', 'dev', 'test')},
        per_reason=dict(reasons), bad_pages=[dict(page_id=k, **v) for k, v in quality.items() if v['bad_page']],
        gate_failures=[p['id'] for p in manifest if not p['gate']['accepted']],
        cer=cer, label_in_holdout=o5['collision_occurrences'], unique_train_collisions=o5['unique_colliding_ids'],
        per_work=per_work, geometry_errors=[a for a in json.loads((OUT / 'read_summary.json').read_text())['pages'] if a['geometry_error']],
        trimmed_crops=sum(r['trimmed'] for r in kept),
        admitted_aligned=sum(r['alignment'] == 'aligned' for r in kept),
        variant_selections=sum(len(g['variant_selections']) for g in gold.values()),
        admission_module_sha256=vouli.ADMISSION_SHA, train_allowed=False,
        unresolved_templates=dict(Counter(x['template'] for g in gold.values() for x in g['unknown_templates'])),
        hyphenation_events=sum(len(g['hyphenation']) for g in gold.values()))
    atomic(OUT / 'admission_summary.json', summary)
    return summary


def pct(value):
    return 'not measured' if value is None else f'{value * 100:.2f}%'


def esc(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def validate():
    """Validate obtained evidence without confusing preparation with completion."""
    from urllib.parse import urlsplit
    from urllib.robotparser import RobotFileParser
    from scripts.harvest.wikisource import HOSTS, local_receipts, load_plan
    vouli.check_frozen()
    books = json.loads((OUT / 'source_books.json').read_text())
    selected = json.loads((OUT / 'selected_pages.json').read_text())
    held = json.loads((OUT / 'holdout_books.json').read_text())
    assert Counter(b['lang'] for b in books) == {'el': 20, 'ru': 10}
    assert Counter(p['lang'] for p in selected) == {'el': 300, 'ru': 100}
    assert len({b['key'] for b in books}) == 30
    assert held == policy.splits(books)
    for b in books:
        assert 1850 <= b['year'] <= 1935
        assert len(b['eligible_pages']) >= (15 if b['lang'] == 'el' else 10)
        assert b['commons_receipt']['status'] == 200
        assert 'creativecommons.org/publicdomain/mark/1.0' in b['licence_url']
    gold = {json.loads(p.read_text())['page']['id']: json.loads(p.read_text())
            for p in (OUT / 'cleaned_transcriptions').glob('*.json')}
    assert set(gold) == {p['id'] for p in selected}
    for p in selected:
        g = gold[p['id']]
        assert g['page'] == p
        assert sha(ROOT / g['raw_path']) == g['receipt']['sha256']
        parsed = policy.strip_wikitext((ROOT / g['raw_path']).read_text())
        assert g['stripping_policy_sha256'] == sha(ROOT / 'greekocr/harvest/wikisource.py')
        assert parsed['proofread_level'] >= (3 if p['lang'] == 'el' else 4)
        assert all(g[k] == v for k, v in parsed.items())
    collisions = read_jsonl(OUT / 'prior_train_exclusions.jsonl')
    o5 = json.loads((OUT / 'label_in_holdout.json').read_text())
    for item in o5['files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    assert len(collisions) == o5['collision_occurrences']
    assert len({(r['source'], r['id']) for r in collisions}) == o5['unique_colliding_ids']
    def cached_allowed(url):
        path = BULK / 'http' / (urlsplit(url).hostname + '.robots.txt')
        parser = RobotFileParser()
        parser.parse(path.read_text(encoding='utf-8-sig').splitlines())
        return parser.can_fetch(UA, url)
    denials = {}
    for host in ('el.wikisource.org', 'ru.wikisource.org', 'commons.wikimedia.org'):
        url = f'https://{host}/w/api.php?action=query&list=allpages&apnamespace=104&format=json'
        denials[host] = not cached_allowed(url)
    assert all(denials.values())
    receipts, unclocked = [], []
    for path in (BULK / 'http').glob('*.json'):
        value = json.loads(path.read_text())
        if 'url' not in value:
            continue
        assert urlsplit(value['url']).hostname in HOSTS
        assert value['url'].endswith('/robots.txt') or cached_allowed(value['url'])
        body = path.with_suffix('.html')
        if not body.exists() and path.name.endswith('.robots.json'):
            body = path.with_name(path.name.replace('.robots.json', '.robots.txt'))
        if body.exists():
            assert sha(body) == value['sha256']
        (receipts if 'started_at' in value else unclocked).append(value)
    events = [v for v in read_jsonl(BULK / 'http/events.jsonl') if 'started_at' in v]
    starts = sorted({v['started_at'] for v in events})
    minimum_gap = min((b-a for a, b in zip(starts, starts[1:])), default=None)
    assert minimum_gap is None or minimum_gap >= 1
    budget = read_jsonl(GOOGLE / 'budget.jsonl')
    assert sum(r['micro_usd'] for r in budget) <= 800_000
    assert all(r['engine'] == 'docai' for r in budget)
    assert len({r['key'] for r in budget}) == len(budget)
    baseline = OUT / 't27e_git_before.json'
    if not baseline.exists():
        baseline = OUT / 'git_before.json'
    git_before = json.loads(baseline.read_text())
    git_after = round1.git_snapshot()
    atomic(OUT / 't27e_git_after.json', git_after)
    changed_git = [k for k in sorted(set(git_before) | set(git_after)) if git_before.get(k) != git_after.get(k)]
    main_metadata = ('HEAD', 'index', 'refs/heads/main', 'logs/HEAD', 'logs/refs/heads/main', 'config', 'packed-refs')
    assert all(git_before.get(k) == git_after.get(k) for k in main_metadata)
    # Concurrent worktrees share this object store. Keep both snapshots and
    # every change; do not overwrite the baseline or claim global equality.
    assert all(k.startswith(('objects/', 'worktrees/', 'refs/heads/astra/', 'logs/refs/heads/astra/')) for k in changed_git)
    atomic(OUT / 'git_metadata_audit.json', dict(main_metadata_unchanged=True,
        global_metadata_unchanged=not changed_git, task_git_writes=0,
        comparison_scope='all .git files; main control metadata checked separately',
        note='Changes in other worktrees, astra branches and the shared object store were observed concurrently; the collector makes no Git writes.',
        changes=[dict(path=k, before=git_before.get(k), after=git_after.get(k)) for k in changed_git]))
    frozen_inputs = json.loads((OUT / 't27e_frozen_inputs.json').read_text())
    for name, digest in frozen_inputs.items():
        assert sha(ROOT / name) == digest, name
    summary = json.loads((OUT / 'admission_summary.json').read_text())
    manifest = json.loads((OUT / 'manifest.json').read_text()) if (OUT / 'manifest.json').exists() else []
    records = read_jsonl(OUT / 'records.jsonl')
    admitted = read_jsonl(OUT / 'admitted.jsonl')
    rejected = read_jsonl(OUT / 'rejected.jsonl')
    plan = load_plan()
    assert manifest == plan['pages']
    assert len(records) == len(admitted) + len(rejected)
    assert len({r['id'] for r in records}) == len(records)
    assert {r['id'] for r in admitted}.isdisjoint(r['id'] for r in rejected)
    assert {r['key'] for r in budget} == {p['image_sha256'] for p in manifest}
    assert len(records) == summary['input_lines']
    assert len(admitted) == summary['admitted']
    assert all(r['split'] in ('dev', 'test') and r['train_pool_eligible'] is False for r in admitted)
    assert policy.cer_summary(records) == summary['cer']
    by_page = {p['id']: p for p in manifest}
    supplied = local_receipts(selected)
    unavailable = {p for p, receipt in supplied.items() if receipt.get('failed')}
    assert set(by_page) == set(supplied) - unavailable
    assert set(summary['acquisition']['unavailable_pages']) == unavailable
    crops_by_page = defaultdict(list)
    for r in admitted:
        crops_by_page[r['page_id']].append(r)
    for p in manifest:
        assert sha(ROOT / p['image']) == p['image_sha256']
        with Image.open(ROOT / p['image']) as image:
            assert image.mode == 'L' and max(image.size) <= 3500
            assert image.size == (p['width'], p['height'])
        assert p['gate']['gate_source_sha256'] == round1.GATE_SHA
        assert p['local_thumbnail_receipt'] == supplied[p['id']]
        assert p['scale_x'] == p['width'] / p['served_size'][0]
        assert p['scale_y'] == p['height'] / p['served_size'][1]
        with Image.open(ROOT / p['image']) as image:
            for r in crops_by_page[p['id']]:
                assert sha(ROOT / r['crop_path']) == r['crop_sha256']
                with Image.open(ROOT / r['crop_path']) as crop:
                    assert crop.mode == 'L'
                    assert image.crop(tuple(r['crop_bbox'])).tobytes() == crop.tobytes()
                    assert crop.size == (r['crop_width'], r['crop_height'])
    for r in records:
        if r['alignment'] == 'aligned':
            assert len(r['human_line_indices']) == 1
            assert r['human_label'] == gold[r['page_id']]['lines'][r['human_line_indices'][0]]['text']
            assert policy.distance(r['human_label'], r['docai_label']) == r['edit_distance']
    compiled = json.loads((BULK / 'compiled/compile_receipt.json').read_text())
    assert {p['page_id'] for p in compiled['pages']} == set(by_page)
    for p in compiled['pages']:
        assert sha(ROOT / p['path']) == p['sha256']
    parsed_keys = set()
    for path in (GOOGLE / 'parsed/docai').glob('*.json'):
        parsed = json.loads(path.read_text())
        assert parsed['status'] == 'ok'
        assert parsed['binding'] == plan['binding']
        parsed_keys.add(parsed['image_sha256'])
        if parsed['status'] == 'ok':
            data, _ = archive.raw_bytes(Path(parsed['raw_json_path']))
            assert all('content' not in p.get('image', {}) for p in json.loads(data)['document']['pages'])
    assert parsed_keys == {p['image_sha256'] for p in manifest}
    provider_ledger = read_jsonl(GOOGLE / 'docai/ledger.jsonl')
    assert len(provider_ledger) == len(parsed_keys)
    assert {r['crop_sha256'] for r in provider_ledger} == parsed_keys
    assert all(r['status'] == 'ok' and r['pages_billed'] == 1 for r in provider_ledger)
    image_events = [v for v in events if v.get('image_request')]
    image_starts = sorted(v['started_at'] for v in image_events)
    image_gap = min((b-a for a,b in zip(image_starts, image_starts[1:])), default=None)
    assert image_gap is None or image_gap >= 3
    resumed_events = [v for v in events if v['started_at'] >= baseline.stat().st_mtime]
    assert not resumed_events, 'T27e forbids all Wikimedia requests'
    image_states = [json.loads(p.read_text()) for p in (OUT / 'image_attempts').glob('*.json')]
    selected_by_id = {p['id']: p for p in selected}
    from scripts.harvest.wikisource import thumbnail_url, retry_delay
    retry_waits_checked = 0
    for state in image_states:
        assert len(state['attempts']) <= 6
        for number, attempt in enumerate(state['attempts']):
            assert attempt['resolution']['method'] == 'deterministic_commons_md5'
            assert attempt['receipt']['url'] == thumbnail_url(selected_by_id[state['page_id']], width=attempt['width'])
            if number:
                previous = state['attempts'][number - 1]['receipt']
                if previous['status'] == 429 or previous['status'] >= 500:
                    delay = retry_delay(previous['headers'], number, now=previous['started_at'])
                    assert attempt['receipt']['started_at'] - previous['started_at'] >= delay - .01
                    retry_waits_checked += 1
    complete = summary['status'] in ('complete', 'complete_with_source_shortfall')
    result = dict(schema='t27e-validation-1', preparation_verified=True, workflow_complete=complete,
        selected_works={'el': 20, 'ru': 10}, transcriptions={'el': 300, 'ru': 100},
        raw_wikitext_hashes_checked=400, frozen_t20_unchanged=True, no_git_writes=True,
        main_git_metadata_unchanged=True, global_git_metadata_unchanged=not changed_git,
        concurrent_git_metadata_changes=len(changed_git),
        frozen_selection_and_transcription_files_checked=len(frozen_inputs),
        robots_denies_standard_api=denials, timestamped_http_requests=len(events),
        minimum_recorded_request_gap_seconds=minimum_gap,
        bootstrap_receipts_without_request_start_timestamps=len(unclocked),
        prior_train_files_unchanged=len(o5['files']), unique_train_collisions=o5['unique_colliding_ids'],
        git_baseline=relative(baseline), obtained_images=len(manifest), google_lines=len(records),
        crop_pixels_checked=len(admitted), image_requests=len(image_events),
        t27e_wikimedia_requests=len(resumed_events), t27e_image_api_calls=0,
        t27e_text_refetches=0, local_jpeg_hashes_checked=len(manifest),
        unavailable_pages=len(unavailable), compiled_pages_checked=len(compiled['pages']),
        successful_unique_google_reads=len(parsed_keys), at_most_once_budget_verified=True,
        image_attempts_checked=sum(len(s['attempts']) for s in image_states),
        retry_waits_checked=retry_waits_checked,
        minimum_image_request_gap_seconds=image_gap,
        cost_usd=sum(r['micro_usd'] for r in budget) / 1_000_000,
        missing_stages=[] if complete else ['scan image acquisition', 'frozen page gates', 'Document AI page reads',
            'live line alignment and CER', 'line admission and native crops', 'compiled read images'],
        validation_scope='source/transcription/O5; actual image, raw response and crop checks only where obtained')
    atomic(OUT / 'validation.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def publish():
    summary = json.loads((OUT / 'admission_summary.json').read_text())
    books = json.loads((OUT / 'source_books.json').read_text())
    pages = json.loads((OUT / 'selected_pages.json').read_text())
    held = {r['book_key']: r['split'] for r in json.loads((OUT / 'holdout_books.json').read_text())}
    cost_file = OUT / 'cost_receipt.json'
    if not cost_file.exists():
        (GOOGLE / 'budget.jsonl').parent.mkdir(parents=True, exist_ok=True)
        (GOOGLE / 'budget.jsonl').touch(exist_ok=True)
        atomic(cost_file, dict(calls_reserved=0, cost_usd=0, cap_usd=.80, vision_calls=0,
            pricing_basis='T21 list-price estimate, USD 1.50 per 1000 pages; no invoice claim'))
    cost = json.loads(cost_file.read_text())
    tree = ET.parse(OUT / 'tests.xml')
    suites = list(tree.getroot().iter('testsuite'))
    tests = sum(int(x.get('tests', 0)) for x in suites)
    if any(int(x.get(k, 0)) for x in suites for k in ('failures', 'errors')):
        raise ValueError('tests failed')
    selection = '# T27 Wikisource work selection\n\n'
    selection += 'Live robots.txt denies standard `/w/api.php` listings on both Wikisources and Commons. '
    selection += 'Discovery used allowed category HTML, followed by index HTML. No denied API request was sent. '
    selection += 'The edition year and quality3/quality4 page links come from each index; the PD statement comes from the Commons description. '
    selection += 'Transcriptions use the allowed article `?action=raw` endpoint, with the raw bytes, hash and returned pagequality retained.\n\n'
    selection += 'Seed 20261015; 15 pages per Greek work, 10 per Russian work. 3 Greek + 1 Russian work are dev, the rest test; never train.\n\n'
    selection += '| Lang | Work / edition | Index page | Commons scan | Licence / PD statement | Eligible pages | Pages selected | Pages read | Split |\n|---|---|---|---|---|---:|---|---:|---|\n'
    for b in books:
        selected = ', '.join(str(p['page']) for p in pages if p['key'] == b['key'])
        read_pages = sum(1 for p in (OUT / 'assignments').glob(b['key'] + '-*.json')) if (OUT / 'assignments').exists() else 0
        selection += f"| {b['lang']} | {esc(b['title'])} ({b['year']}) | [index]({b['index_url']}) | [{esc(b['scan_file'])}]({b['commons_url']}) | [{esc(b['licence'])}]({b['licence_url']}) | {len(b['eligible_pages'])} | {selected} | {read_pages} | {held[b['key']]} |\n"
    (OUT / 'SELECTION.md').write_text(selection)
    report = '# T27e — Wikisource dual-label test collection\n\n'
    report += f"**Status: {summary['status']}.** Selected 20 Greek + 10 Russian works, 300 + 100 pages. "
    report += f"Fetched transcriptions: {summary['transcriptions']['el']} Greek / {summary['transcriptions']['ru']} Russian pages, {summary['human_lines']} source lines. "
    report += f"Scan pages read: {summary['pages_by_language']['el']} / {summary['pages_by_language']['ru']}; Google lines {summary['input_lines']}; aligned {summary['aligned']}; admitted/cropped {summary['admitted']}.\n\n"
    acquisition = summary.get('acquisition', {})
    if summary['status'] == 'blocked_thumbnail_width':
        report += '**Blocked by the prescribed thumbnail width:** deterministic Commons URLs were built from the saved file names '
        report += '(spaces to underscores, UTF-8 MD5 path, saved 1-based scan-page number). No image API was called. '
        report += f"All {acquisition.get('attempted_pages', 0)} attempted pages returned HTTP 400 with `Use thumbnail sizes listed on https://w.wiki/GHai`. "
        report += 'These are permanent width-policy rejections, not HTTP 429 or 404; the authorized fallback/backoff triggers did not occur. '
        report += 'The remaining pages were not requested after this shared policy failure was established. '
        report += '[MediaWiki production documentation](https://www.mediawiki.org/wiki/Common_thumbnail_sizes) lists standard widths '
        report += '20, 40, 60, 120, 250, 330, 500, 960, 1280, 1920 and 3840, and says direct requests at other widths are rejected. '
        report += 'Neither prescribed width (2500 or 1600) is in that list. A concrete 3840-pixel resume path is prepared and offline tested; '
        report += 'it remains unexecuted pending approval to change the coordinator\'s explicit widths. '
        report += 'No scan images or Google readings were obtained. The below-50% exception after exhausted retries does not establish completion here. '
        report += 'CER is undefined, not zero.\n\n'
    elif summary['status'] != 'complete':
        report += f"**Source shortfall:** obtained {acquisition.get('obtained', 0)}/400 page images. "
        report += 'See [acquisition_summary.json](acquisition_summary.json) and per-page [image attempts](image_attempts/). '
        report += 'Only obtained pages are passed to Google, including frozen page-gate failures.\n\n'
    if acquisition.get('shortfall_exception_applied'):
        report += 'The coordinator below-50% exception was applied after a page completed its backoff schedule. '
        report += f"Supported-width requests reached {acquisition['supported_width_attempted_pages']}/400 pages; "
        report += f"{acquisition['retry_exhausted_pages']} page exhausted its six-attempt allowance, including earlier saved requests. "
        report += f"{acquisition['retry_pending_pages']} additional page had pending retries at close-out. "
        report += 'The remaining pages were not exhausted or declared individually unavailable. '
        report += 'No scan images means no frozen image gates, Google reads, crops or compiled page images; language and mark-class CER are undefined. '
        report += 'This closes the bounded acquisition attempt with a source shortfall; the 400-page collection target and independent Google-label measurement were not achieved.\n\n'
        report += 'Retry states remain intact. To continue the remaining pages rather than apply this early-close exception again, '
        report += 'the collector supports `python -m scripts.harvest.wikisource acquire --exhaust-all-pages`; '
        report += 'that path still enforces the saved per-page six-attempt ceiling and all retry delays. It was not executed in this close-out.\n\n'
    report += '## T27e local scan inputs\n\n'
    report += 'The 15 Oct 09:40 coordinator decision supplies the scan of record under `harvest_big/wikisource/thumbs/<page_id>.jpg`. '
    report += 'No Wikimedia request was made during T27e: no image request, image API, new selection or transcription fetch. '
    report += 'The saved API robots denials and category/index HTML fallback from T27 remain the discovery evidence. '
    report += f"The import verified {acquisition.get('local_jpeg_hashes_checked', 0)} JPEG byte counts and SHA-256 hashes against the supplied "
    report += '[receipts](../harvest_big/wikisource/thumbs/receipts.jsonl), and checked each URL against its selected scan file and scan-page number. '
    report += f"Unavailable receipts: {acquisition.get('missing', 0)}; requested widths: `{json.dumps(acquisition.get('requested_widths', {}))}`. "
    report += '[Unavailable pages](unavailable_pages.json) lists only coordinator receipts marked failed. '
    report += 'Each JPEG was converted to greyscale and downscaled without upsampling so its long side is at most 3500 px. '
    report += 'The original dimensions, delivered dimensions and exact horizontal/vertical scale are recorded in [manifest.json](manifest.json). '
    report += 'PNG 200-dpi metadata is nominal; these thumbnails do not establish physical scan dpi. '
    report += f"The frozen gate flagged {len(summary['gate_failures'])} pages; all obtained pages, including flagged ones, were read. "
    report += 'Historical failed HTTP attempts remain unchanged as evidence from earlier attempts.\n\n'
    manifest = json.loads((OUT / 'manifest.json').read_text())
    gate_reasons = Counter(flag for p in manifest if not p['gate']['accepted'] for flag in p['gate']['flags'])
    report += f"Gate flags (overlapping): `{json.dumps(dict(gate_reasons))}`. Geometry extraction errors: {len(summary['geometry_errors'])}.\n\n"
    report += '## Labels and alignment\n\n'
    report += 'The scan licence field carries the recorded Commons PD statement; contributor transcription text has a separate CC-BY-SA-4.0 attribution field. '
    report += 'NFC and whitespace normalization preserve historical spelling and accents. Known formatting wrappers are removed; unknown templates carry a visible sentinel and cannot supply gold. '
    report += f"The {summary['variant_selections']} Russian `ВАР`/`ВАР2` wrappers select the first, historical spelling branch, verified against the supplied scans (Balmont scan page 86 and Satirikon scan page 16). "
    report += 'Poem-only `№` line counters absent from the print are removed; indentation/spacing templates supply no text. '
    report += 'All 400 original saved transcriptions and raw wikitext remain byte-identical; [cleaned_transcriptions/](cleaned_transcriptions/) contains separately derived text and the variant decisions. '
    report += 'Cross-page hyphenation templates retain the printed fragment and starting-page hyphen; decisions are logged. Literal end-of-line hyphens remain. '
    report += 'Source paragraph breaks and poem rows are retained; prose paragraphs are never reflowed into Google rows. Consequently much prose may be unalignable.\n\n'
    report += 'Global monotone sequence alignment uses character Levenshtein similarity (minimum 0.65), skipped-line cost 0.45 and split/merge penalty 0.25. '
    report += 'Only 1:1 blocks receive human_label and CER; split/merged and unmatched blocks remain unaligned. '
    report += 'CER is total NFC character edits / human characters across aligned lines before admission. It is conditional on alignability and similarity, not an unbiased estimate over all print or all Google lines. '
    report += 'Mark classes below are full-line CER cohorts containing that NFD mark in the human label; classes overlap. No-mark cohorts and absent languages have undefined CER.\n\n'
    report += '| Language / mark cohort | Google lines | Aligned | Aligned share | Human chars | Edits | CER |\n|---|---:|---:|---|---:|---:|---|\n'
    for lang in ('el', 'ru'):
        for name, value in [(lang, summary['cer'][lang])] + [(lang + ' / ' + k, v) for k, v in summary['cer'][lang]['mark_classes'].items()]:
            report += f"| {name} | {value['lines']} | {value['aligned']} | {pct(value['aligned_share'])} | {value['human_characters']} | {value['edit_distance']} | {pct(value['cer'])} |\n"
    report += '\n### Per-work coverage\n\n| Lang | Work | Pages | Google lines | Aligned | Aligned share | CER | Admitted |\n|---|---|---:|---:|---:|---:|---:|---:|\n'
    for value in summary['per_work']:
        report += f"| {value['lang']} | {esc(value['title'])} | {value['pages']} | {value['lines']} | {value['aligned']} | {pct(value['aligned_share'])} | {pct(value['cer'])} | {value['admitted']} |\n"
    report += '\n## Admission and train contamination\n\n'
    report += 'Frozen T20 admission remains byte-identical. The pipeline reads and visibly flags frozen page gate failures; post-read bad_page uses the standard T20 rule. '
    report += 'No T27 row can have split=train or train_pool_eligible=true. All source works are held out, including unaligned and rejected labels.\n\n'
    report += 'Admission uses only the Google reading. An admitted unaligned crop retains `human_label=null`; it is not independent human gold. '
    report += 'For human-reference evaluation, filter `alignment=aligned`. The full set remains test/dev only.\n\n'
    report += f"Aligned admitted crops: {summary['admitted_aligned']}; neighbour-trimmed crops: {summary['trimmed_crops']}.\n\n"
    report += '| Class | Dev | Test |\n|---|---:|---:|\n'
    for cls, counts in summary['per_class_split'].items():
        report += f"| {cls} | {counts['dev']} | {counts['test']} |\n"
    report += '\nRejection reasons: ' + (', '.join(f'{k}: {v}' for k, v in summary['per_reason'].items()) or 'none: no Google rows') + '.\n\n'
    o5 = json.loads((OUT / 'label_in_holdout.json').read_text())
    report += f"The O5 audit scanned {o5['files_checked']} JSONL/JSON files, including {len(o5['train_pools'])} populated train pools/admitted inventories. "
    report += 'This includes the T28 collection JSONL exports and `manifest_train.json`, whose training split is implicit in its filename. '
    report += f"It reserved {o5['reserved_labels']} distinct labels from the available human transcriptions and Google readings. "
    report += f"Collisions: {o5['collision_occurrences']} file occurrences / {o5['unique_colliding_ids']} distinct source+line IDs. "
    report += 'Every collision is listed for removal in [prior_train_exclusions.jsonl](prior_train_exclusions.jsonl); [label_in_holdout.json](label_in_holdout.json) binds every scanned file. '
    report += 'Prior snapshots were read only. No trainer should consume a listed collision.\n\n'
    report += '| Train file | Train rows | Collisions |\n|---|---:|---:|\n'
    for p in o5['train_pools']:
        report += f"| {p['path']} | {p['train_rows']} | {p['collisions']} |\n"
    report += '\n| Colliding line ID | Label |\n|---|---|\n'
    unique = {}
    for row in read_jsonl(OUT / 'prior_train_exclusions.jsonl'):
        unique.setdefault((row['source'], row['id']), row)
    for row in unique.values():
        report += f"| {row['id']} | {esc(row['label'])} |\n"
    report += '\nThis audit covers all resolved human source lines and every obtained Google label, including rejected and unaligned lines.\n'
    report += '\n## Cost, validation and limitations\n\n'
    report += f"USD {cost['cost_usd']:.4f} reserved; cap USD 0.80; {cost['calls_reserved']} Document AI attempts; zero Vision calls. "
    report += f"{tests} offline tests passed, including unchanged T20 admission, Greek/Russian wikitext fixtures and split/merge alignment fixtures. "
    report += 'The Google path reuses T21 at-most-once image-SHA reservations, native bbox inversion and symbol confidence, with automatic language detection and no implicit provider retries.\n\n'
    report += 'Page PNGs are grey, at most 3500 px on the long side, never upsampled, with nominal 200-dpi delivery metadata; physical source dpi must not be inferred from that metadata. '
    report += 'Any 1920/1280 px fallback is recorded explicitly and falls below the original 2000 px target under the coordinator exception. Embedded `document.pages[*].image.content` is removed before raw responses are saved. '
    report += 'Compiled scan / Google / human triptychs are under `harvest_big/wikisource/compiled/<lang>/<year>_<title40>/pNNNN.jpg`; '
    report += 'unaligned human panels are marked explicitly. Native greyscale crops retain original-resolution pixels from the delivered PNG. '
    report += 'Template encounter counts include discarded modern variant arguments; only unresolved sentinels surviving in the selected text prevent alignment. '
    report += f"Unresolved template counts: `{json.dumps(summary['unresolved_templates'], ensure_ascii=False)}`. "
    report += f"Hyphenation events retained: {summary['hyphenation_events']}. All HTTP response bodies, robots files and raw source wikitext are frozen under harvest_big/wikisource.\n"
    if (OUT / 'validation.json').exists():
        validation = json.loads((OUT / 'validation.json').read_text())
        report += f"\n[Validation](validation.json) checks all 400 raw text hashes, held-out work assignment, prior train file hashes and Git metadata. "
        report += f"The {validation['timestamped_http_requests']} timestamped crawler requests have minimum recorded spacing {validation['minimum_recorded_request_gap_seconds']:.6f} s; "
        report += f"{validation['bootstrap_receipts_without_request_start_timestamps']} initial bootstrap receipts have no request-start timestamp. "
        report += f"Workflow completion: `{str(validation['workflow_complete']).lower()}`. "
        report += f"Validation checked {validation['local_jpeg_hashes_checked']} local JPEGs, {validation['obtained_images']} grey page images, "
        report += f"{validation['crop_pixels_checked']} native crop rasters and {validation['compiled_pages_checked']} compiled image hashes. "
        report += f"T27e Wikimedia requests: {validation['t27e_wikimedia_requests']}; transcription refetches: {validation['t27e_text_refetches']}.\n"
        if validation.get('global_git_metadata_unchanged'):
            report += '\n[Git metadata audit](git_metadata_audit.json): all snapshotted Git metadata is unchanged during T27e.\n'
        if not validation.get('global_git_metadata_unchanged', True):
            report += '\n[Git metadata audit](git_metadata_audit.json): main HEAD, index, branch reference and logs are unchanged. '
            report += f"{validation['concurrent_git_metadata_changes']} changes were observed in other worktrees, astra branch metadata and the shared object store. "
            report += 'Both full snapshots are retained; global metadata equality is not claimed. The collector makes no Git writes.\n'
    (OUT / 'READS.md').write_text(report)
    state_path = ROOT / 'docs/records/harvest/collection/EXECUTION_STATE.md'
    state = state_path.read_text(); marker = '## Wave 7'
    section = f"{marker}\n\nT27e {summary['status']}: 20 Greek / 10 Russian works selected; "
    section += f"{summary['transcriptions']['el']} / {summary['transcriptions']['ru']} proofread transcriptions fetched; {summary['pages_read']} scan pages read, {summary['input_lines']} Google lines, {summary['admitted']} admitted. "
    section += f"USD {cost['cost_usd']:.4f}; {tests} offline tests passed. Test/dev only (3 Greek + 1 Russian dev works); T20 unchanged; zero Vision calls and Git writes. "
    section += f"Coordinator supplied {acquisition.get('obtained', 0)} receipt-bound JPEGs; {acquisition.get('missing', 0)} unavailable. No Wikimedia requests or text refetches in T27e. "
    if summary['status'] == 'blocked_thumbnail_width':
        section += f"Direct image requests for {acquisition.get('attempted_pages', 0)} pages returned HTTP 400 rejecting nonstandard thumbnail sizes. "
        section += 'No image API was called. Both prescribed widths, 2500 and 1600, are absent from Wikimedia\'s supported steps. '
        section += 'A 3840 px resume awaits approval to change the explicit widths; no Google calls; CER undefined.\n\n'
    else:
        section += f"CER el {pct(summary['cer']['el']['cer'])}; ru {pct(summary['cer']['ru']['cer'])}.\n\n"
    if acquisition.get('shortfall_exception_applied'):
        section += f"Below-50% exception after complete backoff on {acquisition['retry_exhausted_pages']} page; supported-width attempts reached {acquisition['supported_width_attempted_pages']}/400 pages. "
        section += 'Remaining pages were not individually exhausted. No independent CER measurement was obtained.\n\n'
    section += '[Selection](../wikisource/SELECTION.md), [report](../wikisource/READS.md), [summary](../wikisource/admission_summary.json), [train collisions](../wikisource/prior_train_exclusions.jsonl), [inventory](../wikisource/inventory.json).\n'
    state = re.sub(r'^\| 7 Wikisource test labels \|.*$',
        f"| 7 Wikisource test labels | T27 → T27b → T27c → T27d → T27e | {summary['status']} | 2026-10-15 | | {summary['pages_read']} / 400 | {summary['admitted']} | {cost['cost_usd']:.4f} |", state, flags=re.M)
    if marker in state:
        state = re.sub(r'## Wave 7\n.*?(?=\n## |\Z)', section.rstrip(), state, flags=re.S)
    else:
        state = state.rstrip() + '\n\n' + section
    state_path.write_text(state.rstrip() + '\n')
    inventory_path = ROOT / 'docs/INVENTORY.md'; inventory = inventory_path.read_text()
    entry = '## T27 — Wave 7 Wikisource dual labels\n\n'
    entry += '20 Greek / 10 Russian selected works, test/dev only. [Policy](../greekocr/harvest/wikisource.py), [collector](../scripts/harvest/wikisource.py), '
    entry += '[outputs](../scripts/harvest/wikisource_outputs.py), [offline tests](../tests/test_wikisource.py). '
    entry += '[Selection](harvest/wikisource/SELECTION.md), [reads/status](harvest/wikisource/READS.md), [summary](harvest/wikisource/admission_summary.json), '
    entry += '[O5 audit](harvest/wikisource/label_in_holdout.json), [inventory](harvest/wikisource/inventory.json). '
    entry += f"Source HTTP caches and raw proofread wikitext are ignored under harvest_big/wikisource. T27e status: {summary['status']}; "
    entry += f"{summary['pages_read']}/400 scan pages read, {summary['admitted']} admitted. "
    entry += 'T27e imports coordinator JPEGs with receipt/selection binding and recorded downscale factors; zero Wikimedia requests and no text refetch. '
    entry += 'Frozen gates flag only; all obtained pages are read under the USD 0.80 cap. Grey pages have a 3500 px long-side cap; raw responses omit embedded images.\n'
    if '## T27 —' in inventory:
        inventory = re.sub(r'## T27 —.*?(?=\n## |\Z)', entry.rstrip(), inventory, flags=re.S)
    else:
        inventory = inventory.rstrip() + '\n\n' + entry
    inventory_path.write_text(inventory.rstrip() + '\n')
    collection_inventory = ROOT / 'docs/records/harvest/collection/INVENTORY.md'
    text = collection_inventory.read_text()
    addition = '## T27e Wave 7 update\n\n'
    addition += f"{summary['pages_read']} local scan pages read; {summary['input_lines']} Google lines; {summary['aligned']} one-to-one human alignments; {summary['admitted']} test/dev crops. "
    addition += '[Current Wikisource inventory](../wikisource/inventory.json), [report](../wikisource/READS.md), '
    addition += '[validation](../wikisource/validation.json), [train collision exclusions](../wikisource/prior_train_exclusions.jsonl). '
    addition += 'This update supersedes the prior Wave 7 execution-state entry and the root INVENTORY description. '
    addition += 'The T28 output hashes above describe its earlier build; its collection pools remain unchanged and require a separate T28 rebuild.\n'
    if '## T27e Wave 7 update' in text:
        text = re.sub(r'## T27e Wave 7 update\n.*?(?=\n## |\Z)', addition.rstrip(), text, flags=re.S)
    else:
        text = text.rstrip() + '\n\n' + addition
    collection_inventory.write_text(text.rstrip() + '\n')
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name != 'inventory.json']
    files += [ROOT / p for p in ('greekocr/harvest/wikisource.py', 'scripts/harvest/wikisource.py',
        'scripts/harvest/wikisource_outputs.py', 'tests/test_wikisource.py', 'tests/data/wikisource/transcriptions.json')]
    atomic(OUT / 'inventory.json', dict(schema='t27-inventory-1', files=[dict(path=relative(p), bytes=p.stat().st_size, sha256=sha(p))
        for p in sorted(files)], bulk_path=relative(BULK), bulk_files=sum(p.is_file() for p in BULK.rglob('*'))))


if __name__ == '__main__':
    import sys
    {'build': build, 'validate': validate, 'publish': publish}[sys.argv[1]]()
