"""Build the local scoreboard through the prescribed owner_sheet renderer.

Run with collector .venv Python and PYTHONPATH=cleanup. All writes stay here.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
from collections import defaultdict
import html
import json
from pathlib import Path
import sys
# The renderer is loaded before the worktree is placed on sys.path.
sys.dont_write_bytecode=True
from greekocr.adjudicate.owner_sheet import render
import greekocr
ROOT=Path(__file__).resolve().parents[2]
greekocr.__path__.insert(0,str(ROOT/'greekocr'))
from greekocr.labelfix.lqb import DEFAULT, PROJECTS, GROUPS, rows, load_version, error, dump, sha256, measurement_text, intro_sentences


def direction(pair):
    ci=pair['ci95']
    if ci is None:return 'not measured'
    return 'fewer' if ci[1]<0 else 'more' if ci[0]>0 else 'no clear change'


def fmt(x):return 'not measured' if x is None else f'{x:.2f}'


def summary_html(score):
    out=['<section class="lqb-intro">']
    out.extend('<p>'+html.escape(x)+'</p>' for x in intro_sentences(score))
    out.append('<p>Only uniform draws and eligible locked strata carry POPULATION rates. Other counts describe this sample. Decision precision is conditional on sampled decisions. In-sample and regression items are separate. Intervals are descriptive on selected samples.</p><div style="overflow-x:auto"><table><thead><tr><th>class</th><th>version</th><th>sample_type</th><th>measurement</th></tr></thead><tbody>')
    missing=[]
    for cls in GROUPS:
        for name,version in score['versions'].items():
            row=version[cls+'|A+B']
            if row['status']=='not measured':missing.append(cls+' / '+name);continue
            for typ,r in row['by_sample_type'].items():
                if r['status']=='not measured':continue
                out.append('<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in [cls,name,typ,measurement_text(r)])+'</tr>')
    out.append('</tbody></table></div><h2>Not measured</h2><p>'+html.escape('; '.join(missing))+'</p><p>Letters: i-a certifies only 24 selected word scopes / 125 known printed letters on 23 lines, not all 133 lines. Wikisource edition normalization is reference only; literal pixel forms govern certified scopes. i-b: reference transcription, not pixel truth; adjudication pending. See SCORE_v1.md for citations.</p></section>')
    return ''.join(out)


def main(score_path=None, truth_path=None, crop_sources=None):
    registry=json.loads((DEFAULT/'versions.json').read_text());score=json.loads((score_path or DEFAULT/'score_v1.json').read_text());truth=list(rows(truth_path or DEFAULT/'truth_v1.jsonl'));wanted={r['line_id'] for r in truth};cache={}
    # A release admission is a parallel branch, never a successor to RU1.
    names=['google_raw','w1_label','ru1_v1','sf6_release']
    versions={n:load_version(n,registry,wanted,cache) for n in names}
    changed=defaultdict(list)
    for r in truth:
        lid=r['line_id']
        for a,b in [('google_raw','w1_label'),('w1_label','ru1_v1'),('google_raw','sf6_release')]:
            if lid not in versions[a] or lid not in versions[b]:continue
            x=error(r,versions[a][lid]);y=error(r,versions[b][lid])
            if x is not None and y is not None and bool(x[0])!=bool(y[0]):
                changed[lid].append((r,a,b,'fewer' if y[0]<x[0] else 'more'))
    # Read only needed saved crop paths, never regenerate in the collector.
    features=Path(registry['versions']['w1_label']['path']);lookup={}
    for r in rows(features):
        if r['id'] in changed:lookup[r['id']]=r
    for lid, source in (crop_sources or {}).items():
        if lid in changed:
            if lid in lookup:assert lookup[lid]['crop_sha256']==source['crop_sha256']
            else:lookup[lid]=source
    cards=[];ledger=[]
    for lid,events in sorted(changed.items()):
        image=Path(lookup[lid]['crop'])
        if not image.is_file():
            pack=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru1')
            matches=sorted(pack.glob('*/r*/crops/'+lookup[lid]['crop_sha256']+'.png'))
            if matches:image=matches[0]
        if not image.is_file():
            # Existing independently rendered full-line copies are valid display
            # witnesses; never silently substitute a crop from another line.
            candidates=[]
            for p in [ROOT/'artifacts/n1/controls/approved.jsonl',ROOT/'artifacts/n1/n1t/slots.jsonl']:
                for row in rows(p):
                    if row.get('line_id')==lid and row.get('line'):candidates.append(Path(row['line']))
            image=next((p for p in candidates if p.is_file()),image)
        if not image.is_file():raise FileNotFoundError('changed line crop unavailable: '+lid)
        if sha256(image)!=lookup[lid]['crop_sha256']:raise ValueError('saved crop does not match W1 hash: '+lid)
        # Truth is partial (slots); show adjudicated forms explicitly instead of
        # inventing a complete corrected line from unreviewed labels.
        ts=sorted({r['class']+': '+r['printed']+' @ '+json.dumps(r['slot'],ensure_ascii=False,sort_keys=True) for r,a,b,d in events})
        printed='; '.join(ts)
        rs=[dict(name='Google',text=versions['google_raw'][lid])]
        rs.extend(dict(name=n,text=versions[n][lid]) for n in names[1:] if lid in versions[n])
        rs.append(dict(name='Truth (adjudicated slots)',text=printed))
        tags=sorted({r['class'] for r,a,b,d in events}|{'tier '+r['tier'] for r,a,b,d in events}|{a+'→'+b+': '+d for r,a,b,d in events})
        cards.append(dict(line_id=lid,image=str(image),rows=rs,printed=printed,tags=[dict(text=t) for t in tags],note='Frozen adjudicated truth; no reading requested.'))
        ledger.append(dict(line_id=lid,image=str(image),image_sha256=sha256(image),events=[dict(truth_id=r['truth_id'],a=a,b=b,direction=d,tier=r['tier'],used_by=r['used_by']) for r,a,b,d in events]))
    sentinel='LQB_INTRO_PLACEHOLDER'
    page=render(cards,dict(title='Label Quality Scoreboard',intro=sentinel))
    needle='<p class="meta">'+sentinel+'</p>'
    assert page.count(needle)==1
    page=page.replace(needle,summary_html(score))
    # This sheet is a frozen local report. Keep adjudicated Printed values fixed
    # and disable the renderer's optional remote note database entirely.
    start=page.index('<script>');end=page.index('</script>',start)
    page=page[:start]+'<script>document.querySelectorAll("input,textarea").forEach(x=>x.readOnly=true);document.querySelectorAll(".status").forEach(x=>x.textContent="frozen adjudicated truth");</script>'+page[end+9:]
    page=page.replace('</style>',' .lqb-intro table{width:100%;border-collapse:collapse}.lqb-intro td,.lqb-intro th{padding:6px;border-bottom:1px solid #ddd;text-align:left}.lqb-intro{line-height:1.5}</style>',1)
    target=DEFAULT/'scoreboard.html';target.write_text(page)
    if _data_input(target).stat().st_size>=14_000_000:raise ValueError('scoreboard exceeds 14 MB')
    dump(DEFAULT/'scoreboard_cards.json',ledger)
    dump(DEFAULT/'scoreboard_build.json',dict(cards=len(cards),bytes=_data_input(target).stat().st_size,sha256=sha256(target),renderer='greekocr.adjudicate.owner_sheet.render',renderer_sha256=sha256(PROJECTS/'greek-ocr-toolkit-cleanup/greekocr/adjudicate/owner_sheet.py'),python=sys.executable,network=False,notes='frozen read-only; remote database disabled'))
    print('scoreboard',len(cards),'cards',_data_input(target).stat().st_size/1e6,'MB')

if __name__=='__main__':main()
