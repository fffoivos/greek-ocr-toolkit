"""Build the owner's review sheet (crops, letter slots, detected marks, texts, autosaving notes).

Usage: .venv/bin/python scripts/labelfix/sheet_build.py --candidates docs/records/labelfix/validation_candidates_s0_strict.jsonl \
          --out /path/sheet.html [--limit N] [--title "..."] [--intro "..."]
Publish with the Artifact tool to https://claude.ai/artifact/CBAfrctSngHEL377TcYFSW (read it first in a new session),
capabilities {db:{}, user:{}} carried forward; the owner's notes live in the artifact db collection `notes` keyed by line_id.
Format is the owner's (16 Oct 2026): full line crop with slot numbers; detached mark blobs boxed (green above / blue below) and
named by the shape classifier; attached (ascender) ink shown as grey dashes and NOT named; detected sequence by slot; Google /
human (test reference only) / printed-by-owner texts; autosaving notes per line. Keep this format for every iteration.
"""
from __future__ import annotations
import argparse, base64, html, io, json, os, re, unicodedata as ud
from PIL import Image, ImageDraw, ImageFont
from greekocr.labelfix import ink as I, markshape as M
from greekocr.labelfix.linemetric import printed_line, slot_mapping
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.sheet import load_alignments, crop_key
from pathlib import Path

P = '/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/e3b/predictions/'
nfc = lambda s: ud.normalize('NFC', s or '')
nfd = lambda s: ud.normalize('NFD', s or '')
SYM = {'acute': '´', 'grave': '`', 'circumflex': '῀', 'psili': '᾿', 'dasia': '῾', 'subscript': 'ι̣', 'dialytika': '¨', 'none': '·', 'apostrophe': '’'}

def cls_sym(c): return ''.join(SYM.get(p, p) for p in c.split('+')) if c != 'none' else '·'
def text_marks(s):
    out = []
    for ch in nfd(s):
        if ud.category(ch).startswith('M'):
            if out: out[-1] += ch
        elif ch.isalpha(): out.append('◌')
        elif ch == ' ': out.append(' ')
    return out
def seq_html(items): return ' '.join(html.escape(x) if x != ' ' else '&nbsp;&nbsp;' for x in items)
def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

def detect(path, model, line=None, al=None, truth=None, stored=None):
    im = Image.open(path); ci = I.analyse(im)
    letters = sorted([c for c in ci.components if c.role == 'letter'], key=lambda c: c.x0)
    slots = []
    apost = {}
    mapping = None
    if line is not None and al is not None:
        mapping = slot_mapping(line, al, ci, truth or {})
        apost = I.apostrophe_candidates(ci, [(x['component'], x['base'], x['word_final']) for x in mapping])
    apost_boxes = {(b.x0,b.y0,b.x1,b.y1) for bs in apost.values() for b in bs}
    for slot_index, c in enumerate(letters):
        if stored is not None:
            s=stored['slots'][slot_index];ev=s['evidence']
            desc=s['cls']
            if s['above'] and desc=='none':desc='?(unclassified)'
            if s['below'] and 'subscript' not in desc:desc=('' if desc=='none' else desc+'+')+'subscript'
            if s['apostrophe']:desc=('' if desc=='none' else desc+'+')+'apostrophe'
            slots.append(dict(x0=c.x0,x1=c.x1,cls=desc,p=1.,det=[b['bbox'] for b in ev['above']]+[b['bbox'] for b in ev.get('apostrophes',[])],
                              att=[b['bbox'] for b in ev['diagnostics']],below=[b['bbox'] for b in ev['below']]))
            continue
        ev = I.mark_evidence(ci, c.x0, c.x1, base_letter=mapping[slot_index]['base'] if mapping else None)
        det_above = [b for b in ev.above if (b.x0,b.y0,b.x1,b.y1) not in apost_boxes]; att_above = ev.diagnostics
        if det_above or ev.below:
            ev2 = I.MarkEvidence(above=det_above, below=list(ev.below), window=ev.window, xh=ev.xh, meanline=ev.meanline, baseline=ev.baseline,
                                 body=ev.body, body_source=ev.body_source, n_letters_in_span=ev.n_letters_in_span, neighbour_marks=ev.neighbour_marks,
                                 clipped_top=ev.clipped_top, clipped_bottom=ev.clipped_bottom)
            cl, p, _ = model.predict(M.features(ev2)); desc = cl if p >= 0.5 else f'?({len(det_above)}↑{len(ev.below)}↓)'
        else: desc, p = 'none', 1.0
        if slot_index in apost:
            desc = (desc + '+' if desc != 'none' else '') + 'apostrophe'
            det_above += apost[slot_index]
        slots.append(dict(x0=c.x0, x1=c.x1, cls=desc, p=p, det=[(b.x0, b.y0, b.x1, b.y1) for b in det_above],
                          att=[(b.x0, b.y0, b.x1, b.y1) for b in att_above], below=[(b.x0, b.y0, b.x1, b.y1) for b in ev.below]))
    W, Hh = im.size; s = 2 if W < 700 else 1; big = im.convert('RGB').resize((W * s, Hh * s), Image.NEAREST); d = ImageDraw.Draw(big)
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 11 * s)
    except Exception: font = None
    for i, sl in enumerate(slots):
        for bb in sl['det']: d.rectangle([bb[0] * s, bb[1] * s, bb[2] * s, bb[3] * s], outline=(30, 140, 60), width=2)
        for bb in sl['below']: d.rectangle([bb[0] * s, bb[1] * s, bb[2] * s, bb[3] * s], outline=(40, 80, 200), width=2)
        for bb in sl['att']:
            for k in range(bb[0] * s, bb[2] * s, 6): d.line([k, bb[1] * s, min(k + 3, bb[2] * s), bb[1] * s], fill=(170, 170, 170), width=1)
        if sl['cls'] != 'none': d.text((sl['x0'] * s, 0), cls_sym(sl['cls']) if not sl['cls'].startswith('?') else '?', fill=(200, 40, 40), font=font)
        d.text((sl['x0'] * s, Hh * s - 12 * s), str(i + 1), fill=(120, 120, 120), font=font)
    if big.size[0] > 1000: big = big.resize((1000, int(big.size[1] * 1000 / big.size[0])), Image.LANCZOS)
    return slots, uri(big)

