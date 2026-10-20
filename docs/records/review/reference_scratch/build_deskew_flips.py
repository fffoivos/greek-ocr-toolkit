import json,os,sys,re,html as H
from PIL import Image
sys.path.insert(0,os.path.expanduser('~/Projects/greek-ocr-toolkit-cleanup'))
from greekocr.adjudicate.owner_sheet import render
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); from sheet_common import toolpills
R=os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-recut'); D=f'{R}/docs/harvest/collect_v3_admission/segeval1/deskew'
SITE=os.path.expanduser('~/Projects/ocr-review-sites-20261018')
owner={json.loads(l)['line_id']:json.loads(l) for l in open(f'{R}/docs/harvest/collect_v3_admission/segeval1/scored/owner_rows.jsonl')}
G1=f'{R}/docs/harvest/collect_v3_admission/segeval1/gate'; G2=f'{R}/docs/harvest/collect_v3_admission/segeval1/gate2'
v7={}; v8={}
for fn in ('replay_segeval1.jsonl','replay_calibration.jsonl'):
    for l in open(f'{G1}/{fn}'):
        x=json.loads(l); v7[x['line_id']]=(x['after']['verdict'],x['after']['reason'])
    for l in open(f'{G2}/{fn}'):
        x=json.loads(l); e=x['after']['evidence']; p=(e.get('box_evidence') or {}).get('prediction') or {}; pad=(e.get('padding_evidence') or {}).get('total_padding_line_heights')
        num=(f" | ratio {(e['characters']+1)/(p['expected']+1):.2f} | padding {pad:.2f}" if p.get('expected') is not None and pad is not None else '')
        v8[x['line_id']]=(x['after']['verdict'],x['after']['reason']+num)
def inv(frame):
    (a,b,c),(d,e,f),_=frame['source_to_measurement']; det=a*e-b*d
    return [[e/det,-b/det,(b*f-c*e)/det],[-d/det,a/det,(c*d-a*f)/det]]
def pt(M,x,y): return M[0][0]*x+M[0][1]*y+M[0][2], M[1][0]*x+M[1][1]*y+M[1][2]
def rect(M,b,cls):
    xs,ys=zip(pt(M,b[0],b[1]),pt(M,b[2],b[3])); x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    return f'<rect class="{cls}" x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}"/>'
def poly(M,pts,cls,close=False):
    tag='polygon' if close else 'polyline'
    return f'<{tag} class="{cls}" points="'+' '.join('%.1f,%.1f'%pt(M,x,y) for x,y in pts)+'"/>'
def overlay(after,w,h):
    e=after['evidence']; M=inv(after['frame']); out=[]
    for d in e.get('detected_rows',[]):
        if d['votes']<=0: continue
        c=d['curves']
        if d['side']=='main': out.append(poly(M,c['ascender'],'asc')); out.append(poly(M,c['base'],'base'))
        else: out.append(poly(M,c['base'],'nbase'))
    for g in (e.get('neighbour_evidence') or {}).get('group_bindings',[]):
        if g['side']!='main' and g.get('positive'): out.append(rect(M,g['bbox'],'wwhole'))
    bx=e['box_evidence']; 
    if bx.get('bbox'): out.append(rect(M,bx['bbox'],'tbox'))
    rf=bx.get('row_frame')
    if rf: out.append(poly(M,rf['corners'],'rframe',close=True))
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">'+''.join(out)+'</svg>'
cards=[]; svgs={}; sizes={}
def add(rec,group,crop,judge_name,judge):
    a=rec['after']; e=a['evidence']; bx=e['box_evidence']; rf=bx.get('row_frame') or {}
    with Image.open(crop) as im: w,h=im.size
    lid=rec['line_id']; up_h=bx['bbox'][3]-bx['bbox'][1] if bx.get('bbox') else None
    bev=rec['before'].get('evidence',rec['before'])
    pad_b=(bev.get('padding_evidence') or {}).get('total_padding_line_heights'); pad_a=(e.get('padding_evidence') or {}).get('total_padding_line_heights')
    f=lambda v:'n/a' if v is None else f'{v:.2f}'
    t7=v7.get(lid,('?','not replayed')); t8=v8.get(lid,('?','not replayed')); tool=t8[0] if t8[0] in ('KEEP','DROP','UNCERTAIN') else rec['verdict_after']
    rows=[{'name':'Google','text':owner.get(lid,{}).get('google_text') or rec.get('google_text','') or ''},
      {'name':'0.7','text':f"{t7[0]}: {t7[1]}"},
      {'name':'0.8 (latest)','text':f"{t8[0]}: {t8[1]} | skew {rec['theta_deg']:+.2f}° | box height upright {up_h} → de-skewed {rf.get('height',float('nan')):.1f} px, length {rf.get('length',float('nan')):.0f} px"},
      {'name':judge_name,'text':judge}]
    chg=f"0.6 {rec['verdict_after']} → 0.8 {tool}"
    cards.append({'line_id':lid,'label':lid,'image':crop,'group':group,'rows':rows,
      'tags':[{'text':lid.split('--')[0].split('-p0')[0]},{'text':chg,'class':'ok' if tool=='KEEP' else 'bad' if tool=='DROP' else 'warn'},{'text':f"{abs(rec['theta_deg']):.1f}° skew"}],
      'doc_id':f'deskew:{lid}','note_data':{'line':lid,'id':f'deskew:{lid}'},'data':{'tool':tool}})
    svgs[lid]=overlay(a,w,h); sizes[lid]=(w,h)
