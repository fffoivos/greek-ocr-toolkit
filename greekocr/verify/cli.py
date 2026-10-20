"""CLI adapters; images/text/calibrate are offline, vlm is explicitly online."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
import json
from pathlib import Path
from .images import readability_profile, render_overlay
from .text import text_checks
from .judges import CallBudget, vlm_annotate, judge_texts
from .calibration import calibrate


def add_parser(commands):
    parser = commands.add_parser('verify', help='independent image readability and Greek-text checks')
    actions = parser.add_subparsers(dest='verify_command', required=True)
    images = actions.add_parser('images', help='offline raster checks and optional spatial overlays')
    images.add_argument('directory', type=Path)
    images.add_argument('--out', type=Path)
    images.add_argument('--profiles', action='store_true')
    images.add_argument('--overlays', type=Path)
    text = actions.add_parser('text', help='offline Unicode checks; --judge explicitly enables Luna')
    text.add_argument('file', type=Path)
    text.add_argument('--out', type=Path)
    text.add_argument('--judge', action='store_true')
    text.add_argument('--cache', type=Path, default=Path('docs/verify/text_cache.jsonl'))
    vlm = actions.add_parser('vlm', help='explicit bounded Luna calls with image-only inputs')
    vlm.add_argument('directory', type=Path)
    vlm.add_argument('--out', type=Path)
    vlm.add_argument('--cache', type=Path, default=Path('docs/verify/image_cache.jsonl'))
    vlm.add_argument('--batch-size', type=int, choices=range(1,5), default=4)
    for p in (text,vlm):
        p.add_argument('--model', default='gpt-6-luna')
        p.add_argument('--budget', type=int, default=500)
        p.add_argument('--ledger', type=Path, default=Path('docs/verify/calls.jsonl'))
        p.add_argument('--receipts-dir', type=Path, default=Path('docs/verify/receipts'))
    calibration = actions.add_parser('calibrate', help='offline confusion tables from saved checks and labels')
    calibration.add_argument('--checks', type=Path, default=Path('docs/verify/image_checks_sample.jsonl'))
    calibration.add_argument('--labels', type=Path, default=Path('docs/verify/vlm_readability_sample.jsonl'))
    calibration.add_argument('--owner-index', type=Path, default=Path('tests/fixtures/o4d_lines/index.json'))
    calibration.add_argument('--out', type=Path, default=Path('docs/verify/CALIBRATION.md'))


def crop_records(directory: Path) -> list[dict]:
    """Respect fixture indexes (44 means 44; regression pairs aren't silently added)."""
    index = directory/'index.json'
    if index.exists():
        data = json.loads(index.read_text())
        if not isinstance(data, dict) or not isinstance(data.get('lines'), list):
            raise ValueError('crop index must contain lines')
        records = []
        for row in data['lines']:
            path = directory/row['file']
            if not path.is_file():
                path = directory/'crops'/row['file']
            if not path.is_file():
                raise ValueError(f'indexed crop is missing: {row["file"]}')
            records.append({'crop': str(path), 'line_id': row.get('line_id', path.stem)})
        return records
    if not directory.is_dir():
        raise ValueError('image directory does not exist')
    records = [{'crop': str(p), 'line_id': p.stem} for p in sorted(directory.rglob('*'))
               if p.suffix.lower() in ('.png','.jpg','.jpeg','.tif','.tiff','.bmp')]
    if not records:
        raise ValueError('image directory contains no crops')
    return records


def reading_records(path: Path) -> list[dict]:
    content = path.read_text(encoding='utf-8')
    if path.suffix == '.json':
        data = json.loads(content)
        entries = data.get('lines', []) if isinstance(data, dict) else data
    elif path.suffix == '.jsonl':
        entries = [json.loads(line) for line in content.splitlines() if line.strip()]
    else:
        entries = content.splitlines()
    rows=[]
    for number, entry in enumerate(entries):
        if isinstance(entry, str):
            rows.append({'id': str(number), 'text': entry})
        elif isinstance(entry, dict):
            # Intentionally no layer_text/layer fallback: that is another OCR.
            key = next((k for k in ('cllg_text','cllg','text','reading') if k in entry), None)
            if key is None or not isinstance(entry[key], str):
                raise ValueError('reading row needs cllg_text/cllg/text/reading; layer OCR is not a reading reference')
            rows.append({'id': entry.get('line_id', str(number)), 'text': entry[key]})
        else:
            raise ValueError('invalid reading row')
    return rows


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in _data_input(path).read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in rows),encoding='utf-8')


def run(args) -> dict:
    if args.verify_command == 'calibrate':
        notes = json.loads(args.owner_index.read_text()).get('owner_notes', {}) if args.owner_index.exists() else {}
        return calibrate(_read_jsonl(args.checks), _read_jsonl(args.labels), owner_notes=notes, output=args.out)
    if args.verify_command == 'text':
        rows = reading_records(args.file)
        output = [r | {'checks': text_checks(r['text']).to_dict()} for r in rows]
        if args.judge:
            judged = judge_texts([r['text'] for r in rows], model=args.model, cache=args.cache,
                                  budget=CallBudget(args.ledger,args.budget),receipts_dir=args.receipts_dir)
            output = [r | {'judgement':j['judgement'],'receipt':j['receipt']} for r,j in zip(output,judged)]
    else:
        rows = crop_records(args.directory)
        if args.verify_command == 'vlm':
            output = vlm_annotate([r['crop'] for r in rows], model=args.model, cache=args.cache,
                                  batch_size=args.batch_size, budget=CallBudget(args.ledger,args.budget),
                                  receipts_dir=args.receipts_dir)
            output = [j | {'line_id':r['line_id']} for j,r in zip(output,rows)]
        else:
            import hashlib
            output=[]
            if args.overlays:
                args.overlays.mkdir(parents=True,exist_ok=True)
            for row in rows:
                profile=readability_profile(row['crop'])
                result=row | {'crop_sha256': hashlib.sha256(Path(row['crop']).read_bytes()).hexdigest(),
                              'checks': profile.summaries.to_dict()}
                if args.profiles:
                    result['profile']=profile.to_dict()
                if args.overlays:
                    # Hash avoids colliding stems in nested directories.
                    target=args.overlays/(Path(row['crop']).stem+'-'+result['crop_sha256'][:8]+'.png')
                    target.write_bytes(render_overlay(row['crop'],profile))
                    result['overlay']=str(target)
                output.append(result)
    if args.out:
        write_jsonl(args.out,output)
        return {'rows': len(output),'out': str(args.out)}
    return {'rows': output}
