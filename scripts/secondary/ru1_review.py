"""Offline lead sheets from saved crops and retained Google symbol geometry.
No reading calls. The review command must only be run after r2; tests use fixtures.
"""
import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, PACK_ROOT, SCRATCH, PROJECTS, rows, dump, sha

RUN=PROJECTS/'collect-v3-data/run/W1'
REVIEW=SCRATCH/'ru1_review'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'


@lru_cache(maxsize=16)
def document(path):
    d=json.loads(Path(path).read_text());return d.get('document',d)


def segments(layout):
    return [(int(s.get('startIndex',0)),int(s['endIndex'])) for s in layout['textAnchor']['textSegments']]


def bbox(layout, size):
    p=layout['boundingPoly'];vs=p.get('vertices')
    if vs:
        xs=[v.get('x',0) for v in vs];ys=[v.get('y',0) for v in vs]
    else:
        vs=p['normalizedVertices'];xs=[v.get('x',0)*size[0] for v in vs];ys=[v.get('y',0)*size[1] for v in vs]
    return [min(xs),min(ys),max(xs),max(ys)]


def unmask(item, meta):
    text=item['masked_text']
    for n,s in enumerate(meta['slots'],1):text=text.replace(f'⟦{n}⟧',s['google'])
    return text


def symbol_crops(image, text, offset, doc, line, origin):
    """Exact text-anchor alignment; refuse offset guesses or normalized text."""
    spans=segments(line['layout'])
    indices=[i for a,b in spans for i in range(a,b)]
    raw=''.join(doc['text'][a:b] for a,b in spans)
    # DocAI's final line break is not part of the current label.
    if raw.rstrip('\r\n')!=text:raise ValueError('current label differs from retained Google line; manual geometry required')
    if not 0<=offset<len(text):raise ValueError('invalid offset')
    start=offset
    while start>0 and text[start-1].isalpha():start-=1
    target=indices[offset];word_indices=set(indices[start:offset+1])
    page=doc['pages'][0];size=(page['dimension']['width'],page['dimension']['height'])
    final=[];word=[]
    for s in page['symbols']:
        covered={i for a,b in segments(s['layout']) for i in range(a,b)}
        if target in covered:final.append(bbox(s['layout'],size))
        if covered&word_indices:word.append(bbox(s['layout'],size))
    if len(final)!=1 or not word:raise ValueError('missing/ambiguous symbol box')
    def crop(boxes):
        b=[min(b[0] for b in boxes)-origin[0]-2,min(b[1] for b in boxes)-origin[1]-2,
           max(b[2] for b in boxes)-origin[0]+2,max(b[3] for b in boxes)-origin[1]+2]
        b=[max(0,math.floor(b[0])),max(0,math.floor(b[1])),min(image.width,math.ceil(b[2])),min(image.height,math.ceil(b[3]))]
        if b[2]<=b[0] or b[3]<=b[1]:raise ValueError('symbol outside saved crop')
        return image.crop(b),b
    w,wb=crop(word);f,fb=crop(final)
    return w,f,dict(method='Google symbol text anchors',word_box=wb,final_box=fb,offset=offset)


