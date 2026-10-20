"""Compare all 50 frozen mock outputs and discrete decisions without tolerance."""
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
R=BASE/'receipts'
expected={r['id']:r for r in map(json.loads,(R/'mock_50.jsonl').read_text().splitlines())}
assert len(expected)==50
results={}
for host in ('mac','remote'):
    out=BASE/'work'/('mock_'+host)
    execution=json.loads((out/'execution.json').read_text())
    assert execution['ok'] and execution['crops']==50 and execution['pages']==50
    records={}
    for p in sorted((out/'page-lines').glob('*.guarded.jsonl')):
        for line in p.read_text().splitlines():
            r=json.loads(line)
            assert r['id'] not in records
            assert r['original_sha256']==expected[r['id']]['crop_sha256']
            assert r['host'] and r['code_tree_sha']=='63c640a3aa4abe08d200258cf24d235dfa4a1625'
            if host=='mac':
                assert hashlib.sha256((out/r['masked_path']).read_bytes()).hexdigest()==r['output_sha256']
            records[r['id']]=r
    assert set(records)==set(expected)
    results[host]=records
fields=('output_sha256','guard_status','match_status','wrong_line_risk','masked_pixel_count','masked_component_count')
differences=[]
for id in sorted(expected):
    diff={k:dict(mac=results['mac'][id].get(k),remote=results['remote'][id].get(k))
          for k in fields if results['mac'][id].get(k)!=results['remote'][id].get(k)}
    if diff:
        differences.append(dict(id=id,wave=expected[id]['wave'],differences=diff))
receipt=dict(seed=20261017,crops=50,pages=50,compared_fields=fields,byte_identical=50-sum('output_sha256' in r['differences'] for r in differences),
    all_equal=not differences,differences=differences,
    mac_guarded=sum(r['wrong_line_risk'] for r in results['mac'].values()),
    remote_guarded=sum(r['wrong_line_risk'] for r in results['remote'].values()))
(R/'mock_comparison.json').write_text(json.dumps(receipt,indent=2)+'\n')
for host,rows in results.items():
    (R/('mock_'+host+'_records.jsonl')).write_text(''.join(json.dumps(rows[id],sort_keys=True)+'\n' for id in sorted(rows)))
print(json.dumps(receipt))
