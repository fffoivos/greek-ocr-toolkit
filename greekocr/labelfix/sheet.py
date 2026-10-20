"""Crop-and-text sheet: one self-contained HTML page of line crops with the word boxed and the readings.

    python -m greekocr.labelfix.sheet --rows rows.jsonl --seed 0 --title "..." --out sheet.html

Each input row (JSON lines) needs `line_id`, `word_index`, `google`, `human`, `proposal` and `tag`
(the group heading); optional `note`. Crops come from the v2 test instrument; the word box comes
from the cached CTC alignment of the seed's model (the model only locates). The page is for reading
results, not for blinded review (the blinded deck is `deck.py`).
"""
from __future__ import annotations

import argparse
import base64
from collections import defaultdict
import html
import io
import json
from pathlib import Path

from PIL import Image

from .candidates import pair_tokens
from .ctc_align import Alignment, transfer_alignment
from .text import nfc, nfd
from .validate import TOOLKIT, load_three_way

CSS = """
:root{--bg:#f7f5f0;--fg:#1d1a16;--muted:#6b645a;--line:#d9d3c8;--panel:#fffdf9;--accent:#2f5d8a;--ok:#2e7d4f;--bad:#a93a2f;
--soft:#ece7dd;--box:#d0473a;--display:"Source Serif 4",Georgia,serif;--body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
--greek:"GFS Didot","Source Serif 4",Georgia,serif;--mono:"IBM Plex Mono",Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;
--panel:#201f24;--accent:#8fb6e0;--ok:#7fc39a;--bad:#e2796c;--soft:#2a282e;--box:#ff7a6b;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#17161a;--fg:#ebe6dc;--muted:#a39b8e;--line:#3a373f;--panel:#201f24;--accent:#8fb6e0;
--ok:#7fc39a;--bad:#e2796c;--soft:#2a282e;--box:#ff7a6b;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.5;margin:0;padding-block:28px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:980px;margin:0 auto;min-width:0}
h1{font-family:var(--display);font-weight:600;font-size:1.9rem;line-height:1.15;margin:0 0 6px}
h2{font-family:var(--display);font-weight:600;font-size:1.3rem;margin:34px 0 6px}
p{max-width:72ch;margin:0 0 10px}.meta,.note{color:var(--muted);font-size:.9rem}
.row{background:var(--panel);border:1px solid var(--line);padding:10px 12px;margin:10px 0;min-width:0}
.crop{position:relative;overflow-x:auto;background:#fff;border:1px solid var(--line)}
.crop .in{position:relative;display:inline-block}
.crop img{display:block;max-width:none;height:auto}
.crop .box{position:absolute;top:0;bottom:0;border:2px solid var(--box);border-radius:2px;pointer-events:none}
.words{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px;margin-top:8px;font-size:.92rem}
.words .k{color:var(--muted);font-size:.75rem;letter-spacing:.05em;text-transform:uppercase;padding-top:3px}
.words .v{font-family:var(--greek);font-size:1.25rem}
.id{font-family:var(--mono);font-size:.75rem;color:var(--muted);margin-bottom:6px;overflow-wrap:anywhere}
.ok{color:var(--ok)}.bad{color:var(--bad)}
"""


def b64png(im: Image.Image) -> str:
    buf = io.BytesIO()
    im.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def load_alignments(path: Path) -> dict:
    out = {}
    for line in open(path, encoding='utf-8'):
        r = json.loads(line)
        out[crop_key(r['crop'])] = Alignment.from_record(r['alignment'])
    return out


def crop_key(path: str) -> str:
    """Checkout-independent key: the crop path from `docs/` on (caches are shared across worktrees)."""
    i = path.find('docs/harvest/')
    return path[i:] if i >= 0 else path


def word_window(line: dict, al: Alignment | None, word_index: int):
    if al is None:
        return None
    model = nfd(line['model'])
    if nfd(al.prediction) != model:
        al = transfer_alignment(model, al)
    m = dict((g.index, mm) for g, mm in pair_tokens(line['google'], model)).get(word_index)
    if m is None:
        return None
    return al.window(m.start, m.end)


