# OS4: re-tags from the owner's notes on the failure-modes sheet (gpt-6.1-sol, medium, network OFF; no .git writes)

Runs after OS3, on its outputs. Keep every doc id (line id). Change only fault classification and placement.

**Owner notes, via the coordinator:**
1. **Three ia_poly1850 cards in the Latin-lookalike group.** The owner doubts them: "doesn't necessarily have to do with the Latin".
   - The cards: `…41e90f3ba967f920--s006-l0022`, `…a89bd2c9bdb1ca6d--s005-l0038`, `…a89bd2c9bdb1ca6d--s007-l0016`. Resolve the full
     line ids from the spec.
   - Re-classify each from its checker detail and error codes (C1 verdicts) into the fault the evidence supports, e.g. a letter
     confusion or a mark error. Move it to that subsection. If the evidence names no specific fault, use "letter misread
     (unspecified)", never Latin.
   - Record the old tag, the new tag and the evidence sentence.
2. **`nlg--1144074169f43992--s006-l0032` is wrongly under "em dash dropped".** It is a clipped dash stroke plus a mark error. Tag it
   with both, and place it under the clipped-edge fault, cross-listed under the mark error. If the builder supports only one placement,
   put it under the clipped edge with a "mark error" tag.
3. **Audit the rest of the sheet for the same mistake:** any card whose tag comes only from a stratum-level label rather than its own
   error codes. List every such card and re-tag it by the same rule.

**Dashes:** owner ruling "tag only, no track". Keep the dash fault subsection as tagged examples, with no further work.

Re-render `artifacts/owner_sheets/v2/*.html`. Add an OS4 section to `docs/records/owner_sheets/OS2_REPORT.md` with the table: card, old tag, new
tag, evidence. Tests pass.

Last line: `OS4 READY: owner re-tags 4; audit re-tags <n>; doc ids identical yes; tests <n> passed`.
