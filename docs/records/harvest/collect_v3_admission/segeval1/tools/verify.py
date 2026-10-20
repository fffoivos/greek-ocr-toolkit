"""Read-only artifact custody, deterministic draw replay, and pack closure."""
import json,random,sys,hashlib
from pathlib import Path
from common import sha,rows
from scan_rollout import integrity
D=Path(__file__).resolve().parents[1]
r=json.loads((D/'draw_receipt.json').read_text());seal=D/'keys/sealed_decisions.jsonl'
assert sha(seal)==r['seal_sha256'];draw=rows(seal)
assert len(draw)==150 and len({x['row_id'] for x in draw})==150
excluded=set((D/'keys/excluded_ids.txt').read_text().splitlines());assert not excluded&{x['row_id'] for x in draw}
rng=random.Random(20261019);replay=[]
for v,n in [('DROP',50),('KEEP',100)]:
 p=D/f'keys/candidate_order_{v}.jsonl';assert sha(p)==r['candidate_order_hashes'][v]
 order=rows(p);assert len(order)==r['pool_sizes'][v] and len({x['row_id'] for x in order})==len(order)
 reproduced=rng.sample(sorted(order,key=lambda x:x['row_id']),len(order))
 assert reproduced==order
 replay.extend(x['row_id'] for x in order[:n])
assert replay==[x['row_id'] for x in draw]
manifest=rows(D/'crops_manifest.jsonl');assert len(manifest)==150
assert {x['row_id'] for x in manifest}=={x['row_id'] for x in draw}
for m in manifest:assert sha(D/m['path'])==m['sha256'] and (D/m['path']).stat().st_size==m['bytes']
assert not json.loads((D/'crop_failures.json').read_text())
assert seal.stat().st_mtime_ns<min((D/m['path']).stat().st_mtime_ns for m in manifest)
closure=json.loads((D/'pack_closure.json').read_text());root=Path(closure['pack_root'])
keys={};study_ids=set();controls=[]
for bed in closure['manifests']:
 directory=root/bed/'r1';errors,skipped=integrity(directory);assert not errors and not skipped
 assert not (directory/'answers.jsonl').exists()
 key=json.loads((D/'keys'/f'{bed}.json').read_text());cards=rows(directory/'cards.jsonl')
 assert [c['card_id'] for c in cards]==key['order'] and len(cards)==80
 for c in cards:
  assert set(c)=={'card_id','crop','google_text','word_scripts'}
  assert sha(directory/c['crop'])==Path(c['crop']).stem
  m=key['items'][c['card_id']]
  if m['control']:controls.append(m['row_id'])
  else:assert m['row_id'] not in study_ids;study_ids.add(m['row_id'])
assert len(study_ids)==150 and len(controls)==len(set(controls))==10 and not set(controls)&study_ids
for binding in json.loads((D/'keys/exclusion_sources.json').read_text()):
 assert sha(Path(binding['path']))==binding['sha256'],'exclusion source drift: '+binding['path']
P=D.parents[3].parent
assert sha(P/'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/segmentation-policy.js')=='8334dd4028822edbd740a1a96a0ead6367c7af953e545bad8bd60a911c65a819'
reference=P/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/prompts/bsb.md'
assert sha(reference)==sha(D/'prompts/bsb.md')
assert sha(D/'tools/scan_rollout.py')=='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
result=dict(status='PASS',study=150,controls=10,crops=150,replacements=0,draw_replayed=True,seal_sha256=sha(seal),seal_mtime_ns=seal.stat().st_mtime_ns,earliest_crop_mtime_ns=min((D/m['path']).stat().st_mtime_ns for m in manifest),original_png_sha256_verified=150,pack_integrity='pass both contexts',reader_answers_present=0,verbatim_bsb_sha256=sha(reference),blind_archive_sha256=sha(D/'blind_packs.tar.gz'),pipeline_population_gzip_sha256=sha(D/'keys/pipeline_population.jsonl.gz'),original_metadata_gzip_sha256=sha(D/'keys/original_metadata.jsonl.gz'))
(D/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
