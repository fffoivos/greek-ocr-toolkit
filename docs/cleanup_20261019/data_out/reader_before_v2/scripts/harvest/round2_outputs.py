"""T22 offline records, unchanged T20 admission, native crops and evidence."""
from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import random
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from scripts.harvest.round2 import (REPO, OUT, BULK, GOOGLE, SOURCE, ADMISSION_SHA,
    sha, relative, atomic, read_jsonl, select_holdout, replay_slots, Round2Readers, round1)
from scripts.harvest import vouli_outputs as previous
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest.admit_round1 import contact_sheets, stats, write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows, cohort_summary
from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest import admission

REASONS = admission.REASONS + ('crop_geometry',)
OLD_FILES = ('docs/harvest/round1/admitted.jsonl', 'docs/harvest/vouli/admitted.jsonl')
RECORD_FILES = {'anemi_round1': OLD_FILES[0], 'vouli_parliament_1850s': OLD_FILES[1], SOURCE:'docs/harvest/round2/admitted.jsonl'}


def raw_read(page, plan):
    # The T21 raw/cache/image/binding verifier is reused without changing it.
    root = previous.GOOGLE
    try:
        previous.GOOGLE = GOOGLE
        return previous.raw_read(page, plan)
    finally:
        previous.GOOGLE = root


def read_records(plan, write=False):
    records, audits = [], []
    for page in plan['pages']:
        raw, receipt = raw_read(page, plan)
        geometry, rows, docai, custody, median, error = None, [], [], [], None, None
        try:
            geometry = _response_geometry('docai', raw, (page['width'],page['height']))
            rows, docai, custody, median = make_rows(page, raw['document'], geometry)
        except ValueError as exc:
            error = str(exc)
        for r in rows:
            r.update(source=SOURCE, licence='anemi-research-internal', source_url=page['source_url'],
                attribution=page['attribution'], read_batch='round2')
        assignment = dict(schema='t22-page-assignment-1', page=page, reader=receipt,
            coordinate_frame=geometry['coordinate_frame'] if geometry else None,
            docai_lines=docai, docai_symbol_custody=custody, median_counted_line_height=median,
            lost_page=error is not None, geometry_error=error, records=rows)
        path = OUT / 'assignments' / (page['id']+'.json')
        if write:
            atomic(path, assignment)
        elif assignment != json.loads(path.read_text()):
            raise AssertionError('assignment replay changed: '+page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'], **cohort_summary([page],rows),
            empty=not raw['document'].get('text','').strip(),
            no_line_layouts=not raw['document'].get('pages',[{}])[0].get('lines'),
            lost_page=error is not None, geometry_error=error,
            transformed=bool(geometry and geometry['coordinate_frame']['converted']), receipt=receipt))
    return records, dict(schema='t22-read-summary-1', overall=cohort_summary(plan['pages'],records),
        pages=audits, empty_pages=sum(p['empty'] for p in audits),
        no_line_pages=sum(p['no_line_layouts'] for p in audits),
        lost_pages=sum(p['lost_page'] for p in audits), transformed_pages=sum(p['transformed'] for p in audits))


def admit_records(records, held, old):
    quality = admission.page_quality(records)
    splits = {b['book_key']: b['split'] for b in held}
    candidates, rejected = [], []
    for r in records:
        good, cls, reasons, label = admission.admit(dict(r,bad_page=quality[r['page_id']]['bad_page']))
        if good:
            candidates.append(dict(id=r['id'], page_id=r['page_id'], book_key=r['book_key'],
                year=r['year'], decade=r['decade'], split=splits.get(r['book_key'],'train'),
                script_class=cls, label=label, has_spacing_mark=admission.has_spacing_mark(label),
                confidence=r['confidence'], bbox=r['bbox'], source=SOURCE, licence=r['licence'],
                source_url=r['source_url'], attribution=r['attribution'], read_batch='round2', docai_text=r['docai_text']))
        else:
            rejected.append(dict(id=r['id'],reasons=reasons,docai_text=r['docai_text']))
    external = [dict(r) for r in old if r['split'] in ('dev','test')]
    kept, o5 = admission.apply_holdout_labels(candidates+external)
    labels = {r['label'] for r in kept if r['split'] in ('dev','test')}
    kept = [r for r in kept if r['source']==SOURCE]
    rejected.extend(o5)
    exclusions = [dict(id=r['id'],source=r['source'],reason='label_in_holdout',label=r['label'])
        for r in old if r['split']=='train' and admission.normalize_label(r['label']) in labels]
    return kept, sorted(rejected,key=lambda r:r['id']), quality, len(candidates), exclusions


