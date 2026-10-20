#!/usr/bin/env python3
"""Report rereads, render private review sheets, and summarize lead-eye decisions."""
import argparse
from common_full import *
from PIL import Image, ImageDraw, ImageFont

def combine(p1,p2key,answers):
    byp1={}
    for iid,m in p2key.items():
        if m['role']=='bed':
            if m['p1_id'] in byp1: raise ValueError('Duplicate reread bed item')
            byp1[m['p1_id']]=(iid,m)
    if set(byp1)!={r['item_id'] for r in p1['flags']}: raise ValueError('Reread coverage differs from flags')
    rows=[]
    for r in p1['flags']:
        iid,m=byp1[r['item_id']]
        rows.append(dict(r,p1=r['answer'],p2=answers[iid]['accent'],p2_id=iid,p2_context=m['context'],
                         agreement=r['answer']==answers[iid]['accent']))
    return rows

def review_sheets(rows,p2key,root=None):
    root = ROOT if root is None else root
    folder=root/'keys/review'; folder.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
    paths=[]
    for start in range(0,len(rows),30):
        part=rows[start:start+30]; height=math.ceil(len(part)/6)*540
        sheet=Image.new('RGB',(1600,height),'white'); d=ImageDraw.Draw(sheet)
        for j,r in enumerate(part):
            x=j%6*266+5; y=j//6*540; m=p2key[r['p2_id']]
            p=next(p for p in public_rows(BED/m['context']) if p['item_id']==r['p2_id'])
            # Bound text with wrapping, so long label tokens cannot cross tiles.
            def text(value,dy,f=font):
                lines=[]; current=''
                for ch in value:
                    if d.textlength(current+ch,font=f)>252: lines.append(current); current=''
                    current+=ch
                lines.append(current)
                for k,line in enumerate(lines): d.text((x,y+dy+k*18),line,font=f,fill='black')
                return len(lines)
            text(r['item_id']+' / '+r['p2_id'],5,small)
            with Image.open(BED/m['context']/p['letter_image']) as im:
                im=im.convert('RGB'); im.thumbnail((252,300),Image.Resampling.NEAREST); sheet.paste(im,(x,y+40))
            with Image.open(BED/m['context']/p['word_image']) as im:
                im=im.convert('RGB'); im.thumbnail((252,100),Image.Resampling.LANCZOS); sheet.paste(im,(x,y+345))
            used=text(r['word_labelled'],450)
            text(f"label={r['label']} p1={r['p1']} p2={r['p2']}",450+18*used,small)
            text(f"touches_punct={str(r['touches_punct']).lower()}",508,small)
        path=folder/f'flags_{start//30+1}.png'; path.write_bytes(g1.encode(sheet)); paths.append(path)
    return paths

def final_metrics(p1,rows,lead):
    if not isinstance(lead,list): raise ValueError('Lead-eye JSON must be a list')
    expected={r['item_id'] for r in rows}; actual={}
    for r in lead:
        if not isinstance(r,dict) or set(r)!={'item_id','printed'}: raise ValueError('Lead fields: item_id, printed only')
        if r['item_id'] in actual: raise ValueError('Duplicate lead item')
        if r['printed'] not in ACCENTS: raise ValueError('Lead printed must be acute/grave/circumflex/none/unreadable')
        actual[r['item_id']]=r['printed']
    if set(actual)!=expected: raise ValueError('Lead-eye coverage differs from flagged items')
    confirmed=sum(actual[r['item_id']]!=r['label'] for r in rows)
    corrected_grave=sum(actual.get(r['item_id'],r['label'])=='grave' for r in p1['bed'])
    errors=[r for r in rows if r['label']=='acute' and actual[r['item_id']]=='grave']
    return dict(items=p1['items'],flagged=len(rows),confirmed=confirmed,false_flags=len(rows)-confirmed,
                pass_agreement=fraction(sum(r['agreement'] for r in rows),len(rows)),
                p2_accuracy=fraction(sum(r['p2']==actual[r['item_id']] for r in rows),len(rows)),
                stratum_grave_base_rate=fraction(corrected_grave,p1['items']),
                label_acute_printed_grave_per_item=fraction(len(errors),p1['items']),
                label_acute_printed_grave_per_card=fraction(len({r['card_id'] for r in errors}),100),
                lead_unreadable=sum(a=='unreadable' for a in actual.values()),
                c1_comparator=fraction(9,100))

