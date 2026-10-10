"""Audit saved R4 evidence, make per-page comparisons, and link owner artifacts.

This does not rerun or retime the detector. Numerical agreement is never an
accuracy label; the visual review record states the scope of actual inspection.
"""
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from ..round2 import manifest, get_baseline
from ..shared.geometry import roi
from ..shared.manifest import ROOT
from ..shared.review import atlas, save_image
from ..shared.timing import dump
from .reference import DEST, line


OUT = DEST / 'round4'


def read(path):
    return json.loads(path.read_text())


def triplet(values):
    return dict(zip(('median', 'p95', 'max'), np.quantile(values, [.5, .95, 1]).tolist()))


def compare_leaf(data):
    """Nearest lateral hypothesis, with explicit unmatched paths; no truth score."""
    slow, fast = data['slow'], data['fast']
    h = slow['height']
    result = []
    for i, seam in enumerate(slow['seams']):
        p = np.asarray(seam['path'])
        options = [(abs(np.median(p[:, 0]) - np.median(np.asarray(q['path'])[:, 0])), j)
                   for j, q in enumerate(fast['seams'])]
        distance, j = min(options, default=(float('inf'), None))
        record = dict(seam=i, native_outer_contact=seam['outer_contact'],
                      route1=None, route2=None)
        if distance < 2 * h:
            q = fast['seams'][j]
            f = np.asarray(q['path'])
            valid = (p[:, 1] >= f[:, 1].min()) & (p[:, 1] <= f[:, 1].max())
            delta = abs(p[valid, 0] - np.interp(p[valid, 1], f[:, 1], f[:, 0])) / h
            record['route1'] = dict(seam=j, outer_contact=q['outer_contact'],
                                    error_p90_h=float(np.quantile(delta, .9)) if len(delta) else None)
        candidates = [(abs(z['x'] - np.median(p[:, 0])), z) for z in slow['heuristic']]
        distance, z = min(candidates, default=(float('inf'), None), key=lambda q: q[0])
        if distance < 2 * h:
            record['route2'] = dict(x=z['x'], error_p90_h=float(np.quantile(abs(p[:, 0] - z['x']) / h, .9)))
        result.append(record)
    return result


