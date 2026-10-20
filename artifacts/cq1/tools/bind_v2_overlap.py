"""Bind qualification glyph ordinals to exact saved recogniser slot identities."""
import collections,gzip,json,sys,unicodedata as U
from pathlib import Path
from common import ROOT,rows,dump,jsonl,sha
W=ROOT.parents[1];sys.path.insert(0,str(W))
from scripts.labelfix.r2_finalize_manifest import unique_alignment
from scripts.labelfix.r2_cards_resolve import letters
key=json.loads((ROOT/'keys/cap1.json').read_text());items=key['items'];needed={v['line_id'] for v in items.values()}
labels={r['id']:r['label'] for r in rows(W/'docs/labelfix/spellcheck/R2/eligible_lines.jsonl') if r['id'] in needed}
run=W.parent/'greek-ocr-toolkit-spellcheck-r2prep/artifacts/labelfix_r2/output_3681404'
bound=json.loads((W/'artifacts/r2a_manifest/receipt.json').read_text())['source_hashes'];align={};used={}
for rel,digest in bound.items():
 if not rel.endswith('-alignments.jsonl.gz'):continue
 p=run/rel
 with gzip.open(p,'rt') as f:found=[r for r in map(json.loads,f) if r['line_id'] in needed]
 if found:
  assert sha(p)==digest
  used[rel]=digest
  for r in found:align[r['line_id']]=r
v2path=W.parent/'greek-ocr-toolkit-spellcheck-r2prep/artifacts/r2a_manifest/r2a_slots_v2.jsonl'
v2={tuple(r['slot_id']):r for r in rows(v2path)};overlap=[];exclusions=[]
for i,v in items.items():
 a=align.get(v['line_id']);sid=None
 if a:
  assert a['crop_sha256']==v['crop_sha256']
  pred=U.normalize('NFD',a['alignment']['prediction']);starts=[j for j,c in enumerate(pred) if U.category(c) in ('Lu','Ll','Lt','Lo')]
  mapping=unique_alignment(letters(labels[v['line_id']]),[pred[j] for j in starts]);ordinal=v['crop_letter_index']
  if ordinal in mapping:sid=[v['crop_sha256'],starts[mapping[ordinal]]]
 v['slot_id']=sid;v['exact_v2_overlap']=v2.get(tuple(sid)) if sid else None
 if not v['control']:assert v['exact_v2_overlap'],('bed anchor is not in v2',i,sid)
 if v['exact_v2_overlap']:overlap.append(dict(item_id=i,control=v['control'],source_id=v['source_id'],slot_id=sid,manifest_row=v['exact_v2_overlap']))
 exclusions.append(dict(item_id=i,control=v['control'],source_id=v['source_id'],crop_sha256=v['crop_sha256'],crop_letter_index=v['crop_letter_index'],slot_id=sid))
dump(ROOT/'keys/cap1.json',key);dump(ROOT/'keys/v2_overlap.json',overlap);jsonl(ROOT/'keys/topup_exclusions.jsonl',exclusions)
dump(ROOT/'keys/slot_binding_receipt.json',dict(v2_sha256=sha(v2path),alignment_hashes=used,bed_overlap=sum(not v['control'] for v in overlap),control_overlap=sum(v['control'] for v in overlap),unmapped=sum(v['slot_id'] is None for v in items.values())))
print('exact overlap bound',len(overlap))
