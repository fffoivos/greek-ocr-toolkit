# R2 job 3681404: first readback and BASE digest

Job completed with exit 0:0 (coordinator report), 34:46 Slurm elapsed. This is BASE seed spread and teacher-export accounting; it does not establish a repair benefit or authorize another run. No submission, certificate refresh, new extraction or cohort inference was performed. All scoring below uses saved job predictions and frozen R1-A predictions.

## Readback

Pulled 17,730 files / 458,783,338 bytes, 2026-10-17T08:52:25Z to 2026-10-17T08:53:29.820030+00:00 (11:52–11:53 Athens, before 18:30). 17,730/17,730 SHA256 verified; 17,723 against stage/chunk receipts. The remaining seven root envelopes/log have no parent receipt and were verified against remotely captured SHA256 values. Their `receipt_match=no` means no parent receipt; there are zero mismatches or missing stage payloads. BASE checkpoints only; no windows, crops or training shards pulled.

[Readback receipt](../../../../../artifacts/labelfix_r2/output_3681404/READBACK_RECEIPT.json), [remote envelope hashes](../../../../../artifacts/labelfix_r2/readback_3681404_root_sha256.txt).

## Stage timing and measured throughput

| Stage | Receipt min | Reference min |
| --- | --- | --- |
| A | 0.000002 | I/O unforecast |
| B | 15.875242 | 18.902 |
| C | 17.482318 | 30 (training planning allowance) |

A–C receipt sum 33.358 min; Slurm wall 34.767 min vs requested forecast 74 min (forecast unpadded 48.902 min). Stage A reports only result recording: input validation precedes its timer, so this is **not** measured input verification time. Stage B includes startup and receipt/export costs; chunk alignment/windows/teacher totals are 90.946/317.075/278.072 s. Stage C includes parallel seed execution, validation and export; training-only times must not be added to parallel wall.

Teacher end-to-end Stage B: 49.479 lines/s, 1293.825 slots/s (47,129 lines / 1,232,387 slots). Export internal elapsed 930.702 s gives 50.638 lines/s and 1324.148 slots/s. Teacher forward-only: 4431.900 slots/s; alignment-only: 518.211 lines/s.

| Seed | Draws | Train s | Train draws/s | Best val loss |
| --- | --- | --- | --- | --- |
| 20261017 | 29025240 | 914.997 | 31721.681 | 0.01535226 |
| 20261018 | 29025240 | 910.349 | 31883.627 | 0.01396799 |

## Teacher-export inventory

Every exported row was parsed and every head checked for the full named softmax, finite [0,1] values, sum=1 (1e-5 tolerance), argmax/top probability, margin consistency (1e-6 tolerance), and factor/top agreement. Confidence shares below use all role/source slots as denominator, including flagged windows; confidence is uncalibrated and does not admit a pseudo-label. Localisation unknown means coverage evidence_state=UNKNOWN or nonempty uncertainty. Clipping means edge ink, with ownership unadjudicated.

| Role | Lines | Slots | Teacher-seen lines / slots | Top clip | Bottom clip | Outside | Bad span | Locator unknown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 27308 | 717612 | 4398 / 93126 | 39702 | 36441 | 34685 | 499 | 330 |
| validation_reserve | 4943 | 121392 | 0 / 0 | 12210 | 12918 | 6518 | 154 | 96 |
| witness | 8856 | 226680 | 0 / 0 | 4664 | 3897 | 12021 | 74 | 144 |
| calibration | 6022 | 166703 | 0 / 0 | 4520 | 4528 | 7928 | 21 | 75 |

### Probability integrity

| Role | Head | Checked | Missing rows | Invalid rows | Factor mismatch |
| --- | --- | --- | --- | --- | --- |
| train | breathing | 717612 | 0 | 0 | 0 |
| train | accent | 717612 | 0 | 0 | 0 |
| train | dialytika | 717612 | 0 | 0 | 0 |
| train | subscript | 717612 | 0 | 0 | 0 |
| validation_reserve | breathing | 121392 | 0 | 0 | 0 |
| validation_reserve | accent | 121392 | 0 | 0 | 0 |
| validation_reserve | dialytika | 121392 | 0 | 0 | 0 |
| validation_reserve | subscript | 121392 | 0 | 0 | 0 |
| witness | breathing | 226680 | 0 | 0 | 0 |
| witness | accent | 226680 | 0 | 0 | 0 |
| witness | dialytika | 226680 | 0 | 0 | 0 |
| witness | subscript | 226680 | 0 | 0 | 0 |
| calibration | breathing | 166703 | 0 | 0 | 0 |
| calibration | accent | 166703 | 0 | 0 | 0 |
| calibration | dialytika | 166703 | 0 | 0 | 0 |
| calibration | subscript | 166703 | 0 | 0 | 0 |

### Confidence by role and source family

Each cell is p(top)≥0.99 share / margin≥0.20 share / both share. `source` is the exported source-family label. Population line counts (including zero-slot lines), teacher-seen true/false line and slot counts, detailed missing-field counts and probability bins [0,.5), [.5,.9), [.9,.99), [.99,1] are in [teacher inventory JSON](evidence/job1/teacher_inventory.json).

