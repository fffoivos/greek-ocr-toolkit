"""Rotation and near-square observations only; no production-policy modifications."""
from replay import *
import numpy as np,gzip,random,re,hashlib
from PIL import ImageDraw,ImageFont
FONT=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",12)
from greekocr.glyphs.orientation import QuarterTurn
from greekocr.harvest.line_pipeline_native import reconstructed_crop
BASE=R.parent/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'

def metrics(z):
 e=z['evidence'];box=e['box_evidence'];rf=box.get('row_frame');p=box.get('predictions')
 return dict(rows=len(e['lines']),long_side=max(rf['length'],rf['height']) if rf else None,height=rf['height'] if rf else None,
  ratio=(e['characters']+1)/(p[2]+1) if p else None,padding=e['padding_evidence'].get('total_padding_line_heights'),verdict=z['verdict'],reason=z['reason'])

def diagnostic_run(worker,row):
 """Run the full tool unchanged, then measure blocked gates diagnostically.
 Capture existing inventory arguments; reuse frozen measurement and predictor.
 """
 captured={};orig=worker.crop_tools.line_inventory
 def capture(glyphs,lines,components,angle):
  captured.update(glyphs=glyphs,components=components,angle=angle)
  return orig(glyphs,lines,components,angle)
 worker.crop_tools.line_inventory=capture
 try:z=worker(row)
 finally:worker.crop_tools.line_inventory=orig
 g=captured['glyphs'];cs=captured['components'];main=next((l for l in z['evidence']['lines'] if l['side']=='main'),None)
 ids=set(main['component_ids']) if main else set();boxes=[c['bbox'] for c in cs if c['index'] in ids]
 bbox=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)] if boxes else None
 yy,xx=np.nonzero(g.ink);ink=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None
 f=worker.crop_tools.features_from_observation(width=g.width,height=g.height,components=cs,ink_box=ink,ink_pixels=int(g.ink.sum()),xheight=float(g.band.xh),xheight_source=g.band.xh_source,support_count=g.band.n_support,chars=s1.character_count(row['raw_text']),labels=g.labels,angle_deg=captured['angle'])
 box=f['candidate_text_box'];rf=f.get('row_frame_text_box');m=dict(rows=len(z['evidence']['lines']),long_side=None,height=None,ratio=None,padding=None,verdict=z['verdict'],reason=z['reason'])
 if box and rf:
  pred=worker.predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=row.get('script_class','pooled')))
  m.update(long_side=max(rf['length'],rf['height']),height=rf['height'],ratio=(s1.character_count(row['raw_text'])+1)/(pred['expected']+1),padding=(g.height-box['height'])/rf['height'])
 return z,dict(metrics=m,main_row_box=bbox,measurement_after_blocked_gate=z['evidence']['gate']['verdict']!='PASS')

def main_box(z):
 return z.get('_diagnostic',{}).get('main_row_box')

def mapped_box(z,external):
 box=main_box(z)
 if box is None:return None
 x0,y0,x1,y1=box;pts=np.array([[x0,y0,1],[x1,y0,1],[x1,y1,1],[x0,y1,1]])
 pts=pts@np.linalg.inv(np.asarray(z['frame']['source_to_measurement'])@external).T
 return [*pts[:,:2].min(axis=0),*pts[:,:2].max(axis=0)]

def overlay(path,image,z,title):
 im=image.convert('RGB');pen=ImageDraw.Draw(im)
 for l in z['evidence']['detected_rows']:
  color='red' if l['side']=='main' else 'blue'
  for k in ('mean','base'):pen.line([tuple(p) for p in l['curves'][k]],fill=color,width=1)
 box=z['evidence']['box_evidence'].get('bbox')
 if box:pen.rectangle(tuple(box),outline='green',width=1)
 import textwrap
 m=metrics(z)
 labels=textwrap.wrap(title,width=115)+[f"rows={m['rows']}  box L={m['long_side']} H={m['height']}",f"ratio={m['ratio']}  padding={m['padding']}"]+textwrap.wrap(m['verdict']+': '+m['reason'],width=115)
 header=10+18*len(labels)
 canvas=Image.new('RGB',(max(750,im.width+20),im.height+header+20),'white');canvas.paste(im,(10,header));p=ImageDraw.Draw(canvas)
 for i,line in enumerate(labels):p.text((10,5+18*i),line,fill='black',font=FONT)
 canvas.save(path)

