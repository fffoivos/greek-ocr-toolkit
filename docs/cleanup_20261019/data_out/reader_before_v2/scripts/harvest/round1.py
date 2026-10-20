#!/usr/bin/env python3
"""T16: Anemi-only receipted acquisition; all selection/QA is offline."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from contextlib import closing
import copy
import datetime as dt
import hashlib
import html
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import time
import base64
from threading import RLock

PDF_LOCK = RLock()

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.round1 import (allocate, positions, replacement_candidates, book_signals,
    pair_page_lines, quintile, type_reasons, title_flag)
import numpy as np
from PIL import Image
import pypdfium2 as pdfium

OUT = ROOT/'docs/harvest/round1'
BIG = ROOT/'docs/harvest/harvest_big/round1'
PILOT = Path('/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c')
UPSTREAM = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr')
PROPOSAL = UPSTREAM/'docs/evidence/o4c/anemi_wave3_proposal.json'
GATE_SHA = '55c2efd673ce5bca8492e4f5a3fda60ec6c6f26f1def1ca3f265c4459ad8a0e1'


def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path): return json.loads(Path(path).read_text())


def atomic(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    temp.replace(path)


def rows(path):
    return [json.loads(l) for l in Path(path).open() if l.strip()]


def git_snapshot():
    # Read metadata/content only; never invoke a Git command that refreshes index.
    return {str(p.relative_to(ROOT/'.git')):dict(bytes=p.stat().st_size, sha256=sha(p))
            for p in (ROOT/'.git').rglob('*') if p.is_file() and not p.is_symlink()}


def resolve_pilot(path):
    p=Path(path)
    marker='/greek-ocr-toolkit/docs/harvest/'
    if marker in str(p):
        tail=str(p).split(marker,1)[1]
        if (PILOT/tail).exists(): return PILOT/tail
    if not p.exists(): raise FileNotFoundError('missing archived pilot input: '+str(p))
    return p


def anchor_text(document, layout):
    return ''.join(document['text'][int(s.get('startIndex',0)):int(s['endIndex'])]
                   for s in layout.get('textAnchor',{}).get('textSegments',[]))


def feature_summary(features):
    return {k:statistics.median(vals) if (vals:=[f[k] for f in features if f.get(k) is not None]) else None
            for k in ('darkest_percentile_contrast','faintness_proxy','ink_fraction','component_contrast_p10')}


def quality_flags(features, suppression, lines, limits):
    flags=[]
    for k in ('darkest_percentile_contrast','faintness_proxy'):
        if features.get(k) is not None and features[k]<70: flags.append('bad_'+k)
    ink=features.get('ink_fraction')
    if ink is not None and not limits['ink_min']<=ink<=limits['ink_max']: flags.append('bad_ink_fraction')
    contrast=features.get('component_contrast_p10')
    if contrast is not None and contrast<limits['component_min']: flags.append('faint_components')
    ratio=suppression.get('relative faintness',0)/max(1,lines+sum(suppression.values()))
    # The frozen stack's relative-faintness decision is a proxy, not proof of back print.
    if ratio>limits['faint_suppression_max']: flags.append('faint_or_show_through_dominated')
    return flags, ratio


def prepare(redistribute=False):
    OUT.mkdir(parents=True,exist_ok=True);BIG.mkdir(parents=True,exist_ok=True)
    if not (OUT/'git_before.json').exists(): atomic(OUT/'git_before.json',git_snapshot())
    if sha(OUT/'pilot_core.py')!=GATE_SHA: raise ValueError('pilot gate source SHA mismatch')
    proposal=read(PROPOSAL); pgs=read(ROOT/'docs/harvest/pilot_v1/page_gates.json')
    records=rows(PILOT/'pilot_v1/records.jsonl')
    expected=read(ROOT/'docs/harvest/page_reads_v1/sample.json')['records_sha256']
    if sha(PILOT/'pilot_v1/records.jsonl')!=expected: raise ValueError('frozen records hash mismatch')
    bypage=defaultdict(list); bybook=defaultdict(list)
    for r in records: bypage[r['page_id']].append(r)
    for p in pgs: bybook[p['book']].append(p)
    if {p['document_id'] for p in proposal}!=set(bybook) or len(proposal)!=150: raise ValueError('wave-3 scope mismatch')
    summaries={p['id']:feature_summary([r['features'] for r in bypage[p['id']]]) for p in pgs}
    # No pilot page-level photometric cut exists. Keep 70 from the original
    # readability stratum; calibrate broad supplemental guards from ALL 300 pages.
    def quant(key,q): return float(np.percentile([s[key] for s in summaries.values() if s[key] is not None],q))
    ratios=[p.get('stack_suppression_reasons',{}).get('relative faintness',0)/max(1,p['lines_found']+p.get('stack_suppression_count',0)) for p in pgs]
    limits=dict(ink_min=quant('ink_fraction',1),ink_max=quant('ink_fraction',99),
                component_min=quant('component_contrast_p10',1),faint_suppression_max=max(ratios),
                contrast_min=70, calibration='300 pilot page medians, 1st/99th percentile ink; 1st percentile component contrast; maximum pilot faint-suppression share')
    comparisons=rows(ROOT/'docs/harvest/page_reads_v1/comparisons.jsonl')
    comparison_index={(r['id'],r['engine']):r for r in comparisons}
    evidence=[]; confs=[]; agrees=[]
    inputs={str(PROPOSAL):sha(PROPOSAL),str(PILOT/'pilot_v1/records.jsonl'):expected,
            str(ROOT/'docs/harvest/pilot_v1/page_gates.json'):sha(ROOT/'docs/harvest/pilot_v1/page_gates.json'),
            str(ROOT/'docs/harvest/page_reads_v1/comparisons.jsonl'):sha(ROOT/'docs/harvest/page_reads_v1/comparisons.jsonl')}
    for p in sorted(proposal,key=lambda b:(b['year']//10,b['title'])):
        rid=p['document_id']; pages=bybook[rid]; pairs=[]; symbols=[]; blocks=[]; cached_pages=[]
        for pg in pages:
            paths={e:ROOT/f"docs/harvest/page_reads_v1/assignments/{pg['id']}.{e}.json" for e in ('vision','docai')}
            if all(x.exists() for x in paths.values()):
                assignments={e:read(x) for e,x in paths.items()}
                all_lines={e:[v['line'] for v in a['line_assignment']['lines']] for e,a in assignments.items()}
                pp=pair_page_lines(all_lines['vision'],all_lines['docai'])
                pairs.extend(dict(pair,page=pg['page'],page_id=pg['id']) for pair in pp)
                da=assignments['docai']; raw_path=Path(da['raw_json_path'])
                if sha(raw_path)!=da['raw_sha256']: raise ValueError('cached raw response hash mismatch')
                raw=read(raw_path)['document']; native=da['coordinate_frame']['native_size']
                from greekocr.harvest.montage import response_symbols
                symbols.extend(s.get('confidence') for s in response_symbols('docai',{'document':raw},native))
                blocks.extend(anchor_text(raw,b['layout']) for b in raw['pages'][0].get('blocks',[]))
                cached_pages.append(pg['page'])
                for e,x in paths.items(): inputs[str(x)]=sha(x)
                inputs[str(raw_path)]=da['raw_sha256']
        basis='cached full-page native lines/symbols/blocks'
        if not pairs:
            basis='cached pilot crop pairs (no full-page pair available)'
            for pg in pages:
                for r in bypage[pg['id']]:
                    if not r['sampled'] or not r['readers']: continue
                    v,d=r['readers']['vision'],r['readers']['docai']
                    pairs.append(dict(vision=v['text'],docai=d['text'],paired=not v.get('rejected') and not d.get('rejected'),page=r['page'],page_id=r['page_id']))
                    c=comparison_index.get((r['id'],'docai'),{})
                    symbols.extend(s['confidence'] for s in c.get('crop_symbols',[]) if s.get('confidence') is not None)
                    blocks.append(d['text'])
        signal=book_signals(pairs,symbols,blocks)
        scan=[]
        for pg in pages:
            supplemental,ratio=quality_flags(summaries[pg['id']],pg.get('stack_suppression_reasons',{}),pg['lines_found'],limits)
            reasons=pg['page_gate']['flags']+supplemental
            scan.append(dict(page=pg['page'],page_id=pg['id'],accepted=not reasons,flags=reasons,
                             pilot_gate=pg['page_gate'],features=summaries[pg['id']],
                             faint_suppression_share=ratio,image=str(resolve_pilot(bypage[pg['id']][0]['provenance']['page_image'])) if bypage[pg['id']] else str(PILOT/f"harvest_big/t13c/pages/{pg['id']}.png")))
        book=dict(book=rid,key=hashlib.sha256(rid.encode()).hexdigest()[:24],title=p['title'],year=p['year'],decade=p['year']//10*10,
                  pages=sum(v['pages'] for v in pages[0]['catalogue']['volumes']),proposal_pages=p['pages'],catalogue=pages[0]['catalogue'],pilot_pages=[],scan=scan,
                  signals=signal,evidence_basis=basis,full_page_reads=cached_pages,title_flag=title_flag(p['title']),
                  reader_pairs=pairs)
        for pg, scan_page in zip(pages, scan):
            offset=0
            for volume in book['catalogue']['volumes']:
                if volume['volume_id']==pg['fetch_receipt']['volume_id']:break
                offset+=volume['pages']
            global_page=offset+pg['page']
            scan_page['volume_id']=pg['fetch_receipt']['volume_id']
            scan_page['volume_page']=pg['page']
            scan_page['page']=global_page
            book['pilot_pages'].append(global_page)
        evidence.append(book)
        if signal['docai_mean_symbol_confidence'] is not None: confs.append(signal['docai_mean_symbol_confidence'])
        if signal['letters_agree_rate'] is not None: agrees.append(signal['letters_agree_rate'])
    cuts=dict(confidence=quintile(confs),agreement=quintile(agrees),fingerprint=.05,mixed_blocks=.05,
              measured_books=len(confs),inclusive_quintile_ties=True)
    for b in evidence:
        tr=type_reasons(b['signals'],cuts['confidence'],cuts['agreement'])
        failures=sum(not s['accepted'] for s in b['scan']);b['type_reasons']=tr;b['scan_failures']=failures
        # Scan exclusion owns books with no readable pilots, avoiding misleading
        # type classification based solely on absent OCR. Both causes retained.
        b['decision']='OUT_SCAN' if failures==2 else 'OUT_TYPE' if tr else 'REDUCED' if failures==1 else 'IN'
        b['reason']=['both pilot pages fail'] if failures==2 else tr or (['one pilot page fails; half allocation'] if failures==1 else ['passes measured type and scan cuts'])
        if failures==2 and tr:b['reason']+=['also: '+r for r in tr]
    allocations,policy=allocate(evidence,redistribute=redistribute)
    for b in evidence:
        b['allocation']=allocations.get(b['book'],0)
        b['positions']=positions(b['pages'],b['allocation'],b['pilot_pages'],book=b['book'])
        for pos in b['positions']:
            pos['candidates']=replacement_candidates(pos['page'],b['pages'],b['pilot_pages'],[p['page'] for p in b['positions'] if p!=pos])
    data=dict(schema='t16-round1-selection-1',seed=20261014,inputs=inputs,thresholds=cuts,
              quality_limits=limits,allocation_policy=policy,books=evidence,
              pilot_gate_sha256=GATE_SHA,pilot_gate_commit='2bbd00f3255066fe1ba207fb945c3bd3be999b44',
              stack_commit='52cee3bcc882e7426bdc1018d892cd9b1bf9feac')
    descriptor_seeds=[]
    for b in evidence:
        if not b['allocation']:continue
        for v in b['catalogue']['volumes']:
            source=PILOT/f"harvest_big/anemi_wave3_sample_t13c/records/{b['key']}/{v['volume_id']}/viewer.json"
            target=BIG/f"records/{b['key']}/{v['volume_id']}/viewer.json"
            if source.exists():
                if read(source)['source_pdf_url']!=v['source_pdf_url']:raise ValueError('pilot viewer source mismatch')
                if not target.exists():
                    target.parent.mkdir(parents=True,exist_ok=True)
                    temporary=target.with_suffix('.seed.tmp');shutil.copyfile(source,temporary);temporary.replace(target)
                descriptor_seeds.append(dict(source=str(source),target=str(target.relative_to(ROOT)),sha256=sha(source)))
    atomic(OUT/'descriptor_seeds.json',descriptor_seeds)
    atomic(OUT/'selection.json',data)
    selection_report(data)
    print(json.dumps(dict(books=Counter(b['decision'] for b in evidence),allocation=sum(allocations.values()),cuts=cuts,policy=policy),ensure_ascii=False),flush=True)
    return data


def selection_report(data):
    cuts=data['thresholds'];policy=data['allocation_policy'];books=data['books']
    text=['# T16 round 1 selection','',
          'Owner: 14 October 2026. Anemi wave 3 only; all 150 proposal IDs joined to their two pilot pages. Waves 1–2 are excluded by the exact proposal allowlist. No new OCR service calls.','',
          f"DocAI mean-symbol confidence bottom-quintile cut: **{cuts['confidence']:.9f}**. Letters+marks exact line-agreement bottom-quintile cut: **{cuts['agreement']:.9f}**. Values at the cut are OUT (inclusive ties). Each fingerprint kind above **5% of DocAI letter-bearing lines** is OUT. Non-Greek/mixed blocks above **5%** are also OUT (a block needs >=20 letters and >=20% non-Greek letters).",'',
          'Confidence uses every cached full-page symbol once. Agreement uses conservative one-to-one native line-box pairs; unmatched DocAI lines remain in the denominator. All pilot reads are reused offline. Full-page reads cover only 253 of 300 pilot pages; coverage is printed for every book. Where no full-page pair exists, cached sampled crop pairs are used; absent signals fail closed. These proxies cannot prove unusual type or OCR accuracy. Samples are two adjacent middle pages, so book-wide variation remains unknown.','',
          f"The original pilot gate is exported byte-for-byte from commit `{data['pilot_gate_commit']}`; SHA-256 `{GATE_SHA}`. The original frozen stack `{data['stack_commit']}` is reused. The later H1-fix2 gate is deliberately not substituted.",'',
          '**Photometry evidence gap:** the original pilot page gate has no contrast, ink or show-through cut. It supplies rotation/table/non-body/bend flags; the frozen stack already suppresses relative faintness. T16 adds separately recorded, conservative guards using the pilot crop-feature definitions: median darkest-percentile contrast/faintness >=70 (original readability stratum); page-median ink within the 1st/99th pilot percentiles; component-contrast median >=1st pilot percentile; relative-faintness suppression <=maximum observed pilot share. These are T16 guards calibrated on the pilot, not invented historical pilot thresholds. A faintness suppression proxy cannot distinguish front text from show-through; the owner must inspect the images.','',
          'Quality limits: `'+json.dumps(data['quality_limits'],ensure_ascii=False)+'`','',
          'Both pilots failing excludes a book; exactly one failing halves its integer allocation. Books failing both scan and type keep both reasons but count once under OUT_SCAN. Title flags are review aids, not automatic exclusions.','',
          f"Allocation policy: **{policy['policy']}**. Nominal total min(2,000, 13 × surviving books) = {policy['target_total']}; equal decade targets, maximum 16 pages per normal book / 8 per reduced book. Capacity deficits remain unfilled unless redistribution was explicitly selected. This makes the approximate 2,000-page request infeasible after the required exclusions and hard cap; the cuts are retained.",'',
          '| Decade | Nominal budget | Capacity | Allocated |','| --- | ---: | ---: | ---: |']
    for d,n in policy['targets'].items():text.append(f"| {d}s | {n} | {policy['capacities'][d]} | {policy['actual'][d]} |")
    text+=['','Page counts: the five multi-volume proposal counts describe only the first attachment. Position planning uses the sum of all source-declared volume lengths. The per-book table prints this actual total; selection.json retains proposal_pages and volume/local pilot identities.', '',
           'Positions: evenly spaced inclusive ceil(8%)…floor(95%) anchors, seeded 0–2 page forward offsets, nearest available page for pilot/duplicate collisions. Each slot can try the initial page and +1/+2 only; pilot pages, other planned slots, already attempted neighbours and the 95% boundary are excluded. No unbounded search.','',
           '## Books removed by the printed cuts','']
    for b in books:
        if b['type_reasons']:text.append(f"- `{b['key']}` — {b['title']}: "+'; '.join(b['type_reasons']))
    text+=['','## Borderline books nearest the two quintile cuts','',
           '| Signal | Book | Measured value | Cut | Distance above/below cut | Decision |',
           '| --- | --- | ---: | ---: | ---: | --- |']
    for metric,cut_key in [('docai_mean_symbol_confidence','confidence'),('letters_agree_rate','agreement')]:
        threshold=cuts[cut_key]
        nearest=sorted((b for b in books if b['signals'][metric] is not None),key=lambda b:abs(b['signals'][metric]-threshold))[:12]
        for b in nearest:
            value=b['signals'][metric]
            title=b['title'].replace('|','\\|').replace('\n',' ')
            text.append(f"| {metric} | {title} / {b['key']} | {value:.9f} | {threshold:.9f} | {value-threshold:+.9f} | {b['decision']} |")
    text+=['','## Per-book table','',
           '| Decade | Title / book key | Pages | Pilot reads; confidence; letters agree; fingerprint shares; mixed blocks | Pilot scan | Title flag | Decision | Allocation | Reason |',
           '| --- | --- | ---: | --- | --- | --- | --- | ---: | --- |']
    def esc(s):return str(s).replace('|','\\|').replace('\n',' ')
    def val(v):return 'missing' if v is None else f'{v:.6f}'
    for b in books:
        s=b['signals'];sig=f"volume-local read pages {b['full_page_reads']}; {s['lines']} lines/{s['paired_lines']} pairs; C={val(s['docai_mean_symbol_confidence'])}; A={val(s['letters_agree_rate'])}; "+', '.join(f'{k}={v:.1%}' for k,v in s['fingerprint_line_shares'].items())+f"; any-fingerprint={val(s['any_fingerprint_line_share'])}; mixed={val(s['non_greek_mixed_block_share'])}"
        scan='; '.join(f"p{x['page']} "+(','.join(x['flags']) or 'pass')+f" contrast={val(x['features']['darkest_percentile_contrast'])}, ink={val(x['features']['ink_fraction'])}, component={val(x['features']['component_contrast_p10'])}, faint_share={x['faint_suppression_share']:.3f}" for x in b['scan'])
        text.append('| '+' | '.join(map(esc,[str(b['decade'])+'s',b['title']+' / '+b['key'],b['pages'],sig,scan,b['title_flag'],b['decision'],b['allocation'],'; '.join(b['reason'])]))+' |')
    if (OUT/'observations.json').exists():
        text+=['','## Visual observations outside the pilot','']
        for key,note in read(OUT/'observations.json').items():
            text.append(f"- `{key}`: {note['note']} Basis: {note['basis']}")
    (OUT/'SELECTION.md').write_text('\n'.join(text)+'\n')


def load_gate():
    if sha(OUT/'pilot_core.py')!=GATE_SHA:raise ValueError('frozen gate drift')
    spec=importlib.util.spec_from_file_location('t16_pilot_core',OUT/'pilot_core.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def render(pdf,path):
    with PDF_LOCK,pdfium.PdfDocument(pdf) as doc,closing(doc[0]) as page:
        if len(doc)!=1:raise ValueError('single-page PDF required')
        bitmap=page.render(scale=200/72,grayscale=True);image=bitmap.to_pil().copy().convert('L');bitmap.close()
    image.save(path,compress_level=1)
    return image


def gate_pdf(pdf,image_path,stack,gate,limits):
    from greekocr.harvest.pipeline import crop_features, polygon_crop
    start=time.perf_counter();image=render(pdf,image_path);gray=np.asarray(image);result=stack.run(image_path,gray)
    pg=gate.page_gate(gray,result['items'],bend_fired=any(f['side']!=0 for f in result['harvest_bend']))
    # Original feature definitions, computed on physical long detected rows.
    bands=pg['column_bands'];features=[]
    boxes=[gate.bbox(item['polygon']) for item in result['items']]
    for item in result['items']:
        box=gate.bbox(item['polygon'])
        if gate.crop_gate(box,boxes,pg,image.size,item,long_complete=True)['accepted']:
            features.append(crop_features(polygon_crop(image,item['polygon'])))
    feat=feature_summary(features)
    suppression=Counter(q.get('removal','unknown') for q in result.get('removed',[]))
    flags,ratio=quality_flags(feat,suppression,len(result['items']),limits)
    return dict(accepted=pg['accepted'] and not flags,flags=pg['flags']+flags,pilot_gate=pg,
                supplemental_quality_flags=flags,features=feat,feature_rows=len(features),
                faint_suppression_share=ratio,suppression_reasons=dict(suppression),lines=len(result['items']),
                gate_source_sha256=GATE_SHA,stack_source_sha256=stack.source_sha256,stack_model_sha256=stack.model_sha256,
                image_sha256=sha(image_path),dpi=200,grayscale=True,seconds=time.perf_counter()-start)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--run',action='store_true');parser.add_argument('--report',action='store_true');parser.add_argument('--redistribute',action='store_true');parser.add_argument('--smoke',action='store_true')
    a=parser.parse_args()
    if a.prepare:prepare(a.redistribute)
    if a.smoke:
        from greekocr.harvest.pipeline import FrozenStack
        import onnxruntime as ort
        ort.disable_telemetry_events()
        data=read(OUT/'selection.json');stack=FrozenStack(PILOT/'pilot/_stack_52cee3b')
        pg=read(ROOT/'docs/harvest/pilot_v1/page_gates.json')[0];p=resolve_pilot(pg['pdf'])
        result=gate_pdf(p,BIG/'smoke.png',stack,load_gate(),data['quality_limits'])
        print(json.dumps(result,ensure_ascii=False),flush=True)
    if a.run:run()
    if a.report:report()

def fetch_module():
    sys.path.insert(0,str(UPSTREAM/'scripts/fetch'))
    spec=importlib.util.spec_from_file_location('t16_fetcher',ROOT/'scripts/harvest/_anemi_round1_fetcher.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original_resolution=module.pdf_resolution
    def locked_resolution(body):
        with PDF_LOCK:return original_resolution(body)
    module.pdf_resolution=locked_resolution
    return module


def locate(book,page):
    offset=0
    for volume in book['catalogue']['volumes']:
        if offset < page <= offset+volume['pages']:
            return volume,page-offset
        offset+=volume['pages']
    raise ValueError('book page outside all volumes')


def page_path(book,page):
    volume,local=locate(book,page)
    return BIG/f"records/{book['key']}/{volume['volume_id']}/page-{local:06d}.pdf"


def stage_records(books,wanted):
    result=[]
    for b in books:
        if not wanted.get(b['book']):continue
        r=copy.deepcopy(b['catalogue'])
        for v in r['volumes']:v['selected_page_indices']=[]
        for page in wanted[b['book']]:
            v,local=locate(b,page)
            next(x for x in r['volumes'] if x['volume_id']==v['volume_id'])['selected_page_indices'].append(local-1)
        for v in r['volumes']:v['selected_page_indices']=sorted(set(v['selected_page_indices']))
        result.append(r)
    return result


def gate_unaccounted(data,gate_results,stack,gate):
    fm=fetch_module();books={b['book']:b for b in data['books']}
    latest={(r['record_id'],r['volume_id'],r['page_index']):r for r in fm.receipt_rows(BIG/'ledger.jsonl')}
    added=0
    for receipt in latest.values():
        if receipt['state']!='saved':continue
        b=books[receipt['record_id']];offset=0
        for volume in b['catalogue']['volumes']:
            if volume['volume_id']==receipt['volume_id']:break
            offset+=volume['pages']
        page=offset+receipt['page_index']+1;key=f"{b['key']}:{page}"
        if key in gate_results:continue
        directory=BIG/f"records/{b['key']}"
        if not fm.valid_receipt(receipt,directory,b['catalogue'],volume,receipt['page_index']):raise ValueError('unaccounted PDF receipt failed')
        pdf=directory/receipt['path'];image=BIG/f"images/{b['key']}-{page:06d}.png"
        result=gate_pdf(pdf,image,stack,gate,data['quality_limits'])
        gate_results[key]=dict(book=b['book'],page=page,volume=volume['volume_id'],volume_page=receipt['page_index']+1,
            pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),image=str(image.relative_to(ROOT)),fetch_receipt=receipt,gate=result)
        atomic(BIG/'gate_results.json',gate_results);added+=1
    return added


def run():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from urllib.parse import urlsplit
    from greekocr.harvest.pipeline import FrozenStack
    import onnxruntime as ort
    ort.disable_telemetry_events()
    data=read(OUT/'selection.json');books=[b for b in data['books'] if b['allocation']]
    fm=fetch_module();gate=load_gate();stack=FrozenStack(PILOT/'pilot/_stack_52cee3b')
    gate_results=read(BIG/'gate_results.json') if (BIG/'gate_results.json').exists() else {}
    http_root=BIG/'anemi_http';http_root.mkdir(parents=True,exist_ok=True)
    if not (http_root/'rate_state.json').exists():shutil.copyfile(PILOT/'pilot/anemi_http/rate_state.json',http_root/'rate_state.json')
    class PoliteAnemi(fm.AnemiHTTP):
        def check_origin(self,url):
            if urlsplit(url).scheme!='https' or urlsplit(url).netloc!='anemi.lib.uoc.gr':
                raise fm.ProbeError('T16 network is restricted to Anemi HTTPS')
        def check_robots(self,url):
            self.check_origin(url);return super().check_robots(url)
        def _raw(self,url,limit,range_header=None,depth=0):
            self.check_origin(url)
            policy=read(http_root/'backoff.json') if (http_root/'backoff.json').exists() else {}
            delay=max(0,policy.get('not_before',0)-time.time())
            if delay:time.sleep(delay)
            self.interval=max(self.interval,policy.get('interval',2))
            result=super()._raw(url,limit,range_header,depth)
            if result[0]['status'] in (429,503):
                n=policy.get('throttles',0)+1;cooldown=min(600,60*2**(n-1))
                atomic(http_root/'backoff.json',dict(interval=min(30,max(4,self.interval*2)),not_before=time.time()+cooldown,throttles=n))
                print(f'T16_THROTTLE status={result[0]["status"]} cooldown_seconds={cooldown}',flush=True)
            return result
    client=PoliteAnemi(interval=2,root=http_root)
    authenticated=False
    def login(http):
        nonlocal authenticated
        if not authenticated:fm.authenticate(http);authenticated=True
    state_path=OUT/'run_state.json'
    state=read(state_path) if state_path.exists() else dict(started_at=dt.datetime.now(dt.timezone.utc).isoformat(),fetch_seconds=0,gate_seconds=0,stages=[],complete=False)
    used={b['book']:set() for b in books}
    slots=[]
    for b in books:
        for pos in b['positions']:
            slots.append(dict(book=b['book'],original_page=pos['page'],candidate_pages=pos['candidates'],chain=[],accepted_page=None))
    bybook={b['book']:b for b in books}
    # Rebuild slot decisions from persisted SHA-bound gate results on every resume.
    def replay_slots():
        used.clear();used.update({b['book']:set() for b in books})
        for slot in slots:
            slot['chain']=[];slot['accepted_page']=None
            b=bybook[slot['book']]
            for page in slot['candidate_pages']:
                if page in used[b['book']]:
                    slot['chain'].append(dict(page=page,state='skipped',reasons=['already_attempted_by_another_slot']));continue
                key=f"{b['key']}:{page}";g=gate_results.get(key)
                if not g:break
                pdf=page_path(b,page)
                if not pdf.exists() or sha(pdf)!=g['pdf_sha256']:raise ValueError('persisted gate PDF hash drift')
                used[b['book']].add(page)
                slot['chain'].append(dict(page=page,state='accepted' if g['gate']['accepted'] else 'rejected',reasons=g['gate']['flags'],pdf_sha256=g['pdf_sha256']))
                if g['gate']['accepted']:slot['accepted_page']=page;break
    for stage in range(3):
        replay_slots();wanted=defaultdict(list)
        for slot in slots:
            if slot['accepted_page'] is not None:continue
            b=bybook[slot['book']]
            consumed={x['page'] for x in slot['chain']}
            next_page=next((p for p in slot['candidate_pages'] if p not in consumed and p not in used[b['book']]),None)
            if next_page is not None:
                wanted[b['book']].append(next_page);used[b['book']].add(next_page)
        if not wanted:break
        recs=stage_records(books,wanted)
        done=Event()
        def gate_worker():
            for b in books:
                for page in sorted(set(wanted.get(b['book'],[]))):
                    pdf=page_path(b,page);key=f"{b['key']}:{page}"
                    while not pdf.exists() and not done.is_set():time.sleep(.1)
                    if not pdf.exists():continue
                    if key in gate_results:continue
                    v,local=locate(b,page);directory=BIG/f"records/{b['key']}"
                    receipt=None
                    while receipt is None:
                        receipt=fm.latest_receipts(directory).get((v['volume_id'],local-1))
                        if receipt is None:
                            if done.is_set():raise ValueError('PDF has no committed fetch receipt')
                            time.sleep(.1)
                    if not fm.valid_receipt(receipt,directory,b['catalogue'],v,local-1):raise ValueError('invalid fetched receipt')
                    image=BIG/f"images/{b['key']}-{page:06d}.png";image.parent.mkdir(parents=True,exist_ok=True)
                    g=gate_pdf(pdf,image,stack,gate,data['quality_limits'])
                    gate_results[key]=dict(book=b['book'],page=page,volume=v['volume_id'],volume_page=local,
                        pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),image=str(image.relative_to(ROOT)),fetch_receipt=receipt,gate=g)
                    atomic(BIG/'gate_results.json',gate_results)
                    print(f"T16_GATE book={b['key']} page={page} accepted={g['accepted']} reasons={','.join(g['flags']) or 'pass'}",flush=True)
        started=time.perf_counter()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future=executor.submit(gate_worker)
            try:
                failures=0
                while True:
                    summary=fm.fetch_wave(recs,wave=len(recs),max_pages=2000,max_bytes=500_000_000,
                        dest=BIG,http_root=http_root,http_factory=lambda **kwargs:client,login=login,
                        emit=lambda text:print(text,flush=True),page_range='explicit')
                    if summary['stop_reason']=='complete':break
                    failures+=1
                    if failures>=3:raise RuntimeError('Anemi acquisition stopped after three consecutive transport failures')
                    # Rate state enforces the interval; any throttling persists
                    # a 60/120/240-second cooldown and doubles future intervals.
                    if not (http_root/'backoff.json').exists():time.sleep(15*failures)
            finally:done.set()
            future.result()
        gate_unaccounted(data,gate_results,stack,gate)
        elapsed=time.perf_counter()-started
        state['fetch_seconds']+=elapsed
        state['stages'].append(dict(stage=stage,requested=sum(len(set(v)) for v in wanted.values()),seconds=elapsed,fetch_summary=summary))
        atomic(state_path,state)
        replay_slots();atomic(OUT/'slots.json',slots)
        report(data,gate_results,slots,state)
    replay_slots();atomic(OUT/'slots.json',slots)
    state['complete']=all(s['accepted_page'] is not None or all(p in {x['page'] for x in s['chain']} for p in s['candidate_pages']) for s in slots)
    state['finished_at']=dt.datetime.now(dt.timezone.utc).isoformat();state['gate_seconds']=sum(r['gate']['seconds'] for r in gate_results.values())
    atomic(state_path,state);report(data,gate_results,slots,state)


def inline_page(path):
    with Image.open(path) as im:
        im=im.convert('L');im.thumbnail((1200,1600),Image.Resampling.LANCZOS)
        stream=io.BytesIO();im.save(stream,format='WEBP',quality=60,method=4)
        return 'data:image/webp;base64,'+base64.b64encode(stream.getvalue()).decode(),list(im.size)


def gallery(data,manifest,summary):
    bybook=defaultdict(list)
    notes=read(OUT/'observations.json') if (OUT/'observations.json').exists() else {}
    for p in manifest['pages']:
        if p['harvest_accepted']:bybook[p['book']].append(p)
    header='''<!doctype html><html lang="el"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Anemi round 1 · owner look</title><style>*{box-sizing:border-box}body{overflow-wrap:anywhere}
body{font:16px system-ui,sans-serif;margin:24px;color:#20252b;background:#f8f7f2}a{color:#154a8a}.book{padding:20px 0;border-bottom:1px solid #ccc}h2{font-size:18px;max-width:1050px}.pages{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}details{padding:6px;background:white;border:1px solid #c9c7bd}summary{cursor:pointer;list-style:none}summary img{display:block;width:100px;height:140px;object-fit:contain}details[open]{width:min(100%,1250px)}details[open] summary img{width:auto;height:auto;max-width:100%}.replacement{border:3px solid #b51e27}.badge{color:#b51e27;font-weight:bold}.meta{color:#555}nav{display:flex;gap:14px;flex-wrap:wrap}@media(max-width:600px){body{margin:12px}summary img{width:80px;height:115px}h2{overflow-wrap:anywhere}}
</style><body><h1>Anemi · round 1 owner look</h1>'''
    intro=f"<p>{summary['books_in']} books · {summary['pages_accepted']} accepted pages · {summary['replacements']} accepted replacements. No new OCR service calls. Red borders mark replacements.</p><p>Click a page to expand its complete inline review image. Review images are downscaled to at most 1200 × 1600; gating uses the original 200 DPI grayscale PNG. This is an owner screening set, not an OCR accuracy certification.</p>"
    parts=[];current=[];size=len((header+intro).encode())
    def card(src,page,replacement=False,reason=''):
        url,dim=inline_page(src)
        return f'<details class="{"replacement" if replacement else "page"}"><summary><img alt="Page {page}" loading="lazy" src="{url}"><span>p. {page}{" · replacement" if replacement else ""}</span></summary><p>{html.escape(reason)} · {dim[0]}×{dim[1]} review pixels</p></details>'
    def add(row):
        nonlocal current,size
        row_size=len(row.encode())
        if size+row_size>24_000_000 and current:parts.append(current);current=[];size=len((header+intro).encode())
        if row_size>24_000_000:raise ValueError('one book exceeds self-contained gallery cap')
        current.append(row);size+=row_size
    for b in data['books']:
        if not b['allocation']:continue
        pages=sorted(bybook[b['book']],key=lambda p:p['page'])
        row=f'<section class="book" id="{b["key"]}"><h2>{html.escape(b["title"])}</h2><p class="meta">{b["decade"]}s · allocated {b["allocation"]} · accepted {len(pages)} · {html.escape(b["title_flag"])}</p><div class="pages">'
        if b['key'] in notes:row=row.replace('<div class="pages">','<p class="owner-note" style="background:#fff0b8;padding:12px">'+html.escape(notes[b['key']]['note'])+'</p><div class="pages">')
        for p in pages:
            row+=card(ROOT/p['image'],p['page'],p['replacement'], ' ← '.join(str(x['page']) for x in p['replacement_chain'][::-1]))
        add(row+'</div></section>')
    add('<h1 id="removed-books">removed books</h1><p>One original pilot page per removed book, with all recorded reasons.</p>')
    for b in data['books']:
        if b['allocation']:continue
        pg=next((p for p in b['scan'] if not p['accepted']),b['scan'][0])
        row=f'<section class="book removed" id="{b["key"]}"><h2>{html.escape(b["title"])}</h2><p>{b["decade"]}s · {b["decision"]} · {html.escape("; ".join(b["reason"]))}</p><div class="pages">'+card(pg['image'],pg['page'],False,'Original pilot page')+'</div></section>'
        add(row)
    if current:parts.append(current)
    names=['look.html'] if len(parts)==1 else [f'look_{i+1}.html' for i in range(len(parts))]
    nav='<nav>'+''.join(f'<a href="{name}">Part {i+1}</a>' for i,name in enumerate(names))+'</nav>'
    outputs=[]
    for name,part in zip(names,parts):
        path=OUT/name;path.write_text(header+intro+nav+''.join(part)+'</body></html>')
        outputs.append(dict(path=name,bytes=path.stat().st_size,sha256=sha(path),books=len([x for x in part if 'class="book' in x])))
        if path.stat().st_size>25_000_000:raise ValueError('gallery part exceeds 25 MB')
    if len(parts)>1:
        index=header+intro+'<p>The images are split into self-contained parts, each below 25 MB.</p>'+nav+'<ul>'
        for b in data['books']:
            target=next(names[i] for i,part in enumerate(parts) if any(f'id="{b["key"]}"' in row for row in part))
            index+=f'<li><a href="{target}#{b["key"]}">{b["decade"]}s · {html.escape(b["title"])} · {b["decision"]} · {b["allocation"]} pages</a></li>'
        (OUT/'look.html').write_text(index+'</ul></body></html>')
    return outputs


def report(data=None,gate_results=None,slots=None,state=None):
    data=data or read(OUT/'selection.json');gate_results=gate_results if gate_results is not None else read(BIG/'gate_results.json')
    slots=slots if slots is not None else read(OUT/'slots.json');state=state or read(OUT/'run_state.json')
    chain_index={}
    for slot in slots:
        for attempt in slot['chain']:
            if attempt['state']!='skipped':chain_index[(slot['book'],attempt['page'])]=(slot,attempt)
    pages=[]
    for g in gate_results.values():
        pair=chain_index.get((g['book'],g['page']))
        p=copy.deepcopy(g)
        p['selected']=pair is not None
        p['harvest_accepted']=bool(pair and g['gate']['accepted'])
        p['selection_disposition']='selected' if pair else 'superseded_page_plan'
        if pair:
            slot,attempt=pair
            p['replacement']=g['page']!=slot['original_page'];p['original_page']=slot['original_page']
            p['replacement_chain']=slot['chain'][:slot['chain'].index(attempt)+1]
        else:
            p['replacement']=False;p['original_page']=g['page']
            p['replacement_chain']=[dict(page=g['page'],state='not_selected',reasons=['superseded_page_plan'],pdf_sha256=g['pdf_sha256'])]
        pages.append(p)
    pages.sort(key=lambda p:(p['book'],p['page']))
    manifest=dict(schema='t16-round1-manifest-1',selection_sha256=sha(OUT/'selection.json'),
                  pilot_gate_sha256=GATE_SHA,pages=pages,slots=slots,complete=state.get('complete',False))
    accepted=[p for p in pages if p['harvest_accepted']];book_decades={b['book']:b['decade'] for b in data['books']}
    reasons=Counter(f for p in pages if not p['gate']['accepted'] for f in p['gate']['flags'])
    reasons['superseded_page_plan']=sum(not p['selected'] for p in pages)
    if not reasons['superseded_page_plan']:del reasons['superseded_page_plan']
    fetched_receipts=fm_receipts=fetch_module().receipt_rows(BIG/'ledger.jsonl')
    latest={(r['record_id'],r['volume_id'],r['page_index']):r for r in fetched_receipts}
    fetched=sum(r['state']=='saved' for r in latest.values())
    seconds=state['fetch_seconds']
    summary=dict(schema='t16-round1-summary-1',complete=state.get('complete',False),
        books_in=sum(b['allocation']>0 for b in data['books']),books_out_type=sum(b['decision']=='OUT_TYPE' for b in data['books']),books_out_scan=sum(b['decision']=='OUT_SCAN' for b in data['books']),
        books_reduced=sum(b['decision']=='REDUCED' for b in data['books']),pages_planned=sum(b['allocation'] for b in data['books']),
        pages_fetched=fetched,pages_gated=len(pages),pages_accepted=len(accepted),pages_rejected=len(pages)-len(accepted),
        pages_not_selected=sum(not p['selected'] for p in pages),pages_failed_gate=sum(not p['gate']['accepted'] for p in pages),
        replacements=sum(p['replacement'] for p in accepted),replacement_attempts=sum(p['replacement'] for p in pages),
        exhausted_slots=sum(s['accepted_page'] is None and len(s['chain'])==len(s['candidate_pages']) for s in slots),
        failures_by_reason=dict(reasons),fetch_seconds=seconds,fetch_minutes=round(seconds/60,2),
        throughput_pages_per_minute=round(fetched/max(.001,seconds/60),3),
        saved_pdf_bytes=sum(r.get('bytes',0) for r in latest.values() if r['state']=='saved'),
        total_seconds=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(state['started_at'])).total_seconds(),
        gate_cpu_seconds=sum(p['gate']['seconds'] for p in pages),pages_per_decade=dict(sorted(Counter(book_decades[p['book']] for p in accepted).items())),
        pages_per_book={b['book']:dict(allocated=b['allocation'],accepted=sum(p['book']==b['book'] for p in accepted),decision=b['decision']) for b in data['books']},
        allocation_policy=data['allocation_policy'],ocr_service_calls=0,network_origins=['https://anemi.lib.uoc.gr'],
        pilot_gate_sha256=GATE_SHA,started_at=state['started_at'],finished_at=state.get('finished_at'))
    atomic(OUT/'manifest.json',manifest);atomic(OUT/'summary.json',summary)
    if state.get('complete'):
        outputs=gallery(data,manifest,summary);atomic(OUT/'gallery.json',outputs)
        before=read(OUT/'git_before.json');after=git_snapshot()
        atomic(OUT/'git_audit.json',dict(changed=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],git_writes_by_task=False,before=before,after=after))
    print(json.dumps({k:summary[k] for k in ('complete','books_in','pages_fetched','pages_accepted','replacements','fetch_minutes')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