| Role | Slots | breathing | accent | dialytika | subscript |
| --- | --- | --- | --- | --- | --- |
| train | 717612 | 97.808% / 99.767% / 97.808% | 96.689% / 99.794% / 96.689% | 99.956% / 99.997% / 99.956% | 99.933% / 99.997% / 99.933% |
| validation_reserve | 121392 | 97.089% / 99.689% / 97.089% | 95.035% / 99.651% / 95.035% | 99.956% / 99.998% / 99.956% | 99.904% / 99.995% / 99.904% |
| witness | 226680 | 97.467% / 99.715% / 97.467% | 96.312% / 99.702% / 96.312% | 99.945% / 99.999% / 99.945% | 99.947% / 99.994% / 99.947% |
| calibration | 166703 | 97.538% / 99.692% / 97.538% | 96.588% / 99.779% / 96.588% | 99.944% / 99.996% / 99.944% | 99.955% / 99.997% / 99.955% |

| Role / source | Slots | breathing | accent | dialytika | subscript |
| --- | --- | --- | --- | --- | --- |
| calibration / bsb_poly1850 | 10809 | 99.232% / 99.954% / 99.232% | 98.918% / 99.944% / 98.918% | 99.963% / 100.000% / 99.963% | 99.935% / 99.991% / 99.935% |
| calibration / ia_poly1850 | 5585 | 98.639% / 99.839% / 98.639% | 97.816% / 99.875% / 97.816% | 100.000% / 100.000% / 100.000% | 99.893% / 99.982% / 99.893% |
| calibration / nlg | 3314 | 99.970% / 100.000% / 99.970% | 99.698% / 100.000% / 99.698% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| calibration / openarchives:openarchives_Dione | 8377 | 97.410% / 99.690% / 97.410% | 96.073% / 99.785% / 96.073% | 99.845% / 99.988% / 99.845% | 99.857% / 99.988% / 99.857% |
| calibration / openarchives:openarchives_KEIED | 20657 | 97.575% / 99.661% / 97.575% | 96.374% / 99.739% / 96.374% | 99.903% / 99.990% / 99.903% | 99.981% / 99.995% / 99.981% |
| calibration / openarchives:openarchives_Pandemos | 18001 | 98.211% / 99.794% / 98.211% | 97.783% / 99.933% / 97.783% | 99.956% / 100.000% / 99.956% | 99.956% / 100.000% / 99.956% |
| calibration / openarchives:openarchives_anaktisis | 12747 | 97.631% / 99.678% / 97.631% | 96.540% / 99.796% / 96.540% | 99.906% / 100.000% / 99.906% | 99.945% / 100.000% / 99.945% |
| calibration / openarchives:openarchives_apothesis | 23495 | 97.119% / 99.660% / 97.119% | 97.216% / 99.928% / 97.216% | 99.940% / 99.996% / 99.940% | 99.962% / 100.000% / 99.962% |
| calibration / openarchives:openarchives_hellanicus | 5117 | 97.596% / 99.726% / 97.596% | 97.010% / 99.863% / 97.010% | 99.902% / 99.980% / 99.902% | 99.980% / 100.000% / 99.980% |
| calibration / parliament:parliament_proceedings_1975_2000 | 58601 | 96.923% / 99.606% / 96.923% | 95.369% / 99.621% / 95.369% | 99.969% / 99.998% / 99.969% | 99.964% / 99.998% / 99.964% |
| train / bsb_poly1850 | 35439 | 99.103% / 99.904% / 99.103% | 97.898% / 99.881% / 97.898% | 99.975% / 100.000% / 99.975% | 99.828% / 99.989% / 99.828% |
| train / ia_poly1850 | 21739 | 98.556% / 99.913% / 98.556% | 97.622% / 99.834% / 97.622% | 99.949% / 99.995% / 99.949% | 99.885% / 100.000% / 99.885% |
| train / mixed:anemi_mixed | 1765 | 99.660% / 100.000% / 99.660% | 98.357% / 99.943% / 98.357% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| train / mixed:archive_b28038630 | 302 | 99.338% / 100.000% / 99.338% | 98.675% / 100.000% / 98.675% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_Dione | 4592 | 97.147% / 99.760% / 97.147% | 90.767% / 99.521% / 90.767% | 99.913% / 100.000% / 99.913% | 99.826% / 99.978% / 99.826% |
| train / mixed:openarchives_mixed_KEIED | 2907 | 97.110% / 99.759% / 97.110% | 95.941% / 99.862% / 95.941% | 99.931% / 100.000% / 99.931% | 99.897% / 100.000% / 99.897% |
| train / mixed:openarchives_mixed_Pandemos | 124 | 97.581% / 100.000% / 97.581% | 97.581% / 99.194% / 97.581% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_anaktisis | 3262 | 97.731% / 99.785% / 97.731% | 97.762% / 100.000% / 97.762% | 100.000% / 100.000% / 100.000% | 99.908% / 100.000% / 99.908% |
| train / mixed:openarchives_mixed_apothesis | 1492 | 97.520% / 99.598% / 97.520% | 97.453% / 100.000% / 97.453% | 100.000% / 100.000% / 100.000% | 99.531% / 100.000% / 99.531% |
| train / mixed:openarchives_mixed_hellanicus | 1518 | 97.760% / 99.868% / 97.760% | 97.694% / 99.802% / 97.694% | 99.934% / 100.000% / 99.934% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_kallipos | 349 | 97.421% / 99.713% / 97.421% | 97.994% / 100.000% / 97.994% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_ktisis | 2478 | 98.023% / 99.839% / 98.023% | 97.296% / 99.919% / 97.296% | 99.879% / 100.000% / 99.879% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_nemertes | 1148 | 97.125% / 99.652% / 97.125% | 96.429% / 100.000% / 96.429% | 99.652% / 100.000% / 99.652% | 100.000% / 100.000% / 100.000% |
| train / mixed:openarchives_mixed_ntua | 340 | 97.353% / 99.706% / 97.353% | 94.118% / 99.706% / 94.118% | 100.000% / 100.000% / 100.000% | 98.824% / 100.000% / 98.824% |
| train / nlg | 23261 | 99.480% / 99.983% / 99.480% | 99.123% / 99.936% / 99.123% | 99.974% / 99.996% / 99.974% | 99.957% / 100.000% / 99.957% |
| train / openarchives:openarchives_Dione | 43544 | 97.325% / 99.651% / 97.325% | 96.590% / 99.835% / 96.590% | 99.883% / 99.993% / 99.883% | 99.945% / 99.995% / 99.945% |
| train / openarchives:openarchives_KEIED | 38877 | 97.839% / 99.673% / 97.839% | 97.366% / 99.859% / 97.366% | 99.987% / 100.000% / 99.987% | 99.910% / 99.997% / 99.910% |
| train / openarchives:openarchives_Pandemos | 47825 | 98.143% / 99.770% / 98.143% | 98.007% / 99.937% / 98.007% | 99.981% / 100.000% / 99.981% | 99.987% / 100.000% / 99.987% |
| train / openarchives:openarchives_anaktisis | 24381 | 97.818% / 99.762% / 97.818% | 97.609% / 99.914% / 97.609% | 99.975% / 100.000% / 99.975% | 99.996% / 100.000% / 99.996% |
| train / openarchives:openarchives_apothesis | 17178 | 98.038% / 99.761% / 98.038% | 98.038% / 99.930% / 98.038% | 99.983% / 100.000% / 99.983% | 100.000% / 100.000% / 100.000% |
| train / openarchives:openarchives_hellanicus | 42986 | 97.825% / 99.758% / 97.825% | 97.606% / 99.893% / 97.606% | 99.967% / 99.998% / 99.967% | 99.949% / 100.000% / 99.949% |
| train / openarchives:openarchives_kallipos | 28659 | 97.589% / 99.829% / 97.589% | 97.662% / 99.934% / 97.662% | 99.972% / 99.993% / 99.972% | 99.986% / 100.000% / 99.986% |
| train / openarchives:openarchives_ktisis | 33292 | 97.423% / 99.715% / 97.423% | 97.459% / 99.904% / 97.459% | 99.952% / 100.000% / 99.952% | 99.991% / 100.000% / 99.991% |
| train / openarchives:openarchives_nemertes | 24972 | 97.761% / 99.688% / 97.761% | 97.289% / 99.888% / 97.289% | 99.944% / 100.000% / 99.944% | 99.960% / 99.996% / 99.960% |
| train / openarchives:openarchives_ntua | 32023 | 97.836% / 99.685% / 97.836% | 97.589% / 99.928% / 97.589% | 99.938% / 100.000% / 99.938% | 99.969% / 100.000% / 99.969% |
| train / parliament:parliament_proceedings_1975_2000 | 194568 | 96.669% / 99.680% / 96.669% | 93.986% / 99.519% / 93.986% | 99.946% / 99.996% / 99.946% | 99.918% / 99.995% / 99.918% |
| train / round1:anemi_round1 | 56229 | 99.362% / 99.961% / 99.362% | 98.293% / 99.888% / 98.293% | 99.964% / 99.996% / 99.964% | 99.884% / 99.995% / 99.884% |
| train / round2:anemi_round2 | 8521 | 99.542% / 99.953% / 99.542% | 99.026% / 99.965% / 99.026% | 99.953% / 100.000% / 99.953% | 99.918% / 99.988% / 99.918% |
| train / vouli:vouli_parliament_1850s | 23841 | 99.455% / 99.954% / 99.455% | 98.687% / 99.945% / 98.687% | 99.996% / 100.000% / 99.996% | 99.950% / 100.000% / 99.950% |
| validation_reserve / bsb_poly1850 | 18246 | 98.866% / 99.868% / 98.866% | 98.285% / 99.901% / 98.285% | 99.978% / 100.000% / 99.978% | 99.934% / 100.000% / 99.934% |
| validation_reserve / ia_poly1850 | 4718 | 96.058% / 99.682% / 96.058% | 90.844% / 99.110% / 90.844% | 99.936% / 100.000% / 99.936% | 99.385% / 99.979% / 99.385% |
| validation_reserve / nlg | 3343 | 99.551% / 99.970% / 99.551% | 97.846% / 99.880% / 97.846% | 99.970% / 100.000% / 99.970% | 100.000% / 100.000% / 100.000% |
| validation_reserve / openarchives:openarchives_anaktisis | 6638 | 97.891% / 99.684% / 97.891% | 97.981% / 99.955% / 97.981% | 99.985% / 100.000% / 99.985% | 100.000% / 100.000% / 100.000% |
| validation_reserve / openarchives:openarchives_kallipos | 6085 | 96.270% / 99.540% / 96.270% | 95.530% / 99.786% / 95.530% | 99.869% / 99.984% / 99.869% | 99.951% / 100.000% / 99.951% |
| validation_reserve / openarchives:openarchives_ktisis | 6070 | 98.270% / 99.753% / 98.270% | 98.171% / 99.934% / 98.171% | 99.984% / 100.000% / 99.984% | 100.000% / 100.000% / 100.000% |
| validation_reserve / openarchives:openarchives_nemertes | 3145 | 97.806% / 99.714% / 97.806% | 97.679% / 99.968% / 97.679% | 100.000% / 100.000% / 100.000% | 99.968% / 100.000% / 99.968% |
| validation_reserve / parliament:parliament_proceedings_1975_2000 | 73147 | 96.466% / 99.639% / 96.466% | 93.684% / 99.537% / 93.684% | 99.952% / 99.999% / 99.952% | 99.903% / 99.993% / 99.903% |
| witness / bsb_poly1850 | 22624 | 98.789% / 99.867% / 98.789% | 98.241% / 99.867% / 98.241% | 99.982% / 100.000% / 99.982% | 99.903% / 99.982% / 99.903% |
| witness / ia_poly1850 | 12355 | 99.458% / 99.943% / 99.458% | 98.883% / 99.943% / 98.883% | 99.992% / 100.000% / 99.992% | 99.903% / 100.000% / 99.903% |
| witness / mixed:openarchives_mixed_Dione | 2831 | 97.139% / 99.859% / 97.139% | 91.416% / 99.046% / 91.416% | 99.929% / 100.000% / 99.929% | 99.859% / 99.965% / 99.859% |
| witness / mixed:openarchives_mixed_anaktisis | 4000 | 98.450% / 99.875% / 98.450% | 97.350% / 99.825% / 97.350% | 100.000% / 100.000% / 100.000% | 99.975% / 100.000% / 99.975% |
| witness / mixed:openarchives_mixed_apothesis | 1260 | 98.413% / 99.841% / 98.413% | 98.095% / 100.000% / 98.095% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| witness / mixed:openarchives_mixed_ktisis | 342 | 96.199% / 99.415% / 96.199% | 92.982% / 99.123% / 92.982% | 100.000% / 100.000% / 100.000% | 100.000% / 100.000% / 100.000% |
| witness / nlg | 2096 | 98.473% / 99.905% / 98.473% | 95.897% / 99.523% / 95.897% | 99.952% / 100.000% / 99.952% | 99.857% / 100.000% / 99.857% |
| witness / openarchives:openarchives_anaktisis | 13852 | 97.596% / 99.711% / 97.596% | 96.982% / 99.820% / 96.982% | 99.762% / 100.000% / 99.762% | 99.971% / 99.993% / 99.971% |
| witness / openarchives:openarchives_apothesis | 4689 | 97.825% / 99.744% / 97.825% | 97.953% / 99.915% / 97.953% | 99.979% / 100.000% / 99.979% | 99.979% / 100.000% / 99.979% |
| witness / openarchives:openarchives_hellanicus | 9831 | 98.088% / 99.736% / 98.088% | 96.969% / 99.756% / 96.969% | 99.959% / 100.000% / 99.959% | 99.969% / 100.000% / 99.969% |
| witness / openarchives:openarchives_kallipos | 7095 | 98.182% / 99.915% / 98.182% | 98.506% / 99.972% / 98.506% | 100.000% / 100.000% / 100.000% | 99.986% / 100.000% / 99.986% |
| witness / openarchives:openarchives_ktisis | 17166 | 97.536% / 99.738% / 97.536% | 97.017% / 99.883% / 97.017% | 99.965% / 100.000% / 99.965% | 99.971% / 99.994% / 99.971% |
| witness / openarchives:openarchives_nemertes | 13704 | 97.971% / 99.766% / 97.971% | 97.964% / 99.920% / 97.964% | 99.971% / 100.000% / 99.971% | 99.993% / 100.000% / 99.993% |
| witness / parliament:parliament_proceedings_1975_2000 | 114835 | 96.744% / 99.623% / 96.744% | 95.095% / 99.560% / 95.095% | 99.940% / 99.998% / 99.940% | 99.944% / 99.994% / 99.944% |