CSS = '''<title>Polytonic Spell Check Status</title>
<style>
:root{--bg:#f7f5f0;--fg:#1d1a16;--muted:#6b645a;--line:#d9d3c8;--panel:#fffdf9;--ok:#2e7d4f;--warn:#b26a00;--bad:#a93a2f;--soft:#ece7dd;--hl:#fff1a8;--body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;--display:"Source Serif 4",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;--panel:#201f24;--ok:#7fc39a;--warn:#e2a64a;--bad:#e2796c;--soft:#2a282e;--hl:#5a4d12;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;--panel:#201f24;--ok:#7fc39a;--warn:#e2a64a;--bad:#e2796c;--soft:#2a282e;--hl:#5a4d12;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.45;padding-block:24px 56px;padding-inline:16px}
main{max-width:980px;margin:0 auto;min-width:0} h1{font-family:var(--display);font-size:1.9rem;margin:0 0 4px} h2{font-family:var(--display);font-size:1.3rem;margin:34px 0 8px}
p{max-width:72ch;margin:0 0 10px} .meta{color:var(--muted);font-size:.9rem}
.card{background:var(--panel);border:1px solid var(--line);padding:10px;margin:12px 0;min-width:0} .card img{display:block;width:100%;max-width:100%;height:auto;border:1px solid var(--line);background:#fff}
table.w{width:100%;border-collapse:collapse;margin-top:8px;font-size:1.05rem;font-family:"Source Serif 4",Georgia,"Times New Roman",serif}
table.w th{width:92px;text-align:left;font-family:var(--body);font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding:3px 6px 3px 0;vertical-align:top} table.w td{padding:3px 0;word-break:break-word}
mark{background:var(--hl);color:inherit;padding:0 2px} .row{margin-top:6px;font-size:.82rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pill{display:inline-block;font-size:.7rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:1px 7px;border-radius:999px;border:1px solid var(--line);color:var(--fg)} .ok{color:var(--ok);border-color:var(--ok)} .bad{color:var(--bad);border-color:var(--bad)} .warn{color:var(--warn);border-color:var(--warn)}
.why{font-family:"IBM Plex Mono",Menlo,monospace;font-size:.78rem} .seq{font-size:.95rem;line-height:1.7;margin:8px 0;display:grid;gap:4px;font-family:"Source Serif 4",Georgia,serif} .seq b{font-family:var(--body);font-size:.74rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.notes{margin-top:10px;border-top:1px dashed var(--line);padding-top:8px;display:grid;gap:4px}.notes label{font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}.notes textarea{width:100%;box-sizing:border-box;font-family:"Source Serif 4",Georgia,serif;font-size:1rem;padding:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}.nrow{display:flex;gap:10px;align-items:center}.status{font-size:.8rem;color:var(--muted)}.notes.saved .status{color:var(--ok)}
</style>'''

