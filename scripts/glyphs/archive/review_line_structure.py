"""Address and audit frozen delivery records; never rerun the line detector.

The baseline must be captured before modification. Table component grouping is
replayed against the same pixels and matched by exact existing piece boxes.
Annotations are read only after structure construction, solely for evaluation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from greekocr.glyphs.line_structure import (
    ADDRESS, _table_structure, _crosses, build_structure, join_pieces, render_structure,
)
from greekocr.glyphs.page_text_lines import CURVES


def read(path):
    return json.loads(path.read_text())


def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _area(b):
    return max(0,b[2]-b[0])*max(0,b[3]-b[1])


def _overlap(a,b):
    return _area([max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])])


def annotation_audit(ann,cells):
    """Check within-cell printed elements, not semantic multi-line grid rows."""
    elements=[(t,c,e) for t in ann['tables'] for c in t['cells'] for e in c['text_elements']]
    owners=defaultdict(list);piece_owners=defaultdict(list)
    for t,c,e in elements:
        for p in cells:
            if _overlap(e['box'],p['box_pixels']) > .2*max(1,min(_area(e['box']),_area(p['box_pixels']))):
                owners[e['id']].append(p)
                piece_owners[p['index']].append(dict(table=t['id'],cell=c['id'],element=e['id']))
    missing=[];split=[];matched=0
    for _,c,e in elements:
        pieces=owners[e['id']]
        if not pieces:
            missing.append(e['id']);continue
        matched+=1
        rows=sorted({p['row_id'] for p in pieces})
        if len(rows)>1:
            split.append(dict(element=e['id'],cell=c['id'],row_ids=rows,
                              piece_indices=[p['index'] for p in pieces]))
    row_cells=defaultdict(set);row_elements=defaultdict(set);unique_row_cells=defaultdict(set)
    for p in cells:
        for o in piece_owners[p['index']]:
            row_cells[p['row_id']].add(o['cell'])
            row_elements[p['row_id']].add(o['element'])
        own={o['cell'] for o in piece_owners[p['index']]}
        if len(own)==1:unique_row_cells[p['row_id']].update(own)
    return dict(status=ann['status'],tables=len(ann['tables']),elements=len(elements),
        matched_elements=matched,missing_elements=missing,split_elements=split,
        rows_mixing_cells=[dict(row_id=r,cell_ids=sorted(cs)) for r,cs in row_cells.items() if len(cs)>1],
        rows_mixing_unique_cells=[dict(row_id=r,cell_ids=sorted(cs)) for r,cs in unique_row_cells.items() if len(cs)>1],
        rows_mixing_elements=[dict(row_id=r,element_ids=sorted(es)) for r,es in row_elements.items() if len(es)>1],
        ambiguous_pieces=[dict(piece_index=i,owners=o) for i,o in piece_owners.items()
                          if len({v['cell'] for v in o})>1],
        matched_pieces_without_table_id=[p['index'] for p in cells if piece_owners[p['index']] and p['table_id'] is None],
        method='Box overlap >20% of the smaller envelope; provisional annotations, no recognition or PDF text. '
               'A text_element is the available printed-line proxy; semantic grid rows may contain multiple lines.')


def address_errors(lines,cells,s):
    errors=[]
    row_map={r['id']:r for r in s['rows']};columns={c['id'] for c in s['columns']}
    blocks={b['id'] for b in s['blocks']};sides={p['page_side'] for p in s['pages']}
    for kind,records,indices in [('line',lines,'line_indices'),('piece',cells,'piece_indices')]:
        membership=Counter(i for r in s['rows'] for i in r[indices])
        orders=[]
        for i,r in enumerate(records):
            if any(k not in r or r[k] is None for k in ADDRESS):
                errors.append(f'{kind} {i}: incomplete address');continue
            if membership[i]!=1:errors.append(f'{kind} {i}: row memberships={membership[i]}')
            row=row_map.get(r['row_id'])
            if row is None or any(r[k]!=row[k] for k in ('page_side','column_id','block_id')):
                errors.append(f'{kind} {i}: inconsistent row address')
            if r['column_id'] not in columns or r['block_id'] not in blocks or r['page_side'] not in sides:
                errors.append(f'{kind} {i}: missing address target')
            if row:
                members=row[indices];pos=members.index(i)
                for side,delta in [('left',-1),('right',1)]:
                    expected=members[pos+delta] if 0<=pos+delta<len(members) else None
                    if r.get('neighbours',{}).get(side,'missing')!=expected:
                        errors.append(f'{kind} {i}: incorrect {side} neighbour')
            orders.append(r['reading_order'])
        if len(set(orders))!=len(orders):errors.append(f'{kind}: duplicate reading_order')
    for i,p in enumerate(cells):
        l=lines[p['line_index']]
        if any(p[k]!=l[k] for k in ADDRESS):errors.append(f'piece {i}: address differs from line')
    col_order={c['id']:c['reading_order'] for c in s['columns']}
    ordering=[col_order[l['column_id']] for l in sorted(lines,key=lambda l:l['reading_order'])]
    if ordering!=sorted(ordering):errors.append('reading order returns to a previous column')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages',type=Path,default=ROOT/'.astra/pages')
    parser.add_argument('--baseline',type=Path,default=ROOT/'.astra/q1-baseline')
    parser.add_argument('--out',type=Path,default=ROOT/'.astra/out')
    parser.add_argument('--annotations',type=Path,default=ROOT/'docs/tables/annotations')
    parser.add_argument('--report',type=Path,default=ROOT/'docs/reviews/PAGE_LINES_Q1_COORDINATES.md')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    audit=[]
    for path in sorted(args.pages.glob('*.png')):
        key=path.stem
        line_path=args.baseline/f'{key}.lines.json';cell_path=args.baseline/f'{key}.cells.json'
        checks=read(args.baseline/f'{key}.checks.json')
        original_lines=read(line_path);original_cells=read(cell_path)
        lines=deepcopy(original_lines);cell_file=deepcopy(original_cells);cells=cell_file['cells']
        page=Image.open(path).convert('L')
        evidence=checks['checks']['6_column_crossings']
        regions=[(r['id'],r['box_pixels']) for r in checks.get('table_delivery',{}).get('regions',[])]
        sources,boundaries=_table_structure(page,regions) if regions else ({},[])
        missing_sources=[]
        for p in cells:
            if p['table_id'] is None:continue
            source=sources.get((p['table_id'],tuple(p['box_pixels'])))
            if source is None:missing_sources.append(p['index'])
            else:lines[p['line_index']]['row_source']=source
        s=build_structure(lines,cells,page.size,gutters=evidence['all_boundaries'],
                          rules=evidence['continued_rules'],boundaries=boundaries)
        s['provenance']=dict(source_sha256=sha(path),baseline_lines_sha256=sha(line_path),
            baseline_cells_sha256=sha(cell_path),table_regions=[[tid,list(box)] for tid,box in regions],
            line_geometry_redetected=False,table_component_grouping_replayed=bool(regions),
            implementation_sha256=sha(ROOT/'greekocr/glyphs/line_structure.py'))
        geometry_changes=[];other_changes=[]
        for i,(a,b) in enumerate(zip(original_lines,lines)):
            for field in a:
                if field=='neighbours':
                    for direction in a[field]:
                        if direction not in ('left','right') and a[field][direction]!=b[field].get(direction):
                            other_changes.append(dict(line=i,field=f'neighbours.{direction}'))
                elif a[field]!=b[field]:
                    target=geometry_changes if field in (*CURVES,'x0','x1','xheight','column') else other_changes
                    target.append(dict(line=i,field=field,before=a[field],after=b[field]))
        for i,(a,b) in enumerate(zip(original_cells['cells'],cells)):
            for field in a:
                if a[field]!=b[field]:geometry_changes.append(dict(piece=i,field=field,before=a[field],after=b[field]))
        joined=[];blocked=[];ordinary=0;ordinary_equal=0;ordinary_unchanged=0
        for row in s['rows']:
            if row['discounted']:continue
            members=[lines[i] for i in row['line_indices']]
            result=None
            try:
                result=join_pieces(members,structure=s)
                joined.append(result);row['joinable']=True
            except ValueError as e:
                blocked.append(dict(row_id=row['id'],line_indices=row['line_indices'],reason=str(e)))
                row['joinable']=False
            if row['table_id'] is None:
                ordinary+=1
                if len(members)==1:
                    old=original_lines[row['line_indices'][0]]
                    ordinary_unchanged+=all(members[0][k]==old[k] for k in (*CURVES,'x0','x1'))
                    ordinary_equal+=result is not None and all(result[k]==old[k] for k in (*CURVES,'x0','x1'))
        piece_crossings=[]
        for p in cells:
            a,t,b,bot=p['box_pixels']
            ribbon=dict(x0=a,x1=b,top=[t]*(b-a),bottom=[bot]*(b-a))
            cross=[r['id'] for r in s['boundaries'] if _crosses(ribbon,r)]
            if cross:piece_crossings.append(dict(piece_index=p['index'],boundary_ids=cross))
        annpath=args.annotations/f'{key}.json'
        annotations=annotation_audit(read(annpath),cells) if annpath.exists() else None
        errors=address_errors(lines,cells,s)
        rec=dict(key=key,lines=len(lines),pieces=len(cells),active_lines=sum(l.get('discounted') is None for l in lines),
            pages=len(s['pages']),fold=s['fold'],columns=len(s['columns']),rows=len(s['rows']),
            active_rows=sum(not r['discounted'] for r in s['rows']),
            multi_piece_rows=sum(len(r['line_indices'])>1 for r in s['rows']),
            joined_rows=len(joined),blocked_rows=blocked,address_errors=errors,
            geometry_changes=geometry_changes,other_legacy_changes=other_changes,
            ordinary_rows=ordinary,ordinary_exact=ordinary_equal,ordinary_unchanged=ordinary_unchanged,
            line_crossings=[v for v in s['violations'] if v['discounted'] is None],
            diagnostic_crossings=[v for v in s['violations'] if v['discounted'] is not None],
            piece_crossings=piece_crossings,missing_table_row_sources=missing_sources,annotations=annotations)
        write(args.out/f'{key}.structure.json',s)
        (args.out/f'{key}.lines.json').write_text(json.dumps(lines))
        write(args.out/f'{key}.cells.json',cell_file)
        write(args.out/f'{key}.rows.json',dict(schema_version=1,rows=joined,blocked_rows=blocked,
            complete=not blocked,geometry_policy='Original piece samples retained; linear interpolation only in gaps.'))
        render_structure(page,lines,s).save(args.out/f'{key}.structure.jpg',quality=92)
        # Read back every output used by the address and preservation gates.
        assert read(args.out/f'{key}.lines.json')==lines
        assert read(args.out/f'{key}.cells.json')==cell_file
        assert read(args.out/f'{key}.structure.json')==s
        with Image.open(args.out/f'{key}.structure.jpg') as im:assert im.size==page.size;im.verify()
        audit.append(rec)
        print(key,'lines',len(lines),'pieces',len(cells),'rows',rec['active_rows'],
              'multi',rec['multi_piece_rows'],'line crossings',len(rec['line_crossings']),
              'piece crossings',len(piece_crossings),'address errors',len(errors),flush=True)
    gates=dict(complete_addresses=all(not r['address_errors'] for r in audit),
        no_crossing=all(not r['line_crossings'] and not r['piece_crossings'] and not r['diagnostic_crossings']
                        and not r['blocked_rows'] for r in audit),
        geometry_unchanged=all(not r['geometry_changes'] and not r['other_legacy_changes'] for r in audit),
        ordinary_exact=all(r['ordinary_rows']==r['ordinary_exact'] for r in audit))
    test_path=ROOT/'.astra/q1-tests.xml'
    tests=None
    if test_path.exists():
        suites=ET.parse(test_path).getroot().findall('testsuite')
        tests={k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
        tests['passed']=tests['tests']-tests['failures']-tests['errors']-tests['skipped']
        tests['junit_sha256']=sha(test_path)
        gates['executed_tests_pass']=tests['failures']==tests['errors']==0
    receipt=dict(gates=gates,tests=tests,pages=audit)
    write(args.out/'q1-structure-audit.json',receipt)
    write(args.report.with_suffix('.json'),receipt)
    report(args.report,audit,gates,tests)


def report(path,audit,gates,tests=None):
    totals={k:sum(r[k] for r in audit) for k in ('lines','pieces','active_rows','multi_piece_rows','ordinary_rows','ordinary_exact','ordinary_unchanged')}
    lines=['# Q1: line coordinates and grouping','',
        'Structure is added over the frozen delivery geometry. Component row provenance is retained before table '
        'splitting; physical leaf, column, block, row, piece order and reading order are explicit. '
        '`join_pieces` rejects mixed addresses and any boundary intersection. Default delivery keeps table pieces '
        'and ordinary whole lines; `granularity="rows"` explicitly requests safe joined table lines.','',
        '**The no-crossing gate fails. This is not a completed Q1 acceptance.** '
        'Existing records are preserved, including diagnostic candidates and their intersections. '
        'No geometry fixes were applied; the before/after geometry change list is empty.','',
        '## Evidence and contract','',
        '- Baseline: `.astra/q1-baseline/` (162 line, cell and check files captured before edits). '
        'Each structure records the image and baseline SHA-256 hashes.',
        '- All 54 page outputs are in `.astra/out/`: updated `.lines.json` and `.cells.json`, '
        'new `.structure.json`, `.structure.jpg`, and `.rows.json`. Unsafe rows are explicitly listed under '
        '`blocked_rows`, so the joined view cannot silently emit a crossing or claim completeness.',
        '- Full per-record failures and annotation comparisons: [PAGE_LINES_Q1_COORDINATES.json](PAGE_LINES_Q1_COORDINATES.json), '
        'also written to `.astra/out/q1-structure-audit.json`.',
        '- IDs are image-local. `lines.neighbours` uses line indices; `cells.neighbours` uses cell indices. '
        'Null means the end of the row. Discounted candidates receive addresses but are never rendered or joined.',
        '- Each column references finite observed boundary paths; slanted rules retain their slopes. '
        'Overlapping observations are linked as separator tracks without replacing their measured paths. '
        'A block is a column-local prose/table/diagnostic group, not a semantic paragraph. '
        'These are conservative local column regions; complex tables remain fragmented. '
        'Reading-order indices traverse those inferred regions column by column, but human table reading order is not certified.',
        '- Fold inference uses a wide image and a persistent central text separation. It is labelled inferred, '
        'not a scan-metadata fact. Callers can supply an explicit fold path or `fold=False`. '
        'Portrait spreads or unusual landscape single pages require that override.',
        '- The crossing audit samples the **complete curved ribbon** against finite boundary centre paths; '
        'it also checks each delivered rectangle. The older detector check sampled three body offsets. '
        'Consequently these are conservative geometry/boundary conflicts, not all proven cut letters. '
        'New table rule paths are derived from the detector rule mask; provisional whitespace may also be wrong.',
        '- The join guard splits proposed row groups before joining if their intervening gap crosses a stop. '
        'Original per-piece curve samples remain exact; only previously undefined gap samples are interpolated.',
        '- Table word-splitting gaps are not automatically column boundaries. Whitespace needs persistent '
        'overlapping support windows, spanning text interrupts its extent, and rule proposals need continuous '
        'original ink. Separate component seeds may share a printed row when their facing baselines align '
        'inside one column; every source group remains in `row_sources`.',
        '', '## Gates','', '| Gate | Result |','|---|---|']
    lines += [f'| {k} | {"PASS" if v else "FAIL"} |' for k,v in gates.items()]
    lines += ['',
        f"{totals['lines']} line records; {totals['pieces']} delivered pieces; {totals['active_rows']} active rows; "
        f"{totals['multi_piece_rows']} rows contain multiple pieces. "
        f"Ordinary frozen whole-line geometry is unchanged for {totals['ordinary_unchanged']}/{totals['ordinary_rows']} rows; "
        f"{totals['ordinary_exact']}/{totals['ordinary_rows']} can also be safely emitted by the join guard.",
        '', '## Per-page results','',
        'Cross columns count active line ribbons, delivered boxes, and discounted diagnostic ribbons respectively. '
        'Every zero in the address/geometry columns is an exact record comparison, not a visual estimate.','',
        '| Page | Lines | Pieces | Leaves | Columns | Active rows | Multi-piece | Address errors | Geometry changes | Ordinary safely joined / total | Cross line/box/diagnostic | Blocked joins |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in audit:
        lines.append(f"| {r['key']} | {r['lines']} | {r['pieces']} | {r['pages']} | {r['columns']} | "
            f"{r['active_rows']} | {r['multi_piece_rows']} | {len(r['address_errors'])} | {len(r['geometry_changes'])} | "
            f"{r['ordinary_exact']}/{r['ordinary_rows']} | "
            f"{len(r['line_crossings'])}/{len(r['piece_crossings'])}/{len(r['diagnostic_crossings'])} | {len(r['blocked_rows'])} |")
    lines += ['', '## Eight provisional table annotation checks','',
        'The available `text_elements` within annotated cells are used as printed-line proxies. '
        'Semantic table row numbers can cover several printed lines and independent panels; they are not copied '
        'into production row IDs. Missing elements and ambiguous overlaps include existing detector/annotation '
        'limitations. An annotation match is a diagnostic comparison, not certified table ownership.','',
        '| Page | Elements | Matched | Missing | Split over row IDs | Rows mixing cells (all / unique owners) | Ambiguous pieces | Matched pieces lacking table ID |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in audit:
        a=r['annotations']
        if a:
            lines.append(f"| {r['key']} | {a['elements']} | {a['matched_elements']} | {len(a['missing_elements'])} | "
                f"{len(a['split_elements'])} | {len(a['rows_mixing_cells'])}/{len(a['rows_mixing_unique_cells'])} | {len(a['ambiguous_pieces'])} | "
                f"{len(a['matched_pieces_without_table_id'])} |")
    lines += ['', '## Owner cases','',
        '| Page | Fold x (top → bottom) | Active line/box crossings | Diagnostic crossings |',
        '|---|---|---:|---:|']
    cases={'an-5c093c79d6bb-p000199','an-9ea1564fcf4f-p000013','s2-9de6cda8f03f0fc60a58-p00005',
           's2-d1ed1c2db37f431f4acb-p00001','s2-0ce9d1025b3f23c7119e-p00001','an-a73d22211479-p000301'}
    for r in audit:
        if r['key'] in cases:
            fold=r['fold'];pos=f"{fold['path'][0][0]:.3f} → {fold['path'][-1][0]:.3f}" if fold else 'single'
            lines.append(f"| {r['key']} | {pos} | {len(r['line_crossings'])}/{len(r['piece_crossings'])} | {len(r['diagnostic_crossings'])} |")
    lines += ['', '## Every crossing and refused join','',
        'Line/piece indices below refer to the frozen output order. Exact boundary IDs and all provisional '
        'annotation element/cell/row IDs are in the machine-readable audit, without truncation.']
    for r in audit:
        if any(r[k] for k in ('line_crossings','piece_crossings','diagnostic_crossings','blocked_rows')):
            lines += ['',f"### {r['key']}",'',
                '- Active line indices: '+', '.join(str(v['line_index']) for v in r['line_crossings'])+'.',
                '- Piece indices: '+', '.join(str(v['piece_index']) for v in r['piece_crossings'])+'.',
                '- Diagnostic line indices: '+', '.join(str(v['line_index']) for v in r['diagnostic_crossings'])+'.',
                '- Refused row IDs: '+', '.join(v['row_id'] for v in r['blocked_rows'])+'.']
    lines += ['', '## Validation','',
        'The test suite receipt is `.astra/q1-tests.xml` and `.astra/q1-tests.log`. '
        'The focused tests cover a synthetic two-column page, physical spread, split table row, '
        'slanted and finite rules, forged mixed joins, exact sample preservation, and discounted rendering. '
        'The integration tests also cover live table preparation, renderer sidecars, separate component seeds, '
        'and scale invariance.','',
        (f"Full suite: **{tests['passed']} passed, {tests['skipped']} skipped, {tests['failures']} failures, "
         f"{tests['errors']} errors** ({tests['tests']} collected). The 16 browser cases require an unavailable "
         'Chromium executable; they were not executed. One existing Docling deprecation warning remains.' if tests else 'Full test receipt unavailable.'),'',
        'All 54 structure JPEGs decoded at their source dimensions. Three 18-page contact sheets were visually '
        'inspected, as were the six owner cases at larger size and selected table overlays. '
        'Those checks verify artifact presentation, not certified printed-row or table ownership.','',
        '```sh',
        'PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$PY" -m pytest -p no:cacheprovider --junitxml=.astra/q1-tests.xml -q',
        'PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/generate_api_docs.py',
        'PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/archive/review_line_structure.py',
        '# Fresh detections also emit structure (not used to overwrite the frozen baseline):',
        'PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/render_page_line_segments.py --layout .astra/layout --out /tmp/q1-fresh',
        '```','',
        '## Unresolved','',
        'The full-envelope no-crossing gate is not satisfied. Existing crossing records and uncertain table '
        'boundaries need adjudication before geometry corrections can be justified. Table annotation mismatches '
        'are enumerated in the audit; retaining pre-split row provenance alone does not certify a table grid. '
        'The eighth annotated page, `s2-dee99fdf5214acdc6f25-p00005`, has no retained table region in the frozen '
        'delivery, so its table text remains ordinary lines. This run did not change table discovery. '
        'Automatic fold inference remains a heuristic with an explicit metadata override.','']
    path.write_text('\n'.join(lines))


if __name__=='__main__':
    main()
