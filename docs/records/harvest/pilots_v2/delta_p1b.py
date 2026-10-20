"""Deterministic blind delta packs, original-card focus plus full-pilot changes."""
import html
import json
import math
import pathlib
import random
import shutil
from collections import Counter
from pilotlib import BASE,rows,sha,write
from rerun_p1b import DEST

STYLE='''body{font:18px/1.5 system-ui,sans-serif;margin:0;background:#edf1f4;color:#182737}main{max-width:1160px;margin:auto;padding:24px}article{background:white;padding:24px;margin:24px 0;border-radius:12px}img{display:block;max-width:100%;height:auto}p.label{font:24px/1.6 Georgia,serif;overflow-wrap:anywhere;background:#f5f7fa;padding:12px}fieldset{border:1px solid #bbc8d3}fieldset label{display:inline-block;padding:8px 24px 8px 0}a{color:#145da0}button{padding:12px;font:inherit}summary{cursor:pointer}nav{display:flex;gap:24px;flex-wrap:wrap}h2{font-size:20px}@media(max-width:600px){main{padding:12px}article{padding:14px}.label{font-size:21px!important}}'''
SCRIPT='''<script>const pack=PACK;for(const input of document.querySelectorAll('input')){input.checked=localStorage.getItem('P1b:'+pack+':'+input.name)===input.value;input.addEventListener('change',()=>localStorage.setItem('P1b:'+pack+':'+input.name,input.value));}function save(){let answers=[...document.querySelectorAll('article')].map(a=>({card:+a.dataset.card,answer:a.querySelector('input:checked')?.value||null}));let blob=new Blob([JSON.stringify({pack,answers},null,2)],{type:'application/json'});let u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download='P1b-'+pack+'.json';a.click();URL.revokeObjectURL(u);}</script>'''


def document(title,body,script=''):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+STYLE+'</style><main>'+body+'</main>'+script+'</html>'


