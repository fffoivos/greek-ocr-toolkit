"""Rebase code paths only; retain census_03 input bindings in full mode.

Smoke derives at most 40 rows per parent; SF7 files remain whole-file inputs.
All derived files stay inside the selected census_06 attempt.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
BASE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/code/87407ec7430a375f/projects'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare(source, projects, out, *, smoke=False, split_input=None, frozen_05=None):
    from binding_state import require_bound
    require_bound(source)
    config = deepcopy(source)
    projects, out = Path(projects).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for key in ('codec', 'versions'):
        value = str(config[key])
        if value.startswith('@CENSUS06_PROJECTS@/'):
            config[key] = str(projects/value.split('/', 1)[1])
        elif value.startswith(BASE + '/'):
            config[key] = str(projects/Path(value).relative_to(BASE))
    config['component_roots'] = {k: str(projects/k) for k in source.get('component_roots', {})}
    if split_input:
        config['split_input'] = split_input
    if frozen_05:
        config['frozen_05'] = frozen_05
    if smoke:
        config['census06_smoke'] = True
        selected = {}
        for parent in config['parents']:
            original = deepcopy(parent)
            if sha(parent['path']) != parent['sha256']:
                raise ValueError('parent input SHA mismatch')
            lines = []
            with Path(parent['path']).open() as stream:
                for line in stream:
                    if len(lines) == 40:
                        break
                    if line.strip():
                        lines.append(line)
            selected[parent['id']] = {json.loads(line)['id'] for line in lines}
            path = out/(parent['id'] + '.smoke.jsonl')
            path.write_text(''.join(lines))
            parent.update(path=str(path), sha256=sha(path), rows=len(lines), source_input=original)
        for index, correction in enumerate(config.get('corrections', [])):
            original = deepcopy(correction)
            if sha(correction['path']) != correction['sha256']:
                raise ValueError('correction input SHA mismatch')
            if correction['tool'] == 'polytonic':
                correction.update(parent_manifest_sha256=next(
                    p['sha256'] for p in config['parents'] if p['id'] == correction['parent_id']), source_input=original)
                continue  # Load/index the entire hash-bound SF7 file in the census.
            path = out/f'correction-{index}.smoke.jsonl'
            with Path(correction['path']).open() as stream, path.open('w') as target:
                for line in stream:
                    r = json.loads(line)
                    rid = r.get('binding', {}).get('id', r.get('id', r.get('line_id')))
                    if rid in selected[correction['parent_id']]:
                        target.write(line)
            correction.update(path=str(path), sha256=sha(path), parent_manifest_sha256=next(
                p['sha256'] for p in config['parents'] if p['id'] == correction['parent_id']), source_input=original)
    else:
        for key in ('parents', 'corrections', 'metadata', 'final_policy'):
            assert config.get(key) == source.get(key), key
    (out/'config.json').write_text(json.dumps(config, sort_keys=True)+'\n')
    (out/'input_preservation.json').write_text(json.dumps(dict(
        mode='smoke' if smoke else 'full', original_inputs_preserved=True,
        parents=source['parents'], corrections=source.get('corrections', []), metadata=source['metadata'],
        source_config_sha256=hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()), indent=2)+'\n')
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=D/'census06_config.json')
    parser.add_argument('--projects', type=Path, default=D/'package/projects')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--split-file')
    parser.add_argument('--split-sha256')
    args = parser.parse_args()
    if bool(args.split_file) != bool(args.split_sha256):
        parser.error('split-file and split-sha256 must be pinned together')
    if not args.smoke and not args.split_file:
        parser.error('full mode requires split-file and split-sha256')
    split = dict(path=args.split_file, sha256=args.split_sha256) if args.split_file else None
    prepare(json.loads(args.source.read_text()), args.projects, args.out, smoke=args.smoke, split_input=split)


if __name__ == '__main__':
    main()
