"""Fail-closed CQ4 pack custody and public-schema check."""
import json,re
from pathlib import Path
from PIL import Image
from build import sha,dump,SCANNER_SHA
FIELDS={'item_id','word_image','line_image','breathing_options','accent_options'}
def scan(rd,private,write=True):
 rd=Path(rd);errors=[];files={};expected={'items.jsonl','README.md','answer_schema.json'}
 data=[json.loads(s) for s in (rd/'items.jsonl').read_text().splitlines()]
 if len(data)>100 or len(data)<11:errors.append('context size')
 if [r['item_id'] for r in data]!=list(private):errors.append('assignment order')
 if sum(bool(x.get('control')) for x in private.values())!=10:errors.append('control count')
 if len(private)!=len(data):errors.append('duplicate IDs')
 for r in data:
  if set(r)!=FIELDS or not re.fullmatch(r'k[0-9a-f]{10}',r['item_id']):errors.append('public schema')
  if r!=private[r['item_id']]['public']:errors.append('public differs from key')
  for field,values in [('breathing_options',{'none','smooth','rough','unreadable'}),('accent_options',{'none','acute','grave','circumflex','unreadable'})]:
   if set(r[field])!=set('ABCDE'[:len(values)]) or set(r[field].values())!=values:errors.append('options')
  for field in ('word_image','line_image'):
   p=r[field]
   if not re.fullmatch(r'img/[0-9a-f]{64}\.png',p):errors.append('unsafe image path')
   expected.add(p)
 for p in rd.rglob('*'):
  rel=str(p.relative_to(rd))
  if p.is_symlink():errors.append('symlink '+rel)
  if p.is_dir():
   if rel!='img':errors.append('unexpected directory '+rel)
   continue
  if rel not in expected:errors.append('unexpected file '+rel)
  if p.stat().st_nlink!=1:errors.append('hardlink '+rel)
  files[rel]=sha(p)
  if p.suffix=='.png':
   if p.name!=sha(p)+'.png':errors.append('image hash')
   with Image.open(p) as im:
    im.load()
    if im.mode!='RGB' or im.info:errors.append('image metadata/mode')
  else:
   text=p.read_text()
   if re.search(r'(?i)source_id|line_id|truth|verdict|google|expected|/Users/|\.\./',text):errors.append('private text')
 if set(files)!=expected:errors.append('missing files')
 result=dict(scanner_sha256=SCANNER_SHA,ok=not errors,directory=str(rd),items=len(data),violations=errors,files=files)
 if write and not errors:dump(rd.parent/f'MANIFEST.{rd.name}.json',dict(bed='cap1',reader=rd.name,files=files,scanner_sha256=SCANNER_SHA))
 return result
