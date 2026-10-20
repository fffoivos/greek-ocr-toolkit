# CQ4 inventory: STOP

The mandatory pre-build gate fails. No packs, contexts, controls, runner scripts, readings, training or R2a manifest were built.

Preregistration SHA-256 verified: `3b2fdf21169124e0b5e73503860ac299bacc9db5b9aba7917fa65213f65732dc`.

The requested whole-document exclusion union contains **495 documents**. IDs and per-reason membership are in `artifacts/cq4/excluded_docs.json`; input hashes are in `artifacts/cq4/build_receipt.json`.

| Pool | Source | Era | Candidate documents |
|---|---|---|---:|
| W1 | ia_poly1850 | 1870s | 2 |
| W1 | nlg | 1920s | 1 |

Candidate documents:
- `1909952` (supervision, 147 candidate lines)
- `IA41545826_0032` (witness, 142 candidate lines)
- `euripidesexrecen03euri` (supervision, 142 candidate lines)

Even before recogniser/case classification, geometry rejection, class balance, page caps, or document alias merging, 3 documents × 30 slots/document gives at most **90/300 W-CAP slots**. The minimum is **210/300**. This is a generous upper bound, not a claim of available readable slots. At least seven documents are required even for the 70% threshold; ten are required for 300 slots. Splitting the remaining documents between W-CAP and top-up can only lower this bound.

The raw W1 c1_pass polytonic rows and collection-v2 training rows were checked directly. V2 eligibility includes monotonic rows and Greek polytonic rows whose letter sequence is ALL-CAPS; none survive the requested exclusions. R2C saved eligibility is not used to restrict this W-CAP document upper bound.

R1 document_split holds out 16 of the 316 C1 documents; these are already in old_pool_316.

Likely-marked / likely-bare slot counts remain unknown: the gate stops before location or selection. Top-up selection is also stopped. The remaining saved R2C top-up inventory after reserving the three W-CAP candidate documents is empty; no wider top-up availability claim is made.

No reader or limit probe ran. Live Codex percentages are unknown; executed reader cost is 0 points. The requested full initial 1,505 bed items plus 180 controls (18 contexts) would have a HANDOVER §7 upper-bound estimate of 3.37 weekly points before re-reads. No reading is authorized here.

Reproduce: `python3 -B artifacts/cq4/tools/inventory.py`. The script asserts the shortfall and writes inventory artifacts only. Fresh eligible documents or an owner-approved change to the document exclusions/caps is needed before pack construction.

CQ4 BUILD STOPPED: W-CAP document-cap upper bound below 70%; no packs or readers built.