def rotation():
 rs=[r for r in read(D/'replay.jsonl') if r['cohort']=='segeval1'];_,worker=workers();_.close()
 temp=D/'rotation_inputs';temp.mkdir(exist_ok=True);out=[]
 try:
  for i,r in enumerate(rs,1):
   im=Image.open(r['row']['crop_path']);context(worker,r);upright,diag=diagnostic_run(worker,r['row']);assert norm(upright)==norm(r['after']);upright['_diagnostic']=diag;base=mapped_box(upright,np.eye(3))
   for name,angle in [('L',90),('R',270),('180',180)]:
    frame=QuarterTurn(im.width,im.height,angle);path=temp/f'{name}.png';frame.image(im).save(path)
    row=dict(r['row'],crop_path=str(path),crop_sha256=sha(path))
    context(worker,r);z,diag=diagnostic_run(worker,row);z['_diagnostic']=diag;box=mapped_box(z,frame.matrix)
    samebox=(base is None and box is None) or (base is not None and box is not None and max(abs(a-b) for a,b in zip(base,box))<=1)
    a,b=upright['_diagnostic']['metrics'],z['_diagnostic']['metrics']
    agree=dict(row_count=a['rows']==b['rows'],main_row_box=bool(samebox),main_row_detection=a['rows']==b['rows'] and bool(samebox))
    for key in ('long_side','height','ratio','padding','verdict'):agree[key]=a[key]==b[key]
    out.append(dict(line_id=r['line_id'],orientation=name,owner_standard_state=r.get('owner_standard_state'),owner_mark=latest.get(r['line_id']),upright=a,turned=b,upright_main_box=base,turned_main_box_mapped=box,agreement=agree,upright_diagnostic=upright['_diagnostic'],after=z))
   if i%25==0:print(f'rotation {i}/150',flush=True)
 finally:worker.close()
 for p in temp.glob('*.png'):p.unlink()
 temp.rmdir();write(D/'rotation_check.jsonl',out)

def bin_of(w,h):return 'h<=1.25w' if h<=1.25*w else '1.25w<h<=1.5w' if h<=1.5*w else '1.5w<h<=2w' if h<=2*w else 'h>2w'

def census_prepare():
 population_path=BASE/'cells/population_cells.jsonl.gz';candidates=[];count=0
 with gzip.open(population_path,'rt') as f:
  for line in f:
   r=json.loads(line);count+=1
   if r['height_px']>r['width_px'] and 1<=r['characters']<=2:candidates.append(r)
 dump(D/'census_population_receipt.json',dict(population_rows=count,selected_count=len(candidates),aspect_bins=dict(Counter(bin_of(r['width_px'],r['height_px']) for r in candidates)),path=str(population_path),sha256=sha(population_path)))
 wanted={r['row_id'] for r in candidates};bindings={};export=json.loads((BASE/'cells/export_receipt.json').read_text());sources=[]
 pattern=re.compile(rb'"id"\s*:\s*"([^"\\]+)"')
 for wave in ('W1','W2'):
  meta=next(r for r in export['metadata_inputs'] if f'/{wave}_features_' in r['path']);path=Path(meta['path']);h=hashlib.sha256();n=0
  with path.open('rb') as f:
   for line in f:
    h.update(line);n+=1;m=pattern.search(line)
    if m and m[1].decode() in wanted:
     r=json.loads(line);bindings[r['id']]=r
  assert h.hexdigest()==meta['sha256'] and n==meta['rows'];sources.append(meta)
 existing={}
 for directory in [s1.S/'crops',s1.S/'cells/samples',BASE/'crops',BASE/'cells/samples',BASE/'cells_opus/crops',BASE/'small_segments/crops',s1.SITE/'population-images']:
  for p in directory.glob('*.png'):existing.setdefault(p.stem,p)
 available=[];unavailable=[]
 for r in candidates:
  rid=r['row_id'];path=existing.get(rid) or existing.get(r['crop_sha256']);binding=bindings.get(rid)
  page=R.parent/'collect-v3-data/run/cache/pages'/((binding or {}).get('crop_source_sha256','none')+'.jpg')
  if path:available.append(dict(population=r,path=str(path),method='existing'))
  elif binding and page.is_file():available.append(dict(population=r,binding=binding,page=str(page),method='reconstructed'))
  else:unavailable.append(rid)
 selected=random.Random(20261019).sample(sorted(available,key=lambda a:a['population']['row_id']),min(600,len(available)))
 cropdir=D/'census_crops';cropdir.mkdir(exist_ok=True);pages={};inputs=[]
 for s in selected:
  r=s['population'];rid=r['row_id']
  if s['method']=='existing':path=Path(s['path'])
  else:
   page=Path(s['page']);b=s['binding']
   if str(page) not in pages:pages[str(page)]=sha(page);assert pages[str(page)]==b['crop_source_sha256']
   assert b['crop_sha256']==r['crop_sha256']
   with Image.open(page) as im:_,raw=reconstructed_crop(im,b['crop_bbox'],b.get('crop_color_mode','L'))
   assert hashlib.sha256(raw).hexdigest()==r['crop_sha256'];path=cropdir/f'{rid}.png';path.write_bytes(raw)
  assert sha(path)==r['crop_sha256']
  with Image.open(path) as im:assert im.size==(r['width_px'],r['height_px'])
  row=dict(id=rid,parent_id=r['parent_id'],split='unassigned',crop_path=str(path),crop_sha256=r['crop_sha256'],raw_text=r['raw_text'],script_class=r['script_class'],primary_class=r['primary_class'])
  inputs.append(dict(cohort='census_diagnostic',line_id=rid,row=row,width=r['width_px'],height=r['height_px'],chars=r['characters'],method=s['method']))
 write(D/'census_inputs.jsonl',inputs);write(D/'census_candidates.jsonl',candidates)
 dump(D/'census_acquisition_receipt.json',dict(seed=20261019,sampling='uniform random sample without replacement of sorted locally available candidates',available=len(available),unavailable=unavailable,selected=len(selected),metadata_inputs=sources,pages=pages,existing_crop_directories='see diagnostics.py',network='OFF',census_writes=False))

