"""Read-only verification of the CU3 pre-edit snapshot; never refresh the baseline."""
import hashlib
import json
from pathlib import Path
from greekocr.labelfix.release_gate import policy_binding
from greekocr.recogniser.api import sha256


def main():
    root = Path(__file__).resolve().parents[2]
    directory = root/'artifacts/cleanup_step3'
    before = json.loads((directory/'pins_before.json').read_text())
    after = dict(before, policy=policy_binding(), paths={
        path: dict(item, sha256=sha256(root/path)) for path, item in before['paths'].items()})
    assert after['policy'] == before['policy'], 'policy binding changed'
    assert after['paths'] == before['paths'], 'protected bytes changed'
    assert all(not (root/p).is_file() for p in before['missing_receipt_paths']), 'absent pinned path created'
    (directory/'pins_after.json').write_text(json.dumps(after, indent=2)+'\n')
    for name, snapshot in [('before', before), ('after', after)]:
        (directory/f'pinned_{name}.sha256').write_text(''.join(
            f'{v["sha256"]}  {p}\n' for p,v in snapshot['paths'].items()))
        (directory/f'policy_{name}.json').write_text(json.dumps(snapshot['policy'],indent=2)+'\n')
    print(f'pinned bytes unchanged {len(after["paths"])}/{len(before["paths"])}; policy identical yes')
    print('absent receipt paths unchanged:', len(before['missing_receipt_paths']))


if __name__ == '__main__':
    main()
