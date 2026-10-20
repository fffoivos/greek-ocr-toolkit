"""Synthetic S7 boundary probes; no native crops and no learned forward passes."""
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import json
import numpy as np
from greekocr.labelfix import ink as I, toolkit_geometry as G
from greekocr.labelfix.ctc_align import Alignment
from greekocr.glyphs.letters import LetterBox

out={}
# A locally legal 12-pixel mark is discarded before per-column clipping.
lab=np.zeros((70,80),int);lab[21:24,18:22]=1
mean=35.-.5*np.arange(80);base=mean+20
ci=I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,mean,base,[],255.,80,70,20.)
c=NS(index=1,x0=18,x1=22,y0=21,y1=24,w=4,h=3,cx=20.,role='mark',darkness=20.,area=12)
ci.components=[c]
ci.shared_guides=NS(mean=mean,base=base,ascender=mean-10,descender=base+10)
body=NS(index=2,x0=15,x1=45,y0=20,y1=40,w=30,h=20,cx=30.,role='letter')
slot=dict(component=body,component_ids=[],region_bounds=[15,45],case_class='lowercase_body')
b=I._blob(lab==1,0,0,'detached',ci)
q=I.zone_blob(ci,b,upper=mean)
ev=I.mark_evidence(ci,15,45,base_letter='α',certified_body=(15,45),letter_region=slot)
out['per_x_legal_mark_lost_before_clip']=dict(original_pixels=b.area,legal_pixels=q.area if q else 0,
    found=len(ev.above),slot_center_meanline=ev.meanline,mark_column_meanlines=mean[18:22].tolist())

# The physical adapter uses max() tie breaking and leaves the other piece unassigned.
lab=np.zeros((40,40),int);lab[10:30,5:15]=1;lab[10:30,25:35]=2
ci=I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,np.full(40,10.),np.full(40,30.),[],255.,40,40,20.)
ci.components=[NS(index=i) for i in (1,2)]
boxes=[LetterBox(5,10,15,30,(1,),1,1),LetterBox(25,10,35,30,(2,),1,1)]
al=Alignment.from_record(dict(prediction='α',spans=[['α',0,1,5.,35.]],confidence=.9,n_frames=10,scale=1.,strip_width=40))
with patch.object(G,'glyph_view',lambda ink:None),patch.object(G,'letter_boxes',lambda view:boxes):
    slots=G.physical_slots(ci,'α',al)
out['S1_equal_overlap']=dict(mapping=ci.physical_mapping,slot={k:slots[0][k] for k in
    ('component_ids','localisation_unknown','segmentation_uncertain','ambiguity')})

p=Path(__file__).resolve().parent/'geometry_probes.json'
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
