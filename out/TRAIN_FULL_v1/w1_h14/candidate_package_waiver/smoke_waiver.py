"""Narrow h14 smoke inheritance. File reads only; never issues a review PASS.

The original CUDA measurement remains 7e8a. A separate focused PASS must
certify the new administrative gate bytes and bind this entire evidence file.
"""
from pathlib import Path
import hashlib
import json

PARENT = '7e8a497f21527b90bfd758fa8afceeabcc4b329aa31dc08535a2ce0472dde1e6'
REVIEWED = 'cd8078c4d02b89b237ddcf939f4512e124f64e710b5237cb2b6354c146498010'
BUILDER = '056edbcb0c10a7dccd6eec1b58cd85354328e60ba6679e9e07ae726e8f57cede'
RUNTIME = '21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4'
TRIAL = '393f00b4f4c2ab2d0ee62cd5af688ad5f8e26e1336f662a94201556d12a98920'
DECISION = 'c3b54d9d67bc8ddeeb26146cbc1e095b6d04752446fd66680dcb66acff7aff70'
SMOKE = '342d3cd5b1fa843152d4f99d530b67dc003fc6ac06dc1225fe0a43a69dd9019d'
SMOKE_PLAN = 'bccce2d5ac6e798970011739800514c52d04209229ad20a0e1b64d29ea94a261'
PACKET = 'f6445496df7b8a55611e6e160fc41dd125ed98347c28b90b5ef938e4efd94736'
GUARD = 'cb7d072c93978606649955c11c5f1eb10ac87675ae65bf86cbe885cdf967cddf'
ORIGINAL = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel'
BEFORE = """                or s.get('status')!='BIT_IDENTICAL' or s.get('mock') is not False
                or s.get('package_sha256')!=p['payload_sha256'] or s.get('runtime_sha256')!=p['runtime']['sha256']):"""
AFTER = """                or not smoke_admitted(ROOT,plan_path,p,r,s,smoke_report,mem_mib)):"""
IMPORT = '    from smoke_waiver import smoke_admitted\n'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()


