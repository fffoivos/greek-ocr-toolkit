# Evaluation contract

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
python -B evaluate.py --truth data/wcap_truth.jsonl \
  --predictions predictions.jsonl --lead-review lead_review.json \
  --lqb lqb_ledger.jsonl --guard data/lqb_guard.jsonl --out evaluation.json
```
