# L1H — Complete-gate HOLD attribution (stopped; reason tables incomplete)

**Status: incomplete, stopped at the login-node budget.** The requested exact reason/sole-reason and top-ten reason-set tables were not produced. No gate or detector was changed, and no job was submitted.

The live release manifests confirm **ENSEMBLE_AB holds 112,605 / 124,669 lines (90.3%) and keeps 12,064 (9.7%)**. PRESENCE holds 118,364 (94.9%) and keeps 6,305; FULL holds 118,726 (95.2%) and keeps 5,943. These are manifest counts, not a successful independent recount of all three overlays.

## Stop condition

The pilot timed JSON decoding on 1,024 rows per mode and projected 187.8 seconds for all three overlays. The one-process census added hashing, source joins, deduplication and reason-set counters. Its last forecast was **270.2 seconds (4.50 minutes)** at FULL row **8,192**, above the conservative **240-second limit chosen for this run**. It exited with code 124 at that forecast; the 240-second alarm was not reached. The user specified a few minutes of one core, not an exact numerical cap.

The log shows AB through 120,000 rows, then PRESENCE through 120,000 rows, then the FULL forecast stop. The script only emits a completed census after all modes and invariants pass, so partial in-memory AB/PRESENCE counters were not returned. There are no usable full-population reason counts in the returned evidence. No second aggregation pass was attempted after the stop.

## Verified release coverage by wave

| Wave | Lines | PRESENCE held / kept | FULL held / kept | AB held / kept | AB held % |
| --- | --- | --- | --- | --- | --- |
| round1 | 43,869 | 40,662 / 3,207 | 40,847 / 3,022 | 37,899 / 5,970 | 86.4% |
| round2 | 17,026 | 15,459 / 1,567 | 15,549 / 1,477 | 13,983 / 3,043 | 82.1% |
| parliament | 27,224 | 27,068 / 156 | 27,073 / 151 | 26,896 / 328 | 98.8% |
| vouli | 23,088 | 22,585 / 503 | 22,606 / 482 | 22,211 / 877 | 96.2% |
| mixed | 13,227 | 12,388 / 839 | 12,447 / 780 | 11,425 / 1,802 | 86.4% |
| openarchives | 235 | 202 / 33 | 204 / 31 | 191 / 44 | 81.3% |
| ALL | 124,669 | 118,364 / 6,305 | 118,726 / 5,943 | 112,605 / 12,064 | 90.3% |

## Table 1 — Requested slot and sole-reason line counts

**Unavailable.** The table below records the missing results explicitly; “Not computed” is not zero. Once the coordinator runs the prepared script in a small allocation, the report formatter will produce one exact-detail table per mode with six wave columns, each containing `slots / sole-reason lines`, and separate ALL totals.

| Mode | Wave | Held lines (manifest) | Slots per exact reason | Lines held for that exact reason alone |
| --- | --- | --- | --- | --- |
| PRESENCE | round1 | 40,662 | Not computed | Not computed |
| PRESENCE | round2 | 15,459 | Not computed | Not computed |
| PRESENCE | parliament | 27,068 | Not computed | Not computed |
| PRESENCE | vouli | 22,585 | Not computed | Not computed |
| PRESENCE | mixed | 12,388 | Not computed | Not computed |
| PRESENCE | openarchives | 202 | Not computed | Not computed |
| FULL | round1 | 40,847 | Not computed | Not computed |
| FULL | round2 | 15,549 | Not computed | Not computed |
| FULL | parliament | 27,073 | Not computed | Not computed |
| FULL | vouli | 22,606 | Not computed | Not computed |
| FULL | mixed | 12,447 | Not computed | Not computed |
| FULL | openarchives | 204 | Not computed | Not computed |
| ENSEMBLE_AB | round1 | 37,899 | Not computed | Not computed |
| ENSEMBLE_AB | round2 | 13,983 | Not computed | Not computed |
| ENSEMBLE_AB | parliament | 26,896 | Not computed | Not computed |
| ENSEMBLE_AB | vouli | 22,211 | Not computed | Not computed |
| ENSEMBLE_AB | mixed | 11,425 | Not computed | Not computed |
| ENSEMBLE_AB | openarchives | 191 | Not computed | Not computed |

