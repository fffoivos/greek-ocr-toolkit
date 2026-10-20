import json, struct, html, sys, unicodedata
D = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV'
S = sys.argv[1]
key = json.load(open(D + '/private/audit100/items_key.json'))
final = json.load(open(D + '/audit100_private/audit100_final.json'))
script = open(S + '/notes_script.html').read()
nfc = lambda s: unicodedata.normalize('NFC', s)
def size(p):
    b = open(D + '/audit100/' + p, 'rb').read(24); return struct.unpack('>II', b[16:24])
items = {}
for it in key:
    if it.get('control'): continue
    items.setdefault(it['line_id'], []).append(it)
def diffmark(a, b):
    # highlight the letters of b that differ from a (same-length clusters by NFC char)
    a, b = nfc(a), nfc(b)
    if len(a) != len(b): return html.escape(b)
    return ''.join('<mark>%s</mark>' % html.escape(y) if x != y else html.escape(y) for x, y in zip(a, b))
VERD = {'released_right': ('ok', 'matches the print'), 'google_right': ('bad', 'Google was right'), 'unknown': ('warn', 'unreadable')}
def card(lid, rec):
    its = items[lid]; line_img = its[0]['line_img']; w, h = size(line_img)
    out = ['<div class="card" data-line="%s"><div class="lid">%s</div>' % (lid, lid)]
    out.append('<img class="line" src="%s" alt="Printed line" width="%d" height="%d" style="width:%dpx">' % (line_img, w, h, min(2 * w, 960)))
    for verdict, g, r, printed in rec['cards']:
        it = next((i for i in its if nfc(i['forms']['google']) == nfc(g) and nfc(i['forms']['released']) == nfc(r)), None)
        cls, lab = VERD[verdict]
        out.append('<div class="word">')
        if it:
            zw, zh = size(it['img'])
            out.append('<img class="zoom" src="%s" alt="Word" width="%d" height="%d">' % (it['img'], zw, zh))
        out.append('<table class="w"><tr><th>Google</th><td>%s</td></tr><tr><th>Ours</th><td>%s</td></tr><tr><th>Printed</th><td>%s</td></tr></table>'
                   % (html.escape(nfc(g)), diffmark(g, r), html.escape(nfc(printed)) if printed else '<span class="muted">unreadable</span>'))
        out.append('<div class="row"><span class="pill %s">%s</span></div></div>' % (cls, lab))
    out.append('<div class="notes" data-line="%s"><label for="n-%s">Note</label><textarea class="note" id="n-%s" rows="2"></textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>' % (lid, lid, lid))
    return ''.join(out)
lines = list(final.items())
bad = [(l, r) for l, r in lines if not r['ok']]; good = [(l, r) for l, r in lines if r['ok']]
imgs = set()
for l, _ in lines:
    for it in items[l]: imgs.add(it['line_img']); imgs.add(it['img'])
css = open(S + '/audit_css.css').read()
page = ['<title>Accent Corrections Checked</title><meta name="claude:viewport-fit-sides" content="cover">',
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&display=swap">', '<style>' + css + '</style>',
 '<main><h1>Accent Corrections Checked</h1>',
 '<p class="meta">100 lines where we changed Google’s accents, read against the printed page. Ours is highlighted where it differs from Google.</p>',
 '<div class="sum"><div><b>83 / 100</b><span>lines match the print</span></div><div><b>13 of 17</b><span>wrong lines add an iota subscript the print does not have</span></div><div><b>83 / 87</b><span>right when those are left out</span></div></div>',
 '<h2>Wrong (%d)</h2>' % len(bad)] + [card(l, r) for l, r in bad] + ['<h2>Right (%d)</h2>' % len(good)] + [card(l, r) for l, r in good] + ['</main>', script]
open(S + '/accent_corrections_checked.html', 'w').write('\n'.join(page))
json.dump(sorted(imgs), open(S + '/audit_imgs.json', 'w'))
print(len(bad), len(good), len(imgs))