## BASE vs saved A on the 666

The R2 `continuity()` column calls the unchanged R1 physical-slot scorer. Frozen metadata gzip envelopes differ from the original extraction, but the original receipt-bound file was hash-verified and its parsed contents match the fixture exactly. Saved A reproduces every published raw/scored/fused/per-class/per-book value exactly (asserted). Predictions cover the identical 11,329 scored extraction slots. The without-overlay instrument includes 206 apostrophe FN outside the four model heads. Overlays v0, v1 and v1.1 were each applied independently to the frozen truth, symmetrically to all models. v1 excludes the unresolved full tuple; v1.1 resolves it. No key was overwritten.

| Overlay | Model | Physical mark P / R / F1 | Four-head P | Four-head R | Tuple all | Tuple marked |
| --- | --- | --- | --- | --- | --- | --- |
| without_overlay | A16 | 99.143% / 94.202% / 96.609% | 90.397% | 99.023% | 97.797% | 98.815% |
| without_overlay | s17 | 99.009% / 93.659% / 96.260% | 90.423% | 98.441% | 97.746% | 98.263% |
| without_overlay | s18 | 99.090% / 94.054% / 96.506% | 90.338% | 98.790% | 97.797% | 98.684% |
| v0 | A16 | 99.143% / 94.202% / 96.609% | 90.397% | 99.023% | 97.797% | 98.815% |
| v0 | s17 | 99.009% / 93.659% / 96.260% | 90.423% | 98.441% | 97.746% | 98.263% |
| v0 | s18 | 99.090% / 94.054% / 96.506% | 90.338% | 98.790% | 97.797% | 98.684% |
| v1 | A16 | 99.169% / 94.225% / 96.634% | 90.395% | 99.022% | 97.802% | 98.841% |
| v1 | s17 | 99.035% / 93.682% / 96.284% | 90.421% | 98.440% | 97.751% | 98.289% |
| v1 | s18 | 99.116% / 94.077% / 96.531% | 90.336% | 98.790% | 97.802% | 98.710% |
| v1_1 | A16 | 99.143% / 94.202% / 96.609% | 90.376% | 98.999% | 97.797% | 98.815% |
| v1_1 | s17 | 99.009% / 93.659% / 96.260% | 90.402% | 98.418% | 97.746% | 98.263% |
| v1_1 | s18 | 99.090% / 94.054% / 96.506% | 90.317% | 98.767% | 97.797% | 98.684% |

