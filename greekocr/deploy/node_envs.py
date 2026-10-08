"""Reviewable Linux node setup plans. Planning installs nothing."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import shlex
from greekocr.types import PathLike
__all__ = ['EnvironmentRecipe', 'environment_recipes', 'environment_plan', 'write_environment_script']
KRAKEN_WHEEL_SHA256 = '82faba07d9fa4746cb822c669e822570f8a8c42a9ac1570ad187326cedbd48e4'

@dataclass(frozen=True)
class EnvironmentRecipe:
    name: str
    python: str
    torch_index: str
    requirements: tuple[str, ...]
    kraken_wheel_sha256: str | None = None


def environment_recipes() -> dict[str, EnvironmentRecipe]:
    """Owner-bound environments; CLLG is isolated from Paddle/Transformers."""
    return {
        'ocr': EnvironmentRecipe('ocr', '3.11', 'https://download.pytorch.org/whl/cu126',
                                ('numpy', 'Pillow', 'pyarrow', 'pypdfium2', 'safetensors==0.7.0')),
        'cllg-gpu': EnvironmentRecipe('cllg-gpu', '3.11', 'https://download.pytorch.org/whl/cu126',
                                ('kraken==7.1.1', 'safetensors==0.7.0', 'lightning==2.6.1', 'Pillow==11.3.0'), KRAKEN_WHEEL_SHA256),
        'e2ws': EnvironmentRecipe('e2ws', '3.11', 'https://download.pytorch.org/whl/cpu',
                                ('transformers', 'safetensors==0.7.0', 'paddlepaddle==3.1.0', 'PyYAML', 'opencv-python-headless')),
        'kraken': EnvironmentRecipe('kraken', '3.11', 'https://download.pytorch.org/whl/cpu',
                                ('torch==2.9.0+cpu', 'torchvision==0.24.0+cpu', 'kraken==7.1.1',
                                 'safetensors==0.7.0', 'lightning==2.6.1', 'Pillow==11.3.0'), KRAKEN_WHEEL_SHA256),
    }


def environment_plan(name: str, venv: PathLike, *, wheelhouse: PathLike | None = None,
                     paddle_requirements: PathLike | None = None) -> list[list[str]]:
    """Return shell-free argv lists; Kraken needs a pre-staged, hash-checked wheel."""
    recipe = environment_recipes()[name]
    root = Path(venv).expanduser().absolute()
    python = str(root/'bin/python')
    commands = [[f'python{recipe.python}', '-c', 'import sys; assert sys.version_info[:2] == (3,11)'],
                [f'python{recipe.python}', '-m', 'venv', str(root)]]
    requirements = list(recipe.requirements)
    if recipe.kraken_wheel_sha256:
        if wheelhouse is None: raise ValueError('stage the pinned Kraken wheel and pass wheelhouse')
        wheel = Path(wheelhouse).expanduser().absolute()/'kraken-7.1.1-py3-none-any.whl'
        commands.append([python, '-c', 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()==sys.argv[2]', str(wheel), recipe.kraken_wheel_sha256])
        requirements[requirements.index('kraken==7.1.1')] = str(wheel)
    torch = [r for r in requirements if r.startswith(('torch==', 'torchvision=='))] or ['torch', 'torchvision']
    requirements = [r for r in requirements if not r.startswith(('torch==', 'torchvision=='))]
    commands += [[python, '-m', 'pip', 'install', '--index-url', recipe.torch_index, *torch],
                 [python, '-m', 'pip', 'install', *requirements]]
    if name == 'e2ws':
        if paddle_requirements is None: raise ValueError('pass the pinned PaddleOCR requirements.txt')
        commands.append([python, '-m', 'pip', 'install', '-r', str(Path(paddle_requirements).resolve())])
    commands.append([python, '-m', 'pip', 'check'])
    return commands


def write_environment_script(name: str, venv: PathLike, out: PathLike, *, wheelhouse: PathLike | None = None,
                             paddle_requirements: PathLike | None = None) -> Path:
    """Write a Linux-only setup script; caller reviews/executes it on the node."""
    commands = environment_plan(name, venv, wheelhouse=wheelhouse, paddle_requirements=paddle_requirements)
    path = Path(out)
    path.write_text('#!/usr/bin/env bash\nset -euo pipefail\n[[ "$(uname -s)" == Linux ]] || exit 2\n' +
                    '\n'.join(shlex.join(command) for command in commands) + '\n' +
                    shlex.join([str(Path(venv).expanduser().absolute()/'bin/python'), '-m', 'pip', 'freeze']) +
                    ' > ' + shlex.quote(str(Path(venv).expanduser().absolute()/'INSTALLED.txt')) + '\n')
    return path
