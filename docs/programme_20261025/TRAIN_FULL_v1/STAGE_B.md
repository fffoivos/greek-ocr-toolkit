# Stage B — optimizer studies at the adopted batches

**STAGE B FIX READY for a fresh CUDA smoke and focused Astra H1 re-review.**
Prepared offline only; no network, SSH, Slurm, HF, commit or push was performed
by Sol. The full runs wait for B/B2 results. [Commands](../../../out/TRAIN_FULL_v1/COMMANDS.md).

Payload `3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8`,
ID `3c9e5d5f4fb8702e`. [H1 closure, tests, bindings and evidence](STAGE_B_H1_FIX.md). [Machine-readable card](package/study/card.json).
Stage A job3749486 COMPLETED0:0 in44m37s and its adoption are **coordinator-reported
in the 26Oct00:49 brief**, not a new local GPU measurement. Remote planning
requires the actual measured STAGE_A.json, isolation PASS, the exact runtime
hash, and the adopted batch/worker selections. The old local Stage A placeholder
is never accepted as measured evidence.

## Study card and recipe comparison

Goal: optimize nuisance AdamW settings separately for each width, conditional on
its measured batch. Prediction: at least one frozen Halton point may beat the
unscaled S1 control on final pooled dev CER. This is a hypothesis, not a result.
Architecture width is compared through three independent studies; optimizer HPs
are nuisance parameters within each. Batch and short horizon are fixed caveats.

| Parameter | S1 / inherited TRAIN_FULL | Stage B | Change and reason |
|---|---|---|---|
| Architecture/head | compact / nfd | identical; widths1/1.5/2 | Owner's three widths; no architecture implementation edit |
| Batch / accumulation |64 /1 | ×1:256; ×1.5:256; ×2:64 /1 | Adopted Stage A throughput choices |
| AdamW peak LR |1e-4 |16 exact log-Halton points in[5e-5,5e-3], plus1e-4 control | Nuisance search; **no batch scaling** |
| Beta1 / beta2 |.9 /.999 |beta1 one-minus-log[.8,.98]; beta2 .999 | New `--beta1`, default .9; explicit betas identical to S1 at default |
| Weight decay |.05 |log[.001,.3]; control .05 | Nuisance search |
| Epsilon / norm-bias decay / clip |1e-8 /zero /5 |unchanged | S1 update math |
| Data |audited005,793,227 real train +half synthetic |unchanged pools, membership, labels and byte hashes | Reuse in place; no release rebuild |
| Mixture / parliament cap |synthetic .5; real parliament≤.25 |unchanged fractions and largest-remainder assembly | Unchanged S1 synthetic source, recipe SHA2f228950e9a508b5e130e82ce5b89de2b911be4a23872c3acc7f53e83c59dce7 |
| Model / data seed |0 /20261015 |unchanged in51trial study | B2 changes model seed only to0/1/2; data seed remains fixed |
| Furniture fallback / codec / images |furniture /v2.1 /48px strips |unchanged | Admitted numeric lines retained; width128 buckets and packed tails unchanged |
| Workers / CPU native threads |6 /four keys=1 |unchanged;24CPUs/GPU | Adopted Stage A worker choice; no DDP |
| Epoch rows / epochs |1,586,454 /8 full real passes |1,269,164 /1 shortened draw epoch |10% of12,691,632 full drawn lines, rounded up to an exact real+synthetic pair |
| OneCycle |pct_start .075, cycle_momentum=False |same shape over each trial's actual total updates | Short horizon deliberately reinitializes schedule; no mid-cycle truncation |
| Patience |disabled in TRAIN_FULL |disabled | Fixed study length; no stopping or parameter changes from metrics |
| Loss evaluation |four panels every50kdraws +end |**dev only**, every50kactual draws +end | No test instrument is opened |
| Full CER / checkpoint |prior production cadence |final dev CER only; final archive +rolling continuation | Objective is final, never retrospectively best CER |
| Epoch diagnostic |S1 shared validation |seal04 dev437rows, at the sole epoch end | Requested dev-only scope; in-memory split=val view preserves bytes/labels; original unrelated validation pool is not opened |
| Runtime / resume / time reads |deterministic S1 CUDA profile, requeue, standard-time override |unchanged profile and continuation; four independent lanes | Separate claims/state/logs; no cancelled ×2 state reused |

The16points are copied unchanged from [lr_trials.jsonl](hp_study1/lr_trials.jsonl)
and reproduced by the requested skill's `quasi_random.py --trials 16 --seed20261025`.
The skill's analyzer/generator are included unchanged under package/study with
[source hashes](package/study/SOURCE.json). LR range is **not widened**: retain
the expressly requested points; report high/low boundary evidence, and treat an
extension as a new study. No untested linear/sqrt batch scaling is assumed.

