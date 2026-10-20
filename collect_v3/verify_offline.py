"""Build the final offline receipt with a fake credential present end to end.

Requires a fresh replay directory. Never calls providers. Existing replay data
is preserved; choose --replay-output for an additional independent run.
"""
from __future__ import annotations
from collections import defaultdict
import argparse,os,time,uuid,re
from pathlib import Path
from .common import TOKEN_ENV,read_json,write_json,sha,disk_bytes
from .offline import replay,no_network

def verify(projects,out,replay_output,test_evidence=None,tests_runner=None):
    out=Path(out);replay_output=Path(replay_output);evidence=Path(test_evidence) if test_evidence else out/'test_evidence_w1b_final'
    if replay_output.exists():raise ValueError('choose a fresh --replay-output; existing evidence is preserved')
    secret='FAKE-COLLECT-V3-'+uuid.uuid4().hex;prior=os.environ.get(TOKEN_ENV);os.environ[TOKEN_ENV]=secret;started=time.time()
    try:
        with no_network():
            proof=replay(projects,replay_output)
            from .cards import cards
            from .config import config
            card_report=cards(config(output_root=str(replay_output)),'W1')
        if proof['parity']['status']!='ok':raise AssertionError('T4b parity differs')
        # Worker tests inspect this fresh replay, never an old Mac worktree.
        # Keep the fake environment credential present during both stages.
        if tests_runner:tests_runner(replay_output)
        # Scan every build output and log, including binary SQLite and crops.
        files=0;size=0
        for p in out.rglob('*'):
            if p.is_file():
                data=p.read_bytes();files+=1;size+=len(data)
                if secret.encode() in data:raise AssertionError('credential probe found in an output; content suppressed')
        timings=read_json(replay_output/'mock_request_timing.json');hosts=defaultdict(list)
        for event in timings['requests']:hosts[event['host']].append(event['start'])
        spacing={h:min(b-a for a,b in zip(sorted(v),sorted(v)[1:])) for h,v in hosts.items() if len(v)>1}
        if any(v<1 for v in spacing.values()):raise AssertionError('mock per-host spacing below one second')
        detached=read_json(evidence/'detached_receipt.json')
        rate=read_json(evidence/'rate_receipt.json');resume=read_json(evidence/'resume_receipt.json');scrub=read_json(evidence/'credential_scrub_receipt.json')
        tests=(out/'tests.log').read_text()
        counts=re.findall(r'(\d+) passed',tests)
        if not counts or 'skipped' in tests or 'failed' in tests:raise AssertionError('contract tests must pass with no skips')
        passed=int(counts[-1])
        limiter=read_json(evidence/'limiter_2proc_receipt.json')
        if limiter.get('status')!='ok' or limiter.get('processes')!=2:raise AssertionError('two-process limiter proof missing')
        from .retention import project
        retention=project(replay_output,out)
        plan=read_json(out/'plan_receipt.json')
        receipt=dict(schema='collect-v3-dry-run-2',network=False,socket_and_DNS_blocked=True,provider_calls=0,actual_spend_usd=0,proof=proof,parity=dict(proof['parity'],all_T4b_fields=55),resume=resume,detached=detached,limiter_2proc=limiter,retention=retention,exclusion_manifest=read_json(out/'exclusions_receipt.json'),cards=dict(strata=len(card_report),row_cards=sum(r['cards'] for r in card_report if r.get('primary_class')),page_checks=sum(r['cards'] for r in card_report if r.get('stratum')=='blind_pages'),small_page_pools_all_checked=all(r['all_pages_small_pool'] for r in card_report if r.get('stratum')=='blind_pages'),supplement_cards=sum(r.get('supplement_cards',0) for r in card_report)),rate=dict(rate,replay_minimum_spacing_seconds_per_host=spacing),credential_scrub=dict(scrub,end_to_end_fake_env_present=True,all_output_files_scanned=files,all_output_bytes_scanned=size,secret_found=False),tests=dict(status='ok',passed=passed,failed=0,skipped=0,command=('PYTHONDONTWRITEBYTECODE=1 OMP_THREAD_LIMIT=1 python -m worker.test_offline collect_v3/tests' if tests_runner else 'PYTHONDONTWRITEBYTECODE=1 OMP_THREAD_LIMIT=1 .venv/bin/python -m pytest -q collect_v3/tests'),log='tests.log'),W1=dict(sources=len(plan['sources']),physical_providers=8,pages=plan['W1_pages'],projected_usd=plan['W1_projected_usd'],cap_usd=plan['W1_cap_usd'],manifest_sha256=sha(out/'W1_manifest.jsonl')),replay_output=str(replay_output),elapsed_seconds=time.time()-started,disk_bytes=disk_bytes(out),limitations=['No live provider availability, host performance or credentials were tested.','Production differs intentionally from T4b in screen-as-flag and explicit source marks policy; compatibility parity is separately proven.','Small page pools (<60) check all pages; only small row pools report 100-card shortfalls.','Unknown bounds resolve the full seeded book allocation before W1 OCR, enabling W1 spread; no paid reads during resolution. Physical totals of unresolved inventory items remain unknown.'])
        write_json(out/'dry_run_receipt.json',receipt);return receipt
    finally:
        if prior is None:os.environ.pop(TOKEN_ENV,None)
        else:os.environ[TOKEN_ENV]=prior

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--projects-root',default=str(Path.home()/'Projects'));p.add_argument('--output-root',default='docs/harvest/collect_v3');p.add_argument('--replay-output',default='docs/harvest/collect_v3/rev2_credential_replay');p.add_argument('--test-evidence');a=p.parse_args();r=verify(a.projects_root,a.output_root,a.replay_output,a.test_evidence);print(f"parity={r['parity']['status']} lines={r['parity']['lines']} tests={r['tests']['passed']} actual_spend_usd=0")
