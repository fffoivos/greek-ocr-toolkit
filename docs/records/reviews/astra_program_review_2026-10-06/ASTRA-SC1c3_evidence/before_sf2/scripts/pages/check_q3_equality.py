"""Compare Q2's committed implementation and artifacts with the high-level API.

Run from the repository root. The reference package is read from a git archive,
never imported from the working tree. No tolerances, field rounding or sorting
of arrays is used. The report distinguishes runtime equality from frozen files.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import io
import time
import warnings

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from PIL import Image

REFERENCE = '10eda96'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def differences(a, b, path='$'):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b:
                yield dict(path=f'{path}.{k}', kind='missing', q2=k in a, api=k in b)
            else:
                yield from differences(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield dict(path=path, kind='length', q2=len(a), api=len(b))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                yield from differences(x, y, f'{path}[{i}]')
    elif a != b:
        yield dict(path=path, kind='value', q2=a, api=b)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=ROOT/'.astra/q3-equality')
    p.add_argument('--keys', nargs='*')
    p.add_argument('--resume', action='store_true')
    p.add_argument('--summary-name', default='summary.json', help='distinct receipt for a disjoint foreground partition')
    args = p.parse_args()
    if Path(args.summary_name).name != args.summary_name:
        p.error('--summary-name must be a filename')
    args.out.mkdir(parents=True, exist_ok=True)
    base = args.out/'reference'; base.mkdir(exist_ok=True)
    raw = subprocess.check_output(['git','archive',REFERENCE,'greekocr'])
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        archive.extractall(base)
    # Load the exact Q2 package under an independent name. Its three absolute
    # crop imports still refer to the byte-identical protected crop implementation.
    spec = importlib.util.spec_from_file_location('q2_reference',base/'greekocr/__init__.py',
                                                 submodule_search_locations=[str(base/'greekocr')])
    module = importlib.util.module_from_spec(spec);sys.modules[spec.name] = module;spec.loader.exec_module(module)
    from q2_reference.glyphs.page_text_lines import segment_page, extract_line_image
    from q2_reference.glyphs.table_lines import prepare_delivery
    from q2_reference.glyphs.line_structure import delivery_records
    from q2_reference.glyphs.statistics import page_statistics, write_statistics
    from greekocr.pages import PageOptions, process_page
    from greekocr.pages.lines import extract_line_image as new_extract
    from greekocr.pages.statistics import write_statistics as new_write
    from greekocr.pages.layout import read_layout
    import pyarrow.parquet as pq
    warnings.filterwarnings('ignore', category=np.exceptions.RankWarning)
    selection = json.loads((ROOT/'.astra/book_pages/selection.json').read_text())
    books = {r['page']:r['book'] for r in selection['pages']}
    sources = [(p,'development') for p in sorted((ROOT/'.astra/pages').glob('*.png'))]
    sources += [(p,'book') for p in sorted((ROOT/'.astra/book_pages').glob('*.png'))]
    report = dict(reference_commit=subprocess.check_output(['git','rev-parse',REFERENCE]).decode().strip(),
                  pages=[], runtime_differences=[], frozen_differences=[])
    for path, cohort in sources:
        if args.keys and path.stem not in args.keys:continue
        target=args.out/(path.stem+'.json')
        if args.resume and target.exists():
            previous=json.loads(target.read_text())
            if previous['source_sha256']!=hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError(f'Resume source changed: {path}')
            report['pages'].append(previous);continue
        start=time.monotonic();key=path.stem
        book=books.get(key,key.split('-',1)[-1].rsplit('-p',1)[0])
        with Image.open(path) as im: source=im.copy()
        gray=source.convert('L')
        layout=ROOT/'.astra/layout'/f'{key}.json'
        regions=read_layout(layout,source.size) if layout.exists() else []
        row=dict(page_key=key,cohort=cohort,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 modes={},runtime_differences=[],frozen_differences=[])
        for tables in (False,True):
            name='tables' if tables else 'default'
            old=segment_page(gray)
            old,pcs,_=prepare_delivery(gray,old,regions if tables else [],supplement=tables)
            old_lines=[line.to_record() for line in old.lines]
            old_cells=[piece.to_record(i,source.size,[v/3 for v in source.size]) for i,piece in enumerate(pcs)]
            measured=page_statistics(source,old_lines,page_key=key,book_id=book,structure=old.structure)
            new=process_page(source,options=PageOptions(tables=tables,statistics=True),
                             page_key=key,book_id=book,page_size=[v/3 for v in source.size],
                             table_regions=regions if tables else None)
            new_cells=new.to_records()['cells']['cells']
            checks={}
            for field,a,b in [('lines',old_lines,new.lines),('structure',old.structure,new.structure),
                              ('cells',old_cells,new_cells),('statistics',measured,new.statistics),
                              ('segments',old.segments,new.segmentation.segments),
                              ('diagnostics',old.diagnostics,new.segmentation.diagnostics)]:
                same=a==b;checks[field]=same
                if not same:
                    details=list(differences(json.loads(json.dumps(a)),json.loads(json.dumps(b))))
                    diffpath=args.out/f'{key}.{name}.{field}.diff.json'
                    diffpath.write_text(json.dumps(details,indent=2))
                    row['runtime_differences'].append(dict(mode=name,field=field,differences=len(details),file=str(diffpath)))
            old_images=[hashlib.sha256(np.asarray(extract_line_image(gray,p.line)).tobytes()).hexdigest() for p in pcs]
            new_images=[hashlib.sha256(np.asarray(new_extract(source,p.line)).tobytes()).hexdigest() for p in new.pieces]
            checks['delivered_pixels']=old_images==new_images
            if not checks['delivered_pixels']:row['runtime_differences'].append(dict(mode=name,field='delivered_pixels'))
            # Evaluate every pre-existing Q1 granularity and preserve refusal outcomes.
            for granularity in ('default','rows','pieces'):
                outcomes=[]
                for fn,lines,structure in [(delivery_records,old_lines,old.structure),
                                           (__import__('greekocr.pages.structure',fromlist=['delivery_records']).delivery_records,new.lines,new.structure)]:
                    try:outcomes.append(dict(records=fn(lines,structure=structure,granularity=granularity)))
                    except ValueError as error:outcomes.append(dict(error=str(error)))
                checks['join_'+granularity]=outcomes[0]==outcomes[1]
                if outcomes[0]!=outcomes[1]:row['runtime_differences'].append(dict(mode=name,field='join_'+granularity))
            for label,result,writer in [('q2',measured,write_statistics),('api',new.statistics,new_write)]:
                paths=writer(result,args.out/label/name)
                table=pq.read_table(paths['glyphs'])
                if label=='q2':old_rows=table.to_pylist()
                else:checks['parquet_rows']=old_rows==table.to_pylist()
            if not checks['parquet_rows']:row['runtime_differences'].append(dict(mode=name,field='parquet_rows'))
            # Persist exact measurements for a later complete-book comparison.
            with gzip.open(args.out/f'{key}.{name}.measurements.json.gz','wt') as stream:
                json.dump(dict(q2=measured,api=new.statistics),stream,allow_nan=False)
            frozen=ROOT/'.astra/out_after_Q2'
            if cohort=='book':frozen=frozen/'book_pages'
            if tables == (cohort=='development'):
                for field,a,b in [('lines',json.loads((frozen/f'{key}.lines.json').read_text()),new.lines),
                                  ('structure',json.loads((frozen/f'{key}.structure.json').read_text()),new.structure),
                                  ('cells',json.loads((frozen/f'{key}.cells.json').read_text()),new.to_records()['cells'])]:
                    details=list(differences(a,b))
                    if details:
                        diffpath=args.out/f'{key}.frozen.{field}.diff.json';diffpath.write_text(json.dumps(details,indent=2))
                        row['frozen_differences'].append(dict(field=field,differences=len(details),file=str(diffpath)))
            row['modes'][name]=dict(checks=checks,line_count=len(new.lines),piece_count=len(new.pieces),glyph_count=len(new.glyphs),
                                   hashes=dict(lines=digest(new.lines),cells=digest(new_cells),statistics=digest(new.statistics)))
            del old,new,measured,old_rows
        row['seconds']=round(time.monotonic()-start,3)
        target.write_text(json.dumps(row,indent=2));report['pages'].append(row)
        print(key,round(row['seconds'],1),'runtime differences',len(row['runtime_differences']),
              'frozen differences',len(row['frozen_differences']),flush=True)
    for row in report['pages']:
        for field in ('runtime_differences','frozen_differences'):
            report[field].extend(dict(page_key=row['page_key'],**d) for d in row[field])
    report['runtime_equal']=not report['runtime_differences']
    report['frozen_equal']=not report['frozen_differences']
    (args.out/args.summary_name).write_text(json.dumps(report,indent=2))
    print('COMPLETE',len(report['pages']),'runtime_equal',report['runtime_equal'],'frozen_equal',report['frozen_equal'],flush=True)

    return int(not (report['runtime_equal'] and report['frozen_equal']))

if __name__=='__main__':raise SystemExit(main())
