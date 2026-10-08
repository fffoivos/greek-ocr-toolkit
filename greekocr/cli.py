"""Offline CLI; acquiring source data and deploying remain explicit Python APIs."""
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
    commands.add_parser('recipes')
    verify = commands.add_parser('verify-recipe'); verify.add_argument('recipe'); verify.add_argument('--sha256')
    score = commands.add_parser('score'); score.add_argument('readings', type=Path)
    annotate = commands.add_parser('annotate'); annotate.add_argument('text')
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
    measure = geometry_commands.add_parser('measure', help='compare original/refined crops using an explicit reader')
    measure.add_argument('--lines', type=Path, required=True, help='JSONL with original crop, page, box and text')
    measure.add_argument('--reader', required=True, help='importable module:callable accepting a crop Path')
    measure.add_argument('--out', type=Path, required=True, help='new directory for measurement receipt and crops')
    measure.add_argument('--pad', type=int, default=16)
    args = parser.parse_args(argv)
    try:
        if args.command == 'recipes':
            from greekocr.synth import recipe_registry
            result = {k:dict(path=str(v.path),sha256=v.sha256,origin_commit=v.origin_commit) for k,v in recipe_registry().items()}
        elif args.command == 'verify-recipe':
            from greekocr.synth import verify_recipe_sha
            result = dict(sha256=verify_recipe_sha(args.recipe, args.sha256))
        elif args.command == 'annotate':
            from greekocr.annotate import line_categories, word_tags, script_class
            result = dict(script_class=script_class(args.text), categories=line_categories(dict(text=args.text)), word_tags=word_tags(args.text))
        elif args.command == 'score':
            from greekocr.score import score_readings
            result = score_readings([json.loads(s) for s in args.readings.read_text().splitlines() if s.strip()])
        elif args.command == 'validate-mix':
            from greekocr.synth import validate_mix
            result = validate_mix(args.manifest, repo=args.repo, role=args.role)
        elif args.command == 'geometry':
            if args.geometry_command == 'measure':
                result = _geometry_measure(args.lines, args.reader, args.out, args.pad)
            else:
                result = _geometry_refine(args.image, args.boxes, args.out, args.pad, args.profile)
        else:
            from greekocr.deploy.node_envs import environment_plan
            result = environment_plan(args.name,args.venv,wheelhouse=args.wheelhouse,paddle_requirements=args.paddle_requirements)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ImportError, AttributeError) as error:
        print(str(error),file=__import__('sys').stderr)
        return 3


def _geometry_refine(image_path: Path, boxes_path: Path, out: Path, pad: int, profile: str) -> dict:
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
        lines = refine_page_lines(source, boxes, pad=pad)
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
    receipt = dict(schema=GEOMETRY_POLICY, image_sha256=file_sha256(image_path),
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