SCRIPT = '''<script>
(async function(){
  const cards=[...document.querySelectorAll('.notes[data-line]')];
  const setStatus=(el,t,ok)=>{const st=el.querySelector('.status');st.textContent=t;el.classList.toggle('saved',!!ok)};
  let db=null; try{ db=await (window.claude&&window.claude.use?window.claude.use('db'):Promise.resolve(null)); }catch(e){ db=null }
  if(!db){ cards.forEach(el=>setStatus(el,'notes need the signed-in owner view to save',false)); return; }
  const last={};
  const edited={};
  try{ const snap=await db.collection('notes').limit(1000).get();
    snap.docs.forEach(d=>{ if(!d.exists) return; const el=document.querySelector('.notes[data-line="'+d.id+'"]'); if(!el) return; const x=d.data()||{};
      if(x.printed_edited===true && typeof x.printed==='string'){ el.querySelector('.printed').value=x.printed; edited[d.id]=true; } if(typeof x.note==='string') el.querySelector('.note').value=x.note;
      last[d.id]=JSON.stringify({note:x.note||'',...(edited[d.id]?{printed:x.printed,printed_edited:true}:{})}); setStatus(el,'saved '+(x.updated||''),true); });
  }catch(e){ cards.forEach(el=>setStatus(el,'could not load notes ('+(e&&e.code||'error')+')',false)); }
  cards.forEach(el=>{ const lid=el.dataset.line; let timer=null, writing=false, pending=false;
    const body=()=>({note:el.querySelector('.note').value,...(edited[lid]?{printed:el.querySelector('.printed').value,printed_edited:true}:{})});
    async function flush(){ if(writing){ pending=true; return; } const b=body(); const key=JSON.stringify(b); if(key===last[lid]) return;
      writing=true; setStatus(el,'saving…',false); const doc={...b, updated:new Date().toISOString().slice(0,16).replace('T',' ')};
      try{ await db.doc('notes/'+lid).set(doc,{merge:true}); last[lid]=key; setStatus(el,'saved '+doc.updated,true); } catch(e){ setStatus(el,'not saved ('+(e&&e.code||'error')+') — keep typing, it retries',false); }
      writing=false; if(pending){ pending=false; flush(); } }
    const onInput=()=>{ setStatus(el,'editing…',false); clearTimeout(timer); timer=setTimeout(flush,900); };
    el.querySelector('.printed').addEventListener('input',()=>{edited[lid]=true;});
    for(const k of ['.printed','.note']){ el.querySelector(k).addEventListener('input',onInput); el.querySelector(k).addEventListener('blur',()=>{clearTimeout(timer);flush();}); }
  });
})();
</script>'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--candidates'); ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=0); ap.add_argument('--title', default='Polytonic Spell Check Status'); ap.add_argument('--intro', default='')
    ap.add_argument('--shape-model', default='docs/records/labelfix/markshape_model.json'); ap.add_argument('--notes', default='docs/records/labelfix/owner_line_notes_20261016.jsonl')
    ap.add_argument('--all-lines', action='store_true', help='include every candidate line, not only those where Google differs from the reference')
    ap.add_argument('--lines', help='JSONL objects with line_id; preserves requested order')
    ap.add_argument('--metrics', help='S2 summary JSON for the iteration header')
    ap.add_argument('--print-truth', default='docs/records/labelfix/spellcheck/print_truth_s0.json')
    ap.add_argument('--evidence', help='frozen whole-line detector JSONL.gz used for scoring')
    ap.add_argument('--expectations', help='v8-pinned owner expectation JSONL')
    a = ap.parse_args()
    model = M.load_model(a.shape_model)
    owner = {}
    if os.path.exists(a.notes):
        for l in open(a.notes): r = json.loads(l); owner[r['line_id']] = r
    line_map = {l['line_id']:l for l in load_three_way(0)}
    G={lid:nfc(l['google']) for lid,l in line_map.items()};H={lid:nfc(l['human']) for lid,l in line_map.items()}
    frozen={};expectations={}
    if a.evidence:
        import gzip
        with gzip.open(a.evidence,'rt') as f:
            frozen={r['line_id']:r for x in f if (r:=json.loads(x))}
    if a.expectations:
        for x in open(a.expectations):
            e=json.loads(x);expectations.setdefault(e['line_id'],[]).append(e)
    aligns = load_alignments(Path('.cache/labelfix/align_s0.jsonl'))
    truth = json.loads(Path(a.print_truth).read_text())
    rows = [json.loads(l) for l in open(a.candidates)] if a.candidates else []
    if a.lines:
        existing = {r['line_id']:r for r in rows}
        rows = [existing.get(lid,dict(line_id=lid,crop_path=line_map[lid]['crop'],google_token='',corrected_token='',human_token='',decision={}))
                for x in open(a.lines) if (lid := json.loads(x)['line_id'])]
    if not a.all_lines and not a.lines:

        rows = [r for r in rows if nfc(r['google_token']) != nfc(r.get('human_token') or '') and r.get('outcome') in ('correct', 'both_wrong')]
    seen, cards = set(), []
    previous_section=None
    for r in rows:
        lid = r['line_id']
        if lid in seen: continue
        seen.add(lid)
        if a.limit and len(cards) >= a.limit: break
        slots, img = detect(r['crop_path'], model, line_map[lid], aligns.get(crop_key(r['crop_path'])), truth, frozen.get(lid))
        g = G.get(lid, ''); hm = H.get(lid, ''); pr = printed_line(line_map[lid], truth)
        det = [f"{i+1}:{cls_sym(s['cls']) if not s['cls'].startswith('?') else s['cls']}" for i, s in enumerate(slots) if s['cls'] != 'none']
        d = r['decision']; gt = nfc(r['google_token']); ct = nfc(r['corrected_token']); ht = nfc(r.get('human_token') or ''); acc = d.get('accept') or d.get('ink_decisive')
        section='1 · Your 33 noted lines' if lid in owner else '2 · Fixed held-out sample and changed detections'
        heading=f'<h2>{section}</h2>' if a.expectations and section!=previous_section else ''
        previous_section=section
        ee=expectations.get(lid,[])
        status=''
        if a.expectations and lid in owner:
            parts=[]
            for e in ee:
                label=f"slot {e['v8_slot']} (v8) = {e.get('mapped_slot') or 'UNKNOWN'} (now)"
                parts.append(html.escape(label+': '+('fixed' if e['fixed'] else 'not fixed')+'; '+e.get('cause','')))
            status=f'<div class="row"><b>your notes: {sum(e["fixed"] for e in ee)}/{len(ee)} fixed</b></div><div class="why">'+('<br>'.join(parts) if parts else 'No per-slot expectation in your note.')+'</div>'
        cards.append(heading+f'''<div class="card" data-line="{lid}"><img src="{img}" alt="line with detected marks">{status}<div class="seq"><div><b>Image, detached marks by letter slot</b>:<br>{seq_html(det) if det else '<i>no detached marks</i>'}</div>
