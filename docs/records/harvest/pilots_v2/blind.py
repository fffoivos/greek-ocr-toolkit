import html,json,random
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
from pilotlib import *

if __name__=='__main__':
    allrows=rows(BASE/'bulk/alignment.jsonl');pages={r['id']:r for r in rows(BASE/'pages.jsonl')} if (BASE/'pages.jsonl').exists() else {json.loads(p.read_text())['id']:json.loads(p.read_text()) for p in (BASE/'receipts/pages').glob('*.json')}
    summaries=[]
    for pilot in ['wikisource','gutenberg','perseus']:
        rs=[r for r in allrows if r['pilot']==pilot];rng=random.Random(20261016+sum(map(ord,pilot)));selected=[]
        for accepted in [True,False]:
            pool=[r for r in rs if r['accepted']==accepted and (r['accepted_for_target_reference'] if accepted else r['human_mixed_line'] or r['human_script_class'].startswith('greek') or r['mixed_line'])];rng.shuffle(pool)
            if len(pool)<20:pool += [r for r in rs if r['accepted']==accepted and r not in pool][:20-len(pool)]
            # Include Greek-bearing and mixed candidates before Latin-only fill.
            pool.sort(key=lambda r:(not (r['mixed_line'] or r['script_class'].startswith('greek')),r['similarity'] is None))
            borderline=sorted(pool,key=lambda r:(r['similarity'] is None,abs((r['similarity'] or 0)-.92)))[:10]
            used={r['id'] for r in borderline};fill=[r for r in pool if r['id'] not in used]
            selected.extend(borderline+fill[:10])
        rng.shuffle(selected);cards=[];key=[];dest=BASE/'blind_sheets'/pilot;dest.mkdir(parents=True,exist_ok=True)
        for i,r in enumerate(selected,1):
            page=pages[r['page_id']];b=r['bbox'];height=b[3]-b[1]
            with Image.open(BASE/page['image']) as im:
                region=(max(0,int(b[0])-20),max(0,int(b[1]-1.5*height)),min(im.width,int(b[2])+20),min(im.height,int(b[3]+1.5*height)))
                context=dest/f'{i:02d}-context.png';im.crop(region).save(context)
            label=r['candidate_text'] or r['google_text'];crop=BASE/r['crop_path'];relative_crop='../../'+r['crop_path']
            cards.append(f'<article><h2>Card {i:02d}</h2><a href="{html.escape(relative_crop)}" target="_blank"><img class="line" src="{html.escape(relative_crop)}" alt="Native line crop for card {i}"></a><p class="label" lang="el">{html.escape(label)}</p><details><summary>Page context</summary><img src="{i:02d}-context.png" alt="Page context"></details><fieldset><legend>Does the string exactly own the visible line, without missing or borrowed text?</legend>'+''.join(f'<label><input type="radio" name="c{i}" value="{v}"> {v}</label>' for v in ['yes','no','uncertain'])+'</fieldset></article>')
            key.append(dict(card=i,line_id=r['id'],accepted=r['accepted'],reasons=r['reasons'],label_origin='proofread span candidate' if r['candidate_text'] else 'Google string control; no human span assigned',label=label,page_id=r['page_id'],source_span_nfd=r['source_span_nfd'],mixed_line=r['mixed_line'],crop_sha256=r['crop_sha256']))
        document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>P1 blind pixel adjudication</title><style>body{font:18px/1.5 Arial,sans-serif;background:#eef2f5;color:#172536;margin:0}main{max-width:1160px;margin:auto;padding:24px}h1{font-size:30px}article{background:white;border-radius:12px;padding:22px;margin:24px 0;box-shadow:0 2px 8px #cbd5dd}.line{display:block;max-width:100%;height:auto}img{max-width:100%;height:auto}.label{font:23px/1.6 Georgia,serif;overflow-wrap:anywhere;padding:12px;background:#f5f7f9}fieldset{border:1px solid #c7d2db;margin-top:18px}label{display:inline-block;padding:8px 22px 8px 0}button{padding:12px 20px;font:inherit}summary{cursor:pointer}h2{font-size:19px}a{color:#145da0}</style><main><h1>P1 — blind pixel adjudication</h1><p>40 shuffled lines. Accepted/rejected status, source type and reader identity are hidden. Judge literal letters, marks, punctuation, hyphens and crop ownership. Use “uncertain” for illegible or ambiguous ink. Context and native pixels are available on every card. No judgment releases a dataset automatically.</p>'''+''.join(cards)+'''<button onclick="downloadAnswers()">Download judgments</button><script>function downloadAnswers(){let a=[...document.querySelectorAll('article')].map((e,i)=>({card:i+1,answer:e.querySelector('input:checked')?.value||null}));let u=URL.createObjectURL(new Blob([JSON.stringify(a,null,2)],{type:'application/json'}));let t=document.createElement('a');t.href=u;t.download='P1-blind-judgments.json';t.click();URL.revokeObjectURL(u)}</script></main></html>'''
        sheet=dest/'sheet.html';sheet.write_text(document)
        static=[];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',26)
        small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
        for part in range(2):
            rendered=[]
            for card,r in zip(key[part*20:(part+1)*20],selected[part*20:(part+1)*20]):
                text=card['label'];words=text.split();wrapped=[];current=''
                for word in words:
                    candidate=(current+' '+word).strip()
                    if font.getlength(candidate)>1500 and current:wrapped.append(current);current=word
                    else:current=candidate
                if current:wrapped.append(current)
                with Image.open(BASE/r['crop_path']) as im:
                    im=im.convert('RGB');im.thumbnail((1500,180),Image.Resampling.LANCZOS)
                height=80+im.height+len(wrapped)*38+66;tile=Image.new('RGB',(1600,height),'white');draw=ImageDraw.Draw(tile)
                draw.text((30,14),f'Card {card["card"]:02d}',font=small,fill='#172536');tile.paste(im,(30,55));y=65+im.height
                for line in wrapped:draw.text((30,y),line,font=font,fill='#172536');y+=38
                draw.text((30,y+10),'Judgment:  yes [ ]    no [ ]    uncertain [ ]',font=small,fill='#34485a');rendered.append(tile)
            out=Image.new('RGB',(1600,sum(im.height for im in rendered)+12*(len(rendered)-1)+70),'#dce4eb');draw=ImageDraw.Draw(out);draw.text((30,20),f'P1 blind pixel sheet / cards {part*20+1:02d}–{part*20+len(rendered):02d}',font=small,fill='#172536');y=70
            for tile in rendered:out.paste(tile,(0,y));y+=tile.height+12
            target=dest/f'cards-{part*20+1:02d}-{part*20+len(rendered):02d}.jpg';out.save(target,quality=94);static.append(str(target.relative_to(BASE)))
        write(BASE/'receipts/blind-keys'/(pilot+'.json'),dict(pilot=pilot,seed=20261016+sum(map(ord,pilot)),cards=key,status='coordinator adjudication pending; this is the unblinding key'))
        summary=dict(pilot=pilot,cards=len(selected),accepted=sum(r['accepted'] for r in selected),rejected=sum(not r['accepted'] for r in selected),mixed=sum(r['mixed_line'] for r in selected),path=str(sheet.relative_to(BASE)),sha256=sha(sheet),static_sheets=static,disposition_hidden=True,judgments_received=0)
        write(BASE/'receipts/blind-sheets'/(pilot+'.json'),summary);summaries.append(summary)
    print(json.dumps(summaries,ensure_ascii=False))
