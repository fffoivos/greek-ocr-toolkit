"""Build off-tree and smoke-test package resources in an isolated installed wheel."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ('codec/v2.1.json', 'mix.schema.json', 'CONSOLIDATION.md', 'LEGACY_COMPARISON.diff')


def test_installed_wheel_has_train_resources_and_loads_codec(tmp_path):
    # A fresh source copy avoids setuptools build/egg-info writes in the checkout.
    source = tmp_path/'source'
    source.mkdir()
    shutil.copy2(ROOT/'pyproject.toml', source/'pyproject.toml')
    shutil.copytree(ROOT/'greekocr', source/'greekocr', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    wheels = tmp_path/'wheels'
    wheels.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    env.pop('PYTHONPATH', None)

    def run(args, **kwargs):
        result = subprocess.run(args, env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, **kwargs)
        assert result.returncode == 0, result.stdout
        return result.stdout

    run([sys.executable, '-c', 'from setuptools.build_meta import build_wheel; '
         f'build_wheel({str(wheels)!r})'], cwd=source)
    wheel, = wheels.glob('*.whl')
    resource_receipts = []
    with zipfile.ZipFile(wheel) as archive:
        for name in RESOURCES:
            relative = 'greekocr/train/'+name
            payload = archive.read(relative)
            assert payload == (ROOT/relative).read_bytes()
            resource_receipts.append(dict(path=relative, bytes=len(payload),
                                          sha256=hashlib.sha256(payload).hexdigest()))
    isolated = tmp_path/'venv'
    venv.EnvBuilder(with_pip=True).create(isolated)
    python = isolated/'bin/python'
    run([str(python), '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', str(wheel)], cwd=tmp_path)
    result = run([str(python), '-I', '-c', '''
import json, sys
from importlib.resources import files
from pathlib import Path
import greekocr.train
from greekocr.train.cer import load_codec
assert Path(greekocr.train.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
resources = files('greekocr.train')
for name in ('codec/v2.1.json', 'mix.schema.json', 'CONSOLIDATION.md', 'LEGACY_COMPARISON.diff'):
    assert resources.joinpath(name).is_file(), name
codec = load_codec(str(resources.joinpath('codec/v2.1.json')))
assert codec.version == 'v2.1' and codec.n_classes == 266
ids = list(range(1, codec.n_classes))
text = codec.decode(ids)
encode = {ch: i for i, ch in enumerate(codec.atom_by_id) if i}
assert [encode[ch] for ch in text] == ids
print(json.dumps({'import_from_installed_wheel': True, 'codec_version': codec.version,
                  'codec_classes': codec.n_classes, 'all_atoms_round_trip': True}))
'''], cwd=tmp_path)
    receipt = dict(schema='rel0-s2b-wheel-smoke-v1', wheel=wheel.name,
                   bytes=wheel.stat().st_size, sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
                   build='setuptools.build_meta.build_wheel; off-tree source copy; no network',
                   install='fresh venv; pip --no-index --no-deps; python -I outside checkout',
                   resources=resource_receipts, checks=json.loads(result),
                   cleanup='temporary build/wheel/venv removed with passing pytest basetemp')
    (tmp_path/'WHEEL.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
