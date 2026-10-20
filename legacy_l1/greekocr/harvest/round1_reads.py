"""Offline T17 DocAI-line harvest and self-contained numbered owner reviews."""
from __future__ import annotations

import base64
from collections import Counter
from difflib import SequenceMatcher
import html
import io
from pathlib import Path
import re
import statistics
import unicodedata as ud

from PIL import Image, ImageDraw, ImageFont

from .core import list_return
from .montage_controls import letters_marks
from .page_reads import assign_page_lines, polygon_overlap


def letter_count(text):
    return sum(ud.category(c).startswith('L') for c in letters_marks(text))


def line_tier(docai, vision, *, usable=True):
    """Strict NFD, then unchanged T14b L/M agreement; DocAI supplies labels."""
    if usable and docai.strip() and vision.strip() and letters_marks(docai):
        if ud.normalize('NFD', docai) == ud.normalize('NFD', vision):
            return dict(tier=1, label=docai)
        if letters_marks(docai) == letters_marks(vision):
            return dict(tier=2, label=docai)
    return dict(tier=3, label=None)


def _polygon(box):
    x0, y0, x1, y1 = box
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def attach_vision(docai, vision):
    """T15 geometry first; unique mutual text match only among nearby ambiguous boxes.

    Fallback: L/M SequenceMatcher >=.75, >=.10 margin on both sides, >=3
    letters, touching boxes with >=50% shorter-width overlap. Never share a
    Vision line or silently split a merged transcription. Ties stay withheld.
    """
    targets = [dict(id=str(i), polygon=_polygon(d['bbox'])) for i, d in enumerate(docai)]
    geometry = assign_page_lines(vision, targets)
    results, used = [], set()
    for i, d in enumerate(docai):
        a = geometry['targets'][str(i)]
        good = not a['rejected'] and not a['lost']
        indices = [p['line_index'] for p in a['pieces']]
        if good:
            used.update(indices)
        results.append(dict(text=a['text'], usable=good, method='box_overlap' if good else 'unresolved',
                            vision_indices=indices, flags=list(a['flags']) +
                            (['vision_merged_touch'] if a['merged'] else []) +
                            (['vision_lost'] if a['lost'] else []), alignment=None))
    scores = {}
    for di, (d, result) in enumerate(zip(docai, results)):
        if result['usable'] or letter_count(d['text']) < 3:
            continue
        for vi, v in enumerate(vision):
            if vi in used or letter_count(v['text']) < 3:
                continue
            overlap = polygon_overlap(v['bbox'], targets[di]['polygon'])
            if not overlap['touch'] or overlap['horizontal_fraction'] < .5:
                continue
            parsed = list_return([v])
            if parsed['rejected']:
                continue
            score = SequenceMatcher(None, letters_marks(d['text']), letters_marks(v['text']), autojunk=False).ratio()
            scores[di, vi] = score
    matches = []
    for (di, vi), score in scores.items():
        row_other = max((s for (d, v), s in scores.items() if d == di and v != vi), default=0.)
        col_other = max((s for (d, v), s in scores.items() if v == vi and d != di), default=0.)
        if score >= .75 and score-row_other >= .10-1e-12 and score-col_other >= .10-1e-12:
            matches.append((di, vi, score, row_other, col_other))
    for di, vi, score, row_other, col_other in matches:
        if vi in used:
            raise AssertionError('Vision box reuse')
        used.add(vi)
        results[di].update(text=vision[vi]['text'].strip(), usable=True, method='text_alignment',
                           vision_indices=[vi], alignment=dict(score=score, row_runner_up=row_other, column_runner_up=col_other),
                           flags=results[di]['flags'] + ['text_alignment_fallback'])
    return dict(results=results, geometry=geometry, fallback_scores=[dict(docai_index=d, vision_index=v, score=s)
                for (d, v), s in sorted(scores.items())], unassigned_vision_indices=sorted(set(range(len(vision)))-used))


