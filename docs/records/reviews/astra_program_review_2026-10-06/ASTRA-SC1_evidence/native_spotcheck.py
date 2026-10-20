"""Six existing S6 fixture crops only; no recognition, training or network."""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
R=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
O=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.letters import letter_boxes
from greekocr.labelfix import ink as I
from greekocr.labelfix.case import estimate_font
from greekocr.labelfix.reading import read_ink
from greekocr.labelfix.ctc_align import Alignment, Recognizer
from greekocr.labelfix.markshape import load_model
def forbidden(*a,**k):raise RuntimeError('No CTC permitted')
Recognizer.__init__=forbidden
model=load_model(R/'docs/labelfix/markshape_model_S4.json')
default=load_model(R/'docs/labelfix/markshape_model.json')
cases=json.loads((R/'tests/data/labelfix_s6/cases.json').read_text())
assert len(cases)<=6
results=[]
for c in cases:
    with Image.open(R/'tests/data/labelfix_s6'/f'{c["line_id"]}.png') as source: im=source.convert('L')
    g=line_glyphs(im);ci=I.analyse(im);estimate_font(ci)
    al=Alignment.from_record(c['alignment'])
    rd=read_ink(ci,c['recogniser_text'],al,model,filtered=False)
    # Same decoded crop; independently rebuild CropInk, exactly as the builder would.
    dr=read_ink(I.analyse(im),c['recogniser_text'],al,default,filtered=False)
    results.append(dict(line_id=c['line_id'],toolkit_xh=g.band.xh,s6_xh=ci.xh,
        toolkit_band_degree=g.band.degree,toolkit_letters=len(letter_boxes(g)),recogniser_letters=len(rd.slots),
        toolkit_unresolved=sum(not b.resolved for b in letter_boxes(g)),
        baseline_max_delta=float(np.max(abs(g.band.bottom-ci.bottom))),s6_font_source=ci.font_fit['source'],
        S4_model_reading=rd.text,builder_default_reading=dr.text,model_changes_text=rd.text!=dr.text))
    if c['line_id']=='602cc72e-p000113-l0030':
        canvas=im.convert('RGB'); d=ImageDraw.Draw(canvas)
        for arr,color in [(g.band.top,'blue'),(g.band.bottom,'blue'),(ci.top,'red'),(ci.bottom,'red')]:
            d.line(list(zip(range(im.width),map(float,arr))),fill=color,width=1)
        canvas.save(O/'native_guide_comparison.png')
(O/'native_spotcheck.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
