# SR-G3 full-stratum grave/acute pass

Built offline from all 100 C1 `nlg__poly1900` cards. Only exact SR-G1 geometry is admitted. The private key records literal token, accent anchor, label accent, punctuation, source/card/word identities, geometry and SR-G1 overlap. Word indices are 1-based; anchor indices are 0-based, as in SR-G1.

Public packs are `PACK_ROOT/grave_full/p1c1/` through `p1c4/`; sibling `MANIFEST.p1c*.json` files bind their contents. Each folder contains only `items.jsonl` and `img/`. Pass 1 has at most 90 bed items plus ceil(n/9) controls per context. Controls use original copied pixels, fresh IDs, and a visually checked pool from Lekythos/Kosmopolis only. Verification details and the viewed sheet remain private in `keys/CONTROL_VERIFICATION.json` and `keys/control_candidates.png`.

Selection examines the last accent-bearing vowel after NFD. It must have acute or grave and no later vowel, except one adjacent second diphthong member without diaeresis (`αι ει οι υι αυ ευ ηυ ου`). Circumflex on the last accented vowel is excluded. This is an explicit orthographic final-syllable rule, with no length filter. Hyphen fragments are excluded. The receipt distinguishes these exclusions from geometry failures and lists every dropped candidate.

All commands use:

```sh
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
/usr/bin/arch -x86_64 "$PY" -B docs/records/harvest/sol_reading/grave_full/tools/build_full.py
/usr/bin/arch -x86_64 "$PY" -B docs/records/harvest/sol_reading/grave_full/tools/test_full.py
```

After readers supply `docs/records/harvest/sol_reading/answers/grave_full/p1c1.jsonl`, etc.:

```sh
/usr/bin/arch -x86_64 "$PY" -B docs/records/harvest/sol_reading/grave_full/tools/flag_full.py --build-reread
```

Answers use exactly `item_id, accent, confidence, note` in public item order. Allowed accents: acute, grave, circumflex, none, unreadable; confidence: high or low; note: string. Duplicate fields, extra/missing answers, unexpected context files, invalid values and ordering errors are rejected using the SR-G2 validator. Missing answers are never replaced with labels. PASS1.json and PASS1.md report controls, all flag types, bed-only shares and G1 overlap agreement. More than one control error flags a context, without discarding its bed flags.

Rereads include every flag, fresh IDs and seeded order `sol-grave-full:p2`. A single pack is `p2/`; if split, packs are `p2c1/`, etc. Each reread context has at most 90 total items, including ceil(n/9) controls (at least two). Verified controls absent from the contributing pass-1 contexts are preferred; limited circumflex/none pools can require reuse. Only the two available accent classes fit when exactly two controls are requested. Source/control mappings stay private in `keys/p2_key.json` and `keys/P2_BUILD_RECEIPT.json`.

After readers supply `answers/grave_full/p2.jsonl` or `p2c*.jsonl`:

```sh
/usr/bin/arch -x86_64 "$PY" -B docs/records/harvest/sol_reading/grave_full/tools/confirm_full.py
```

This writes FLAGS.md, private six-column review sheets (30 flags maximum each), and LEAD_EYE.template.json. Copy the template to `grave_full/LEAD_EYE.json` and fill every `printed: null` with acute, grave, circumflex, none or unreadable. The entry IDs are the original pass-1 IDs shown on the sheets.

```sh
/usr/bin/arch -x86_64 "$PY" -B docs/records/harvest/sol_reading/grave_full/tools/confirm_full.py --final docs/records/harvest/sol_reading/grave_full/LEAD_EYE.json
```

FINAL.md uses the lead on flagged items and labels elsewhere, explicitly assuming unflagged items match the label. The grave-to-acute error direction is printed grave / label acute. Its item denominator is all admitted bed items, its card denominator all 100 C1 cards, and the C1 comparison is 9/100 cards. Pass agreement and p2 accuracy cover flagged bed items only. Unreadable remains a distinct category. No FINAL.md is created without a complete valid lead file.

At initial build, real pass reports are pending; no reader answers or lead decisions have been invented. `keys/synthetic/` contains a separately labelled end-to-end test run, reports, reread packs, sheets and lead fixtures; these are test observations only. The tools can be rerun idempotently against unchanged inputs. If the number of reread contexts changes, old context files must be removed from the authorized grave_full tree before supplying answers, so stale answer contexts are rejected.
