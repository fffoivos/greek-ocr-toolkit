import json,os,sys,re,html as H,collections
from PIL import Image
sys.path.insert(0,os.path.expanduser('~/Projects/greek-ocr-toolkit-cleanup'))
from greekocr.adjudicate.owner_sheet import render
HERE=os.path.dirname(os.path.abspath(__file__)); PREFIX=sys.argv[1] if len(sys.argv)>1 else 'gate'; OUT=sys.argv[2] if len(sys.argv)>2 else 'sheet_gate.html'
sys.path.insert(0,HERE); from sheet_common import toolpills
R=os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-recut'); S=f'{R}/docs/harvest/collect_v3_admission/segeval1'; G=f'{S}/gate2'
owner={json.loads(l)['line_id']:json.loads(l) for l in open(f'{S}/scored/owner_rows.jsonl')}
rows=[json.loads(l) for l in open(f'{G}/replay_segeval1.jsonl')]
def inv(frame):
    (a,b,c),(d,e,f),_=frame['source_to_measurement']; det=a*e-b*d
    return [[e/det,-b/det,(b*f-c*e)/det],[-d/det,a/det,(c*d-a*f)/det]]
def pt(M,x,y): return M[0][0]*x+M[0][1]*y+M[0][2], M[1][0]*x+M[1][1]*y+M[1][2]
def rect(M,b,cls):
    xs,ys=zip(pt(M,b[0],b[1]),pt(M,b[2],b[3])); x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    return f'<rect class="{cls}" x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}"/>'
def poly(M,pts,cls,close=False):
    return f'<{"polygon" if close else "polyline"} class="{cls}" points="'+' '.join('%.1f,%.1f'%pt(M,x,y) for x,y in pts)+'"/>'
def noguard(r):
    return r['verdict_08'],r['after']['reason']
def overlay(a,w,h):
    e=a['evidence']; M=inv(a['frame']); out=[]; W,Hh=a['frame']['width'],a['frame']['height']
    for d in e.get('detected_rows',[]):
        if d['votes']<=0: continue
        c=d['curves']
        if d['side']=='main': out.append(poly(M,c['ascender'],'asc')); out.append(poly(M,c['base'],'base'))
        else: out.append(poly(M,c['base'],'nbase'))
    for L in e['lines']:
        if L['side']=='main': continue
        for g in L['word_groups']: out.append(rect(M,g['bbox'],'wwhole' if g['whole'] else 'wpart'))
    m=e['gate']['main_cut']
    for s in m['cut_spans']:
        y=0.5 if s['edge']=='top' else Hh-0.5
        out.append(poly(M,[[s['x0'],y],[s['x1'],y]],'cutspan' if s['min_visible']<.6 else 'cutspan2'))
    for c in m['crossings']:
        if 'leaves' in c.get('meaning',''):
            y=0.5 if c['edge']=='top' else Hh-0.5; x,yy=pt(M,c['x'],y)
            out.append(f'<circle class="cross" cx="{x:.1f}" cy="{yy:.1f}" r="5"/>')
    bx=e.get('box_evidence') or {}
    if bx.get('bbox'): out.append(rect(M,bx['bbox'],'tbox'))
    if bx.get('row_frame'): out.append(poly(M,bx['row_frame']['corners'],'rframe',close=True))
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">'+''.join(out)+'</svg>'
def inventory(e):
    bits=[]
    for L in e['lines']:
        tag='complete' if L['complete'] else f"{int(round(L['visible']*100))}% visible"
        if L['side']=='main': bits.append(f"MAIN: {L['bodies']} letters, {tag}, covers {int(round(L['coverage']*100))}%")
        else: bits.append(f"{L['side'].upper()}: {tag}, {L['bodies']} letter bodies, {L['whole_words']} whole / {L['cutoff_words']} cut-off words")
    return ' | '.join(bits) if bits else 'no rows detected'