def training_pool(old, new, exclusions):
    excluded = {r['id'] for r in exclusions}
    rows = [r for r in old+new if r['split']=='train' and r['id'] not in excluded]
    vouli = [r for r in rows if r['source']=='vouli_parliament_1850s' and r['script_class']=='greek_poly']
    others = [r for r in rows if r['source']!='vouli_parliament_1850s' and r['script_class']=='greek_poly']
    maximum = 2*len(others)//3
    kept_vouli = {r['id'] for r in sorted(vouli,key=lambda r:previous.sha_seed(r['id']))[:maximum]}
    cap_exclusions = [dict(id=r['id'],source=r['source'],reason='per_source_cap',label=r['label']) for r in vouli if r['id'] not in kept_vouli]
    excluded.update(r['id'] for r in cap_exclusions)
    rows = [r for r in rows if r['id'] not in excluded]
    poly = [r for r in rows if r['script_class']=='greek_poly']
    n = sum(r['source']=='vouli_parliament_1850s' for r in poly)
    pool = [dict({k:r[k] for k in ('id','source','script_class','label','crop_path','crop_sha256','book_key','read_batch','licence')},
                 split='train',admission_record_file=RECORD_FILES[r['source']]) for r in rows]
    return pool, cap_exclusions, dict(limit=.4,vouli_poly_train=n,combined_poly_train=len(poly),
        share=n/len(poly) if poly else 0,excluded=len(cap_exclusions),passed=5*n<=2*len(poly))


def compiled_path(page):
    return compiler.relative_path(page)


def render_compiled(image, rows, quality):
    canvas, layout = compiler.render_page(image,rows)
    bad = quality.get('bad_page',False)
    if bad:
        text = 'REJECTED: bad_page | '+', '.join(quality['triggers'])+' | all lines excluded at admission'
        ImageDraw.Draw(canvas).text((40,8),text,font=compiler.number_font(),fill=compiler.RED)
    layout['bad_page'] = bad
    layout['bad_page_triggers'] = quality.get('triggers',[])
    return canvas, layout


def compile_task(task):
    p, rows, quality = task
    with Image.open(REPO/p['image']) as image:
        canvas, layout = render_compiled(image,rows,quality)
    path = BULK/'compiled'/compiled_path(p)
    path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path,'JPEG',quality=85)
    return dict(page_id=p['id'],path=str(compiled_path(p)),jpeg_sha256=sha(path),
        raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(),**layout)


