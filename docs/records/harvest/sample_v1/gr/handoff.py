"""Offline disjoint P1 yields, survey intervals, blind packs and review sheets."""
from f2lib import *
from collections import Counter,defaultdict
from PIL import ImageDraw,ImageFont
import shutil,unicodedata
sys.path.insert(0,str(P1))
from greekocr.harvest.admission import page_quality
from classify import inspect
SOURCES=['openarchives','kosmopolis','pleias','pergamos','nlg-digital','elstat','government-gazette','lekythos','anemi']
TARGETS={'poly1850':40000,'poly1900':50000,'modern_scanned':40000,'mixed_greek_latin':20000,'latin':8000,'cyrillic':12000,'headings_caps':6000,'numerics_tables':10000,'leaders_indices':4000,'dialogue_fiction':12000}
def primary(r,p):
 greek=r.get('inventory',{}).get('greek_letters',0);tags=r.get('line_tags',[])
 if r.get('mixed_line'):return 'mixed_greek_latin'
 if 'leaders' in tags:return 'leaders_indices'
 if greek>=3 and any(t in tags for t in ['caps','heading']):return 'headings_caps'
 if 'numeric' in tags:return 'numerics_tables'
 if greek>=3 and 'dialogue_punctuation' in tags:return 'dialogue_fiction'
 if r['script_class']=='greek_poly' and p['period'] in ['poly1850','poly1900'] and p.get('target_regime')!='ancient_or_bilingual_edition_auxiliary':return p['period']
 if r['script_class'] in ['greek_mono','greek_poly'] and ((p['source'] in ['openarchives','elstat'] and p.get('year') and p['year']>=1900) or p['period']=='modern') and p.get('target_regime')!='ancient_or_bilingual_edition_auxiliary':return 'modern_scanned'
 return r['script_class']
