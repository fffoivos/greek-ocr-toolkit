"""Finish Q3 exact book/corpus and frozen statistics comparisons after page runs."""
from collections import defaultdict
import gzip
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.pages.check_q3_equality import differences, digest
from greekocr.pages import PageOptions, PageResult, process_book
from greekocr.pages.statistics import write_statistics, corpus_statistics


def main():
    directory=ROOT/'.astra/q3-equality'
    summary=json.loads((directory/'summary.json').read_text())
    assert len(summary['pages'])==95,'Complete the 95 page runs first'
    ref=directory/'reference/greekocr'
    spec=importlib.util.spec_from_file_location('q2_reference',ref/'__init__.py',submodule_search_locations=[str(ref)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    from q2_reference.glyphs.statistics import book_statistics as q2_book
    from q2_reference.glyphs.statistics import corpus_statistics as q2_corpus
    import pyarrow.parquet as pq
    selections=json.loads((ROOT/'.astra/book_pages/selection.json').read_text())
    identities={p['page']:p['book'] for p in selections['pages']}
    selection_order={p['page']:i for i,p in enumerate(selections['pages'])}
    groups=defaultdict(list)
    for row in summary['pages']:
        key=row['page_key'];book=identities.get(key,key.split('-',1)[-1].rsplit('-p',1)[0])
        groups[book].append(row)
    report=dict(books=[],runtime_differences=[],frozen_differences=[])
    old_corpus=[];new_corpus=[];old_book_corpus=[];new_book_corpus=[]
    for book,rows in sorted(groups.items()):
        for mode in ('default','tables','frozen_mode','book_only'):
            mode_rows = [row for row in rows if row['cohort']=='book'] if mode=='book_only' else rows
            if not mode_rows:continue
            if mode=='book_only':
                # The separate Q2 book snapshot used the original selection
                # manifest order. Preserve that input order before reduction;
                # sorting outputs would hide both ordering and float changes.
                mode_rows=sorted(mode_rows,key=lambda row:selection_order[row['page_key']])
            old_pages=[];new_pages=[]
            for row in mode_rows:
                key=row['page_key']
                selected = ('default' if mode=='book_only' else mode) if mode!='frozen_mode' else ('tables' if row['cohort']=='development' else 'default')
                with gzip.open(directory/f'{key}.{selected}.measurements.json.gz','rt') as stream:data=json.load(stream)
                old_pages.append(data['q2'])
                result=PageResult(key,book,tuple(data['api']['stats']['image_size']),tuple(data['api']['stats']['image_size']),
                                  PageOptions(statistics=True),SimpleNamespace(structure={}),[],[],[],data['api'])
                new_pages.append(result)
            old=q2_book(old_pages,book_id=book)
            new=process_book(new_pages,book_id=book,options=PageOptions(statistics=True))
            matches=old['stats']==new.statistics and old['pages']==[p.statistics for p in new.pages]
            item=dict(book_id=book,mode=mode,pages=len(mode_rows),equal=matches,statistics_sha256=digest(new.statistics),
                      input_order='selection manifest' if mode=='book_only' else 'development filenames, then book filenames')
            report['books'].append(item)
            if not matches:report['runtime_differences'].append(item)
            if mode=='book_only':
                old_book_corpus.extend(p['stats'] for p in old['pages'])
                new_book_corpus.extend(p.statistics['stats'] for p in new.pages)
                expected=ROOT/'.astra/out_after_Q2/book_pages/books'/f'{book}.stats.json'
                details=list(differences(json.loads(expected.read_text()),new.statistics))
                if details:
                    target=directory/f'{book}.frozen.book_only.diff.json';target.write_text(json.dumps(details,indent=2))
                    report['frozen_differences'].append(dict(book_id=book,field='book_only',differences=len(details),file=str(target)))
                continue
            if mode!='frozen_mode':continue
            old_corpus.extend(p['stats'] for p in old['pages']);new_corpus.extend(p.statistics['stats'] for p in new.pages)
            for meta,page in zip(rows,new.pages):
                frozen=ROOT/'.astra/out_after_Q2'
                if meta['cohort']=='book':frozen=frozen/'book_pages'
                key=page.page_key
                paths=write_statistics(page.statistics,directory/'book_api')
                expected=json.loads((frozen/f'{key}.stats.json').read_text())
                actual=json.loads(Path(paths['stats']).read_text())
                details=list(differences(expected,actual))
                if details:
                    target=directory/f'{key}.frozen.statistics.diff.json';target.write_text(json.dumps(details,indent=2))
                    report['frozen_differences'].append(dict(page_key=key,field='statistics',differences=len(details),file=str(target)))
                expected_rows=pq.read_table(frozen/f'{key}.glyphs.parquet').to_pylist()
                actual_rows=pq.read_table(paths['glyphs']).to_pylist()
                if expected_rows!=actual_rows:
                    details=list(differences(expected_rows,actual_rows))
                    target=directory/f'{key}.frozen.parquet.diff.json';target.write_text(json.dumps(details,indent=2))
                    report['frozen_differences'].append(dict(page_key=key,field='parquet',differences=len(details),file=str(target)))
            frozen_book=ROOT/'.astra/out_after_Q2/books'/f'{book}.stats.json'
            if frozen_book.exists():
                details=list(differences(json.loads(frozen_book.read_text()),new.statistics))
                if details:
                    target=directory/f'{book}.frozen.book.diff.json';target.write_text(json.dumps(details,indent=2))
                    report['frozen_differences'].append(dict(book_id=book,field='book',differences=len(details),file=str(target)))
            print(book,len(rows),'book variants equal',matches,flush=True)
    old=q2_corpus(old_corpus);new=corpus_statistics(new_corpus)
    report['corpus_equal']=old==new
    if old!=new:report['runtime_differences'].append(dict(field='corpus'))
    details=list(differences(json.loads((ROOT/'.astra/out_after_Q2/corpus.stats.json').read_text()),new))
    if details:
        target=directory/'corpus.frozen.diff.json';target.write_text(json.dumps(details,indent=2))
        report['frozen_differences'].append(dict(field='corpus',differences=len(details),file=str(target)))
    old=q2_corpus(old_book_corpus);new=corpus_statistics(new_book_corpus)
    report['book_only_corpus_equal']=old==new
    if old!=new:report['runtime_differences'].append(dict(field='book_only_corpus'))
    details=list(differences(json.loads((ROOT/'.astra/out_after_Q2/book_pages/corpus.stats.json').read_text()),new))
    if details:
        target=directory/'corpus.book_only.frozen.diff.json';target.write_text(json.dumps(details,indent=2))
        report['frozen_differences'].append(dict(field='book_only_corpus',differences=len(details),file=str(target)))
    report['runtime_equal']=not report['runtime_differences']
    report['frozen_equal']=not report['frozen_differences']
    (directory/'books-summary.json').write_text(json.dumps(report,indent=2))
    print('COMPLETE',report['runtime_equal'],report['frozen_equal'],flush=True)

    return int(not (report['runtime_equal'] and report['frozen_equal']))

if __name__=='__main__':raise SystemExit(main())