def audit():
    rows = manifest()['pages']
    counts = Counter()

    def check(ok, label):
        if not ok:
            raise AssertionError(label)
        counts['checks'] += 1

    repeats = []
    for repeat in (1, 2):
        meta = read(OUT / f'runtime/repeat-{repeat}.meta.json')
        for path, digest in meta['source'].items():
            check(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path)
            counts['runtime_source_hashes'] += 1
        records = [json.loads(s) for s in (OUT / f'runtime/repeat-{repeat}.jsonl').read_text().splitlines()]
        check({r['page'] for r in records} == {r['page'] for r in rows}, 'runtime corpus')
        check(len(records) == 195, 'runtime record count')
        for r in records:
            check(all(r[k] for k in ('baseline_equal', 'prior_equal', 'study_equal')), r['page'])
            counts['fresh_exact_replays'] += 1
        repeats.append(records)

    per_page = []
    for row in rows:
        p = row['page']
        original = get_baseline(row)
        prior = read(DEST / 'corrections-v6' / (p + '.json'))['items']
        final = read(OUT / 'runtime/detector' / (p + '.json'))
        study = read(OUT / 'fragments-v5' / (p + '.json'))
        evidence = read(OUT / 'fragments-v5' / (p + '.evidence.json'))
        v3 = read(OUT / 'fragments-v3' / (p + '.evidence.json'))
        check(final['items'] == study['items'], p + ' timed/study items')
        check(final['page'] == p and final['image_size'] == row['image_size'] and final['unit'] == 'line', p + ' schema')
        check(np.isfinite(final['seconds']) and final['seconds'] > 0, p + ' measured time')
        w, h = row['image_size']
        for item in final['items']:
            poly = np.asarray(item['polygon'])
            check(poly.ndim == 2 and poly.shape[0] >= 3 and poly.shape[1] == 2 and np.isfinite(poly).all(), p + ' finite polygon')
            check((poly >= 0).all() and (poly <= [w, h]).all(), p + ' clipped polygon')
            check('baseline' in item and np.isfinite(item['score']) and not item.get('discounted'), p + ' item schema')
            counts['export_items'] += 1
        if row['parked']:
            check(final['items'] == prior and not evidence['joins'], p + ' parked exact')
        else:
            check(Counter(i for q in final['items'] for i in q['source_ids']) ==
                  Counter(i for q in prior for i in q['source_ids']), p + ' source multiplicity')
        participants = {i for j in evidence['joins'] for i in j['source_ids']}
        untouched = [q for q in prior if not participants.intersection(q.get('source_ids', []))]
        check(untouched == [q for q in final['items'] if not participants.intersection(q.get('source_ids', []))], p + ' untouched items')
        check(len(prior) - len(final['items']) == sum(len(j['source_ids']) - 1 for j in evidence['joins']), p + ' join count')
        if row['group'] == 'agreement':
            check(final['items'] == prior, p + ' agreement fragment invariance')
            counts['agreement_unchanged_by_fragments'] += 1
        for join in evidence['joins']:
            check(any(join['source_ids'] == old['source_ids'] and join['polygon'] == old['polygon'] for old in v3['joins']), p + ' reviewed subset')
            old = [q for q in prior if participants.intersection(q['source_ids']) and set(q['source_ids']) <= set(join['source_ids'])]
            check(len(old) == len(join['source_ids']) and all(len(q['source_ids']) == 1 for q in old), p + ' no separator reversal')
            points = np.concatenate([np.asarray(q['polygon']) for q in old] +
                                    [np.asarray(original[i]['polygon']) for i in join['source_ids']] +
                                    [np.asarray(join['polygon'])])
            x0, y0, x1, y1 = roi([*points.min(0)-2, *points.max(0)+2], (h, w))
            a = np.zeros((y1-y0, x1-x0), np.uint8)
            b = np.zeros_like(a)
            for q in old:
                cv2.fillPoly(a, [np.rint(np.asarray(q['polygon'])-[x0, y0]).astype(np.int32)], 1)
            cv2.fillPoly(b, [np.rint(np.asarray(join['polygon'])-[x0, y0]).astype(np.int32)], 1)
            check(not np.any((a > 0) & (b == 0)), p + ' every old polygon pixel retained')
            a.fill(0)
            for i in join['source_ids']:
                cv2.fillPoly(a, [np.rint(np.asarray(original[i]['polygon'])-[x0, y0]).astype(np.int32)], 1)
            check(not np.any((a > 0) & (b == 0)), p + ' original Paddle pixels retained')
            counts['joins_checked'] += 1
        contact = read(OUT / 'contact-audit' / (p + '.json'))
        check(contact['components_equal'], p + ' native components')
        for q in contact['lines']:
            check(q['observed_equal'] and q['alternatives_equal'] and q['r1_max_h'] <= .0625 + 1e-9, p + ' native routes')
            counts['contact_lines_checked'] += 1
        leaf = compare_leaf(read(OUT / 'leaves-v4' / (p + '.json')))
        skew = read(OUT / 'skew-v2' / (p + '.json'))['lines']
        page_record = dict(page=p, group=row['group'], joins=evidence['joins'],
                           contacts=contact, leaf_routes=leaf, skew=skew)
        dump(OUT / 'page-ledger' / (p + '.json'), page_record)
        per_page.append(page_record)
        for relative in [f'body-slow-v7/{p}.jpg', f'body-slow-v7/{p}.route2.jpg',
                         f'body-explicit_fast-v7/{p}.jpg', f'contact-audit/{p}.jpg',
                         f'skew-v2/{p}.jpg', f'leaves-v4/{p}.slow.jpg',
                         f'leaves-v4/{p}.route1.jpg', f'leaves-v4/{p}.route2.jpg', f'fragments-v5/{p}.jpg']:
            im = cv2.imread(str(OUT / relative))
            check(im is not None and im.size > 0, relative)
            counts['images_decoded'] += 1

    times = []
    for repeat, records in enumerate(repeats, 1):
        for group in ['agreement', 'discrepancy', 'discrepancy_extra', 'development', 'new101', 'all']:
            part = [r for r in records if group == 'all' or r['group'] == group or (group == 'new101' and r['group'].startswith('discrepancy'))]
            times.append(dict(repeat=repeat, group=group, pages=len(part), **{
                key: triplet([r[key]*1000 for r in part]) for key in ['fragment_s', 'scout_s', 'geometry_s', 'separator_s', 'added_s', 'total_s']},
                worst_fragment=max(part, key=lambda r: r['fragment_s'])['page']))
    leaves = [q for r in per_page for q in r['leaf_routes']]
    summary = dict(pages=195, counts=dict(counts), timing_ms=times,
                   changed_pages=[dict(page=r['page'], source_ids=[q['source_ids'] for q in r['joins']]) for r in per_page if r['joins']],
                   leaf=dict(native_hypotheses=len(leaves), native_outer_contacts=sum(q['native_outer_contact'] for q in leaves),
                             unmatched_route1=sum(q['route1'] is None for q in leaves), unmatched_route2=sum(q['route2'] is None for q in leaves),
                             matched_route1_outer_disagreements=sum(q['route1'] is not None and q['route1']['outer_contact'] != q['native_outer_contact'] for q in leaves)),
                   skew=dict(lines=sum(len(r['skew']) for r in per_page), provisional_straight=sum(q['native']['provisional_straight'] for r in per_page for q in r['skew'])),
                   warning='Counts describe observations and invariants, not segmentation accuracy or physical leaf truth.')
    dump(OUT / 'summary.json', summary)
    dump(OUT / 'validation.json', dict(passed=True, **dict(counts)))
    return rows, per_page


