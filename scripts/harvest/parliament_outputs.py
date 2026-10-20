"""T23 offline records, unchanged T20 admission, native crops and evidence."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import gzip
import io
import json
import multiprocessing
from pathlib import Path
import random
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from scripts.harvest.parliament import (REPO, OUT, BULK, GOOGLE, SOURCE, ADMISSION_SHA,
    sha, relative, atomic, read_jsonl, holdout, ParliamentReaders, round1)
from scripts.harvest import vouli_outputs as previous
from scripts.harvest import compile_page_reads as compiler
from scripts.harvest.admit_round1 import contact_sheets, stats, write_jsonl
from scripts.harvest.build_round1_reads_rest import make_rows, cohort_summary
from greekocr.harvest.parliament_geometry import response_geometry as _response_geometry
from greekocr.harvest import admission

REASONS = admission.REASONS + ('crop_geometry',)
OLD_FILES = ('docs/records/harvest/round1/admitted.jsonl', 'docs/records/harvest/vouli/admitted.jsonl', 'docs/records/harvest/round2/admitted.jsonl')
RECORD_FILES = {'anemi_round1': OLD_FILES[0], 'vouli_parliament_1850s': OLD_FILES[1], 'anemi_round2': OLD_FILES[2], SOURCE:'docs/records/harvest/parliament/admitted.jsonl'}


def raw_read(page, plan):
    # The T21 raw/cache/image/binding verifier is reused without changing it.
    parsed_path=GOOGLE/'parsed/docai'/(page['image_sha256']+'.json')
    parsed=json.loads(parsed_path.read_text())
    if parsed['status']!='ok':
        if parsed['image_sha256']!=sha(REPO/page['image']):raise ValueError('failed image custody changed')
        attempts=[r for r in read_jsonl(GOOGLE/'docai/ledger.jsonl') if r['crop_sha256']==page['image_sha256']]
        if len(attempts)!=1 or attempts[0]['status']!='error':raise ValueError('failed attempt is not unique')
        receipt=attempts[0];raw_path=Path(receipt['raw_json_path'])
        if receipt['binding']!=plan['binding'] or receipt['raw_sha256']!=sha(raw_path):
            raise ValueError('failed raw custody changed')
        error=json.loads(raw_path.read_text())['error']
        return None,dict(status='error',error=error,receipt_id=receipt['receipt_id'],
            raw_json_path=relative(raw_path),raw_sha256=sha(raw_path),
            parsed_path=relative(parsed_path),parsed_sha256=sha(parsed_path))
    # T21 custody checks, with exact original raw bytes recoverable from gzip.
    if parsed['binding']!=plan['binding'] or parsed['image_sha256']!=sha(REPO/page['image']):
        raise ValueError('parsed image/binding changed')
    from scripts.harvest.compact_parliament_raw import raw_bytes
    raw_path=Path(parsed['raw_json_path']);cache_path=raw_path.parent/'cache.json'
    cache=json.loads(cache_path.read_text());data,archive=raw_bytes(raw_path)
    digest=hashlib.sha256(data).hexdigest()
    if (cache['raw_sha256']!=digest or cache['crop_sha256']!=page['image_sha256']
        or cache['binding']!=plan['binding'] or cache['receipt_id']!=parsed['receipt_id']):
        raise ValueError('raw response custody changed')
    receipt=dict(status='ok',receipt_id=parsed['receipt_id'],raw_json_path=relative(raw_path),raw_sha256=digest,
        cache_path=relative(cache_path),cache_sha256=sha(cache_path),
        parsed_path=relative(parsed_path),parsed_sha256=sha(parsed_path))
    if archive is not None:receipt.update(raw_gzip_path=relative(archive),raw_gzip_sha256=sha(archive))
    return json.loads(data),receipt


def read_records(plan, write=False):
    records, audits = [], []
    for page in plan['pages']:
        raw, receipt = raw_read(page, plan)
        geometry, rows, docai, custody, median, error = None, [], [], [], None, None
        document=raw['document'] if raw is not None else {}
        if raw is not None:
            try:
                geometry = _response_geometry('docai', raw, (page['width'],page['height']))
                rows, docai, custody, median = make_rows(page, document, geometry)
            except ValueError as exc:
                error = str(exc)
        else:
            error=receipt['error']['message']
        for r in rows:
            r.update(source=SOURCE, licence='CC-BY-4.0', source_url=page['source_url'],
                attribution=page['attribution'], read_batch='parliament_modern', era=page['era'])
            if geometry['coordinate_frame'].get('vertex_source')=='provider_normalized_vertices':
                r['flags'].append('docai_normalized_vertices_native_frame')
        assignment = dict(schema='t23-page-assignment-1', page=page, reader=receipt,
            coordinate_frame=geometry['coordinate_frame'] if geometry else None,
            docai_lines=docai, docai_symbol_custody=custody, median_counted_line_height=median,
            lost_page=error is not None, geometry_error=error, records=rows)
        path = OUT / 'assignments' / (page['id']+'.json')
        if write:
            atomic(path, assignment)
        elif assignment != json.loads(path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())):
            raise AssertionError('assignment replay changed: '+page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'], **cohort_summary([page],rows),
            empty=raw is not None and not document.get('text','').strip(),
            no_line_layouts=raw is not None and not document.get('pages',[{}])[0].get('lines'),
            lost_page=error is not None, geometry_error=error,
            transformed=bool(geometry and geometry['coordinate_frame']['converted']),
            vertex_source=geometry['coordinate_frame'].get('vertex_source') if geometry else None,receipt=receipt))
    return records, dict(schema='t23-read-summary-1', overall=cohort_summary(plan['pages'],records),
        pages=audits, empty_pages=sum(p['empty'] for p in audits),
        no_line_pages=sum(p['no_line_layouts'] for p in audits),
        lost_pages=sum(p['lost_page'] for p in audits), transformed_pages=sum(p['transformed'] for p in audits),
        successful_pages=sum(p['receipt']['status']=='ok' for p in audits),
        failed_reads=sum(p['receipt']['status']!='ok' for p in audits),
        normalized_frame_pages=sum(p['vertex_source']=='provider_normalized_vertices' for p in audits))


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
                source_url=r['source_url'], attribution=r['attribution'], read_batch='parliament_modern', era=r['era'], docai_text=r['docai_text']))
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
    return Path(str(page['year'])) / f"{page['year']}_{compiler.slug(page['title'])}_{page['key'][:6]}" / f"p{page['page']:04d}.jpg"


def render_compiled(image, rows, quality):
    canvas, layout = compiler.render_page(image,rows)
    bad = quality.get('bad_page',False)
    if bad:
        text = 'REJECTED: bad_page | '+', '.join(quality['triggers'])+' | all lines excluded at admission'
        ImageDraw.Draw(canvas).text((40,8),text,font=compiler.number_font(),fill=compiler.RED)
    layout['bad_page'] = bad
    layout['bad_page_triggers'] = quality.get('triggers',[])
    if quality.get('read_error'):
        ImageDraw.Draw(canvas).text((40,8),'REJECTED: read_error | '+quality['read_error'],font=compiler.number_font(),fill=compiler.RED)
    layout['read_error']=quality.get('read_error')
    return canvas, layout


def compiled_quality(quality,reads):
    result=dict(quality)
    for p in reads['pages']:
        if p['lost_page']:
            result[p['page_id']]=dict(quality.get(p['page_id'],{}),read_error=p['geometry_error'])
    return result


def compile_task(task):
    p, rows, quality = task
    with Image.open(REPO/p['image']) as image:
        canvas, layout = render_compiled(image,rows,quality)
    path = BULK/'compiled'/compiled_path(p)
    path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path,'JPEG',quality=85,optimize=True)
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
                path = BULK/'crops'/r['book_key'][:8]/f"p{r['page']:06d}-l{r['line_number']:04d}.png"
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
    summary=dict(schema='t23-admission-1',input_lines=len(records),pages=len(groups),
        pages_attempted=len(plan['pages']),pages_read=reads['successful_pages'],failed_reads=reads['failed_reads'],
        admitted_before_o5=before,admitted=len(admitted),rejected=len(rejected),crops=len(admitted),
        trimmed=sum(r['trimmed'] for r in admitted),has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),
        per_reason={r:reasons[r] for r in REASONS},per_split=dict(Counter(r['split'] for r in admitted)),
        per_class={c:sum(r['script_class']==c for r in admitted) for c in admission.CLASSES},
        per_class_split={c:{s:sum(r['script_class']==c and r['split']==s for r in admitted) for s in ('train','dev','test')} for c in admission.CLASSES},
        per_decade={str(d):dict(Counter(r['split'] for r in admitted if r['decade']==d)) for d in range(1970,2010,10)},
        label_in_holdout=reasons['label_in_holdout'],bad_pages=[dict(page_id=pid,**q) for pid,q in quality.items() if q['bad_page']],
        crop_failures=len(crop_failures),contact_sheets=sheets,
        crop_size_stats={k:stats([r['crop_'+k] for r in admitted]) for k in ('width','height')},
        per_class_split_era={c:{s:{era:sum(r['script_class']==c and r['split']==s and r['era']==era for r in admitted) for era in sorted({r['era'] for r in records})} for s in ('train','dev','test')} for c in admission.CLASSES},
        per_era=dict(Counter(r['era'] for r in admitted)),
        holdout_policy=dict(seed=20261015,books=16,dev=4,test=12,selection='one book in each of 16 chronological available-year strata before reads'),
        previous_train_label_exclusions=len(exclusions),per_source_cap=cap,admission_module_sha256=ADMISSION_SHA)
    for name,rows in [('admitted',admitted),('rejected',rejected),('train_pool',pool),('train_pool_exclusions',exclusions+cap_exclusions)]:
        write_jsonl(OUT/(name+'.jsonl'),rows)
    expected_paths={REPO/r['crop_path'] for r in admitted}
    stale=[]
    for path in (BULK/'crops').rglob('*.png'):
        if path not in expected_paths:
            stale.append(dict(path=relative(path),sha256=sha(path)))
            path.unlink()
    atomic(OUT/'stale_crop_cleanup.json',dict(reason='remove superseded intermediate crops absent from final admitted records',files=stale))
    atomic(OUT/'admission_summary.json',summary)
    display_quality=compiled_quality(quality,reads)
    tasks=[(p,groups.get(p['id'],[]),display_quality.get(p['id'],{})) for p in plan['pages']]
    compiled=[]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as process_pool:
        for i,result in enumerate(process_pool.map(compile_task,tasks,chunksize=1),1):
            compiled.append(result)
            if i%100==0: print(f'compiled {i}/{len(tasks)}',flush=True)
    atomic(BULK/'compiled/compile_receipt.json',dict(schema='t23-compiled-1',pages=compiled,page_count=len(compiled),
        records_sha256=sha(_data_input(OUT/'records.jsonl')),base_builder_sha256=sha(Path(compiler.__file__)),
        builder_sha256=sha(Path(__file__)),jpeg_quality=85,pad=40,gap=40))
    (BULK/'compiled/README.txt').write_text(compiler.README.replace(' (the weakest 5%)','')+
        'Bad pages remain compiled, with a red REJECTED: bad_page heading and their triggers. All their lines are excluded from admission.\n'
        'Failed reads retain the native page and a red REJECTED: read_error heading; no lines are fabricated.\n')
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
    """Offline replay of source custody, scope, reads, admission and final pixels."""
    from greekocr.harvest.parliament import eligible, candidate_slots, page_spread, neighbours, MAX_PDF
    from greekocr.harvest.parliament_http import ParliamentHTTP
    from scripts.harvest.parliament import CATALOGUE, SOURCE as expected_source
    books=json.loads((OUT/'books.json').read_text())
    manifest=json.loads((_data_input(OUT/'manifest.json')).read_text())
    slots=json.loads((OUT/'slots.json').read_text())
    held=json.loads((OUT/'holdout_books.json').read_text())
    selection=json.loads((OUT/'selection_summary.json').read_text())
    assert len(books)==len({b['book'] for b in books})==selection['selected']
    assert len({b['key'] for b in books})==len(books)
    assert all(n==4 for n in Counter(b['year'] for b in books).values())
    catalogue={r['document_id']:r for r in read_jsonl(CATALOGUE)}
    candidates={(s['year'],s['stratum']):s['candidates'] for s in candidate_slots(catalogue.values())}
    for b in books:
        assert eligible(catalogue[b['book']]) and catalogue[b['book']]==b['catalogue']
        assert b['catalogue'] in candidates[b['year'],b['stratum']]
        assert b['source_url']==b['catalogue']['record_url'] and b['source_url'].startswith('https://hdl.handle.net/')
        assert b['attribution']=='Hellenic Parliament Library; '+b['title']
        assert b['licence']=='CC-BY-4.0' and b['source']==expected_source
        assert b['pdf_bytes']<=MAX_PDF and not (REPO/b['pdf']).exists()
        download=json.loads((REPO/b['download_receipt']).read_text())
        assert download['sha256']==b['pdf_sha256'] and download['bytes']==b['pdf_bytes']
        assert b['bitstream']['size'] in (None,b['pdf_bytes'])
        retention=json.loads((BULK/'pdf_receipts'/(b['book']+'.retention.json')).read_text())
        assert retention['deleted'] and retention['page_count']==b['page_count']
        assert retention['sha256']==b['pdf_sha256'] and retention['bytes']==b['pdf_bytes']
        own=[s for s in slots if s['key']==b['key']]
        assert len(own)==12 and [s['position'] for s in own]==page_spread(b['page_count'],b['book'])
        reserved={s['original_page'] for s in own}
        for s in own:
            wanted=neighbours(s['original_page'],b['page_count'],reserved)
            reserved.update(wanted)
            assert wanted==s['candidate_pages']
            assert len(s['attempts'])<=3 and s['attempts']==wanted[:len(s['attempts'])]
            found=[p for p in manifest if p['key']==b['key'] and p['page'] in s['attempts']]
            accepted=[p['page'] for p in found if p['harvest_accepted']]
            assert accepted==([] if s['accepted_page'] is None else [s['accepted_page']])
    assert held==holdout(books) and Counter(b['split'] for b in held)=={'test':12,'dev':4}
    assert len({b['year'] for b in held})==16
    assert len(manifest)==len({p['id'] for p in manifest})==plan['pages_rendered']
    assert plan['pages']==[p for p in manifest if p['harvest_accepted']]
    reference_gate=json.loads((round1.OUT/'manifest_all.json').read_text())[0]['gate']
    retention=json.loads((OUT/'page_image_retention.json').read_text())
    retained_rejects={p['page_id']:p for p in retention['pages']}
    for p in manifest:
        assert p['image_sha256']==p['gate']['image_sha256']
        if (REPO/p['image']).exists():
            assert sha(REPO/p['image'])==p['image_sha256']
            with Image.open(REPO/p['image']) as im:assert im.mode=='L' and im.size==(p['width'],p['height'])
        else:
            assert not p['harvest_accepted'] and not retained_rejects[p['id']]['native_retained']
        if not p['harvest_accepted']:
            r=retained_rejects[p['id']]
            assert r['image_sha256']==p['image_sha256'] and r['native_size']==[p['width'],p['height']]
            assert r['pdf_sha256']==p['pdf_sha256'] and r['flags']==p['gate']['flags']
            assert sha(REPO/r['preview'])==r['preview_sha256']
            with Image.open(REPO/r['preview']) as im:assert list(im.size)==r['preview_size']
        g=p['gate']
        assert g['gate_source_sha256']==round1.GATE_SHA
        assert all(g[k]==reference_gate[k] for k in ('stack_source_sha256','stack_model_sha256'))
        flags,ratio=round1.quality_flags(g['features'],g['suppression_reasons'],g['lines'],plan['quality_limits'])
        assert flags==g['supplemental_quality_flags'] and ratio==g['faint_suppression_share']
        assert g['flags']==g['pilot_gate']['flags']+flags
        assert g['accepted']==(g['pilot_gate']['accepted'] and not flags)
        assert not p['harvest_accepted'] or 'more_than_two_columns' not in g['flags']
    api=ParliamentHTTP(BULK/'http_t23',offline=True).receipt()
    assert api==json.loads((OUT/'api_politeness.json').read_text()) and api['gap_passed']
    budget=read_jsonl(GOOGLE/'budget.jsonl');ledger=read_jsonl(GOOGLE/'docai/ledger.jsonl')
    hashes={p['image_sha256'] for p in plan['pages']}
    assert len(budget)==len({r['key'] for r in budget})==plan['max_calls']
    assert {r['key'] for r in budget}==hashes and all(r['engine']=='docai' and r['micro_usd']==1500 for r in budget)
    assert len(ledger)==len({r['crop_sha256'] for r in ledger})==len(budget)
    assert all(r['status'] in ('ok','error') and not r['cached'] for r in ledger)
    for r in ledger:
        if r['status']=='error':
            raw_path=Path(r['raw_json_path'])
            assert sha(raw_path)==r['raw_sha256']
            assert json.loads(raw_path.read_text())['error']==dict(code=400,message='Input Document too large',status='INVALID_ARGUMENT')
    assert len(budget)*1500<=2_500_000 and not (GOOGLE/'vision').exists()
    first_reservation=min(r['time'] for r in budget)
    frozen_mtimes={name:(OUT/name).stat().st_mtime for name in ('books.json','holdout_books.json','plan.json')}
    assert all(t<=first_reservation for t in frozen_mtimes.values())
    assert json.loads((GOOGLE/'budget.state.json').read_text())['calls']==len(budget)
    cost=json.loads((OUT/'cost_receipt.json').read_text())
    assert cost['calls_reserved']==len(budget) and cost['cost_usd']==len(budget)*.0015
    records,reads=read_records(plan)
    assert records==read_jsonl(_data_input(OUT/'records.jsonl')) and reads==json.loads((OUT/'read_summary.json').read_text())
    assert len(records)==len({r['id'] for r in records})
    assert all(r['source']==SOURCE and r['licence']=='CC-BY-4.0' and r['read_batch']=='parliament_modern' for r in records)
    old=[r for name in OLD_FILES for r in read_jsonl(REPO/name)]
    expected,rejected,quality,before,exclusions=admit_records(records,held,old)
    expected,crop_rejected,crop_failures,geometries=previous.plan_crops(records,expected,{p['id']:(p['width'],p['height']) for p in plan['pages']})
    actual=read_jsonl(_data_input(OUT/'admitted.jsonl'));summary=json.loads((OUT/'admission_summary.json').read_text())
    assert sorted(rejected+crop_rejected,key=lambda r:r['id'])==read_jsonl(_data_input(OUT/'rejected.jsonl'))
    assert len(actual)+len(rejected)+len(crop_rejected)==len(records)
    assert [r['id'] for r in actual]==[r['id'] for r in expected]
    assert all(all(a[k]==v for k,v in e.items() if k!='docai_text') for a,e in zip(actual,expected))
    pool,cap_exclusions,cap=training_pool(old,actual,exclusions)
    assert pool==read_jsonl(_data_input(OUT/'train_pool.jsonl')) and exclusions+cap_exclusions==read_jsonl(OUT/'train_pool_exclusions.jsonl')
    labels={admission.normalize_label(r['label']) for r in old+actual if r['split'] in ('dev','test')}
    assert not labels&{r['label'] for r in pool} and cap['passed']
    amap={r['id']:r for r in actual};groups=defaultdict(list)
    for r in records:groups[r['page_id']].append(r)
    checked=0
    for i,(pid,rows) in enumerate(groups.items(),1):
        with Image.open(REPO/rows[0]['image']) as image:
            image.load()
            for r in rows:
                if r['id'] not in amap:continue
                a=amap[r['id']];bounds,trimmed=geometries[r['id']]
                assert bounds==a['crop_bbox'] and trimmed==a['trimmed'] and sha(REPO/a['crop_path'])==a['crop_sha256']
                assert Path(a['crop_path']).parent.name==r['book_key'][:8]
                assert Path(a['crop_path']).name==f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                with Image.open(REPO/a['crop_path']) as crop:
                    assert crop.mode=='L' and crop.size==(a['crop_width'],a['crop_height'])
                    assert crop.tobytes()==image.crop(tuple(bounds)).tobytes()
                checked+=1
        if i%100==0:print(f'validated crops {i}/{len(groups)}',flush=True)
    assert checked==len(actual)==summary['crops']
    assert {relative(p) for p in (BULK/'crops').rglob('*.png')}=={r['crop_path'] for r in actual}
    assert summary['per_class_split_era']=={c:{s:{era:sum(r['script_class']==c and r['split']==s and r['era']==era for r in actual) for era in sorted({r['era'] for r in records})} for s in ('train','dev','test')} for c in admission.CLASSES}
    assert summary['per_reason']=={reason:sum(reason in r['reasons'] for r in rejected+crop_rejected) for reason in REASONS}
    receipt=json.loads((BULK/'compiled/compile_receipt.json').read_text())
    from greekocr.harvest.parliament_provenance import verify_source
    snapshot=OUT/'source_snapshots'/('parliament_outputs-'+receipt['builder_sha256']+'.py')
    binding=verify_source(receipt['builder_sha256'],Path(__file__),snapshot)
    assert receipt['base_builder_sha256']==sha(Path(compiler.__file__))
    atomic(OUT/'compiled_replay_binding.json',binding)
    assert receipt['page_count']==plan['page_count']
    entries={e['page_id']:e for e in receipt['pages']}
    display_quality=compiled_quality(quality,reads)
    tasks=[(p,groups.get(p['id'],[]),display_quality.get(p['id'],{}),entries[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as process_pool:
        for _ in process_pool.map(validate_compiled_task,tasks,chunksize=1):pass
    assert {e['page_id'] for e in receipt['pages'] if e['bad_page']}=={p['page_id'] for p in summary['bad_pages']}
    assert {e['page_id'] for e in receipt['pages'] if e['read_error']}=={p['page_id'] for p in reads['pages'] if p['lost_page']}
    for cls,sheet in summary['contact_sheets'].items():
        assert sha(REPO/sheet['path'])==sheet['sha256']
        assert len(sheet['ids'])==len(set(sheet['ids']))==min(60,summary['per_class'][cls])
        assert all(amap[i]['script_class']==cls for i in sheet['ids'])
        with Image.open(REPO/sheet['path']) as im:assert im.size==(sheet['width'],sheet['height'])
    before_hashes={relative(p):sha(p) for p in (GOOGLE/'budget.jsonl',GOOGLE/'budget.state.json',GOOGLE/'docai/ledger.jsonl')}
    readers=ParliamentReaders(plan)
    def forbidden(*args,**kwargs):raise AssertionError('offline replay cannot call provider')
    readers.docai.read=forbidden
    statuses={r['crop_sha256']:r['status'] for r in ledger}
    for p in plan['pages']:assert readers.call('docai',REPO/p['image'])['status']==statuses[p['image_sha256']]
    assert before_hashes=={p:sha(REPO/p) for p in before_hashes}
    assert sha(REPO/'greekocr/harvest/admission.py')==ADMISSION_SHA
    atomic(OUT/'resume_check.json',dict(pages_replayed=plan['page_count'],new_calls=0,new_reservations=0,provider_method_forbidden=True,unchanged_ledger_hashes=before_hashes))
    result=dict(passed=True,volumes=len(books),target_volumes=104,missing_years=selection['missing_years'],
        pages_rendered=len(manifest),pages_attempted=plan['page_count'],pages_read=reads['successful_pages'],
        failed_reads=reads['failed_reads'],unique_calls=len(budget),lines=len(records),
        admitted=len(actual),crops_checked=checked,native_pixels_checked=checked,compiled_rasters_replayed=len(tasks),
        train_holdout_equal_labels=0,holdout_books=16,holdouts_frozen_before_reads=True,
        frozen_input_mtimes=frozen_mtimes,first_google_reservation_time=first_reservation,
        per_source_cap=cap,api_politeness=api)
    result['page_image_retention']={k:v for k,v in retention.items() if k!='pages'}
    atomic(OUT/'validation.json',result)
    print(json.dumps(result),flush=True)
    return result


def publish(plan):
    """Publish local evidence only after complete offline validation."""
    from datetime import timezone
    validation=json.loads((OUT/'validation.json').read_text())
    assert validation['passed']
    root=ET.parse(OUT/'tests.xml').getroot()
    suites=[root] if root.tag=='testsuite' else root.findall('testsuite')
    tests=sum(int(s.attrib.get('tests',0)) for s in suites)
    assert all(int(s.attrib.get('failures',0))==int(s.attrib.get('errors',0))==0 for s in suites)
    summary=json.loads((OUT/'admission_summary.json').read_text())
    reads=json.loads((OUT/'read_summary.json').read_text())
    cost=json.loads((OUT/'cost_receipt.json').read_text())
    books=json.loads((OUT/'books.json').read_text())
    selection=json.loads((OUT/'selection_summary.json').read_text())
    api=json.loads((OUT/'api_politeness.json').read_text())
    manifest=json.loads((_data_input(OUT/'manifest.json')).read_text())
    held={b['book_key']:b['split'] for b in json.loads((OUT/'holdout_books.json').read_text())}
    zero_gate_volumes=[b['key'] for b in books if not any(p['key']==b['key'] and p['harvest_accepted'] for p in manifest)]
    records=read_jsonl(_data_input(OUT/'records.jsonl'));admitted=read_jsonl(_data_input(OUT/'admitted.jsonl'))
    splits=summary['per_split'];classes=summary['per_class']
    before=json.loads((OUT/'git_before.json').read_text());after=round1.git_snapshot()
    main_paths=('HEAD','index','refs/heads/main','packed-refs','logs/HEAD','logs/refs/heads/main','config')
    audit=dict(unchanged=before==after,main_worktree_unchanged=all(before.get(p)==after.get(p) for p in main_paths),
        main_metadata={p:dict(before=before.get(p),after=after.get(p)) for p in main_paths},
        changed=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],
        note='This task issued no Git mutation commands; shared worktree changes are recorded separately.')
    atomic(OUT/'git_audit.json',audit)
    skip_counts=Counter(s['reason'] for s in selection['skips'])
    from greekocr.harvest.parliament import resolve_pdf
    from greekocr.harvest.parliament_http import ParliamentHTTP
    attempted={b['book'] for b in books}|{s['uuid'] for s in selection['skips']}
    offline_client=ParliamentHTTP(BULK/'http_t23',offline=True)
    resolved=0
    for uuid in attempted:
        try:resolve_pdf(offline_client,uuid)
        except (RuntimeError,ValueError):continue
        resolved+=1
    downloaded=len([p for p in (BULK/'pdf_receipts').glob('*.json') if not p.name.endswith('.retention.json')])
    last=(f"T23: done | volumes: {len(books)} | pages: {plan['pages_rendered']}/{plan['pages_accepted']}/{reads['successful_pages']} | "
        f"lines: {summary['input_lines']} | admitted: {summary['admitted']} | mono: {classes['greek_mono']} | poly: {classes['greek_poly']} | "
        f"train: {splits.get('train',0)} | dev: {splits.get('dev',0)} | test: {splits.get('test',0)} | usd: {cost['cost_usd']:.2f} | tests: {tests} passed")
    reason_counts=Counter(flag for p in manifest for flag in p['gate']['flags'])
    lines=['# T23 — Wave 3 Parliament proceedings: page reads and admitted crops','',
        f"**{len(books)} selected volumes; {plan['pages_rendered']} pages rendered / {plan['pages_accepted']} accepted / "
        f"{reads['successful_pages']} read. {len(records):,} lines; {len(admitted):,} admitted native crops.**",'',
        f"**Scope shortfall:** the supplied 76,246-row catalogue has eligible proceedings in 18 of 26 requested years. "
        f"Missing years: {', '.join(map(str,selection['missing_years']))}. Four volumes per available year gives {len(books)} rather than 104; "
        'the absent 32 volumes were not replaced from other years. Complete live `title:YYYY` search results also returned no eligible '
        'records for these eight years; this checks dated titles, not a claim that the repository can never acquire those proceedings. '
        'The run proceeds on the available authorized source scope, with this limitation explicit. [Probe](missing_year_probe.json).', '',
        f"Volumes selected/resolved/downloaded/skipped(size)/failed: **{len(books)} / {resolved} / {downloaded} / "
        f"{skip_counts['size']} / {sum(n for r,n in skip_counts.items() if r not in ('size','short_pdf'))}**. "
        f"{skip_counts['short_pdf']} downloaded candidates were too short for twelve distinct sampled pages. "
        'These counts include replaced candidates in resolved/downloaded; the 72 final selections each have an ORIGINAL PDF receipt. '
        'All PDFs and partial downloads from this run were deleted after sampling; PDF SHA-256, byte count, bitstream checksum and decoded page count remain. '
        '[Selection table](SELECTION.md), [candidate dispositions](selection_summary.json), [volume receipts](volumes/).', '',
        'Selection uses seed 20263, four chronological session strata per year, with deterministic shuffled backups within each stratum. '
        'The raw rights must contain CC BY 4.0; any NC/ND declaration is excluded. Each source URL is the catalogue handle, '
        'and attribution is `Hellenic Parliament Library; <title>`. Source declaration is retained verbatim.', '',
        'Each PDF is streamed into `<uuid>.pdf` under the 250,000,000-byte bound. Twelve pages span inclusive 8–95% positions, '
        'with independently seeded 0–2 offsets and unique page identities. A failed slot gets at most two following physical neighbours '
        '(original plus at most two retries), without crossing the 95% boundary or borrowing another slot’s page. '
        'Short session PDFs have few unreserved neighbours. [Slots](slots.json) records every attempt and exhausted slot.', '',
        f"Rendering is pypdfium2, 200 dpi grayscale L PNG. Frozen gate SHA `{round1.GATE_SHA}`; unchanged T16 photometric guards and limits. "
        'Two-column handling is inherited exactly, including rejection of `more_than_two_columns`; no threshold relaxation. '
        'No owner look during this run, as recorded in the collection execution state.','',
        '| Page-gate reason | Pages (overlapping) |','| --- | ---: |']
    lines += [f'| {r} | {n} |' for r,n in sorted(reason_counts.items())]
    lines += ['', 'DocAI uses the unchanged T19 EU processor/version, Greek hint, symbol setting and ADC binding. '
        'The same T21 raw/cache SHA and binding checks apply. T19 native line layouts, inverse transforms, symbol-scoped mean/min '
        'confidence and line flags remain unchanged. T20 admission is byte-identical, including bad_page, mixed_word and all other rules.','',
        f"Native frame correction: **{reads['normalized_frame_pages']} pages** have provider integer vertices inconsistent with the native image's normalized vertices. "
        'The T23 adapter uses the provider normalized vertices relative to the explicitly reported native pixel dimensions, as defined in '
        '[NormalizedVertex](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document#NormalizedVertex). '
        'Agreeing integer frames retain their original coordinates; recorded-transform cases retain the T15 inverse mapping. '
        'Raw responses, text anchors, confidence values and T20 rules are unchanged. '
        'Native before/after cards in [frame_before_visual_selection.json](frame_before_visual_selection.json) and '
        '[visual_qa_corrected_selection.json](visual_qa_corrected_selection.json) verify the corrected row association. '
        'The initial integer-frame build was superseded before publication.', '',
        'Reads use a forward queue with three workers and a backward queue with six workers paced at ≥6.1 s between new starts. '
        'Both queues share image-SHA locks, parsed caches and one budget ledger; cache hits do not call the provider. '
        'The fixed selection and hold-outs predate both queues.', '',
        'Storage: complete raw responses are retained as lossless gzip archives. For exact embedded copies of an input PNG, '
        '`.json.dedup.gz` keeps every other response field and a SHA-bound reference to the saved native PNG. '
        'The loader reconstructs the original base64 field and canonical response bytes, verifying the original raw SHA-256. '
        'No pixels, text, confidences or geometry are discarded. Full gzip remains the fallback when the embedded image differs. '
        'To materialize one original JSON offline: `python -m scripts.harvest.compact_parliament_raw --restore <original-raw-json-path>`. '
        'The archive journal is `harvest_big/parliament/google/raw_archives.jsonl`; intermediate full archives may be superseded by their deduplicated representation.', '',
        'Debug page assignments are losslessly gzipped under `assignments/`; byte/hash receipts are in `assignment_archives.json`. '
        'The requested records and admission JSONL files remain uncompressed. Assignment JSON bytes can be restored with `gzip -dk <file.json.gz>`.', '',
        'Every gate-accepted native PNG is retained, including failed DocAI inputs, as are native counterexamples for every page-gate flag. '
        'Other gate-rejected PNG intermediates have a review preview, original PNG/PDF SHA, source bitstream and exact render recipe in '
        '[page_image_retention.json](page_image_retention.json). They were released to fit the requested crops and compiled pages on disk. '
        'They contribute no lines. Regeneration, without Google: `python -m scripts.harvest.parliament_retention --restore <page-id>` '
        '(public PDF download, SHA check, byte-identical re-render, temporary PDF deletion).','',
        '| Class | Split | Era 1975–1981 | Era 1982–2000 | Total |','| --- | --- | ---: | ---: | ---: |']
    for c in admission.CLASSES:
        for s in ('train','dev','test'):
            counts=summary['per_class_split_era'][c][s]
            lines.append(f"| {c} | {s} | {counts.get('1975_1981_polytonic_possible',0)} | {counts.get('1982_2000_monotonic',0)} | {sum(counts.values())} |")
    late_poly=sum(r['year']>=1982 and r['script_class']=='greek_poly' for r in admitted)
    lines += ['', 'Era tags describe the catalogue year: 1975–1981 can be polytonic; 1982+ has the monotonic-era tag. '
        f'The unchanged script classifier decides each line independently; **{late_poly} post-1981 lines classify as greek_poly**. '
        'No accents or labels are silently rewritten to fit the year.','',
        '| Admission rejection reason | Lines (overlapping) |','| --- | ---: |']
    lines += [f'| {r} | {n} |' for r,n in summary['per_reason'].items()]
    lines += ['', 'Hold-out seed 20261015: sixteen books from sixteen represented years, spread across sixteen chronological year strata; '
        '12 test / 4 dev, frozen before any Google call. All lines inherit their whole-volume split. '
        f"O5 excludes {summary['label_in_holdout']} new train lines equal to any round-1, Vouli, round-2 or new dev/test label. "
        f"A combined [training pool](train_pool.jsonl) additionally excludes {summary['previous_train_label_exclusions']} old train matches; "
        'old admitted artifacts stay byte-identical. The inherited Vouli polytonic-source cap also applies to this pool.', '',
        f"API politeness: **{api['request_count']} requests; minimum start gap {api['min_gap_s']:.6f} s (required ≥2 s)**. "
        'The serial cross-process lock covers metadata, streamed PDFs, redirects and failed probes. Cache hits are not requests. '
        'Two compound-query discovery probes returned HTTP 500 and were replaced by complete title-field queries; no request retry was performed. '
        '[Politeness receipt](api_politeness.json); bulk transport ledger `http_t23/requests.jsonl`.', '',
        f"Google: **{cost['calls_reserved']} unique reserved calls, USD {cost['cost_usd']:.4f}**, within USD 2.50. "
        '[Document AI list price](https://cloud.google.com/products/document-ai/pricing) checked 15 October 2026: USD 1.50/1,000 OCR pages; '
        'the conservative ledger deducts no free allowance. This is a reservation estimate, not invoice readback. '
        '`harvest_big/parliament/google/budget.jsonl` reserves before calling, at most once per page-image SHA. '
        'No Vision instance/calls, provider retries or second reads. Definitive HTTP 400 size refusals retain their raw response and reservation and are never retried; other pages continue at native 200 dpi. See [Document AI limits](https://docs.cloud.google.com/document-ai/limits). [Cache replay](resume_check.json) makes zero network calls.', '',
        f"Zero-acceptance volumes: {len(zero_gate_volumes)} ({', '.join(zero_gate_volumes) or 'none'}). "
        'They retain their original selection and whole-volume split, with zero reads; they are not replaced by a quality-driven volume draw. '
        f"Read failures: {reads['failed_reads']} definitive size refusals; {reads['lost_pages']-reads['failed_reads']} unusable geometry pages; {reads['empty_pages']} empty reads; {reads['no_line_pages']} no-line reads; "
        f"{reads['transformed_pages']} inverse-transformed pages. Admission: {len(summary['bad_pages'])} bad pages; "
        f"{summary['crop_failures']} uncuttable geometries rejected; {summary['trimmed']} native crops trimmed. "
        'Crops retain the T20 spatial-neighbour >15% midpoint rule and 4/2 px padding. All final native crop pixels and compiled rasters are replayed. '
        'Bad read pages retain a visible red rejection heading in their compiled JPEG. Automatic checks do not establish transcription accuracy or single-row glyph ownership. '
        '[Visual sample](visual_qa.json) records the inspected physical evidence. '
        'The compiled raster, fonts and quality 85 remain the approved format; optimized JPEG entropy coding reduces disk use while retaining the same decoded pixels.', '',
        'A retained counterexample is `f401a95f-p000044-l0116`: the provider combines two physical rows and reverses their reading order. '
        'It has mean confidence 0.964975 and passes the unchanged T20 quality rules. The native frame correction aligns its box to those rows, '
        'but does not repair the teacher text or impose an extra admission rule. The record and context remain available for post-hoc owner review.', '',
        f"**{tests} offline tests passed**. [Validation](validation.json), [tests](tests.xml), [plan](plan.json), [records](records.jsonl), "
        '[admitted](admitted.jsonl), [rejected](rejected.jsonl), [summary](admission_summary.json), [hold-outs](holdout_books.json), '
        '[inventory](inventory.json), [Git audit](git_audit.json). '
        f"Main Git bookkeeping unchanged: {audit['main_worktree_unchanged']}; no Git mutation commands were issued.", '',
        '| Year | UUID | Split | PDF pages | Rendered | Accepted | Read | Lines | Admitted |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for b in books:
        pages=[p for p in manifest if p['key']==b['key']]
        lines.append(f"| {b['year']} | {b['book']} | {held.get(b['key'],'train')} | {b['page_count']} | {len(pages)} | "
            f"{sum(p['harvest_accepted'] for p in pages)} | {sum(a['page_id'].startswith(b['key']+'-') and a['receipt']['status']=='ok' for a in reads['pages'])} | {sum(r['book_key']==b['key'] for r in records)} | {sum(r['book_key']==b['key'] for r in admitted)} |")
    lines+=['',last]
    (OUT/'READS.md').write_text('\n'.join(lines)+'\n')
    state_path=REPO/'docs/records/harvest/collection/EXECUTION_STATE.md';state=state_path.read_text()
    now=datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    old_row=next(s for s in state.splitlines() if s.startswith('| 3 parliament'))
    state=state.replace(old_row,f"| 3 parliament 1975–2000 | T23 | complete (72/104; source shortfall) | 2026-10-15 03:12 | {now} | "
        f"{plan['pages_rendered']} / {plan['pages_accepted']} / {reads['successful_pages']} | {summary['admitted']} | {cost['cost_usd']:.4f} |")
    section='\n'.join(['## Wave 3','',
        f"T23 completed available-source scope {now} Athens: {len(books)} volumes (four/year in 18 available years), "
        f"{plan['pages_rendered']} rendered / {plan['pages_accepted']} accepted / {reads['successful_pages']} DocAI-read pages; "
        f"{len(records)} lines; {len(admitted)} admitted native crops. USD {cost['cost_usd']:.4f}; {tests} offline tests passed.", '',
        'The 104-volume target remains short by 32: no eligible catalogue rows for '+', '.join(map(str,selection['missing_years']))+
        '. Complete live dated-title searches also returned zero eligible records. No replacement across years or licence relaxation.', '',
        f"Monotonic class {classes['greek_mono']} / polytonic class {classes['greek_poly']}; train {splits.get('train',0)}, "
        f"dev {splits.get('dev',0)}, test {splits.get('test',0)}. Sixteen year-stratified held-out volumes (12 test / 4 dev), frozen before reads. "
        'O5 checks all four waves. Era and script class stay separate. T20 admission unchanged; zero Vision calls.', '',
        f"{api['request_count']} public API/download requests; minimum gap {api['min_gap_s']:.6f} s. PDFs deleted after sampled render/gate; hashes, sizes and page counts retained. "
        'All crop pixels and compiled rasters validated. [Selection](../parliament/SELECTION.md), [report](../parliament/READS.md), '
        '[summary](../parliament/admission_summary.json), [validation](../parliament/validation.json), [inventory](../parliament/inventory.json).', '',last])
    if '\n## Wave 3\n' in state:
        head,tail=state.split('\n## Wave 3\n',1);offset=tail.find('\n## ')
        state=head.rstrip()+'\n\n'+section+'\n'+(tail[offset:] if offset>=0 else '')
    else:state=state.rstrip()+'\n\n'+section+'\n'
    state_path.write_text(state)
    inv_path=REPO/'docs/INVENTORY.md';text=inv_path.read_text()
    section='\n'.join(['<!-- T23:begin -->','## T23 — Parliament Wave 3 (15 October 2026)','',
        f"{len(books)} of 104 requested volumes (eight missing source years); {plan['pages_rendered']} rendered / {plan['pages_accepted']} accepted / "
        f"{reads['successful_pages']} read pages; {len(records)} DocAI lines; {len(admitted)} admitted crops; USD {cost['cost_usd']:.4f}; {tests} tests.", '',
        '`python -m scripts.harvest.parliament select-fetch-gate|run|build|validate|publish`; network only for fetch/gate and run. '
        'Seeded chronological selection and year-stratified hold-out; CC BY 4.0 raw-only; ORIGINAL PDFs bounded to 250 MB and deleted after sampling; '
        'frozen T16 gate/T20 admission/T21 DocAI mapping; at-most-once SHA ledger and USD 2.50 cap.', '',
        '[Selection](harvest/parliament/SELECTION.md), [reads](harvest/parliament/READS.md), [records](harvest/parliament/records.jsonl), '
        '[admitted](harvest/parliament/admitted.jsonl), [rejected](harvest/parliament/rejected.jsonl), [summary](harvest/parliament/admission_summary.json), '
        '[hold-outs](harvest/parliament/holdout_books.json), [training pool](harvest/parliament/train_pool.jsonl), '
        '[validation](harvest/parliament/validation.json), [tests](harvest/parliament/tests.xml), [hash inventory](harvest/parliament/inventory.json). '
        'Raw caches, page PNGs, UUID8 crops, compiled JPEGs and class sheets remain ignored under harvest_big/parliament/.','', '<!-- T23:end -->'])
    if '<!-- T23:begin -->' in text:
        a,rest=text.split('<!-- T23:begin -->',1);_,b=rest.split('<!-- T23:end -->',1);text=a+section+b
    else:text+='\n\n'+section+'\n'
    inv_path.write_text(text)
    files={p for p in OUT.rglob('*') if p.is_file() and p.name!='inventory.json'}
    # Keep old census caches out of this task inventory; bind its catalogue and resolver inputs explicitly.
    for name in ('images','pdf_receipts','google','crops','compiled','admission_sheet','http_t23','qa','qa_integer_frame','rejected_previews'):
        files.update(p for p in (BULK/name).rglob('*') if p.is_file())
    files.update(REPO/p for p in plan['inputs'])
    files.update([state_path,inv_path,Path(__file__),REPO/'scripts/harvest/parliament.py',
        REPO/'greekocr/harvest/parliament.py',REPO/'greekocr/harvest/parliament_http.py',
        REPO/'greekocr/harvest/parliament_geometry.py',
        REPO/'greekocr/harvest/parliament_provenance.py',
        REPO/'greekocr/harvest/admission.py',REPO/'tests/test_parliament.py',
        REPO/'tests/fixtures/parliament_resolution.json',Path(compiler.__file__),
        REPO/'scripts/harvest/vouli.py',REPO/'scripts/harvest/vouli_outputs.py',
        REPO/'scripts/harvest/compact_parliament_raw.py',
        REPO/'scripts/harvest/parliament_retention.py',
        REPO/'docs/records/harvest/COLLECTION_PLAN_v1.md',BULK/'o4c_discover_parliament.py',BULK/'o4c_common.py'])
    files.update(REPO/p for p in (
        'greekocr/harvest/pipeline.py','greekocr/harvest/readers.py','greekocr/harvest/page_reads.py',
        'greekocr/harvest/round1.py','greekocr/harvest/round1_reads.py',
        'greekocr/readers/services/google_docai.py','scripts/harvest/round1.py',
        'scripts/harvest/round1_reads.py','scripts/harvest/build_round1_reads_rest.py',
        'scripts/harvest/admit_round1.py','docs/records/harvest/round1/pilot_core.py',
        'docs/records/briefs/T20_line_admission_crops.md','docs/records/briefs/T21_vouli_reads.md',
        'tests/test_harvest_admission.py','tests/test_vouli.py','tests/test_round2.py',
        'tests/test_round1_reads_rest.py','tests/test_compile_page_reads.py','tests/test_docai.py'))
    atomic(OUT/'inventory.json',dict(schema='t23-file-inventory-1',file_count=len(files),
        generated_utc=datetime.now(timezone.utc).isoformat(),excluded_self=relative(OUT/'inventory.json'),
        files=[dict(path=relative(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]))
    print(last,flush=True)
    return last