**Why four-head precision (~90.4%) is far below continuity precision (~99.1%), and why that is not a regression:** the four-head column also scores 1,334 recognised letters that have no hand-checked truth slot. The union adapter assumes these are unmarked, so every mark the reader puts on them counts as an error: 406 of A16's 452 false positives (404 for s17, 405 for s18), mostly ι/υ/α/ε and some word-initial capitals. The continuity scorer skips those letters (715 unmapped reader slots). On letters both scorers check, they agree: 98.9% vs 99.1%. The effect is identical for A16/s17/s18. **Scorer defect to fix (lead ruling):** letters without print truth must be UNKNOWN, not assumed unmarked (ASTRA-R2design §5). The fix goes into the next Sol package together with R2a.

With v1.1, the three-seed continuity range (max minus min) is precision 0.134 pp, recall 0.543 pp, f1 0.350 pp. These are observed seed ranges, not calibrated statistical acceptance margins. Stage D was skipped because no hash-bound R2a manifest was supplied.

### without_overlay: exact composed classes

| Class | Support | A16 P / R | s17 P / R | s18 P / R |
| --- | --- | --- | --- | --- |
| acute | 1418 | 99.859% / 99.859% | 99.298% / 99.718% | 99.508% / 99.929% |
| acute+subscript | 2 | 100.000% / 50.000% | — / 0.000% | 100.000% / 50.000% |
| circumflex | 303 | 99.669% / 99.340% | 98.671% / 98.020% | 99.662% / 97.360% |
| circumflex+subscript | 39 | 100.000% / 100.000% | 100.000% / 94.872% | 100.000% / 100.000% |
| dasia | 223 | 97.345% / 98.655% | 94.068% / 99.552% | 97.797% / 99.552% |
| dasia+acute | 102 | 97.115% / 99.020% | 95.283% / 99.020% | 96.190% / 99.020% |
| dasia+circumflex | 18 | 87.500% / 77.778% | 85.714% / 66.667% | 100.000% / 72.222% |
| dasia+circumflex+subscript | 3 | 100.000% / 33.333% | 100.000% / 33.333% | 100.000% / 66.667% |
| dasia+grave | 7 | 87.500% / 100.000% | 87.500% / 100.000% | 87.500% / 100.000% |
| dialytika | 1 | 100.000% / 100.000% | 100.000% / 100.000% | 100.000% / 100.000% |
| dialytika+acute | 3 | 100.000% / 100.000% | 100.000% / 100.000% | 100.000% / 100.000% |
| grave | 661 | 99.547% / 99.697% | 99.695% / 98.941% | 99.394% / 99.244% |
| none | 14228 | 98.565% / 99.909% | 98.531% / 99.972% | 98.565% / 99.944% |
| psili | 646 | 98.767% / 99.226% | 99.532% / 98.762% | 98.921% / 99.381% |
| psili+acute | 268 | 97.436% / 99.254% | 98.507% / 98.507% | 99.251% / 98.881% |
| psili+acute+subscript | 1 | — / 0.000% | — / 0.000% | — / 0.000% |
| psili+circumflex | 40 | 90.476% / 95.000% | 97.297% / 90.000% | 84.444% / 95.000% |
| psili+grave | 11 | 76.923% / 90.909% | 84.615% / 100.000% | 78.571% / 100.000% |
| subscript | 49 | 97.959% / 97.959% | 100.000% / 95.918% | 100.000% / 97.959% |

