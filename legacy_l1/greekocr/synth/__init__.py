"""Recipe identity, Rust factory invocation and manifest-only mix custody."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Sequence
from greekocr.types import PathLike, Record
from greekocr._vendor.train import mix as _mix

__all__ = ["Recipe", "recipe_registry", "verify_recipe_sha", "build_shards", "build_mix", "validate_mix", "assemble_mix"]
_ASSETS = Path(__file__).resolve().parents[1] / '_vendor'

@dataclass(frozen=True)
class Recipe:
    name: str
    path: Path
    sha256: str
    origin_commit: str | None


def recipe_registry() -> dict[str, Recipe]:
    """Return v5/v7/v8 pinned to the captured source bytes (not a mutable rehash)."""
    origins = json.loads((_ASSETS / 'origins.json').read_text())
    registry = {}
    for name in ('v5', 'v7', 'v8'):
        relative = f'factory/recipe.{name}.json'
        origin = next(e for e in origins if e['path'] == 'greekocr/_vendor/' + relative)
        registry[name] = Recipe(name, _ASSETS / relative, origin['source_sha256'], origin['commit'])
    return registry


def verify_recipe_sha(recipe: Recipe | PathLike, expected: str | None = None) -> str:
    """Assert recipe byte identity; unknown paths require an explicit expected digest."""
    if isinstance(recipe, Recipe):
        path, digest = recipe.path, expected or recipe.sha256
    elif str(recipe) in recipe_registry():
        entry = recipe_registry()[str(recipe)]
        path, digest = entry.path, expected or entry.sha256
    else:
        path, digest = Path(recipe), expected
    if digest is None:
        raise _mix.MixError('unregistered recipe requires expected SHA-256')
    actual = _mix.sha256(path)
    if actual != digest:
        raise _mix.MixError('recipe SHA-256 mismatch')
    return actual


def build_shards(recipe: Recipe | str, binary: PathLike, out: PathLike, *, pool: PathLike,
                 workdir: PathLike | None = None, timeout: float = 3600) -> Record:
    """Run an existing linefactory; require its audit, recipe and exact shard receipt."""
    entry = recipe_registry()[recipe] if isinstance(recipe, str) else recipe
    digest = verify_recipe_sha(entry)
    directory = Path(out).resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('use a fresh output directory')
    command = [str(Path(binary).expanduser().absolute()), 'build', '--recipe', str(entry.path),
               '--pool', str(Path(pool).resolve()), '--out', str(directory)]
    subprocess.run(command, cwd=workdir, check=True, timeout=timeout)
    receipt = json.loads((directory/'build_info.json').read_text())
    if receipt.get('recipe_sha256') != digest or receipt.get('audit_ok') is not True:
        raise _mix.MixError('factory recipe/audit receipt mismatch')
    actual = _mix.shard_inventory(directory)
    if not actual or receipt.get('shard_sha256') != actual:
        raise _mix.MixError('factory shard hash or inventory mismatch')
    return receipt


def build_mix(components: Sequence[Record], out: PathLike, *, repo: PathLike, seed: int = 0,
              codec_version: str = 'v1', created_by: str = 'greekocr.synth', notes: str = '',
              role: str = 'train') -> Record:
    """Bind factory receipts using the unchanged HEAD-blob custody validator."""
    return _mix.build(list(components), Path(out), seed=seed, codec_version=codec_version,
                      created_by=created_by, notes=notes, repo=Path(repo), role=role)


def validate_mix(path: PathLike, *, repo: PathLike, role: str = 'train') -> Record:
    """Fail closed on recipes, role, receipt fields and exact shard membership."""
    return _mix.validate(Path(path), repo=Path(repo), role=role)


def assemble_mix(groups: Sequence[Sequence[Record]], fractions: Sequence[float], seed: int,
                 *, epoch: int = 0, max_rows: int | None = None) -> tuple[list[Record], list[int]]:
    """Unchanged largest-remainder quotas and seed:epoch:component cycling."""
    return _mix.assemble(groups, fractions, seed, epoch, max_rows)
