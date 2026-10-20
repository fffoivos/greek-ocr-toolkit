import sys,types,subprocess,json,socket,hashlib,time
from pathlib import Path
from collections import Counter
import greekocr.labelfix as package
start=time.monotonic()
def forbidden(*a,**kw):raise RuntimeError('offline baseline audit')
socket.socket.connect=forbidden;socket.create_connection=forbidden
head='efdf5756c513fc935d7302df4be85a0f9c084702';bindings={}
for short in ('ink','case','reading'):
 path=f'greekocr/labelfix/{short}.py'
 source=subprocess.check_output(['git','--no-optional-locks','show',head+':'+path])
 bindings[path]=hashlib.sha256(source).hexdigest()
 name='greekocr.labelfix.'+short;mod=types.ModuleType(name);mod.__package__='greekocr.labelfix';mod.__file__=str(Path(path).resolve())
 sys.modules[name]=mod;setattr(package,short,mod);exec(compile(source,path,'exec'),mod.__dict__)
from PIL import Image
from greekocr.labelfix import ink,reading,markshape
from greekocr.labelfix.ctc_align import Recognizer
Recognizer.__init__=forbidden;Recognizer.align_batch=forbidden
from greekocr.labelfix.sheet import load_alignments,crop_key
from scripts.labelfix.s5_validate import read
from scripts.labelfix.owner_reading import serialize
O=Path('docs/labelfix/spellcheck');lines=read(O/'S6_lines.jsonl.gz');truth=read(O/'S5_capital_truth.jsonl')
als=load_alignments(Path('.cache/labelfix/align_s0.jsonl'));model=markshape.load_model(Path('docs/labelfix/markshape_model_S4.json'))
by={}
for line in lines:
 with Image.open(line['crop']) as im:rd=reading.read_ink(ink.analyse(im),line['recogniser_text'],als[crop_key(line['crop'])],model,filtered=False)
 olds={r['start']:r for r in line['recogniser_slots']}
 by[line['line_id']]=[(olds[s['start']]['component_slot'],s['pixel_class'],s['case_class']) for s in rd.slots]
counts={k:Counter() for k in ('pixel','combined')}
for t in truth:
 r=next((s for s in by[t['line_id']] if s[0]==t['slot']),None)
 for k,i in [('pixel',1),('combined',2)]:
  d=bool(r and r[i]=='capital');v=t['truth'];counts[k].update(tp=int(d and v),fp=int(d and not v),fn=int(not d and v))
receipt=dict(head=head,original_sources=bindings,capitals=counts,lines=len(lines),network=False,ctc_forward_passes=0,elapsed_seconds=time.monotonic()-start)
(O/'S7_evidence/original_launch_baseline.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
