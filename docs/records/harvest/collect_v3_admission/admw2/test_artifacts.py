"""Full real-artifact checks; run after builder and both staging passes."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import pytest
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
import build_release_admission as b


def rows(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as f:
        for line in f:
            if line.strip():yield json.loads(line)

@pytest.fixture(scope='module')
def artifacts():
    out={}
    for name in ('w1_originals_v3_screened','w2_originals_v3','gazette_w2_originals_v3'):
        receipt=json.loads((BASE/(name+'_receipt.json')).read_text())
        out[name]=(receipt,list(rows(BASE/receipt['files'][0]['path'])),list(rows(BASE/receipt['files'][1]['path'])))
    return out


def test_actual_population_exact_and_exclusions(artifacts):
    excluded,_,_=b.exclusions(b.EXCLUSIONS)
    for name,wave in [('w1_originals_v3_screened','W1'),('w2_originals_v3','W2')]:
        expected=set()
        for r in rows(b.SNAPSHOTS/f'{wave}_features_20261018_0524.jsonl'):
            if b.included(r,wave) and r['id'] not in excluded:expected.add(r['id'])
        receipt,decisions,admitted=artifacts[name]
        actual={r['row_id'] for r in decisions}
        assert len(actual)==len(decisions)
        assert actual==expected
        assert not actual&excluded
        assert {r['row_id'] for r in admitted}=={r['row_id'] for r in decisions if r['pass']}


def test_all_output_byte_hashes(artifacts):
    for receipt,decisions,admitted in artifacts.values():
        for info in receipt['files']:
            path=BASE/info['path'];assert b.sha(path)==info['sha256']
            h=hashlib.sha256();size=0;n=0
            opener=gzip.open if path.suffix=='.gz' else open
            with opener(path,'rb') as stream:
                for line in stream:h.update(line);size+=len(line);n+=1
            assert h.hexdigest()==info['uncompressed_sha256']
            assert size==info['uncompressed_bytes'] and n==info['rows']
            assert (size>50_000_000)==(path.suffix=='.gz')


def test_all_counts_reconcile_and_gazette_exact(artifacts):
    for receipt,decisions,admitted in artifacts.values():
        for group,stat in [('all',receipt['totals']),*receipt['counts_per_source_class'].items()]:
            rr=decisions if group=='all' else [r for r in decisions if r['source']+'|'+r['primary_class']==group]
            assert len(rr)==stat['pre_screen_n']
            assert sum(r['pass'] for r in rr)==stat['admitted_n']
            assert sum(not r['pass'] for r in rr)==stat['dropped_n']
            hits=Counter(k for r in rr for k in r['rules_failed'])
            first=Counter(r['rules_failed'][0] for r in rr if r['rules_failed'])
            assert all(stat['dropped_per_rule'][k]==hits[k] for k in b.DROP_ORDER)
            assert all(stat['first_drop'][k]==first[k] for k in b.DROP_ORDER)
            assert stat['admitted_n']+sum(first.values())==len(rr)
            assert sum(r['geometry_unavailable'] for r in rr)==stat['geometry_unavailable_n']
            assert stat['unavailable_share']==(stat['geometry_unavailable_n']/len(rr) if rr else 0)
            assert sum(r['orientation_unknown'] for r in rr)==stat['orientation_unknown_n']
            assert sum(r['edge_clip_candidate'] is True for r in rr)==stat['edge_clip_candidate_n']
        assert all(not r['geometry_unavailable'] and r['orientation'] is not True and not r['rules_failed'] for r in decisions if r['pass'])
    _,w2,w2a=artifacts['w2_originals_v3'];_,gaz,gaza=artifacts['gazette_w2_originals_v3']
    assert gaz==[r for r in w2 if r['source']=='gazette_modern']
    assert gaza==[r for r in w2a if r['source']=='gazette_modern']


def test_staged_sha_and_every_deferred_row_accounted(artifacts):
    manifest={r['row_id']:r for r in rows(BASE/'crops_manifest.jsonl')}
    for name in ('w1_originals_v3_screened','w2_originals_v3'):
        receipt,_,admitted=artifacts[name]
        stage=json.loads((BASE/(name+'_admitted_crops_receipt.json')).read_text())
        deferred=list(rows(BASE/(name+'_admitted_crops_deferred.jsonl')))
        assert stage['admitted_sha256']==receipt['files'][1]['uncompressed_sha256']
        assert stage['features_sha256']==receipt['inputs'][stage['features_file']]
        assert stage['failures']==0
        wanted={r['row_id'] for r in admitted}
        present=wanted&manifest.keys();missing=wanted-present
        assert missing=={r['row_id'] for r in deferred}
        assert len(present)==stage['count']
        assert stage['admitted_count']==len(present)+stage['disk_deferred']
        assert stage['minimum_free_gb']==10
        if stage['free_before']<10_000_000_000:assert stage['new_count']==0
        for r in admitted:
            if r['row_id'] not in present:continue
            m=manifest[r['row_id']];p=BASE/m['path']
            assert m['admitted'] is True
            assert m['path']==f"crops/{r['source']}/{r['row_id']}.png"
            assert b.sha(p)==m['sha256']==r['crop_sha256']
            assert m['bytes']==p.stat().st_size


def test_existing_w1_admitted_untouched():
    assert b.sha(BASE/'w1_originals_v3_admitted.jsonl')=='b6d13fa8bb4b07be632e299fd650cd75dd80348ecf0e0fd9e5cb34bdb6c72bfe'
