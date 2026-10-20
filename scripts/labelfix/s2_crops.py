"""Draw before/after native-pixel detector witnesses; no OCR masks changed."""
from greekocr.ops.data_root import input_path as _data_input
import json,gzip
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path('docs/records/labelfix/spellcheck');D=O/'crops_S2';D.mkdir(exist_ok=True)
ls={l['line_id']:l for x in gzip.open(_data_input(O/'S2_lines.jsonl.gz'),'rt') if (l:=json.loads(x))}
notes=[json.loads(x) for x in open(O/'owner_notes_db_20261016.jsonl')]
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12)
thumbs=[]
for note in notes:
 l=ls[note['line_id']];im=Image.open(l['crop']).convert('RGB');w,h=im.size
 out=Image.new('RGB',(w,2*h+40),'white');draw=ImageDraw.Draw(out)
 for j,(label,key) in enumerate([('BEFORE','before_evidence'),('S2','evidence')]):
  y=20+j*(h+20);out.paste(im,(0,y));draw.text((2,y-17),label+' '+l['line_id'],fill='black',font=font)
  for s in l['slots']:
   for k,color in [('above','green'),('below','blue'),('diagnostics','gray')]:
    for b in s[key].get(k,[]):
     x0,y0,x1,y1=b['bbox'];draw.rectangle((x0,y0+y,x1,y1+y),outline=color,width=1)
   draw.text((s['bbox'][0],y+h-12),str(s['slot']),fill='red',font=font)
 out.save(D/(l['line_id']+'.png'))
 if l['dev'] and len(thumbs)<6:
  z=out.copy();z.thumbnail((950,260));thumbs.append(z)
contact=Image.new('RGB',(950,sum(z.height for z in thumbs)),'white');y=0
for z in thumbs:contact.paste(z,(0,y));y+=z.height
contact.save('/private/tmp/s2_dev_witnesses.png')
print('paired crops',len(notes))
