# SEGCENSUS-1b: pin the edition-split file as a package input (gpt-6.1-sol, medium, network ON for read-only Clariden checks and the deploy copy only; no .git writes; no submission)

Runs AFTER SEGCENSUS-1. Read its hand-off `docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md` first.

**Dependency (coordinator).** No collect-v3 W1/W2 row can be admitted until the edition split exists. Census_03's 65,900 admits are
collection-v2 only; its 142,959 `split_or_edition_identity_unresolved` holds are exactly the collect-v3 W1/W2 rows (parent
`collect-v3-W1/W2-20261018-0524`, split "unassigned"). The sourcing lead is building that split (SPLIT1: whole-edition
train/dev/test, owner sheet).

**Do.**
1. **Find how the pipeline assigns split** to collect-v3 parents. State exactly whether it already consumes a split file, which
   one and with which schema. If not, state the minimal change needed: read a pinned split file (path + sha256 in the config, like
   the metadata join) keyed by edition/row id, and use its split for collect-v3 rows.
   - Implement the change ONLY as input plumbing, with tests. Rows absent from the file keep today's "unassigned" hold. No new
     admission rule.
   - Get the expected SPLIT1 schema from the sourcing lead's docs if present (search sol-recut / sol-collect `docs/` for SPLIT1);
     otherwise define a minimal schema and list it for the lead.
2. **The package runs in two modes from the same code:**
   - (i) **no split file pinned:** W1/W2 stay held, so only v2 rows change, by 0.8;
   - (ii) **split file pinned:** W1/W2 are admitted per split.

   Mock-test both modes on the ~200-row slice (with a fake split file in mode ii) and the 150+888 identity. Re-deploy as a new code
   hash if anything changed: `VERIFY_OK`, sha table, and `--test-only` per job kind.
3. Append a section "1b: split input" to the hand-off: the current split behaviour, the change made, the schema, mock results for
   both modes, the new deploy hash, and submit commands for mode (i) now and for mode (ii) later. Do not submit anything.

**Last line:** `SEGCENSUS1b READY: split consumed before <yes|no>; change <none|plumbing>; schema <fields>; mock mode-i <ok> mode-ii <ok>; deploy <hash> VERIFY_OK; tests <n> passed`
