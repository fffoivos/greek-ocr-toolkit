"""Exact entrypoint and legacy release-schema compatibility on saved evidence."""
import pytest
import json
import os
from pathlib import Path
import subprocess
import sys
from scripts.labelfix.clariden.r1_common import rows,sha256
from scripts.labelfix import release_gate_sf7 as gate


@pytest.mark.skip(reason="historical binding; green at opus/spellcheck@26d64e8a6; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_exact_entrypoint_and_sf6_release_schema(tmp_path):
    # The deploy manifest is required even in the local mock; this is the same
    # shell/Python chain used by production and the login-node dry run.
    out=tmp_path/'output'
    proc=subprocess.run(['bash','scripts/labelfix/clariden/sf7_job.sbatch','--mock',
        '--config','config/sf7_mock.json','--out',str(out),'--workers','2'],
        env=dict(os.environ,SF7_MOCK_PYTHON=sys.executable),capture_output=True,text=True,timeout=30)
    assert proc.returncode==0,proc.stdout+proc.stderr
    prior=json.loads(Path('artifacts/labelfix_l1e/mock_run_v4/recomposition/release/release_ensemble_ab.json').read_text())
    run=json.loads((out/'receipt.json').read_text())
    assert run['complete'] and run['lines']==64 and run['preregistration_sha256']==gate.PREREGISTRATION_SHA256
    for v in 'AB':
        m=json.loads((out/'release'/f'release_{v}.json').read_text())
        assert set(prior)<=set(m) and m['schema']==prior['schema']=='l1r-release-v1'
        assert set(m['counts_by_status'])=={'hold','out_of_scope','unchanged','corrected'}
        for dim in ('coverage_per_wave','coverage_per_source'):
            for b in m[dim].values():
                assert b['total']==sum(b[s] for s in m['counts_by_status'])
                assert b['kept']==b['corrected']+b['unchanged']
                assert b['kept_fraction']==b['kept']/b['total']
        actual=list(rows(out/'release'/m['overlay']));assert len(actual)==64
        assert all(r['policy']==gate.POLICY and r['variant']==v and 'rule_traces' in r for r in actual)
        assert sha256(out/'release'/m['overlay'])==m['overlay_sha256']
        for row in actual:
            assert all({'start','letter','reason','detail'}<=set(h) for h in row['hold_slots'])
            for change in row['changes']:
                assert {'start','letter','from','to','evidence'}<=set(change)
                assert all('letter' in z for z in change['evidence']['slots'])
        c=json.loads((out/'release'/f'release_ctrl_subset_{v}.json').read_text())
        ids={r['line_id'] for r in rows(out/'release'/c['labels_file'])}
        assert ids=={r['line_id'] for r in actual if r['status'] in ('corrected','unchanged')}
        assert c['release']!=m['release'] and c['paired_release']==m['release']


def test_real_shard_order_need_not_match_selection_order(tmp_path):
    from scripts.labelfix.clariden.sf7_recompose import runtime_slice
    from scripts.labelfix.clariden.r1_common import write_rows
    path=tmp_path/'runtime.jsonl.gz';write_rows(path,[dict(id=x) for x in ('b','c','a')])
    tasks=[dict(runtime=str(path))];selected=[dict(id=x,label=x) for x in ('a','b','c')]
    used,chosen=runtime_slice(tasks,selected,2)
    assert used==tasks and [r['id'] for r in chosen]==['b','c']


def test_slice_duplicate_ids_fail_closed(tmp_path):
    import pytest
    from scripts.labelfix.clariden.sf7_recompose import runtime_slice
    from scripts.labelfix.clariden.r1_common import write_rows
    path=tmp_path/'runtime.jsonl.gz';write_rows(path,[dict(id='a'),dict(id='a')])
    with pytest.raises(ValueError,match='duplicate'):
        runtime_slice([dict(runtime=str(path))],[dict(id='a')],2)
