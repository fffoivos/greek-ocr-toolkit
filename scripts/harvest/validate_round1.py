#!/usr/bin/env python3
"""T16 offline PDF/receipt/gate/position/gallery validation and custody receipt."""
from __future__ import annotations
import base64
from collections import Counter
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('t16_driver',ROOT/'scripts/harvest/round1.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
from greekocr.harvest.round1 import book_signals,type_reasons,allocate,positions,replacement_candidates,pair_page_lines,quintile


def validate():
    data=driver.read(driver.OUT/'selection.json');manifest=driver.read(driver.OUT/'manifest.json');summary=driver.read(driver.OUT/'summary.json')
    assert summary['complete'] and manifest['complete']
    assert driver.sha(driver.OUT/'selection.json')==manifest['selection_sha256']
    assert len(data['books'])==150
    assert manifest['pilot_gate_sha256']==driver.GATE_SHA==driver.sha(driver.OUT/'pilot_core.py')
    for path,expected in data['inputs'].items():assert driver.sha(path)==expected,path
    books={b['book']:b for b in data['books']};fm=driver.fetch_module()
    pilot_records=driver.rows(driver.PILOT/'pilot_v1/records.jsonl')
    models={r['provenance']['stack_model_sha256'] for r in pilot_records}
    stack_sources={r['provenance']['stack_source_sha256'] for r in pilot_records}
    gate_replay=driver.read(driver.OUT/'pilot_gate_replay.json')
    assert gate_replay['pages']==gate_replay['exact_gate_replays']==300
    assert gate_replay['source_sha256']==driver.GATE_SHA
    assert len(books)==150 and len(set(b['key'] for b in books.values()))==150
    allocations,policy=allocate(data['books'],redistribute=data['allocation_policy']['policy']=='redistributed')
    assert policy=={k:({int(d):v for d,v in values.items()} if isinstance(values,dict) else values) for k,values in data['allocation_policy'].items()}
    seen=set();accepted=[];failures=Counter();render_bytes=0
    recomputed_signals=[]
    for b in data['books']:
        assert b['allocation']==allocations.get(b['book'],0)
        assert b['pages']==sum(v['pages'] for v in b['catalogue']['volumes'])
        assert b['positions']==[dict(p,candidates=replacement_candidates(p['page'],b['pages'],b['pilot_pages'],[q['page'] for q in positions(b['pages'],b['allocation'],b['pilot_pages'],book=b['book']) if q!=p])) for p in positions(b['pages'],b['allocation'],b['pilot_pages'],book=b['book'])]
        assert b['allocation']<= (8 if b['decision']=='REDUCED' else 16)
        pairs=[];symbols=[];blocks=[]
        for pg in b['scan']:
            paths={e:ROOT/f"docs/records/harvest/page_reads_v1/assignments/{pg['page_id']}.{e}.json" for e in ('vision','docai')}
            if not all(p.exists() for p in paths.values()):continue
            aa={e:driver.read(p) for e,p in paths.items()}
            lines={e:[x['line'] for x in a['line_assignment']['lines']] for e,a in aa.items()}
            pairs.extend(dict(p,page=pg['volume_page'],page_id=pg['page_id']) for p in pair_page_lines(lines['vision'],lines['docai']))
            da=aa['docai'];raw=driver.read(da['raw_json_path'])['document']
            from greekocr.harvest.montage import response_symbols
            symbols.extend(x.get('confidence') for x in response_symbols('docai',{'document':raw},da['coordinate_frame']['native_size']))
            blocks.extend(driver.anchor_text(raw,x['layout']) for x in raw['pages'][0].get('blocks',[]))
        if not pairs:assert not b['reader_pairs'],'unimplemented nonempty crop fallback in validator'
        recomputed=book_signals(pairs,symbols,blocks)
        assert recomputed==b['signals'],b['key']
        recomputed_signals.append(recomputed)
        reasons=type_reasons(b['signals'],data['thresholds']['confidence'],data['thresholds']['agreement'])
        assert reasons==b['type_reasons']
    assert data['thresholds']['confidence']==quintile([s['docai_mean_symbol_confidence'] for s in recomputed_signals])
    assert data['thresholds']['agreement']==quintile([s['letters_agree_rate'] for s in recomputed_signals])
    assert sum(b['allocation'] for b in books.values())<=2000
    for p in manifest['pages']:
        key=(p['book'],p['page']);assert key not in seen;seen.add(key);b=books[p['book']]
        assert b['allocation'] and p['page'] not in b['pilot_pages']
        if p['selected']:assert .08*b['pages']<=p['page']<=.95*b['pages']
        else:assert p['selection_disposition']=='superseded_page_plan' and not p['harvest_accepted']
        pdf=ROOT/p['pdf'];assert driver.sha(pdf)==p['pdf_sha256']==p['fetch_receipt']['sha256']
        v,local=driver.locate(b,p['page']);assert v['volume_id']==p['volume'] and local==p['volume_page']
        assert fm.valid_receipt(p['fetch_receipt'],driver.BIG/f"records/{b['key']}",b['catalogue'],v,local-1)
        image=ROOT/p['image'];assert driver.sha(image)==p['gate']['image_sha256']
        assert p['gate']['gate_source_sha256']==driver.GATE_SHA
        assert p['gate']['stack_model_sha256'] in models and p['gate']['stack_source_sha256'] in stack_sources
        assert p['gate']['accepted']==(p['gate']['pilot_gate']['accepted'] and not p['gate']['supplemental_quality_flags'])
        assert p['gate']['flags']==p['gate']['pilot_gate']['flags']+p['gate']['supplemental_quality_flags']
        flags,ratio=driver.quality_flags(p['gate']['features'],p['gate']['suppression_reasons'],p['gate']['lines'],data['quality_limits'])
        assert flags==p['gate']['supplemental_quality_flags'] and ratio==p['gate']['faint_suppression_share']
        assert p['replacement']==(p['page']!=p['original_page'])
        assert len([x for x in p['replacement_chain'] if x['state']!='skipped'])<=3
        assert p['replacement_chain'][-1]['page']==p['page']
        assert all(x['page']<=p['original_page']+2 for x in p['replacement_chain'])
        assert p['harvest_accepted']==(p['selected'] and p['gate']['accepted'])
        if p['harvest_accepted']:accepted.append(p)
        if not p['gate']['accepted']:failures.update(p['gate']['flags'])
        if not p['selected']:failures.update(['superseded_page_plan'])
        render_bytes+=image.stat().st_size
    for slot in manifest['slots']:
        b=books[slot['book']]
        assert len(slot['candidate_pages'])<=3
        assert slot['candidate_pages']==replacement_candidates(slot['original_page'],b['pages'],b['pilot_pages'],[p['page'] for p in b['positions'] if p['page']!=slot['original_page']])
        assert slot['accepted_page'] is not None or all(p in {x['page'] for x in slot['chain']} for p in slot['candidate_pages'])
        if slot['accepted_page'] is not None:assert slot['chain'][-1]['state']=='accepted'
    fetched={(r['record_id'],r['volume_id'],r['page_index']) for r in fm.receipt_rows(driver.BIG/'ledger.jsonl') if r['state']=='saved'}
    assert len(fetched)==len(manifest['pages'])==summary['pages_fetched']==summary['pages_gated']
    assert len(accepted)==summary['pages_accepted']
    assert dict(failures)==summary['failures_by_reason']
    assert sum(p['replacement'] for p in accepted)==summary['replacements']
    assert summary['ocr_service_calls']==0
    transport=driver.rows(driver.BIG/'anemi_http/transfer.jsonl')
    from urllib.parse import urlsplit
    assert all(urlsplit(r['url']).netloc=='anemi.lib.uoc.gr' for r in transport)
    # Original transport records request STARTS; server latency can only lengthen gaps.
    intervals=[]
    for a,b in zip(transport,transport[1:]):
        gap=(driver.dt.datetime.fromisoformat(b['request_started_at'])-driver.dt.datetime.fromisoformat(a['request_started_at'])).total_seconds()
        assert gap>=1.99,(a['url'],b['url'],gap)
        intervals.append(gap)
    parts=driver.read(driver.OUT/'gallery.json');all_html='';images=0;all_ids=[];thumbnail_sizes=[]
    for part in parts:
        path=driver.OUT/part['path'];assert path.stat().st_size<=25_000_000
        assert driver.sha(path)==part['sha256'];text=path.read_text();all_html+=text
        assert '*{box-sizing:border-box}' in text and 'overflow-wrap:anywhere' in text
        all_ids.extend(re.findall(r'<section class="book(?: removed)?" id="([^"]+)"',text))
        assert not re.search(r'<(?:img|script|link)[^>]+(?:src|href)="https?://',text)
        for kind,encoded in re.findall(r'src="data:image/(jpeg|webp);base64,([^"]+)"',text):
            with Image.open(io.BytesIO(base64.b64decode(encoded,validate=True))) as im:
                im.load();assert im.width<=1200 and im.height<=1600
                thumbnail_sizes.append([im.width,im.height])
            images+=1
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"',text):assert (driver.OUT/href).is_file(),href
    assert all_ids==[b['key'] for b in data['books'] if b['allocation']]+[b['key'] for b in data['books'] if not b['allocation']]
    assert images==len(accepted)+summary['books_out_type']+summary['books_out_scan']
    assert all_html.count('class="replacement"')==summary['replacements']
    xml=ET.parse(driver.OUT/'tests.xml').getroot();tests=sum(int(x.attrib.get('tests',0)) for x in xml.findall('testsuite'))
    assert sum(int(x.attrib.get('failures',0))+int(x.attrib.get('errors',0)) for x in xml.findall('testsuite'))==0
    receipt=dict(validated=True,pages=len(seen),accepted=len(accepted),books=150,inline_images=images,
        gallery_parts=len(parts),gallery_bytes=sum(p['bytes'] for p in parts),
        minimum_request_start_gap_seconds=min(intervals),transport_requests=len(transport),
        transport_statuses=dict(Counter(r['status'] for r in transport)),native_png_bytes=render_bytes,tests_passed=tests,
        exact_original_pilot_gate_replays=300,stack_bindings_match_pilot=True,browser_layout_verified=False,
        source_sha256={str(p.relative_to(ROOT)):driver.sha(p) for p in [ROOT/'greekocr/harvest/round1.py',ROOT/'scripts/harvest/round1.py',ROOT/'scripts/harvest/_anemi_round1_fetcher.py',ROOT/'scripts/harvest/validate_round1.py',ROOT/'tests/test_harvest_round1.py',driver.OUT/'pilot_core.py']})
    driver.atomic(driver.OUT/'validation.json',receipt)
    inventory={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=driver.sha(p))
        for p in sorted(driver.OUT.rglob('*')) if p.is_file() and p.name not in ('inventory.json','validation.log')}
    driver.atomic(driver.OUT/'inventory.json',dict(artifacts=inventory,bulk=dict(root=str(driver.BIG.relative_to(ROOT)),pages=summary['pages_fetched'],saved_pdf_bytes=summary['saved_pdf_bytes'],native_png_bytes=render_bytes),sources=receipt['source_sha256']))
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':validate()
