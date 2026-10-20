"""Options sheet: 10 examples per census class (by print truth) + the owner's ᾗσι case; per card the full line, a zoom on the disputed
vowel with the detector's mark boxes (green above, blue below, red vowel body, grey meanline/baseline) and the classifier's reading, then
Google / Wikisource (reference) / Printed (blind readers) and what each option does."""
import base64, html, io, json, random, sys, unicodedata as u
from PIL import Image, ImageDraw
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.ctc_align import transfer_alignment
from greekocr.labelfix.ink import analyse, mark_evidence
from greekocr.labelfix.markshape import features, load_model, mark_class
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.spellink import locate
from greekocr.labelfix.text import clusters, nfd, tokenize
from greekocr.labelfix.validate import TOOLKIT, load_three_way
W = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/'
S = sys.argv[1]
nfc = lambda s: u.normalize('NFC', s or '')
pt = json.load(open(W + 'docs/labelfix/spellcheck/print_truth_s0.json'))
reach = {f"{json.loads(l)['line_id']}|{json.loads(l)['word_index']}": json.loads(l) for l in open(W + 'docs/labelfix/spellcheck/reach_s0.jsonl')}
words = {f"{json.loads(l)['line_id']}|{json.loads(l)['word_index']}": json.loads(l) for l in open(W + 'docs/labelfix/spellcheck/words_s0.jsonl')}
uni = json.load(open(S + '/memo/opt2_unigram_s0.json'))
opt1 = {}
for l in open(S + '/memo/opt1_s0.jsonl'):
    r = json.loads(l); opt1[(r['line_id'], r['w'], r['c'])] = r
L = {l['line_id']: l for l in load_three_way(0)}
A = load_alignments(TOOLKIT / '.cache/labelfix/align_s0.jsonl')
model = load_model(TOOLKIT / 'docs/labelfix/markshape_model.json')
rng = random.Random(7)
def diff_c(a, b):
    ca, cb = clusters(nfd(a)), clusters(nfd(b))
    d = [i for i, (x, y) in enumerate(zip(ca, cb)) if x.marks != y.marks] if len(ca) == len(cb) else []
    return d[0] if d else None
