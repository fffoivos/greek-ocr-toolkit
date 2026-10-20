import json,os,sys,re,html as H,collections
from PIL import Image
sys.path.insert(0,os.path.expanduser('~/Projects/greek-ocr-toolkit-cleanup'))
from greekocr.adjudicate.owner_sheet import render
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); from sheet_common import toolpills
S=os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1')
sol=[json.loads(l) for l in open(f'{S}/cells/samples.jsonl')]
opus=[json.loads(l) for l in open(f'{S}/cells_opus/samples.jsonl')]
cards=[]; sizes={}; seen=set(); n=collections.Counter()
def add(lid,crop,group,text,w,h,chars,v05,r05,extra,owner=None):
    if lid in seen or not os.path.exists(crop): return
    seen.add(lid); n[group]+=1
    with Image.open(crop) as im: W,Hh=im.size
    rows=[{'name':'Google','text':text or '(empty)'},
          {'name':'Size','text':f"{w}×{h} px, {chars} chars, width/height {w/h:.2f} → {w/h/max(chars,1):.2f} per char"},
          {'name':'Filter 0.5','text':f"{v05}: {r05 or ''}"},
          {'name':'Seen','text':extra or ''}]
    if owner: rows.append({'name':'Owner rating','text':owner})
    cards.append({'line_id':lid,'label':lid,'image':crop,'group':group,'rows':rows,
      'tags':[{'text':lid.split('--')[0].split('-p0')[0]},{'text':v05,'class':'ok' if v05=='KEEP' else 'bad' if v05=='DROP' else 'warn'}],
      'doc_id':f'cells:{lid}','note_data':{'line':lid,'id':f'cells:{lid}'},'data':{'tool':v05 if v05 in ('KEEP','DROP','UNCERTAIN') else 'UNCERTAIN'}})
    sizes[lid]=(W,Hh)
for r in sol:
    add(r['row_id'],r['crop_path'],'sol_'+r['group'],r['text'],r['width'],r['height'],r['chars'],r['verdict_05'],r.get('reason_05'),'')
for r in opus:
    t=r.get('type'); grp='opus_'+(t or 'numeric')
    add(r['line_id'],r['crop_path'],grp,r['text'],r['width'],r['height'],r['chars'],r.get('verdict_05') or '?',r.get('reason_05'),(r.get('note') or ''),owner=(json.dumps(r['owner'],ensure_ascii=False) if r.get('owner') else None))
order=[('sol_cells','Numeric cells: numeric output and small image (Sol, uniform draw across the corpus, %d)'),('sol_numeric_not_small','Numeric output but NOT small (boundary, %d)'),('sol_small_not_numeric','Small image but NOT numeric (Sol draw, %d)'),('opus_numeric','Numeric cells looked at by the Opus study (%d)')]
types=[t for t,_ in collections.Counter(c['group'] for c in cards if c['group'].startswith('opus_') and c['group']!='opus_numeric').most_common()]
LABEL={'word_or_phrase':'short non-numeric: words or phrases','heading_caps_display':'short non-numeric: headings / display capitals','text_covers_part_of_crop':'short non-numeric: Google returned only part of a full line','punctuation_only':'punctuation only (leaders, ditto marks, rules)','abbreviation_reference_label':'abbreviations, references, labels','noise_non_text':'noise / non-text','handwriting':'handwriting','map_figure_ornament_logo':'map labels, figures, ornaments','cut_fragment':'cut fragments of a longer line','foreign_script_printed':'printed foreign script (CJK)','roman_numeral_lowercase':'lower-case Roman numerals','scan_watermark':'scan watermark','show_through_mirrored':'show-through (mirrored)','multi_line_crop':'multi-line crop'}
groups=[{'id':g,'heading':h%n[g]} for g,h in order if n[g]]+[{'id':t,'heading':LABEL.get(t[5:],t[5:])+f' ({n[t]})'} for t in types]
intro=('What the "numeric output + small image" rule finds across the whole census (592,466 rows): numeric output 54,440; cells (≤200×40 px, ≤10 chars) 39,014, all in W1/W2 (gazette 21,489, elstat 12,626); small non-numeric 21,027.\n'
 'Short crops (≤9 chars) follow their own width/height-vs-characters line: numeric ratio = 0.46·chars + 0.79 (spread 0.63) against 0.39·chars + 2.0 (spread 3.1) for text lines, so the text-line model expects every short numeric crop to be 0.4–1.2 heights wider than it is. Short non-numeric crops follow no line (R² 0.20).\n'
 'Filter 0.5 on cells: KEEP 31,527 / DROP 2,419 / UNCERTAIN 5,068 (3,781 "no supported row"). Crops are byte-exact to the census (reconstructed from cached pages). Types for the short non-numeric crops are the Opus study\'s by-eye labels on a uniform draw of 120, not blind reads.\n'
 'Frames: OUTER border = your mark; INNER frame = the filter verdict these rows have (0.5, the census run): green KEEP, red DROP, amber UNCERTAIN. Keys: ↑ ↓ move, SPACE toggles KEEP / DROP, z zoom, hover for the lens, Esc leaves the note box.')
spec={'title':'Numeric cells and short crops across the corpus','intro':intro,'groups':groups}
html=render(cards,spec)
parts=html.split('<div class="card"')
for i in range(1,len(parts)):
    p=parts[i]; lid=H.unescape(re.search(r'<div class="lid">([^<]+)</div>',p).group(1)); j=p.index('<img '); k=p.index('>',j)+1
    w,h=sizes[lid]; scale=min(3.0,940/w,300/h); dw=int(w*scale)
    parts[i]=p[:j]+f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}">'+p[j:k]+'</div><div class="lens" hidden></div></div>'+p[k:]
html='<div class="card"'.join(parts)
css=open(os.path.join(HERE,'segeval_sheet.css')).read(); html=html.replace('</style></head>',css+'</style></head>',1)
js=open(os.path.join(HERE,'segeval_sheet.js')).read(); i=html.rindex('<script>'); j=html.rindex('</script>'); html=html[:i]+'<script>'+js+html[j:]
html=toolpills(html); open(os.path.join(HERE,'sheet_cells.html'),'w').write(html); print('cards',len(cards),dict(n),'bytes',len(html))
