import collections, gzip, hashlib, json, pathlib, socket, time
base=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
root=base/'l1e_20261017/output_3679545/recomposition'
out={'host':socket.gethostname(),'release':str(root/'release'),'pilot':{}}
for mode in ('presence','full','ensemble_ab'):
 p=root/'release'/('overlay_'+mode+'.jsonl.gz')
 t=time.monotonic(); n=0; size=0; reason=collections.Counter(); fields=collections.Counter()
 with gzip.open(p,'rb') as f:
  for raw in f:
   r=json.loads(raw); n+=1; size+=len(raw)
   for s in r.get('hold_slots',[]):
    fields.update(s.keys()); reason.update([s.get('reason','<missing>')])
   if n==1:
    projection={k:v for k,v in r.items() if k not in ('changes','hold_slots','slot_evidence','evidence')}
    projection['keys']=list(r); projection['hold_slots_first_3']=r.get('hold_slots',[])[:3]
    out.setdefault('schema_samples',{})[mode]=projection
   if n>=1024: break
 elapsed=time.monotonic()-t
 out['pilot'][mode]={'rows':n,'uncompressed_bytes':size,'elapsed_s':elapsed,'projected_full_seconds':elapsed*124669/n,'compressed_file_bytes':p.stat().st_size,'hold_entry_fields':dict(fields),'reason_counts':dict(reason)}
 p=root/'release'/('release_'+mode+'.json')
 r=json.loads(p.read_text())
 out.setdefault('manifests',{})[mode]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'data':{k:v for k,v in r.items() if k in ('schema','variant','overlay','overlay_sha256','counts_by_status','coverage_per_wave','kept_lines','source_label_file','source_sha256','selection_sha256','policy_binding','policy_sha','r1_sha','release','hold_policy')}}
for p in (base/'docs/labelfix/DIRECTION_DECISION_20261017.md',base/'l1e_20261017/docs/labelfix/DIRECTION_DECISION_20261017.md'):
 if p.is_file(): out['direction_reference']={'path':str(p),'text':p.read_text()}
for sub in ('','l1e_20261017'):
 for name in ('greekocr/labelfix/release_gate.py','scripts/labelfix/clariden/l1r_recompose.py'):
  p=base/sub/name
  if p.is_file(): out.setdefault('source_readback',[]).append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text':p.read_text()})
print(json.dumps(out,ensure_ascii=False,indent=2))