def gallery(rows, records):
    links = []

    def anchor(relative, label):
        path = OUT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        links.append(relative)
        return f'<a href="{html.escape(relative)}">{html.escape(label)}</a>'

    body = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Geometry round 4 evidence</title><style>body{font:16px system-ui;max-width:1500px;margin:2em auto;padding:0 1em;background:#faf9f5;color:#202621}a{color:#145a7a}table{border-collapse:collapse;width:100%}td,th{text-align:left;border-bottom:1px solid #ccc;padding:.6em;vertical-align:top}td:first-child{overflow-wrap:anywhere}details{margin:1em 0}ul{line-height:1.8}.scroll{overflow-x:auto}</style>',
            '<h1>Geometry round 4: curled fragments, skew, physical leaves</h1>',
            '<p>195 supplied pages. Fifteen fragment groups joined on seven pages. All original polygon pixels retained; Q8 and prior geometry preserved. Physical leaves and generic pure-skew correction remain unresolved. No held-out pages used.</p>',
            '<p>Body contacts: cyan component boxes, green observed ink paths, grey original detector. Fast native comparison: green slow / purple fast. Tangent route: purple hypotheses, never sufficient for joining. Skew: green provisional affine fit, amber uncertain, purple map slope, cyan box slope at the same centre. Leaf: amber seam, green isolated outer contact (not proof of leaves), red neighboring ink, purple reduced path, cyan recurring dark column. Corrections: green new, grey old geometry, red removed separator stripe.</p>',
            '<p>' + ' · '.join(anchor(p, label) for p, label in [('README.md', 'Methods and limitations'), ('summary.json', 'Raw summary'), ('validation.json', 'Validation'), ('runtime/repeat-1.jsonl', 'Fresh timing 1'), ('runtime/repeat-2.jsonl', 'Fresh timing 2'), ('review/notes.md', 'Visual review notes')]) + '</p>',
            '<details><summary>Iteration history and review sheets</summary><ul>']
    for directory in sorted(OUT.iterdir()):
        if directory.is_dir() and directory.name not in ('page-ledger', 'runtime'):
            files = sorted(directory.glob('*.jpg'))
            if files:
                body.append('<li>' + html.escape(directory.name) + ': ' + ' · '.join(anchor(str(p.relative_to(OUT)), p.name) for p in files if 'detail' not in p.name) + '</li>')
    body.extend(['</ul></details><div class="scroll"><table><thead><tr><th>Page / group</th><th>Curl</th><th>Skew</th><th>Leaf separation</th><th>Correction / evidence</th></tr></thead><tbody>'])
    for row, record in zip(rows, records):
        p = row['page']
        cells = [html.escape(p) + '<br>' + row['group']]
        cells.append(' · '.join(anchor(f'{d}/{p}{ext}', name) for d, ext, name in [('body-slow-v7','.jpg','Slow ink'), ('body-explicit_fast-v7','.jpg','R1 native'), ('contact-audit','.jpg','R1 against slow'), ('body-slow-v7','.route2.jpg','R2 tangent')]))
        details = sorted((OUT / 'body-slow-v7').glob(p + '.detail-*.jpg'))
        if details:
            cells[-1] += '<details><summary>Raw / contacts by source</summary>' + ' · '.join(anchor(str(q.relative_to(OUT)), str(i+1)) for i, q in enumerate(details)) + '</details>'
        cells.append(anchor(f'skew-v2/{p}.jpg', 'Native / R1 / R2'))
        if (OUT / f'skew-v2/{p}.detail.jpg').exists():
            cells[-1] += ' · ' + anchor(f'skew-v2/{p}.detail.jpg', 'Raw fit crops')
        cells.append(' · '.join(anchor(f'leaves-v4/{p}.{route}.jpg', label) for route, label in [('slow','Slow'),('route1','R1'),('route2','R2')]))
        cells.append(' · '.join(anchor(f'{d}/{p}.{ext}', label) for d, ext, label in [('fragments-v5','jpg',f"{len(record['joins'])} joins"),('runtime/detector','json','Timed detector JSON'),('page-ledger','json','Per-line ledger')]))
        details = sorted((OUT / 'fragments-v5').glob(p + '.detail-*.jpg'))
        if details:
            cells[-1] += '<br>' + ' · '.join(anchor(str(q.relative_to(OUT)), f'Raw join crop {i+1}') for i, q in enumerate(details))
        body.append('<tr>' + ''.join('<td>'+x+'</td>' for x in cells) + '</tr>')
    body.append('</tbody></table></div></html>')
    (OUT / 'index.html').write_text('\n'.join(body))
    dump(OUT / 'gallery-links.json', dict(links=len(links), unique=len(set(links)), all_exist=True))


