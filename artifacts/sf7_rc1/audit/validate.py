"""Offline closure and behavioural checks. Never starts a reader or a probe."""
import ast, copy, struct, tempfile
from driver import *

def validate_build():
 r=load(A/'routing.json');assert len(r['lines'])==100 and len(r['heads'])==107
 assert len({h['head_id'] for h in r['heads']})==107
 assert r['counts']=={'Sol-accent':79,'Opus-later':25,'Sol-capital':3}
 frame=rows(A.parent/'audit100_frame.jsonl');release={x['line_id']:x for x in rows(A.parent/'release_edits_only_A.jsonl')};assert sum(len(release[f['line_id']]['edits']) for f in frame)==107
 b=load(A/'build_receipt.json')
 for path,digest in b['inputs'].items():
  # HANDOVER may intentionally advance after the build; runtime rebinds it.
  if Path(path)!=SR/'HANDOVER.md':assert sha(path)==digest,path
 assert (A/'prompts/accent.md').read_bytes()==(SR/'prompts/grave.md').read_bytes()
 assert (A/'prompts/capital.md').read_bytes()==(CQ/'cq1/prompts/cap1.md').read_bytes()
 coverage=[];files=0;images=0;contexts=load(A/'contexts.json')
 for c in contexts:
  assert c['items']<=90 and c['controls']==10;manifest=integrity(c);key=load(c['key']);rd=Path(c['reader_dir']);pub=rows(rd/'items.jsonl');assert len(pub)==c['items']+10
  assert [p['item_id'] for p in pub]==list(key)
  assert len({p['item_id'] for p in pub})==len(pub)
  referenced={'items.jsonl'}|({'README.md','answer_schema.json'} if c['track']=='capital' else set())
  for p in pub:
   assert re.fullmatch('k[0-9a-f]{10}',p['item_id'])
   allowed={'item_id','word_image','line_image'}|({'breathing_options','accent_options'} if c['track']=='capital' else {'letter_image','word_bare','anchor_index','anchor_base'})
   assert set(p)==allowed
   if c['track']=='accent':assert p['word_bare']==bare(p['word_bare']) and p['word_bare'][p['anchor_index']]==p['anchor_base']
   else:
    assert set(p['breathing_options'].values())=={'none','smooth','rough','unreadable'}
    assert set(p['accent_options'].values())=={'none','acute','grave','circumflex','unreadable'}
   for f in ('word_image','line_image','letter_image'):
    if f not in p:continue
    path=rd/p[f];referenced.add(p[f]);assert path.name==sha(path)+'.png';assert not path.is_symlink() and path.stat().st_nlink==1
    data=path.read_bytes();pos=8;chunks=[]
    while pos<len(data):
     n=int.from_bytes(data[pos:pos+4],'big');chunks.append(data[pos+4:pos+8]);pos+=n+12
    assert set(chunks)<={b'IHDR',b'IDAT',b'IEND'}
    with Image.open(path) as im:assert im.mode=='RGB';images+=1
   m=key[p['item_id']];assert sha(m['native_asset'])==m['native_asset_sha256']
   if m['control']:
    assert Path(m['verification']).is_file()
    if c['track']=='capital':assert any(x['source_id']==m['source_id'] and x.get('verified') is True for x in load(CQ/'cq4/control_review/lead_review.json')['items'])
   else:coverage.extend(m['heads'])
  assert set(manifest)==referenced;files+=len(manifest)
 assert set(coverage)=={h['head_id'] for h in r['heads'] if h['route']!='Opus-later'} and len(coverage)==82
 # Exercise gates and strict answer parsing against complete synthetic fixtures outside the packs.
 with tempfile.TemporaryDirectory(prefix='au1-check-') as tmp:
  path=Path(tmp)/'answers.jsonl'
  for c in contexts:
   key=load(c['key']);pub=rows(Path(c['reader_dir'])/'items.jsonl');answers=[]
   for p in pub:
    m=key[p['item_id']];answer=dict(item_id=p['item_id'],confidence='high',note='');expected=m.get('expected',{'accent':'none','breathing':'none'})
    for h in ('breathing','accent') if c['track']=='capital' else ('accent',):
     value=expected.get(h,'none');answer[h]=next(k for k,v in p[h+'_options'].items() if v==value) if c['track']=='capital' else value
    answers.append(answer)
   jsonl(path,answers);_,gate=validate(c,path);assert gate['errors']==0 and gate['passed']
   controls=[i for i,p in enumerate(pub) if key[p['item_id']]['control']]
   for n,i in enumerate(controls[:2],1):
    answers[i]['accent']=next(k for k,v in pub[i]['accent_options'].items() if v!=key[pub[i]['item_id']]['expected']['accent']) if c['track']=='capital' else next(v for v in ('none','grave','acute') if v!=key[pub[i]['item_id']]['expected']['accent'])
    jsonl(path,answers);_,gate=validate(c,path);assert gate['errors']==n and gate['passed']==(n<=1)
   jsonl(path,list(reversed(answers)))
   try:validate(c,path)
   except AssertionError:pass
   else:raise AssertionError('order accepted')
 assert trigger('capital',{'breathing':'smooth','accent':'none'})
 assert trigger('capital',{'breathing':'none','accent':'unreadable'})
 assert not trigger('capital',{'breathing':'smooth','accent':'acute'})
 assert trigger('accent',{'accent':'grave','confidence':'high'},'acute')
 assert not trigger('accent',{'accent':'acute','confidence':'high'},'acute')
 for p in A.glob('*.py'):ast.parse(p.read_text())
 summary=dict(status='PASS',frame_lines=100,heads=107,sol_heads=82,opus_pending_heads=25,contexts=len(contexts),closure_files=files,image_references_checked=images,reader_runs=0,network=False,git_writes=False,scanner_hash_matches_at_build=b['scanner_expected_at_build']==b['scanner_actual_at_build'],tests=['routing coverage','strict public closure','metadata-free content-hash PNGs','no links','prompt byte equality','native hashes','verified control membership','zero/one/two-error controls gates','answer order','compound and accent re-read triggers'])
 dump(A/'validation.json',summary);print(json.dumps(summary))
if __name__=='__main__':validate_build()
