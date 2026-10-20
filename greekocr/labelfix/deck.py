"""The owner's review deck: static HTML, one batch per rule, yes / no / uncertain per card.

    python -m greekocr.labelfix.deck --candidates docs/records/labelfix/candidates_train_sample.jsonl \
        --controls docs/records/labelfix/validation_candidates_s0_strict.jsonl --out docs/records/labelfix/review_deck

Blinding: a card shows ONE reading of the boxed word and asks whether the print reads exactly
so. Which reading is shown (the proposed correction or Google's label) is drawn at random per
card (SHOW_MODEL_SHARE of the cards show the correction) and never displayed; control cards
from the three-way lines are mixed in: negative controls show a reading the human
transcription contradicts, positive controls show the human reading. The summary page
computes, per rule, precision on the cards that showed the correction (with the exact 95 %
lower bound), the yes-rate on Google-shown cards, and the owner's false-yes rate on negative
controls. Decisions live in localStorage and can be downloaded as JSON.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random

from PIL import Image

from .rules import RULES
from .text import strip_marks

SHOW_MODEL_SHARE = 0.7
CONTEXT_CHARS = 2
SCALE = 3


def card_image(c: dict, out_png: Path) -> dict:
    """Native-pixel crop of the word with ±CONTEXT_CHARS characters; returns the box geometry."""
    im = Image.open(c['crop_path']).convert('L')
    w, h = im.size
    ww = c.get('word_window') or c.get('cluster_window') or [0, w]
    n_chars = max(1, len(strip_marks(c['model_core'])))
    cw = max(4.0, (ww[1] - ww[0]) / n_chars)
    x0 = int(max(0, ww[0] - CONTEXT_CHARS * cw))
    x1 = int(min(w, ww[1] + CONTEXT_CHARS * cw))
    if x1 - x0 < 8:
        x0, x1 = 0, w
    region = im.crop((x0, 0, x1, h))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    region.save(out_png)
    ink = c.get('ink') or {}
    box = ink.get('body') or c.get('cluster_window') or ww
    return dict(x0=x0, width=x1 - x0, height=h, box=[round(box[0] - x0, 1), round(box[1] - x0, 1)],
                word=[round(ww[0] - x0, 1), round(ww[1] - x0, 1)])


def stratified(cands: list, n: int, rng: random.Random) -> list:
    by_wave = defaultdict(list)
    for c in cands:
        by_wave[c['wave']].append(c)
    for v in by_wave.values():
        rng.shuffle(v)
    out = []
    waves = sorted(by_wave)
    while len(out) < n and any(by_wave.values()):
        for w in waves:
            if by_wave[w] and len(out) < n:
                out.append(by_wave[w].pop())
    return out


def build(candidates: list[Path], controls: list[Path], out: Path, per_rule: int, n_neg: int, n_pos: int, seed: int,
          append_rules: tuple = ()) -> dict:
    """Build the deck. With `append_rules`, the existing `deck_data.js` is kept byte-for-byte for the
    batches it already has (the owner's answers are keyed by card id) and only batches for
    `append_rules` are added, drawn with their own random stream."""
    existing = None
    n_prev = 0
    if append_rules:
        existing = json.loads((out / 'deck_data.js').read_text().split('=', 1)[1].rstrip(';\n'))
        rng = random.Random(seed + 1)
    else:
        rng = random.Random(seed)
    accepted = defaultdict(list)
    for path in candidates:
        for line in open(path, encoding='utf-8'):
            c = json.loads(line)
            if c['decision']['accept']:
                accepted[c['decision']['rule']].append(c)
            elif c['decision'].get('ink_decisive'):
                # pass-4 variant: lexicon-neutral candidates the mark-shape classifier decides; its own batch
                accepted['ink_decisive'].append(c)
    neg, pos = defaultdict(list), defaultdict(list)
    for path in controls:
        for line in open(path, encoding='utf-8'):
            c = json.loads(line)
            if c.get('outcome') in ('google_right', 'both_wrong') and not c['decision']['reason'].startswith('excluded'):
                neg[c['decision']['rule']].append(c)
                if c['decision'].get('lexicon_neutral'):
                    neg['ink_decisive'].append(c)
            elif c.get('outcome') == 'correct' and c['decision']['accept']:
                pos[c['decision']['rule']].append(c)
            elif c.get('outcome') == 'correct' and c['decision'].get('ink_decisive'):
                pos['ink_decisive'].append(c)
    cards_dir = out / 'cards'
    batches = []
    counts = {}
    carded = set()
    if existing:
        batches = list(existing['batches'])
        counts = dict(existing['counts'])
        carded = {(c['line_id'], c['word_index']) for b in batches for c in b['cards']}
    for rule in list(RULES) + ['ink_decisive']:
        if existing and rule not in append_rules:
            continue
        pool = accepted.get(rule, [])
        batch_name = rule
        if existing:
            # a second batch for a rule that already has one: only candidates never carded before
            pool = [c for c in pool if (c['line_id'], c['word_index']) not in carded]
            n_prev = sum(1 for b in batches if b['rule'] == rule or b['rule'].startswith(rule + '#'))
            batch_name = rule if n_prev == 0 else f'{rule}#{n_prev + 1}'
            if not pool:
                continue
        chosen = stratified(pool, per_rule, rng)
        if not chosen and not neg.get(rule) and not pos.get(rule):
            continue
        cards = []
        for c in chosen:
            show_model = rng.random() < SHOW_MODEL_SHARE
            cards.append((c, 'sample', show_model))
        for c in rng.sample(neg.get(rule, []), min(n_neg, len(neg.get(rule, [])))):
            cards.append((c, 'neg', True))        # shows the model's form, which the human text contradicts
        for c in rng.sample(pos.get(rule, []), min(n_pos, len(pos.get(rule, [])))):
            cards.append((c, 'pos', True))        # shows the model's form, which equals the human text
        rng.shuffle(cards)
        recs = []
        for k, (c, kind, show_model) in enumerate(cards):
            cid = f'{batch_name}-{k:03d}'
            png = cards_dir / batch_name.replace('#', '_') / f'{cid}.png'
            geo = card_image(c, png)
            shown = c['corrected_nfc'] if show_model else c['google_nfc']
            recs.append(dict(id=cid, rule=rule, png=f'cards/{batch_name.replace("#", "_")}/{cid}.png', shown=shown, kind=kind,
                             shown_is_model=show_model, geo=geo, line_id=c['line_id'], wave=c['wave'],
                             word_index=c['word_index'], crop=str(Path(c['crop_path']).name),
                             google=c['google_nfc'], model=c['corrected_nfc'], human=c.get('human_nfc'),
                             reason=c['decision']['reason'][:120]))
        if existing and n_prev:
            # a second batch carries no controls (they were already shown in the first batch)
            cards = [x for x in cards if x[1] == 'sample']
            recs = [r for r in recs if r['kind'] == 'sample']
        batches.append(dict(rule=batch_name, cards=recs))
        counts[batch_name] = dict(sample=len(chosen), neg=sum(1 for c in cards if c[1] == 'neg'),
                                  pos=sum(1 for c in cards if c[1] == 'pos'), available=len(pool))
    (out / 'deck_data.js').write_text('window.DECK = ' + json.dumps(dict(batches=batches, counts=counts,
                                       show_model_share=SHOW_MODEL_SHARE, scale=SCALE), ensure_ascii=False) + ';\n')
    (out / 'index.html').write_text(INDEX_HTML)
    (out / 'README.md').write_text(README.format(rules=', '.join(counts), per_rule=per_rule, n_neg=n_neg, n_pos=n_pos,
                                                 table='\n'.join(f'| {r} | {v["available"]} | {v["sample"]} | {v["neg"]} | {v["pos"]} |' for r, v in counts.items())))
    return counts


INDEX_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Label-correction review deck</title>
<style>
body{font-family:-apple-system,Helvetica,Arial,sans-serif;margin:0;background:#f4f4f2;color:#222}
header{padding:10px 18px;background:#fff;border-bottom:1px solid #ddd;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header a{color:#0b5cad;text-decoration:none;margin-right:8px}
#card{max-width:1200px;margin:24px auto;padding:18px;background:#fff;border:1px solid #ddd;border-radius:6px}
.imgwrap{position:relative;display:inline-block;overflow-x:auto;max-width:100%;background:#fff}
.imgwrap img{image-rendering:pixelated;display:block}
.box{position:absolute;border:2px solid #d00;box-sizing:border-box;pointer-events:none}
.word{position:absolute;border-bottom:2px solid #28a;pointer-events:none}
.shown{font-size:44px;margin:16px 0 4px;font-family:"Times New Roman",Times,serif}
.q{font-size:18px;color:#444}
.keys button{font-size:20px;padding:8px 22px;margin:8px 10px 0 0;border-radius:6px;border:1px solid #999;background:#fafafa;cursor:pointer}
.keys button.sel{background:#dfe;border-color:#2a6}
.small{color:#777;font-size:13px}
table{border-collapse:collapse;margin:12px 0}td,th{border:1px solid #ccc;padding:4px 10px;text-align:right}th:first-child,td:first-child{text-align:left}
#summary{max-width:1100px;margin:24px auto;padding:18px;background:#fff;border:1px solid #ddd;border-radius:6px;display:none}
</style></head><body>
<header><strong>Label-correction review</strong>
<span id="nav"></span>
<span id="progress" class="small"></span>
<button onclick="showSummary()">Summary</button>
<button onclick="download()">Download decisions (JSON)</button>
<label class="small">zoom <select id="zoom" onchange="render()"><option>2</option><option selected>3</option><option>4</option></select>×</label>
<span id="netstate" class="small"></span>
</header>
<div id="card"></div>
<div id="summary"></div>
<script src="deck_data.js"></script>
<script>
const D = window.DECK; let bi = 0, ci = 0;
const KEY = 'labelfix-deck-v1';
let dec = {}; try { dec = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { dec = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(dec)); } catch (e) {} }
function nav(){
  const n = document.getElementById('nav'); n.innerHTML = '';
  D.batches.forEach((b, i) => { const a = document.createElement('a'); a.href = '#'; a.textContent = b.rule + ' (' + done(i) + '/' + b.cards.length + ')';
    if (i === bi) a.style.fontWeight = 'bold'; a.onclick = (e) => { e.preventDefault(); bi = i; ci = firstOpen(i); render(); }; n.appendChild(a); });
}
function done(i){ return D.batches[i].cards.filter(c => dec[c.id]).length; }
function firstOpen(i){ const cs = D.batches[i].cards; for (let k = 0; k < cs.length; k++) if (!dec[cs[k].id]) return k; return 0; }
function render(){
  document.getElementById('summary').style.display = 'none'; document.getElementById('card').style.display = 'block';
  nav(); const b = D.batches[bi]; const c = b.cards[ci]; const z = parseInt(document.getElementById('zoom').value);
  const g = c.geo; const d = dec[c.id] ? dec[c.id].d : null;
  document.getElementById('progress').textContent = 'batch ' + b.rule + ': card ' + (ci + 1) + ' of ' + b.cards.length + ' — keys: y = reads exactly as shown, n = does not, u = uncertain / neither; ← → to move';
  document.getElementById('card').innerHTML =
    '<div class="imgwrap" style="width:' + (g.width * z) + 'px;height:' + (g.height * z) + 'px">' +
    '<img src="' + c.png + '" width="' + (g.width * z) + '" height="' + (g.height * z) + '">' +
    '<div class="box" style="left:' + (g.box[0] * z) + 'px;top:0;width:' + ((g.box[1] - g.box[0]) * z) + 'px;height:' + (g.height * z) + 'px"></div>' +
    '<div class="word" style="left:' + (g.word[0] * z) + 'px;top:' + (g.height * z - 3) + 'px;width:' + ((g.word[1] - g.word[0]) * z) + 'px;height:0"></div></div>' +
    '<div class="shown">' + c.shown + '</div>' +
    '<div class="q">Does the underlined word read <em>exactly</em> as shown (look at the boxed letter and its marks)?</div>' +
    '<div class="keys"><button class="' + (d === 'y' ? 'sel' : '') + '" onclick="answer(\'y\')">y — yes</button>' +
    '<button class="' + (d === 'n' ? 'sel' : '') + '" onclick="answer(\'n\')">n — no</button>' +
    '<button class="' + (d === 'u' ? 'sel' : '') + '" onclick="answer(\'u\')">u — uncertain / neither</button></div>' +
    '<div class="small">' + c.id + ' · ' + c.wave + ' · ' + c.crop + '</div>';
}
const SERVED = location.protocol.startsWith('http');
function post(c, v, t){ if (!SERVED) return;
  fetch('/decision', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: c.id, rule: c.rule, line_id: c.line_id, word_index: c.word_index, shown: c.shown, shown_is_model: c.shown_is_model, kind: c.kind, google: c.google, proposed: c.model, decision: v, time: t }) })
    .then(r => { document.getElementById('netstate').textContent = r.ok ? 'saved to server' : 'server error ' + r.status; })
    .catch(() => { document.getElementById('netstate').textContent = 'server unreachable (kept in browser)'; }); }
function answer(v){ const c = D.batches[bi].cards[ci]; const t = new Date().toISOString(); dec[c.id] = { d: v, t: t }; save(); post(c, v, t);
  if (ci + 1 < D.batches[bi].cards.length) ci++; render(); }
if (SERVED) { fetch('/decisions').then(r => r.json()).then(rows => { let n = 0; rows.forEach(r => { if (r.id && r.decision && !dec[r.id]) { dec[r.id] = { d: r.decision, t: r.time || '' }; n++; } }); if (n) { save(); render(); }
  document.getElementById('netstate').textContent = 'server capture on (' + rows.length + ' on disk)'; }).catch(() => {}); }
else { document.getElementById('netstate').textContent = 'opened from disk: answers stay in this browser (serve with deck_serve for automatic capture)'; }
document.addEventListener('keydown', (e) => { if (e.target.tagName === 'SELECT') return;
  if (e.key === 'y' || e.key === 'n' || e.key === 'u') answer(e.key);
  else if (e.key === 'ArrowRight' && ci + 1 < D.batches[bi].cards.length) { ci++; render(); }
  else if (e.key === 'ArrowLeft' && ci > 0) { ci--; render(); } });
function lb95(k, n){ if (n === 0 || k === 0) return 0; let lo = 0, hi = 1;   // exact one-sided bound: P(X >= k | p) = 0.05
  const tail = (p) => { let s = 0; for (let x = k; x <= n; x++) s += Math.exp(lchoose(n, x) + x * Math.log(p) + (n - x) * Math.log(1 - p || 1e-300)); return s; };
  for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (tail(m) < 0.05) lo = m; else hi = m; } return lo; }
function lchoose(n, k){ return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1); }
function lgamma(z){ const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - lgamma(1 - z); z -= 1; let x = c[0]; for (let i = 1; i < g + 2; i++) x += c[i] / (z + i); const t = z + g + 0.5; return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x); }
function pct(k, n){ return n ? (100 * k / n).toFixed(1) + '%' : '-'; }
function showSummary(){
  document.getElementById('card').style.display = 'none'; const s = document.getElementById('summary'); s.style.display = 'block';
  let h = '<h2>Precision per rule from your decisions</h2><p class="small">Correction cards = cards that showed the proposed correction; precision = y / (y + n) on those, LB95 = exact one-sided 95% lower bound. Google-shown cards showed the existing label instead (a "y" there means the label was right, i.e. the correction would have been wrong). Negative controls showed a reading the human transcription contradicts: a "y" is a false yes. Positive controls showed the human reading.</p>';
  h += '<table><tr><th>rule</th><th>correction cards</th><th>y</th><th>n</th><th>u</th><th>precision</th><th>LB95</th><th>Google-shown: y / n / u</th><th>neg controls: false-yes / n</th><th>pos controls: y / n</th><th>open</th></tr>';
  D.batches.forEach(b => { const m = { y: 0, n: 0, u: 0 }, g = { y: 0, n: 0, u: 0 }, ng = { y: 0, n: 0 }, ps = { y: 0, n: 0 }; let open = 0;
    b.cards.forEach(c => { const d = dec[c.id]; if (!d) { open++; return; }
      if (c.kind === 'neg') { if (d.d === 'y') ng.y++; else if (d.d === 'n') ng.n++; }
      else if (c.kind === 'pos') { if (d.d === 'y') ps.y++; else if (d.d === 'n') ps.n++; }
      else if (c.shown_is_model) m[d.d]++; else g[d.d]++; });
    h += '<tr><td>' + b.rule + '</td><td>' + (m.y + m.n + m.u) + '</td><td>' + m.y + '</td><td>' + m.n + '</td><td>' + m.u + '</td><td>' + pct(m.y, m.y + m.n) + '</td><td>' + (100 * lb95(m.y, m.y + m.n)).toFixed(1) + '%</td><td>' + g.y + ' / ' + g.n + ' / ' + g.u + '</td><td>' + ng.y + ' / ' + ng.n + '</td><td>' + ps.y + ' / ' + ps.n + '</td><td>' + open + '</td></tr>'; });
  s.innerHTML = h + '</table><p><button onclick="render()">Back to cards</button></p>';
}
function download(){ const rows = []; D.batches.forEach(b => b.cards.forEach(c => { const d = dec[c.id]; rows.push({ id: c.id, rule: c.rule, line_id: c.line_id, word_index: c.word_index, shown: c.shown, shown_is_model: c.shown_is_model, kind: c.kind, google: c.google, proposed: c.model, decision: d ? d.d : null, time: d ? d.t : null }); }));
  const blob = new Blob([JSON.stringify(rows, null, 1)], { type: 'application/json' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'labelfix_decisions.json'; a.click(); }
render();
</script></body></html>
'''

README = '''# Label-correction review deck

Preferred: `python -m greekocr.labelfix.deck_serve docs/records/labelfix/review_deck` and open
http://127.0.0.1:8765/index.html — every answer is then written immediately to
`docs/records/labelfix/decisions/<date>.jsonl` (no download needed; the header shows "server capture on").
Fallback: open `index.html` from disk (double-click; nothing is fetched); answers stay in the
browser's localStorage, which `python -m greekocr.labelfix.pull_firefox` can read from the Firefox
profile, or use "Download decisions". One batch per
rule: {rules}. Each card shows the native pixels of the line around one word (zoom 2–4×, pixel-exact),
the disputed letter boxed in red, the word underlined in blue, and ONE reading of that word.
Answer whether the print reads exactly as shown: `y` / `n` / `u` (uncertain, or neither reading).
Arrow keys move; decisions are saved in the browser (localStorage) as you go; "Download decisions"
writes `labelfix_decisions.json`; "Summary" computes precision per rule from your answers.

A batch of 100 cards takes about 6–10 minutes (3–5 s per card).

## What is hidden from you, and why

The reading shown is the proposed correction on about {per_rule} × 70 % of the cards of a batch and
the existing Google label on the rest, drawn at random and never indicated. Mixed in are control
cards from the Wikisource three-way lines: up to {n_neg} negative controls (a reading the human
transcription contradicts) and {n_pos} positive controls (the human reading). The summary separates
them. So a `y` on a Google-shown card is not an error, and the negative controls measure your
false-yes rate.

| rule | accepted candidates available | correction/label cards | negative controls | positive controls |
|---|---:|---:|---:|---:|
{table}

## What the result means

Corrected labels are **derived**, not truth: they are Google's label rewritten where our
recogniser, a lexicon and the ink agree. A precision estimate from this deck is a check on that
derivation, and a test instrument whose labels were corrected by a model cannot be used to judge
that model (or any model trained with it): it would score the model's own habits as correct.
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidates', type=Path, nargs='+', required=True)
    ap.add_argument('--controls', type=Path, nargs='*', default=[])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--per-rule', type=int, default=100)
    ap.add_argument('--neg', type=int, default=20)
    ap.add_argument('--pos', type=int, default=10)
    ap.add_argument('--seed', type=int, default=20261016)
    ap.add_argument('--append', nargs='*', default=None, help='keep the existing deck and add batches for these rules only')
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    counts = build(a.candidates, a.controls, a.out, a.per_rule, a.neg, a.pos, a.seed, tuple(a.append or ()))
    print(json.dumps(counts))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
