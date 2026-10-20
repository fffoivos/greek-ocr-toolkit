import hashlib,json
from pathlib import Path
from greekocr.labelfix.release_gate import policy_binding,_render_reading,edit_guard
p=Path('artifacts/sq1')
r=json.loads((p/'line_result.json').read_text());raw=json.loads((p/'runtime.json').read_text());side=json.loads((p/'owner_side.json').read_text())
assert raw['detector']==side['raw_line_reading']
assert r['policy']['sha256']==policy_binding()['sha256']=='6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
a=next(s for s in raw['detector']['slots'] if s['base']=='Α')
assert a['display_slot']==19 and [b['source_ids'] for b in a['evidence']['above']]==[[5],[6]]
assert next(q for q in raw['r1_predictions'] if q['base']=='Α')['parts']==['psili','acute']
assert all(x['status']=='hold' for x in r['overlays'].values())
assert _render_reading('"Αδεια',[dict(start=1,parts=['psili','acute'])])=='"Ἄδεια'
protected=json.loads((p/'protected_before.json').read_text());assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in protected.items())
print('Verified: raw owner evidence equality; policy frozen; Alpha owns both blobs; reader psili+acute; PRESENCE/FULL HOLD; conditional quote kept.')
