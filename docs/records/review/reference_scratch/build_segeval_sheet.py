import json,os,sys,re,html as H
from PIL import Image
sys.path.insert(0,os.path.expanduser('~/Projects/greek-ocr-toolkit-cleanup'))
from greekocr.adjudicate.owner_sheet import render
HERE=os.path.dirname(os.path.abspath(__file__))
B=os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1')
rows=[json.loads(l) for l in open(f'{B}/scored/owner_rows.jsonl')]
seg={json.loads(l)['row_id']:json.loads(l) for l in open(os.path.join(HERE,'segeval1_seg.jsonl'))}
TXT={'extra_text','missing_word_or_span','crop_clipped','merged_two_lines'}
def faults(r):
    a=r['reader_answer']
    return [k for k in ('multi_line','neighbour_whole_word','rotated','horizontally_missegmented') if a.get(k)=='yes']+sorted(set(a.get('errors',[]))&TXT)
def grp(r):
    d=r['decision']; f=faults(r)
    if r['reader_state']=='unresolved': return 'un'
    if d=='REJECT': return 'tp' if f else 'fp'
    return 'fn' if f else 'ok'
def inv(frame):
    (a,b,c),(d,e,f),_=frame['source_to_measurement']; det=a*e-b*d
    return [[e/det,-b/det,(b*f-c*e)/det],[-d/det,a/det,(c*d-a*f)/det]]
def pt(M,x,y):
    return M[0][0]*x+M[0][1]*y+M[0][2], M[1][0]*x+M[1][1]*y+M[1][2]
def rect(M,b,cls):
    xs,ys=zip(pt(M,b[0],b[1]),pt(M,b[2],b[3]))
    x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    return f'<rect class="{cls}" x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}"/>'
def poly(M,pts,cls):
    return '<polyline class="%s" points="%s"/>'%(cls,' '.join('%.1f,%.1f'%pt(M,x,y) for x,y in pts))
def overlay(s,w,h):
    e=s['evidence']; M=inv(s['frame']); out=[]
    for d in e.get('detected_rows',[]):
        if d['votes']<=0: continue
        side=d['side']; c=d['curves']
        if side=='main':
            out.append(poly(M,c['ascender'],'asc')); out.append(poly(M,c['base'],'base'))
            out.append(poly(M,c['mean'],'mean')); out.append(poly(M,c['descender'],'desc'))
        else:
            out.append(poly(M,c['ascender'],'nasc')); out.append(poly(M,c['base'],'nbase'))
    n=e.get('neighbour_evidence') or {}
    for g in n.get('group_bindings',[]):
        if g['side']=='main': cls='wmain'
        elif g.get('unresolved'): cls='wunres'
        elif g.get('positive'): cls='wwhole'
        else: cls='wpart'
        out.append(rect(M,g['bbox'],cls))
    bx=e['box_evidence'].get('bbox')
    if bx: out.append(rect(M,bx,'tbox'))
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">'+''.join(out)+'</svg>'
def numbers(s):
    e=s['evidence']; bits=[]
    chars=e.get('characters'); p=e['box_evidence'].get('prediction') or {}
    if p.get('expected') is not None:
        ratio=(chars+1)/(p['expected']+1); bits.append(f"OCR chars {chars} vs expected {p['expected']:.1f} → ratio {ratio:.2f} (rule keeps 0.5–1.5)")
    pad=e.get('padding_evidence') or {}
    if pad.get('available'): bits.append(f"padding {pad['total_padding_line_heights']:.2f} line-heights (max 1.5)")
    n=e.get('neighbour_evidence')
    if n:
        if n.get('status')=='measured': bits.append(f"whole neighbour words {n.get('whole_neighbour_words')} (max 2), partial {n.get('partial_neighbour_words')}, extra full lines {n.get('additional_full_line_count')}")
        else: bits.append(f"neighbour words {n.get('status')}")
    else:
        bits.append('no neighbouring rows detected')
    fr=s['frame']
    if fr.get('normalization_cw'): bits.append(f"measured after {fr['normalization_cw']}° turn ({fr['status']})")
    return ' | '.join(bits)
cards=[]; n={'fp':0,'tp':0,'fn':0,'un':0,'ok':0}; svgs={}; sizes={}
for r in rows:
    g=grp(r); n[g]+=1
    if g=='ok' and n['ok']>12: continue
    a=r['reader_answer']; flags=faults(r)
    s=seg[r['line_id']]; img=os.path.join(B,r['crop'])
    tvc=('crop_ok '+a.get('crop_ok','?')+' | errors: '+(', '.join(a.get('errors',[])) or 'none')+(' | '+a.get('detail','') if a.get('detail') else ''))
    with Image.open(img) as im: w,h=im.size
    cards.append({'line_id':r['line_id'],'label':r['line_id'],'image':img,'group':g,
      'rows':[{'name':'Google','text':r.get('google_text','')},{'name':'Filter 0.5','text':f"{r['decision']}: {r.get('reason','')}"},{'name':'Numbers','text':numbers(s)},{'name':'Text vs crop','text':tvc},{'name':'Owner standard','text':('FAULT: '+', '.join(flags) if flags else 'fine — one line, text matches, no whole neighbour line')+(' — '+a.get('segmentation_detail','') if a.get('segmentation_detail') else '')}],
      'tags':[{'text':r['line_id'].split('--')[0]},{'text':r['decision'],'class':'bad' if r['decision']=='REJECT' else 'ok'}],'doc_id':f"segeval:{r['line_id']}",'note_data':{'line':r['line_id'],'id':f"segeval:{r['line_id']}"}})
    svgs[r['line_id']]=overlay(s,w,h); sizes[r['line_id']]=(w,h)
