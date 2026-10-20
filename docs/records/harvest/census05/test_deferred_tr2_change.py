"""Deferred config-only TR2 edit: dry assertion, no output/config write."""
from copy import deepcopy
import json
from pathlib import Path


def test_deferred_tr2_status_change():
    original = json.loads((Path(__file__).resolve().parent.parent/'seg_census/census04_config.json').read_text())
    candidate = original['corrections'][3]
    assert candidate['tool'] == 'polytonic'
    assert candidate['parent_id'] == 'collection-v2-train'
    assert candidate['sha256'] == '51dae7b4da738e26a46f434fa25a5ee7ea9e2be39be50b26e28e92ced6e1935c'
    assert candidate['status'] == 'candidate_pre_audit'
    after = deepcopy(original)
    after['corrections'][3]['status'] = 'released'
    restored = deepcopy(after)
    restored['corrections'][3]['status'] = 'candidate_pre_audit'
    assert restored == original
    assert after['corrections'][3]['status'] == 'released'


if __name__ == '__main__':
    test_deferred_tr2_status_change()
    print('DEFERRED_TR2_CONFIG_ASSERTION_PASS: no config written; no promotion applied')