def near_square():
 records=read(D/'replay.jsonl');out=[]
 for r in records:
  chars=s1.character_count(r['row']['raw_text'])
  if r['height']>r['width'] and chars<=2:out.append(dict(r,chars=chars,diagnostic_population='replay',aspect=r['height']/r['width'],aspect_bin=bin_of(r['width'],r['height']),owner_mark=latest.get(r['line_id'])))
 a,b=workers()
 try:
  for i,r in enumerate(read(D/'census_inputs.jsonl'),1):
   old=a(r['row']);new=b(r['row'])
   out.append(dict(r,before=old,after=new,verdict_s1=old['verdict'],verdict_s2=new['verdict'],diagnostic_population='census',aspect=r['height']/r['width'],aspect_bin=bin_of(r['width'],r['height']),owner_mark=latest.get(r['line_id'])))
   if i%100==0:print(f'census replay {i}',flush=True)
 finally:a.close();b.close()
 write(D/'near_square.jsonl',out)
 render_examples(out)

def render_examples(out):
 # Diagnostic examples: owner-marked first, then round robin over aspect bins.
 unique={r['line_id']:r for r in out};pool=sorted(unique.values(),key=lambda r:r['line_id']);examples=[r for r in pool if r.get('owner_mark')][:6]
 bins=list(dict.fromkeys(bin_of(100,h) for h in (110,140,180,250)))
 while len(examples)<24:
  added=False
  for bin in bins:
   r=next((r for r in pool if r['aspect_bin']==bin and r['line_id'] not in {r['line_id'] for r in examples}),None)
   if r and len(examples)<24:examples.append(r);added=True
  if not added:break
 assert len(examples)==24
 directory=D/'near_square';directory.mkdir(exist_ok=True)
 for r in examples:
  im=Image.open(r['row']['crop_path']);rid=r['line_id']
  # Both S1 and S2 inventories are drawn in their actual measurement frames,
  # inverse-transformed onto the requested as-given and clockwise rasters.
  for name,z,target in [('upright',r['before'],0),('turned',r['after'],270)]:
   target_frame=QuarterTurn(im.width,im.height,target);display=target_frame.image(im).convert('RGB');pen=ImageDraw.Draw(display)
   mapping=target_frame.matrix@np.linalg.inv(z['frame']['source_to_measurement'])
   for l in z['evidence']['detected_rows']:
    for key in ('mean','base'):
     pts=np.array([[x,y,1] for x,y in l['curves'][key]])@mapping.T
     if len(pts)>1:pen.line([tuple(p[:2]) for p in pts],fill='red' if l['side']=='main' else 'blue',width=1)
   canvas=Image.new('RGB',(max(750,display.width+20),display.height+100),'white');canvas.paste(display,(10,85));p=ImageDraw.Draw(canvas)
   p.text((10,5),rid+' '+name,fill='black',font=FONT);p.text((10,25),'Google: '+r['row']['raw_text'],fill='black',font=FONT);p.text((10,45),f"owner={(r.get('owner_mark') or {}).get('owner_mark')} {z['verdict']} {r['aspect_bin']}",fill='black',font=FONT);p.text((10,65),z['reason'],fill='black',font=FONT);canvas.save(directory/f'{rid}_{name}.png')
 write(D/'near_square_examples.jsonl',[{k:r.get(k) for k in ('line_id','cohort','aspect','aspect_bin','owner_mark','verdict_s1','verdict_s2')} for r in examples])

 # Paired contact sheets for complete overlay readback, without clipping panels.
 for batch in range(2):
  pairs=[[Image.open(directory/f"{r['line_id']}_{kind}.png") for kind in ('upright','turned')] for r in examples[batch*12:batch*12+12]]
  heights=[max(im.height for im in pair)+8 for pair in pairs];width=max(im.width for pair in pairs for im in pair)
  canvas=Image.new('RGB',(2*width,sum(heights)),'white');pen=ImageDraw.Draw(canvas);y=0
  for pair,h in zip(pairs,heights):
   for j,im in enumerate(pair):canvas.paste(im,(j*width,y))
   y+=h;pen.line([(0,y-1),(2*width,y-1)],fill='grey')
  canvas.save(D/f'near_square_contact_{batch+1}.png')

marks=read(BASE/'owner_marks_20261019.jsonl');latest={}
for i,m in enumerate(marks):
 old=latest.get(m['line_id'])
 if old is None or (m['updated'],i) >= (old['updated'],old['file_line']):latest[m['line_id']]=dict(m,file_line=i)
if __name__=='__main__':
 if sys.argv[1]=='prepare':census_prepare()
 elif sys.argv[1]=='rotation':rotation()
 elif sys.argv[1]=='near':near_square()
 elif sys.argv[1]=='examples':render_examples(read(D/'near_square.jsonl'))
