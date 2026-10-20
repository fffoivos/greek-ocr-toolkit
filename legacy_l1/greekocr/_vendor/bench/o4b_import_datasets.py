"""Convert published native line pairs/PAGE/ALTO/LMDB/Arrow to import-real JSONL.

No networking, training or direct shard writes. Native payload layouts must be
checked against the downloaded release; rights and work mapping are mandatory.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw
from greekocr._vendor.bench.common import sha256, write_json
from greekocr._vendor.bench.o4b_common import Admission, Partition, fresh, inside, rights

DATASETS = ('polyton_db', 'grpoly_db', 'cllg')


def document_map(root, name):
    """path (native pair/XML/LMDB key) -> reviewed source_doc_id; never guess a book."""
    result = {}
    for row in csv.DictReader(inside(root, name).open(encoding='utf-8'), delimiter='\t'):
        if not row.get('path') or not row.get('source_doc_id') or row['path'] in result:
            raise ValueError('doc map requires unique path and source_doc_id')
        result[row['path']] = row['source_doc_id']
    return result


def local(element):
    return element.tag.rsplit('}', 1)[-1]


def xml_lines(path, image_path, fmt, spec=None):
    """PAGE polygons are masked to retain owned pixels; ALTO uses line rectangles."""
    tree = ET.parse(path).getroot(); spec = spec or {}
    with Image.open(image_path) as im:
        page_image = im.convert('L')
    for i, line in enumerate(x for x in tree.iter() if local(x) == 'TextLine'):
        polygon = None; twin = {}
        if 'layer_text' in line.attrib: twin['layer_text'] = line.attrib['layer_text']
        layer_elements = [x for x in line if local(x) == 'LayerText']
        if layer_elements:
            if len(layer_elements) != 1 or twin: raise ValueError('ambiguous XML layer_text twin')
            twin['layer_text'] = layer_elements[0].text or ''
        if fmt == 'page-xml':
            equivalents = [x for x in line if local(x) == 'TextEquiv']
            if 'text_equiv_index' in spec:
                gold = [x for x in equivalents if x.attrib.get('index') == str(spec['text_equiv_index'])]
            else: gold = equivalents
            if len(gold) != 1:
                raise ValueError('PAGE needs exactly one line-level TextEquiv (choose a reviewed revision)')
            values = [x.text or '' for x in gold[0] if local(x) == 'Unicode']
            if len(values) != 1: raise ValueError('PAGE lacks line-level Unicode')
            text = values[0]
            if 'layer_text_equiv_index' in spec:
                layer = [x for x in equivalents if x.attrib.get('index') == str(spec['layer_text_equiv_index'])]
                values = [x.text or '' for e in layer for x in e if local(x) == 'Unicode']
                if len(layer) != 1 or len(values) != 1 or twin or layer[0] is gold[0]:
                    raise ValueError('ambiguous/missing PAGE layer twin revision')
                twin['layer_text'] = values[0]
            coords = next((x for x in line if local(x) == 'Coords'), None)
            if coords is None: raise ValueError('PAGE line lacks Coords')
            polygon = [tuple(map(float, p.split(','))) for p in coords.attrib['points'].split()]
            if len(polygon) < 3: raise ValueError('invalid PAGE polygon')
            xs, ys = zip(*polygon)
            box = [min(xs), min(ys), max(xs), max(ys)]
        else:
            # ALTO explicit SP elements define spaces; do not invent spaces by joining words.
            children = [x for x in line if local(x) in ('String', 'SP', 'HYP')]
            text = ''.join(' ' if local(x) == 'SP' else x.attrib.get('CONTENT', '') for x in children)
            x, y, w, h = (float(line.attrib[k]) for k in ('HPOS', 'VPOS', 'WIDTH', 'HEIGHT'))
            box = [x, y, x+w, y+h]
        import math
        box = [math.floor(box[0]), math.floor(box[1]), math.ceil(box[2]), math.ceil(box[3])]
        if not (0 <= box[0] < box[2] <= page_image.width and 0 <= box[1] < box[3] <= page_image.height):
            raise ValueError('annotation/image coordinate mismatch; pixel coordinates required')
        crop = page_image.crop(box)
        if polygon:
            mask = Image.new('L', crop.size, 0)
            ImageDraw.Draw(mask).polygon([(x-box[0], y-box[1]) for x, y in polygon], fill=255)
            crop = Image.composite(crop, Image.new('L', crop.size, 255), mask)
        yield dict(text=text, line_id=line.attrib.get('id', line.attrib.get('ID', str(i))),
                   image=crop, native_geometry=box, polygon=polygon, **twin)


def native_rows(spec, root):
    fmt = spec['format']
    docs = document_map(root, spec['document_map']) if spec.get('document_map') else {}
    if fmt == 'pairs':
        # Kraken/Tesseract .gt.txt pairs; also supports corpus *.txt via suffix.
        suffix = spec.get('text_suffix', '.gt.txt')
        for path in sorted(root.rglob('*'+suffix)):
            key = path.relative_to(root).as_posix()
            stem = path.name[:-len(suffix)]
            exts = (spec['image_suffix'],) if spec.get('image_suffix') else ('.png', '.tif', '.tiff', '.jpg', '.jpeg')
            images = [path.with_name(stem+ext) for ext in exts if path.with_name(stem+ext).is_file()]
            if len(images) != 1: raise ValueError(f'need exactly one image for {key}')
            if key not in docs: raise ValueError(f'pair missing document mapping: {key}')
            r = dict(text=path.read_text(encoding='utf-8').lstrip('\ufeff').rstrip('\r\n'), crop_path=images[0],
                     line_id=key, source_doc_id=docs[key], native_path=key)
            if spec.get('layer_text_suffix'):
                layer = path.with_name(stem+spec['layer_text_suffix'])
                if layer.is_file(): r['layer_text'] = layer.read_text(encoding='utf-8').rstrip('\r\n')
            yield r
    elif fmt == 'tsv':
        # Polyton/GRPOLY exported manifests and CLLG line lists. Column names explicit.
        columns = spec.get('columns', {})
        for row in csv.DictReader(inside(root, spec['manifest']).open(encoding='utf-8'), delimiter='\t'):
            get = lambda name: row[columns.get(name, name)]
            key = get('line_id')
            doc = docs.get(key) or get('source_doc_id')
            r = dict(text=get('text'), crop_path=inside(root, get('crop_path')), line_id=key,
                     source_doc_id=doc, native_path=get('crop_path'))
            layer_column = columns.get('layer_text', 'layer_text')
            if 'layer_text' in columns and layer_column not in row: raise ValueError('declared TSV layer_text column missing')
            if row.get(layer_column) is not None: r['layer_text'] = row[layer_column]
            if columns.get('bbox'):
                box = json.loads(row[columns['bbox']])
                with Image.open(r['crop_path']) as image:
                    if len(box) != 4 or not (0 <= box[0] < box[2] <= image.width and
                                             0 <= box[1] < box[3] <= image.height):
                        raise ValueError('invalid TSV crop bbox')
                    r['image'] = image.crop(box).copy()
                r['native_geometry'] = box
            yield r
    elif fmt in ('page-xml', 'alto'):
        for pair in spec['pages']:
            key = pair['xml']
            doc = pair.get('source_doc_id') or docs.get(key)
            if not doc: raise ValueError('XML page missing document identity')
            xml, image = inside(root, key), inside(root, pair['image'])
            for r in xml_lines(xml, image, fmt, spec):
                if r['line_id'] in pair.get('layer_text', {}):
                    if 'layer_text' in r: raise ValueError('ambiguous XML layer_text twin')
                    r['layer_text'] = pair['layer_text'][r['line_id']]
                r.update(line_id=key+'#'+r['line_id'], source_doc_id=doc, native_path=key,
                         annotation_sha256=sha256(xml), page_sha256=sha256(image))
                yield r
    elif fmt == 'lmdb':
        import lmdb  # Optional; never installed or fetched by this tool.
        path = (root/spec['path']).resolve()
        if not path.is_relative_to(root) or not path.exists(): raise ValueError('LMDB path escape or missing')
        env = lmdb.open(str(path),
                        readonly=True, lock=False, readahead=False)
        try:
            with env.begin() as txn:
                count = int(txn.get(b'num-samples'))
                for i in range(1, count+1):
                    key = f'{i:09d}'
                    if key not in docs: raise ValueError('LMDB line needs a reviewed book map: '+key)
                    payload, label = txn.get(('image-'+key).encode()), txn.get(('label-'+key).encode())
                    if payload is None or label is None: raise ValueError('incomplete LMDB pair')
                    with Image.open(io.BytesIO(payload)) as image: crop = image.copy()
                    r = dict(image=crop, text=label.decode(), line_id=key,
                             source_doc_id=docs[key], native_path=spec['path']+'#'+key)
                    layer = txn.get((spec.get('layer_text_prefix', 'layer_text-')+key).encode())
                    if layer is not None: r['layer_text'] = layer.decode('utf-8')
                    yield r
        finally:
            env.close()
    elif fmt == 'kraken-arrow':
        import pyarrow as pa
        import pyarrow.ipc as ipc
        path = inside(root, spec['path'])
        with pa.memory_map(str(path), 'r') as source:
            try: reader = ipc.open_file(source)
            except pa.ArrowInvalid:
                source.seek(0); reader = ipc.open_stream(source)
            batches = (reader.get_batch(i) for i in range(reader.num_record_batches)) if hasattr(reader, 'num_record_batches') else reader
            i = 0
            for batch in batches:
                for row in batch.to_pylist():
                    key = str(row.get('line_id', i)); i += 1
                    if key not in docs: raise ValueError('Arrow line lacks original book map: '+key)
                    with Image.open(io.BytesIO(row[spec.get('image_column', 'image')])) as image: crop = image.copy()
                    r = dict(image=crop, text=row[spec.get('text_column', 'text')], line_id=key,
                             source_doc_id=docs[key], native_path=spec['path']+'#'+key)
                    layer = row.get(spec.get('layer_text_column', 'layer_text'))
                    if layer is not None: r['layer_text'] = layer
                    yield r
    else:
        raise ValueError('unsupported native format: '+fmt)


def convert(manifest, partition, out, seed=20261007):
    manifest = Path(manifest).resolve()
    specs = json.loads(manifest.read_text())['datasets']
    # Validate rights/partition before producing crops; unknown licences never default to gold.
    for spec in specs:
        rights(spec)
        if spec['source_dataset'] not in DATASETS: raise ValueError('unknown S1 dataset')
        if spec['label_tier'] not in ('gold', 'silver'): raise ValueError('S1 tier must be gold or silver')
        if spec['source_dataset'] == 'cllg' and spec['label_tier'] == 'gold' and not spec.get('human_gold_evidence'):
            raise ValueError('CLLG aligned training corpus is silver; gold requires human evidence')
    admission = Admission(Partition(partition, seed), out)
    fresh(out)
    crops = Path(out)/'crops'; crops.mkdir()
    inputs = {str(manifest): sha256(manifest)}
    for spec in specs:
        root = (manifest.parent/spec['root']).resolve()
        # Bind native annotations, document maps and container bytes as well as crops.
        for p in sorted(root.rglob('*')):
            if p.is_file(): inputs[str(p)] = sha256(p)
        for r in native_rows(spec, root):
            native_id = r['line_id']
            import hashlib
            ident = spec['source_dataset']+'-'+hashlib.sha256(native_id.encode()).hexdigest()[:24]
            path = crops/(ident+'.png')
            image = r.pop('image', None)
            if image is None:
                original = Path(r['crop_path'])
                inputs[str(original)] = sha256(original)
                with Image.open(original) as im: image = im.convert('L')
            image.convert('L').save(path)
            r.update(crop_path=str(path.resolve()), line_id=ident, native_line_id=native_id,
                     source_dataset=spec['source_dataset'], label_tier=spec['label_tier'],
                     licence=spec['licence'], source_url=spec['source_url'], attribution=spec['attribution'],
                     licence_evidence=spec['licence_evidence'], rights_reviewed=True)
            admission.add(r)
    report = admission.finish()
    report.update(manifest_sha256=sha256(manifest), input_images_sha256=inputs)
    write_json(Path(out)/'report.json', report)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--partition', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seed', type=int, default=20261007)
    a = p.parse_args(argv)
    print(json.dumps(convert(a.manifest, a.partition, a.out, a.seed), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
