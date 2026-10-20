import json, sys
d = json.load(open(sys.argv[1])); OUT = sys.argv[2]
def chart_dev(R):
    G = R['_grid']; M = R['_M']; c0, c1 = R['column_x']
    W, H, pad = 900, 300, 40
    ymin, ymax = -50, 20
    X = lambda x: pad + (x - c0) / (c1 - c0) * (W - 2 * pad)
    Y = lambda y: pad / 2 + (y - ymin) / (ymax - ymin) * (H - pad)
    parts = [f'<svg viewBox="0 0 {W} {H}" class="ch" role="img" aria-label="departure from straight per line">']
    for v in range(ymin, ymax + 1, 10):
        parts.append(f'<line x1="{pad}" x2="{W - pad}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{pad - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for row in M:
        pts = [(X(g), Y(max(ymin, min(ymax, v)))) for g, v in zip(G, row) if v is not None]
        if len(pts) > 1:
            parts.append('<polyline class="ln" points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + '"/>')
    med = []
    for j, g in enumerate(G):
        vals = sorted(r[j] for r in M if r[j] is not None)
        if len(vals) >= max(3, len(M) // 3):          # only where at least a third of the lines are present
            med.append((X(g), Y(max(ymin, min(ymax, vals[len(vals) // 2])))))
    parts.append('<polyline class="med" points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in med) + '"/>')
    for x in range(int(c0 // 250 * 250 + 250), int(c1), 250):
        parts.append(f'<text x="{X(x):.1f}" y="{H - 4}" text-anchor="middle">{x}</text>')
    parts.append('</svg>')
    return ''.join(parts)
def chart_skew(R):
    L = R['lines']; W, H, pad = 900, 220, 40
    y0, y1 = 0, 4523; smin, smax = -2.5, 1.0
    X = lambda y: pad + (y - y0) / (y1 - y0) * (W - 2 * pad)
    Y = lambda s: pad / 2 + (smax - s) / (smax - smin) * (H - pad)
    parts = [f'<svg viewBox="0 0 {W} {H}" class="ch" role="img" aria-label="skew per line down the page">']
    for v in (-2, -1.5, -1, -.5, 0, .5, 1):
        parts.append(f'<line x1="{pad}" x2="{W - pad}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{pad - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}°</text>')
    for l in L:
        parts.append(f'<circle cx="{X(l["y"]):.1f}" cy="{Y(max(smin, min(smax, l["skew_deg"]))):.1f}" r="4" class="pt"><title>{l["box"]}: {l["skew_deg"]}°</title></circle>')
    for y in range(500, 4523, 500):
        parts.append(f'<text x="{X(y):.1f}" y="{H - 4}" text-anchor="middle">y {y}</text>')
    parts.append('</svg>')
    return ''.join(parts)
sec = ''
for name in ('left', 'right'):
    R = d[name]; on_l = R['curving_starts_left']; on_r = R['curving_starts_right']
    sec += f'''<section><h2>{name.capitalize()} column — {R["n_lines"]} lines measured (x {R["column_x"][0]}–{R["column_x"][1]})</h2>
<div class="facts">
<div><b>Skew</b>median {R["skew_deg"]["median"]}°, 10–90 % range {R["skew_deg"]["p10"]}° to {R["skew_deg"]["p90"]}° (sd {R["skew_deg"]["sd"]}°)</div>
<div><b>Straight all the way</b>{R["straight_lines"]} of {R["n_lines"]} lines stay within 4 px of a straight line; {R["curved_lines"]} curve</div>
<div><b>Where curving starts</b>left end: {on_l["n"]} lines, at x ≈ {on_l["median_x"]} (half of them within {on_l["iqr_px"]} px of each other); right end: {on_r["n"]} lines, at x ≈ {on_r["median_x"]} (IQR {on_r["iqr_px"]} px)</div>
<div><b>Same curve shape?</b>each line's curve (skew removed) differs from the column's median shape by {R["shape_rms_vs_column_px"]["median"]} px rms (median line; worst {R["shape_rms_vs_column_px"]["max"]} px)</div>
</div>
<h3>Every line's departure from a straight line (skew removed), px — grey: one line each; dark: the column's median shape</h3>
<div class="scroll">{chart_dev(R)}</div>
<h3>Skew of every line, down the page</h3>
<div class="scroll">{chart_skew(R)}</div></section>'''
html = f'''<title>Column Line Geometry</title>
<style>
:root {{ --bg: #f4f5f6; --fg: #1b1f24; --muted: #5b6570; --rule: #d5dbe0; --surface: #fff; --ln: #8c96a0; --med: #0d6e72; --pt: #2c5bb0; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #12171c; --fg: #e3e8ed; --muted: #98a3ad; --rule: #2b343d; --surface: #1a222a; --ln: #5d6873; --med: #4db5b8; --pt: #86a9ee; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #12171c; --fg: #e3e8ed; --muted: #98a3ad; --rule: #2b343d; --surface: #1a222a; --ln: #5d6873; --med: #4db5b8; --pt: #86a9ee; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, -apple-system, sans-serif; }}
main {{ max-width: 980px; margin: 0 auto; padding-inline: 16px; padding-block: 20px 48px; display: grid; gap: 22px; }}
h1 {{ font-size: 1.35rem; margin: 0; }} h2 {{ font-size: 1.1rem; margin: 0; }} h3 {{ font-size: .85rem; font-weight: 500; color: var(--muted); margin: 6px 0 0; }}
p {{ margin: 0; max-width: 75ch; color: var(--muted); }}
section {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 14px; display: grid; gap: 8px; }}
.facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px 20px; font-size: .9rem; }}
.facts b {{ display: block; font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
.scroll {{ overflow-x: auto; }} .ch {{ width: 100%; min-width: 560px; height: auto; }}
.ch text {{ font: 11px ui-monospace, Menlo, monospace; fill: var(--muted); }} .grid {{ stroke: var(--rule); }}
.ln {{ fill: none; stroke: var(--ln); stroke-width: 1; opacity: .7; }} .med {{ fill: none; stroke: var(--med); stroke-width: 3; }} .pt {{ fill: var(--pt); }}
</style>
<main><h1>Do the lines of a column share their geometry?</h1>
<p>Page s2-49598b2e848ab1f0ee1e-p00001. Every line fitted on its own (its baseline letters, a smooth curve), separately for the two columns. Skew = the slope of a straight line through the line's central 60 %; departure = how far the line's own curve leaves that straight line; curving starts where the departure first exceeds 4 px. Negative departure = the line rises (image rows go up). 2 of 91 lines could not be fitted (no baseline letters found from their box) and are left out.</p>
{sec}</main>'''
open(OUT, 'w').write(html)
