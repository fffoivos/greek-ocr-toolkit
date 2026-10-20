# Final-source default cost — 15 October 2026

Two sequential full208 passes,416 file-to-final executions. Values are median/p95/max milliseconds. These are descriptive clocks, not a before/after speedup. Aggregate primary-detector drift is **+5.674%**, above the preset5% control; no replacement run was permitted by the frozen plan. Both raw runs remain local and hash-bound in [AUDIT.json](AUDIT.json).

| Scope | Forward | Reverse |
|---|---:|---:|
| decode_s | 24.1/94.9/128.8 | 28.5/109.5/129.2 |
| detector_s | 137.0/163.7/223.1 | 140.0/182.4/223.8 |
| paddle_file_s | 157.1/238.5/351.8 | 170.9/291.6/353.0 |
| correction_s | 264.4/1766.8/2735.1 | 264.6/1992.8/3311.6 |
| total_s | 426.1/2009.5/2939.3 | 407.3/2255.0/3566.9 |

Agreement40 correction overhead: **78.4/722.3/956.4** forward, **82.2/782.2/973.1** reverse. These pages include native crop/descender defects (historical db97p90/f9ecp12 controls); no verified-clean40 latency is claimed. The owner supplied no numeric threshold for negligible overhead.

Startup50.50/20.62ms lies outside warm per-page clocks. Each arm creates one session and warms the same two pages. OpenCV request0/observed1; ONNX CPU sequential intra/inter1/1 observed from session options. All five numerical-library environment controls are1. Model hash, exact208 allowlist/input hashes, selectors, startup boundary and UTC start/end times are in the frozen plan/raw records. A setup import-path error occurred before any session/page run; its log remains and it is not a discarded timing pass.

## Every page at or above one second

| Page | Forward corrections ms | Reverse corrections ms | Largest forward scope |
|---|---:|---:|---|
| `an-9ea1564fcf4f-p000013` | 1055.5 | 1044.4 | field_proposal_s |
| `an-9ea1564fcf4f-p000202` | 2206.6 | 2143.9 | field_proposal_s |
| `an-9ea1564fcf4f-p000218` | 1464.9 | 1416.1 | field_proposal_s |
| `an-c8b96a901917-p000036` | 1869.7 | 1735.4 | field_proposal_s |
| `an-c8b96a901917-p000068` | 1508.1 | 1400.9 | field_proposal_s |
| `an-c8b96a901917-p000155` | 1373.5 | 1256.4 | field_proposal_s |
| `s2-0ce9d1025b3f23c7119e-p00001` | 1392.2 | 1347.3 | field_proposal_s |
| `s2-31f40cef90235c91b023-p00001` | 1290.7 | 1415.8 | field_proposal_s |
| `s2-3229200bf47ca465a42d-p00004` | 855.8 | 1062.1 | field_proposal_s |
| `s2-3229200bf47ca465a42d-p00006` | 1294.8 | 1591.6 | type_s |
| `s2-44b5cf9e0d680b361091-p00001` | 1478.3 | 1860.3 | field_proposal_s |
| `s2-44b5cf9e0d680b361091-p00002` | 2194.9 | 2685.1 | field_proposal_s |
| `s2-44b5cf9e0d680b361091-p00003` | 903.3 | 1125.6 | field_proposal_s |
| `s2-44b5cf9e0d680b361091-p00005` | 1236.7 | 1499.4 | field_proposal_s |
| `s2-49598b2e848ab1f0ee1e-p00001` | 2514.2 | 3076.7 | field_proposal_s |
| `s2-49598b2e848ab1f0ee1e-p00004` | 2338.7 | 2875.6 | field_proposal_s |
| `s2-49598b2e848ab1f0ee1e-p00005` | 2735.1 | 3311.6 | type_s |
| `s2-60f24a3d8a2d714767f2-p00003` | 1474.4 | 1809.7 | field_proposal_s |
| `s2-661ddf05c8865e7b2c45-p00004` | 1792.2 | 2206.6 | field_proposal_s |
| `s2-661ddf05c8865e7b2c45-p00010` | 1719.4 | 2061.9 | field_proposal_s |
| `s2-6f045b952f909b38d4db-p00001` | 1525.4 | 1864.3 | type_s |
| `s2-74cdb23a34ca4a6cd01e-p00006` | 841.5 | 1014.6 | field_proposal_s |
| `s2-74cdb23a34ca4a6cd01e-p00007` | 1415.0 | 1788.2 | field_proposal_s |
| `s2-831443dc5e6f1ccfbaf5-p00042` | 1022.3 | 1169.0 | field_proposal_s |
| `s2-86865c33eef5932c013b-p00005` | 1299.8 | 1619.3 | field_proposal_s |
| `s2-86865c33eef5932c013b-p00007` | 1176.7 | 1423.3 | field_proposal_s |
| `s2-93f8070059f938bda524-p00001` | 2129.0 | 2607.1 | field_proposal_s |
| `s2-9de6cda8f03f0fc60a58-p00005` | 1356.6 | 1628.0 | field_proposal_s |
| `s2-c0b02fe229794d2fe76d-p00007` | 1320.2 | 1589.6 | field_proposal_s |
| `s2-d12a9a4feb23254f4080-p00008` | 2280.2 | 2305.9 | field_proposal_s |
| `s2-d1ed1c2db37f431f4acb-p00001` | 2349.1 | 2439.3 | field_proposal_s |
| `s2-dfcc21869afc140111ce-p00001` | 2271.2 | 2271.5 | field_proposal_s |

