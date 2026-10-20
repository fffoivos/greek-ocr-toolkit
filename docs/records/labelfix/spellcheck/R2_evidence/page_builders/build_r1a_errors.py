"""Owner adjudication sheet: every held-out slot where reader arm A disagrees with the frozen S4 slot truth.
Same mapping as r1_error_types (A_mapped_lines of score_3678928_K1c_vsS6, held-out only, Google marks by word pairing)."""
import gzip, json, html, io, base64, sys, os, unicodedata as ud
from collections import Counter, defaultdict
from PIL import Image, ImageDraw
sys.path.insert(0, os.getcwd())
import importlib.util
_sp = importlib.util.spec_from_file_location('r1et', '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/r1_error_types.py')
_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m)
google_marks, atomic, kind, G = _m.google_marks, _m.atomic, _m.kind, _m.G
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd, tokenize
S = sys.argv[1]
D = 'artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz'
ADJ = json.load(open('docs/labelfix/spellcheck/print_truth_s0.json'))
nfc = lambda s: ud.normalize('NFC', s or '')
NAME = {'psili': 'smooth breathing', 'dasia': 'rough breathing', 'acute': 'acute', 'grave': 'grave', 'circumflex': 'circumflex',
        'subscript': 'iota subscript', 'dialytika': 'diaeresis'}
def names(ms): return ' + '.join(NAME[n] for _, n in sorted(ms)) or 'no mark'
def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def word_of(text, idx):
    ts = tokenize(text); return ts[idx].text if idx < len(ts) else ''
