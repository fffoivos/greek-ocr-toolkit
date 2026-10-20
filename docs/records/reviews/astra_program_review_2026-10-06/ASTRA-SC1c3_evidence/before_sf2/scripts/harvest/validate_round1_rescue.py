#!/usr/bin/env python3
"""Read-only offline T18 receipt, gate, image, slot and combined-manifest replay."""
from collections import Counter
import datetime as dt
import importlib.util
from pathlib import Path
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('t18_driver_validation',ROOT/'scripts/harvest/round1_rescue.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
from greekocr.harvest.round1_rescue import rescue_selection, look_relative
from PIL import Image


def validate():
    data=d.read(d.OUT/'selection.json');manifest=d.read(d.OUT/'manifest.json');summary=d.read(d.OUT/'summary.json')
    d.verify_inputs(data)
    assert manifest['complete'] and summary['complete']
    assert manifest['selection_sha256']==d.sha(d.OUT/'selection.json')
    expected=rescue_selection(d.read(d.BASE/'selection.json'),d.read(d.BASE/'rescues.json'))
    assert {k:v for k,v in data.items() if k!='inputs'}==expected
    assert len(data['books'])==51 and sum(b['allocation'] for b in data['books'])==693
    assert d.t16.GATE_SHA==manifest['pilot_gate_sha256']==d.sha(d.BASE/'pilot_core.py')
    books={b['book']:b for b in data['books']};seen=set();accepted=[];failures=Counter()
    fm=d.t16.fetch_module()
    ledger=fm.receipt_rows(d.BIG/'ledger.jsonl')
    receipt_ids={fm.receipt_identity(r) for r in ledger}
    baseline=d.read(d.BASE/'manifest.json')
    stacks={(p['gate']['stack_source_sha256'],p['gate']['stack_model_sha256']) for p in baseline['pages']}
    assert len(stacks)==1
    for p in manifest['pages']:
        b=books[p['book']];identity=(p['book'],p['page'])
        assert identity not in seen;seen.add(identity)
        assert .08*b['pages']<=p['page']<=.95*b['pages'] and p['page'] not in b['pilot_pages']
        assert p['selected'] and p['selection_disposition']=='selected'
        assert p['harvest_accepted']==p['gate']['accepted']
        pdf=ROOT/p['pdf'];image=ROOT/p['image'];g=p['gate']
        assert d.sha(pdf)==p['pdf_sha256']==p['fetch_receipt']['sha256']
        v,local=d.t16.locate(b,p['page'])
        assert p['volume']==v['volume_id'] and p['volume_page']==local
        assert fm.valid_receipt(p['fetch_receipt'],d.BIG/f"records/{b['key']}",b['catalogue'],v,local-1)
        assert fm.receipt_identity(p['fetch_receipt']) in receipt_ids
        assert d.sha(image)==g['image_sha256'] and g['dpi']==200 and g['grayscale']
        with Image.open(image) as im:
            im.load();assert im.mode=='L'
            # Independently decode and re-render the single-page source PDF.
            with d.t16.PDF_LOCK,d.t16.pdfium.PdfDocument(pdf) as doc,d.t16.closing(doc[0]) as pg:
                assert len(doc)==1
                bitmap=pg.render(scale=200/72,grayscale=True)
                native=bitmap.to_pil().copy().convert('L');bitmap.close()
            assert im.size==native.size and im.tobytes()==native.tobytes()
        assert g['gate_source_sha256']==d.t16.GATE_SHA
        assert (g['stack_source_sha256'],g['stack_model_sha256']) in stacks
        assert g['accepted']==(g['pilot_gate']['accepted'] and not g['supplemental_quality_flags'])
        assert g['flags']==g['pilot_gate']['flags']+g['supplemental_quality_flags']
        flags,ratio=d.t16.quality_flags(g['features'],g['suppression_reasons'],g['lines'],data['quality_limits'])
        assert flags==g['supplemental_quality_flags'] and ratio==g['faint_suppression_share']
        assert p['replacement']==(p['page']!=p['original_page'])
        chain=p['replacement_chain']
        assert chain[-1]['page']==p['page'] and chain[-1]['pdf_sha256']==p['pdf_sha256']
        assert len(chain)<=3 and all(p['original_page']<=a['page']<=p['original_page']+2 for a in chain)
        if p['harvest_accepted']:accepted.append(p)
        else:failures.update(g['flags'])
    bypage={(p['book'],p['page']):p for p in manifest['pages']}
    attempts=set()
    for slot in manifest['slots']:
        b=books[slot['book']]
        pos=next(p for p in b['positions'] if p['page']==slot['original_page'])
        assert slot['candidate_pages']==pos['candidates']
        assert slot['accepted_page'] is not None or {a['page'] for a in slot['chain']}==set(pos['candidates'])
        for i,a in enumerate(slot['chain']):
            if a['state']=='skipped':
                assert a['reasons']==['already_attempted_by_another_slot']
                assert (slot['book'],a['page']) in attempts
                continue
            identity=(slot['book'],a['page']);assert identity not in attempts;attempts.add(identity)
            p=bypage[identity]
            assert a['pdf_sha256']==p['pdf_sha256'] and a['reasons']==p['gate']['flags']
            assert a['state']==('accepted' if p['gate']['accepted'] else 'rejected')
            assert p['replacement_chain']==slot['chain'][:i+1]
        if slot['accepted_page'] is not None:
            assert slot['chain'][-1]['page']==slot['accepted_page'] and slot['chain'][-1]['state']=='accepted'
    assert attempts==seen
    latest={(r['record_id'],r['volume_id'],r['page_index']):r for r in ledger}
    assert len([r for r in latest.values() if r['state']=='saved'])==len(seen)==summary['pages_fetched']==summary['pages_gated']
    assert len(accepted)==summary['pages_accepted'] and len(manifest['slots'])==summary['pages_planned']
    assert dict(failures)==summary['failures_by_reason']
    assert summary['replacements']==sum(p['replacement'] for p in accepted)
    assert summary['replacement_attempts']==sum(p['replacement'] for p in manifest['pages'])
    assert summary['pages_per_decade']=={str(k):v for k,v in sorted(Counter(books[p['book']]['decade'] for p in accepted).items())}
    for rid,b in books.items():
        assert summary['pages_per_book'][rid]==dict(allocated=b['allocation'],accepted=sum(p['book']==rid for p in accepted),decision='RESCUED')
    assert summary['ocr_service_calls']==0
    combined=d.read(d.BASE/'manifest_all.json')
    expected_union=[dict(p,origin=origin) for origin,m in [('t16',baseline),('rescue',manifest)]
                    for p in m['pages'] if p['harvest_accepted']]
    assert isinstance(combined,list) and combined==expected_union
    assert len({(p['book'],p['page']) for p in combined})==len(combined)
    look=d.read(d.OUT/'look_manifest.json');assert len(look)==len(accepted)
    for row,p in zip(look,accepted):
        assert (row['book'],row['page'])==(p['book'],p['page'])
        assert ROOT/row['path']==d.LOOK/look_relative(books[p['book']],p)
        assert d.sha(ROOT/row['path'])==row['sha256']==p['gate']['image_sha256']
    expected_paths={str(ROOT/r['path']) for r in look}
    actual_paths={str(p) for p in d.LOOK.glob('accepted/*/RESCUED_*/*.png')}
    assert expected_paths==actual_paths
    assert (d.BIG/'anemi_http').resolve()==(d.BIG.parent/'anemi_http').resolve()
    transport=d.t16.rows(d.BIG/'anemi_http/transfer.jsonl')
    gaps=[]
    for a,b in zip(transport,transport[1:]):
        gap=(dt.datetime.fromisoformat(b['request_started_at'])-dt.datetime.fromisoformat(a['request_started_at'])).total_seconds()
        assert gap>=1.99;gaps.append(gap)
    assert all(urlsplit(r['url']).scheme=='https' and urlsplit(r['url']).netloc=='anemi.lib.uoc.gr' for r in transport)
    own=[r for r in transport if r['request_started_at']>=summary['started_at']]
    tests=ET.parse(d.OUT/'tests.xml').getroot()
    suites=list(tests) if tests.tag=='testsuites' else [tests]
    assert sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in suites)==0
    count=sum(int(s.get('tests',0))-int(s.get('skipped',0)) for s in suites)
    return dict(ok=True,books=len(books),pages_fetched=len(seen),pages_accepted=len(accepted),
                combined_pages=len(combined),look_images=len(look),native_pdf_rasters_verified=len(seen),
                replacements=summary['replacements'],tests_passed=count,ocr_service_calls=0,
                transport_requests=len(own),transport_statuses=dict(Counter(r['status'] for r in own)),
                minimum_shared_request_gap_seconds=min(gaps),fetch_minutes=summary['fetch_minutes'])


if __name__=='__main__':
    result=validate()
    d.atomic(d.OUT/'validation.json',result)
    print(__import__('json').dumps(result,indent=2))
