"""Offline RU1-L shape-comparison sheets. No inference or label changes."""
import json
import random
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ru1_review import Resolver, symbol_crops, document, segments, FONT
from ru1_owner_sheet import google_offset
from ru1_decide import accepted_contexts
from reading.common import ROOT, PACK_ROOT, PROJECTS, SCRATCH, rows, dump, jsonl, sha
from ru1_map_answers import DISPUTED_CONTROL

SEED = '20261017:RU1L:audit'
OUT = SCRATCH/'ru1_review/lead'
INPUTS = {}


def bind(path):
    path = Path(path)
    INPUTS[str(path)] = sha(path)
    return path


class Crops:
    def __init__(self):
        self.resolver = Resolver()

    @lru_cache(maxsize=256)
    def get(self, ctx, iid, offset):
        item, meta = self.resolver.lookup[ctx, iid]
        if not meta['w1_id']:
            result = self.resolver.resolve(ctx, iid, offset)
            bind(result['crop'])
            return result
        row = self.resolver.w1[meta['w1_id']]
        off = google_offset(row['label'], row['text'], offset)
        if off is None:
            raise ValueError(f'Unaligned word: {meta["row_id"]}:{offset}')
        path = bind(PACK_ROOT/ctx/'r1'/item['crop'])
        if sha(path) != meta['source_crop_sha256'] or sha(path) != row['crop_sha256']:
            raise ValueError('crop hash mismatch')
        binding = json.loads(bind(PROJECTS/f'collect-v3-data/run/W1/pages/{row["page_id"]}.json').read_text())
        response = bind(binding['response'])
        if sha(response) != binding['response_sha256']:
            raise ValueError('response hash mismatch')
        doc = document(str(response))
        line = doc['pages'][0]['lines'][row['docai_line_index']]
        text = ''.join(doc['text'][a:b] for a,b in segments(line['layout'])).rstrip('\r\n')
        if text != row['text']:
            raise ValueError('retained text mismatch')
        with Image.open(path) as im:
            image = im.convert('RGB')
        word, final, geo = symbol_crops(image, text, off, doc, line, row['crop_bbox'][:2])
        geo.update(label_offset=offset, google_offset=off)
        return dict(line=image, word=word, final=final, geometry=geo, crop=str(path), crop_sha256=sha(path), book=meta['book'])


def proportional(pool, count, rng):
    groups = defaultdict(list)
    for p in pool:
        groups[p['book']].append(p)
    quotas = {b: len(ps)*count//len(pool) for b,ps in groups.items()}
    order = sorted(groups, key=lambda b: (-(len(groups[b])*count % len(pool)), b))
    for b in order[:count-sum(quotas.values())]:
        quotas[b] += 1
    chosen = []
    for b in sorted(groups):
        chosen.extend(rng.sample(sorted(groups[b], key=lambda p:(p['row_id'],p['offset'])), quotas[b]))
    return sorted(chosen, key=lambda p:(p['book'],p['row_id'],p['offset'])), quotas


def scaled(im, scale):
    return im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)


