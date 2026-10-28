"""Unavailable research adapters fail before custody I/O or optional imports."""
import json

import pytest

from greekocr.train import mix

MODES = ('codec_recovery', 'label_versions', 'matched_replay', 's1_selection')
SEALED = 'docs/programme_20261025/TRAIN_FULL_v1/stage_c_package'


def assert_historical_error(action, mode):
    with pytest.raises(mix.MixError) as caught:
        action()
    assert str(caught.value) == (
        f'{mode} ({mix.HISTORICAL_MODES[mode]}): historical mode not included '
        f'in this release; see sealed package {SEALED}'
    )


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('entrypoint', ('validate_metadata', 'validate', 'load_rows'))
def test_historical_modes_fail_before_data_or_recipe_access(tmp_path, monkeypatch, mode, entrypoint):
    def no_custody(*args, **kwargs):
        pytest.fail('historical mode attempted recipe custody')
    monkeypatch.setattr(mix, 'committed_recipes', no_custody)
    spec = {mode: {'path': 'absent historical input'}}
    path = tmp_path/'mix.json'
    path.write_text(json.dumps(spec))
    action = (lambda: mix.load_rows(spec, 'train')) if entrypoint == 'load_rows' else (
        lambda: getattr(mix, entrypoint)(path))
    assert_historical_error(action, mode)


@pytest.mark.parametrize('keyword,mode', [('recovery', 'codec_recovery'), ('replay', 'matched_replay')])
def test_direct_assembly_rejects_historical_modes(keyword, mode):
    assert_historical_error(lambda: mix.assemble([], [], 0, **{keyword: {}}), mode)


def test_direct_replay_plan_rejects_historical_mode():
    assert_historical_error(lambda: mix.replay_plan({}), 'matched_replay')


@pytest.mark.parametrize('mode', MODES)
def test_historical_cli_reports_release_scope(tmp_path, capsys, mode):
    path = tmp_path/'mix.json'
    path.write_text(json.dumps({mode: {}}))
    assert mix.main(['validate', str(path)]) == 3
    captured = capsys.readouterr()
    assert 'historical mode not included in this release' in captured.err
    assert f'see sealed package {SEALED}' in captured.err
    assert not captured.out
