"""Offline artifact, custody, random-draw and budget validation; no paid calls."""
from f2lib import *
from handoff import SOURCES
from collections import Counter
import subprocess,re,gzip
def main():
 errors=[];checks=0;exceptions=[]
 def check(value,message):
  nonlocal checks
  checks+=1
  if not value:errors.append(message)
 pages=rows(BASE/'pages.jsonl');ss=rows(BASE/'sources.jsonl');by={r['source']:r for r in ss}
 check(set(by)==set(SOURCES),'source set differs')
 for source in SOURCES:
  pp=[p for p in pages if p['source']==source];target=20 if source=='anemi' else 30
  check(len(pp)==target,source+' final page target');items=Counter(p['item'] for p in pp);check(len(items)>=6,source+' fewer than six items');check(max(items.values(),default=0)<=8,source+' >8 pages/item')
  if source!='anemi':check(sum(p['role']=='band' for p in pp)==6,source+' band target')
  frame=rows(BASE/f'population_{source}.jsonl');draw=rows(BASE/f'draw_{source}.jsonl');vv=rows(BASE/f'verification_{source}.jsonl');check(len({r['id'] for r in frame})==len(frame),source+' duplicate frame ID');check({r['id'] for r in draw}=={r['item'] for r in vv},source+' draw/verification identity loss')
  if source=='openarchives':
   for col in sorted({r['collection_slug'] for r in frame}):
    ff=sorted([r for r in frame if r['collection_slug']==col],key=lambda r:r['id']);dd=[r['id'] for r in draw if r['collection_slug']==col];expected=[r['id'] for r in rng('openarchives:'+col).sample(ff,min(20,len(ff)))];check(dd==expected,'OA '+col+' random draw differs')
  else:
   expected=[r['id'] for r in rng(source).sample(sorted(frame,key=lambda r:r['id']),min(20,len(frame)))];check([r['id'] for r in draw]==expected,source+' random draw differs')
  for r in frame:check(not any(r.get('overlap_screen',{}).get(k) for k in ['collected','held_out']),source+' overlap in eligible frame')
  cards=rows(BASE/'label_cards'/source/'cards.jsonl');key=json.loads((BASE/'label_cards'/(source+'_key.json')).read_text());check(len(cards)==40,source+' label card target');check({r['card'] for r in cards}=={r['card'] for r in key},source+' card/key mismatch')
  for r in cards:
   p=BASE/'label_cards'/source/r['crop'];check(p.exists(),source+' missing native crop')
   if p.exists():check(sha(p)==r['crop_sha256'],source+' changed crop hash')
  linecounts=Counter(r['primary_allocation'] for r in rows(BASE/'lines.jsonl') if r['source']==source and r['usable_candidate']);check(dict(linecounts)==by[source]['primary_counts'],source+' primary count mismatch');check(sum(linecounts.values())==by[source]['usable'],source+' primary allocation not disjoint/complete')
 for p in pages:
  image=BASE/p['image'];review=BASE/p['review_image'];check(image.exists(),'missing '+p['image']);check(review.exists(),'missing '+p['review_image'])
  if image.exists():
   check(sha(image)==p['image_sha256'],'changed native '+p['id'])
   with Image.open(image) as im:check(im.mode=='L' and max(im.size)<=3500,'native raster mode/size '+p['id'])
  if review.exists():
   check(sha(review)==p['review_sha256'],'changed review '+p['id'])
   with Image.open(review) as im:check(max(im.size)<=1600,'review >1600 '+p['id'])
  pos=(p['page']-.5)/max(1,p.get('page_count') or 1)
  if p['role']=='body':check(.10<=pos<=.90,'body band '+p['id'])
  else:
   edge=(p['page']-1)/max(1,(p.get('page_count') or 1)-1);check(edge<=.08 or edge>=.95,'edge band '+p['id'])
  if p['physical'].get('classification')=='born_digital_text':check(not p['machine_pass'],'born digital passed '+p['id'])
  if p['machine_pass']:
   rp=BASE/'receipts/reads'/(p['id']+'.json');check(rp.exists(),'passed page not read '+p['id'])
   if rp.exists():check(json.loads(rp.read_text())['status']=='ok','Google read failed '+p['id'])
 for key in json.loads((BASE/'blind_pages_key.json').read_text()):
  p=BASE/'blind_pages'/key['file'];check(p.exists(),'blind page missing '+key['file'])
  if p.exists():check(sha(p)==key['sha256'],'blind hash '+key['file'])
 blindkey=json.loads((BASE/'blind_pages_key.json').read_text());check(len(blindkey)==len(pages),'blind count');check({r['page_id'] for r in blindkey}=={p['id'] for p in pages},'blind cohort mismatch')
 ledger=rows(BASE/'google/ledger.jsonl');check(all(r['micro_usd']==1500 and r['state']=='reserved' for r in ledger),'reservation unit/state');check(len({r['key'] for r in ledger})==len(ledger),'duplicate paid reservation');check(sum(r['micro_usd'] for r in ledger)<=1_000_000,'USD cap exceeded')
 reserved={r['key']:r for r in ledger};provider=rows(BASE/'google/docai/ledger.jsonl')
 for r in provider:
  check(r['crop_sha256'] in reserved,'provider request not reserved')
  if r['crop_sha256'] in reserved:
   t=__import__('datetime').datetime.fromisoformat(r['timestamp']).timestamp();check(reserved[r['crop_sha256']]['time']<=t,'reservation after provider I/O')
  raw=r.get('raw_json_path')
  if raw and pathlib.Path(raw).exists():
   rr=json.loads(pathlib.Path(raw).read_text());check(all('image' not in page for page in rr.get('document',{}).get('pages',[])),'embedded image retained')
 total_images=sum(p.stat().st_size for p in BASE.rglob('*') if p.suffix.lower() in ['.jpg','.jpeg','.png','.tif','.tiff']);check(total_images<=600_000_000,'600 MB image cap exceeded')
 al=rows(BASE/'receipts/anemi-page-reservations.jsonl');check(len(al)<=50,'Anemi viewer cap exceeded')
 paces=json.loads((BASE/'receipts/anemi-pacing-audit.json').read_text())
 if not paces['passed']:exceptions.append(dict(kind='historical_Anemi_pacing',count=len(paces['deviations_below_2s']),receipt='receipts/anemi-pacing-audit.json'))
 years={p.get('year') for p in pages if p['source']=='government-gazette'}
 if not any(y and y<1900 for y in years):exceptions.append(dict(kind='Gazette_early_period_not_sampled',reason='uniform random A0 draw had no pre-1900 item; A0 add-item limit retained'))
 commit_status=json.loads((BASE/'receipts/commit-status.json').read_text())
 if commit_status.get('status')=='blocked':exceptions.append(dict(kind='commit_blocked_shared_Git_metadata',receipt='receipts/commit-status.json',commit_created=False))
 # Validate all local Markdown links, excluding remote URLs and inline code.
 text=(BASE/'REPORT.md').read_text()
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in target:continue
  check((BASE/target.split('#')[0]).exists(),'broken report link '+target)
 result=dict(artifact_checks_passed=not errors,checks=checks,errors=errors,task_exceptions=exceptions,final_pages=len(pages),paid_attempts=len(ledger),usd_reserved=sum(r['micro_usd'] for r in ledger)/1e6,image_bytes=total_images,anemi_viewer_attempts=len(al),at=stamp(),interpretation='Artifact/custody checks do not certify native line ownership, transcription correctness, complete source population, or training admission.')
 write(BASE/'receipts/validation.json',result);print(json.dumps(result,ensure_ascii=False,indent=2));return not errors
if __name__=='__main__':raise SystemExit(0 if main() else 1)