def build(plan):
    records, reads = read_records(plan,write=True)
    write_jsonl(OUT/'records.jsonl',records)
    atomic(OUT/'read_summary.json',reads)
    old = [r for name in OLD_FILES for r in read_jsonl(REPO/name)]
    held = json.loads((OUT/'holdout_books.json').read_text())
    admitted, rejected, quality, before, exclusions = admit_records(records,held,old)
    sizes = {p['id']:(p['width'],p['height']) for p in plan['pages']}
    admitted, crop_rejected, crop_failures, geometries = previous.plan_crops(records,admitted,sizes)
    rejected = sorted(rejected+crop_rejected,key=lambda r:r['id'])
    atomic(OUT/'crop_failures.json',crop_failures)
    groups, kept = defaultdict(list), {r['id']:r for r in admitted}
    for r in records:
        groups[r['page_id']].append(r)
    for i,(pid,rows) in enumerate(groups.items(),1):
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            assert image.mode=='L' and sha(REPO/rows[0]['image'])==rows[0]['image_sha256']
            for r in rows:
                if r['id'] not in kept:
                    continue
                a = kept[r['id']]
                bounds,trimmed = geometries[r['id']]
                crop = image.crop(tuple(bounds))
                path = BULK/'crops'/r['book_key'][:6]/f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                path.parent.mkdir(parents=True,exist_ok=True)
                stream=io.BytesIO();crop.save(stream,format='PNG',compress_level=3)
                data=stream.getvalue();digest=hashlib.sha256(data).hexdigest()
                if not path.exists() or sha(path)!=digest:
                    path.write_bytes(data)
                a.update(crop_path=relative(path),crop_sha256=digest,crop_width=crop.width,crop_height=crop.height,
                    crop_bbox=bounds,trimmed=trimmed)
                a.pop('docai_text')
        if i%100==0:
            print(f'crops {i}/{len(groups)}',flush=True)
    pool,cap_exclusions,cap = training_pool(old,admitted,exclusions)
    pool_ids = {r['id'] for r in pool}
    for r in admitted:
        r['train_pool_eligible']=r['id'] in pool_ids
    sheets=contact_sheets(REPO,admitted,BULK/'admission_sheet')
    reasons=Counter(reason for r in rejected for reason in r['reasons'])
    summary=dict(schema='t22-admission-1',input_lines=len(records),pages=len(groups),
        admitted_before_o5=before,admitted=len(admitted),rejected=len(rejected),crops=len(admitted),
        trimmed=sum(r['trimmed'] for r in admitted),has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),
        per_reason={r:reasons[r] for r in REASONS},per_split=dict(Counter(r['split'] for r in admitted)),
        per_class={c:sum(r['script_class']==c for r in admitted) for c in admission.CLASSES},
        per_class_split={c:{s:sum(r['script_class']==c and r['split']==s for r in admitted) for s in ('train','dev','test')} for c in admission.CLASSES},
        per_decade={str(d):dict(Counter(r['split'] for r in admitted if r['decade']==d)) for d in range(1860,1940,10)},
        label_in_holdout=reasons['label_in_holdout'],bad_pages=[dict(page_id=pid,**q) for pid,q in quality.items() if q['bad_page']],
        crop_failures=len(crop_failures),contact_sheets=sheets,
        crop_size_stats={k:stats([r['crop_'+k] for r in admitted]) for k in ('width','height')},
        holdout_policy=dict(seed=20261015,books=8,dev=2,test=6,selection='one seeded book per decade before reads'),
        previous_train_label_exclusions=len(exclusions),per_source_cap=cap,admission_module_sha256=ADMISSION_SHA)
    for name,rows in [('admitted',admitted),('rejected',rejected),('train_pool',pool),('train_pool_exclusions',exclusions+cap_exclusions)]:
        write_jsonl(OUT/(name+'.jsonl'),rows)
    atomic(OUT/'admission_summary.json',summary)
    tasks=[(p,groups.get(p['id'],[]),quality.get(p['id'],{})) for p in plan['pages']]
    compiled=[]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as process_pool:
        for i,result in enumerate(process_pool.map(compile_task,tasks,chunksize=1),1):
            compiled.append(result)
            if i%100==0: print(f'compiled {i}/{len(tasks)}',flush=True)
    atomic(BULK/'compiled/compile_receipt.json',dict(schema='t22-compiled-1',pages=compiled,page_count=len(compiled),
        records_sha256=sha(OUT/'records.jsonl'),base_builder_sha256=sha(Path(compiler.__file__)),
        builder_sha256=sha(Path(__file__)),jpeg_quality=85,pad=40,gap=40))
    (BULK/'compiled/README.txt').write_text(compiler.README.replace(' (the weakest 5%)','')+
        'Bad pages remain compiled, with a red REJECTED: bad_page heading and their triggers. All their lines are excluded from admission.\n')
    print(json.dumps(dict(lines=len(records),admitted=len(admitted),compiled=len(compiled))),flush=True)
    return summary


def validate_compiled_task(task):
    p,rows,quality,entry=task
    assert entry['path']==str(compiled_path(p))
    path=BULK/'compiled'/entry['path']
    assert sha(path)==entry['jpeg_sha256']
    with Image.open(REPO/p['image']) as image:
        canvas,layout=render_compiled(image,rows,quality)
    assert hashlib.sha256(canvas.tobytes()).hexdigest()==entry['raster_sha256']
    assert all(entry[k]==v for k,v in layout.items())
    with Image.open(path) as im: assert im.size==canvas.size
    return p['id']


