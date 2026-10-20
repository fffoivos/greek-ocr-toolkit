import json,os,glob,collections,sys
sys.path.insert(0,os.path.expanduser('~/Projects/greek-ocr-toolkit-cleanup'))
from greekocr.adjudicate.owner_sheet import render
from PIL import Image
root=os.path.expanduser('~/Projects/collect-v3-data/run/W1')
crops=os.path.join(root,'crops')
d=json.load(open('c1_results.json'))
cards={}; labels={}
for f in glob.glob(os.path.join(root,'c1','*','cards.jsonl')):
    st=os.path.basename(os.path.dirname(f))
    for l in open(f):
        r=json.loads(l); cards[(st,r.get('card_id'))]=r.get('line_id'); labels[r.get('line_id')]=r.get('label') or r.get('text') or r.get('google') or ''
verd={}
for f in glob.glob('verdicts/*__a.jsonl'):
    st=os.path.basename(f)[:-len('__a.jsonl')]
    for l in open(f):
        r=json.loads(l); verd[(st,r['card_id'])]=r
CLASS={'bsb_poly1850__poly1850':'Polytonic 1850s (BSB)','ia_poly1850__poly1850':'Polytonic 1850s (IA)','nlg__poly1850':'Polytonic 1850s (NLG)','nlg__greek_poly':'Polytonic (NLG greek_poly)','nlg__poly1900':'Polytonic 1900s (NLG)','kosmopolis__poly1900':'Polytonic 1900s (Kosmopolis)','lekythos__poly1900':'Polytonic 1900s (Lekythos)','ia_poly1850__mixed_greek_latin':'Mixed Greek + Latin','ia_poly1850__latin':'Latin','ia_russian__cyrillic':'Cyrillic, Russian pre-1918','serbia__cyrillic':'Cyrillic, Serbian','elstat__numerics_tables':'Numerics and tables (ELSTAT)','gazette_modern__modern_scanned__measured_1986_1990':'Modern monotonic (Gazette 1986–90)','gazette_modern__modern_scanned__probe_1982_1985':'Modern monotonic (Gazette 1982–85)'}
def fault(errors,detail):
    e=set(errors); dt=detail or ''
    if 'crop_overrun' in e or 'merged_two_lines' in e or 'crop_clipped' in e: return None
    if 'р' in dt or 'ъ' in dt or 'ь' in dt: return 'hard sign ъ flattened to ь'
    if 'ϲ' in dt or 'lunate' in dt.lower(): return 'lunate sigma written as σ'
    if 'ϛ' in dt: return 'stigma ligature replaced'
    if any(c in dt for c in '²³¹⁰⁴⁵⁶⁷⁸⁹ⁿ') or 'superscript' in dt.lower(): return 'superscript dropped or garbled'
    if '—' in dt or 'dash' in dt.lower(): return 'em dash dropped or hyphenated'
    if '·' in dt and any(ch.isdigit() for ch in dt) or 'separator' in dt.lower() or 'thousands' in dt.lower() or 'decimal' in dt.lower(): return 'number separator changed'
    if 'lookalike_script_letter' in e: return 'Latin siglum labelled with a Greek lookalike'
    if 'missing_mark' in e and any(c in dt for c in 'ῳῃᾳᾷῇῷᾶ'): return 'iota subscript dropped'
    if 'wrong_mark' in e and any(c in dt for c in 'ὰὲὴὶὸὺὼ'): return 'grave written as acute'
    if 'wrong_mark' in e and any(c in dt for c in 'ᾶῆῖῦῶῦ'): return 'circumflex written as acute'
    if 'missing_mark' in e and any(c in dt for c in 'ἈἘἨἸὈὙὨἉἙἩἹὉὩῬ'): return 'breathing dropped on a capital'
    if 'missing_mark' in e: return 'mark dropped'
    if 'wrong_mark' in e: return 'mark misnamed'
    if 'extra_mark' in e: return 'mark added where none is printed'
    if 'wrong_letter' in e: return 'letter misread'
    if 'missing_word_or_span' in e: return 'span missing from the label'
    if 'punctuation' in e: return 'punctuation changed'
    if 'digits' in e: return 'digits changed'
    return None
# ---------- Sheet A: failure modes per class ----------
by=collections.OrderedDict()
for st,s in d.items():
    cl=CLASS.get(st,st)
    pool=[]
    for key in ('mark_errors','superscript','dash','separator','lunate_sigma'):
        for e in s.get(key,[]) or []:
            if isinstance(e,dict): pool.append((e['card_id'],e.get('line_id') or cards.get((st,e['card_id'])),e.get('errors',[key]),e.get('detail','')))
    for (st2,cid),r in verd.items():
        if st2==st and (r.get('letters')=='n' or r.get('marks')=='n'):
            pool.append((cid,cards.get((st,cid)),r.get('errors',[]),r.get('detail','')))
    seen=set()
    for cid,lid,errs,det in pool:
        if not lid or (cid in seen): continue
        f=fault(errs,det)
        if not f: continue
        seen.add(cid); by.setdefault(cl,collections.OrderedDict()).setdefault(f,[]).append((cid,lid,errs,det,st))
lines=[]; groups=[]; sections=[]
for ci,(cl,faults) in enumerate(by.items()):
    sid=f's{ci}'; sections.append({'id':sid,'heading':cl,'header':''})
    for fi,(f,items) in enumerate(faults.items()):
        gid=f'{sid}g{fi}'; groups.append({'id':gid,'section':sid,'heading':f'{f}  ({len(items)} cards found; showing {min(6,len(items))})'})
        for cid,lid,errs,det,st in items[:6]:
            p=os.path.join(crops,lid+'.png')
            if not os.path.exists(p): continue
            lines.append({'line_id':lid,'label':lid,'image':p,'group':gid,'rows':[{'name':'Google','text':labels.get(lid,'')},{'name':'Checker','text':det or ', '.join(errs)}],'tags':[{'text':cl},{'text':f},{'text':'card '+cid}],'printed':'','doc_id':lid})
