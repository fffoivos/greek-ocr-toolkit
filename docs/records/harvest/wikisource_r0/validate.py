"""Read-only validation of T7 custody, selection, geometry, labels and budget."""
import sys
sys.dont_write_bytecode=True
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import unicodedata
from urllib.parse import urlsplit
import numpy as np
from PIL import Image
import harvest as h

def rows(name):
    p=h.OUT/name
    return [json.loads(l) for l in p.read_text().split('\n') if l.strip()] if p.exists() else []

def main():
    books=rows('books.jsonl');pages=rows('pages.jsonl');lines=rows('lines.jsonl')
    assert len(books)==5
    expected=set()
    for b in books:
        assert b['train_pool_eligible'] is False and b['training_release_allowed'] is False
        assert len(b['drawn_pages'])<=40
        draw=sorted(random.Random(b['sampling_seed']).sample(sorted(b['eligible_pages'],key=lambda p:p['page']),min(30,len(b['eligible_pages']))),key=lambda p:p['page'])
        assert draw==b['drawn_pages']
        assert all(q['quality'] in (3,4) for q in draw)
        assert h.sha(h.ROOT/b['scan_path'],'sha1')==b['scan_sha1']
        expected.update((b['key'],p['page']) for p in draw)
    assert len(expected)<=150
    assert {(p['book_key'],p['page']) for p in pages}==expected
    assert len(pages)==len(expected)
    all_images=list((h.OUT/'images').glob('*.png'))
    assert len(all_images)<=150
    for path,value in h.load('exclusions/input_hashes.json').items():assert h.sha(path)==value, path
    for b in h.load('exclusions/local20_books.json'):assert h.sha(h.ROOT/b['scan_path'],'sha1')==b['scan_sha1']
    # T7b must retain the original selection, drawn images and exclusions byte for byte.
    for path,digest in h.load('T7B_INPUTS.json')['files'].items():assert h.sha(h.ROOT/path)==digest,path
    audit=h.load('exclusions/disjointness.json')
    assert len(audit['intersections'])==8
    assert all(not v['L1'] and not v['local20'] for v in audit['intersections'].values())
    page_by_id={p['page_id']:p for p in pages}
    human={}
    read_pages=[]
    for p in pages:
        fixed={k:v for k,v in p.items() if k not in {'geometry','google_status','google'}}
        assert hashlib.sha256(json.dumps(fixed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==h.load('T7B_INPUTS.json')['reused_page_fields_sha256'][p['page_id']]
        assert p['split']=='locked_test_R0' and not p['training_release_allowed']
        assert h.sha(h.ROOT/p['image'])==p['image_sha256']
        assert h.sha(h.ROOT/p['wikitext'])==p['wikitext_sha256']
        human[p['page_id']]=h.clean((h.ROOT/p['wikitext']).read_text())
        assert human[p['page_id']]['proofread_level'] in (3,4)
        with Image.open(h.ROOT/p['image']) as image:assert image.size==(p['width'],p['height'])
        if p['google_status']=='ok':
            read_pages.append(p)
            assert h.sha(h.ROOT/p['google']['raw_path'])==p['google']['raw_sha256']
            b=p['google']['binding']
            assert (b['project'],b['location'],b['processor'],b['version'])==('ocr-ground-truth-20261008','eu','9a98b7aca3c19561','pretrained-ocr-v2.1-2024-08-07')
            assert p['google']['token_boxes'] is not None
            from greekocr.harvest.page_reads import _response_geometry
            raw=h.load(str(Path(p['google']['raw_path']).relative_to(h.OUT.relative_to(h.ROOT))))
            returned=raw['document']['pages'][0]
            assert p['google']['line_boxes']==returned.get('lines',[])
            assert p['google']['token_boxes']==returned.get('tokens',[])
            assert p['google']['transforms']==returned.get('transforms',[])
            assert p['google']['page_dimension']==returned.get('dimension')
            geometry=_response_geometry('docai',raw,(p['width'],p['height']))
            geometry.pop('symbols',None)
            assert geometry==p['geometry']
    assert len({r['line_id'] for r in lines})==len(lines)
    rejected=h.load('qa/source_line_rejections.json')['rejections'] if (h.OUT/'qa/source_line_rejections.json').exists() else []
    assert not {r['line_id'] for r in rejected}&{r['line_id'] for r in lines}
    for witness in rejected:
        assert h.sha(h.ROOT/witness['record']['crop_path'])==witness['record']['crop_sha256']
    expected_assignments={}
    for p in read_pages:
        physical=[r for r in p['geometry']['lines'] if r['source']=='lines']
        assignments,blocks=h.policy.align_lines([r['text'] for r in physical],human[p['page_id']]['lines'])
        saved=h.load('assignments/'+p['page_id']+'.json')
        assert assignments==saved['assignments'] and blocks==saved['blocks']
        expected_assignments[p['page_id']]=(physical,assignments)
    used_human=set();used_google=set()
    for r in lines:
        p=page_by_id[r['page_id']]
        assert r['pagequality'] in (3,4)
        assert r['split']=='locked_test_R0' and not r['train_pool_eligible'] and not r['training_release_allowed']
        a=r['alignment'];assert a['alignment']=='aligned' and a['alignment_reason']=='one_to_one' and len(a['human_line_indices'])==1
        physical,assignments=expected_assignments[p['page_id']]
        i=a['google_line_index'];j=a['human_line_indices'][0]
        assert (p['page_id'],i) not in used_google and (p['page_id'],j) not in used_human
        used_google.add((p['page_id'],i));used_human.add((p['page_id'],j))
        assert all(a[k]==v for k,v in assignments[i].items())
        assert a['google_text']==physical[i]['text'] and r['google_line_bbox']==physical[i]['bbox']
        assert a['google_receipt_id']==p['google']['receipt_id'] and a['wikitext_sha256']==p['wikitext_sha256']
        assert r['page']==p['page'] and r['book_key']==p['book_key'] and r['image_sha256']==p['image_sha256']
        assert r['line_id']=='r0-ws-'+p['page_id']+f'-l{i+1:04d}'
        source=human[r['page_id']]['lines'][a['human_line_indices'][0]]
        assert source['usable'] and source['literal']==r['human_label_literal'] and source['text']==r['human_label_nfc']==r['label']
        assert unicodedata.normalize('NFC',r['human_label_literal'])==r['human_label_nfc']
        assert h.policy.UNKNOWN not in r['label'] and not r['label'].startswith(':')
        assert a['policy_sha256']==h.sha(h.ROOT/'greekocr/harvest/wikisource.py')
        assert a['alignment_similarity']>=.65
        crop=h.ROOT/r['crop_path'];assert h.sha(crop)==r['crop_sha256']
        with Image.open(crop) as c,Image.open(h.ROOT/p['image']) as im:
            assert list(c.size)==r['crop_size']
            assert np.array_equal(np.asarray(c),np.asarray(im.crop(r['crop_bbox'])))
    ledger=rows('google/ledger.jsonl');micro=sum(x['micro_usd'] for x in ledger)
    state=h.OUT/'google/ledger.state.json'
    if state.exists():assert json.loads(state.read_text())['calls']==len(ledger),'ambiguous reservation state requires reconciliation'
    assert micro<=300000 and len(ledger)<=116
    assert all(r['micro_usd']==1500 and r['engine']=='docai' for r in ledger)
    assert len({r['key'] for r in ledger})==len(ledger)
    assert {p['image_sha256'] for p in read_pages}<={r['key'] for r in ledger}
    provider=rows('google/provider/ledger.jsonl')
    docai_requests=[e for e in rows('google/network.jsonl') if e['host']=='eu-documentai.googleapis.com']
    assert len(provider)==len(docai_requests)==len(read_pages)==len(ledger)
    for reservation,request,response in zip(ledger,docai_requests,provider):
        assert reservation['time']<=request['started_at']
        assert reservation['key']==response['crop_sha256']
        assert response['status']=='ok' and response['cached'] is False and response['pages_billed']==1
        assert request['status']==200
    events=rows('limiter/events.jsonl')+rows('google/network.jsonl')
    hosts={'el.wikisource.org','upload.wikimedia.org','commons.wikimedia.org','eu-documentai.googleapis.com','oauth2.googleapis.com'}
    starts=collections.defaultdict(list)
    for e in events:
        host=e.get('host') or urlsplit(e.get('url','')).hostname
        assert host in hosts
        if 'started_at' in e:starts[host].append(e['started_at'])
    for host,ts in starts.items():
        ts.sort();assert all(b-a>=1.0 for a,b in zip(ts,ts[1:])),host
    continuation=h.load('T7B_POLICY.json')
    assert all(e['started_at']<continuation['deadline_epoch'] for e in docai_requests)
    inspection=h.load('qa/crop_inspection.json')
    emitted={r['line_id'] for r in lines};excluded={r['line_id'] for r in rejected}
    assert {r['book_key'] for r in inspection['samples']}=={b['key'] for b in books}
    for sample in inspection['samples']:
        assert sample['line_id'] in (excluded if sample['disposition']=='excluded' else emitted)
        assert h.sha(h.ROOT/sample['crop_path'])==sample['crop_sha256']
        assert h.sha(h.ROOT/sample['sheet'])==sample['sheet_sha256']
    incomplete=[p['page_id'] for p in pages if p['google_status']!='ok']
    result=dict(schema='t7-validation-1',books=len(books),pages=len(pages),lines=len(lines),
        total_physical_page_images=len(all_images),provisional_page_images=len(all_images)-len(pages),
        google_read_pages=len(read_pages),unread_pages=len(incomplete),reservations=len(ledger),reserved_usd=micro/1e6,
        aligned_per_page=len(lines)/len(pages),google_http_requests=len(docai_requests),fixed_input_hashes=len(h.load('T7B_INPUTS.json')['files']),
        native_source_rejections=len(rejected),
        visually_inspected_candidates=len(inspection['samples']),
        checks='seeded draw; quality; input immutability; zero intersections; image/scan/raw/crop hashes; exact crop pixels; unchanged alignment policy; literal/NFC/source custody; locked test flags; network allowlist and rates; reservation cap',
        checked_counts=dict(selected_scan_sha1=5,local20_scan_sha1=20,page_images=len(pages),human_wikitext=len(pages),provider_responses=len(read_pages),line_labels=len(lines),crop_pixels=len(lines)),
        complete=len(read_pages)==len(ledger)==116 and not incomplete and bool(lines) and {r['book_key'] for r in lines}=={b['key'] for b in books})
    h.save('validation.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':main()
