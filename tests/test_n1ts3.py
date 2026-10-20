"""Third independent votes, preserved scan exclusion, lead authority and size cap."""
import copy
import json
from collections import Counter
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
import n1ts3
from greekocr.numerics.combine_v2 import decide
from test_n1t import owner_fixture,vote

@pytest.mark.parametrize('meanings,expected',[
    (['raised dot','baseline dot','raised dot'],'raised dot'),
    (['raised dot','raised dot','baseline dot'],'raised dot'),
    (['raised dot','baseline dot','comma'],None),
    (['nothing','nothing','nothing'],'nothing')])
def test_two_of_three(meanings,expected,tmp_path):
    _,slots,_=owner_fixture(tmp_path)
    s=next(s for s in slots if s['glyph']=='-')
    d=decide(s,[vote(r,meaning=m) for r,m in zip(('r1','r2','r3'),meanings)])
    assert d['truth_candidate']==expected

@pytest.mark.parametrize('bad', ['VOID','INVALID','low'])
def test_unusable_r3_cannot_break_tie(bad,tmp_path):
    _,slots,_=owner_fixture(tmp_path);s=next(s for s in slots if s['glyph']=='-')
    votes=[vote('r1',meaning='raised dot'),vote('r2',meaning='baseline dot'),vote('r3',meaning='raised dot')]
    if bad=='low':votes[-1]['confidence']='low'
    else:votes[-1]['context_status']=bad
    assert decide(s,votes)['truth_candidate'] is None

@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@c5f864222; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_all_scans_reconciled_and_no_new_voids():
    receipt=json.loads((_data_input(n1ts3.BASE/'N1TS3_SCANS.json')).read_text())
    assert receipt['scanner_sha256']==n1ts3.EXPECTED
    rr=receipt['records']
    assert len(rr)==len(list((n1ts3.BASE/'answers').rglob('*.run.json')))
    assert all(r['new_ok'] for r in rr if r['old_ok'])
    for r in rr:
        p=ROOT/r['run'];scan=p.with_name(p.name.replace('.run.json','.scan.json'))
        assert n1ts3.sha(scan)==r['new_scan_sha256']
        assert json.loads(_data_input(scan).read_text())['violations']==r['new_findings']
        if not r['new_ok']:assert r['disposition']=='VOID'

@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@c5f864222; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_actual_combination_authority_and_independence():
    slots,before,after,g2,g3=n1ts3.combine()
    assert len(g3)==6 and len(after)==len(slots)==2129
    assert all(g['control_status'] in ('VALID','VOID') for g in g3.values())
    lead={r['slot_id']:r for r in n1ts3.rows(n1ts3.BASE/'lead_t.jsonl')}
    for d in after:
        assert len(d['reads'])==len({r['reader'] for r in d['reads']})
        assert not d['apply_edit'] and d['edit'] is None
        if d['line_id']==n1ts3.MIRROR:
            assert d['truth_candidate'] is None and d['edit_candidate'] is None and d['status']=='excluded'
        elif d['slot_id'] in lead:
            assert d['truth_candidate']==(None if lead[d['slot_id']]['truth']=='hold' else lead[d['slot_id']]['truth'])
        elif d['truth_candidate'] is not None and d['reads']:
            assert sum(r['context_status']=='VALID' and r['confidence']=='high' and r['meaning']==d['truth_candidate'] for r in d['reads'])>=2

@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@c5f864222; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_review_sheets_complete_and_templates_unfilled():
    r=json.loads((_data_input(n1ts3.BASE/'N1TS3_RECEIPT.json')).read_text())
    _,before,after,_,_=n1ts3.combine();bb={d['slot_id']:d for d in before}
    ruled={d['slot_id'] for d in n1ts3.rows(n1ts3.BASE/'lead_t.jsonl')}
    raised={d['slot_id'] for d in after if d['truth_candidate']=='raised dot' and bb[d['slot_id']]['truth_candidate']!='raised dot' and d['slot_id'] not in ruled and any(v['reader']=='r3' for v in d['reads'])}
    assert set(r['sheets']['raised_r3']['slot_ids'])==raised
    for name in ('geo_audit','raised_r3'):
        info=r['sheets'][name];p=Path(info['path']);assert n1ts3.sha(p)==info['sha256']
        cells=n1ts3.rows(p.with_name(name+'_template.jsonl'))
        assert len(cells)==info['cells'] and all(c['truth'] is None for c in cells)
        assert all(c['geometry'] and c['reads'] for c in cells)
        if name=='geo_audit':assert len(cells)==17 and sum(c['anchor'] for c in cells)==4

def test_sheet_cap_native_rasters_and_jpeg85():
    require_file('artifacts/n1/owner_sheet/n1_sheet.html')
    import base64,io,re
    from PIL import Image
    r=json.loads((_data_input(n1ts3.BASE/'N1TS3_RECEIPT.json')).read_text());owner=r['owner']
    p=n1ts3.BASE/'owner_sheet/n1_sheet.html'
    assert _data_input(p).stat().st_size==owner['sheet_bytes']<=14_000_000
    assert n1ts3.sha(p)==owner['hashes']['n1_sheet.html']
    cards=json.loads((_data_input(p.parent/'cards.json')).read_text())
    assert len(cards)==owner['cards']
    html=_data_input(p).read_text();images=re.findall(r'<img src="(data:image/[^\"]+)"',html)
    assert len(images)==len(cards) # zoom images carry a class before src
    byid={c['line_id']:c for c in cards}
    ordered=[c for g in json.loads((_data_input(p.parent/'spec.json')).read_text())['groups'] for c in cards if c['group']==g['id']]
    for uri,c in zip(images,ordered):
        with Image.open(io.BytesIO(base64.b64decode(uri.split(',')[1]))) as image, Image.open(_data_input(c['image'])) as source:
            assert image.size==(source.width,source.height+30)
    assert 'suspect:mirrored' in html
    assert 'boxes with a dashed outline are gaps we have not decided yet' in html
    assert 'data-legacy-note-ids=' in html
    for c in cards:
        for z in c['zooms']:
            assert z['image'].startswith('data:image/jpeg;')
            with Image.open(io.BytesIO(base64.b64decode(z['image'].split(',')[1]))) as im:
                assert im.format=='JPEG' and im.quantization[0][0]==5 # Pillow quality 85
