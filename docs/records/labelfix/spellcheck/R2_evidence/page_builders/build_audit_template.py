"""Audit100 results through the owner template (snap6/build_owner.py card format): line crop with slot numbers and the
release's own saved detections boxed (green above, blue below), Google line, Ours (released label), pill, one note."""
import gzip, json, hashlib, html, io, base64, sys, unicodedata as ud
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, sys.argv[1] + '/snap6')
import importlib.util
spec = importlib.util.spec_from_file_location('tpl', sys.argv[1] + '/snap6/build_owner.py')
src = open(sys.argv[1] + '/snap6/build_owner.py').read()
CSS = src.split("CSS = '''", 1)[1].split("'''", 1)[0]; SCRIPT = src.split("SCRIPT = '''", 1)[1].split("'''", 1)[0]
EXTRA_JS = '''<script>
(function(){
  const Z=3;
  document.querySelectorAll('.zw').forEach(w=>{
    const img=w.querySelector('img'), lens=w.querySelector('.lens');
    function show(e){ const r=img.getBoundingClientRect(); const x=e.clientX-r.left, y=e.clientY-r.top;
      if(x<0||y<0||x>r.width||y>r.height){ lens.hidden=true; return; }
      lens.hidden=false; const lw=lens.offsetWidth, lh=lens.offsetHeight;
      lens.style.left=Math.max(0,Math.min(r.width-lw,x-lw/2))+'px'; lens.style.top=(y-lh-12<-r.top? y+16 : y-lh-12)+'px';
      lens.style.backgroundSize=(r.width*Z)+'px '+(r.height*Z)+'px';
      lens.style.backgroundPosition=(lw/2-x*Z)+'px '+(lh/2-y*Z)+'px'; }
    img.addEventListener('pointermove',e=>{ if(e.pointerType!=='touch') show(e); });
    img.addEventListener('pointerleave',e=>{ if(e.pointerType!=='touch') lens.hidden=true; });
    img.addEventListener('click',e=>{ if(lens.hidden||e.pointerType==='touch') show(e); else lens.hidden=true; });
  });
  document.addEventListener('click',e=>{ if(!e.target.closest('.zw')) document.querySelectorAll('.lens').forEach(l=>l.hidden=true); });
})();
</script>'''
CSS = CSS.replace('</style>', ''':root{--nohl:#ffb4ac}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--nohl:#7a2a24}}:root[data-theme="dark"]{--nohl:#7a2a24}mark.no{background:var(--nohl)}
.zw{position:relative;touch-action:pan-y}.zw img{cursor:zoom-in}
.lens{position:absolute;width:300px;height:130px;max-width:90%;border:2px solid var(--fg);border-radius:10px;background-color:#fff;background-repeat:no-repeat;pointer-events:none;box-shadow:0 4px 18px rgba(0,0,0,.25);z-index:5}</style>''')
CSS = CSS.replace('<title>Polytonic Spell Check Status</title>', '<title>Accent Corrections Checked</title>')
D = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/'
nfc = lambda s: ud.normalize('NFC', s or ''); nfd = lambda s: ud.normalize('NFD', s or '')
recs = {r['line_id']: r for r in json.load(gzip.open(D + 'private/audit100/selected_overlays.json.gz', 'rt'))['records']}
final = json.load(open(D + 'audit100_private/audit100_final.json'))
key = [i for i in json.load(open(D + 'private/audit100/items_key.json')) if not i.get('control')]
crop = {i['line_id']: i['source_crop'] for i in key}; osha = {i['line_id']: i['original_label_sha256'] for i in key}
G = {}
for l in open('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'):
    r = json.loads(l)
    if r['id'] in recs: G[r['id']] = r['label']
bad_sha = [l for l in recs if hashlib.sha256(G[l].encode()).hexdigest() != osha[l] and hashlib.sha256(nfd(G[l]).encode()).hexdigest() != osha[l]]
def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def image(lid):
    r = recs[lid]; slots = r['changes'][0]['evidence']['slots']
    im = Image.open(crop[lid]); W, Hh = im.size; s = 2 if W < 700 else 1
    clean = uri(im.convert('RGB'))
    big = im.convert('RGB').resize((W * s, Hh * s), Image.NEAREST); d = ImageDraw.Draw(big)
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 11 * s)
    except Exception: font = None
    for i, sl in enumerate(slots):
        ev = sl['evidence']
        for b in ev.get('above', []) + ev.get('apostrophes', []):
            x0, y0, x1, y1 = b['bbox']; d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(30, 140, 60), width=2)
        for b in ev.get('below', []):
            x0, y0, x1, y1 = b['bbox']; d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(40, 80, 200), width=2)
        x = (sl.get('locator_span') or [None])[0]
        if x is not None: d.text((max(0, x) * s, Hh * s - 12 * s), str(i + 1), fill=(120, 120, 120), font=font)
    for q in r.get('opening_quotes') or []:
        if 'bbox' in q: x0, y0, x1, y1 = q['bbox']; d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(30, 140, 60), width=2)
    if big.size[0] > 1000: big = big.resize((1000, int(big.size[1] * 1000 / big.size[0])), Image.LANCZOS)
    return uri(big), clean
