# KR3 kosmo2 scoring

c2b is accepted under v4.1: **53 exact + 11 v4-downscale = 64/64**, with no violations and the manifest check enabled. The fresh scan resolves the recorded pwd/template paths, including record 27; all other v4 checks remain unchanged. The ordinary v4 image rule accepts exact matches or downscales with long side 2048, aspect within 1 px and RGB MAD < 2. The previous strict KR2 rejection is superseded; its scan is retained as historical evidence. c1 passes v4; c2 remains VOID and excluded.

| Run | Cards | Letters y | Crop_ok y | Marks y | Controls |
|---|---:|---:|---:|---:|---:|
| c1 + c2b | 100 | 96 | 100 | 89 | 10/10 |
| SRK2 `87db4392`, **pre-handover, no controls** | 100 | 96 | 99 | 90 | none |

Letters and crop_ok are final Sol verdicts. Marks remain **pending_opus**. Scoring is mechanical with network OFF; no new reader or visual adjudication was run. Both contexts have zero control errors and are unflagged.

Pairing uses exactly the same 100 unique line IDs and verifies crop SHA256 identity. The SRK2 answer file was read from commit `87db4392` and checked byte-for-byte against the local file. Agreement measures verdict agreement, not independent accuracy.

**letters: 100/100 agreement**; transitions (SRK2 → current): y->y: 96, n->n: 4.


**crop_ok: 99/100 agreement**; transitions (SRK2 → current): y->y: 99, n->y: 1.

- `kosmopolis--aaa124307e36f113--s001-l0085`: n → y; current detail: (empty). Previous detail: ἰσχυρόταται (τελικὸ ι κομμένο) → ἰσχυρόταται.

**marks: 97/100 agreement**; transitions (SRK2 → current): y->y: 88, n->n: 9, y->n: 2, n->y: 1.

- `kosmopolis--aaa124307e36f113--s006-l0098`: y → n; current detail: ἂς → ἃς. Previous detail: (empty).
- `kosmopolis--aaa124307e36f113--s000-l0030`: y → n; current detail: σκεπτομένη → σκεπτομενη. Previous detail: (empty).
- `kosmopolis--aaa124307e36f113--s002-l0035`: n → y; current detail: (empty). Previous detail: ἐπιοῦσαν → ἐπιοῦσὰν.

The [review queue](review_queue.jsonl) has **19 unique cards** (16 bed, 3 controls). It includes every current negative/unreadable verdict, nonempty error list and control disagreement. Expected-negative controls are included as flags and distinguished from control errors. Paired flips are retained separately above and in results.json. Each queue record preserves the crop, IDs, verdicts, errors and original reader detail. Review remains pending.

Four wrapper tests pass: real witness acceptance and template resolution, true outside-path rejection, parent escape rejection, and v4 downscale limits (MAD, aspect, long side). [Final scan](scan/kosmo2/c2b.scan_v41_final.json); [test log](scan/v41_final.tests.log).

**HANDOVER limitation:** this session cannot write the Sol-reading worktree. The §5 addition is prepared as [HANDOVER.v41.patch](handover/HANDOVER.v41.patch), with before/after hashes and a guarded external commit list. The existing HANDOVER contains no v4.1 bullet, so the patch adds the corrected ordinary-v4 wording. It has not been applied there. No staging or commit was attempted in either worktree.

KR3_COMMIT_FILES.txt and KR3_COMMIT_GUARD.json bind the recut change set. The handover/ directory contains the separate Sol-reading list and guard. Require matching HEAD/branch, empty index, and all input/output hashes; stage only the exact listed paths and verify the staged set. Stop on mismatch.

KR3: done | c2b accepted (v4.1) | letters y: 96 | crop_ok y: 100 | marks y: 89 (pending opus) | controls: 10/10 | paired agreement letters/crop: 100/99 | review queue: 19