<div><b>Google</b>: {seq_html(text_marks(g))}</div><div><b>Human (test reference)</b>: {seq_html(text_marks(hm))}</div>{('<div><b>Printed (adjudicated / agreement; UNKNOWN excluded)</b>: ' + seq_html(text_marks(pr)) + '</div>') if pr else ''}</div>
<table class="w"><tr><th>Google</th><td>{html.escape(g).replace(html.escape(gt), '<mark>' + html.escape(gt) + '</mark>', 1)}</td></tr><tr><th>Human</th><td>{html.escape(hm)}</td></tr>{('<tr><th>Printed</th><td>' + html.escape(pr) + '</td></tr>') if pr else ''}<tr><th>Tool</th><td>{html.escape(ct)} <span class="pill {'ok' if acc else 'bad'}">{'CORRECTED' if acc else 'NOT corrected'}</span> <span class="pill">{html.escape(d.get('rule') or '')}</span></td></tr></table>
<div class="row"><span class="why">{html.escape(lid)} · {html.escape(d.get('reason', '')[:140])}</span></div>
<div class="notes" data-line="{lid}"><label>What is printed (whole line; prefilled with Google's label)</label><textarea class="printed" rows="2">{html.escape(g)}</textarea><label>Note</label><textarea class="note" rows="2">{html.escape(owner.get(lid, {}).get('note', ''))}</textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>''')
    intro = a.intro or f'{len(cards)} held-out lines · full line crop with slot numbers; detached marks boxed (green above / blue below) and named (´ ` ῀ ᾿ ῾, subscript, ¨, ? = unnamed); ascender ink shown as grey dashes, not named; then the detected sequence by slot and the Google / human / printed marks per letter (◌ = letter without marks). Human text is a test reference only; the printed line wins.'
    if a.metrics:
        met = json.loads(Path(a.metrics).read_text())
        b, z = met['before']['total'], met['after']['total']
        intro = (f"Iteration {met['iteration']} · held-out mark P {b['precision']:.1%} → {z['precision']:.1%}; R {b['recall']:.1%} → {z['recall']:.1%}. "
                 + met.get('engine_header','') + ' ' + intro)
        intro += ' '+met.get('regression_header','')
    page = [CSS, f'<main><h1>{html.escape(a.title)}</h1><p class="meta">{html.escape(intro)}</p>'] + cards + ['</main>', SCRIPT]
    open(a.out, 'w').write('\n'.join(page)); print('cards', len(cards), 'bytes', os.path.getsize(a.out))

if __name__ == '__main__': main()