### without_overlay: capitals, compounds and paired churn

| Model | Capital detection P / R | Capital naming P / R / F1 | Marked capitals | Subscript P / R | Dialytika P / R |
| --- | --- | --- | --- | --- | --- |
| A16 | 89.320% / 98.925% | 98.913% / 97.849% / 98.378% | 93 | 95.652% / 93.617% | 66.667% / 100.000% |
| s17 | 97.895% / 100.000% | 97.849% / 97.849% / 97.849% | 93 | 96.552% / 89.362% | 80.000% / 100.000% |
| s18 | 92.929% / 98.925% | 98.913% / 97.849% / 98.378% | 93 | 96.739% / 94.681% | 80.000% / 100.000% |

Physical ledger exact-set changes versus A (all known physical slots, apostrophes retained):

| Pair | Old right → new wrong | Old wrong → new right | Both wrong, changed |
| --- | --- | --- | --- |
| s17 | 31 | 19 | 5 |
| s18 | 17 | 17 | 8 |

Seed17→18 physical changes: {'old_wrong_new_right': 31, 'old_right_new_wrong': 19, 'both_wrong_changed': 10}. Complete slot ledgers carry line, physical slot, base, truth, old/new marks and direction; union/head paired ledgers with document bootstrap intervals are in [full scores](evidence/job1/scores.json).

