"""Offline A/B acceptance measurements using the owner's installed-stage probes.

Labels test geometry and source ownership, not recognition. No PDF is opened.
All failures and per-element IDs are retained; success is never inferred from
label survival alone. Foreground execution; no model downloads.
"""
import os
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
from pathlib import Path
import sys,json,copy,hashlib
from collections import Counter
from types import SimpleNamespace as NS
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'.astra/docling_research')]
import research_tables as rt
import research_layout as rl
from docling_core.types.doc import DoclingDocument,Size,DocItemLabel
from docling.models.stages.reading_order.readingorder_model import ReadingOrderModel
from greekocr.deploy.docling_plugin.model import GlossapiOcrModel

OUT=ROOT/'.astra/out/acceptance';OUT.mkdir(exist_ok=True)
rt.OUT=rl.OUT=OUT


def save(name,data):
 (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=rt.serial)+'\n')


def intersect(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def area(b):return max(0,b[2]-b[0])*max(0,b[3]-b[1])


def labels_for(annotation):
 cells=[];meta=[]
 for ti,t in enumerate(annotation['tables']):
  for c in t['cells']:
   for e in c['text_elements']:
    label=f'A{len(cells):05d}'
    cells.append(rt.label_cell(len(cells),label,[v/3 for v in e['box']]))
    meta.append(dict(label=label,table_id=t['id'],cell_id=c['id'],element_id=e['id'],box=e['box'],
                     panel=c['panel'],row=c['row'],column=c['column'],row_span=c['row_span'],column_span=c['column_span']))
 return cells,meta


def frozen(model,key,image,table,cells,meta,variant):
 page,cluster,backend=rt.page_for(image,cells,table['extent'])
 # Test actual replacement against conflicting native and old OCR caches.
 backend.segmented.word_cells=[rt.label_cell(99999,'BACKEND_WORD',[v/3 for v in table['extent']])]
 backend.segmented.char_cells=[rt.label_cell(99998,'OLD_CHAR',[v/3 for v in table['extent']])]
 backend.segmented.textline_cells=[rt.label_cell(99997,'OLD_LINE',[v/3 for v in table['extent']])]
 page.parsed_page=backend.segmented
 GlossapiOcrModel._install(cells,page)
 assert not backend.segmented.word_cells and not backend.segmented.char_cells
 model.predict_tables(NS(timings={}),[page])
 prediction=page.predictions.tablestructure.table_map[0]
 doc=DoclingDocument(name=key);doc.add_page(page_no=1,size=page.size)
 item=ReadingOrderModel.__new__(ReadingOrderModel)._add_table_element(prediction,doc)
 landing={};counts=Counter()
 for i,c in enumerate(item.data.table_cells):
  for label in c.text.split():
   counts[label]+=1
   landing.setdefault(label,[]).append(dict(cell=i,row=c.start_row_offset_idx,column=c.start_col_offset_idx,
     row_span=c.row_span,column_span=c.col_span,box=c.bbox.model_dump(mode='json') if c.bbox else None))
 known={m['label']:m for m in meta}
 wrong=[];mixed=[];bycell={}
 for label,locations in landing.items():
  if label not in known:continue
  for loc in locations:bycell.setdefault(loc['cell'],set()).add(known[label]['cell_id'])
 for m in meta:
  places=landing.get(m['label'],[])
  # Independent panels cannot be compared as if they shared a rectangular row
  # phase. Still reject every mixed-owner output cell, rather than accepting
  # the mere retention of its labels. Exact grid metrics remain separate.
  if len(places)==1 and len(bycell.get(places[0]['cell'],set()))>1:wrong.append(m['label'])
  if table['panels'].keys()=={'main'} and len(places)==1:
   loc=places[0]
   if any(loc[k]!=m[k] for k in ('row','column','row_span','column_span')) and m['label'] not in wrong:wrong.append(m['label'])
 expected={m['label'] for m in meta}
 metric=dict(page=key,table=table['id'],mode=model.mode.value,variant=variant,input=len(meta),
   lost=sum(counts[t]==0 for t in expected),duplicated=sum(counts[t]>1 for t in expected),
   wrong_owner=len(wrong),mixed_owner_cells=sum(len(v)>1 for v in bycell.values()),
   rows=prediction.num_rows,columns=prediction.num_cols,materialized_cells=len(item.data.table_cells),
   sentinel_survived=any(x in counts for x in ('BACKEND_WORD','OLD_CHAR','OLD_LINE')),
   exact_grid_comparable=list(table['panels'])==['main'])
 save(f'{key}.{table["id"]}.{model.mode.value}.{variant}.json',dict(metrics=metric,landing=landing,
   wrong_owner_labels=wrong,missing_labels=sorted(t for t in expected if not counts[t]),annotation_metadata=meta,
   table_item=item.model_dump(mode='json')))
 print('FROZEN',metric,flush=True)
 return metric


def geometry(annotation,records,image):
 gray=np.asarray(image.convert('L'));bg=ndi.maximum_filter(gray,size=max(3,round(.015*min(gray.shape))))
 ink=bg.astype(float)-gray>30
 failures=[];crossings=[];tables=[]
 for table in annotation['tables']:
  textcells=[c for c in table['cells'] if not c['empty']]
  own=[]
  for p in records:
   b=p['box_pixels']
   if intersect(b,table['extent'])/max(1,area(b))>.8:
    own.append(p)
    overlaps=[c['id'] for c in textcells if any(intersect(b,e['box'])/max(1,area(e['box']))>.2 for e in c['text_elements'])]
    if len(set(overlaps))>1:crossings.append(dict(piece=p['index'],table=table['id'],cells=overlaps))
  total=complete=0
  for c in textcells:
   for e in c['text_elements']:
    a,t,b,bot=map(int,e['box']);target=ink[t:bot,a:b];mask=np.zeros_like(target)
    for p in own:
     x,y,r,d=map(int,p['box_pixels'])
     if intersect((a,t,b,bot),(x,y,r,d)):
      mask[max(0,y-t):min(bot,d)-t,max(0,x-a):min(b,r)-a]=True
    coverage=float((mask&target).sum()/max(1,target.sum()))
    total+=1;complete+=coverage>=.98
    if coverage<.98:failures.append(dict(table=table['id'],cell=c['id'],element=e['id'],coverage=coverage,box=e['box']))
  tables.append(dict(id=table['id'],elements=total,complete=complete,missing_or_partial=total-complete,delivered=len(own)))
 finite=all(np.isfinite(p['box_page']).all() and area(p['box_page'])>0 and p['coord_origin']=='TOPLEFT' for p in records)
 return dict(tables=tables,omissions=failures,crossing_pieces=crossings,positive_finite_topleft=finite,
             unique_ids=len({p['index'] for p in records})==len(records),
             method='At least 98% of independently annotated element contrast pixels covered; crossing means overlap with text in multiple annotated entries. Provisional annotations.')


def main():
 annotations=[json.loads(f.read_text()) for f in sorted((ROOT/'docs/records/tables/annotations').glob('*.json'))]
 art=OUT/'layout-artifacts';art.mkdir(exist_ok=True);link=art/'docling-project--docling-layout-heron'
 if not link.exists():link.symlink_to(rl.SNAPSHOT,target_is_directory=True)
 layout=rl.LayoutObjectDetectionModel(artifacts_path=art,accelerator_options=rl.AcceleratorOptions(device='cpu',num_threads=4),options=rl.LayoutObjectDetectionOptions())
 post=rl.LayoutPostprocessingModel(options=rl.LayoutPostprocessorOptions())
 summary={}
 for ann in annotations:
  key=ann['key'];image=Image.open(ROOT/'.astra/pages'/f'{key}.png').convert('RGB')
  rec=json.loads((ROOT/'.astra/out'/f'{key}.cells.json').read_text())['cells']
  pieces=[rt.label_cell(p['index'],f'P{p["index"]:05d}',p['box_page']) for p in rec]
  old=json.loads((ROOT/'.astra/previous_round3'/f'{key}.lines.json').read_text())
  lines=[rt.label_cell(i,f'L{i:05d}',[l['x0']/3,max(0,min(l['top']))/3,l['x1']/3,min(image.height,max(l['bottom']))/3]) for i,l in enumerate(old) if l['discounted'] is None]
  words=[];mask=rt.ink_mask(image)
  for i,l in enumerate(old):
   if l['discounted'] is not None:continue
   for a,b in rt.spans_for_line(l,mask,'word'):
    ix0,ix1=a-l['x0'],b-l['x0']
    words.append(rt.label_cell(len(words),f'W{len(words):05d}',[a/3,max(0,min(l['top'][ix0:ix1]))/3,b/3,min(image.height,max(l['bottom'][ix0:ix1]))/3]))
  anncells,meta=labels_for(ann)
  missing=[c for c in pieces if all(intersect([v*3 for v in c.rect.to_bounding_box().as_tuple()],[t['extent'][0],t['extent'][1],t['extent'][0]+.35*(t['extent'][2]-t['extent'][0]),t['extent'][3]])==0 for t in ann['tables'])]
  variants={}
  for name,cells in [('lines',lines),('pieces',pieces),('words',words),('omitted_columns',missing),('no_cells',[]),('annotated',anncells)]:
   variants[name]=rl.run(layout,post,key,image,name,copy.deepcopy(cells),[])
  identity=rl.table_identity(variants['lines']['final_tables'])
  invariant=all(x['raw_prediction']==variants['lines']['raw_prediction'] and rl.table_identity(x['final_tables'])==identity for x in variants.values())
  retained=variants['pieces']['final_tables'];admitted=Counter(t for x in variants['annotated']['final_tables'] for t in x['tokens'])
  discovery=[dict(id=t['id'],maximum_extent_coverage=max([intersect(t['extent'],[v*3 for v in r['box']])/area(t['extent']) for r in retained]+[0.])) for t in ann['tables']]
  geom=geometry(ann,rec,image)
  summary[key]=dict(layout_invariant=invariant,discovery=discovery,annotated_elements=len(anncells),
    admitted_exactly_once=sum(admitted[c.text]==1 for c in anncells),admission_excluded=[c.text for c in anncells if not admitted[c.text]],
    geometry=geom,frozen=[],raw_tables=variants['pieces']['raw_tables'],retained_tables=retained)
  # Border control keeps fixed image pixels but excludes the deliberately fused
  # child. No retained table is invented on the two missed layout pages.
  if retained:
   box=max(retained,key=lambda c:area(c['box']))['box'];l,t,r,b=box;d=min(.1*(b-t),.8*t)
   bad=[rt.label_cell(9999,'BORDER_FUSED',[l+.3*(r-l),t-d,l+.7*(r-l),t+d])]
   control=rl.run(layout,post,key,image,'border_fused',bad,[])
   summary[key]['border_control']=dict(table_identity_unchanged=rl.table_identity(control['final_tables'])==identity,
     admitted=sum('BORDER_FUSED' in x['tokens'] for x in control['final_tables']))
  save('summary.json',summary)
 for mode in ('accurate','fast'):
  model,captured,forwards=rt.build_model(mode)
  for ann in annotations:
   key=ann['key'];image=Image.open(ROOT/'.astra/pages'/f'{key}.png').convert('RGB');cells,meta=labels_for(ann)
   for table in ann['tables']:
    indices=[i for i,m in enumerate(meta) if m['table_id']==table['id']]
    tc=[cells[i] for i in indices];tm=[meta[i] for i in indices]
    try:
     metric=frozen(model,key,image,table,tc,tm,'annotated')
     summary[key]['frozen'].append(metric)
     # Real-model fused negative: two independent adjacent entries, both labels
     # survive as one indivisible string in one structural cell.
     pair=next(((i,j) for i,m in enumerate(tm) for j,n in enumerate(tm[i+1:],i+1) if m['row']==n['row'] and m['cell_id']!=n['cell_id'] and abs(m['column']-n['column'])==1),None)
     if pair:
      i,j=pair;b0=tm[i]['box'];b1=tm[j]['box'];box=[min(b0[0],b1[0]),min(b0[1],b1[1]),max(b0[2],b1[2]),max(b0[3],b1[3])]
      fused=rt.label_cell(tc[i].index,tc[i].text+' '+tc[j].text,[v/3 for v in box])
      neg=frozen(model,key,image,table,[c for k,c in enumerate(tc) if k not in pair]+[fused],tm,'fused_negative')
      summary[key].setdefault('fused_controls',[]).append(neg)
    except Exception as exc:
     summary[key]['frozen'].append(dict(table=table['id'],mode=mode,error=repr(exc)))
     print('ERROR',key,table['id'],mode,repr(exc),flush=True)
    save('summary.json',summary)
  save(f'forwards-{mode}.json',forwards)
 save('manifest.json',dict(annotations={a['key']:hashlib.sha256((ROOT/'docs/records/tables/annotations'/f'{a["key"]}.json').read_bytes()).hexdigest() for a in annotations},
   scripts={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'.astra/docling_research/research_tables.py',ROOT/'.astra/docling_research/research_layout.py']},
   offline=True,recognition='unique labels, not recognised text'))

if __name__=='__main__':main()
