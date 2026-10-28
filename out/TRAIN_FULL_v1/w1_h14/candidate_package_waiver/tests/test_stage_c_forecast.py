from pathlib import Path
import sys
PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG))
from common import atomic
from forecast import forecast


def test_epoch_validation_renewals_and_retained_yield_inodes_are_counted(tmp_path):
    costs=[dict(width_mult=w,projected_train_hours=t,loss_seconds_mean=60.,
        cer_seconds_mean=100.,checkpoint_seconds=.1,loss_checkpoint_seconds_mean=.1,
        loss_checkpoint_bytes_max=1000,selection_seconds_mean=2.,full_state_bytes=10000,
        restart_startup_seconds_mean=100.,restart_startup_seconds_max=150.)
        for w,t in [(1.,12.),(1.5,13.),(2.,28.)]]
    smoke=tmp_path/'smoke.json';atomic(smoke,dict(costs=costs))
    r=forecast(PKG.parent/'evidence',tmp_path/'forecast.json',smoke)
    for row in r['costs']:
        assert row['selection_GPU_h']==16/3600
        for name,case in row['scenarios'].items():
            assert case['retained_yield_bytes_estimate']==case['retained_yield_inodes_assumed']*10000
            assert case['storage_bytes_estimate']>254000+case['retained_yield_bytes_estimate']
            if row['width_mult']==2:
                assert case['segment_renewals']>=1
                assert case['renewal_startup_GPU_h']>0
    assert r['budget']['owner_stage_C_authority_GPU_h']==82
