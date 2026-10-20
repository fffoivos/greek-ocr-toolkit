"""Offline native-page polygon assignment and blinded review construction (T15)."""
from __future__ import annotations

import base64
from collections import Counter
import copy
import html
import io
import math
from pathlib import Path
import random
import statistics
from typing import Any, Iterable

from PIL import Image
import numpy as np

from .core import list_return, normalise, tier
from .montage import compare_nfd, response_lines, response_symbols
from .montage_controls import letters_marks

__all__ = ["polygon_overlap", "assign_page_lines", "assign_page_symbols",
           "page_summary", "build_blind_review"]


def _response_geometry(engine, raw, native_size):
    """Map provider-preprocessed DocAI geometry back with recorded matrices.

    No raw response is mutated. Invert the composed OpenCV affine/projective
    transforms on reported polygon vertices before forming native line boxes;
    never scale dimensions heuristically or invert an already-unioned AABB.
    """
    frame = dict(native_size=list(native_size), returned_size=list(native_size),
                 converted=False, transforms=[], inverse_to_native=None)
    if engine != 'docai':
        return dict(lines=response_lines(engine, raw, native_size),
                    symbols=response_symbols(engine, raw, native_size), coordinate_frame=frame)
    page = raw['document']['pages'][0]
    if len(raw['document']['pages']) != 1:
        raise ValueError('one DocAI page required')
    dimension = page.get('dimension', {})
    returned_size = (dimension.get('width', native_size[0]), dimension.get('height', native_size[1]))
    frame['returned_size'] = list(returned_size)
    transforms = page.get('transforms', [])
    if not transforms:
        if tuple(returned_size) != tuple(native_size):
            raise ValueError('different DocAI frame without a recorded transform')
        return dict(lines=response_lines(engine, raw, native_size),
                    symbols=response_symbols(engine, raw, native_size), coordinate_frame=frame)
    total = np.eye(3)
    for item in transforms:
        if item['type'] not in (5, 6) or (item['rows'], item['cols']) not in ((2, 3), (3, 3)):
            raise ValueError('unsupported DocAI transform matrix')
        data = base64.b64decode(item['data'], validate=True)
        matrix = np.frombuffer(data, dtype='<f4' if item['type'] == 5 else '<f8').reshape(item['rows'], item['cols'])
        if not np.isfinite(matrix).all():
            raise ValueError('nonfinite DocAI matrix')
        if item['rows'] == 2:
            matrix = np.vstack((matrix, [0, 0, 1]))
        total = matrix @ total
        frame['transforms'].append(matrix.tolist())
    try:
        inverse = np.linalg.inv(total)
    except np.linalg.LinAlgError as error:
        raise ValueError('singular DocAI transform') from error
    converted = copy.deepcopy(raw)
    converted_page = converted['document']['pages'][0]
    converted_polygons = set()
    for kind in ('lines', 'paragraphs', 'symbols'):
        for node in converted_page.get(kind, []):
            polygon = node.get('layout', {}).get('boundingPoly', {})
            if id(polygon) in converted_polygons:
                continue
            converted_polygons.add(id(polygon))
            vertices = polygon.get('vertices')
            if not vertices:
                vertices = [dict(x=v.get('x', 0) * returned_size[0], y=v.get('y', 0) * returned_size[1]) for v in polygon.get('normalizedVertices', [])]
            if not vertices:
                continue
            points = np.asarray([[v.get('x', 0), v.get('y', 0), 1.] for v in vertices])
            transformed = (inverse @ points.T).T
            if np.any(np.abs(transformed[:, 2]) < 1e-12):
                raise ValueError('DocAI vertex maps to infinity')
            polygon['vertices'] = [dict(x=float(v[0] / v[2]), y=float(v[1] / v[2])) for v in transformed]
            polygon.pop('normalizedVertices', None)
    frame.update(converted=True, inverse_to_native=inverse.tolist())
    lines = response_lines(engine, converted, native_size)
    symbols = response_symbols(engine, converted, native_size)
    for kind, items in (('lines', lines), ('symbols', symbols)):
        reported = response_lines(engine, raw, returned_size) if kind == 'lines' else response_symbols(engine, raw, returned_size)
        if len(items) != len(reported):
            raise ValueError('coordinate conversion changed response item count')
        for item, original in zip(items, reported):
            item['reported_bbox'] = original['bbox']
    return dict(lines=lines, symbols=symbols, coordinate_frame=frame)


