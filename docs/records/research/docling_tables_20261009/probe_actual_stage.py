"""Actual full-table fusion and ignored-field controls on Vouli page 35."""
import copy
from types import SimpleNamespace as NS
from research_tables import *
from docling_core.types.doc.page import TextDirection

name='s2-200e977f2dab5291c42c-p00035'
image=Image.open(ROOT/'pages'/(name+'.png')).convert('RGB')
model,captured,forwards=build_model('accurate')
cells,meta=controlled_cells(name,image,'line')
base=run_case(model,captured,name,image,cells,meta,TABLES[name],'probe-baseline')
left=next(c for c in cells if c.text=='L0126P00')
right=next(c for c in cells if c.text=='L0164P00')
lb=left.rect.to_bounding_box(); rb=right.rect.to_bounding_box()
union=[min(lb.l,rb.l),min(lb.t,rb.t),max(lb.r,rb.r),max(lb.b,rb.b)]
fused=label_cell(max(c.index for c in cells)+1,'FUSED_L0126P00_L0164P00',union)
fused_cells=[c for c in cells if c is not left and c is not right]+[fused]
fused_meta=[m for m in meta if m['token'] not in [left.text,right.text]]+[dict(id=fused.index,token=fused.text,source_box=[v*3 for v in union])]
fusion=run_case(model,captured,name,image,fused_cells,fused_meta,TABLES[name],'probe-fused-column')
changed=[]
for c in cells:
    b=c.rect.to_bounding_box(); d=(b.b-b.t)*.15
    skew=BoundingRectangle(r_x0=b.l,r_y0=b.b-d,r_x1=b.r,r_y1=b.b,
        r_x2=b.r,r_y2=b.t+d,r_x3=b.l,r_y3=b.t,coord_origin=CoordOrigin.TOPLEFT)
    changed.append(c.model_copy(update=dict(confidence=0.,from_ocr=False,
        orig='UNUSED_ORIG',text_direction=TextDirection.RIGHT_TO_LEFT,rect=skew)))
fields=run_case(model,captured,name,image,changed,meta,TABLES[name],'probe-fields-and-skew')
def final_json(kind):
    return json.loads((OUT/f'{name}.accurate.{kind}.matching-1.json').read_text())
bj=final_json('probe-baseline'); fj=final_json('probe-fused-column'); cj=final_json('probe-fields-and-skew')
assert bj['final_table_item']==cj['final_table_item']
save('actual-probes-summary.json',dict(baseline=base,fusion=fusion,fields=fields,
    same_final_table_after_field_and_skew_change=True,
    original_landing={left.text:bj['landing'][left.text],right.text:bj['landing'][right.text]},
    fused_landing=fj['landing'].get(fused.text,[]),forwards=forwards))
print('FIELD_AND_SKEW_INVARIANCE',True,'FUSION_LANDING',fj['landing'].get(fused.text,[]),flush=True)