cards = defaultdict(list); new_errors = 0; unfixed = 0
for l in gzip.open(D, 'rt'):
    r = json.loads(l)
    if r.get('dev'): continue
    lid = r['line_id']; g_line = G[lid]; gm = google_marks(g_line, nfd(r['recogniser_text']))
    rd = {g.index: m for g, m in pair_tokens(g_line, nfd(r['reading']))}
    wl = defaultdict(int)
    for s in r['slots']: wl[s.get('word')] += 1
    im = None
    for s in r['slots']:
        if s.get('truth') is None: continue
        T = atomic(s['truth']); O = atomic(s.get('detected', []))
        if O == T: continue
        paired = s.get('recogniser_start') in gm; Gm = gm.get(s.get('recogniser_start'))
        if paired and Gm != T:
            sec = 'unfixed'; unfixed += 1; sub = kind(s, T, Gm, wl[s.get('word')])
        else:
            sec = 'false' if not T and O else ('missed' if T and not O else 'misnamed'); sub = None
            if paired: new_errors += 1
        key = f"{lid}|{s['word']}"
        prov = ('print-checked by two blind readers' + (f" ({ADJ[key]['status']})" if ADJ[key].get('status') else '')) if key in ADJ \
               else 'Google, human text and recogniser agree'
        if key in ADJ: truth_word = ADJ[key]['printed'] or ''
        else:
            gh = {g.index: h for g, h in pair_tokens(g_line, r.get('human') or '')}
            truth_word = word_of(g_line, s['word'])  # three-way agreement: Google's word equals the printed word
        if im is None: im = Image.open(r['crop']).convert('RGB')
        W, H = im.size; x0, y0, x1, y1 = s['bbox']
        line = im.copy(); d = ImageDraw.Draw(line); d.rectangle([x0 - 2, 0, x1 + 2, H - 1], outline=(200, 40, 40), width=2)
        ws = [t['bbox'] for t in r['slots'] if t.get('word') == s['word'] and t.get('bbox')]
        wx0 = max(0, min(b[0] for b in ws) - 6); wx1 = min(W, max(b[2] for b in ws) + 6)
        word = im.crop((wx0, 0, wx1, H)); word = word.resize((word.width * 3, H * 3), Image.LANCZOS)
        pad = max(6, (x1 - x0) // 2); vx0 = max(0, x0 - pad); vx1 = min(W, x1 + pad)
        vow = im.crop((vx0, 0, vx1, H)); vow = vow.resize((vow.width * 8, H * 8), Image.NEAREST)
        gword = word_of(g_line, s['word']); aword = rd[s['word']].text if s['word'] in rd and rd[s['word']] else ''
        cards[sec].append(dict(lid=lid, slot=s['slot'], base=s['base'], T=T, O=O, G=Gm, paired=paired, sub=sub, prov=prov,
            truth_word=nfc(truth_word), gword=nfc(gword), aword=nfc(aword), line=uri(line), word=uri(word), vow=uri(vow), gline=nfc(g_line)))
print('unfixed', unfixed, 'new errors (Google right)', new_errors, {k: len(v) for k, v in cards.items()})
assert new_errors == 24 and unfixed == 14, (new_errors, unfixed)
src = open(S + '/snap6/build_owner.py').read()
CSS = src.split("CSS = '''", 1)[1].split("'''", 1)[0].replace('<title>Polytonic Spell Check Status</title>', '<title>Reader Errors Held-out</title>')
CSS = CSS.replace('</style>', '.zoomrow{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;margin-top:8px}.zoom{width:auto;max-width:100%;height:auto;max-height:240px;border:1px solid var(--line);background:#fff}'
                  '.pr{display:flex;gap:8px;align-items:center}.pr input{flex:1;min-width:0;font-family:"Noto Serif","GFS Didot",serif;font-size:1.1rem;padding:4px 6px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}</style>')
SCRIPT = '''<script>
(async function(){
  const boxes=[...document.querySelectorAll('.notes[data-id]')];
  const st=(el,t,ok)=>{const s=el.querySelector('.status');s.textContent=t;el.classList.toggle('saved',!!ok)};
  let db=null; try{ db=await (window.claude&&window.claude.use?window.claude.use('db'):Promise.resolve(null)); }catch(e){ db=null }
  if(!db){ boxes.forEach(el=>st(el,'notes save in the signed-in view',false)); return; }
  const last={};
  try{ const snap=await db.collection('notes').limit(1000).get();
    snap.docs.forEach(d=>{ if(!d.exists) return; const el=document.querySelector('.notes[data-id="'+d.id+'"]'); if(!el) return; const x=d.data()||{};
      if(typeof x.note==='string') el.querySelector('.note').value=x.note;
      if(typeof x.printed==='string') el.querySelector('.printed').value=x.printed;
      last[d.id]=JSON.stringify([x.note||'',x.printed||'']); st(el,'saved '+(x.updated||''),true); });
  }catch(e){ boxes.forEach(el=>st(el,'could not load notes',false)); }
  boxes.forEach(el=>{ const id=el.dataset.id, ta=el.querySelector('.note'), pr=el.querySelector('.printed'); let t=null, busy=false, again=false;
    async function flush(){ if(busy){again=true;return;} const v=JSON.stringify([ta.value,pr.value]);
      if(v===(last[id]??JSON.stringify(['',pr.defaultValue]))) return; busy=true; st(el,'saving…',false);
      const doc={note:ta.value, printed:pr.value, line_id:el.dataset.line, slot:el.dataset.slot, updated:new Date().toISOString().slice(0,16).replace('T',' ')};
      try{ await db.doc('notes/'+id).set(doc,{merge:true}); last[id]=v; st(el,'saved '+doc.updated,true); }catch(e){ st(el,'not saved, keep typing to retry',false); }
      busy=false; if(again){again=false;flush();} }
    [ta,pr].forEach(x=>{ x.addEventListener('input',()=>{st(el,'editing…',false);clearTimeout(t);t=setTimeout(flush,900);}); x.addEventListener('blur',()=>{clearTimeout(t);flush();}); });
  });
})();
</script>'''
def card(c):
    did = f"{c['lid']}:s{c['slot']}"
    tags = [f'<span class="pill bad">{"Google error left unfixed · " + c["sub"] if c["sub"] else ("false mark" if not c["T"] else ("missed mark" if not c["O"] else "misnamed"))}</span>',
            f'<span class="pill">{html.escape(c["prov"])}</span>']
    if c['paired'] and c['G'] == c['T']: tags.append('<span class="pill warn">new error, Google right</span>')
    if not c['paired']: tags.append('<span class="pill">Google word not paired</span>')
    return f'''<div class="card"><div class="lid">{html.escape(c["lid"])} · slot {c["slot"]} ({html.escape(c["base"])})</div><img src="{c["line"]}" alt="full line, letter outlined">
<div class="zoomrow"><img class="zoom" src="{c["word"]}" alt="word zoom 3x"><img class="zoom" src="{c["vow"]}" alt="letter zoom 8x"></div>
<table class="w"><tr><th>Google</th><td>{html.escape(c["gword"])}</td></tr><tr><th>Truth</th><td>{html.escape(c["truth_word"])} <span class="muted">· {html.escape(names(c["T"]))}</span></td></tr>
<tr><th>Reader</th><td>{html.escape(c["aword"])} <span class="muted">· {html.escape(names(c["O"]))}</span></td></tr></table>
<div class="row">{"".join(tags)}</div>
<div class="notes" data-id="{did}" data-line="{c["lid"]}" data-slot="{c["slot"]}"><div class="pr"><label for="p-{did}">Printed</label><input class="printed" id="p-{did}" value="{html.escape(c["truth_word"])}"></div>
<label for="n-{did}">Note</label><textarea class="note" id="n-{did}" rows="2"></textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>'''
H = [('unfixed', 'Google errors the reader left unfixed'), ('false', 'False mark: the reader names a mark where the truth has none'),
     ('missed', 'Missed mark: the truth has a mark, the reader none'), ('misnamed', 'Misnamed: both have a mark, different names')]
tot = sum(len(v) for v in cards.values())
intro = (f'{tot} letters on the 666 held-out test lines where our reader disagrees with the current truth. Per card: the full line with the '
         'letter outlined in red, the word at 3×, the letter at 8×; Google’s word, the truth word and our reader’s word, with the marks each '
         'gives this letter. The tag says where the truth came from. “Printed” is prefilled with the current truth: correct it if the '
         'print shows something else. No note = the truth is right.')
page = [CSS, f'<main><h1>Reader Errors Held-out</h1><p class="meta">{html.escape(intro)}</p>']
for k, h in H:
    page.append(f'<h2>{h} ({len(cards[k])})</h2>'); page += [card(c) for c in cards[k]]
page += ['</main>', SCRIPT]
open(S + '/reader_errors_heldout.html', 'w').write('\n'.join(page))
print('bytes', os.path.getsize(S + '/reader_errors_heldout.html'))
exp = [dict(section=k, line_id=c['lid'], slot=c['slot'], base=c['base'], google_word=c['gword'], truth_word=c['truth_word'], reader_word=c['aword'],
            truth_marks=sorted(n for _, n in c['T']), reader_marks=sorted(n for _, n in c['O']), google_marks=sorted(n for _, n in c['G']) if c['G'] is not None else None,
            google_error_kind=c['sub'], new_error_google_right=bool(c['paired'] and c['G'] == c['T']), truth_provenance=c['prov'], db_id=f"{c['lid']}:s{c['slot']}")
       for k, _ in H for c in cards[k]]
json.dump(exp, open(S + '/reader_errors_39.json', 'w'), ensure_ascii=False, indent=1)
