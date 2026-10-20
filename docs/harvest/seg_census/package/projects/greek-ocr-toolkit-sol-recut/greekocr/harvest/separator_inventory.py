"""CP5 explicit separator preparation and read-only source-bound cache loading.

No line detector, ownership update, admission-time fallback, or live-run writes.
The existing pixel preparer supplies gutters/rules; build_structure validates
those proposals on original ink using the already recorded row curves.
"""
import json
from pathlib import Path
from . import geometry_observations as g

OPTIONS = dict(pixel_preparer='pages.pixels.prepare_pixels',
               structure='pages.structure.build_structure', refit_rows=False,
               tables=False, orientation=False)


def binding(page):
    return dict(schema='SEG-CP5b-separators-1', page_binding=page['binding'],
                implementation=g.implementation_binding(), adapter_sha256=g.sha(__file__),
                options=OPTIONS)


def prepare(page):
    """Caller must claim the source-bound once-only attempt before this call."""
    from PIL import Image
    from greekocr.pages.pixels import prepare_pixels
    from greekocr.pages.structure import build_structure
    with Image.open(page['source']) as im:
        pixels = prepare_pixels(im)
    # build_structure mutates addresses: supply copies and preserve frozen rows.
    lines = [{k: v.tolist() if hasattr(v, 'tolist') else v for k, v in r.items()
              if not k.startswith('_')} for r in page['rows']]
    structure = build_structure(lines, [], page['binding']['image_size'],
        gutters=pixels.gutters, rules=pixels.column_boundaries,
        page=pixels.gray, _original_ink=pixels.original_ink)
    return dict(binding=binding(page), boundaries=structure['boundaries'],
                rejected_boundaries=structure['rejected_boundaries'],
                columns=structure['columns'],
                invalid_row_ids=[r['row_id'] for r in page.get('invalid_rows', [])])


def load(page, directory):
    directory = Path(directory)
    receipt = json.loads((directory/'receipt.json').read_text())
    if receipt['binding'] != binding(page):
        raise ValueError('stale_separator_inventory')
    if g.sha(directory/'inventory.json') != receipt['inventory_sha256']:
        raise ValueError('corrupt_separator_inventory')
    data = json.loads((directory/'inventory.json').read_text())
    if data['binding'] != receipt['binding']:
        raise ValueError('separator_binding_mismatch')
    return data
