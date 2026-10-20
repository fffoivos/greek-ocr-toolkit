"""Offline lead contact sheets from ALL reads, including VOID contexts.

Re-run after n1_decide.py after r2. No annotations are inferred. The lead answer
template is created empty only once, so a later rebuild cannot erase lead work.
"""
import hashlib
import json
from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont
from n1r2_prepare import OUT, SCRATCH, rows, sha, dump

DEST=SCRATCH/'n1_review/raised'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)

def paste_fit(canvas,path,box):
    with Image.open(path) as im:
        im=im.convert('RGB'); w,h=box[2]-box[0],box[3]-box[1]
        scale=min(w/im.width,h/im.height)
        size=(max(1,round(im.width*scale)),max(1,round(im.height*scale)))
        im=im.resize(size,Image.Resampling.LANCZOS)
        canvas.paste(im,(box[0]+(w-size[0])//2,box[1]+(h-size[1])//2))

def reference_set(approved):
    # Use exact approved controls only; never upgrade an unapproved bed/read to truth.
    raised=sorted([r for r in approved if r['truth']=='raised dot'],key=lambda r:r['slot_id'])[:2]
    baseline=sorted([r for r in approved if r['truth']=='baseline dot'],key=lambda r:(not r['document'].startswith('elstat:'),r['slot_id']))[:2]
    assert len(raised)==len(baseline)==2
    return raised+baseline

def build(out=OUT,dest=DEST):
    dest.mkdir(parents=True,exist_ok=True)
    decisions=rows(out/'decisions.jsonl'); bed={r['slot_id']:r for r in rows(out/'step1_rendered_v3.jsonl')}
    cards=json.loads((out/'owner_sheet/cards.json').read_text())
    group={r['slot_id'] for r in cards if r['group']=='Hyphen printed as raised dot'}
    selected=sorted([r for r in decisions if r['lead_pixel_check_required'] or r['slot_id'] in group],key=lambda r:(r['document'],r['slot_id']))
    refs=reference_set(rows(out/'controls/approved.jsonl'))
    for r in [*refs,*[bed[r['slot_id']] for r in selected]]:
        for kind in ('line','zoom'): assert sha(r[kind])==r[kind+'_sha256']
    same_doc=len({r['document'] for r in refs})==1
    limitation=None if same_doc else 'Same-document references UNAVAILABLE: no approved baseline-dot controls in the raised-control document. Cross-document approved references shown; lead substitution required.'
    sheets=[]; cells=[]
    for offset in range(0,len(selected),8):
        chunk=selected[offset:offset+8]; number=offset//8+1
        canvas=Image.new('RGB',(2400,3260),'white'); draw=ImageDraw.Draw(canvas)
        draw.text((35,20),f'N1 raised-dot lead review / sheet {number} / {len(chunk)} bed cells + 4 references',font=font(37,True),fill='black')
        draw.text((35,70),'All reads shown, including VOID. Raised-dot calls are evidence awaiting lead pixels.',font=font(27),fill='black')
        if limitation:
            for i,line in enumerate(textwrap.wrap(limitation,153)):
                draw.text((35,112+i*30),line,font=font(26,True),fill='#9b2318')
        refinfo=[]
        for j,r in enumerate(refs):
            x=30+j*590; y=190
            draw.rectangle((x,y,x+575,y+465),outline='#777777',width=2)
            draw.text((x+12,y+10),f'Reference {j+1}: APPROVED {r["truth"]}',font=font(24,True),fill='black')
            for k,line in enumerate(textwrap.wrap(r['document'],42)):
                draw.text((x+12,y+45+k*26),line,font=font(22),fill='black')
            paste_fit(canvas,r['zoom'],(x+12,y+112,x+563,y+358))
            paste_fit(canvas,r['line'],(x+12,y+370,x+563,y+445))
            refinfo.append({k:r[k] for k in ('slot_id','truth','document','line_sha256','zoom_sha256','approval_cell_number')})
        info=[]
        for j,r in enumerate(chunk):
            n=offset+j+1; x=30+(j%2)*1180; y=700+(j//2)*630; source=bed[r['slot_id']]
            draw.rectangle((x,y,x+1150,y+600),outline='#555555',width=2)
            draw.text((x+15,y+12),f'Cell {n} / Google {json.dumps(r["google_glyph"],ensure_ascii=False)} / {r["position"]}',font=font(29,True),fill='black')
            for k,line in enumerate(textwrap.wrap(r['slot_id'],85)):
                draw.text((x+15,y+50+k*24),line,font=font(21),fill='black')
            paste_fit(canvas,source['zoom'],(x+20,y+95,x+1130,y+385))
            paste_fit(canvas,source['line'],(x+20,y+400,x+1130,y+475))
            for k,read in enumerate(r['reads']):
                label=f'{read["context"]}.{read["reader"]} [{read["context_status"]}]: {read["meaning"] or "not read"}'
                if read.get('confidence'): label+=' / '+read['confidence']
                draw.text((x+15,y+490+k*35),label,font=font(26),fill='black')
            draw.text((x+15,y+565),'Lead printed glyph: __________________',font=font(24),fill='black')
            entry=dict(cell_number=n,slot_id=r['slot_id'],document=r['document'],google_glyph=r['google_glyph'],
                       reads=r['reads'],from_hyphen_sheet_group=r['slot_id'] in group,
                       line_sha256=source['line_sha256'],zoom_sha256=source['zoom_sha256'],sheet=f'raised_{number:02}.png',
                       bbox=[x,y,x+1150,y+600])
            info.append(entry);cells.append(entry)
        path=dest/f'raised_{number:02}.png';canvas.save(path)
        sheets.append(dict(file=path.name,sha256=sha(path),bed_cells=len(chunk),total_cells=len(chunk)+4,
                           references=refinfo,cells=info,same_document_references=same_doc))
    index=dict(bed_cells=len(cells),sheets=sheets,reads_present=sorted({f'{a["context"]}.{a["reader"]}' for r in selected for a in r['reads'] if a['read_status']!='missing'}),
               complete_same_document_references=same_doc,reference_limitation=limitation,
               selection='ANY raised-dot read (VALID, VOID or INVALID) UNION Hyphen printed as raised dot sheet group',
               max_total_cells_per_sheet=12,source_decisions_sha256=sha(out/'decisions.jsonl'),
               source_cards_sha256=sha(out/'owner_sheet/cards.json'))
    dump(dest/'sheets_index.json',index)
    template=out/'lead_raised_template.jsonl'
    if not template.exists(): template.write_text('')
    print(json.dumps(dict(cells=len(cells),sheets=len(sheets),reference_limitation=limitation)))
    return index
if __name__=='__main__': build()
