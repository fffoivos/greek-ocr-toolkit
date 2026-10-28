# Stage C memory request correction — historical memory-only delta

**27 Oct correction:** this note describes an older seal. Its selection claim
was incorrect: those Stage C seals loaded legacy validation (13,088 rows), not
seal04 dev. [Current H1 fix](STAGE_C_SELECTION_FIX.md) installs the Stage B
seal04-dev437 view and requires fresh CUDA smoke. The old memory-only carry
helper does not apply to this behavior change. Owner 82-GPU-h authority stands.


The new payload is `515b7d86f5f5758b` (SHA256
`515b7d86f5f5758be544e401ae06720e67db8b311e38ef6bcff22c649db5bf8d`).
The **only payload-file change** against the running smoke's `8b228d6e138151f4`
is this added line in `stage_c.sbatch`:

```diff
 #SBATCH --cpus-per-task=24
+#SBATCH --mem=110G
 #SBATCH --requeue
```

The new PAYLOAD hashes that shell. Every scientific/runtime/driver/test file is
byte-identical. The old seal and shell are retained under
`evidence/STAGE_C_PRE_MEMORY_PAYLOAD.json` and `STAGE_C_PRE_MEMORY.sbatch`.
Stage B, prepared005, the running smoke deployment, its PLANs, claims, outputs
and logs are untouched. No remote action is performed by Sol.

## Resource scope and remaining measurement

The coordinator's live observation is `cpu=24,mem=450G,node=1,gres/gpu=1` for
3756429, with partition default memory unlimited. Omitting `--mem` therefore
prevents other jobs sharing that node's memory allocation. Explicit **110G/job**
allows four 1-GPU/24-CPU jobs within the reported 450G node capacity (440G total,
10G unrequested); three full runs request 330G. This enables scheduling together;
Slurm can still place them on separate nodes. No guaranteed node-hour saving or
shared-node throughput measurement is claimed. GPU HBM remains a separate limit.

**110G is a proposed resource share, not a measured host-memory requirement.**
No completed Stage C MaxRSS/cgroup-peak capture was copied locally at preparation.
The frozen adapter loads all prepared pools into the parent Python process;
the training loader uses six persistent workers with prefetch factor four (24 prefetched batches).
Therefore a crop/prefetch estimate alone cannot justify the request. Retain
per-step MaxRSS for all six actual smoke lanes and their requeues. The helper
reports each peak, 110G headroom and its raw capture line; missing/over-limit
measurements fail. Check that the site's single-task memory accounting includes
all six child workers; sampled MaxRSS may miss peaks and must not be summed
blindly across tasks or mistaken for a cgroup aggregate. Inspect any available
job/cgroup memory peak and OOM diagnostics as well. Full-data pool startup is
part of even the tiny-horizon smoke, making its RSS informative for C.

After that readback, the coordinator/Astra can justify the share against measured
RSS and headroom. If the cgroup/children semantics are unresolved or headroom is
insufficient, run a bounded 110G resource qualification in a fresh attempt; do
not claim 110G is capacity-qualified by the old unlimited-memory smoke. If an
old smoke job is killed/OOM/incomplete, its identity cannot be carried forward.
The exact fresh-smoke fallback commands are in COMMANDS.md.

## Early stopping and retention: no training change needed

`stage_c.execute()` sets `trainer.PATIENCE = args.epochs + 1` before `train()`.
The smoke's two epochs explain the printed **patience 3**. Full configs have
eight epochs and **patience 9**. In `vendor/train/train.py`, `bad_epochs` is
incremented only once per completed epoch and reset on improvement. It cannot
reach nine within eight epochs; a resume restores the saved count rather than
adding an extra epoch decision. The resume shortcut checks that same threshold.
Thus the inherited generic log mentions early stop, but it cannot shorten C.

`selection_metric=val_cer` and `transfer_mix=null` feed only `val_loader`.
**Correction:** at this historical seal, `run.install()` left that loader on the
legacy S1 validation mixture (13,088 rows); it was not the seal04-dev437 view.
The current H1 package corrects it to that exact Stage B view with matching
provenance, retaining all four reporting pools and full-pass checks. The `best.pt` comparison receives `val_res['cer']` from that loader.
Harvest/seal04 test loss and CER run through `full_hook`'s reporting path, which
does not return a selection value to the trainer and restores RNG/model mode.
Harvest dev is reported separately; it also does not replace this inherited
selection metric. No test metric stops, selects or changes training.

`last.pt` is written every epoch irrespective of improvement. The final
`segment.pt` must have the exact total step/draw position before COMPLETE is
written. `full_hook.checkpoint_eval()` archives the full state at all four
configured points without a best-metric condition or pruning. Thus 25/50/75/100%
CER checkpoints and the final/last states remain, regardless of metric trends.
New external regression tests run the real frozen trainer/CTC/optimizer with a
tiny stochastic model for eight successively worsening dev epochs at all three
width settings, assert the full horizon, best epoch 1, seven bad epochs, last
state and all four archives, with extreme test references. The existing suite
also checks test-reference changes leave training state identical.

## Smoke decision and authenticated reuse

**No repeated CUDA TERM/identity smoke is required for this memory-only diff.**
Finish the original smoke on its immutable old deployment; do not modify or
rebind it. Its real TERM/requeue/checkpoint identity evidence remains valid for
the identical training/evaluation/controller code. All six jobs must actually
complete and pass the old sealed readout before that statement is an outcome.
Fresh full PLAN/configs must bind the new payload; an old full PLAN is superseded.
Runtime/data/smoke trajectories are unchanged; claims are never overwritten.

`memory_fix/carry_smoke.py` lives **outside** the seal. It authenticates both
complete payloads against the exact known SHA256s, checks that the only changed
file is the shell and the only shell change is the exact 110G insertion. It
checks the new full PLAN with the new sealed `checked()` and invokes the old
sealed `smoke-readout` afresh, writing its result into the new attempt only.
That readout still requires all real CUDA state/loss/CER identity, actual Slurm
requeue, measured allocation ends and unchanged global GPU/same-host CPU checks.
It requires identical runtime SHA, all six measured lane RSS records and a
SHA-bound capture. It leaves the original report's payload identity intact in
`ORIGINAL_SMOKE_IDENTITY.json`. A separate `SMOKE_COMPATIBLE.json` names the new
payload, original payload/report/PLAN, exact delta, RSS limitations, helper SHA
and new full PLAN. This derived report satisfies the unchanged submission gate;
it is explicitly carried evidence, not a claim of a new CUDA run under 110G.

Focused Astra review must include this external helper and its tests, sole-line
payload diff, actual old smoke readout, RSS/child-memory evidence, fresh full
PLAN and refreshed forecast. The final Astra receipt must bind the derived
report SHA and new payload/full PLAN. Owner spending renewal recorded at 19:09
remains recorded; the final full-launch go is the coordinator/owner's action.