def cutinfo(m):
    bits=['diagnostics only (no verdict): '+(f"skew {m['angle_deg']:+.1f}°" if m.get('angle_deg') is not None else 'no main row')]
    if m['baseline_exit']: bits.append('baseline LEAVES the crop at x='+', '.join(str(int(c['x'])) for c in m['crossings'] if 'leaves' in c.get('meaning','')))
    if m['low_visibility_span']: bits.append('letter bodies <60% visible over '+', '.join(f"{s['x0']}–{s['x1']} ({s['edge']}, {int(s['min_visible']*100)}%)" for s in m['cut_spans'] if s['min_visible']<.6))
    if m['cut_letters']: bits.append(f"{len(m['cut_letters'])} letters touch an edge")
    return ' | '.join(bits)
cards=[]; svgs={}; sizes={}; n=collections.Counter()
for r in rows:
    a=r['after']; e=a['evidence']; g=e['gate']; m=g['main_cut']; lid=r['line_id']; st=r['owner_standard_state']
    v,reason=noguard(r)
    maxvis=max([L['visible'] for L in e['lines'] if L['side']!='main'] or [0.0])
    faults=list(r['owner_faults']); nwnote=''
    if 'neighbour_whole_word' in faults and maxvis<0.9:
        faults.remove('neighbour_whole_word'); nwnote=f" (reader saw readable neighbour words, but the other rows are at most {int(maxvis*100)}% visible → cut-off words, not whole, under your 100% rule)"
        if not faults and st=='faulty': st='fine'
    r['owner_faults']=faults; r['owner_standard_state']=st
    grp='un' if st=='unresolved' else ('unc' if v=='UNCERTAIN' else ('fp' if v=='DROP' and st=='fine' else 'tp' if v=='DROP' else 'fn' if st=='faulty' else 'ok'))
    n[grp]+=1
    if grp=='ok' and n['ok']>12: continue
    crop=f"{S}/{owner[lid]['crop']}"
    with Image.open(crop) as im: w,h=im.size
    ans=owner[lid]['reader_answer']
    bx=e.get('box_evidence') or {}; rf=bx.get('row_frame') or {}; p=bx.get('prediction') or {}
    pad=(e.get('padding_evidence') or {}).get('total_padding_line_heights')
    length=('not measured (gate failed)' if g['verdict']!='PASS' else
            (f"OCR chars {e['characters']} vs expected {p['expected']:.1f} → ratio {(e['characters']+1)/(p['expected']+1):.2f} (0.5–1.5) | padding {pad:.2f} de-skewed heights (max 1.5) | de-skewed box {rf.get('length',0):.0f}×{rf.get('height',0):.1f} px, upright height {bx['bbox'][3]-bx['bbox'][1]}" if p.get('expected') is not None else 'length unavailable'))
    rows_=[{'name':'Google','text':owner[lid]['google_text']},
      {'name':'Lines found','text':inventory(e)},
      {'name':'Main line cut?','text':cutinfo(m)},
      {'name':'Gate','text':f"{g['verdict']}: {g['reason']} (whole neighbour words {g['whole_words']}, cut-off {g['cutoff_words']}, complete other rows {len(g['complete_rows'])})"},
      {'name':'Length','text':length},
      {'name':'0.7 → 0.8','text':f"0.7 {r['verdict_07']} → 0.8 {v}: {reason}"},
      {'name':'Text vs crop','text':'crop_ok '+ans.get('crop_ok','?')+' | errors: '+(', '.join(ans.get('errors',[])) or 'none')+(' | '+ans['detail'] if ans.get('detail') else '')},
      {'name':'Owner standard','text':('FAULT: '+', '.join(r['owner_faults']) if r['owner_faults'] else ('unresolved' if st=='unresolved' else 'fine'))+nwnote+(' — '+ans['segmentation_detail'] if ans.get('segmentation_detail') else '')}]
    cards.append({'line_id':lid,'label':lid,'image':crop,'group':grp,'rows':rows_,
      'tags':[{'text':lid.split('--')[0].split('-p0')[0]},{'text':v,'class':'ok' if v=='KEEP' else 'bad' if v=='DROP' else 'warn'},{'text':f"{w}×{h} px"}],
      'doc_id':f'{PREFIX}:{lid}','note_data':{'line':lid,'id':f'{PREFIX}:{lid}'},'data':{'tool':v}})
    svgs[lid]=overlay(a,w,h); sizes[lid]=(w,h)
