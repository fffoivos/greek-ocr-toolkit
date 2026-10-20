"""S2 text-layer candidates. Reuse O1 char-box assembly; all labels start silver.

--sources is JSON {books:[{input_path,source_doc_id,source_dataset,licence,
source_url,licence_evidence,attribution,rights_reviewed:true,...}]}.
Use archive source.json entries or reviewed Anemi snapshots. Never runs OCR to
invent a missing layer. DjVu conversion retains its char geometry when present.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import closing
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image
from greekocr._vendor.bench.common import sha256, write_json
from greekocr._vendor.bench.extract_lines import SCALE, native_rows, overlaps, group_chars, union
from greekocr._vendor.bench.admission import admit, ink_diagnostics, char_ink_diagnostics
from greekocr._vendor.bench.o4b_common import Admission, Partition, fresh, rights, nfc


def pdf_pages(path, pages=None):
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(str(path)) as document:
        for pi in (pages if pages is not None else range(len(document))):
            if not 0 <= pi < len(document): raise ValueError('page outside PDF')
            with closing(document[pi]) as page, closing(page.get_textpage()) as tp:
                if not tp.count_chars():
                    yield pi+1, None, [], 'no_text_layer'; continue
                bitmap = page.render(scale=SCALE, grayscale=True)
                image = bitmap.to_pil().copy(); bitmap.close()
                rows = native_rows(page, tp, image)
                overlaps(rows)
                yield pi+1, image, rows, None


def djvu_pages(path, work, pages=None):
    """DjVuLibre XML CHAR/CHARACTER geometry only; WORD-only layers are flagged.

    Most IA DjVu layers contain WORD boxes, not chars. Do not fabricate character
    geometry by uniform subdivision. Coordinator can choose the searchable PDF.
    """
    work.mkdir(parents=True, exist_ok=True)
    xml = work/'layer.xml'
    with xml.open('wb') as out:
        subprocess.run(['djvutoxml', str(path)], stdout=out, check=True)
    objects = [x for x in ET.parse(xml).getroot().iter() if x.tag.rsplit('}', 1)[-1] == 'OBJECT']
    for pi, obj in enumerate(objects):
        if pages is not None and pi not in pages: continue
        chars = [x for x in obj.iter() if x.tag.rsplit('}', 1)[-1] in ('CHAR', 'CHARACTER')]
        if not chars:
            yield pi+1, None, [], 'djvu_no_character_boxes'; continue
        ppm = work/f'p{pi+1:04d}.ppm'
        subprocess.run(['ddjvu', '-format=ppm', f'-page={pi+1}', str(path), str(ppm)], check=True)
        with Image.open(ppm) as im: image = im.convert('L')
        records = []
        # DjVu coordinates are left,bottom,right,top in top-origin page pixels.
        for i, char in enumerate(chars):
            x0, y1, x1, y0 = map(float, char.attrib['coords'].split(','))
            text = ''.join(char.itertext())
            if len(text) != 1: raise ValueError('DjVu CHAR must represent exactly one codepoint')
            records.append(dict(text=text, box=[x0, image.height-y1, x1, image.height-y0],
                                baseline=image.height-y1, size=y1-y0, index=i))
        rows = []
        for group in group_chars(records, []):
            box = union([c['box'] for c in group]); x0, yb, x1, yt = box
            pix = [max(0, int(x0)-2), max(0, int(image.height-yt)-2),
                   min(image.width, int(x1)+3), min(image.height, int(image.height-yb)+3)]
            text = ''.join(c['text'] for c in sorted(group, key=lambda c: c['box'][0]))
            crop = image.crop(pix)
            expected = [[c['box'][0]-pix[0], image.height-c['box'][3]-pix[1],
                         c['box'][2]-pix[0], image.height-c['box'][1]-pix[1]] for c in group if not c['text'].isspace()]
            row = dict(text=text, crop_text=text, bbox_pixel=pix,
                       geometry_basis='djvu_char_pixels', font_names=[])
            row.update(ink_diagnostics(crop, None), char_ink_diagnostics(crop, expected))
            rows.append(row)
        overlaps(rows)
        yield pi+1, image, rows, None


def extract(sources, partition, out, pages=None, seed=20261007):
    books = json.loads(Path(sources).read_text())['books']
    for book in books: rights(book)
    admission = Admission(Partition(partition, seed), out)
    fresh(out)
    out = Path(out); crops = out/'crops'; crops.mkdir()
    page_failures = Counter(); page_receipts = []
    for book in books:
        path = (Path(sources).resolve().parent/book['input_path']).resolve()
        digest = sha256(path)
        if book.get('sha256') and book['sha256'] != digest: raise ValueError('book checksum mismatch')
        group, split = admission.partition.assign(book['source_doc_id'], digest)
        if not split:
            page_failures['excluded_document'] += 1; continue
        import hashlib
        prefix = hashlib.sha256(book['source_doc_id'].encode()).hexdigest()[:20]
        iterator = pdf_pages(path, pages) if path.suffix.lower() == '.pdf' else \
                   djvu_pages(path, out/'djvu'/prefix, pages) if path.suffix.lower() == '.djvu' else None
        if iterator is None: raise ValueError('S2 supports PDF and char-box DjVu only')
        seen = set()
        for page, image, rows, error in iterator:
            if error: page_failures[error] += 1
            page_receipts.append(dict(source_doc_id=book['source_doc_id'], page=page,
                                      document_sha256=digest, error=error, candidates=len(rows)))
            for j, row in enumerate(rows):
                ident = f's2-{prefix}-p{page:05d}-l{j:05d}'
                crop = crops/(ident+'.png'); image.crop(row['bbox_pixel']).save(crop)
                # Retain all geometric rejections and raw layer text from O1.
                admit(row, seen)
                row['text'] = nfc(row['text_raw'])
                row.update(line_id=ident, crop_path=str(crop.resolve()), source_doc_id=book['source_doc_id'],
                           source_dataset=book['source_dataset'], licence=book['licence'],
                           label_tier='silver_ocr_layer', document_sha256=digest, page=page,
                           source_url=book['source_url'], attribution=book['attribution'],
                           licence_evidence=book['licence_evidence'], rights_reviewed=True,
                           geometry_admitted=row['admitted'], layer_text=row['text_raw'],
                           label_status='unadjudicated')
                admission.add(row)
    report = admission.finish()
    from greekocr._vendor.bench.common import write_rows
    write_rows(out/'all.jsonl', admission.rows+admission.rejected)
    report.update(source_manifest_sha256=sha256(sources), page_failures=dict(page_failures), pages=page_receipts,
                  import_policy='adjudicate records.jsonl before training import; silver_ocr_layer is provisional')
    write_json(out/'report.json', report)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True); p.add_argument('--partition', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True); p.add_argument('--pages', help='optional 1-based page list')
    a = p.parse_args(argv)
    print(json.dumps(extract(a.sources, a.partition, a.out,
                            [int(x)-1 for x in a.pages.split(',')] if a.pages else None), indent=2))


if __name__ == '__main__': main()