def link_copy(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(source,dest)
    assert sha(source)==sha(dest)


def make_pack(name, selected, original_ids, before, rng):
    rng.shuffle(selected);root=DEST/'delta_blind'/name;root.mkdir(parents=True,exist_ok=True)
    key=[];chunks=[];nchunks=math.ceil(len(selected)/40)
    for i,r in enumerate(selected,1):
        opaque=f'{i:04d}';crop=root/'images'/(opaque+'.png')
        link_copy(BASE/r['crop_path'],crop)
        page=json.loads((BASE/'receipts/pages'/(r['page_id']+'.json')).read_text())
        page_name=sha(BASE/page['image'])[:20]+'.png';link_copy(BASE/page['image'],root/'pages'/page_name)
        label=r['candidate_text'] or r['google_text']
        card=f'''<article data-card="{i}"><h2>Card {i:04d}</h2><a href="images/{opaque}.png" target="_blank"><img loading="lazy" src="images/{opaque}.png" alt="Native line crop for card {i}"></a><p class="label" lang="el">{html.escape(label)}</p><details><summary>Full page</summary><a href="pages/{page_name}" target="_blank">Open native full page</a><img loading="lazy" src="pages/{page_name}" alt="Full page context"></details><fieldset><legend>Does the string exactly match the visible line, with no missing or borrowed text?</legend>'''+''.join(f'<label><input type="radio" name="c{i}" value="{value}"> {value}</label>' for value in ['yes','no','uncertain'])+'</fieldset></article>'
        chunks.append(card)
        key.append(dict(card=i,line_id=r['id'],pilot=r['pilot'],label=label,previous_label=before[r['id']]['candidate_text'] or before[r['id']]['google_text'],
            changed=r['text_changed'],original_card=original_ids.get(r['id']),accepted=r['accepted'],flags=r['flags'],reasons=r['reasons'],crop_sha256=r['crop_sha256']))
    for part in range(nchunks):
        nav='<nav><a href="../index.html">All packs</a>'+''.join(f'<a href="sheet-{n+1:02d}.html">{n+1}</a>' for n in range(nchunks))+'</nav>'
        body=f'<h1>P1b — blind pixel adjudication</h1><p>Pack {html.escape(name)}, part {part+1} of {nchunks}. Judge the complete printed line, including punctuation, diacritics and margin ink. “Uncertain” is available for ambiguous pixels. Native crops and full pages are linked. Choices are saved locally; download each part after judging.</p>'+nav+''.join(chunks[part*40:(part+1)*40])+'<button onclick="save()">Download this part’s judgments</button>'+nav
        script=SCRIPT.replace('PACK',json.dumps(name+'-'+str(part+1)))
        (root/f'sheet-{part+1:02d}.html').write_text(document('P1b blind adjudication',body,script))
    write(DEST/'delta_keys'/(name+'.json'),dict(pack=name,seed=20261016,cards=key,disposition_hidden=True))
    return dict(pack=name,cards=len(selected),parts=nchunks,changed=sum(r['text_changed'] for r in selected),controls_by_source=dict(Counter(r['pilot'] for r in selected if not r['text_changed'])),path=f'delta_blind/{name}/sheet-01.html')


def main():
    after=rows(DEST/'alignment.jsonl');before={r['id']:r for r in rows(BASE/'bulk/alignment.jsonl')}
    originals={k['line_id']:dict(source=s,card=k['card']) for s in ['wikisource','perseus','gutenberg'] for k in json.loads((BASE/'receipts/blind-keys'/(s+'.json')).read_text())['cards']}
    rng=random.Random(20261016);controls=[]
    for s in ['wikisource','perseus','gutenberg']:
        pool=[r for r in after if r['pilot']==s and not r['text_changed'] and r['id'] in originals]
        rng.shuffle(pool)
        pool += [r for r in after if r['pilot']==s and not r['text_changed'] and r['id'] not in originals]
        assert len(pool)>=10;controls.extend(pool[:10])
    packs=[]
    packs.append(make_pack('focus',[r for r in after if r['text_changed'] and r['id'] in originals]+controls,originals,before,rng))
    packs.append(make_pack('complete',[r for r in after if r['text_changed']]+controls,originals,before,rng))
    body='<h1>P1b — second blind adjudication</h1><p>The focus pack contains every changed card from the original 120-card adjudication plus ten unchanged controls per source. The complete pack contains every changed text region across the 150-page pilot plus the same controls. Release decisions, flags, old labels, source identities and change/control status are absent from the cards.</p><ul>'+''.join(f'<li><a href="{p["pack"]}/sheet-01.html">{p["pack"].capitalize()} pack</a>: {p["cards"]} cards in {p["parts"]} parts</li>' for p in packs)+'</ul>'
    (DEST/'delta_blind/index.html').write_text(document('P1b second blind adjudication',body))
    # Separate, explicitly unblinded owner triage. Never link this from the blind pack.
    flagged=[r for r in after if r['accepted'] and r['disagrees_with_page_read']]
    prior={r['id'] for r in flagged if r['id'] in originals};flagged.sort(key=lambda r:(r['id'] not in prior,'expanded_hyphenation_disagreement' not in r['flags'],r['id']))
    body='<h1>P1b — owner/ink checks (unblinded)</h1><p>Eligible labels with a page-read letter or accent disagreement, followed by expanded-hyphenation evidence. These are triage flags, not proof that the reader is correct. Labels retain the proofread spelling. The blind packs contain no flags.</p>'
    for r in flagged:
        body+=f'<article><h2>{html.escape(r["id"])}</h2><img loading="lazy" src="../{html.escape(r["crop_path"])}" alt="Native crop"><p class="label">{html.escape(r["human_label"])}</p><p>Cached page read: {html.escape(r["alignment_query"])}</p><p>{html.escape(", ".join(r["flags"]))}</p></article>'
    (DEST/'owner_ink_checks.html').write_text(document('P1b owner/ink checks',body))
    jsonl=lambda path,rs:path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs))
    jsonl(DEST/'owner_ink_checks.jsonl',flagged)
    write(DEST/'delta_summary.json',dict(packs=packs,owner_checks=len(flagged),index='p1b/delta_blind/index.html',judgments_received=0))
    print(json.dumps(packs,indent=2))

if __name__=='__main__':main()
