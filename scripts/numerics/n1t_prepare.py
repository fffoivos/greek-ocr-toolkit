"""Phase-A offline enumeration, exact geometry, v3 renders, unfitted dash controls."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[2]),str(Path(__file__).resolve().parent)]
from greekocr.numerics.locks import load_locks
from greekocr.numerics.line_complete import enumerate_line, select_lines
from greekocr.numerics.slots_geom import locate_slot
from greekocr.numerics.tokens import tokenize
from greekocr.numerics.dash import digit_widths, measure_dash
from n1_render import SCRATCH, render
from n1t_packs import rows, sha, dump
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/n1';RUN=Path.home()/'Projects/collect-v3-data/run/W1'
COLLECT=Path.home()/'Projects/greek-ocr-toolkit-sol-collect'


def jsonl(path, records):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f: f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))


def controls_sheet(controls, widths, path):
    from PIL import Image, ImageDraw, ImageFont
    canvas=Image.new('RGB',(1800,300*((len(controls)+2)//3)),'white');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    index=[]
    for i,c in enumerate(controls):
        x=(i%3)*600;y=(i//3)*300
        draw.text((x+10,y+6),f"Cell {c['approval_cell_number']}    hyphen / en / em: ______",font=font,fill='black')
        with Image.open(c['zoom']) as im:
            im=im.convert('RGB');scale=min(580/im.width,190/im.height)
            im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
            canvas.paste(im,(x+10,y+40))
        w=widths[c['slot_id']]
        if w['status']=='ok':
            length=w['median_digit_width']*3*scale
            draw.line((x+20,y+253,x+20+length,y+253),fill='black',width=2)
            for xx in (x+20,x+20+length):draw.line((xx,y+247,xx,y+259),fill='black',width=2)
            draw.text((x+20,y+265),'one digit width',font=font,fill='black')
        else: draw.text((x+20,y+245),'digit width unavailable',font=font,fill='black')
        index.append(dict(cell_number=c['approval_cell_number'],slot_id=c['slot_id'],digit_width=w,zoom_sha256=c['zoom_sha256']))
    path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path)
    return index


def main():
    from PIL import Image
    from greekocr.glyphs.components import line_glyphs
    out=OUT/'n1t'
    if (_data_input(out/'slots.jsonl')).exists(): raise ValueError('refusing to overwrite phase A build')
    prior={str(p):sha(p) for p in OUT.rglob('*') if p.is_file()}
    for name in ('sep.md','sep2.md'):
        p=ROOT/'docs/records/labelfix/secondary/prompts'/name;prior[str(p)]=sha(p)
    priorpath=SCRATCH/'n1_review/n1t_prior.json'
    if priorpath.exists():
        prior=json.loads(priorpath.read_text())
        assert all(sha(p)==h for p,h in prior.items())
    else: dump(priorpath,prior)
    locks=load_locks(OUT);frame=rows(OUT/'frame_step1.jsonl');cards=json.loads((_data_input(OUT/'owner_sheet/cards.json')).read_text())
    summary=json.loads((OUT/'owner_sheet/summary.json').read_text())
    assert summary['cards']==len(cards) and sha(_data_input(OUT/'owner_sheet/cards.json'))==summary['hashes']['cards.json']
    # r1 data is independently decoded and gates/provenance rechecked, not trusted by filename.
    from n1_score import decode_and_gate
    byslot={s['slot_id']:s for s in frame};valid=[];gates={}
    for i in range(1,8):
        ctx=f'ctx{i:02}';key=json.loads((OUT/'keys'/f'{ctx}.json').read_text())
        gate,decoded=decode_and_gate(key,rows(OUT/'answers'/f'{ctx}.r1.jsonl'))
        scan=json.loads((OUT/'answers'/f'{ctx}.r1.scan.json').read_text());run=json.loads((OUT/'answers'/f'{ctx}.r1.run.json').read_text())
        assert scan['ok'] and scan['scanner_version'] in (4, 'v4.4-canonical') and run['rc']==0 and run['model']=='gpt-6.1-sol'
        gates[ctx]=gate['status']
        if gate['status']=='VALID': valid += [byslot[r['slot_id']] for r in decoded if not r['control']]
    wanted={c['slot_id'].split(':t')[0] for c in cards}|{s['line_id'] for s in valid if s['glyph']=='-' and s['digit_count']>=4}
    approved=rows(OUT/'controls/approved.jsonl');dashcontrols=[c for c in approved if c['truth']=='hyphen or dash']
    control_lines={c['line_id'] for c in dashcontrols};byid={}
    for line in (RUN/'features.jsonl').open():
        row=json.loads(line)
        if row['id'] in wanted|control_lines:byid[row['id']]=row
    ids,selection=select_lines(cards,valid,frame,byid,locks)
    locks.assert_fit_rows(control_lines)
    inputs={str(RUN/'features.jsonl'):sha(RUN/'features.jsonl')}
    allrows=[byid[lid] for lid in sorted(set(ids)|control_lines)]
    request=SCRATCH/'n1_review/n1t_crop_request.jsonl';result=SCRATCH/'n1_review/n1t_crops.json'
    if request.exists(): assert rows(request)==allrows
    else: jsonl(request,allrows)
    # Invoke only the established offline crop function under its native Pillow.
    code='import sys; sys.path.insert(0,sys.argv[1]); from pathlib import Path; from n1cb_prepare import regenerate; regenerate(Path(sys.argv[2]),Path(sys.argv[3]))'
    subprocess.run(['/usr/bin/arch','-arm64',str(COLLECT/'.venv/bin/python'),'-B','-s','-c',code,str(ROOT/'scripts/numerics'),str(request),str(result)],check=True)
    crops={r['line_id']:r for r in json.loads(result.read_text())['records']}
    document_cache={}
    def document(row):
        p=RUN/'pages'/(row['page_id']+'.json');inputs[str(p)]=sha(p);record=json.loads(p.read_text())
        response=Path(record['response'])
        if str(response) not in document_cache:
            inputs[str(response)]=sha(response)
            if inputs[str(response)]!=record['response_sha256']:raise ValueError('response custody mismatch')
            document_cache[str(response)]=json.loads(response.read_text())['document']
        return document_cache[str(response)]
    slots=[];lines=[];width_cache={}
    for index,lid in enumerate(ids):
        row=byid[lid];doc=document(row);tokens=tokenize(row['text']);crop=crops[lid]
        glyphs=None
        if not crop['crop_unavailable']:
            assert sha(crop['crop'])==row['crop_sha256']
            with Image.open(crop['crop']) as im:glyphs=line_glyphs(im)
        for ti,t in enumerate(tokens):width_cache[(lid,ti)]=digit_widths(row,t,doc)
        current=enumerate_line(row,locks)
        for s in current:
            g=locate_slot(row,s,doc,exact_boundary=True)
            s.update(geometry=g,google_glyph=s['glyph'],source=row['source'],source_era=next(r['source_era'] for r in frame if r['line_id']==lid),
                document=row['source']+':'+row['item'],crop_sha256=row['crop_sha256'],crop_unavailable=crop['crop_unavailable'])
            if crop['crop_unavailable']:
                s['geometry']=dict(geom_status='crop_unavailable',reason=crop['crop_error'])
            elif g['geom_status']=='ok':
                s.update(render(crop['crop'],g,SCRATCH/'n1_cache/n1t_rendered',glyphs=glyphs))
                s['dash']=measure_dash(s['measurements'],width_cache[(lid,s['token_index'])])
            slots.append(s)
        lines.append(dict(line_id=lid,text=row['text'],source=row['source'],source_era=current[0]['source_era'] if current else row['source'],
            crop=crop.get('crop'),crop_sha256=row['crop_sha256'],slots=[s['slot_id'] for s in current]))
        if (index+1)%25==0: print('rendered lines',index+1,'slots',len(slots),flush=True)
    widths={}
    for c in dashcontrols:
        row=byid[c['line_id']];token=tokenize(row['text'])[int(c['slot_id'].split(':t')[1].split(':')[0])]
        widths[c['slot_id']]=digit_widths(row,token,document(row))
    sheet=SCRATCH/'n1_review/dash_controls.png';index=controls_sheet(dashcontrols,widths,sheet)
    jsonl(OUT/'controls/dash_types_template.jsonl',[dict(slot_id=c['slot_id'],cell_number=c['approval_cell_number'],truth=None,lead_note='') for c in dashcontrols])
    dump(out/'dash_controls_index.json',dict(sheet=str(sheet),sha256=sha(sheet),cells=index,ratio_printed=False))
    jsonl(out/'slots.jsonl',slots);jsonl(out/'lines.jsonl',lines)
    dump(out/'selection.json',dict(selection,r1_gates=gates,line_ids=ids,step1_documents_only=True,reserved_lines=0))
    dump(out/'build.json',dict(lines=len(lines),slots=len(slots),geometry=dict(Counter(s['geometry']['geom_status'] for s in slots)),
        inputs=inputs,crops=str(result),dash_control_sheet=str(sheet),prior_snapshot=str(SCRATCH/'n1_review/n1t_prior.json')))
    assert all(sha(p)==h for p,h in prior.items())
    print(json.dumps(dict(lines=len(lines),slots=len(slots),geometry=dict(Counter(s['geometry']['geom_status'] for s in slots)))))
if __name__=='__main__':main()
