# RUC1: ia_russian after RU1 v1

Prepared offline for the sourcing lead's fresh admission re-check. No reader, limit probe, scoring, or admission update was run. Sol decisions will use letters and crop_ok only; marks remain pending Opus. The admission thresholds are letters ≥90/100 and crop_ok ≥90/100. C1 on the old labels was letters 74/100, crop_ok 97/100.

The RU1 artifact SHA256 is `1fb0a9f5bde4a166fd480ffb414d5e376596b600fd728b6e099b6b1803af2db0`, matching both the requested binding and `ru1_v1_manifest.json`. All 314 unique RU1 ids exist in W1 and every `label_parent` equals its W1 `label`; statuses are 311 ok and 3 hold. Source files were read only. Input hashes are in `build_receipt.json`.

The pool contains **846** W1 rows with source `ia_russian`, primary_class `cyrillic`, and candidate_usable exactly true. The 100 old C1 line ids, all three RU1 hold ids, and the union of every current release-exclusion class are removed. Classes checked: locked_eval, eval_only_dev, locked_eval_ia_wikisource, locked_eval_ib_wikisource, separator_ambiguous, rotated_crop, and n1_locked_eval. No additional length, source, crop_tight_page, or usable_final gate is used.

For each eligible row, the label is exactly `label_ru1_v1` when RU1 status is ok, otherwise exactly the original W1 label. **128 pool labels change**; 289 pool rows have an ok RU1 record (161 of these retain identical text). In this report, “repaired” counts actual text changes. Full pool membership and label provenance are private in `keys/pool.jsonl`.

Draw: Python `random.Random('ruc1:ia_russian:cyrillic').sample(sorted(pool, key=id), 100)`, uniform without replacement. **18 drawn labels change**; 31 drawn rows have an ok RU1 record. Private draw order is `keys/draw.jsonl`.

All 100 bed crops were regenerated through the read-only collector `collect_v3.storage.ensure_crop`, redirecting only the output crop path to this task's fresh cache. The invocation used `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` exclusively. That venv is a symlink to `greek-ocr-toolkit/.venv`; the resolved executable and requested invocation path are recorded in the receipt. The x86_64 interpreter was used only for scanner/tests, never crop regeneration. Each regenerated crop and pack copy matches the corresponding W1 `crop_sha256`. Private custody: `keys/crop_custody.json`.

Packs are outside repositories at:
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/ruc1/`

Contexts c1 and c2 each contain 50 disjoint bed cards plus five controls. Ten lead-approved CAPS1/CAPS1b controls are reused exactly: c057, c009, c013, c026, c046, c041, c029, c072, c035, c066. Their crops, public label/scripts, truth, 7-positive/3-negative mix, and original context allocations are preserved; all receive fresh opaque RUC1 ids and seeded context order. Keys and reports remain here, outside PACK_ROOT; each reader folder contains only cards.jsonl and content-hash PNG copies under crops/. No image links or metadata.

The prompt `prompts/ruc1.md` is byte-identical to the reference `prompts/bsb.md`. Its old-Cyrillic checks, including ъ, apply unchanged. Reader settings are gpt-6.1-sol, medium, network OFF, web search disabled, apps/plugins/multi-agent disabled, workspace-write, approval never, project docs disabled. Launchers retain the HANDOVER budget probes and stop rules. Current weekly usage was not probed because this task prepares packs offline; launchers will probe before and after each reader and refuse to start at ≥78% (HANDOVER hard stop 80%). No credits were spent by a reader run in this task.

Closure uses the explicitly requested CAPS1 adapter, routed to read-only reference source functions, with only bed/path vocabulary, grayscale-original allowance, and disjoint-batch contract substitutions inherited from KR1. Both contexts are clean (55 items each); manifests are beside the reader folders. Evidence: `scan/closure.json`, `runtime_bindings.json`, `launchers.diff`, `public_launcher.diff`, and `adapter_approval.json`. Public launchers dispatch RUC1 to the task's configured private launchers. The runtime includes the reference mandatory rollout scan, answer mapper, and usage ledger; every flag/unreadable remains for lead review under HANDOVER §8.

Launch these separately (prepared only; not executed):

```bash
bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh ruc1 c1
bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh ruc1 c2
```

Validation: 11 tests passed with the HANDOVER x86_64 Python 3.11 scanner interpreter (`test_ruc1.py`). Tests cover RU1 binding/parent identity, complete pool/exclusions, exact substitution and scripts, seeded draw/context order, regenerated crop SHA and PNG custody, unchanged controls/disjoint contexts, clean closure, rejection of deliberate contamination, prompt/launcher settings, fresh ids/input bindings, and synthetic mapper/control behavior with marks ignored for control decisions. Synthetic answers were held in memory and are never reader results. Build refuses to overwrite an existing pack or reuse regeneration cache.

RUC1: done | pool: 846 (repaired labels 128) | cards: 100 (repaired 18) | controls: 10 reused | closure: clean | launch lines: 2 | tests: 11 passed
