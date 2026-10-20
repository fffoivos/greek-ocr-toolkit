#!/usr/bin/env python3
"""T15 complete offline replay, receipts, blind image/text checks and inventory."""
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
import base64
import io
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.harvest.page_reads import build_blind_review, _response_geometry
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.montage_controls import git_state, audit_git
from scripts.harvest.page_reads import OUT, BULK, ENGINES, preflight, evaluate, sha


class ReviewParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = {}
        self.card = None
        self.in_pre = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article':
            self.card = attrs['id']
            assert self.card not in self.cards
            self.cards[self.card] = dict(images=[], readings=[], selects=0)
        elif self.card and tag == 'img':
            assert attrs['src'].startswith('data:image/png;base64,')
            data = base64.b64decode(attrs['src'].split(',', 1)[1], validate=True)
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                self.cards[self.card]['images'].append(np.asarray(image).copy())
        elif self.card and tag == 'pre':
            self.in_pre = True
            self.cards[self.card]['readings'].append('')
        elif self.card and tag == 'select':
            self.cards[self.card]['selects'] += 1
        if tag in ('img', 'link', 'script', 'iframe'):
            assert not any(attrs.get(k, '').startswith(('http:', 'https:', 'file:')) for k in ('src', 'href'))
    def handle_endtag(self, tag):
        if tag == 'article':
            self.card = None
        elif tag == 'pre':
            self.in_pre = False
    def handle_data(self, data):
        if self.card and self.in_pre:
            self.cards[self.card]['readings'][-1] += data


