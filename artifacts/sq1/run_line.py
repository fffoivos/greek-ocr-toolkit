import json,hashlib,base64
from pathlib import Path
import numpy as np
from PIL import Image
from greekocr.labelfix import case,ink,reading,markshape
from greekocr.labelfix.ctc_align import Recognizer
from greekocr.labelfix.release_gate import policy_binding,serialize,compose_runtime
from scripts.labelfix.clariden.r1_extract import extract_line
from scripts.labelfix.clariden.l1_infer import load_reader,predictions
from scripts.labelfix.clariden.l1_common import overlay
from scripts.labelfix.owner_reading import page_reading,ReadingConfiguration
O=Path('artifacts/sq1'); lid='nlg--f4b52df5f8130047--s005-l0015'
protected={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('greekocr/labelfix').glob('*.py')}
binding=policy_binding(); protected.update(binding['sources']); (O/'protected_before.json').write_text(json.dumps(protected,indent=2))
p=Path.home()/'Projects/collect-v3-data/run/W1/crops'/f'{lid}.png'
ck=Path.home()/'Projects/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt'
assert hashlib.sha256(ck.read_bytes()).hexdigest()=='5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663'
im=Image.open(p).convert('L'); rec=Recognizer(ck,device='cpu',threads=4); al=rec.align_batch([im])[0]
(O/'alignment.json').write_text(json.dumps(al.to_record(),ensure_ascii=False,indent=2))
case.configure_model('docs/labelfix/case_model_S5.json'); model=markshape.load_model('docs/labelfix/markshape_model_S4.json')
raw=reading.read_ink(ink.analyse(im),al.prediction,al,model,filtered=False)
ss,wide,_,loss,coverage,size=extract_line(dict(id=lid,recogniser_text=al.prediction,_line=0),al.to_record(),im,evaluation=True)
samples=[dict(start=s[3],letter=s[4],mask=s[7][0]) for s in ss]
rck=Path('artifacts/labelfix_r1/output_3678928/A/best.pt')
pred=predictions(load_reader(rck,'cpu'),samples,np.asarray(wide,dtype=np.uint8),'cpu',512)
runtime=dict(id=lid,recogniser_text=al.prediction,detector=serialize(raw),recognition_confidence=al.confidence,image_width=im.width,recognition_evidence=al.recognition_evidence(raw.slots,im.width),coverage=coverage,r1_predictions=pred)
(O/'runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2))
# Use owner-sheet's exact detection_image renderer on the unmodified raw detector.
config=ReadingConfiguration(constraint_policy=dict(output='print'))
_,_,_,side=page_reading(p,model,dict(line_id=lid,model=al.prediction),al,config,lambda big: big.save(O/'line_overlay.png'))
(O/'owner_side.json').write_text(json.dumps(side,ensure_ascii=False,indent=2))
# Original Google label from C1 key, selected by id.
key=json.loads((Path.home()/'Projects/collect-v3-data/run/W1/c1/nlg__poly1900_key.json').read_text())
original=next(x['literal_label'] for x in key.values() if x['line_id']==lid)
b=dict(detector='S6',r1_sha256=hashlib.sha256(rck.read_bytes()).hexdigest(),policy_sha256=binding['sha256'])
out=dict(original=original,policy=binding,recogniser=al.prediction,checkpoint_sha256=hashlib.sha256(ck.read_bytes()).hexdigest(),r1_sha256=b['r1_sha256'],compositions={},overlays={})
for mode in ('PRESENCE','FULL'):
 out['compositions'][mode]=compose_runtime(runtime,mode)
 out['overlays'][mode]=overlay(dict(id=lid,label=original,script_class='greek_poly'),runtime,mode.lower(),b)
(O/'line_result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(dict(original=original,recogniser=al.prediction,overlays=out['overlays']),ensure_ascii=False))
