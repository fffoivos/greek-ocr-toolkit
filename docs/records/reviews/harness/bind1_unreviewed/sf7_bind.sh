#!/usr/bin/env bash
# Offline BIND1 handoff. Preparation only; coordinator invokes --execute after audit.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 PYTHONOPTIMIZE=
ROOT=$(cd "$(dirname "$0")/../../.." && pwd -P)
MODE=--dry-run
if [[ ${1:-} == --dry-run || ${1:-} == --execute ]]; then MODE=$1; shift; fi
if [[ $# -lt 1 || $# -gt 2 || ${1:-} == --* ]]; then
  echo 'usage: sf7_bind.sh [--dry-run|--execute] FINAL_SCORE.json [TR2_OUTPUT_DIR]' >&2
  exit 2
fi
# No git operations, network clients, hooks or remote commands.
exec python3 -B - "$ROOT" "$MODE" "$1" "${2:-artifacts/sf7_rc1_test}" <<'PY'
import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(sys.argv[1]).resolve()
EXECUTE = sys.argv[2] == '--execute'
REGISTRY = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c/labels/VERSIONS.json')
LQB = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/versions.json')
DOC = 'docs/labelfix/spellcheck/'
TRAIN_ID = 'sf7_rc1_edits_A'
TEST_ID = 'sf7_rc1_test_edits_A'
TRAIN_SHA = '1e3ac3344d0054d8e7639325afdf13826181e6eec10983b7e162b9648c5faf5a'
POLICY = 'f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047'
PREREG = '64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'

def local(name):
    p = Path(name)
    if not p.is_absolute(): p = ROOT / p
    # Reject symlinks, including internal aliases, and hardlinked write targets.
    if not p.is_relative_to(ROOT): raise ValueError(f'outside worktree: {p}')
    for q in (p, *p.parents):
        if q == ROOT: break
        if q.is_symlink(): raise ValueError(f'symlink refused: {q}')
    if not p.resolve().is_relative_to(ROOT) or '.git' in p.relative_to(ROOT).parts:
        raise ValueError(f'protected path: {p}')
    if p.is_file() and p.stat().st_nlink != 1: raise ValueError(f'hardlink refused: {p}')
    return p

def digest(data): return hashlib.sha256(data).hexdigest()
def sha(p): return digest(p.read_bytes())
def load(p): return json.loads(p.read_text())
def encoded(obj): return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()
def require(ok, message):
    if not ok: raise ValueError(message)

def main():
    verdict_path = local(sys.argv[3])
    raw = verdict_path.read_bytes()
    verdict = json.loads(raw)
    s = verdict['summary']
    for key in ('frame_lines', 'correct', 'incorrect', 'pending', 'scored'):
        require(type(s[key]) is int and s[key] >= 0, f'invalid summary {key}')
    lines = verdict['lines']
    tally = collections.Counter(x['status'] for x in lines)
    require(len(lines) == 100 and len({x['line_id'] for x in lines}) == 100,
            'audit must contain 100 unique lines')
    require(set(tally) <= {'CORRECT', 'INCORRECT', 'PENDING'}, 'invalid line status')
    require(s['frame_lines'] == 100 and all(s[k] == tally[v] for k,v in
            [('correct','CORRECT'),('incorrect','INCORRECT'),('pending','PENDING')]), 'summary/lines mismatch')
    require(s['scored'] == s['correct'] + s['incorrect'], 'scored count mismatch')
    if s['pending'] or any(x.get('status') == 'PENDING' for x in verdict.get('heads', [])):
        raise ValueError('PENDING audit: binding refused')
    require(s['final_line_precision'] == s['correct']/100, 'precision mismatch')
    reasons = verdict.get('reasons', s.get('reasons', []))
    if isinstance(reasons, str): reasons = [reasons]
    require(isinstance(reasons, list) and all(isinstance(x,str) for x in reasons), 'invalid reasons')
    reasons = list(reasons)
    if s['correct'] < 83: reasons.append(f"line precision {s['correct']}/100 below 83/100")
    if s.get('controls_gate_passed') is False: reasons.append('reader controls failed')
    if s.get('full_preregistration_pass') is False: reasons.append('full preregistration failed (including line-class constraint)')
    explicit = verdict.get('verdict')
    require(explicit in (None, 'PASS', 'FAIL', 'PENDING'), 'unknown verdict')
    require(explicit != 'PENDING', 'PENDING verdict: binding refused')
    if explicit == 'FAIL': require(reasons, 'FAIL must include reasons')
    failed = bool(reasons) or explicit == 'FAIL'
    if explicit == 'PASS': require(not failed, 'PASS contradicts audit evidence')
    if not failed:
        require(s.get('controls_gate_passed') is True and s.get('line_precision_bar_pass') is True,
                'PENDING reader controls or precision gate')
        require(s.get('full_preregistration_pass') is True,
                'PENDING full_preregistration_pass: resolve separate sf6 line-class comparison first')
        require(s.get('cluster_bootstrap') is not None, 'missing preregistered bootstrap interval')
    result = 'FAIL' if failed else 'PASS'
    timestamp = subprocess.check_output(['date', '+%Y-%m-%dT%H:%M:%S%z'],
                                       env={**os.environ, 'TZ':'Europe/Athens'}, text=True).strip()
    audit = dict(verdict=result, verdict_path=str(verdict_path.relative_to(ROOT)),
                 verdict_sha256=digest(raw), time_athens=timestamp, timezone='Europe/Athens',
                 correct=s['correct'], total=100, pending=0, reasons=reasons,
                 cluster_bootstrap=s.get('cluster_bootstrap'))
    receipt_path = local('artifacts/sf7_rc1/RELEASE_RECEIPT.json')
    train = load(receipt_path)
    require(train['sha256'] == TRAIN_SHA and train['variant'] == 'A', 'wrong train candidate')
    require(train['status'] in ('candidate_pre_audit', 'bound', 'rejected'), 'unexpected train status')
    writes = {}
    def put(path, data): writes[local(path)] = data
    train.update(status='rejected' if failed else 'bound', bound=not failed, binding_audit=audit)
    if failed:
        train['rejection_reasons'] = reasons
        put(receipt_path, encoded(train))
        put(DOC+'SF7_BINDING.md', ('# SF7 binding\n\nREJECTED. Audit '+str(s['correct'])+
            '/100.\n\n'+'\n'.join('- '+r for r in reasons)+'\n\nAudit SHA256: `'+digest(raw)+
            '`. Athens time: '+timestamp+'.\n\nOnly the train receipt and this report change; no registration or experiment-A handoff.\n').encode())
    else:
        require(sha(local('docs/labelfix/spellcheck/SF7_PREREGISTRATION.md')) == PREREG,
                'preregistration bytes changed')
        def release(r, path, expected_split=None):
            require(r.get('schema') == 'rb7-edits-only-release-v1' and r['parent'] == 'google_raw_v2_import'
                    and r['variant'] == 'A' and r['policy_digest'] == POLICY
                    and r['preregistration_sha256'] == PREREG, 'release contract mismatch')
            if expected_split:
                require(r.get('split') == expected_split and r.get('release_id') == TEST_ID, 'counterpart identity mismatch')
                require(str(r.get('source_job','')).isdigit(), 'counterpart is not a production job')
            require(sha(path) == r['sha256'], f'release SHA mismatch: {path}')
            rows = [json.loads(x) for x in path.read_text().splitlines()]
            require(len(rows) == r['row_count'] and len({x['line_id'] for x in rows}) == len(rows), 'row count/duplicate mismatch')
            require(sum(len(x['edits']) for x in rows) == r['edit_count'], 'edit count mismatch')
            require(all(isinstance(x['text'],str) and x['edits'] and x['parent'] == 'google_raw_v2_import' for x in rows), 'invalid sparse rows')
            if expected_split: require(all(x.get('split') == expected_split for x in rows), 'row split mismatch')
            return rows
        train_file = local(train['path'])
        release(train, train_file)
        train.update(release_id=TRAIN_ID)
        train.pop('rejection_reasons', None)
        counterpart = local(sys.argv[4])
        entries = {}
        def entry(path, sha256, rows, edits, role, receipts):
            return dict(path=str(path), portable_path=str(path), sha256=sha256,
                parent='google_raw_v2_import', text_field='text', id_field='line_id', status='local',
                role=role, population=dict(rows=rows, edits=edits, definition='Exact-import sparse edits-only A; omitted IDs uncovered'),
                read='exact line_id text; no fallback', binding_status='bound', binding_audit=audit,
                derivation=dict(receipts=receipts, policy_digest=POLICY))
        entries[TRAIN_ID] = entry(train_file, TRAIN_SHA, train['row_count'], train['edit_count'], 'train corrections', [str(receipt_path)])
        entries[TRAIN_ID]['derivation'].update(parent_sha256=train['parent_sha256'], preregistration_sha256=PREREG)
        pending = []
        if counterpart.exists():
            jobpath = local(counterpart/'receipt.json')
            job = load(jobpath)
            require(job.get('complete') is True and job.get('dry_run') is False and
                    job.get('inference_executed') is True and job.get('release_id') == TEST_ID, 'incomplete or mock TR2 output')
            all_rows=[]; split_info={}; split_receipts=[]; total_edits=0
            for split in ('test','dev'):
                rp = local(counterpart/split/f'RELEASE_RECEIPT_{split}.json')
                r = load(rp)
                payload = local(counterpart/split/f'release_edits_only_{split}_A.jsonl')
                all_rows.extend(release(r, payload, split))
                require(job['releases'][split]['sha256'] == r['sha256'], 'TR2 job/receipt mismatch')
                r.update(status='bound', bound=True, binding_audit=audit)
                put(rp, encoded(r)); split_receipts.append(str(rp)); total_edits+=r['edit_count']
                split_info[split] = dict(rows=r['row_count'], edits=r['edit_count'], sha256=r['sha256'],
                                        parent_sha256=r['parent_sha256'], parent_path=r['parent_path'])
            require(len({r['line_id'] for r in all_rows}) == len(all_rows), 'test/dev overlap')
            combined = b''.join((json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n').encode() for r in all_rows)
            combined_path = local('artifacts/sf7_rc1_test/release_edits_only_A.jsonl')
            put(combined_path, combined)
            e = entry(combined_path,digest(combined),len(all_rows),total_edits,'test reference; never training',split_receipts)
            e.update(parent_splits=['test','dev'], split_field='split')
            e['population']['splits'] = {k:v['rows'] for k,v in split_info.items()}
            e['sources'] = {k:dict(path=v['parent_path'],sha256=v['parent_sha256'],text_field='label',id_field='id') for k,v in split_info.items()}
            e['derivation']['parent_splits'] = split_info
            entries[TEST_ID]=e
            job.update(status='bound',bound=True,binding_audit=audit)
            put(jobpath, encoded(job))
        else: pending.append(dict(release_id=TEST_ID,status='pending',reason='TR2 production counterpart absent'))
        train['test_counterpart'] = dict(release_id=TEST_ID,status='pending' if pending else 'bound')
        put(receipt_path, encoded(train))
        # Patch envelopes only. The external registries are read, never opened for writing.
        for target, output in ((REGISTRY,'sf7_registry_entries.json'),(LQB,'sf7_lqb_registration.json')):
            registry = load(target)
            require(all(k in registry['versions'] for k in ('ru1_v3_edits','ru1_v3_test_edits')), 'missing edits-only pattern')
            patch = dict(schema='sf7-registry-patch-v1',target=str(target),base_sha256=sha(target),
                         pattern=['ru1_v3_edits','ru1_v3_test_edits'],versions={},pending=pending)
            for key,value in entries.items():
                e = dict(value)
                if target == LQB:
                    e.update(overlay=True, read='Exact line_id overlay text; omitted IDs inherit exact google_raw_v2_import.label in recorded split')
                    e.pop('portable_path',None)
                require(key not in registry['versions'], f'already registered: {key}; coordinator must reconcile')
                patch['versions'][key]=e
            put(DOC+output,encoded(patch))
        marks = local(DOC+'CORRECTION_STATUS_MARKS.md')
        old = marks.read_text()
        start='<!-- SF7_BIND1_START -->'; end='<!-- SF7_BIND1_END -->'
        block=(start+'\n\n| SF7 release | Audit | Release IDs | Status |\n|---|---|---|---|\n'+
            f"| Edits-only A | {s['correct']}/100; no PENDING | {TRAIN_ID}; {TEST_ID} | train bound; test/dev {'pending' if pending else 'bound'}; registry patches awaiting leads |\n\n"+end)
        if start in old:
            require(old.count(start)==old.count(end)==1, 'malformed SF7 status block')
            before,tail=old.split(start); _,after=tail.split(end); old=before+block+after
        else: old=old.rstrip()+'\n\n'+block+'\n'
        put(marks,old.encode())
        report=['# SF7 binding','',f"PASS: {s['correct']}/100; no PENDING. Athens time: {timestamp}.",
                f'Audit verdict SHA256: `{digest(raw)}`.',f'Cluster bootstrap: `{json.dumps(s["cluster_bootstrap"])}`.','',
                '| Version | SHA256 | Rows | Edits |','|---|---|---:|---:|']
        for key,e in entries.items(): report.append(f"| {key} | {e['sha256']} | {e['population']['rows']} | {e['population']['edits']} |")
        report += ['',f'Test/dev counterpart: {"pending; train bound alone" if pending else "bound; split hashes and counts recorded in registration patches"}.',
            '',f'Registry pattern source: `{REGISTRY}`; secondary LQB target: `{LQB}`.',
            'The JSON patches await application by the coordinator and secondary lead; neither external registry was changed.',
            '',f'Experiment-A switch-on handoff: version `{TRAIN_ID}`, SHA256 `{TRAIN_SHA}`.',
            'Coordinator: apply the registry patch, stage these exact bytes, verify SHA and sparse overlay fields (line_id/text), then enable this version in the isolated experiment-A registry. Test/dev is reference-only. No compute was launched.','']
        put(DOC+'SF7_BINDING.md','\n'.join(report).encode())
    # Preflight every destination before the first write, including the log.
    log = local('docs/reviews/harness/sf7_bind.log')
    for path in writes: local(path)
    logline = f'{timestamp} {"EXECUTE" if EXECUTE else "DRY-RUN"} {result} audit_sha256={digest(raw)}\n'
    for path,data in writes.items():
        print(('WRITE' if EXECUTE else 'WOULD WRITE'),path.relative_to(ROOT),digest(data))
    if EXECUTE:
        for path,data in writes.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            # Exclusive temp file inside the same worktree; replace avoids modifying hardlinks.
            import tempfile
            fd,tmp = tempfile.mkstemp(prefix='.sf7-bind-',dir=path.parent)
            try:
                with os.fdopen(fd,'wb') as f: f.write(data)
                os.replace(tmp,path)
            finally:
                if os.path.exists(tmp): os.unlink(tmp)
    with log.open('a') as f: f.write(logline)
    print(logline.strip())

try: main()
except (ValueError, KeyError, OSError, TypeError) as e:
    print(f'ABORT: {e}',file=sys.stderr)
    sys.exit(2)
PY
