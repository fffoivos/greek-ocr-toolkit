"""Offline T24c records, unchanged T20 admission, crops, compilation and audit."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit
from PIL import Image,ImageDraw
from greekocr.harvest import admission
from greekocr.harvest.page_reads import _response_geometry
from scripts.harvest.openarchives import (REPO,OUT,BULK,GOOGLE,CAP,ADMISSION_SHA,PRIOR_WAVES,
    sha,relative,atomic,read_jsonl,policy,vouli,round1,git_snapshot,disk_check,OpenArchivesReaders)
from scripts.harvest import vouli_outputs as previous
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest.admit_round1 import contact_sheets,stats,write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows,cohort_summary

REASONS=admission.REASONS+('crop_geometry',)


def raw_read(page,plan):
    parsed_path=GOOGLE/'parsed/docai'/(page['image_sha256']+'.json')
    parsed=json.loads(parsed_path.read_text())
    if parsed['status']!='ok':return None,dict(status=parsed['status'],error_class=parsed.get('error_class'))
    assert parsed['binding']==plan['binding'] and parsed['image_sha256']==sha(REPO/page['image'])
    path=Path(parsed['raw_json_path']);cache_path=path.parent/'cache.json';cache=json.loads(cache_path.read_text())
    assert sha(path)==cache['raw_sha256'] and cache['crop_sha256']==page['image_sha256']
    assert cache['binding']==plan['binding'] and cache['receipt_id']==parsed['receipt_id']
    raw=json.loads(path.read_text());assert raw['content_stripped']
    assert all('content' not in p.get('image',{}) for p in raw['document']['pages'])
    return raw,dict(status='ok',receipt_id=parsed['receipt_id'],raw_json_path=relative(path),raw_sha256=sha(path),
        cache_path=relative(cache_path),cache_sha256=sha(cache_path),parsed_path=relative(parsed_path),parsed_sha256=sha(parsed_path))


def read_records(plan,write=False):
    records,audits=[],[]
    for i,p in enumerate(plan['pages'],1):
        raw,receipt=raw_read(p,plan);geometry=None;rows=[];docai=[];custody=[];median=None;error=None
        if raw is not None:
            try:
                geometry=_response_geometry('docai',raw,(p['width'],p['height']))
                rows,docai,custody,median=make_rows(p,raw['document'],geometry)
            except ValueError as e:error=str(e)
        else:error='provider_read_failure'
        for r in rows:
            r.update(**{k:p[k] for k in ('source','licence','source_url','attribution','collection_slug')},read_batch='openarchives')
        assignment=dict(schema='t24c-assignment-1',page=p,reader=receipt,
            coordinate_frame=geometry['coordinate_frame'] if geometry else None,docai_lines=docai,
            docai_symbol_custody=custody,median_counted_line_height=median,geometry_error=error,records=rows)
        path=OUT/'assignments'/(p['id']+'.json')
        if write:disk_check();atomic(path,assignment)
        else:assert assignment==json.loads(path.read_text()),p['id']
        records.extend(rows)
        audits.append(dict(page_id=p['id'],book_key=p['key'],**cohort_summary([p],rows),
            read_ok=raw is not None,empty=raw is not None and not raw['document'].get('text','').strip(),
            no_line_layouts=raw is not None and not raw['document']['pages'][0].get('lines'),
            lost_page=error is not None,geometry_error=error,receipt=receipt))
        if i%100==0:print(f'records {i}/{len(plan["pages"])}',flush=True)
    return records,dict(schema='t24c-reads-1',overall=cohort_summary(plan['pages'],records),pages=audits,
        pages_read=sum(p['read_ok'] for p in audits),empty_pages=sum(p['empty'] for p in audits),
        lost_pages=sum(p['lost_page'] for p in audits),no_line_pages=sum(bool(p['no_line_layouts']) for p in audits))


def old_records():
    return [r for wave in PRIOR_WAVES for r in read_jsonl(REPO/f'docs/records/harvest/{wave}/admitted.jsonl')]


def admit_records(records,held,old):
    quality=admission.page_quality(records);splits={b['book_key']:b['split'] for b in held};kept=[];rejected=[]
    for r in records:
        good,cls,reasons,label=admission.admit(dict(r,bad_page=quality[r['page_id']]['bad_page']))
        if not good:rejected.append(dict(id=r['id'],reasons=reasons,docai_text=r['docai_text']));continue
        fields=('id','page_id','book_key','year','decade','confidence','bbox','source','licence','source_url','attribution','read_batch','collection_slug','docai_text')
        kept.append(dict({k:r[k] for k in fields},split=splits.get(r['book_key'],'train'),script_class=cls,
            label=label,has_spacing_mark=admission.has_spacing_mark(label)))
    count=len(kept);ids={r['id'] for r in kept}
    kept,o5=admission.apply_holdout_labels(kept+[dict(r) for r in old if r['split'] in ('dev','test')])
    kept=[r for r in kept if r['id'] in ids];rejected.extend(o5)
    labels={admission.normalize_label(r['label']) for r in kept+old if r['split'] in ('dev','test')}
    exclusions=[dict(id=r['id'],source=r['source'],reason='label_in_holdout',label=r['label']) for r in old
        if r['split']=='train' and admission.normalize_label(r['label']) in labels]
    return kept,sorted(rejected,key=lambda r:r['id']),quality,count,exclusions


def compiled_path(p):
    title=compiler.slug(p['title']) or 'untitled';year=p['year'] if p['year'] is not None else 'unknown'
    return Path(p['collection_slug'])/f"{year}_{title}_{p['key'][:6]}"/f"p{p['page']:04d}.jpg"


def render_compiled(image,rows,quality):
    canvas,layout=compiler.render_page(image,rows)
    if quality.get('bad_page'):ImageDraw.Draw(canvas).text((40,8),'REJECTED: bad_page',font=compiler.number_font(),fill=compiler.RED)
    layout['bad_page']=bool(quality.get('bad_page'));return canvas,layout


def compile_task(task):
    disk_check();p,rows,q=task
    with Image.open(REPO/p['image']) as image:canvas,layout=render_compiled(image,rows,q)
    path=BULK/'compiled'/compiled_path(p);path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,'JPEG',quality=85)
    return dict(page_id=p['id'],path=str(compiled_path(p)),jpeg_sha256=sha(path),raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(),**layout)


def build(plan):
    records,reads=read_records(plan,write=True)
    write_jsonl(OUT/'records.jsonl',records);atomic(OUT/'read_summary.json',reads)
    held=json.loads((OUT/'holdout_books.json').read_text());old=old_records()
    admitted,rejected,quality,before,exclusions=admit_records(records,held,old)
    admitted,crej,failures,geometry=previous.plan_crops(records,admitted,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    rejected=sorted(rejected+crej,key=lambda r:r['id']);atomic(OUT/'crop_failures.json',failures)
    groups=defaultdict(list);kept={r['id']:r for r in admitted}
    for r in records:groups[r['page_id']].append(r)
    for i,(pid,rows) in enumerate(groups.items(),1):
        disk_check();assert sha(REPO/rows[0]['image'])==rows[0]['image_sha256']
        with Image.open(REPO/rows[0]['image']) as image:
            assert image.mode=='L';image.load()
            for r in rows:
                if r['id'] not in kept:continue
                a=kept[r['id']];bounds,trimmed=geometry[r['id']];crop=image.crop(tuple(bounds))
                path=BULK/'crops'/r['book_key']/f"p{r['page']:06d}-l{r['line_number']:04d}.png";path.parent.mkdir(parents=True,exist_ok=True)
                buf=io.BytesIO();crop.save(buf,format='PNG',compress_level=6);data=buf.getvalue();digest=hashlib.sha256(data).hexdigest()
                if not path.exists() or sha(path)!=digest:path.write_bytes(data)
                a.update(crop_path=relative(path),crop_sha256=digest,crop_width=crop.width,crop_height=crop.height,crop_bbox=bounds,trimmed=trimmed)
                a.pop('docai_text')
        if i%100==0:print(f'crops {i}/{len(groups)}',flush=True)
    sheets=contact_sheets(REPO,admitted,BULK/'admission_sheet');reasons=Counter(reason for r in rejected for reason in r['reasons'])
    book_rows=json.loads((OUT/'books.json').read_text())
    per_repo={repo:{c:{s:sum(r['collection_slug']==repo and r['script_class']==c and r['split']==s for r in admitted)
        for s in ('train','dev','test')} for c in admission.CLASSES} for repo in sorted({b['collection_slug'] for b in book_rows})}
    outcomes=Counter(r['outcome'] for r in json.loads((_data_input(OUT/'acquisition_results.json')).read_text()))
    summary=dict(schema='t24c-admission-1',documents=len(book_rows),pages=len(plan['pages']),
        documents_tried=sum(outcomes.values()),documents_downloaded=outcomes['downloaded'],dead_links=outcomes['dead_link'],skipped_size=outcomes['skipped_size'],
        pages_rendered=plan['pages_rendered'],pages_accepted=plan['pages_accepted'],pages_read=reads['pages_read'],
        input_lines=len(records),admitted_before_o5=before,admitted=len(admitted),rejected=len(rejected),crops=len(admitted),
        trimmed=sum(r['trimmed'] for r in admitted),has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),
        per_reason={reason:reasons[reason] for reason in REASONS},per_split={s:sum(r['split']==s for r in admitted) for s in ('train','dev','test')},
        per_class={c:sum(r['script_class']==c for r in admitted) for c in admission.CLASSES},
        per_class_split={c:{s:sum(r['script_class']==c and r['split']==s for r in admitted) for s in ('train','dev','test')} for c in admission.CLASSES},
        per_repository_class_split=per_repo,label_in_holdout=reasons['label_in_holdout'],previous_train_label_exclusions=len(exclusions),
        bad_pages=[dict(page_id=pid,**q) for pid,q in quality.items() if q['bad_page']],crop_failures=len(failures),
        contact_sheets=sheets,crop_size_stats={k:stats([r['crop_'+k] for r in admitted]) for k in ('width','height')},admission_module_sha256=ADMISSION_SHA)
    for name,rows in [('admitted',admitted),('rejected',rejected),('prior_train_exclusions',exclusions)]:write_jsonl(OUT/(name+'.jsonl'),rows)
    atomic(OUT/'admission_summary.json',summary)
    # Preserve existing source-cap policies and add reverse O5 exclusions.
    prior_pool=read_jsonl(_data_input(REPO/'docs/records/harvest/cyrillic/train_pool.jsonl'));excluded={r['id'] for r in exclusions}
    train=[r for r in prior_pool if r['id'] not in excluded]
    fields=('id','source','script_class','label','crop_path','crop_sha256','book_key','read_batch','licence','split')
    train.extend(dict({k:r[k] for k in fields},admission_record_file='docs/records/harvest/openarchives/admitted.jsonl') for r in admitted if r['split']=='train')
    write_jsonl(OUT/'train_pool.jsonl',train)
    tasks=[(p,groups[p['id']],quality.get(p['id'],{})) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
        entries=[]
        for i,entry in enumerate(pool.map(compile_task,tasks,chunksize=1),1):
            entries.append(entry)
            if i%100==0:print(f'compiled {i}/{len(tasks)}',flush=True)
    atomic(BULK/'compiled/compile_receipt.json',dict(schema='t24c-compiled-1',pages=entries,page_count=len(entries),builder_sha256=sha(Path(__file__)),base_builder_sha256=sha(Path(compiler.__file__)),records_sha256=sha(_data_input(OUT/'records.jsonl'))))
    (BULK/'compiled/README.txt').write_text(compiler.README+'Red headings identify bad_page admission exclusions. Repository and title/year are pipeline metadata, not independently verified PDF identity.\n')
    print(json.dumps(dict(lines=len(records),admitted=len(admitted),compiled=len(entries))),flush=True)


def validate_compiled(task):
    p,rows,q,entry=task
    assert entry['path']==str(compiled_path(p))
    with Image.open(REPO/p['image']) as image:canvas,layout=render_compiled(image,rows,q)
    assert hashlib.sha256(canvas.tobytes()).hexdigest()==entry['raster_sha256']
    assert all(entry[k]==v for k,v in layout.items());path=BULK/'compiled'/entry['path'];assert sha(path)==entry['jpeg_sha256']
    with Image.open(path) as im:assert im.size==canvas.size


def validate(plan):
    books=json.loads((OUT/'books.json').read_text());held=json.loads((OUT/'holdout_books.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    config=json.loads((OUT/'selection_config.json').read_text())
    assert len({b['key'] for b in books})==len(books) and len(books)<=130
    assert max(Counter(b['collection_slug'] for b in books).values())<=config['cap_used']
    assert held==policy.holdout(books) and Counter(r['split'] for r in held)=={'test':15,'dev':5}
    assert not list((BULK/'pdf').glob('*.pdf')) and not list((BULK/'pdf').glob('*.part'))
    for b in books:
        assert b['pdf_bytes']<=policy.MAX_PDF
        receipt=json.loads((BULK/'pdf_receipts'/(b['key']+'.retention.json')).read_text())
        assert receipt==dict(sha256=b['pdf_sha256'],bytes=b['pdf_bytes'],page_count=b['page_count'],deleted=True)
    slots=json.loads((OUT/'slots.json').read_text());assert len(slots)==12*len(books)
    assert all(len(s['attempts'])<=3 for s in slots)
    assert {(s['key'],s['accepted_page']) for s in slots if s['accepted_page'] is not None}=={(p['key'],p['page']) for p in plan['pages']}
    for p in manifest:
        with Image.open(REPO/p['image']) as im:assert im.mode=='L' and im.size==(p['width'],p['height']) and max(im.size)<=3500
        assert p['image_sha256']==sha(REPO/p['image'])==p['gate']['image_sha256']
        assert p['coordinate_frame']=='rendered PNG' and 0<p['render_scale_factor']<=1
        g=p['gate'];assert g['gate_source_sha256']==round1.GATE_SHA
        flags,ratio=round1.quality_flags(g['features'],Counter(g['suppression_reasons']),g['lines'],plan['quality_limits'])
        assert flags==g['supplemental_quality_flags'] and ratio==g['faint_suppression_share']
        assert p['harvest_accepted']==(g['pilot_gate']['accepted'] and not flags)
    records,reads=read_records(plan);assert records==read_jsonl(_data_input(OUT/'records.jsonl')) and reads==json.loads((OUT/'read_summary.json').read_text())
    old=old_records();expected,rejected,quality,before,exclusions=admit_records(records,held,old)
    expected,crej,failures,geometry=previous.plan_crops(records,expected,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    actual=read_jsonl(_data_input(OUT/'admitted.jsonl'));amap={r['id']:r for r in actual}
    assert sorted(rejected+crej,key=lambda r:r['id'])==read_jsonl(OUT/'rejected.jsonl')
    assert exclusions==read_jsonl(OUT/'prior_train_exclusions.jsonl')
    assert {r['id'] for r in expected}==set(amap) and len(actual)+len(rejected)+len(crej)==len(records)
    for r in expected:assert all(amap[r['id']][k]==v for k,v in r.items() if k!='docai_text')
    groups=defaultdict(list)
    for r in records:groups[r['page_id']].append(r)
    checked=0
    for rows in groups.values():
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            for r in rows:
                if r['id'] not in amap:continue
                a=amap[r['id']];bounds,trimmed=geometry[r['id']]
                assert a['crop_bbox']==bounds and a['trimmed']==trimmed and sha(REPO/a['crop_path'])==a['crop_sha256']
                assert a['crop_path']==relative(BULK/'crops'/r['book_key']/f"p{r['page']:06d}-l{r['line_number']:04d}.png")
                with Image.open(REPO/a['crop_path']) as crop:
                    assert crop.mode=='L' and crop.size==(a['crop_width'],a['crop_height']) and crop.tobytes()==image.crop(tuple(bounds)).tobytes()
                checked+=1
    summary=json.loads((OUT/'admission_summary.json').read_text());assert checked==summary['crops']==summary['admitted']==len(actual)
    labels={admission.normalize_label(r['label']) for r in old+actual if r['split'] in ('dev','test')}
    assert not any(admission.normalize_label(r['label']) in labels for r in read_jsonl(_data_input(OUT/'train_pool.jsonl')))
    entries=json.loads((BULK/'compiled/compile_receipt.json').read_text());assert entries['page_count']==len(plan['pages'])
    emap={e['page_id']:e for e in entries['pages']}
    tasks=[(p,groups[p['id']],quality.get(p['id'],{}),emap[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
        for _ in pool.map(validate_compiled,tasks,chunksize=1):pass
    for cls,s in summary['contact_sheets'].items():
        assert sha(REPO/s['path'])==s['sha256'] and len(set(s['ids']))==min(60,summary['per_class'][cls])
        assert all(amap[i]['script_class']==cls for i in s['ids'])
    ledger=read_jsonl(GOOGLE/'budget.jsonl');assert len({r['key'] for r in ledger})==len(ledger)==plan['max_calls']
    assert all(r['engine']=='docai' for r in ledger) and len(ledger)*1500<=3_000_000
    paths=[GOOGLE/'budget.jsonl',GOOGLE/'budget.state.json',GOOGLE/'docai/ledger.jsonl'];hashes={relative(p):sha(p) for p in paths}
    readers=OpenArchivesReaders(plan)
    def forbidden(*args,**kwargs):raise AssertionError('no provider in offline validation')
    readers.docai.read=forbidden
    for p in plan['pages']:assert readers.call('docai',REPO/p['image'])['status']=='ok'
    assert hashes=={relative(p):sha(p) for p in paths}
    assert readers.budget.receipt()['cost_usd']==json.loads((OUT/'cost_receipt.json').read_text())['cost_usd']
    for p,v in config['inputs'].items():assert sha(REPO/p)==v['sha256']
    assert sha(REPO/'greekocr/harvest/admission.py')==ADMISSION_SHA
    requests_log=read_jsonl(BULK/'http/requests.jsonl');hosts=defaultdict(list)
    for r in requests_log:hosts[r['host']].append(r['started'])
    gaps=[b-a for starts in hosts.values() for a,b in zip(starts,starts[1:])];assert not gaps or min(gaps)>=1
    before=json.loads((OUT/'git_before_t24c.json').read_text());after=git_snapshot()
    atomic(OUT/'git_audit.json',dict(unchanged=before==after,before=before,after=after,t24c_git_write_operations=0))
    result=dict(passed=True,documents=len(books),pages_rendered=len(manifest),pages_accepted=len(plan['pages']),pages_read=reads['pages_read'],lines=len(records),admitted=len(actual),native_pixels_checked=checked,compiled_rasters_replayed=len(tasks),
        holdout_documents=20,train_holdout_equal_labels=0,cost_usd=readers.budget.receipt()['cost_usd'],no_vision=True,no_new_calls_on_replay=True,min_host_gap_s=min(gaps) if gaps else None,git_unchanged=before==after)
    atomic(OUT/'validation.json',result);print(json.dumps(result),flush=True)


def test_count():
    suites=list(ET.parse(OUT/'tests.xml').getroot().iter('testsuite'))
    assert not sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in suites)
    return sum(int(s.get('tests',0)) for s in suites)


def final_line(plan,s,tests,cost):
    results=json.loads((_data_input(OUT/'acquisition_results.json')).read_text());read=json.loads((OUT/'read_summary.json').read_text())
    return (f"T24c: done | docs: {s['documents']}/{len(results)} | pages: {plan['pages_rendered']}/{plan['pages_accepted']}/{read['pages_read']} | lines: {s['input_lines']} | admitted: {s['admitted']} | mono: {s['per_class']['greek_mono']} | cs: {s['per_class']['greek_latin_cs']} | train: {s['per_split']['train']} | dev: {s['per_split']['dev']} | test: {s['per_split']['test']} | usd: {cost:.2f} | tests: {tests} passed")


def publish(plan):
    validation=json.loads((OUT/'validation.json').read_text());assert validation['passed']
    s=json.loads((OUT/'admission_summary.json').read_text());pool=json.loads((OUT/'pool_summary.json').read_text());config=json.loads((OUT/'selection_config.json').read_text())
    reads=json.loads((OUT/'read_summary.json').read_text())
    results=json.loads((_data_input(OUT/'acquisition_results.json')).read_text());cost=json.loads((OUT/'cost_receipt.json').read_text());tests=test_count();line=final_line(plan,s,tests,cost['cost_usd'])
    atomic(OUT/'preflight.json',dict(schema='t24c-preflight-1',status='complete' if s['documents']==130 else 'available_scope_complete',
        pool_size=config['pool_size'],overdraw=config['overdraw'],cap_used=config['cap_used'],
        target_documents=130,downloaded=s['documents'],document_shortfall=max(0,130-s['documents']),
        note='T24/T24b blocked preflights retained in their archive folders; pipeline metadata controls selection.'))
    esc=lambda v:' '.join(str(v).split()).replace('|','\\|')
    text=['# T24c — Open Archives Wave 4','',f"Completed {datetime.now(ZoneInfo('Europe/Athens')).isoformat()}. {s['documents']} downloaded documents from {len(results)} tried; {plan['pages_rendered']} rendered / {plan['pages_accepted']} accepted / {validation['pages_read']} read pages; {s['input_lines']} lines, {s['admitted']} admitted native crops.",'',
        'Selection uses pipeline metadata directly: download_success/ocr_success true; filter ok; is_empty false; Greek ≥80%; 20–600 metadata pages; direct http(s) PDF. Null quality scores pass; non-null mojibake is zero. Only measured Greek-badness scores enter the median. No external-table status or collection join controls eligibility.','',
        f"The coordinator's 6,141 documents are reproduced **before** the measured-median filter. The literal median rule reduces this to {config['pool_size']} in {len(pool['pool_per_repository'])} metadata repositories; median {pool['median_greek_badness']}. All {pool['measured_greek_badness_documents']} pre-median candidates have measured scores. Seed {policy.SEED}, cap {config['cap_used']}, type × decade stratified draw of {config['overdraw']}.",'',
        f"Informational URL coverage: {pool['counts']['joined_metadata_rows']}/{pool['counts']['metadata_rows']} overall; {pool['counts']['joined_scanned_rows']}/{pool['counts']['scanned_metadata_rows']} scanned. Cross-collection URL matches are allowed for status/source external_link lookup only. Metadata repository/title/year are recorded provenance and have not been independently verified against PDF contents. Licence: {policy.LICENCE}.",'',
        '| Sequential filter | Rows/documents remaining |','| --- | ---: |']
    text.insert(4,f"The bounded overdraw is exhausted. The 130-document target remains {130-s['documents']} documents short; the approximate 1,500 accepted-page target remains {max(0,1500-plan['pages_accepted'])} pages short. No draw beyond the authorized 173 candidates was made.\n")
    for k in ('metadata_rows','download_success','ocr_success','filter_ok','is_empty_false','percentage_greek_ge80',
              'mojibake_zero','pages_20_600','finite_greek_badness','direct_pdf_url','unique_pre_median_documents','greek_badness_le_median'):
        text.append(f"| {k} | {pool['counts'][k]} |")
    text+=['','| Repository | Pool | Downloaded |','| --- | ---: | ---: |']
    books=json.loads((OUT/'books.json').read_text());book_repos=Counter(b['collection_slug'] for b in books)
    text += [f'| {repo} | {n} | {book_repos[repo]} |' for repo,n in sorted(pool['pool_per_repository'].items())]
    outcomes=Counter(r['outcome'] for r in results)
    candidates={r['key']:r for r in json.loads((OUT/'selection.json').read_text())}
    dead_hosts=Counter(urlsplit(candidates[r['key']]['pdf_url']).hostname for r in results if r['outcome']=='dead_link')
    text+=['','| Failed PDF URL host | Candidates |','| --- | ---: |']
    text += [f'| {host} | {n} |' for host,n in sorted(dead_hosts.items())]
    text+=['',f"Documents tried {len(results)}; downloaded {outcomes['downloaded']}; dead-link/invalid-PDF {outcomes['dead_link']}; skipped-size {outcomes['skipped_size']}. Document target shortfall: {max(0,130-s['documents'])} (bounded overdraw exhausted if nonzero). At most three download attempts per candidate. Initial page plus at most two physical neighbours; 12 accepted slots requested per document, no unbounded replacement. Accepted-page target shortfall: {max(0,1500-plan['pages_accepted'])}.",'',
        'Images: nominal 200 dpi grey, long side ≤3500 px, PNG compression 6. Each page records native PDF points, native 200 dpi dimensions, render scale and effective dpi. All boxes and crops use the rendered frame. One PDF at a time; PDFs deleted after sampled render/gate; SHA/size/page-count and retention receipts kept. Embedded DocAI page image content is stripped before saving with content_stripped note; page PNG is the image of record. Free disk checked throughout; abort threshold 4 GiB.','',
        f"Unchanged T20 admission SHA: `{ADMISSION_SHA}`. Hold-out: 20 whole documents stratified by metadata repository, seed 20261015; 15 test / 5 dev, frozen before paid reads. O5 checks all existing wave hold-outs; {s['previous_train_label_exclusions']} previous train rows excluded in the combined training overlay. {len(s['bad_pages'])} bad pages; {s['crop_failures']} uncuttable crops.",'',
        '| Class | Train | Dev | Test | Total |','| --- | ---: | ---: | ---: | ---: |']
    for c,d in s['per_class_split'].items():text.append(f"| {c} | {d['train']} | {d['dev']} | {d['test']} | {sum(d.values())} |")
    text+=['','| Repository | Class | Train | Dev | Test |','| --- | --- | ---: | ---: | ---: |']
    for repo,classes in s['per_repository_class_split'].items():
        for c,d in classes.items():text.append(f"| {repo} | {c} | {d['train']} | {d['dev']} | {d['test']} |")
    text+=['','| Reason (overlapping) | Lines |','| --- | ---: |']
    text += [f'| {reason} | {n} |' for reason,n in s['per_reason'].items()]
    text+=['',f"Google: USD {cost['cost_usd']:.4f} reserved at USD 0.0015/page, cap USD 3.00; {cost['calls_reserved']} unique page-SHA reservations, zero Vision calls. Reservations include failed/ambiguous attempts; this is not an invoice readback. No automatic Google retries.",'',
        f"Validation: {tests} offline tests passed; {validation['native_pixels_checked']} crops checked against source pixels; {validation['compiled_rasters_replayed']} compiled rasters replayed; offline cache reuse added no calls/reservations. Minimum logged acquisition same-host request gap {validation['min_host_gap_s']} s. Git metadata unchanged: {validation['git_unchanged']}; no Git write operations. All four source tables and the 7,341 Wave 5 candidates retain their pre-run hashes.",'',
        'One extra standalone connection probe was made to an already failed IKEE HTTPS endpoint; it returned RemoteDisconnected and downloaded zero PDF bytes. This exceeded the intended three-attempt boundary for that endpoint by one diagnostic request; it is recorded in [connection_probe.json](connection_probe.json). Subsequent acquisition starts are journalled across resume.','',
        f"Read failures: {reads['empty_pages']} empty / {reads['no_line_pages']} no-line / {reads['lost_pages']} lost-geometry pages. Sample visual checks covered 12 crops across four populated classes, a compiled page, and all four bad-page headings. One terminal hyphen extends beyond the DocAI bbox/crop and is omitted in the label; it is retained under unchanged T20 rules. A concrete metadata/PDF-source mismatch is also recorded in [visual spot checks](visual_qa.json).",'',
        'Automatic admission and raster checks do not establish transcription accuracy or glyph ownership. ocr_success records pipeline routing and does not certify a physical scan. Contact sheets and compiled pages are available for owner review; no owner acceptance is claimed.','',
        '[Selection](SELECTION.md) · [records](records.jsonl) · [admitted](admitted.jsonl) · [rejected](rejected.jsonl) · [hold-outs](holdout_books.json) · [summary](admission_summary.json) · [combined training pool](train_pool.jsonl) · [validation](validation.json) · [inventory](inventory.json)','',line]
    (OUT/'READS.md').write_text('\n'.join(text)+'\n')
    section=f"## Wave 4\n\n{line}\n\nPipeline-metadata selection; measured-median pool {config['pool_size']} after 6,141 pre-median candidates; cap {config['cap_used']}. T20 unchanged; 20 hold-out documents (15 test / 5 dev). One PDF at a time, 3500 px page cap, embedded DocAI image stripping, USD 3.00 cap. No Vision or Git writes. Owner visual/transcription acceptance remains pending.\n\n[Report](../openarchives/READS.md), [selection](../openarchives/SELECTION.md), [summary](../openarchives/admission_summary.json), [validation](../openarchives/validation.json), [inventory](../openarchives/inventory.json). Earlier preflights remain in t24_preflight/ and t24b_preflight/.\n\n"
    state_path=REPO/'docs/records/harvest/collection/EXECUTION_STATE.md';state=state_path.read_text();start=state.index('## Wave 4');end=state.find('\n## ',start+5)
    state_path.write_text(state[:start]+section+(state[end+1:] if end>=0 else ''))
    inv_path=REPO/'docs/INVENTORY.md';inv=inv_path.read_text();start=inv.index('<!-- T24:begin -->');end=inv.index('<!-- T24:end -->',start)+len('<!-- T24:end -->')
    inv_path.write_text(inv[:start]+f"<!-- T24:begin -->\n## T24c — Open Archives Wave 4\n\n{line}\n\nEntrypoint: `python -m scripts.harvest.openarchives prepare|acquire|plan|read|build|validate|publish`. [Policy](../greekocr/harvest/openarchives.py), [runner](../scripts/harvest/openarchives.py), [outputs/validation](../scripts/harvest/openarchives_outputs.py), [tests](../tests/test_openarchives.py). [Report](harvest/openarchives/READS.md), [selection](harvest/openarchives/SELECTION.md), [records](harvest/openarchives/records.jsonl), [summary](harvest/openarchives/admission_summary.json), [hold-outs](harvest/openarchives/holdout_books.json), [validation](harvest/openarchives/validation.json), [hash inventory](harvest/openarchives/inventory.json). Bulk PNGs, crops, raw DocAI responses, compiled JPEGs and class sheets remain under harvest_big/openarchives/. Original preflight folders and Wave 5 candidates retained.\n<!-- T24:end -->"+inv[end:])
    sources=[REPO/p for p in ('greekocr/harvest/openarchives.py','scripts/harvest/openarchives.py','scripts/harvest/openarchives_outputs.py','tests/test_openarchives.py','tests/test_openarchives_preflight.py','tests/test_openarchives_run.py','greekocr/harvest/admission.py')]
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='inventory.json' and not any(part in ('t24_preflight','t24b_preflight') for part in p.parts)]
    files += [p for p in BULK.rglob('*') if p.is_file() and p.suffix not in ('.lock',)]+sources
    atomic(OUT/'inventory.json',dict(schema='t24c-inventory-1',files=[dict(path=relative(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(files))]))
    print(line,flush=True)


def abort_report():
    abort=json.loads((OUT/'disk_abort.json').read_text())
    results=json.loads((_data_input(OUT/'acquisition_results.json')).read_text()) if (_data_input(OUT/'acquisition_results.json')).exists() else []
    pages=json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else []
    (OUT/'READS.md').write_text('# T24c — gracefully aborted for disk space\n\n'+json.dumps(abort,ensure_ascii=False,indent=2)+f"\n\n{len(results)} completed candidate receipts; {len(pages)} rendered pages. Per-candidate checkpoints and Google reservations retained. Harvest incomplete.\n")