def symbol_confidences(document):
    """Use original DocAI text-anchor custody, independent of overlapping AABBs."""
    page = document['pages'][0]
    symbols = page.get('symbols', [])
    output = []
    for line in page.get('lines', []):
        spans = [(int(s.get('startIndex', 0)), int(s['endIndex']))
                 for s in line.get('layout', {}).get('textAnchor', {}).get('textSegments', [])]
        indices = []
        for i, symbol in enumerate(symbols):
            ss = symbol.get('layout', {}).get('textAnchor', {}).get('textSegments', [])
            if ss and all(any(a <= int(s.get('startIndex', 0)) < int(s['endIndex']) <= b for a, b in spans) for s in ss):
                indices.append(i)
        values = [symbols[i]['layout'].get('confidence') for i in indices]
        values = [float(c) for c in values if c is not None]
        output.append(dict(symbol_indices=indices, symbol_confidences=values, symbol_count=len(values),
                           mean=statistics.mean(values) if values else None,
                           minimum=min(values) if values else None))
    return output


def cohort_summary(pages, records):
    rows = [r for r in records if r['counted']]
    tiers = Counter(r['tier'] for r in rows)
    symbols = [c for r in rows for c in r['symbol_confidences']]
    return dict(pages=len(pages), records=len(records), lines=len(rows), short_lines=len(records)-len(rows),
                tier1=tiers[1], tier2=tiers[2], tier3=tiers[3], labels=tiers[1]+tiers[2],
                label_yield_pct=100*(tiers[1]+tiers[2])/len(rows) if rows else 0.,
                mean_confidence=statistics.mean(symbols) if symbols else None, symbol_count=len(symbols),
                attachment_counts=dict(Counter(r['attachment_method'] for r in rows)),
                geometry_only_labels=sum(r['tier'] in (1, 2) and r['attachment_method'] == 'box_overlap' for r in rows),
                fallback_labels=sum(r['tier'] in (1, 2) and r['attachment_method'] == 'text_alignment' for r in rows))


def median_page(pages, records):
    """Lower middle page ranked by counted label-yield fraction, ties by page/id."""
    ranked = sorted(pages, key=lambda p: (cohort_summary([p], [r for r in records if r['page_id'] == p['id']])['label_yield_pct'], p['page'], p['id']))
    return ranked[(len(ranked)-1)//2]


def book_folder(page):
    # Keep UTF-8 component comfortably below Finder's 255-byte limit.
    title = re.sub(r'[^\w .-]', '_', page['title'], flags=re.UNICODE)
    while len(title.encode('utf-8')) > 140:
        title = title[:-1]
    return f"{page['year']}_{title.strip().replace(' ', '_')}_{page['key']}"


def numbered_image(image_path, records, *, max_size=None):
    with Image.open(image_path) as source:
        image = source.convert('RGB')
    native = image.size
    if max_size:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    sx, sy = image.width/native[0], image.height/native[1]
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=14 if max_size else 19)
    for r in records:
        x0, y0, x1, y1 = r['bbox']
        x0, y0, x1, y1 = x0*sx, y0*sy, x1*sx, y1*sy
        draw.rectangle((x0, y0, x1, y1), outline='#008d42', width=2)
        value = str(r['line_number'])
        bounds = draw.textbbox((0, 0), value, font=font)
        width, height = bounds[2]-bounds[0]+6, bounds[3]-bounds[1]+4
        tx, ty = max(0, x0-width-2), max(0, y0)
        draw.rectangle((tx, ty, tx+width, ty+height), fill='#008d42')
        draw.text((tx+3, ty+2-bounds[1]), value, font=font, fill='white')
    return image


def page_text(page, records):
    lines = [f"{page['year']} · {page['title']}", f"page {page['page']} | {page['id']} | native {page['width']}×{page['height']} | 200 dpi",
             'Green numbered boxes are DocAI layouts. Tier 1 exact NFD; tier 2 T14b letters+marks; tier 3 unlabelled.', '']
    for r in records:
        lines += [f"{r['line_number']:03d} | tier {r['tier']} | {'counted' if r['counted'] else 'short: excluded from counts'} | {r['attachment_method']} | confidence {r['confidence']}",
                  'DocAI: ' + r['docai_text'], 'Vision: ' + r['vision_text'], 'Flags: ' + ', '.join(r['flags']), '']
    return '\n'.join(lines)