### without_overlay: raw exact named head confusion

Rows are printed truth, columns predicted. Alphabetic union, mark-blind and case-preserving alignment; unmatched print positives are FN, inserted predicted positives FP. This uses the frozen physical-truth adapter, not newly adjudicated complete line truth. UNKNOWN and coverage counts are preserved in the machine-readable result. Compounds are separate exact tuples.

| Model | Union slots | Covered | UNKNOWN | Unmatched print | Inserted prediction |
| --- | --- | --- | --- | --- | --- |
| A16 | 20487 | 11329 | 924 | 62 | 1334 |
| s17 | 20487 | 11329 | 924 | 62 | 1334 |
| s18 | 20487 | 11329 | 924 | 62 | 1334 |

The union adapter has 1,334 inserted prediction slots against the physical alphabetic base sequence; this changes the denominator and contributes false positives compared with the continuity mapping. These are instrument results, not a certification of complete independently printed line truth. Held-out exports lack crop-validity flags, so absent clipped/localisation flags must not be interpreted as verified clean crops.

**A16, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18124 | 85 | 32 |
| psili | 7 | 958 | 1 |
| dasia | 1 | 5 | 350 |

**s17, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18129 | 77 | 35 |
| psili | 9 | 951 | 6 |
| dasia | 1 | 2 | 353 |

**s18, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18125 | 84 | 32 |
| psili | 7 | 957 | 2 |
| dasia | 1 | 7 | 348 |

**A16, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16371 | 169 | 96 | 50 |
| acute | 7 | 1786 | 2 | 0 |
| grave | 3 | 1 | 674 | 1 |
| circumflex | 4 | 2 | 2 | 395 |

**s17, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16375 | 171 | 94 | 46 |
| acute | 8 | 1783 | 2 | 2 |
| grave | 4 | 4 | 670 | 1 |
| circumflex | 14 | 2 | 2 | 385 |

**s18, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16374 | 168 | 95 | 49 |
| acute | 7 | 1785 | 2 | 1 |
| grave | 5 | 2 | 672 | 0 |
| circumflex | 5 | 3 | 5 | 390 |

**A16, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19557 | 2 |
| dialytika | 0 | 4 |

**s17, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19558 | 1 |
| dialytika | 0 | 4 |

**s18, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19558 | 1 |
| dialytika | 0 | 4 |

**A16, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19465 | 4 |
| subscript | 6 | 88 |

**s17, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19466 | 3 |
| subscript | 10 | 84 |

**s18, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19466 | 3 |
| subscript | 5 | 89 |

**A16, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19557 | 1 | 1 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |

**s17, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19558 | 1 | 0 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |

**s18, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19558 | 1 | 0 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |


### v1_1: exact composed classes

| Class | Support | A16 P / R | s17 P / R | s18 P / R |
| --- | --- | --- | --- | --- |
| acute | 1418 | 99.859% / 99.859% | 99.298% / 99.718% | 99.508% / 99.929% |
| acute+subscript | 2 | 100.000% / 50.000% | — / 0.000% | 100.000% / 50.000% |
| circumflex | 303 | 99.669% / 99.340% | 98.671% / 98.020% | 99.662% / 97.360% |
| circumflex+subscript | 39 | 100.000% / 100.000% | 100.000% / 94.872% | 100.000% / 100.000% |
| dasia | 223 | 97.345% / 98.655% | 94.068% / 99.552% | 97.797% / 99.552% |
| dasia+acute | 102 | 97.115% / 99.020% | 95.283% / 99.020% | 96.190% / 99.020% |
| dasia+circumflex | 18 | 87.500% / 77.778% | 85.714% / 66.667% | 100.000% / 72.222% |
| dasia+circumflex+subscript | 3 | 100.000% / 33.333% | 100.000% / 33.333% | 100.000% / 66.667% |
| dasia+grave | 7 | 87.500% / 100.000% | 87.500% / 100.000% | 87.500% / 100.000% |
| dialytika | 1 | 100.000% / 100.000% | 100.000% / 100.000% | 100.000% / 100.000% |
| dialytika+acute | 3 | 100.000% / 100.000% | 100.000% / 100.000% | 100.000% / 100.000% |
| grave | 661 | 99.547% / 99.697% | 99.695% / 98.941% | 99.394% / 99.244% |
| none | 14228 | 98.565% / 99.909% | 98.531% / 99.972% | 98.565% / 99.944% |
| psili | 646 | 98.767% / 99.226% | 99.532% / 98.762% | 98.921% / 99.381% |
| psili+acute | 267 | 97.436% / 99.625% | 98.507% / 98.876% | 99.251% / 99.251% |
| psili+acute+subscript | 1 | — / 0.000% | — / 0.000% | — / 0.000% |
| psili+circumflex | 41 | 90.476% / 92.683% | 97.297% / 87.805% | 84.444% / 92.683% |
| psili+grave | 11 | 76.923% / 90.909% | 84.615% / 100.000% | 78.571% / 100.000% |
| subscript | 49 | 97.959% / 97.959% | 100.000% / 95.918% | 100.000% / 97.959% |

