"""Verify, seal and archive CQ6C locally; no deployment or submission."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[3]
CQ=ROOT/'artifacts/cq4'
P=CQ/'cq6c_package'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def frozen_check():
    expected=json.loads((P/'evidence/source_inputs.json').read_text())['frozen_cq6_hashes']
    actual_paths={str(p.relative_to(CQ)) for p in (CQ/'cq6_package').rglob('*') if p.is_file()}
    expected_paths={p for p in expected if p.startswith('cq6_package/')}
    assert actual_paths==expected_paths
    assert all(sha(CQ/p)==h for p,h in expected.items()),'frozen CQ6 changed'
    return len(expected)

def main():
    immutable_count=frozen_check()
    # Use the architecture matching this Mac's installed NumPy. Linux coordinator
    # commands use the unchanged parent environment, not this local workaround.
    python=['arch','-x86_64',sys.executable] if sys.platform=='darwin' else [sys.executable]
    logs=[]
    for script in ('test_instrument.py','test_admission.py'):
        result=subprocess.run(python+['-B',str(P/script)],capture_output=True,text=True,check=True)
        logs.append(script+'\n'+result.stdout+result.stderr)
    (P/'evidence/local_semantic_tests.txt').write_text('\n'.join(logs))
    for path in P.rglob('*.py'):
        ast.parse(path.read_text(),filename=str(path))
    for path in (P/'slurm').glob('*.sbatch'):
        subprocess.run(['bash','-n',str(path)],check=True)
    for source in (CQ/'tools/build_cq6c.py',CQ/'tools/seal_cq6c.py'):
        shutil.copyfile(source,P/'evidence'/source.name)
    data=[dict(path=str(p.relative_to(P)),sha256=sha(p),bytes=p.stat().st_size)
          for p in sorted((P/'data').iterdir()) if p.is_file()]
    dump(P/'DATA_MANIFEST.json',dict(files=data))
    dump(P/'validation_receipt.json',dict(
        status='PASS_FOR_ASSEMBLY_ONLY',capital_quota_pass=True,
        parent_recipe_parameters=19,intended_changes=0,
        parent_sources_config_and_three_run_bindings_live_hash_verified=True,
        instrument_semantic_tests_passed=4,parent_unknown_quarantine_fixture_passed=1,
        python_syntax_pass=True,sbatch_syntax_pass=True,
        frozen_cq6_files_unchanged=immutable_count,
        local_test_environment='macOS x86_64 Python via arch; installed NumPy architecture workaround',
        remote_access='read-only SSH clariden: sacct, scontrol, sha256sum only',
        real_input_dry_run=False,training_smoke=False,
        production_training_admission=False,production_submission_commands='missing',
        deployed=False,submitted=False))
    r=json.loads((P/'assembly_receipt.json').read_text())
    handoff='''# CQ6C — new assembly from the CQ7-updated aggregate

19 October 2026, Europe/Athens. **Assembly ready at 800/800 negatives and
500/500 positives. Training admission is not established; production submission
commands remain missing.** This is a new attempt, not an unstopping of CQ6.
Nothing was deployed or submitted. Clariden access was read-only SSH.

| Capital slice | Negative | Positive |
|---|---:|---:|
| Frozen R2a v2 | 214 | 127 |
| Resolved top-up available | 720 | 387 |
| Selected top-up | 586 | 373 |
| Assembled total | 800 / 800 | 500 / 500 |
| Unused resolved top-up | 134 | 14 |

All 1,107 resolved labels, including the 98 CQ7 positive labels carrying
`C_sol_two_independent_CQ7_agreed`, are available to the same frozen selection
order. Take the first 586 negatives and first 373 positives in that order, then
retain their original interleaving. This selects 95 CQ7 labels and 278 previously
resolved positives; CQ7 labels are not preferentially selected. The 959 selected
top-up proposals plus the byte-identical 1,572-row v2 file yield 2,531 assembled
overlay rows. The other 148 resolved top-up labels are preserved separately;
quarantine is not promoted. Source selections match CQ4's frozen build hashes.

W-CAP remains **witness only**, 281/300 resolved (133 marked, 148 bare, 19
quarantined). All 300 selected identities are in the exposure guard with
`trained_on=false`; planned overlay identities are also guarded. Top-up and
W-CAP documents are disjoint. Saved zero-old-crop overlap evidence is retained;
W-CAP is checked against old training and v2 documents. Old-pool references retain
1,935,016 rows, 1,935,011 identities, and all five excess duplicate rows. The old
pool was not rewritten, transformed or deduplicated. Unique corrections replace
in place; duplicate-key hits refuse admission, following R2J4.

## Frozen scientific contract and other heads

Preregistration SHA256:
`7cb5a6fb53a4b5c35a55e85cce9a14961570b4a880cc79a6e4f227b9149f6964`
(amendment 1a). No preregistration or aggregate receipt was rewritten. The current
aggregate and amendment binding are copied and hashed with the new package.

“The validation documents are now exposed to capitals witness selection, so they
cannot serve as a fresh final capitals readout. The locked (ii)/(i-b) strata are
the only untouched final cohorts. The LQB in-sample guard lists the W-CAP items
against R2a-2.” This is an exposure guard, not training on W-CAP.

CQ4/CQ7 assert only breathing/accent on top-up rows. The unread diaeresis and
subscript heads remain UNKNOWN (`null, null`), without zero-fill, teacher fill,
or a new masked loss. Actual parent `r2_manifest.py` quarantines an entire
UNKNOWN tuple; actual parent `r2a_run.py` rejects such overlay rows. The captured
parent implementation is live-hash-verified and its quarantine branch passes a
small semantic fixture. Consequently all 959 assembled top-up proposals remain
unadmitted for four-head training under the unchanged parent policy.

The quota stop is cleared for this NEW assembly only. The word `ready` here and
`verify_deploy.py --require-ready` refer to assembly/coordinator review, not
trainability or authorization. `--require-training-ready` refuses this package.
See `HEADS_AND_ADMISSION.md` and `data/HEAD_ADMISSION.json`. Completing the missing
truth/runtime admission cannot be replaced by inventing a rule.

## Recipe, resources and instrument

Actual R2a job 3683130: **19 parameters, 0 intended changes**, re-tabled in
`PARAMETERS_VS_R2A.md`, including additional effective settings and every parent
config leaf. Seeds remain 20261016, 20261017, 20261018. Live read-only SSH verified
trainer/model/extractor/common sources, manifest/runner sources, config and all
three run-binding hashes against the captured evidence.

Live sacct confirms COMPLETED, `normal`, `01:21:00`, one node/four GPUs/account
a0140. The combined job is the only per-kind evidence available: prepare, train,
and evaluate explicitly inherit normal/81 minutes; no separate per-kind timing
measurements are invented. Smoke explicitly uses debug/81 minutes, within the
live 90-minute maximum. Smoke tests instrument semantics and parent quarantine,
not real-input training. Prepare audits admission; train is guarded and has no
production runtime. Evaluate consumes external ledgers offline.

The preserved W-CAP instrument implements exact-tuple recall, >=10 pp gain,
50,000 paired document-cluster bootstrap replicates (seed 20261017), CI lower
>0, gain in >=2/3 seeds with positive mean, <=+2 pooled invented marks, explicit
false additions, secondary R2a comparison, and tier-A/B LQB named-mark precision.
Complete paired predictions and blind lead pixel review are required. Protection
families remain unchanged; their scorer/digest are evidence, not a claim of an
integrated production run or overall PASS. Four instrument fixtures and the
parent quarantine fixture pass locally. No real model evaluation occurred.

## Coordinator commands and custody

Package: `artifacts/cq4/cq6c_package`. Read its `SUBMIT.md` for exact safe checks,
documented coordinator debug-smoke/admission-audit commands, offline evaluation,
and production limitations. The local instrument test uses `arch -x86_64`
because this Mac's installed NumPy extension is x86_64; Clariden uses the parent
venv directly. No environment was installed or changed.

```sh
python3 -B artifacts/cq4/cq6c_package/verify_deploy.py --require-ready
python3 -B artifacts/cq4/cq6c_package/verify_deploy.py --require-training-ready
# Second command is expected NOT_ADMITTED / nonzero.
```

`DATA_MANIFEST.json` binds data. `DEPLOY_FILES.txt` and `DEPLOY_SHA256.txt` bind
DEPLOY_COUNT payload files; the two list files travel with the package but are
excluded from their own hash list. These conventional names do not certify
production deployability. Smoke and verification commands are ready; production
training/submission commands are missing pending legitimate four-head admission,
source/extractor qualification, runtime adaptation, real-input/debug training
smoke, protection integration and a new seal. No fresh scientific rule is added.

The original CQ6 tree, hand-off, stopped tar and sidecar are checked byte-for-byte
against their pre-assembly snapshot. Custody: `CQ6C_PACKAGE_BUNDLE.tar` plus
`CQ6C_PACKAGE_BUNDLE.sha256`, containing this package and an identical hand-off.
No git metadata was changed; the source HEAD is recorded in source_inputs.json.

CQ6C: STATUS | top-up assembled 800/800 500/500 | package artifacts/cq4/cq6c_package | deploy files DEPLOY_COUNT | smoke/verify/submit commands: missing | commit bundle
'''.replace('STATUS',r['status'])
    (P/'CQ6C_HANDOFF.md').write_text(handoff)
    paths=sorted(p for p in P.rglob('*') if p.is_file() and p.name not in ('DEPLOY_FILES.txt','DEPLOY_SHA256.txt') and '__pycache__' not in p.parts)
    handoff=handoff.replace('DEPLOY_COUNT',str(len(paths)))
    (P/'CQ6C_HANDOFF.md').write_text(handoff)
    (CQ/'CQ6C_HANDOFF.md').write_text(handoff)
    (P/'DEPLOY_FILES.txt').write_text(''.join(str(p.relative_to(P))+'\n' for p in paths))
    (P/'DEPLOY_SHA256.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n' for p in paths))
    subprocess.run([sys.executable,'-B',str(P/'verify_deploy.py'),'--require-ready'],check=True)
    gate=subprocess.run([sys.executable,'-B',str(P/'verify_deploy.py'),'--require-training-ready'],capture_output=True,text=True)
    assert gate.returncode!=0 and 'NOT_ADMITTED:' in gate.stderr
    assert frozen_check()==immutable_count
    bundle=CQ/'CQ6C_PACKAGE_BUNDLE.tar'
    with tarfile.open(bundle,'w') as tar:
        # Include only sealed files and the two closure lists; no Python caches.
        for path in paths+[P/'DEPLOY_FILES.txt',P/'DEPLOY_SHA256.txt']:
            tar.add(path,arcname='cq6c_package/'+str(path.relative_to(P)),recursive=False)
        tar.add(CQ/'CQ6C_HANDOFF.md',arcname='CQ6C_HANDOFF.md',recursive=False)
    (CQ/'CQ6C_PACKAGE_BUNDLE.sha256').write_text(sha(bundle)+'  '+bundle.name+'\n')
    print(handoff.splitlines()[-1])

if __name__=='__main__':
    main()
