"""Immutable upstream detector identity and verified Hugging Face acquisition."""
from pathlib import Path
import hashlib
import os

SMALL_DETECTOR = {
    'repo_id': 'PaddlePaddle/PP-OCRv6_small_det_onnx',
    'revision': '28fe5895c24fd108c19eb3e8479f4ab385fbfc62',
    'filename': 'inference.onnx',
    'sha256': 'd73e0058b7a8086bbd57f3d10b8bcd4ff95363f67e06e2762b5e814fe9c9410e',
    'bytes': 9880512,
    'licence': 'Apache-2.0',
    'upstream_url': 'https://huggingface.co/PaddlePaddle/PP-OCRv6_small_det_onnx/tree/28fe5895c24fd108c19eb3e8479f4ab385fbfc62',
}


def cache_root():
    return Path(os.environ.get('GREEKOCR_CACHE_DIR', '~/.cache/greekocr')).expanduser()


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path, identity):
    path = Path(path)
    if path.stat().st_size != identity['bytes'] or sha256(path) != identity['sha256']:
        raise ValueError(f'Asset size/SHA256 mismatch: {path}; file retained')
    return path


def fetch_small_detector():
    from huggingface_hub import hf_hub_download
    from huggingface_hub.utils import LocalEntryNotFoundError
    pin = SMALL_DETECTOR
    kwargs = dict(repo_id=pin['repo_id'], filename=pin['filename'], revision=pin['revision'],
                  cache_dir=str(cache_root() / 'detectors'))
    try:
        path = hf_hub_download(**kwargs, local_files_only=True)
    except LocalEntryNotFoundError:
        path = hf_hub_download(**kwargs)
    return verify_file(path, pin)
