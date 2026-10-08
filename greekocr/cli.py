"""Offline tools and explicit, bounded web page acquisition."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Sequence
__all__ = ['main']

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='greekocr')
    parser.add_argument('--version', action='version', version='greekocr 0.1.0')
    commands = parser.add_subparsers(dest='command', required=True)
    from greekocr.verify.cli import add_parser as add_verify_parser
    add_verify_parser(commands)
    commands.add_parser('recipes')
    verify = commands.add_parser('verify-recipe'); verify.add_argument('recipe'); verify.add_argument('--sha256')
    score = commands.add_parser('score'); score.add_argument('readings', type=Path)
    annotate = commands.add_parser('annotate', help='text tags, line metadata or distribution reports')
    annotate.add_argument('action', help='lines, report, text, or legacy text to tag')
    annotate.add_argument('inputs', nargs='*', type=str)
    annotate.add_argument('--catalogue', type=Path)
    annotate.add_argument('--lexicon', type=Path)
    annotate.add_argument('--font-model', type=Path)
    annotate.add_argument('--out', type=Path, help='new metadata JSONL or Markdown report')
    mix = commands.add_parser('validate-mix'); mix.add_argument('manifest', type=Path)
    mix.add_argument('--repo', type=Path, required=True); mix.add_argument('--role', default='train')
    env = commands.add_parser('env-plan'); env.add_argument('name'); env.add_argument('venv', type=Path)
    env.add_argument('--wheelhouse', type=Path); env.add_argument('--paddle-requirements', type=Path)
    geometry = commands.add_parser('geometry', help='offline pixel-box line rectification')
    geometry_commands = geometry.add_subparsers(dest='geometry_command', required=True)
    refine = geometry_commands.add_parser('refine')
    refine.add_argument('--image', type=Path, required=True)
    refine.add_argument('--boxes', type=Path, required=True, help='JSON pixel boxes or bbox_pixel/text rows')
    refine.add_argument('--out', type=Path, required=True, help='new output directory; rejected crops are retained')
    refine.add_argument('--pad', type=int, default=16)
    refine.add_argument('--profile', choices=('scan', 'born_digital'), default='scan')
    refine.add_argument('--policy', choices=('v1', 'v2', 'v3'), default='v3')
    measure = geometry_commands.add_parser('measure', help='compare original/refined crops using an explicit reader')
    measure.add_argument('--lines', type=Path, required=True, help='JSONL with original crop, page, box and text')
    measure.add_argument('--reader', required=True, help='importable module:callable accepting a crop Path')
    measure.add_argument('--out', type=Path, required=True, help='new directory for measurement receipt and crops')
    measure.add_argument('--pad', type=int, default=16)
    evaluate = geometry_commands.add_parser('evaluate', help='reference-free pixel and independent reader comparison')
    evaluate.add_argument('--records', type=Path, required=True)
    evaluate.add_argument('--page-images', type=Path, help='local directory or JSON page-id to image-path mapping')
    evaluate.add_argument('--policies', default='original,v1,v2,v3')
    evaluate.add_argument('--readers', default='cllg', help='comma-separated independent reader names')
    evaluate.add_argument('--reader-config', type=Path, help='JSON of locally staged cllg/ours checkpoints and runtime paths')
    evaluate.add_argument('--reader', action='append', default=[], help='NAME=MODULE:CALLABLE local reader override')
    evaluate.add_argument('--out', type=Path, required=True)
    evaluate.add_argument('--pad', type=int, default=16)
    evaluate.add_argument('--blind-seed', type=int, default=0)
    web = commands.add_parser('web', help='render HTML as receipt-bound exact page data')
    web_commands = web.add_subparsers(dest='web_command', required=True)
    render = web_commands.add_parser('render')
    render.add_argument('--sources', nargs='+', required=True, help='catalog names, URLs, HTML paths or JSON manifests')
    render.add_argument('--max-pages', type=int, default=10)
    render.add_argument('--dest', type=Path, required=True)
    render.add_argument('--viewport', default='794x1123')
    render.add_argument('--scale', type=float, default=2.0)
    render.add_argument('--licence', help='caller supplied licence for direct paths/URLs')
    render.add_argument('--offline', action='store_true')
    render.add_argument('--allow-media', action='store_true')
    render.add_argument('--no-pdf', action='store_true')
    render.add_argument('--no-screenshot', action='store_true')
    render.add_argument('--category', help='Wikisource category name')
    render.add_argument('--mastodon-instance', default='https://mastodon.social')
    render.add_argument('--interval', type=float, default=1.0, help='per-origin request interval, >=1 second')
    render.add_argument('--timeout', type=float, default=30.0, help='request/navigation timeout in seconds')
    records = web_commands.add_parser('records')
    records.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            from greekocr.verify.cli import run as run_verify
            result = run_verify(args)
        elif args.command == 'recipes':
            from greekocr.synth import recipe_registry
            result = {k:dict(path=str(v.path),sha256=v.sha256,origin_commit=v.origin_commit) for k,v in recipe_registry().items()}
        elif args.command == 'verify-recipe':
            from greekocr.synth import verify_recipe_sha
            result = dict(sha256=verify_recipe_sha(args.recipe, args.sha256))
        elif args.command == 'annotate':
            if args.action in ('lines', 'report'):
                from greekocr.annotate import annotate_records, distribution_report
                inputs = args.inputs
                if args.action == 'lines':
                    if len(inputs) == 2 and args.out is None:
                        records, output = inputs
                    elif len(inputs) == 1 and args.out is not None:
                        records, output = inputs[0], args.out
                    else:
                        raise ValueError('annotate lines needs INPUT OUTPUT (or INPUT --out OUTPUT)')
                    result = annotate_records(records, output, catalogue=args.catalogue, lexicon=args.lexicon, font_model=args.font_model)
                else:
                    if len(inputs) != 1:
                        raise ValueError('annotate report needs one annotated JSONL or synthetic shard directory')
                    report = distribution_report(inputs[0], catalogue=args.catalogue, lexicon=args.lexicon, font_model=args.font_model)
                    if args.out is not None:
                        with args.out.open('x', encoding='utf-8') as stream:
                            stream.write(report)
                    print(report, end='')
                    return 0
            else:
                from greekocr.annotate import line_categories, word_tags, script_class
                if args.action == 'text' and len(args.inputs) == 1:
                    text = args.inputs[0]
                elif not args.inputs:
                    text = args.action
                else:
                    raise ValueError('text tagging accepts one quoted text argument')
                result = dict(script_class=script_class(text), categories=line_categories(dict(text=text)), word_tags=word_tags(text))
        elif args.command == 'score':
            from greekocr.score import score_readings
            result = score_readings([json.loads(s) for s in args.readings.read_text().splitlines() if s.strip()])
        elif args.command == 'validate-mix':
            from greekocr.synth import validate_mix
            result = validate_mix(args.manifest, repo=args.repo, role=args.role)
        elif args.command == 'geometry':
            if args.geometry_command == 'measure':
                result = _geometry_measure(args.lines, args.reader, args.out, args.pad)
            elif args.geometry_command == 'evaluate':
                result = _geometry_evaluate(args)
            else:
                result = _geometry_refine(args.image, args.boxes, args.out, args.pad, args.profile, args.policy)
        elif args.command == 'web':
            if args.web_command == 'records':
                from greekocr.real.sources.web_render import page_records
                result = page_records(args.directory)
            else:
                result = _web_render(args)
        else:
            from greekocr.deploy.node_envs import environment_plan
            result = environment_plan(args.name,args.venv,wheelhouse=args.wheelhouse,paddle_requirements=args.paddle_requirements)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ImportError, AttributeError, RuntimeError) as error:
        print(str(error),file=__import__('sys').stderr)
        return 3


def _web_render(args: argparse.Namespace) -> dict:
    from dataclasses import asdict
    from itertools import islice
    from greekocr.real.sources.web_render import render_pages
    from greekocr.real.sources.web_sources import source_pages
    from greekocr.real.sources.web_sources import _PoliteHTTP
    if args.max_pages < 1:
        raise ValueError('max-pages must be positive')
    if args.offline and any(not Path(source).is_file() for source in args.sources):
        raise ValueError('offline render requires local HTML or recorded HTML manifests')
    client = _PoliteHTTP(interval=args.interval, timeout=args.timeout)
    try:
        viewport = tuple(int(v) for v in args.viewport.lower().split('x'))
    except ValueError as error:
        raise ValueError('viewport must be WIDTHxHEIGHT') from error

    def inputs():
        named = []
        for source in args.sources:
            path = Path(source)
            if not path.is_file() and not source.startswith(('http://', 'https://')):
                named.extend(source.split(','))
                continue
            if named:
                yield from source_pages(tuple(named), args.max_pages, category=args.category,
                                        mastodon_instance=args.mastodon_instance, client=client)
                named.clear()
            if path.is_file() and path.suffix.lower() == '.json':
                manifest = json.loads(path.read_text())
                entries = manifest.get('pages', manifest.get('sources')) if isinstance(manifest, dict) else manifest
                if not isinstance(entries, list):
                    raise ValueError('source manifest must be a list or contain pages/sources')
                for entry in entries:
                    spec = dict(entry) if isinstance(entry, dict) else {'url': entry}
                    target = spec.get('url') or spec.get('path')
                    if target and not str(target).startswith(('http://', 'https://')):
                        spec['url'] = str((path.resolve().parent / target).resolve())
                    yield spec
            elif path.is_file() or source.startswith(('http://', 'https://')):
                yield dict(url=source, licence=args.licence)
        if named:
            yield from source_pages(tuple(named), args.max_pages, category=args.category,
                                    mastodon_instance=args.mastodon_instance, client=client)

    pages = render_pages(islice(inputs(), args.max_pages), args.dest, viewport=viewport,
                         scale=args.scale, print_to_pdf=not args.no_pdf,
                         screenshot=not args.no_screenshot, block_media=not args.allow_media,
                         offline=args.offline, client=client, interval=args.interval, timeout=args.timeout)
    return dict(pages=[asdict(page) for page in pages])


def _geometry_refine(image_path: Path, boxes_path: Path, out: Path, pad: int, profile: str,
                     policy: str = 'v3') -> dict:
    import hashlib
    from PIL import Image
    from greekocr.real.geometry import GEOMETRY_POLICY, refine_page_lines, scan_admission
    from greekocr.ops.receipts import file_sha256
    boxes = json.loads(boxes_path.read_text())
    if isinstance(boxes, dict):
        boxes = boxes['boxes']
    if not isinstance(boxes, list):
        raise ValueError('boxes JSON must be a list or an object containing boxes')
    with Image.open(image_path) as source:
        source.load()
        lines = refine_page_lines(source, boxes, pad=pad, policy=policy)
    decisions = [scan_admission(line.diagnostics, profile=profile) for line in lines]
    # Validate all inputs before creating output; never replace an existing extraction.
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for index, (line, admission) in enumerate(zip(lines, decisions)):
        name = f'line{index:05d}.png'
        line.image.save(out/name)
        rows.append(line.receipt() | {'crop_path': name,
                                      'crop_sha256': file_sha256(out/name),
                                      'raster_sha256': hashlib.sha256(line.image.tobytes()).hexdigest(),
                                      'admission': admission.receipt()})
    receipt = dict(schema=f'o4d-local-line-geometry-{policy}', image_sha256=file_sha256(image_path),
                   boxes_sha256=file_sha256(boxes_path), coordinate_system='top-origin half-open page pixels',
                   pad=pad, profile=profile, input_boxes=len(boxes), output_lines=len(lines),
                   admitted=sum(d.admitted for d in decisions), lines=rows,
                   label_tier='silver_ocr_layer', label_status='unadjudicated',
                   label_assignment='caller assigns split-line text')
    (out/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    return receipt


def _geometry_measure(lines_path: Path, reader_spec: str, out: Path, pad: int) -> dict:
    from importlib import import_module
    from greekocr.real.geometry_measure import measure_geometry
    module, separator, attribute = reader_spec.partition(':')
    if not module or not separator or not attribute:
        raise ValueError('--reader must be module:callable accepting a crop Path')
    reader = getattr(import_module(module), attribute)
    return measure_geometry(lines_path, reader, out=out, pad=pad, reader_name=reader_spec)


def _geometry_evaluate(args: argparse.Namespace) -> dict:
    from importlib import import_module
    import os
    from greekocr.real.geometry_evaluate import POLICIES, evaluate_geometry
    selected = args.readers.split(',')
    policies = args.policies.split(',')
    if not selected or any(not n for n in selected) or len(set(selected)) != len(selected):
        raise ValueError('--readers must contain unique nonempty names')
    if any(p not in POLICIES for p in policies) or len(set(policies)) != len(policies):
        raise ValueError('--policies must contain unique choices from original,v1,v2,v3')
    if args.pad < 0:
        raise ValueError('pad must be a nonnegative integer')
    if args.out.exists():
        raise FileExistsError(f'File exists: {args.out}')
    config = json.loads(args.reader_config.read_text(encoding='utf-8')) if args.reader_config else {}
    if not isinstance(config, dict):
        raise ValueError('reader-config must be a JSON object keyed by reader name')
    overrides = {}
    for entry in args.reader:
        name, sep, spec = entry.partition('=')
        if not sep or name not in selected or name in overrides:
            raise ValueError('--reader must be a unique selected NAME=MODULE:CALLABLE')
        overrides[name] = spec
    base = args.reader_config.resolve().parent if args.reader_config else Path.cwd()
    def local_path(value: str | None) -> Path:
        if not value:
            raise ValueError('reader requires a locally staged checkpoint/codec; use --reader-config')
        return (base/Path(value).expanduser()).absolute()
    readers, owned = {}, []
    try:
        for name in selected:
            spec = config.get(name, {})
            if not isinstance(spec, dict):
                raise ValueError(f'reader-config {name} must be an object')
            callable_spec = overrides.get(name, spec.get('callable'))
            if callable_spec:
                module, sep, attribute = callable_spec.partition(':')
                if not module or not sep or not attribute:
                    raise ValueError('reader callable must be MODULE:CALLABLE accepting a crop Path')
                readers[name] = getattr(import_module(module), attribute)
            elif name == 'cllg':
                from greekocr.readers.cllg import load_cllg_worker
                if os.environ.get('CLLG_ACCELERATOR', 'cpu') != 'cpu':
                    raise ValueError('geometry evaluate requires CLLG_ACCELERATOR=cpu')
                contract = json.loads(local_path(spec['contract']).read_text()) if spec.get('contract') else None
                reader = load_cllg_worker(local_path(spec.get('checkpoint', os.environ.get('CLLG_CHECKPOINT'))),
                                          contract, python=local_path(spec['python']) if spec.get('python') else None,
                                          timeout=spec.get('timeout', 300), confidence=True)
                owned.append(reader)
                readers[name] = reader.read
            elif name == 'ours':
                from greekocr.readers.ours import load_ours
                reader = load_ours(local_path(spec.get('checkpoint', os.environ.get('GREEKOCR_OURS_CHECKPOINT'))),
                                   local_path(spec.get('codec', os.environ.get('GREEKOCR_OURS_CODEC'))))
                readers[name] = reader.read
            else:
                raise ValueError(f'unknown local reader {name}; supply --reader {name}=MODULE:CALLABLE')
        return evaluate_geometry(args.records, page_images=args.page_images, policies=policies,
                                 readers=readers, out=args.out, pad=args.pad, blind_seed=args.blind_seed)
    finally:
        for reader in owned:
            reader.close()
