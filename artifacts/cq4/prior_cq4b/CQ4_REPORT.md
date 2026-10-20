# CQ4b amended inventory: STOP

Amendment 1 enlarges W-CAP to 20 candidate documents, but the unchanged top-up exclusions fail the mandatory 70% gate. No packs, control pool, run scripts, readings, training or R2a manifest were built.

Preregistration SHA-256 verified: `dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc`.
Canonical scanner v4.4 copied without modification; source before/after and destination SHA-256: `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. Dependencies copied from the same canonical directory with hashes in the receipt. CQ4 does not import or invoke a CQ1 v4.3 wrapper.
CQ1 canonical re-scan: **r1 VOID**, `/zoom/batch1.png` at record **24**; **r1b clean**, with manifest integrity enabled. Full audits: `artifacts/cq4/regression/`.

The exclusion union remains 495 documents for top-up. Removing only the validation reason for W-CAP gives 478 excluded documents; the 17 validation-role documents have no other exclusion reason. Calibration remains excluded from both sets. Original CQ4 inventory/report artifacts are preserved in `artifacts/cq4/prior_cq4/`.

## Inventory gate

| Set | Candidate documents | Per-document slot cap | Generous slot upper bound | 70% minimum | Result |
|---|---:|---:|---:|---:|---|
| W-CAP | 20 | 30 | 600 | 210 | Document bound passes; actual slot availability not located |
| Top-up, before reserving any W-CAP document | 3 | 120 | 360 | 844 | **STOP** |

Top-up requires about 735 likely-bare + 470 likely-marked slots (1,205). Even granting all three unused documents exclusively to top-up gives at most 360 slots. Choosing any for W-CAP reduces that bound. The 97 other supervision-role and 29 other witness-role documents are already excluded; validation and calibration remain excluded for top-up. At least eight eligible top-up documents are necessary for the 844-slot gate under the generous 120-slot cap.

The broader raw top-up scan includes all Greek monotonic and polytonic v2 train lines, not only ALL-CAPS lines or saved R2C eligibility; **zero v2 documents survive**. W1 c1_pass Greek candidates leave the same three unused documents. The impossibility holds even without the 25% oversampling: 70% of the 959-slot repair deficit is 672, above 360. No marked/bare, geometry, page-cap or manifest-overlap assumption is needed.

## Counts per candidate document

Line counts are saved eligible lines for W-CAP and broad admitted source lines for top-up. Slot columns are optimistic document-cap upper bounds; actual located, marked-likely and bare-likely counts remain unknown. Documents appearing in both columns are alternatives, never selected for both.

| Canonical document | Pool / source | Era | Role | W-CAP lines | W-CAP slot cap | Top-up lines | Top-up slot cap |
|---|---|---|---|---:|---:|---:|---:|
| `1831672` | W1 / nlg | 1870s | validation | 94 | 30 | 0 | 0 |
| `1833530` | W1 / nlg | 1910s | validation | 76 | 30 | 0 | 0 |
| `1909952` | W1 / nlg | 1920s | supervision | 147 | 30 | 147 | 120 |
| `1d5ad22a` | v2 / openarchives:openarchives_ktisis | 2010s | validation | 202 | 30 | 0 | 0 |
| `29bccf95` | v2 / parliament:parliament_proceedings_1975_2000 | 1990s | validation | 1603 | 30 | 0 | 0 |
| `70ec3f44` | v2 / openarchives:openarchives_anaktisis | 2000s | validation | 255 | 30 | 0 | 0 |
| `IA41545826_0032` | W1 / ia_poly1850 | 1870s | witness | 142 | 30 | 142 | 120 |
| `a8b6ae98` | v2 / parliament:parliament_proceedings_1975_2000 | 1980s | validation | 1307 | 30 | 0 | 0 |
| `aab19902` | v2 / openarchives:openarchives_nemertes | 2000s | validation | 116 | 30 | 0 | 0 |
| `b2619986` | v2 / openarchives:openarchives_kallipos | 2010s | validation | 199 | 30 | 0 | 0 |
| `bsb10800804` | W1 / bsb_poly1850 | 1850s | validation | 251 | 30 | 0 | 0 |
| `bsb10931672` | W1 / bsb_poly1850 | 1880s | validation | 183 | 30 | 0 | 0 |
| `bsb11330089` | W1 / bsb_poly1850 | 1870s | validation | 155 | 30 | 0 | 0 |
| `bsb11338903` | W1 / bsb_poly1850 | 1860s | validation | 144 | 30 | 0 | 0 |
| `bsb11880340` | W1 / bsb_poly1850 | 1890s | validation | 121 | 30 | 0 | 0 |
| `bub_gb__SJFAAAAMAAJ` | W1 / ia_poly1850 | 1850s | validation | 172 | 30 | 0 | 0 |
| `dasmarcusevange00weisgoog` | W1 / ia_poly1850 | 1870s | validation | 17 | 30 | 0 | 0 |
| `decallimachivita00linc` | W1 / ia_poly1850 | 1860s | validation | 35 | 30 | 0 | 0 |
| `euripidesexrecen03euri` | W1 / ia_poly1850 | 1870s | supervision | 142 | 30 | 142 | 120 |
| `geschichtederal00goog` | W1 / ia_poly1850 | 1890s | validation | 13 | 30 | 0 | 0 |

## W-CAP candidates by source and era

| Pool | Source | Era | Documents |
|---|---|---|---:|
| W1 | bsb_poly1850 | 1850s | 1 |
| W1 | bsb_poly1850 | 1860s | 1 |
| W1 | bsb_poly1850 | 1870s | 1 |
| W1 | bsb_poly1850 | 1880s | 1 |
| W1 | bsb_poly1850 | 1890s | 1 |
| W1 | ia_poly1850 | 1850s | 1 |
| W1 | ia_poly1850 | 1860s | 1 |
| W1 | ia_poly1850 | 1870s | 3 |
| W1 | ia_poly1850 | 1890s | 1 |
| W1 | nlg | 1870s | 1 |
| W1 | nlg | 1910s | 1 |
| W1 | nlg | 1920s | 1 |
| v2 | openarchives:openarchives_anaktisis | 2000s | 1 |
| v2 | openarchives:openarchives_kallipos | 2010s | 1 |
| v2 | openarchives:openarchives_ktisis | 2010s | 1 |
| v2 | openarchives:openarchives_nemertes | 2000s | 1 |
| v2 | parliament:parliament_proceedings_1975_2000 | 1980s | 1 |
| v2 | parliament:parliament_proceedings_1975_2000 | 1990s | 1 |

## Reproduction and limits

Run `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/cq4/tools/inventory.py`, then the same interpreter with `-m unittest discover -s artifacts/cq4/tools -p "test_*.py"`. Input hashes and scanner identity are recorded in the build receipt; validation results are in `artifacts/cq4/validation.json`. **8 inventory/custody/scanner regression tests passed.** Selection, pack closure and re-read tests are deferred because the mandatory inventory gate stops before those components are built.
No network calls, `.git` writes, reader calls, model inference or limit probes were made. Executed reader cost is **0 weekly points**; live weekly usage is unknown. The requested full 18-context initial read remains an upper-bound estimate of **3.37 weekly points**, before re-reads. This inventory does not qualify located W-CAP slots or printed truth.
Continuation requires a coordinator amendment to top-up document eligibility or additional eligible documents. The present instruction explicitly keeps validation documents excluded from top-up, so they were not repurposed.

CQ4b BUILD STOPPED: W-CAP candidate docs 20 (slot upper bound 600, located counts unknown); top-up candidate docs 3 (slot upper bound 360 < 844); contexts 0; controls pool 0; scanner v4.4 sha ok; CQ1 rescan r1 VOID / r1b clean; executed reader Codex 0 pts.
