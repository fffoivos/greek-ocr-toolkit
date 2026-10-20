# DEL2: approved deletion of collect-v3-data/v2_masked/l1e_sample_r2, retry (gpt-6.1-sol, medium, network OFF)

DEL1 stopped correctly on its rule "no citation waived". Its only hit was its own brief, `docs/records/briefs/DEL1_v2masked_r2.md`, and that
brief is not a data consumer. **Lead ruling:** the deletion paperwork does not count as a citation.

Excluded from the citation scan (exactly these):
- `docs/records/briefs/DEL1_v2masked_r2.md`
- `docs/records/briefs/DEL2_v2masked_r2.md`
- `docs/records/labelfix/spellcheck/R2/receipts/DEL1_v2masked_l1e_sample_r2.json`
- `docs/records/labelfix/spellcheck/R2/receipts/DEL2_*`
- the target folder itself
- the cleanup-plan / routing docs that list this folder AS A DELETION CANDIDATE. Name each such hit and show its line in the receipt; a
  hit whose line does not describe the folder as a deletion candidate is a real citation.

Everything else in DEL1's procedure stands:
- target `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked/l1e_sample_r2` (222 files, 1,985,664 bytes per the DEL1
  inventory; it must be unchanged, or STOP);
- before/after inventories with sha256; sibling invariance; any other citation = STOP.

**Make the broad scan finish**, since DEL1 had to interrupt it:
- `grep -rIl --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=__pycache__`, plus the exclusions above;
- across `~/Projects/greek-ocr-toolkit*` and `~/Projects/collect-v3-data`, skipping files over 50 MB (`find -size -50M`). Count the
  skipped big files in the receipt.

Then delete the target only. Receipt: `docs/records/labelfix/spellcheck/R2/receipts/DEL2_v2masked_l1e_sample_r2.json`.
Last line: `DEL2 READY: deleted <yes|no>; files <n>; bytes <n>; citations <n> (excluded paperwork <n>); siblings unchanged <yes>`.