def contact(source,pp):
 cols=5;cw=300;ch=440;canvas=Image.new('RGB',(cols*cw,math.ceil(max(1,len(pp))/cols)*ch),'#dddddd');d=ImageDraw.Draw(canvas);key=[]
 for i,p in enumerate(pp):
  with Image.open(BASE/p['review_image']) as im:
   im=im.convert('RGB');im.thumbnail((cw-14,ch-48));x=(i%cols)*cw+(cw-im.width)//2;y=(i//cols)*ch+29;canvas.paste(im,(x,y))
  label=f"{i+1:02d}  {p['item'][:22]} p{p['page']} {p['role']}";d.text(((i%cols)*cw+5,(i//cols)*ch+7),label,fill='black');key.append(dict(number=i+1,page_id=p['id']))
 dest=BASE/'contact_sheets'/(source+'.jpg');dest.parent.mkdir(exist_ok=True);canvas.save(dest,quality=88,optimize=True);write(BASE/'receipts'/(source+'-contact-key.json'),key)
 return str(dest.relative_to(BASE))
def cards(source,rr,pages):
 eligible=[r for r in rr if r['admitted']]
 groups=defaultdict(list)
 for r in eligible:groups[r['primary_allocation']].append(r)
 for values in groups.values():values.sort(key=lambda r:(len(r['text'])<30,-len(r['text']),r['id']))
 chosen=[];seenitems=Counter();classcounts=Counter();selectedids=set()
 def take(values):
  pool=[r for r in values if r['id'] not in selectedids]
  if not pool:return False
  row=min(pool,key=lambda r:(len(r['text'])<30,seenitems[r['item']],-len(r['text']),r['id']))
  chosen.append(row);selectedids.add(row['id']);seenitems[row['item']]+=1;classcounts[row['primary_allocation']]+=1;return True
 # Represent every admitted primary class, then prioritise long complete lines
 # across items, followed by a balanced tail for the rare classes.
 for key in sorted(groups):take(groups[key])
 while len(chosen)<min(28,len(eligible)):
  if not take(eligible):break
 while len(chosen)<min(40,len(eligible)):
  progressed=False
  for key in sorted(groups,key=lambda k:(classcounts[k],k)):
   if len(chosen)<40:progressed=take(groups[key]) or progressed
  if not progressed:break
 rng(source+':cards').shuffle(chosen);dest=BASE/'label_cards'/source;dest.mkdir(parents=True,exist_ok=True);cr=dest/'crops';cr.mkdir(exist_ok=True);out=[];key=[]
 for i,r in enumerate(chosen,1):
  cid=f'c{i:03d}';path=cr/(cid+'.png');page=pages[r['page_id']]
  with Image.open(BASE/page['image']) as im:im.crop(r['crop_bbox']).save(path,compress_level=3)
  assert sha(path)==r['crop_sha256'],'selected native crop did not reconstruct exactly'
  out.append(dict(card=cid,crop='crops/'+path.name,text=r['text'],crop_sha256=sha(path),native_pixels=True))
  key.append(dict(card=cid,line_id=r['id'],page_id=r['page_id'],source=source,item=r['item'],page=r['page'],primary_class=r['primary_allocation'],usable=r['usable_candidate'],geometry_positive=r['geometry_positive'],codec_v1_pass=r['codec_v1_pass']))
 jsonl(dest/'cards.jsonl',out);write(BASE/'label_cards'/(source+'_key.json'),key)
 # A numbered review sheet is supplemental; native crops + cards.jsonl are the
 # actual checker input. Text is rendered with a system Greek-capable font.
 fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
 try:font=ImageFont.truetype(fontpath,17)
 except OSError:font=ImageFont.load_default()
 sheet=Image.new('RGB',(1600,max(1,len(out))*145),'white');d=ImageDraw.Draw(sheet)
 for i,card in enumerate(out):
  with Image.open(dest/card['crop']) as im:
   im=im.convert('RGB');im.thumbnail((1540,80));sheet.paste(im,(40,i*145+4))
  text=card['text'];d.text((10,i*145+90),card['card']+' '+text[:160],fill='black',font=font)
 sheet.save(dest/'sheet.jpg',quality=85,optimize=True)
 return len(out)

def build():
 pages=[]
 for name in SOURCES:
  for p in rows(BASE/f'pages_{name}.jsonl'):
   mp=BASE/'receipts/machine'/(p['id']+'.json');p=json.loads(mp.read_text()) if mp.exists() else p;p['period']=period(p.get('year'))
   if p['source']=='openarchives' and p['item'] in ['hf-37ca3aaa0bd5dc77','hf-9b97145b1b53b803']:p['target_regime']='ancient_or_bilingual_edition_auxiliary';p['regime_basis']='conservative local catalogue/native review inference for Basilicorum libri LX and Philonis Iudaei opera omnia; no historical-Modern-Greek body quota credit'
   pages.append(p)
 lookup={p['id']:p for p in pages};jsonl(BASE/'pages.jsonl',pages)
 allrows=[];global_seen=set();quality=[];summaries=[]
 for source in SOURCES:
  pp=[p for p in pages if p['source']==source];rr=[];readpages=[]
  for p in pp:
   readp=BASE/'receipts/reads'/(p['id']+'.json')
   if readp.exists() and json.loads(readp.read_text())['status']=='ok':readpages.append(p)
   lp=BASE/'bulk/lines'/(p['id']+'.jsonl');lines=rows(lp)
   for r in lines:r.update(inspect(r['docai_raw_text'],r['confidence'],tall=r['tall_box']))
   inp=[dict(page_id=p['id'],docai_text=r['text'],confidence=r['confidence'] or 0,flags=['tall_box'] if r['tall_box'] and 'heading' not in r['line_tags'] else []) for r in lines]
   q=page_quality(inp).get(p['id'],dict(bad_page=False));quality.append(dict(page_id=p['id'],**q))
   for r in lines:
    r['bad_page']=q['bad_page'];r['pre_page_admitted']=r['admitted']
    if q['bad_page']:r['admitted']=False;r['rejection_reasons']=sorted(set(r['rejection_reasons']+['bad_page']))
    key=(r['crop_sha256'],r['canonical_label']);r['duplicate_crop_label']=key in global_seen
    eligible=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False
    if eligible:global_seen.add(key)
    r['usable_candidate']=eligible and not r['duplicate_crop_label'];r['primary_allocation']=primary(r,p);r['period']=p['period'];r['year']=p['year'];r['source']=source
   rr+=lines
  allrows+=rr;usable=[r for r in rr if r['usable_candidate']];pc=Counter(r['primary_allocation'] for r in usable);nread=len(readpages)
  ledger=rows(BASE/'google/ledger.jsonl');hashes={p['image_sha256'] for p in pp}
  read_receipts=[json.loads(x.read_text()) for x in (BASE/'receipts/reads').glob('*.json')]
  source_hashes={r['image_sha256'] for r in read_receipts if r.get('source')==source}
  usd=sum(x['micro_usd'] for x in ledger if x['key'] in source_hashes)/1e6
  final_usd=sum(x['micro_usd'] for x in ledger if x['key'] in hashes)/1e6
  per=[]
  for period_ in sorted({p['period'] for p in pp}):
   np_=sum(p['period']==period_ for p in readpages);counts=Counter(r['primary_allocation'] for r in usable if r['period']==period_)
   per.append(dict(period=period_,pages_read=np_,usable=sum(counts.values()),primary_rows_per_read_page={k:v/np_ for k,v in counts.items()} if np_ else {}))
  sheet=contact(source,pp) if pp else None
  count=cards(source,rr,lookup) if rr else 0
  summary=dict(source=source,pages_sampled=len(pp),passed_machine=sum(p['machine_pass'] for p in pp),excluded_reasons=dict(Counter(x for p in pp for x in p['excluded_reasons'])),pages_read=nread,usd_reserved=usd,lines=len(rr),admitted=sum(r['admitted'] for r in rr),codec_admitted=sum(r['admitted'] and r['codec_v1_pass'] for r in rr),usable=len(usable),usable_per_read_page=len(usable)/nread if nread else None,primary_counts=dict(pc),primary_rows_per_read_page={k:v/nread for k,v in pc.items()} if nread else {},per_period=per,geometry_positive=sum(r['geometry_positive'] is True for r in rr if r['admitted'] and r['codec_v1_pass']),geometry_unresolved=sum(r['geometry_positive'] is None for r in rr if r['admitted'] and r['codec_v1_pass']),rejections=dict(Counter(x for r in rr for x in r['rejection_reasons'])),contact_sheet=sheet,label_cards=count,items_sampled=len({p['item'] for p in pp}),band_pages=sum(p['role']=='band' for p in pp))
  summary.update(usd_final_cohort=final_usd,usd_superseded_or_nonfinal=usd-final_usd,superseded_or_nonfinal_attempts=sum(x['key'] in source_hashes and x['key'] not in hashes for x in ledger))
  summaries.append(summary)
 jsonl(BASE/'bulk/records.jsonl',allrows)
 compact=[]
 for r in allrows:
  keep={k:r.get(k) for k in ['id','page_id','source','item','page','year','period','confidence','admitted','codec_v1_pass','geometry_positive','duplicate_crop_label','usable_candidate','primary_allocation','crop_bbox','crop_sha256','rejection_reasons','codec_unknown','line_tags']}
  keep.update(label_sha256=digest(r['text'].encode()),label_characters=len(r['text']));compact.append(keep)
 jsonl(BASE/'lines.jsonl',compact);jsonl(BASE/'page_quality.jsonl',quality);jsonl(BASE/'sources.jsonl',summaries)
 # One global deterministic shuffle; key stays outside the blind page directory.
 blind=BASE/'blind_pages';blind.mkdir(exist_ok=True);shuffled=list(pages);rng('blind-pages').shuffle(shuffled);key=[]
 for i,p in enumerate(shuffled,1):
  name=f'p{i:04d}.jpg';dest=blind/name;shutil.copyfile(BASE/p['review_image'],dest);key.append(dict(file=name,source=p['source'],item=p['item'],page=p['page'],page_id=p['id'],sha256=sha(dest)))
 write(BASE/'blind_pages_key.json',key)
 print('HANDOFF',[(s['source'],s['pages_sampled'],s['pages_read'],s['usable']) for s in summaries],flush=True)
 return summaries
if __name__=='__main__':build()
