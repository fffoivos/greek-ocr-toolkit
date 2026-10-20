"""Hash-bound owner page reading and serialization, independent of reference fields."""
from dataclasses import asdict
import hashlib
import html
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
from greekocr.labelfix import reading as R, ink as I, case
from greekocr.labelfix.text import clusters,nfd,nfc

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_SHAPE='docs/labelfix/markshape_model_S4.json'
SOURCES=('scripts/labelfix/owner_reading.py','scripts/labelfix/owner_pages_build.py','scripts/labelfix/owner_pages_build_combined.py','greekocr/labelfix/reading.py','greekocr/labelfix/ink.py','greekocr/labelfix/case.py','greekocr/labelfix/segmentation.py','greekocr/labelfix/markshape.py')
SOURCES += ('greekocr/labelfix/toolkit_geometry.py','greekocr/glyphs/letters.py','greekocr/glyphs/components.py','greekocr/glyphs/baseline.py','greekocr/pages/font.py')

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def policy(output='print'):
    data=dict(schema='sf1-constraints-v1',output=output,rules=sorted(R.APPLIED_CONSTRAINT_RULES),reader_sha256=digest(ROOT/'greekocr/labelfix/reading.py'))
    return dict(data,sha256=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest())

class ReadingConfiguration(dict):
    """Configuration verified against checkout, assets and explicit output policy."""


def load_configuration(path):
    c=json.loads(Path(path).read_text())
    if c.get('schema')!='sf1-reading-v1':raise ValueError('explicit sf1-reading-v1 configuration required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if c['detector_commit']!=head:raise ValueError('detector commit differs from checkout')
    if c['source_sha256']!={p:digest(ROOT/p) for p in SOURCES}:raise ValueError('detector source hash mismatch')
    for name,default in [('shape_model',DEFAULT_SHAPE),('case_model','docs/labelfix/case_model_S5.json')]:
        asset=c[name];asset.setdefault('path',default)
        if digest(ROOT/asset['path'])!=asset['sha256']:raise ValueError(name+' hash mismatch')
    if c['constraint_policy']!=policy(c['constraint_policy']['output']):raise ValueError('constraint policy hash mismatch')
    if c['constraint_policy']['output'] not in ('print','normalised'):raise ValueError('unknown output policy')
    if 'r1_checkpoint' not in c:raise ValueError('r1_checkpoint must be explicit (null for detector-only)')
    if c['r1_checkpoint'] is not None:
        ck=c['r1_checkpoint']
        if digest(ROOT/ck['path'])!=ck['sha256']:raise ValueError('R1 checkpoint hash mismatch')
    case.configure_model(ROOT/c['case_model']['path'])
    return ReadingConfiguration(c)

def serialize(rd):
    slots=[]
    for i,s in enumerate(rd.slots,1):
        c=s.get('component')
        d={k:v for k,v in s.items() if k not in ('component','evidence','naming')}
        d['display_slot']=i
        d['parts']=list(s.get('parts',()))
        d['bbox']=[c.x0,c.y0,c.x1,c.y1] if c is not None else s.get('bbox')
        d['component_ids']=list(s.get('component_ids',()))
        ev=s.get('evidence',{})
        d['evidence']=ev.to_record() if hasattr(ev,'to_record') else ev
        naming=s.get('naming',{})
        d['naming']=asdict(naming) if hasattr(naming,'__dataclass_fields__') else naming
        slots.append(d)
    record = dict(schema='line-reading-sf1-v1',text=rd.text,slots=slots,unnamed=rd.unnamed,
        opening_quotes=rd.opening_quotes,removed_by_constraint=rd.removed_by_constraint,constraint_flags=rd.constraint_flags)
    if getattr(rd,'geometry',None):record['geometry']=rd.geometry
    return record

def reading_html(record):
    it=iter(record['slots']);out=[]
    for cl in clusters(nfd(record['text'])):
        text=html.escape(nfc(cl.base+cl.marks))
        if cl.base.isalpha():
            sl=next(it)
            if sl.get('hold') or sl.get('constraint_flags'):
                text=f'<span class="un" title="reader and detector disagree / impossible by rule">{text}</span>'
            elif sl.get('unnamed'):
                text=f'<span class="un" title="mark detected, not named">{text}</span>'
        out.append(text)
    return ''.join(out)

def page_reading(path,model,line,alignment,config,uri,combine=None):
    if not isinstance(config,ReadingConfiguration):raise ValueError('explicit hash-bound reading configuration required; use load_configuration')
    if alignment is None:raise ValueError('missing cached alignment')
    with Image.open(path) as source:im=source.convert('L')
    ci=I.analyse(im)
    raw=R.read_ink(ci,line['model'],alignment,model,filtered=False)
    rawrecord=serialize(raw)
    rd=combine(line['line_id'],raw)[0] if combine else raw
    rd,_=R.apply_constraints(rd,output=config['constraint_policy']['output'])
    record=serialize(rd)
    boxes=[];zones=[]
    for sl,rawsl in zip(record['slots'],rawrecord['slots']):
        ev=sl['evidence'];slot=sl['display_slot'];bbox=sl['bbox']
        sl['raw_parts']=rawsl['parts']
        sl['raw_detection']=rawsl['evidence']
        if bbox:
            xh=ev.get('xh',ci.xh);window=ev.get('window',[bbox[0],bbox[2]])
            zones.append(dict(display_slot=slot,mark_zone=[window[0],ev.get('meanline',bbox[1])-1.3*xh,window[1],ev.get('baseline',bbox[3])+.9*xh]))
        for field,kind in [('above','above'),('below','below'),('apostrophes','above')]:
            for b in ev.get(field,[]):
                status='flagged-by-constraint' if sl.get('constraint_flags') else 'raw-detection'
                boxes.append(dict(kind=kind,bbox=b['bbox'],display_slot=slot,status=status,source_ids=b.get('source_ids'),pixel_runs=b.get('pixel_runs')))
    for b in record['opening_quotes']:boxes.append(dict(kind='quote',bbox=b['bbox'],status='raw-detection'))
    scale=2 if im.width<700 else 1
    big=im.convert('RGB').resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);draw=ImageDraw.Draw(big)
    try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',11*scale)
    except OSError:font=None
    for box in boxes:
        color=(180,100,0) if box['status']=='flagged-by-constraint' else (40,80,200) if box['kind']=='below' else (30,140,60)
        draw.rectangle([v*scale for v in box['bbox']],outline=color,width=2)
    for sl in record['slots']:
        if sl['bbox']:draw.text((sl['bbox'][0]*scale,im.height*scale-12*scale),str(sl['display_slot']),fill=(120,120,120),font=font)
    if big.width>1000:big=big.resize((1000,int(big.height*1000/big.width)),Image.Resampling.LANCZOS)
    side=dict(reading=record['text'],boxes=boxes,letters=[[s['bbox'][0],s['bbox'][2]] for s in record['slots'] if s['bbox']],
              letter_zones=zones,line_reading=record,raw_line_reading=rawrecord,reading_configuration=config)
    return reading_html(record),record['text'],uri(big),side