specA={'title':'Failure modes per class','intro':'Google label faults seen on the 17 October quality cards, grouped by training class and fault. Each card: the crop as Google cut it, Google\'s label, the checker\'s note. Notes autosave; use Printed for the form you read in the ink.','groups':groups,'sections':sections}
htmlA=render(lines,specA)
open('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/db202b49-34e2-49d2-9fbd-271fe776b56d/scratchpad/sheet_failure_modes.html','w').write(htmlA)
print('A cards',len(lines),'classes',len(sections),'bytes',len(htmlA))
# ---------- Sheet B: segmentation ----------
recs=[]
for st,s in d.items():
    for e in s.get('neighbour_ink',[]): recs.append(dict(st=st,card=e['card_id'],line=e['line_id'],errors=e['errors'],detail=e['detail']))
for (st,cid),r in verd.items():
    if r.get('crop_ok')=='n' and not any(x['st']==st and x['card']==cid for x in recs):
        lid=cards.get((st,cid))
        if lid: recs.append(dict(st=st,card=cid,line=lid,errors=r['errors'],detail=r.get('detail','')))
def typ(r):
    e=set(r['errors']); dt=r['detail']
    if 'merged_two_lines' in e or 'crop holds' in dt or 'full lines' in dt or 'three lines' in dt: return 'merged'
    if 'two table columns' in dt or 'column rule' in dt: return 'column'
    if 'crop_clipped' in e: return 'clipped'
    if 'missing_word_or_span' in e: return 'fragment'
    if 'crop_overrun' in e: return 'overrun'
    return None
for r in recs: r['type']=typ(r)
cnt=collections.Counter(r['type'] for r in recs if r['type'])
sg=os.path.expanduser('~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery')
sgex=[json.loads(l) for l in open(os.path.join(sg,'examples.jsonl'))]
titles=[('merged','Two or more lines in one crop, label covers one'),('fragment','Crop shorter than the printed line'),('overrun','Neighbouring line ink inside the crop'),('column','Crop spans two table columns'),('clipped','Clipped at the edge'),('rotated','Vertical line stored rotated')]
per={'merged':99,'fragment':99,'overrun':12,'column':99,'clipped':99}
linesB=[]; groupsB=[]; used=set()
for t,title in titles:
    gid='g_'+t; n=cnt.get(t,0)
    groupsB.append({'id':gid,'heading':f'{title}  ({n} of 1,400 C1 cards)' if t!='rotated' else title+'  (2.9% of Gazette modern rows, 20% of its headings)'})
    # SG1 examples with strips first
    for e in sgex:
        if e.get('type')!=t: continue
        lid=e['line_id']; strip=os.path.join(sg,f"{e['id']}-strip.png"); crop=os.path.join(sg,f"{e['id']}-crop.png")
        if lid in used or not os.path.exists(crop): continue
        used.add(lid)
        linesB.append({'line_id':lid,'label':lid,'image':crop,'group':gid,'zooms':[{'image':strip,'alt':'page strip, red box = Google crop'}] if os.path.exists(strip) else [],'rows':[{'name':'Google','text':e.get('label_text','')},{'name':'Checker','text':e.get('card_verdict_detail') or e.get('classification_note') or ''}],'tags':[{'text':e.get('source','')},{'text':e.get('class','')},{'text':t},{'text':f"crop height {e.get('crop_height','')} px"}],'doc_id':lid})
    k=0
    for r in sorted([x for x in recs if x['type']==t],key=lambda x:x['st']):
        if k>=per.get(t,0): break
        if r['line'] in used: continue
        p=os.path.join(crops,r['line']+'.png')
        if not os.path.exists(p): continue
        used.add(r['line']); k+=1
        linesB.append({'line_id':r['line'],'label':r['line'],'image':p,'group':gid,'rows':[{'name':'Google','text':labels.get(r['line'],'')},{'name':'Checker','text':r['detail'] or ', '.join(r['errors'])}],'tags':[{'text':CLASS.get(r['st'],r['st'])},{'text':t},{'text':'card '+r['card']}],'doc_id':r['line']})
if not any(l['group']=='g_rotated' for l in linesB):
    rot=[]
    for p in sorted(glob.glob(os.path.join(crops,'gazette_modern--*.png')))[:6000]:
        im=Image.open(p)
        if im.height>im.width and im.height>60: rot.append(p)
        if len(rot)>=4: break
    for p in rot:
        lid=os.path.basename(p)[:-4]
        linesB.append({'line_id':lid,'label':lid,'image':p,'group':'g_rotated','rows':[{'name':'Google','text':labels.get(lid,'')}],'tags':[{'text':'Modern monotonic (Gazette)'},{'text':'rotated'}],'doc_id':lid})
intro=('Crops exactly as Document AI cut them. Measured: neighbouring-line ink on 27–46 of 100 cards on the Gazette, Kosmopolis and Lekythos originals (2–4 after masking); merged lines 8%, 18%, 12% of their candidate rows; rotated verticals 2.9% of Gazette modern rows and 20% of its headings; in E3 2.8% of test lines had a 3+ atom length mismatch and carried 44% of all edits; about 19% of printed rows get no Google box at all (rows with no box: strips pending).')
htmlB=render(linesB,{'title':'Google segmentation failures','intro':intro,'groups':groupsB})
open('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/db202b49-34e2-49d2-9fbd-271fe776b56d/scratchpad/sheet_segmentation.html','w').write(htmlB)
print('B cards',len(linesB),'bytes',len(htmlB), dict(cnt))