def png(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def card(k, title_pill):
    v = pt[k]; e = reach[k]; lid, wi = k.split('|'); wi = int(wi); l = L[lid]
    printed = v.get('printed'); ci = diff_c(v['google'], printed or v['human'])
    im = Image.open(l['crop']).convert('RGB'); w, h = im.size
    al = A[crop_key(l['crop'])]
    if nfd(al.prediction) != l['model']: al = transfer_alignment(l['model'], al)
    g = tokenize(l['google'])[wi]; m = dict((a.index, b) for a, b in pair_tokens(l['google'], l['model'])).get(wi)
    line = im.copy(); d = ImageDraw.Draw(line)
    if m: x0, x1 = al.window(m.start, m.end); d.rectangle([x0 - 3, 0, x1 + 3, h - 1], outline=(220, 0, 0), width=3)
    zoom_uri, cap = None, 'no single differing vowel (two clusters differ)'
    if ci is not None:
        loc = locate(g, m, al, ci)
        if loc:
            ink = analyse(Image.open(l['crop'])); how, a0, a1, b0, b1 = loc
            ev = mark_evidence(ink, a0, a1, core_x0=b0, core_x1=b1)
            pred, prob, _ = model.predict(features(ev))
            z = im.copy(); dz = ImageDraw.Draw(z)
            for b in ev.above: dz.rectangle([b.x0, b.y0, b.x1, b.y1], outline=(30, 150, 60) if b.source == 'detached' else (150, 150, 150), width=1)
            for b in ev.below: dz.rectangle([b.x0, b.y0, b.x1, b.y1], outline=(40, 80, 210), width=1)
            dz.rectangle([ev.body[0], ev.meanline, ev.body[1], ev.baseline], outline=(220, 0, 0), width=1)
            dz.line([0, ev.meanline, w, ev.meanline], fill=(170, 170, 170)); dz.line([0, ev.baseline, w, ev.baseline], fill=(170, 170, 170))
            cx0, cx1 = max(0, int(ev.body[0] - 1.5 * ev.xh)), min(w, int(ev.body[1] + 1.5 * ev.xh))
            z = z.crop((cx0, 0, cx1, h)); f = max(1, min(8, int(500 / max(1, z.size[0]))))
            z = z.resize((z.size[0] * f, h * f), Image.NEAREST); zoom_uri = png(z)
            att = sum(1 for b in ev.above if b.source != 'detached')
            cap = (f"marks found: {sum(1 for b in ev.above if b.source == 'detached')} detached above (green)"
                   f"{f', {att} attached above (grey, may be ascender ink)' if att else ''}, {len(ev.below)} below (blue) · "
                   f"shape classifier: {pred} p={prob:.3f} (threshold 0.998) · printed mark: {mark_class(clusters(nfd(printed))[ci].marks) if printed else '?'} · "
                   f"Google mark: {mark_class(clusters(nfd(v['google']))[ci].marks)}")
    s = 1000 / w if w > 1000 else 1
    line = line.resize((int(w * s), int(h * s)))
    # what each option does
    o1 = opt1.get((lid, wi, ci)) if ci is not None else None
    if o1 is None: o1t = 'no reading (not located)'
    elif o1.get('abstain'): o1t = f"abstains ({o1['abstain']})"
    elif o1['prob'] >= 0.998 and o1['pred'] != o1['g']: o1t = f"changes to {o1['pred']} (p={o1['prob']:.3f})"
    else: o1t = f"keeps Google (reads {o1['pred']} p={o1['prob']:.3f})"
    p2 = uni.get(k); o2t = f"proposes {nfc(p2)}" if p2 and nfc(p2) != v['google'] else 'keeps Google (most frequent form)'
    wd = words.get(k, {}); dec = wd.get('decision', {})
    o3t = (f"{dec.get('column')} → {nfc(dec.get('proposal'))} ({wd.get('stage')})" if dec.get('column')
           else f"no change ({wd.get('stage') or e['stage']}: {(dec.get('reason') or 'not a candidate')[:70]})")
    target = printed
    def judge(txt, prop):
        if prop is None: return ''
        return ' ✓ = print' if target and nfc(prop) == nfc(target) else (' ✗ normalises the print' if target == v['google'] else ' ✗')
    o1prop = None
    rows = f'''<tr><th>Google</th><td><mark>{html.escape(v['google'])}</mark> · line: {html.escape(nfc(l['google']))}</td></tr>
<tr><th>Wikisource</th><td>{html.escape(v['human'])} <span class="why">(reference only)</span></td></tr>
<tr><th>Printed</th><td><mark>{html.escape(printed or 'unresolved')}</mark> <span class="why">blind readers</span></td></tr>
<tr><th>1 · image</th><td>{html.escape(o1t)}</td></tr>
<tr><th>2 · restorer</th><td>{html.escape(o2t)}{judge(o2t, p2 if p2 and nfc(p2) != v['google'] else None)}</td></tr>
<tr><th>3 · hybrid</th><td>{html.escape(o3t)}{judge(o3t, dec.get('proposal') if dec.get('column') else None)}</td></tr>'''
    z = f'<div class="zoomrow"><img class="zoom" src="{zoom_uri}" alt="vowel zoom with detected marks"><div class="inkcap">{html.escape(cap)}</div></div>' if zoom_uri else f'<div class="row">{html.escape(cap)}</div>'
    return f'''<div class="card"><img src="{png(line)}" alt="line crop">{z}<table class="w">{rows}</table><div class="row"><span class="pill">{html.escape(title_pill)}</span><span class="pill">{'model also wrong' if not e['model_right'] else 'model right'}</span><span class="why">{html.escape(k)}</span></div></div>'''
classes = [('Worked example: ᾗσι (compound breathing + perispomeni + subscript)', ['384c3f89-p000096-l0004|3'])]
order = ['constraint', 'grave', 'grave_line_end', 'lex_unique', 'lex_compete', 'lex_miss', 'real_word', 'guard', 'human_unatt']
for st in order:
    ks = [k for k, e in reach.items() if e['stage'] == st and pt.get(k, {}).get('verdict') in ('human', 'other')]
    rng.shuffle(ks); classes.append((f'{st} · real Google errors by print truth ({len(ks)})', ks[:10]))
ks = [k for k, v in pt.items() if v['verdict'] == 'google']; rng.shuffle(ks)
classes.append((f'Google read the print, Wikisource normalised it ({len(ks)}) — any correction here is wrong', ks[:10]))
css = open(S + '/memo/v4.css').read().split('<style>')[1].split('</style>')[0]
css = css.replace('padding-inline:16px', 'padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))')
out = ['<title>Fixing Options Examples</title><meta name="claude:viewport-fit-sides" content="cover"><style>' + css + '</style><main>',
       '<h1>Fixing Options Examples</h1>',
       '<p class="meta">16 Oct 2026 · three-way Wikisource lines, seed 0 · print truth = blind two-reader pixel adjudication. Each card: the line with the word boxed; a zoom on the disputed vowel with the detector\'s marks (green = detached mark above, grey = attached ink above, often an ascender; blue = below the baseline; red = the vowel body; grey lines = meanline and baseline) and the classifier\'s reading; then Google, the Wikisource reference, what is printed, and what each option does: 1 = image only (today\'s classifier at τ 0.998), 2 = context-free restorer (most frequent attested form; lower bound for an ML restorer, before any ink check), 3 = the hybrid as built (S1). ✓ = equals the print; ✗ normalises the print = the restorer changed a word Google had read correctly.</p>']
for t, ks in classes:
    out.append(f'<h2>{html.escape(t)}</h2>')
    for k in ks:
        try: out.append(card(k, t.split(' ·')[0]))
        except Exception as ex: out.append(f'<p class="meta">{html.escape(k)}: {html.escape(repr(ex))}</p>')
out.append('</main>')
open(S + '/options_examples.html', 'w').write('\n'.join(out))
print('ok')
