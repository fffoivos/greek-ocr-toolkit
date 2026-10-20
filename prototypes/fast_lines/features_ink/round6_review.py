"""R6 feature comparisons and transparent per-segment, per-comment review files."""
import argparse,html,json,re
from pathlib import Path
import cv2,numpy as np
from .round6_faintness import DEST,ROOT,REVIEW,PREVIOUS,cohort,inputs,picture
from ..shared.ink_faintness import classify
from ..shared.timing import dump
from ..shared.geometry import roi
from ..shared.contracts import bbox


def compare():
    out=DEST/'comparison';out.mkdir(exist_ok=True);records=[];panels=[]
    for row in cohort():
        p=row['page'];g,items=inputs(row);fast=json.load(open(DEST/'fast-v9'/(p+'.json')))
        native=[]
        for route in ('slow','explicit'):
            # Extraction unchanged: v8 strengthens the preservation predicate.
            src=DEST/'native-v7-all'/(p+'.'+route+'.json');e=json.load(open(src))
            classify(e['regions'],e['reference']);e['suppress_indices']=[r['line'] for r in e['regions'] if r['drop']]
            e.update(version=9,derivation=str(src.relative_to(ROOT)),note='v7 native measurements, v9 classification; seconds are extraction-study timing, not runtime')
            dump(out/(p+'.'+route+'.json'),e);picture(g,items,e,out/(p+'.'+route+'.jpg'));native.append(e)
        regions={r['line']:r for r in fast['regions']};strips={r['line']:r for r in fast['scout']['regions']}
        rr=[]
        for i,q in enumerate(items):
            a=native[0]['regions'][i];b=native[1]['regions'][i];f=regions.get(i,{})
            rr.append(dict(line=i,polygon=q['polygon'],slow=a['drop'],reduced=b['drop'],localized=f.get('drop',False),
                           heuristic=strips[i]['candidate'],normal_share=a['normal_share'],normal_bodies=a['normal'],bodies=a['bodies'],
                           localized_normal_share=f.get('normal_share'),scout_skipped=i not in regions))
        dump(out/(p+'.segments.json'),rr)
        records.append(dict(page=p,n=len(rr),slow=native[0]['suppress_indices'],reduced=native[1]['suppress_indices'],localized=fast['suppress_indices'],heuristic=fast['scout']['candidate_indices'],parked=row['parked']))
        # Runtime decisions over the native rendering; R2 tile strips separately.
        im=cv2.imread(str(out/(p+'.slow.jpg')));s=im.shape[1]/g.shape[1]
        for r in rr:
            if not (r['slow'] or r['localized'] or r['heuristic']):continue
            color=(0,150,0) if r['localized']==r['slow'] else (180,0,180)
            cv2.polylines(im,[np.rint(np.array(r['polygon'])*s).astype(np.int32)],True,color,3)
        cv2.imwrite(str(out/(p+'.routes.jpg')),im)
        im=cv2.cvtColor(cv2.resize(g,None,fx=s,fy=s),cv2.COLOR_GRAY2BGR)
        for r in fast['scout']['regions']:
            x,y,z,w=bbox(items[r['line']]);n=len(r['cores'])
            for j,v in enumerate(r['cores']):
                c=(20,150,20) if v>=fast['scout']['reference']['boundary'] else (0,140,255)
                cv2.line(im,(round((x+j*(z-x)/n)*s),round((y+w)*s/2)),(round((x+(j+1)*(z-x)/n)*s),round((y+w)*s/2)),c,2)
        cv2.imwrite(str(out/(p+'.heuristic.jpg')),im)
        for r in rr:
            if r['slow']!=r['localized'] and not row['parked']:
                x,y,z,w=roi(np.array(bbox(items[r['line']]))+[-15,-15,15,15],g.shape)
                cv2.imwrite(str(out/f'{p}.difference-{r["line"]}.jpg'),g[y:w,x:z])
        print('comparison',p,flush=True)
    dump(out/'records.json',records)
    dump(out/'summary.json',dict(segments=sum(r['n'] for r in records),slow=sum(len(r['slow']) for r in records),reduced=sum(len(r['reduced']) for r in records),localized=sum(len(r['localized']) for r in records),heuristic=sum(len(r['heuristic']) for r in records),
                               different=[dict(page=r['page'],native_only=sorted(set(r['slow'])-set(r['localized'])),localized_only=sorted(set(r['localized'])-set(r['slow']))) for r in records if set(r['slow'])!=set(r['localized'])]))


