"""Offline expected remote bindings; no remote files, scheduler or data copies.

Reconstruct every old trial and require its deployed SHA before changing only
the payload binding and destination paths. The coordinator runs the unchanged
production planner remotely and compares its output to these expected hashes.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys

EVIDENCE = Path(__file__).resolve().parent
PACKAGE = EVIDENCE.parent / 'package'
REPO = EVIDENCE.parents[3]
sys.path.insert(0, str(PACKAGE))
from common import atomic, read, sha, spec
import stage_b
from verify import verify, data_compatibility


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + '\n').encode()


def remote_spec(path, data):
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def main():
    verify()
    data_compatibility()
    payload = sha(PACKAGE / 'PAYLOAD.json')
    parent = sha(EVIDENCE / 'STAGE_B_H1_PARENT_PAYLOAD.json')
    receipts = REPO / 'out/TRAIN_FULL_v1/receipts_stage_b'
    runtime = REPO / 'out/TRAIN_FULL_v1/receipts_005/data_prepared_runtime.json'
    work = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-009-stage-b-h1')
    remote_package = work.parents[1] / 'pkg' / payload[:16]
    destination = EVIDENCE / 'STAGE_B_H1_BINDINGS'
    summary = dict(payload_sha256=payload, parent_payload_sha256=parent,
                   work=str(work), package=str(remote_package), plans={},
                   status='OFFLINE_EXPECTED_REMOTE_BINDINGS; verify actual remote planner output before submission',
                   scientific_changes=[], remote_actions=[])
    for mode in ('smoke', 'study'):
        old = read(receipts / (mode + '_PLAN.json'))
        assert old['payload_sha256'] == parent and old['fixture'] is False
        assert (sha(runtime), runtime.stat().st_size) == (old['runtime']['sha256'], old['runtime']['bytes'])
        new = copy.deepcopy(old)
        new['payload_sha256'] = payload
        for name, filename in [('points', 'lr_trials.jsonl'), ('space', 'lr_space.json')]:
            s = spec(PACKAGE / 'study' / filename)
            assert (s['sha256'], s['bytes']) == (old[name]['sha256'], old[name]['bytes'])
            new[name] = dict(s, path=str(remote_package / 'study' / filename))
        expected = []
        if mode == 'smoke':
            for name, width in [('control', 1.), ('requeue', 1.), ('w1.5', 1.5), ('w2', 2.)]:
                trial = stage_b.make_trial(runtime, width, dict(stage_b.points()[-1], trial_id=name), smoke=True)
                if name == 'requeue':
                    trial['force_requeue_step'] = 12
                expected.append((name, trial))
        else:
            for width in stage_b.ADOPTED:
                for point in stage_b.points():
                    expected.append(('w%g-%s' % (width, point['trial_id']),
                                     stage_b.make_trial(runtime, width, point)))
        original_entries = [t for group in old['groups'] for t in group]
        assert len(expected) == len(original_entries)
        entries = []
        for (name, trial), original in zip(expected, original_entries):
            # Prove all original HPs, cadence, runtime, seeds and policies match.
            trial['runtime'] = old['runtime']
            old_trial = dict(trial, payload_sha256=parent)
            assert remote_spec(original['config']['path'], encoded(old_trial)) == original['config'], name
            trial['payload_sha256'] = payload
            path = destination / mode / 'trials' / (name + '.json')
            atomic(path, trial)
            entries.append(dict(config=remote_spec(work / mode / 'trials' / path.name, encoded(trial)),
                                output=str(work / mode / 'runs' / name)))
        new['groups'] = [entries[i:i+4] for i in range(0, len(entries), 4)]
        path = destination / mode / 'PLAN.json'
        atomic(path, new)
        summary['plans'][mode] = dict(expected_remote=remote_spec(work / mode / 'PLAN.json', encoded(new)),
                                     local=spec(path), trials=len(entries), groups=len(new['groups']),
                                     all_parent_trial_hashes_reproduced=True)
    atomic(destination / 'BINDINGS.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
