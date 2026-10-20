"""Offline T26 mapping, page-language exclusion, unchanged T20 admission and validation."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
from greekocr.harvest import admission
from greekocr.harvest.page_reads import _response_geometry
from scripts.harvest.cyrillic import (REPO,OUT,BULK,GOOGLE,CAP,ADMISSION_SHA,PRIOR_WAVES,
    sha,relative,atomic,read_jsonl,policy,vouli,round1,round2,CyrillicReaders)
from scripts.harvest import vouli_outputs as previous
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest import compact_parliament_raw as archive
from scripts.harvest.admit_round1 import contact_sheets,stats,write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows,cohort_summary
from scripts.harvest.mixed_outputs import distribution

REASONS=admission.REASONS+('not_cyrillic_page','crop_geometry')


def raw_read(page,plan):
    parsed_path=GOOGLE/'parsed/docai'/(page['image_sha256']+'.json')
    parsed=json.loads(parsed_path.read_text());assert parsed['status']=='ok'
    assert parsed['binding']==plan['binding'] and parsed['image_sha256']==sha(REPO/page['image'])
    raw=Path(parsed['raw_json_path']);cache_path=raw.parent/'cache.json';cache=json.loads(cache_path.read_text())
    data,packed=archive.raw_bytes(raw)
    assert hashlib.sha256(data).hexdigest()==cache['raw_sha256']
    assert cache['crop_sha256']==page['image_sha256'] and cache['binding']==plan['binding'] and cache['receipt_id']==parsed['receipt_id']
    return json.loads(data),dict(receipt_id=parsed['receipt_id'],raw_json_path=relative(raw),raw_sha256=cache['raw_sha256'],
        storage_path=relative(packed or raw),storage_sha256=sha(packed or raw),cache_path=relative(cache_path),cache_sha256=sha(cache_path),
        parsed_path=relative(parsed_path),parsed_sha256=sha(parsed_path))


def read_records(plan,write=False):
    records,audits=[],[]
    for i,p in enumerate(plan['pages'],1):
        raw,receipt=raw_read(p,plan);doc=raw['document'];page=doc['pages'][0]
        script=policy.page_script(doc.get('text',''))
        languages=page.get('detectedLanguages',[])
        rows=[];geometry=None;error=None;docai=[];custody=[];median=None
        try:
            geometry=_response_geometry('docai',raw,(p['width'],p['height']))
            rows,docai,custody,median=make_rows(p,doc,geometry)
        except ValueError as exc:error=str(exc)
        for r in rows:
            r.update(source=p['source'],licence=p['licence'],source_url=p['source_url'],attribution=p['attribution'],
                read_batch='cyrillic',detected_languages=languages,**script)
        assignment=dict(schema='t26-assignment-1',page=p,reader=receipt,coordinate_frame=geometry['coordinate_frame'] if geometry else None,
            docai_lines=docai,docai_symbol_custody=custody,median_counted_line_height=median,geometry_error=error,
            detected_languages=languages,page_script=script,records=rows)
        path=OUT/'assignments'/(p['id']+'.json')
        if write:atomic(path,assignment)
        else:assert assignment==json.loads(path.read_text()),p['id']
        records.extend(rows)
        audits.append(dict(page_id=p['id'],book_key=p['key'],**script,detected_languages=languages,
            **cohort_summary([p],rows),empty=not doc.get('text','').strip(),no_line_layouts=not page.get('lines'),
            lost_page=error is not None,geometry_error=error,receipt=receipt))
        if i%100==0:print(f'records {i}/{len(plan["pages"])}',flush=True)
    return records,dict(schema='t26-reads-1',overall=cohort_summary(plan['pages'],records),pages=audits,
        empty_pages=sum(p['empty'] for p in audits),no_line_pages=sum(p['no_line_layouts'] for p in audits),
        lost_pages=sum(p['lost_page'] for p in audits))


def old_records():
    return [r for wave in PRIOR_WAVES for r in read_jsonl(REPO/f'docs/harvest/{wave}/admitted.jsonl')]


def admit_records(records,held,old):
    quality=admission.page_quality(records);splits={b['book_key']:b['split'] for b in held}
    kept,rejected=[],[]
    for r in records:
        good,cls,reasons,label=policy.admit(r,quality[r['page_id']],r)
        if not good:
            rejected.append(dict(id=r['id'],reasons=reasons,docai_text=r['docai_text']));continue
        fields=('id','page_id','book_key','year','decade','confidence','bbox','source','licence','source_url','attribution','read_batch','docai_text')
        kept.append(dict({k:r[k] for k in fields},split=splits.get(r['book_key'],'train'),script_class=cls,label=label,
            has_spacing_mark=admission.has_spacing_mark(label)))
    count=len(kept);ids={r['id'] for r in kept}
    kept,o5=admission.apply_holdout_labels(kept+[dict(r) for r in old if r['split'] in ('test','dev')])
    kept=[r for r in kept if r['id'] in ids];rejected.extend(o5)
    labels={admission.normalize_label(r['label']) for r in kept+old if r['split'] in ('dev','test')}
    exclusions=[dict(id=r['id'],source=r['source'],reason='label_in_holdout',label=r['label']) for r in old
        if r['split']=='train' and admission.normalize_label(r['label']) in labels]
    return kept,sorted(rejected,key=lambda r:r['id']),quality,count,exclusions


def compiled_path(page):
    return Path(f"{page['year']}_{compiler.slug(page['title']) or 'untitled'}_{page['key'][:6]}")/f"p{page['page']:04d}.jpg"


def render_compiled(image,rows,quality,script):
    canvas,layout=compiler.render_page(image,rows)
    reasons=(['bad_page'] if quality.get('bad_page') else [])+(['not_cyrillic_page'] if script['not_cyrillic_page'] else [])
    if reasons:ImageDraw.Draw(canvas).text((40,8),'REJECTED: '+', '.join(reasons),font=compiler.number_font(),fill=compiler.RED)
    layout.update(rejection_reasons=reasons)
    return canvas,layout


def compile_task(task):
    p,rows,q,script=task
    with Image.open(REPO/p['image']) as image:canvas,layout=render_compiled(image,rows,q,script)
    path=BULK/'compiled'/compiled_path(p);path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path,'JPEG',quality=85)
    return dict(page_id=p['id'],path=str(compiled_path(p)),jpeg_sha256=sha(path),
        raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(),**layout)


def share_report(audits):
    values=[p['cyrillic_share'] for p in audits if p['cyrillic_share'] is not None]
    return dict(definition='Cyrillic letters / all Unicode category-L letters in full Document AI document.text; no line filtering. Empty pages fail; exactly 70% passes.',
        distribution=distribution(values),empty_denominators=sum(p['letters']==0 for p in audits),
        rejected_pages=sum(p['not_cyrillic_page'] for p in audits),pages=[{k:p[k] for k in
            ('page_id','book_key','letters','cyrillic_letters','cyrillic_share','not_cyrillic_page','detected_languages')} for p in audits])


def build(plan):
    # Lossless compression removes redundant embedded input PNG copies, retaining exact raw reconstruction.
    archive.compact(GOOGLE,image_paths={p['image_sha256']:REPO/p['image'] for p in plan['pages']})
    records,reads=read_records(plan,write=True)
    write_jsonl(OUT/'records.jsonl',records);atomic(OUT/'read_summary.json',reads)
    held=json.loads((OUT/'holdout_books.json').read_text());old=old_records()
    admitted,rejected,quality,before,exclusions=admit_records(records,held,old)
    admitted,crej,failures,geometries=previous.plan_crops(records,admitted,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    rejected=sorted(rejected+crej,key=lambda r:r['id']);atomic(OUT/'crop_failures.json',failures)
    groups=defaultdict(list);kept={r['id']:r for r in admitted}
    for r in records:groups[r['page_id']].append(r)
    for i,(pid,rows) in enumerate(groups.items(),1):
        assert sha(REPO/rows[0]['image'])==rows[0]['image_sha256']
        with Image.open(REPO/rows[0]['image']) as image:
            assert image.mode=='L';image.load()
            for r in rows:
                if r['id'] not in kept:continue
                a=kept[r['id']];bounds,trimmed=geometries[r['id']];crop=image.crop(tuple(bounds))
                path=BULK/'crops'/r['book_key'][:8]/f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                path.parent.mkdir(parents=True,exist_ok=True)
                buf=io.BytesIO();crop.save(buf,format='PNG',compress_level=3);data=buf.getvalue();digest=hashlib.sha256(data).hexdigest()
                if not path.exists() or sha(path)!=digest:path.write_bytes(data)
                a.update(crop_path=relative(path),crop_sha256=digest,crop_width=crop.width,crop_height=crop.height,crop_bbox=bounds,trimmed=trimmed)
                a.pop('docai_text')
        if i%100==0:print(f'crops {i}/{len(groups)}',flush=True)
    sheets=contact_sheets(REPO,admitted,BULK/'admission_sheet')
    reasons=Counter(reason for r in rejected for reason in r['reasons'])
    books=json.loads((OUT/'books.json').read_text())
    per_item={b['key']:dict(book=b['book'],lines=sum(r['book_key']==b['key'] for r in records),
        admitted=sum(r['book_key']==b['key'] for r in admitted),per_class_split={c:{s:sum(r['book_key']==b['key'] and r['script_class']==c and r['split']==s for r in admitted)
        for s in ('train','dev','test')} for c in admission.CLASSES}) for b in books}
    summary=dict(schema='t26-admission-1',items=len(books),pages=len(plan['pages']),input_lines=len(records),admitted_before_o5=before,
        admitted=len(admitted),rejected=len(rejected),crops=len(admitted),trimmed=sum(r['trimmed'] for r in admitted),
        has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),per_reason={reason:reasons[reason] for reason in REASONS},
        per_split={s:sum(r['split']==s for r in admitted) for s in ('train','dev','test')},
        per_class={c:sum(r['script_class']==c for r in admitted) for c in admission.CLASSES},
        per_class_split={c:{s:sum(r['script_class']==c and r['split']==s for r in admitted) for s in ('train','dev','test')} for c in admission.CLASSES},
        per_item=per_item,label_in_holdout=reasons['label_in_holdout'],previous_train_label_exclusions=len(exclusions),
        bad_pages=[dict(page_id=pid,**q) for pid,q in quality.items() if q['bad_page']],
        not_cyrillic_pages=[p['page_id'] for p in reads['pages'] if p['not_cyrillic_page']],
        crop_failures=len(failures),contact_sheets=sheets,crop_size_stats={k:stats([r['crop_'+k] for r in admitted]) for k in ('width','height')},
        admission_module_sha256=ADMISSION_SHA)
    for stem,rows in [('admitted',admitted),('rejected',rejected),('prior_train_exclusions',exclusions)]:write_jsonl(OUT/(stem+'.jsonl'),rows)
    atomic(OUT/'admission_summary.json',summary);atomic(OUT/'cyrillic_share.json',share_report(reads['pages']))
    # Carry prior O5/source-cap exclusions forward in a minimal combined training overlay.
    prior_pool=read_jsonl(_data_input(REPO/'docs/records/harvest/mixed/train_pool.jsonl'));excluded={r['id'] for r in exclusions}
    pool=[r for r in prior_pool if r['id'] not in excluded]
    fields=('id','source','script_class','label','crop_path','crop_sha256','book_key','read_batch','licence','split')
    pool.extend(dict({k:r[k] for k in fields},admission_record_file='docs/records/harvest/cyrillic/admitted.jsonl') for r in admitted if r['split']=='train')
    write_jsonl(OUT/'train_pool.jsonl',pool)
    audits={p['page_id']:p for p in reads['pages']}
    tasks=[(p,groups[p['id']],quality.get(p['id'],{}),audits[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as workers:
        entries=[]
        for i,entry in enumerate(workers.map(compile_task,tasks,chunksize=1),1):
            entries.append(entry)
            if i%100==0:print(f'compiled {i}/{len(tasks)}',flush=True)
    atomic(BULK/'compiled/compile_receipt.json',dict(schema='t26-compiled-1',pages=entries,page_count=len(entries),
        builder_sha256=sha(Path(__file__)),base_builder_sha256=sha(Path(compiler.__file__)),records_sha256=sha(_data_input(OUT/'records.jsonl'))))
    (BULK/'compiled/README.txt').write_text(compiler.README+'Red headings mark bad_page and/or not_cyrillic_page exclusions. No owner Cyrillic transcription review is available.\n')
    print(json.dumps(dict(lines=len(records),admitted=len(admitted),compiled=len(entries))),flush=True)


def validate_compiled(task):
    p,rows,q,script,entry=task
    assert entry['path']==str(compiled_path(p))
    with Image.open(REPO/p['image']) as image:canvas,layout=render_compiled(image,rows,q,script)
    assert hashlib.sha256(canvas.tobytes()).hexdigest()==entry['raster_sha256']
    assert all(entry[k]==v for k,v in layout.items())
    path=BULK/'compiled'/entry['path'];assert sha(path)==entry['jpeg_sha256']
    with Image.open(path) as image:assert image.size==canvas.size
    return p['id']


def validate(plan):
    books=json.loads((OUT/'books.json').read_text());sources=json.loads((OUT/'source_books.json').read_text())
    held=json.loads((OUT/'holdout_books.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    assert len(books)==13 and held==policy.holdout(sources)
    assert Counter(r['split'] for r in held)=={'test':2,'dev':1}
    assert len({b['key'][:8] for b in books})==13
    for b in books:
        assert b['positions']==policy.sample(b['pages'],b['book'])
        assert b['pdf_bytes']<=policy.MAX_BYTES
    gates={f"{p['key']}:{p['page']}":p for p in manifest}
    slots,_=round2.replay_slots(books,gates,json.loads((OUT/'fetch_failures.json').read_text()))
    assert slots==json.loads((OUT/'slots.json').read_text())
    chosen={(s['key'],s['accepted_page']) for s in slots if s['accepted_page'] is not None}
    assert chosen=={(p['key'],p['page']) for p in plan['pages']}
    limits=plan['quality_limits']
    for p in manifest:
        with Image.open(REPO/p['image']) as image:assert image.mode=='L' and image.size==(p['width'],p['height'])
        assert sha(REPO/p['image'])==p['image_sha256']==p['gate']['image_sha256']
        g=p['gate'];assert g['gate_source_sha256']==round1.GATE_SHA
        flags,ratio=round1.quality_flags(g['features'],Counter(g['suppression_reasons']),g['lines'],limits)
        assert g['supplemental_quality_flags']==flags and g['faint_suppression_share']==ratio
        assert p['harvest_accepted']==(g['pilot_gate']['accepted'] and not flags)
        assert not p['harvest_accepted'] or 'more_than_two_columns' not in g['flags']
    records,reads=read_records(plan);assert records==read_jsonl(_data_input(OUT/'records.jsonl'))
    assert reads==json.loads((OUT/'read_summary.json').read_text())
    old=old_records();expected,rejected,quality,before,exclusions=admit_records(records,held,old)
    expected,crej,failures,geometry=previous.plan_crops(records,expected,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    rejected=sorted(rejected+crej,key=lambda r:r['id']);actual=read_jsonl(_data_input(OUT/'admitted.jsonl'))
    assert rejected==read_jsonl(_data_input(OUT/'rejected.jsonl')) and exclusions==read_jsonl(OUT/'prior_train_exclusions.jsonl')
    assert {r['id'] for r in expected}=={r['id'] for r in actual}
    assert len(actual)+len(rejected)==len(records)
    amap={r['id']:r for r in actual};groups=defaultdict(list)
    for r in records:groups[r['page_id']].append(r)
    for expected_row in expected:
        a=amap[expected_row['id']]
        assert all(a[k]==v for k,v in expected_row.items() if k!='docai_text')
    checked=0
    for pid,rows in groups.items():
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            for r in rows:
                if r['id'] not in amap:continue
                a=amap[r['id']];bounds,trimmed=geometry[r['id']]
                assert not r['not_cyrillic_page']
                assert bounds==a['crop_bbox'] and trimmed==a['trimmed'] and sha(REPO/a['crop_path'])==a['crop_sha256']
                assert a['crop_path']==relative(BULK/'crops'/r['book_key'][:8]/f"p{r['page']:06d}-l{r['line_number']:04d}.png")
                with Image.open(REPO/a['crop_path']) as crop:
                    assert crop.mode=='L' and crop.size==(a['crop_width'],a['crop_height']) and crop.tobytes()==image.crop(tuple(bounds)).tobytes()
                checked+=1
    summary=json.loads((OUT/'admission_summary.json').read_text())
    assert checked==summary['crops']==summary['admitted']==len(actual)
    assert summary['per_reason']=={reason:sum(reason in r['reasons'] for r in rejected) for reason in REASONS}
    assert summary['per_class_split']=={c:{s:sum(r['script_class']==c and r['split']==s for r in actual) for s in ('train','dev','test')} for c in admission.CLASSES}
    assert json.loads((OUT/'cyrillic_share.json').read_text())==share_report(reads['pages'])
    pool=read_jsonl(_data_input(OUT/'train_pool.jsonl'));labels={admission.normalize_label(r['label']) for r in old+actual if r['split'] in ('test','dev')}
    assert not any(admission.normalize_label(r['label']) in labels for r in pool)
    compiled=json.loads((BULK/'compiled/compile_receipt.json').read_text());assert compiled['page_count']==len(plan['pages'])
    assert compiled['builder_sha256']==sha(Path(__file__)) and compiled['base_builder_sha256']==sha(Path(compiler.__file__))
    entries={e['page_id']:e for e in compiled['pages']};audits={p['page_id']:p for p in reads['pages']}
    tasks=[(p,groups[p['id']],quality.get(p['id'],{}),audits[p['id']],entries[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as workers:
        for _ in workers.map(validate_compiled,tasks,chunksize=1):pass
    for cls,s in summary['contact_sheets'].items():
        assert sha(REPO/s['path'])==s['sha256'] and len(set(s['ids']))==min(60,summary['per_class'][cls])
        assert all(amap[i]['script_class']==cls for i in s['ids'])
    ledger=read_jsonl(GOOGLE/'budget.jsonl');assert len({r['key'] for r in ledger})==len(ledger)==plan['max_calls']
    assert all(r['engine']=='docai' for r in ledger) and len(ledger)*1500<=1_200_000
    before_hashes={relative(p):sha(p) for p in (GOOGLE/'budget.jsonl',GOOGLE/'budget.state.json',GOOGLE/'docai/ledger.jsonl')}
    reader=CyrillicReaders(plan)
    def forbidden(*args,**kwargs):raise AssertionError('offline validation forbids provider')
    reader.docai.read=forbidden
    for p in plan['pages']:assert reader.call('docai',REPO/p['image'])['status']=='ok'
    assert before_hashes=={p:sha(REPO/p) for p in before_hashes}
    budget=reader.budget.receipt();cost=json.loads((OUT/'cost_receipt.json').read_text())
    assert cost['cost_usd']==budget['cost_usd']==len(ledger)*.0015
    assert sha(REPO/'greekocr/harvest/admission.py')==ADMISSION_SHA
    before=json.loads((OUT/'git_before.json').read_text());after=round1.git_snapshot()
    atomic(OUT/'git_audit.json',dict(unchanged=before==after,before=before,after=after,t26_git_write_operations=0))
    atomic(OUT/'resume_check.json',dict(pages_replayed=len(plan['pages']),provider_forbidden=True,new_calls=0,new_reservations=0,ledger_hashes=before_hashes))
    result=dict(passed=True,items=13,pages_rendered=len(manifest),pages_accepted=len(plan['pages']),pages_read=len(plan['pages']),lines=len(records),
        admitted=len(actual),native_pixels_checked=checked,compiled_rasters_replayed=len(tasks),holdout_items=3,
        train_holdout_equal_labels=0,not_cyrillic_pages=len(summary['not_cyrillic_pages']),no_vision=True,
        language_hints=[],cost_usd=budget['cost_usd'],git_unchanged=before==after,t26_git_write_operations=0)
    atomic(OUT/'validation.json',result);print(json.dumps(result),flush=True)


def test_count():
    suites=list(ET.parse(OUT/'tests.xml').getroot().iter('testsuite'))
    assert not sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in suites)
    return sum(int(s.get('tests',0))-int(s.get('skipped',0)) for s in suites)


def final_line(plan,s,tests,cost):
    c=s['per_class'];p=s['per_split']
    return (f"T26: done | items: {s['items']} | pages: {plan['pages_rendered']}/{plan['pages_accepted']}/{plan['page_count']} | "
        f"lines: {s['input_lines']} | admitted: {s['admitted']} | cyr: {c['cyrillic']} | latin: {c['latin']} | "
        f"train: {p['train']} | dev: {p['dev']} | test: {p['test']} | usd: {cost:.2f} | tests: {tests} passed")


def esc(text):return ' '.join(str(text).split()).replace('|','\\|')


def publish(plan):
    validation=json.loads((OUT/'validation.json').read_text());assert validation['passed']
    s=json.loads((OUT/'admission_summary.json').read_text());reads=json.loads((OUT/'read_summary.json').read_text())
    books=json.loads((OUT/'books.json').read_text());held=json.loads((OUT/'holdout_books.json').read_text())
    split={b['book_key']:b['split'] for b in held};tests=test_count();cost=json.loads((OUT/'cost_receipt.json').read_text())['cost_usd']
    line=final_line(plan,s,tests,cost)
    languages=Counter(l['languageCode'] for p in reads['pages'] for l in p['detected_languages'])
    primary=Counter((max(p['detected_languages'],key=lambda l:l.get('confidence',0))['languageCode'] if p['detected_languages'] else 'und') for p in reads['pages'])
    shares=json.loads((OUT/'cyrillic_share.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    report=['# T26 — Wave 6 Cyrillic scans','',
        f"**13 items; {plan['pages_rendered']} rendered / {plan['pages_accepted']} gate-accepted / {plan['page_count']} DocAI-read pages; "
        f"{s['input_lines']:,} lines; {s['admitted']:,} admitted native crops.** USD {cost:.4f} reserved list-price estimate, cap USD 1.20. {tests} offline tests passed.",'',
        'Seed 20266; 45 inclusive 8–95% anchors per item, seeded 0–2 offsets, and at most +1/+2 physical neighbours after failure. '
        'No replacement beyond those bounds. Gate and photometric thresholds are frozen T16; more_than_two_columns fails. '
        'All input candidates have verified-target-sample print review and source-declared public-domain or CC-BY rights. '
        'All selected PDFs were below 300 MB; no DjVu fallback was needed. PDFs were deleted after rendering; hashes, sizes and download receipts remain. '
        'Rendered PNGs are native 200-DPI grey. No raster cap or rescaling was introduced.','',
        'The owner cannot read Cyrillic. Quality rests on automatic gates; these are silver OCR labels, with no human transcription validation. '
        'The additional page gate rejects all lines when fewer than 70% of the letters in the complete DocAI page text are Cyrillic. '
        'Exactly 70% passes, and empty letter denominators fail. All pre-existing T20 rules, normalization, script classes, '
        'mixed-word rejection and crop geometry remain unchanged. A Cyrillic/Latin or Cyrillic/Greek mixed word drops the line.','',
        'DocAI uses the T21 processor/version/symbol binding with languageHints=[] (automatic detection), one whole-page request per unique PNG SHA. '
        'No Vision calls, crop requests, Google retries or Git writes. Budget reservations include failed/ambiguous attempts. '
        'Lossless raw gzip archives reference identical input PNGs and reconstruct the original response bytes and SHA.','',
        '| Item | Year (catalogue) | Licence | Split | Rendered | Accepted/read | Lines | Admitted |','|---|---:|---|---|---:|---:|---:|---:|']
    for b in books:
        pages=[p for p in plan['pages'] if p['key']==b['key']];item=s['per_item'][b['key']]
        report.append(f"| [{b['book']}]({b['source_url']}) | {b['year']} | {b['licence']} | {split.get(b['key'],'train')} | "
            f"{sum(p['key']==b['key'] for p in manifest)} | {len(pages)} | {item['lines']} | {item['admitted']} |")
    report+=['','Catalogue year/language and rights retain their upstream verification limits; specific editions and underlying rights were not re-adjudicated. '
        'Titles, creators, raw rights statements and print-review evidence are retained in books.json and selection.json.','',
        '| Class | Train | Dev | Test | Total |','|---|---:|---:|---:|---:|']
    for c,d in s['per_class_split'].items():report.append(f"| {c} | {d['train']} | {d['dev']} | {d['test']} | {sum(d.values())} |")
    report+=['','| Item | Class | Train | Dev | Test |','|---|---|---:|---:|---:|']
    for key,item in s['per_item'].items():
        for c,d in item['per_class_split'].items():
            report.append(f"| {item['book']} | {c} | {d['train']} | {d['dev']} | {d['test']} |")
    report+=['','Seed 20261015 selects exactly two whole items for test and one for dev before reads. '
        f"O5 drops {s['label_in_holdout']} new train lines equal to a normalized dev/test label across every wave. "
        f"{s['previous_train_label_exclusions']} prior train lines are excluded in the combined train_pool.jsonl overlay; earlier files remain frozen. "
        'The prior mixed-wave source-cap and O5 exclusions are carried forward.','',
        '| Detected language | Pages containing language | Highest-confidence language pages |','|---|---:|---:|']
    for lang in sorted(set(languages)|set(primary)):report.append(f"| {lang} | {languages[lang]} | {primary[lang]} |")
    report+=['','Multiple languages can occur on a page. Full codes/confidences are recorded per page in read_summary.json, assignments and records.','',
        'Cyrillic-share definition: '+shares['definition'],'',
        '| Pages | Min | P10 | P25 | Median | P75 | P90 | Max | Mean |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    d=shares['distribution'];report.append('| '+str(d['pages'])+' | '+' | '.join(f"{d[k]:.1%}" if d[k] is not None else '—' for k in ('min','p10','p25','median','p75','p90','max','mean'))+' |')
    report += ['',f"{shares['rejected_pages']} read pages fail not_cyrillic_page; {shares['empty_denominators']} empty letter denominators. "
        f"{len(s['bad_pages'])} bad_page exclusions; {s['crop_failures']} crop geometry failures. "
        f"Lost coordinate pages {reads['lost_pages']}; empty reads {reads['empty_pages']}; no-line reads {reads['no_line_pages']}.",'',
        '| Admission reason (overlapping line counts) | Lines |','|---|---:|']
    report += [f'| {r} | {n} |' for r,n in s['per_reason'].items()]
    report += ['','| Page gate / photometric reason (overlapping pages) | Pages |','|---|---:|']
    report += [f'| {r} | {n} |' for r,n in sorted(Counter(f for p in manifest for f in p['gate']['flags']).items())]
    requests=read_jsonl(BULK/'archive_http/requests.jsonl')
    network_errors=Counter(str(r.get('status') or r.get('error','transport')) for r in requests if r.get('error'))
    report += ['',f"Public IA HTTP requests: {len(requests)}; failures by status/error: {dict(network_errors)}. "
        'The source-level download resumed from completed item receipts after the transient failure; Google pages were not retried.','']
    report += ['',f"585 sampled slots; {585-plan['pages_accepted']} exhausted slots after bounded replacement. "
        f"Approximate target: 550 gate-accepted pages; actual {plan['pages_accepted']}; shortfall {max(0,550-plan['pages_accepted'])}. No threshold was relaxed. "
        'The script-page gate applies after paid reads and does not trigger additional requests.','',
        f"Native pixels of all {s['crops']} crops and all {plan['page_count']} compiled rasters were replayed. "
        'This verifies artifact fidelity and the automatic policy, not transcription accuracy or perfect glyph ownership. '
        'The 60 seeded Cyrillic crops and labels are in harvest_big/cyrillic/admission_sheet/cyrillic.jpg. '
        'Compiled pages with rejected page rules show red rejection headings.','',
        '[Records](records.jsonl), [summary](admission_summary.json), [hold-outs](holdout_books.json), [page shares](cyrillic_share.json), '
        '[validation](validation.json), [tests](tests.xml), [cost](cost_receipt.json), [inventory](inventory.json).','',line]
    (OUT/'READS.md').write_text('\n'.join(report)+'\n')
    statepath=REPO/'docs/records/harvest/collection/EXECUTION_STATE.md';state=statepath.read_text()
    now=datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    start=datetime.fromisoformat(json.loads((OUT/'run_state.json').read_text())['started_at']).astimezone(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    old=next(l for l in state.splitlines() if l.startswith('| 6 Cyrillic |'))
    status='complete' if plan['pages_accepted']>=550 else 'complete (bounded page shortfall)'
    state=state.replace(old,f"| 6 Cyrillic | T26 | {status} | {start} | {now} | {plan['pages_rendered']} / {plan['pages_accepted']} / {plan['page_count']} | {s['admitted']} | {cost:.4f} |")
    section=f"## Wave 6\n\nT26 completed {now} Athens: 13 IA items; {plan['pages_rendered']} rendered / {plan['pages_accepted']} accepted / {plan['page_count']} read pages; "
    section+=f"{s['input_lines']} DocAI lines, {s['admitted']} native crops; {s['per_class']['cyrillic']} Cyrillic and {s['per_class']['latin']} Latin. "
    section+=f"Train {s['per_split']['train']} / dev {s['per_split']['dev']} / test {s['per_split']['test']}; two test items and one dev, seed 20261015. "
    section+=f"USD {cost:.4f} (cap 1.20); {tests} offline tests. {shares['rejected_pages']} read pages dropped by <70% Cyrillic; language detection has no hints. "
    section+='T20 unchanged; automatic checks only, no owner Cyrillic transcription validation; zero Vision calls and Git writes. '
    section+=f"Approximately 550 accepted pages requested; bounded shortfall {max(0,550-plan['pages_accepted'])}.\n\n"
    section+='[Report](../cyrillic/READS.md), [validation](../cyrillic/validation.json), [inventory](../cyrillic/inventory.json).\n\n'+line+'\n'
    if '\n## Wave 6\n' in state:
        prefix,tail=state.split('\n## Wave 6\n',1);idx=tail.find('\n## ')
        state=prefix.rstrip()+'\n\n'+section+(tail[idx:] if idx>=0 else '')
    else:state=state.rstrip()+'\n\n'+section
    statepath.write_text(state)
    inventory=REPO/'docs/INVENTORY.md';text=inventory.read_text();marker='## T26 — Wave 6 Cyrillic collection'
    item=f"{marker}\n\n13 Internet Archive items; {plan['page_count']} DocAI-read pages; {s['admitted']} admitted crops. "
    item+='[Policy](../greekocr/harvest/cyrillic.py), [runner](../scripts/harvest/cyrillic.py), [outputs/validation](../scripts/harvest/cyrillic_outputs.py), [tests](../tests/test_cyrillic.py). '
    item+='[Report](harvest/cyrillic/READS.md), [records](harvest/cyrillic/records.jsonl), [summary](harvest/cyrillic/admission_summary.json), [hold-outs](harvest/cyrillic/holdout_books.json), '
    item+='[validation](harvest/cyrillic/validation.json), [inventory](harvest/cyrillic/inventory.json). Bulk PNGs, compressed raw responses, native crops, compiled JPEGs and class sheets remain ignored under harvest_big/cyrillic.\n'
    if marker not in text:inventory.write_text(text.rstrip()+'\n\n'+item)
    paths=[p for p in OUT.rglob('*') if p.is_file() and p.name!='inventory.json']
    paths += [REPO/n for n in ('greekocr/harvest/cyrillic.py','scripts/harvest/cyrillic.py','scripts/harvest/cyrillic_outputs.py','tests/test_cyrillic.py')]
    bulk=[p for p in BULK.rglob('*') if p.is_file()]
    atomic(OUT/'inventory.json',dict(schema='t26-inventory-1',files=[dict(path=relative(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(paths+bulk))],
        bulk=relative(BULK),bulk_files=len(bulk),crops=s['crops'],compiled_pages=plan['page_count']))
    print(line,flush=True)