def _clip(points, axis, bound, keep_above):
    result = []
    for previous, current in zip(points[-1:] + points[:-1], points):
        a = previous[axis] >= bound if keep_above else previous[axis] <= bound
        b = current[axis] >= bound if keep_above else current[axis] <= bound
        if a != b:
            fraction = (bound - previous[axis]) / (current[axis] - previous[axis])
            result.append([previous[i] + fraction * (current[i] - previous[i]) for i in (0, 1)])
        if b:
            result.append(current)
    return result


def polygon_overlap(box: list[float], polygon: list[list[float]]) -> dict[str, Any]:
    """Mean vertical box-height overlap with a polygon band over the shared x span.

    Exact polygon clipping integrates vertical overlap for sloping/curved bands.
    Divide by shared x width, then returned box height; this is not the fraction
    of the returned box area (width outside the polygon does not dilute height).
    Horizontal fraction is overlap / shorter projected width. Edge-only contact
    has zero height and is not a touch. Coordinates are native page pixels.
    """
    if len(box) != 4 or not all(math.isfinite(v) for v in box):
        raise ValueError("four finite box coordinates required")
    if len(polygon) < 3 or any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in polygon):
        raise ValueError("finite polygon with at least three vertices required")
    x0, y0, x1, y1 = box
    px0, px1 = min(p[0] for p in polygon), max(p[0] for p in polygon)
    width, height = x1 - x0, y1 - y0
    shared = max(0., min(x1, px1) - max(x0, px0))
    if width <= 0 or height <= 0 or px1 <= px0 or shared <= 0:
        return dict(height_fraction=0., horizontal_fraction=0., touch=False)
    points = polygon
    for axis, bound, above in ((0, x0, True), (0, x1, False), (1, y0, True), (1, y1, False)):
        points = _clip(points, axis, bound, above)
        if not points:
            break
    area = abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(points, points[1:] + points[:1]))) / 2
    return dict(height_fraction=min(1., area / shared / height),
                horizontal_fraction=shared / min(width, px1 - px0), touch=area > 1e-8)


def _page_hits(box, records):
    return {r["id"]: value for r in records
            if (value := polygon_overlap(box, r["polygon"]))["touch"]}