groups=[('fp',f"Filter REJECTED, line is fine under the owner standard = false positives ({n['fp']}/50)"),('tp',f"Filter REJECTED, line has a fault = correct drops ({n['tp']}/50)"),('fn',f"Filter ACCEPTED, line has a fault = false negatives ({n['fn']}/100)"),('un',f"Reader unresolved ({n['un']})"),('ok',f"Filter ACCEPTED, line is fine (12 of {n['ok']} shown)")]
intro=('Uniform draw, seed 20261019: 50 lines the filter rejected and 100 it accepted, none used in any calibration. Read blind by Sol with the crop and the Google text side by side (bsb protocol + owner rubric). '
 'Scored under the owner standard (19 Oct): a fault is any of multi-line, rotated, end clipped, a whole neighbouring word, or text that is more or less than the visible line (extra_text, missing span, crop clipped, merged lines). Partial neighbour letter bodies alone are allowed. '
 'Result: false positives 26/50 (24 from the two length rules), false negatives 7/100 (6 end/edge clips, 1 neighbour words).\n'
 'Boxes drawn on each crop are the saved evidence the filter decided on (census_02 export, policy 8334dd40): BLUE = the text box whose length is compared with the OCR output; GREEN lines = the target row (ascender, mean, base, descender); ORANGE dashed = neighbouring rows above/below; '
 'thin GREEN boxes = word groups on the target row; RED = a whole neighbouring word (counted against the max of 2); GREY dashed = a clipped neighbouring word (allowed); PURPLE dashed = unresolved. Press b to hide/show the boxes. Zoom: hover or click the crop for a 3× lens; press z to show the selected crop at 3× full size (scroll sideways), z again to shrink.\n'
 'Keys: ↑ ↓ move between lines (also from inside the note box); SPACE marks the selected line KEEP (green tick), again DROP (red cross), again clears; it also works inside an empty note box, and clicking the badge cycles too. Esc leaves the note box. Marks and notes autosave.')
spec={'title':'Segmentation filter 0.5 — blind check on 150 unseen lines','intro':intro,'groups':[{'id':g,'heading':h} for g,h in groups]}
html=render(cards,spec)
# wrap each card's crop image with its evidence overlay
parts=html.split('<div class="card"')
assert len(parts)==len(svgs)+1
for i in range(1,len(parts)):
    p=parts[i]; lid=re.search(r'<div class="lid">([^<]+)</div>',p).group(1); svg=svgs[H.unescape(lid)]
    j=p.index('<img '); k=p.index('>',j)+1
    w,h=sizes[lid]; scale=min(3.0, 940/w, 300/h); dw=int(w*scale)
    parts[i]=p[:j]+f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}">'+p[j:k]+svg+'</div><div class="lens" hidden></div></div>'+p[k:]
html='<div class="card"'.join(parts)
css='''
.ov{position:relative;max-width:100%}.ov svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:hidden}.noboxes .ov svg{display:none}
.ov svg *{fill:none;vector-effect:non-scaling-stroke}
.ov .tbox{stroke:#1d5fd6;stroke-width:2}
.ov .asc,.ov .base{stroke:#15a04a;stroke-width:1.6}.ov .mean,.ov .desc{stroke:#15a04a;stroke-width:1;stroke-dasharray:3 3;opacity:.7}
.ov .nasc,.ov .nbase{stroke:#f08c00;stroke-width:1.4;stroke-dasharray:5 3}
.ov .wmain{stroke:#15a04a;stroke-width:1;opacity:.55}.ov .wwhole{stroke:#d61f1f;stroke-width:2.2}.ov .wpart{stroke:#7a7a7a;stroke-width:1.2;stroke-dasharray:4 3}.ov .wunres{stroke:#8a2be2;stroke-width:1.6;stroke-dasharray:4 3}
.card{position:relative;border-width:2px}.card.cur{outline:3px solid #3b82f6;outline-offset:2px}.card.vkeep{border-color:#15a04a}.card.vdrop{border-color:#d61f1f}
.lid{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.verdict{font-family:var(--body);font-size:.78rem;font-weight:700;letter-spacing:.04em;padding:1px 9px;border-radius:999px;border:1px dashed var(--line);color:var(--muted);cursor:pointer;user-select:none;min-width:2.5em;text-align:center}
.verdict.KEEP{background:#15a04a;border-color:#15a04a;color:#fff}.verdict.DROP{background:#d61f1f;border-color:#d61f1f;color:#fff}
#tally{position:fixed;top:8px;right:12px;z-index:9;background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:.8rem;color:var(--muted);box-shadow:0 2px 8px rgba(0,0,0,.15)}
#tally b.k{color:#15a04a}#tally b.d{color:#d61f1f}
.zw{overflow-x:auto;overflow-y:hidden;max-width:100%}.zw .ov img{cursor:zoom-in}.ov.big{max-width:none}.lens{width:360px;height:160px}
'''
html=html.replace('</style></head>',css+'</style></head>',1)
js=open(os.path.join(HERE,'segeval_sheet.js')).read()
i=html.rindex('<script>'); j=html.rindex('</script>')
html=html[:i]+'<script>'+js+html[j:]
open(os.path.join(HERE,'sheet_segeval1.html'),'w').write(html); print('cards',len(cards),n,'bytes',len(html))