def final_md(metrics):
    headers=['items','flagged','confirmed','false flags','pass-agreement p1 vs p2','p2 accuracy against lead','stratum grave base rate','label grave_to_acute per item','label grave_to_acute per card','C1 comparator']
    vals=[metrics[k] for k in ('items','flagged','confirmed','false_flags')]
    for k in ('pass_agreement','p2_accuracy','stratum_grave_base_rate','label_acute_printed_grave_per_item','label_acute_printed_grave_per_card','c1_comparator'):
        vals.append(frac(metrics[k]['count'],metrics[k]['total']))
    return '\n'.join(['# SR-G3 final lead-eye summary','','| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |','| '+' | '.join(map(str,vals))+' |','',
        'The stratum grave base rate uses lead-eye decisions on flagged items and labels on unflagged items; it assumes all unflagged items match the label. Geometry drops and hyphen fragments are outside the item denominator. Card rates use all 100 C1 cards.',
        'grave_to_acute means label acute / printed grave. Confirmed and false flags follow the supplied lead categories literally; unreadable is retained as a distinct printed category, not imputed.',
        f"Lead unreadable: {metrics['lead_unreadable']}. Pass agreement and p2 accuracy cover flagged bed items only; controls are reported in FLAGS.md.",''])

def run(final=None,answer_root=None):
    p1=load(ROOT/'PASS1.json')
    if p1.get('status')!='complete': raise ValueError('Pass 1 is pending')
    if p1['key_sha256']!=sha(ROOT/'keys/key.json'): raise ValueError('Pass-1 key changed; rerun flag_full')
    receipt=load(ROOT/'keys/P2_BUILD_RECEIPT.json')
    if receipt['pass1_sha256']!=sha(ROOT/'PASS1.json') or receipt['key_sha256']!=sha(ROOT/'keys/p2_key.json'):
        raise ValueError('Stale reread build; rebuild from current pass 1')
    key=load(ROOT/'keys/p2_key.json'); answers=read_contexts(key,'p2',answer_root)
    rows=combine(p1,key,answers); controls=control_report(key,answers)
    lines=['# SR-G3 flagged-item rereads','','| Item | P2 id | Label word | Label | P1 | P2 | Agree | touches_punct |','| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        word=r['word_labelled'].replace('|','\\|')
        lines.append(f"| {r['item_id']} | {r['p2_id']} | {word} | {r['label']} | {r['p1']} | {r['p2']} | {r['agreement']} | {r['touches_punct']} |")
    lines += ['', '| P2 control context | Item | G1 source | Expected | P2 | Pass |','| --- | --- | --- | --- | --- | --- |']
    for name,c in controls.items():
        for r in c['items']: lines.append(f"| {name} | {r['item_id']} | {r['g1_id']} | {r['expected']} | {r['answer']} | {r['passed']} |")
        lines += ['',f"{name}: {c['passes']}/{c['total']} control passes; context flagged={c['flagged']}.",'']
    (ROOT/'FLAGS.md').write_text('\n'.join(lines)+'\n')
    review_sheets(rows,key)
    dump(ROOT/'LEAD_EYE.template.json',[dict(item_id=r['item_id'],printed=None) for r in rows])
    dump(ROOT/'keys/CONFIRM_RECEIPT.json',dict(pass1_sha256=sha(ROOT/'PASS1.json'),p2_key_sha256=sha(ROOT/'keys/p2_key.json'),
        answers={str(p):sha(p) for p in sorted((Path(answer_root) if answer_root else SR/'answers/grave_full').glob('p2*.jsonl'))},
        controls=controls,rows=rows))
    if final:
        # Reuse duplicate-field rejection from the SR-G2 JSONL parser for JSON too.
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d: raise ValueError('Duplicate lead JSON field')
                d[k]=v
            return d
        lead=json.loads(Path(final).read_text(),object_pairs_hook=unique)
        metrics=final_metrics(p1,rows,lead)
        (ROOT/'FINAL.md').write_text(final_md(metrics))
        dump(ROOT/'keys/FINAL_RECEIPT.json',dict(metrics=metrics,lead_sha256=sha(final),lead_file=str(Path(final).resolve())))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--final',type=Path); args=p.parse_args()
    try: rows=run(args.final)
    except (OSError,ValueError,KeyError) as e: p.exit(2,f'Invalid/incomplete reread or lead review: {e}\n')
    print(f'Review prepared: {len(rows)} flags')
if __name__=='__main__': main()
