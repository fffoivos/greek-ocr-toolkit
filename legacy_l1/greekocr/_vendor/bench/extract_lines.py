#!/usr/bin/env python3
"""Render native-PDF candidates at 200 dpi; scan mode reuses pipeline projection bands.

Run as python -m bench.extract_lines PDF_OR_DIR --out RUN [--manifest CSV] [--scan].
All pages are processed unless --pages is explicitly supplied (1-based comma list).
PDFium is isolated in processes, never threads. Every candidate including rejects has a PNG.
"""
from __future__ import annotations
import argparse
import csv
from contextlib import closing
import ctypes as ct
import json
import math
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import median
from PIL import Image
import pypdfium2 as pdfium
from greekocr._vendor.bench.common import ROOT, SCHEMA, features, sha256, write_json
from greekocr._vendor.bench.admission import RULES, admit, ink_diagnostics, char_ink_diagnostics

DPI = 200
SCALE = DPI / 72


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def char_records(textpage):
    """One record per Unicode scalar, with all contributing PDFium indices.

    PDFium can expose non-BMP text as adjacent UTF-16 high/low units. Decode
    before grouping/filtering and union their boxes; coincident unrelated
    glyphs remain separate. Unpaired surrogates still become U+FFFD.
    """
    raw = pdfium.raw
    fonts = {}
    i, count = 0, textpage.count_chars()
    while i < count:
        cp = raw.FPDFText_GetUnicode(textpage, i)
        indices, codepoints = [i], [cp]
        if 0xD800 <= cp <= 0xDBFF and i+1 < count:
            low = raw.FPDFText_GetUnicode(textpage, i+1)
            if 0xDC00 <= low <= 0xDFFF:
                indices.append(i+1)
                codepoints.append(low)
                cp = 0x10000 + ((cp-0xD800) << 10) + low-0xDC00
        c = chr(cp) if 0 < cp <= 0x10FFFF and not 0xD800 <= cp <= 0xDFFF else '\ufffd'
        if c in '\r\n' and raw.FPDFText_IsGenerated(textpage, i) == 1:
            yield dict(text=c, separator=True, source_indices=indices, source_codepoints=codepoints)
            i += len(indices)
            continue
        b = union([list(textpage.get_charbox(j)) for j in indices])
        x, y = ct.c_double(), ct.c_double()
        raw.FPDFText_GetCharOrigin(textpage, i, ct.byref(x), ct.byref(y))
        size = raw.FPDFText_GetFontSize(textpage, i)
        # Cache by PDF text object: one object can contain a whole same-font/style run.
        obj = raw.FPDFText_GetTextObject(textpage, i)
        key = ct.cast(obj, ct.c_void_p).value
        if key not in fonts:
            flag = ct.c_int()
            n = raw.FPDFText_GetFontInfo(textpage, i, None, 0, ct.byref(flag))
            buf = ct.create_string_buffer(max(1,n))
            raw.FPDFText_GetFontInfo(textpage, i, buf, len(buf), ct.byref(flag))
            name = buf.value.decode('utf-8', errors='replace')
            weight = raw.FPDFText_GetFontWeight(textpage, i)
            fonts[key] = (name, flag.value, weight)
        name, flags, weight = fonts[key]
        yield dict(text=c, box=b, x=x.value, baseline=y.value, size=size,
                   raw_codepoint=cp, source_indices=indices, source_codepoints=codepoints,
                   font=name, bold=(weight >= 700 or bool(flags & (1 << 18)) or 'bold' in name.lower()),
                   italic=(bool(flags & 64) or any(s in name.lower() for s in ('italic','oblique'))),
                   angle=float(raw.FPDFText_GetCharAngle(textpage,i)), index=i)
        i += len(indices)


def valid_box(c):
    b = c['box']
    return all(math.isfinite(v) for v in b) and b[2] > b[0] and b[3] > b[1]