## Table 2 — Requested top-ten line reason sets

**Unavailable.** No population reason-set rankings can be inferred from the schema pilot or release-status totals.

| Mode | Wave | Top 10 exact reason sets and line counts |
| --- | --- | --- |
| PRESENCE | round1 | Not computed — stopped before full census output |
| PRESENCE | round2 | Not computed — stopped before full census output |
| PRESENCE | parliament | Not computed — stopped before full census output |
| PRESENCE | vouli | Not computed — stopped before full census output |
| PRESENCE | mixed | Not computed — stopped before full census output |
| PRESENCE | openarchives | Not computed — stopped before full census output |
| FULL | round1 | Not computed — stopped before full census output |
| FULL | round2 | Not computed — stopped before full census output |
| FULL | parliament | Not computed — stopped before full census output |
| FULL | vouli | Not computed — stopped before full census output |
| FULL | mixed | Not computed — stopped before full census output |
| FULL | openarchives | Not computed — stopped before full census output |
| ENSEMBLE_AB | round1 | Not computed — stopped before full census output |
| ENSEMBLE_AB | round2 | Not computed — stopped before full census output |
| ENSEMBLE_AB | parliament | Not computed — stopped before full census output |
| ENSEMBLE_AB | vouli | Not computed — stopped before full census output |
| ENSEMBLE_AB | mixed | Not computed — stopped before full census output |
| ENSEMBLE_AB | openarchives | Not computed — stopped before full census output |

## Pilot and schema evidence

The overlay stores a broad `hold_slots[].reason` and a more specific `hold_slots[].detail`. The first sampled line records `detector_clipped_top` and a mode-specific disagreement detail, while its broad reason calls clipping `localisation_unknown`. The analysis must use detailed strings for the main attribution, retaining the broad mapping as a separate view.

| Mode | Pilot rows | Decode s | Projected complete decode s | Pilot broad reason-entry counts |
| --- | --- | --- | --- | --- |
| PRESENCE | 1024 | 0.474 | 57.7 | localisation_unknown=7,963; kind_disagreement=1,716; edit_guard=751; k1_flag=144 |
| FULL | 1024 | 0.462 | 56.2 | localisation_unknown=7,963; kind_disagreement=1,884; edit_guard=751; k1_flag=144 |
| ENSEMBLE_AB | 1024 | 0.607 | 73.8 | localisation_unknown=8,065; edit_guard=751; k1_flag=144; ensemble_disagreement=129 |

These pilot counts describe only the first 1,024 rows per file and are neither joined to wave nor a random sample. They do not establish the top reasons or sole-reason line counts for the complete gate.

## Sample IDs

Schema-only sample ID:

- `66112e132fd96ac8e30e5328-p000016-l0005`

The pilot returned three mode projections for this one unique line, including gate-decision evidence and the first three HOLD entries. The projections are in [samples.jsonl](L1H_evidence/samples.jsonl), with the complete ID list in [sample_ids.txt](L1H_evidence/sample_ids.txt). **No crops were transferred (0 images)**. This line is a schema witness, not an adjudicated or representative HOLD sample. The transfer stayed below 200 sampled records and 200 images; no full overlays or source manifest were copied to the Mac.

## Prepared method and checks

The prepared aggregator joins overlay `line_id` to source `id`/`wave` on Clariden, with one process and no scientific-library threads. It counts distinct `(line_id, start, letter, detail)` slot/reason keys. A line is sole-reason only when the union of all its detailed HOLD reasons is exactly that one reason. Exact sorted reason sets partition held lines. Top tens rank by descending count, then lexical set order.

