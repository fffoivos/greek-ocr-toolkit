"""O5 runtime identity; legacy attribution is for reporting, never cache reuse."""
import json
import os
from pathlib import Path
import sys

RUNTIME_FIELDS = ('device_type', 'amp_dtype', 'torch_version', 'deterministic_flags')


def runtime_binding(device):
    import torch
    # The trainer/evaluator use flat imports from train/, including train.py.
    from greekocr.train.model import amp_dtype_for

    device = torch.device(device)
    dtype = amp_dtype_for(device)
    return {
        'device_type': device.type,
        'amp_dtype': str(dtype).removeprefix('torch.') if dtype is not None else 'float32',
        'torch_version': str(torch.__version__),
        'deterministic_flags': {
            'algorithms': torch.are_deterministic_algorithms_enabled(),
            'warn_only': torch.is_deterministic_algorithms_warn_only_enabled(),
            'cudnn_enabled': torch.backends.cudnn.enabled,
            'cudnn_deterministic': torch.backends.cudnn.deterministic,
            'cudnn_benchmark': torch.backends.cudnn.benchmark,
            'cudnn_allow_tf32': torch.backends.cudnn.allow_tf32,
            'matmul_allow_tf32': torch.backends.cuda.matmul.allow_tf32,
            'float32_matmul_precision': torch.get_float32_matmul_precision(),
            'cublas_workspace_config': os.environ.get('CUBLAS_WORKSPACE_CONFIG'),
        },
    }


def receipt_runtime(binding, legacy_device=None):
    present = set(RUNTIME_FIELDS) & binding.keys()
    if present:
        if present != set(RUNTIME_FIELDS):
            raise ValueError(f'incomplete O5 runtime binding: {sorted(present)}')
        return {key: binding[key] for key in RUNTIME_FIELDS}
    if legacy_device and legacy_device.split(':')[0] == 'cuda':
        return dict(device_type='legacy-cuda', amp_dtype='unknown', torch_version='unknown',
                    deterministic_flags='unknown')
    raise ValueError('missing O5 runtime binding (legacy attribution requires runner device cuda)')


def require_same_runtime(saved, requested):
    if saved != requested:
        raise ValueError('O5 runtime mismatch: saved runtime '
                         f'{json.dumps(saved, sort_keys=True)}; requested runtime '
                         f'{json.dumps(requested, sort_keys=True)}; select a fresh O5_OUT')
