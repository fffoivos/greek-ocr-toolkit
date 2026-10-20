import json,pathlib,re,unicodedata as u
root=pathlib.Path.home()/'Projects/collect-v3-data/run'
found=[];target=[]
for p in root.glob('W*/c1/*_key.json'):
 try:d=json.loads(p.read_text())
 except (ValueError,OSError):continue
 for card,r in d.items():
  if not isinstance(r,dict):continue

  t=r.get('literal_label','');t=u.normalize('NFD',t)
  if re.search('["“«][Α-Ω][\u0313\u0314]',t):found.append(dict(key=str(p),card=card,**r))
  if r.get('line_id')=='nlg--f4b52df5f8130047--s005-l0015':target.append(dict(key=str(p),card=card,**r))
pathlib.Path('artifacts/sq1/c1_search.json').write_text(json.dumps(dict(criterion='literal Google label quote immediately before capital plus combining breathing; candidates require pixel verification',candidates=found,target=target),ensure_ascii=False,indent=2))
print(json.dumps(found[:8],ensure_ascii=False,indent=2));print('TOTAL',len(found))