### v1_1: capitals, compounds and paired churn

| Model | Capital detection P / R | Capital naming P / R / F1 | Marked capitals | Subscript P / R | Dialytika P / R |
| --- | --- | --- | --- | --- | --- |
| A16 | 89.320% / 98.925% | 98.913% / 97.849% / 98.378% | 93 | 95.652% / 93.617% | 66.667% / 100.000% |
| s17 | 97.895% / 100.000% | 97.849% / 97.849% / 97.849% | 93 | 96.552% / 89.362% | 80.000% / 100.000% |
| s18 | 92.929% / 98.925% | 98.913% / 97.849% / 98.378% | 93 | 96.739% / 94.681% | 80.000% / 100.000% |

Physical ledger exact-set changes versus A (all known physical slots, apostrophes retained):

| Pair | Old right → new wrong | Old wrong → new right | Both wrong, changed |
| --- | --- | --- | --- |
| s17 | 31 | 19 | 5 |
| s18 | 17 | 17 | 8 |

Seed17→18 physical changes: {'old_wrong_new_right': 31, 'old_right_new_wrong': 19, 'both_wrong_changed': 10}. Complete slot ledgers carry line, physical slot, base, truth, old/new marks and direction; union/head paired ledgers with document bootstrap intervals are in [full scores](evidence/job1/scores.json).

### v1_1: raw exact named head confusion

Rows are printed truth, columns predicted. Alphabetic union, mark-blind and case-preserving alignment; unmatched print positives are FN, inserted predicted positives FP. This uses the frozen physical-truth adapter, not newly adjudicated complete line truth. UNKNOWN and coverage counts are preserved in the machine-readable result. Compounds are separate exact tuples.

| Model | Union slots | Covered | UNKNOWN | Unmatched print | Inserted prediction |
| --- | --- | --- | --- | --- | --- |
| A16 | 20487 | 11329 | 924 | 62 | 1334 |
| s17 | 20487 | 11329 | 924 | 62 | 1334 |
| s18 | 20487 | 11329 | 924 | 62 | 1334 |

The union adapter has 1,334 inserted prediction slots against the physical alphabetic base sequence; this changes the denominator and contributes false positives compared with the continuity mapping. These are instrument results, not a certification of complete independently printed line truth. Held-out exports lack crop-validity flags, so absent clipped/localisation flags must not be interpreted as verified clean crops.

**A16, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18124 | 85 | 32 |
| psili | 7 | 958 | 1 |
| dasia | 1 | 5 | 350 |

**s17, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18129 | 77 | 35 |
| psili | 9 | 951 | 6 |
| dasia | 1 | 2 | 353 |

**s18, breathing**

| Truth / prediction | none | psili | dasia |
| --- | --- | --- | --- |
| none | 18125 | 84 | 32 |
| psili | 7 | 957 | 2 |
| dasia | 1 | 7 | 348 |

**A16, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16371 | 169 | 96 | 50 |
| acute | 7 | 1785 | 2 | 0 |
| grave | 3 | 1 | 674 | 1 |
| circumflex | 4 | 3 | 2 | 395 |

**s17, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16375 | 171 | 94 | 46 |
| acute | 8 | 1782 | 2 | 2 |
| grave | 4 | 4 | 670 | 1 |
| circumflex | 14 | 3 | 2 | 385 |

**s18, accent**

| Truth / prediction | none | acute | grave | circumflex |
| --- | --- | --- | --- | --- |
| none | 16374 | 168 | 95 | 49 |
| acute | 7 | 1784 | 2 | 1 |
| grave | 5 | 2 | 672 | 0 |
| circumflex | 5 | 4 | 5 | 390 |

**A16, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19557 | 2 |
| dialytika | 0 | 4 |

**s17, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19558 | 1 |
| dialytika | 0 | 4 |

**s18, dialytika**

| Truth / prediction | none | dialytika |
| --- | --- | --- |
| none | 19558 | 1 |
| dialytika | 0 | 4 |

**A16, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19465 | 4 |
| subscript | 6 | 88 |

**s17, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19466 | 3 |
| subscript | 10 | 84 |

**s18, subscript**

| Truth / prediction | none | subscript |
| --- | --- | --- |
| none | 19466 | 3 |
| subscript | 5 | 89 |

**A16, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19557 | 1 | 1 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |

**s17, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19558 | 1 | 0 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |

**s18, dialytika compounds**

| Truth / prediction | none | dialytika-only | dialytika+acute | dialytika+grave | dialytika+circumflex |
| --- | --- | --- | --- | --- | --- |
| none | 19558 | 1 | 0 | 0 | 0 |
| dialytika-only | 0 | 1 | 0 | 0 | 0 |
| dialytika+acute | 0 | 0 | 3 | 0 | 0 |
| dialytika+grave | 0 | 0 | 0 | 0 | 0 |
| dialytika+circumflex | 0 | 0 | 0 | 0 | 0 |