groups=[('fp',f"DROPPED but fine under your standard = false rejects ({n['fp']})"),('fn',f"KEPT but faulty = misses ({n['fn']})"),('unc',f"UNCERTAIN = pipeline HOLD ({n['unc']})"),('tp',f"DROPPED and faulty = correct drops ({n['tp']})"),('un',f"reader unresolved ({n['un']})"),('ok',f"KEPT and fine (12 of {n['ok']} shown)")]
intro=('Segmentation 0.8 (Sol, SEG-GATE-2, commit 410f4566): exactly your three rules, in this order, crop only: (1) other lines — more than two whole words from other rows, or a second complete line, is DROP; cut-off words do not count; (2) the de-skewed main-line box, long side normalised by its own height, against the Google output (0.5–1.5); (3) crop height at most the upright box height + 1.5 × the de-skewed line height. Nothing else decides. Cut measurements are shown as diagnostics only.\n'
 'Scores on the 150 under your standard: false rejects 0.5 = 26, 0.6 = 21, 0.7 = 59, 0.8 = 18; misses 8 / 11 / 8 / 14; HOLD 0 / 5 / 11 / 11. Agreement with your 135 rated calibration lines: 98 / 97 / 65 / 94.\n'
 'Overlay: GREEN = detected main row (ascender, base); ORANGE dashed = other rows; RED box = whole neighbour word, GREY dashed = cut-off word; ORANGE bar on the edge = letter bodies <60% visible there (diagnostic); RED dot = baseline leaving the crop (diagnostic); BLUE = upright text box; MAGENTA = de-skewed box. Press b to hide boxes, z to zoom, hover for the lens.\n'
 'Frames: the OUTER border is your mark (green KEEP, red DROP); the INNER frame is the latest tool verdict (0.8): green KEEP, red DROP, amber UNCERTAIN. Keys: ↑ ↓ move, SPACE toggles KEEP / DROP, Esc leaves the note box. Marks and notes autosave.')
spec={'title':'Segmentation 0.8 — your three rules on the 150 unseen lines','intro':intro,'groups':[{'id':g,'heading':h} for g,h in groups]}
html=render(cards,spec)
parts=html.split('<div class="card"')
for i in range(1,len(parts)):
    p=parts[i]; lid=H.unescape(re.search(r'<div class="lid">([^<]+)</div>',p).group(1)); j=p.index('<img '); k=p.index('>',j)+1
    w,h=sizes[lid]; scale=min(3.0,940/w,300/h); dw=int(w*scale)
    parts[i]=p[:j]+f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}">'+p[j:k]+svgs[lid]+'</div><div class="lens" hidden></div></div>'+p[k:]
html='<div class="card"'.join(parts)
css=open(os.path.join(HERE,'segeval_sheet.css')).read()+"\n.ov .cutspan{stroke:#f08c00;stroke-width:6}.ov .cutspan2{stroke:#f08c00;stroke-width:2;opacity:.6}.ov .cross{fill:#d61f1f;stroke:#fff;stroke-width:1.5}\n"
html=html.replace('</style></head>',css+'</style></head>',1)
js=open(os.path.join(HERE,'segeval_sheet.js')).read(); i=html.rindex('<script>'); j=html.rindex('</script>'); html=html[:i]+'<script>'+js+html[j:]
html=toolpills(html); open(os.path.join(HERE,OUT),'w').write(html); print('cards',len(cards),dict(n),'bytes',len(html))
