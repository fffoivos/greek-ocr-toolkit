"""Substitution cases through the owner template: crop with slot numbers + saved detections (green above, blue below),
Google line, Ours = Google's line with the contradicting mark swapped, one tag per swap, one note; hover magnifier on the clean crop."""
import json, html, io, base64, sys, os, unicodedata as ud
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
tpl = open(S + '/build_audit_template.py').read()
src = open(S + '/snap6/build_owner.py').read()
CSS = src.split("CSS = '''", 1)[1].split("'''", 1)[0]; SCRIPT = src.split("SCRIPT = '''", 1)[1].split("'''", 1)[0]
EXTRA_JS = tpl.split("EXTRA_JS = '''", 1)[1].split("'''", 1)[0]
extra_css = tpl.split("CSS = CSS.replace('</style>', '''", 1)[1].split("</style>''')", 1)[0]
CSS = CSS.replace('</style>', extra_css + '</style>').replace('<title>Polytonic Spell Check Status</title>', '<title>Accent Substitutions</title>')
nfc = lambda s: ud.normalize('NFC', s or ''); nfd = lambda s: ud.normalize('NFD', s or '')
MK = {'acute': '́', 'grave': '̀', 'circumflex': '͂', 'psili': '̓', 'dasia': '̔'}
NAME = {'acute': 'acute', 'grave': 'grave', 'circumflex': 'circumflex', 'psili': 'smooth breathing', 'dasia': 'rough breathing'}
TAG = {'agree': ('ok', 'reader and detector agree'), 'other': ('warn', 'detector sees ink, names {det}'), 'noink': ('bad', 'no ink found')}
ROOT = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/'
d = json.load(open(S + '/subst_sample.json'))
def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def image(x):
    im = Image.open(ROOT + x['crop']); W, Hh = im.size; s = 2 if W < 700 else 1; clean = uri(im.convert('RGB'))
    big = im.convert('RGB').resize((W * s, Hh * s), Image.NEAREST); dr = ImageDraw.Draw(big)
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 11 * s)
    except Exception: font = None
    for i, sl in enumerate(x['slots']):
        for b in sl['above']: dr.rectangle([b[0] * s, b[1] * s, b[2] * s, b[3] * s], outline=(30, 140, 60), width=2)
        for b in sl['below']: dr.rectangle([b[0] * s, b[1] * s, b[2] * s, b[3] * s], outline=(40, 80, 200), width=2)
        if sl.get('body'): dr.text((sl['body'][0] * s, Hh * s - 12 * s), str(i + 1), fill=(120, 120, 120), font=font)
    if big.size[0] > 1000: big = big.resize((1000, int(big.size[1] * 1000 / big.size[0])), Image.LANCZOS)
    return uri(big), clean
def lines(x):
    """Google's line and ours (Google's with each contradicting mark swapped), both highlighted at the swapped letters."""
    by = {c['letter']: c for c in x['con']}
    gh, oh, li = [], [], -1; cl = []
    for ch in nfd(x['label']):
        if ud.category(ch).startswith('M') and cl: cl[-1] += ch
        else: cl.append(ch)
    for c in cl:
        if c[0].isalpha(): li += 1
        con = by.get(li) if c[0].isalpha() else None
        if not con: gh.append(html.escape(nfc(c))); oh.append(html.escape(nfc(c))); continue
        new = c[0] + ''.join(MK[con['ours']] if m == MK[con['google']] else m for m in c[1:])
        k = '' if con['tier'] == 'agree' else ' class="no"'
        gh.append(f'<mark{k}>{html.escape(nfc(c))}</mark>'); oh.append(f'<mark{k}>{html.escape(nfc(new))}</mark>')
    return ''.join(gh), ''.join(oh)
def tag(c):
    cls, t = TAG[c['tier']]
    det = ' + '.join(NAME.get(p, p) for p in c['det'] if p in NAME) or 'no mark'
    return f'<span class="pill {cls}">{NAME[c["google"]]} → {NAME[c["ours"]]} · {t.format(det=det)}</span>'
def card(x):
    img, clean = image(x); gh, oh = lines(x); lid = x['line_id']
    return f'''<div class="card" data-line="{lid}"><div class="lid">{html.escape(lid)}</div><div class="zw"><img src="{img}" alt="line with detected marks"><div class="lens" style="background-image:url({clean})" hidden></div></div>
<table class="w"><tr><th>Google</th><td>{gh}</td></tr><tr><th>Ours</th><td>{oh}</td></tr></table>
<div class="row">{''.join(tag(c) for c in x['con'])}</div>
<div class="notes" data-line="{lid}"><label>Note</label><textarea class="note" rows="2"></textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>'''
sz = d['sizes']; smp = d['sample']
intro = ('Lines where our reading puts a different mark than Google on the same letter (acute ↔ grave ↔ circumflex, smooth ↔ rough '
         'breathing). All are held today, so the label keeps Google’s mark. Full line crop with slot numbers; marks we detect boxed '
         '(green above, blue below); Google’s line, then ours with the mark swapped. Yellow = reader and detector agree, red = they do not. '
         '20 random lines per group. No note = our line is right.')
H = {'agree': 'Reader and detector agree', 'other': 'Detector sees ink, names another mark', 'noink': 'Detector sees no ink'}
page = [CSS, f'<main><h1>Accent Substitutions</h1><p class="meta">{html.escape(intro)}</p>']
for t in ('agree', 'other', 'noink'):
    page.append(f'<h2>{H[t]} ({sz[t]:,} lines)</h2>'); page += [card(x) for x in smp[t]]
page += ['</main>', SCRIPT, EXTRA_JS]
open(S + '/accent_substitutions.html', 'w').write('\n'.join(page))
print('cards', sum(len(v) for v in smp.values()), os.path.getsize(S + '/accent_substitutions.html'))