def main():
    receipt = json.loads((OUT / 'receipt.json').read_text())
    for name, digest in receipt['source_sha256'].items():
        assert sha(REPO / name) == digest, name
    for name, digest in receipt['artifact_sha256'].items():
        assert sha(OUT / name) == digest, name
    rows, all_rows, baselines, manifest, sample, plan = preflight()
    # preflight independently re-renders all PDFs and verifies all original
    # cached crops/raws/receipt hashes against the frozen evidence, disk only.
    comparisons, summary = evaluate(rows, baselines, manifest, sample, write=False)
    assert comparisons == read_jsonl(OUT / 'comparisons.jsonl')
    assert summary == json.loads((OUT / 'summary.json').read_text())
    assert len(comparisons) == 1000 and len(manifest) == 253
    assert len(list((OUT / 'assignments').glob('*.json'))) == 506
    reservations = read_jsonl(BULK / 'google/budget.jsonl')
    assert len(reservations) == 506 == json.loads((BULK / 'google/budget.state.json').read_text())['calls']
    assert Counter(r['engine'] for r in reservations) == dict(vision=253, docai=253)
    assert len({(r['engine'], r['key']) for r in reservations}) == 506
    expected = {(e, p['image_sha256']) for p in manifest for e in ENGINES}
    assert {(r['engine'], r['key']) for r in reservations} == expected
    assert sum(r['micro_usd'] for r in reservations) == 759000
    assert receipt['cost']['cost_usd'] == .759 and receipt['cost']['cap_usd'] == 2
    response_receipts = json.loads((OUT / 'page_response_receipts.json').read_text())
    converted_docai_pages = 0
    for engine in ENGINES:
        ledger_path = BULK / ('google/vision/adapter_receipts/ledger.jsonl' if engine == 'vision' else 'google/docai/ledger.jsonl')
        ledger = read_jsonl(ledger_path)
        assert len(ledger) == 253
        assert all(r['status'] == 'ok' and not r['cached'] and r['pages_billed'] == 1 for r in ledger)
        assert {r['crop_sha256'] for r in ledger} == {p['image_sha256'] for p in manifest}
        reserved = {r['key']: r for r in reservations if r['engine'] == engine}
        for response in ledger:
            raw_path = Path(response['raw_json_path'])
            assert raw_path.is_relative_to(BULK)
            assert response['binding'] == sample['bindings'][engine]
            assert sha(raw_path) == response['raw_sha256']
            raw = json.loads(raw_path.read_text())
            native_page = next(p for p in manifest if p['image_sha256'] == response['crop_sha256'])
            if engine == 'vision':
                returned = raw['responses'][0]['fullTextAnnotation']['pages']
                assert len(returned) == 1
                assert (returned[0]['width'], returned[0]['height']) == (native_page['width'], native_page['height'])
            else:
                returned = raw['document']['pages']
                assert len(returned) == 1
                assert returned[0]['dimension']['unit'] == 'pixels'
                geometry = _response_geometry(engine, raw, (native_page['width'], native_page['height']))
                converted_docai_pages += geometry['coordinate_frame']['converted']
                assert geometry['coordinate_frame']['native_size'] == [native_page['width'], native_page['height']]
                if (returned[0]['dimension']['width'], returned[0]['dimension']['height']) != (native_page['width'], native_page['height']):
                    assert geometry['coordinate_frame']['converted']
            reservation = reserved[response['crop_sha256']]
            assert reservation['time'] <= datetime.fromisoformat(response['timestamp']).timestamp()
            if engine == 'vision':
                cache_path = BULK / 'google/vision/responses' / (response['crop_sha256'] + '.json')
            else:
                cache_path = raw_path.parent / 'cache.json'
            cache = json.loads(cache_path.read_text())
            assert cache['binding'] == response['binding']
            assert cache['raw_sha256'] == response['raw_sha256'] and cache['receipt_id'] == response['receipt_id']
            matching = [r for r in response_receipts if r['engine'] == engine and r['receipt_id'] == response['receipt_id']]
            assert len(matching) == 1 and matching[0]['raw_sha256'] == response['raw_sha256']
    assert converted_docai_pages == 1
    page, key = build_blind_review(comparisons, all_rows, manifest)
    assert page == (_data_input(OUT / 'blind_review.html')).read_text()
    assert key == json.loads((OUT / 'blind_key.json').read_text())
    parser = ReviewParser()
    parser.feed(page)
    assert len(parser.cards) == 40
    assert Counter(c['stratum'] for c in key['cards']) == dict(vision_only=10, docai_only=10, both=10)
    assert len({c['id'] for c in key['cards']}) == 30
    indexed = {(r['id'], r['engine']): r for r in comparisons}
    records = {r['id']: r for r in rows}
    pages = {p['id']: p for p in manifest}
    for card in key['cards'] + key['most_changed']:
        ident = card['id']
        parsed = parser.cards[card['card']]
        assert parsed['selects'] == 2
        expected_text = [indexed[ident, e][card['order'][e][letter] + '_text'] or '∅' for e in ENGINES for letter in ('A', 'B')]
        assert parsed['readings'] == expected_text
        with Image.open(records[ident]['straight_crop']) as crop:
            np.testing.assert_array_equal(parsed['images'][0], np.asarray(crop))
        if 'context_box' in card:
            with Image.open(pages[records[ident]['page_id']]['image']) as native:
                np.testing.assert_array_equal(parsed['images'][1], np.asarray(native.crop(tuple(card['context_box']))))
        else:
            assert len(parsed['images']) == 1
    examples = json.loads((OUT / 'failure_examples.json').read_text())
    blind_ids = {c['id'] for c in key['cards'] + key['most_changed']}
    assert len(examples['examples']) == 6
    for example in examples['examples']:
        assert example['id'] not in blind_ids
        assert (OUT / example['image']).exists()
        with Image.open(OUT / example['image']) as overlay:
            box = example['region_box']
            assert overlay.size == (box[2] - box[0], box[3] - box[1])
        assignment = json.loads((OUT / example['assignment']).read_text())
        assert all(item == assignment['line_assignment']['lines'][item['index']] for item in example['returned_boxes'])
        assert assignment['line_assignment']['targets'][example['id']][example['flag']]
    for engine, counts in examples['merged_box_diagnostics'].items():
        assert sum(counts.values()) == summary['page_box_counts'][engine]['merged_boxes']
    tests = ET.parse(OUT / 'tests.xml').getroot()
    cases = tests.findall('.//testcase')
    assert cases and not tests.findall('.//failure') and not tests.findall('.//error')
    git_audit = audit_git(json.loads((OUT / 'git_before.json').read_text()), git_state())
    atomic(OUT / 'git_audit.json', git_audit)
    result = dict(status='passed', timestamp=datetime.now(timezone.utc).isoformat(), offline=True,
        pages_rerendered=253, native_png_byte_matches=253, pdf_recorded_hash_matches=253,
        converted_docai_pages=converted_docai_pages,
        preserved_crop_baselines=500, page_responses=506, unique_reserved_attempts=506,
        calls_per_reader=253, cost_usd=.759, replayed_assignments=506, replayed_comparisons=1000,
        blind_cards=30, context_cards=10, decoded_native_inline_images=50, tests_passed=len(cases),
        git_audit=git_audit)
    atomic(OUT / 'validation.json', result)
    qa = json.loads((OUT / 'gallery_qa.json').read_text())
    qa.update(structural_qa='passed', validated_cards=30, validated_context_cards=10,
              decoded_native_inline_images=50, tests_passed=len(cases))
    atomic(OUT / 'gallery_qa.json', qa)
    files = {}
    for root in (OUT, BULK):
        for path in sorted(root.rglob('*')):
            if path.is_file() and path.name != 'inventory.json':
                files[str(path.relative_to(REPO))] = dict(bytes=path.stat().st_size, sha256=sha(path))
    for name in (*receipt['source_sha256'], 'docs/records/harvest/PAGE_READS_v1.md', 'docs/INVENTORY.md'):
        path = REPO / name
        files[name] = dict(bytes=path.stat().st_size, sha256=sha(path))
    atomic(OUT / 'inventory.json', dict(schema='greekocr-t15-inventory-1', files=files))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