def spatial_text(chars):
    """LTR printed order, with source index as tie-break for coincident glyphs/spaces."""
    import unicodedata
    return unicodedata.normalize('NFC', ''.join(c['text'] for c in
        sorted(chars, key=lambda c: (c['box'][0], c['index']))).strip(' '))


def column_gutters(chars, *, candidate=False):
    """X-range occupancy across baselines, tolerating rare headers/footers.

    Bins are 1/4 median letter width; normal gaps below 3 widths are filled
    within each baseline cluster (including TOC leaders). A gutter is >=3 widths with
    occupancy on <=5% of baselines (two outliers allowed for a full-width
    note and folio even on sparse pages). Both sides need >=6 baselines and
    >=25% of the page's baselines. Candidate gutters need >=3 baselines per
    side; these are admission guards, not permission to split a page.
    This detects columns
    with independent line spacing and a centered folio, without requiring that
    their baselines coincide. The inferred structure is a conservative page
    heuristic, not a language/reading-order classifier.
    """
    from collections import defaultdict
    visible = [c for c in chars if not c.get('separator') and
               not c['text'].isspace() and valid_box(c)]
    if not visible:
        return []
    letters = [c for c in visible if c['text'].isalpha()] or visible
    width = max(1., median(c['box'][2]-c['box'][0] for c in letters))
    step = width/4
    left = min(c['box'][0] for c in visible)
    right = max(c['box'][2] for c in visible)
    occupancy = [set() for _ in range(math.ceil((right-left)/step)+1)]
    baselines = {round(c['baseline']/3) for c in visible}
    ranges = defaultdict(list)
    for c in visible:
        ranges[round(c['baseline']/3)].append(c['box'])
    for baseline, boxes in ranges.items():
        clusters = []
        for box in sorted(boxes):
            if clusters and box[0]-clusters[-1][1] < 3*width:
                clusters[-1][1] = max(clusters[-1][1],box[2])
            else:
                clusters.append([box[0],box[2]])
        for x0,x1 in clusters:
            for i in range(math.floor((x0-left)/step), math.ceil((x1-left)/step)):
                occupancy[i].add(baseline)
    rare = max(2, math.floor(.05*len(baselines)))
    support = max(3 if candidate else 6, math.ceil(.25*len(baselines)))
    gutters,start = [],None
    for i,n in enumerate([len(o) for o in occupancy]+[len(baselines)+1]):
        if n <= rare and start is None:
            start = i
        elif n > rare and start is not None:
            x0,x1 = left+start*step,left+i*step
            before = {round(c['baseline']/3) for c in visible if c['box'][2]<=x0}
            after = {round(c['baseline']/3) for c in visible if c['box'][0]>=x1}
            if x1-x0 >= 3*width and min(len(before),len(after)) >= support:
                gutters.append([x0,x1])
            start = None
    return gutters


def spanning_gutters(chars, gutters):
    """A full-width baseline must have glyphs on both sides AND in the gutter.

    A bbox union across two columns is insufficient. Require at least three
    glyphs on each side, ink geometry in the central third of the gutter, and
    no gap >=3 median letter widths through it. This preserves continuous
    notes/headings without exempting the empty gap in a column merge.
    """
    visible = sorted((c for c in chars if not c.get('separator') and
                      not c['text'].isspace() and valid_box(c)), key=lambda c:c['box'][0])
    letters = [c for c in visible if c['text'].isalpha()] or visible
    width = max(1., median(c['box'][2]-c['box'][0] for c in letters)) if letters else 1.
    spans = []
    for g in gutters:
        x0,x1 = g
        third = (x1-x0)/3
        if (sum(c['box'][2] <= x0 for c in visible) < 3 or
            sum(c['box'][0] >= x1 for c in visible) < 3 or
            not any(c['box'][0] < x1-third and c['box'][2] > x0+third for c in visible)):
            continue
        if any(b['box'][0]-a['box'][2] >= 3*width and
               a['box'][2] < x1 and b['box'][0] > x0 for a,b in zip(visible,visible[1:])):
            continue
        spans.append(g)
    return spans


