import json,pathlib,collections,bisect,datetime,hashlib,base64,numpy as np,math
R=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run'); O=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/mirror')
def spans(x):return [(int(s.get('startIndex',0)),int(s['endIndex'])) for s in x['layout'].get('textAnchor',{}).get('textSegments',[])]
def cx(x):
 v=x['layout']['boundingPoly'].get('vertices',[]);return sum(p.get('x',0) for p in v)/len(v) if v else None
w1=collections.defaultdict(list)
with (R/'W1/features.jsonl').open() as f:
 for l in f:
  x=json.loads(l);w1[x['page_id']].append({k:x.get(k) for k in ['id','source','page_id','docai_line_index','crop_bbox','crop_sha256','label','candidate_usable','usable_final']})
prior=json.loads((O/'scan.json').read_text()); files={t:[R/t/'pages'/n for n in prior['snapshot_page_files'][t]] for t in ['W1','W2']};out={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'signal':'PAGE_UP line, all overlapping tokens PAGE_UP, >=2 strict adjacent token-centre x decreases in text-anchor order','counts':{},'candidates':[],'page_fields':{},'errors':[]};counts=collections.Counter();ori=collections.Counter(); keys=collections.Counter()
for t in files:
 for pi,p in enumerate(files[t]):
  rec=json.loads(p.read_text())
  if rec.get('status')!='completed':continue
  data=pathlib.Path(rec['response']).read_bytes(); assert hashlib.sha256(data).hexdigest()==rec['response_sha256']; doc=json.loads(data)['document']; pg=doc['pages'][0];
  rows=w1[rec['id']] if t=='W1' else rec.get('rows')
  if rows is None: rows=[dict(id=rec['id']+f'-l{i+1:04d}',docai_line_index=i) for i in range(len(pg.get('lines',[])))]
  if t=='W1': assert len(rows)==len(pg.get('lines',[])),(rec['id'],len(rows),len(pg.get('lines',[])))
  counts[t,'pages',rec['source']]+=1;counts[t,'rows',rec['source']]+=len(rows);ori[t,'page',pg.get('layout',{}).get('orientation','ABSENT')]+=1
  for k in pg:
   if any(s in k.lower() for s in ['transform','orient','mirror']):keys[t,k]+=1
  toks=sorted([(spans(tok)[0][0],tok) for tok in pg.get('tokens',[]) if spans(tok)],key=lambda x:x[0]);starts=[a for a,tok in toks]
  for row in rows:
   li=row['docai_line_index'];line=pg['lines'][li];ss=spans(line);a=min(s[0] for s in ss);z=max(s[1] for s in ss);ts=[tok for _,tok in toks[max(0,bisect.bisect_left(starts,a)-1):bisect.bisect_left(starts,z)] if any(max(c,a)<min(d,z) for c,d in spans(tok))];xs=[cx(tok) for tok in ts];xs=[x for x in xs if x is not None];dec=sum(b<a for a,b in zip(xs,xs[1:])); lo=line['layout'].get('orientation','ABSENT');ori[t,'line',lo]+=1
   if lo=='PAGE_UP' and all(tok['layout'].get('orientation')=='PAGE_UP' for tok in ts) and dec>=2:
    if not row.get('crop_bbox'):
     vs=line['layout']['boundingPoly']['vertices']; points=np.array([[v.get('x',0),v.get('y',0),1.] for v in vs]);total=np.eye(3)
     for tr in pg.get('transforms',[]):
      mat=np.frombuffer(base64.b64decode(tr['data']),dtype='<f4' if tr['type']==5 else '<f8').reshape(tr['rows'],tr['cols']); mat=np.vstack((mat,[0,0,1])) if mat.shape==(2,3) else mat;total=mat@total
     mapped=(np.linalg.inv(total)@points.T).T; mapped=mapped[:,:2]/mapped[:,2:];row['crop_bbox']=[max(0,math.floor(mapped[:,0].min())-2),max(0,math.floor(mapped[:,1].min())-2),math.ceil(mapped[:,0].max())+2,math.ceil(mapped[:,1].max())+2]
    out['candidates'].append(dict(tranche=t,id=row['id'],page_id=rec['id'],source=rec['source'],line_index=li,crop_bbox=row.get('crop_bbox'),crop_sha256=row.get('crop_sha256'),label=row.get('label',doc['text'][a:z]),raw_text=doc['text'][a:z],decreases=dec,token_centres=xs,image=rec['image'],response=rec['response'],candidate_usable=row.get('candidate_usable'),usable_final=row.get('usable_final')))
  if pi%200==0:print(t,pi,flush=True)
out['counts']={'|'.join(k):v for k,v in counts.items()};out['orientations']={'|'.join(k):v for k,v in ori.items()};out['page_special_fields']={'|'.join(k):v for k,v in keys.items()};out['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out['snapshot_page_files']={t:[p.name for p in files[t]] for t in files};(O/'scan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('DONE',len(out['candidates']),len(set(x['page_id'] for x in out['candidates'])),out['counts'],out['orientations'])