def render(rows: list[dict], seed: int, title: str, intro: str, align_path: Path | None) -> str:
    lines = {l['line_id']: l for l in load_three_way(seed)}
    aligns = load_alignments(align_path) if align_path and align_path.exists() else {}
    groups = defaultdict(list)
    for r in rows:
        groups[r['tag']].append(r)
    parts = [f'<title>{html.escape(title)}</title><meta name="claude:viewport-fit-sides" content="cover">',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;'
             '8..60,600&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&family=GFS+Didot&display=swap">',
             f'<style>{CSS}</style><main>', f'<h1>{html.escape(title)}</h1>', intro]
    for tag, rs in groups.items():
        parts.append(f'<h2>{html.escape(tag)} <span class="note">({len(rs)})</span></h2>')
        for r in rs:
            l = lines[r['line_id']]
            im = Image.open(l['crop']).convert('L')
            w, h = im.size
            win = word_window(l, aligns.get(crop_key(l['crop'])), r['word_index'])
            box = ''
            if win:
                x0, x1 = max(0.0, win[0] - 3), min(float(w), win[1] + 3)
                box = f'<div class="box" style="left:{100 * x0 / w:.2f}%;width:{100 * (x1 - x0) / w:.2f}%"></div>'
            ok = r.get('ok')
            mark = '' if ok is None else (' <span class="ok">✓ matches the human text</span>' if ok
                                          else ' <span class="bad">✗ Google was right</span>')
            parts.append(
                f'<div class="row"><div class="id">{html.escape(r["line_id"])} · word {r["word_index"] + 1}'
                f'{" · " + html.escape(r["note"]) if r.get("note") else ""}</div>'
                f'<div class="crop"><div class="in"><img alt="line crop" width="{w}" height="{h}" '
                f'src="data:image/png;base64,{b64png(im)}">{box}</div></div>'
                f'<div class="words"><span class="k">Google</span><span class="v">{html.escape(nfc(r["google"]))}</span>'
                f'<span class="k">Proposal</span><span class="v">{html.escape(nfc(r["proposal"]))}{mark}</span>'
                f'<span class="k">Human</span><span class="v">{html.escape(nfc(r["human"]))}</span>'
                f'<span class="k">Line</span><span class="v" style="font-size:1rem">{html.escape(nfc(l["google"]))}</span></div></div>')
    parts.append('</main>')
    return '\n'.join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rows', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--title', required=True)
    ap.add_argument('--intro', default='')
    ap.add_argument('--align', type=Path, default=None)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.rows, encoding='utf-8')]
    align = a.align or TOOLKIT / f'.cache/labelfix/align_s{a.seed}.jsonl'
    a.out.write_text(render(rows, a.seed, a.title, a.intro, align), encoding='utf-8')
    print(a.out, len(rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


def highlighted_line(text, word_index, replacement=None):
    """Preserve the original line spacing/punctuation; mark exactly the paired token."""
    from .text import tokenize
    ts = tokenize(text)
    if word_index is None or word_index >= len(ts):
        return html.escape(nfc(text))
    t = ts[word_index]
    return (html.escape(nfc(text[:t.start])) + '<mark>' + html.escape(nfc(replacement or t.text)) +
            '</mark>' + html.escape(nfc(text[t.end:])))


def highlighted_human(line, row):
    """One-to-one reference token, or a display-only aligned span when scoring is unknown."""
    if row.get('human_word_index') is not None:
        return highlighted_line(line['human'], row['human_word_index'])
    from .candidates import align_chars
    from .text import tokenize
    g = tokenize(line['google'])[row['word_index']]
    hits = [j for i,j in align_chars(line['google'], line['human'])
            if i is not None and j is not None and g.start <= i < g.end]
    if not hits:
        return html.escape(nfc(line['human'])) + ' <mark>(unpaired)</mark>'
    ts = [t for t in tokenize(line['human']) if t.start <= max(hits) and t.end > min(hits)]
    start, end = (ts[0].start,ts[-1].end) if ts else (min(hits),max(hits)+1)
    h = line['human']
    return html.escape(nfc(h[:start])) + '<mark>' + html.escape(nfc(h[start:end])) + '</mark>' + html.escape(nfc(h[end:]))


def spellcheck_zoom(im, row):
    """Audit raster: native crop pixels enlarged 3x, with detector boxes and band guides."""
    from PIL import ImageDraw
    ev = row.get('ink') or {}
    win = row.get('cluster_window') or ev.get('body')
    if not win:
        return None
    xh = ev.get('xh', im.height / 2)
    left = max(0, int(min(win) - xh))
    right = min(im.width, int(max(win) + xh + 1))
    if right <= left:
        return None
    zoom = im.crop((left, 0, right, im.height)).convert('RGB').resize(((right-left)*3, im.height*3), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(zoom)
    for y in (ev.get('meanline'), ev.get('baseline')):
        if y is not None:
            d.line((0, y*3, zoom.width, y*3), fill='#888888', width=2)
    d.rectangle(((win[0]-left)*3, 0, (win[1]-left)*3, zoom.height-1), outline='#d0473a', width=2)
    for key, color in (('above', '#25a64a'), ('below', '#3478dc')):
        for b in ev.get(key, []):
            x0,y0,x1,y1 = b['bbox']
            d.rectangle(((x0-left)*3,y0*3,(x1-left)*3,y1*3), outline=color, width=2)
    return zoom


def render_spellcheck(rows, lines_by_seed, title, reference=None):
    """Owner v4 card contract, verbatim reference CSS, all images embedded (offline)."""
    import re
    reference = reference or TOOLKIT / 'docs/records/labelfix/spellcheck/sheet_format_reference_v4.html'
    ref = reference.read_text(encoding='utf-8')
    styles = '\n'.join(re.findall(r'<style>.*?</style>', ref, flags=re.S))
    esc = html.escape
    parts = ['<!doctype html><html><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
             '<meta name="claude:viewport-fit-sides" content="cover">', f'<title>{esc(title)}</title>', styles,
             '</head><body><main>', f'<h1>{esc(title)}</h1>',
             '<p class="meta">Both seeds · strict default. Every ACCEPT and HOLD, including false fires. '
             'Human (test reference) is used only for scoring. Green = above, blue = below, red = vowel window, '
             'grey = meanline and baseline. CTC only locates.</p>']
    for r in rows:
        line = lines_by_seed[r['seed']][r['line_id']]
        with Image.open(line['crop']) as src:
            im = src.convert('RGB')
        zoom = spellcheck_zoom(im, r)
        ev, shape = r.get('ink') or {}, r.get('shape') or {}
        prob = f"{shape['prob']:.6f}" if 'prob' in shape else 'unavailable'
        cap = (f"marks found: {len(ev.get('above', []))} above, {len(ev.get('below', []))} below · "
               f"shape classifier: {shape.get('pred', 'unavailable')} p={prob} (threshold {shape.get('tau', 'unavailable')}) · "
               f"ink verdict: {r.get('ink_verdict', 'abstains')} ({r['decision']['reason']}); "
               f"lexicon: {r['lexicon_reason']}, Google={r['written_count']}, proposal={r.get('proposal_count', 0)}")
        if r['outcome'] == 'unknown':
            cap += '; human span is display-only (no one-to-one reference token)'
        why = (f"{r['google_nfc']} → {r['corrected_nfc']} (human {r.get('human_nfc')}) · "
               f"{r['decision']['column']}: {r['decision']['reason']}")
        parts += [f'<div class="card"><div class="meta">seed {r["seed"]} · {esc(r["line_id"])} · word {r["word_index"]+1}</div>',
                  f'<img src="data:image/png;base64,{b64png(im)}" alt="line crop">', '<div class="zoomrow">']
        if zoom:
            parts.append(f'<img class="zoom" src="data:image/png;base64,{b64png(zoom)}" alt="vowel zoom with detected marks">')
        parts += [f'<div class="inkcap">{esc(cap)}<br><span class="why">{esc(why)}</span></div></div>']
        for ck in r.get('cluster_checks', [])[1:]:
            extra_zoom = spellcheck_zoom(im, ck)
            if extra_zoom is not None:
                ce, cs = ck.get('ink') or {}, ck.get('shape') or {}
                caption = (f"cluster {ck['cluster']}: marks found: {len(ce.get('above', []))} above, "
                           f"{len(ce.get('below', []))} below · shape classifier: {cs.get('pred', 'unavailable')} "
                           f"p={cs.get('prob', 0):.6f} (threshold {cs.get('tau', 'unavailable')}) · "
                           f"ink verdict: {'supports' if ck['accept'] else 'abstains'} ({ck['reason']}); lexicon: {r['lexicon_reason']}")
                parts.append(f'<div class="zoomrow"><img class="zoom" src="data:image/png;base64,{b64png(extra_zoom)}" alt="vowel zoom with detected marks"><div class="inkcap">{esc(caption)}</div></div>')
        parts.append('<table class="w">')
        for label, content in (
            ('Google', highlighted_line(line['google'], r['word_index'])),
            ('Human (test reference)', highlighted_human(line, r)),
            ('Tool', highlighted_line(line['google'], r['word_index'], r['corrected_token']))):
            parts.append(f'<tr><th>{label}</th><td>{content}</td></tr>')
        outcome = {'correct': '= human', 'google_right': 'Google was right', 'both_wrong': 'both wrong', 'unknown': 'unknown'}[r['outcome']]
        color = 'ok' if r['outcome'] == 'correct' else 'bad'
        parts.append(f'</table><div class="row"><span class="pill">{r["stage"]}</span> '
                     f'<span class="pill">{r["decision"]["column"]}</span> <span class="pill {color}">{outcome}</span></div></div>')
    parts.append('</main></body></html>')
    return '\n'.join(parts)