def additional_review(rows, records):
    out = OUT / 'review'
    for kind, relative in [('leaves', 'leaves-v4/{}.route1.jpg'), ('skew', 'skew-v2/{}.jpg')]:
        chosen = rows if kind == 'skew' else [r for r, rec in zip(rows, records) if rec['leaf_routes']]
        for start in range(0, len(chosen), 12):
            atlas([(r['page'], cv2.imread(str(OUT / relative.format(r['page'])))) for r in chosen[start:start+12]],
                  out / f'{kind}-{start//12:02d}.jpg', columns=3, cell_width=450)
    ranked = sorted([(q['r1_end_error_h'], r['page'], q) for r in records for q in r['skew']
                     if q['native']['provisional_straight'] and q['r1_end_error_h'] is not None], key=lambda x:x[0], reverse=True)[:8]
    tiles = []
    bypage = {r['page']:r for r in rows}
    for error, page, fit in ranked:
        q = next(q for q in read(OUT / f'body-slow-v7/{page}.json')['lines'] if q['line'] == fit['line'])
        gray = cv2.imread(str(ROOT / bypage[page]['path']), 0)
        h = q['height']; box = np.asarray(q['bbox']); x0,y0,x1,y1 = roi(box+[-h,-h,h,h], gray.shape)
        raw = cv2.cvtColor(gray[y0:y1,x0:x1], cv2.COLOR_GRAY2BGR); draw = raw.copy()
        line(draw, np.asarray(q['path'])-[x0,y0], (150,150,150), 1)
        line(draw, np.asarray(fit['native']['path'])-[x0,y0], (30,170,20), 2)
        centre = np.mean(fit['native']['path'],axis=0);xs = np.asarray(fit['native']['span'])
        line(draw, np.c_[xs,centre[1]+fit['route1']['slope']*(xs-centre[0])]-[x0,y0],(190,30,180),1)
        tile=np.vstack([raw,draw]);scale=min(1,1400/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale)
        panel=np.full((tile.shape[0]+28,1400,3),255,np.uint8);panel[28:,:tile.shape[1]]=tile
        cv2.putText(panel,f'{page} source{fit["line"]} slope difference {error:.3f}h',(5,19),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1);tiles.append(panel)
    for start in range(0,len(tiles),4):save_image(out/f'skew-disagreement-{start//4:02d}.jpg',np.vstack(tiles[start:start+4]))


if __name__ == '__main__':
    cv2.setNumThreads(1)
    source = Path(__file__).parent
    (OUT / 'README.md').write_text((source / 'ROUND4_README.md').read_text())
    (OUT / 'review/notes.md').write_text((source / 'ROUND4_REVIEW.md').read_text())
    rows, records = audit()
    additional_review(rows, records)
    gallery(rows, records)
    print((OUT / 'validation.json').read_text())
