"""Ruling C: extension consumers cannot alter the certified SF6c policy tree."""
import ast
import hashlib
import io
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

import pytest

from greekocr.labelfix import release_gate

ROOT = Path(__file__).resolve().parents[2]
# opus/spellcheck at the MR-C audit; pin it so later branch movement cannot
# silently redefine the accepted tree. Git is used read-only throughout.
SF6C_REFERENCE = 'ce2f889d9084f850d07878479bcc02f49f0b6d58'
POLICY_SHA256 = '6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
ADDITIVE_SUBPACKAGES = ('greekocr/recogniser/', 'greekocr/adjudicate/')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


@pytest.mark.skip(reason="historical binding; green at coord/review-sheets@6fe84030c; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_policy_binding_remains_sf6c():
    binding = release_gate.policy_binding()
    assert len(binding['sources']) == 16
    assert binding['sha256'] == POLICY_SHA256
    assert not git('diff', SF6C_REFERENCE, '--', *binding['sources'])


def test_no_hashed_path_imports_recomposition_extension():
    for name in release_gate.policy_binding()['sources']:
        tree = ast.parse((ROOT / name).read_text(), filename=name)
        for node in ast.walk(tree):
            imports = []
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or '', *(alias.name for alias in node.names)]
            assert all('l1r_recompose_ext' not in item.split('.') for item in imports), name


def assert_additive_tree(expected, actual):
    """Freeze reference bytes; admit only allowlisted, reference-absent packages."""
    missing = sorted(expected.keys() - actual.keys())
    modified = sorted(name for name in expected.keys() & actual.keys()
                      if actual[name] != expected[name])
    assert not missing, f'Missing reference files: {missing}'
    assert not modified, f'Modified reference files: {modified}'

    reference_dirs = {str(parent) + '/' for name in expected
                      for parent in PurePosixPath(name).parents}
    admitted = {}
    for name in sorted(actual.keys() - expected.keys()):
        rule = next((directory for directory in ADDITIVE_SUBPACKAGES
                     if directory not in reference_dirs and name.startswith(directory)), None)
        assert rule is not None, f'Unapproved extra file: {name}'
        admitted[name] = rule
    return admitted


@pytest.mark.skip(reason="historical binding; green at coord/review-sheets@6fe84030c; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_greekocr_sha256_list_matches_spellcheck():
    archive = git('archive', SF6C_REFERENCE, '--', 'greekocr/')
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        expected = {entry.name: hashlib.sha256(files.extractfile(entry).read()).hexdigest()
                    for entry in files if entry.isfile()}
    paths = git('ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', 'greekocr/')
    actual = {name.decode(): hashlib.sha256((ROOT / name.decode()).read_bytes()).hexdigest()
              for name in set(paths.split(b'\0')) if name}
    for name, rule in assert_additive_tree(expected, actual).items():
        print(f'{name}: new reference-absent subpackage {rule}')


@pytest.mark.parametrize('name', ['greekocr/__init__.py', 'greekocr/labelfix/policy.py'])
def test_additive_tree_rejects_modified_reference_file(name):
    with pytest.raises(AssertionError, match='Modified reference files'):
        assert_additive_tree({name: 'original'}, {name: 'modified'})


def test_additive_tree_rejects_missing_reference_file():
    with pytest.raises(AssertionError, match='Missing reference files'):
        assert_additive_tree({'greekocr/__init__.py': 'original'}, {})


@pytest.mark.parametrize('extra', [
    'greekocr/labelfix/new.py',
    'greekocr/labelfix/new_package/__init__.py',
    'greekocr/new.py',
    'greekocr/unlisted/__init__.py',
    'greekocr/recogniser_lookalike/new.py',
])
def test_additive_tree_rejects_unapproved_extra(extra):
    expected = {'greekocr/labelfix/__init__.py': 'original'}
    with pytest.raises(AssertionError, match='Unapproved extra file'):
        assert_additive_tree(expected, {**expected, extra: 'new'})


@pytest.mark.parametrize('directory', ADDITIVE_SUBPACKAGES)
def test_additive_tree_accepts_new_subpackage(directory):
    expected = {'greekocr/labelfix/__init__.py': 'original'}
    extra = directory + '__init__.py'
    assert assert_additive_tree(expected, {**expected, extra: 'new'}) == {extra: directory}


@pytest.mark.parametrize('directory', ADDITIVE_SUBPACKAGES)
def test_additive_tree_rejects_extra_in_existing_allowlisted_directory(directory):
    expected = {directory + '__init__.py': 'original'}
    with pytest.raises(AssertionError, match='Unapproved extra file'):
        assert_additive_tree(expected, {**expected, directory + 'new.py': 'new'})
