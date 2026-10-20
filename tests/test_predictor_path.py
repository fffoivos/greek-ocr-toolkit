"""Predictor configuration precedence, locked scratch builds and failure modes."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from greekocr.harvest import predictor_path as resolver


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    source = tmp_path / 'runtime'
    source.mkdir()
    (source / 'Cargo.lock').write_text('locked fixture\n')
    monkeypatch.setattr(resolver, '_RUNTIME', source)
    monkeypatch.delenv('GREEK_OCR_PREDICTOR', raising=False)
    monkeypatch.setenv('GREEK_OCR_BUILD_DIR', str(tmp_path / 'build'))
    return source, tmp_path / 'build'


def executable(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\nexit 0\n')
    path.chmod(0o755)
    return path


def test_override_scratch_and_legacy_precedence(runtime, monkeypatch):
    source, scratch = runtime
    legacy = executable(source / 'target/debug' / resolver._BINARY)
    assert resolver.predictor_binary() == legacy
    cached = executable(scratch / 'debug' / resolver._BINARY)
    assert resolver.predictor_binary() == cached
    explicit = executable(scratch / 'explicit')
    monkeypatch.setenv('GREEK_OCR_PREDICTOR', str(explicit))
    assert resolver.predictor_binary('release') == explicit
    monkeypatch.setenv('GREEK_OCR_PREDICTOR', str(scratch / 'missing'))
    with pytest.raises(RuntimeError, match='GREEK_OCR_PREDICTOR is not an executable'):
        resolver.predictor_binary()


def test_builds_both_profiles_offline_locked_with_receipt(runtime, monkeypatch):
    source, scratch = runtime
    monkeypatch.setattr(resolver.shutil, 'which', lambda name: '/toolchain/cargo')
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        if command[0] == 'rustc':
            return SimpleNamespace(stdout='rustc test-version\n')
        assert kwargs['cwd'] == source
        assert command[:4] == ['/toolchain/cargo', 'build', '--offline', '--locked']
        assert command[4:6] == ['--target-dir', str(scratch)]
        executable(scratch / ('release' if '--release' in command else 'debug') / resolver._BINARY)
        return SimpleNamespace()

    monkeypatch.setattr(resolver.subprocess, 'run', run)
    assert resolver.predictor_binary('release') == scratch / 'release' / resolver._BINARY
    assert len(calls) == 3
    receipt = json.loads((scratch / 'BUILD_RECEIPT.json').read_text())
    assert receipt['cargo_lock_sha256'] == hashlib.sha256((source / 'Cargo.lock').read_bytes()).hexdigest()
    assert receipt['rustc_version'] == 'rustc test-version'
    for profile in ('debug', 'release'):
        binary = scratch / profile / resolver._BINARY
        assert receipt['binaries'][profile] == dict(path=str(binary), sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    assert not (source / 'target').exists()
    assert resolver.predictor_binary() == scratch / 'debug' / resolver._BINARY
    assert len(calls) == 3


def test_missing_cargo_names_all_options(runtime, monkeypatch):
    monkeypatch.setattr(resolver.shutil, 'which', lambda name: None)
    with pytest.raises(RuntimeError) as error:
        resolver.predictor_binary()
    for option in ('cargo is unavailable', 'GREEK_OCR_PREDICTOR', 'GREEK_OCR_BUILD_DIR', 'in-repo target'):
        assert option in str(error.value)


def test_default_cache_is_keyed_by_lockfile(runtime, monkeypatch):
    source, _ = runtime
    monkeypatch.delenv('GREEK_OCR_BUILD_DIR')
    monkeypatch.setattr(Path, 'home', lambda: source.parent)
    monkeypatch.setattr(resolver.sys, 'platform', 'darwin')
    lock_sha = hashlib.sha256((source / 'Cargo.lock').read_bytes()).hexdigest()
    cached = executable(source.parent / 'Library/Caches/greek-ocr-toolkit/filter_runtime' /
                        lock_sha / 'debug' / resolver._BINARY)
    assert resolver.predictor_binary() == cached


def test_failed_offline_build_is_an_error(runtime, monkeypatch):
    monkeypatch.setattr(resolver.shutil, 'which', lambda name: '/toolchain/cargo')

    def fail(command, **kwargs):
        raise resolver.subprocess.CalledProcessError(101, command, stderr='offline dependency missing')

    monkeypatch.setattr(resolver.subprocess, 'run', fail)
    with pytest.raises(RuntimeError, match='Offline locked predictor build failed: offline dependency missing'):
        resolver.predictor_binary()
    assert not (runtime[1] / 'BUILD_RECEIPT.json').exists()


def test_invalid_profile(runtime):
    with pytest.raises(ValueError, match='profile'):
        resolver.predictor_binary('fast')