def sheets(directory,pattern='*.jpg',prefix='sheet'):
    paths=sorted(p for p in directory.glob(pattern) if not p.name.startswith(prefix));tiles=[];ledger=[]
    for p in paths:
        im=cv2.imread(str(p));s=min(600/im.shape[1],920/im.shape[0]);im=cv2.resize(im,None,fx=s,fy=s)
        tile=np.full((950,600,3),255,np.uint8);tile[30:30+im.shape[0],:im.shape[1]]=im
        cv2.putText(tile,p.stem[:62],(3,20),0,.34,(0,0,0),1);tiles.append(tile);ledger.append(dict(image=p.name,sheet=(len(ledger)//6)))
        if len(tiles)==6:
            cv2.imwrite(str(directory/f'{prefix}-{(len(ledger)-1)//6:02d}.jpg'),np.vstack([np.hstack(tiles[:3]),np.hstack(tiles[3:])]));tiles=[]
    if tiles:
        tiles.extend([np.full((950,600,3),255,np.uint8)]*(6-len(tiles)))
        cv2.imwrite(str(directory/f'{prefix}-{(len(ledger)-1)//6:02d}.jpg'),np.vstack([np.hstack(tiles[:3]),np.hstack(tiles[3:])]))
    dump(directory/(prefix+'-ledger.json'),ledger)


def final_review(version):
    out=DEST/version;links=[];receipts=[json.load(open(p)) for p in out.glob('*.r[12].json')];summary={}
    for repeat in (1,2):
        for group in ('agreement','discrepancy','all'):
            rr=[json.load(open(p)) for p in out.glob(f'*.r{repeat}.json')]
            rr=[r for r in rr if group=='all' or r['group']==group or (group=='discrepancy' and r['group'].startswith('discrepancy'))]
            if not rr:continue
            summary[f'{group}_r{repeat}']={}
            for key in ('correction_s','total_s','faint_s','faint_scout_s'):
                values=np.array([r.get(key,r['stages'].get(key,0)) for r in rr])*1000
                summary[f'{group}_r{repeat}'][key]=dict(n=len(rr),median=float(np.median(values)),p95=float(np.percentile(values,95)),max=float(values.max()),max_page=rr[int(values.argmax())]['page'])
    dump(out/'summary.json',summary)
    changes={r['page']:json.load(open(out/(r['page']+'.delta.json'))) for r in cohort()}
    # Owner marks use the zero-based measurement item index (rows_r5.json), independently
    # of the XY display order. Preserve both original number and exact polygon.
    marks_path=ROOT.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r5_rows/owner_marks.json'
    marks=json.load(open(marks_path));marked=[]
    for m in marks:
        row=next(r for r in cohort() if r['page']==m['page']);_,old=inputs(row);i=m['segment']
        touched=i in {q['index'] for q in changes[m['page']]['removed']}
        marked.append(dict(m,item_index=i,polygon=old[i]['polygon'],touched=touched,outcome='removed as wholly faint' if touched else 'identical segment retained; row count not changed by task A'))
    dump(out/'owner-marks.json',marked)
    # Verbatim owner comments are retained even where this task makes no claim.
    review=(REVIEW/'REVIEW.md').read_text();comments=[]
    for block in re.split(r'^## ',review,flags=re.M)[1:]:
        p=block.splitlines()[0].strip();text='\n'.join(line[2:] if line.startswith('> ') else '' for line in block.splitlines() if line.startswith('>')).strip()
        if p not in changes:continue
        delta=changes[p];comments.append(dict(page=p,comment=text,removed_r5_indices=[q['index'] for q in delta['removed']],status='new faintness removals; inspect the linked exact footprints' if delta['removed'] else 'no task-A change',image=p+'.jpg'))
    dump(out/'owner-comments.json',comments)
    (out/'COMMENTS.md').write_text('# Owner comments — task A delta only\n\nNumbers in the original comments belong to round4. The table links round6 and gives exact removed round5 item indices (zero based), not renumbered guesses. Splitting, curvature and missing-row clauses are outside task A.\n\n'+''.join(f'## {r["page"]}\n\n> '+r['comment'].replace('\n','\n> ')+f'\n\n{r["status"]}. Removed R5 indices: {r["removed_r5_indices"]}. [Numbered result]({r["image"]}); [exact delta]({r["page"]}.delta.json).\n\n' for r in comments))
    for row in cohort():
        p=row['page'];d=changes[p]
        links.append(f'<article><h3>{html.escape(p)}</h3><p>{len(d["removed"])} new faint removals</p><a href="{p}.jpg"><img loading="lazy" src="{p}.jpg"></a><p><a href="{p}.json">detector JSON</a> · <a href="{p}.evidence.json">evidence</a> · <a href="{p}.delta.json">R5 delta</a> · <a href="../comparison/{p}.slow.jpg">native darkness</a> · <a href="../comparison/{p}.slow.strokes.jpg">native strokes</a> · <a href="../comparison/{p}.routes.jpg">routes</a> · <a href="../comparison/{p}.heuristic.jpg">scout</a> · <a href="../comparison/{p}.segments.json">every segment</a></p></article>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R6 A relative faintness</title><style>body{font:16px system-ui;margin:24px;background:#f4f2ed}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}article{background:white;padding:12px}img{width:100%}h3{overflow-wrap:anywhere}@media(max-width:900px){main{grid-template-columns:1fr}}</style><h1>Round 6 A: relative faintness</h1><p>Blue unchanged; green added; purple reshaped over grey original; red removed. Task A only removes final R5 segments.</p><p><a href="COMMENTS.md">Verbatim owner comments</a> · <a href="owner-marks.json">Every owner-marked segment</a> · <a href="summary.json">Two fresh timing passes</a> · <a href="../README.md">Rendering legend and failures</a></p><main>'+''.join(links)+'</main>')
    sheets(out,pattern='*.jpg',prefix='overview')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action');a=ap.parse_args()
    if a.action=='compare':compare();sheets(DEST/'comparison','*.slow.jpg','native-overview')
    else:final_review(a.action)
