"""Build the owner's review sheet (crops, letter slots, detected marks, texts, autosaving notes).

Usage: .venv/bin/python scripts/labelfix/sheet_build.py --candidates docs/labelfix/validation_candidates_s0_strict.jsonl \
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

def cls_sym(c): return 'unnamed' if c == 'unnamed' else (''.join(SYM.get(p, p) for p in c.split('+')) if c != 'none' else '·')
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


from greekocr.labelfix.spellink import locate as _locate
from greekocr.labelfix.candidates import pair_tokens as _pair
from greekocr.labelfix.ctc_align import transfer_alignment as _transfer
from greekocr.labelfix.text import MARK_BEARERS as _MB, clusters as _clusters, tokenize as _tok
_MK = {'psili': '\u0313', 'dasia': '\u0314', 'dialytika': '\u0308', 'acute': '\u0301', 'grave': '\u0300', 'circumflex': '\u0342', 'subscript': '\u0345'}
def ours_line(line, al, slots):
    """Google's letters, each vowel carrying the marks our detector read at its slot (Google's marks kept where we read none)."""
    if al is None or not slots: return line['google']
    if nfd(al.prediction) != line['model']: al = _transfer(line['model'], al)
    gm = {g.index: m for g, m in _pair(line['google'], line['model'])}
    out = []
    for g in _tok(line['google']):
        if not g.core: out.append(g.text); continue
        w = []
        for j, c in enumerate(_clusters(g.core)):
            mk = None
            if c.base in _MB:
                loc = _locate(g, gm.get(g.index), al, j)
                if loc is not None:
                    b0, b1 = loc[-2:]
                    ovs = [max(0, min(sl['x1'], b1) - max(sl['x0'], b0)) for sl in slots]
                    k = max(range(len(slots)), key=lambda i: ovs[i])
                    cls = slots[k]['cls']
                    if ovs[k] > 0 and cls != 'unnamed':
                        mk = '' if cls == 'none' else ''.join(_MK.get(x, '') for x in cls.split('+'))
            w.append(c.base + (c.marks if mk is None else mk))
        out.append(g.lead + ''.join(w) + g.trail)
    return ' '.join(out)

_ENG = {}
def _load_engine(path='docs/labelfix/spellcheck/S3_engine/words_s0.jsonl'):
    for l in open(path, encoding='utf-8'):
        r = json.loads(l)
        if r['decision'].get('accept'):
            _ENG[(r['line_id'], r['word_index'])] = r.get('corrected_token') or r['decision'].get('proposal')
def reconstructed(line):
    """Our reconstruction = Google's line with the corrections our tool accepts (ink-confirmed); everything else stays Google's."""
    if not _ENG: _load_engine()
    toks = _tok(line['google']); out = []; changed = 0
    for t in toks:
        c = _ENG.get((line['line_id'], t.index))
        if c: out.append(c); changed += 1
        else: out.append(t.text)
    return ' '.join(out), changed

_VOW = set('αεηιουωΑΕΗΙΟΥΩρΡ')
def independent_line(line, al, slots):
    """Our own reading, independent of Google: letters from our recogniser, every mark from our detector at that letter's slot.
    A letter whose slot has no detected mark is written bare; an unnamed detection is shown as a marked-but-unnamed letter."""
    text = nfd(line['model'])
    if al is None:
        return html.escape(nfc(''.join(ch for ch in text if not ud.category(ch).startswith('M')))), ''
    if nfd(al.prediction) != text: al = _transfer(text, al)
    base_idx = [i for i, ch in enumerate(text) if not ud.category(ch).startswith('M')]
    owner = {}
    for i in base_idx:
        ch = text[i]
        if not ch.isalpha() or not slots: continue
        x0, x1 = al.window(i, i + 1)
        ovs = [max(0, min(sl['x1'], x1) - max(sl['x0'], x0)) for sl in slots]
        k = max(range(len(slots)), key=lambda j: ovs[j])
        if ovs[k] > 0: owner.setdefault(k, []).append(i)
    marks_at = {}
    for k, idxs in owner.items():
        cls = slots[k]['cls']
        if cls == 'none': continue
        tgt = next((i for i in idxs if text[i] in _VOW), idxs[0])
        marks_at[tgt] = cls
    out = []
    for i in base_idx:
        ch = text[i]; cls = marks_at.get(i)
        if cls is None: out.append(html.escape(nfc(ch))); continue
        if cls == 'unnamed':
            out.append(f'<span class="un" title="mark detected, not named">{html.escape(ch)}</span>'); continue
        parts = cls.split('+')
        mk = ''.join(_MK.get(x, '') for x in parts if x != 'apostrophe')
        out.append(html.escape(nfc(ch + mk)) + ('’' if 'apostrophe' in parts else ''))
    plain = ''.join(re.sub(r'<[^>]+>', '', o) for o in out)
    return ''.join(out), plain

def detect(path, model, line=None, al=None, truth=None):
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
        ev = I.mark_evidence(ci, c.x0, c.x1, base_letter=mapping[slot_index]['base'] if mapping else None)
        det_above = [b for b in ev.above if (b.x0,b.y0,b.x1,b.y1) not in apost_boxes]; att_above = ev.diagnostics
        if det_above or ev.below:
            ev2 = I.MarkEvidence(above=det_above, below=list(ev.below), window=ev.window, xh=ev.xh, meanline=ev.meanline, baseline=ev.baseline,
                                 body=ev.body, body_source=ev.body_source, n_letters_in_span=ev.n_letters_in_span, neighbour_marks=ev.neighbour_marks,
                                 clipped_top=ev.clipped_top, clipped_bottom=ev.clipped_bottom)
            cl, p, _ = model.predict(M.features(ev2)); desc = cl if p >= 0.5 else 'unnamed'
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
        d.text((sl['x0'] * s, Hh * s - 12 * s), str(i + 1), fill=(120, 120, 120), font=font)
    if big.size[0] > 1000: big = big.resize((1000, int(big.size[1] * 1000 / big.size[0])), Image.LANCZOS)
    return slots, uri(big)

CSS = '''<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&display=swap"><title>Polytonic Spell Check Status</title>
<style>
:root{--bg:#f7f5f0;--fg:#1d1a16;--muted:#6b645a;--line:#d9d3c8;--panel:#fffdf9;--ok:#2e7d4f;--warn:#b26a00;--bad:#a93a2f;--soft:#ece7dd;--hl:#fff1a8;--body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;--display:"Source Serif 4",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;--panel:#201f24;--ok:#7fc39a;--warn:#e2a64a;--bad:#e2796c;--soft:#2a282e;--hl:#5a4d12;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;--panel:#201f24;--ok:#7fc39a;--warn:#e2a64a;--bad:#e2796c;--soft:#2a282e;--hl:#5a4d12;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.45;padding-block:24px 56px;padding-inline:16px}
main{max-width:980px;margin:0 auto;min-width:0} h1{font-family:var(--display);font-size:1.9rem;margin:0 0 4px} h2{font-family:var(--display);font-size:1.3rem;margin:34px 0 8px}
p{max-width:72ch;margin:0 0 10px} .meta{color:var(--muted);font-size:.9rem}
.card{background:var(--panel);border:1px solid var(--line);padding:10px;margin:12px 0;min-width:0} .card img{display:block;width:100%;max-width:100%;height:auto;border:1px solid var(--line);background:#fff}
table.w{width:100%;border-collapse:collapse;margin-top:8px;font-size:1.15rem;font-family:"Noto Serif","GFS Didot","Times New Roman",serif}
table.w th{width:92px;text-align:left;font-family:var(--body);font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding:3px 6px 3px 0;vertical-align:top} table.w td{padding:3px 0;word-break:break-word}
mark{background:var(--hl);color:inherit;padding:0 2px} .row{margin-top:6px;font-size:.82rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pill{display:inline-block;font-size:.7rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:1px 7px;border-radius:999px;border:1px solid var(--line);color:var(--fg)} .ok{color:var(--ok);border-color:var(--ok)} .bad{color:var(--bad);border-color:var(--bad)} .warn{color:var(--warn);border-color:var(--warn)}
.why{font-family:"IBM Plex Mono",Menlo,monospace;font-size:.78rem} .seq{font-size:.95rem;line-height:1.7;margin:8px 0;display:grid;gap:4px;font-family:"Source Serif 4",Georgia,serif} .seq b{font-family:var(--body);font-size:.74rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.notes{margin-top:10px;border-top:1px dashed var(--line);padding-top:8px;display:grid;gap:4px}.notes label{font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}.notes textarea{width:100%;box-sizing:border-box;font-family:"Source Serif 4",Georgia,serif;font-size:1rem;padding:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}.nrow{display:flex;gap:10px;align-items:center}.status{font-size:.8rem;color:var(--muted)}.notes.saved .status{color:var(--ok)}
.un{text-decoration:underline dotted var(--bad);text-underline-offset:3px}.lid{font-family:"IBM Plex Mono",Menlo,monospace;font-size:.95rem;font-weight:600;margin:0 0 6px}</style>'''

SCRIPT = '''<script>
(async function(){
  const boxes=[...document.querySelectorAll('.notes[data-line]')];
  const st=(el,t,ok)=>{const s=el.querySelector('.status');s.textContent=t;el.classList.toggle('saved',!!ok)};
  let db=null; try{ db=await (window.claude&&window.claude.use?window.claude.use('db'):Promise.resolve(null)); }catch(e){ db=null }
  if(!db){ boxes.forEach(el=>st(el,'notes save in the signed-in view',false)); return; }
  const last={};
  try{ const snap=await db.collection('notes').limit(1000).get();
    snap.docs.forEach(d=>{ if(!d.exists) return; const el=document.querySelector('.notes[data-line="'+d.id+'"]'); if(!el) return; const x=d.data()||{};
      if(typeof x.note==='string'){ el.querySelector('.note').value=x.note; last[d.id]=x.note; st(el,'saved '+(x.updated||''),true); } });
  }catch(e){ boxes.forEach(el=>st(el,'could not load notes',false)); }
  boxes.forEach(el=>{ const id=el.dataset.line, ta=el.querySelector('.note'); let t=null, busy=false, again=false;
    async function flush(){ if(busy){again=true;return;} const v=ta.value; if(v===(last[id]??'')) return; busy=true; st(el,'saving…',false);
      const doc={note:v, updated:new Date().toISOString().slice(0,16).replace('T',' ')};
      try{ await db.doc('notes/'+id).set(doc,{merge:true}); last[id]=v; st(el,'saved '+doc.updated,true); }catch(e){ st(el,'not saved, keep typing to retry',false); }
      busy=false; if(again){again=false;flush();} }
    ta.addEventListener('input',()=>{st(el,'editing…',false);clearTimeout(t);t=setTimeout(flush,900);});
    ta.addEventListener('blur',()=>{clearTimeout(t);flush();});
  });
})();
</script>'''

from greekocr.labelfix import reading as R
R1 = {}
def _kinds(parts):
    return {'breathing' if x in ('psili','dasia') else 'accent' if x in ('acute','grave','circumflex') else x for x in parts}
def combine(lid, rd):
    """Presence from the detector, names from R1-A where both agree on the mark kinds; otherwise HOLD (R1's reading shown, flagged)."""
    for s in rd.slots:
        p = R1.get((lid, s['start']))
        if p is None or s.get('component') is None: continue
        r1 = [x for x in p['cls'].split('+') if x != 'none']
        det = [x for x in s.get('parts', ())]
        s['hold'] = _kinds(r1) != _kinds(det)
        s['parts'] = r1
    text = R.render_reading(rd.text if False else LINE_TEXT[lid], rd.slots)
    lr = R.LineReading(text, rd.slots, rd.unnamed)
    lr, removed = R.apply_constraints(lr)
    return lr, removed
LINE_TEXT = {}
def detect_s4(path, model, line, al):
    """Boxes and our line from the S4 reader: letters from our recogniser, every mark from our detector (no Google)."""
    im = Image.open(path); ci = I.analyse(im)
    letters = sorted([c for c in ci.components if c.role == 'letter'], key=lambda c: c.x0)
    ours = html.escape(nfc(''.join(ch for ch in nfd(line['model']) if not ud.category(ch).startswith('M')))); plain = ours
    boxes_above, boxes_below, quotes = [], [], []
    if al is not None:
        rd = R.read_ink(ci, line['model'], al, model)
        if R1:
            LINE_TEXT[line['line_id']] = line['model']; rd, _removed = combine(line['line_id'], rd)
        located = [s for s in rd.slots if s['component'] is not None]
        apost = I.apostrophe_candidates(ci, [(s['component'], s['base'], s['word_final']) for s in located])
        for s in located:
            ev = s['evidence']; boxes_above += ev.above; boxes_below += ev.below
        for bs in apost.values(): boxes_above += bs
        quotes = rd.opening_quotes
        by = {s['start']: s for s in rd.slots}; out = []
        for cl in _clusters(nfd(line['model'])):
            if cl.base in R.ELISION: continue
            sl = by.get(cl.start)
            if sl is None: out.append(html.escape(cl.base)); continue
            t = nfc(cl.base + ''.join(R.MARKS[x] for x in sl.get('parts', ()) if x in R.MARKS))
            out.append(f'<span class="un" title="reader and detector disagree">{html.escape(t)}</span>' if sl.get('hold') else f'<span class="un" title="mark detected, not named">{html.escape(t)}</span>' if (sl.get('unnamed') and not R1) else html.escape(t))
            if sl.get('apostrophe'): out.append('’')
        ours = ''.join(out)
        if rd.text.startswith('“'): ours = '“' + ours.lstrip('“”«»„&quot; ')
        plain = re.sub(r'<[^>]+>', '', ours)
    W, Hh = im.size; s = 2 if W < 700 else 1; big = im.convert('RGB').resize((W * s, Hh * s), Image.NEAREST); d = ImageDraw.Draw(big)
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 11 * s)
    except Exception: font = None
    for b in boxes_above: d.rectangle([b.x0 * s, b.y0 * s, b.x1 * s, b.y1 * s], outline=(30, 140, 60), width=2)
    for b in boxes_below: d.rectangle([b.x0 * s, b.y0 * s, b.x1 * s, b.y1 * s], outline=(40, 80, 200), width=2)
    for q in quotes:
        x0, y0, x1, y1 = q['bbox']; d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(30, 140, 60), width=2)
    for i, c in enumerate(letters): d.text((c.x0 * s, Hh * s - 12 * s), str(i + 1), fill=(120, 120, 120), font=font)
    if big.size[0] > 1000: big = big.resize((1000, int(big.size[1] * 1000 / big.size[0])), Image.LANCZOS)
    boxes = ([dict(kind='above', bbox=[b.x0, b.y0, b.x1, b.y1]) for b in boxes_above]
             + [dict(kind='below', bbox=[b.x0, b.y0, b.x1, b.y1]) for b in boxes_below]
             + [dict(kind='quote', bbox=list(q['bbox'])) for q in quotes])
    letters_x = [[c.x0, c.x1] for c in letters]
    return ours, plain, uri(big), dict(reading=plain, boxes=boxes, letters=letters_x)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--candidates'); ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=0); ap.add_argument('--title', default='Polytonic Spell Check Status'); ap.add_argument('--intro', default='')
    ap.add_argument('--shape-model', default='docs/labelfix/markshape_model.json'); ap.add_argument('--notes', default='docs/labelfix/owner_line_notes_20261016.jsonl')
    ap.add_argument('--all-lines', action='store_true', help='include every candidate line, not only those where Google differs from the reference')
    ap.add_argument('--lines', help='JSONL objects with line_id; preserves requested order')
    ap.add_argument('--r1', nargs='*', default=[], help='R1 prediction jsonl files (line_id, start, cls): combined reading')
    ap.add_argument('--boxes-out', help='JSON sidecar: line_id -> reading, mark boxes, letter x-ranges (regression diff)')
    ap.add_argument('--metrics', help='S2 summary JSON for the iteration header')
    ap.add_argument('--print-truth', default='docs/labelfix/spellcheck/print_truth_s0.json')
    a = ap.parse_args()
    model = M.load_model(a.shape_model)
    for f in a.r1:
        for l in open(f):
            q = json.loads(l); R1[(q['line_id'], q['start'])] = q
    G = {json.loads(l)['line_id']: nfc(json.loads(l)['gt']) for l in open(P + 'full_s0_v2_test.jsonl')}
    H = {}
    for l in open(P + 'full_s0_wikisource_human.jsonl'):
        r = json.loads(l); H[r['line_id'].replace('-human', '')] = nfc(r['gt'])
    owner = {}
    if os.path.exists(a.notes):
        for l in open(a.notes): r = json.loads(l); owner[r['line_id']] = r
    line_map = {l['line_id']:l for l in load_three_way(0)}
    aligns = load_alignments(Path('.cache/labelfix/align_s0.jsonl'))
    truth = json.loads(Path(a.print_truth).read_text())
    rows = [json.loads(l) for l in open(a.candidates)] if a.candidates else []
    if a.lines:
        existing = {r['line_id']:r for r in rows}
        rows = [existing.get(lid,dict(line_id=lid,crop_path=line_map[lid]['crop'],google_token='',corrected_token='',human_token='',decision={}))
                for x in open(a.lines) if (lid := json.loads(x)['line_id'])]
    if not a.all_lines and not a.lines:

        rows = [r for r in rows if nfc(r['google_token']) != nfc(r.get('human_token') or '') and r.get('outcome') in ('correct', 'both_wrong')]
    seen, cards, sidecar = set(), [], {}
    for r in rows:
        lid = r['line_id']
        if lid in seen: continue
        seen.add(lid)
        if a.limit and len(cards) >= a.limit: break
        ours_html, ours_plain, img, side = detect_s4(r['crop_path'], model, line_map[lid], aligns.get(crop_key(r['crop_path'])))
        sidecar[lid] = side
        g = G.get(lid, ''); hm = H.get(lid, ''); pr = printed_line(line_map[lid], truth)
        d = r['decision']; gt = nfc(r['google_token']); ct = nfc(r['corrected_token']); ht = nfc(r.get('human_token') or ''); acc = d.get('accept') or d.get('ink_decisive')
        nchg = (lambda t: ''.join(ch for ch in nfd(t) if ch.isalpha() or ud.category(ch).startswith('M')))(html.unescape(ours_plain)) != (lambda t: ''.join(ch for ch in nfd(t) if ch.isalpha() or ud.category(ch).startswith('M')))(g)
        cards.append(f'''<div class="card" data-line="{lid}"><div class="lid">{html.escape(lid)}</div><img src="{img}" alt="line with detected marks">
<table class="w"><tr><th>Google</th><td>{html.escape(g)}</td></tr><tr><th>Ours</th><td>{ours_html}</td></tr></table>
<div class="row"><span class="pill {'warn' if nchg else 'ok'}">{'differs from Google' if nchg else 'same as Google'}</span></div>
<div class="notes" data-line="{lid}"><label>Note</label><textarea class="note" rows="2">{html.escape(owner.get(lid, {}).get('note', ''))}</textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>''')
    intro = a.intro or f'{len(cards)} held-out lines · full line crop with slot numbers; marks we detect boxed (green above, blue below; grey dashes = letter ink we do not count as a mark); then Google’s line and ours, read independently of Google: letters from our recogniser, every mark from our detector (a letter with a dotted underline carries a mark we detect but cannot name). No note = our line is right.'
    if a.metrics:
        met = json.loads(Path(a.metrics).read_text())
        b, z = met['before']['total'], met['after']['total']
        intro = (f"Iteration {met['iteration']} · held-out mark P {b['precision']:.1%} → {z['precision']:.1%}; R {b['recall']:.1%} → {z['recall']:.1%}. "
                 + met.get('engine_header','') + ' ' + intro)
    page = [CSS, f'<main><h1>{html.escape(a.title)}</h1><p class="meta">{html.escape(intro)}</p>'] + cards + ['</main>', SCRIPT]
    if a.boxes_out: json.dump(sidecar, open(a.boxes_out, 'w'), ensure_ascii=False)
    open(a.out, 'w').write('\n'.join(page)); print('cards', len(cards), 'bytes', os.path.getsize(a.out))

if __name__ == '__main__': main()
