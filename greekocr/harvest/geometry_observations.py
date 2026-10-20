"""CP2 read-only cache observations. No detector or cache-miss preparation path.

Collector geometry is evidence, not a qualified whole-word/structural decision.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import gzip
from collections.abc import Mapping
import hashlib
from types import ModuleType
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from PIL import Image, __version__ as pillow_version
from greekocr.glyphs import foreign_ink

COLLECTOR = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect'
OPTIONS = dict(join_lines=True, granularity='rows', tables=False, statistics=False, orientation=False)
SCHEMA = 'greekocr-labelfix-geometry-1'
PARAMS_SHA = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'


def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()


def code_identity(root):
    """Exactly geometry.io.detector_identity's complete pages/glyphs scheme."""
    root = Path(root)
    paths = sorted([*(root/'pages').glob('*.py'), *(root/'glyphs').glob('*.py')])
    if not paths or not (root/'pages').is_dir() or not (root/'glyphs').is_dir():
        raise ValueError('missing_detector_code')
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def vendor_ownership(collector=COLLECTOR):
    path = Path(collector)/'collect_v3/vendor/geometry/ownership.py'
    # Read/compile explicitly: SourceFileLoader can write collector bytecode.
    module = ModuleType('_seg_cp2_ownership')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def vendor_magnitude(collector=COLLECTOR):
    """Read-only existing local guide-band measurement; no detector imports."""
    path = Path(collector)/'collect_v3/vendor/geometry/magnitude.py'
    namespace = {'__name__': '_seg_cp3_magnitude', '__file__': str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
    return namespace


def implementation_binding(collector=COLLECTOR):
    root = Path(__file__).resolve().parents[1]
    return dict(detector_sha256=code_identity(Path(collector)/'greekocr'),
                runtime_geometry_sha256=code_identity(root),
                adapter_sha256=sha(__file__),
                row_inclusion_sha256=sha(Path(__file__).with_name('row_inclusion.py')),
                neighbour_adapter_sha256=sha(Path(__file__).with_name('neighbour_words.py')),
                admission_adapter_sha256=sha(Path(__file__).with_name('admission.py')),
                vendor={name: sha(Path(collector)/'collect_v3/vendor/geometry'/name)
                        for name in ('io.py', 'ownership.py', 'magnitude.py')},
                ownership_params_sha256=PARAMS_SHA,
                dependencies=dict(python=platform.python_version(), numpy=np.__version__,
                                  scipy=scipy.__version__, pillow=pillow_version,
                                  opencv=__import__('cv2').__version__))


def frozen():
    digest = hashlib.sha256(json.dumps(foreign_ink.PARAMETERS, sort_keys=True,
                                      separators=(',', ':')).encode()).hexdigest()
    if digest != PARAMS_SHA:
        raise ValueError('foreign-ink parameters changed')
    return digest


def prepare_geometry_row(r, structural, ink, labels, ownership):
    """Established CP2 row validation/quarantine, shared with live observations.

    Only a nonpositive outer envelope is row-local unavailability. Never fix
    curves or suppress malformed arrays, labels, identities or body guides.
    """
    foreign_ink._centre_fit(r)
    n = r['x1'] - r['x0']
    curves = {k: np.asarray(r[k], dtype=float) for k in ownership.CURVES}
    if (not 0 <= r['x0'] < r['x1'] <= ink.shape[1] or
            any(v.shape != (n,) or not np.isfinite(v).all() for v in curves.values())):
        raise ValueError('invalid_detector_geometry')
    delta = curves['bottom'] - curves['top']
    if np.any(delta <= 0):
        if not structural.get('line_indices'):
            raise ValueError('missing_invalid_row_line_indices')
        return None, dict(r, status='invalid_geometry',
            reason='nonpositive_row_envelope', minimum_bottom_minus_top=float(delta.min()),
            unavailable_box=[min(r['x0'], r['owned_box'][0]),
                min(r['owned_box'][1], *(float(v.min()) for v in curves.values())),
                max(r['x1'], r['owned_box'][2]),
                max(r['owned_box'][3], *(float(v.max()) for v in curves.values()))])
    return ownership.prepare_row(r, ink, labels), None


def load_cached_page(source, cache, expected_sha, *, collector=COLLECTOR):
    """Cache-hit branch of geometry.io.cache_page, with strict frame/options checks.

    Does not call cache_page (which can write on a miss). No lock or mkdir.
    The source path as well as its bytes is bound, never its basename alone.
    """
    frozen()
    source, cache = Path(source).resolve(), Path(cache)
    binding = implementation_binding(collector)
    receipt = json.loads((cache/'receipt.json').read_text())
    if (receipt['schema'] != SCHEMA or receipt['source_sha256'] != expected_sha
            or Path(receipt['source']).resolve() != source or sha(source) != expected_sha
            or receipt['detector_sha256'] != binding['detector_sha256']
            or receipt['options'] != OPTIONS
            or receipt['row_ink_source'] != 'detector_assigned_components'):
        raise ValueError('stale_detector_cache')
    for name, field in [('detector.json.gz','geometry_sha256'), ('ink.png','mask_sha256'),
                        ('labels.npz','labels_sha256')]:
        if sha(cache/name) != receipt[field]:
            raise ValueError('corrupt_detector_cache:'+name)
    data = json.loads(gzip.decompress((_data_input(cache/'detector.json.gz')).read_bytes()))
    with Image.open(source) as image:
        size = image.size
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('ambiguous_source_frame')
    with Image.open(_data_input(cache/'ink.png')) as mask:
        ink = np.asarray(mask).astype(bool)
    with np.load(_data_input(cache/'labels.npz'), allow_pickle=False) as archive:
        labels = archive['labels']
    if (data['schema'] != SCHEMA or list(size) != data['image_size']
            or ink.shape != size[::-1] or labels.shape != ink.shape
            or not np.issubdtype(labels.dtype, np.integer) or np.any(labels < 0)
            or not np.array_equal(labels > 0, ink)):
        raise ValueError('invalid_source_frame_or_labels')
    structure = {r['id']: r for r in data['structure_rows']}
    if len(structure) != len(data['structure_rows']):
        raise ValueError('duplicate_structural_row')
    ownership = vendor_ownership(collector)
    rows = []; invalid_rows = []
    present_ids = set(map(int, np.unique(labels)))
    for r in data['rows']:
        required = {'row_id', 'column_id', 'block_id', 'component_ids', 'owned_box',
                    'neighbours', 'x0', 'x1', 'xheight', *ownership.CURVES}
        if not required <= r.keys() or r['row_id'] not in structure:
            raise ValueError('missing_row_geometry_fields')
        structural = structure[r['row_id']]
        if any(r[k] != structural[k] for k in ('column_id','block_id')):
            raise ValueError('inconsistent_structural_row')
        if not r['component_ids'] or not set(r['component_ids']) <= present_ids:
            raise ValueError('missing_native_component')
        prepared,invalid=prepare_geometry_row(r,structural,ink,labels,ownership)
        if invalid is not None:invalid_rows.append(invalid)
        else:rows.append(prepared)
    ink.flags.writeable = labels.flags.writeable = False
    binding.update(source=str(source), source_sha256=expected_sha, frame=0,
                   cache_directory=str(cache.resolve()),
                   image_size=list(size), options=OPTIONS, cache_receipt=receipt,
                   receipt_sha256=sha(cache/'receipt.json'))
    return dict(rows=rows, invalid_rows=invalid_rows, invalid_geometry_count=len(invalid_rows),
                structure=structure, ink=ink, labels=labels,
                binding=binding, source=source, ownership=ownership)


def invalid_geometry_dependencies(page, box, *, target_row_id=None):
    """Conservative crop/target/direct-neighbour quarantine, never a clean row.

    Serialized neighbours name detector line indices (not list positions).
    Structural line_indices bind them to the physical row identities.
    """
    invalid = page.get('invalid_rows', [])
    if not invalid:
        return []
    bad_ids = {r['row_id'] for r in invalid}
    bad_lines = {i for rid in bad_ids for i in page['structure'][rid].get('line_indices', [])}
    affected = set()
    for r in invalid:
        a,b,c,d = r['unavailable_box']
        if r['row_id'] == target_row_id or (a < box[2] and box[0] < c and b < box[3] and box[1] < d):
            affected.add(r['row_id'])
    for r in page['rows']:
        relevant = r['row_id'] == target_row_id or page['ownership'].box_hits(r, box).any()
        if relevant:
            refs = {i for value in r['neighbours'].values()
                    for i in (value if isinstance(value, list) else [value])
                    if isinstance(i, (int, np.integer)) and i >= 0}
            if refs & bad_lines:
                affected.update(rid for rid in bad_ids
                    if set(page['structure'][rid].get('line_indices', [])) & refs)
    return sorted(affected)


def measure_foreign(page, line, neighbours, box):
    """One non-painting entrypoint for the unmodified 801d517e core.

    MaskPage inputs retain their exact ink (for equivalence checks). Raw inputs
    use prepare_mask_page; no fill/ring/masking operation is called.
    """
    frozen()
    if isinstance(page, Mapping):
        # Cached native foreground is already receipt-bound. The measure-only
        # core reads ink alone; painting fields deliberately remain absent.
        prepared = foreign_ink.MaskPage(None, None, page['ink'], page['labels'], [])
    else:
        prepared = page if isinstance(page, foreign_ink.MaskPage) else foreign_ink.prepare_mask_page(page)
    if len(box) != 4 or any(not isinstance(v, (int, np.integer)) for v in box):
        raise ValueError('integer native crop rectangle required')
    x0,y0,x1,y1 = box
    if not (0 <= x0 < x1 <= prepared.ink.shape[1] and 0 <= y0 < y1 <= prepared.ink.shape[0]):
        raise ValueError('crop must lie inside page')
    if not neighbours:
        return dict(status='unavailable', reason='missing_neighbour', mask=None)
    from greekocr.glyphs.recut import LineFit
    own = line if isinstance(line, LineFit) else foreign_ink._centre_fit(line)
    others = [r if isinstance(r, LineFit) else foreign_ink._centre_fit(r) for r in neighbours]
    mask = foreign_ink._foreign_mask(prepared.ink, own, others, tuple(box))
    return dict(status='measured', reason=None, mask=mask, prepared=prepared)


def observe_crop(page, box, *, target_row_id=None):
    """Record row-assigned hits before target selection; never break a tie.

    With no supplied structural identity, only a unique supported row is a
    target. Multiple supported rows remain ambiguous for later CP3 work.
    """
    if (len(box) != 4 or any(not isinstance(v,(int,np.integer)) for v in box)
            or not (0 <= box[0] < box[2] <= page['ink'].shape[1]
                    and 0 <= box[1] < box[3] <= page['ink'].shape[0])):
        raise ValueError('invalid_native_crop_box')
    from .row_inclusion import supported_rows
    row_evidence = supported_rows(page, box)
    ownership = page['ownership']
    hits = [dict(row_id=r['row_id'], column_id=r['column_id'],
                 component_ids=r['component_ids'], xheight=r['xheight'],
                 pixels=int(ownership.box_hits(r, box).sum())) for r in page['rows']]
    supported = {r['row_id'] for r in hits if r['pixels']}
    result = dict(status='unavailable', matched=False, components=[], xheight=None,
                  crop_box=list(box), row_hits=hits, binding=page['binding'],
                  row_inclusion=row_evidence)
    invalid = invalid_geometry_dependencies(page, box, target_row_id=target_row_id)
    if invalid:
        return dict(result, reason='invalid_geometry', invalid_row_ids=invalid)
    if target_row_id is None:
        if len(supported) != 1:
            return dict(result, reason='ambiguous_target' if supported else 'missing_target')
        target_row_id = next(iter(supported))
    own = [r for r in page['rows'] if r['row_id'] == target_row_id]
    if len(own) != 1 or target_row_id not in supported:
        return dict(result, reason='ambiguous_target' if len(own)>1 else 'missing_target')
    neighbours = [r for r in page['rows'] if r['row_id'] != target_row_id]
    with Image.open(page['source']) as opened:
        observed = measure_foreign(opened, own[0], neighbours, box)
    if observed['status'] != 'measured':
        return dict(result, reason=observed['reason'])
    # Preserve both native label planes: detector ids for row assignment and
    # frozen core ids for mask equivalence; never relabel a clipped foreign mask.
    mask = observed['mask']
    x0,y0,x1,y1 = box
    native = page['labels'][y0:y1,x0:x1]
    ids = [int(i) for i in np.unique(native[mask]) if i]
    return dict(result, status='measured', matched=True, reason=None,
                target_row_id=target_row_id, xheight=own[0]['xheight'],
                neighbours=[dict(row_id=r['row_id'], xheight=r['xheight'],
                                 component_ids=r['component_ids']) for r in neighbours],
                native_foreign_component_ids=ids,
                foreign_mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest(),
                foreign_pixels=int(mask.sum()),
                # CP4 owns the word predicate. This receipt is not a clean-word
                # certificate and must not be passed through legacy runs().
                decision_status='unqualified_cp2')


def admission_evidence_status(record, measurement):
    """Fail closed at the public boundary; CP2 has no qualified predicate.

    A caller-supplied qualification tag is not authority. Even a positively
    tagged observation must bind the current source, code, payloads and crop.
    Later checkpoints must supply a separately reviewed qualified consumer;
    legacy components/runs never participate in this boundary.
    """
    if not isinstance(measurement, Mapping):
        return 'unavailable', 'missing_measurement'
    if measurement.get('status') != 'measured' or measurement.get('matched') is not True:
        return 'unavailable', 'unavailable_or_legacy_measurement'
    binding = measurement.get('binding')
    if not isinstance(binding, Mapping):
        return 'unavailable', 'missing_binding'
    try:
        # Re-read the receipt, complete implementation identity and all payload
        # hashes. A digest-shaped string or a saved status is not validation.
        source = Path(binding['source']).resolve()
        if (record['image_sha256'] != binding['source_sha256']
                or Path(record['crop_source_image']).resolve() != source
                or record['page_id'] != Path(binding['cache_directory']).name
                or list(record['crop_bbox']) != measurement['crop_box']
                or record['geometry_row_id'] != measurement['target_row_id']):
            return 'unavailable', 'record_binding_mismatch'
        page = load_cached_page(source, binding['cache_directory'], binding['source_sha256'])
        if page['binding'] != binding:
            return 'unavailable', 'stale_binding'
        expected = observe_crop(page, record['crop_bbox'], target_row_id=record['geometry_row_id'])
        if dict(measurement, decision_status='unqualified_cp2') != expected:
            return 'unavailable', 'observation_binding_mismatch'
    except (KeyError, ValueError, OSError, TypeError, AttributeError, EOFError):
        return 'unavailable', 'invalid_binding'
    if measurement.get('decision_status') != 'qualified':
        return 'unresolved', 'unqualified_measurement'
    # Valid geometry does not qualify the absent CP3/CP4 decision policy.
    return 'unresolved', 'qualification_not_supported_cp2'