import difflib
def clus(t):
    out = []
    for ch in nfd(t):
        if ud.category(ch).startswith('M') and out: out[-1] += ch
        else: out.append(ch)
    return out
NAME = {'̓': 'smooth breathing', '̔': 'rough breathing', '́': 'acute', '̀': 'grave', '͂': 'circumflex',
        'ͅ': 'iota subscript', '̈': 'diaeresis'}
def changes(lid):
    """Each released change: its NFD offset in our line, what was added, and whether the detector found ink where it was added."""
    r = recs[lid]; gd = sorted(r['gate_decisions'], key=lambda g: g['start']); lab = nfd(r['label']); out = []
    for c in r['changes']:
        slot = max((g for g in gd if g['start'] < c['start']), key=lambda g: g['start']); ev = slot['evidence']  # the mark is inserted after its letter
        assert slot['base'] == c['letter'], (lid, slot['base'], c['letter'])
        added = [ch for ch in c['to'] if ch not in c['from']]
        below = 'ͅ' in added
        out.append(dict(start=c['start'], names=[NAME.get(ch, 'mark') for ch in added], ink=bool(ev['below'] if below else ev['above'])))
    return out
PAIRS = [0]
def marked(a, b, chg):
    PAIRS[0] = 0
    """Both lines with a background on every character whose marks differ: yellow where the detector found ink for the
    added mark, red where it found none."""
    A, B = clus(a), clus(b); ha, hb = [], []
    seen = [0]
    def cls_for(j):
        # changes and highlighted letters are both in line order; pair them one to one
        k = seen[0]; seen[0] += 1
        if k < len(chg): return '' if chg[k]['ink'] else ' class="no"'
        return ''
    sm = difflib.SequenceMatcher(None, [c[0] for c in A], [c[0] for c in B], autojunk=False)
    for op, i0, i1, j0, j1 in sm.get_opcodes():
        for k in range(max(i1 - i0, j1 - j0)):
            x = A[i0 + k] if i0 + k < i1 else None; y = B[j0 + k] if j0 + k < j1 else None
            same = op == 'equal' and x == y
            cl = '' if same or y is None else cls_for(j0 + k)
            if not same and y is not None: PAIRS[0] += 1
            if x is not None: ha.append(html.escape(nfc(x)) if same else '<mark%s>%s</mark>' % (cl, html.escape(nfc(x))))
            if y is not None: hb.append(html.escape(nfc(y)) if same else '<mark%s>%s</mark>' % (cl, html.escape(nfc(y))))
    return ''.join(ha), ''.join(hb)
MISMATCH = []
def card(lid):
    img, clean = image(lid); g = nfc(G[lid]); ours = nfc(recs[lid]['label']); chg = changes(lid); gh, oh = marked(g, ours, chg)
    if PAIRS[0] != len(chg): MISMATCH.append((lid, PAIRS[0], len(chg)))
    return f'''<div class="card" data-line="{lid}"><div class="lid">{html.escape(lid)}</div><div class="zw"><img src="{img}" alt="line with detected marks"><div class="lens" style="background-image:url({clean})" hidden></div></div>
<table class="w"><tr><th>Google</th><td>{gh}</td></tr><tr><th>Ours</th><td>{oh}</td></tr></table>
<div class="row">{''.join(f'<span class="pill {"ok" if c["ink"] else "bad"}">{" + ".join(c["names"])} added · {"ink found" if c["ink"] else "no ink found"}</span>' for c in chg)}</div>
<div class="notes" data-line="{lid}"><label>Note</label><textarea class="note" rows="2"></textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>'''
bad = [l for l, v in final.items() if not v['ok']]; good = [l for l, v in final.items() if v['ok']]
intro = ('100 lines where we changed Google’s accents, read against the print. Full line crop with slot numbers; marks we detect boxed '
         '(green above, blue below); then Google’s line and ours. Changed letters: yellow = the detector found ink where we add the mark, red = it found none. No note = our line is right.')
page = [CSS, f'<main><h1>Accent Corrections Checked</h1><p class="meta">{html.escape(intro)}</p>', f'<h2>Wrong ({len(bad)})</h2>'] \
       + [card(l) for l in bad] + [f'<h2>Right ({len(good)})</h2>'] + [card(l) for l in good] + ['</main>', SCRIPT, EXTRA_JS]
open(sys.argv[1] + '/accent_corrections_checked.html', 'w').write('\n'.join(page))
print('pair mismatches', MISMATCH); print('cards', len(bad) + len(good), 'google sha mismatches', len(bad_sha), 'missing google', len(set(recs) - set(G)))