def column_index(box, gutters):
    return sum((box[0]+box[2])/2 > (g[0]+g[1])/2 for g in gutters)


def group_chars(chars, gutters=None):
    """Apply page columns only outside continuous full-width baselines."""
    gutters = column_gutters(chars) if gutters is None else gutters
    if not gutters:
        return _group_chars(chars, [])
    full_width = [g for g in _group_chars(chars, []) if spanning_gutters(g, gutters)]
    indices = {c['index'] for g in full_width for c in g}
    remaining = [c for c in chars if c.get('index') not in indices]
    groups = full_width + _group_chars(remaining, gutters)
    return sorted(groups, key=lambda g:(-median(c['baseline'] for c in g),min(c['box'][0] for c in g)))


def _group_chars(chars, gutters):
    """Physical baseline membership precedes LTR ordering; CR/LF are not lines.

    Large glyphs establish baselines first. Smaller raised/lowered glyphs attach
    within 0.65 of the parent font size and eight median glyph widths in x.
    Equal-size glyphs need baseline agreement within 0.12 font size. A line is
    assembled within its column, then split at >8 median glyph widths.
    Whitespace/control chars are retained; generated CR/LF alone are discarded.
    """
    chars = [c for c in chars if not c.get('separator')]
    visible = [c for c in chars if not c['text'].isspace()]
    if not visible:
        return [chars] if chars else []
    widths = [c['box'][2]-c['box'][0] for c in visible if valid_box(c)]
    width = median(widths) if widths else 4.
    gap_limit = 8 * max(1.,width)
    bands = []
    # Establish full-size prose before superscripts/subscripts, independent of
    # source object order and glyph top. No transitive drift of the anchor.
    for c in sorted(visible, key=lambda c: (-c['size'], -c['baseline'], c['box'][0])):
        choices = []
        for i, band in enumerate(bands):
            if column_index(c['box'],gutters) != band['column']:
                continue
            dy = abs(c['baseline']-band['baseline'])
            distance = max(0, band['left']-c['box'][2], c['box'][0]-band['right'])
            script = c['size'] <= .8*band['size'] and distance <= gap_limit
            tolerance = (.65 if script else .12) * max(c['size'],band['size'])
            if dy <= tolerance:
                choices.append((dy/max(1,band['size']) + distance/max(1,gap_limit)*.1, i))
        if choices:
            band = bands[min(choices)[1]]
            band['chars'].append(c)
            band['left'] = min(band['left'],c['box'][0])
            band['right'] = max(band['right'],c['box'][2])
        else:
            bands.append(dict(chars=[c], column=column_index(c['box'],gutters), baseline=c['baseline'], size=c['size'],
                              left=c['box'][0], right=c['box'][2]))
    groups = []
    for band in sorted(bands, key=lambda b: (-b['baseline'],b['left'])):
        parts, part, edge = [], [], None
        for c in sorted(band['chars'], key=lambda c: (c['box'][0],c['index'])):
            x = c['box'][0]
            split = edge is not None and (x-edge > gap_limit or any(edge <= g[0] and x >= g[1] for g in gutters))
            if split:
                parts.append(part); part = []
            part.append(c); edge = max(edge if edge is not None else x,c['box'][2])
        if part: parts.append(part)
        # PDF space origins may have zero boxes/size 1; assign by baseline and x,
        # never allow them to establish a new physical line or bridge a gutter.
        for part in parts:
            x0,x1 = min(c['box'][0] for c in part),max(c['box'][2] for c in part)
            part.extend(c for c in chars if c['text'].isspace() and
                        abs(c['baseline']-band['baseline']) <= .65*band['size'] and
                        x0 <= c['box'][0] <= x1 and
                        min((b for b in bands if b['left'] <= c['box'][0] <= b['right'] and
                             column_index(c['box'],gutters) == b['column']), default=None,
                            key=lambda b: abs(c['baseline']-b['baseline'])) is band)
            groups.append(part)
    return groups


