"""Amendment-only scoring invocation; synthetic drift, no reader calls."""
import sys
from pathlib import Path
from tests._paths import ADMISSION
import pytest

CP7 = ADMISSION / 'seg/cp7'
sys.path.insert(0, str(CP7))
import score_cp7d as d


@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_original_bindings_verified():
    assert d.verify()['files']


@pytest.mark.parametrize('target', ['freeze', 'amendment', 'runtime', 'screen', 'scorer'])
def test_drift_rejected(monkeypatch, target):
    import r2_common
    actual_sha = d.scorer.sha
    paths = {
        'freeze': d.scorer.FREEZE,
        'amendment': d.runtime_r2.AMENDMENT,
        'runtime': Path(d.runtime_r2.__file__),
        'screen': d.scorer.ROOT / 'greekocr/harvest/admission.py',
        'scorer': Path(d.scorer.__file__),
    }
    def altered(path):
        return '0' * 64 if Path(path).resolve() == paths[target].resolve() else actual_sha(path)
    monkeypatch.setattr(d.scorer, 'sha', altered)
    monkeypatch.setattr(d.runtime_r2, 'sha', altered)
    monkeypatch.setattr(r2_common, 'sha', altered)
    with pytest.raises(AssertionError):
        d.verify()
    assert r2_common.sha is altered


def test_original_scorer_main_and_restore(monkeypatch):
    original = d.scorer.verify
    called = []
    def main():
        assert d.scorer.verify is d.verify
        called.append(True)
    monkeypatch.setattr(d.scorer, 'main', main)
    d.main()
    assert called == [True] and d.scorer.verify is original
