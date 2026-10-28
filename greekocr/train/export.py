"""Export a trusted trainer checkpoint without changing any tensor.

A release directory contains model.safetensors, config.json, codec.json and
MANIFEST.json. Safetensors metadata binds the exact config and codec bytes;
the manifest records all three file hashes and input custody. See COMMANDS.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from safetensors.torch import save_file, load_file

from .cer import load_codec
from .ckpt_io import sha256_file
from .model import DET_PAD_MARGIN, build_model

CODEC_SHA256 = 'eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6'
NORMALISATION = {'mean': 0.5, 'std': 0.5, 'padding': 'own-background-right-halo',
                 'pad_margin': DET_PAD_MARGIN}
DECODE = {'method': 'greedy_ctc', 'internal': 'NFD', 'output': 'NFC'}


def validate_config(config, codec_path):
    """Only the trained release profile; reject unsupported config rather than guessing."""
    expected = dict(arch='compact', head='nfd', n_classes=266, input_height=48,
                    normalisation=NORMALISATION, decode=DECODE, codec_sha256=CODEC_SHA256,
                    codec_version='v2.1')
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValueError(f'unsupported release config: {key}')
    if type(config.get('width_mult')) not in (int, float) or config['width_mult'] not in (1, 1.5, 2):
        raise ValueError('unsupported release width_mult')
    codec = load_codec(str(codec_path))
    if sha256_file(str(codec_path)) != CODEC_SHA256 or codec.n_classes != 266 or codec.version != 'v2.1':
        raise ValueError('release codec SHA/version/class count mismatch')
    return codec


def load_state_strict(model, state):
    # torch's strict=True tolerates absent BatchNorm num_batches_tracked for
    # backwards compatibility. A sealed release requires exact keys/dtypes too.
    expected = model.state_dict()
    if set(state) != set(expected):
        raise RuntimeError('Missing key or unexpected key in release state_dict')
    if any(state[k].dtype != expected[k].dtype for k in expected):
        raise ValueError('release state dtype mismatch; implicit casting refused')
    model.load_state_dict(state, strict=True)


def export_checkpoint(checkpoint, run_config, codec_path, output, *, trusted_checkpoint=False):
    """Full resume .pt files require trusted=True pickle export in the training environment.

    The exact supplied .pt is read, never a possibly stale safetensors sibling.
    This function is not called by the inference loader.
    """
    if not trusted_checkpoint:
        raise ValueError('export requires explicit trusted_checkpoint for own-custody trainer .pt')
    checkpoint, run_config, codec_path, output = map(Path, (checkpoint, run_config, codec_path, output))
    run = json.loads(run_config.read_text())
    parameters = run.get('parameters', run.get('args', run))
    width = parameters.get('width_mult', run.get('width_mult'))
    if width is None:
        raise ValueError('run config must declare width_mult')
    ck = torch.load(checkpoint, map_location='cpu', weights_only=False)  # own-custody export only
    config = dict(arch='compact', width_mult=width, head='nfd', n_classes=266,
                  input_height=48, normalisation=NORMALISATION, decode=DECODE,
                  codec_version='v2.1', codec_sha256=CODEC_SHA256)
    validate_config(config, codec_path)
    for key in ('arch', 'width_mult', 'head', 'n_classes', 'codec_version', 'codec_sha256'):
        if ck.get(key) != config[key]:
            raise ValueError(f'checkpoint/config mismatch: {key}')
        if key in parameters and parameters[key] != config[key]:
            raise ValueError(f'run config mismatch: {key}')
    sd = ck['model']
    if not all(t.dtype == torch.float32 for t in sd.values() if t.is_floating_point()):
        raise ValueError('release requires original fp32 weights; no casting is performed')
    model, _ = build_model(n_classes=266, arch='compact', width_mult=width, verbose=False)
    load_state_strict(model, sd)
    output.mkdir(parents=True, exist_ok=False)
    (output/'codec.json').write_bytes(codec_path.read_bytes())
    (output/'config.json').write_text(json.dumps(config, sort_keys=True, indent=2)+'\n')
    metadata = {key: str(config[key]) for key in ('arch', 'width_mult', 'head', 'n_classes',
                                                'codec_version', 'codec_sha256')}
    metadata['config_sha256'] = sha256_file(str(output/'config.json'))
    tensors = {k: v.detach().cpu().contiguous().clone() for k, v in sd.items()}
    save_file(tensors, str(output/'model.safetensors'), metadata=metadata)
    readback = load_file(str(output/'model.safetensors'))
    if set(readback) != set(sd) or any(not torch.equal(readback[k], sd[k].cpu()) for k in sd):
        raise ValueError('export tensor readback differs from checkpoint')
    def receipt(p):
        return dict(bytes=p.stat().st_size, sha256=sha256_file(str(p)))
    manifest = dict(schema='greekocr-release-v1',
                    files={name: receipt(output/name) for name in ('model.safetensors', 'config.json', 'codec.json')},
                    inputs={str(p): receipt(p) for p in (checkpoint, run_config, codec_path)},
                    tensor_readback='identical; no weight casting or transformation')
    (output/'MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
    return manifest


def load_release(directory):
    """Safe release load, strict tensor structure and exact config/codec binding."""
    from safetensors import safe_open
    directory = Path(directory)
    manifest = json.loads((directory/'MANIFEST.json').read_text())
    if manifest.get('schema') != 'greekocr-release-v1':
        raise ValueError('unsupported release manifest')
    for name in ('model.safetensors', 'config.json', 'codec.json'):
        p = directory/name
        if p.is_symlink():
            raise ValueError('release files must be regular files')
        actual = dict(bytes=p.stat().st_size, sha256=sha256_file(str(p)))
        if manifest['files'].get(name) != actual:
            raise ValueError(f'release SHA mismatch: {name}')
    config = json.loads((directory/'config.json').read_text())
    codec = validate_config(config, directory/'codec.json')
    with safe_open(str(directory/'model.safetensors'), framework='pt', device='cpu') as f:
        metadata = f.metadata() or {}
    for key in ('arch', 'width_mult', 'head', 'n_classes', 'codec_version', 'codec_sha256'):
        # The exporter preserves the JSON number representation in metadata.
        if metadata.get(key) != str(config[key]):
            raise ValueError(f'release metadata mismatch: {key}')
    if metadata.get('config_sha256') != sha256_file(str(directory/'config.json')):
        raise ValueError('release config SHA binding mismatch')
    sd = load_file(str(directory/'model.safetensors'))
    if any(t.is_floating_point() and t.dtype != torch.float32 for t in sd.values()):
        raise ValueError('release requires fp32 weights')
    model, _ = build_model(n_classes=266, arch='compact', width_mult=config['width_mult'], verbose=False)
    load_state_strict(model, sd)
    return model.eval(), codec, config


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('checkpoint', 'run-config', 'codec', 'output'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--trusted-checkpoint', action='store_true', help='Own-custody .pt; enables pickle only for export')
    args = parser.parse_args(argv)
    export_checkpoint(args.checkpoint, args.run_config, args.codec, args.output,
                      trusted_checkpoint=args.trusted_checkpoint)


if __name__ == '__main__':
    main()
