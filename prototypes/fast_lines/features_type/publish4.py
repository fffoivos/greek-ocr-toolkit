"""Publish a linked evidence index and measured tables without rewriting round3."""
from html import escape
import json
from pathlib import Path
import re
import numpy as np
from ..shared.manifest import ROOT
from ..shared.timing import dump
from .reference import DEST
from .audit4 import pointer


def run():
    validation=json.loads((DEST/'round4-validation.json').read_text())
    timings=json.loads((DEST/'round4-feature-timings.json').read_text())
    text=['\n<!-- ROUND4 MEASURED TABLES -->\n',
          'Milliseconds, raw per-page receipts in `round4-final-1c9641d65801/`.\n',
          '| Cohort/repeat | n | C median / p95 / max | Q8+C median / p95 / max | Full median / max |',
          '|---|---:|---|---|---|']
    for r in validation['repeats']:
        fields=[]
        for key in ('type_s','stack_added_s','total_s'):
            v=r[key];fields.append(' / '.join(f'{v[z]:.3f}' for z in (('median','p95','maximum') if key!='total_s' else ('median','maximum'))))
        text.append(f"| {r['cohort']} r{r['repeat']} | {r['n']} | "+' | '.join(fields)+' |')
    text+=['','The worst C page across all195 is `s2-0ce9d1025b3f23c7119e-p00001`: reflected-print rejection, not an accepted correction. The new discrepancy maximum is `s2-6f045b952f909b38d4db-p00001`, also a rejection. Paying ownership to reject a false wake is still charged.','',
           'On-demand census (median / maximum ms; all extraction included, image I/O excluded):','',
           '| Feature / route | n per repeat | repeat1 | repeat2 |','|---|---:|---|---|']
    for feature in ('rows','table_extents','glyph_atlas'):
        for route in ('slow','explicit','heuristic'):
            cells=[]
            for repeat in (1,2):
                v=[r['seconds']*1000 for r in timings if r['feature']==feature and r['route']==route and r['repeat']==repeat]
                cells.append(f'{np.median(v):.3f} / {max(v):.3f}')
            text.append(f'| {feature} / {route} | {len(v)} | '+' | '.join(cells)+' |')
    text+=['','The atlas charges fresh native extraction for both pages of each pairing (once for a within-page pairing). It is not a fast clean-page feature. The row census also remains outside the runtime. The numbers above measure v3 rows, v6 table extents and v3 atlas routes; the late v7 dot-interior diagnostic was not substituted into these timings.','']
    report=ROOT/'docs/research/FAST_LINES_FEATURES_C.md';body=report.read_text().split('<!-- ROUND4 MEASURED TABLES -->')[0].rstrip();report.write_text(body+'\n'+'\n'.join(text))

    dirs=[('Row bands and physical guides',pointer('active-rows4.json')),
          ('Same-page and book glyph exemplars',pointer('active-identity4.json')),
          ('Table boundary cycle6',pointer('active-extents4.json')),
          ('Triggered table counterexamples',pointer('active-extents4-triggered.json')),
          ('Dot interior cycle7',DEST/'round4-table-dots-v7'),
          ('Grid extensions all195',pointer('active-edges4.json')),
          ('Per-line audit and worst crops',DEST/'round4-audit'),
          ('Final detector corrections',pointer('active-final4.json')),
          ('Cooperation table conflict',DEST/'cooperation-round4')]
    intro='''# Round4 type evidence

Sixteen added rows on fourteen pages in the experimental Q8+C pipeline: the fourteen round3 additions plus two inspected drop-cap rows. All old output items preserved; all585 fresh executions reproduce exactly. This is separate from stack's frozen fifteen-addition composition.

[Open the image and data index](round4.html). [Read the report](../../../../docs/research/FAST_LINES_FEATURES_C.md).

## Legend

- Row crops: raw / native / R1 / R2 vertically. Green body candidates have supported contacts; amber are unsupported. Orange boxes are detached/other marks. Blue and purple paths enclose physical ink mass, not semantic baselines. A false-clear joined flag remains on Arabic17/26/31.
- Glyph boards: each pair shows the original query and an observed alternate. Captions identify route, source line and similarity. Three alternatives remain in JSON. Similarity is not character or font identity.
- Tablev6: purple proposed dots, blue seed row boxes, green protected extents. Missing protection means unknown. Tablev7: purple filled interiors, red rejected interiors. Neither rendering establishes complete boundaries.
- Grid boards: raw / native / R1 / R2. Grey existing grid axes, green supported unowned candidates, amber uncertain or already-owned candidates. Green does not certify front text; ornaments and verso can look regular.
- Final correction images: original small-detector boxes grey, new ink/lines green, removed ink red. Q8 separator cuts are included. `new-00.jpg` shows both new raw/after crops. JSON uses detector format with null baselines.

## Late table cycle7 inspection

The filled-interior test removes many compact prose fragments on4959p5 while preserving the922ep5 table, but a large false prose region remains. Native and both reduced routes are rendered on21pages. This cycle is diagnostic only; runtime and timing receipts retain v6. Component-to-row ownership and dot scale remain unresolved.

## Review coverage and failures

Every page/line/slot has the saved comparison records. Human inspection covered selected crops from each rendering iteration, twelve worst height disagreements, all ten slots positive on any route in the final195 study, both new raw/after corrections, the prior fourteen additions in round3, and named atlas/table counterexamples. It was not exhaustive transcription of195pages.

The scalar Arabic height can still be false-clear, dense row resolution is incomplete, atlas routes disagree and do not name fonts,63c4 table protection is partial,4959 prose is overprotected,7792 ornament escapes B's default motif scout (regional detector declines it), and global pitch misses severe curl. The native atlas is too slow for runtime.

## Reproduction

From the worktree root with the mandated Python and PYTHONDONTWRITEBYTECODE=1:

```
python -m prototypes.fast_lines.features_type.rows4 slow --version 3
python -m prototypes.fast_lines.features_type.rows4 fast --version 3
python -m prototypes.fast_lines.features_type.identity4 slow --version 3
python -m prototypes.fast_lines.features_type.identity4 fast --version 3
python -m prototypes.fast_lines.features_type.extents4 slow --version 6
python -m prototypes.fast_lines.features_type.extents4 fast --version 6
python -m prototypes.fast_lines.features_type.edges4 slow --version 2 --all
python -m prototypes.fast_lines.features_type.edges4 fast --version 2 --all
python -m prototypes.fast_lines.features_type.extended4 --repeat 1
python -m prototypes.fast_lines.features_type.extended4 --repeat 2
python -m prototypes.fast_lines.features_type.extended4 --repeat 3
python -m prototypes.fast_lines.features_type.extents4 slow --version 6 --triggered
python -m prototypes.fast_lines.features_type.extents4 fast --version 6 --triggered
python -m prototypes.fast_lines.features_type.table_dots7 slow
python -m prototypes.fast_lines.features_type.table_dots7 fast
python -m prototypes.fast_lines.features_type.audit4
python -m prototypes.fast_lines.features_type.validate4
python -m prototypes.fast_lines.features_type.measure4
python -m prototypes.fast_lines.features_type.publish4
```

Run slow rendering, inspect, then fast routes when extending a feature. The sequence above reproduces already inspected final versions; it is not permission to skip that method for new ideas.

## Evidence directories
'''
    intro+='\n'.join(f'- {title}: [{d.name}/]({d.name}/)' for title,d in dirs)
    intro+='\n\n[Export checks and per-page comparisons](round4-validation.json); [raw census times](round4-feature-timings.json).\n'
    (DEST/'round4-README.md').write_text(intro)
    html=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Round4 type evidence</title><style>body{font:16px/1.5 system-ui;max-width:1150px;margin:2rem auto;padding:0 1rem;color:#202620}h1,h2{line-height:1.2}a{color:#18583b}li{overflow-wrap:anywhere}img{max-width:100%;height:auto}details{margin:1rem 0}summary{font-weight:650;cursor:pointer}.hero{max-width:850px}small{color:#555}</style><body><h1>Round4 type evidence</h1><p>Physical renderings, failed iterations and reproducible conditional corrections.</p><p><a href="round4-README.md">Legend, limitations and reproduction</a> · <a href="round4-validation.json">29,549 export checks and per-page comparisons</a></p>']
    final=pointer('active-final4.json')
    html.append(f'<p>Two new inspected rows; fourteen round3 additions retained. Separate from the frozen combined stack.</p><a href="{final.name}/new-00.jpg"><img class="hero" src="{final.name}/new-00.jpg" alt="Two new rows, original and corrected crops"></a>')
    for title,d in dirs:
        html.append(f'<details><summary>{escape(title)}</summary><ul>')
        for f in sorted(d.iterdir()):
            if f.suffix not in ('.jpg','.json') or '.r1.' in f.name or '.r2.' in f.name or '.r3.' in f.name:continue
            href=f.relative_to(DEST).as_posix();html.append(f'<li><a href="{escape(href)}">{escape(f.name)}</a></li>')
        html.append('</ul></details>')
    html.append('<p>Original and failed versions remain in adjacent round4 directories. No font identification, semantic baselines or complete table-boundary claim.</p></body></html>')
    content='\n'.join(html);(DEST/'round4.html').write_text(content)
    links=re.findall(r'(?:href|src)="([^"]+)"',content)
    assert all((DEST/p).is_file() for p in links), 'broken artifact link'
    dump(DEST/'round4-index-validation.json',dict(links=len(links),all_exist=True))
    root=DEST/'README.md';link='\n\n[Round4 continuation: evidence, failures and timings](round4-README.md).\n'
    if 'Round4 continuation:' not in root.read_text():root.write_text(root.read_text()+link)
    root=DEST/'index.html';body=root.read_text()
    if 'round4.html' not in body:root.write_text(body.replace('<body>','<body><p><a href="round4.html">Round4 continuation</a></p>',1))
    print('linked artifacts',len(links))


if __name__=='__main__':run()