def assign_page_lines(lines: Iterable[dict[str, Any]], records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Assign 70% height/50% shorter-width; any two polygon touches are merged.

    Only supplied records are targets. Merged boxes are withheld, never guessed.
    Zero unique boxes is lost; >=2 is split. Flags are independent. Side-by-side
    pieces use the pilot list_return rule in x order; rejected stacked pieces
    remain LF-separated for inspection. Merged partial readings remain rejected.
    """
    records = list(records)
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("target IDs must be unique")
    groups = {r["id"]: [] for r in records}
    merges = {r["id"]: [] for r in records}
    audit = []
    for index, line in enumerate(lines):
        hits = _page_hits(line["bbox"], records)
        entry = dict(index=index, line=line, overlaps=hits, target_id=None)
        if len(hits) > 1:
            entry["status"] = "merged"
            for ident in hits:
                merges[ident].append(index)
        elif hits:
            ident, overlap = next(iter(hits.items()))
            if overlap["height_fraction"] + 1e-12 >= .70 and overlap["horizontal_fraction"] + 1e-12 >= .50:
                groups[ident].append(dict(line, line_index=index))
                entry.update(status="assigned", target_id=ident)
            else:
                entry["status"] = "unassigned"
        else:
            entry["status"] = "unassigned"
        audit.append(entry)
    targets = {}
    for ident, pieces in groups.items():
        parsed = list_return(pieces)
        text = parsed["text"]
        if parsed["rejected"] and pieces:
            text = "\n".join(p["text"].strip() for p in sorted(pieces, key=lambda p: (p["bbox"][1], p["bbox"][0])))
        merged, lost, split = bool(merges[ident]), not pieces, len(pieces) >= 2
        targets[ident] = dict(text=text, merged=merged, lost=lost, split=split,
            rejected=merged or parsed["rejected"], status="merged" if merged else "lost" if lost else "split" if split else "ok",
            assigned_line_count=len(pieces), merged_line_indices=merges[ident], pieces=pieces,
            flags=parsed["flags"], dropped=parsed["dropped"])
    return dict(targets=targets, lines=audit, merged_box_count=sum(a["status"] == "merged" for a in audit),
                unassigned_box_count=sum(a["status"] == "unassigned" for a in audit))


def assign_page_symbols(symbols: Iterable[dict[str, Any]], records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Apply the identical polygon height/width rule to symbol confidences."""
    records = list(records)
    targets, unassigned, audit = {r["id"]: [] for r in records}, [], []
    for index, symbol in enumerate(symbols):
        hits = _page_hits(symbol["bbox"], records) if symbol.get("bbox") else {}
        ident = None
        if len(hits) == 1:
            candidate, overlap = next(iter(hits.items()))
            if overlap["height_fraction"] + 1e-12 >= .70 and overlap["horizontal_fraction"] + 1e-12 >= .50:
                ident = candidate
        if ident is None:
            unassigned.append(symbol)
        else:
            targets[ident].append(symbol)
        audit.append(dict(index=index, target_id=ident, overlaps=hits))
    return dict(targets=targets, unassigned=unassigned, symbols=audit)


def page_summary(comparisons: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Same-denominator reader preservation and usable-pair HARVEST agreement.

    Strict tier1 uses nonempty exact NFD equality. Letters+marks uses the T14b
    helper. Pilot tier1 additionally exposes core.tier's documented substitutions
    and whitespace normalization, separately from both requested strict metrics.
    Confidence means are weighted over symbols with reported confidences.
    """
    comparisons = list(comparisons)
    if not comparisons:
        raise ValueError("empty cohort")
    readers, paired = {}, {}
    for row in comparisons:
        paired.setdefault(row["id"], {})[row["engine"]] = row
    if any(set(pair) != {"vision", "docai"} for pair in paired.values()) or len(comparisons) != 2 * len(paired):
        raise ValueError("exactly one row per line and reader required")
    for engine in ("vision", "docai"):
        rows = [r for r in comparisons if r["engine"] == engine]
        value = dict(lines=len(rows), **{flag: sum(r[flag] for r in rows)
            for flag in ("merged", "lost", "split", "rejected", "identical", "letters_marks_identical")})
        value.update(exact_pct=100 * value["identical"] / len(rows),
                     letters_marks_pct=100 * value["letters_marks_identical"] / len(rows))
        for mode in ("crop", "page"):
            symbols = [s["confidence"] for r in rows for s in r[mode + "_symbols"] if s.get("confidence") is not None]
            value[mode + "_symbol_count"] = len(symbols)
            value[mode + "_mean_symbol_confidence"] = statistics.mean(symbols) if symbols else None
        readers[engine] = value
    harvest = {}
    for mode in ("crop", "page"):
        counts = Counter()
        for pair in paired.values():
            a, b = pair["vision"], pair["docai"]
            ta, tb = a[mode + "_text"], b[mode + "_text"]
            valid = all(not r[mode + "_rejected"] and r[mode + "_status"] == "ok" for r in (a, b)) and bool(ta.strip() and tb.strip())
            counts["usable_pairs"] += valid
            counts["tier1_exact"] += valid and compare_nfd(ta, tb)["identical"]
            counts["letters_agree"] += valid and bool(letters_marks(ta)) and letters_marks(ta) == letters_marks(tb)
            counts["pilot_tier1"] += valid and tier(ta, tb)["tier"] == "tier1"
            counts["pilot_whitespace_exact"] += valid and normalise(ta) == normalise(tb)
        harvest[mode] = dict(lines=len(paired), **counts,
            **{k + "_pct": 100 * counts[k] / len(paired) for k in ("tier1_exact", "letters_agree", "pilot_tier1", "pilot_whitespace_exact")})
    return dict(lines=len(paired), readers=readers, harvest=harvest)


def _data_image(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def build_blind_review(comparisons: Iterable[dict[str, Any]], records: Iterable[dict[str, Any]],
                       manifest: Iterable[dict[str, Any]], *, seed: int = 15) -> tuple[str, dict[str, Any]]:
    """Return self-contained 30-card HTML and a separate reproducible A/B key.

    Ten changed lines from each reader-change stratum, without duplicate IDs.
    Every reader/card independently shuffles crop/page A/B. Ten largest summed
    NFD edit distances also show native page context +/-2 detected rows in the
    same column. Their source boxes and ranking are retained only in the key.
    The page contains neither the key nor stratum/mode labels.
    """
    rows = list(comparisons)
    by_id = {r["id"]: r for r in records}
    pages = {p["id"]: p for p in manifest}
    pairs = {}
    for row in rows:
        pairs.setdefault(row["id"], {})[row["engine"]] = row
    strata = {"vision_only": [], "docai_only": [], "both": []}
    for ident, pair in pairs.items():
        v, d = not pair["vision"]["identical"], not pair["docai"]["identical"]
        if v or d:
            strata["both" if v and d else "vision_only" if v else "docai_only"].append(ident)
    rng = random.Random(seed)
    selected = []
    for stratum, ids in strata.items():
        if len(ids) < 10:
            raise ValueError("fewer than 10 changed lines in " + stratum)
        selected.extend((ident, stratum) for ident in rng.sample(sorted(ids), 10))
    rng.shuffle(selected)
    key = dict(schema="greekocr-page-blind-1", seed=seed, candidates={k: len(v) for k, v in strata.items()}, cards=[], most_changed=[])

    def readings(ident, tag):
        result, orders = [], {}
        for engine in ("vision", "docai"):
            order = ["crop", "page"]
            rng.shuffle(order)
            orders[engine] = dict(zip(("A", "B"), order))
            values = "".join('<div><b>' + letter + '</b><pre>' +
                html.escape(pairs[ident][engine][mode + "_text"] or "∅") + '</pre></div>'
                for letter, mode in zip(("A", "B"), order))
            result.append('<section><h3>' + engine.title() + '</h3><div class="readings">' + values +
                '</div><label>Preferred reading <select aria-label="' + tag + ' ' + engine +
                '"><option value="">Choose</option><option>A</option><option>B</option><option>Same</option><option>Neither</option></select></label></section>')
        return "".join(result), orders

    cards = []
    for index, (ident, stratum) in enumerate(selected, 1):
        tag = f"B{index:02d}"
        text, orders = readings(ident, tag)
        cards.append('<article id="' + tag + '"><h2>' + tag + '</h2><img alt="Straight crop ' + tag +
            '" src="' + _data_image(by_id[ident]["straight_crop"]) + '">' + text +
            '<label>Notes <textarea aria-label="' + tag + ' notes"></textarea></label></article>')
        key["cards"].append(dict(card=tag, id=ident, stratum=stratum, order=orders))
    changed = [ident for ids in strata.values() for ident in ids]
    ranked = sorted(changed, key=lambda ident: (-sum(pairs[ident][e]["nfd_edits"] for e in ("vision", "docai")), ident))[:10]
    for index, ident in enumerate(ranked, 1):
        row = by_id[ident]
        column = row.get("gates", {}).get("column")
        neighbors = [r for r in by_id.values() if r["page_id"] == row["page_id"] and r.get("gates", {}).get("column") == column]
        neighbors.sort(key=lambda r: ((r["bbox"][1] + r["bbox"][3]) / 2, r["id"]))
        location = next(i for i, r in enumerate(neighbors) if r["id"] == ident)
        region = neighbors[max(0, location - 2):location + 3]
        box = [math.floor(min(r["bbox"][0] for r in region)) - 8, math.floor(min(r["bbox"][1] for r in region)) - 8,
               math.ceil(max(r["bbox"][2] for r in region)) + 8, math.ceil(max(r["bbox"][3] for r in region)) + 8]
        with Image.open(pages[row["page_id"]]["image"]) as image:
            box = [max(0, box[0]), max(0, box[1]), min(image.width, box[2]), min(image.height, box[3])]
            stream = io.BytesIO()
            image.crop(tuple(box)).save(stream, format="PNG")
        uri = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()
        tag = f"C{index:02d}"
        text, orders = readings(ident, tag)
        cards.append('<article id="' + tag + '"><h2>' + tag + '</h2><div class="context"><figure><figcaption>Straight crop</figcaption><img alt="Straight crop ' +
            tag + '" src="' + _data_image(row["straight_crop"]) + '"></figure><figure><figcaption>Native page region (±2 detected lines)</figcaption><img alt="Page region ' +
            tag + '" src="' + uri + '"></figure></div>' + text + '</article>')
        key["most_changed"].append(dict(card=tag, id=ident, nfd_edits=sum(pairs[ident][e]["nfd_edits"] for e in ("vision", "docai")),
            context_box=box, neighbor_ids=[r["id"] for r in region], order=orders))
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Real page OCR — blind review</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef0ed;color:#17231f;font:16px/1.55 system-ui,sans-serif}main{max-width:1320px;margin:auto;padding:24px}h1,h2,h3{line-height:1.2}article{background:white;border:1px solid #bac7bd;border-radius:8px;padding:20px;margin:24px 0}img{max-width:100%;height:auto;display:block}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:22px/1.7 Georgia,serif;margin:8px 0}.readings,.context{display:grid;grid-template-columns:1fr 1fr;gap:24px}.readings>div{min-width:0;background:#f5f6f2;padding:12px}section{margin-top:24px}figure{margin:0;min-width:0}figcaption{margin-bottom:8px}textarea{display:block;width:100%;min-height:64px}select,button{font:inherit;padding:6px}label{display:block;margin-top:12px}@media(max-width:700px){main{padding:12px}article{padding:12px}.readings,.context{grid-template-columns:1fr}pre{font-size:19px}}
</style><main><h1>Real page OCR — blind review</h1><p>30 changed lines. For each reader, compare A and B with the crop and select the better transcription. A/B order varies independently. ∅ means no returned reading. Accuracy is for you to judge.</p><p>Your choices remain in this page until downloaded; reload clears them.</p><button id="export">Download review choices</button>'''
    page += "".join(cards[:30]) + '<h1>10 largest changes with native context</h1><p>Ranked by summed NFD edit count across both readers. The target appears as the separate straight crop; nearby rows come from the original page.</p>' + "".join(cards[30:])
    page += '''</main><script>document.getElementById('export').onclick=()=>{const choices=Array.from(document.querySelectorAll('article')).map(a=>({card:a.id,readers:Array.from(a.querySelectorAll('select')).map(s=>({reader:s.getAttribute('aria-label').split(' ').pop(),choice:s.value})),notes:a.querySelector('textarea')?.value||''}));const u=URL.createObjectURL(new Blob([JSON.stringify(choices,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=u;link.download='blind_choices.json';link.click();URL.revokeObjectURL(u)};</script></html>'''
    return page, key
