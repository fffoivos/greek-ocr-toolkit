"""ADM3 offline append; standard-library reads only, writes confined to HERE."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import append_adm2_poly1850 as prior

HERE, ROOT, W, RUN = prior.HERE, prior.ROOT, prior.W, prior.RUN
ADMISSIONS, SUMMARY = prior.ADMISSIONS, prior.SUMMARY
ARM, WAVE_ARM = prior.ARM, prior.WAVE_ARM
BASE_HEAD = '6ec7ebadd9d3d011c95720bc41cea78d63d03e22'
BASE_SHA = '5fedf0eedf97b3eb3b132d3581c4e4fc7e34dad3be71ef6cb9c2400ad3b2489f'
KOSMO_SHA = '8703ddec7b7c14370f428dd8d9f9cdf8a63c18d3bb45d483661841c30dc5dd5a'
sha, digest, require, encode = prior.sha, prior.digest, prior.require, prior.encode
CAPS = W / 'caps3'


def load(path):
    return json.loads(Path(path).read_text())


def records(path, ids=None):
    out = {}
    with Path(path).open() as stream:
        for line in stream:
            row = json.loads(line)
            if ids is not None and row['id'] not in ids:
                continue
            require(row['id'] not in out, 'duplicate id: ' + row['id'])
            out[row['id']] = row
    return out


def baseline():
    data = prior.git_bytes(BASE_HEAD, str(ADMISSIONS.relative_to(ROOT)))
    require(digest(data) == BASE_SHA, 'ADM2 baseline drift')
    lines = data.splitlines(keepends=True)
    wave = b''.join(l for l in lines if load_line(l)['arm'] == WAVE_ARM)
    kos = b''.join(l for l in lines if load_line(l)['arm'] == ARM)
    require(len(lines) == 17024 and digest(wave) == prior.BASE_SHA
            and digest(kos) == KOSMO_SHA, 'frozen subset drift')
    return data


def load_line(line):
    return json.loads(line)


def input_paths():
    paths = prior.input_paths()
    paths.update(adm2_builder=HERE / 'append_adm2_poly1850.py',
                 caps3_records=W / 'caps_masked/records.jsonl',
                 caps3_pool=CAPS / 'keys/pool.jsonl', caps3_screen=CAPS / 'screen.jsonl',
                 caps3_screen_receipt=CAPS / 'screen_receipt.json',
                 caps3_pipeline=CAPS / 'pipeline.py', caps4_results=CAPS / 'results.json')
    for path in load(CAPS / 'screen_receipt.json')['helper_sources']:
        paths['clip_helper:' + Path(path).name] = Path(path)
    return paths


def bindings():
    return {k: dict(path=str(p), sha256=sha(p)) for k, p in sorted(input_paths().items())}


def screen_provenance(inputs):
    receipt = load(CAPS / 'screen_receipt.json')
    return dict(build='sol/recut-v1 d8c31c97', helper=receipt['helper'],
                tolerance=receipt['tolerance'],
                screen_sha256=inputs['caps3_screen']['sha256'],
                receipt_sha256=inputs['caps3_screen_receipt']['sha256'])


def make_row(r, x, screen):
    require(x['output_kind'] in ('masked', 'guarded_original'), 'unsupported output kind')
    crop = W / 'caps_masked' / x['masked_crop']
    require(crop.resolve().is_relative_to((W / 'caps_masked').resolve()), 'crop outside CAPS3')
    want = x['masked_crop_sha256'] if x['output_kind'] == 'masked' else x['original_crop_sha256']
    require(sha(crop) == want, 'CAPS3 crop hash mismatch: ' + r['id'])
    require(x['original_crop_sha256'] == r['crop_sha256'], 'collector crop hash mismatch: ' + r['id'])
    require(x['source'] == r['source'] and x['page_id'] == r['page_id'], 'metadata mismatch')
    masked = x['output_kind'] == 'masked'
    return dict(row_id=r['id'], source=r['source'], primary_class=r['primary_class'],
                gazette_stratum=r.get('gazette_stratum') if r['source'] == 'gazette_modern' else None,
                page_id=r['page_id'], line_index=int(r['id'].rsplit('-l', 1)[1]),
                tranche='W1', label=r['label'], crop=str(crop), crop_sha256=want,
                original_crop_sha256=x['original_crop_sha256'],
                guard_status='masked' if masked else 'guarded_original',
                wrong_line_risk=bool(x.get('wrong_line_risk')),
                crop_masked_tag='crop_masked' if masked else None,
                arm=ARM, marks_status='pending_opus',
                provenance=dict(t6b_commit='sol/recut-v1 63c640a3',
                                t6b_checks_commit='sol/recut-v1 7f70de90',
                                params_sha256=x.get('params_sha256', prior.PARAMS_SHA),
                                caps3_build='sol/recut-v1 d8c31c97',
                                sol_reading='sol/recut-v1 abaa200c', clip_screen=screen))


def candidates():
    before = bindings()
    for rev, names in [('d8c31c97', ['caps_masked/records.jsonl', 'caps3/screen.jsonl',
                                   'caps3/screen_receipt.json', 'caps3/keys/pool.jsonl']),
                       ('abaa200c', ['caps3/results.json'])]:
        for name in names:
            require(prior.git_bytes(rev, 'docs/harvest/recut_v1/w1_masked/' + name, W.parents[3])
                    == (W / name).read_bytes(), 'evidence commit mismatch: ' + name)
    receipt = load(CAPS / 'screen_receipt.json')
    for p, expected in receipt['helper_sources'].items():
        require(sha(p) == expected, 'clip helper drift: ' + p)
    results = load(CAPS / 'results.json')
    require(results['bed']['n'] == 100 and results['bed']['letters']['y'] == 100
            and results['bed']['crop_ok']['y'] == 99
            and results['bed']['marks']['sol_counts']['y'] == 98
            and results['ruling']['marks'] == 'pending_opus', 'CAPS4 results drift')
    screen = records(CAPS / 'screen.jsonl')
    pool = records(CAPS / 'keys/pool.jsonl')
    recs = records(W / 'caps_masked/records.jsonl')
    require(set(screen) == set(pool) and len(pool) == receipt['pool'] == 2211, 'screen coverage mismatch')
    flagged = {rid for rid, x in screen.items() if x['flagged']}
    require(len(flagged) == receipt['removed'] == 544, 'screen removal mismatch')
    actual = Counter(screen[rid]['source'] for rid in flagged)
    require(all(actual[s] == n for s, n in receipt['removed_per_source'].items()), 'source removals mismatch')
    require(set(recs) == set(pool) - flagged, 'records differ from screened pool')
    excluded = set()
    for name, spec in load(prior.EXCLUSIONS / 'release_exclusions.json')['classes'].items():
        path = prior.EXCLUSIONS / spec['file']
        require(sha(path) == spec['sha256'], 'exclusion hash mismatch: ' + name)
        ids = path.read_text().split()
        require(len(set(ids)) == spec['n'], 'exclusion count mismatch: ' + name)
        excluded.update(ids)
    rotated = set((prior.EXCLUSIONS / 'w1_rotated_crop_ids.txt').read_text().split())
    w1 = records(RUN / 'W1/crop_tight_page.jsonl', pool)
    # Features supplies an independent merged-screen/metadata check.
    features = records(RUN / 'W1/features.jsonl', pool)
    counts, dropped, out = Counter(), defaultdict(list), []
    for rid, p in sorted(pool.items()):
        require(rid in features, 'missing W1 feature row: ' + rid)
        f, x = features[rid], recs.get(rid)
        r = w1.get(rid, f)
        require(r['primary_class'] == f['primary_class'] == 'headings_caps', 'not headings_caps')
        require(screen[rid]['crop_sha256'] == r['crop_sha256'], 'screen crop mismatch')
        counts['screen_pool'] += 1
        if rid in flagged: reason = 'edge_clip_screen'
        elif any(z.get('screen_merged') for z in (r, f, x or {})): reason = 'screen_merged'
        elif rid in rotated or any(z.get('rotated_crop') for z in (r, f, x or {})): reason = 'rotated_crop'
        elif rid in excluded: reason = 'release_exclusions_line_class'
        elif x is None: reason = 'missing_caps3_record'
        elif x['output_kind'] not in ('masked', 'guarded_original'): reason = 'output_kind:' + x['output_kind']
        else:
            counts['collector:crop_tight_page' if rid in w1 else 'collector:features'] += 1
            out.append(make_row(r, x, screen_provenance(before)))
            counts['admitted'] += 1
            continue
        counts[reason] += 1
        dropped[reason].append(rid)
    require(bindings() == before, 'inputs changed during validation')
    return out, dict(counts), dict(dropped), before


def expected_summary(base, rows, counts, dropped, inputs):
    summary = json.loads(prior.git_bytes(BASE_HEAD, str(SUMMARY.relative_to(ROOT))))
    all_rows = [json.loads(l) for l in base.splitlines()] + rows
    arms = Counter(r['arm'] for r in all_rows)
    receipt = load(CAPS / 'screen_receipt.json')
    summary.update(rows=len(all_rows), sha256=digest(base + encode(rows)),
        status='wave-1d and ADM2 kosmopolis bytes preserved; kosmopolis and headings_caps release-v3 candidates; marks pending Opus',
        kosmopolis_subset_sha256=KOSMO_SHA, kosmopolis_subset_rows=462,
        kosmopolis_subset_bytes_unchanged=True,
        release_exclusions_sha256=inputs['release_exclusions']['sha256'],
        bound_inputs=inputs,
        arm_filter_counts={a: arms[a] for a in ('wave-1d', WAVE_ARM, ARM)},
        candidate_filter_counts=dict(wave1d=16562, kosmopolis_poly1850=462, headings_caps=len(rows)),
        counts_per_arm_source_class=[dict(arm=a, source=s, primary_class=c, rows=n)
            for (a, s, c), n in sorted(Counter((r['arm'], r['source'], r['primary_class']) for r in all_rows).items())],
        validation=[v.replace('every admitted row', 'every historical wave-1d/ADM2 row') for v in summary['validation']] + ['ADM3 headings_caps: collector metadata from crop_tight_page when present, otherwise features; every original crop hash must match.'],
        adm3=dict(arm=ARM, primary_class='headings_caps', rows=len(rows), marks_status='pending_opus',
            build='sol/recut-v1 d8c31c97', sol_reading='sol/recut-v1 abaa200c',
            expected_rows=1629, difference_from_1629=len(rows)-1629,
            difference_reason='None; 2211 screened pool - 544 edge clips - 38 unmatched originals = 1629.' if len(rows)==1629 else '1629 masked/guarded records minus two n1_locked_eval masked rows and one W1-features screen_merged masked row = 1626. One further screen_merged row is already unmatched_original (38 unmatched total; 37 counted in the unmatched branch). See excluded_row_ids for exact IDs.',
            selection_counts=counts, excluded_row_ids=dropped,
            guard_status_counts=dict(Counter(r['guard_status'] for r in rows)),
            edge_clip_screen=dict(**screen_provenance(inputs), removed=receipt['removed'],
                removed_per_source=receipt['removed_per_source'],
                caps2_validation=dict(clipped_flagged=receipt['clipped_flagged'], clipped_n=receipt['clipped_n'],
                                      false_positives=receipt['fp'], crop_ok_n=receipt['crop_ok_n'])),
            letters=dict(y=100,n=100,status='final_sol'), crop_ok=dict(y=99,n=100,status='final_sol'),
            marks=dict(y=98,n=100,status='pending_opus')))
    return summary


def verify():
    base = baseline()
    rows, counts, dropped, inputs = candidates()
    data = ADMISSIONS.read_bytes()
    require(data == base + encode(rows), 'admissions differ from frozen prefix plus CAPS3 rows')
    parsed = [json.loads(l) for l in data.splitlines()]
    require(len({r['row_id'] for r in parsed}) == len(parsed), 'duplicate admission id')
    require(load(SUMMARY) == expected_summary(base, rows, counts, dropped, inputs), 'summary mismatch')
    return dict(wave1d_rows=16562, kosmopolis_rows=462, caps_rows=len(rows), sha256=digest(data),
                wave1d_subset_sha256=prior.BASE_SHA, kosmopolis_subset_sha256=KOSMO_SHA)


def append():
    base = baseline()
    rows, counts, dropped, inputs = candidates()
    current, expected = ADMISSIONS.read_bytes(), base + encode(rows)
    require(current in (base, expected), 'refusing unexpected admissions')
    if current == base:
        with ADMISSIONS.open('ab') as stream: stream.write(encode(rows))
    SUMMARY.write_text(json.dumps(expected_summary(base, rows, counts, dropped, inputs), ensure_ascii=False, indent=1) + '\n')
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify() if args.check_only else append(), indent=2))
