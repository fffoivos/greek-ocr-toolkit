"""SX1: stdin-only read-only login-node extraction, then local receipts.
Run from the repository root: python3 artifacts/sx1/extract.py
Remote stdout contains only selected truth lines; remote stderr carries hash metadata.
No remote files, authentication refreshes, scheduler calls, or git operations.
"""
import collections
import datetime
import gzip
import hashlib
import json
import pathlib
import re
import signal
import socket
import subprocess
import sys
import time

TRUTH_SHA = 'd2cdc75c5b0e529c4b7ddd20ea85f778e9da105c3f1cad4afb318d3c438ca34f'
SELECTION_SHA = 'ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec'
RECEIPT_SHA = 'c7cfcc852281c9ba6ebbe4c6d121455e8b094f48da84472989b0ac795fd991a3'
POLICY_SHA = '6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
BASE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017'
RUN = BASE + '/l1e_20261017/l1r_sf6_3680729'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def encode(x):
    return (json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()

def remote_main(payload):
    def timeout(*_):
        raise TimeoutError('180-second login-node budget')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(180)
    start = time.monotonic()
    assert re.fullmatch(r'clariden-ln\d+(?:\..*)?', socket.gethostname()), socket.gethostname()
    selection = pathlib.Path(BASE) / 'artifacts/labelfix_l1/binding/selection.jsonl'
    receipt_path = pathlib.Path(RUN) / 'receipt.json'
    selection_bytes = selection.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    assert sha(selection_bytes) == SELECTION_SHA
    assert sha(receipt_bytes) == RECEIPT_SHA
    receipt = json.loads(receipt_bytes)
    assert receipt['complete'] and receipt['policy']['schema'] == 'sf6-release-v1'
    assert receipt['policy'] == payload['expected_remote_policy']
    selected = {}
    for line in selection_bytes.splitlines():
        r = json.loads(line)
        assert r['id'] not in selected
        selected[r['id']] = r
    assert len(selected) == 124669
    targets = set(payload['line_ids']) & selected.keys()
    output = {}
    for lid in targets:
        r = selected[lid]
        output[lid] = dict(line_id=lid, google_text=r['label'], source=r['source'], wave=r['wave'],
                           truth_sets=payload['line_ids'][lid], modes={})
    rx = re.compile(r'"line_id"\s*:\s*"([^"\\]+)"')
    overlays = {}
    for mode in ('presence', 'full'):
        p = pathlib.Path(RUN) / 'release' / ('overlay_' + mode + '.jsonl.gz')
        seen = set()
        counts = collections.Counter()
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            for line in f:
                match = rx.search(line)
                assert match, 'missing line_id'
                lid = match[1]
                assert lid in selected and lid not in seen
                seen.add(lid)
                if lid not in targets:
                    continue
                r = json.loads(line)
                status = r['status']
                assert status in ('corrected', 'unchanged', 'hold'), (lid, status)
                assert r['original_label_sha256'] == sha(selected[lid]['label'].encode())
                reasons = r['hold_slots']
                if status == 'hold':
                    assert reasons and r.get('label') is None
                    label = None
                else:
                    assert not reasons and isinstance(r['label'], str)
                    label = r['label']
                    if status == 'unchanged':
                        assert label == selected[lid]['label']
                mapped = 'HOLD' if status == 'hold' else 'released-' + status
                output[lid]['modes'][mode.upper()] = dict(status=mapped, label=label, hold_reasons=reasons)
                counts[mapped] += 1
        assert seen == selected.keys()
        overlays[mode.upper()] = dict(path=str(p), compressed_bytes=p.stat().st_size,
                                      scanned_lines=len(seen), extract_status_counts=dict(counts))
    h = hashlib.sha256()
    for lid in sorted(output):
        assert len(output[lid]['modes']) == 2
        b = encode(output[lid])
        h.update(b)
        sys.stdout.buffer.write(b)
    sys.stdout.buffer.flush()
    meta = dict(hostname=socket.gethostname(), selection_path=str(selection), selection_sha256=SELECTION_SHA,
                selected_lines=len(selected), receipt_path=str(receipt_path), receipt_sha256=RECEIPT_SHA,
                production_policy=receipt['policy'], overlays=overlays,
                extract_sha256=h.hexdigest(), extract_lines=len(output),
                not_in_selection=sorted(set(payload['line_ids']) - selected.keys()),
                elapsed_seconds=time.monotonic()-start)
    print('SX1_METADATA ' + json.dumps(meta, ensure_ascii=False, sort_keys=True), file=sys.stderr)

def main():
    root = pathlib.Path('artifacts/sx1')
    source = pathlib.Path.home() / 'Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1.jsonl'
    data = source.read_bytes()
    assert sha(data) == TRUTH_SHA, 'STOP: truth SHA mismatch'
    target = root / 'truth_v1_input.jsonl'
    if target.exists():
        assert target.read_bytes() == data
    else:
        target.write_bytes(data)
    target.chmod(0o444)
    truth = [json.loads(line) for line in data.splitlines()]
    membership = collections.defaultdict(set)
    sets = collections.defaultdict(set)
    for r in truth:
        for provenance in r.get('provenance_all', [r['provenance']]):
            name = provenance['set']
            membership[r['line_id']].add(name)
            sets[name].add(r['line_id'])
    # SQ1's exact production binding; the local policy digest has distinct packaging.
    sq1 = json.loads(pathlib.Path('artifacts/sq1/census.json').read_text())
    assert sq1['selection_sha256'] == SELECTION_SHA and sq1['receipt_sha256'] == RECEIPT_SHA
    payload = dict(line_ids={k:sorted(v) for k,v in membership.items()}, expected_remote_policy=sq1['policy'])
    script = pathlib.Path(__file__).read_text()
    command = [ 'ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20',
                '-o', 'StrictHostKeyChecking=yes', '-o', 'UpdateHostKeys=no',
                '-o', 'ForwardAgent=no', 'clariden', 'python3 -B -' ]
    # JSON is passed as a Python string literal: no shell interpolation or remote files.
    program = script + '\nremote_main(json.loads(' + repr(json.dumps(payload)) + '))\n'
    proc = subprocess.run(command, input=program.encode(), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=240)
    (root/'remote.stderr').write_bytes(proc.stderr)
    if proc.returncode:
        raise SystemExit('STOP: remote failed; no retry or auth refresh. See artifacts/sx1/remote.stderr')
    metadata_lines = [x[len('SX1_METADATA '):] for x in proc.stderr.decode().splitlines() if x.startswith('SX1_METADATA ')]
    assert len(metadata_lines) == 1
    remote = json.loads(metadata_lines[0])
    assert sha(proc.stdout) == remote['extract_sha256'], 'transfer SHA mismatch'
    extract = root/'sf6_release_extract_lqb.jsonl'
    extract.write_bytes(proc.stdout)
    assert sha(extract.read_bytes()) == remote['extract_sha256']
    rows = [json.loads(x) for x in proc.stdout.splitlines()]
    indexed = {r['line_id']:r for r in rows}
    assert len(indexed) == len(rows) == remote['extract_lines']
    missing = set(remote['not_in_selection'])
    assert set(indexed).isdisjoint(missing) and set(indexed)|missing == set(membership)
    not_covered = b''.join(encode(dict(line_id=lid, truth_sets=sorted(membership[lid]))) for lid in sorted(missing))
    (root/'not_in_selection.jsonl').write_bytes(not_covered)
    def coverage(ids):
        present = ids & indexed.keys()
        counts = dict(truth_line_ids=len(ids), in_selection=len(present), not_covered=len(ids-present), modes={})
        for mode in ('PRESENCE','FULL'):
            statuses = collections.Counter(indexed[lid]['modes'][mode]['status'] for lid in present)
            held = statuses['HOLD']
            counts['modes'][mode] = dict(released=len(present)-held, held=held,
                released_corrected=statuses['released-corrected'], released_unchanged=statuses['released-unchanged'])
        counts['held_either_mode'] = sum(any(indexed[lid]['modes'][m]['status']=='HOLD' for m in ('PRESENCE','FULL')) for lid in present)
        counts['held_both_modes'] = sum(all(indexed[lid]['modes'][m]['status']=='HOLD' for m in ('PRESENCE','FULL')) for lid in present)
        return counts
    result = dict(schema='sx1-release-extract-v1', created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        truth_input=dict(source_path=str(source), local_path=str(target), sha256=TRUTH_SHA, rows=len(truth), unique_line_ids=len(membership), read_only=True),
        script=dict(path=str(pathlib.Path(__file__)), sha256=sha(script.encode())),
        policy_digest=POLICY_SHA,
        policy_digest_note='Frozen local 16-path policy digest supplied by requester/SQ1; production merged L1R3 packaging uses production_policy.sha256. These are distinct bindings.',
        remote=remote, extract=dict(path=str(extract), sha256=sha(proc.stdout), bytes=len(proc.stdout), transfer_sha_verified=True),
        not_in_selection=dict(path=str(root/'not_in_selection.jsonl'), sha256=sha(not_covered), lines=len(missing)),
        membership_definition='Unique line_id per provenance_all[].set (fallback provenance.set); memberships may overlap.',
        counts=coverage(set(membership)), counts_by_truth_set={k:coverage(v) for k,v in sorted(sets.items())},
        cq1_capitals_subset=coverage({r['line_id'] for r in truth if r['class']=='capitals'}),
        execution=dict(network='Clariden SSH only', remote_files_written=False, git_operations=False, submission=False, auth_refresh=False))
    (root/'RECEIPT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=result['counts'], counts_by_truth_set=result['counts_by_truth_set'], cq1=result['cq1_capitals_subset'], extract_sha256=remote['extract_sha256']),ensure_ascii=False,indent=2))

if __name__ == '__main__' and not ('--remote' in sys.argv):
    # stdin execution must not invoke the local coordinator.
    if sys.argv[0] != '-':
        main()
