# REG2: register the mirrored_showthrough exclusion class and tag the ledger (gpt-6.1-sol, medium, network OFF, mechanical)

Write only under `docs/records/harvest/collect_v3/release_exclusions/` and `docs/records/harvest/collect_v3/` (ledger files). The live W2 Gazette run imports `collect_v3/`: never touch it.

## Coordinator ruling
- Register exclusion class **`mirrored_showthrough`** with the **1 visually confirmed id**: `lekythos--dcfa99599048d352--s000-l0144`.
  - Evidence: sol/recut-v1 ea56555a, `docs/records/harvest/recut_v1/w1_masked/mirror/MIR1.md` (show-through: reversed verso ink on the last page of the issue).
- Rule text: "row-level; ids added only on visual confirmation from card checks; no automatic screen (the MIR1 signal had 1/10 precision)".
- Add "show-through / reversed verso ink" to the tagged label-fault list in `WEAK_CATEGORY_LEDGER.md` (+ `weak_ledger/ledger.json`) under the affected categories, with the MIR1 path.

## Do
1. Write `release_exclusions/w1_mirrored_showthrough_ids.txt` (1 id), and add the class entry to `release_exclusions.json`: file, n, sha256, owner, rule, provenance.
   - Check overlap with `release_admissions/w1_masked_1d.jsonl` per arm and report it. If the id is in arm wave-1d, **STOP and report**: wave 1d is preregistered.
2. Update the ledger files as above.
3. Tests: id existence in W1 features (read-only), JSON validity, and the overlap result.

The last line must be exactly:
`REG2: done | mirrored_showthrough: 1 id | wave-1d overlap: <0|STOP> | release_exclusions sha: <sha> | ledger tagged`
