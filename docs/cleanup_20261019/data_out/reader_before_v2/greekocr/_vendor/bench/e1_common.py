"""E1 byte custody and small atomic writers. No training/runtime imports."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from greekocr._vendor.train.mix import sha256, shard_inventory

FRACTIONS = (0, 25, 50, 75, 100)
SEEDS = (0, 1, 2)
CLASSES = ('greek_mono', 'greek_poly', 'greek_latin_cs', 'latin', 'cyrillic', 'cyrillic_latin_cs')


def read_json(path):
    return json.loads(Path(path).read_text())


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    os.replace(temp, path)


def run(cmd, **kwargs):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), cwd=ROOT, check=True, **kwargs)


def files_binding(paths):
    return {str(Path(p).resolve()): sha256(p) for p in sorted(set(map(Path, paths))) if p.is_file()}


def code_files():
    return [p for pattern in ('bench/e1*', 'train/*.py', 'factory/src/*.rs', 'factory/*.json',
                             'codec/v1.json', 'assets/fonts/*', 'assets/watermarks/*',
                             'factory/exclusions/*', 'bench/o5_prepare.py', 'bench/codec_coverage.py',
                             'bench/common.py', 'bench/o5_runtime.py', 'factory/Cargo.toml', 'factory/Cargo.lock')
            for p in ROOT.glob(pattern) if p.is_file()]


def head(repo=ROOT):
    return subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()


def runtime_binding(device='cuda'):
    """O5 runtime identity plus the CUDA/GPU implementation used by E1."""
    import torch
    from greekocr._vendor.bench.o5_runtime import runtime_binding as base_binding
    result=base_binding(device)
    result.update(cuda_version=torch.version.cuda,cudnn_version=torch.backends.cudnn.version())
    if str(device).split(':')[0] == 'cuda' and torch.cuda.is_available():
        properties=torch.cuda.get_device_properties(torch.device(device))
        result.update(gpu_name=properties.name,gpu_capability=[properties.major,properties.minor],
                      gpu_uuid=str(getattr(properties,'uuid','unavailable')))
    return result


def check_files(binding):
    for name, expected in binding.items():
        if sha256(name) != expected:
            raise ValueError(f'changed hash-bound input: {name}; use a fresh E1_OUT')


def verify_prepared(out, *, historical_code_revision=None):
    info = read_json(Path(out)/'build_info.json')
    if historical_code_revision is None:
        check_files(info['inputs'])
    else:
        # E2 re-executes bound DATA after reviewed code-only custody changes.
        # Changed code must match the retained historical revision's bytes;
        # data, recipes, fonts, executable and all factory artifacts stay strict.
        import hashlib
        rebuilt = []
        for name, expected in info['inputs'].items():
            path = Path(name).resolve()
            if sha256(path) == expected: continue
            if path.name == 'linefactory' and path.parent.name == 'release':
                # Coordinator disclosure (8 Oct 2026): the E1-era executable bytes were lost with the
                # terminated pod; a rebuilt executable is accepted ONLY because every shard inventory
                # below must still match the E1 receipts byte-for-byte (59/59 reproduced on the node).
                rebuilt.append(dict(input=name, expected_sha256=expected, actual_sha256=sha256(path)))
                continue
            if path.suffix not in ('.py', '.rs') or not path.is_relative_to(ROOT):
                raise ValueError(f'changed E1 data input: {name}')
            original = subprocess.check_output(['git','-C',str(ROOT),'show',
                historical_code_revision+':'+str(path.relative_to(ROOT))])
            if hashlib.sha256(original).hexdigest() != expected:
                raise ValueError(f'E1 historical source receipt mismatch: {name}')
    NON_DATA_ARTIFACTS = ('pool.jsonl.ingest_report.json', 'real/word_tags.jsonl')  # reports/sidecars, never training bytes
    changed_non_data = []
    for name, expected in info['artifacts'].items():
        if sha256(Path(out)/name) != expected:
            if historical_code_revision is not None and name in NON_DATA_ARTIFACTS:
                changed_non_data.append(dict(artifact=name, expected_sha256=expected, actual_sha256=sha256(Path(out)/name)))
                continue
            raise ValueError(f'changed E1 artifact: {name}')
    for name in ('real', 'synthetic', 'synthetic_heldout'):
        receipt = read_json(Path(out)/name/'build_info.json')
        if shard_inventory(Path(out)/name) != receipt['shard_sha256']:
            raise ValueError(f'changed factory shard inventory: {name}')
    if historical_code_revision is not None and (rebuilt or changed_non_data):
        disclosure = Path(out)/'factory_executable_rebuilt.json'
        atomic_json(disclosure, dict(disclosure='E1 factory executable rebuilt and/or non-data artifacts regenerated; accepted because all shard inventories and every data artifact match the E1 receipts',
                                    rebuilt=rebuilt, changed_non_data_artifacts=changed_non_data))
        info['factory_executable_rebuilt'] = rebuilt
        info['changed_non_data_artifacts'] = changed_non_data
    return info


def shards(root, split):
    import pyarrow.parquet as pq
    return [r for p in sorted((Path(root)/split).glob('shard-*.parquet')) for r in pq.read_table(p).to_pylist()]
