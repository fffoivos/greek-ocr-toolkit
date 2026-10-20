# T14b — Two controls for the montage result: reader determinism on single crops, and montages WITHOUT the grey rule (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Vision + Document AI; ADC). No `.git` writes. Cost cap USD 0.50.
Context: T14 (docs/records/harvest/MONTAGE_v1.md, docs/records/harvest/montage_v1/comparisons.jsonl): montages lose no crops and keep confidences, but exact identity with the cached
single-crop reads is only 60–82%; coordinator's recount: even comparing letters+marks only (apostrophe variants unified, edge punctuation stripped) identity is
70% (Vision) / 89% (DocAI) at N=20; one Vision montage read contains a '*' that is the separator rule. Unknown: whether the readers are deterministic at all on
the SAME single crop — if single-vs-single also differs at that rate, the montage gate (97% exact) was wrong and montages cost nothing.
Required:
1. Determinism control: pick 30 of the 100 T14 lines (stratified over the 'identical' outcome in T14: 15 identical, 15 differing at N=20, Vision). Re-read each
   single crop ONCE more with BOTH readers (new calls, bypass the cache deliberately and store under docs/records/harvest/montage_v1/determinism/). Compare the new single
   read with the cached single read: exact NFD identity %, letters+marks identity %, char-kind histogram of the differences. 60 calls.
2. Montage without the rule: rebuild N=20 montages for the same 30 crops with the SAME gaps but NO grey rule (plain paper-white gap), read both readers (4 calls),
   and compare with (a) the cached single read and (b) the new single read from step 1, same metrics. Report whether the '*' artefact disappears.
3. Report `docs/records/harvest/MONTAGE_v1.md` addendum "Controls": a table with rows {single-vs-single, montage(rule)-vs-single, montage(no rule)-vs-single} × readers ×
   {exact, letters+marks}; and a verdict: if montage-vs-single ≈ single-vs-single, montages are equivalent to single reads and the adoption gate becomes
   "no merged/lost and agreement ≥ single-vs-single − 3 points"; state the recommended N (20 unless the data says otherwise). receipt.json updated.
4. Tests (no network) for the no-rule layout and the comparison helper. INVENTORY.
Last line exactly: `T14B: done | single_vs_single_exact_vision: <pct> | single_vs_single_exact_docai: <pct> | montage_norule_vs_single_vision: <pct> | montage_norule_vs_single_docai: <pct> | calls: <n> | tests: <n> passed`.