## Horizons, metric and logs

| Width | Batch / workers | Draws/trial | Optimizer updates | Loss points | Final CER points |
|---|---|---:|---:|---:|---:|
|1|256 /6|1,269,164|4,958|26|1|
|1.5|256 /6|1,269,164|4,958|26|1|
|2|64 /6|1,269,164|19,831|26|1|

The true full target is16×793,227=12,691,632 mixed draws. Ten percent is
1,269,163.2; round up to1,269,164 to retain exactly634,582real and634,582synthetic
draws. This is0.8of a real pass, not an8-epoch trial. Frozen assembly takes a
deterministic subset/permutation of every real component according to its same
fractions. Final packed batch has172rows at256 or44rows at64; the sampler
shuffles that partial batch, so `ceil(50000/batch)` repeated is **not** the exact
step list. Each trial precomputes and seals LOSS_CADENCE.json using the actual
assembler and sampler: thresholds50k…1.25M plus final,26distinct points. Actual
step/drawn-line counts are checked during training.

Both dev instruments are complete: **seal04 dev437 +harvest dev16,350 =16,787
rows** at every point. Same training fp32 CPU CTC loss, blank0, zero_infinity=True,
target-normalized per-example loss, dataset sample-weighted mean; eval mode,
no decoding for loss points, RNG and mode restored in finally. The unchanged
S1 scorer gives final CER separately per panel. Primary `val_error` is the
**sum of literal NFD-atom Levenshtein edits divided by sum of reference NFD atoms**
over both panels, not an average of their CER rates. Other original scorer modes
remain reported. No test loading, decoding or selection occurs.

Each trial has immutable CLAIM.json/RUN_BINDING.json, rolling segment.pt,
allocation receipts and immutable yield archives, per-point loss JSON,
append-only loss_eval.jsonl, final dev predictions/eval, train_log.csv and
COMPLETE.json. Train loss at every loss point is in both point and journal;
epoch aggregate is in train_log.csv. The analyzer input records final objective,
separate dev metrics, train loss, seed, max_steps and HPs. It omits best_step:
there is only one CER measurement, so the analyzer's retrospective checkpoint
position diagnostic cannot identify a best checkpoint. Inspect loss curves for
length/instability evidence instead. Failed/diverged trials have null objective
and explicit failure receipts, never an invented bad CER. Infrastructure failures
need log/accounting investigation and a same-binding retry before interpretation.

## Continuation, smoke and data reuse

All update/model/sampler/scorer modules are byte-exact S1 except the declared
checkpoint hook and beta1 parser/validation/explicit AdamW betas. verify.py undoes
exactly those trainer edits to prove the original trainer SHA. Every data-producing
module, registry, importer, codec, template and environment still matches the
prepared005 parent. Only the original runtime SHA
`21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`
may inherit its parent-package binding. Pool bytes are rehashed when consumed.
No audit, rebind, factory or data relocation is repeated. Native nonletter fallback
is unchanged. No old scientific smoke/review/training checkpoint is inherited.

Four independent srun steps/node use one visible GPU,24disjoint CPUs and6workers
each. Kernel physical-host identity, physical GPU UUID, CPU affinity and start/end
intervals attest that overlapping trials never share a GPU UUID globally or CPUs
on the same physical host. CPU numbers may repeat on distinct hosts. This proves resource separation; memory,
filesystem and interconnect contention remain measured node conditions. Claims
and fcntl output locks refuse duplicate concurrent owners or changed configs.
Completed lanes validate their bound artifacts and skip on node requeue. An
unfinished lane resumes model, optimizer, scheduler, RNG and exact draw/iterator
cursor. Only failed/incomplete work is replayed from the latest durable state.
A hard-killed allocation intent keeps its original bytes. On a new Slurm allocation, a separate RECOVERED witness bounds its end before the new node controller starts any lanes; GPU UUID and physical host were attested before training. Recovery preserves the original host with its prior-file SHA and records the next host separately; it never substitutes the new host for the original. Same-allocation unfinished claims refuse recovery. No dependencies on purged jobs exist: the13groups are independent.

CUDA smoke: one node/four lanes, ×1control and ×1forced-requeue twin at batch256,
plus ×1.5/b256 and ×2/b64,40updates each. Loss points8/16/24/32/40 use **all dev
rows**, with final dev CER. The twin yields at12, archives that exact state, and
the wrapper calls real `scontrol requeue`. Readout requires the same job ID with
increased restart count, BIT_IDENTICAL full continuation state, equal loss/CER,
all five journal points and hardware isolation PASS. It measures per-width full
dev loss and final CER cost. Local tests use a stochastic toy model with real S1
updates/CTC; they additionally SIGKILL/restart each width configuration at a loss
point and poison test paths. They do not certify CUDA arithmetic.