def pixel_box(box, page, image):
    w, h = page.get_size()
    rot = page.get_rotation()
    def transform(x,y):
        if rot == 90:
            return y*SCALE,x*SCALE
        if rot == 180:
            return (w-x)*SCALE,y*SCALE
        if rot == 270:
            return (h-y)*SCALE,(w-x)*SCALE
        return x*SCALE,(h-y)*SCALE
    pts = [transform(x,y) for x in (box[0],box[2]) for y in (box[1],box[3])]
    tight = [min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
    padded = [max(0,math.floor(tight[0])-3),max(0,math.floor(tight[1])-3),
              min(image.width,math.ceil(tight[2])+3),min(image.height,math.ceil(tight[3])+3)]
    # Ensure malformed out-of-page unions still have an inspectable minimal crop and rejection.
    padded = [min(image.width-1,padded[0]),min(image.height-1,padded[1]),
              max(1,padded[2]),max(1,padded[3])]
    padded[2] = max(padded[0]+1,padded[2]); padded[3] = max(padded[1]+1,padded[3])
    return tight, padded


def overlaps(rows):
    for i,a in enumerate(rows):
        ax,ay,ar,ab = a['bbox_pixel']
        for b in rows[i+1:]:
            bx,by,br,bb = b['bbox_pixel']
            inter = max(0,min(ar,br)-max(ax,bx))*max(0,min(ab,bb)-max(ay,by))
            if inter / max(1,min((ar-ax)*(ab-ay),(br-bx)*(bb-by))) > .2:
                a['overlapping_lines'] = b['overlapping_lines'] = True


def native_rows(page, tp, image):
    chars = [c for c in char_records(tp) if not c.get('separator')]
    gutters = column_gutters(chars)
    candidates_gutters = column_gutters(chars, candidate=True)
    groups = group_chars(chars, gutters)
    # Index ALL page glyphs by vertical pixel bins, not by candidate membership.
    # Completeness uses the padded crop (including partial glyph intersections).
    from collections import defaultdict
    pixel_chars, yindex = {}, defaultdict(list)
    for c in chars:
        if valid_box(c):
            tight, _ = pixel_box(c['box'], page, image)
            pixel_chars[c['index']] = tight
            for y in range(math.floor(tight[1]/32),math.floor(tight[3]/32)+1):
                yindex[y].append(c)
    rows = []
    for group in groups:
        spans = spanning_gutters(group, candidates_gutters)
        local_gutters = [g for g in gutters if g not in spans]
        vis = [c for c in group if not c['text'].isspace() and valid_box(c)]
        box = union([c['box'] for c in vis]) if vis else [0,0,1,1]
        if not vis: vis = group
        tight, pix = pixel_box(box, page, image)
        text = spatial_text(group)
        candidates = {c['index']:c for y in range(pix[1]//32,pix[3]//32+1) for c in yindex[y]}
        intersecting = [c for i,c in candidates.items() if
                       min(pixel_chars[i][2],pix[2]) > max(pixel_chars[i][0],pix[0]) and
                       min(pixel_chars[i][3],pix[3]) > max(pixel_chars[i][1],pix[1])]
        # Zero-area PDF spaces still carry text. Include their origins only when
        # inside the crop's tight text range and near an intersecting baseline.
        intersecting.extend(c for c in chars if c['text'].isspace() and not valid_box(c) and
                            box[0] <= c['box'][0] <= box[2] and box[1] <= c['baseline'] <= box[3])
        own = {c['index'] for c in group}
        body = median(c['size'] for c in vis)
        width = median(c['box'][2]-c['box'][0] for c in vis if valid_box(c)) if any(valid_box(c) for c in vis) else 4.
        baseline = median(c['baseline'] for c in vis if c['size'] >= .8*body)
        # Neighbours just outside the crop cannot escape the union check.
        # Wide same-baseline splits without a confirmed histogram gutter are
        # ambiguous (e.g. justified headings): reject every affected piece.
        missing = [c for c in chars if c['index'] not in own and not c['text'].isspace() and valid_box(c) and
                   abs(c['baseline']-baseline) <= (.65 if c['size'] <= .8*body else .12)*body and
                   (max(0,box[0]-c['box'][2],c['box'][0]-box[2]) <= 2*max(1,width) or
                    abs(c['baseline']-baseline) <= .12*body) and
                   column_index(c['box'],local_gutters) == column_index(box,local_gutters)]
        ordered = sorted(group, key=lambda c: (c['box'][0],c['index']))
        spacing_gaps = [[a['index'],b['index']] for a,b in zip(ordered,ordered[1:])
                        if not a['text'].isspace() and b['text'].isalpha() and
                        b['index'] != a.get('source_indices', [a['index']])[-1]+1 and
                        b['box'][0]-a['box'][2] > .5*max(1,width)]
        sizes = [c['size'] for c in vis]
        row = dict(text=text,bbox_pdf=box,bbox_pixel=pix,char_bbox_pixel=tight,
                   crop_text=spatial_text(intersecting),
                   crop_char_indices=sorted(c['index'] for c in intersecting),
                   line_char_indices=sorted(own), baseline_pdf=baseline,column_gutters_pdf=gutters,
                   line_source_indices=sorted(i for c in group for i in c.get('source_indices', [c['index']])),
                   crop_source_indices=sorted(i for c in intersecting for i in c.get('source_indices', [c['index']])),
                   column_candidate_gutters_pdf=candidates_gutters,spanning_gutters_pdf=spans,
                   cross_column=any(any(c['box'][2] <= g[0] for c in vis) and
                                    any(c['box'][0] >= g[1] for c in vis)
                                    for g in candidates_gutters if g not in spans),
                   missing_baseline_neighbour=bool(missing),
                   label_spacing_gap=bool(spacing_gaps),spacing_gap_indices=spacing_gaps,
                   omitted_neighbour_indices=[c['index'] for c in missing],
                   font_names=sorted({c['font'] for c in vis}),size=median(sizes),
                   invalid_unicode_codepoints=[c['raw_codepoint'] for c in group if c['text']=='\ufffd'],
                   size_min=min(sizes),size_max=max(sizes), bold=any(c['bold'] for c in vis),
                   italic=any(c['italic'] for c in vis),
                   rotated_text=bool(page.get_rotation()) or any(abs(math.remainder(c['angle'],2*math.pi))>.035 for c in vis),
                   invalid_char_geometry=any(not valid_box(c) for c in group if not c['text'].isspace()),
                   features=features(text),provenance='born_digital_candidate')
        crop = image.crop(pix)
        row.update(ink_diagnostics(crop,[tight[0]-pix[0],tight[1]-pix[1],tight[2]-pix[0],tight[3]-pix[1]]))
        # Audit pixels just beyond the left/right crop edges as well: source
        # bullets may be image-backed and absent from every PDF char record.
        # Five median glyph widths, same vertical band, clipped at column midpoints.
        halo = math.ceil(5*max(1,width)*SCALE)
        audit = [max(0,pix[0]-halo),pix[1],min(image.width,pix[2]+halo),pix[3]]
        for g in local_gutters:
            mid = (g[0]+g[1])/2*SCALE
            if box[2] <= g[0]: audit[2] = min(audit[2],math.floor(mid))
            if box[0] >= g[1]: audit[0] = max(audit[0],math.ceil(mid))
        expected = [[pixel_chars[c['index']][0]-audit[0],pixel_chars[c['index']][1]-audit[1],
                     pixel_chars[c['index']][2]-audit[0],pixel_chars[c['index']][3]-audit[1]]
                    for c in vis if valid_box(c)]
        row.update(char_ink_diagnostics(image.crop(audit),expected))
        row['ink_audit_bbox_pixel'] = audit
        rows.append(row)
    return rows


def scan_rows(page, image):
    # Reuse repo page tool rather than maintaining a second projection implementation.
    sys.path.insert(0,str(ROOT/'pipeline'))
    import lines_v0 as projection
    from layout_v0 import otsu_threshold
    import numpy as np
    # The legacy mask uses a strict lower bin edge. A two-tone image can then lose
    # every foreground pixel. Adapt the quantized Otsu bin to its inclusive upper edge.
    old_mask=projection.ink_mask
    projection.ink_mask=lambda img: img <= min(254/255,otsu_threshold(img)+1/255)
    try:
        boxes=projection.lines_in_block(np.asarray(image,dtype=np.float32)/255.0, (0,0), pad=3)
    finally:
        projection.ink_mask=old_mask
    rows=[]
    for pix in boxes:
        x0,y0,x1,y1=pix
        w,h=page.get_size()
        row=dict(text='',bbox_pdf=[x0/SCALE,h-y1/SCALE,x1/SCALE,h-y0/SCALE],bbox_pixel=list(pix),
                 char_bbox_pixel=None,font_names=[],size=None,size_min=None,size_max=None,bold=None,italic=None,
                 features=features(''),provenance='scan_unlabelled',rotated_text=bool(page.get_rotation()))
        row.update(ink_diagnostics(image.crop(pix),None))
        rows.append(row)
    return rows


def save_crop(crop_image, destination, previous=None):
    """Reuse storage only after fresh raster equality; never mutate a hard link."""
    if previous is not None and previous.exists():
        with Image.open(previous) as old:
            equal = old.mode == crop_image.mode and old.size == crop_image.size and old.tobytes() == crop_image.tobytes()
        if equal:
            # Replace the destination entry, not the shared file's contents.
            temporary = destination.with_suffix('.link.tmp')
            temporary.unlink(missing_ok=True)
            os.link(previous, temporary)
            temporary.replace(destination)
            return True
    temporary = destination.with_suffix('.png.tmp')
    crop_image.save(temporary, format='PNG', compress_level=1)
    temporary.replace(destination)
    return False


def extract_document(task):
    pdf, out, meta, scan, pages, lexicon_path = task
    pdf,out=Path(pdf),Path(out)
    doc=pdf.stem
    crops=out/'crops'/doc; crops.mkdir(parents=True,exist_ok=True)
    records=out/'records'; records.mkdir(parents=True,exist_ok=True)
    lexicon=set(Path(lexicon_path).read_text().casefold().split()) if lexicon_path else None
    counts=Counter({r:0 for r in RULES}); seen=set(); nrows=admitted=0
    start=time.perf_counter()
    reuse_root = os.environ.get('O1_CROP_REUSE_ROOT')
    reused_crops = 0
    digest=sha256(pdf)
    receipt=dict(doc=doc,pdf=str(pdf),pdf_sha256=digest,host=meta.get('host','unknown'),
                 document_type=meta.get('document_type','unknown'),manifest_pages=meta.get('pages'),
                 scan=scan,pages_processed=0,text_chars=0,empty_pages=0,errors=[],page_coverage=[],
                 code_sha256={name:sha256(ROOT/name) for name in ('bench/extract_lines.py','bench/admission.py','bench/common.py','pipeline/lines_v0.py','pipeline/layout_v0.py')})
    with pdfium.PdfDocument(str(pdf)) as document, (records/(doc+'.jsonl')).open('w',encoding='utf-8') as f:
        receipt['pages_total']=len(document)
        for pi in (pages if pages is not None else range(len(document))):
            if pi<0 or pi>=len(document):
                raise ValueError(f'{doc}: page {pi+1} outside PDF')
            with closing(document[pi]) as page:
                with closing(page.get_textpage()) as tp:
                    chars=tp.count_chars(); receipt['text_chars']+=chars
                    receipt['empty_pages']+=int(chars==0)
                    bitmap=page.render(scale=SCALE,grayscale=True)
                    image=bitmap.to_pil().copy(); bitmap.close()
                    rows=scan_rows(page,image) if scan or not chars else native_rows(page,tp,image)
                overlaps(rows)
                receipt['page_coverage'].append(dict(page=pi+1,text_chars=chars,candidates=len(rows),
                    column_gutters_pdf=rows[0].get('column_gutters_pdf',[]) if rows else [],
                    column_candidate_gutters_pdf=rows[0].get('column_candidate_gutters_pdf',[]) if rows else []))
                for j,row in enumerate(rows):
                    ident=f'{doc}-p{pi+1:04d}-l{j+1:04d}'
                    crop=crops/(ident+'.png')
                    previous = Path(reuse_root)/('scans' if scan else 'native')/'crops'/doc/crop.name if reuse_root else None
                    reused_crops += save_crop(image.crop(row['bbox_pixel']),crop,previous)
                    row.update(schema=SCHEMA,id=ident,doc=doc,page=pi+1,crop_path=str(crop.resolve()),
                               pdf_sha256=digest,host=receipt['host'],document_type=receipt['document_type'],dpi=DPI)
                    neighbours=[rows[k]['text'] for k in (j-1,j+1) if 0<=k<len(rows)]
                    admit(row,seen,lexicon,neighbours)
                    counts.update(row['reject_reasons']); nrows+=1; admitted+=row['admitted']
                    f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
            receipt['pages_processed']+=1
    receipt.update(rows=nrows,admitted=admitted,rejected=nrows-admitted,rule_counts=dict(counts),
                   crop_reuse_root=reuse_root,pixel_verified_reused_crops=reused_crops,
                   runtime_seconds=time.perf_counter()-start,dpi=DPI,dictionary_enabled=bool(lexicon),
                   records_sha256=sha256(records/(doc+'.jsonl')))
    write_json(out/'receipts'/(doc+'.json'),receipt)
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pdf',type=Path); ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--manifest',type=Path); ap.add_argument('--scan',action='store_true')
    ap.add_argument('--workers',type=int,default=1); ap.add_argument('--pages')
    ap.add_argument('--lexicon',type=Path)
    a=ap.parse_args()
    files=sorted(a.pdf.glob('*.pdf')) if a.pdf.is_dir() else [a.pdf]
    manifest={r['filename']:r for r in csv.DictReader(a.manifest.open())} if a.manifest else {}
    pages=[int(s)-1 for s in a.pages.split(',')] if a.pages else None
    tasks=[(str(p),str(a.out),manifest.get(p.name,{}),a.scan,pages,str(a.lexicon) if a.lexicon else None) for p in files]
    receipts=[]; start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for receipt in ex.map(extract_document,tasks):
            receipts.append(receipt)
            print(f"{receipt['doc']}: {receipt['pages_processed']} pages, {receipt['rows']} candidates, {receipt['admitted']} admitted",flush=True)
    counts=Counter({r:0 for r in RULES})
    for r in receipts: counts.update(r['rule_counts'])
    summary=dict(documents=len(receipts),pages=sum(r['pages_processed'] for r in receipts),
                 rows=sum(r['rows'] for r in receipts),admitted=sum(r['admitted'] for r in receipts),
                 rule_counts=dict(counts),runtime_seconds=time.perf_counter()-start,dpi=DPI,
                 dictionary_enabled=bool(a.lexicon),documents_receipts=receipts)
    write_json(a.out/'summary.json',summary)

if __name__=='__main__': main()