Forward≥1s:29/208; reverse:32/208; union:32/208. A paired page here means the same source/input in two orders, not baseline versus candidate. Detector per-page drift flags remain in the JSON.

## Non-overlapping built-in stages

No new nested timers were added. These are mutually exclusive top-level scopes already returned by compose; nested scout/refinement/native fields are not summed.

| Scope | Forward sum s | Reverse sum s |
|---|---:|---:|
| rule_scout_s | 2.915 | 3.132 |
| q8_correction_s | 0.188 | 0.217 |
| ink_s | 6.760 | 6.499 |
| edge_scout_s | 1.144 | 1.237 |
| field_cuts_s | 0.548 | 0.636 |
| field_proposal_s | 40.693 | 45.054 |
| field_early_replace_s | 4.871 | 5.276 |
| geometry_all_s | 3.843 | 4.077 |
| type_s | 15.895 | 17.180 |
| shape_s | 3.146 | 3.168 |
| ink_identity_s | 0.087 | 0.097 |
| faint_s | 3.292 | 3.511 |
| field_replace_s | 0.343 | 0.360 |
| rows_s | 4.350 | 4.831 |
| row_ownership_s | 8.534 | 9.336 |
| final_faint_s | 0.524 | 0.590 |
| frame_s | 1.087 | 1.162 |
| final_bands_s | 0.000 | 0.000 |

Unassigned correction dispatch/allocations:0.165/0.187s. Field proposals dominate at40.693/45.054s, then type15.895/17.180s and row ownership8.534/9.336s. Regional Paddle is included inside corrections/field proposals; primary detector time is separate.

Historical adopted speed evidence remains source-paired: R8-04 field stage−5.1/−5.6% on42active pages within83paired pages, pooled corrections−3.3/−2.6%, with the disclosed reversed-baseline JSON-work overlap. Consolidation removes103closings/CC,8remaps,2205histograms and368mean filters; overall timings were small/order-sensitive. These are not obtained by subtracting the present medians from R7.

Parked M17 pilot953fc4a: roughly3–5% integrated gain in its older population, not deployed here. Current explicit shifts_many Rust:4.741772→5.183365s batch work (9.3% slower), no repeated integrated gain; approximate removable5.144% ceiling1.0542× has separate-run boundaries. SLOW27 coherent Python upper19.908%, free ceiling1.2486×; combined proposals+replacement sensitivity25.8–26.8% raw/23.3–25.0% scaled is not one coherent port boundary and includes NumPy/profiler attribution limits. No new port. Experimental final_export20–34s tails are off-default.
