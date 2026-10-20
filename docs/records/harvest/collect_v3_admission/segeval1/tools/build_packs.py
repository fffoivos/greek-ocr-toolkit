"""Two isolated blind contexts: 75 study cards + five pre-approved controls each."""
import json,hashlib,random,shutil,sys,tarfile,unicodedata,struct
from pathlib import Path
from common import sha,rows
D=Path(__file__).resolve().parents[1];ROOT=D.parents[3];P=ROOT.parent
PACK=Path('/private/tmp/segeval1-packs-20261019')
OLDPACK=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs')
SC='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def scripts(text):
 out=[]
 for w in text.split():
  s={next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in unicodedata.name(c,'')),'Other') for c in w if c.isalpha()}
  out.append([w,next(iter(s)) if len(s)==1 else 'Mixed' if s else 'none'])
 return out
assert not PACK.exists(),'Refuse overwrite'
receipt=json.loads((D/'draw_receipt.json').read_text())
assert sha(D/'keys/sealed_decisions.jsonl')==receipt['seal_sha256']
assert sha(D/'tools/scan_rollout.py')==SC
study=rows(D/'keys/sealed_decisions.jsonl');assert len(study)==150
random.Random('20261019:split').shuffle(study)
controls=json.loads((ROOT/'docs/harvest/recut_v1/w1_masked/caps1/keys/control_truth.json').read_text());assert len(controls)==10
oldkeys=json.loads((ROOT/'docs/harvest/recut_v1/w1_masked/caps1/keys/caps1.json').read_text())
keys={};manifests={};custody=[]
from PIL import Image
for i,bed in enumerate(['segeval1_a','segeval1_b']):
 rd=PACK/bed/'r1';(rd/'crops').mkdir(parents=True)
 batch=[dict(r,control=False) for r in study[i*75:(i+1)*75]]
 for c in controls:
  if c['context']!='c'+str(i+1):continue
  m=oldkeys['items'][c['opaque_id']]
  old=next(x for x in rows(OLDPACK/'caps1'/c['context']/'cards.jsonl') if x['card_id']==c['opaque_id'])
  crop=OLDPACK/'caps1'/c['context']/old['crop'];assert sha(crop)==m['crop_sha256']
  batch.append(dict(row_id=c['line_id'],control=True,google_text=c['source_card']['google_text'],crop_sha256=m['crop_sha256'],control_origin=c,original_crop=str(crop)))
 random.Random('20261019:order:'+bed).shuffle(batch)
 public=[];key={}
 for r in batch:
  iid='k'+hashlib.sha256(('20261019:'+bed+':'+r['row_id']).encode()).hexdigest()[:10]
  original=Path(r['original_crop']) if r['control'] else D/'crops'/(r['row_id']+'.png')
  assert sha(original)==r['crop_sha256']
  data=original.read_bytes();metadata_removed=[]
  with Image.open(original) as im:
   im.load();mode,size,pixels=im.mode,im.size,im.tobytes()
   if im.info:
    # Remove only the ICC metadata chunk; preserve all compressed raster bytes.
    assert set(im.info)=={'icc_profile'}
    pos=8;chunks=[data[:8]]
    while pos<len(data):
     n=struct.unpack('>I',data[pos:pos+4])[0];chunk=data[pos:pos+n+12]
     if chunk[4:8]!=b'iCCP':chunks.append(chunk)
     else:metadata_removed.append('iCCP')
     pos+=n+12
    data=b''.join(chunks)
  public_sha=hashlib.sha256(data).hexdigest()
  dest=rd/'crops'/(public_sha+'.png');dest.write_bytes(data)
  with Image.open(dest) as im:
   im.load();assert not im.info
   assert (im.mode,im.size,im.tobytes())==(mode,size,pixels)
  assert dest.stat().st_nlink==1 and not dest.is_symlink()
  public.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=r['google_text'],word_scripts=scripts(r['google_text'])))
  key[iid]=r;custody.append(dict(card_id=iid,row_id=r['row_id'],original=str(original),destination=str(dest),sha256=sha(dest),original_sha256=r['crop_sha256'],metadata_removed=metadata_removed))
 (rd/'cards.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False,sort_keys=True)+'\n' for c in public))
 assert len(public)==80 and sum(not r['control'] for r in key.values())==75
 files={str(p.relative_to(rd)):sha(p) for p in sorted(rd.rglob('*')) if p.is_file()}
 manifest=dict(bed=bed,reader='r1',files=files)
 dump(rd.parent/'MANIFEST.r1.json',manifest);manifests[bed]=manifest
 keys[bed]=key
 dump(D/'keys'/f'{bed}.json',dict(items=key,order=[c['card_id'] for c in public]))
dump(D/'pack_closure.json',dict(pack_root=str(PACK),contexts=2,study=150,controls=10,items_per_context=80,scanner_sha256=SC,manifests=manifests,readers_started=0))
dump(D/'keys/crop_custody.json',custody)
with tarfile.open(D/'blind_packs.tar.gz','w:gz') as tar:
 for bed in manifests:tar.add(PACK/bed,arcname=bed)
print(json.dumps(dict(paths=[str(PACK/b/'r1') for b in manifests],archive_sha256=sha(D/'blind_packs.tar.gz'))))
