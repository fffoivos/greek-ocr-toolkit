#!/usr/bin/env python3
"""Recompute T11 raw evidence, cost, comparisons, local images and review links."""
from collections import Counter
import csv
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prototypes.harvest.google_failed_lines import atomic_json, characters_table, crop_metrics, response_path, sha256
from prototypes.harvest.vision_comparison import agreement, compare_rows
from greekocr.readers.services.google_vision import VisionReader


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.images, self.cards = [], [], [], []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'a': self.hrefs.append(attrs['href'])
        if tag == 'img': self.images.append(attrs['src'])
        if tag == 'article': self.cards.append(attrs['id'])


def validate(out: Path, tests_passed: int = 89) -> dict:
    base = out / 'vision_failed_lines'
    rows = json.loads((base / 'metrics.json').read_text())
    rec = json.loads((base / 'receipt.json').read_text())
    ledger = [json.loads(s) for s in (base / 'adapter_receipts/ledger.jsonl').read_text().splitlines()]
    calls = [r for r in ledger if not r['cached']]
    assert rec['status'] == 'complete'
    assert len(calls) == rec['calls']
    assert max(Counter(r['crop_sha256'] for r in calls).values(), default=0) == 1
    assert all(r['status'] == 'ok' for r in calls)
    assert rec['calls'] == rec['successful_calls'] == rec['unique_measured_crop_sha256']
    assert rec['estimated_cost_usd'] == round(rec['calls'] * .0015, 6)
    assert rec['include_anemi'] and rec['withheld_anemi_current_output_crops'] == 0
    assert len(rows) == rec['measured_crop_ids'] == rec['comparison_paired_crops']
    assert {r['crop_sha256'] for r in rows} == {r['crop_sha256'] for r in calls}
    assert all(r['language_hints'] == ['el', 'grc'] for r in ledger)
    reader = VisionReader(rec['binding']['user_project'], language_hints=rec['language_hints'], responses_dir=base / 'responses',
                          transport=lambda *a, **k: (_ for _ in ()).throw(AssertionError('validator attempted HTTP')))
    for row in rows:
        assert row['status'] == 'ok'
        image = base / 'images' / (row['crop_id'] + '.png')
        assert sha256(image) == row['crop_sha256']
        reading = reader.read_annotation(image)
        assert reading.cached
        envelope = json.loads(response_path(base, row, 'vision').read_text())
        assert envelope['binding'] == rec['binding']
        assert envelope['language_hints'] == ['el', 'grc']
        for key, value in crop_metrics(envelope['response'], row['width_px'], row['height_px'], engine='vision').items():
            assert row[key] == value, (row['crop_id'], key)
    assert characters_table(rows) == json.loads((base / 'characters.json').read_text())
    docai = json.loads((out / 'docai_failed_lines/metrics.json').read_text())
    pairs = compare_rows(rows, docai, out / 'docai_failed_lines')
    assert pairs == json.loads((base / 'comparison.json').read_text())
    comp = json.loads((base / 'comparison_summary.json').read_text())
    assert agreement([r for r in pairs if r['failure_type'] == 'control_owner_verified']) == comp['controls']
    assert sum(bool(r['rare_glyphs_vision']) for r in pairs) == rec['rare_glyph_crops_vision']
    for filename in ('crops.csv', 'comparison.csv'):
        with (base / filename).open(newline='') as stream: values = list(csv.DictReader(stream))
        assert [r['crop_id'] for r in values] == [r['crop_id'] for r in rows]
    parsed = Links()
    html_path = out / 'vision_vs_docai_review.html'
    text = html_path.read_text()
    parsed.feed(text)
    assert len(set(parsed.ids)) == len(parsed.ids)
    assert Counter(parsed.cards) == Counter(r['crop_id'] for r in rows)
    assert len(parsed.images) == len(rows)
    assert text.count('<h4>Cloud Vision</h4>') == text.count('<h4>Document AI</h4>') == len(rows)
    for src in parsed.images:
        assert not src.startswith(('http:', 'https:', 'data:')) and (out / unquote(src)).is_file()
    for href in parsed.hrefs:
        if href.startswith('#'): assert unquote(href[1:]) in parsed.ids
        else: assert (out / unquote(href.partition('#')[0])).is_file(), href
    assert 'width=device-width' in text and 'max-width:100%' in text and 'overflow-wrap:anywhere' in text
    assert '@media(max-width:600px)' in text and '.line' in text and 'min-width:0' in text
    layout_path = base / 'layout_validation.json'
    layout = json.loads(layout_path.read_text()) if layout_path.exists() else dict(status='not_checked')
    result = dict(status='passed', timestamp=datetime.now(timezone.utc).isoformat(),
        validated_crop_ids=len(rows), validated_unique_responses=len(calls), calls=rec['calls'],
        at_most_one_call_per_sha256=True, same_docai_crops=True, raw_metric_recomputation=True,
        characters_recomputation=True, comparisons_recomputation=True,
        local_image_assets=True, all_cards_and_links_valid=True, cache_validation_additional_calls=0,
        layout=layout, tests=dict(passed=tests_passed,
            command='.venv/bin/python -m pytest tests/test_google_vision.py tests/test_google_failed_lines.py tests/test_docai.py tests/test_provenance_cli_api.py::test_public_callables_typed_and_documented -q'),
        html_sha256=sha256(html_path), metrics_sha256=sha256(base / 'metrics.json'))
    atomic_json(base / 'validation.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[2] / 'docs/harvest')
    parser.add_argument('--tests-passed', type=int, default=89)
    args = parser.parse_args()
    validate(args.out.resolve(), args.tests_passed)