class Resolver:
    def __init__(self):
        self.w1={r['id']:r for r in rows(RUN/'features.jsonl') if r['source']=='ia_russian'}
        self.legacy=None
        self.old_rows=None
        self.lookup={}
        for path in sorted((ROOT/'keys').glob('ctx[0-9][0-9].json')):
            ctx=path.stem;k=json.loads(path.read_text());items={i['item_id']:i for i in rows(PACK_ROOT/ctx/'r1/items.jsonl')}
            for iid,m in k['items'].items():self.lookup[(ctx,iid)]=(items[iid],m)

    def resolve(self, ctx, iid, offset):
        item,m=self.lookup[(ctx,iid)];path=PACK_ROOT/ctx/'r1'/item['crop']
        if sha(path)!=m['source_crop_sha256']:raise ValueError('crop hash mismatch')
        with Image.open(path) as im:image=im.convert('RGB')
        text=unmask(item,m)
        if m['w1_id']:
            r=self.w1[m['w1_id']]
            if r['label']!=text:raise ValueError('pack/current label mismatch')
            binding=json.loads((RUN/f"pages/{r['page_id']}.json").read_text())
            if sha(binding['response'])!=binding['response_sha256']:raise ValueError('response hash mismatch')
            doc=document(binding['response']);line=doc['pages'][0]['lines'][r['docai_line_index']];origin=r['crop_bbox'][:2]
        else:
            if self.legacy is None:
                self.legacy=json.loads((PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/efficiency/keys/input_mapping.json').read_text())['yer']
            old=self.legacy[m['adjudication_id']];doc=document(old['response'])
            hits=[l for l in doc['pages'][0]['lines'] if ''.join(doc['text'][a:b] for a,b in segments(l['layout'])).rstrip('\r\n')==text]
            if len(hits)!=1:raise ValueError('v2 masked-offset line not unique')
            line=hits[0];b=bbox(line['layout'],old['native_size'])
            if self.old_rows is None:
                self.old_rows={r['id']:r for r in rows(PROJECTS/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/features.jsonl')}
            saved=self.old_rows[m['source_id']]
            cb=saved['crop_bbox']
            if image.size!=(cb[2]-cb[0],cb[3]-cb[1]):raise ValueError('v2 saved crop frame differs')
            origin=cb[:2]
        word,final,geo=symbol_crops(image,text,offset,doc,line,origin)
        return dict(line=image,word=word,final=final,geometry=geo,crop=str(path),crop_sha256=sha(path),source_id=m['source_id'],book=m['book'])


def render_sheets(cells, output, prefix='review', max_cells=12):
    if not 1<=max_cells<=12:raise ValueError('at most 12 cells per sheet')
    output=Path(output);output.mkdir(parents=True,exist_ok=True);index=[]
    font=ImageFont.truetype(FONT,20);small=ImageFont.truetype(FONT,16)
    for page in range(0,len(cells),max_cells):
        batch=cells[page:page+max_cells];layouts=[]
        for c in batch:
            # Native 4x/8x crops retain their exact pixel sizes; expand cells to fit.
            w=c['word'].resize((c['word'].width*4,c['word'].height*4),Image.Resampling.NEAREST)
            f=c['final'].resize((c['final'].width*8,c['final'].height*8),Image.Resampling.NEAREST)
            width=max(1200,w.width+f.width+80)
            line=c['line'].copy();line.thumbnail((width-40,170))
            height=125+line.height+max(w.height,f.height)+60
            layouts.append((width,height,line,w,f))
        cw=max(l[0] for l in layouts);heights=[max(l[1] for l in layouts[i:i+2]) for i in range(0,len(batch),2)]
        sheet=Image.new('RGB',(2*cw,sum(heights)), 'white');draw=ImageDraw.Draw(sheet)
        y=0
        for i,(c,(width,height,line,w,f)) in enumerate(zip(batch,layouts)):
            if i and i%2==0:y+=heights[i//2-1]
            x=(i%2)*cw
            draw.rectangle((x,y,x+cw-1,y+heights[i//2]-1),outline='#777777',width=2)
            labels=[c['title'],c['source_id'],c['annotation']]
            for j,label in enumerate(labels):draw.text((x+16,y+12+j*27),label,font=font if j!=1 else small,fill='black')
            sheet.paste(line,(x+16,y+100));top=y+115+line.height
            draw.text((x+16,top),'word 4×',font=small,fill='black');draw.text((x+40+w.width,top),'final 8×',font=small,fill='black')
            sheet.paste(w,(x+16,top+25));sheet.paste(f,(x+40+w.width,top+25))
        filename=f'{prefix}.png' if len(cells)<=max_cells else f'{prefix}_{page//max_cells+1:03}.png'
        path=output/filename;sheet.save(path)
        for i,c in enumerate(batch):
            index.append(dict(sheet=filename,cell=i+1,word_native_size=list(c['word'].size),final_native_size=list(c['final'].size),word_scale=4,final_scale=8,**{k:v for k,v in c.items() if k not in {'line','word','final'}}))
    dump(output/'sheets_index.json',dict(cells=len(cells),sheets=len({r['sheet'] for r in index}),items=index))
    return index


def failed_controls():
    resolver=Resolver();failed=[];passed=[]
    for n in range(1,5):
        ctx=f'ctx{n:02}'
        for r in rows(ROOT/f'answers/{ctx}.mapped.jsonl'):
            if not r['control']:continue
            r=dict(r,ctx=ctx)
            (passed if r['call']==r['control_truth'] else failed).append(r)
    assert len(failed)==5
    books={resolver.lookup[(r['ctx'],r['item_id'])][1]['book'] for r in failed}
    anchors=[];seen=set()
    for truth in ['ъ','ь']:
        candidates=[r for r in passed if r['control_truth']==truth and resolver.lookup[(r['ctx'],r['item_id'])][1]['book'] in books]
        supplements=[r for r in passed if r['control_truth']==truth and resolver.lookup[(r['ctx'],r['item_id'])][1]['book'] not in books and resolver.lookup[(r['ctx'],r['item_id'])][1]['orthography']=='pre1918']
        # Same-book correct reads first. The remaining same-book soft controls failed r1.
        candidates+=supplements
        chosen_books=set();chosen_sources=set()
        while sum(a['control_truth']==truth for a in anchors)<3:
            available=[r for r in candidates if (r['source_id'],r['offset']) not in seen]
            if not available:break
            def rank(r):
                book=resolver.lookup[(r['ctx'],r['item_id'])][1]['book']
                return (book not in books,book in chosen_books,r['source_id'] in chosen_sources)
            r=min(available,key=rank)
            seen.add((r['source_id'],r['offset']));anchors.append(r)
            chosen_books.add(resolver.lookup[(r['ctx'],r['item_id'])][1]['book']);chosen_sources.add(r['source_id'])
        assert sum(a['control_truth']==truth for a in anchors)==3
    cells=[]
    for i,r in enumerate(failed+anchors):
        c=resolver.resolve(r['ctx'],r['item_id'],r['offset'])
        same_book=c['book'] in books
        c.update(title=('FAILED CONTROL' if i<5 else 'ANCHOR (correct r1; '+('same book' if same_book else 'OTHER BOOK')+')')+f" | {r['ctx']} slot {r['slot']}",
            annotation=f"truth: {r['control_truth']}   r1: {r['call']}   offset: {r['offset']}",
            truth=r['control_truth'],r1=r['call'],offset=r['offset'],anchor=i>=5,same_failure_book=same_book)
        cells.append(c)
    return render_sheets(cells,REVIEW,'ru1_failed_controls')


def reviews(decisions,output):
    resolver=Resolver();cells=[]
    for d in decisions:
        if d['decision']!='lead_review':continue
        if any(d['reads'][r] is None for r in ['r1','r2']):raise ValueError('r2 missing: review builder only after r2')
        r=d['reads']['r1'];c=resolver.resolve(r['pack_context'],r['item_id'],d['offset'])
        c.update(title=f"LEAD REVIEW | offset {d['offset']}",annotation=f"r1: {r['call']} ({r['gate_status']})   r2: {d['reads']['r2']['call']} ({d['reads']['r2']['gate_status']})   prior: {d['prior']}",row_id=d['row_id'],offset=d['offset'],reads=d['reads'],prior=d['prior'])
        cells.append(c)
    return render_sheets(cells,output)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--failed-controls',action='store_true');p.add_argument('--decisions',type=Path,default=ROOT/'decisions.jsonl');p.add_argument('--output',type=Path,default=REVIEW/'positions');a=p.parse_args()
    result=failed_controls() if a.failed_controls else reviews(rows(a.decisions),a.output)
    print(json.dumps(dict(cells=len(result),sheets=sorted({r['sheet'] for r in result}))))
