"""Offline validation of the complete S8a4 DEV baseline and blind card set."""
from collections import Counter
import gzip
import json
import math
import random
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scripts.labelfix.s8_prepare import (
    E, OUT, ROOT, SEED, WAVES, METRICS, MODES, binding, canon, digest, dump,
    elision_policy, load, metrics, planted, rows, sha, word_box,
)
from scripts.labelfix.s8_verify_evidence import verify


def main():
    remote = verify()
    ids = set((OUT / 'S8_DEV_ids.txt').read_text().split())
    sources = load(E / 'sources.json')
    bound = load(E / 'frozen_binding.json')
    assert binding(bound['sources']) == bound
    baseline = rows(E / 'baseline_per_line.jsonl')
    assert len(baseline) == 600 and {r['id'] for r in baseline} == ids
    assert all(r['variant'] == 'original' for r in baseline)
    assert len(list((E / 'baseline/original').glob('*.json.gz'))) == 600
    for row in baseline:
        record = json.loads(gzip.decompress((E / 'baseline/original' / (row['id'] + '.json.gz')).read_bytes()))
        assert record['binding_sha256'] == digest(bound)
        assert record['crop_sha256'] == sha(record['crop'])
        assert digest(metrics(record['detector'])) == digest(row['metrics'])
        assert record['reader_inputs_sha256'] == digest({k: remote['runtime'][row['id']].get(k) for k in (
            'recogniser_text', 'recogniser_nfd', 'r1_predictions', 'coverage', 'peer_predictions', 'peer_coverage', 'k1_flags')})
        for mode in MODES:
            assert row['gate'][mode]['status'] == record['decisions'][mode]['status']
            assert row['gate'][mode]['proposal'] == record['modes'][mode]['text']
    aggregate = load(E / 'baseline_by_wave.json')
    for total in aggregate:
        selected = [r for r in baseline if total['wave'] == 'ALL' or r['wave'] == total['wave']]
        assert total['lines'] == len(selected)
        for field in ('letters', 'component_assignments', 'unnamed_blobs') + METRICS:
            assert total[field] == sum(r['metrics'][field] for r in selected)
        for field in METRICS:
            assert total['rates_percent'][field] == 100 * total[field] / total['letters']
        for mode in MODES:
            assert total['gate'][mode] == dict(Counter(r['gate'][mode]['status'] for r in selected))

    summary = load(E / 'card_counts.json')
    census = rows(E / 'word_census.jsonl'); plan = rows(E / 'dev_plan.jsonl')
    blind = load(OUT / 'cards/items_blind.json'); key = load(OUT / 'private/cards/items_key.json')
    data = [k for k in key if not k['control']]; controls = [k for k in key if k['control']]
    required = math.ceil(len(plan) * .08 / .92)
    assert len(census) == summary['words'] == 4942
    assert len(data) == len(plan) == summary['cards'] == 1649
    assert len(controls) == required == summary['controls_required'] == 144
    assert len(key) == len(blind) == len(data) + len(controls) <= 2000
    assert len(controls) / len(key) >= .08
    assert len({k['id'] for k in key}) == len(key)
    assert {x['uid'] for x in data} == {x['uid'] for x in plan}
    assert {x['line_id'] for x in data} <= ids
    assert all(set(b) == {'id', 'img', 'line_img', 'options', 'other_options'} for b in blind)
    assert not list((OUT / 'cards').rglob('items_key.json'))
    assert [b['id'] for b in blind] == [k['id'] for k in key]
    for wave in WAVES:
        pool = sorted([x for x in census if x['wave'] == wave and x['selection'] == 'all_agree_sample'], key=lambda x: x['uid'])
        expected = random.Random(SEED + wave).sample(pool, math.ceil(.05 * len(pool)))
        disputed = [x for x in census if x['wave'] == wave and x['selection'] == 'disagreement']
        selected = [x for x in data if x['wave'] == wave]
        assert {x['uid'] for x in selected} == {x['uid'] for x in expected + disputed}
        assert all(x['inclusion_probability'] == len(expected) / len(pool) for x in pool)
        assert all(x['inclusion_probability'] == 1 for x in disputed)
    for x in census:
        expected = elision_policy(x['raw_forms'])
        assert all(x[k] == v for k, v in expected.items())
        assert x['forms'] == {s: canon(v) for s, v in x['raw_forms'].items()}
    assert summary['by_elision_policy'] == dict(Counter(x['scoring_policy'] for x in data))
    # Counterexamples: accents, breathing, letters and numeral signs are never elision policy changes.
    for a, b in [('ἀπ’', 'ἀπ'), ('ἀπ\u1fbd', "ἀπ'")]:
        assert elision_policy({'a': a, 'b': b})['elision_alias_only']
    for a, b in [('ἀπ’', 'ἁπ'), ('ἀπ’', 'ἀπὸ'), ('α\u0374', 'α'), ('α\u0374', 'α\u02b9'), ('α\u0384', 'α\u1ffd')]:
        assert not elision_policy({'a': a, 'b': b})['elision_alias_only']
    verified = load(E / 'controls_verified.json')
    expected_controls = planted(verified, required, 'cards')
    assert {x['uid'] for x in controls} == {x['uid'] for x in expected_controls}
    location = lambda x: (x['line_id'], x['start'], x['end'])
    assert not {location(x) for x in controls} & {location(x) for x in data}
    assert len({location(x) for x in controls}) == required
    for x in verified:
        assert x['pixel_verified'] and x['source_crop_sha256'] == sha(sources[x['line_id']]['original_path'])
        assert x['review_sheet_sha256'] == sha(E / x['review_sheet'])
        assert x['full_line_sheet_sha256'] == sha(E / x['full_line_sheet'])
    answers = load(OUT / 'cards/answers_blank.json')
    assert [a['id'] for a in answers] == [b['id'] for b in blind]
    assert all(v is None for a in answers for k, v in a.items() if k != 'id')
    checked_lines = set()
    for b, k in zip(blind, key):
        assert b['options'] == k['options']
        assert b['other_options'] == ['none of these', 'unreadable']
        assert set(b['options'].values()) == {v or '∅' for v in k['forms'].values()}
        assert all(b[field] == k[field] for field in ('img', 'line_img'))
        assert k['crop_box'] == word_box(k, sources, remote)
        path = sources[k['line_id']]['original_path']
        assert k['source_crop_sha256'] == sha(path)
        with Image.open(path) as source:
            if k['line_id'] not in checked_lines:
                with Image.open(OUT / 'cards' / b['line_img']) as full:
                    assert full.size == source.size
                    assert np.array_equal(np.asarray(full), np.asarray(source.convert('RGB')))
                checked_lines.add(k['line_id'])
            box = k['crop_box']; width, height = box[2] - box[0], box[3] - box[1]
            with Image.open(OUT / 'cards' / b['img']) as word:
                assert 0 < k['zoom_scale'] <= 3 and word.width <= 3 * width and word.height <= 3 * height
                assert abs(word.width / width - word.height / height) <= 1 / width + 1 / height
                expected = source.crop(box).convert('RGB').resize(word.size, Image.Resampling.LANCZOS)
                assert np.array_equal(np.asarray(expected), np.asarray(word))
        if k['control']:
            assert k['options'][k['expected_choice']] == k['known_answer'] == k['correct'] and k['pixel_verified']
        else:
            assert k['expected_choice'] is None
            assert all(k[field] == elision_policy(k['raw_forms'])[field] for field in (
                'elision_alias_only', 'alias_only', 'elision_presence_only', 'scoring_policy'))
    html = (OUT / 'cards/index.html').read_text()
    assert html.count('<section>') == len(blind)
    assert all(b['id'] in html for b in blind)
    assert not re.search(r'https?://', html)
    for path in re.findall(r'<img[^>]+src="([^"]+)"', html):
        assert (OUT / 'cards' / path).is_file()
    # Representative final-raster QA: all waves/selections and every policy class,
    # multiword groups, absent candidates and geometry extremes; truths remain pending.
    sample = []
    def add(candidates, count):
        for x in candidates[:count]:
            if x['id'] not in {s['id'] for s in sample}: sample.append(x)
    for wave in WAVES:
        for selection in ('disagreement', 'all_agree_sample'):
            add(sorted([x for x in data if x['wave'] == wave and x['selection'] == selection], key=lambda x: x['id']), 4)
    for policy in ('alias_only', 'elision_presence_only'):
        add([x for x in data if x['scoring_policy'] == policy], 5)
    add([x for x in data if len(x['anchor_words']) > 1], 5)
    add([x for x in data if '' in x['forms'].values()], 5)
    add(sorted(data, key=lambda x: x['crop_box'][2] - x['crop_box'][0]), 3)
    add(sorted(data, key=lambda x: x['crop_box'][2] - x['crop_box'][0], reverse=True), 3)
    sheets = []
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
    for page in range(math.ceil(len(sample) / 12)):
        canvas = Image.new('RGB', (1800, 1440), '#eee'); draw = ImageDraw.Draw(canvas)
        for j, x in enumerate(sample[page * 12:page * 12 + 12]):
            col, row = j % 2, j // 2; left, top = col * 900, row * 240
            draw.text((left + 4, top + 2),f'{x["id"]} {x["wave"]} {x["scoring_policy"]}',font=font,fill='black')
            with Image.open(OUT / 'cards' / x['img']) as word:
                scale = min(1., 885 / word.width, 160 / word.height)
                canvas.paste(word.resize((round(word.width * scale), round(word.height * scale))), (left + 4, top + 26))
            with Image.open(OUT / 'cards' / x['line_img']) as full:
                scale = min(1., 885 / full.width, 46 / full.height)
                canvas.paste(full.resize((round(full.width * scale), round(full.height * scale))), (left + 4, top + 188))
        name = f'dev_final_raster_QA_{page:02d}.png'; canvas.save(E / name); sheets.append(name)
    dump(E / 'dev_visual_QA_selection.json', dict(ids=[x['id'] for x in sample], sheets=sheets))
    result = dict(status='PASS', DEV_lines=600, letters=next(x['letters'] for x in aggregate if x['wave']=='ALL'),
        baseline_metrics_and_aggregates_match=True, saved_reader_identities_and_hashes_match=True,
        data_cards=len(data), controls=len(controls), control_fraction=len(controls)/len(key),
        complete_seeded_selection=True, exact_inclusion_probabilities=True, source_candidates_complete=True,
        elision_policy_counts=summary['by_elision_policy'], numeral_and_non_elision_counterexamples_pass=True,
        all_original_line_and_word_pixels_match=True, native_lines_checked=len(checked_lines),
        uniform_zoom_at_most_3=True, blind_sources_and_controls_hidden=True, blank_answers=True,
        controls_disjoint_from_selected_data_words=True, controls_review_hashes_match=True,
        frozen_source_files=len(bound['sources']), reader_runs=0, network=False, masked_pending=True,
        visual_QA_sheets=sheets, visual_QA_items=len(sample), adjudication='PENDING')
    dump(E / 'dev_validation.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
