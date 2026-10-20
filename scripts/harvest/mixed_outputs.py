"""T25 offline DocAI mapping, frozen admission, crops and evidence reports."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import ast
from datetime import datetime
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import time
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

import numpy as np
from PIL import Image, ImageDraw

from scripts.harvest.mixed import (REPO,OUT,BULK,GOOGLE,ADMISSION_SHA,PRIOR_WAVES,
    PARTS,sha,relative,atomic,read_jsonl,policy,round1,round2,vouli,MixedReaders,previous_page_hashes,replay_slots)
from scripts.harvest import vouli_outputs as previous
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest.admit_round1 import contact_sheets,stats,write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows,cohort_summary
from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest import admission

REASONS = admission.REASONS+('crop_geometry',)


def old_records():
    return [r for wave in PRIOR_WAVES for r in read_jsonl(REPO/f'docs/records/harvest/{wave}/admitted.jsonl')]


def raw_read(page,plan):
    root = previous.GOOGLE
    try:
        previous.GOOGLE = GOOGLE
        return previous.raw_read(page,plan)
    finally:
        previous.GOOGLE = root


def read_records(plan,write=False):
    records,audits = [],[]
    for i,page in enumerate(plan['pages'],1):
        raw,receipt = raw_read(page,plan)
        geometry,rows,docai,custody,median,error = None,[],[],[],None,None
        try:
            geometry = _response_geometry('docai',raw,(page['width'],page['height']))
            rows,docai,custody,median = make_rows(page,raw['document'],geometry)
        except ValueError as exc:
            error = str(exc)
        for row in rows:
            row.update(source=page['source'],licence=page['licence'],source_url=page['source_url'],
                attribution=page['attribution'],read_batch='mixed',part=page['part'])
        assignment = dict(schema='t25-page-assignment-1',page=page,reader=receipt,
            coordinate_frame=geometry['coordinate_frame'] if geometry else None,
            docai_lines=docai,docai_symbol_custody=custody,median_counted_line_height=median,
            lost_page=error is not None,geometry_error=error,records=rows)
        path = OUT/'assignments'/(page['id']+'.json')
        if write:
            atomic(path,assignment)
        elif assignment!=json.loads(path.read_text()):
            raise AssertionError('assignment replay changed: '+page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'],part=page['part'],**cohort_summary([page],rows),
            empty=not raw['document'].get('text','').strip(),
            no_line_layouts=not raw['document'].get('pages',[{}])[0].get('lines'),
            lost_page=error is not None,geometry_error=error,
            transformed=bool(geometry and geometry['coordinate_frame']['converted']),receipt=receipt))
        if i%100==0:
            print(f'records {i}/{len(plan["pages"])}',flush=True)
    return records,dict(schema='t25-read-summary-1',overall=cohort_summary(plan['pages'],records),
        pages=audits,empty_pages=sum(p['empty'] for p in audits),no_line_pages=sum(p['no_line_layouts'] for p in audits),
        lost_pages=sum(p['lost_page'] for p in audits),transformed_pages=sum(p['transformed'] for p in audits))


def admit_records(records,held,old):
    quality = admission.page_quality(records)
    splits = {b['book_key']:b['split'] for b in held}
    candidates,rejected = [],[]
    for r in records:
        good,cls,reasons,label = admission.admit(dict(r,bad_page=quality[r['page_id']]['bad_page']))
        if not good:
            rejected.append(dict(id=r['id'],reasons=reasons,docai_text=r['docai_text']))
            continue
        fields = ('id','page_id','book_key','year','decade','confidence','bbox','source','licence',
            'source_url','attribution','read_batch','part','docai_text')
        candidates.append(dict({k:r[k] for k in fields},split=splits.get(r['book_key'],'train'),
            script_class=cls,label=label,has_spacing_mark=admission.has_spacing_mark(label)))
    ids = {r['id'] for r in candidates}
    kept,o5 = admission.apply_holdout_labels(candidates+[dict(r) for r in old if r['split'] in ('test','dev')])
    kept = [r for r in kept if r['id'] in ids]
    rejected.extend(o5)
    labels = {admission.normalize_label(r['label']) for r in kept+old if r['split'] in ('test','dev')}
    exclusions = [dict(id=r['id'],source=r['source'],reason='label_in_holdout',label=r['label'])
        for r in old if r['split']=='train' and admission.normalize_label(r['label']) in labels]
    return kept,sorted(rejected,key=lambda r:r['id']),quality,len(candidates),exclusions


def training_pool(old,new,exclusions):
    excluded = {r['id'] for r in exclusions}
    rows = [r for r in old+new if r['split']=='train' and r['id'] not in excluded]
    vouli_rows = [r for r in rows if r['source']=='vouli_parliament_1850s' and r['script_class']=='greek_poly']
    other_poly = [r for r in rows if r['source']!='vouli_parliament_1850s' and r['script_class']=='greek_poly']
    maximum = 2*len(other_poly)//3
    kept = {r['id'] for r in sorted(vouli_rows,key=lambda r:previous.sha_seed(r['id']))[:maximum]}
    cap_exclusions = [dict(id=r['id'],source=r['source'],reason='per_source_cap',label=r['label'])
        for r in vouli_rows if r['id'] not in kept]
    excluded.update(r['id'] for r in cap_exclusions)
    rows = [r for r in rows if r['id'] not in excluded]
    files = {r['source']:f'docs/records/harvest/{wave}/admitted.jsonl' for wave in PRIOR_WAVES
        for r in read_jsonl(REPO/f'docs/records/harvest/{wave}/admitted.jsonl')[:1]}
    for r in new:files[r['source']]='docs/records/harvest/mixed/admitted.jsonl'
    fields = ('id','source','script_class','label','crop_path','crop_sha256','book_key','read_batch','licence')
    pool = [dict({k:r[k] for k in fields},split='train',admission_record_file=files[r['source']]) for r in rows]
    poly = [r for r in rows if r['script_class']=='greek_poly']
    count = sum(r['source']=='vouli_parliament_1850s' for r in poly)
    cap = dict(limit=.4,vouli_poly_train=count,combined_poly_train=len(poly),
        share=count/len(poly) if poly else 0,excluded=len(cap_exclusions),passed=5*count<=2*len(poly))
    return pool,cap_exclusions,cap


def compiled_path(page):
    year = page['year'] if page['year'] is not None else 'unknown'
    title = compiler.slug(page['title']) or 'untitled'
    return Path(page['part'])/f"{year}_{title}_{page['key'][:6]}"/f"p{page['page']:04d}.jpg"


def render_compiled(image,rows,quality):
    canvas,layout = compiler.render_page(image,rows)
    bad = quality.get('bad_page',False)
    if bad:
        ImageDraw.Draw(canvas).text((40,8),'REJECTED: bad_page | '+', '.join(quality['triggers']),
            font=compiler.number_font(),fill=compiler.RED)
    layout.update(bad_page=bad,bad_page_triggers=quality.get('triggers',[]))
    return canvas,layout


def compile_task(task):
    page,rows,quality = task
    rows_sha=hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
    custody=dict(page_image_sha256=page['image_sha256'],rows_sha256=rows_sha,quality=quality,
        builder_sha256=sha(Path(__file__)),base_builder_sha256=sha(Path(compiler.__file__)))
    cache=OUT/'compiled_pages'/(page['id']+'.json')
    path = BULK/'compiled'/compiled_path(page)
    if cache.exists():
        saved=json.loads(cache.read_text())
        if (saved.get('custody')==custody and path.exists() and sha(path)==saved['jpeg_sha256']):
            return saved
    with Image.open(REPO/page['image']) as image:
        canvas,layout = render_compiled(image,rows,quality)
    path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path,'JPEG',quality=85)
    entry=dict(page_id=page['id'],path=str(compiled_path(page)),jpeg_sha256=sha(path),
        raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(),custody=custody,**layout)
    atomic(cache,entry)
    return entry


def compile_watch():
    """Compile paid cached pages while acquisition continues; no Google calls."""
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as processes:
        while True:
            pages={}
            plans={}
            for file in sorted((OUT/'read_snapshots').glob('*.json')):
                plan=json.loads(file.read_text())
                for page in plan['pages']:
                    pages[page['id']]=page;plans[page['id']]=plan
            tasks=[]
            for pid,page in pages.items():
                if (OUT/'compiled_pages'/(pid+'.json')).exists():continue
                parsed=GOOGLE/'parsed/docai'/(page['image_sha256']+'.json')
                if not parsed.exists() or json.loads(parsed.read_text())['status']!='ok':continue
                raw,_=raw_read(page,plans[pid])
                try:
                    geometry=_response_geometry('docai',raw,(page['width'],page['height']))
                    rows,*_=make_rows(page,raw['document'],geometry)
                    for row in rows:
                        row.update(source=page['source'],licence=page['licence'],source_url=page['source_url'],
                            attribution=page['attribution'],read_batch='mixed',part=page['part'])
                except ValueError:
                    rows=[]
                quality=admission.page_quality(rows).get(pid,{})
                tasks.append((page,rows,quality))
            if tasks:
                for _ in processes.map(compile_task,tasks,chunksize=1):pass
                print(f'compiled cached pages: {len(list((OUT/"compiled_pages").glob("*.json")))}',flush=True)
            complete=all((p:=OUT/f'fetch_summary_{part}.json').exists() and json.loads(p.read_text()).get('complete',False) for part in PARTS)
            if complete:
                wanted={p['id'] for part in PARTS for p in json.loads((OUT/f'manifest_{part}.json').read_text()) if p['harvest_accepted']}
                cached={p.stem for p in (OUT/'compiled_pages').glob('*.json')}
                if wanted<=cached:return
            time.sleep(20)


def distribution(values):
    if not values:return dict(pages=0,min=None,p10=None,p25=None,median=None,p75=None,p90=None,max=None,mean=None)
    return dict(pages=len(values),**{name:float(np.percentile(values,q))
        for name,q in [('min',0),('p10',10),('p25',25),('median',50),('p75',75),('p90',90),('max',100)]},
        mean=float(np.mean(values)))


def share_report(plan,records,admitted):
    groups,kept = defaultdict(list),defaultdict(list)
    for row in records:groups[row['page_id']].append(row)
    for row in admitted:kept[row['page_id']].append(row)
    pages = []
    for p in plan['pages']:
        rows = groups[p['id']]
        eligible = [r for r in rows if admission.inventory(r['docai_text'])['letter_count']>=10]
        raw_cs = sum(admission.script_class(r['docai_text'])=='greek_latin_cs' for r in eligible)
        good = kept[p['id']]
        cs = sum(r['script_class']=='greek_latin_cs' for r in good)
        pages.append(dict(page_id=p['id'],part=p['part'],docai_lines=len(rows),eligible_raw_lines=len(eligible),
            detected_cs_lines=raw_cs,detected_cs_share=raw_cs/len(eligible) if eligible else None,
            admitted_lines=len(good),admitted_cs_lines=cs,admitted_cs_share=cs/len(good) if good else None))
    summaries = {part:dict(detected=distribution([p['detected_cs_share'] for p in pages
        if p['part']==part and p['detected_cs_share'] is not None]),
        admitted=distribution([p['admitted_cs_share'] for p in pages
        if p['part']==part and p['admitted_cs_share'] is not None]),
        zero_admitted_pages=sum(p['part']==part and not p['admitted_lines'] for p in pages)) for part in PARTS}
    return dict(definition='Greek-majority plus a whole Latin word >=2 letters. Detected: all >=10-letter DocAI lines before confidence/quality/O5. Admitted: cs / all admitted lines on that page. Empty denominators excluded from distributions and counted separately.',
        per_part=summaries,pages=pages)


def build(plan):
    records,reads = read_records(plan,write=True)
    write_jsonl(OUT/'records.jsonl',records);atomic(OUT/'read_summary.json',reads)
    old = old_records();held = json.loads((OUT/'holdout_books.json').read_text())
    admitted,rejected,quality,before,exclusions = admit_records(records,held,old)
    sizes = {p['id']:(p['width'],p['height']) for p in plan['pages']}
    admitted,crop_rejected,failures,geometries = previous.plan_crops(records,admitted,sizes)
    rejected = sorted(rejected+crop_rejected,key=lambda r:r['id'])
    atomic(OUT/'crop_failures.json',failures)
    groups,kept = defaultdict(list),{r['id']:r for r in admitted}
    for row in records:groups[row['page_id']].append(row)
    for i,(pid,rows) in enumerate(groups.items(),1):
        if sha(REPO/rows[0]['image'])!=rows[0]['image_sha256']:raise ValueError('crop image changed')
        with Image.open(REPO/rows[0]['image']) as image:
            assert image.mode=='L';image.load()
            for r in rows:
                if r['id'] not in kept:continue
                a=kept[r['id']];bounds,trimmed=geometries[r['id']]
                crop=image.crop(tuple(bounds))
                path=BULK/'crops'/r['book_key'][:8]/f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                path.parent.mkdir(parents=True,exist_ok=True)
                stream=io.BytesIO();crop.save(stream,format='PNG',compress_level=3)
                data=stream.getvalue();digest=hashlib.sha256(data).hexdigest()
                if not path.exists() or sha(path)!=digest:path.write_bytes(data)
                a.update(crop_path=relative(path),crop_sha256=digest,crop_width=crop.width,crop_height=crop.height,
                    crop_bbox=bounds,trimmed=trimmed)
                a.pop('docai_text')
        if i%100==0:print(f'crops {i}/{len(groups)}',flush=True)
    pool,cap_exclusions,cap=training_pool(old,admitted,exclusions)
    pool_ids={r['id'] for r in pool}
    for r in admitted:r['train_pool_eligible']=r['id'] in pool_ids
    sheets=contact_sheets(REPO,admitted,BULK/'admission_sheet')
    reasons=Counter(reason for r in rejected for reason in r['reasons'])
    summary=dict(schema='t25-admission-1',input_lines=len(records),pages=len(plan['pages']),
        admitted_before_o5=before,admitted=len(admitted),rejected=len(rejected),crops=len(admitted),
        trimmed=sum(r['trimmed'] for r in admitted),has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),
        per_reason={reason:reasons[reason] for reason in REASONS},
        per_split=dict(Counter(r['split'] for r in admitted)),
        per_class={cls:sum(r['script_class']==cls for r in admitted) for cls in admission.CLASSES},
        per_class_split={cls:{s:sum(r['script_class']==cls and r['split']==s for r in admitted)
            for s in ('train','dev','test')} for cls in admission.CLASSES},
        per_part={part:dict(lines=sum(r['part']==part for r in records),admitted=sum(r['part']==part for r in admitted),
            per_class_split={cls:{s:sum(r['part']==part and r['script_class']==cls and r['split']==s for r in admitted)
                for s in ('train','dev','test')} for cls in admission.CLASSES}) for part in PARTS},
        label_in_holdout=reasons['label_in_holdout'],bad_pages=[dict(page_id=pid,**q) for pid,q in quality.items() if q['bad_page']],
        crop_failures=len(failures),contact_sheets=sheets,crop_size_stats={k:stats([r['crop_'+k] for r in admitted]) for k in ('width','height')},
        holdout_policy=dict(seed=20261015,per_part=dict(Counter(b['part'] for b in held)),
            rounding='ceil(15% sources); nearest total dev count at 1/4, largest remainders per part; A 4/2, B 5/1, C 1/0 test/dev'),
        previous_train_label_exclusions=len(exclusions),per_source_cap=cap,admission_module_sha256=ADMISSION_SHA)
    for stem,rows in [('admitted',admitted),('rejected',rejected),('train_pool',pool),('train_pool_exclusions',exclusions+cap_exclusions)]:
        write_jsonl(OUT/(stem+'.jsonl'),rows)
    atomic(OUT/'admission_summary.json',summary)
    atomic(OUT/'mixed_share.json',share_report(plan,records,admitted))
    tasks=[(p,groups.get(p['id'],[]),quality.get(p['id'],{})) for p in plan['pages']]
    compiled=[]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as processes:
        for i,result in enumerate(processes.map(compile_task,tasks,chunksize=1),1):
            compiled.append(result)
            if i%100==0:print(f'compiled {i}/{len(tasks)}',flush=True)
    atomic(BULK/'compiled/compile_receipt.json',dict(schema='t25-compiled-1',pages=compiled,page_count=len(compiled),
        records_sha256=sha(_data_input(OUT/'records.jsonl')),base_builder_sha256=sha(Path(compiler.__file__)),builder_sha256=sha(Path(__file__)),jpeg_quality=85))
    (BULK/'compiled/README.txt').write_text(compiler.README.replace(' (the weakest 5%)','')+
        'Bad pages have red REJECTED: bad_page headings. Their lines are excluded at admission. Parts A/B/C follow the selection report.\n')
    print(json.dumps(dict(lines=len(records),admitted=len(admitted),compiled=len(compiled))),flush=True)


def validate_compiled(task):
    page,rows,quality,entry=task
    assert entry['path']==str(compiled_path(page))
    path=BULK/'compiled'/entry['path'];assert sha(path)==entry['jpeg_sha256']
    with Image.open(REPO/page['image']) as image:canvas,layout=render_compiled(image,rows,quality)
    assert hashlib.sha256(canvas.tobytes()).hexdigest()==entry['raster_sha256']
    assert all(entry[k]==v for k,v in layout.items())
    with Image.open(path) as image:assert image.size==canvas.size
    return page['id']


def validate(plan):
    books=json.loads((OUT/'books.json').read_text());held=json.loads((OUT/'holdout_books.json').read_text())
    selection=json.loads((OUT/'selection.json').read_text());manifest=json.loads((_data_input(OUT/'manifest.json')).read_text())
    assert Counter(b['part'] for b in books)=={'A':40,'B':40,'C':1}
    assert len({b['key'][:8] for b in books})==81
    assert held==policy.select_holdout(books)
    assert all(n<=5 for n in Counter(b['collection_slug'] for b in books if b['part']=='B').values())
    assert all(n<=5 for n in Counter(urlsplit(b['pdf_url']).netloc.lower() for b in books if b['part']=='B').values())
    anemi_catalogue={r['document_id']:r for r in read_jsonl(round2.CATALOGUE)}
    assert all(policy.anemi_eligible(anemi_catalogue[b['book']],set(selection['excluded']))[0] for b in books if b['part']=='A')
    combined=[]
    for part in PARTS:
        part_books=[b for b in books if b['part']==part]
        gates={f"{p['key']}:{p['page']}":p for p in manifest if p['part']==part}
        failed=json.loads((OUT/f'fetch_failures_{part}.json').read_text())
        slots,_=replay_slots(part_books,gates,failed)
        slot_order=lambda s:(s['key'],s['original_page'])
        assert sorted(slots,key=slot_order)==sorted(json.loads((OUT/f'slots_{part}.json').read_text()),key=slot_order)
        combined.extend(slots)
        for b in part_books:
            picks=policy.repository_positions(b['pages'],b['book']) if part=='B' else policy.spread_positions(b['pages'],12 if part=='A' else 100,b['book'])
            assert b['positions']==picks
    # Slot order in acquisition may differ from canonical source order.
    assert sorted(combined,key=lambda s:(s['key'],s['original_page']))==sorted(json.loads((OUT/'slots.json').read_text()),key=lambda s:(s['key'],s['original_page']))
    chosen={(s['key'],s['accepted_page']) for s in combined if s['accepted_page'] is not None}
    assert plan['pages']==[p for p in manifest if (p['key'],p['page']) in chosen]
    assert len(plan['pages'])==sum(p['harvest_accepted'] for p in manifest)
    reference=json.loads((round1.OUT/'manifest_all.json').read_text())[0]['gate']
    for p in manifest:
        assert sha(REPO/p['image'])==p['image_sha256']==p['gate']['image_sha256']
        g=p['gate'];assert g['gate_source_sha256']==round1.GATE_SHA
        assert all(g[k]==reference[k] for k in ('stack_source_sha256','stack_model_sha256'))
        flags,ratio=round1.quality_flags(g['features'],g['suppression_reasons'],g['lines'],plan['quality_limits'])
        assert flags==g['supplemental_quality_flags'] and ratio==g['faint_suppression_share']
        assert g['flags']==g['pilot_gate']['flags']+flags
        assert g['accepted']==(g['pilot_gate']['accepted'] and not flags)
        assert not (g['accepted'] and 'more_than_two_columns' in g['flags'])
        with Image.open(REPO/p['image']) as image:assert image.mode=='L' and image.size==(p['width'],p['height'])
        if p['part']=='A':
            assert sha(REPO/p['pdf'])==p['pdf_sha256']
    assert not list((BULK/'pdf').glob('*'))
    budget=read_jsonl(GOOGLE/'budget.jsonl');ledger=read_jsonl(GOOGLE/'docai/ledger.jsonl')
    hashes={p['image_sha256'] for p in plan['pages']}
    assert not previous_page_hashes()&hashes and not (GOOGLE/'vision').exists()
    assert len(budget)==len({r['key'] for r in budget})==len(hashes)==plan['max_calls']
    assert {r['key'] for r in budget}==hashes
    assert all(r['engine']=='docai' and r['micro_usd']==1500 for r in budget)
    assert len(ledger)==len({r['crop_sha256'] for r in ledger})==len(budget)
    assert all(r['status']=='ok' and not r['cached'] for r in ledger)
    assert len(budget)*1500<=2_000_000
    direct=read_jsonl(BULK/'direct_http/requests.jsonl')
    by_host=defaultdict(list)
    for r in direct:by_host[r['host']].append(r['started'])
    gaps=[b-a for times in by_host.values() for a,b in zip(sorted(times),sorted(times)[1:])]
    assert all(g>=1 for g in gaps)
    atomic(OUT/'direct_http_validation.json',dict(requests=len(direct),required_host_gap_s=1,
        min_host_gap_s=min(gaps) if gaps else None,passed=True,per_host=dict(Counter(r['host'] for r in direct))))
    records,reads=read_records(plan)
    assert records==read_jsonl(_data_input(OUT/'records.jsonl')) and reads==json.loads((OUT/'read_summary.json').read_text())
    assert len({r['id'] for r in records})==len(records)
    old=old_records();expected,rejected,quality,before,exclusions=admit_records(records,held,old)
    expected,crop_rejected,failures,geometries=previous.plan_crops(records,expected,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    actual=read_jsonl(_data_input(OUT/'admitted.jsonl'));summary=json.loads((OUT/'admission_summary.json').read_text())
    rejected=sorted(rejected+crop_rejected,key=lambda r:r['id'])
    assert rejected==read_jsonl(_data_input(OUT/'rejected.jsonl'))
    assert len(actual)+len(rejected)==len(records)
    assert [r['id'] for r in actual]==[r['id'] for r in expected]
    assert all(all(a[k]==v for k,v in e.items() if k!='docai_text') for a,e in zip(actual,expected))
    pool,cap_exclusions,cap=training_pool(old,actual,exclusions)
    assert len(pool)==len({r['id'] for r in pool})
    assert pool==read_jsonl(_data_input(OUT/'train_pool.jsonl'))
    assert exclusions+cap_exclusions==read_jsonl(OUT/'train_pool_exclusions.jsonl')
    labels={admission.normalize_label(r['label']) for r in old+actual if r['split'] in ('dev','test')}
    assert not labels&{r['label'] for r in pool} and cap['passed']
    amap={r['id']:r for r in actual};groups=defaultdict(list)
    for r in records:groups[r['page_id']].append(r)
    checked=0
    for i,(pid,rows) in enumerate(groups.items(),1):
        neighbours=admission.spatial_neighbours(rows)
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            for r in rows:
                if r['id'] not in amap:continue
                a=amap[r['id']];bounds,trimmed=admission.crop_geometry(r['bbox'],*neighbours[r['id']],image.size)
                assert bounds==a['crop_bbox'] and trimmed==a['trimmed'] and sha(REPO/a['crop_path'])==a['crop_sha256']
                assert Path(a['crop_path']).parent.name==r['book_key'][:8]
                assert Path(a['crop_path']).name==f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                with Image.open(REPO/a['crop_path']) as crop:
                    assert crop.mode=='L' and crop.size==(a['crop_width'],a['crop_height'])
                    assert crop.tobytes()==image.crop(tuple(bounds)).tobytes()
                checked+=1
        if i%100==0:print(f'validated native crops {i}/{len(groups)}',flush=True)
    assert checked==len(actual)==summary['crops']
    assert summary['per_reason']=={reason:sum(reason in r['reasons'] for r in rejected) for reason in REASONS}
    assert summary['per_class_split']=={cls:{s:sum(r['script_class']==cls and r['split']==s for r in actual)
        for s in ('train','dev','test')} for cls in admission.CLASSES}
    assert json.loads((OUT/'mixed_share.json').read_text())==share_report(plan,records,actual)
    compiled=json.loads((BULK/'compiled/compile_receipt.json').read_text())
    assert compiled['page_count']==len(plan['pages'])
    assert len({entry['path'] for entry in compiled['pages']})==len(plan['pages'])
    build_source=REPO/compiled.get('build_source_snapshot',relative(Path(__file__)))
    assert compiled['builder_sha256']==sha(build_source)
    assert compiled['base_builder_sha256']==sha(Path(compiler.__file__))
    # Preserve the actual build version when a validation-only repair follows
    # the build. The render functions must match and every raster is replayed.
    def render_functions(path):
        return {node.name:ast.dump(node,include_attributes=False)
            for node in ast.parse(path.read_text()).body if isinstance(node,ast.FunctionDef)
            and node.name in ('compiled_path','render_compiled','compile_task')}
    assert render_functions(build_source)==render_functions(Path(__file__))
    entries={e['page_id']:e for e in compiled['pages']}
    tasks=[(p,groups.get(p['id'],[]),quality.get(p['id'],{}),entries[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as processes:
        for _ in processes.map(validate_compiled,tasks,chunksize=1):pass
    for cls,sheet in summary['contact_sheets'].items():
        assert sha(REPO/sheet['path'])==sheet['sha256']
        assert len(sheet['ids'])==len(set(sheet['ids']))==min(60,summary['per_class'][cls])
        assert all(amap[ident]['script_class']==cls for ident in sheet['ids'])
    before_hashes={relative(p):sha(p) for p in (GOOGLE/'budget.jsonl',GOOGLE/'budget.state.json',GOOGLE/'docai/ledger.jsonl')}
    reader=MixedReaders(plan)
    def forbidden(*args,**kwargs):raise AssertionError('offline validation cannot call provider')
    reader.docai.read=forbidden
    for p in plan['pages']:assert reader.call('docai',REPO/p['image'])['status']=='ok'
    assert before_hashes=={p:sha(REPO/p) for p in before_hashes}
    assert sha(REPO/'greekocr/harvest/admission.py')==ADMISSION_SHA
    cost=json.loads((OUT/'cost_receipt.json').read_text())
    assert cost['calls_reserved']==len(budget) and cost['cost_usd']==len(budget)*.0015
    from scripts.harvest.mixed import git_audit
    git=git_audit()
    assert git['reflog_prefix_unchanged']
    atomic(OUT/'resume_check.json',dict(pages_replayed=len(plan['pages']),new_calls=0,new_reservations=0,
        provider_method_forbidden=True,unchanged_ledger_hashes=before_hashes))
    result=dict(passed=True,sources=dict(Counter(b['part'] for b in books)),pages_rendered=len(manifest),
        pages_read=len(plan['pages']),unique_calls=len(budget),lines=len(records),admitted=len(actual),
        crops_checked=checked,native_pixels_checked=checked,compiled_rasters_replayed=len(tasks),
        train_holdout_equal_labels=0,holdout_books=len(held),per_source_cap=cap,no_vision=True,git_unchanged=git['unchanged'],
        t25_git_write_operations=0,external_git_commits=len(git['appended_main_commits']),
        compiled_build_source=relative(build_source),compiled_build_sha256=compiled['builder_sha256'],
        render_functions_match_build_source=True)
    atomic(OUT/'validation.json',result);print(json.dumps(result),flush=True)


def tests_passed():
    suites=ET.parse(OUT/'tests.xml').getroot()
    rows=list(suites.iter('testsuite'))
    assert not sum(int(s.get('errors',0))+int(s.get('failures',0)) for s in rows)
    return sum(int(s.get('tests',0))-int(s.get('skipped',0)) for s in rows)


def final_line(plan,summary,tests,cost):
    books=json.loads((OUT/'books.json').read_text());counts=Counter(b['part'] for b in books)
    c=summary['per_class']
    return (f"T25: done | sources: {counts['A']}/{counts['B']}/{counts['C']} | "
        f"pages: {plan['pages_rendered']}/{plan['pages_accepted']}/{plan['page_count']} | "
        f"lines: {summary['input_lines']} | admitted: {summary['admitted']} | "
        f"cs: {c['greek_latin_cs']} | latin: {c['latin']} | poly: {c['greek_poly']} | mono: {c['greek_mono']} | "
        f"usd: {cost:.2f} | tests: {tests} passed")


def esc(value):return ' '.join(str(value).split()).replace('|','\\|')


def publish(plan):
    validation=json.loads((OUT/'validation.json').read_text());assert validation['passed']
    summary=json.loads((OUT/'admission_summary.json').read_text());reads=json.loads((OUT/'read_summary.json').read_text())
    books=json.loads((OUT/'books.json').read_text());held=json.loads((OUT/'holdout_books.json').read_text())
    splits={b['book_key']:b['split'] for b in held}
    shares=json.loads((OUT/'mixed_share.json').read_text());tests=tests_passed()
    visual=json.loads((OUT/'visual_qa.json').read_text())
    cost=json.loads((OUT/'cost_receipt.json').read_text())['cost_usd']
    fetch={part:json.loads((OUT/f'fetch_summary_{part}.json').read_text()) for part in PARTS}
    attempts=json.loads((OUT/'repository_attempts.json').read_text())
    unavailable_path=OUT/'anemi_unavailable_volumes.json'
    unavailable=json.loads(unavailable_path.read_text()) if unavailable_path.exists() else {}
    line=final_line(plan,summary,tests,cost)
    selection=['# T25 — Wave 5 selection','',
        'Seed 20265. A: 40 title-filtered Anemi sources, excluding round 1, round 2 and the 57 previously fetched early-print books. '
        'B: retained T24 OCR-routed candidates with 20–50% Latin; direct source links are used even when the metadata join was absent. '
        'Both recorded repository slug and actual bitstream host are capped at five documents: some metadata slugs disagree with the link host. '
        'The incompatible Wave 4 >=80% Greek/null-mojibake filters do not apply to this wave. '
        'C: b28038630, 1883, Public Domain Mark in the live Internet Archive metadata.','',
        'A/C: 12/100 seeded positions across 8–95%. B: seven positions strictly after floor(0.88 × page count), '
        'and three at 40/50/60%. Failed pages try at most the next two physical neighbours within their sampling region, '
        'excluding reserved positions. The frozen gate and photometric guards are unchanged; more_than_two_columns is rejected.','',
        'Hold-out seed 20261015, frozen before reads within each part: six of forty sources in each of A/B; '
        'A 4 test + 2 dev, B 5 test + 1 dev. C has one indivisible source, held out entirely as test. '
        'The total 10 test / 3 dev is the nearest whole-source apportionment of 3:1 for 13 held sources. '
        'No owner look was required in this run; class contact sheets and compiled pages support the post-hoc look.','',
        '| Part | Year | ID | Recorded repository / bitstream host | Title | Actual pages | Split | Picked pages |',
        '|---|---:|---|---|---|---:|---|---|']
    for b in books:
        selection.append(f"| {b['part']} | {b['year']} | {b['key'][:8]} | {b.get('collection_slug','—')} / {urlsplit(b.get('pdf_url',b['source_url'])).netloc} | "
            f"[{esc(b['title'])}]({b['source_url']}) | {b['pages']} | {splits.get(b['key'],'train')} | "+
            ', '.join(str(p['page']) for p in b['positions'])+' |')
    selection += ['','| Part | Target | Rendered | Accepted | Replacements | Failed/unavailable page candidates | Exhausted slots |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for part,s in fetch.items():
        selection.append(f"| {part} | {s['target']} | {s['rendered']} | {s['accepted']} | {s['replacements']} | {s['failures']} | {s['target']-s['accepted']} |")
    selection += ['','Full page replacement chains: [slots.json](slots.json). '
        'Full page gate flags: [manifest.json](manifest.json). Repository attempt ledger: [repository_attempts.json](repository_attempts.json).','',
        '| Failed repository candidate | Repository | Reason |','|---|---|---|']
    selection += [f"| {r['key']} | {r['repository']} | {esc(r.get('reason',r.get('error_class')))} |"
        for r in attempts if r['state']=='failed']
    if unavailable:
        selection += ['','| Unavailable Anemi volume | Source | Reason |','|---|---|---|']
        lookup={b['book']:b for b in books}
        selection += [f"| {entry['volume_id']} | {esc(lookup[entry['book']]['title'])} | {esc(entry['reason'])} |" for entry in unavailable.values()]
        selection += ['','Candidates skipped under a volume failure are marked source_unavailable in slots.json. '
            'The public transfer ledger and anemi_fetch_invocations retain the bounded acquisition evidence.']
    (OUT/'SELECTION.md').write_text('\n'.join(selection)+'\n')
    report=['# T25 — Wave 5 mixed and Latin reads','',
        f"**{len(books)} sources; {plan['pages_rendered']} rendered / {plan['pages_accepted']} gate-accepted / "
        f"{plan['page_count']} Document AI-read pages; {summary['input_lines']:,} lines; {summary['admitted']:,} admitted native crops.** "
        f"USD {cost:.4f} reserved at the T19 list-price estimate, cap USD 2.00; zero Vision calls. {tests} offline tests passed.",'',
        '| Part | Sources selected | Sources with rendered pages | Sources read | Rendered | Accepted/read | DocAI lines | Admitted |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for part in PARTS:
        pages=[p for p in plan['pages'] if p['part']==part]
        rendered=json.loads((OUT/f'manifest_{part}.json').read_text())
        report.append(f"| {part} | {sum(b['part']==part for b in books)} | {len({p['key'] for p in rendered})} | {len({p['key'] for p in pages})} | {fetch[part]['rendered']} | "
            f"{len(pages)} | {summary['per_part'][part]['lines']} | {summary['per_part'][part]['admitted']} |")
    report += ['','A = Anemi dictionaries/grammars/journals; B = repository bibliography/middle pages; '
        'C = Internet Archive lexicon. Recorded rights for each B source are retained in books.json; repository licences are unverified. '
        'OCR routing metadata identifies candidates; it is not proof that every sampled page is a scan.','',
        '| Gate / photometric flag (overlapping counts) | A | B | C |','|---|---:|---:|---:|']
    gate_flags=sorted({flag for part in PARTS for flag in fetch[part]['gate_flags']})
    report += ['| '+flag+' | '+' | '.join(str(fetch[part]['gate_flags'].get(flag,0)) for part in PARTS)+' |' for flag in gate_flags]
    report += ['',
        '| Class | Train | Dev | Test | Total |','|---|---:|---:|---:|---:|']
    for cls,counts in summary['per_class_split'].items():
        report.append(f"| {cls} | {counts['train']} | {counts['dev']} | {counts['test']} | {sum(counts.values())} |")
    report += ['','| Part | Class | Train | Dev | Test |','|---|---|---:|---:|---:|']
    for part in PARTS:
        for cls,counts in summary['per_part'][part]['per_class_split'].items():
            report.append(f"| {part} | {cls} | {counts['train']} | {counts['dev']} | {counts['test']} |")
    report += ['','Greek-majority lines containing a whole Latin word of at least two letters are greek_latin_cs; '
        'Latin-majority lines are latin. Classification and every admission rule use the unchanged T20 module. '
        'Labels are normalized as T20, with spacing marks flagged rather than silently corrected.','',
        'Mixed-line share per page: '+shares['definition'],'',
        '| Part | Stage | Pages with denominator | Min | P10 | P25 | Median | P75 | P90 | Max | Mean |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for part,d in shares['per_part'].items():
        for stage in ('detected','admitted'):
            s=d[stage]
            report.append(f"| {part} | {stage} | {s['pages']} | "+' | '.join(
                f"{s[k]:.1%}" if s[k] is not None else '—' for k in ('min','p10','p25','median','p75','p90','max','mean'))+' |')
    report += ['','Empty admitted denominators: '+', '.join(f"{p}: {s['zero_admitted_pages']}" for p,s in shares['per_part'].items())+'.','',
        '| Rejection reason (overlapping counts) | Lines |','|---|---:|']
    report += [f'| {reason} | {n} |' for reason,n in summary['per_reason'].items()]
    report += ['',f"{len(summary['bad_pages'])} bad pages; {summary['crop_failures']} invalid crop geometries; "
        f"{summary['trimmed']} crops trimmed at neighbour overlaps. Lost coordinate-frame pages: {reads['lost_pages']}; "
        f"empty responses: {reads['empty_pages']}; responses without line layouts: {reads['no_line_pages']}.",'',
        f"Hold-out: A 6 sources (4 test / 2 dev), B 6 (5 test / 1 dev); C's only source is entirely test. "
        'Total 10 test / 3 dev, the nearest integer 3:1 allocation for 13 sources. '
        f"All existing hold-out labels participate in O5. {summary['label_in_holdout']} new train lines dropped; "
        f"{summary['previous_train_label_exclusions']} prior train lines excluded in the combined overlay. "
        'Use train_pool.jsonl for the combined training pool; earlier waves remain frozen. '
        'No normalized equal labels remain between that pool and any hold-out. '
        f"Vouli contributes {summary['per_source_cap']['share']:.2%} of combined polytonic train lines (cap 40%).",'',
        f"Target 980 accepted pages; actual shortfall {980-plan['pages_accepted']} after bounded neighbour replacements. "
        f"Repository documents tried {len(attempts)}, downloaded/rendered {sum(r['state']=='downloaded_rendered' for r in attempts)}, "
        f"failed {sum(r['state']=='failed' for r in attempts)}. No more than five selected documents per repository. "
        'Repository and IA PDFs were deleted after rendering; SHA-256, size, page count and download receipts remain.','',
        f"Anemi unavailable volumes: {len(unavailable)}. Volume failures and skipped candidates are distinguished from individual page requests "
        'in [anemi_unavailable_volumes.json](anemi_unavailable_volumes.json) and [slots.json](slots.json). '
        'A viewer stall recovered with a fresh authenticated client; [recovery evidence](anemi_recoveries.json) retains the observations without assuming a cause.','',
        f"Native review confirmed two cross-column provider-line merges; {visual['wide_box_review']['count']} wide bboxes are "
        'flagged for review in [column_width_review.jsonl](column_width_review.jsonl). '
        'The heuristic flags do not change admission. See [visual QA](visual_qa.json) for source-linked examples and review limits.','',
        'All crop pixels and all compiled rasters were replay-validated. Those checks establish artifact fidelity, '
        'not transcription accuracy or perfect glyph ownership. '
        'At-most-once cached replay made zero new provider calls. T25 invoked no Git writes. '
        f"The [Git audit](git_audit.json) records {validation['external_git_commits']} external T24/T24b commits during this run; frozen data inputs still match.",'',
        '[Selection](SELECTION.md), [admission summary](admission_summary.json), [hold-outs](holdout_books.json), '
        '[mixed shares](mixed_share.json), [validation](validation.json), [tests](tests.xml), '
        '[cost](cost_receipt.json), [inventory](inventory.json).','',line]
    (OUT/'READS.md').write_text('\n'.join(report)+'\n')
    state_path=REPO/'docs/records/harvest/collection/EXECUTION_STATE.md';state=state_path.read_text()
    now=datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    start=json.loads((OUT/'run_state.json').read_text())['started_at']
    start=datetime.fromisoformat(start).astimezone(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    old=next(l for l in state.splitlines() if l.startswith('| 5 mixed + Latin |'))
    state=state.replace(old,f"| 5 mixed + Latin | T25 | complete (bounded page shortfall) | {start} | {now} | "
        f"{plan['pages_rendered']} / {plan['pages_accepted']} / {plan['page_count']} | {summary['admitted']} | {cost:.4f} |")
    section=f"## Wave 5\n\nT25 completed {now} Athens: 40 Anemi / 40 repository / 1 Internet Archive sources; "
    section+=f"{plan['pages_rendered']} rendered / {plan['pages_accepted']} accepted / {plan['page_count']} read pages. "
    section+=f"{summary['input_lines']} DocAI lines, {summary['admitted']} admitted native crops; "
    section+=f"{summary['per_class']['greek_latin_cs']} Greek-with-Latin and {summary['per_class']['latin']} Latin lines. "
    section+=f"USD {cost:.4f}, cap 2.00; {tests} offline tests passed. Zero Vision calls; T20 unchanged; no Git writes by T25 (external T24/T24b commits recorded in Git audit).\n\n"
    section+='A/B hold-outs: six sources each; A 4 test / 2 dev, B 5 test / 1 dev; the single IA source is test-only. Total 10 test / 3 dev after integer rounding. '
    section+=f"O5 includes all prior hold-outs; {summary['previous_train_label_exclusions']} earlier train lines excluded in the combined overlay. "
    section+=f"Target shortfall {980-plan['pages_accepted']} pages after bounded replacements. "
    section+='All native crops and compiled rasters replay-validated; physical/transcription limitations remain in visual QA.\n\n'
    section+='[Selection](../mixed/SELECTION.md), [report](../mixed/READS.md), [validation](../mixed/validation.json), '
    section+='[combined training pool](../mixed/train_pool.jsonl), [inventory](../mixed/inventory.json).\n\n'+line+'\n'
    if '## Wave 5' in state:state=state.split('## Wave 5')[0].rstrip()+'\n\n'+section
    else:state=state.rstrip()+'\n\n'+section
    state_path.write_text(state)
    inventory_path=REPO/'docs/INVENTORY.md';inventory=inventory_path.read_text()
    marker='## T25 — Wave 5 mixed and Latin collection'
    item=f"{marker}\n\nSeeded three-part acquisition and frozen admission: "
    item+='[policy](../greekocr/harvest/mixed.py), [runner](../scripts/harvest/mixed.py), '
    item+='[outputs and verification](../scripts/harvest/mixed_outputs.py), [offline tests](../tests/test_mixed.py). '
    item+=f"81 sources; {plan['page_count']} read pages; {summary['admitted']} admitted crops. "
    item+='[Report](harvest/mixed/READS.md), [selection](harvest/mixed/SELECTION.md), '
    item+='[file inventory](harvest/mixed/inventory.json). Bulk crops, pages, responses and class sheets are under harvest_big/mixed.\n'
    if marker not in inventory:inventory_path.write_text(inventory.rstrip()+'\n\n'+item)
    paths=[p for p in OUT.rglob('*') if p.is_file() and p.name!='inventory.json']
    paths += [REPO/'greekocr/harvest/mixed.py',REPO/'scripts/harvest/mixed.py',Path(__file__),REPO/'tests/test_mixed.py']
    atomic(OUT/'inventory.json',dict(schema='t25-inventory-1',files=[dict(path=relative(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(paths))],
        bulk=relative(BULK),bulk_files=sum(p.is_file() for p in BULK.rglob('*')),
        crops=summary['crops'],compiled_pages=plan['page_count'],contact_sheets=summary['contact_sheets']))
    print(line,flush=True)