def review_html(decade, selected):
    cards = []
    for page, rows, image_path in selected:
        image = numbered_image(image_path, rows, max_size=(1200, 1600))
        stream = io.BytesIO()
        image.save(stream, format='WEBP', quality=86)
        encoded = base64.b64encode(stream.getvalue()).decode()
        line_cards = []
        for r in rows:
            d, v = html.escape(r['docai_text']), html.escape(r['vision_text'])
            if r['tier'] == 1:
                readings = '<p>'+d+'</p>'
            elif r['tier'] == 2:
                readings = '<p><b>DocAI</b> '+d+'</p><details><summary>Vision reading</summary><p>'+v+'</p></details>'
            else:
                readings = '<p><b>DocAI</b> '+d+'</p><p><b>Vision</b> '+(v or '∅')+'</p>'
            excluded = ' · fewer than 3 letters; excluded' if not r['counted'] else ''
            confidence = '—' if r['confidence'] is None else f"{r['confidence']:.3f}"
            line_cards.append(f'<li class="tier{r["tier"]}" data-line="{r["line_number"]}"><div class="meta">{r["line_number"]} · tier {r["tier"]} · confidence {confidence} · {r["attachment_method"]}{excluded}</div>{readings}</li>')
        counts = cohort_summary([page], rows)
        cards.append(f'<section data-book="{html.escape(page["book"], quote=True)}" data-page="{page["page"]}"><h2>{page["year"]} · {html.escape(page["title"])}</h2>'
                     f'<p>Median-yield page {page["page"]} · {counts["lines"]} counted lines · {counts["label_yield_pct"]:.1f}% labels</p>'
                     f'<div class="pair"><div class="page"><img width="{image.width}" height="{image.height}" alt="Page {page["page"]} with numbered green DocAI boxes" src="data:image/webp;base64,{encoded}"></div><ol>{"".join(line_cards)}</ol></div></section>')
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+f'<title>T17 · {decade}s owner review</title>'+'''<style>
*{box-sizing:border-box}body{font:16px system-ui,sans-serif;margin:24px auto;padding:0 20px;max-width:1600px;background:#f7f7f5;color:#202522}h1,h2{overflow-wrap:anywhere}h2{font-size:20px}section{background:white;padding:20px;margin:24px 0;border:1px solid #d8ded9;border-radius:8px}.pair{display:grid;grid-template-columns:minmax(0,46fr) minmax(0,54fr);gap:20px;align-items:start}.page{position:sticky;top:12px}img{display:block;width:100%;height:auto}ol{padding:0;margin:0;list-style:none;min-width:0}li{border-left:4px solid;padding:8px 12px;margin-bottom:8px;overflow-wrap:anywhere}li p{margin:6px 0;white-space:pre-wrap;line-height:1.5}.tier1{border-color:#168342;background:#edf8ef}.tier2{border-color:#d08b00;background:#fff7e3}.tier3{border-color:#c93b3b;background:#fff0f0}.meta{font:12px system-ui;color:#4a514e}summary{cursor:pointer;font-size:13px}a{color:#166941}@media(max-width:760px){body{padding:0 10px;margin:12px auto}section{padding:12px}.pair{grid-template-columns:1fr}.page{position:static}}
</style></head><body>'''+f'<h1>T17 · {decade}s</h1><p>One median-yield page for each of {len(selected)} books. Green boxes: native DocAI line layouts. Green tier 1: exact NFD; amber tier 2: T14b letters+marks agree, label from DocAI; red tier 3: both readings, no label. Agreement is provisional; owner review remains pending.</p>'+''.join(cards)+'</body></html>'