The intended completed run checks compressed overlay SHA-256 against every manifest, source SHA-256, unique identical mode populations, every source/wave join, every wave/status total, HOLD/status consistency, and partition/deduplication invariants. **Those full-run checks cannot be claimed as completed from the returned stop receipt.** The pilot did read the current manifests and the gate/recomposition source snapshots; both source hashes match the policy binding recorded in those manifests.

The completed-run formatter preserves every exact reason string, including edit-guard offsets, and exports supplementary broad-reason and family views (`K1:*`, `edit_guard:*`, reader uncertainty prefixes). It does not infer neighbour ink or gate correctness. Line-level guard failures can be repeated across slots, so slot counts are not independent physical-defect counts.

Part (2) remains dropped: no masking experiment, neighbour-ink classification, detector-blob scan, detector rerun, quality assessment or gate recommendation was performed. The requested `DIRECTION_DECISION_20261017.md` reference was absent from this checkout and the two explicit Clariden documentation paths checked; no unrelated verification worktree was accessed.

## Data identity

- Release root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/output_3679545/recomposition/release`.
- Mode overlays: `overlay_presence.jsonl.gz`, `overlay_full.jsonl.gz`, `overlay_ensemble_ab.jsonl.gz`; pre-SF4 job 3679545.
- Wave join source intended by the prepared script: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/import_real_v2_train.jsonl` (same source identity as the locally symlinked manifest).
- Source SHA-256 **recorded in the manifests**: `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`.
- Release policy SHA-256: `965f3c5575ae8d385b2128919ba4e181b9992a3f5edaacbb6982f1789851a6b7`.

| Mode | Overlay SHA-256 recorded in live manifest |
| --- | --- |
| PRESENCE | `f43411aacbe6fc7d2a56eb3494b5fe9129bc611c4d647c356cb568bfb26196db` |
| FULL | `c4e9c357ba602fd262138f18bcc4dae2c81004e73dd6c70bcc57b5cfd773cbcf` |
| ENSEMBLE_AB | `a7006746e05eaee623c9b180950752b6144d4646518ed061671b81b4bd1e335d` |

## Coordinator handoff

The next step requires the coordinator’s small allocation under the user’s stop-and-report rule. [aggregate.py](L1H_evidence/aggregate.py) is ready to run there: it retains the 240-second forecast/alarm on a login node and removes that login limit only when `SLURM_JOB_ID` is present. It has not been launched in an allocation. Its output should replace `L1H_evidence/aggregation.json`; then run `build_report.py` locally to produce the requested full tables and compact CSVs. No submission command was executed.

The exact script used for the stopped attempt is preserved separately as [aggregate_login_attempt.py](L1H_evidence/aggregate_login_attempt.py). Local work was limited to report/evidence files; `.git`, gates, detectors and the other verification worktrees were not modified.

## Evidence index

- [Stop receipt](L1H_evidence/aggregation.json) and [execution log](L1H_evidence/aggregation_ssh.log).
- [Live manifest projections](L1H_evidence/release_manifests.json), [coverage CSV](L1H_evidence/status_by_wave.csv), and [explicit pending-table CSV](L1H_evidence/pending_tables.csv).
- [Schema/timing pilot](L1H_evidence/schema_probe.json), [pilot script](L1H_evidence/probe.py), and [pilot SSH log](L1H_evidence/probe_ssh.log).
- SHA-bound [gate source readback](L1H_evidence/release_gate_source_readback.py) and [recomposition source readback](L1H_evidence/l1r_recompose_source_readback.py), evidence only.
- [Validation and scope receipt](L1H_evidence/validation.json), [prepared aggregator](L1H_evidence/aggregate.py), and [completed-run report formatter](L1H_evidence/build_report.py).

L1H RESULT: AB held 90.3%: top reasons NOT COMPUTED (login-budget stop); per-wave sole-reason lines NOT COMPUTED (all six waves); PRESENCE/FULL held 94.9% / 95.2%, kept 6,305 / 5,943; reason census INCOMPLETE.