def spec(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def bound(item):
    path = Path(item['path'])
    if spec(path) != item:
        raise ValueError('waiver evidence file binding changed: ' + str(path))
    return path


def patch_gate(text):
    if text.count(BEFORE) != 1:
        raise ValueError('reviewed smoke predicate changed')
    header = 'def submit(plan_path,review=None,smoke_report=None,*,command=subprocess.run,mem_mib=None):\n'
    if text.count(header) != 1:
        raise ValueError('reviewed submit header changed')
    return text.replace(BEFORE, AFTER).replace(header, header + IMPORT)


def manifest(root):
    root = Path(root).resolve()
    payload = read(root/'PAYLOAD.json')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if actual != set(payload['files']) | {'PAYLOAD.json'}:
        raise ValueError('missing/extra package files')
    for name, item in payload['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('foreign payload path')
        s = spec(root/name)
        if dict(bytes=s['bytes'], sha256=s['sha256']) != item:
            raise ValueError('payload mismatch: ' + name)
    return payload


def source_delta(parent, target):
    parent, target = Path(parent).resolve(), Path(target).resolve()
    if sha(parent/'PAYLOAD.json') != PARENT:
        raise ValueError('wrong waiver parent')
    old, new = manifest(parent), manifest(target)
    delta = sorted(n for n in set(old['files']) | set(new['files'])
                   if old['files'].get(n) != new['files'].get(n))
    if delta != ['adopted/w1-h14.json', 'smoke_waiver.py', 'stage_c.py']:
        raise ValueError('source delta exceeds h14 waiver permission')
    text = (target/'stage_c.py').read_text()
    if text.count(AFTER) != 1 or text.count(IMPORT) != 1:
        raise ValueError('waiver gate delta changed')
    restored = text.replace(AFTER, BEFORE).replace(IMPORT, '')
    if hashlib.sha256(restored.encode()).hexdigest() != BUILDER:
        raise ValueError('source differs from Astra-reviewed h14 builder')
    if sha(target/'adopted/w1-h14.json') != TRIAL:
        raise ValueError('wrong h14 trial')
    for key in set(old) | set(new):
        if key not in ('files', 'source_state', 'producing_commit') and old.get(key) != new.get(key):
            raise ValueError('unexpected payload metadata change')
    return dict(parent_sha256=PARENT, reviewed_candidate_sha256=REVIEWED,
                reviewed_builder_sha256=BUILDER,
                target_sha256=sha(target/'PAYLOAD.json'),
                changed={n: dict(before=old['files'].get(n), after=new['files'][n]) for n in delta},
                unchanged_original_members=len(old['files'])-1,
                scope='reviewed h14 builder + exact smoke admission call + sealed waiver verifier only')


def source_packet(root):
    root = Path(root).resolve()
    files = {str(p.relative_to(root)): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(root.rglob('*')) if p.is_file()}
    if digest(files) != PACKET:
        raise ValueError('original selection-smoke packet changed/missing')
    report, plan = root/'SMOKE_IDENTITY.json', root/'smoke_tree/PLAN.json'
    s, p = read(report), read(plan)
    if (sha(report) != SMOKE or sha(plan) != SMOKE_PLAN or s['status'] != 'BIT_IDENTICAL'
            or s['mock'] is not False or s['package_sha256'] != PARENT
            or s['runtime_sha256'] != RUNTIME or p['fixture'] is not False
            or p['payload_sha256'] != PARENT or p['runtime']['sha256'] != RUNTIME):
        raise ValueError('original real CUDA smoke binding changed')
    # Keep original absolute paths, including references unavailable in the copy.
    # This authenticates archived bytes; it does not claim new remote readbacks or
    # a new local comparison of absent checkpoint tensors.
    originals = {}
    for name, item in files.items():
        if name.startswith('smoke_tree/'):
            originals[ORIGINAL + '/smoke/' + name[len('smoke_tree/'):]] = item
        elif name in ('SMOKE_IDENTITY.json', 'SMOKE_SACCT_ALL.txt'):
            originals[ORIGINAL + '/' + name] = item
    references = {}
    def collect(value):
        if isinstance(value, dict):
            if {'path', 'bytes', 'sha256'} <= value.keys() and str(value['path']).startswith('/iopsstor/'):
                item = {k: value[k] for k in ('bytes', 'sha256')}
                if value['path'] in originals and originals[value['path']] != item:
                    raise ValueError('archived copy differs from remote original reference')
                references[value['path']] = dict(**item,
                    copy_verified=value['path'] in originals)
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    for name in files:
        if name.endswith('.json'):
            collect(read(root/name))
    return dict(root=str(root), packet_sha256=PACKET, files=files,
                report=spec(report), plan=spec(plan), remote_originals=originals,
                remote_references=references,
                custody='PRESERVED_ARCHIVE; original remote paths retained; no new remote readback',
                tensor_equality='INHERITED remote-validator result; missing tensors not re-compared locally')


def evidence(target, parent, plan_path, decision, packet):
    import stage_c
    target, plan_path = Path(target).resolve(), Path(plan_path).resolve()
    if stage_c.ROOT != target:
        raise ValueError('wrong loaded candidate')
    delta = source_delta(parent, target)
    p = stage_c.checked(plan_path)
    if (plan_path.parent.name != 'full' or plan_path.parent.parent.name != 'full-v1-014-w1-h14'
            or p['smoke'] is not False or len(p['runs']) != 1
            or p['runtime']['sha256'] != RUNTIME):
        raise ValueError('waiver applies only to fresh 014 one-lane h14 PLAN/runtime')
    e = p['runs'][0]
    cfg = read(bound(e['config']))
    expected_run = dict(name='w1-full', config=spec(plan_path.parent/'configs/w1-full.json'),
                        output=str(plan_path.parent/'runs/w1-full'), signal_smoke=False)
    expected_plan = dict(schema='TRAIN_FULL-stage-C-plan-v1', payload_sha256=sha(target/'PAYLOAD.json'),
        runtime=spec(bound(p['runtime'])), smoke=False, fixture=False, runs=[expected_run],
        resources='one non-exclusive 1-GPU job/run; 24 CPUs; 6 workers; no DDP',
        time_limit='23:00:00', warning_seconds=600)
    if (p != expected_plan or cfg['adopted'] != spec(target/'adopted/w1-h14.json')
            or cfg['total_updates'] != 49584 or cfg['target_drawn_lines'] != 12691632):
        raise ValueError('waiver target trial/configuration/PLAN changed')
    if (Path(decision).name != 'ASTRA_STAGE_C_H14_REVIEW.md' or sha(decision) != DECISION
            or 'SMOKE: WAIVED' not in Path(decision).read_text().splitlines()):
        raise ValueError('wrong Astra waiver decision')
    return dict(schema='TRAIN_FULL-h14-smoke-waiver-v1', status='WAIVED', measurement='INHERITED',
        mock=False, candidate_cuda_measured=False, incremental_smoke_GPU_h=0,
        parent_package=spec(Path(parent)/'PAYLOAD.json'), target_package=spec(target/'PAYLOAD.json'),
        runtime=p['runtime'], trial=cfg['adopted'], trial_name='w1-h14',
        plan=spec(plan_path), config=e['config'], source_delta=delta,
        decision=dict(report=spec(decision), smoke='SMOKE: WAIVED', overall_verdict='HOLD 0/1'),
        guard_sha256=GUARD, mem_mib=266240, source=source_packet(packet))


def rebind(s, evidence_sha):
    """Fields the real focused static rebind review must certify (no PASS here)."""
    return dict(target_package_sha256=s['target_package']['sha256'], plan_sha256=s['plan']['sha256'],
        config_sha256=s['config']['sha256'], evidence_sha256=evidence_sha,
        source_delta_sha256=digest(s['source_delta']), decision_sha256=DECISION,
        measurement='INHERITED', guard_sha256=GUARD, mem_mib=266240)


def smoke_admitted(target, plan_path, p, review, s, evidence_path, mem_mib):
    if s.get('status') != 'WAIVED':
        # Preserve the original measured-smoke route exactly.
        return (s.get('status') == 'BIT_IDENTICAL' and s.get('mock') is False
                and s.get('package_sha256') == p['payload_sha256']
                and s.get('runtime_sha256') == p['runtime']['sha256'])
    try:
        if mem_mib != 266240:
            raise ValueError('wrong waiver memory command')
        expected = evidence(target, bound(s['parent_package']).parent, plan_path,
                            bound(s['decision']['report']), s['source']['root'])
        if s != expected or review.get('waiver_rebind') != rebind(expected, sha(evidence_path)):
            raise ValueError('missing/unbound focused waiver rebind')
    except (KeyError, TypeError, OSError, ValueError) as exc:
        raise ValueError('h14 waiver refused: ' + str(exc)) from exc
    return True
