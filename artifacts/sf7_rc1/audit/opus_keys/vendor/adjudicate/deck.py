"""Blind decks from explicit local data; private keys never enter the blind tree."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import io
import html
from importlib.resources import files
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import tempfile
from typing import Any
from PIL import Image

__all__ = ['build_deck', 'crop_image', 'leak_scan']

# Padding is in units of the native line height. Caps apply before emission.
_PROFILES = {
    'letter': (.6, 3., 900, Image.Resampling.LANCZOS),
    'word': (.6, 3., 900, Image.Resampling.LANCZOS),
    'mark': (.6, 3., 900, Image.Resampling.LANCZOS),
    'line': (0., 1., None, Image.Resampling.LANCZOS),
    'page': (0., 1., None, Image.Resampling.LANCZOS),
}


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def crop_image(image: Image.Image | str | Path, profile: str = 'word', *, bbox: list[float] | None = None, crop_box: list[float] | None = None, zoom_cap: float = 3.) -> tuple[Image.Image, dict]:
    """Apply a named native crop profile, returning pixels and private geometry."""
    if profile not in _PROFILES:
        raise ValueError('unknown crop profile')
    if not math.isfinite(zoom_cap) or zoom_cap <= 0 or zoom_cap > 3:
        raise ValueError('blind zoom cap must be in (0, 3]')
    if not isinstance(image, Image.Image):
        with Image.open(image) as opened:
            image = opened.copy()
    padding, zoom, width_cap, interpolation = _PROFILES[profile]
    width, height = image.size
    if crop_box is not None:
        box = list(crop_box)
    elif bbox is not None:
        x0, y0, x1, y1 = bbox
        pad = padding * height
        box = [max(0, int(x0-pad)), 0, min(width, max(int(x0+1), math.ceil(x1+pad))), height]
    elif profile in ('line', 'page'):
        box = [0, 0, width, height]
    else:
        raise ValueError('target crop requires bbox or crop_box')
    if (len(box) != 4 or not all(math.isfinite(x) for x in box) or
            not (0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height)):
        raise ValueError('crop outside native image')
    cropped = image.crop(box).convert('RGB')
    scale = min(zoom, zoom_cap, width_cap / max(1, cropped.width) if width_cap else zoom)
    cropped = cropped.resize((max(1, round(cropped.width*scale)), max(1, round(cropped.height*scale))), interpolation)
    return cropped, dict(crop_box=box, zoom_scale=scale, profile=profile)


def leak_scan(blind_dir: str | Path, forbidden: list[str] | None = None) -> dict:
    """Scan emitted text, paths and PNG metadata; intrinsic printed content is retained."""
    root = Path(blind_dir)
    findings = []
    needles = set(forbidden or []) | {'candidate_sources', 'known_answer', 'expected_choice', 'source_crop', 'line_id', 'control', 'Google', 'google'}
    for path in sorted(root.rglob('*')):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            findings.append(dict(file=relative, reason='symlink'))
            continue
        if not path.is_file():
            continue
        for needle in needles:
            if needle and needle in relative:
                findings.append(dict(file=relative, reason='private_path', needle=needle))
        if path.suffix == '.png':
            if path.stem != hashlib.sha256(path.read_bytes()).hexdigest():
                findings.append(dict(file=relative, reason='not_content_hash'))
            with Image.open(path) as image:
                if image.info:
                    findings.append(dict(file=relative, reason='image_metadata', metadata=sorted(image.info)))
        else:
            try:
                text = path.read_text()
            except UnicodeError:
                findings.append(dict(file=relative, reason='unexpected_binary'))
                continue
            for needle in needles:
                if needle and needle in text:
                    findings.append(dict(file=relative, reason='private_text', needle=needle))
            if re.search(r'(?:/Users/|/home/|file://|\.\./)', text):
                findings.append(dict(file=relative, reason='external_path'))
    return dict(passed=not findings, findings=findings,
                limits='Text/path/PNG metadata only; native printed text can identify its source. Sibling keys remain reachable by explicit path under full filesystem access.')


def build_deck(spec: dict[str, Any]) -> dict:
    """Build a new two-reader deck with shuffled controls and an exclusive sibling key.

    spec: blind_dir, optional private_dir, items, controls, seed, profile,
    control_fraction (default .08). Each input has image, options, private
    provenance and bbox/crop_box. Historical replay requires protocol='historical'
    and preserve_order=True; it labels preserved old ordering explicitly.
    """
    from .protocol import INSTRUCTIONS, ANSWER_SCHEMA
    def serializable(value):
        if isinstance(value, Path): return str(value)
        raise TypeError('spec must be JSON data: ' + type(value).__name__)
    spec_bytes = json.dumps(spec, sort_keys=True, ensure_ascii=False, allow_nan=False, default=serializable).encode()
    blind = Path(spec['blind_dir']).resolve()
    private = Path(spec.get('private_dir', blind.parent/'private')).resolve()
    if private == blind or private.is_relative_to(blind) or blind.is_relative_to(private) or not private.is_relative_to(blind.parent):
        raise ValueError('private tree must be a sibling of the blind tree')
    if blind.exists():
        raise FileExistsError(blind)
    if (private/'items_key.json').exists():
        raise FileExistsError('private key is write-once')
    historical = spec.get('protocol') == 'historical'
    if spec.get('readers', 2) != 2:
        raise ValueError('every new deck requires two readers plus tiebreak; single-reader protocols are descriptive only')
    if spec.get('preserve_order') and not historical:
        raise ValueError('fixed ordering is historical replay only')
    items = [dict(deepcopy(it), control=False) for it in spec['items']]
    controls = [dict(deepcopy(it), control=True) for it in spec.get('controls', [])]
    for control in controls:
        if control.get('pixel_verified') is not True or 'known_answer' not in control:
            raise ValueError('controls require pixel-verified literal truth')
    records = items + controls
    if not records:
        raise ValueError('empty deck')
    fraction = len(controls)/len(records)
    required = spec.get('control_fraction', .08)
    if not 0 <= required <= 1 or fraction < required or (not historical and not controls):
        raise ValueError('insufficient planted controls')
    rng = random.Random(spec.get('seed', 20261017))
    if historical and spec.get('preserve_order'):
        records.sort(key=lambda r: r['position'])
    else:
        rng.shuffle(records)
    blind.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.adjudicate-', dir=blind.parent))
    key = []
    public = []
    image_map = []
    forbidden = list(spec.get('forbidden', []))
    def image_file(image):
        # Reconstruct pixels without carrying PNG info, EXIF, comments or paths.
        if image.mode == 'P':
            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
        with io.BytesIO() as stream:
            clean = Image.frombytes(image.mode, image.size, image.tobytes())
            clean.save(stream, 'PNG')
            data = stream.getvalue()
        name = 'img/' + hashlib.sha256(data).hexdigest() + '.png'
        (stage/'img').mkdir(exist_ok=True)
        (stage/name).write_bytes(data)
        return name
    try:
        for index, record in enumerate(records):
            ident = record.get('id') if historical else f'item{index:05d}'
            if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', ident):
                raise ValueError('opaque card ID required')
            options = record.get('options', [] if record.get('free_text') else None)
            if not isinstance(options, (dict, list)):
                raise ValueError('options must be strings')
            forms = list(options.values()) if isinstance(options, dict) else list(options)
            if not all(isinstance(f, str) for f in forms) or not (0 if record.get('free_text') else 1) <= len(forms) <= 3 or len(set(forms)) != len(forms):
                raise ValueError('one to three unique literal options required')
            if not (historical and spec.get('preserve_order')):
                rng.shuffle(forms)
                if len(forms) > 1 and forms == record.get("previous_options"):
                    forms = forms[1:] + forms[:1]
            opts = {chr(65+j): f for j, f in enumerate(forms)}
            if record['control'] and not record.get('free_text') and record['known_answer'] not in forms:
                raise ValueError('control answer missing from options')
            with Image.open(record['image']) as opened:
                original = opened.copy()
            if record.get('prepared_image'):
                if not historical:
                    raise ValueError('pre-rendered crops are historical replay only')
                scale = record['zoom_scale']
                if not math.isfinite(scale) or not 0 < scale <= 3:
                    raise ValueError('zoom cap')
                cropped = original
                geometry = dict(zoom_scale=scale, crop_box=record.get('crop_box'), profile=record.get('profile', 'word'))
            else:
                cropped, geometry = crop_image(original, record.get('profile', spec.get('profile', 'word')), bbox=record.get('bbox'), crop_box=record.get('crop_box', record.get('word_box')), zoom_cap=spec.get('zoom_cap', 3.))
            img = image_file(cropped)
            line = record.get('line_image', record['image'])
            with Image.open(line) as opened:
                line_img = image_file(opened.copy())
            pub = dict(id=ident, img=img, line_img=line_img)
            if record.get('profile', spec.get('profile', 'word')) == 'mark' and 'letter_box' in record:
                from .mark_profile import mark_views
                views = mark_views(original, record['word_box'], record['letter_box'])
                img = image_file(views['word'])
                pub['img'] = img
                pub['mark_img'] = image_file(views['letter'])
                geometry.update(word_box=record['word_box'], letter_box=record['letter_box'],
                                word_scale=3, letter_scale=8)

            if historical and spec.get('schema') == 'r0': pub.update(opts)
            else: pub.update(options=opts, other_options=['none of these', 'unreadable'])
            extra = record.get('public', {})
            if set(extra) - {'anchor_index', 'target_head'}:
                raise ValueError('unsupported public card metadata')
            if 'anchor_index' in extra and (type(extra['anchor_index']) is not int or extra['anchor_index'] < 0):
                raise ValueError('invalid anchor index')
            if 'target_head' in extra and extra['target_head'] not in ('breathing', 'accent', 'diaeresis', 'subscript'):
                raise ValueError('invalid target head')
            pub.update(extra)
            public.append(pub)
            provenance = deepcopy(record.get('private', {}))
            for name in ('line_id', 'doc', 'source', 'crop'):
                if provenance.get(name): forbidden.append(str(provenance[name]))
            key.append(dict(id=ident, public=pub, control=record['control'],
                            known_answer=record.get('known_answer'), expected_fields=deepcopy(record.get('expected_fields', {})), expected_choice=next((k for k, v in opts.items() if v == record.get('known_answer')), None),
                            geometry=geometry, provenance=provenance))
            image_map.append(dict(id=ident, old_img=record.get('old_img'), img=img, old_line_img=record.get('old_line_img'), line_img=line_img))
        if len({r['id'] for r in public}) != len(public):
            raise ValueError('duplicate card IDs')
        (stage/'items_blind.json').write_text(_json(public))
        (stage/'reader_2.json').write_text(_json(list(reversed(public))))
        (stage/'README.md').write_text(INSTRUCTIONS)
        (stage/'answer_schema.json').write_text(_json(ANSWER_SCHEMA))
        viewer_js = files(__package__).joinpath('deck.js').read_text()
        manifest = json.dumps(public, ensure_ascii=False).replace('</', '<\\/')
        deck_hash = hashlib.sha256(_json(public).encode()).hexdigest()
        (stage/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Independent print reading</title><style>body{font:18px Georgia;max-width:1100px;margin:auto;padding:16px}article{border:1px solid #aaa;padding:12px;margin:20px 0;overflow:auto}img{display:block;max-width:100%;margin:8px 0}label{display:block;margin:8px 0}input,textarea{width:95%}</style>'
            '<body data-deck="'+deck_hash+'"><h1 id="assignment"></h1><p>'+html.escape(INSTRUCTIONS)+'</p>'
            '<button id="export">Export answers</button><main id="cards"></main><script id="manifest" type="application/json">'+manifest+'</script><script>'+viewer_js+'</script>')
        scan = leak_scan(stage, forbidden)
        if not scan['passed']:
            raise ValueError('blind leak scan failed: ' + _json(scan))
        private.mkdir(parents=True, exist_ok=True)
        # O_EXCL, even on an interrupted/raced build. Never overwrite or unlink a key.
        key_bytes = _json(key)
        fd = os.open(private/'items_key.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(key_bytes)
        stage.rename(blind)
    finally:
        if stage.exists(): shutil.rmtree(stage)
    receipt = dict(items=len(public), controls=len(controls), control_fraction=fraction,
                blind_dir=str(blind), private_key=str(private/'items_key.json'),
                image_map=image_map, leak_scan=scan, readers=2, tiebreak=True,
                protocol='historical-replay' if historical else 'two-reader-v1',
                protocol_changes=['content-hash images; image metadata stripped', 'shared instructions/schema/viewer; code-emitted reader-2 reversal'],
                blind_sha256=hashlib.sha256((blind/'items_blind.json').read_bytes()).hexdigest(),
                key_sha256=hashlib.sha256((private/'items_key.json').read_bytes()).hexdigest())

    package = Path(__file__).parent
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(package.iterdir()) if p.suffix in ('.py', '.js', '.css')}
    receipt.update(spec_sha256=hashlib.sha256(spec_bytes).hexdigest(),
                   code_sha256=hashlib.sha256(_json(code).encode()).hexdigest(), code_files=code,
                   files={str(p.relative_to(blind)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(blind.rglob('*')) if p.is_file()},
                   other_options=['none of these', 'unreadable'])
    (private/'receipt.json').write_text(_json(receipt))
    return receipt
