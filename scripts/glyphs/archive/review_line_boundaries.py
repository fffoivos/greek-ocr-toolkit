"""Rebuild Q1 structure from frozen records and audit every boundary/crossing."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from greekocr.glyphs.line_structure import ADDRESS, build_structure, join_pieces, _crosses, _x, render_structure
from greekocr.glyphs.boundary_evidence import BoundaryEvidence
from greekocr.glyphs.page_text_lines import CURVES
from scripts.glyphs.archive.review_line_structure import address_errors, read, write, sha


def crossing_panels(page, lines, structure, key, destination):
    """Original crop beside frozen geometry; never draw discounted candidates."""
    crossings = [c for c in structure['crossing_evidence'] if c['discounted'] is None]
    destination.mkdir(parents=True,exist_ok=True)
    paths = []
    for start in range(0,len(crossings),12):
        subset = crossings[start:start+12]
        sheet = Image.new('RGB',(960,250*len(subset)),'white')
        draw = ImageDraw.Draw(sheet)
        for j,c in enumerate(subset):
            l = lines[c['line_index']]
            xh = l['xheight']
            y = max(c['boundary_path'][0][1],min(c['boundary_path'][-1][1],
                    .5*(min(l['top'])+max(l['bottom']))))
            centre = float(_x(dict(path=c['boundary_path']),y))
            a = max(0,int(max(l['x0']-xh,centre-5*xh)))
            b = min(page.width,int(min(l['x1']+xh,centre+5*xh)))
            t = max(0,int(min(l['top'])-xh))
            bot = min(page.height,int(max(l['bottom'])+xh))
            raw = page.crop((a,t,b,bot)).convert('RGB')
            overlay = raw.copy()
            d = ImageDraw.Draw(overlay)
            xs = range(max(a,l['x0']),min(b,l['x1']))
            top = [(x-a,l['top'][x-l['x0']]-t) for x in xs]
            bottom = [(x-a,l['bottom'][x-l['x0']]-t) for x in xs]
            if top:d.line(top+bottom[::-1]+top[:1],fill=(220,30,20),width=1)
            d.line([(x-a,y-t) for x,y in c['boundary_path']],fill=(0,100,220),width=1)
            draw.text((8,j*250+4),f"line {c['line_index']} / {c['boundary_id']} ({c['proposal_id']}) / {c['classification']}",fill='black')
            for col,im in enumerate((raw,overlay)):
                factor = min(464/im.width,220/im.height,3.)
                im = im.resize((max(1,round(im.width*factor)),max(1,round(im.height*factor))))
                sheet.paste(im,(8+480*col,j*250+25))
        path = destination/f'{key}-{start//12+1:02d}.jpg'
        sheet.save(path,quality=90)
        paths.append(str(path.relative_to(ROOT/'docs/records/reviews')))
    return paths


def unchanged(old, new):
    """Compare every preexisting non-address field, including exact curve samples."""
    changes = []
    if len(old) != len(new):
        changes.append(dict(field='record_count', before=len(old), after=len(new)))
    for i,(a,b) in enumerate(zip(old,new)):
        for k,v in a.items():
            if k in ADDRESS:
                continue
            if k == 'neighbours':
                for direction,value in v.items():
                    if direction not in ('left','right') and value != b[k].get(direction):
                        changes.append(dict(index=i, field=f'{k}.{direction}'))
            elif v != b.get(k):
                changes.append(dict(index=i, field=k))
    return changes


def review_page(path, baseline, out):
    key = path.stem
    original = read(baseline/f'{key}.lines.json')
    original_cells = read(baseline/f'{key}.cells.json')
    previous = read(baseline/f'{key}.structure.json')
    lines, cells_file = deepcopy(original), deepcopy(original_cells)
    cells = cells_file['cells']
    page = Image.open(path).convert('L')
    s = build_structure(lines,cells,page.size,boundaries=previous['boundaries'],
                        fold=None if previous['fold'] else False,page=page)
    # Existing fold proposals are included exactly once; build_structure must
    # also use them to address physical leaves.
    s['provenance'] = dict(source_sha256=sha(path),
        baseline_lines_sha256=sha(baseline/f'{key}.lines.json'),
        baseline_cells_sha256=sha(baseline/f'{key}.cells.json'),
        baseline_structure_sha256=sha(baseline/f'{key}.structure.json'))
    evidence = s['crossing_evidence']
    for crossing in evidence:
        crossing['piece_indices'] = [p['index'] for p in cells if p['line_index']==crossing['line_index']]
        crossing['row_id'] = lines[crossing['line_index']]['row_id']
        boundary = next(b for b in s['boundaries'] if b['id']==crossing['boundary_id'])
        crossing['proposal_id'] = boundary['proposal_id']
    by_proposal = {b['proposal_id']:b for b in s['boundaries']}
    rejected = {b['proposal_id']:b for b in s['rejected_boundaries']}
    previous_crossings = []
    for v in previous['violations']:
        for bid in v['boundary_ids']:
            b = by_proposal.get(bid)
            c = next((c for c in evidence if c['line_index']==v['line_index'] and c['proposal_id']==bid),None)
            previous_crossings.append(dict(line_index=v['line_index'],proposal_id=bid,
                discounted=v['discounted'],classification=c['classification'] if c else
                'false boundary' if bid in rejected else 'outside validated rule extent/path',
                boundary_evidence=(b or rejected[bid])['evidence']))
    joined, blocked = [], []
    ordinary, ordinary_exact = 0, 0
    unsafe_joined = []
    for row in s['rows']:
        if row['discounted']:
            continue
        members = [lines[i] for i in row['line_indices']]
        try:
            merged = join_pieces(members, structure=s)
        except ValueError as exc:
            crossings = [c for c in evidence if c['line_index'] in row['line_indices']]
            blocked.append(dict(row_id=row['id'],line_indices=row['line_indices'],
                table_id=row['table_id'],reason=str(exc),crossings=crossings))
            row['joinable'] = False
        else:
            row['joinable'] = True
            joined.append(merged)
            if any(_crosses(merged,b) for b in s['boundaries']):
                unsafe_joined.append(row['id'])
            if row['table_id'] is None:
                old = original[row['line_indices'][0]]
                ordinary_exact += len(members)==1 and all(merged[k]==old[k] for k in ('x0','x1',*CURVES))
        ordinary += row['table_id'] is None
    box_crossings = []
    pixel_evidence = None
    for p in cells:
        a,t,b,bot = p['box_pixels']
        ribbon = dict(x0=a,x1=b,top=[t]*(b-a),bottom=[bot]*(b-a))
        for boundary in s['boundaries']:
            if not _crosses(ribbon,boundary):
                continue
            c = next((c for c in evidence if c['line_index']==p['line_index'] and c['boundary_id']==boundary['id']),None)
            if c is None:
                pixel_evidence = pixel_evidence or BoundaryEvidence(page,lines)
                pixel_evidence.validated_rules = [b for b in s['boundaries'] if b['kind']=='rule']
                c = pixel_evidence.crossing(p['line_index'],boundary)
            box_crossings.append(dict(c,piece_index=p['index']))
    rec = dict(key=key,boundaries_before=len(previous['boundaries']),boundaries_after=len(s['boundaries']),
        retained_boundaries=s['boundaries'],false_boundaries=s['rejected_boundaries'],
        crossings=evidence,box_crossings=box_crossings,previous_crossings=previous_crossings,
        blocked_rows=blocked,ordinary_rows=ordinary,ordinary_exact=ordinary_exact,
        address_errors=address_errors(lines,cells,s),
        geometry_changes=unchanged(original,lines)+unchanged(original_cells['cells'],cells),
        unsafe_joined_rows=unsafe_joined,lines=len(lines),pieces=len(cells),
        columns_before=len(previous['columns']),columns_after=len(s['columns']),
        rows_before=sum(not r['discounted'] for r in previous['rows']),
        rows_after=sum(not r['discounted'] for r in s['rows']),joined_rows=len(joined),
        newly_joinable_lines=sorted({i for r in s['rows'] if r.get('joinable') for i in r['line_indices']} -
            {i for r in previous['rows'] if r.get('joinable') for i in r['line_indices']}),
        provenance=s['provenance'])
    rec['crossing_panels'] = crossing_panels(page,lines,s,key,ROOT/'docs/records/reviews/q1b-evidence')
    write(out/f'{key}.structure.json',s)
    (out/f'{key}.lines.json').write_text(json.dumps(lines))
    write(out/f'{key}.cells.json',cells_file)
    # Compact JSON keeps exact samples while avoiding indentation of every
    # pixel in the joined records and their embedded source pieces.
    (out/f'{key}.rows.json').write_text(json.dumps(dict(schema_version=1,rows=joined,
        blocked_rows=blocked,complete=not blocked,
        geometry_policy='Exact original piece samples; interpolate only missing gap samples.')))
    render_structure(page,lines,s).save(out/f'{key}.structure.jpg',quality=92)
    assert read(out/f'{key}.lines.json') == lines
    assert read(out/f'{key}.cells.json') == cells_file
    assert read(out/f'{key}.structure.json') == s
    rows_readback = read(out/f'{key}.rows.json')
    assert rows_readback['rows'] == joined and rows_readback['blocked_rows'] == blocked
    with Image.open(out/f'{key}.structure.jpg') as image:
        assert image.size == page.size
        image.verify()
    return rec


def report(audit, path, tests_path):
    tests = None
    if tests_path.exists():
        root = ET.parse(tests_path).getroot()
        suites = [root] if root.tag=='testsuite' else list(root)
        tests = {k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
        tests['passed'] = tests['tests']-tests['failures']-tests['errors']-tests['skipped']
    unresolved = [dict(page=r['key'],**c) for r in audit for c in r['crossings']+r['box_crossings']
                  if c['classification']!='real crossing']
    gates = dict(no_false_boundaries=all(all(b['evidence']['accepted'] for b in r['retained_boundaries']) for r in audit),
        all_crossings_real=not unresolved,
        no_joined_boundary_crossings=all(not r['unsafe_joined_rows'] for r in audit),
        complete_addresses=all(not r['address_errors'] for r in audit),
        geometry_unchanged=all(not r['geometry_changes'] for r in audit),
        ordinary_exact_except_real_crossings=all(r['ordinary_exact']+sum(b['table_id'] is None and
            bool(b['crossings']) and all(c['classification']=='real crossing' for c in b['crossings'])
            for b in r['blocked_rows'])==r['ordinary_rows'] for r in audit),
        executed_tests_pass=bool(tests and tests['failures']==tests['errors']==0))
    write(path.with_suffix('.json'),dict(gates=gates,tests=tests,pages=audit,unresolved=unresolved))
    prefix = path.read_text().split('## Results')[0]
    md = [prefix+'## Results','',
        'The initial rules were recorded before evaluation; measurement corrections and their synthetic '
        'regressions are disclosed above. Every retained/rejected proposal, '
        'its local measurements, all original Q1 crossings and all remaining line/box crossings are in '
        '[the machine-readable audit](PAGE_LINES_Q1B_BOUNDARIES.json). Original Q1 files are frozen in '
        '`.astra/q1b-baseline/`; rebuilt sidecars and overlays are in `.astra/out/`.','',
        '| Gate | Result |','|---|---|']
    md += [f'| {k} | {"PASS" if v else "FAIL"} |' for k,v in gates.items()]
    md += ['',f"Boundaries: {sum(r['boundaries_before'] for r in audit)} → {sum(r['boundaries_after'] for r in audit)}. "
        f"Records: {sum(r['lines'] for r in audit)} lines, {sum(r['pieces'] for r in audit)} delivered pieces. "
        f"Ordinary whole lines safely rejoined exactly: {sum(r['ordinary_exact'] for r in audit)}/{sum(r['ordinary_rows'] for r in audit)}.",
        '', 'Remaining line/boundary pairs: '+', '.join(f'{n} {state} ({kind})' for (state,kind),n in sorted(
            Counter((c['classification'],'active' if c['discounted'] is None else 'diagnostic')
                    for r in audit for c in r['crossings']).items()))+'.',
        '', 'Rule paths are refitted and trimmed against original ink. This can expose additional envelope '
        'intersections without moving any line or piece. Removed proposal IDs are Q1 IDs; retained boundary '
        'IDs belong to the rebuilt structure. The retained-boundary gate checks the declared pixel tests; '
        'fold inference retains Q1 provenance and is not scan-metadata certification.',
        '', 'Original Q1 active crossing ledger (all 119 pairs): '+
        ', '.join(f'{n} {k}' for k,n in sorted(Counter(c['classification'] for r in audit for c in r['previous_crossings']
            if c['discounted'] is None).items()))+'.',
        '', '## Every page','',
        'Crossings count line/boundary pairs; active and discounted records are separate. '
        'A removed proposal is unsubstantiated by the fixed rule, not a claim that its entire neighbourhood is blank.', '',
        '| Page | Boundaries before → after | Rejected | Real active / diagnostic | Unresolved line / box | Columns before → after | Rows before → after | Blocked rows |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in audit:
        real = [c for c in r['crossings'] if c['classification']=='real crossing']
        md.append(f"| {r['key']} | {r['boundaries_before']} → {r['boundaries_after']} | {len(r['false_boundaries'])} | "
            f"{sum(c['discounted'] is None for c in real)} / {sum(c['discounted'] is not None for c in real)} | "
            f"{sum(c['classification']!='real crossing' for c in r['crossings'])} / "
            f"{sum(c['classification']!='real crossing' for c in r['box_crossings'])} | "
            f"{r['columns_before']} → {r['columns_after']} | {r['rows_before']} → {r['rows_after']} | {len(r['blocked_rows'])} |")
    md += ['', '## Heading and four table pages','']
    cases = ['an-1f8e7d022643-p000003','an-7a2b17a3fb0f-p000200','s2-200e977f2dab5291c42c-p00035',
             's2-6419488b7f8e69fd20da-p00001','s2-831443dc5e6f1ccfbaf5-p00020']
    for key in cases:
        r = next(r for r in audit if r['key']==key)
        counts = Counter(c['classification'] for c in r['previous_crossings'] if c['discounted'] is None)
        md += [f"- **{key}:** {r['boundaries_before']} → {r['boundaries_after']} boundaries. "
               'Original active flags: '+', '.join(f'{n} {k}' for k,n in sorted(counts.items()))+'.']
        if key == cases[0]:
            b = next(b for b in r['false_boundaries'] if b['proposal_id']=='boundary-0003')
            e = b['evidence']
            md += [f"  The Α Κ Ο Λ Ο Υ Θ Ι Α heading is still x=101–1426. Q1 boundary-0003 "
                f"was {e['width_px']:.1f}px / {e['local_xheight_max_px']:.2f}px = {e['width_xh']:.3f} local x-heights; "
                f"required width {e['required_width_px']:.2f}px. Rejected: {', '.join(b['rejection_reasons'])}."]
            md += ['  [Heading comparison](q1b-evidence/heading.jpg). The frozen fitted x-height above is '
                '51.58px; the nine substantial capital components measure 82, 81, 80, 78, 78, 85, 81, 86, '
                '85px (median 81px, agreeing with the owner’s example). Thus 78px is 0.963 observed '
                'capital-heights. No fitted geometry was changed. The gutter also lacks a left-hand block '
                'and has only two nearby baselines.']
    md += ['', '## Original pixels beside crossing geometry','',
        'Each panel shows the original crop on the left and its frozen ribbon (red) and validated boundary '
        '(blue) on the right. All active line/boundary pairs are included; discounted candidates are not drawn.','']
    for r in audit:
        if r.get('crossing_panels'):
            md.append(f"- {r['key']}: "+', '.join(f'[panel {i+1}]({p})' for i,p in enumerate(r['crossing_panels']))+'.')
    md += ['', '## Real crossings for the next detector round','',
        'L/R are original letter-band ink pixels within three own x-heights of the stop; '
        'shared rows must cover at least 0.2 x-height. Rule ink within 0.35 x-height is excluded. '
        'Discounted records remain diagnostic and are never rendered/delivered. IDs refer to rebuilt structure; '
        'the Q1 proposal ID is also preserved. Geometry was left unchanged.','',
        '| Page | Line | Pieces | Boundary (Q1 proposal) | Status | L/R ink | Shared rows | x-height |',
        '|---|---:|---|---|---|---:|---:|---:|']
    for r in audit:
        for c in r['crossings']:
            if c['classification']!='real crossing': continue
            md.append(f"| {r['key']} | {c['line_index']} | {', '.join(map(str,c['piece_indices'])) or '—'} | "
                f"{c['boundary_id']} ({c['proposal_id']}) | {c['discounted'] or 'active'} | "
                f"{c['own_ink_pixels_sides'][0]}/{c['own_ink_pixels_sides'][1]} | {c['common_ink_rows']} | {c['xheight_px']:.2f} |")
    md += ['', '## Rejected proposals and refused rows','']
    for r in audit:
        if r['false_boundaries'] or r['blocked_rows']:
            md += [f"### {r['key']}",'']
            reasons = {}
            for b in r['false_boundaries']:
                reasons.setdefault(', '.join(b['rejection_reasons']),[]).append(b['proposal_id'])
            md += [f"- Removed ({reason}): {', '.join(ids)}." for reason,ids in reasons.items()]
            md += [f"- Refused {b['row_id']}, lines {', '.join(map(str,b['line_indices']))}: "
                +', '.join(f"{c['boundary_id']} ({c['classification']})" for c in b['crossings'])+'.' for b in r['blocked_rows']]
    md += ['', '## Unresolved envelope overlaps','',
        'These are not proven real crossings. A valid stop is not removed merely to make the crossing count zero. '
        'The join guard remains conservative. Any entry below fails the all-crossings-real gate.','']
    for c in unresolved:
        md.append(f"- {c['page']}, line {c['line_index']}, boundary {c['boundary_id']}"+
            (f", piece {c['piece_index']}" if 'piece_index' in c else '')+
            f": L/R ink {c['own_ink_pixels_sides']}, shared rows {c['common_ink_rows']}, x-height {c['xheight_px']:.2f}.")
    if not unresolved: md.append('None.')
    md += ['', '## Validation','',
        (f"**{tests['passed']} passed, {tests['skipped']} skipped, {tests['failures']} failures, "
         f"{tests['errors']} errors** ({tests['tests']} collected). The 16 skipped tests require unavailable "
         'Chromium; they were not executed. The existing Docling deprecation warning remains.' if tests else 'Test receipt pending.'), '',
        'The audit reads back all 54 line/cell/structure/row outputs, compares all original non-address '
        'fields, checks reciprocal addresses and tests every emitted joined ribbon against every retained stop. '
        'No OCR or line detection is rerun. Pixel segmentation proposals remain detector inputs; validated '
        'boundaries are structure outputs, so line geometry and delivered pieces stay frozen.','',
        '```sh',
        'PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$PY" -m pytest -p no:cacheprovider --junitxml=.astra/q1b-tests.xml -q',
        'PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/archive/review_line_boundaries.py',
        '```','']
    path.write_text('\n'.join(md))
    print('GATES',gates,flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,default=ROOT/'.astra/q1b-baseline')
    parser.add_argument('--pages',type=Path,default=ROOT/'.astra/pages')
    parser.add_argument('--out',type=Path,default=ROOT/'.astra/out')
    parser.add_argument('--report',type=Path,default=ROOT/'docs/records/reviews/PAGE_LINES_Q1B_BOUNDARIES.md')
    parser.add_argument('--report-only',action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    if args.report_only:
        audit = read(args.report.with_suffix('.json'))['pages']
    else:
        audit = []
        for path in sorted(args.pages.glob('*.png')):
            r = review_page(path,args.baseline,args.out)
            audit.append(r)
            print(r['key'], f"boundaries {r['boundaries_before']} -> {r['boundaries_after']}",
                Counter(c['classification'] for c in r['crossings']),flush=True)
    report(audit,args.report,ROOT/'.astra/q1b-tests.xml')


if __name__ == '__main__':
    main()
