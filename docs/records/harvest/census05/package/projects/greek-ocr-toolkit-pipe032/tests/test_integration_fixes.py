"""census_03 input wiring regressions; tiny mock census fixtures, no readers."""
import json
import sqlite3

import pytest

from greekocr.harvest.line_pipeline import automatic_result
from greekocr.harvest.line_pipeline_census import run
from test_line_pipeline import row, expected, census_config, segment


@pytest.mark.parametrize('text,candidate', [
    ('1.234', True), ('12 - 3', True), ('4·5', True),
    ('Α.Β. 12', False), ('12.', False), ('-5', False),
])
def test_numeric_adjacency(text, candidate):
    result = automatic_result(row(text), 'numerics', expected(), 'fixture', 'fixture')
    if candidate:
        assert result is None  # no automatic verified_no_change for a candidate
    else:
        assert result['status'] == 'verified_no_change'
        assert result['evidence']['candidate_scan'] == 'no adjacent numeric separator candidate'


@pytest.mark.parametrize('observed', [False, True])
def test_configured_crop_protection_matches_observed_heldout(tmp_path, observed):
    protected = row('1234')
    protected.update(primary_class='numerics_tables', script_class='nonletter')
    unaffected = dict(protected, id='unaffected', crop_sha256='b' * 64)
    rows = [protected, unaffected]
    if observed:
        rows.append(dict(protected, id='heldout', split='test', edition_id='different-edition'))
    config = census_config(tmp_path, rows)
    if not observed:
        config['final_policy']['heldout_crop_sha256'] = [protected['crop_sha256']]
    out = tmp_path / 'mock-census'
    run(config, out, execute=True, segmenter_factory=lambda: segment)
    with sqlite3.connect(out / 'ledger.sqlite') as db:
        if not observed:
            assert db.execute("SELECT count(*) FROM observations WHERE split IN ('dev','test')").fetchone()[0] == 0
        decisions = {rid: json.loads(payload) for rid, payload in db.execute('SELECT id,payload FROM decisions')}
    assert decisions['r1']['pre_dedup_disposition'] == 'ADMIT'
    assert decisions['r1']['disposition'] == 'DROP'
    assert decisions['r1']['reasons'] == [dict(reason='heldout_crop_identity')]
    assert decisions['unaffected']['disposition'] == 'ADMIT'
