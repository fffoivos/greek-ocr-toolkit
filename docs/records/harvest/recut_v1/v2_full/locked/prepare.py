"""Read-only T6i source resolution. Does not run masking or claim a mock pass."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t6h', HERE.parent / 'run.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
PROJECTS = Path.home() / 'Projects'
EXCLUSIONS = PROJECTS / 'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions'
FUNNEL = PROJECTS / 'greek-ocr-toolkit-sol-funnel-gr/docs/harvest'
WSROOT = PROJECTS / 'greek-ocr-toolkit-sol-wsr0'
WS = WSROOT / 'docs/harvest/wikisource_r0'


def prepare():
    h.offline()
    from PIL import Image, ImageChops
    completion = json.loads((HERE.parent / 'receipts/COMPLETION_RECEIPT_20261017.json').read_text())
    assert completion['status'] == 'completed_and_verified' and completion['verification']['ok']
    assert completion['tree_sha'] == h.TREE and completion['params_sha256'] == h.PARAM
    bindings = {}
    def bind(p):
        bindings[str(p)] = h.sha(p)
        return p
    features_path = bind(FUNNEL / 'screen_v1/features.jsonl')
    features = {r['id']: r for r in h.rows(features_path)}
    ws_path = bind(WS / 'lines.jsonl')
    ws_lines = {r['line_id']: r for r in h.rows(ws_path)}
    pages_path = bind(WS / 'pages.jsonl')
    ws_pages = {r['page_id']: r for r in h.rows(pages_path)}
    keys = {}
    for key_path in sorted((FUNNEL / 'blind_checks_v1').glob('*/*_key.json')):
        if key_path.parent.name not in ('t4c', 'c0'):
            continue
        for card, r in json.loads(bind(key_path).read_text()).items():
            if isinstance(r, dict) and 'line_id' in r:
                crop = key_path.parent / key_path.name.removesuffix('_key.json') / 'crops' / (card + '.png')
                keys.setdefault(r['line_id'], []).append((key_path, crop))
    result = []
    seen = set()
    for stratum, filename, n in [('ii', 'r0_locked_eval_ids.txt', 200),
                                 ('i-b', 'r0_ib_spellcheck_subset_ids.txt', 400)]:
        ids_path = bind(EXCLUSIONS / filename)
        ids = ids_path.read_text().splitlines()
        assert len(ids) == len(set(ids)) == n
        assert not seen.intersection(ids)
        seen.update(ids)
        for ident in ids:
            record = dict(id=ident, stratum=stratum, resolution_status='unresolved',
                          training_release_allowed=False, train_pool_eligible=False)
            try:
                if stratum == 'ii':
                    f = features[ident]
                    candidates = keys.get(ident, [])
                    if not candidates:
                        raise ValueError('no exact T4c/C0 key/card identity')
                    key_path, original = candidates[0]
                    raster, box = Path(f['crop_page_path']), f['crop_bbox']
                    record.update(key_path=str(key_path), card_path=str(original),
                                  feature_crop_sha256=f['crop_sha256'])
                else:
                    line = ws_lines[ident]
                    page = ws_pages[line['page_id']]
                    original = WSROOT / line['crop_path']
                    raster, box = WSROOT / page['image'], line['crop_bbox']
                    if h.sha(original) != line['crop_sha256']:
                        raise ValueError('Wikisource stored crop hash mismatch')
                    if h.sha(raster) != page['image_sha256']:
                        raise ValueError('Wikisource page hash mismatch')
                record.update(raster=str(raster), crop_bbox=box, original_path=str(original))
                allowed = [PROJECTS / ('greek-ocr-toolkit-sol-funnel-' + x) / 'docs/harvest'
                           for x in ('gr', 'ia', 'intl')] + [WS]
                for path in (raster, original):
                    if not any(path.resolve().is_relative_to(root.resolve()) for root in allowed):
                        raise ValueError('source outside authorized read-only roots')
                if len(box) != 4 or any(type(x) is not int for x in box):
                    raise ValueError('invalid recorded crop box')
                with Image.open(raster) as native, Image.open(original) as crop:
                    x0, y0, x1, y1 = box
                    if not (0 <= x0 < x1 <= native.width and 0 <= y0 < y1 <= native.height):
                        raise ValueError('recorded box outside native raster')
                    recut = native.crop(tuple(box))
                    if crop.mode != recut.mode or crop.size != recut.size or ImageChops.difference(crop, recut).getbbox():
                        raise ValueError('stored original/native crop pixels differ')
                    record['scan'] = dict(sha=h.sha(raster), w=native.width, h=native.height, mode=native.mode)
                record.update(original_sha256=h.sha(original), resolution_status='resolved')
            except (OSError, KeyError, ValueError) as e:
                record['reason'] = f'{type(e).__name__}: {e}'
            result.append(record)
    h.write_rows(HERE / 'resolution.jsonl', result)
    h.write_json(HERE / 'preparation.json', dict(task='T6i', masking_started=False,
        mock_5_identical=None, tree_sha=h.TREE, params_sha256=h.PARAM,
        resolution_sha256=h.sha(HERE / 'resolution.jsonl'), source_bindings=bindings,
        per_stratum={s: dict(Counter(r['resolution_status'] for r in result if r['stratum'] == s))
                     for s in ('ii', 'i-b')}))
    print(json.dumps(json.loads((HERE / 'preparation.json').read_text())['per_stratum']))

if __name__ == '__main__':
    prepare()