TXT={'extra_text','missing_word_or_span','crop_clipped','merged_two_lines'}
n150=0
for l in open(f'{D}/replay_segeval1.jsonl'):
    r=json.loads(l)
    if r['verdict_before']==r['verdict_after']: continue
    o=owner[r['line_id']]; a=o['reader_answer']; flags=[k for k in ('multi_line','neighbour_whole_word','rotated','horizontally_missegmented') if a.get(k)=='yes']+sorted(set(a.get('errors',[]))&TXT)
    maxvis=max([d['visible'] for d in r['after']['evidence'].get('detected_rows',[]) if d['side']!='main'] or [0.0])
    if 'neighbour_whole_word' in flags and maxvis<0.9: flags.remove('neighbour_whole_word'); a=dict(a, segmentation_detail=(a.get('segmentation_detail','')+f' [other rows ≤{int(maxvis*100)}% visible → cut-off words, not whole, under your 100% rule]'))
    add(r,'s150',f"{R}/docs/harvest/collect_v3_admission/segeval1/{o['crop']}",'Owner standard',('FAULT: '+', '.join(flags)+' → should be DROP' if flags else 'fine → should be KEEP')+(' — '+a.get('segmentation_detail','') if a.get('segmentation_detail') else '')+(' | text vs crop: '+a.get('detail','') if a.get('detail') else '')); n150+=1
import gzip
natives={r['id']:r for r in json.loads(gzip.decompress(open(f'{SITE}/review-data/font-normalized/predicted-rows.json.gz','rb').read()))}
population=json.loads(open(f'{SITE}/review-data/population.json').read()); CH=population['detail_chunk_size']; dcache={}
def gtext(lid,index):
    t=natives.get(lid,{}).get('google_text')
    if t is not None: return t
    chunk=index//CH
    if chunk not in dcache: dcache[chunk]=json.loads(gzip.decompress(open(f'{SITE}/population-data/details/{chunk:05d}.json.gz','rb').read()))
    d=dcache[chunk][index%CH]; assert d[0]==lid; return d[2]
n888=0
for l in open(f'{D}/replay_calibration.jsonl'):
    r=json.loads(l)
    if r['verdict_before']==r['verdict_after']: continue
    crop=f"{SITE}/population-images/{r['after']['binding']['crop_sha256']}.png"
    r['google_text']=gtext(r['line_id'],r['index'])
    add(r,'c888',crop,'Owner rating',(r.get('owner_rating') or 'unrated')); n888+=1
groups=[('s150',f'150 unseen SEGEVAL-1 lines: every verdict change ({n150})'),('c888',f'888 accepted calibration decisions: every verdict change ({n888})')]
intro=('The 27 lines whose verdict changed when the text box was de-skewed (0.5 → 0.6). Each card shows only the last two versions: 0.7 and 0.8 (= exactly your three rules, commit 410f4566). '
 'Frames: the OUTER border is your mark (green KEEP, red DROP); the INNER frame is the latest tool verdict (0.8): green KEEP, red DROP, amber UNCERTAIN.\n'
 'Boxes: BLUE = upright text box; MAGENTA = de-skewed box; GREEN = detected target row; ORANGE dashed = other rows; RED = whole neighbour word. Press b to hide boxes, z to zoom, hover for the lens. Keys: ↑ ↓ move, SPACE toggles KEEP / DROP, Esc leaves the note box.')
spec={'title':'De-skewed text box (segmentation 0.6) — every verdict change','intro':intro,'groups':[{'id':g,'heading':h} for g,h in groups]}
html=render(cards,spec)
parts=html.split('<div class="card"')
for i in range(1,len(parts)):
    p=parts[i]; lid=H.unescape(re.search(r'<div class="lid">([^<]+)</div>',p).group(1)); j=p.index('<img '); k=p.index('>',j)+1
    w,h=sizes[lid]; scale=min(3.0, 940/w, 300/h); dw=int(w*scale)
    parts[i]=p[:j]+f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}">'+p[j:k]+svgs[lid]+'</div><div class="lens" hidden></div></div>'+p[k:]
html='<div class="card"'.join(parts)
css=open(os.path.join(HERE,'segeval_sheet.css')).read() if os.path.exists(os.path.join(HERE,'segeval_sheet.css')) else ''
html=html.replace('</style></head>',css+'</style></head>',1)
js=open(os.path.join(HERE,'segeval_sheet.js')).read(); i=html.rindex('<script>'); j=html.rindex('</script>'); html=html[:i]+'<script>'+js+html[j:]
html=toolpills(html); open(os.path.join(HERE,'sheet_deskew_flips.html'),'w').write(html); print('cards',len(cards),n150,n888,'bytes',len(html))
