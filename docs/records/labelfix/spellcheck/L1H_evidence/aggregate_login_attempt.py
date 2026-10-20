"""Read-only, one-process Clariden aggregation; stdout is aggregates + <=60 lines."""
import collections as C
import datetime, gzip, hashlib, json, pathlib, resource, signal, socket, sys, time
BASE=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
REL=BASE/'l1e_20261017/output_3679545/recomposition/release'
SOURCE=BASE.parent/'collection_v2/import_real_v2_train.jsonl'
WAVES=('round1','round2','parliament','vouli','mixed','openarchives')
MODES=('ensemble_ab','presence','full')
started=time.monotonic(); cpu0=time.process_time()
def abort(signum=None,frame=None):
 print(json.dumps({'complete':False,'stop':'240-second login-node wall limit','elapsed_s':time.monotonic()-started}),flush=True)
 raise SystemExit(124)
signal.signal(signal.SIGALRM,abort); signal.alarm(240)
class HashReader:
 def __init__(self,p): self.f=open(p,'rb'); self.h=hashlib.sha256()
 def read(self,n=-1):
  b=self.f.read(n); self.h.update(b); return b
 def close(self): self.f.close()
def stat(p):
 s=p.stat(); return {'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'inode':s.st_ino}
def blank():
 return {'status':C.Counter(),'raw_slots':C.Counter(),'raw_lines':C.Counter(),'raw_sole':C.Counter(),'raw_sets':C.Counter(),
         'broad_slots':C.Counter(),'broad_lines':C.Counter(),'broad_sole':C.Counter(),'broad_sets':C.Counter(),
         'family_slots':C.Counter(),'family_lines':C.Counter(),'family_sole':C.Counter(),'family_sets':C.Counter(),
         'unique_held_slots':0,'reason_entries':0,'duplicate_slot_reason_entries':0,'held_slots_per_line':C.Counter()}
def family(s):
 if s.startswith('edit_guard:'): return 'edit_guard:*'
 if s.startswith('K1:'): return 'K1:*'
 if s.startswith('r1_uncertainty:'): return 'r1_uncertainty:*'
 if s.startswith('r1_b_uncertainty:'): return 'r1_b_uncertainty:*'
 return s
meta={}; sh=hashlib.sha256(); source_stat=stat(SOURCE); source_keys=None
with open(SOURCE,'rb') as f:
 for b in f:
  sh.update(b); r=json.loads(b)
  if source_keys is None: source_keys=sorted(r)
  if r['id'] in meta: raise ValueError('duplicate source id')
  meta[r['id']]={'wave':r.get('wave'), 'crop':r.get('crop',r.get('image',r.get('crop_path')))}
assert source_stat==stat(SOURCE)
print('source joined: %d lines in %.2fs' % (len(meta),time.monotonic()-started),file=sys.stderr,flush=True)
result={'schema':'l1h-hold-aggregation-v1','complete':False,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'host':socket.gethostname(),'source':{'path':str(SOURCE),'sha256':sh.hexdigest(),'stat':source_stat,'rows':len(meta),'keys':source_keys},
 'release':str(REL),'wave_order':WAVES,'modes':{},'samples':{},'max_samples':60,'raw_to_broad':{},'invariants':[]}
samples=result['samples']; selected_tags=set()
TARGETS=('detector_clipped_top','detector_clipped_bottom','detector_segmentation_uncertain','detector_localisation_unknown',
         'detector_unnamed_mark','K1:*','edit_guard:*','ensemble_ab_mark_set_disagreement','r1_evidence_UNKNOWN','r1_uncertainty:*','r1_b_uncertainty:*')
seen_ref=None
for mode in MODES:
 p=REL/('overlay_'+mode+'.jsonl.gz'); before=stat(p); t=time.monotonic()
 manifest_path=REL/('release_'+mode+'.json'); mb=manifest_path.read_bytes(); manifest=json.loads(mb)
 assert manifest['source_sha256']==sh.hexdigest(), 'source identity mismatch'
 buckets={w:blank() for w in (*WAVES,'ALL')}; seen=set(); raw_bytes=0
 stream=HashReader(p)
 try:
  with gzip.GzipFile(fileobj=stream,mode='rb') as f:
   for n,b in enumerate(f,1):
    raw_bytes+=len(b); r=json.loads(b); ident=r['line_id']; status=r['status']
    assert ident in meta and ident not in seen, 'missing source or duplicate line'
    seen.add(ident); wave=meta[ident]['wave']; assert wave in WAVES, wave
    hs=r['hold_slots']; rawset={s['detail'] for s in hs}; broadset={s['reason'] for s in hs}; famset={family(s) for s in rawset}
    assert bool(hs)==(status=='hold'), 'hold/status mismatch'
    rawpairs={(s['start'],s['letter'],s['detail']) for s in hs}
    broadpairs={(s['start'],s['letter'],s['reason']) for s in hs}
    fampairs={(s['start'],s['letter'],family(s['detail'])) for s in hs}
    for s in hs: result['raw_to_broad'].setdefault(s['detail'],set()).add(s['reason'])
    for w in (wave,'ALL'):
     c=buckets[w]; c['status'][status]+=1
     if status!='hold': continue
     c['unique_held_slots']+=len({(s['start'],s['letter']) for s in hs})
     c['reason_entries']+=len(hs); c['duplicate_slot_reason_entries']+=len(hs)-len(rawpairs)
     c['held_slots_per_line'][len({(s['start'],s['letter']) for s in hs})]+=1
     for prefix,pairs,ss in (('raw',rawpairs,rawset),('broad',broadpairs,broadset),('family',fampairs,famset)):
      c[prefix+'_slots'].update(x[2] for x in pairs)
      c[prefix+'_lines'].update(ss)
      c[prefix+'_sets'][tuple(sorted(ss))]+=1
      if len(ss)==1: c[prefix+'_sole'].update(ss)
    tags=[]
    if status=='hold':
     tag=(mode,wave,'first_held')
     if tag not in selected_tags: tags.append(tag)
     if mode=='ensemble_ab':
      for target in TARGETS:
       tag=(mode,wave,target)
       if target in famset and tag not in selected_tags: tags.append(tag)
      tag=(mode,wave,'sole_raw_reason')
      if len(rawset)==1 and tag not in selected_tags: tags.append(tag)
    if tags and (ident in samples or len(samples)<60):
     s=samples.setdefault(ident,{'line_id':ident,'wave':wave,'source_crop':meta[ident]['crop'],'selection_tags':[],'modes':{}})
     selected_tags.update(tags); s['selection_tags'].extend(tags)
    if ident in samples:
     samples[ident]['modes'][mode]={'status':status,'raw_reason_set':sorted(rawset),'broad_reason_set':sorted(broadset),
        'hold_slots':hs,'original_label_sha256':r.get('original_label_sha256'),'policy_sha':r.get('policy_sha')}
    if n%10000==0:
     print('%s %d rows %.1fs (total %.1fs)' % (mode,n,time.monotonic()-t,time.monotonic()-started),file=sys.stderr,flush=True)
    if n==8192:
     ratio=(time.monotonic()-t)/n
     current_left=ratio*(124669-n)
     other=sum({'ensemble_ab':73.84,'presence':57.75,'full':56.25}[m] for m in MODES[MODES.index(mode)+1:])
     projected=time.monotonic()-started+current_left+other
     print('bounded forecast %.1fs' % projected,file=sys.stderr,flush=True)
     if projected>240:
      print(json.dumps({'complete':False,'stop':'forecast exceeds 240 seconds','forecast_s':projected,'rows':n,'mode':mode}),flush=True)
      raise SystemExit(124)
 finally: stream.close()
 assert before==stat(p), 'overlay changed during read'
 assert stream.h.hexdigest()==manifest['overlay_sha256'], 'overlay sha mismatch'
 assert dict(buckets['ALL']['status'])=={k:v for k,v in manifest['counts_by_status'].items() if v}, 'status totals'
 for wave in WAVES:
  for k,v in manifest['coverage_per_wave'][wave].items():
   if k in ('corrected','unchanged','hold','out_of_scope'): assert buckets[wave]['status'][k]==v,(mode,wave,k)
 if seen_ref is None: seen_ref=seen
 else: assert seen==seen_ref, 'mode population mismatch'
 cooked={}
 for wave,c in buckets.items():
  assert sum(c['raw_sets'].values())==c['status']['hold']
  assert sum(c['raw_sole'].values())==sum(v for k,v in c['raw_sets'].items() if len(k)==1)
  assert sum(c['raw_slots'].values())==c['reason_entries']-c['duplicate_slot_reason_entries']
  cooked[wave]={k:([{'reasons':list(ss),'lines':v} for ss,v in sorted(x.items(),key=lambda z:(-z[1],z[0]))] if k.endswith('_sets') else dict(x) if isinstance(x,C.Counter) else x) for k,x in c.items()}
 result['modes'][mode]={'overlay':str(p),'overlay_stat':before,'overlay_sha256':stream.h.hexdigest(),
  'manifest_sha256':hashlib.sha256(mb).hexdigest(),'manifest':manifest,'rows':len(seen),'uncompressed_bytes':raw_bytes,
  'elapsed_s':time.monotonic()-t,'waves':cooked}
result['raw_to_broad']={k:sorted(v) for k,v in sorted(result['raw_to_broad'].items())}
result['invariants']=['all overlay compressed SHA256 match their manifests','source SHA256 matches every manifest',
 'identical unique line populations across modes','all ids join exactly to requested waves',
 'status totals and per-wave statuses match manifests','hold iff hold_slots nonempty',
 'raw reason-set partitions sum to held lines','sole raw reason totals equal singleton reason-set totals',
 'slot counts deduplicate line/start/letter/detail','source and overlay stat unchanged during reads']
result['elapsed_s']=time.monotonic()-started; result['cpu_s']=time.process_time()-cpu0
result['maxrss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
result['sample_line_count']=len(samples); result['complete']=True
signal.alarm(0)
# Manifests contain large historical code maps. Keep release-relevant readback only.
for m in result['modes'].values():
 m['manifest']={k:v for k,v in m['manifest'].items() if k in ('schema','release','variant','overlay_sha256','counts_by_status','coverage_per_wave','kept_lines','source_sha256','selection_sha256','policy_binding','hold_policy')}
print(json.dumps(result,ensure_ascii=False,separators=(',',':')))
