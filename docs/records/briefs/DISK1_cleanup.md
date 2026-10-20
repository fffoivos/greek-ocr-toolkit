# DISK1: free disk space, regenerable copies only (gpt-6.1-sol, medium, network OFF; no .git writes)

The coordinator approved deleting regenerable copies (the Mac has 16 GB free). **Scope:** this worktree
`~/Projects/greek-ocr-toolkit-secondary` and this session's scratchpad
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/`. Nothing else.

**NEVER delete:**
- anything under `sol_packs/ru2t/`: a reading is running now;
- answers, keys, receipts, manifests, truth files, decisions, label versions (`*.jsonl` label/decision files), reports, briefs, code
  or tests;
- any file a receipt or manifest cites by path or sha, unless an identical-sha copy stays at a cited location;
- tracked git files.

**Delete candidates (regenerable):**
- crop copies inside reader packs (`sol_packs/*/ctx*/r*/crops|img/`) for FINISHED readings, but only where the source crop exists
  at its recorded collector or cache path with the same sha;
- `zoom/` folders in packs;
- contact sheets and montage PNGs in the scratchpad (`*_review/`, `n1_ctrl_sheets/`): keep their `sheets_index.json`;
- the regenerated crop caches (`n1_cache/`, `ru1_cache/`): crops reproducible byte-exactly with `ensure_crop` from the retained
  rasters;
- mock and test temporary outputs.

**Do.**
1. Inventory with sizes, then classify each item (delete / keep, with the reason). Check every delete candidate for receipt
   citations first.
2. Delete only the candidates.
3. Write `docs/records/labelfix/secondary/DISK1_REPORT.md`: freed GB, a table of the removed paths with sizes and the reason each is
   regenerable, and any candidate kept because something cites it.
4. Report free disk space before and after (`df -h /`).

**Last line:** `DISK1 READY: freed <GB> GB (worktree <GB>, scratchpad <GB>); kept-cited <n>; df before <GB> after <GB>`