def render(cells, refs, crops):
    font = ImageFont.truetype(FONT, 23)
    small = ImageFont.truetype(FONT, 18)
    index = []
    for kind in ['review', 'audit']:
        chosen = [c for c in cells if c['set']==kind]
        for start in range(0,len(chosen),10):
            batch = chosen[start:start+10]
            layouts = []
            for c in batch:
                images = crops.get(c['ctx'],c['iid'],c['offset'])
                anchors = [refs[c['book']][sign] for sign in ['ъ','ь']]
                fs = [scaled(crops.get(a['ctx'],a['iid'],a['offset'])['final'],8) for a in anchors]
                final = scaled(images['final'],8)
                word = scaled(images['word'],4)
                line = images['line'].copy()
                width = max(1250, sum(im.width for im in [fs[0],final,fs[1]])+100, word.width+32)
                line.thumbnail((width-32,110))
                fh = max(im.height for im in [fs[0],final,fs[1]])
                height = 175+fh+45+word.height+40+line.height+24
                layouts.append((images,anchors,fs,final,word,line,width,height))
            cw = max(l[-2] for l in layouts)
            heights = [max(l[-1] for l in layouts[i:i+2]) for i in range(0,len(batch),2)]
            sheet = Image.new('RGB',(2*cw,sum(heights)),'white')
            draw = ImageDraw.Draw(sheet)
            filename = f'{kind}_{start//10+1:03}.png'
            y = 0
            for i,(c,l) in enumerate(zip(batch,layouts)):
                images,anchors,fs,final,word,line,_,_ = l
                if i and i%2==0: y += heights[i//2-1]
                x = i%2*cw
                draw.rectangle((x,y,x+cw-1,y+heights[i//2]-1),outline='#777777',width=2)
                draw.text((x+16,y+12),f'Cell {c["cell"]} | {kind} | offset {c["offset"]}',font=font,fill='black')
                draw.text((x+16,y+46),c['row_id'],font=small,fill='black')
                calls = '   '.join(f'{r}: {v["call"]} ({v["context"]})' if v else f'{r}: missing' for r,v in c['reads'].items())
                draw.text((x+16,y+73),calls,font=font,fill='black')
                left = x+16
                for label,im,anchor in [('ъ',fs[0],anchors[0]),('Position',final,None),('ь',fs[1],anchors[1])]:
                    draw.text((left,y+110),label+(' reference' if anchor else ' 8×'),font=font,fill='black')
                    if anchor:
                        status = anchor.get('status') or ('ink-truth control' if anchor['basis']=='ink_truth' else 'agreement reference, not adjudicated')
                        draw.text((left,y+140),status,font=small,fill='black')
                    sheet.paste(im,(left,y+175))
                    # Reserve enough width for the full provenance label.
                    left += max(im.width+30,375 if anchor else im.width+30)
                # The annotation label widths can exceed glyph widths: expand checked below.
                if left > x+cw:
                    raise ValueError('reference labels overflow cell')
                top = y+175+max(im.height for im in [fs[0],final,fs[1]])+15
                draw.text((x+16,top),'Word 4×',font=small,fill='black')
                sheet.paste(word,(x+16,top+30))
                top += 30+word.height+10
                draw.text((x+16,top),'Line crop',font=small,fill='black')
                sheet.paste(line,(x+16,top+27))
                index.append({k:v for k,v in c.items() if k not in {'ctx','iid'}} | dict(sheet=filename,sheet_cell=i+1,cell_box=[x,y,x+cw,y+heights[i//2]],word_scale=4,final_scale=8,geometry=images['geometry'],crop_sha256=images['crop_sha256'],references={s:refs[c['book']][s]['reference_id'] for s in ['ъ','ь']}))
            sheet.save(OUT/filename)
    return index


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    bind(Path(__file__).resolve())
    crops = Crops()
    bind(PROJECTS/'collect-v3-data/run/W1/features.jsonl')
    inventory = json.loads(bind(ROOT/'keys/control_inventory.json').read_text())
    table_path = PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json'
    table = {t['item_id']:t for t in json.loads(bind(table_path).read_text())}
    truths = {}
    for control in inventory:
        truth = {int(m[1]):m[3] for t in table[control['adjudication_id']]['slots'] if (m:=re.fullmatch(r'(\d+):g=([ъь]) ink=(ъ|ь|other|u) prior=.+',t))}
        for n,s in enumerate(control['slots'],1):
            if truth[n] != s['control_truth']: raise ValueError('table/inventory truth mismatch')
            if (control['source_id'],n) != DISPUTED_CONTROL:
                truths[control['source_id'],s['offset']] = s['control_truth']
    positions = {}
    for ctx,reader,stem in accepted_contexts():
        key = json.loads(bind(ROOT/f'keys/{stem}.json').read_text())
        bind(PACK_ROOT/ctx/reader/'items.jsonl')
        for r in rows(bind(ROOT/f'answers/{stem}.mapped.jsonl')):
            m = key['items'][r['item_id']]
            k = (r['source_id'],r['offset'])
            if k not in positions:
                positions[k] = dict(row_id=r['row_id'],source_id=r['source_id'],book=m['book'],offset=r['offset'],kind=r['kind'],google=r['google'],control=r['control'],reads=[])
            p = positions[k]
            p['reads'].append(dict(reader=reader,context=f'{ctx}/{reader}',call=r['call']))
            if reader=='r1':p.update(ctx=ctx,iid=r['item_id'])
    books = sorted({p['book'] for p in positions.values() if not p['control']})
    refs = {b:{} for b in books}
    for bi,b in enumerate(books,1):
        for sign in ['ъ','ь']:
            candidates = [p for k,p in positions.items() if p['book']==b and p['kind']=='final' and k in truths and truths[k]==sign and p['control']]
            def unanimous(p):return len(p['reads'])>=2 and all(r['call']==sign for r in p['reads'])
            candidates.sort(key=lambda p:(not unanimous(p),p['source_id'],p['offset']))
            basis = 'ink_truth'
            if not candidates:
                basis = 'agreement'
                candidates = sorted([p for p in positions.values() if p['book']==b and not p['control'] and p['kind']=='final' and unanimous(p) and (sign=='ь' or p['google']=='ъ')],key=lambda p:(p['source_id'],p['offset']))
            if not candidates: raise ValueError(f'No reference for {b} {sign}')
            # Geometry refusal is never bypassed; try the next eligible reference.
            for p in candidates:
                try: im = crops.get(p['ctx'],p['iid'],p['offset'])
                except ValueError: continue
                break
            else: raise ValueError(f'No aligned reference: {b} {sign}')
            rid = f'book{bi:02}_{"hard" if sign=="ъ" else "soft"}'
            dest = OUT/'references'/f'{rid}.png';dest.parent.mkdir(exist_ok=True)
            scaled(im['final'],8).save(dest)
            refs[b][sign] = dict(reference_id=rid,book=b,sign=sign,basis=basis,status='ink-truth control' if basis=='ink_truth' else 'agreement reference, not adjudicated',source_id=p['source_id'],row_id=p['row_id'],offset=p['offset'],ctx=p['ctx'],iid=p['iid'],reads=p['reads'],all_readers_correct=unanimous(p) if basis=='ink_truth' else None,path=str(dest),scale=8,native_size=list(im['final'].size),geometry=im['geometry'],crop_sha256=im['crop_sha256'])
    decisions = rows(bind(ROOT/'decisions.jsonl'))
    for d in decisions:
        p = positions[d['source_id'],d['offset']]
        d.update(book=p['book'],ctx=p['ctx'],iid=p['iid'])
    rng = random.Random(SEED)
    hard,quotas = proportional([d for d in decisions if d['decision']=='edit_hard'],30,rng)
    soft = rng.sample(sorted([d for d in decisions if d['decision']=='keep_soft'],key=lambda d:(d['row_id'],d['offset'])),10)
    review = [d for d in decisions if d['decision']=='lead_review']
    cells = []
    for kind,ds in [('review',review),('audit',hard+sorted(soft,key=lambda d:(d['row_id'],d['offset'])))]:
        for d in ds:
            cells.append(dict(cell=len(cells)+1,row_id=d['row_id'],offset=d['offset'],set=kind,decision=d['decision'],reads=d['reads'],book=d['book'],ctx=d['ctx'],iid=d['iid']))
    index = render(cells,refs,crops)
    dump(OUT/'references.json',refs)
    dump(OUT/'sheets_index.json',dict(cells=len(index),sheets=len({r['sheet'] for r in index}),items=index))
    template = ROOT/'lead_review_template.jsonl'
    jsonl(template,[{k:c[k] for k in ['cell','row_id','offset','set']} | dict(lead=None,note='') for c in cells])
    # Only requested check: index, answer rows and rendered cell counts agree.
    indexed = json.loads((OUT/'sheets_index.json').read_text())['items']
    answers = rows(template)
    assert len(indexed)==len(answers)==67 and len(review)==27 and len(hard)==30 and len(soft)==10
    assert [{k:r[k] for k in ['cell','row_id','offset','set']} for r in indexed] == [{k:r[k] for k in ['cell','row_id','offset','set']} for r in answers]
    assert len({r['cell'] for r in indexed})==67
    assert all(n<=10 for n in Counter(r['sheet'] for r in indexed).values())
    assert all(sha(p)==h for p,h in INPUTS.items()), 'input drift'
    agreement_books = sum(all(r['basis']=='agreement' for r in ss.values()) for ss in refs.values())
    mixed_books = sum(len({r['basis'] for r in ss.values()})==2 for ss in refs.values())
    outputs = [*OUT.glob('*.png'),*OUT.glob('*.json'),*OUT.glob('references/*.png'),template]
    receipt = dict(schema='RU1L-receipt-v1',status='READY',date='2026-10-17',python=sys.executable,output=str(OUT),constraints=dict(network_used=False,git_writes=False,reader_run=False,classifications_made=0),references=dict(books=len(refs),agreement_only_books=agreement_books,mixed_basis_books=mixed_books,books_with_any_agreement=agreement_books+mixed_books,agreement_glyphs=sum(r['basis']=='agreement' for ss in refs.values() for r in ss.values()),selection='same-book ink-truth controls; prefer all accepted readers correct; otherwise unanimous bed positions; disputed control excluded',manifest=str(OUT/'references.json')),review=dict(cells=len(review),sheets=3),audit=dict(cells=40,sheets=4,edit_hard=30,keep_soft=10,seed=SEED,hard_book_population=dict(Counter(d['book'] for d in decisions if d['decision']=='edit_hard')),hard_book_quotas=quotas,sampling='Hamilton largest-remainder proportional book quotas (lexical book tie-break); seeded random sample per book, then 10 keep_soft from sorted population using the same RNG'),validation=dict(index_cell_answer_count='passed',cells=67,max_cells_per_sheet=10),inputs=INPUTS,outputs={str(p):sha(p) for p in outputs})
    dump(ROOT/'RU1L_RECEIPT.json',receipt)
    print(f'RU1L READY: references {len(refs)} books (agreement-only {agreement_books}); review cells 27 on 3 sheets; audit cells 40 on 4 sheets')


if __name__=='__main__':build()
