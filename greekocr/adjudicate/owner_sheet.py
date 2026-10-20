"""Data-driven owner sheets; assets are shipped with this package."""
from __future__ import annotations
import base64
import html
import io
import hashlib
from importlib.resources import files
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageFont

__all__ = ['render', 'detection_image']


def image_path(path: str | Path) -> Path:
    """Use a byte-preserved sheet raster when an archived source was removed."""
    path = Path(path)
    if path.is_file():
        return path
    cached = (Path(__file__).resolve().parents[2] / 'artifacts/owner_sheets/v2/recovered_crops' /
              (hashlib.sha256(str(path).encode()).hexdigest() + '.png'))
    return cached if cached.is_file() else path


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _uri(image: Any) -> str:
    if isinstance(image, str) and image.startswith('data:image/'):
        return image
    if not isinstance(image, Image.Image):
        with Image.open(image_path(image)) as opened:
            image = opened.copy()
    stream = io.BytesIO()
    image.save(stream, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(stream.getvalue()).decode()


def detection_image(image: Image.Image | str | Path, slots: list[dict], *, opening_quotes: list[dict] | None = None) -> Image.Image:
    """Draw saved detections and slot numbers without running a detector or model."""
    if not isinstance(image, Image.Image):
        with Image.open(image) as opened:
            image = opened.copy()
    width, height = image.size
    scale = 2 if width < 700 else 1
    big = image.convert('RGB').resize((width * scale, height * scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(big)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 11 * scale)
    except OSError:
        font = None
    def box(record, color):
        x0, y0, x1, y1 = record['bbox']
        draw.rectangle([x0 * scale, y0 * scale, x1 * scale, y1 * scale], outline=color, width=2)
    for index, slot in enumerate(slots):
        evidence = slot.get('evidence', {})
        for key, color in [('above', (30, 140, 60)), ('apostrophes', (30, 140, 60)),
                           ('below', (40, 80, 200)), ('attached', (120, 120, 120))]:
            for record in evidence.get(key, []):
                box(record, color)
        x = (slot.get('locator_span') or [None])[0]
        if x is not None:
            draw.text((max(0, x) * scale, height * scale - 12 * scale), str(index + 1), fill=(120, 120, 120), font=font)
    for record in opening_quotes or []:
        if 'bbox' in record:
            box(record, (30, 140, 60))
    if big.width > 1000:
        big = big.resize((1000, int(big.height * 1000 / big.width)), Image.Resampling.LANCZOS)
    return big


def _segments(row: dict) -> str:
    parts = row.get('segments', [dict(text=row.get('text', ''))])
    out = []
    for part in parts:
        text = _e(part['text'])
        kind = part.get('kind')
        if kind in ('changed', 'no_ink'):
            text = '<mark' + (' class="no"' if kind == 'no_ink' else '') + '>' + text + '</mark>'
        elif kind == 'muted':
            text = '<span class="muted">' + text + '</span>'
        elif kind is not None:
            raise ValueError('unknown text segment kind')
        out.append(text)
    return ''.join(out)


def _size(image: Any) -> tuple[int, int]:
    if isinstance(image, Image.Image):
        return image.size
    source = (io.BytesIO(base64.b64decode(image.split(',', 1)[1]))
              if isinstance(image, str) and image.startswith('data:image/')
              else image_path(image))
    with Image.open(source) as opened:
        return opened.size


def _rows(line: dict) -> str:
    versions = line.get('versions', [])[-2:]
    version_rows = []
    for i, version in enumerate(versions):
        name = str(version['name']) + (' (latest)' if i == len(versions) - 1 else '')
        verdict = version.get('verdict', '')
        version_rows.append(f'<tr class="version"><th>{_e(name)}</th><td>' +
                            (f'<b>{_e(verdict)}</b>: ' if verdict else '') + _segments(version) + '</td></tr>')
    rows = []
    for row in line['rows']:
        if row['name'] in ('Text vs crop', 'Owner standard') and version_rows:
            rows.extend(version_rows)
            version_rows = []
        rows.append(f'<tr><th>{_e(row["name"])}</th><td>{_segments(row)}</td></tr>')
    return ''.join(rows + version_rows)


def render(lines: list[dict], spec: dict[str, Any]) -> str:
    """Render ordered card records and group headings into a self-contained owner HTML sheet.

    Cards carry line_id, image, rows (name and text/segments), tags, optional
    zooms, clean_image, printed, slot, data attributes, tool_verdict, versions,
    overlay_svg and display. Group order comes from spec.groups. Explicit doc_id
    wins; otherwise sheet_prefix gives prefix:line_id, or the legacy identity is
    line_id / line_id:s{slot}. variant defaults to decision.
    """
    css = files(__package__).joinpath('owner_sheet.css').read_text()
    js = files(__package__).joinpath('owner_sheet.js').read_text()
    title = _e(spec['title'])
    variant = spec.get('variant', 'decision')
    if variant not in ('decision', 'correction'):
        raise ValueError('unknown sheet variant')
    meaning = ('KEEP = accept the proposed correction; DROP = reject it. Printed is editable.'
               if variant == 'correction' else 'KEEP = keep the line; DROP = drop the line.')
    legend = ('Inner frame: CHANGED amber, UNCHANGED green, UNCERTAIN grey.'
              if variant == 'correction' else 'Inner frame: KEEP green, DROP red, UNCERTAIN amber.')
    out = ['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
           f'<title>{title}</title><style>{css}</style></head><body data-variant="{variant}">',
           f'<main><h1>{title}</h1><p class="meta">' + '<br>'.join(_e(spec.get('intro', '')).splitlines()) + '</p>',
           f'<p class="meta instructions">{meaning} Outer border: your mark, green KEEP / red DROP. {legend} '
           '↑ ↓ move (also in notes); SPACE toggles KEEP / DROP, including in an empty note; click the badge to mark. '
           'b toggles overlays; z toggles 3× zoom; hover or click the crop for the lens; Esc leaves the note box. '
           'Marks, notes and Printed autosave in the signed-in view.</p>']
    seen = set()
    def card(line):
        lid = str(line['line_id'])
        default = lid + (f':s{line["slot"]}' if 'slot' in line else '')
        if 'sheet_prefix' in spec:
            default = f'{spec["sheet_prefix"]}:{lid}'
        doc_id = str(line.get('doc_id', default))
        if doc_id in seen:
            raise ValueError('duplicate note document: ' + doc_id)
        seen.add(doc_id)
        def attrs(data):
            if any(not k.replace('-', '').isalnum() for k in data):
                raise ValueError('invalid data attribute name')
            return ''.join(f' data-{k}="{_e(v)}"' for k, v in data.items())
        data = dict(line.get('data', {}))
        tool = line.get('tool_verdict', data.get('tool'))
        if tool is not None:
            if tool not in ('KEEP', 'DROP', 'UNCERTAIN', 'CHANGED', 'UNCHANGED'):
                raise ValueError('unknown tool verdict')
            data['tool'] = tool
        image = line['image']
        if line.get('slots') is not None:
            image = detection_image(image, line['slots'], opening_quotes=line.get('opening_quotes'))
        w, h = _size(image)
        tall = h > w  # a vertical segment: crop on the left, text on the right, taller display cap
        prior = line.get('prior')  # the owner's earlier mark on another sheet: shown as a dashed border, never saved
        if prior not in (None, 'KEEP', 'DROP'):
            raise ValueError('prior must be KEEP or DROP')
        out.append('<div class="card' + (' tall' if tall else '') + (f' p{prior.lower()}' if prior else '') + '"' + attrs(data) + '><div class="lid">' + _e(line.get('label', lid)) +
                   (f'<span class="toolpill {tool}">tool: {tool}</span>' if tool else '') +
                   '<button type="button" class="verdict" title="click or press space to toggle KEEP / DROP" '
                   'aria-label="Owner mark: unmarked">–</button></div>')
        display = line.get('display') or {}
        cap_h = 640 if tall else 300
        scale = min(3.0, display.get('scale', 3.0), min(940, display.get('max_width', 940)) / w,
                    min(cap_h, display.get('max_height', cap_h)) / h)
        if scale <= 0:
            raise ValueError('display dimensions must be positive')
        dw = max(1, int(w * scale))
        img = f'<img src="{_uri(image)}" alt="{_e(line.get("alt", "line with detected marks"))}">'
        clean = f' style="background-image:url({_uri(line["clean_image"])})"' if line.get('clean_image') is not None else ''
        out.append(f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}">' +
                   img + line.get('overlay_svg', '') + f'</div><div class="lens"{clean} hidden></div></div>')
        if line.get('zooms'):
            out.append('<div class="zoomrow">' + ''.join(f'<img class="zoom" src="{_uri(z["image"])}" alt="{_e(z["alt"])}">' for z in line['zooms']) + '</div>')
        out.append('<table class="w">' + _rows(line) + '</table>')
        out.append('<div class="row">' + ''.join(f'<span class="pill{(" " + _e(t["class"])) if t.get("class") else ""}">{_e(t["text"])}</span>' for t in line.get('tags', [])) + '</div>')
        default_data = {'line': lid}
        if doc_id != lid or 'slot' in line:
            default_data['id'] = doc_id
        if 'slot' in line:
            default_data['slot'] = line['slot']
        data = line.get('note_data', default_data)
        if str(data.get('id', data.get('line', ''))) != doc_id or str(data.get('line', '')) != lid:
            raise ValueError('note attributes and document identity disagree')
        out.append('<div class="notes"' + attrs(data) + '>')
        if 'printed' in line or variant == 'correction':
            out.append(f'<div class="pr"><label for="p-{_e(doc_id)}">Printed</label><input class="printed" id="p-{_e(doc_id)}" value="{_e(line.get("printed", ""))}"></div>')
        out.append(f'<label for="n-{_e(doc_id)}">Note</label><textarea class="note" id="n-{_e(doc_id)}" rows="2">{_e(line.get("note", ""))}</textarea><div class="nrow"><span class="status">autosaves as you type</span></div></div></div>')
    groups = spec.get('groups')
    if groups is None:
        for line in lines: card(line)
    else:
        keys = [g['id'] for g in groups]
        if len(set(keys)) != len(keys) or any(l.get('group') not in keys for l in lines):
            raise ValueError('invalid group assignment')
        sections = {s['id']: s for s in spec.get('sections', [])}
        current_section = None
        for group in groups:
            section_id = group.get('section')
            if section_id is not None and section_id != current_section:
                section = sections[section_id]
                out.append('<header><h2>' + _e(section['heading']) + '</h2><p class="meta">' + _e(section.get('header', '')) + '</p></header>')
                current_section = section_id
            level = 'h3' if section_id is not None else 'h2'
            out.append('<' + level + '>' + _e(group['heading']) + '</' + level + '>')
            if group.get('gap'):
                out.append('<span class="pill warn">' + _e(group['gap']) + '</span>')
            for line in lines:
                if line['group'] == group['id']: card(line)
    out.append('</main><script>' + js + '</script></body></html>')
    return '\n'.join(out)
