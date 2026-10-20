# Top-up truth and unchanged R2a admission

CQ4 and CQ7 assert breathing and accent only. CQ6C encodes their values in the
first two targets and retains `null, null` with
`unknown: ["diaeresis", "subscript"]` for the other two. These are assembled
truth proposals. Their presence does not certify four-head training admission.
The byte-identical 1,572-row v2 overlay retains its original four-head targets;
the old pool retains its original labels, row order and duplicates.

The preregistration freezes the R2a recipe. It does not authorize filling
unread heads with zero, using teacher guesses, or introducing a masked loss.
Actual parent `evidence/r2_manifest.py`, `ManifestPool.__init__`, quarantines
the WHOLE tuple when `unknown` is nonempty. Parent `evidence/r2a_run.py`,
`validate`, rejects overlays with UNKNOWN heads; its pool cardinality check
also rejects quarantine. Thus all 959 CQ6C top-up proposals are presently
unadmitted under the unchanged R2a implementation. Counting them as assembled
breathing/accent labels is distinct from counting them as trainable rows.

No new rule is inferred from the fact that these are capitals. No partial-head
training, zero-fill, label propagation or quarantine bypass is implemented.
Only existing, authorized four-head evidence could complete admission without
changing this policy. Otherwise the coordinator must resolve the scientific
contract explicitly; this package cannot resolve it by inventing labels.

CQ6C is **assembly ready**, because 800/500 is met; it is **not training ready**
and has no admitted production runtime. This distinction avoids reopening the
frozen CQ6 attempt or imposing another quota stop. `--require-ready` checks the
assembly. `--require-training-ready` explicitly refuses production admission.

Physical frozen-extractor coverage, native-source/runtime binding, real-input
A/B dry run, debug training smoke, and protection-runtime integration also
remain unexecuted. W-CAP stays witness only. All 300 selected W-CAP identities
are guarded against fresh final capitals claims; only locked (ii)/(i-b) strata
remain untouched final cohorts under amendment 1a.