BASE seed churn: **81 / 11,329 extraction slots** have different four-head tuples between seeds 17 and 18, independent of overlays. This observed spread is the BASE noise-floor instrument for future paired non-target comparisons; no criterion is declared passed. Full per-book results and UNKNOWN counts remain in scores.json.

## R2S rescore

**Comparison flag:** s18's paired union tuple accuracy versus A16 changes from a tie (0) to −0.000164573; s17 stays negative (−0.000511169 → −0.000658292). Four-head F1 comparisons keep their sign: both BASE seeds remain below A16. Precision comparisons also keep their signs (s17 above A16, s18 below); recall is unchanged.

Inserted recogniser slots now have UNKNOWN truth on all four heads. They contribute to no confusion cell, tuple denominator, compound score or paired error ledger. Print-truth None remains UNKNOWN, and missing predictions on known truth still score as before. The earlier tables and `scores.json` retain the historical scorer results; the corrected symmetric **overlay v1.1** results are in [scores_r2s.json](evidence/job1/scores_r2s.json).

| Arm | Four-head P old → new | R old → new | F1 old → new | Matched-slot FP |
| --- | --- | --- | --- | --- |
| A16 | 90.376% → 98.907% | 98.999% → 98.999% | 94.491% → 98.953% | 47 |
| s17 | 90.402% → 98.947% | 98.418% → 98.418% | 94.240% → 98.682% | 45 |
| s18 | 90.317% → 98.836% | 98.767% → 98.767% | 94.353% → 98.801% | 50 |

Each arm has 1,334 inserted slots, separate from 924 print-truth UNKNOWN slots (2,258 UNKNOWN total). Marked inserted letters number 366/364/363 for A16/s17/s18; their head counts (breathing/accent/dialytika/subscript) are 101/300/2/3, 102/298/1/3 and 102/299/1/3. These are diagnostics, never errors; per-letter and per-head details are in the new JSON. Removing them eliminates 406/404/405 FPs. The expected approximate 46/44/49 matched FPs use pre-v1.1 truth: v1.1's acute→circumflex correction adds one FP per arm, giving 47/45/50. TP and FN are unchanged by R2S. Continuity results match the saved scores exactly.

Input discrepancy: this worktree's HEAD is `8897a861b` rather than the requested `d891bcaa3`; `artifacts/labelfix_r2/scorer_inputs/` contains a one-line synthetic fixture. The rescore therefore uses the saved job-3681404 exports, receipt-bound frozen A16 predictions and held-out metadata, and frozen S4 truth used by the original digest. Reinstating the old insertion default reproduces every arm's historical atomic counts exactly. Input/code hashes and comparisons are recorded in the new JSON; [rescore_r2s.py](evidence/job1/rescore_r2s.py) reproduces it offline from the worktree root with `PYTHONPATH=.`.

Validation: **31 tests passed** (`test_r2.py`, `test_r2_readback_digest.py`, `test_policy_frozen_after_merge.py`). New tests verify marked insertions leave head P/R, confusion matrices, tuple/compound scores and paired error counts unchanged, and deletion-side positives remain FN. Changed expectations: `test_union_missing_print_positive_and_inserted_prediction` now expects FP 0 and breathing false-addition rate 0 instead of FP 1/rate 500; `test_case_preserving_and_mark_blind_names` now expects FP 0 instead of 1 for the inserted lowercase substitution. Both preserve the missing-truth-side FN.

Deploy manifests updated: `R2_DEPLOY_SHA256.txt` and `docs/records/labelfix/spellcheck/R2/R2_DEPLOY_SHA256.txt` carry the current scorer and test hashes for the later R2a + DEV package. Nothing deployed; network OFF, no inference, no `.git` writes. `greekocr/labelfix` and all 16 policy paths remain unchanged; policy digest remains `6f62925a`.

## DEV

**DEV pending: needs window extraction on Clariden for 600 lines** in the S8 DEV census (600 total; supplied truth has cards on 542 lines, including 527 with noncontrol cards). [Exact line list](evidence/job1/DEV_required_lines.txt), [one-stage job specification](evidence/job1/DEV_pending.json). S8 truth is a sampled word/card instrument, not complete line truth; keep its original inclusion weights, waves, controls and UNKNOWN policy. The exact crop/label/wave selection is in [DEV selection](evidence/job1/DEV_selection.jsonl). Saved A forms alone cannot establish paired BASE metrics. Inspected this worktree and the S8/original spellcheck extraction inventories; no matching BASE DEV predictions or complete DEV reader windows were available. No new cohort extraction/inference or submission was performed. The 20-min job cap is provisional; native crop/alignment paths and hashes must be bound before any coordinator submission.

## Validation

All **1,477 labelfix tests passed**, including 10 new readback/digest regressions; see [test log](evidence/job1/tests.log). The R2 physical-truth adapter now expands compound atoms before factorisation; a real frozen-witness regression verifies all overlay versions. The historical continuity scorer and frozen runtime remain unchanged.

Final F1 below uses the symmetric v1.1 continuity column; without-overlay values are tabulated above.

R2RB READY: readback 17730/458783338 sha ok 17730/17730; stages A 0.000002 B 15.875 C 17.482 min vs forecast 74; teacher rows 1232387 (717612/121392/226680/166703); BASE F1 s17 96.260% s18 96.506% vs A 96.609%; seed churn 81 slots; DEV pending
