"""Seal a STOPPED CQ6 evidence package, not a deployable training candidate."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[3]
CQ=ROOT/'artifacts/cq4'
P=CQ/'cq6_package'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def render(x):return json.dumps(x,ensure_ascii=False).replace('|','\\|')

def main():
    receipts=[load(P/f'evidence/run_binding_{s}.json') for s in (20261016,20261017,20261018)]
    for name in ('r1_train.py','r1_common.py','r1_model.py','r1_extract.py'):
        for r in receipts:
            assert sha(P/'evidence'/name)==r['file_sha256']['scripts/labelfix/clariden/'+name]
    recipe=receipts[0]['parameters'];n=len(recipe)
    for r in receipts:
        assert r['runtime']['job_id']=='3683130'
        assert {k:v for k,v in r['parameters'].items() if k not in ('seed','sampler_seed')}=={k:v for k,v in recipe.items() if k not in ('seed','sampler_seed')}
    rows=[]
    for k in recipe:
        val={str(s):r['parameters'][k] for s,r in zip((20261016,20261017,20261018),receipts)} if k in ('seed','sampler_seed') else recipe[k]
        rows.append((k,val,val,'0; intended unchanged'))
    effective={
        'training_initialization':'new MarkReader; seeded from scratch, no parent checkpoint warm start',
        'arm':'A','training_view':'wide; grey plus recogniser-span mask, 2 x 64 x 128',
        'embedding_dimension':64,'network_channels':[32,64,128,192],
        'model_MLP':'256 + ReLU; four factor heads',
        'augmentation':'none in actual training loop',
        'learning_rate_schedule':'constant; no scheduler',
        'AdamW_other_options':'not supplied; same installed torch defaults required',
        'class_weights':'old targets only; sqrt(N/max(count,1)); capped at 10, normalized to mean 1',
        'loss':'sum of four weighted cross entropies; overlay per-row weight 1',
        'sampler':'ArmBatches; replacement; 40% none, >=5% rare/compound, remainder equal head/value pools',
        'rare_definition':'marked and >=2 heads, or composed class count <1000',
        'sampler_epoch_seed':'sampler_seed + epoch (1..15)',
        'steps_per_epoch':'ceil(pool size / 512); final batch truncated',
        'workers':4,'torch_threads':8,'pin_memory':True,'persistent_workers':True,
        'memory_format':'channels_last','cudnn_benchmark':True,
        'gradient_accumulation':1,'gradient_clipping':'none','GradScaler':'none',
        'checkpoint_selection':'strict improvement in natural validation loss; best.pt each improvement',
        'seed_execution':'three threads, one seed per cuda:0/1/2; fourth GPU not assigned a seed',
        'native_extraction_workers':8,'inference_batch_size':512,'inference_workers':4,
        'recognizer_alignment_batch_size':16,'recognizer_threads':8,
        'OMP_NUM_THREADS':8,'OPENBLAS_NUM_THREADS':1,'VECLIB_MAXIMUM_THREADS':2,
        'uenv':'none in parent sbatch; direct venv_l1/bin/python',
        'python_runtime':receipts[0]['runtime']['python'],'torch_runtime':receipts[0]['runtime']['torch'],
        'hardware':'NVIDIA GH200 120GB','production_partition':'normal','production_time':'01:21:00',
        'nodes':1,'tasks':1,'gpus_per_node':4,'exclusive':True,'account':'a0140'}
    text=['# Actual R2a recipe: job 3683130','',
          f'{n} fields in the actual `run_binding.parameters` object, all preserved in the intended CQ6 recipe (0 changed). No CQ6 training ran. The additional effective settings below are also disclosed; the field count in the hand-off refers only to that actual binding object.',
          '', '| Parameter | Actual R2a | Intended R2a-2 | Change |','|---|---|---|---|']
    text += [f'| {k} | `{render(a)}` | `{render(b)}` | {d} |' for k,a,b,d in rows]
    text += ['', '## Effective code, environment and resource settings','',
             '| Parameter | Actual R2a | Intended R2a-2 | Change |','|---|---|---|---|']
    text += [f'| {k} | `{render(v)}` | same | 0 intended |' for k,v in effective.items()]
    text += ['', 'The trainer/model/extractor source SHA256 values match all three actual run bindings. `evidence/r2a_run.py` supplies CLI arguments and concurrency; `evidence/r1_train.py` supplies sampler, optimiser, loss and validation behavior. Runtime/library defaults are preserved by requiring the same recorded environment; they are not newly tuned. Sampler exposure and the number of batches naturally depend on the changed training pool.',
             '', '## Data and package differences (scientific intervention; not hidden recipe changes)','',
             '| Surface | Actual R2a | CQ6 |','|---|---|---|',
             '| Old pool | 1,935,016 rows; 1,935,011 keys; 5 excess duplicate rows | Same reference and exact BASE order required; no removal |',
             '| v2 overlay | 1,572 slots; capitals 214 negative / 127 positive | Byte-identical copy |',
             '| Separate top-up | absent | 875 provisional rows (586 negative / 289 positive); partial only |',
             '| Final capital slice | 214 / 127 | 800 / 416; 84 positive shortfall; STOPPED |',
             '| Witness | T4 and protection cohorts | W-CAP 281 resolved, 133 marked; never training |',
             '| Preregistration | amendment 1, dbac559f… | amendment 1a exposure consequence note; current hash below |',
             '| Job kinds | one combined A/B/C/D normal job, 81 minutes | normal 81-minute resource stubs for prepare/train/eval; no independently measured kind times |',
             '| Debug | no debug evidence in this parent sacct | semantic smoke stub explicitly debug, 81 minutes; partition override is not a recipe change |',
             '| Production runner | actual R2a runner | not adapted: frozen quota stop occurs before deployable runtime construction |',
             '', '## Every parent config leaf','',
             'Path/hash/count differences are explicit below. These are custody or data parameters rather than training hyperparameters. Parent config is preserved as evidence, not presented as a runnable CQ6 config.',
             '', '| Parent config field | Actual value | CQ6 disposition |','|---|---|---|']
    def leaves(x,prefix=''):
        if isinstance(x,dict):
            for k,v in x.items():yield from leaves(v,prefix+'.'+k if prefix else k)
        else:yield prefix,x
    for k,v in leaves(load(P/'evidence/config.json')):
        disposition='frozen parent reference; requires rebinding for a future ready candidate'
        if k=='seeds':disposition='identical full seeds'
        if k in ('data','heldout','teacher','recognizer','checkpoints.A16.path','checkpoints.BASEs17.path','checkpoints.BASEs18.path'):disposition='same parent reference required'
        if k=='manifest':disposition='partial overlay has its own hash; NOT admitted for training'
        if k.startswith('forecast'):disposition='historical R2a forecast, not a CQ6 forecast'
        text.append(f'| {k} | `{render(v)}` | {disposition} |')
    (P/'PARAMETERS_VS_R2A.md').write_text('\n'.join(text)+'\n')
    dump(P/'recipe_equivalence.json',dict(parent_job=3683130,parameter_fields=n,changed=0,
        scope='intended recipe only; no CQ6 training executed',actual_parameters_by_seed={str(s):r['parameters'] for s,r in zip((20261016,20261017,20261018),receipts)},effective_settings=effective))
    (P/'slurm').mkdir(exist_ok=True)
    for kind in ('prepare','train','evaluate','smoke'):
        partition='debug' if kind=='smoke' else 'normal'
        body='''#!/usr/bin/env bash
# Resource specification only: STOPPED CQ6 candidate. Nothing has been submitted.
#SBATCH --account=a0140
#SBATCH --partition=PARTITION
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:21:00
#SBATCH --job-name=CQ6_KIND
#SBATCH --output=CQ6_KIND_%j.log
set -euo pipefail
cd "${CQ6_PACKAGE_ROOT:?set the reviewed package root}"
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
CQ6_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
'''.replace('PARTITION',partition).replace('KIND',kind)
        if kind=='smoke':
            body+='''# Semantic smoke only; real-input trainer smoke is pending a complete candidate.
"$CQ6_PYTHON" -B verify_deploy.py
srun --ntasks=1 --cpu-bind=none "$CQ6_PYTHON" -B test_instrument.py
'''
        else:
            body+='''"$CQ6_PYTHON" -B verify_deploy.py --require-ready
echo 'STOP: runtime adaptation is not present in this stopped evidence package' >&2
exit 78
'''
        (P/'slurm'/f'{kind}.sbatch').write_text(body)
    (P/'EVALUATION.md').write_text('''# Evaluation contract

`evaluate.py` is an offline instrument, not an inference runner. W-CAP remains
evaluation only: all 281 resolved tuples, 133 marked and 148 bare. Missing arm
predictions stop scoring rather than shrinking support. Inputs are JSONL rows
`seed, arm, slot_id, breathing, accent`; arms are BASE, R2a, R2a-2 for each full
seed 20261016, 20261017, 20261018. Truth additionally has `doc`.

Primary: exact breathing+accent tuple recall on marked capitals versus same-seed
BASE. Pooled gain must be >=10 percentage points; 50,000 document-cluster
bootstrap replicates, numpy default_rng seed 20261017, percentile 95% lower bound
strictly >0; >=2 seeds improve and mean gain positive; bare-capital invented marks
increase <=2 pooled. Pool seed-observations but resample each document's slots and
all seeds together. Report false-addition counts and delta separately. Secondary
versus R2a has no pass criterion.

Every disagreement between any arms must receive blind lead pixel review before
scoring. `--lead-review` is JSON with `truth_sha256`, `predictions_sha256`, `items`;
each item is `seed, slot_id, pixel_checked: true, blind_to_arm: true, evidence`.
Its exact item set must match disagreements. Review evidence is supplied by the
lead; this task performed no pixel adjudication. Any truth correction must be
logged, applied symmetrically to all arms, and bound by the reviewed truth hash.
Never replace the frozen truth without retaining original/correction receipts.
The CLI enforces the same 281 identities and document mappings. Corrections need
`original_truth_sha256` and `truth_corrections` entries with `slot_id, old_tuple,
new_tuple, evidence` in the lead-review JSON; the ledger must match every change.

LQB `--lqb` input is complete canonical slot ledgers with `slot_id, arm,
truth_tier, truth, prediction`: four integer heads in R1 order, null for UNKNOWN.
Tier A/B named-mark precision counts correct predicted nonzero heads divided by
predicted nonzero heads on known truth. False additions count nonzero predictions
on known zero heads. Wrong names and missing predictions are separate counts.
Use `--guard data/lqb_guard.jsonl`. All 300 W-CAP selected identities are listed
against R2a-2, including the 19 quarantined slots; planned v2/top-up identities
are also excluded from independent LQB readout. Exposed results are descriptive.
This guard records exposure/planned training, not completed CQ6 training.

The main instrument can establish only the primary, never overall adoption.
Unchanged protection families must still use the frozen parent scorer/digest
(captured under evidence): held-out 16 documents, T4 791 word witnesses,
DEV 600 lines / 1,793 items, owner overlay v1.1 symmetrically applied.
Common held-out classes >=200 support: precision lower bound >-0.20 pp, recall
lower bound >-0.50 pp, same Holm families as parent. Sparse exact-name errors:
no net increase; list every paired regression. Non-target T4 uses same margins.
Owner named-slot regression fails. Inconclusive primary means not adopted;
any protection FAIL or point-estimate margin breach prevents adoption. DEV is
descriptive. No automatic overall-PASS function is supplied in this stopped
package; adapting and validating the parent protection runtime remains pending.

Example (only after real prediction ledgers and blind lead review exist):

```sh
python -B evaluate.py --truth data/wcap_truth.jsonl \\
  --predictions predictions.jsonl --lead-review lead_review.json \\
  --lqb lqb_ledger.jsonl --guard data/lqb_guard.jsonl --out evaluation.json
```
''')
    (P/'SUBMIT.md').write_text('''# Coordinator hand-off — STOPPED

Do not deploy or submit this package. The frozen 800/500 capital slice can only
be assembled to 800/416 from the resolved labels. The missing 84 positives are
not supplied by duplicating rows, using W-CAP, or treating quarantine as truth.
The written W-CAP minimum of 210 passes (281); CQ4's inventory minimum 844 also
passes. Neither rule authorizes a smaller final training quota. No separate
lower final-training minimum exists in the supplied preregistration.

Local receipt/byte checks (safe; no deployment or scheduler action):

```sh
cd artifacts/cq4/cq6_package
python3 -B verify_deploy.py
python3 -B verify_deploy.py --require-ready  # expected STOP / nonzero
```

If a separately reviewed package is later staged, its coordinator verifies it
read-only with (this command is documented, not executed here):

```sh
ssh clariden 'cd /REVIEWED/PACKAGE/PATH && python3 -B verify_deploy.py --require-ready'
```

No valid sbatch submission command is authorized for this stopped package.
`slurm/{prepare,train,evaluate}.sbatch` are guarded resource specifications; all
refuse to execute work. They preserve parent normal/01:21:00/one node/four GPUs.
Parent sacct has one combined job, not three independent per-kind limits; no
per-kind timing measurement is claimed. `slurm/smoke.sbatch` explicitly uses
debug/01:21:00 for semantic fixtures, not a qualified real-input training smoke.
Nothing was submitted, including smoke.

Continuation needs 84 additional admissible positive capital labels from the
authorized lead process (or an explicit scientific quota amendment), then a new
manifest seal. Keep the 134 unused resolved negatives available, not appended.
The provisional top-up records contain CQ4 breathing/accent truth only: unasserted
diaeresis/subscript heads remain UNKNOWN rather than invented zero labels. Their
four-head admission and physical frozen-extractor coverage must be resolved and
verified before they can become executable training rows.

Only after complete admission: adapt the parent runtime to the top-up native
sources without weakening R2J4, run the real-input A/B check and debug training
smoke, finish protection-family scoring integration, bind every native asset
and checkpoint, reseal DEPLOY closure, then prepare concrete coordinator sbatch
commands. This package stops before those operations and must not be called ready.
''')
    dump(P/'validation_receipt.json',dict(
        status='PASS_FOR_STOPPED_EVIDENCE_PACKAGE_ONLY',
        actual_parent_source_hashes_verified=True,three_seed_recipe_bindings_equal=True,
        instrument_semantic_tests=4,full_production_bootstrap_run=False,
        real_input_dry_run=False,training_smoke=False,deployed=False,submitted=False,
        scientific_readiness='STOPPED: 84 positive capital labels missing',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    for source in (CQ/'tools/build_cq6.py',CQ/'tools/seal_cq6.py'):
        shutil.copyfile(source,P/'evidence'/source.name)
    prereg=sha(P/'R2A2_PREREGISTRATION.md')
    handoff=f'''# CQ6 — stopped at the frozen capital quota

19 October 2026, Europe/Athens. Prepared locally; Clariden access was read-only
SSH `clariden`. No deployment, Slurm submission, reader, OCR, training, inference,
remote write or real-input dry run occurred. This is a stopped evidence package,
not a trainable or deployable candidate. Source checkout remains at the recorded
HEAD; unrelated untracked files were preserved. Custody is a local tar bundle.

## Assembly

| Capital slice | Negative | Positive |
|---|---:|---:|
| Frozen R2a v2 | 214 | 127 |
| Resolved top-up labels available | 720 | 289 |
| Selected additional labels | 586 | 289 |
| Assembled total | 800 / 800 | 416 / 500 |
| Shortfall | 0 | 84 |

The 875 selected top-up identities follow the already frozen selection order;
134 excess resolved negatives are retained separately. The v2 1,572-slot file
is copied byte-for-byte (20b24e0f…). The partial combined overlay has 2,447 rows.
CQ4 top-up and v2 identities are disjoint; W-CAP/top-up documents are disjoint.
The old pool is referenced exactly as BASE used it: 1,935,016 rows, five excess
duplicate rows retained. Actual parent bindings and the saved zero-old-crop
overlap receipt are included. No old pool was rewritten or deduplicated.

W-CAP stays witness only: 281/300 resolved, 133 marked / 148 bare, 19 quarantined.
The explicit preregistered 210-slot W-CAP minimum passes. CQ4's build inventory
minimum 844 also passes (1,009 resolved, 875 selected). The frozen preregistration
does not specify a separate reduced final-training quota. Because it explicitly
requires 800/500, this task does not certify 800/416 as exactly preregistered.
This stop is a final-quota shortfall, not a failure of the W-CAP minimum or a
claim of demonstrated statistical power.

The partial top-up rows are truth proposals, not admitted four-head training
rows: CQ4 asserts breathing/accent only; other heads remain UNKNOWN. No physical
extraction admission, real-input dry run, adapted production runner, or training
smoke is claimed. These are pending a complete training candidate.

## Amendment 1a and custody

Current preregistration SHA256: `{prereg}`.
Original amendment-1 SHA256:
`dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc`.

The amendment quotes the consequence: “The validation documents are now exposed
to capitals witness selection, so they cannot serve as a fresh final capitals
readout. The locked (ii)/(i-b) strata are the only untouched final cohorts. The
LQB in-sample guard lists the W-CAP items against R2a-2.”

It is explicitly dated after the existing reads, not backdated. CQ4 build,
re-read-build, aggregate and rescan-evidence receipts have a separate
`cq6_amendment1a_binding`; their historical freeze hashes remain intact.
Original receipt bytes are archived inside the package. All 300 selected W-CAP
items, including quarantine, are in the R2a-2 exposure guard; `trained_on=false`.
The combined LQB guard also covers proposed training overlay identities.

## Recipe, instruments and limits

Read the actual parent config, run bindings for all three seeds, trainer,
extractor, model, sbatch, and sacct on Clariden. The four critical source hashes
match all actual bindings. `{n}` actual recipe fields, 0 intended changes;
additional effective settings and every config leaf are tabled in
`cq6_package/PARAMETERS_VS_R2A.md`. This states intended equality, not a new-run
measurement. Full seeds remain 20261016, 20261017, 20261018.

Parent job 3683130 COMPLETED: partition `normal`, limit `01:21:00`, one node,
four GPUs, account a0140. Parent sacct supplies only a combined-job limit.
The prepare/train/evaluate resource stubs explicitly preserve it; debug semantic
smoke explicitly overrides partition to `debug` and keeps 81 minutes (live debug
max 90 minutes). No independently observed per-kind limits are fabricated.
Production stubs refuse admission. Real training smoke remains pending.

`evaluate.py` implements exact-tuple W-CAP recall, >=10 pp gain, 50,000 paired
document-cluster bootstrap replicates (seed 20261017), CI lower >0, gains in
>=2/3 seeds with positive mean, <=+2 pooled invented marks, explicit false
additions, secondary R2a comparison, and LQB tier-A/B named-mark precision.
Complete predictions and blind lead pixel-review receipts are required. Four
small semantic fixtures passed. No real model predictions or full endpoint
results are claimed. Parent protection scorer/digest are preserved by reference;
protection integration and overall adoption remain unestablished.

## Coordinator files and verification

- Package: `artifacts/cq4/cq6_package/`.
- Read `SUBMIT.md`, `EVALUATION.md`, `assembly_receipt.json` and parameter table.
- `DATA_MANIFEST.json` binds data; `DEPLOY_FILES.txt` and `DEPLOY_SHA256.txt` bind
  the whole stopped package, despite their conventional deployment filenames.
- Run `python3 -B artifacts/cq4/cq6_package/verify_deploy.py` for byte closure.
- Add `--require-ready` for expected refusal. No deployment command was run.
- Bundle: `artifacts/cq4/CQ6_STOPPED_BUNDLE.tar`; SHA256 sidecar accompanies it.

No reduced quota was silently adopted, no quarantine promoted to truth, and no
W-CAP label trained on. Remaining admission work is listed in `SUBMIT.md`.

CQ6: stopped | top-up assembled 800/800 416/500 | W-CAP witness 281/300 | seeds 20261016/17/18 | recipe = 3683130 ({n} params, 0 changed) | package artifacts/cq4/cq6_package | commit bundle
'''
    (CQ/'CQ6_HANDOFF.md').write_text(handoff)
    shutil.copyfile(CQ/'CQ6_HANDOFF.md',P/'CQ6_HANDOFF.md')
    for f in P.rglob('*.py'):ast.parse(f.read_text())
    for f in (P/'slurm').glob('*.sbatch'):subprocess.run(['bash','-n',str(f)],check=True)
    files=sorted(p for p in P.rglob('*') if p.is_file() and p.name not in ('DEPLOY_FILES.txt','DEPLOY_SHA256.txt') and '__pycache__' not in p.parts)
    (P/'DEPLOY_FILES.txt').write_text(''.join(str(p.relative_to(P))+'\n' for p in files))
    (P/'DEPLOY_SHA256.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n' for p in files))
    subprocess.run(['python3','-B',str(P/'verify_deploy.py')],check=True)
    rejected=subprocess.run(['python3','-B',str(P/'verify_deploy.py'),'--require-ready'],capture_output=True,text=True)
    assert rejected.returncode!=0 and 'STOP:' in rejected.stderr
    bundle=CQ/'CQ6_STOPPED_BUNDLE.tar'
    with tarfile.open(bundle,'w') as tf:tf.add(P,arcname='cq6_package')
    (CQ/'CQ6_STOPPED_BUNDLE.sha256').write_text(sha(bundle)+'  '+bundle.name+'\n')
    print(f'SEALED_STOPPED_PACKAGE {len(files)} files; {n} parent recipe parameters; readiness refusal verified')

if __name__=='__main__':main()