## Recorded execution and H1 status (26 October)

The previous payload `f3944e2a242e83de` completed CUDA smoke job **3749768**,
COMPLETED0:0 in241s: **BIT_IDENTICAL**, mock=false, no test instruments opened,
five loss points across an actual forced requeue. This is recorded evidence in
[out/receipts_stage_b/SMOKE_IDENTITY.json](../../../out/TRAIN_FULL_v1/receipts_stage_b/SMOKE_IDENTITY.json),
not a smoke of the new payload. [Astra review](ASTRA_STAGE_B_REVIEW.md) then held
launch on H1: host-local CPU numbers were compared globally. H1 is repaired and
**140 local tests pass**; review of the repair remains pending. The new allocation
recording requires a fresh smoke binding. Do not reuse old smoke/review/claims.
Audit, prepared005 pools/runtime, Stage A, all51trial settings and the scientific
recipe remain unchanged. Fresh attempt: `full-v1-009-stage-b-h1`.

The prior smoke gives the following measured-eval projections, which the new
smoke will refresh (these are not completed-study costs):

| Width | B17 GPU-h | B2 three seeds GPU-h | Eval / training |
|---|---:|---:|---:|
|×1|16.2364|2.8652|15.34%|
|×1.5|18.5787|3.2786|14.19%|
|×2|21.8420|3.8545|12.91%|
|Total|**56.6571**|**9.9983**|all below25%|

## Budget and decision

These projections use the coordinator's measured Stage A rates; remote smoke
recomputes the budget from the actual report and measured complete dev-eval time.

| Width | Lines/s |17trial training GPU-h |3seed training GPU-h |Trial training minutes |
|---|---:|---:|---:|---:|
|1|425.8|14.08|2.48|49.68|
|1.5|368.4|16.27|2.87|57.42|
|2|309.8|19.35|3.41|68.28|
|Total|—|**49.69**|**8.77**|—|

Before overhead: B+B2≈58.46GPU-h; future C≈29.23GPU-h. One concurrent wave uses
13nodes,12groups of4GPUs and1group of3,51GPUs total. Two-hour limits request
**102GPU-h** for B; B2groups4/4/1 request18GPU-h;80-minute4GPU smoke requests
5.33GPU-h. Exclusive nodes may account as four GPUs even for final partial groups:
conservatively allow104/24GPU-h for B/B2 and use actual ReqTRES accounting. These
are reservations, not forecasts of runtime or permission to exceed the350requested
GPU-h cap. Coordinator reconciled the ledger to184.41GPU-h used /165.59remaining at the01:27brief; refresh all owner's jobs for intervening work. No C reservation is
included in the B submission.

Per trial projected eval seconds =26×maximum measured complete loss-eval seconds
+one measured final dev CER pass. The latter includes loss/scoring/prediction
write. Smoke readout reports the ratio to Stage A training time and options if
it exceeds25%: budget the unchanged full coverage, explicitly change cadence
with a new binding/decision, or optimize and requalify the identical evaluator.
**No subsampling occurs.** Startup, recurring checkpoint writes, data rereads,
legacy final437-row epoch diagnostic, storage contention and requeues add cost;
the40-update smoke cannot fully forecast them. Trials that reach the2h warning
yield durably and requeue within the1day partition cap; extra reservations must
stay within the refreshed wave budget.

Run the included analyzer separately per width with `--objective val_error` and
**omit --scientific**. Inspect infeasible fraction, boundaries, density and curves.
Then B2creates fresh seed0/1/2runs of each width's best final dev point, with the
same trial horizon/batch. Adopt only if **control(seed0)CER−best-study(seed0)CER >
max(best-rerun CER)−min(best-rerun CER)**. Report all seeds and mean, edge positions,
and unmeasured control/study variance. No improvement beyond spread means retain
the control. Short OneCycle settings need confirmation at the full horizon.
Stage C is a separate package/review after these results, with all four complete
instruments and50k-drawn-line loss cadence. The prior single-width full-run command
is historical and must not be used.

Method: requested [nn-tuning skill](/Users/foivoskarounos-zamparloukos/.claude/skills/nn-tuning/SKILL.md),
dependency order4 and references/tuning_loop.md §§5–8,10. These prescribe
batch-before-optimizer tuning, quasi-random exploration, diagnostic checks and
retrain-variance evidence. Owner's frozen3HP/17trial design takes precedence over
the skill's general tuning-budget heuristic. The GPU-time projection and max-minus-min
spread rule are explicitly limited evidence, not guarantees of optimality.

STAGE B FIX READY (fresh-binding CUDA smoke and focused Astra H1 re-review pending coordinator execution).
