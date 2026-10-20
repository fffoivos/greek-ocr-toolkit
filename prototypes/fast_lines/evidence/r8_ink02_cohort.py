import json,hashlib,os,subprocess
from pathlib import Path
R=Path.cwd();S=R.parent/'greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-RUST-02-i1';O=R/'.astra/fast_lines/out/round8/R8-INK-02-i1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (O/'INK02_COHORT.json').exists(), 'preserve the pre-edit frozen cohort'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='6950557bbce4c4611400846154475c827f996862'
for p in (R/'prototypes/fast_lines').rglob('*.py'):
 if '/evidence/' not in str(p) and not p.name.startswith('test_'):
  blob=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))])
  assert hashlib.sha256(blob).hexdigest()==sha(p), 'freeze before runtime editing'
def walk(v,path='$'):
 if isinstance(v,dict):
  if v.get('version')=='B5':yield path,v
  for k,x in v.items():yield from walk(x,path+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from walk(x,path+f'[{i}]')
ids=[r['page'] for r in json.loads((S/'TIMING_PER_PAGE.json').read_text()) if not r['appendix']];assert len(ids)==len(set(ids))==208
inputs=json.loads((R.parent/'greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-01b/inputs-208.json').read_text())['pages'];assert {r['page'] for r in inputs}==set(ids)
rows=[]
for r in sorted(inputs,key=lambda x:x['page']):
 p=S/'same-input/H'/(r['page']+'.evidence.json');d=json.loads(p.read_text());calls=[dict(json_path=k,caller=k,atlas_glyphs=v['atlas_glyphs'],anchors=v['anchors'],suspects=v['suspects'],requested_regions=len(v['regions']),coordinate_frame='original native full page',index_space='requested regions') for k,v in walk(d)]
 assert sha(r['path'])==r['sha256']
 rows.append(dict(r,evidence=str(p),evidence_sha256=sha(p),export=str(p).replace('.evidence.json','.json'),export_sha256=sha(str(p).replace('.evidence.json','.json')),book=r['page'].split('-p')[0],calls=calls,roles=['atlas-active'] if any(c['atlas_glyphs']>0 for c in calls) else []))
books=sorted({r['book'] for r in rows if r['roles']});missing=[]
for book in books:
 negatives=[r for r in rows if r['book']==book and not any(c['atlas_glyphs']>0 for c in r['calls'])]
 if negatives:negatives[0]['roles'].append('same-book-zero-atlas')
 else:missing.append(book)
controls=[('0ce9',1),('93f8',1),('8686',5),('8686',7),('8686',26),('31f40',1),('1be6',215),('3229',2),('4959',5)]
for prefix,page in controls:
 matches=[r for r in rows if r['page'].split('-')[1].startswith(prefix) and int(r['page'].split('-p')[1])==page];assert len(matches)==1,(prefix,page);matches[0]['roles'].append('named-control')
appendix=[]
for r in json.loads((S/'OWNER22_FROZEN.json').read_text())['pages']:
 p=S/'same-input/H'/(r['page']+'.evidence.json');calls=[dict(json_path=k,atlas_glyphs=v['atlas_glyphs']) for k,v in walk(json.loads(p.read_text()))];appendix.append(dict(page=r['page'],path=r['path'],sha256=r['sha256'],evidence=str(p),evidence_sha256=sha(p),calls=calls,export=str(S/'same-input/H'/(r['page']+'.json'))))
source={str(p.relative_to(R)):sha(p) for p in (R/'prototypes/fast_lines').rglob('*.py') if '/evidence/' not in str(p) and not p.name.startswith('test_')}
d=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),thread_id=os.getenv('CODEX_THREAD_ID'),frozen_before_runtime_edit=True,timing_inventory_sha256=sha(S/'TIMING_PER_PAGE.json'),accepted_runtime_binding='6950557 docs merge; RUST i2 confirms 3605b92 equivalent to 5560714 accepted H plus off-default native batch',exposure='development; no held-out validation',denominator=208,pages=rows,cohort_pages=[r['page'] for r in rows if r['roles']],represented_books=books,books_without_negative=missing,owner22_separate=appendix,source=source)
(O/'INK02_COHORT.json').write_text(json.dumps(d,indent=1)+'\n');print('cohort',len(d['cohort_pages']),'active',sum('atlas-active' in r['roles'] for r in rows),'books',len(books),'appendix active',sum(any(c['atlas_glyphs'] for c in r['calls']) for r in appendix));print([(r['page'],[(c['json_path'],c['atlas_glyphs']) for c in r['calls'] if c['atlas_glyphs']]) for r in rows if 'atlas-active' in r['roles']])