def validate(plan):
    from scripts.harvest.round2 import eligible, early_exclusions, CATALOGUE, previous_page_hashes
    books=json.loads((OUT/'books.json').read_text());selection=json.loads((OUT/'selection.json').read_text())
    held=json.loads((OUT/'holdout_books.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    failed=json.loads((OUT/'fetch_failures.json').read_text())
    assert len(books)==len({b['book'] for b in books})==50
    assert Counter(b['decade'] for b in books)=={int(k):v for k,v in selection['quotas'].items()}
    assert all(6<=n<=7 for n in Counter(b['decade'] for b in books).values())
    excluded=set(selection['excluded_round1'])|set(selection['excluded_early'])
    assert len(selection['excluded_round1'])==150 and len(selection['excluded_early'])==57
    catalogue={r['document_id']:r for r in read_jsonl(CATALOGUE)}
    assert all(eligible(catalogue[b['book']],excluded)[0] for b in books)
    assert held==select_holdout(books) and Counter(b['split'] for b in held)=={'test':6,'dev':2}
    gate_map={f"{p['key']}:{p['page']}":p for p in manifest}
    slots,_=replay_slots(books,gate_map,failed)
    assert slots==json.loads((OUT/'slots.json').read_text()) and len(slots)==650
    assert all(len(s['candidate_pages'])<=3 and all(s['original_page']<=n<=s['original_page']+2 for n in s['candidate_pages']) for s in slots)
    selected={(s['key'],s['accepted_page']) for s in slots if s['accepted_page'] is not None}
    assert len(selected)==sum(s['accepted_page'] is not None for s in slots)
    assert plan['pages']==[p for p in manifest if (p['key'],p['page']) in selected]
    assert {p['id'] for p in plan['pages']}=={p['id'] for p in manifest if p['harvest_accepted']}
    fm=round1.fetch_module()
    bmap={b['key']:b for b in books}
    reference_gate=json.loads((round1.OUT/'manifest_all.json').read_text())[0]['gate']
    saved={(p['record_id'],p['volume_id'],p['page_index'],p['sha256'])
        for p in read_jsonl(BULK/'ledger.jsonl') if p.get('state')=='saved'}
    assert saved=={(p['book'],p['volume'],p['volume_page']-1,p['pdf_sha256']) for p in manifest}
    for p in manifest:
        b=bmap[p['key']];v,local=round1.locate(b,p['page'])
        assert fm.valid_receipt(p['fetch_receipt'],BULK/'records'/p['key'],b['catalogue'],v,local-1)
        assert sha(REPO/p['pdf'])==p['pdf_sha256'] and sha(REPO/p['image'])==p['image_sha256']==p['gate']['image_sha256']
        g=p['gate'];assert g['gate_source_sha256']==round1.GATE_SHA
        assert all(g[k]==reference_gate[k] for k in ('stack_source_sha256','stack_model_sha256'))
        flags,ratio=round1.quality_flags(g['features'],g['suppression_reasons'],g['lines'],plan['quality_limits'])
        assert flags==g['supplemental_quality_flags'] and ratio==g['faint_suppression_share']
        assert g['flags']==g['pilot_gate']['flags']+flags and g['accepted']==(g['pilot_gate']['accepted'] and not flags)
        with Image.open(REPO/p['image']) as im: assert im.mode=='L' and im.size==(p['width'],p['height'])
    budget=read_jsonl(GOOGLE/'budget.jsonl');ledger=read_jsonl(GOOGLE/'docai/ledger.jsonl')
    assert not previous_page_hashes() & {p['image_sha256'] for p in plan['pages']}
    assert not (GOOGLE/'vision').exists()
    assert len(budget)==len({r['key'] for r in budget})==plan['max_calls']
    assert {r['key'] for r in budget}=={p['image_sha256'] for p in plan['pages']}
    assert all(r['engine']=='docai' and r['micro_usd']==1500 for r in budget)
    assert len(ledger)==len({r['crop_sha256'] for r in ledger})==len(budget)
    assert all(r['status']=='ok' and not r['cached'] for r in ledger)
    assert len(budget)*1500<=1_500_000
    assert json.loads((GOOGLE/'budget.state.json').read_text())['calls']==len(budget)
    cost=json.loads((OUT/'cost_receipt.json').read_text())
    assert cost['calls_reserved']==len(budget) and cost['cost_usd']==len(budget)*.0015
    records,reads=read_records(plan)
    assert records==read_jsonl(OUT/'records.jsonl') and reads==json.loads((OUT/'read_summary.json').read_text())
    assert len(records)==len({r['id'] for r in records})
    assert all(r['source']==SOURCE and r['licence']=='anemi-research-internal' and r['read_batch']=='round2' for r in records)
    old=[r for name in OLD_FILES for r in read_jsonl(REPO/name)]
    expected,rejected,quality,before,exclusions=admit_records(records,held,old)
    expected,crop_rejected,crop_failures,geometries=previous.plan_crops(records,expected,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    actual=read_jsonl(OUT/'admitted.jsonl');summary=json.loads((OUT/'admission_summary.json').read_text())
    assert sorted(rejected+crop_rejected,key=lambda r:r['id'])==read_jsonl(OUT/'rejected.jsonl')
    assert len(actual)+len(rejected)+len(crop_rejected)==len(records)
    assert [r['id'] for r in actual]==[r['id'] for r in expected]
    assert all(all(a[k]==v for k,v in e.items() if k!='docai_text') for a,e in zip(actual,expected))
    pool,cap_exclusions,cap=training_pool(old,actual,exclusions)
    assert pool==read_jsonl(OUT/'train_pool.jsonl') and exclusions+cap_exclusions==read_jsonl(OUT/'train_pool_exclusions.jsonl')
    labels={r['label'] for r in old+actual if r['split'] in ('dev','test')}
    assert not labels&{r['label'] for r in pool} and cap['passed']
    amap={r['id']:r for r in actual};groups=defaultdict(list)
    for r in records: groups[r['page_id']].append(r)
    checked=0
    for i,(pid,rows) in enumerate(groups.items(),1):
        neighbours=admission.spatial_neighbours(rows)
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            for r in rows:
                if r['id'] not in amap: continue
                a=amap[r['id']];bounds,trimmed=admission.crop_geometry(r['bbox'],*neighbours[r['id']],image.size)
                assert bounds==a['crop_bbox'] and trimmed==a['trimmed'] and sha(REPO/a['crop_path'])==a['crop_sha256']
                assert Path(a['crop_path']).parent.name==r['book_key'][:6]
                assert Path(a['crop_path']).name==f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                with Image.open(REPO/a['crop_path']) as crop:
                    assert crop.mode=='L' and crop.size==(a['crop_width'],a['crop_height'])
                    assert crop.tobytes()==image.crop(tuple(bounds)).tobytes()
                checked+=1
        if i%100==0: print(f'validated native crops {i}/{len(groups)}',flush=True)
    assert checked==len(actual)==summary['crops']
    assert summary['per_class_split']=={c:{s:sum(r['script_class']==c and r['split']==s for r in actual) for s in ('train','dev','test')} for c in admission.CLASSES}
    all_rejected=read_jsonl(OUT/'rejected.jsonl')
    assert summary['per_reason']=={reason:sum(reason in r['reasons'] for r in all_rejected) for reason in REASONS}
    assert summary['per_source_cap']==cap
    receipt=json.loads((BULK/'compiled/compile_receipt.json').read_text())
    assert receipt['builder_sha256']==sha(Path(__file__)) and receipt['base_builder_sha256']==sha(Path(compiler.__file__))
    assert receipt['page_count']==plan['page_count']
    entries={e['page_id']:e for e in receipt['pages']}
    tasks=[(p,groups.get(p['id'],[]),quality.get(p['id'],{}),entries[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as process_pool:
        for _ in process_pool.map(validate_compiled_task,tasks,chunksize=1): pass
    assert {e['page_id'] for e in receipt['pages'] if e['bad_page']}=={p['page_id'] for p in summary['bad_pages']}
    for cls,sheet in summary['contact_sheets'].items():
        assert sha(REPO/sheet['path'])==sheet['sha256']
        assert len(sheet['ids'])==len(set(sheet['ids']))==min(60,summary['per_class'][cls])
        assert all(amap[i]['script_class']==cls for i in sheet['ids'])
        with Image.open(REPO/sheet['path']) as im: assert im.size==(sheet['width'],sheet['height'])
    before_hashes={relative(p):sha(p) for p in (GOOGLE/'budget.jsonl',GOOGLE/'budget.state.json',GOOGLE/'docai/ledger.jsonl')}
    readers=Round2Readers(plan)
    def forbidden(*args,**kwargs): raise AssertionError('offline replay cannot call provider')
    readers.docai.read=forbidden
    for p in plan['pages']: assert readers.call('docai',REPO/p['image'])['status']=='ok'
    assert before_hashes=={p:sha(REPO/p) for p in before_hashes}
    assert sha(REPO/'greekocr/harvest/admission.py')==ADMISSION_SHA
    atomic(OUT/'resume_check.json',dict(pages_replayed=plan['page_count'],new_calls=0,new_reservations=0,provider_method_forbidden=True,unchanged_ledger_hashes=before_hashes))
    result=dict(passed=True,books=50,pages_fetched=len(manifest),pages_read=plan['page_count'],unique_calls=len(budget),
        lines=len(records),admitted=len(actual),crops_checked=checked,native_pixels_checked=checked,
        compiled_rasters_replayed=len(tasks),bad_pages_visibly_marked=len(summary['bad_pages']),
        train_holdout_equal_labels=0,holdout_books=8,per_source_cap=cap)
    atomic(OUT/'validation.json',result)
    print(json.dumps(result),flush=True)
    return result


def publish(plan):
    validation=json.loads((OUT/'validation.json').read_text());assert validation['passed']
    suites=list(ET.parse(OUT/'tests.xml').getroot().iter('testsuite'))
    assert suites and not any(int(s.get(k,0)) for s in suites for k in ('failures','errors','skipped'))
    tests=sum(int(s.get('tests',0)) for s in suites)
    s=json.loads((OUT/'admission_summary.json').read_text());fetch=json.loads((OUT/'fetch_summary.json').read_text())
    reads=json.loads((OUT/'read_summary.json').read_text());cost=json.loads((OUT/'cost_receipt.json').read_text())
    acquisition=json.loads((OUT/'run_state.json').read_text())
    acquisition_wall_seconds=(datetime.fromisoformat(acquisition['finished_at'])-datetime.fromisoformat(acquisition['started_at'])).total_seconds()
    transport=read_jsonl(BULK/'anemi_http/transfer.jsonl')
    # This exact short response lacked both the login form and viewer iframe;
    # its body was never persisted. HTTP 200 alone did not make it usable.
    unusable_sha='9c11a7de9aa43bf4e96ac339d636bfb4c2b4ac6ff0a6a55a7d5dcbb2a57ead74'
    transport_issues=[{k:r.get(k) for k in ('url','method','status','bytes','sha256','fetched_at','read_error')}
        for r in transport if r['status']==0 or r['status']>=400 or r['sha256']==unusable_sha]
    atomic(OUT/'transport_issues.json',dict(issues=transport_issues,
        note='Public response metadata only; known unusable 81-byte response or failed transport/HTTP error status. No login or error bodies stored.'))
    books=json.loads((OUT/'books.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    fetched_books=len({p['book'] for p in manifest})
    read_books=len({p['book'] for p in plan['pages']})
    held={r['book_key']:r['split'] for r in json.loads((OUT/'holdout_books.json').read_text())}
    records=read_jsonl(OUT/'records.jsonl');admitted=read_jsonl(OUT/'admitted.jsonl');splits=s['per_split']
    last=(f"T22: done | books: {len(books)} | pages: {fetch['fetched']}/{fetch['accepted']}/{plan['page_count']} | "
        f"lines: {len(records)} | admitted: {s['admitted']} | poly: {s['per_class']['greek_poly']} | "
        f"train: {splits.get('train',0)} | dev: {splits.get('dev',0)} | test: {splits.get('test',0)} | "
        f"usd: {cost['cost_usd']:.2f} | tests: {tests} passed")
    lines=['# T22 — Wave 2 Anemi round 2', '',
        f"**50 new books; {fetch['fetched']} pages fetched, {fetch['accepted']} gate accepted, {plan['page_count']} read; "
        f"{len(records):,} DocAI lines, {s['admitted']:,} admitted native crops.**", '',
        f"{fetched_books} books yielded fetched pages; **{read_books} yielded accepted/read pages**. "
        'A selected book whose sampled pages all fail the unchanged gate remains visible with zero reads in the book table; '
        'it is not silently replaced by a different book after the seeded draw.', '',
        f"Selection seed 20262: 6 books each in the 1860s–1900s and 1920s; 7 each in the 1910s and 1930s. "
        'All 150 round-1 books and the 57 early-print books with saved receipts are excluded. '
        '[SELECTION.md](SELECTION.md) reports the full draw, eligibility, round-1 place/publisher counts and diversity weighting.', '',
        'Exactly 13 initial slots/book spread 8–95%, with seeded 0–2 offsets. Failed pages can use +1/+2 neighbours only. '
        f"**Accepted-page target shortfall: {fetch['shortfall']}.** {fetch['replacements']} accepted replacements. "
        'Exhausted slots are retained in [slots.json](slots.json); no extra page search weakens the frozen gate or replacement bound.', '',
        f"The unchanged T16 page gate SHA `{round1.GATE_SHA}` and calibrated photometric guards were used. "
        'pypdfium2 renders source-bound single-page PDFs to 200 dpi grey PNG. Source original page/volume positions, '
        'PDF/image hashes and fetch receipts are in [manifest.json](manifest.json). Two-page spreads remain whole pages. '
        'No owner look was applied, as authorized on 15 October.', '',
        'DocAI uses the pinned T19 EU binding, Greek hint, symbol option and ADC. Provider line layouts, anchored symbol '
        'mean/min confidence and inverse transforms follow T21. Source is `anemi_round2`, licence '
        '`anemi-research-internal`, batch `round2`. All T20 rules are reused byte-for-byte, including bad_page. '
        'Native bboxes and labels remain automatic OCR evidence for later owner review.', '',
        '| Class | Train | Dev | Test | Total |','|---|---:|---:|---:|---:|']
    for cls in admission.CLASSES:
        c=s['per_class_split'][cls];lines.append(f"| {cls} | {c['train']} | {c['dev']} | {c['test']} | {sum(c.values())} |")
    lines+=['','| Rejection reason | Lines (overlapping) |','|---|---:|']
    lines += [f'| {reason} | {n} |' for reason,n in s['per_reason'].items()]
    lines += ['', 'Seed 20261015 freezes 8 held-out books before reads, one per decade: 6 test / 2 dev. '
        f"O5 drops {s['label_in_holdout']} round-2 train labels equal to **any round-1, Vouli or round-2 hold-out label**. "
        f"The combined [train_pool.jsonl](train_pool.jsonl) also excludes {s['previous_train_label_exclusions']} earlier train rows "
        'with matching hold-out labels. Earlier admitted artifacts remain frozen. '
        f"Vouli provides {s['per_source_cap']['share']:.2%} of the combined polytonic train pool (limit 40%).", '',
        f"Crops: unchanged spatial-neighbour >15% overlap midpoint trim, 4 px horizontal / 2 px vertical padding, "
        f"native grey PNG; {s['trimmed']} trimmed. Paths use the requested `<id6>/p<page6>-l<line4>.png`. "
        f"{len(s['bad_pages'])} bad pages are excluded after the read and remain in compiled JPEGs with a red `REJECTED: bad_page` header. "
        f"All {plan['page_count']} read pages are compiled under `<decade>s/<year>_<title40>_<id6>/pNNNN.jpg`. "
        'Five class sheets show 60 seeded unique examples per populated class, or all available when fewer than 60.', '',
        f"Cost: {cost['calls_reserved']} unique reserved DocAI calls, **USD {cost['cost_usd']:.4f}** (cap USD 1.50), "
        'at the same T19 list-price estimate of USD 1.50/1,000 pages; this is not invoice readback. '
        'Ledger: `docs/harvest/harvest_big/round2/google/budget.jsonl`. Zero Vision calls. '
        'Reservations precede requests under SHA locks. Offline replay of every cache invoked no provider and changed no ledger hashes.', '',
        'Reads began on frozen snapshots of permanently accepted slots while acquisition continued. '
        '`read_snapshots/` binds each early page/image set to the already frozen books and hold-outs. '
        'The final plan contains every earlier reserved image SHA; the final run reuses those responses. '
        'Validation checks exact equality between final unique image hashes and the one-reservation-per-image ledger.', '',
        f"Fetch failures: {fetch['fetch_failures']} page attempts; read failures: {reads['lost_pages']} lost coordinate frames, "
        f"{reads['empty_pages']} empty, {reads['no_line_pages']} without line layouts; {s['crop_failures']} uncuttable crop geometries. "
        '[fetch_failures.json](fetch_failures.json) contains source-bound failed page receipts. '
        '[prefetch_transport_failures.json](prefetch_transport_failures.json) records the corrected initial pre-page login bookkeeping; '
        'those unattempted pages were returned to their original slots before resume. '
        f"[transport_issues.json](transport_issues.json) records {len(transport_issues)} unusable short or error responses, "
        'including a later viewer-only pause that resumed from its public source-bound descriptor. '
        'These interruptions are separate from page-fetch failures and successful PDF receipts.', '',
        '| Cost / acquisition measure | Value |','|---|---:|',
        f"| Unique DocAI calls reserved | {cost['calls_reserved']} |",
        f"| Estimated USD / cap | {cost['cost_usd']:.4f} / 1.50 |",
        f"| Fetch/gate total wall minutes, including interruption/resume | {acquisition_wall_seconds/60:.2f} |",
        f"| Fetched pages per wall minute | {fetch['fetched']/(acquisition_wall_seconds/60):.2f} |",
        f"| Page-fetch failures | {fetch['fetch_failures']} |",
        f"| Unusable short / error transport responses | {len(transport_issues)} |",
        f"| Exhausted page slots | {fetch['shortfall']} |", '',
        '| Page gate flag | Pages (overlapping) |','|---|---:|']
    lines += [f'| {reason} | {n} |' for reason,n in sorted(fetch['gate_flags'].items())]
    lines += ['', '| Book | Year | Split | Fetched | Accepted | Read | Lines | Admitted |', '|---|---:|---|---:|---:|---:|---:|---:|']
    for b in books:
        c=fetch['per_book'][b['key']];title=b['title'].replace('|','\\|').replace('\n',' ')
        lines.append(f"| [{title}]({b['source_url']}) (`{b['id6']}`) | {b['year']} | {held.get(b['key'],'train')} | "
            f"{c['fetched']} | {c['accepted']} | {sum(p['key']==b['key'] for p in plan['pages'])} | "
            f"{sum(r['book_key']==b['key'] for r in records)} | {sum(r['book_key']==b['key'] for r in admitted)} |")
    lines += ['',f'**{tests} offline tests passed.** Full admission decisions, native pixels, compiled rasters, '
        'selection exclusions, quotas and at-most-once replay are checked in [validation.json](validation.json). '
        '[tests](tests.xml), [summary](admission_summary.json), [hold-outs](holdout_books.json), [inventory](inventory.json).', '',last]
    (OUT/'READS.md').write_text('\n'.join(lines)+'\n')
    before=json.loads((OUT/'git_before.json').read_text());after=round1.git_snapshot()
    main_paths=('HEAD','index','refs/heads/main','packed-refs','logs/HEAD','logs/refs/heads/main','config')
    atomic(OUT/'git_audit.json',dict(unchanged=before==after,
        main_worktree_unchanged=all(before.get(p)==after.get(p) for p in main_paths),
        main_metadata={p:dict(before=before.get(p),after=after.get(p)) for p in main_paths},
        changed=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],
        note='No git mutation commands issued; shared worktree/object activity is recorded separately.'))
    state_path=REPO/'docs/harvest/collection/EXECUTION_STATE.md';state=state_path.read_text()
    now=datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    row=next(x for x in state.splitlines() if x.startswith('| 2 polytonic round 2 |'))
    state=state.replace(row,f"| 2 polytonic round 2 | T22 | complete | 2026-10-15 02:01 | {now} | {fetch['fetched']} / {fetch['accepted']} / {plan['page_count']} | {s['admitted']} | {cost['cost_usd']:.4f} |")
    section='\n'.join(['## Wave 2','',
        f"T22 completed {now} Athens: 50 new Anemi books, {fetch['fetched']} fetched / {fetch['accepted']} accepted / {plan['page_count']} read pages. "
        f"{read_books} books yielded accepted/read pages. "
        f"{len(records)} DocAI lines, {s['admitted']} admitted native crops, {s['per_class']['greek_poly']} polytonic. "
        f"Train {splits.get('train',0)} / dev {splits.get('dev',0)} / test {splits.get('test',0)}; 8 held-out books (6 test / 2 dev). "
        f"USD {cost['cost_usd']:.4f}, cap 1.50; zero Vision calls. {tests} offline tests passed.",'',
        f"Target 650 accepted pages; shortfall {fetch['shortfall']}, after the bounded original/+1/+2 neighbour rule. "
        f"{len(s['bad_pages'])} bad pages rejected after reading and marked in compiled images. "
        'O5 checks all three waves and the combined training overlay; the T20 admission module is unchanged. '
        f"Vouli polytonic train share {s['per_source_cap']['share']:.2%} (≤40%).",'',
        '[Selection](../round2/SELECTION.md), [report](../round2/READS.md), [summary](../round2/admission_summary.json), '
        '[validation](../round2/validation.json), [training pool](../round2/train_pool.jsonl), [inventory](../round2/inventory.json).','',last])
    tail=''
    if '\n## Wave 2\n' in state:
        state,old_section=state.split('\n## Wave 2\n',1)
        next_heading=old_section.find('\n## ')
        if next_heading>=0: tail=old_section[next_heading:]
    state_path.write_text(state.rstrip()+'\n\n'+section+'\n'+tail)
    inventory_path=REPO/'docs/INVENTORY.md';text=inventory_path.read_text()
    section='\n'.join(['<!-- T22:begin -->','## T22 — Anemi Wave 2 (15 October 2026)','',
        f"50 new books; {fetch['fetched']} fetched / {fetch['accepted']} accepted / {plan['page_count']} read; "
        f"{len(records)} DocAI lines; {s['admitted']} native crops; USD {cost['cost_usd']:.4f}; {tests} offline tests passed.",'',
        '`python -m scripts.harvest.round2 select|fetch-gate|plan|read-watch|run|build|validate|publish`; '
        'fetch-gate uses Anemi; read-watch (optional overlap) and run use Document AI. '
        'Unchanged T16 gate/T20 admission/T21 read mapping; seeded selection/hold-outs; at-most-once page SHA reads. '
        'Compiled bad pages retain visible red rejection headings. Bulk PDFs, PNGs, Google caches, crops and JPEGs remain ignored under `harvest_big/round2/`.', '',
        '[Selection](harvest/round2/SELECTION.md), [reads](harvest/round2/READS.md), [records](harvest/round2/records.jsonl), '
        '[admitted](harvest/round2/admitted.jsonl), [rejected](harvest/round2/rejected.jsonl), [summary](harvest/round2/admission_summary.json), '
        '[hold-outs](harvest/round2/holdout_books.json), [training pool](harvest/round2/train_pool.jsonl), '
        '[validation](harvest/round2/validation.json), [tests](harvest/round2/tests.xml), [hash inventory](harvest/round2/inventory.json).','', '<!-- T22:end -->'])
    if '<!-- T22:begin -->' in text:
        a,rest=text.split('<!-- T22:begin -->',1);_,b=rest.split('<!-- T22:end -->',1);text=a+section+b
    else: text=text.rstrip()+'\n\n'+section+'\n'
    inventory_path.write_text(text)
    files=[p for root in (OUT,BULK) for p in root.rglob('*') if p.is_file() and p.name!='inventory.json']
    sources=[REPO/p for p in ('scripts/harvest/round2.py','scripts/harvest/round2_outputs.py','tests/test_round2.py','greekocr/harvest/admission.py')]
    atomic(OUT/'inventory.json',dict(files={relative(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in files},
        sources={relative(p):sha(p) for p in sources},admission_module_sha256=ADMISSION_SHA))
    print(last,flush=True)
    return last
