# CP7b adjudication sheet

Reader labels are provisional owner-standard truth; the lead has not yet adjudicated pixels. No new reading was performed for CP7b.

Includes every FP/FN for union **or any standalone screen**, plus any letters/marks/crop_ok n/u, errors, nonempty detail, explicit flag, or unreadable. Controls are reported separately; none missed. Unknown-axis and unavailable-geometry rows are listed in the receipt even when they need no adjudication.

Crop paths below point to the original CP7a public packs; repository copies were checked byte-identical. Full sealed evidence is retained in `scored_cp7b.jsonl.gz`. Contact sheets are previews; use original crops for the lead pixel check.

## gazette_modern--27c637eaf14409d5--s000-l0054

Card `kde8215c76d`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/763dffc42fbe541ba040c8db85761a616db1f18ab01f2b2a0d50d79a11f774b9.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/763dffc42fbe541ba040c8db85761a616db1f18ab01f2b2a0d50d79a11f774b9.png`; SHA-256 `763dffc42fbe541ba040c8db85761a616db1f18ab01f2b2a0d50d79a11f774b9`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kde8215c76d",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Only clipped portions of the lower neighbouring line are visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line remains within one column and both ends are visible.",
  "line_id": "gazette_modern--27c637eaf14409d5--s000-l0054"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00047",
  "neighbour_rows": [
    {
      "row_id": "row-00048",
      "column_id": "single:column-0000",
      "xheight": 13.87067839434701,
      "profile_runs": [
        [
          65,
          75
        ],
        [
          79,
          92
        ],
        [
          94,
          106
        ],
        [
          108,
          121
        ],
        [
          123,
          128
        ],
        [
          145,
          154
        ],
        [
          155,
          177
        ],
        [
          179,
          183
        ],
        [
          200,
          252
        ],
        [
          253,
          263
        ],
        [
          264,
          269
        ],
        [
          270,
          282
        ],
        [
          283,
          295
        ],
        [
          296,
          307
        ],
        [
          308,
          312
        ],
        [
          330,
          341
        ],
        [
          342,
          355
        ],
        [
          356,
          366
        ],
        [
          367,
          377
        ],
        [
          379,
          384
        ],
        [
          385,
          397
        ],
        [
          398,
          409
        ],
        [
          410,
          420
        ],
        [
          436,
          451
        ],
        [
          454,
          466
        ],
        [
          468,
          479
        ],
        [
          481,
          530
        ],
        [
          546,
          553
        ],
        [
          569,
          583
        ],
        [
          584,
          594
        ],
        [
          596,
          608
        ],
        [
          609,
          621
        ],
        [
          622,
          632
        ],
        [
          633,
          643
        ],
        [
          644,
          665
        ],
        [
          666,
          676
        ],
        [
          692,
          706
        ],
        [
          707,
          712
        ],
        [
          728,
          741
        ],
        [
          742,
          752
        ],
        [
          753,
          763
        ],
        [
          764,
          777
        ],
        [
          779,
          783
        ]
      ],
      "profile_gaps": [
        [
          75,
          79
        ],
        [
          92,
          94
        ],
        [
          106,
          108
        ],
        [
          121,
          123
        ],
        [
          128,
          145
        ],
        [
          154,
          155
        ],
        [
          177,
          179
        ],
        [
          183,
          200
        ],
        [
          252,
          253
        ],
        [
          263,
          264
        ],
        [
          269,
          270
        ],
        [
          282,
          283
        ],
        [
          295,
          296
        ],
        [
          307,
          308
        ],
        [
          312,
          330
        ],
        [
          341,
          342
        ],
        [
          355,
          356
        ],
        [
          366,
          367
        ],
        [
          377,
          379
        ],
        [
          384,
          385
        ],
        [
          397,
          398
        ],
        [
          409,
          410
        ],
        [
          420,
          436
        ],
        [
          451,
          454
        ],
        [
          466,
          468
        ],
        [
          479,
          481
        ],
        [
          530,
          546
        ],
        [
          553,
          569
        ],
        [
          583,
          584
        ],
        [
          594,
          596
        ],
        [
          608,
          609
        ],
        [
          621,
          622
        ],
        [
          632,
          633
        ],
        [
          643,
          644
        ],
        [
          665,
          666
        ],
        [
          676,
          692
        ],
        [
          706,
          707
        ],
        [
          712,
          728
        ],
        [
          741,
          742
        ],
        [
          752,
          753
        ],
        [
          763,
          764
        ],
        [
          777,
          779
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 19362
      },
      "groups": [
        {
          "box": [
            65,
            1127,
            183,
            1150
          ],
          "body_count": 8,
          "width_xh": 8.507154202932918,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            200,
            1129,
            420,
            1156
          ],
          "body_count": 18,
          "width_xh": 15.86079597156985,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            436,
            1132,
            530,
            1159
          ],
          "body_count": 6,
          "width_xh": 6.7768855514889355,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            569,
            1134,
            676,
            1160
          ],
          "body_count": 9,
          "width_xh": 7.714114404354427,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            692,
            1136,
            712,
            1159
          ],
          "body_count": 2,
          "width_xh": 1.4418905428699862,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      85,
      1094,
      787,
      1138
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00047"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00047"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00047",
      "column_id": "single:column-0000",
      "xheight": 13.48576039416696,
      "assigned_pixels": 4536,
      "supported": null,
      "runs": [
        {
          "x0": 93,
          "x1": 105,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 108,
          "x1": 113,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 123,
          "x1": 136,
          "body_cut_fraction": 0.0,
          "body_pixels": 104,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 137,
          "x1": 149,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 151,
          "x1": 177,
          "body_cut_fraction": 0.0,
          "body_pixels": 176,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 178,
          "x1": 189,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 190,
          "x1": 200,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 201,
          "x1": 214,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 223,
          "x1": 233,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 235,
          "x1": 245,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 247,
          "x1": 256,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 258,
          "x1": 262,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 272,
          "x1": 290,
          "body_cut_fraction": 0.0,
          "body_pixels": 121,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 292,
          "x1": 301,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 303,
          "x1": 315,
          "body_cut_fraction": 0.0,
          "body_pixels": 91,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 317,
          "x1": 353,
          "body_cut_fraction": 0.0,
          "body_pixels": 216,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 363,
          "x1": 382,
          "body_cut_fraction": 0.0,
          "body_pixels": 132,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 384,
          "x1": 389,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 390,
          "x1": 401,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 402,
          "x1": 412,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 415,
          "x1": 419,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 421,
          "x1": 431,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 433,
          "x1": 443,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 445,
          "x1": 449,
          "body_cut_fraction": 0.0,
          "body_pixels": 17,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 459,
          "x1": 472,
          "body_cut_fraction": 0.0,
          "body_pixels": 94,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 474,
          "x1": 484,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 486,
          "x1": 495,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 504,
          "x1": 517,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 519,
          "x1": 527,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 528,
          "x1": 561,
          "body_cut_fraction": 0.0,
          "body_pixels": 202,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 563,
          "x1": 572,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 574,
          "x1": 586,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 588,
          "x1": 599,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 600,
          "x1": 609,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 618,
          "x1": 652,
          "body_cut_fraction": 0.0,
          "body_pixels": 221,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 653,
          "x1": 663,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 672,
          "x1": 688,
          "body_cut_fraction": 0.0,
          "body_pixels": 116,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 690,
          "x1": 702,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 704,
          "x1": 716,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 717,
          "x1": 741,
          "body_cut_fraction": 0.0,
          "body_pixels": 151,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 742,
          "x1": 755,
          "body_cut_fraction": 0.0,
          "body_pixels": 93,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 763,
          "x1": 773,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 774,
          "x1": 784,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00048",
      "column_id": "single:column-0000",
      "xheight": 13.87067839434701,
      "assigned_pixels": 603,
      "supported": null,
      "runs": [
        {
          "x0": 85,
          "x1": 92,
          "body_cut_fraction": 0.4021786908743423,
          "body_pixels": 33,
          "body_extent_px": 8,
          "complete": false
        },
        {
          "x0": 94,
          "x1": 106,
          "body_cut_fraction": 0.43199554069119317,
          "body_pixels": 42,
          "body_extent_px": 8,
          "complete": false
        },
        {
          "x0": 108,
          "x1": 121,
          "body_cut_fraction": 0.4764291227167481,
          "body_pixels": 40,
          "body_extent_px": 8,
          "complete": false
        },
        {
          "x0": 145,
          "x1": 154,
          "body_cut_fraction": 0.5569379412857693,
          "body_pixels": 18,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 155,
          "x1": 177,
          "body_cut_fraction": 0.5708878078443305,
          "body_pixels": 59,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 200,
          "x1": 251,
          "body_cut_fraction": 0.6730652463955824,
          "body_pixels": 67,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 253,
          "x1": 263,
          "body_cut_fraction": 0.793863703130486,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 264,
          "x1": 269,
          "body_cut_fraction": 0.8317862737135269,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 270,
          "x1": 282,
          "body_cut_fraction": 0.8738220183823282,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 283,
          "x1": 291,
          "body_cut_fraction": 0.9132999692453948,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 109,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "60c0e633467a8c55c53dcccc1d664f5a378c16a21415a44e086126c697adb212"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.8377184889359961,
    "polarity_confidence": 0.4,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--288c8a27405ee9c3--s000-l0084

Card `kf43a61e87f`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/ae72a06f9d1a50a6ad08f75f3929178c9be040f8cf80448d3af28103b872a0e1.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/ae72a06f9d1a50a6ad08f75f3929178c9be040f8cf80448d3af28103b872a0e1.png`; SHA-256 `ae72a06f9d1a50a6ad08f75f3929178c9be040f8cf80448d3af28103b872a0e1`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kf43a61e87f",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Clipped neighbouring letter portions do not form a complete word.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--288c8a27405ee9c3--s000-l0084"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00081",
  "neighbour_rows": [
    {
      "row_id": "row-00080",
      "column_id": "single:column-0000",
      "xheight": 11.802878610360267,
      "profile_runs": [
        [
          850,
          862
        ],
        [
          864,
          873
        ],
        [
          875,
          879
        ],
        [
          881,
          890
        ],
        [
          892,
          904
        ],
        [
          905,
          915
        ],
        [
          928,
          952
        ],
        [
          953,
          963
        ],
        [
          964,
          973
        ],
        [
          975,
          991
        ],
        [
          992,
          1002
        ],
        [
          1004,
          1013
        ],
        [
          1026,
          1038
        ],
        [
          1040,
          1052
        ],
        [
          1055,
          1066
        ],
        [
          1069,
          1080
        ],
        [
          1083,
          1092
        ],
        [
          1095,
          1108
        ],
        [
          1109,
          1121
        ],
        [
          1124,
          1133
        ],
        [
          1136,
          1150
        ],
        [
          1152,
          1161
        ],
        [
          1165,
          1176
        ],
        [
          1179,
          1191
        ],
        [
          1193,
          1202
        ],
        [
          1205,
          1217
        ],
        [
          1219,
          1232
        ],
        [
          1234,
          1246
        ],
        [
          1259,
          1269
        ],
        [
          1270,
          1280
        ],
        [
          1282,
          1294
        ],
        [
          1295,
          1306
        ],
        [
          1308,
          1324
        ],
        [
          1325,
          1334
        ],
        [
          1335,
          1347
        ],
        [
          1359,
          1372
        ],
        [
          1373,
          1381
        ],
        [
          1393,
          1425
        ],
        [
          1437,
          1449
        ],
        [
          1450,
          1462
        ],
        [
          1463,
          1473
        ],
        [
          1486,
          1498
        ],
        [
          1500,
          1513
        ],
        [
          1515,
          1519
        ],
        [
          1521,
          1533
        ],
        [
          1537,
          1540
        ],
        [
          1543,
          1555
        ],
        [
          1557,
          1569
        ]
      ],
      "profile_gaps": [
        [
          862,
          864
        ],
        [
          873,
          875
        ],
        [
          879,
          881
        ],
        [
          890,
          892
        ],
        [
          904,
          905
        ],
        [
          915,
          928
        ],
        [
          952,
          953
        ],
        [
          963,
          964
        ],
        [
          973,
          975
        ],
        [
          991,
          992
        ],
        [
          1002,
          1004
        ],
        [
          1013,
          1026
        ],
        [
          1038,
          1040
        ],
        [
          1052,
          1055
        ],
        [
          1066,
          1069
        ],
        [
          1080,
          1083
        ],
        [
          1092,
          1095
        ],
        [
          1108,
          1109
        ],
        [
          1121,
          1124
        ],
        [
          1133,
          1136
        ],
        [
          1150,
          1152
        ],
        [
          1161,
          1165
        ],
        [
          1176,
          1179
        ],
        [
          1191,
          1193
        ],
        [
          1202,
          1205
        ],
        [
          1217,
          1219
        ],
        [
          1232,
          1234
        ],
        [
          1246,
          1259
        ],
        [
          1269,
          1270
        ],
        [
          1280,
          1282
        ],
        [
          1294,
          1295
        ],
        [
          1306,
          1308
        ],
        [
          1324,
          1325
        ],
        [
          1334,
          1335
        ],
        [
          1347,
          1359
        ],
        [
          1372,
          1373
        ],
        [
          1381,
          1393
        ],
        [
          1425,
          1437
        ],
        [
          1449,
          1450
        ],
        [
          1462,
          1463
        ],
        [
          1473,
          1486
        ],
        [
          1498,
          1500
        ],
        [
          1513,
          1515
        ],
        [
          1519,
          1521
        ],
        [
          1533,
          1537
        ],
        [
          1540,
          1543
        ],
        [
          1555,
          1557
        ]
      ],
      "directional_missing": {
        "above": 11208,
        "below": 0
      },
      "groups": [
        {
          "box": [
            850,
            524,
            915,
            549
          ],
          "body_count": 6,
          "width_xh": 5.507131111468405,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            928,
            531,
            1013,
            550
          ],
          "body_count": 7,
          "width_xh": 7.2016329919202215,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1026,
            526,
            1246,
            553
          ],
          "body_count": 16,
          "width_xh": 18.639520684969987,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1259,
            537,
            1347,
            555
          ],
          "body_count": 7,
          "width_xh": 7.455808273987994,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      845,
      546,
      1338,
      584
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00081"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00081"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00080",
      "column_id": "single:column-0000",
      "xheight": 11.802878610360267,
      "assigned_pixels": 276,
      "supported": null,
      "runs": [
        {
          "x0": 1153,
          "x1": 1160,
          "body_cut_fraction": 0.9712663850594883,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1165,
          "x1": 1176,
          "body_cut_fraction": 0.9467007617477841,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1179,
          "x1": 1191,
          "body_cut_fraction": 0.9237824251239113,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1194,
          "x1": 1201,
          "body_cut_fraction": 0.9104222897326353,
          "body_pixels": 4,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1205,
          "x1": 1217,
          "body_cut_fraction": 0.8981318045102165,
          "body_pixels": 11,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1219,
          "x1": 1232,
          "body_cut_fraction": 0.880784947568057,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1234,
          "x1": 1246,
          "body_cut_fraction": 0.8584097038846613,
          "body_pixels": 9,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1259,
          "x1": 1269,
          "body_cut_fraction": 0.8046598322460388,
          "body_pixels": 10,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1270,
          "x1": 1280,
          "body_cut_fraction": 0.7792877900819308,
          "body_pixels": 11,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1282,
          "x1": 1294,
          "body_cut_fraction": 0.7610265824125377,
          "body_pixels": 25,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1295,
          "x1": 1306,
          "body_cut_fraction": 0.7529903799496271,
          "body_pixels": 19,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1308,
          "x1": 1324,
          "body_cut_fraction": 0.7508723993497364,
          "body_pixels": 34,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1325,
          "x1": 1334,
          "body_cut_fraction": 0.7551754328158709,
          "body_pixels": 8,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1335,
          "x1": 1338,
          "body_cut_fraction": 0.7558178942611852,
          "body_pixels": 6,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00081",
      "column_id": "single:column-0000",
      "xheight": 11.855798029307948,
      "assigned_pixels": 2808,
      "supported": null,
      "runs": [
        {
          "x0": 850,
          "x1": 862,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 863,
          "x1": 875,
          "body_cut_fraction": 0.0,
          "body_pixels": 80,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 876,
          "x1": 886,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 888,
          "x1": 899,
          "body_cut_fraction": 0.0,
          "body_pixels": 79,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 900,
          "x1": 912,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 913,
          "x1": 931,
          "body_cut_fraction": 0.0,
          "body_pixels": 110,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 932,
          "x1": 935,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 946,
          "x1": 967,
          "body_cut_fraction": 0.0,
          "body_pixels": 123,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 968,
          "x1": 978,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 989,
          "x1": 995,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1003,
          "x1": 1011,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1012,
          "x1": 1021,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1023,
          "x1": 1027,
          "body_cut_fraction": 0.0,
          "body_pixels": 13,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1038,
          "x1": 1052,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1053,
          "x1": 1072,
          "body_cut_fraction": 0.0,
          "body_pixels": 115,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1074,
          "x1": 1082,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1083,
          "x1": 1102,
          "body_cut_fraction": 0.0,
          "body_pixels": 114,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1104,
          "x1": 1114,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1115,
          "x1": 1137,
          "body_cut_fraction": 0.0,
          "body_pixels": 153,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1139,
          "x1": 1148,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1158,
          "x1": 1167,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1169,
          "x1": 1184,
          "body_cut_fraction": 0.0,
          "body_pixels": 93,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1185,
          "x1": 1194,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1205,
          "x1": 1218,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1219,
          "x1": 1237,
          "body_cut_fraction": 0.0,
          "body_pixels": 115,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1238,
          "x1": 1248,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1249,
          "x1": 1260,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1262,
          "x1": 1278,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1279,
          "x1": 1288,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1298,
          "x1": 1320,
          "body_cut_fraction": 0.0,
          "body_pixels": 129,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1321,
          "x1": 1330,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1333,
          "x1": 1336,
          "body_cut_fraction": 0.0,
          "body_pixels": 10,
          "body_extent_px": 4,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 126,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.572317739635996,
        "required_common_rows": 2.3605757220720536,
        "xheight_px": 11.802878610360267,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          850,
          521.994,
          1338,
          555.96
        ],
        "boundary_path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "row_id": "row-00080"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.622397876469689,
        "required_common_rows": 2.37115960586159,
        "xheight_px": 11.855798029307948,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          850,
          549.337,
          1336,
          583.472
        ],
        "boundary_path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "row_id": "row-00081"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "width": 30,
        "extent": [
          804,
          1728,
          834,
          1992
        ],
        "source": "detector",
        "proposal_id": "proposal-0006",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 11.916477220731394,
          "width_xh": 2.51752253995067,
          "required_width_px": 17.87471583109709,
          "spacing_sides": [
            {
              "samples": 74,
              "letter_q25_xh": 0.08586565293489502,
              "median_xh": 0.16968501280117906,
              "word_q75_xh": 0.17389930563561726,
              "q90_xh": 0.462246801457529
            },
            {
              "samples": 50,
              "letter_q25_xh": 0.08587437834100385,
              "median_xh": 0.16783483599671134,
              "word_q75_xh": 0.2615305933499593,
              "q90_xh": 0.7570180262935844
            }
          ],
          "side_row_counts": [
            8,
            6
          ],
          "side_span_xh": [
            19.15801085935259,
            15.753565128577321
          ],
          "shared_span_xh": 15.753565128577321,
          "occupied_rows": 11,
          "bilateral_rows": 7,
          "participants": [
            {
              "line_index": 112,
              "xheight": 11.500908486608523
            },
            {
              "line_index": 113,
              "xheight": 11.76368880264613
            },
            {
              "line_index": 114,
              "xheight": 11.5380847210389
            },
            {
              "line_index": 115,
              "xheight": 11.608473727100545
            },
            {
              "line_index": 116,
              "xheight": 11.646100225409327
            },
            {
              "line_index": 117,
              "xheight": 11.405116480082143
            },
            {
              "line_index": 118,
              "xheight": 11.786544768944395
            },
            {
              "line_index": 120,
              "xheight": 11.67743940148307
            },
            {
              "line_index": 121,
              "xheight": 11.806868066662219
            },
            {
              "line_index": 123,
              "xheight": 11.552267431804466
            },
            {
              "line_index": 124,
              "xheight": 11.444075871056157
            },
            {
              "line_index": 125,
              "xheight": 11.916477220731394
            },
            {
              "line_index": 126,
              "xheight": 11.644916904423326
            },
            {
              "line_index": 127,
              "xheight": 11.768330411588067
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            62,
            0.0,
            0.0,
            66,
            66,
            72,
            49,
            0.0,
            123,
            123
          ],
          "white_rows": 7,
          "baseline_matching_reach_px": 13.125499999999988,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "51c27ed949896ec4c16f4d3af370b1b3e4e821916c88ce49decd17b8c3d63572"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.9365792914870877,
    "polarity_confidence": 1.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## elstat--0a2c92120843658d--s000-l0191

Card `k37078da342`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/67e16a0952ef92485b40afb350e4f9b434c48ac0bb9a37f5c3a59e1e8916712d.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/67e16a0952ef92485b40afb350e4f9b434c48ac0bb9a37f5c3a59e1e8916712d.png`; SHA-256 `67e16a0952ef92485b40afb350e4f9b434c48ac0bb9a37f5c3a59e1e8916712d`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k37078da342",
  "letters": "y",
  "marks": "na",
  "crop_ok": "y",
  "errors": [
    "punctuation"
  ],
  "detail": "1.197,5 → 1.197.5",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "elstat--0a2c92120843658d--s000-l0191"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00243",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      1069,
      1708,
      1164,
      1732
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00243"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0023",
        "row_ids": [
          "row-00243"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00243",
      "column_id": "single:column-0023",
      "xheight": 18.0,
      "assigned_pixels": 488,
      "supported": null,
      "runs": [
        {
          "x0": 1078,
          "x1": 1085,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1092,
          "x1": 1096,
          "body_cut_fraction": 0.0,
          "body_pixels": 11,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1100,
          "x1": 1108,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1112,
          "x1": 1123,
          "body_cut_fraction": 0.0,
          "body_pixels": 99,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1124,
          "x1": 1134,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1139,
          "x1": 1144,
          "body_cut_fraction": 0.0,
          "body_pixels": 23,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 1147,
          "x1": 1158,
          "body_cut_fraction": 0.0,
          "body_pixels": 97,
          "body_extent_px": 17,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 255,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            725.0,
            505.0
          ],
          [
            725.0,
            734.0
          ]
        ],
        "row_id": "row-00243"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            848.5,
            505.0
          ],
          [
            848.5,
            734.0
          ]
        ],
        "row_id": "row-00243"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            1105.5,
            505.0
          ],
          [
            1105.5,
            734.0
          ]
        ],
        "row_id": "row-00243"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            1328.5,
            505.0
          ],
          [
            1328.5,
            734.0
          ]
        ],
        "row_id": "row-00243"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            781.5,
            1568.0
          ],
          [
            781.5,
            1810.0
          ]
        ],
        "row_id": "row-00243"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0005",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 12.96,
        "required_common_rows": 3.6,
        "xheight_px": 18.0,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 231.0,
          "ink_q10": 71.0,
          "threshold": 151.0
        },
        "line_extent": [
          1078,
          1697.537,
          1158,
          1745.547
        ],
        "boundary_path": [
          [
            736.0,
            1810.0
          ],
          [
            736.0,
            2016.0
          ]
        ],
        "row_id": "row-00243"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            725.0,
            505.0
          ],
          [
            725.0,
            734.0
          ]
        ],
        "width": 38,
        "extent": [
          706,
          505,
          744,
          734
        ],
        "source": "detector",
        "proposal_id": "proposal-0000",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 38.0,
          "local_xheight_max_px": 17.5,
          "width_xh": 2.1714285714285713,
          "required_width_px": 26.25,
          "spacing_sides": [
            {
              "samples": 65,
              "letter_q25_xh": 0.1203796513069354,
              "median_xh": 0.23529411764705882,
              "word_q75_xh": 0.29411764705882354,
              "q90_xh": 0.6305000414473821
            },
            {
              "samples": 61,
              "letter_q25_xh": 0.17647058823529413,
              "median_xh": 0.25,
              "word_q75_xh": 0.35294117647058826,
              "q90_xh": 0.47349461582621144
            }
          ],
          "side_row_counts": [
            6,
            6
          ],
          "side_span_xh": [
            9.544171428571424,
            9.432657142857137
          ],
          "shared_span_xh": 9.432657142857137,
          "occupied_rows": 6,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 96,
              "xheight": 16.884267000731256
            },
            {
              "line_index": 98,
              "xheight": 16.509496668187126
            },
            {
              "line_index": 100,
              "xheight": 17.306246692625564
            },
            {
              "line_index": 102,
              "xheight": 17.0
            },
            {
              "line_index": 104,
              "xheight": 16.61410361540709
            },
            {
              "line_index": 106,
              "xheight": 17.0
            },
            {
              "line_index": 123,
              "xheight": 16.5
            },
            {
              "line_index": 124,
              "xheight": 17.0
            },
            {
              "line_index": 125,
              "xheight": 17.5
            },
            {
              "line_index": 126,
              "xheight": 17.0
            },
            {
              "line_index": 127,
              "xheight": 17.0
            },
            {
              "line_index": 128,
              "xheight": 16.639555488345877
            },
            {
              "line_index": 144,
              "xheight": 16.89565146594248
            },
            {
              "line_index": 145,
              "xheight": 16.08835235514971
            },
            {
              "line_index": 146,
              "xheight": 17.0
            },
            {
              "line_index": 147,
              "xheight": 16.16328497176187
            },
            {
              "line_index": 148,
              "xheight": 17.0
            },
            {
              "line_index": 149,
              "xheight": 15.68925649767425
            },
            {
              "line_index": 167,
              "xheight": 16.051049614437034
            },
            {
              "line_index": 168,
              "xheight": 16.0
            },
            {
              "line_index": 169,
              "xheight": 16.0
            },
            {
              "line_index": 170,
              "xheight": 16.283381374833425
            },
            {
              "line_index": 171,
              "xheight": 16.83834997583699
            },
            {
              "line_index": 172,
              "xheight": 16.0
            }
          ],
          "observed_gap_widths_px": [
            43,
            44,
            42,
            60,
            58,
            58
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 12.15300000000002,
          "interpiece_spacing_samples": [
            6,
            6
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0002"
      },
      {
        "kind": "gutter",
        "path": [
          [
            848.5,
            505.0
          ],
          [
            848.5,
            734.0
          ]
        ],
        "width": 39,
        "extent": [
          829,
          505,
          868,
          734
        ],
        "source": "detector",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 39.0,
          "local_xheight_max_px": 17.5,
          "width_xh": 2.2285714285714286,
          "required_width_px": 26.25,
          "spacing_sides": [
            {
              "samples": 60,
              "letter_q25_xh": 0.11837365395655286,
              "median_xh": 0.23529411764705882,
              "word_q75_xh": 0.31276023768121425,
              "q90_xh": 0.666145154243593
            },
            {
              "samples": 71,
              "letter_q25_xh": 0.15211074826250404,
              "median_xh": 0.29411764705882354,
              "word_q75_xh": 0.3125,
              "q90_xh": 0.375
            }
          ],
          "side_row_counts": [
            6,
            6
          ],
          "side_span_xh": [
            9.541399999999996,
            9.425228571428573
          ],
          "shared_span_xh": 9.425228571428573,
          "occupied_rows": 6,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 123,
              "xheight": 16.5
            },
            {
              "line_index": 124,
              "xheight": 17.0
            },
            {
              "line_index": 125,
              "xheight": 17.5
            },
            {
              "line_index": 126,
              "xheight": 17.0
            },
            {
              "line_index": 127,
              "xheight": 17.0
            },
            {
              "line_index": 128,
              "xheight": 16.639555488345877
            },
            {
              "line_index": 144,
              "xheight": 16.89565146594248
            },
            {
              "line_index": 145,
              "xheight": 16.08835235514971
            },
            {
              "line_index": 146,
              "xheight": 17.0
            },
            {
              "line_index": 147,
              "xheight": 16.16328497176187
            },
            {
              "line_index": 148,
              "xheight": 17.0
            },
            {
              "line_index": 149,
              "xheight": 15.68925649767425
            },
            {
              "line_index": 167,
              "xheight": 16.051049614437034
            },
            {
              "line_index": 168,
              "xheight": 16.0
            },
            {
              "line_index": 169,
              "xheight": 16.0
            },
            {
              "line_index": 170,
              "xheight": 16.283381374833425
            },
            {
              "line_index": 171,
              "xheight": 16.83834997583699
            },
            {
              "line_index": 172,
              "xheight": 16.0
            },
            {
              "line_index": 185,
              "xheight": 16.709179603735492
            },
            {
              "line_index": 186,
              "xheight": 16.0
            },
            {
              "line_index": 187,
              "xheight": 16.847142289524527
            },
            {
              "line_index": 188,
              "xheight": 17.0
            },
            {
              "line_index": 189,
              "xheight": 16.214908495949317
            },
            {
              "line_index": 190,
              "xheight": 15.854172930041955
            }
          ],
          "observed_gap_widths_px": [
            43,
            41,
            44,
            66,
            55,
            45
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 12.126000000000033,
          "interpiece_spacing_samples": [
            6,
            6
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0003"
      },
      {
        "kind": "gutter",
        "path": [
          [
            1105.5,
            505.0
          ],
          [
            1105.5,
            734.0
          ]
        ],
        "width": 61,
        "extent": [
          1075,
          505,
          1136,
          734
        ],
        "source": "detector",
        "proposal_id": "proposal-0002",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 61.0,
          "local_xheight_max_px": 17.0,
          "width_xh": 3.588235294117647,
          "required_width_px": 25.5,
          "spacing_sides": [
            {
              "samples": 63,
              "letter_q25_xh": 0.15211074826250404,
              "median_xh": 0.25,
              "word_q75_xh": 0.3125,
              "q90_xh": 0.40441176470588247
            },
            {
              "samples": 65,
              "letter_q25_xh": 0.17780474129864884,
              "median_xh": 0.24593241100269245,
              "word_q75_xh": 0.3106278830382105,
              "q90_xh": 0.4382393584605396
            }
          ],
          "side_row_counts": [
            6,
            6
          ],
          "side_span_xh": [
            9.613794117647057,
            9.7270294117647
          ],
          "shared_span_xh": 9.613794117647057,
          "occupied_rows": 6,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 167,
              "xheight": 16.051049614437034
            },
            {
              "line_index": 168,
              "xheight": 16.0
            },
            {
              "line_index": 169,
              "xheight": 16.0
            },
            {
              "line_index": 170,
              "xheight": 16.283381374833425
            },
            {
              "line_index": 171,
              "xheight": 16.83834997583699
            },
            {
              "line_index": 172,
              "xheight": 16.0
            },
            {
              "line_index": 185,
              "xheight": 16.709179603735492
            },
            {
              "line_index": 186,
              "xheight": 16.0
            },
            {
              "line_index": 187,
              "xheight": 16.847142289524527
            },
            {
              "line_index": 188,
              "xheight": 17.0
            },
            {
              "line_index": 189,
              "xheight": 16.214908495949317
            },
            {
              "line_index": 190,
              "xheight": 15.854172930041955
            },
            {
              "line_index": 209,
              "xheight": 16.0
            },
            {
              "line_index": 210,
              "xheight": 16.87244096017139
            },
            {
              "line_index": 211,
              "xheight": 16.5
            },
            {
              "line_index": 212,
              "xheight": 16.396945224841375
            },
            {
              "line_index": 213,
              "xheight": 16.5
            },
            {
              "line_index": 214,
              "xheight": 16.0515419190657
            },
            {
              "line_index": 234,
              "xheight": 16.94089274397288
            },
            {
              "line_index": 235,
              "xheight": 16.096430079282186
            },
            {
              "line_index": 236,
              "xheight": 16.699860108266307
            },
            {
              "line_index": 237,
              "xheight": 16.2646313419674
            },
            {
              "line_index": 238,
              "xheight": 16.384200449623904
            },
            {
              "line_index": 239,
              "xheight": 16.601070843786374
            }
          ],
          "observed_gap_widths_px": [
            67,
            66,
            66,
            65,
            66,
            65
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 12.000750000000039,
          "interpiece_spacing_samples": [
            6,
            6
          ]
        },
        "id": "boundary-0002",
        "track_id": "separator-0018"
      },
      {
        "kind": "gutter",
        "path": [
          [
            1328.5,
            505.0
          ],
          [
            1328.5,
            734.0
          ]
        ],
        "width": 39,
        "extent": [
          1309,
          505,
          1348,
          734
        ],
        "source": "detector",
        "proposal_id": "proposal-0003",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 39.0,
          "local_xheight_max_px": 17.0,
          "width_xh": 2.2941176470588234,
          "required_width_px": 25.5,
          "spacing_sides": [
            {
              "samples": 65,
              "letter_q25_xh": 0.17780474129864884,
              "median_xh": 0.24593241100269245,
              "word_q75_xh": 0.3106278830382105,
              "q90_xh": 0.4382393584605396
            },
            {
              "samples": 32,
              "letter_q25_xh": 0.12104012655961663,
              "median_xh": 0.2354031419436322,
              "word_q75_xh": 0.2945699170406685,
              "q90_xh": 0.3649182848717632
            }
          ],
          "side_row_counts": [
            6,
            6
          ],
          "side_span_xh": [
            9.7270294117647,
            9.72564705882353
          ],
          "shared_span_xh": 9.548999999999992,
          "occupied_rows": 6,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 209,
              "xheight": 16.0
            },
            {
              "line_index": 210,
              "xheight": 16.87244096017139
            },
            {
              "line_index": 211,
              "xheight": 16.5
            },
            {
              "line_index": 212,
              "xheight": 16.396945224841375
            },
            {
              "line_index": 213,
              "xheight": 16.5
            },
            {
              "line_index": 214,
              "xheight": 16.0515419190657
            },
            {
              "line_index": 234,
              "xheight": 16.94089274397288
            },
            {
              "line_index": 235,
              "xheight": 16.096430079282186
            },
            {
              "line_index": 236,
              "xheight": 16.699860108266307
            },
            {
              "line_index": 237,
              "xheight": 16.2646313419674
            },
            {
              "line_index": 238,
              "xheight": 16.384200449623904
            },
            {
              "line_index": 239,
              "xheight": 16.601070843786374
            },
            {
              "line_index": 250,
              "xheight": 17.0
            },
            {
              "line_index": 251,
              "xheight": 16.388208769356652
            },
            {
              "line_index": 252,
              "xheight": 16.98426057497295
            },
            {
              "line_index": 253,
              "xheight": 16.94288971737228
            },
            {
              "line_index": 254,
              "xheight": 17.0
            },
            {
              "line_index": 255,
              "xheight": 16.0
            }
          ],
          "observed_gap_widths_px": [
            43,
            42,
            43,
            45,
            68,
            67
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 12.064000000000021,
          "interpiece_spacing_samples": [
            6,
            0
          ]
        },
        "id": "boundary-0003",
        "track_id": "separator-0019"
      },
      {
        "kind": "gutter",
        "path": [
          [
            781.5,
            1568.0
          ],
          [
            781.5,
            1810.0
          ]
        ],
        "width": 49,
        "extent": [
          757,
          1568,
          806,
          1810
        ],
        "source": "detector",
        "proposal_id": "proposal-0007",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 49.0,
          "local_xheight_max_px": 17.323823895431815,
          "width_xh": 2.8284748387982055,
          "required_width_px": 38.71131964317748,
          "spacing_sides": [
            {
              "samples": 57,
              "letter_q25_xh": 0.18181818181818182,
              "median_xh": 0.24873455150573293,
              "word_q75_xh": 0.30580762192146527,
              "q90_xh": 1.4897141984680575
            },
            {
              "samples": 60,
              "letter_q25_xh": 0.17647058823529413,
              "median_xh": 0.2666874501834664,
              "word_q75_xh": 0.31769312429600194,
              "q90_xh": 0.685140748159711
            }
          ],
          "side_row_counts": [
            6,
            6
          ],
          "side_span_xh": [
            9.460844267945877,
            9.576956046277363
          ],
          "shared_span_xh": 9.460844267945877,
          "occupied_rows": 6,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 115,
              "xheight": 16.88419188844273
            },
            {
              "line_index": 116,
              "xheight": 16.479057108426787
            },
            {
              "line_index": 117,
              "xheight": 14.487046704362456
            },
            {
              "line_index": 118,
              "xheight": 15.665383950319665
            },
            {
              "line_index": 119,
              "xheight": 15.86681867006564
            },
            {
              "line_index": 120,
              "xheight": 17.0
            },
            {
              "line_index": 132,
              "xheight": 16.5
            },
            {
              "line_index": 133,
              "xheight": 13.078996019393799
            },
            {
              "line_index": 134,
              "xheight": 16.567465088024164
            },
            {
              "line_index": 135,
              "xheight": 16.08140073739537
            },
            {
              "line_index": 136,
              "xheight": 17.131961051700728
            },
            {
              "line_index": 137,
              "xheight": 16.350148399126738
            },
            {
              "line_index": 157,
              "xheight": 17.0
            },
            {
              "line_index": 158,
              "xheight": 17.0
            },
            {
              "line_index": 159,
              "xheight": 17.0
            },
            {
              "line_index": 160,
              "xheight": 17.0
            },
            {
              "line_index": 161,
              "xheight": 17.150053573187733
            },
            {
              "line_index": 162,
              "xheight": 17.0
            },
            {
              "line_index": 175,
              "xheight": 16.870574059323417
            },
            {
              "line_index": 176,
              "xheight": 16.34287222660987
            },
            {
              "line_index": 177,
              "xheight": 16.95372499378118
            },
            {
              "line_index": 178,
              "xheight": 16.822354666387582
            },
            {
              "line_index": 179,
              "xheight": 17.323823895431815
            },
            {
              "line_index": 180,
              "xheight": 16.957060691082688
            }
          ],
          "observed_gap_widths_px": [
            55,
            55,
            56,
            53,
            53,
            55
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 14.562750000000051,
          "interpiece_spacing_samples": [
            6,
            6
          ]
        },
        "id": "boundary-0004",
        "track_id": "separator-0020"
      },
      {
        "kind": "gutter",
        "path": [
          [
            736.0,
            1810.0
          ],
          [
            736.0,
            2016.0
          ]
        ],
        "width": 64,
        "extent": [
          704,
          1810,
          768,
          2016
        ],
        "source": "detector",
        "proposal_id": "proposal-0008",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 64.0,
          "local_xheight_max_px": 16.273567650774567,
          "width_xh": 3.9327577930923967,
          "required_width_px": 26.93861103396386,
          "spacing_sides": [
            {
              "samples": 26,
              "letter_q25_xh": 0.07454164731474117,
              "median_xh": 0.07827580385734381,
              "word_q75_xh": 0.36660241839459007,
              "q90_xh": 1.1035732549886061
            },
            {
              "samples": 34,
              "letter_q25_xh": 0.07737664175288833,
              "median_xh": 0.15300041397312533,
              "word_q75_xh": 0.15475328350577666,
              "q90_xh": 0.8822541667036942
            }
          ],
          "side_row_counts": [
            5,
            5
          ],
          "side_span_xh": [
            8.083015526944964,
            8.036160404800695
          ],
          "shared_span_xh": 6.455007423956001,
          "occupied_rows": 6,
          "bilateral_rows": 4,
          "participants": [
            {
              "line_index": 30,
              "xheight": 15.5
            },
            {
              "line_index": 31,
              "xheight": 16.01212899488644
            },
            {
              "line_index": 33,
              "xheight": 12.642277861711818
            },
            {
              "line_index": 34,
              "xheight": 12.91123272637833
            },
            {
              "line_index": 35,
              "xheight": 13.59221051452073
            },
            {
              "line_index": 36,
              "xheight": 14.934613888138301
            },
            {
              "line_index": 150,
              "xheight": 12.944164843012459
            },
            {
              "line_index": 151,
              "xheight": 12.923796863575717
            },
            {
              "line_index": 152,
              "xheight": 13.071860056217247
            },
            {
              "line_index": 153,
              "xheight": 16.273567650774567
            },
            {
              "line_index": 154,
              "xheight": 13.292868979368222
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            110,
            72,
            71,
            166,
            0.0
          ],
          "white_rows": 4,
          "baseline_matching_reach_px": 12.877125000000035,
          "interpiece_spacing_samples": [
            1,
            0
          ]
        },
        "id": "boundary-0005",
        "track_id": "separator-0021"
      }
    ],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            228.44109722733228,
            1299
          ],
          [
            228.50583551481316,
            1793
          ]
        ],
        "radius": 3.3600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0012",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 16.72204217147123,
          "support_fraction": 0.45692883895131087,
          "supported_rows": 2,
          "thin_support_fraction": 0.01639344262295082,
          "original_ink_rows": 122,
          "sampled_rows": 495,
          "extent_xh": 15.966949327248882,
          "thickness_q90_xh": 0.059801308341756114,
          "residual_q90_xh": 6.4586905551400724e-15,
          "dash_lengths_xh": [
            0.7176157001010733,
            1.8538405585944395,
            0.8970196251263417,
            1.0166222418098538,
            2.15284710030322,
            0.17940392502526833,
            0.4784104667340489
          ],
          "gap_lengths_xh": [
            0.17940392502526833,
            0.8970196251263417,
            2.8106614920625375,
            0.23920523336702446,
            1.2558274751768783,
            3.2890719587965864
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            227.91898840895576,
            1299.0
          ],
          [
            228.40245600125766,
            1793.0
          ]
        ],
        "id": "boundary-0006",
        "track_id": "separator-0009",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            905.6869219087007,
            1299
          ],
          [
            902.697767162523,
            1785
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0013",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.90061512048726,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 487,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            905.7560923456612,
            1299.0
          ],
          [
            902.68827015415,
            1785.0
          ]
        ],
        "id": "boundary-0007",
        "track_id": "separator-0010",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            364.60975852832973,
            1299
          ],
          [
            363.75654296423227,
            1793
          ]
        ],
        "radius": 3.3600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0014",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.241477623599167,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 495,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            364.2871435126528,
            1299.0
          ],
          [
            363.954225669463,
            1793.0
          ]
        ],
        "id": "boundary-0008",
        "track_id": "separator-0011",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            184.48205256443887,
            291
          ],
          [
            181.07798117359766,
            728
          ]
        ],
        "radius": 3.3600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0015",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.916261267140953,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 438,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            184.47029238451825,
            291.0
          ],
          [
            181.20799065102725,
            728.0
          ]
        ],
        "id": "boundary-0009",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            296.87081149258273,
            291
          ],
          [
            294.9954231925499,
            729
          ]
        ],
        "radius": 3.3600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0016",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": true,
            "isolated_thin_support": true,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.898045402583648,
          "support_fraction": 1.0,
          "supported_rows": 9,
          "thin_support_fraction": 0.75,
          "original_ink_rows": 12,
          "sampled_rows": 439,
          "extent_xh": 0.7101413041632167,
          "thickness_q90_xh": 0.05917844201360139,
          "residual_q90_xh": 4.03668596029102e-15,
          "dash_lengths_xh": [
            0.7101413041632167
          ],
          "gap_lengths_xh": [],
          "style": "continuous"
        },
        "proposal_path": [
          [
            297.2598176344125,
            291.0
          ],
          [
            294.4776997068987,
            729.0
          ]
        ],
        "id": "boundary-0010",
        "track_id": "separator-0001",
        "rejection_reasons": [
          "long_enough"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            1039.121190572722,
            1368
          ],
          [
            1037.4385930226267,
            1791
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0017",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 16.955392842431934,
          "support_fraction": 0.13125,
          "supported_rows": 4,
          "thin_support_fraction": 0.19047619047619047,
          "original_ink_rows": 21,
          "sampled_rows": 424,
          "extent_xh": 9.436525681645662,
          "thickness_q90_xh": 0.15924137087777057,
          "residual_q90_xh": 0.010910982819387512,
          "dash_lengths_xh": [
            0.4128479985719978,
            0.058978285510285396,
            0.7667177116337102
          ],
          "gap_lengths_xh": [
            7.667177116337101,
            0.5308045695925685
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1039.1402699363298,
            1368.0
          ],
          [
            1037.5793220028997,
            1791.0
          ]
        ],
        "id": "boundary-0011",
        "track_id": "separator-0012",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            1172.46025339154,
            1370
          ],
          [
            1172.39483410139,
            1791
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0018",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 16.8464643628555,
          "support_fraction": 0.23684210526315788,
          "supported_rows": 24,
          "thin_support_fraction": 0.26666666666666666,
          "original_ink_rows": 90,
          "sampled_rows": 422,
          "extent_xh": 22.556661849940213,
          "thickness_q90_xh": 0.17807890934163326,
          "residual_q90_xh": 0.12229181086486632,
          "dash_lengths_xh": [
            0.17807890934163326,
            0.4155174551304776,
            0.6529560009193219,
            1.0684734560497995,
            0.17807890934163326,
            0.9497541831553774,
            0.4155174551304776,
            0.05935963644721109,
            1.1871927289442217,
            0.23743854578884435
          ],
          "gap_lengths_xh": [
            0.23743854578884435,
            0.5342367280248997,
            1.0091138196025884,
            2.4337450943356544,
            7.954191283926286,
            0.3561578186832665,
            0.11871927289442218,
            4.333253460646409,
            0.23743854578884435
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1172.9903053667442,
            1370.0
          ],
          [
            1172.013493878367,
            1791.0
          ]
        ],
        "id": "boundary-0012",
        "track_id": "separator-0014",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            719.65563141123,
            297
          ],
          [
            718.635770854033,
            728
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0019",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.22787684027969,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 432,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            719.382933961706,
            297.0
          ],
          [
            718.8564092791614,
            728.0
          ]
        ],
        "id": "boundary-0013",
        "track_id": "separator-0002",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            842.4775542827779,
            299
          ],
          [
            842.3455597596967,
            728
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0020",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.16328497176187,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 430,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            842.2136905668098,
            299.0
          ],
          [
            842.1964389951386,
            728.0
          ]
        ],
        "id": "boundary-0014",
        "track_id": "separator-0003",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            770.488135976291,
            1369
          ],
          [
            769.0493917282515,
            1788
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0021",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.567465088024164,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 420,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            770.6887677175062,
            1369.0
          ],
          [
            768.8761465726707,
            1788.0
          ]
        ],
        "id": "boundary-0015",
        "track_id": "separator-0013",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            408.77103488039387,
            364
          ],
          [
            407.3531172328601,
            729
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0022",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.8871429922101,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 366,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            408.9435286750751,
            364.0
          ],
          [
            407.35372392789094,
            729.0
          ]
        ],
        "id": "boundary-0016",
        "track_id": "separator-0006",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            965.1370473243917,
            366
          ],
          [
            965.4805480298551,
            731
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0023",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.12581866345579,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 366,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            965.1034612419983,
            366.0
          ],
          [
            965.1813094562302,
            731.0
          ]
        ],
        "id": "boundary-0017",
        "track_id": "separator-0007",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            1088.6632770687913,
            376
          ],
          [
            1087.723511858756,
            730
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0024",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.274006358400413,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 355,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1088.915677566171,
            376.0
          ],
          [
            1087.6458096827446,
            730.0
          ]
        ],
        "id": "boundary-0018",
        "track_id": "separator-0008",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            634.6269373348002,
            1441
          ],
          [
            633.9157041908533,
            1789
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0025",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.5,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 349,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            635.0145296140486,
            1441.0
          ],
          [
            633.6807185936125,
            1789.0
          ]
        ],
        "id": "boundary-0019",
        "track_id": "separator-0016",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            1306.7451592140062,
            1372
          ],
          [
            1306.7465033163658,
            1788
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0026",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 16.785479270006817,
          "support_fraction": 0.17567567567567569,
          "supported_rows": 3,
          "thin_support_fraction": 0.07692307692307693,
          "original_ink_rows": 39,
          "sampled_rows": 417,
          "extent_xh": 13.22571708730899,
          "thickness_q90_xh": 0.1787259065852566,
          "residual_q90_xh": 0.056695306758739863,
          "dash_lengths_xh": [
            0.1787259065852566,
            0.05957530219508554,
            0.655328324145941,
            0.9532048351213687,
            0.05957530219508554,
            0.1787259065852566,
            0.23830120878034217
          ],
          "gap_lengths_xh": [
            0.7149036263410264,
            0.05957530219508554,
            2.621313296583764,
            7.3277621699955215,
            0.11915060439017108,
            0.05957530219508554
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1306.603616834817,
            1372.0
          ],
          [
            1307.0047592579979,
            1788.0
          ]
        ],
        "id": "boundary-0020",
        "track_id": "separator-0015",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            1212.214842677928,
            301
          ],
          [
            1209.8166010119896,
            731
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0027",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.384200449623904,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 431,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1211.7484551426726,
            301.0
          ],
          [
            1210.0041706828604,
            731.0
          ]
        ],
        "id": "boundary-0021",
        "track_id": "separator-0004",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            630.7933731770478,
            363
          ],
          [
            631.2065236200032,
            728
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0028",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 16.626829551876483,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 366,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            630.012743949082,
            363.0
          ],
          [
            631.4795359150205,
            728.0
          ]
        ],
        "id": "boundary-0022",
        "track_id": "separator-0005",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      },
      {
        "kind": "rule",
        "path": [
          [
            499.7551790495923,
            1441
          ],
          [
            498.830524280595,
            1790
          ]
        ],
        "radius": 2.8600000000000003,
        "source": "direct_rule",
        "proposal_id": "proposal-0029",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 16.5,
          "support_fraction": 0.11666666666666667,
          "supported_rows": 7,
          "thin_support_fraction": 0.25,
          "original_ink_rows": 28,
          "sampled_rows": 350,
          "extent_xh": 14.545454545454545,
          "thickness_q90_xh": 0.12121212121212122,
          "residual_q90_xh": 0.044153293490596705,
          "dash_lengths_xh": [
            0.6060606060606061,
            0.48484848484848486,
            0.6060606060606061
          ],
          "gap_lengths_xh": [
            1.2121212121212122,
            11.636363636363637
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            500.2159490995964,
            1441.0
          ],
          [
            498.76813356727126,
            1790.0
          ]
        ],
        "id": "boundary-0023",
        "track_id": "separator-0017",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      }
    ],
    "inventory_sha256": "fe512639e5a2be92d8a33782cbc9146ecb6d292ac1939760e56270f03abd010d"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "line_block_disagreement",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.6875951535143363,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## ia_poly1850--63f57af8d450f3e8--s011-l0033

Card `kab1eb0f9af`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/1a458412b7ba55ce56fd897fbb702b57042981ee30efb1159000ae5a570d90ea.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/1a458412b7ba55ce56fd897fbb702b57042981ee30efb1159000ae5a570d90ea.png`; SHA-256 `1a458412b7ba55ce56fd897fbb702b57042981ee30efb1159000ae5a570d90ea`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kab1eb0f9af",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Neighbouring ink is clipped; no complete word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "ia_poly1850--63f57af8d450f3e8--s011-l0033"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00030",
  "neighbour_rows": [
    {
      "row_id": "row-00029",
      "column_id": "single:column-0000",
      "xheight": 30.96392344137257,
      "profile_runs": [
        [
          67,
          91
        ],
        [
          96,
          127
        ],
        [
          134,
          161
        ],
        [
          166,
          200
        ],
        [
          201,
          230
        ],
        [
          234,
          259
        ],
        [
          298,
          335
        ],
        [
          336,
          337
        ],
        [
          343,
          367
        ],
        [
          413,
          433
        ],
        [
          434,
          450
        ],
        [
          457,
          483
        ],
        [
          489,
          515
        ],
        [
          521,
          546
        ],
        [
          551,
          552
        ],
        [
          553,
          582
        ],
        [
          590,
          617
        ],
        [
          624,
          645
        ],
        [
          650,
          668
        ],
        [
          718,
          746
        ],
        [
          753,
          783
        ],
        [
          790,
          806
        ],
        [
          856,
          882
        ],
        [
          885,
          911
        ],
        [
          915,
          933
        ],
        [
          971,
          1007
        ],
        [
          1015,
          1037
        ],
        [
          1042,
          1069
        ],
        [
          1074,
          1104
        ],
        [
          1111,
          1124
        ],
        [
          1133,
          1165
        ],
        [
          1169,
          1189
        ],
        [
          1198,
          1213
        ],
        [
          1220,
          1236
        ],
        [
          1239,
          1251
        ],
        [
          1256,
          1268
        ],
        [
          1307,
          1333
        ],
        [
          1337,
          1369
        ],
        [
          1408,
          1446
        ],
        [
          1455,
          1480
        ],
        [
          1489,
          1520
        ],
        [
          1525,
          1552
        ],
        [
          1559,
          1587
        ]
      ],
      "profile_gaps": [
        [
          91,
          96
        ],
        [
          127,
          134
        ],
        [
          161,
          166
        ],
        [
          200,
          201
        ],
        [
          230,
          234
        ],
        [
          259,
          298
        ],
        [
          335,
          336
        ],
        [
          337,
          343
        ],
        [
          367,
          413
        ],
        [
          433,
          434
        ],
        [
          450,
          457
        ],
        [
          483,
          489
        ],
        [
          515,
          521
        ],
        [
          546,
          551
        ],
        [
          552,
          553
        ],
        [
          582,
          590
        ],
        [
          617,
          624
        ],
        [
          645,
          650
        ],
        [
          668,
          718
        ],
        [
          746,
          753
        ],
        [
          783,
          790
        ],
        [
          806,
          856
        ],
        [
          882,
          885
        ],
        [
          911,
          915
        ],
        [
          933,
          971
        ],
        [
          1007,
          1015
        ],
        [
          1037,
          1042
        ],
        [
          1069,
          1074
        ],
        [
          1104,
          1111
        ],
        [
          1124,
          1133
        ],
        [
          1165,
          1169
        ],
        [
          1189,
          1198
        ],
        [
          1213,
          1220
        ],
        [
          1236,
          1239
        ],
        [
          1251,
          1256
        ],
        [
          1268,
          1307
        ],
        [
          1333,
          1337
        ],
        [
          1369,
          1408
        ],
        [
          1446,
          1455
        ],
        [
          1480,
          1489
        ],
        [
          1520,
          1525
        ],
        [
          1552,
          1559
        ]
      ],
      "directional_missing": {
        "above": 95364,
        "below": 0
      },
      "groups": [
        {
          "box": [
            66,
            2273,
            1268,
            2340
          ],
          "body_count": 32,
          "width_xh": 38.81936997667236,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1408,
            2292,
            1588,
            2340
          ],
          "body_count": 5,
          "width_xh": 5.813216801831136,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00031",
      "column_id": "single:column-0000",
      "xheight": 30.01155019806356,
      "profile_runs": [
        [
          65,
          94
        ],
        [
          103,
          140
        ],
        [
          145,
          159
        ],
        [
          168,
          197
        ],
        [
          200,
          225
        ],
        [
          233,
          271
        ],
        [
          275,
          301
        ],
        [
          348,
          372
        ],
        [
          377,
          404
        ],
        [
          411,
          438
        ],
        [
          444,
          474
        ],
        [
          478,
          506
        ],
        [
          512,
          543
        ],
        [
          594,
          632
        ],
        [
          634,
          663
        ],
        [
          671,
          700
        ],
        [
          705,
          735
        ],
        [
          741,
          772
        ],
        [
          773,
          797
        ],
        [
          800,
          830
        ],
        [
          834,
          865
        ],
        [
          871,
          889
        ],
        [
          953,
          954
        ],
        [
          986,
          1048
        ],
        [
          1056,
          1083
        ],
        [
          1090,
          1101
        ],
        [
          1109,
          1146
        ],
        [
          1153,
          1189
        ],
        [
          1196,
          1232
        ],
        [
          1250,
          1262
        ],
        [
          1309,
          1340
        ],
        [
          1349,
          1376
        ],
        [
          1383,
          1408
        ],
        [
          1413,
          1447
        ],
        [
          1498,
          1525
        ],
        [
          1530,
          1562
        ],
        [
          1569,
          1588
        ]
      ],
      "profile_gaps": [
        [
          94,
          103
        ],
        [
          140,
          145
        ],
        [
          159,
          168
        ],
        [
          197,
          200
        ],
        [
          225,
          233
        ],
        [
          271,
          275
        ],
        [
          301,
          348
        ],
        [
          372,
          377
        ],
        [
          404,
          411
        ],
        [
          438,
          444
        ],
        [
          474,
          478
        ],
        [
          506,
          512
        ],
        [
          543,
          594
        ],
        [
          632,
          634
        ],
        [
          663,
          671
        ],
        [
          700,
          705
        ],
        [
          735,
          741
        ],
        [
          772,
          773
        ],
        [
          797,
          800
        ],
        [
          830,
          834
        ],
        [
          865,
          871
        ],
        [
          889,
          953
        ],
        [
          954,
          986
        ],
        [
          1048,
          1056
        ],
        [
          1083,
          1090
        ],
        [
          1101,
          1109
        ],
        [
          1146,
          1153
        ],
        [
          1189,
          1196
        ],
        [
          1232,
          1250
        ],
        [
          1262,
          1309
        ],
        [
          1340,
          1349
        ],
        [
          1376,
          1383
        ],
        [
          1408,
          1413
        ],
        [
          1447,
          1498
        ],
        [
          1525,
          1530
        ],
        [
          1562,
          1569
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 102237
      },
      "groups": [
        {
          "box": [
            986,
            2409,
            1262,
            2472
          ],
          "body_count": 8,
          "width_xh": 9.19645930245244,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1309,
            2410,
            1589,
            2460
          ],
          "body_count": 7,
          "width_xh": 9.329741321328562,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      11,
      2328,
      1594,
      2423
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00030"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00030"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00029",
      "column_id": "single:column-0000",
      "xheight": 30.96392344137257,
      "assigned_pixels": 879,
      "supported": null,
      "runs": []
    },
    {
      "row_id": "row-00030",
      "column_id": "single:column-0000",
      "xheight": 29.939369241302757,
      "assigned_pixels": 21808,
      "supported": null,
      "runs": [
        {
          "x0": 15,
          "x1": 35,
          "body_cut_fraction": 0.0,
          "body_pixels": 323,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 38,
          "x1": 57,
          "body_cut_fraction": 0.0,
          "body_pixels": 296,
          "body_extent_px": 27,
          "complete": true
        },
        {
          "x0": 67,
          "x1": 101,
          "body_cut_fraction": 0.0,
          "body_pixels": 692,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 151,
          "x1": 185,
          "body_cut_fraction": 0.0,
          "body_pixels": 664,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 192,
          "x1": 222,
          "body_cut_fraction": 0.0,
          "body_pixels": 508,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 227,
          "x1": 257,
          "body_cut_fraction": 0.0,
          "body_pixels": 553,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 260,
          "x1": 289,
          "body_cut_fraction": 0.0,
          "body_pixels": 589,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 294,
          "x1": 317,
          "body_cut_fraction": 0.0,
          "body_pixels": 443,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 320,
          "x1": 347,
          "body_cut_fraction": 0.0,
          "body_pixels": 396,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 398,
          "x1": 442,
          "body_cut_fraction": 0.0,
          "body_pixels": 623,
          "body_extent_px": 31,
          "complete": true
        },
        {
          "x0": 453,
          "x1": 494,
          "body_cut_fraction": 0.0,
          "body_pixels": 612,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 497,
          "x1": 529,
          "body_cut_fraction": 0.0,
          "body_pixels": 467,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 534,
          "x1": 564,
          "body_cut_fraction": 0.0,
          "body_pixels": 439,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 569,
          "x1": 598,
          "body_cut_fraction": 0.0,
          "body_pixels": 586,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 605,
          "x1": 621,
          "body_cut_fraction": 0.0,
          "body_pixels": 305,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 622,
          "x1": 623,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 627,
          "x1": 654,
          "body_cut_fraction": 0.0,
          "body_pixels": 453,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 658,
          "x1": 676,
          "body_cut_fraction": 0.0,
          "body_pixels": 319,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 722,
          "x1": 752,
          "body_cut_fraction": 0.0,
          "body_pixels": 440,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 756,
          "x1": 786,
          "body_cut_fraction": 0.0,
          "body_pixels": 614,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 840,
          "x1": 869,
          "body_cut_fraction": 0.0,
          "body_pixels": 525,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 871,
          "x1": 903,
          "body_cut_fraction": 0.0,
          "body_pixels": 514,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 907,
          "x1": 947,
          "body_cut_fraction": 0.0,
          "body_pixels": 649,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 953,
          "x1": 970,
          "body_cut_fraction": 0.0,
          "body_pixels": 314,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 974,
          "x1": 987,
          "body_cut_fraction": 0.0,
          "body_pixels": 237,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 994,
          "x1": 1025,
          "body_cut_fraction": 0.0,
          "body_pixels": 499,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 1035,
          "x1": 1062,
          "body_cut_fraction": 0.0,
          "body_pixels": 364,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 1065,
          "x1": 1083,
          "body_cut_fraction": 0.0,
          "body_pixels": 303,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1092,
          "x1": 1118,
          "body_cut_fraction": 0.0,
          "body_pixels": 445,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 1122,
          "x1": 1153,
          "body_cut_fraction": 0.0,
          "body_pixels": 583,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 1203,
          "x1": 1234,
          "body_cut_fraction": 0.0,
          "body_pixels": 567,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1242,
          "x1": 1270,
          "body_cut_fraction": 0.0,
          "body_pixels": 543,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 1278,
          "x1": 1317,
          "body_cut_fraction": 0.0,
          "body_pixels": 580,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1320,
          "x1": 1342,
          "body_cut_fraction": 0.0,
          "body_pixels": 360,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1348,
          "x1": 1379,
          "body_cut_fraction": 0.0,
          "body_pixels": 497,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1384,
          "x1": 1419,
          "body_cut_fraction": 0.0,
          "body_pixels": 624,
          "body_extent_px": 28,
          "complete": true
        },
        {
          "x0": 1426,
          "x1": 1452,
          "body_cut_fraction": 0.0,
          "body_pixels": 403,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 1499,
          "x1": 1527,
          "body_cut_fraction": 0.0,
          "body_pixels": 578,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 1533,
          "x1": 1562,
          "body_cut_fraction": 0.0,
          "body_pixels": 527,
          "body_extent_px": 29,
          "complete": true
        },
        {
          "x0": 1569,
          "x1": 1589,
          "body_cut_fraction": 0.0,
          "body_pixels": 380,
          "body_extent_px": 30,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00031",
      "column_id": "single:column-0000",
      "xheight": 30.01155019806356,
      "assigned_pixels": 1107,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 36,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "d350a52c0586d4345e72bf3cbfee215d127c7073023f002cd9c39a989e263a2a"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.8459331705619172,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--a93e57bdf58c5799--s000-l0104

Card `kde1292090c`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/ab0b4861801f17b6d2e8cc0046590f5b2531ac4b520d7f66d5c8041cb89482d5.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/ab0b4861801f17b6d2e8cc0046590f5b2531ac4b520d7f66d5c8041cb89482d5.png`; SHA-256 `ab0b4861801f17b6d2e8cc0046590f5b2531ac4b520d7f66d5c8041cb89482d5`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kde1292090c",
  "letters": "n",
  "marks": "y",
  "crop_ok": "y",
  "errors": [
    "wrong_letter",
    "digits"
  ],
  "detail": "ε) → 8)",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Neighbouring ink is clipped; no complete word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--a93e57bdf58c5799--s000-l0104"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00096",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      869,
      990,
      1079,
      1026
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00096"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00096"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00096",
      "column_id": "single:column-0000",
      "xheight": 12.137896759524438,
      "assigned_pixels": 939,
      "supported": null,
      "runs": [
        {
          "x0": 873,
          "x1": 882,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 10,
          "complete": true
        },
        {
          "x0": 889,
          "x1": 892,
          "body_cut_fraction": 0.0,
          "body_pixels": 20,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 915,
          "x1": 932,
          "body_cut_fraction": 0.0,
          "body_pixels": 105,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 938,
          "x1": 948,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 950,
          "x1": 952,
          "body_cut_fraction": 0.0,
          "body_pixels": 5,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 953,
          "x1": 964,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 965,
          "x1": 966,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 968,
          "x1": 978,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 981,
          "x1": 989,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 994,
          "x1": 998,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1002,
          "x1": 1010,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1013,
          "x1": 1022,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1025,
          "x1": 1036,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1037,
          "x1": 1038,
          "body_cut_fraction": 0.0,
          "body_pixels": 4,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1039,
          "x1": 1049,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1052,
          "x1": 1062,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1066,
          "x1": 1076,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00095",
      "column_id": "single:column-0002",
      "xheight": 12.987858072739414,
      "assigned_pixels": 30,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 136,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.893141509794954,
        "required_common_rows": 2.4275793519048876,
        "xheight_px": 12.137896759524438,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          873,
          995.985,
          1076,
          1030.289
        ],
        "boundary_path": [
          [
            822.5,
            735.0
          ],
          [
            822.5,
            994.0
          ]
        ],
        "row_id": "row-00096"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.747378292704894,
        "required_common_rows": 2.597571614547883,
        "xheight_px": 12.987858072739414,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          872,
          957.315,
          1032,
          997.895
        ],
        "boundary_path": [
          [
            822.5,
            735.0
          ],
          [
            822.5,
            994.0
          ]
        ],
        "row_id": "row-00095"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            822.5,
            735.0
          ],
          [
            822.5,
            994.0
          ]
        ],
        "width": 37,
        "extent": [
          804,
          735,
          841,
          994
        ],
        "source": "detector",
        "proposal_id": "proposal-0002",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 37.0,
          "local_xheight_max_px": 13.463716634888556,
          "width_xh": 2.748126761976097,
          "required_width_px": 31.74621821010375,
          "spacing_sides": [
            {
              "samples": 49,
              "letter_q25_xh": 0.24396881935320258,
              "median_xh": 0.32529175913760344,
              "word_q75_xh": 0.3275751301075688,
              "q90_xh": 1.5719393126976402
            },
            {
              "samples": 67,
              "letter_q25_xh": 0.15897738720093008,
              "median_xh": 0.25003067686840874,
              "word_q75_xh": 0.4538060582471195,
              "q90_xh": 1.4363062667927229
            }
          ],
          "side_row_counts": [
            5,
            9
          ],
          "side_span_xh": [
            14.038916974099294,
            17.786656277320127
          ],
          "shared_span_xh": 14.038916974099294,
          "occupied_rows": 14,
          "bilateral_rows": 10,
          "participants": [
            {
              "line_index": 121,
              "xheight": 12.271504370180082
            },
            {
              "line_index": 124,
              "xheight": 12.372229599942102
            },
            {
              "line_index": 125,
              "xheight": 12.226664573017388
            },
            {
              "line_index": 126,
              "xheight": 12.210939208622108
            },
            {
              "line_index": 127,
              "xheight": 12.296653350839847
            },
            {
              "line_index": 129,
              "xheight": 11.974399654958916
            },
            {
              "line_index": 130,
              "xheight": 13.463716634888556
            },
            {
              "line_index": 131,
              "xheight": 12.497493731989266
            },
            {
              "line_index": 132,
              "xheight": 12.523390343155938
            },
            {
              "line_index": 133,
              "xheight": 11.9985276909797
            },
            {
              "line_index": 134,
              "xheight": 11.874076091638699
            },
            {
              "line_index": 135,
              "xheight": 12.637942222964057
            },
            {
              "line_index": 136,
              "xheight": 12.221983318826119
            },
            {
              "line_index": 137,
              "xheight": 12.987858072739414
            }
          ],
          "observed_gap_widths_px": [
            42,
            42,
            0.0,
            0.0,
            0.0,
            42,
            42,
            71,
            71,
            41,
            41,
            71,
            71,
            0.0
          ],
          "white_rows": 10,
          "baseline_matching_reach_px": 14.784374999999983,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "17888b42f39621d36afa35e99bde360064f9fddf4ce7d15c83b69eef2c3da463"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "line_block_disagreement",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.34994776742182054,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--af75990d6ac88d5d--s000-l0080

Card `keb1a85002c`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/2f5476220e32cd841100622f4c027950a58fbc3700cf809166f9053c47d7dbbf.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/2f5476220e32cd841100622f4c027950a58fbc3700cf809166f9053c47d7dbbf.png`; SHA-256 `2f5476220e32cd841100622f4c027950a58fbc3700cf809166f9053c47d7dbbf`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "keb1a85002c",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Clipped neighbouring ink does not show a complete word.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--af75990d6ac88d5d--s000-l0080"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00064",
  "neighbour_rows": [
    {
      "row_id": "row-00063",
      "column_id": "single:column-0000",
      "xheight": 11.974471606968564,
      "profile_runs": [
        [
          137,
          153
        ],
        [
          155,
          163
        ],
        [
          165,
          175
        ],
        [
          177,
          187
        ],
        [
          189,
          205
        ],
        [
          207,
          217
        ],
        [
          219,
          229
        ],
        [
          246,
          264
        ],
        [
          266,
          274
        ],
        [
          276,
          285
        ],
        [
          287,
          299
        ],
        [
          301,
          310
        ],
        [
          313,
          320
        ],
        [
          322,
          332
        ],
        [
          334,
          344
        ],
        [
          346,
          358
        ],
        [
          359,
          370
        ],
        [
          372,
          381
        ],
        [
          383,
          393
        ],
        [
          409,
          418
        ],
        [
          420,
          430
        ],
        [
          432,
          441
        ],
        [
          459,
          462
        ],
        [
          464,
          473
        ],
        [
          476,
          481
        ],
        [
          482,
          494
        ],
        [
          495,
          505
        ],
        [
          507,
          518
        ],
        [
          519,
          531
        ],
        [
          532,
          543
        ],
        [
          545,
          554
        ],
        [
          557,
          561
        ],
        [
          578,
          590
        ],
        [
          591,
          603
        ],
        [
          604,
          614
        ],
        [
          616,
          626
        ],
        [
          628,
          632
        ],
        [
          634,
          645
        ],
        [
          647,
          657
        ],
        [
          678,
          683
        ],
        [
          690,
          703
        ],
        [
          704,
          716
        ],
        [
          717,
          727
        ],
        [
          728,
          738
        ],
        [
          739,
          749
        ],
        [
          751,
          761
        ],
        [
          763,
          768
        ],
        [
          784,
          795
        ],
        [
          796,
          807
        ],
        [
          808,
          819
        ],
        [
          820,
          826
        ]
      ],
      "profile_gaps": [
        [
          153,
          155
        ],
        [
          163,
          165
        ],
        [
          175,
          177
        ],
        [
          187,
          189
        ],
        [
          205,
          207
        ],
        [
          217,
          219
        ],
        [
          229,
          246
        ],
        [
          264,
          266
        ],
        [
          274,
          276
        ],
        [
          285,
          287
        ],
        [
          299,
          301
        ],
        [
          310,
          313
        ],
        [
          320,
          322
        ],
        [
          332,
          334
        ],
        [
          344,
          346
        ],
        [
          358,
          359
        ],
        [
          370,
          372
        ],
        [
          381,
          383
        ],
        [
          393,
          409
        ],
        [
          418,
          420
        ],
        [
          430,
          432
        ],
        [
          441,
          459
        ],
        [
          462,
          464
        ],
        [
          473,
          476
        ],
        [
          481,
          482
        ],
        [
          494,
          495
        ],
        [
          505,
          507
        ],
        [
          518,
          519
        ],
        [
          531,
          532
        ],
        [
          543,
          545
        ],
        [
          554,
          557
        ],
        [
          561,
          578
        ],
        [
          590,
          591
        ],
        [
          603,
          604
        ],
        [
          614,
          616
        ],
        [
          626,
          628
        ],
        [
          632,
          634
        ],
        [
          645,
          647
        ],
        [
          657,
          678
        ],
        [
          683,
          690
        ],
        [
          703,
          704
        ],
        [
          716,
          717
        ],
        [
          727,
          728
        ],
        [
          738,
          739
        ],
        [
          749,
          751
        ],
        [
          761,
          763
        ],
        [
          768,
          784
        ],
        [
          795,
          796
        ],
        [
          807,
          808
        ],
        [
          819,
          820
        ]
      ],
      "directional_missing": {
        "above": 16055,
        "below": 0
      },
      "groups": [
        {
          "box": [
            137,
            1893,
            229,
            1918
          ],
          "body_count": 7,
          "width_xh": 7.683011244225628,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            245,
            1892,
            393,
            1918
          ],
          "body_count": 12,
          "width_xh": 12.359626784189054,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            409,
            1892,
            561,
            1914
          ],
          "body_count": 12,
          "width_xh": 12.693670751329298,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            578,
            1892,
            768,
            1917
          ],
          "body_count": 15,
          "width_xh": 15.867088439161623,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            784,
            1891,
            830,
            1914
          ],
          "body_count": 4,
          "width_xh": 3.841505622112814,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00065",
      "column_id": "single:column-0000",
      "xheight": 11.988402638735352,
      "profile_runs": [
        [
          109,
          122
        ],
        [
          123,
          135
        ],
        [
          137,
          149
        ],
        [
          151,
          161
        ],
        [
          169,
          176
        ],
        [
          186,
          197
        ],
        [
          199,
          202
        ],
        [
          205,
          217
        ],
        [
          218,
          230
        ],
        [
          233,
          241
        ],
        [
          245,
          258
        ],
        [
          259,
          269
        ],
        [
          278,
          285
        ],
        [
          295,
          311
        ],
        [
          314,
          321
        ],
        [
          323,
          325
        ],
        [
          327,
          339
        ],
        [
          342,
          351
        ],
        [
          354,
          366
        ],
        [
          367,
          377
        ],
        [
          380,
          384
        ],
        [
          393,
          405
        ],
        [
          406,
          418
        ],
        [
          419,
          429
        ],
        [
          430,
          440
        ],
        [
          441,
          453
        ],
        [
          456,
          465
        ],
        [
          473,
          483
        ],
        [
          485,
          495
        ],
        [
          497,
          506
        ],
        [
          515,
          531
        ],
        [
          534,
          546
        ],
        [
          548,
          561
        ],
        [
          564,
          576
        ],
        [
          578,
          591
        ],
        [
          594,
          606
        ],
        [
          611,
          619
        ],
        [
          629,
          640
        ],
        [
          642,
          649
        ],
        [
          651,
          662
        ],
        [
          663,
          672
        ],
        [
          675,
          678
        ],
        [
          687,
          697
        ],
        [
          698,
          710
        ],
        [
          712,
          722
        ],
        [
          723,
          733
        ],
        [
          736,
          739
        ],
        [
          742,
          746
        ],
        [
          755,
          768
        ],
        [
          770,
          780
        ],
        [
          782,
          792
        ],
        [
          800,
          808
        ],
        [
          810,
          821
        ]
      ],
      "profile_gaps": [
        [
          122,
          123
        ],
        [
          135,
          137
        ],
        [
          149,
          151
        ],
        [
          161,
          169
        ],
        [
          176,
          186
        ],
        [
          197,
          199
        ],
        [
          202,
          205
        ],
        [
          217,
          218
        ],
        [
          230,
          233
        ],
        [
          241,
          245
        ],
        [
          258,
          259
        ],
        [
          269,
          278
        ],
        [
          285,
          295
        ],
        [
          311,
          314
        ],
        [
          321,
          323
        ],
        [
          325,
          327
        ],
        [
          339,
          342
        ],
        [
          351,
          354
        ],
        [
          366,
          367
        ],
        [
          377,
          380
        ],
        [
          384,
          393
        ],
        [
          405,
          406
        ],
        [
          418,
          419
        ],
        [
          429,
          430
        ],
        [
          440,
          441
        ],
        [
          453,
          456
        ],
        [
          465,
          473
        ],
        [
          483,
          485
        ],
        [
          495,
          497
        ],
        [
          506,
          515
        ],
        [
          531,
          534
        ],
        [
          546,
          548
        ],
        [
          561,
          564
        ],
        [
          576,
          578
        ],
        [
          591,
          594
        ],
        [
          606,
          611
        ],
        [
          619,
          629
        ],
        [
          640,
          642
        ],
        [
          649,
          651
        ],
        [
          662,
          663
        ],
        [
          672,
          675
        ],
        [
          678,
          687
        ],
        [
          697,
          698
        ],
        [
          710,
          712
        ],
        [
          722,
          723
        ],
        [
          733,
          736
        ],
        [
          739,
          742
        ],
        [
          746,
          755
        ],
        [
          768,
          770
        ],
        [
          780,
          782
        ],
        [
          792,
          800
        ],
        [
          808,
          810
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 20350
      },
      "groups": [
        {
          "box": [
            169,
            1946,
            384,
            1972
          ],
          "body_count": 13,
          "width_xh": 17.93399892203489,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            515,
            1945,
            619,
            1965
          ],
          "body_count": 7,
          "width_xh": 8.67505064135641,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            629,
            1945,
            678,
            1964
          ],
          "body_count": 5,
          "width_xh": 4.087283475254463,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      101,
      1911,
      831,
      1949
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00064"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00064"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00063",
      "column_id": "single:column-0000",
      "xheight": 11.974471606968564,
      "assigned_pixels": 187,
      "supported": null,
      "runs": [
        {
          "x0": 137,
          "x1": 153,
          "body_cut_fraction": 0.9168745759173207,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 155,
          "x1": 163,
          "body_cut_fraction": 0.9170546357961553,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 165,
          "x1": 175,
          "body_cut_fraction": 0.9160744557365812,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 177,
          "x1": 187,
          "body_cut_fraction": 0.916930425995675,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 189,
          "x1": 205,
          "body_cut_fraction": 0.9199423760484795,
          "body_pixels": 9,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 207,
          "x1": 217,
          "body_cut_fraction": 0.9225083930450472,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 219,
          "x1": 229,
          "body_cut_fraction": 0.9209056061732191,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 246,
          "x1": 257,
          "body_cut_fraction": 0.9173233726597722,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 258,
          "x1": 264,
          "body_cut_fraction": 0.9178103165103112,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 266,
          "x1": 274,
          "body_cut_fraction": 0.9197791185619746,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 276,
          "x1": 285,
          "body_cut_fraction": 0.9217871392780912,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 287,
          "x1": 299,
          "body_cut_fraction": 0.9212418141454348,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 301,
          "x1": 310,
          "body_cut_fraction": 0.9158230725691953,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 313,
          "x1": 320,
          "body_cut_fraction": 0.9099531154933613,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 322,
          "x1": 332,
          "body_cut_fraction": 0.9140771793865416,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 334,
          "x1": 344,
          "body_cut_fraction": 0.9338683546840806,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 346,
          "x1": 358,
          "body_cut_fraction": 0.955189188060658,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 359,
          "x1": 370,
          "body_cut_fraction": 0.9639766170665054,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 372,
          "x1": 381,
          "body_cut_fraction": 0.9581701772292863,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 383,
          "x1": 393,
          "body_cut_fraction": 0.9416922768572956,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 409,
          "x1": 418,
          "body_cut_fraction": 0.9041375534708502,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 420,
          "x1": 430,
          "body_cut_fraction": 0.9134062116365873,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 432,
          "x1": 441,
          "body_cut_fraction": 0.9371259429716728,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 482,
          "x1": 494,
          "body_cut_fraction": 0.966518897928221,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00064",
      "column_id": "single:column-0000",
      "xheight": 11.953684965114462,
      "assigned_pixels": 3919,
      "supported": null,
      "runs": [
        {
          "x0": 110,
          "x1": 126,
          "body_cut_fraction": 0.0,
          "body_pixels": 103,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 129,
          "x1": 140,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 141,
          "x1": 146,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 147,
          "x1": 157,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 159,
          "x1": 169,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 170,
          "x1": 183,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 184,
          "x1": 195,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 196,
          "x1": 207,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 208,
          "x1": 216,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 217,
          "x1": 234,
          "body_cut_fraction": 0.0,
          "body_pixels": 103,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 235,
          "x1": 245,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 259,
          "x1": 263,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 269,
          "x1": 281,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 284,
          "x1": 296,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 299,
          "x1": 303,
          "body_cut_fraction": 0.0,
          "body_pixels": 14,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 314,
          "x1": 325,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 327,
          "x1": 337,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 339,
          "x1": 349,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 358,
          "x1": 370,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 372,
          "x1": 380,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 381,
          "x1": 401,
          "body_cut_fraction": 0.0,
          "body_pixels": 109,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 402,
          "x1": 410,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 411,
          "x1": 414,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 416,
          "x1": 425,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 427,
          "x1": 434,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 436,
          "x1": 439,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 441,
          "x1": 452,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 454,
          "x1": 462,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 471,
          "x1": 481,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 482,
          "x1": 492,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 493,
          "x1": 505,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 506,
          "x1": 516,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 526,
          "x1": 541,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 544,
          "x1": 555,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 558,
          "x1": 560,
          "body_cut_fraction": 0.0,
          "body_pixels": 15,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 561,
          "x1": 569,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 571,
          "x1": 583,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 584,
          "x1": 595,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 596,
          "x1": 608,
          "body_cut_fraction": 0.0,
          "body_pixels": 85,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 610,
          "x1": 615,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 624,
          "x1": 634,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 635,
          "x1": 646,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 654,
          "x1": 663,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 664,
          "x1": 673,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 675,
          "x1": 685,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 686,
          "x1": 696,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 709,
          "x1": 716,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 720,
          "x1": 733,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 736,
          "x1": 747,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 750,
          "x1": 762,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 765,
          "x1": 770,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 780,
          "x1": 784,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 787,
          "x1": 794,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 10,
          "complete": true
        },
        {
          "x0": 797,
          "x1": 809,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 811,
          "x1": 821,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00065",
      "column_id": "single:column-0000",
      "xheight": 11.988402638735352,
      "assigned_pixels": 227,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 140,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          1,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.7355188106438515,
        "required_common_rows": 2.394894321393713,
        "xheight_px": 11.974471606968564,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          137,
          1887.267,
          826,
          1919.161
        ],
        "boundary_path": [
          [
            842.0,
            0.0
          ],
          [
            842.0,
            2339.0
          ]
        ],
        "row_id": "row-00063"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          77,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.715623369808141,
        "required_common_rows": 2.3907369930228923,
        "xheight_px": 11.953684965114462,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          109,
          1916.584,
          821,
          1950.034
        ],
        "boundary_path": [
          [
            842.0,
            0.0
          ],
          [
            842.0,
            2339.0
          ]
        ],
        "row_id": "row-00064"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.74887191313747,
        "required_common_rows": 2.3976805277470703,
        "xheight_px": 11.988402638735352,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          108,
          1944.319,
          822,
          1977.151
        ],
        "boundary_path": [
          [
            842.0,
            0.0
          ],
          [
            842.0,
            2339.0
          ]
        ],
        "row_id": "row-00065"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.7355188106438515,
        "required_common_rows": 2.394894321393713,
        "xheight_px": 11.974471606968564,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          137,
          1887.267,
          826,
          1919.161
        ],
        "boundary_path": [
          [
            837.0,
            296.0
          ],
          [
            837.0,
            500.0
          ]
        ],
        "row_id": "row-00063"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.715623369808141,
        "required_common_rows": 2.3907369930228923,
        "xheight_px": 11.953684965114462,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          109,
          1916.584,
          821,
          1950.034
        ],
        "boundary_path": [
          [
            837.0,
            296.0
          ],
          [
            837.0,
            500.0
          ]
        ],
        "row_id": "row-00064"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.74887191313747,
        "required_common_rows": 2.3976805277470703,
        "xheight_px": 11.988402638735352,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          108,
          1944.319,
          822,
          1977.151
        ],
        "boundary_path": [
          [
            837.0,
            296.0
          ],
          [
            837.0,
            500.0
          ]
        ],
        "row_id": "row-00065"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.7355188106438515,
        "required_common_rows": 2.394894321393713,
        "xheight_px": 11.974471606968564,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          137,
          1887.267,
          826,
          1919.161
        ],
        "boundary_path": [
          [
            842.0,
            1082.0
          ],
          [
            842.0,
            1306.0
          ]
        ],
        "row_id": "row-00063"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.715623369808141,
        "required_common_rows": 2.3907369930228923,
        "xheight_px": 11.953684965114462,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          109,
          1916.584,
          821,
          1950.034
        ],
        "boundary_path": [
          [
            842.0,
            1082.0
          ],
          [
            842.0,
            1306.0
          ]
        ],
        "row_id": "row-00064"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.74887191313747,
        "required_common_rows": 2.3976805277470703,
        "xheight_px": 11.988402638735352,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          108,
          1944.319,
          822,
          1977.151
        ],
        "boundary_path": [
          [
            842.0,
            1082.0
          ],
          [
            842.0,
            1306.0
          ]
        ],
        "row_id": "row-00065"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          1,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.7355188106438515,
        "required_common_rows": 2.394894321393713,
        "xheight_px": 11.974471606968564,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          137,
          1887.267,
          826,
          1919.161
        ],
        "boundary_path": [
          [
            848.0,
            1851.0
          ],
          [
            848.0,
            2106.0
          ]
        ],
        "row_id": "row-00063"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          51,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.715623369808141,
        "required_common_rows": 2.3907369930228923,
        "xheight_px": 11.953684965114462,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          109,
          1916.584,
          821,
          1950.034
        ],
        "boundary_path": [
          [
            848.0,
            1851.0
          ],
          [
            848.0,
            2106.0
          ]
        ],
        "row_id": "row-00064"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.74887191313747,
        "required_common_rows": 2.3976805277470703,
        "xheight_px": 11.988402638735352,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          108,
          1944.319,
          822,
          1977.151
        ],
        "boundary_path": [
          [
            848.0,
            1851.0
          ],
          [
            848.0,
            2106.0
          ]
        ],
        "row_id": "row-00065"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            842.0,
            0.0
          ],
          [
            842.0,
            2339.0
          ]
        ],
        "width": 32,
        "extent": [
          826,
          0,
          858,
          2339
        ],
        "source": "detector",
        "proposal_id": "proposal-0000",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 19.31300740780182,
          "width_xh": 1.656914395790738,
          "required_width_px": 28.96951111170273,
          "spacing_sides": [
            {
              "samples": 485,
              "letter_q25_xh": 0.08826432421549012,
              "median_xh": 0.1684065848550246,
              "word_q75_xh": 0.2519737156181937,
              "q90_xh": 0.7560834033930117
            },
            {
              "samples": 555,
              "letter_q25_xh": 0.0837788129937189,
              "median_xh": 0.16644724759196525,
              "word_q75_xh": 0.24925162174602397,
              "q90_xh": 0.7454580337297462
            }
          ],
          "side_row_counts": [
            53,
            65
          ],
          "side_span_xh": [
            109.34749598588621,
            109.56219584657825
          ],
          "shared_span_xh": 109.34749598588621,
          "occupied_rows": 101,
          "bilateral_rows": 69,
          "participants": [
            {
              "line_index": 0,
              "xheight": 14.019179570583468
            },
            {
              "line_index": 1,
              "xheight": 16.150000000000006
            },
            {
              "line_index": 2,
              "xheight": 12.981449286340393
            },
            {
              "line_index": 3,
              "xheight": 12.71987339318298
            },
            {
              "line_index": 5,
              "xheight": 12.64261309030664
            },
            {
              "line_index": 6,
              "xheight": 12.911044934579024
            },
            {
              "line_index": 7,
              "xheight": 15.855139762479496
            },
            {
              "line_index": 8,
              "xheight": 12.94916773876082
            },
            {
              "line_index": 9,
              "xheight": 12.503884953342663
            },
            {
              "line_index": 10,
              "xheight": 18.297610523213223
            },
            {
              "line_index": 11,
              "xheight": 12.358587390896702
            },
            {
              "line_index": 13,
              "xheight": 11.857572841033857
            },
            {
              "line_index": 14,
              "xheight": 12.020863017645866
            },
            {
              "line_index": 15,
              "xheight": 11.842646470770319
            },
            {
              "line_index": 16,
              "xheight": 11.903333373212718
            },
            {
              "line_index": 17,
              "xheight": 11.954341860830255
            },
            {
              "line_index": 19,
              "xheight": 11.86133077963882
            },
            {
              "line_index": 20,
              "xheight": 11.903204371032189
            },
            {
              "line_index": 21,
              "xheight": 11.876020178912427
            },
            {
              "line_index": 22,
              "xheight": 11.906003737889023
            },
            {
              "line_index": 24,
              "xheight": 11.731768957050917
            },
            {
              "line_index": 25,
              "xheight": 11.890579018031076
            },
            {
              "line_index": 26,
              "xheight": 11.875857802015162
            },
            {
              "line_index": 27,
              "xheight": 11.917545222066337
            },
            {
              "line_index": 28,
              "xheight": 11.419636442922297
            },
            {
              "line_index": 29,
              "xheight": 11.434640835028972
            },
            {
              "line_index": 30,
              "xheight": 11.329605804929543
            },
            {
              "line_index": 31,
              "xheight": 11.265610580981502
            },
            {
              "line_index": 33,
              "xheight": 11.46008378378201
            },
            {
              "line_index": 34,
              "xheight": 16.317154219064832
            },
            {
              "line_index": 35,
              "xheight": 11.31320308382783
            },
            {
              "line_index": 37,
              "xheight": 11.4661646186305
            },
            {
              "line_index": 38,
              "xheight": 11.547793740729048
            },
            {
              "line_index": 39,
              "xheight": 11.73122218919275
            },
            {
              "line_index": 40,
              "xheight": 11.305796940837809
            },
            {
              "line_index": 42,
              "xheight": 11.69309665102196
            },
            {
              "line_index": 43,
              "xheight": 11.581523589460403
            },
            {
              "line_index": 44,
              "xheight": 11.354864664344632
            },
            {
              "line_index": 46,
              "xheight": 11.797923183205057
            },
            {
              "line_index": 47,
              "xheight": 11.79673293248311
            },
            {
              "line_index": 48,
              "xheight": 11.916444818951504
            },
            {
              "line_index": 50,
              "xheight": 11.918529099438729
            },
            {
              "line_index": 57,
              "xheight": 11.949400081183057
            },
            {
              "line_index": 58,
              "xheight": 11.850513714628505
            },
            {
              "line_index": 59,
              "xheight": 11.975622649193156
            },
            {
              "line_index": 62,
              "xheight": 11.974471606968564
            },
            {
              "line_index": 63,
              "xheight": 11.953684965114462
            },
            {
              "line_index": 64,
              "xheight": 11.988402638735352
            },
            {
              "line_index": 66,
              "xheight": 11.87906023949563
            },
            {
              "line_index": 67,
              "xheight": 11.947084554115008
            },
            {
              "line_index": 68,
              "xheight": 11.968180499847676
            },
            {
              "line_index": 70,
              "xheight": 11.988739800277926
            },
            {
              "line_index": 71,
              "xheight": 11.903815195030802
            },
            {
              "line_index": 72,
              "xheight": 11.974329916214629
            },
            {
              "line_index": 73,
              "xheight": 13.724797717655534
            },
            {
              "line_index": 74,
              "xheight": 11.972316085316749
            },
            {
              "line_index": 75,
              "xheight": 12.090010135819654
            },
            {
              "line_index": 76,
              "xheight": 12.17184877479454
            },
            {
              "line_index": 77,
              "xheight": 12.104636865842139
            },
            {
              "line_index": 78,
              "xheight": 12.036030012502238
            },
            {
              "line_index": 79,
              "xheight": 12.184065042889188
            },
            {
              "line_index": 80,
              "xheight": 12.10783704686196
            },
            {
              "line_index": 81,
              "xheight": 12.114529790677864
            },
            {
              "line_index": 82,
              "xheight": 12.10880077842603
            },
            {
              "line_index": 83,
              "xheight": 12.073520833216833
            },
            {
              "line_index": 84,
              "xheight": 12.097282834296493
            },
            {
              "line_index": 85,
              "xheight": 12.072843187826493
            },
            {
              "line_index": 86,
              "xheight": 12.153910979950865
            },
            {
              "line_index": 91,
              "xheight": 19.31300740780182
            },
            {
              "line_index": 92,
              "xheight": 12.01539513569901
            },
            {
              "line_index": 93,
              "xheight": 11.974268917450559
            },
            {
              "line_index": 94,
              "xheight": 12.53604800094422
            },
            {
              "line_index": 96,
              "xheight": 11.976332467678844
            },
            {
              "line_index": 97,
              "xheight": 11.982203004591497
            },
            {
              "line_index": 98,
              "xheight": 11.901248159051761
            },
            {
              "line_index": 99,
              "xheight": 12.060823848101109
            },
            {
              "line_index": 100,
              "xheight": 12.032820503407152
            },
            {
              "line_index": 101,
              "xheight": 11.991010626391812
            },
            {
              "line_index": 102,
              "xheight": 11.920776916731029
            },
            {
              "line_index": 103,
              "xheight": 11.876271847663702
            },
            {
              "line_index": 104,
              "xheight": 11.662013529619571
            },
            {
              "line_index": 105,
              "xheight": 11.863659703615212
            },
            {
              "line_index": 106,
              "xheight": 11.906714104684397
            },
            {
              "line_index": 107,
              "xheight": 11.785061651338083
            },
            {
              "line_index": 108,
              "xheight": 11.516196672725528
            },
            {
              "line_index": 109,
              "xheight": 11.766466224727083
            },
            {
              "line_index": 110,
              "xheight": 11.720748120080316
            },
            {
              "line_index": 111,
              "xheight": 11.946215607117665
            },
            {
              "line_index": 112,
              "xheight": 11.849130660601531
            },
            {
              "line_index": 113,
              "xheight": 11.826305566904466
            },
            {
              "line_index": 114,
              "xheight": 11.859306630711444
            },
            {
              "line_index": 115,
              "xheight": 11.994270507941565
            },
            {
              "line_index": 116,
              "xheight": 11.980576837267108
            },
            {
              "line_index": 117,
              "xheight": 11.977248520326611
            },
            {
              "line_index": 118,
              "xheight": 11.893243807348881
            },
            {
              "line_index": 119,
              "xheight": 12.022420851666084
            },
            {
              "line_index": 120,
              "xheight": 12.046392014973662
            },
            {
              "line_index": 121,
              "xheight": 12.016902685685181
            },
            {
              "line_index": 122,
              "xheight": 12.119140513858838
            },
            {
              "line_index": 123,
              "xheight": 12.043824212207255
            },
            {
              "line_index": 124,
              "xheight": 12.17475203120307
            },
            {
              "line_index": 125,
              "xheight": 12.0
            },
            {
              "line_index": 126,
              "xheight": 11.995351932403992
            },
            {
              "line_index": 127,
              "xheight": 12.348439883568744
            },
            {
              "line_index": 128,
              "xheight": 12.113500412591748
            },
            {
              "line_index": 129,
              "xheight": 12.015818999319663
            },
            {
              "line_index": 130,
              "xheight": 12.066122124598678
            },
            {
              "line_index": 131,
              "xheight": 11.975324164252925
            },
            {
              "line_index": 132,
              "xheight": 12.042414678789328
            },
            {
              "line_index": 133,
              "xheight": 12.18308390336756
            },
            {
              "line_index": 134,
              "xheight": 12.069708442069441
            },
            {
              "line_index": 135,
              "xheight": 12.014219056988395
            },
            {
              "line_index": 136,
              "xheight": 12.017250782284009
            },
            {
              "line_index": 137,
              "xheight": 12.002207683676716
            },
            {
              "line_index": 138,
              "xheight": 11.936192030734219
            },
            {
              "line_index": 139,
              "xheight": 12.11583742155699
            },
            {
              "line_index": 140,
              "xheight": 12.04814405840989
            },
            {
              "line_index": 141,
              "xheight": 12.020747010700688
            },
            {
              "line_index": 142,
              "xheight": 11.995747972295248
            }
          ],
          "observed_gap_widths_px": [
            49,
            0.0,
            64,
            40,
            52,
            0.0,
            0.0,
            0.0,
            40,
            40,
            40,
            40,
            0.0,
            0.0,
            39,
            39,
            39,
            39,
            0.0,
            39,
            39,
            0.0,
            0.0,
            0.0,
            38,
            38,
            0.0,
            0.0,
            37,
            68,
            72,
            0.0,
            66,
            66,
            36,
            36,
            36,
            36,
            93,
            93,
            36,
            36,
            35,
            35,
            63,
            63,
            0.0,
            35,
            36,
            36,
            0.0,
            44,
            44,
            36,
            36,
            64,
            0.0,
            44,
            44,
            36,
            36,
            37,
            0.0,
            36,
            36,
            35,
            35,
            36,
            36,
            0.0,
            66,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            66,
            66,
            38,
            38,
            0.0,
            0.0,
            0.0,
            0.0,
            75,
            75,
            46,
            46,
            0.0,
            74,
            74,
            52,
            52,
            45,
            0.0,
            44,
            45,
            76
          ],
          "white_rows": 69,
          "baseline_matching_reach_px": 13.52875000000006,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            837.0,
            296.0
          ],
          [
            837.0,
            500.0
          ]
        ],
        "width": 32,
        "extent": [
          821,
          296,
          853,
          500
        ],
        "source": "detector",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 18.297610523213223,
          "width_xh": 1.7488622330988668,
          "required_width_px": 27.446415784819834,
          "spacing_sides": [
            {
              "samples": 70,
              "letter_q25_xh": 0.12614206055331745,
              "median_xh": 0.1581951441299301,
              "word_q75_xh": 0.2427461897635478,
              "q90_xh": 0.5744993157737299
            },
            {
              "samples": 57,
              "letter_q25_xh": 0.08266319087497422,
              "median_xh": 0.16532638174994843,
              "word_q75_xh": 0.41139021079288945,
              "q90_xh": 0.8261995714704456
            }
          ],
          "side_row_counts": [
            7,
            7
          ],
          "side_span_xh": [
            8.749858337889943,
            9.249787002804691
          ],
          "shared_span_xh": 8.121825514400706,
          "occupied_rows": 14,
          "bilateral_rows": 10,
          "participants": [
            {
              "line_index": 5,
              "xheight": 12.64261309030664
            },
            {
              "line_index": 6,
              "xheight": 12.911044934579024
            },
            {
              "line_index": 7,
              "xheight": 15.855139762479496
            },
            {
              "line_index": 8,
              "xheight": 12.94916773876082
            },
            {
              "line_index": 9,
              "xheight": 12.503884953342663
            },
            {
              "line_index": 10,
              "xheight": 18.297610523213223
            },
            {
              "line_index": 11,
              "xheight": 12.358587390896702
            },
            {
              "line_index": 80,
              "xheight": 12.10783704686196
            },
            {
              "line_index": 81,
              "xheight": 12.114529790677864
            },
            {
              "line_index": 82,
              "xheight": 12.10880077842603
            },
            {
              "line_index": 83,
              "xheight": 12.073520833216833
            },
            {
              "line_index": 84,
              "xheight": 12.097282834296493
            },
            {
              "line_index": 85,
              "xheight": 12.072843187826493
            },
            {
              "line_index": 86,
              "xheight": 12.153910979950865
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            40,
            40,
            40,
            40,
            0.0,
            0.0,
            39,
            39,
            39,
            39,
            0.0,
            39,
            39
          ],
          "white_rows": 10,
          "baseline_matching_reach_px": 13.400999999999996,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            842.0,
            1082.0
          ],
          [
            842.0,
            1306.0
          ]
        ],
        "width": 32,
        "extent": [
          826,
          1082,
          858,
          1306
        ],
        "source": "detector",
        "proposal_id": "proposal-0003",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 16.317154219064832,
          "width_xh": 1.961126282830094,
          "required_width_px": 24.47573132859725,
          "spacing_sides": [
            {
              "samples": 62,
              "letter_q25_xh": 0.135226108560197,
              "median_xh": 0.17678459276126587,
              "word_q75_xh": 0.25978988431521816,
              "q90_xh": 0.695348185733975
            },
            {
              "samples": 75,
              "letter_q25_xh": 0.08531878594735534,
              "median_xh": 0.16797245507164318,
              "word_q75_xh": 0.17366844773819426,
              "q90_xh": 0.6859878853408404
            }
          ],
          "side_row_counts": [
            7,
            8
          ],
          "side_span_xh": [
            10.105407952039963,
            11.967956996559671
          ],
          "shared_span_xh": 10.105407952039963,
          "occupied_rows": 10,
          "bilateral_rows": 8,
          "participants": [
            {
              "line_index": 33,
              "xheight": 11.46008378378201
            },
            {
              "line_index": 34,
              "xheight": 16.317154219064832
            },
            {
              "line_index": 35,
              "xheight": 11.31320308382783
            },
            {
              "line_index": 37,
              "xheight": 11.4661646186305
            },
            {
              "line_index": 38,
              "xheight": 11.547793740729048
            },
            {
              "line_index": 39,
              "xheight": 11.73122218919275
            },
            {
              "line_index": 40,
              "xheight": 11.305796940837809
            },
            {
              "line_index": 104,
              "xheight": 11.662013529619571
            },
            {
              "line_index": 105,
              "xheight": 11.863659703615212
            },
            {
              "line_index": 106,
              "xheight": 11.906714104684397
            },
            {
              "line_index": 107,
              "xheight": 11.785061651338083
            },
            {
              "line_index": 108,
              "xheight": 11.516196672725528
            },
            {
              "line_index": 109,
              "xheight": 11.766466224727083
            },
            {
              "line_index": 110,
              "xheight": 11.720748120080316
            },
            {
              "line_index": 111,
              "xheight": 11.946215607117665
            }
          ],
          "observed_gap_widths_px": [
            35,
            36,
            36,
            0.0,
            44,
            44,
            36,
            36,
            64,
            0.0
          ],
          "white_rows": 8,
          "baseline_matching_reach_px": 12.416875000000061,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0002",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            848.0,
            1851.0
          ],
          [
            848.0,
            2106.0
          ]
        ],
        "width": 32,
        "extent": [
          832,
          1851,
          864,
          2106
        ],
        "source": "detector",
        "proposal_id": "proposal-0004",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 12.18308390336756,
          "width_xh": 2.6265927620472835,
          "required_width_px": 18.27462585505134,
          "spacing_sides": [
            {
              "samples": 55,
              "letter_q25_xh": 0.0837024292805866,
              "median_xh": 0.16710977913689176,
              "word_q75_xh": 0.2508166518980607,
              "q90_xh": 0.8016195519191666
            },
            {
              "samples": 77,
              "letter_q25_xh": 0.08350504640075307,
              "median_xh": 0.16607964875372222,
              "word_q75_xh": 0.24855612829415022,
              "q90_xh": 0.6150621579172159
            }
          ],
          "side_row_counts": [
            6,
            9
          ],
          "side_span_xh": [
            13.512342302304628,
            19.349205986740397
          ],
          "shared_span_xh": 13.512342302304628,
          "occupied_rows": 14,
          "bilateral_rows": 9,
          "participants": [
            {
              "line_index": 62,
              "xheight": 11.974471606968564
            },
            {
              "line_index": 63,
              "xheight": 11.953684965114462
            },
            {
              "line_index": 64,
              "xheight": 11.988402638735352
            },
            {
              "line_index": 66,
              "xheight": 11.87906023949563
            },
            {
              "line_index": 67,
              "xheight": 11.947084554115008
            },
            {
              "line_index": 68,
              "xheight": 11.968180499847676
            },
            {
              "line_index": 131,
              "xheight": 11.975324164252925
            },
            {
              "line_index": 132,
              "xheight": 12.042414678789328
            },
            {
              "line_index": 133,
              "xheight": 12.18308390336756
            },
            {
              "line_index": 134,
              "xheight": 12.069708442069441
            },
            {
              "line_index": 135,
              "xheight": 12.014219056988395
            },
            {
              "line_index": 136,
              "xheight": 12.017250782284009
            },
            {
              "line_index": 137,
              "xheight": 12.002207683676716
            },
            {
              "line_index": 138,
              "xheight": 11.936192030734219
            },
            {
              "line_index": 139,
              "xheight": 12.11583742155699
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            0.0,
            0.0,
            75,
            75,
            46,
            46,
            0.0,
            74,
            74,
            52,
            52,
            45,
            0.0
          ],
          "white_rows": 9,
          "baseline_matching_reach_px": 13.420500000000061,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0003",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "56f93f904a6a92ac77917b1868e6fbfe8c65cff9a3430fd0944cf43cf7f7dd07"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.8062815357067142,
    "polarity_confidence": 0.75,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## ia_poly1850--b3d418e8a99d8bec--s034-l0015

Card `k6ca1372aaa`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/d1a621cfb3d277cc2220c2175ba0b9480d74da1268c11e37da63a32d85438d30.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/d1a621cfb3d277cc2220c2175ba0b9480d74da1268c11e37da63a32d85438d30.png`; SHA-256 `d1a621cfb3d277cc2220c2175ba0b9480d74da1268c11e37da63a32d85438d30`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k6ca1372aaa",
  "letters": "y",
  "marks": "n",
  "crop_ok": "y",
  "errors": [
    "missing_mark"
  ],
  "detail": "Οἴμοι → Οίμοι; τί → τι",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only the main line is complete.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "ia_poly1850--b3d418e8a99d8bec--s034-l0015"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00010",
  "neighbour_rows": [
    {
      "row_id": "row-00009",
      "column_id": "single:column-0000",
      "xheight": 8.948667318842183,
      "profile_runs": [
        [
          500,
          507
        ],
        [
          509,
          513
        ],
        [
          514,
          522
        ],
        [
          523,
          530
        ],
        [
          541,
          551
        ],
        [
          552,
          560
        ],
        [
          562,
          568
        ],
        [
          570,
          577
        ],
        [
          579,
          585
        ],
        [
          597,
          605
        ],
        [
          606,
          614
        ],
        [
          616,
          620
        ],
        [
          628,
          636
        ],
        [
          638,
          647
        ],
        [
          648,
          655
        ],
        [
          656,
          662
        ],
        [
          663,
          670
        ],
        [
          671,
          679
        ],
        [
          681,
          684
        ],
        [
          685,
          693
        ],
        [
          695,
          701
        ],
        [
          709,
          715
        ],
        [
          718,
          724
        ],
        [
          726,
          732
        ],
        [
          734,
          739
        ],
        [
          741,
          758
        ],
        [
          760,
          770
        ],
        [
          771,
          776
        ],
        [
          778,
          784
        ],
        [
          785,
          792
        ],
        [
          794,
          799
        ],
        [
          804,
          807
        ],
        [
          819,
          829
        ],
        [
          830,
          837
        ],
        [
          838,
          843
        ],
        [
          845,
          861
        ],
        [
          863,
          870
        ],
        [
          872,
          889
        ],
        [
          890,
          894
        ]
      ],
      "profile_gaps": [
        [
          507,
          509
        ],
        [
          513,
          514
        ],
        [
          522,
          523
        ],
        [
          530,
          541
        ],
        [
          551,
          552
        ],
        [
          560,
          562
        ],
        [
          568,
          570
        ],
        [
          577,
          579
        ],
        [
          585,
          597
        ],
        [
          605,
          606
        ],
        [
          614,
          616
        ],
        [
          620,
          628
        ],
        [
          636,
          638
        ],
        [
          647,
          648
        ],
        [
          655,
          656
        ],
        [
          662,
          663
        ],
        [
          670,
          671
        ],
        [
          679,
          681
        ],
        [
          684,
          685
        ],
        [
          693,
          695
        ],
        [
          701,
          709
        ],
        [
          715,
          718
        ],
        [
          724,
          726
        ],
        [
          732,
          734
        ],
        [
          739,
          741
        ],
        [
          758,
          760
        ],
        [
          770,
          771
        ],
        [
          776,
          778
        ],
        [
          784,
          785
        ],
        [
          792,
          794
        ],
        [
          799,
          804
        ],
        [
          807,
          819
        ],
        [
          829,
          830
        ],
        [
          837,
          838
        ],
        [
          843,
          845
        ],
        [
          861,
          863
        ],
        [
          870,
          872
        ],
        [
          889,
          890
        ]
      ],
      "directional_missing": {
        "above": 8024,
        "below": 0
      },
      "groups": [
        {
          "box": [
            541,
            344,
            585,
            357
          ],
          "body_count": 5,
          "width_xh": 4.916933263051834,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            709,
            340,
            799,
            358
          ],
          "body_count": 10,
          "width_xh": 10.057363492606024,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            819,
            341,
            894,
            358
          ],
          "body_count": 7,
          "width_xh": 8.381136243838354,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      495,
      356,
      895,
      381
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00010"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00010"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00009",
      "column_id": "single:column-0000",
      "xheight": 8.948667318842183,
      "assigned_pixels": 22,
      "supported": null,
      "runs": []
    },
    {
      "row_id": "row-00010",
      "column_id": "single:column-0000",
      "xheight": 8.583723684359427,
      "assigned_pixels": 1591,
      "supported": null,
      "runs": [
        {
          "x0": 499,
          "x1": 510,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 511,
          "x1": 519,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 520,
          "x1": 526,
          "body_cut_fraction": 0.0,
          "body_pixels": 19,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 528,
          "x1": 542,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 543,
          "x1": 550,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 551,
          "x1": 557,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 558,
          "x1": 565,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 567,
          "x1": 570,
          "body_cut_fraction": 0.0,
          "body_pixels": 8,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 582,
          "x1": 592,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 593,
          "x1": 597,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 599,
          "x1": 608,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 609,
          "x1": 616,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 618,
          "x1": 621,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 632,
          "x1": 639,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 640,
          "x1": 643,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 644,
          "x1": 658,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 666,
          "x1": 674,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 675,
          "x1": 683,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 684,
          "x1": 692,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 693,
          "x1": 711,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 716,
          "x1": 719,
          "body_cut_fraction": 0.0,
          "body_pixels": 17,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 730,
          "x1": 737,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 739,
          "x1": 743,
          "body_cut_fraction": 0.0,
          "body_pixels": 22,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 755,
          "x1": 765,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 767,
          "x1": 774,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 775,
          "x1": 778,
          "body_cut_fraction": 0.0,
          "body_pixels": 17,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 779,
          "x1": 793,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 794,
          "x1": 801,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 802,
          "x1": 809,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 821,
          "x1": 828,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 830,
          "x1": 838,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 839,
          "x1": 846,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 848,
          "x1": 854,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 855,
          "x1": 864,
          "body_cut_fraction": 0.0,
          "body_pixels": 36,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 866,
          "x1": 880,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 881,
          "x1": 885,
          "body_cut_fraction": 0.0,
          "body_pixels": 19,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 890,
          "x1": 893,
          "body_cut_fraction": 0.0,
          "body_pixels": 12,
          "body_extent_px": 8,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 133,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 3.203145871332566,
        "required_common_rows": 1.7897334637684368,
        "xheight_px": 8.948667318842183,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          500,
          337.527,
          894,
          359.611
        ],
        "boundary_path": [
          [
            907.0,
            0.0
          ],
          [
            907.0,
            1729.0
          ]
        ],
        "row_id": "row-00009"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          33,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 2.9472124915773192,
        "required_common_rows": 1.7167447368718856,
        "xheight_px": 8.583723684359427,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          499,
          358.513,
          893,
          380.663
        ],
        "boundary_path": [
          [
            907.0,
            0.0
          ],
          [
            907.0,
            1729.0
          ]
        ],
        "row_id": "row-00010"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 3.203145871332566,
        "required_common_rows": 1.7897334637684368,
        "xheight_px": 8.948667318842183,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          500,
          337.527,
          894,
          359.611
        ],
        "boundary_path": [
          [
            906.5,
            565.0
          ],
          [
            906.5,
            732.0
          ]
        ],
        "row_id": "row-00009"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 2.9472124915773192,
        "required_common_rows": 1.7167447368718856,
        "xheight_px": 8.583723684359427,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          499,
          358.513,
          893,
          380.663
        ],
        "boundary_path": [
          [
            906.5,
            565.0
          ],
          [
            906.5,
            732.0
          ]
        ],
        "row_id": "row-00010"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 3.203145871332566,
        "required_common_rows": 1.7897334637684368,
        "xheight_px": 8.948667318842183,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          500,
          337.527,
          894,
          359.611
        ],
        "boundary_path": [
          [
            906.5,
            1254.0
          ],
          [
            906.5,
            1401.0
          ]
        ],
        "row_id": "row-00009"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 2.9472124915773192,
        "required_common_rows": 1.7167447368718856,
        "xheight_px": 8.583723684359427,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          499,
          358.513,
          893,
          380.663
        ],
        "boundary_path": [
          [
            906.5,
            1254.0
          ],
          [
            906.5,
            1401.0
          ]
        ],
        "row_id": "row-00010"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 3.203145871332566,
        "required_common_rows": 1.7897334637684368,
        "xheight_px": 8.948667318842183,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          500,
          337.527,
          894,
          359.611
        ],
        "boundary_path": [
          [
            906.0,
            1401.0
          ],
          [
            906.0,
            1548.0
          ]
        ],
        "row_id": "row-00009"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 2.9472124915773192,
        "required_common_rows": 1.7167447368718856,
        "xheight_px": 8.583723684359427,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          499,
          358.513,
          893,
          380.663
        ],
        "boundary_path": [
          [
            906.0,
            1401.0
          ],
          [
            906.0,
            1548.0
          ]
        ],
        "row_id": "row-00010"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            907.0,
            0.0
          ],
          [
            907.0,
            1729.0
          ]
        ],
        "width": 22,
        "extent": [
          896,
          0,
          918,
          1729
        ],
        "source": "detector",
        "proposal_id": "proposal-0000",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 22.0,
          "local_xheight_max_px": 10.586133926523871,
          "width_xh": 2.0781902205939744,
          "required_width_px": 15.879200889785807,
          "spacing_sides": [
            {
              "samples": 524,
              "letter_q25_xh": 0.11241561929808756,
              "median_xh": 0.1188821566720189,
              "word_q75_xh": 0.23592889413826942,
              "q90_xh": 0.9433488214991981
            },
            {
              "samples": 533,
              "letter_q25_xh": 0.11178596510303684,
              "median_xh": 0.12217314331252935,
              "word_q75_xh": 0.23960143971222148,
              "q90_xh": 0.8886673141268407
            }
          ],
          "side_row_counts": [
            68,
            67
          ],
          "side_span_xh": [
            132.70576489497543,
            132.44277936887846
          ],
          "shared_span_xh": 132.40489962894853,
          "occupied_rows": 76,
          "bilateral_rows": 75,
          "participants": [
            {
              "line_index": 0,
              "xheight": 9.254713813449314
            },
            {
              "line_index": 1,
              "xheight": 8.507877198032773
            },
            {
              "line_index": 2,
              "xheight": 8.723654702094876
            },
            {
              "line_index": 3,
              "xheight": 8.887317842999948
            },
            {
              "line_index": 4,
              "xheight": 8.947182943347343
            },
            {
              "line_index": 5,
              "xheight": 8.895561010506412
            },
            {
              "line_index": 6,
              "xheight": 8.813535820184768
            },
            {
              "line_index": 7,
              "xheight": 8.880958469372786
            },
            {
              "line_index": 8,
              "xheight": 8.404114724672297
            },
            {
              "line_index": 9,
              "xheight": 8.948667318842183
            },
            {
              "line_index": 10,
              "xheight": 8.583723684359427
            },
            {
              "line_index": 11,
              "xheight": 8.563469287880139
            },
            {
              "line_index": 12,
              "xheight": 8.188085257372336
            },
            {
              "line_index": 13,
              "xheight": 8.088141175195005
            },
            {
              "line_index": 14,
              "xheight": 8.507426033090724
            },
            {
              "line_index": 15,
              "xheight": 8.913852815859627
            },
            {
              "line_index": 16,
              "xheight": 8.199866409632477
            },
            {
              "line_index": 17,
              "xheight": 8.61842379287458
            },
            {
              "line_index": 18,
              "xheight": 8.763308531084022
            },
            {
              "line_index": 19,
              "xheight": 8.430929704085202
            },
            {
              "line_index": 20,
              "xheight": 8.485267861370744
            },
            {
              "line_index": 21,
              "xheight": 8.390689182081871
            },
            {
              "line_index": 22,
              "xheight": 8.623028257327292
            },
            {
              "line_index": 23,
              "xheight": 8.57216316074937
            },
            {
              "line_index": 24,
              "xheight": 8.640781373288405
            },
            {
              "line_index": 25,
              "xheight": 8.41928149808325
            },
            {
              "line_index": 26,
              "xheight": 8.845954136798696
            },
            {
              "line_index": 27,
              "xheight": 8.452811381731863
            },
            {
              "line_index": 28,
              "xheight": 8.984107002970518
            },
            {
              "line_index": 29,
              "xheight": 8.936752400725481
            },
            {
              "line_index": 30,
              "xheight": 8.983092338925758
            },
            {
              "line_index": 31,
              "xheight": 8.117780040940147
            },
            {
              "line_index": 32,
              "xheight": 8.747668442468353
            },
            {
              "line_index": 33,
              "xheight": 8.882900524523734
            },
            {
              "line_index": 34,
              "xheight": 9.016649322269245
            },
            {
              "line_index": 35,
              "xheight": 8.948239732379989
            },
            {
              "line_index": 36,
              "xheight": 8.931723425396626
            },
            {
              "line_index": 37,
              "xheight": 8.989516278223164
            },
            {
              "line_index": 38,
              "xheight": 8.762085736760014
            },
            {
              "line_index": 39,
              "xheight": 8.752126681561094
            },
            {
              "line_index": 40,
              "xheight": 9.01430507150144
            },
            {
              "line_index": 41,
              "xheight": 8.952186208239254
            },
            {
              "line_index": 42,
              "xheight": 8.725728144701407
            },
            {
              "line_index": 43,
              "xheight": 9.000379135746698
            },
            {
              "line_index": 44,
              "xheight": 8.907969034554526
            },
            {
              "line_index": 45,
              "xheight": 8.930805057052112
            },
            {
              "line_index": 46,
              "xheight": 8.977546919579254
            },
            {
              "line_index": 47,
              "xheight": 8.953357829097058
            },
            {
              "line_index": 48,
              "xheight": 9.015106878990082
            },
            {
              "line_index": 49,
              "xheight": 8.798746338110504
            },
            {
              "line_index": 50,
              "xheight": 8.669091005034488
            },
            {
              "line_index": 51,
              "xheight": 8.781586047937935
            },
            {
              "line_index": 52,
              "xheight": 8.813796452777979
            },
            {
              "line_index": 53,
              "xheight": 8.944745422025335
            },
            {
              "line_index": 54,
              "xheight": 8.869312220735537
            },
            {
              "line_index": 55,
              "xheight": 9.001140690198099
            },
            {
              "line_index": 56,
              "xheight": 9.270762135879977
            },
            {
              "line_index": 57,
              "xheight": 9.272909809502607
            },
            {
              "line_index": 58,
              "xheight": 9.00682014727181
            },
            {
              "line_index": 59,
              "xheight": 9.127382934502066
            },
            {
              "line_index": 60,
              "xheight": 8.923716737526775
            },
            {
              "line_index": 61,
              "xheight": 8.987762625137066
            },
            {
              "line_index": 62,
              "xheight": 9.003834371492076
            },
            {
              "line_index": 63,
              "xheight": 8.901463350825907
            },
            {
              "line_index": 64,
              "xheight": 8.872807127378337
            },
            {
              "line_index": 65,
              "xheight": 8.998442585888824
            },
            {
              "line_index": 66,
              "xheight": 9.033997301848558
            },
            {
              "line_index": 67,
              "xheight": 10.586133926523871
            },
            {
              "line_index": 68,
              "xheight": 8.613660863556532
            },
            {
              "line_index": 69,
              "xheight": 9.052625050538552
            },
            {
              "line_index": 70,
              "xheight": 8.989518039012978
            },
            {
              "line_index": 71,
              "xheight": 8.185104949308823
            },
            {
              "line_index": 72,
              "xheight": 9.073620576076848
            },
            {
              "line_index": 73,
              "xheight": 8.487662126870532
            },
            {
              "line_index": 74,
              "xheight": 8.59364274365953
            },
            {
              "line_index": 75,
              "xheight": 8.9527943905602
            },
            {
              "line_index": 76,
              "xheight": 8.749908273833626
            },
            {
              "line_index": 77,
              "xheight": 8.76366462631222
            },
            {
              "line_index": 78,
              "xheight": 8.976139737973938
            },
            {
              "line_index": 79,
              "xheight": 8.858571954934177
            },
            {
              "line_index": 80,
              "xheight": 8.347195252257848
            },
            {
              "line_index": 81,
              "xheight": 8.598439254265429
            },
            {
              "line_index": 82,
              "xheight": 9.1693442900513
            },
            {
              "line_index": 83,
              "xheight": 8.663225627497354
            },
            {
              "line_index": 84,
              "xheight": 8.973555844498378
            },
            {
              "line_index": 85,
              "xheight": 8.615460155473215
            },
            {
              "line_index": 86,
              "xheight": 8.675914068202246
            },
            {
              "line_index": 87,
              "xheight": 8.448170763610051
            },
            {
              "line_index": 88,
              "xheight": 8.780382342720486
            },
            {
              "line_index": 89,
              "xheight": 9.000442845304292
            },
            {
              "line_index": 90,
              "xheight": 8.807031033974681
            },
            {
              "line_index": 91,
              "xheight": 8.949784319708783
            },
            {
              "line_index": 92,
              "xheight": 8.864088670269098
            },
            {
              "line_index": 93,
              "xheight": 8.949588813999753
            },
            {
              "line_index": 94,
              "xheight": 8.915349766763029
            },
            {
              "line_index": 95,
              "xheight": 8.676493669898036
            },
            {
              "line_index": 96,
              "xheight": 8.941493380042175
            },
            {
              "line_index": 97,
              "xheight": 8.930673937581673
            },
            {
              "line_index": 98,
              "xheight": 9.353533530247205
            },
            {
              "line_index": 99,
              "xheight": 8.953982900466372
            },
            {
              "line_index": 100,
              "xheight": 8.965978535534418
            },
            {
              "line_index": 101,
              "xheight": 8.988550072513704
            },
            {
              "line_index": 102,
              "xheight": 9.887443185690813
            },
            {
              "line_index": 103,
              "xheight": 9.18259376577305
            },
            {
              "line_index": 104,
              "xheight": 8.72045931674063
            },
            {
              "line_index": 105,
              "xheight": 8.863115105049474
            },
            {
              "line_index": 106,
              "xheight": 8.749522647232425
            },
            {
              "line_index": 107,
              "xheight": 8.977511281796751
            },
            {
              "line_index": 108,
              "xheight": 8.770770339804471
            },
            {
              "line_index": 109,
              "xheight": 8.505253194827446
            },
            {
              "line_index": 110,
              "xheight": 8.948196026717369
            },
            {
              "line_index": 111,
              "xheight": 9.01144807213268
            },
            {
              "line_index": 112,
              "xheight": 8.535297989561059
            },
            {
              "line_index": 113,
              "xheight": 8.979030104667117
            },
            {
              "line_index": 114,
              "xheight": 6.689666315688555
            },
            {
              "line_index": 115,
              "xheight": 9.093361588023527
            },
            {
              "line_index": 116,
              "xheight": 8.954166643757844
            },
            {
              "line_index": 117,
              "xheight": 8.945666829268475
            },
            {
              "line_index": 118,
              "xheight": 8.53424350678506
            },
            {
              "line_index": 119,
              "xheight": 8.867785969231136
            },
            {
              "line_index": 120,
              "xheight": 8.880484491560765
            },
            {
              "line_index": 121,
              "xheight": 10.139800517761046
            },
            {
              "line_index": 122,
              "xheight": 8.990013775264515
            },
            {
              "line_index": 123,
              "xheight": 9.011231220450554
            },
            {
              "line_index": 124,
              "xheight": 9.395447306265169
            },
            {
              "line_index": 125,
              "xheight": 9.276468658339127
            },
            {
              "line_index": 126,
              "xheight": 9.269363489917396
            },
            {
              "line_index": 127,
              "xheight": 8.988198296938435
            },
            {
              "line_index": 128,
              "xheight": 8.937808615457925
            },
            {
              "line_index": 129,
              "xheight": 8.12912856633784
            },
            {
              "line_index": 130,
              "xheight": 8.939361195699803
            },
            {
              "line_index": 131,
              "xheight": 9.0
            },
            {
              "line_index": 132,
              "xheight": 8.98502784341349
            },
            {
              "line_index": 133,
              "xheight": 8.863885187725145
            },
            {
              "line_index": 134,
              "xheight": 9.388448132159965
            }
          ],
          "observed_gap_widths_px": [
            24,
            27,
            26,
            26,
            28,
            28,
            26,
            26,
            0.0,
            27,
            27,
            27,
            27,
            26,
            26,
            27,
            26,
            25,
            27,
            27,
            26,
            26,
            27,
            25,
            25,
            25,
            25,
            26,
            25,
            26,
            25,
            25,
            25,
            26,
            26,
            25,
            25,
            24,
            25,
            25,
            25,
            24,
            24,
            25,
            26,
            26,
            25,
            25,
            26,
            25,
            26,
            25,
            26,
            28,
            24,
            26,
            26,
            26,
            26,
            27,
            26,
            26,
            25,
            27,
            27,
            25,
            25,
            24,
            26,
            26,
            26,
            26,
            25,
            26,
            28,
            27
          ],
          "white_rows": 75,
          "baseline_matching_reach_px": 10.418499999999995,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            906.5,
            565.0
          ],
          [
            906.5,
            732.0
          ]
        ],
        "width": 23,
        "extent": [
          895,
          565,
          918,
          732
        ],
        "source": "detector",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 23.0,
          "local_xheight_max_px": 9.000442845304292,
          "width_xh": 2.555429815545082,
          "required_width_px": 13.500664267956438,
          "spacing_sides": [
            {
              "samples": 66,
              "letter_q25_xh": 0.11665666894662573,
              "median_xh": 0.11897735125702107,
              "word_q75_xh": 0.23835944302059897,
              "q90_xh": 0.9740425528466743
            },
            {
              "samples": 65,
              "letter_q25_xh": 0.11216609848870555,
              "median_xh": 0.11389025682111277,
              "word_q75_xh": 0.22778051364222554,
              "q90_xh": 0.9025774120775898
            }
          ],
          "side_row_counts": [
            8,
            8
          ],
          "side_span_xh": [
            16.278254583488398,
            16.152316335839686
          ],
          "shared_span_xh": 15.918216743606928,
          "occupied_rows": 8,
          "bilateral_rows": 8,
          "participants": [
            {
              "line_index": 20,
              "xheight": 8.485267861370744
            },
            {
              "line_index": 21,
              "xheight": 8.390689182081871
            },
            {
              "line_index": 22,
              "xheight": 8.623028257327292
            },
            {
              "line_index": 23,
              "xheight": 8.57216316074937
            },
            {
              "line_index": 24,
              "xheight": 8.640781373288405
            },
            {
              "line_index": 25,
              "xheight": 8.41928149808325
            },
            {
              "line_index": 26,
              "xheight": 8.845954136798696
            },
            {
              "line_index": 27,
              "xheight": 8.452811381731863
            },
            {
              "line_index": 87,
              "xheight": 8.448170763610051
            },
            {
              "line_index": 88,
              "xheight": 8.780382342720486
            },
            {
              "line_index": 89,
              "xheight": 9.000442845304292
            },
            {
              "line_index": 90,
              "xheight": 8.807031033974681
            },
            {
              "line_index": 91,
              "xheight": 8.949784319708783
            },
            {
              "line_index": 92,
              "xheight": 8.864088670269098
            },
            {
              "line_index": 93,
              "xheight": 8.949588813999753
            },
            {
              "line_index": 94,
              "xheight": 8.915349766763029
            }
          ],
          "observed_gap_widths_px": [
            25,
            25,
            26,
            25,
            26,
            25,
            25,
            25
          ],
          "white_rows": 8,
          "baseline_matching_reach_px": 10.416750000000036,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            906.5,
            1254.0
          ],
          [
            906.5,
            1401.0
          ]
        ],
        "width": 23,
        "extent": [
          895,
          1254,
          918,
          1401
        ],
        "source": "detector",
        "proposal_id": "proposal-0002",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 23.0,
          "local_xheight_max_px": 10.139800517761046,
          "width_xh": 2.268289199547152,
          "required_width_px": 16.929486784620853,
          "spacing_sides": [
            {
              "samples": 48,
              "letter_q25_xh": 0.11102697551953479,
              "median_xh": 0.11274831408709496,
              "word_q75_xh": 0.7696120610561834,
              "q90_xh": 1.1130716529690354
            },
            {
              "samples": 56,
              "letter_q25_xh": 0.10788227272430671,
              "median_xh": 0.11260646881938846,
              "word_q75_xh": 0.22315503658681218,
              "q90_xh": 0.8208499626438354
            }
          ],
          "side_row_counts": [
            7,
            7
          ],
          "side_span_xh": [
            12.3395425561713,
            12.23801195917417
          ],
          "shared_span_xh": 11.85703799491979,
          "occupied_rows": 8,
          "bilateral_rows": 8,
          "participants": [
            {
              "line_index": 53,
              "xheight": 8.944745422025335
            },
            {
              "line_index": 54,
              "xheight": 8.869312220735537
            },
            {
              "line_index": 55,
              "xheight": 9.001140690198099
            },
            {
              "line_index": 56,
              "xheight": 9.270762135879977
            },
            {
              "line_index": 57,
              "xheight": 9.272909809502607
            },
            {
              "line_index": 58,
              "xheight": 9.00682014727181
            },
            {
              "line_index": 59,
              "xheight": 9.127382934502066
            },
            {
              "line_index": 120,
              "xheight": 8.880484491560765
            },
            {
              "line_index": 121,
              "xheight": 10.139800517761046
            },
            {
              "line_index": 122,
              "xheight": 8.990013775264515
            },
            {
              "line_index": 123,
              "xheight": 9.011231220450554
            },
            {
              "line_index": 124,
              "xheight": 9.395447306265169
            },
            {
              "line_index": 125,
              "xheight": 9.276468658339127
            },
            {
              "line_index": 126,
              "xheight": 9.269363489917396
            }
          ],
          "observed_gap_widths_px": [
            26,
            27,
            26,
            26,
            25,
            27,
            27,
            25
          ],
          "white_rows": 8,
          "baseline_matching_reach_px": 10.286000000000058,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0002",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            906.0,
            1401.0
          ],
          [
            906.0,
            1548.0
          ]
        ],
        "width": 20,
        "extent": [
          896,
          1401,
          916,
          1548
        ],
        "source": "detector",
        "proposal_id": "proposal-0003",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 20.0,
          "local_xheight_max_px": 9.033997301848558,
          "width_xh": 2.2138594170166015,
          "required_width_px": 13.550995952772837,
          "spacing_sides": [
            {
              "samples": 56,
              "letter_q25_xh": 0.11122938208024116,
              "median_xh": 0.11270390369631213,
              "word_q75_xh": 0.22468215855929277,
              "q90_xh": 0.7807041582159933
            },
            {
              "samples": 53,
              "letter_q25_xh": 0.11188424848015896,
              "median_xh": 0.2222222222222222,
              "word_q75_xh": 0.4920576624367492,
              "q90_xh": 0.72473029310029
            }
          ],
          "side_row_counts": [
            7,
            7
          ],
          "side_span_xh": [
            14.049373246329058,
            14.331252896600688
          ],
          "shared_span_xh": 13.857985099727967,
          "occupied_rows": 9,
          "bilateral_rows": 9,
          "participants": [
            {
              "line_index": 60,
              "xheight": 8.923716737526775
            },
            {
              "line_index": 61,
              "xheight": 8.987762625137066
            },
            {
              "line_index": 62,
              "xheight": 9.003834371492076
            },
            {
              "line_index": 63,
              "xheight": 8.901463350825907
            },
            {
              "line_index": 64,
              "xheight": 8.872807127378337
            },
            {
              "line_index": 65,
              "xheight": 8.998442585888824
            },
            {
              "line_index": 66,
              "xheight": 9.033997301848558
            },
            {
              "line_index": 127,
              "xheight": 8.988198296938435
            },
            {
              "line_index": 128,
              "xheight": 8.937808615457925
            },
            {
              "line_index": 129,
              "xheight": 8.12912856633784
            },
            {
              "line_index": 130,
              "xheight": 8.939361195699803
            },
            {
              "line_index": 131,
              "xheight": 9.0
            },
            {
              "line_index": 132,
              "xheight": 8.98502784341349
            },
            {
              "line_index": 133,
              "xheight": 8.863885187725145
            }
          ],
          "observed_gap_widths_px": [
            25,
            24,
            26,
            26,
            26,
            26,
            25,
            26,
            28
          ],
          "white_rows": 9,
          "baseline_matching_reach_px": 10.932875000000024,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0003",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "eed7b6470145a2248da9bbf5404c8e290b5dc119c7806d1ff4e0609de061df89"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 1.0,
    "polarity_confidence": 1.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--80010a2714d1484a--s000-l0137

Card `k90c9feff29`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/23ba90395d78a44eddc2e3bbdd5f2e172bbcfc8a5254655a1b27707a366c296d.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/23ba90395d78a44eddc2e3bbdd5f2e172bbcfc8a5254655a1b27707a366c296d.png`; SHA-256 `23ba90395d78a44eddc2e3bbdd5f2e172bbcfc8a5254655a1b27707a366c296d`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k90c9feff29",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "The neighbouring words are cut through their letter bodies; none is complete.",
  "multi_line": "no",
  "multi_line_reason": "Only the main line is complete.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--80010a2714d1484a--s000-l0137"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00130",
  "neighbour_rows": [
    {
      "row_id": "row-00129",
      "column_id": "single:column-0001",
      "xheight": 11.984593916782615,
      "profile_runs": [
        [
          836,
          847
        ],
        [
          848,
          859
        ],
        [
          860,
          869
        ],
        [
          871,
          882
        ],
        [
          884,
          893
        ],
        [
          894,
          904
        ],
        [
          906,
          916
        ],
        [
          917,
          927
        ],
        [
          928,
          933
        ],
        [
          935,
          946
        ],
        [
          948,
          964
        ],
        [
          966,
          976
        ],
        [
          986,
          995
        ],
        [
          997,
          1010
        ],
        [
          1011,
          1022
        ],
        [
          1023,
          1034
        ],
        [
          1035,
          1045
        ],
        [
          1046,
          1065
        ],
        [
          1067,
          1077
        ],
        [
          1079,
          1088
        ],
        [
          1089,
          1106
        ],
        [
          1108,
          1117
        ],
        [
          1127,
          1137
        ],
        [
          1138,
          1150
        ],
        [
          1151,
          1161
        ],
        [
          1171,
          1178
        ],
        [
          1180,
          1190
        ],
        [
          1191,
          1203
        ],
        [
          1205,
          1210
        ],
        [
          1211,
          1221
        ],
        [
          1223,
          1231
        ],
        [
          1233,
          1238
        ],
        [
          1239,
          1251
        ],
        [
          1252,
          1262
        ],
        [
          1264,
          1268
        ],
        [
          1279,
          1291
        ],
        [
          1301,
          1314
        ],
        [
          1315,
          1327
        ],
        [
          1329,
          1339
        ],
        [
          1341,
          1364
        ],
        [
          1366,
          1377
        ],
        [
          1388,
          1398
        ],
        [
          1399,
          1412
        ],
        [
          1413,
          1425
        ],
        [
          1427,
          1437
        ],
        [
          1439,
          1447
        ],
        [
          1449,
          1459
        ],
        [
          1461,
          1465
        ],
        [
          1467,
          1484
        ],
        [
          1485,
          1494
        ],
        [
          1504,
          1515
        ],
        [
          1516,
          1525
        ],
        [
          1527,
          1537
        ],
        [
          1539,
          1549
        ],
        [
          1551,
          1560
        ]
      ],
      "profile_gaps": [
        [
          847,
          848
        ],
        [
          859,
          860
        ],
        [
          869,
          871
        ],
        [
          882,
          884
        ],
        [
          893,
          894
        ],
        [
          904,
          906
        ],
        [
          916,
          917
        ],
        [
          927,
          928
        ],
        [
          933,
          935
        ],
        [
          946,
          948
        ],
        [
          964,
          966
        ],
        [
          976,
          986
        ],
        [
          995,
          997
        ],
        [
          1010,
          1011
        ],
        [
          1022,
          1023
        ],
        [
          1034,
          1035
        ],
        [
          1045,
          1046
        ],
        [
          1065,
          1067
        ],
        [
          1077,
          1079
        ],
        [
          1088,
          1089
        ],
        [
          1106,
          1108
        ],
        [
          1117,
          1127
        ],
        [
          1137,
          1138
        ],
        [
          1150,
          1151
        ],
        [
          1161,
          1171
        ],
        [
          1178,
          1180
        ],
        [
          1190,
          1191
        ],
        [
          1203,
          1205
        ],
        [
          1210,
          1211
        ],
        [
          1221,
          1223
        ],
        [
          1231,
          1233
        ],
        [
          1238,
          1239
        ],
        [
          1251,
          1252
        ],
        [
          1262,
          1264
        ],
        [
          1268,
          1279
        ],
        [
          1291,
          1301
        ],
        [
          1314,
          1315
        ],
        [
          1327,
          1329
        ],
        [
          1339,
          1341
        ],
        [
          1364,
          1366
        ],
        [
          1377,
          1388
        ],
        [
          1398,
          1399
        ],
        [
          1412,
          1413
        ],
        [
          1425,
          1427
        ],
        [
          1437,
          1439
        ],
        [
          1447,
          1449
        ],
        [
          1459,
          1461
        ],
        [
          1465,
          1467
        ],
        [
          1484,
          1485
        ],
        [
          1494,
          1504
        ],
        [
          1515,
          1516
        ],
        [
          1525,
          1527
        ],
        [
          1537,
          1539
        ],
        [
          1549,
          1551
        ]
      ],
      "directional_missing": {
        "above": 16317,
        "below": 0
      },
      "groups": [
        {
          "box": [
            834,
            2135,
            976,
            2161
          ],
          "body_count": 13,
          "width_xh": 11.84854497248759,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            986,
            2137,
            1161,
            2163
          ],
          "body_count": 14,
          "width_xh": 14.602080071727663,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1171,
            2145,
            1268,
            2163
          ],
          "body_count": 10,
          "width_xh": 8.093724382614763,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1279,
            2146,
            1291,
            2164
          ],
          "body_count": 1,
          "width_xh": 1.001285490632754,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1301,
            2146,
            1560,
            2165
          ],
          "body_count": 19,
          "width_xh": 21.611078506156943,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00131",
      "column_id": "single:column-0001",
      "xheight": 11.910546659548345,
      "profile_runs": [
        [
          836,
          857
        ],
        [
          858,
          868
        ],
        [
          870,
          880
        ],
        [
          881,
          891
        ],
        [
          893,
          898
        ],
        [
          899,
          911
        ],
        [
          912,
          922
        ],
        [
          924,
          934
        ],
        [
          936,
          945
        ],
        [
          959,
          969
        ],
        [
          971,
          983
        ],
        [
          984,
          995
        ],
        [
          997,
          1019
        ],
        [
          1020,
          1033
        ],
        [
          1034,
          1039
        ],
        [
          1040,
          1051
        ],
        [
          1052,
          1061
        ],
        [
          1063,
          1071
        ],
        [
          1072,
          1082
        ],
        [
          1095,
          1105
        ],
        [
          1106,
          1118
        ],
        [
          1120,
          1129
        ],
        [
          1142,
          1150
        ],
        [
          1152,
          1162
        ],
        [
          1163,
          1175
        ],
        [
          1177,
          1182
        ],
        [
          1183,
          1193
        ],
        [
          1195,
          1203
        ],
        [
          1205,
          1210
        ],
        [
          1211,
          1223
        ],
        [
          1225,
          1234
        ],
        [
          1236,
          1240
        ],
        [
          1254,
          1266
        ],
        [
          1280,
          1292
        ],
        [
          1293,
          1305
        ],
        [
          1306,
          1316
        ],
        [
          1317,
          1329
        ],
        [
          1331,
          1341
        ],
        [
          1343,
          1354
        ],
        [
          1356,
          1364
        ],
        [
          1366,
          1375
        ],
        [
          1377,
          1389
        ],
        [
          1403,
          1415
        ],
        [
          1417,
          1426
        ],
        [
          1428,
          1438
        ],
        [
          1440,
          1453
        ],
        [
          1454,
          1463
        ],
        [
          1465,
          1477
        ],
        [
          1479,
          1492
        ],
        [
          1493,
          1506
        ],
        [
          1507,
          1520
        ],
        [
          1521,
          1530
        ],
        [
          1532,
          1549
        ],
        [
          1550,
          1560
        ]
      ],
      "profile_gaps": [
        [
          857,
          858
        ],
        [
          868,
          870
        ],
        [
          880,
          881
        ],
        [
          891,
          893
        ],
        [
          898,
          899
        ],
        [
          911,
          912
        ],
        [
          922,
          924
        ],
        [
          934,
          936
        ],
        [
          945,
          959
        ],
        [
          969,
          971
        ],
        [
          983,
          984
        ],
        [
          995,
          997
        ],
        [
          1019,
          1020
        ],
        [
          1033,
          1034
        ],
        [
          1039,
          1040
        ],
        [
          1051,
          1052
        ],
        [
          1061,
          1063
        ],
        [
          1071,
          1072
        ],
        [
          1082,
          1095
        ],
        [
          1105,
          1106
        ],
        [
          1118,
          1120
        ],
        [
          1129,
          1142
        ],
        [
          1150,
          1152
        ],
        [
          1162,
          1163
        ],
        [
          1175,
          1177
        ],
        [
          1182,
          1183
        ],
        [
          1193,
          1195
        ],
        [
          1203,
          1205
        ],
        [
          1210,
          1211
        ],
        [
          1223,
          1225
        ],
        [
          1234,
          1236
        ],
        [
          1240,
          1254
        ],
        [
          1266,
          1280
        ],
        [
          1292,
          1293
        ],
        [
          1305,
          1306
        ],
        [
          1316,
          1317
        ],
        [
          1329,
          1331
        ],
        [
          1341,
          1343
        ],
        [
          1354,
          1356
        ],
        [
          1364,
          1366
        ],
        [
          1375,
          1377
        ],
        [
          1389,
          1403
        ],
        [
          1415,
          1417
        ],
        [
          1426,
          1428
        ],
        [
          1438,
          1440
        ],
        [
          1453,
          1454
        ],
        [
          1463,
          1465
        ],
        [
          1477,
          1479
        ],
        [
          1492,
          1493
        ],
        [
          1506,
          1507
        ],
        [
          1520,
          1521
        ],
        [
          1530,
          1532
        ],
        [
          1549,
          1550
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 20082
      },
      "groups": [
        {
          "box": [
            959,
            2192,
            1082,
            2219
          ],
          "body_count": 11,
          "width_xh": 10.326981919120767,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      830,
      2156,
      1561,
      2198
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00130"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0001",
        "row_ids": [
          "row-00130"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00129",
      "column_id": "single:column-0001",
      "xheight": 11.984593916782615,
      "assigned_pixels": 659,
      "supported": null,
      "runs": [
        {
          "x0": 1089,
          "x1": 1106,
          "body_cut_fraction": 0.9740055758432468,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1138,
          "x1": 1149,
          "body_cut_fraction": 0.9781536827732643,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1151,
          "x1": 1161,
          "body_cut_fraction": 0.9539496190976883,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1171,
          "x1": 1178,
          "body_cut_fraction": 0.9335216707194991,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1180,
          "x1": 1190,
          "body_cut_fraction": 0.9080562393091058,
          "body_pixels": 4,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1191,
          "x1": 1203,
          "body_cut_fraction": 0.8808207652780966,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1205,
          "x1": 1210,
          "body_cut_fraction": 0.8685668513450412,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1211,
          "x1": 1221,
          "body_cut_fraction": 0.8638013467170629,
          "body_pixels": 9,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1223,
          "x1": 1231,
          "body_cut_fraction": 0.8573276176768141,
          "body_pixels": 6,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1233,
          "x1": 1238,
          "body_cut_fraction": 0.8551808153797322,
          "body_pixels": 4,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1239,
          "x1": 1251,
          "body_cut_fraction": 0.8613019413695268,
          "body_pixels": 10,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1252,
          "x1": 1262,
          "body_cut_fraction": 0.8657276838609611,
          "body_pixels": 11,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1264,
          "x1": 1268,
          "body_cut_fraction": 0.8683299261546188,
          "body_pixels": 5,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1279,
          "x1": 1291,
          "body_cut_fraction": 0.866245758469153,
          "body_pixels": 6,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1301,
          "x1": 1314,
          "body_cut_fraction": 0.8333044499643771,
          "body_pixels": 11,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1315,
          "x1": 1327,
          "body_cut_fraction": 0.8349441655425596,
          "body_pixels": 16,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1329,
          "x1": 1339,
          "body_cut_fraction": 0.8289152002136037,
          "body_pixels": 16,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1341,
          "x1": 1363,
          "body_cut_fraction": 0.8119318074071272,
          "body_pixels": 24,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1366,
          "x1": 1373,
          "body_cut_fraction": 0.801554379440235,
          "body_pixels": 6,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1374,
          "x1": 1377,
          "body_cut_fraction": 0.7980418880204719,
          "body_pixels": 6,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1388,
          "x1": 1398,
          "body_cut_fraction": 0.7858918945980695,
          "body_pixels": 14,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1399,
          "x1": 1412,
          "body_cut_fraction": 0.7809856352456416,
          "body_pixels": 16,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1413,
          "x1": 1425,
          "body_cut_fraction": 0.7736375140802974,
          "body_pixels": 13,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1427,
          "x1": 1437,
          "body_cut_fraction": 0.7628897807965394,
          "body_pixels": 21,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1439,
          "x1": 1447,
          "body_cut_fraction": 0.7603546284224263,
          "body_pixels": 14,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1449,
          "x1": 1459,
          "body_cut_fraction": 0.7597667005991046,
          "body_pixels": 19,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1461,
          "x1": 1465,
          "body_cut_fraction": 0.7558146811573005,
          "body_pixels": 10,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1467,
          "x1": 1484,
          "body_cut_fraction": 0.7508994438908994,
          "body_pixels": 34,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1485,
          "x1": 1494,
          "body_cut_fraction": 0.7513025903469246,
          "body_pixels": 9,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1504,
          "x1": 1515,
          "body_cut_fraction": 0.7235682318137002,
          "body_pixels": 20,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1516,
          "x1": 1525,
          "body_cut_fraction": 0.7115771516516927,
          "body_pixels": 14,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1527,
          "x1": 1537,
          "body_cut_fraction": 0.7033501606241364,
          "body_pixels": 20,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1539,
          "x1": 1549,
          "body_cut_fraction": 0.7185174059610818,
          "body_pixels": 21,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1551,
          "x1": 1560,
          "body_cut_fraction": 0.7921808219686064,
          "body_pixels": 23,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00130",
      "column_id": "single:column-0001",
      "xheight": 11.988621958604199,
      "assigned_pixels": 3843,
      "supported": null,
      "runs": [
        {
          "x0": 836,
          "x1": 846,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 848,
          "x1": 860,
          "body_cut_fraction": 0.0,
          "body_pixels": 87,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 861,
          "x1": 871,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 872,
          "x1": 883,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 884,
          "x1": 896,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 898,
          "x1": 908,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 910,
          "x1": 920,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 922,
          "x1": 931,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 940,
          "x1": 952,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 954,
          "x1": 965,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 967,
          "x1": 974,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 976,
          "x1": 987,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 989,
          "x1": 998,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1000,
          "x1": 1010,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1012,
          "x1": 1032,
          "body_cut_fraction": 0.0,
          "body_pixels": 124,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1034,
          "x1": 1039,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1040,
          "x1": 1052,
          "body_cut_fraction": 0.0,
          "body_pixels": 73,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1054,
          "x1": 1070,
          "body_cut_fraction": 0.0,
          "body_pixels": 98,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1071,
          "x1": 1081,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1091,
          "x1": 1101,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1102,
          "x1": 1115,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1117,
          "x1": 1127,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1129,
          "x1": 1140,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1141,
          "x1": 1151,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1152,
          "x1": 1165,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1167,
          "x1": 1171,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1173,
          "x1": 1182,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1184,
          "x1": 1194,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1195,
          "x1": 1200,
          "body_cut_fraction": 0.0,
          "body_pixels": 36,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1201,
          "x1": 1212,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1213,
          "x1": 1222,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1232,
          "x1": 1245,
          "body_cut_fraction": 0.0,
          "body_pixels": 92,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1247,
          "x1": 1257,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1259,
          "x1": 1268,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1279,
          "x1": 1288,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1291,
          "x1": 1303,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1313,
          "x1": 1323,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1325,
          "x1": 1334,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1335,
          "x1": 1345,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1347,
          "x1": 1357,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1359,
          "x1": 1367,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1369,
          "x1": 1379,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1380,
          "x1": 1389,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1391,
          "x1": 1400,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1402,
          "x1": 1414,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1416,
          "x1": 1421,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1431,
          "x1": 1444,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1445,
          "x1": 1453,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1463,
          "x1": 1472,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1474,
          "x1": 1484,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1486,
          "x1": 1496,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1497,
          "x1": 1507,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1516,
          "x1": 1529,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1530,
          "x1": 1541,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1543,
          "x1": 1550,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1552,
          "x1": 1559,
          "body_cut_fraction": 0.0,
          "body_pixels": 20,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00131",
      "column_id": "single:column-0001",
      "xheight": 11.910546659548345,
      "assigned_pixels": 57,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 130,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          3
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.745219654007314,
        "required_common_rows": 2.396918783356523,
        "xheight_px": 11.984593916782615,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          836,
          2133.442,
          1560,
          2169.175
        ],
        "boundary_path": [
          [
            820.5,
            0.0
          ],
          [
            820.5,
            2339.0
          ]
        ],
        "row_id": "row-00129"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          137
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.749082258653072,
        "required_common_rows": 2.39772439172084,
        "xheight_px": 11.988621958604199,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          836,
          2161.616,
          1559,
          2195.468
        ],
        "boundary_path": [
          [
            820.5,
            0.0
          ],
          [
            820.5,
            2339.0
          ]
        ],
        "row_id": "row-00130"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.67444486917113,
        "required_common_rows": 2.382109331909669,
        "xheight_px": 11.910546659548345,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          836,
          2189.921,
          1560,
          2223.353
        ],
        "boundary_path": [
          [
            820.5,
            0.0
          ],
          [
            820.5,
            2339.0
          ]
        ],
        "row_id": "row-00131"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.745219654007314,
        "required_common_rows": 2.396918783356523,
        "xheight_px": 11.984593916782615,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          836,
          2133.442,
          1560,
          2169.175
        ],
        "boundary_path": [
          [
            821.0,
            1323.0
          ],
          [
            821.0,
            1550.0
          ]
        ],
        "row_id": "row-00129"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.749082258653072,
        "required_common_rows": 2.39772439172084,
        "xheight_px": 11.988621958604199,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          836,
          2161.616,
          1559,
          2195.468
        ],
        "boundary_path": [
          [
            821.0,
            1323.0
          ],
          [
            821.0,
            1550.0
          ]
        ],
        "row_id": "row-00130"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.67444486917113,
        "required_common_rows": 2.382109331909669,
        "xheight_px": 11.910546659548345,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          836,
          2189.921,
          1560,
          2223.353
        ],
        "boundary_path": [
          [
            821.0,
            1323.0
          ],
          [
            821.0,
            1550.0
          ]
        ],
        "row_id": "row-00131"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            820.5,
            0.0
          ],
          [
            820.5,
            2339.0
          ]
        ],
        "width": 31,
        "extent": [
          805,
          0,
          836,
          2339
        ],
        "source": "detector",
        "proposal_id": "proposal-0000",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 31.0,
          "local_xheight_max_px": 18.967830858370917,
          "width_xh": 1.634346079500125,
          "required_width_px": 28.451746287556375,
          "spacing_sides": [
            {
              "samples": 470,
              "letter_q25_xh": 0.08477106828819082,
              "median_xh": 0.16666666666666666,
              "word_q75_xh": 0.24565893968883798,
              "q90_xh": 0.6005458886690196
            },
            {
              "samples": 573,
              "letter_q25_xh": 0.08372392441102328,
              "median_xh": 0.16666666666666666,
              "word_q75_xh": 0.2505486372842758,
              "q90_xh": 0.7525783931313436
            }
          ],
          "side_row_counts": [
            47,
            65
          ],
          "side_span_xh": [
            113.15579604363575,
            113.33138280549949
          ],
          "shared_span_xh": 112.99515564027325,
          "occupied_rows": 90,
          "bilateral_rows": 59,
          "participants": [
            {
              "line_index": 0,
              "xheight": 14.068895786753558
            },
            {
              "line_index": 1,
              "xheight": 11.969158907288318
            },
            {
              "line_index": 2,
              "xheight": 15.845037669075822
            },
            {
              "line_index": 3,
              "xheight": 12.643217341206594
            },
            {
              "line_index": 4,
              "xheight": 12.010005104787666
            },
            {
              "line_index": 5,
              "xheight": 12.007228057131641
            },
            {
              "line_index": 6,
              "xheight": 11.989198254500195
            },
            {
              "line_index": 9,
              "xheight": 12.212053034992039
            },
            {
              "line_index": 10,
              "xheight": 12.025252448968388
            },
            {
              "line_index": 11,
              "xheight": 12.0
            },
            {
              "line_index": 13,
              "xheight": 12.018511005000732
            },
            {
              "line_index": 18,
              "xheight": 13.0
            },
            {
              "line_index": 19,
              "xheight": 11.974584284316734
            },
            {
              "line_index": 20,
              "xheight": 15.326275377779098
            },
            {
              "line_index": 22,
              "xheight": 15.789367322030273
            },
            {
              "line_index": 23,
              "xheight": 11.904192907455808
            },
            {
              "line_index": 24,
              "xheight": 11.796258122703648
            },
            {
              "line_index": 25,
              "xheight": 11.712535504130983
            },
            {
              "line_index": 26,
              "xheight": 11.665677551844965
            },
            {
              "line_index": 27,
              "xheight": 12.03766324246999
            },
            {
              "line_index": 28,
              "xheight": 11.494017270539189
            },
            {
              "line_index": 29,
              "xheight": 11.898269287376934
            },
            {
              "line_index": 30,
              "xheight": 11.725929181966194
            },
            {
              "line_index": 31,
              "xheight": 11.956209618435878
            },
            {
              "line_index": 32,
              "xheight": 11.79655063209907
            },
            {
              "line_index": 34,
              "xheight": 11.728992622367286
            },
            {
              "line_index": 35,
              "xheight": 11.401313028036611
            },
            {
              "line_index": 37,
              "xheight": 11.652314613116005
            },
            {
              "line_index": 38,
              "xheight": 11.84595652535154
            },
            {
              "line_index": 39,
              "xheight": 11.834834437811878
            },
            {
              "line_index": 40,
              "xheight": 11.951113705538091
            },
            {
              "line_index": 41,
              "xheight": 11.961566514336027
            },
            {
              "line_index": 42,
              "xheight": 11.96321538813072
            },
            {
              "line_index": 43,
              "xheight": 12.005521057051965
            },
            {
              "line_index": 44,
              "xheight": 11.983966957463736
            },
            {
              "line_index": 46,
              "xheight": 12.014701437103213
            },
            {
              "line_index": 47,
              "xheight": 11.976918671341764
            },
            {
              "line_index": 48,
              "xheight": 12.043680765397312
            },
            {
              "line_index": 49,
              "xheight": 12.0
            },
            {
              "line_index": 55,
              "xheight": 13.004730813935907
            },
            {
              "line_index": 56,
              "xheight": 18.967830858370917
            },
            {
              "line_index": 57,
              "xheight": 14.525100199519102
            },
            {
              "line_index": 58,
              "xheight": 12.125745791431655
            },
            {
              "line_index": 59,
              "xheight": 12.016435536530025
            },
            {
              "line_index": 60,
              "xheight": 12.026920167847493
            },
            {
              "line_index": 61,
              "xheight": 12.06412186891339
            },
            {
              "line_index": 62,
              "xheight": 12.037510818434384
            },
            {
              "line_index": 63,
              "xheight": 12.126580176609878
            },
            {
              "line_index": 64,
              "xheight": 14.039019640600529
            },
            {
              "line_index": 65,
              "xheight": 12.718485819763345
            },
            {
              "line_index": 66,
              "xheight": 12.0
            },
            {
              "line_index": 67,
              "xheight": 11.922545984399477
            },
            {
              "line_index": 68,
              "xheight": 11.994698836708835
            },
            {
              "line_index": 69,
              "xheight": 11.977136550429407
            },
            {
              "line_index": 70,
              "xheight": 12.057742818651263
            },
            {
              "line_index": 71,
              "xheight": 12.007961621922448
            },
            {
              "line_index": 72,
              "xheight": 12.030737461469869
            },
            {
              "line_index": 73,
              "xheight": 11.958887050361113
            },
            {
              "line_index": 74,
              "xheight": 12.03900565209915
            },
            {
              "line_index": 75,
              "xheight": 12.0
            },
            {
              "line_index": 76,
              "xheight": 12.006334700830962
            },
            {
              "line_index": 77,
              "xheight": 11.941778292950573
            },
            {
              "line_index": 78,
              "xheight": 12.0
            },
            {
              "line_index": 79,
              "xheight": 12.062260155561603
            },
            {
              "line_index": 80,
              "xheight": 11.973723076354872
            },
            {
              "line_index": 81,
              "xheight": 12.087069750869091
            },
            {
              "line_index": 82,
              "xheight": 11.968471554110124
            },
            {
              "line_index": 83,
              "xheight": 11.993543361537036
            },
            {
              "line_index": 84,
              "xheight": 11.908335083836391
            },
            {
              "line_index": 85,
              "xheight": 11.90885975393644
            },
            {
              "line_index": 90,
              "xheight": 16.149999999999977
            },
            {
              "line_index": 91,
              "xheight": 12.59961759367252
            },
            {
              "line_index": 92,
              "xheight": 12.680974609078248
            },
            {
              "line_index": 93,
              "xheight": 11.791725239567313
            },
            {
              "line_index": 94,
              "xheight": 11.789552832153731
            },
            {
              "line_index": 95,
              "xheight": 11.495027192119778
            },
            {
              "line_index": 96,
              "xheight": 11.575280918086719
            },
            {
              "line_index": 97,
              "xheight": 17.15407706725523
            },
            {
              "line_index": 98,
              "xheight": 18.533797797634406
            },
            {
              "line_index": 99,
              "xheight": 12.729487224552486
            },
            {
              "line_index": 100,
              "xheight": 12.615336074169136
            },
            {
              "line_index": 101,
              "xheight": 11.954134826730979
            },
            {
              "line_index": 102,
              "xheight": 11.490397182492188
            },
            {
              "line_index": 103,
              "xheight": 11.77258006402758
            },
            {
              "line_index": 104,
              "xheight": 11.889655895297437
            },
            {
              "line_index": 105,
              "xheight": 11.930024125106229
            },
            {
              "line_index": 106,
              "xheight": 11.98011293371269
            },
            {
              "line_index": 107,
              "xheight": 11.937724541580792
            },
            {
              "line_index": 108,
              "xheight": 11.901892386113104
            },
            {
              "line_index": 109,
              "xheight": 17.70431498790481
            },
            {
              "line_index": 110,
              "xheight": 12.591802178043054
            },
            {
              "line_index": 111,
              "xheight": 11.978038245505104
            },
            {
              "line_index": 112,
              "xheight": 11.981594125275478
            },
            {
              "line_index": 113,
              "xheight": 11.994207899765115
            },
            {
              "line_index": 114,
              "xheight": 11.996322070450788
            },
            {
              "line_index": 115,
              "xheight": 11.99483311239419
            },
            {
              "line_index": 116,
              "xheight": 12.066437183723338
            },
            {
              "line_index": 117,
              "xheight": 11.972725667151053
            },
            {
              "line_index": 118,
              "xheight": 12.011950631643913
            },
            {
              "line_index": 119,
              "xheight": 11.934553353547471
            },
            {
              "line_index": 120,
              "xheight": 12.245515971065288
            },
            {
              "line_index": 121,
              "xheight": 11.881103668430796
            },
            {
              "line_index": 122,
              "xheight": 11.999092343761276
            },
            {
              "line_index": 123,
              "xheight": 11.944017281019114
            },
            {
              "line_index": 124,
              "xheight": 11.998236781312471
            },
            {
              "line_index": 125,
              "xheight": 12.005368232186811
            },
            {
              "line_index": 126,
              "xheight": 12.0
            },
            {
              "line_index": 127,
              "xheight": 11.964249256325274
            },
            {
              "line_index": 128,
              "xheight": 12.077528400163828
            },
            {
              "line_index": 129,
              "xheight": 11.984593916782615
            },
            {
              "line_index": 130,
              "xheight": 11.988621958604199
            },
            {
              "line_index": 131,
              "xheight": 11.910546659548345
            },
            {
              "line_index": 132,
              "xheight": 12.006329087314043
            }
          ],
          "observed_gap_widths_px": [
            37,
            42,
            38,
            38,
            37,
            55,
            37,
            0.0,
            0.0,
            0.0,
            37,
            65,
            36,
            0.0,
            37,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            35,
            70,
            73,
            0.0,
            64,
            64,
            35,
            35,
            35,
            35,
            35,
            35,
            0.0,
            35,
            35,
            35,
            35,
            0.0,
            35,
            64,
            64,
            66,
            66,
            93,
            93,
            35,
            35,
            35,
            35,
            36,
            36,
            36,
            0.0,
            35,
            35,
            64,
            64,
            35,
            35,
            36,
            36,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            36,
            36,
            36,
            36,
            0.0,
            0.0,
            36,
            64,
            36,
            37,
            36,
            37,
            37
          ],
          "white_rows": 59,
          "baseline_matching_reach_px": 14.061749999999961,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            821.0,
            1323.0
          ],
          [
            821.0,
            1550.0
          ]
        ],
        "width": 32,
        "extent": [
          805,
          1323,
          837,
          1550
        ],
        "source": "detector",
        "proposal_id": "proposal-0004",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 12.005521057051965,
          "width_xh": 2.6654403293227666,
          "required_width_px": 18.008281585577947,
          "spacing_sides": [
            {
              "samples": 72,
              "letter_q25_xh": 0.08441699054524633,
              "median_xh": 0.16717913496603062,
              "word_q75_xh": 0.19120104658908257,
              "q90_xh": 0.7447024223124585
            },
            {
              "samples": 69,
              "letter_q25_xh": 0.08402025220516869,
              "median_xh": 0.16753611570058563,
              "word_q75_xh": 0.26108758055562015,
              "q90_xh": 0.8377887172503352
            }
          ],
          "side_row_counts": [
            8,
            8
          ],
          "side_span_xh": [
            16.735883352766194,
            16.80206123844268
          ],
          "shared_span_xh": 16.263100874352578,
          "occupied_rows": 14,
          "bilateral_rows": 14,
          "participants": [
            {
              "line_index": 37,
              "xheight": 11.652314613116005
            },
            {
              "line_index": 38,
              "xheight": 11.84595652535154
            },
            {
              "line_index": 39,
              "xheight": 11.834834437811878
            },
            {
              "line_index": 40,
              "xheight": 11.951113705538091
            },
            {
              "line_index": 41,
              "xheight": 11.961566514336027
            },
            {
              "line_index": 42,
              "xheight": 11.96321538813072
            },
            {
              "line_index": 43,
              "xheight": 12.005521057051965
            },
            {
              "line_index": 44,
              "xheight": 11.983966957463736
            },
            {
              "line_index": 101,
              "xheight": 11.954134826730979
            },
            {
              "line_index": 102,
              "xheight": 11.490397182492188
            },
            {
              "line_index": 103,
              "xheight": 11.77258006402758
            },
            {
              "line_index": 104,
              "xheight": 11.889655895297437
            },
            {
              "line_index": 105,
              "xheight": 11.930024125106229
            },
            {
              "line_index": 106,
              "xheight": 11.98011293371269
            },
            {
              "line_index": 107,
              "xheight": 11.937724541580792
            },
            {
              "line_index": 108,
              "xheight": 11.901892386113104
            }
          ],
          "observed_gap_widths_px": [
            35,
            64,
            64,
            66,
            66,
            93,
            93,
            35,
            35,
            35,
            35,
            36,
            36,
            36
          ],
          "white_rows": 14,
          "baseline_matching_reach_px": 14.109500000000025,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "a4006ca6d78db505b4bff4d32c421953ba78c67c17dec08a3779b0d986c70ee1"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.8891717689926492,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--7e2146762fbf8ed6--s000-l0092

Card `kf5efbfe800`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/9b1b452bb3190811593d124b305b7f9e545f8e6534fd0b1219df0d3c5d819ade.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/9b1b452bb3190811593d124b305b7f9e545f8e6534fd0b1219df0d3c5d819ade.png`; SHA-256 `9b1b452bb3190811593d124b305b7f9e545f8e6534fd0b1219df0d3c5d819ade`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kf5efbfe800",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "The neighbouring words are cut through their letter bodies; none is complete.",
  "multi_line": "no",
  "multi_line_reason": "Only the main line is complete.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--7e2146762fbf8ed6--s000-l0092"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00111",
  "neighbour_rows": [
    {
      "row_id": "row-00110",
      "column_id": "single:column-0000",
      "xheight": 11.979265917446583,
      "profile_runs": [
        [
          854,
          864
        ],
        [
          866,
          875
        ],
        [
          877,
          893
        ],
        [
          894,
          912
        ],
        [
          913,
          916
        ],
        [
          918,
          929
        ],
        [
          930,
          952
        ],
        [
          962,
          975
        ],
        [
          976,
          984
        ],
        [
          994,
          1015
        ],
        [
          1025,
          1037
        ],
        [
          1038,
          1050
        ],
        [
          1052,
          1061
        ],
        [
          1063,
          1073
        ],
        [
          1074,
          1083
        ],
        [
          1094,
          1110
        ],
        [
          1111,
          1133
        ],
        [
          1135,
          1147
        ],
        [
          1148,
          1168
        ],
        [
          1170,
          1182
        ],
        [
          1183,
          1192
        ],
        [
          1194,
          1199
        ],
        [
          1200,
          1211
        ],
        [
          1213,
          1223
        ],
        [
          1233,
          1243
        ],
        [
          1245,
          1250
        ],
        [
          1259,
          1267
        ],
        [
          1268,
          1278
        ],
        [
          1279,
          1291
        ],
        [
          1293,
          1298
        ],
        [
          1299,
          1308
        ],
        [
          1310,
          1320
        ],
        [
          1322,
          1327
        ],
        [
          1337,
          1344
        ],
        [
          1346,
          1350
        ],
        [
          1352,
          1364
        ],
        [
          1365,
          1378
        ],
        [
          1379,
          1397
        ],
        [
          1398,
          1401
        ],
        [
          1403,
          1413
        ],
        [
          1424,
          1437
        ],
        [
          1439,
          1451
        ],
        [
          1452,
          1462
        ],
        [
          1464,
          1481
        ],
        [
          1482,
          1490
        ],
        [
          1492,
          1497
        ],
        [
          1498,
          1508
        ],
        [
          1509,
          1519
        ],
        [
          1529,
          1540
        ],
        [
          1541,
          1554
        ],
        [
          1555,
          1560
        ]
      ],
      "profile_gaps": [
        [
          864,
          866
        ],
        [
          875,
          877
        ],
        [
          893,
          894
        ],
        [
          912,
          913
        ],
        [
          916,
          918
        ],
        [
          929,
          930
        ],
        [
          952,
          962
        ],
        [
          975,
          976
        ],
        [
          984,
          994
        ],
        [
          1015,
          1025
        ],
        [
          1037,
          1038
        ],
        [
          1050,
          1052
        ],
        [
          1061,
          1063
        ],
        [
          1073,
          1074
        ],
        [
          1083,
          1094
        ],
        [
          1110,
          1111
        ],
        [
          1133,
          1135
        ],
        [
          1147,
          1148
        ],
        [
          1168,
          1170
        ],
        [
          1182,
          1183
        ],
        [
          1192,
          1194
        ],
        [
          1199,
          1200
        ],
        [
          1211,
          1213
        ],
        [
          1223,
          1233
        ],
        [
          1243,
          1245
        ],
        [
          1250,
          1259
        ],
        [
          1267,
          1268
        ],
        [
          1278,
          1279
        ],
        [
          1291,
          1293
        ],
        [
          1298,
          1299
        ],
        [
          1308,
          1310
        ],
        [
          1320,
          1322
        ],
        [
          1327,
          1337
        ],
        [
          1344,
          1346
        ],
        [
          1350,
          1352
        ],
        [
          1364,
          1365
        ],
        [
          1378,
          1379
        ],
        [
          1397,
          1398
        ],
        [
          1401,
          1403
        ],
        [
          1413,
          1424
        ],
        [
          1437,
          1439
        ],
        [
          1451,
          1452
        ],
        [
          1462,
          1464
        ],
        [
          1481,
          1482
        ],
        [
          1490,
          1492
        ],
        [
          1497,
          1498
        ],
        [
          1508,
          1509
        ],
        [
          1519,
          1529
        ],
        [
          1540,
          1541
        ],
        [
          1554,
          1555
        ]
      ],
      "directional_missing": {
        "above": 15356,
        "below": 0
      },
      "groups": [
        {
          "box": [
            854,
            1379,
            952,
            1399
          ],
          "body_count": 8,
          "width_xh": 8.180801784963549,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            962,
            1378,
            984,
            1397
          ],
          "body_count": 2,
          "width_xh": 1.8365065231550823,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            994,
            1377,
            1083,
            1396
          ],
          "body_count": 7,
          "width_xh": 7.429503661854651,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1094,
            1370,
            1223,
            1389
          ],
          "body_count": 11,
          "width_xh": 10.768606431227528,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1233,
            1375,
            1250,
            1387
          ],
          "body_count": 2,
          "width_xh": 1.4191186769834727,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1259,
            1374,
            1327,
            1393
          ],
          "body_count": 7,
          "width_xh": 5.676474707933891,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1337,
            1366,
            1519,
            1392
          ],
          "body_count": 13,
          "width_xh": 15.19291760064659,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      848,
      1386,
      1558,
      1429
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00111"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00111"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00110",
      "column_id": "single:column-0000",
      "xheight": 11.979265917446583,
      "assigned_pixels": 786,
      "supported": null,
      "runs": [
        {
          "x0": 854,
          "x1": 864,
          "body_cut_fraction": 0.49436523307065716,
          "body_pixels": 34,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 866,
          "x1": 875,
          "body_cut_fraction": 0.48521950450325046,
          "body_pixels": 38,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 877,
          "x1": 893,
          "body_cut_fraction": 0.4942139532942389,
          "body_pixels": 49,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 894,
          "x1": 912,
          "body_cut_fraction": 0.515058341217282,
          "body_pixels": 35,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 913,
          "x1": 916,
          "body_cut_fraction": 0.5323743008987387,
          "body_pixels": 13,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 918,
          "x1": 929,
          "body_cut_fraction": 0.5465659861880572,
          "body_pixels": 36,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 930,
          "x1": 952,
          "body_cut_fraction": 0.5803850590413747,
          "body_pixels": 61,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 962,
          "x1": 975,
          "body_cut_fraction": 0.6268461202578779,
          "body_pixels": 48,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 976,
          "x1": 984,
          "body_cut_fraction": 0.6442322742213186,
          "body_pixels": 24,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 994,
          "x1": 1015,
          "body_cut_fraction": 0.6601009699475272,
          "body_pixels": 44,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1025,
          "x1": 1037,
          "body_cut_fraction": 0.667684602274702,
          "body_pixels": 27,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1038,
          "x1": 1050,
          "body_cut_fraction": 0.674599309922643,
          "body_pixels": 27,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1052,
          "x1": 1061,
          "body_cut_fraction": 0.6931788669164829,
          "body_pixels": 28,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1063,
          "x1": 1073,
          "body_cut_fraction": 0.7169200203684696,
          "body_pixels": 18,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1074,
          "x1": 1083,
          "body_cut_fraction": 0.7331119623793056,
          "body_pixels": 11,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1094,
          "x1": 1110,
          "body_cut_fraction": 0.7455861176617904,
          "body_pixels": 32,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1111,
          "x1": 1133,
          "body_cut_fraction": 0.7562465613083147,
          "body_pixels": 35,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1135,
          "x1": 1147,
          "body_cut_fraction": 0.7870707885803342,
          "body_pixels": 20,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1148,
          "x1": 1168,
          "body_cut_fraction": 0.8183658477540422,
          "body_pixels": 22,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1170,
          "x1": 1182,
          "body_cut_fraction": 0.8437169569814676,
          "body_pixels": 15,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1183,
          "x1": 1192,
          "body_cut_fraction": 0.8441546395577476,
          "body_pixels": 8,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1194,
          "x1": 1199,
          "body_cut_fraction": 0.8406571390410027,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1200,
          "x1": 1211,
          "body_cut_fraction": 0.8443955376792884,
          "body_pixels": 8,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1213,
          "x1": 1223,
          "body_cut_fraction": 0.8616112794570682,
          "body_pixels": 7,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1233,
          "x1": 1243,
          "body_cut_fraction": 0.8914451716308305,
          "body_pixels": 6,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1245,
          "x1": 1250,
          "body_cut_fraction": 0.9074259574610161,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1259,
          "x1": 1267,
          "body_cut_fraction": 0.927873779113448,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1268,
          "x1": 1278,
          "body_cut_fraction": 0.929471179932384,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1279,
          "x1": 1291,
          "body_cut_fraction": 0.9338151917578549,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1293,
          "x1": 1298,
          "body_cut_fraction": 0.9456901013406359,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1299,
          "x1": 1308,
          "body_cut_fraction": 0.9574541103577471,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1310,
          "x1": 1320,
          "body_cut_fraction": 0.9709746894617273,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00111",
      "column_id": "single:column-0000",
      "xheight": 12.029461001636491,
      "assigned_pixels": 4154,
      "supported": null,
      "runs": [
        {
          "x0": 855,
          "x1": 861,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 865,
          "x1": 871,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 873,
          "x1": 895,
          "body_cut_fraction": 0.0,
          "body_pixels": 145,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 896,
          "x1": 921,
          "body_cut_fraction": 0.0,
          "body_pixels": 147,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 922,
          "x1": 932,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 934,
          "x1": 943,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 954,
          "x1": 970,
          "body_cut_fraction": 0.0,
          "body_pixels": 97,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 972,
          "x1": 988,
          "body_cut_fraction": 0.0,
          "body_pixels": 111,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 989,
          "x1": 998,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1000,
          "x1": 1010,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1011,
          "x1": 1020,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1022,
          "x1": 1054,
          "body_cut_fraction": 0.0,
          "body_pixels": 205,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1056,
          "x1": 1070,
          "body_cut_fraction": 0.0,
          "body_pixels": 87,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1072,
          "x1": 1082,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1083,
          "x1": 1092,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1103,
          "x1": 1113,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1115,
          "x1": 1120,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1130,
          "x1": 1141,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1142,
          "x1": 1154,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1156,
          "x1": 1166,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1168,
          "x1": 1172,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1173,
          "x1": 1184,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1185,
          "x1": 1190,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1201,
          "x1": 1211,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1213,
          "x1": 1225,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1236,
          "x1": 1244,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1245,
          "x1": 1254,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1255,
          "x1": 1263,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1265,
          "x1": 1274,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1276,
          "x1": 1288,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1289,
          "x1": 1300,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1301,
          "x1": 1311,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1312,
          "x1": 1321,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1332,
          "x1": 1343,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1354,
          "x1": 1365,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1367,
          "x1": 1379,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1380,
          "x1": 1390,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1392,
          "x1": 1400,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1401,
          "x1": 1410,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1411,
          "x1": 1424,
          "body_cut_fraction": 0.0,
          "body_pixels": 96,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1425,
          "x1": 1434,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1445,
          "x1": 1455,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1456,
          "x1": 1464,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1465,
          "x1": 1476,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1479,
          "x1": 1495,
          "body_cut_fraction": 0.0,
          "body_pixels": 94,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1497,
          "x1": 1507,
          "body_cut_fraction": 0.0,
          "body_pixels": 73,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1509,
          "x1": 1514,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1515,
          "x1": 1525,
          "body_cut_fraction": 0.0,
          "body_pixels": 73,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1526,
          "x1": 1536,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1537,
          "x1": 1550,
          "body_cut_fraction": 0.0,
          "body_pixels": 97,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1552,
          "x1": 1555,
          "body_cut_fraction": 0.0,
          "body_pixels": 10,
          "body_extent_px": 4,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 133,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.740112476835892,
        "required_common_rows": 2.3958531834893164,
        "xheight_px": 11.979265917446583,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          854,
          1363.493,
          1558,
          1399.783
        ],
        "boundary_path": [
          [
            845.0,
            1938.0
          ],
          [
            845.0,
            2209.0
          ]
        ],
        "row_id": "row-00110"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.788317279595729,
        "required_common_rows": 2.4058922003272984,
        "xheight_px": 12.029461001636491,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          854,
          1391.451,
          1555,
          1433.408
        ],
        "boundary_path": [
          [
            845.0,
            1938.0
          ],
          [
            845.0,
            2209.0
          ]
        ],
        "row_id": "row-00111"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            845.0,
            1938.0
          ],
          [
            845.0,
            2209.0
          ]
        ],
        "width": 30,
        "extent": [
          830,
          1938,
          860,
          2209
        ],
        "source": "detector",
        "proposal_id": "proposal-0005",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 13.070252660332926,
          "width_xh": 2.2952884523072288,
          "required_width_px": 19.60537899049939,
          "spacing_sides": [
            {
              "samples": 43,
              "letter_q25_xh": 0.08120758531423532,
              "median_xh": 0.15706554922373567,
              "word_q75_xh": 0.16241517062847063,
              "q90_xh": 0.37980464218588184
            },
            {
              "samples": 81,
              "letter_q25_xh": 0.08136982242941487,
              "median_xh": 0.08185140155349035,
              "word_q75_xh": 0.16286106161548689,
              "q90_xh": 0.24186193005308335
            }
          ],
          "side_row_counts": [
            6,
            9
          ],
          "side_span_xh": [
            15.038921213554655,
            17.071934705378254
          ],
          "shared_span_xh": 13.693078829544326,
          "occupied_rows": 13,
          "bilateral_rows": 8,
          "participants": [
            {
              "line_index": 120,
              "xheight": 10.095324390847054
            },
            {
              "line_index": 121,
              "xheight": 13.070252660332926
            },
            {
              "line_index": 122,
              "xheight": 12.733537111636451
            },
            {
              "line_index": 123,
              "xheight": 12.314120609921702
            },
            {
              "line_index": 124,
              "xheight": 12.267629272382237
            },
            {
              "line_index": 125,
              "xheight": 12.35325389638092
            },
            {
              "line_index": 126,
              "xheight": 12.280406256481228
            },
            {
              "line_index": 127,
              "xheight": 12.420234684990874
            },
            {
              "line_index": 128,
              "xheight": 12.289568419145326
            },
            {
              "line_index": 129,
              "xheight": 12.248848758100848
            },
            {
              "line_index": 130,
              "xheight": 12.16346074596322
            },
            {
              "line_index": 131,
              "xheight": 12.422026136582645
            },
            {
              "line_index": 132,
              "xheight": 12.217261781968318
            },
            {
              "line_index": 133,
              "xheight": 12.403771024822163
            },
            {
              "line_index": 134,
              "xheight": 12.478986548859211
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            0.0,
            43,
            43,
            54,
            45,
            0.0,
            0.0,
            46,
            46,
            47,
            47,
            0.0
          ],
          "white_rows": 8,
          "baseline_matching_reach_px": 13.962249999999983,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "08ee8f5f0fd79be345b474f7dc5bb1ab1afef183fec841fa96e1640ed6977c96"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.9027329216595407,
    "polarity_confidence": 0.6,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## lekythos--9447d290d59a2411--s001-l0432

Card `k4516c91d18`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/41d09fdbce95e10876a1575ff24ab5a0d003b64e66085315cac951a4057a93e9.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/41d09fdbce95e10876a1575ff24ab5a0d003b64e66085315cac951a4057a93e9.png`; SHA-256 `41d09fdbce95e10876a1575ff24ab5a0d003b64e66085315cac951a4057a93e9`.

Triggers: {"mismatches": {"union": "FP", "geometry_unavailable": "FP"}, "flag": false, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k4516c91d18",
  "letters": "y",
  "marks": "y",
  "crop_ok": "y",
  "errors": [],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "lekythos--9447d290d59a2411--s001-l0432"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": null,
  "neighbour_words": null,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": true,
  "screen_drop": true,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": true,
    "drop": true,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "unavailable"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "unavailable",
  "structural_reason": "invalid_source_frame_or_labels",
  "target_row_id": null,
  "neighbour_rows": [],
  "row_inclusion": {},
  "row_inclusion_rows": [],
  "omitted_zero_ink_rows": 0,
  "crossing": {
    "status": "unavailable",
    "drop": null,
    "reason": "geometry_unavailable"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "line_block_disagreement",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.7911547268630383,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--d837e6d93bcd94ad--s000-l0073

Card `k9ee04c07b4`; context `segcp7_a`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/66b4383d88b930365f72359cdfa5aa98d8f87332a0455b28b31908c9221331ac.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/66b4383d88b930365f72359cdfa5aa98d8f87332a0455b28b31908c9221331ac.png`; SHA-256 `66b4383d88b930365f72359cdfa5aa98d8f87332a0455b28b31908c9221331ac`.

Triggers: {"mismatches": {"geometry_unavailable": "FN", "crossing": "FN"}, "flag": false, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k9ee04c07b4",
  "letters": "y",
  "marks": "y",
  "crop_ok": "y",
  "errors": [],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "yes",
  "rotated_reason": "The entire text line is rotated approximately 90 degrees counterclockwise.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The complete line stays together without a column crossing.",
  "line_id": "gazette_modern--d837e6d93bcd94ad--s000-l0073"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": true,
  "neighbour_words": true,
  "orientation": true,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": true,
  "composed": {
    "measured_drop": true,
    "geometry_unavailable": false,
    "drop": true,
    "orientation_status": "measured",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00226",
  "neighbour_rows": [
    {
      "row_id": "row-00222",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "profile_runs": [
        [
          674,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 75,
        "below": 0
      },
      "groups": [
        {
          "box": [
            674,
            701,
            684,
            712
          ],
          "body_count": 1,
          "width_xh": 0.9090909090909091,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00223",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "profile_runs": [
        [
          674,
          685
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            674,
            715,
            685,
            727
          ],
          "body_count": 1,
          "width_xh": 0.9166666666666666,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00224",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          674,
          685
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            674,
            729,
            685,
            739
          ],
          "body_count": 1,
          "width_xh": 1.1,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00225",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "profile_runs": [
        [
          673,
          685
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            673,
            742,
            685,
            753
          ],
          "body_count": 1,
          "width_xh": 1.0909090909090908,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00227",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "profile_runs": [
        [
          672,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            672,
            808,
            684,
            819
          ],
          "body_count": 1,
          "width_xh": 1.0909090909090908,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00228",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "profile_runs": [
        [
          673,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            673,
            821,
            684,
            832
          ],
          "body_count": 1,
          "width_xh": 1.0,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00229",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "profile_runs": [
        [
          673,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            673,
            861,
            684,
            872
          ],
          "body_count": 1,
          "width_xh": 1.0,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00230",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          672,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            672,
            875,
            684,
            885
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00231",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          672,
          684
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            672,
            902,
            684,
            912
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00232",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          672,
          683
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            672,
            915,
            683,
            925
          ],
          "body_count": 1,
          "width_xh": 1.1,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00233",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "profile_runs": [
        [
          672,
          683
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 104
      },
      "groups": [
        {
          "box": [
            672,
            941,
            683,
            953
          ],
          "body_count": 1,
          "width_xh": 0.9166666666666666,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      657,
      698,
      691,
      956
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00222",
      "row-00223",
      "row-00224",
      "row-00225",
      "row-00226",
      "row-00227",
      "row-00228",
      "row-00229",
      "row-00230",
      "row-00231",
      "row-00232",
      "row-00233"
    ],
    "supported_row_count": 12,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00222",
          "row-00223",
          "row-00224",
          "row-00225",
          "row-00226",
          "row-00227",
          "row-00228",
          "row-00229",
          "row-00230",
          "row-00231",
          "row-00232",
          "row-00233"
        ],
        "count": 12
      }
    ],
    "merged": true
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00222",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "assigned_pixels": 54,
      "supported": null,
      "runs": [
        {
          "x0": 674,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00223",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "assigned_pixels": 78,
      "supported": null,
      "runs": [
        {
          "x0": 674,
          "x1": 685,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00224",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 60,
      "supported": null,
      "runs": [
        {
          "x0": 674,
          "x1": 685,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00225",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "assigned_pixels": 73,
      "supported": null,
      "runs": [
        {
          "x0": 673,
          "x1": 685,
          "body_cut_fraction": 0.0,
          "body_pixels": 73,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00226",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 72,
      "supported": null,
      "runs": [
        {
          "x0": 673,
          "x1": 685,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00227",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "assigned_pixels": 78,
      "supported": null,
      "runs": [
        {
          "x0": 672,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00228",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "assigned_pixels": 63,
      "supported": null,
      "runs": [
        {
          "x0": 673,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00229",
      "column_id": "single:column-0000",
      "xheight": 11.0,
      "assigned_pixels": 58,
      "supported": null,
      "runs": [
        {
          "x0": 673,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00230",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 70,
      "supported": null,
      "runs": [
        {
          "x0": 672,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00231",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 66,
      "supported": null,
      "runs": [
        {
          "x0": 672,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00232",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 55,
      "supported": null,
      "runs": [
        {
          "x0": 672,
          "x1": 683,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00233",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "assigned_pixels": 62,
      "supported": null,
      "runs": [
        {
          "x0": 672,
          "x1": 683,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 644,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "validated": [],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            1038.8308879258975,
            366
          ],
          [
            1032.0038701004084,
            647
          ]
        ],
        "radius": 2.96,
        "source": "direct_rule",
        "proposal_id": "proposal-0036",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 12.0,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 282,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1038.8633373347368,
            366.0
          ],
          [
            1032.0047935592238,
            647.0
          ]
        ],
        "id": "boundary-0000",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      }
    ],
    "inventory_sha256": "353f8bed293e941a31a38e1629d5e981eeb3e0e5f18a7d5826d9b95ab1d35f39"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "vertical",
    "orientation_cw": null,
    "axis_confidence": 1.0,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--da6dbe3e9a901b78--s000-l0090

Card `ked12eb206b`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/5d8b7489fbbf5d443fbbea5b85b080ec556f354b3a05ec20d9e0f78f0b4e73bb.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/5d8b7489fbbf5d443fbbea5b85b080ec556f354b3a05ec20d9e0f78f0b4e73bb.png`; SHA-256 `5d8b7489fbbf5d443fbbea5b85b080ec556f354b3a05ec20d9e0f78f0b4e73bb`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "ked12eb206b",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Only clipped neighbouring letter portions are visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--da6dbe3e9a901b78--s000-l0090"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00069",
  "neighbour_rows": [
    {
      "row_id": "row-00068",
      "column_id": "single:column-0000",
      "xheight": 12.356088176179128,
      "profile_runs": [
        [
          850,
          854
        ],
        [
          863,
          875
        ],
        [
          878,
          888
        ],
        [
          892,
          900
        ],
        [
          904,
          912
        ],
        [
          915,
          924
        ],
        [
          928,
          932
        ],
        [
          935,
          947
        ],
        [
          964,
          976
        ],
        [
          979,
          983
        ],
        [
          987,
          998
        ],
        [
          1016,
          1027
        ],
        [
          1030,
          1041
        ],
        [
          1058,
          1071
        ],
        [
          1072,
          1080
        ],
        [
          1082,
          1092
        ],
        [
          1094,
          1103
        ],
        [
          1106,
          1117
        ],
        [
          1118,
          1131
        ],
        [
          1134,
          1145
        ],
        [
          1148,
          1157
        ],
        [
          1161,
          1173
        ],
        [
          1189,
          1199
        ],
        [
          1201,
          1213
        ],
        [
          1216,
          1225
        ],
        [
          1229,
          1232
        ]
      ],
      "profile_gaps": [
        [
          854,
          863
        ],
        [
          875,
          878
        ],
        [
          888,
          892
        ],
        [
          900,
          904
        ],
        [
          912,
          915
        ],
        [
          924,
          928
        ],
        [
          932,
          935
        ],
        [
          947,
          964
        ],
        [
          976,
          979
        ],
        [
          983,
          987
        ],
        [
          998,
          1016
        ],
        [
          1027,
          1030
        ],
        [
          1041,
          1058
        ],
        [
          1071,
          1072
        ],
        [
          1080,
          1082
        ],
        [
          1092,
          1094
        ],
        [
          1103,
          1106
        ],
        [
          1117,
          1118
        ],
        [
          1131,
          1134
        ],
        [
          1145,
          1148
        ],
        [
          1157,
          1161
        ],
        [
          1173,
          1189
        ],
        [
          1199,
          1201
        ],
        [
          1213,
          1216
        ],
        [
          1225,
          1229
        ]
      ],
      "directional_missing": {
        "above": 7410,
        "below": 0
      },
      "groups": [
        {
          "box": [
            863,
            1095,
            947,
            1113
          ],
          "body_count": 7,
          "width_xh": 6.798268092804701,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            964,
            1095,
            998,
            1113
          ],
          "body_count": 3,
          "width_xh": 2.7516799423257123,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1016,
            1093,
            1232,
            1111
          ],
          "body_count": 15,
          "width_xh": 17.48126081006923,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00070",
      "column_id": "single:column-0000",
      "xheight": 12.136770292458095,
      "profile_runs": [
        [
          844,
          854
        ],
        [
          856,
          867
        ],
        [
          868,
          878
        ],
        [
          899,
          909
        ],
        [
          910,
          923
        ],
        [
          924,
          937
        ],
        [
          939,
          947
        ],
        [
          951,
          958
        ],
        [
          962,
          972
        ],
        [
          974,
          978
        ],
        [
          983,
          994
        ],
        [
          1014,
          1023
        ],
        [
          1026,
          1036
        ],
        [
          1038,
          1047
        ],
        [
          1070,
          1081
        ],
        [
          1085,
          1088
        ],
        [
          1093,
          1098
        ],
        [
          1106,
          1110
        ],
        [
          1115,
          1120
        ],
        [
          1122,
          1125
        ],
        [
          1128,
          1147
        ],
        [
          1150,
          1156
        ],
        [
          1176,
          1184
        ],
        [
          1187,
          1199
        ],
        [
          1201,
          1209
        ],
        [
          1213,
          1217
        ],
        [
          1220,
          1228
        ],
        [
          1232,
          1244
        ],
        [
          1262,
          1274
        ],
        [
          1276,
          1289
        ],
        [
          1290,
          1295
        ],
        [
          1296,
          1298
        ],
        [
          1300,
          1312
        ],
        [
          1316,
          1327
        ],
        [
          1329,
          1341
        ],
        [
          1344,
          1352
        ],
        [
          1356,
          1361
        ],
        [
          1362,
          1365
        ],
        [
          1366,
          1371
        ],
        [
          1373,
          1385
        ],
        [
          1386,
          1394
        ],
        [
          1421,
          1437
        ],
        [
          1438,
          1450
        ],
        [
          1477,
          1489
        ],
        [
          1493,
          1500
        ],
        [
          1504,
          1513
        ],
        [
          1515,
          1524
        ],
        [
          1528,
          1532
        ],
        [
          1536,
          1548
        ]
      ],
      "profile_gaps": [
        [
          854,
          856
        ],
        [
          867,
          868
        ],
        [
          878,
          899
        ],
        [
          909,
          910
        ],
        [
          923,
          924
        ],
        [
          937,
          939
        ],
        [
          947,
          951
        ],
        [
          958,
          962
        ],
        [
          972,
          974
        ],
        [
          978,
          983
        ],
        [
          994,
          1014
        ],
        [
          1023,
          1026
        ],
        [
          1036,
          1038
        ],
        [
          1047,
          1070
        ],
        [
          1081,
          1085
        ],
        [
          1088,
          1093
        ],
        [
          1098,
          1106
        ],
        [
          1110,
          1115
        ],
        [
          1120,
          1122
        ],
        [
          1125,
          1128
        ],
        [
          1147,
          1150
        ],
        [
          1156,
          1176
        ],
        [
          1184,
          1187
        ],
        [
          1199,
          1201
        ],
        [
          1209,
          1213
        ],
        [
          1217,
          1220
        ],
        [
          1228,
          1232
        ],
        [
          1244,
          1262
        ],
        [
          1274,
          1276
        ],
        [
          1289,
          1290
        ],
        [
          1295,
          1296
        ],
        [
          1298,
          1300
        ],
        [
          1312,
          1316
        ],
        [
          1327,
          1329
        ],
        [
          1341,
          1344
        ],
        [
          1352,
          1356
        ],
        [
          1361,
          1362
        ],
        [
          1365,
          1366
        ],
        [
          1371,
          1373
        ],
        [
          1385,
          1386
        ],
        [
          1394,
          1421
        ],
        [
          1437,
          1438
        ],
        [
          1450,
          1477
        ],
        [
          1489,
          1493
        ],
        [
          1500,
          1504
        ],
        [
          1513,
          1515
        ],
        [
          1524,
          1528
        ],
        [
          1532,
          1536
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 21580
      },
      "groups": [
        {
          "box": [
            1093,
            1146,
            1156,
            1167
          ],
          "body_count": 4,
          "width_xh": 5.190837305304262,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1176,
            1146,
            1244,
            1171
          ],
          "body_count": 6,
          "width_xh": 5.602808520010949,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1262,
            1146,
            1394,
            1170
          ],
          "body_count": 10,
          "width_xh": 10.876040068256549,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1421,
            1143,
            1450,
            1165
          ],
          "body_count": 1,
          "width_xh": 2.3894330452987873,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      867,
      1104,
      1550,
      1147
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00069"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00069"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00068",
      "column_id": "single:column-0000",
      "xheight": 12.356088176179128,
      "assigned_pixels": 448,
      "supported": null,
      "runs": [
        {
          "x0": 867,
          "x1": 875,
          "body_cut_fraction": 0.634013839430237,
          "body_pixels": 12,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 878,
          "x1": 888,
          "body_cut_fraction": 0.6302827730208314,
          "body_pixels": 22,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 892,
          "x1": 900,
          "body_cut_fraction": 0.6302238768222221,
          "body_pixels": 19,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 904,
          "x1": 912,
          "body_cut_fraction": 0.6375647458724503,
          "body_pixels": 20,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 915,
          "x1": 924,
          "body_cut_fraction": 0.6550034171432666,
          "body_pixels": 15,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 928,
          "x1": 932,
          "body_cut_fraction": 0.6703423438005847,
          "body_pixels": 11,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 935,
          "x1": 947,
          "body_cut_fraction": 0.6737437024947239,
          "body_pixels": 28,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 964,
          "x1": 976,
          "body_cut_fraction": 0.6991852920943666,
          "body_pixels": 8,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 979,
          "x1": 983,
          "body_cut_fraction": 0.7099789575914535,
          "body_pixels": 11,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 987,
          "x1": 998,
          "body_cut_fraction": 0.723191359432596,
          "body_pixels": 24,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1016,
          "x1": 1027,
          "body_cut_fraction": 0.7511753323670706,
          "body_pixels": 13,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1030,
          "x1": 1041,
          "body_cut_fraction": 0.7341097875909586,
          "body_pixels": 21,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1058,
          "x1": 1071,
          "body_cut_fraction": 0.7221156958936148,
          "body_pixels": 23,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1072,
          "x1": 1080,
          "body_cut_fraction": 0.7249643395482006,
          "body_pixels": 18,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1082,
          "x1": 1092,
          "body_cut_fraction": 0.7381353188734218,
          "body_pixels": 14,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1094,
          "x1": 1103,
          "body_cut_fraction": 0.7598107981727292,
          "body_pixels": 4,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1106,
          "x1": 1117,
          "body_cut_fraction": 0.7820581678524403,
          "body_pixels": 11,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1118,
          "x1": 1131,
          "body_cut_fraction": 0.8016422937327639,
          "body_pixels": 21,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1134,
          "x1": 1145,
          "body_cut_fraction": 0.8242088921915611,
          "body_pixels": 13,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1148,
          "x1": 1157,
          "body_cut_fraction": 0.8453742671126964,
          "body_pixels": 7,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1161,
          "x1": 1173,
          "body_cut_fraction": 0.8588433653684031,
          "body_pixels": 20,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1189,
          "x1": 1199,
          "body_cut_fraction": 0.8611212275718059,
          "body_pixels": 6,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1201,
          "x1": 1213,
          "body_cut_fraction": 0.8429855739075911,
          "body_pixels": 14,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1216,
          "x1": 1225,
          "body_cut_fraction": 0.8068234955577139,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1229,
          "x1": 1232,
          "body_cut_fraction": 0.7932718247545049,
          "body_pixels": 6,
          "body_extent_px": 2,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00069",
      "column_id": "single:column-0000",
      "xheight": 12.39212839941797,
      "assigned_pixels": 2880,
      "supported": null,
      "runs": [
        {
          "x0": 873,
          "x1": 874,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 876,
          "x1": 883,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 890,
          "x1": 893,
          "body_cut_fraction": 0.0,
          "body_pixels": 24,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 915,
          "x1": 934,
          "body_cut_fraction": 0.0,
          "body_pixels": 114,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 935,
          "x1": 944,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 946,
          "x1": 951,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 952,
          "x1": 961,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 964,
          "x1": 972,
          "body_cut_fraction": 0.0,
          "body_pixels": 41,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 976,
          "x1": 984,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 988,
          "x1": 992,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 995,
          "x1": 1005,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1008,
          "x1": 1019,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1022,
          "x1": 1026,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1045,
          "x1": 1054,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1057,
          "x1": 1067,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1071,
          "x1": 1074,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1094,
          "x1": 1107,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1125,
          "x1": 1146,
          "body_cut_fraction": 0.0,
          "body_pixels": 111,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1149,
          "x1": 1157,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1158,
          "x1": 1165,
          "body_cut_fraction": 0.0,
          "body_pixels": 36,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1167,
          "x1": 1177,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1179,
          "x1": 1189,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1191,
          "x1": 1199,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1203,
          "x1": 1207,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1208,
          "x1": 1211,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 1212,
          "x1": 1219,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1236,
          "x1": 1247,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1249,
          "x1": 1261,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1263,
          "x1": 1271,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1274,
          "x1": 1287,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1288,
          "x1": 1293,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1294,
          "x1": 1297,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 1298,
          "x1": 1303,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1306,
          "x1": 1315,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1319,
          "x1": 1329,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1330,
          "x1": 1343,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1344,
          "x1": 1352,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1374,
          "x1": 1385,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1388,
          "x1": 1398,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1399,
          "x1": 1409,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1412,
          "x1": 1420,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1421,
          "x1": 1422,
          "body_cut_fraction": 0.0,
          "body_pixels": 2,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1424,
          "x1": 1432,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1436,
          "x1": 1440,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1443,
          "x1": 1455,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1458,
          "x1": 1469,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1472,
          "x1": 1476,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1480,
          "x1": 1491,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1511,
          "x1": 1522,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1524,
          "x1": 1536,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1538,
          "x1": 1547,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00070",
      "column_id": "single:column-0000",
      "xheight": 12.136770292458095,
      "assigned_pixels": 101,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 115,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.106916600700546,
        "required_common_rows": 2.471217635235826,
        "xheight_px": 12.356088176179128,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          867,
          1082.775,
          1232,
          1116.057
        ],
        "boundary_path": [
          [
            822.5,
            1172.0
          ],
          [
            822.5,
            1393.0
          ]
        ],
        "row_id": "row-00068"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.142593850706455,
        "required_common_rows": 2.4784256798835944,
        "xheight_px": 12.39212839941797,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          873,
          1109.072,
          1547,
          1146.808
        ],
        "boundary_path": [
          [
            822.5,
            1172.0
          ],
          [
            822.5,
            1393.0
          ]
        ],
        "row_id": "row-00069"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.892047725275735,
        "required_common_rows": 2.4273540584916193,
        "xheight_px": 12.136770292458095,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          867,
          1139.944,
          1548,
          1176.007
        ],
        "boundary_path": [
          [
            822.5,
            1172.0
          ],
          [
            822.5,
            1393.0
          ]
        ],
        "row_id": "row-00070"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            822.5,
            1172.0
          ],
          [
            822.5,
            1393.0
          ]
        ],
        "width": 39,
        "extent": [
          803,
          1172,
          842,
          1393
        ],
        "source": "detector",
        "proposal_id": "proposal-0003",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 39.0,
          "local_xheight_max_px": 12.783280785976785,
          "width_xh": 3.05085999853675,
          "required_width_px": 19.30167046481103,
          "spacing_sides": [
            {
              "samples": 65,
              "letter_q25_xh": 0.23468153834898076,
              "median_xh": 0.31290871779864105,
              "word_q75_xh": 0.3987755839572809,
              "q90_xh": 1.0066101594193197
            },
            {
              "samples": 60,
              "letter_q25_xh": 0.16637792039054217,
              "median_xh": 0.32159776576932075,
              "word_q75_xh": 0.4100084969808488,
              "q90_xh": 0.8002934768542752
            }
          ],
          "side_row_counts": [
            7,
            7
          ],
          "side_span_xh": [
            14.475704875621284,
            14.21117966831226
          ],
          "shared_span_xh": 13.959757513561057,
          "occupied_rows": 7,
          "bilateral_rows": 7,
          "participants": [
            {
              "line_index": 104,
              "xheight": 12.103556384878402
            },
            {
              "line_index": 105,
              "xheight": 11.89976766105383
            },
            {
              "line_index": 106,
              "xheight": 12.209529398258155
            },
            {
              "line_index": 107,
              "xheight": 12.247492804064223
            },
            {
              "line_index": 108,
              "xheight": 12.783280785976785
            },
            {
              "line_index": 109,
              "xheight": 12.069895662801628
            },
            {
              "line_index": 110,
              "xheight": 12.538380485540529
            },
            {
              "line_index": 111,
              "xheight": 12.020825812135172
            },
            {
              "line_index": 112,
              "xheight": 12.259840909922104
            },
            {
              "line_index": 113,
              "xheight": 12.07583615676026
            },
            {
              "line_index": 114,
              "xheight": 12.437897354265715
            },
            {
              "line_index": 115,
              "xheight": 12.215957360445145
            },
            {
              "line_index": 116,
              "xheight": 12.13203939813252
            },
            {
              "line_index": 117,
              "xheight": 11.527740265406692
            }
          ],
          "observed_gap_widths_px": [
            59,
            45,
            45,
            72,
            43,
            56,
            43
          ],
          "white_rows": 7,
          "baseline_matching_reach_px": 15.228750000000048,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "b9bf68376748538d41740d4b21fce71b107dacfc8ec704546eb76b57bcae773e"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "mixed_region_axes",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.4600848544790301,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## nlg--6ae0ac01064a587e--s007-l0013

Card `k9420de9361`; context `segcp7_a`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/fdd97d32afbc2bd839bfadd278c1811b057edb9af3326e2a7ea25b36c73e3b57.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/fdd97d32afbc2bd839bfadd278c1811b057edb9af3326e2a7ea25b36c73e3b57.png`; SHA-256 `fdd97d32afbc2bd839bfadd278c1811b057edb9af3326e2a7ea25b36c73e3b57`.

Triggers: {"mismatches": {"union": "FN", "merged": "FN", "neighbour_words": "FN", "orientation": "FN", "geometry_unavailable": "FN", "crossing": "FN"}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k9420de9361",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_clipped"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "yes",
  "horizontally_missegmented_reason": "The right boundary cuts through the terminal full stop.",
  "line_id": "nlg--6ae0ac01064a587e--s007-l0013"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00013",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      107,
      1057,
      1151,
      1129
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00013"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00013"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00013",
      "column_id": "single:column-0000",
      "xheight": 20.429853190204994,
      "assigned_pixels": 7259,
      "supported": null,
      "runs": [
        {
          "x0": 112,
          "x1": 130,
          "body_cut_fraction": 0.0,
          "body_pixels": 158,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 136,
          "x1": 156,
          "body_cut_fraction": 0.0,
          "body_pixels": 170,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 162,
          "x1": 168,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 173,
          "x1": 188,
          "body_cut_fraction": 0.0,
          "body_pixels": 139,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 194,
          "x1": 208,
          "body_cut_fraction": 0.0,
          "body_pixels": 103,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 229,
          "x1": 230,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 231,
          "x1": 252,
          "body_cut_fraction": 0.0,
          "body_pixels": 162,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 255,
          "x1": 263,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 265,
          "x1": 271,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 14,
          "complete": true
        },
        {
          "x0": 272,
          "x1": 282,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 288,
          "x1": 302,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 325,
          "x1": 347,
          "body_cut_fraction": 0.0,
          "body_pixels": 217,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 350,
          "x1": 372,
          "body_cut_fraction": 0.0,
          "body_pixels": 211,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 376,
          "x1": 397,
          "body_cut_fraction": 0.0,
          "body_pixels": 191,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 416,
          "x1": 420,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 421,
          "x1": 432,
          "body_cut_fraction": 0.0,
          "body_pixels": 94,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 436,
          "x1": 449,
          "body_cut_fraction": 0.0,
          "body_pixels": 144,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 456,
          "x1": 476,
          "body_cut_fraction": 0.0,
          "body_pixels": 132,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 480,
          "x1": 495,
          "body_cut_fraction": 0.0,
          "body_pixels": 144,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 497,
          "x1": 515,
          "body_cut_fraction": 0.0,
          "body_pixels": 146,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 519,
          "x1": 535,
          "body_cut_fraction": 0.0,
          "body_pixels": 109,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 555,
          "x1": 574,
          "body_cut_fraction": 0.0,
          "body_pixels": 119,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 580,
          "x1": 601,
          "body_cut_fraction": 0.0,
          "body_pixels": 195,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 623,
          "x1": 645,
          "body_cut_fraction": 0.0,
          "body_pixels": 185,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 650,
          "x1": 671,
          "body_cut_fraction": 0.0,
          "body_pixels": 197,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 676,
          "x1": 684,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 688,
          "x1": 704,
          "body_cut_fraction": 0.0,
          "body_pixels": 146,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 711,
          "x1": 718,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 723,
          "x1": 745,
          "body_cut_fraction": 0.0,
          "body_pixels": 199,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 751,
          "x1": 757,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 780,
          "x1": 796,
          "body_cut_fraction": 0.0,
          "body_pixels": 157,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 800,
          "x1": 822,
          "body_cut_fraction": 0.0,
          "body_pixels": 205,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 840,
          "x1": 860,
          "body_cut_fraction": 0.0,
          "body_pixels": 132,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 864,
          "x1": 879,
          "body_cut_fraction": 0.0,
          "body_pixels": 139,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 902,
          "x1": 922,
          "body_cut_fraction": 0.0,
          "body_pixels": 173,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 926,
          "x1": 947,
          "body_cut_fraction": 0.0,
          "body_pixels": 195,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 949,
          "x1": 969,
          "body_cut_fraction": 0.0,
          "body_pixels": 114,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 974,
          "x1": 989,
          "body_cut_fraction": 0.0,
          "body_pixels": 144,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 992,
          "x1": 1007,
          "body_cut_fraction": 0.0,
          "body_pixels": 123,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1011,
          "x1": 1027,
          "body_cut_fraction": 0.0,
          "body_pixels": 153,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1030,
          "x1": 1039,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1041,
          "x1": 1057,
          "body_cut_fraction": 0.0,
          "body_pixels": 135,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1061,
          "x1": 1082,
          "body_cut_fraction": 0.0,
          "body_pixels": 156,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1085,
          "x1": 1100,
          "body_cut_fraction": 0.0,
          "body_pixels": 141,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1103,
          "x1": 1120,
          "body_cut_fraction": 0.0,
          "body_pixels": 149,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1124,
          "x1": 1140,
          "body_cut_fraction": 0.0,
          "body_pixels": 122,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1146,
          "x1": 1151,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 7,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 26,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "1c1a102613197d06a57805ab75564f8b555cca462184508efdae203197f5858c"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "mixed_region_axes",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.047619047619047616,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--f304fbe9ad00db89--s000-l0031

Card `kbf28ea35fc`; context `segcp7_a`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_a/r1/crops/444502d4fb9281c2e898086f4274d4d698fbc84304f618d78d3729bc620a2a3e.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/444502d4fb9281c2e898086f4274d4d698fbc84304f618d78d3729bc620a2a3e.png`; SHA-256 `444502d4fb9281c2e898086f4274d4d698fbc84304f618d78d3729bc620a2a3e`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "kbf28ea35fc",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Neighbouring capitals are cut through; no full neighbouring word is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows a horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "No split line or column crossing is visible.",
  "line_id": "gazette_modern--f304fbe9ad00db89--s000-l0031"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00042",
  "neighbour_rows": [
    {
      "row_id": "row-00041",
      "column_id": "single:column-0000",
      "xheight": 15.29686620951179,
      "profile_runs": [
        [
          376,
          389
        ],
        [
          390,
          395
        ],
        [
          400,
          409
        ],
        [
          425,
          430
        ],
        [
          431,
          440
        ],
        [
          442,
          451
        ],
        [
          453,
          465
        ],
        [
          466,
          477
        ],
        [
          478,
          491
        ],
        [
          492,
          493
        ],
        [
          494,
          504
        ],
        [
          519,
          522
        ],
        [
          524,
          535
        ],
        [
          540,
          550
        ],
        [
          553,
          567
        ],
        [
          569,
          582
        ],
        [
          584,
          594
        ],
        [
          596,
          609
        ],
        [
          610,
          623
        ]
      ],
      "profile_gaps": [
        [
          389,
          390
        ],
        [
          395,
          400
        ],
        [
          409,
          425
        ],
        [
          430,
          431
        ],
        [
          440,
          442
        ],
        [
          451,
          453
        ],
        [
          465,
          466
        ],
        [
          477,
          478
        ],
        [
          491,
          492
        ],
        [
          493,
          494
        ],
        [
          504,
          519
        ],
        [
          522,
          524
        ],
        [
          535,
          540
        ],
        [
          550,
          553
        ],
        [
          567,
          569
        ],
        [
          582,
          584
        ],
        [
          594,
          596
        ],
        [
          609,
          610
        ]
      ],
      "directional_missing": {
        "above": 6709,
        "below": 0
      },
      "groups": [
        {
          "box": [
            423,
            1156,
            623,
            1185
          ],
          "body_count": 13,
          "width_xh": 13.074573396977048,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00043",
      "column_id": "single:column-0000",
      "xheight": 14.265624039494014,
      "profile_runs": [
        [
          311,
          316
        ],
        [
          317,
          327
        ],
        [
          329,
          337
        ],
        [
          340,
          348
        ],
        [
          350,
          367
        ],
        [
          369,
          370
        ],
        [
          375,
          379
        ],
        [
          389,
          405
        ],
        [
          409,
          426
        ],
        [
          443,
          457
        ],
        [
          458,
          461
        ],
        [
          468,
          482
        ],
        [
          484,
          485
        ],
        [
          489,
          491
        ],
        [
          492,
          503
        ],
        [
          510,
          513
        ],
        [
          518,
          526
        ],
        [
          529,
          537
        ],
        [
          545,
          550
        ],
        [
          556,
          557
        ],
        [
          563,
          567
        ],
        [
          574,
          579
        ],
        [
          584,
          600
        ]
      ],
      "profile_gaps": [
        [
          316,
          317
        ],
        [
          327,
          329
        ],
        [
          337,
          340
        ],
        [
          348,
          350
        ],
        [
          367,
          369
        ],
        [
          370,
          375
        ],
        [
          379,
          389
        ],
        [
          405,
          409
        ],
        [
          426,
          443
        ],
        [
          457,
          458
        ],
        [
          461,
          468
        ],
        [
          482,
          484
        ],
        [
          485,
          489
        ],
        [
          491,
          492
        ],
        [
          503,
          510
        ],
        [
          513,
          518
        ],
        [
          526,
          529
        ],
        [
          537,
          545
        ],
        [
          550,
          556
        ],
        [
          557,
          563
        ],
        [
          567,
          574
        ],
        [
          579,
          584
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 6132
      },
      "groups": [
        {
          "box": [
            308,
            1214,
            426,
            1236
          ],
          "body_count": 7,
          "width_xh": 8.271632539405218,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            442,
            1216,
            557,
            1238
          ],
          "body_count": 9,
          "width_xh": 8.061336796877967,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            561,
            1216,
            600,
            1237
          ],
          "body_count": 3,
          "width_xh": 2.733844652854267,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      403,
      1181,
      610,
      1220
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00042"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00042"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00041",
      "column_id": "single:column-0000",
      "xheight": 15.29686620951179,
      "assigned_pixels": 52,
      "supported": null,
      "runs": [
        {
          "x0": 584,
          "x1": 594,
          "body_cut_fraction": 0.9907060220706969,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 597,
          "x1": 608,
          "body_cut_fraction": 0.9801560472892747,
          "body_pixels": 5,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00042",
      "column_id": "single:column-0000",
      "xheight": 15.031326947793787,
      "assigned_pixels": 876,
      "supported": null,
      "runs": [
        {
          "x0": 409,
          "x1": 412,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 422,
          "x1": 426,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 445,
          "x1": 449,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 456,
          "x1": 459,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 466,
          "x1": 476,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 479,
          "x1": 489,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 494,
          "x1": 499,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 502,
          "x1": 514,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 517,
          "x1": 525,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 529,
          "x1": 541,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 544,
          "x1": 547,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 549,
          "x1": 557,
          "body_cut_fraction": 0.0,
          "body_pixels": 41,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 559,
          "x1": 569,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 571,
          "x1": 580,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 582,
          "x1": 593,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 596,
          "x1": 605,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00043",
      "column_id": "single:column-0000",
      "xheight": 14.265624039494014,
      "assigned_pixels": 280,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 124,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 9.359764633268146,
        "required_common_rows": 3.0593732419023585,
        "xheight_px": 15.29686620951179,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          403,
          1136.626,
          610,
          1185.5
        ],
        "boundary_path": [
          [
            847.0,
            635.0
          ],
          [
            847.0,
            879.0
          ]
        ],
        "row_id": "row-00041"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 9.037631592458867,
        "required_common_rows": 3.0062653895587577,
        "xheight_px": 15.031326947793787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          408,
          1177.272,
          605,
          1216.301
        ],
        "boundary_path": [
          [
            847.0,
            635.0
          ],
          [
            847.0,
            879.0
          ]
        ],
        "row_id": "row-00042"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 8.140321169447581,
        "required_common_rows": 2.853124807898803,
        "xheight_px": 14.265624039494014,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 1.8000000000000003,
          "threshold": 128.4
        },
        "line_extent": [
          403,
          1212.297,
          600,
          1246.588
        ],
        "boundary_path": [
          [
            847.0,
            635.0
          ],
          [
            847.0,
            879.0
          ]
        ],
        "row_id": "row-00043"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            847.0,
            635.0
          ],
          [
            847.0,
            879.0
          ]
        ],
        "width": 34,
        "extent": [
          830,
          635,
          864,
          879
        ],
        "source": "detector",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 34.0,
          "local_xheight_max_px": 12.657955594510327,
          "width_xh": 2.686057771821034,
          "required_width_px": 18.98693339176549,
          "spacing_sides": [
            {
              "samples": 55,
              "letter_q25_xh": 0.15974375890784379,
              "median_xh": 0.16289462948890007,
              "word_q75_xh": 0.24434194423335012,
              "q90_xh": 0.635952756687319
            },
            {
              "samples": 76,
              "letter_q25_xh": 0.08838998812225449,
              "median_xh": 0.16357034547578675,
              "word_q75_xh": 0.28027573650138476,
              "q90_xh": 0.8574285303476159
            }
          ],
          "side_row_counts": [
            5,
            8
          ],
          "side_span_xh": [
            9.349930098611514,
            16.86070064051732
          ],
          "shared_span_xh": 9.349930098611514,
          "occupied_rows": 8,
          "bilateral_rows": 5,
          "participants": [
            {
              "line_index": 112,
              "xheight": 12.657955594510327
            },
            {
              "line_index": 113,
              "xheight": 12.277875619811539
            },
            {
              "line_index": 114,
              "xheight": 12.26506201597465
            },
            {
              "line_index": 115,
              "xheight": 12.520050947053278
            },
            {
              "line_index": 116,
              "xheight": 12.411743953946939
            },
            {
              "line_index": 119,
              "xheight": 12.285274407141742
            },
            {
              "line_index": 120,
              "xheight": 12.530949523379263
            },
            {
              "line_index": 121,
              "xheight": 11.942829944458481
            },
            {
              "line_index": 122,
              "xheight": 11.313498522218083
            },
            {
              "line_index": 123,
              "xheight": 12.272674478810302
            },
            {
              "line_index": 124,
              "xheight": 12.034314459315283
            },
            {
              "line_index": 125,
              "xheight": 12.227155198471223
            },
            {
              "line_index": 126,
              "xheight": 12.296541998893872
            }
          ],
          "observed_gap_widths_px": [
            67,
            40,
            69,
            38,
            68,
            0.0,
            0.0,
            0.0
          ],
          "white_rows": 5,
          "baseline_matching_reach_px": 14.803250000000048,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "5fccfc533d2eb06a9b40de09df7546f817d19e0f26053aaa7baf758b9a694332"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.5038095108644547,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--feb39c43ac177ef8--s000-l0665

Card `k600f621de1`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/94c497379da0a67cb367e121bb780afd47eca6592f55970a161ea3e2ecad6827.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/94c497379da0a67cb367e121bb780afd47eca6592f55970a161ea3e2ecad6827.png`; SHA-256 `94c497379da0a67cb367e121bb780afd47eca6592f55970a161ea3e2ecad6827`.

Triggers: {"mismatches": {"union": "FN", "merged": "FN", "neighbour_words": "FN", "orientation": "FN", "geometry_unavailable": "FN", "crossing": "FN"}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k600f621de1",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_clipped"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "yes",
  "horizontally_missegmented_reason": "The right edge cuts into the final word δεξιά.",
  "line_id": "gazette_modern--feb39c43ac177ef8--s000-l0665"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00115",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      93,
      1977,
      535,
      1997
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00115"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00115"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00115",
      "column_id": "single:column-0000",
      "xheight": 8.50182381219031,
      "assigned_pixels": 1137,
      "supported": null,
      "runs": [
        {
          "x0": 99,
          "x1": 108,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 10,
          "complete": true
        },
        {
          "x0": 109,
          "x1": 117,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 118,
          "x1": 125,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 126,
          "x1": 133,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 135,
          "x1": 142,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 143,
          "x1": 146,
          "body_cut_fraction": 0.0,
          "body_pixels": 20,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 147,
          "x1": 155,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 156,
          "x1": 163,
          "body_cut_fraction": 0.0,
          "body_pixels": 41,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 167,
          "x1": 169,
          "body_cut_fraction": 0.0,
          "body_pixels": 17,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 170,
          "x1": 190,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 194,
          "x1": 200,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 204,
          "x1": 212,
          "body_cut_fraction": 0.0,
          "body_pixels": 19,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 215,
          "x1": 222,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 6,
          "complete": true
        },
        {
          "x0": 223,
          "x1": 236,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 237,
          "x1": 250,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 6,
          "complete": true
        },
        {
          "x0": 251,
          "x1": 256,
          "body_cut_fraction": 0.0,
          "body_pixels": 19,
          "body_extent_px": 6,
          "complete": true
        },
        {
          "x0": 259,
          "x1": 273,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 274,
          "x1": 283,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 284,
          "x1": 290,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 5,
          "complete": true
        },
        {
          "x0": 291,
          "x1": 312,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 315,
          "x1": 326,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 327,
          "x1": 343,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 9,
          "complete": true
        },
        {
          "x0": 346,
          "x1": 352,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 353,
          "x1": 365,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 8,
          "complete": true
        },
        {
          "x0": 366,
          "x1": 375,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 6,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 1154,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "6de02ab6f1f0e5f030f69d143326046a73d987269d6033aed7eaa940a3660ca3"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 1.0,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--b9f59878fb904d91--s000-l0007

Card `k59004cfecb`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/41c2b2232b4187a73d0a7f31af78229037e36ebe7e64fa436b89bb354067c23f.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/41c2b2232b4187a73d0a7f31af78229037e36ebe7e64fa436b89bb354067c23f.png`; SHA-256 `41c2b2232b4187a73d0a7f31af78229037e36ebe7e64fa436b89bb354067c23f`.

Triggers: {"mismatches": {"geometry_unavailable": "FN", "crossing": "FN"}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k59004cfecb",
  "letters": "n",
  "marks": "n",
  "crop_ok": "n",
  "errors": [
    "missing_word_or_span",
    "merged_two_lines",
    "crop_clipped",
    "crop_overrun",
    "missing_mark"
  ],
  "detail": "«ΑΝΩΝΥΜΟΣ ΞΕΝΟΔΟΧΕΙΑΚΗ…», ΕΝΕΡΓΗΤΙΚΟΝ, Ι. ΠΑΓΙΟΝ, 1984, 1985 → omitted; Ἰσολογισμός → Ισολογισμός",
  "neighbour_whole_word": "yes",
  "neighbour_whole_word_reason": "Complete words from the large heading and table headings accompany the target line.",
  "multi_line": "yes",
  "multi_line_reason": "Several complete rotated text lines and table headings are visible.",
  "rotated": "yes",
  "rotated_reason": "The printed lines run vertically, rotated approximately 90 degrees.",
  "horizontally_missegmented": "yes",
  "horizontally_missegmented_reason": "The crop includes multiple table columns and cuts the large heading.",
  "line_id": "gazette_modern--b9f59878fb904d91--s000-l0007"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": true,
  "neighbour_words": true,
  "orientation": true,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": true,
  "composed": {
    "measured_drop": true,
    "geometry_unavailable": false,
    "drop": true,
    "orientation_status": "measured",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00150",
  "neighbour_rows": [
    {
      "row_id": "row-00113",
      "column_id": "single:column-0000",
      "xheight": 35.0,
      "profile_runs": [
        [
          267,
          308
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 1470,
        "below": 0
      },
      "groups": [
        {
          "box": [
            267,
            1348,
            309,
            1383
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00114",
      "column_id": "single:column-0000",
      "xheight": 34.0,
      "profile_runs": [
        [
          266,
          307
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            266,
            1386,
            307,
            1420
          ],
          "body_count": 1,
          "width_xh": 1.2058823529411764,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00132",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          333,
          351
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            328,
            1483,
            351,
            1499
          ],
          "body_count": 1,
          "width_xh": 2.3,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00133",
      "column_id": "single:column-0000",
      "xheight": 9.0,
      "profile_runs": [
        [
          333,
          351
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            328,
            1501,
            351,
            1510
          ],
          "body_count": 1,
          "width_xh": 2.5555555555555554,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": true
        }
      ]
    },
    {
      "row_id": "row-00117",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          265,
          272
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            265,
            1513,
            273,
            1528
          ],
          "body_count": 1,
          "width_xh": 0.5333333333333333,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00118",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          303,
          307
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            301,
            1513,
            307,
            1528
          ],
          "body_count": 1,
          "width_xh": 0.4,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00119",
      "column_id": "single:column-0000",
      "xheight": 27.0,
      "profile_runs": [
        [
          277,
          297
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            275,
            1517,
            298,
            1544
          ],
          "body_count": 1,
          "width_xh": 0.8518518518518519,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00120",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          265,
          272
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            265,
            1531,
            273,
            1547
          ],
          "body_count": 1,
          "width_xh": 0.5,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00134",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1533,
            350,
            1548
          ],
          "body_count": 1,
          "width_xh": 1.0666666666666667,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00121",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          302,
          307
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            300,
            1533,
            307,
            1549
          ],
          "body_count": 1,
          "width_xh": 0.4375,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00135",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1550,
            350,
            1566
          ],
          "body_count": 1,
          "width_xh": 1.0,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00136",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          334,
          356
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1575,
            356,
            1591
          ],
          "body_count": 1,
          "width_xh": 1.375,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00137",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          334,
          356
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1610,
            356,
            1625
          ],
          "body_count": 1,
          "width_xh": 1.4666666666666666,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00122",
      "column_id": "single:column-0000",
      "xheight": 40.0,
      "profile_runs": [
        [
          267,
          306
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            266,
            1595,
            307,
            1635
          ],
          "body_count": 1,
          "width_xh": 1.025,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00138",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1627,
            350,
            1641
          ],
          "body_count": 1,
          "width_xh": 1.1428571428571428,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00139",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1642,
            351,
            1657
          ],
          "body_count": 1,
          "width_xh": 1.1333333333333333,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00140",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1659,
            350,
            1673
          ],
          "body_count": 1,
          "width_xh": 1.1428571428571428,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00123",
      "column_id": "single:column-0000",
      "xheight": 40.0,
      "profile_runs": [
        [
          264,
          305
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            264,
            1638,
            305,
            1678
          ],
          "body_count": 1,
          "width_xh": 1.025,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00124",
      "column_id": "single:column-0000",
      "xheight": 37.0,
      "profile_runs": [
        [
          265,
          306
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            265,
            1681,
            306,
            1718
          ],
          "body_count": 1,
          "width_xh": 1.1081081081081081,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00141",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1734,
            350,
            1750
          ],
          "body_count": 1,
          "width_xh": 1.0,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00126",
      "column_id": "single:column-0000",
      "xheight": 30.0,
      "profile_runs": [
        [
          265,
          275
        ],
        [
          279,
          290
        ],
        [
          294,
          306
        ]
      ],
      "profile_gaps": [
        [
          275,
          279
        ],
        [
          290,
          294
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            265,
            1747,
            306,
            1778
          ],
          "body_count": 3,
          "width_xh": 1.3666666666666667,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": true
        }
      ]
    },
    {
      "row_id": "row-00142",
      "column_id": "single:column-0000",
      "xheight": 7.599999999999909,
      "profile_runs": [
        [
          333,
          334
        ],
        [
          336,
          340
        ],
        [
          342,
          350
        ]
      ],
      "profile_gaps": [
        [
          334,
          336
        ],
        [
          340,
          342
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            327,
            1763,
            350,
            1781
          ],
          "body_count": 1,
          "width_xh": 3.0263157894737205,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00143",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          334,
          352
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1806,
            352,
            1821
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00144",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          334,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            334,
            1822,
            350,
            1838
          ],
          "body_count": 1,
          "width_xh": 1.0,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00127",
      "column_id": "single:column-0000",
      "xheight": 31.0,
      "profile_runs": [
        [
          275,
          305
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            273,
            1818,
            305,
            1849
          ],
          "body_count": 1,
          "width_xh": 1.032258064516129,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00145",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "profile_runs": [
        [
          333,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            1840,
            350,
            1854
          ],
          "body_count": 1,
          "width_xh": 1.2142857142857142,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00146",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          333,
          352
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            1873,
            352,
            1888
          ],
          "body_count": 1,
          "width_xh": 1.2666666666666666,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00147",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "profile_runs": [
        [
          333,
          355
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            1907,
            355,
            1923
          ],
          "body_count": 1,
          "width_xh": 1.375,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00148",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "profile_runs": [
        [
          333,
          350
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            1924,
            350,
            1940
          ],
          "body_count": 1,
          "width_xh": 1.4166666666666667,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00149",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          333,
          355
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            1950,
            355,
            1965
          ],
          "body_count": 1,
          "width_xh": 1.4666666666666666,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00128",
      "column_id": "single:column-0000",
      "xheight": 34.0,
      "profile_runs": [
        [
          263,
          305
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            263,
            1943,
            305,
            1977
          ],
          "body_count": 1,
          "width_xh": 1.2352941176470589,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00129",
      "column_id": "single:column-0000",
      "xheight": 36.0,
      "profile_runs": [
        [
          263,
          304
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            263,
            1981,
            305,
            2017
          ],
          "body_count": 1,
          "width_xh": 1.1666666666666667,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00130",
      "column_id": "single:column-0000",
      "xheight": 35.0,
      "profile_runs": [
        [
          263,
          305
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            263,
            2064,
            305,
            2099
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00151",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "profile_runs": [
        [
          333,
          349
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            2105,
            349,
            2121
          ],
          "body_count": 1,
          "width_xh": 1.3333333333333333,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00152",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "profile_runs": [
        [
          333,
          351
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            333,
            2130,
            351,
            2145
          ],
          "body_count": 1,
          "width_xh": 1.2,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00131",
      "column_id": "single:column-0000",
      "xheight": 31.0,
      "profile_runs": [
        [
          274,
          303
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            273,
            2144,
            303,
            2175
          ],
          "body_count": 1,
          "width_xh": 0.967741935483871,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00153",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "profile_runs": [
        [
          333,
          349
        ]
      ],
      "profile_gaps": [],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            326,
            2162,
            349,
            2177
          ],
          "body_count": 1,
          "width_xh": 2.3,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": true
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      232,
      1352,
      445,
      2265
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00114",
      "row-00117",
      "row-00118",
      "row-00119",
      "row-00120",
      "row-00121",
      "row-00122",
      "row-00123",
      "row-00124",
      "row-00126",
      "row-00127",
      "row-00128",
      "row-00129",
      "row-00130",
      "row-00131",
      "row-00132",
      "row-00134",
      "row-00135",
      "row-00136",
      "row-00137",
      "row-00138",
      "row-00139",
      "row-00140",
      "row-00141",
      "row-00142",
      "row-00143",
      "row-00144",
      "row-00145",
      "row-00146",
      "row-00147",
      "row-00148",
      "row-00149",
      "row-00150",
      "row-00151",
      "row-00152",
      "row-00153"
    ],
    "supported_row_count": 36,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00114",
          "row-00117",
          "row-00118",
          "row-00119",
          "row-00120",
          "row-00121",
          "row-00122",
          "row-00123",
          "row-00124",
          "row-00126",
          "row-00127",
          "row-00128",
          "row-00129",
          "row-00130",
          "row-00131",
          "row-00132",
          "row-00134",
          "row-00135",
          "row-00136",
          "row-00137",
          "row-00138",
          "row-00139",
          "row-00140",
          "row-00141",
          "row-00142",
          "row-00143",
          "row-00144",
          "row-00145",
          "row-00146",
          "row-00147",
          "row-00148",
          "row-00149",
          "row-00150",
          "row-00151",
          "row-00152",
          "row-00153"
        ],
        "count": 36
      }
    ],
    "merged": true
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00113",
      "column_id": "single:column-0000",
      "xheight": 35.0,
      "assigned_pixels": 923,
      "supported": null,
      "runs": [
        {
          "x0": 267,
          "x1": 308,
          "body_cut_fraction": 0.11428571428571432,
          "body_pixels": 921,
          "body_extent_px": 31,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00114",
      "column_id": "single:column-0000",
      "xheight": 34.0,
      "assigned_pixels": 958,
      "supported": null,
      "runs": [
        {
          "x0": 266,
          "x1": 307,
          "body_cut_fraction": 0.0,
          "body_pixels": 958,
          "body_extent_px": 34,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00132",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 190,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 351,
          "body_cut_fraction": 0.0,
          "body_pixels": 113,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00133",
      "column_id": "single:column-0000",
      "xheight": 9.0,
      "assigned_pixels": 94,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 351,
          "body_cut_fraction": 0.0,
          "body_pixels": 94,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00117",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 83,
      "supported": null,
      "runs": [
        {
          "x0": 265,
          "x1": 272,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00118",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 48,
      "supported": null,
      "runs": [
        {
          "x0": 303,
          "x1": 307,
          "body_cut_fraction": 0.0,
          "body_pixels": 48,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00119",
      "column_id": "single:column-0000",
      "xheight": 27.0,
      "assigned_pixels": 385,
      "supported": null,
      "runs": [
        {
          "x0": 277,
          "x1": 297,
          "body_cut_fraction": 0.0,
          "body_pixels": 385,
          "body_extent_px": 27,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00120",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 89,
      "supported": null,
      "runs": [
        {
          "x0": 265,
          "x1": 272,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00134",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 158,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 158,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00121",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 61,
      "supported": null,
      "runs": [
        {
          "x0": 302,
          "x1": 307,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00135",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 241,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 172,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00136",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 201,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 356,
          "body_cut_fraction": 0.0,
          "body_pixels": 201,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00137",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 181,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 356,
          "body_cut_fraction": 0.0,
          "body_pixels": 181,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00122",
      "column_id": "single:column-0000",
      "xheight": 40.0,
      "assigned_pixels": 826,
      "supported": null,
      "runs": [
        {
          "x0": 267,
          "x1": 306,
          "body_cut_fraction": 0.0,
          "body_pixels": 823,
          "body_extent_px": 40,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00138",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "assigned_pixels": 150,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 150,
          "body_extent_px": 14,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00139",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 151,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 150,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00140",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "assigned_pixels": 154,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 154,
          "body_extent_px": 14,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00123",
      "column_id": "single:column-0000",
      "xheight": 40.0,
      "assigned_pixels": 1092,
      "supported": null,
      "runs": [
        {
          "x0": 264,
          "x1": 305,
          "body_cut_fraction": 0.0,
          "body_pixels": 1092,
          "body_extent_px": 40,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00124",
      "column_id": "single:column-0000",
      "xheight": 37.0,
      "assigned_pixels": 1064,
      "supported": null,
      "runs": [
        {
          "x0": 265,
          "x1": 306,
          "body_cut_fraction": 0.0,
          "body_pixels": 1064,
          "body_extent_px": 37,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00141",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 264,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 179,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00126",
      "column_id": "single:column-0000",
      "xheight": 30.0,
      "assigned_pixels": 828,
      "supported": null,
      "runs": [
        {
          "x0": 265,
          "x1": 275,
          "body_cut_fraction": 0.0,
          "body_pixels": 297,
          "body_extent_px": 30,
          "complete": true
        },
        {
          "x0": 279,
          "x1": 290,
          "body_cut_fraction": 0.0,
          "body_pixels": 209,
          "body_extent_px": 21,
          "complete": true
        },
        {
          "x0": 294,
          "x1": 306,
          "body_cut_fraction": 0.0,
          "body_pixels": 312,
          "body_extent_px": 30,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00142",
      "column_id": "single:column-0000",
      "xheight": 7.599999999999909,
      "assigned_pixels": 182,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 334,
          "body_cut_fraction": 0.0,
          "body_pixels": 7,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 336,
          "x1": 339,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 342,
          "x1": 349,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00143",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 148,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 352,
          "body_cut_fraction": 0.0,
          "body_pixels": 148,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00144",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 175,
      "supported": null,
      "runs": [
        {
          "x0": 334,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 175,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00127",
      "column_id": "single:column-0000",
      "xheight": 31.0,
      "assigned_pixels": 579,
      "supported": null,
      "runs": [
        {
          "x0": 275,
          "x1": 305,
          "body_cut_fraction": 0.0,
          "body_pixels": 579,
          "body_extent_px": 31,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00145",
      "column_id": "single:column-0000",
      "xheight": 14.0,
      "assigned_pixels": 111,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 111,
          "body_extent_px": 14,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00146",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 153,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 352,
          "body_cut_fraction": 0.0,
          "body_pixels": 153,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00147",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 208,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 355,
          "body_cut_fraction": 0.0,
          "body_pixels": 208,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00148",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "assigned_pixels": 251,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 130,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00149",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 155,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 355,
          "body_cut_fraction": 0.0,
          "body_pixels": 155,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00128",
      "column_id": "single:column-0000",
      "xheight": 34.0,
      "assigned_pixels": 721,
      "supported": null,
      "runs": [
        {
          "x0": 263,
          "x1": 305,
          "body_cut_fraction": 0.0,
          "body_pixels": 721,
          "body_extent_px": 34,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00129",
      "column_id": "single:column-0000",
      "xheight": 36.0,
      "assigned_pixels": 1076,
      "supported": null,
      "runs": [
        {
          "x0": 263,
          "x1": 304,
          "body_cut_fraction": 0.0,
          "body_pixels": 1074,
          "body_extent_px": 36,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00150",
      "column_id": "single:column-0000",
      "xheight": 16.0,
      "assigned_pixels": 258,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 349,
          "body_cut_fraction": 0.0,
          "body_pixels": 174,
          "body_extent_px": 16,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00130",
      "column_id": "single:column-0000",
      "xheight": 35.0,
      "assigned_pixels": 952,
      "supported": null,
      "runs": [
        {
          "x0": 263,
          "x1": 305,
          "body_cut_fraction": 0.0,
          "body_pixels": 952,
          "body_extent_px": 35,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00151",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "assigned_pixels": 252,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 349,
          "body_cut_fraction": 0.0,
          "body_pixels": 144,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00152",
      "column_id": "single:column-0000",
      "xheight": 15.0,
      "assigned_pixels": 155,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 351,
          "body_cut_fraction": 0.0,
          "body_pixels": 155,
          "body_extent_px": 15,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00131",
      "column_id": "single:column-0000",
      "xheight": 31.0,
      "assigned_pixels": 612,
      "supported": null,
      "runs": [
        {
          "x0": 274,
          "x1": 303,
          "body_cut_fraction": 0.0,
          "body_pixels": 610,
          "body_extent_px": 31,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00153",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 89,
      "supported": null,
      "runs": [
        {
          "x0": 333,
          "x1": 349,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 237,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "50dd821e4a3cc80373eb0c648971541076fcdbbdc542e42060a2ce8201562512"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "vertical",
    "orientation_cw": 270,
    "axis_confidence": 0.8117994314984134,
    "polarity_confidence": 0.45454545454545453,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--288c8a27405ee9c3--s000-l0089

Card `k89c206dd7a`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/7feaaee46c789e5eb3b2b73d2c4d3281f22c4fbb14a6c5cfad04f6c15388ec72.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/7feaaee46c789e5eb3b2b73d2c4d3281f22c4fbb14a6c5cfad04f6c15388ec72.png`; SHA-256 `7feaaee46c789e5eb3b2b73d2c4d3281f22c4fbb14a6c5cfad04f6c15388ec72`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k89c206dd7a",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Upper portions of the next line are visible, but no whole word is complete.",
  "multi_line": "no",
  "multi_line_reason": "The target line is complete; the next line has only its upper portions visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--288c8a27405ee9c3--s000-l0089"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00086",
  "neighbour_rows": [
    {
      "row_id": "row-00087",
      "column_id": "single:column-0000",
      "xheight": 11.468690395954354,
      "profile_runs": [
        [
          847,
          858
        ],
        [
          859,
          871
        ],
        [
          872,
          876
        ],
        [
          878,
          888
        ],
        [
          901,
          922
        ],
        [
          924,
          933
        ],
        [
          947,
          960
        ],
        [
          961,
          970
        ],
        [
          972,
          983
        ],
        [
          985,
          989
        ],
        [
          991,
          1000
        ],
        [
          1002,
          1009
        ],
        [
          1011,
          1028
        ],
        [
          1029,
          1039
        ],
        [
          1052,
          1064
        ],
        [
          1065,
          1074
        ],
        [
          1076,
          1097
        ],
        [
          1098,
          1108
        ],
        [
          1109,
          1120
        ],
        [
          1123,
          1133
        ],
        [
          1134,
          1142
        ],
        [
          1156,
          1167
        ],
        [
          1168,
          1180
        ],
        [
          1181,
          1190
        ],
        [
          1191,
          1203
        ],
        [
          1217,
          1228
        ],
        [
          1231,
          1243
        ],
        [
          1245,
          1249
        ],
        [
          1252,
          1264
        ],
        [
          1266,
          1271
        ],
        [
          1272,
          1278
        ],
        [
          1280,
          1285
        ],
        [
          1287,
          1292
        ],
        [
          1295,
          1298
        ],
        [
          1301,
          1313
        ],
        [
          1315,
          1327
        ],
        [
          1329,
          1335
        ],
        [
          1336,
          1341
        ],
        [
          1355,
          1365
        ],
        [
          1367,
          1389
        ],
        [
          1391,
          1395
        ],
        [
          1410,
          1420
        ],
        [
          1422,
          1426
        ],
        [
          1427,
          1439
        ],
        [
          1441,
          1445
        ],
        [
          1447,
          1456
        ],
        [
          1457,
          1467
        ],
        [
          1469,
          1479
        ],
        [
          1481,
          1493
        ],
        [
          1494,
          1512
        ],
        [
          1513,
          1523
        ],
        [
          1524,
          1534
        ],
        [
          1547,
          1557
        ],
        [
          1559,
          1567
        ]
      ],
      "profile_gaps": [
        [
          858,
          859
        ],
        [
          871,
          872
        ],
        [
          876,
          878
        ],
        [
          888,
          901
        ],
        [
          922,
          924
        ],
        [
          933,
          947
        ],
        [
          960,
          961
        ],
        [
          970,
          972
        ],
        [
          983,
          985
        ],
        [
          989,
          991
        ],
        [
          1000,
          1002
        ],
        [
          1009,
          1011
        ],
        [
          1028,
          1029
        ],
        [
          1039,
          1052
        ],
        [
          1064,
          1065
        ],
        [
          1074,
          1076
        ],
        [
          1097,
          1098
        ],
        [
          1108,
          1109
        ],
        [
          1120,
          1123
        ],
        [
          1133,
          1134
        ],
        [
          1142,
          1156
        ],
        [
          1167,
          1168
        ],
        [
          1180,
          1181
        ],
        [
          1190,
          1191
        ],
        [
          1203,
          1217
        ],
        [
          1228,
          1231
        ],
        [
          1243,
          1245
        ],
        [
          1249,
          1252
        ],
        [
          1264,
          1266
        ],
        [
          1271,
          1272
        ],
        [
          1278,
          1280
        ],
        [
          1285,
          1287
        ],
        [
          1292,
          1295
        ],
        [
          1298,
          1301
        ],
        [
          1313,
          1315
        ],
        [
          1327,
          1329
        ],
        [
          1335,
          1336
        ],
        [
          1341,
          1355
        ],
        [
          1365,
          1367
        ],
        [
          1389,
          1391
        ],
        [
          1395,
          1410
        ],
        [
          1420,
          1422
        ],
        [
          1426,
          1427
        ],
        [
          1439,
          1441
        ],
        [
          1445,
          1447
        ],
        [
          1456,
          1457
        ],
        [
          1467,
          1469
        ],
        [
          1479,
          1481
        ],
        [
          1493,
          1494
        ],
        [
          1512,
          1513
        ],
        [
          1523,
          1524
        ],
        [
          1534,
          1547
        ],
        [
          1557,
          1559
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 15280
      },
      "groups": [
        {
          "box": [
            847,
            799,
            1039,
            826
          ],
          "body_count": 13,
          "width_xh": 16.74123141973813,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1052,
            803,
            1203,
            827
          ],
          "body_count": 12,
          "width_xh": 13.166280960314886,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1217,
            804,
            1341,
            824
          ],
          "body_count": 10,
          "width_xh": 10.812045291914211,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1355,
            806,
            1395,
            831
          ],
          "body_count": 3,
          "width_xh": 3.487756545778778,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1410,
            807,
            1534,
            832
          ],
          "body_count": 12,
          "width_xh": 10.812045291914211,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      869,
      768,
      1570,
      812
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00086"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00086"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00086",
      "column_id": "single:column-0000",
      "xheight": 11.842938178555073,
      "assigned_pixels": 4243,
      "supported": null,
      "runs": [
        {
          "x0": 875,
          "x1": 879,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 880,
          "x1": 893,
          "body_cut_fraction": 0.0,
          "body_pixels": 91,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 895,
          "x1": 903,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 910,
          "x1": 928,
          "body_cut_fraction": 0.0,
          "body_pixels": 99,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 929,
          "x1": 932,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 933,
          "x1": 942,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 950,
          "x1": 962,
          "body_cut_fraction": 0.0,
          "body_pixels": 93,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 963,
          "x1": 975,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 976,
          "x1": 986,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 995,
          "x1": 1006,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1013,
          "x1": 1018,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1024,
          "x1": 1028,
          "body_cut_fraction": 0.0,
          "body_pixels": 12,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1030,
          "x1": 1042,
          "body_cut_fraction": 0.0,
          "body_pixels": 92,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1045,
          "x1": 1048,
          "body_cut_fraction": 0.0,
          "body_pixels": 11,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 1051,
          "x1": 1063,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1065,
          "x1": 1077,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1086,
          "x1": 1110,
          "body_cut_fraction": 0.0,
          "body_pixels": 172,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1112,
          "x1": 1122,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1123,
          "x1": 1134,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1136,
          "x1": 1147,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1148,
          "x1": 1171,
          "body_cut_fraction": 0.0,
          "body_pixels": 142,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1179,
          "x1": 1200,
          "body_cut_fraction": 0.0,
          "body_pixels": 118,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1203,
          "x1": 1211,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1220,
          "x1": 1226,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1235,
          "x1": 1242,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1243,
          "x1": 1252,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1254,
          "x1": 1259,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1260,
          "x1": 1283,
          "body_cut_fraction": 0.0,
          "body_pixels": 139,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1285,
          "x1": 1294,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1302,
          "x1": 1315,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1317,
          "x1": 1326,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1327,
          "x1": 1336,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1339,
          "x1": 1346,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1350,
          "x1": 1373,
          "body_cut_fraction": 0.0,
          "body_pixels": 144,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1374,
          "x1": 1383,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1391,
          "x1": 1400,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1401,
          "x1": 1411,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1419,
          "x1": 1432,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1433,
          "x1": 1441,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1442,
          "x1": 1451,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1452,
          "x1": 1475,
          "body_cut_fraction": 0.0,
          "body_pixels": 141,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1477,
          "x1": 1481,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1483,
          "x1": 1494,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1495,
          "x1": 1505,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1513,
          "x1": 1524,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1525,
          "x1": 1533,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1535,
          "x1": 1546,
          "body_cut_fraction": 0.0,
          "body_pixels": 85,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1547,
          "x1": 1559,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1560,
          "x1": 1567,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00087",
      "column_id": "single:column-0000",
      "xheight": 11.468690395954354,
      "assigned_pixels": 1096,
      "supported": null,
      "runs": [
        {
          "x0": 869,
          "x1": 871,
          "body_cut_fraction": 0.4625948208213443,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 872,
          "x1": 876,
          "body_cut_fraction": 0.4739721846797734,
          "body_pixels": 14,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 878,
          "x1": 888,
          "body_cut_fraction": 0.5049090560312504,
          "body_pixels": 32,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 901,
          "x1": 922,
          "body_cut_fraction": 0.5214100355000104,
          "body_pixels": 72,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 924,
          "x1": 933,
          "body_cut_fraction": 0.5566513917011395,
          "body_pixels": 27,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 947,
          "x1": 960,
          "body_cut_fraction": 0.5629334513796669,
          "body_pixels": 34,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 961,
          "x1": 970,
          "body_cut_fraction": 0.6035672072700491,
          "body_pixels": 28,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 972,
          "x1": 983,
          "body_cut_fraction": 0.6277604274005608,
          "body_pixels": 34,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 985,
          "x1": 989,
          "body_cut_fraction": 0.6319128065395103,
          "body_pixels": 12,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 991,
          "x1": 1000,
          "body_cut_fraction": 0.6322637524462784,
          "body_pixels": 26,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1002,
          "x1": 1009,
          "body_cut_fraction": 0.6265336372581989,
          "body_pixels": 19,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1011,
          "x1": 1028,
          "body_cut_fraction": 0.627699788171453,
          "body_pixels": 41,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1029,
          "x1": 1039,
          "body_cut_fraction": 0.6650448612310023,
          "body_pixels": 20,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1052,
          "x1": 1064,
          "body_cut_fraction": 0.7275184560832413,
          "body_pixels": 26,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1065,
          "x1": 1074,
          "body_cut_fraction": 0.7639729889456197,
          "body_pixels": 10,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1076,
          "x1": 1093,
          "body_cut_fraction": 0.7682002359337324,
          "body_pixels": 29,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1094,
          "x1": 1097,
          "body_cut_fraction": 0.7641690402836709,
          "body_pixels": 4,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1098,
          "x1": 1108,
          "body_cut_fraction": 0.76644054200164,
          "body_pixels": 17,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1109,
          "x1": 1117,
          "body_cut_fraction": 0.7745672930200106,
          "body_pixels": 13,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1118,
          "x1": 1120,
          "body_cut_fraction": 0.7816723341180595,
          "body_pixels": 3,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1123,
          "x1": 1133,
          "body_cut_fraction": 0.7933244395615896,
          "body_pixels": 11,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1134,
          "x1": 1142,
          "body_cut_fraction": 0.8089025493465866,
          "body_pixels": 10,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1156,
          "x1": 1167,
          "body_cut_fraction": 0.8547172503448162,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1168,
          "x1": 1180,
          "body_cut_fraction": 0.8766939146230698,
          "body_pixels": 7,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1181,
          "x1": 1190,
          "body_cut_fraction": 0.8961732222437504,
          "body_pixels": 8,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1191,
          "x1": 1203,
          "body_cut_fraction": 0.9102990757426043,
          "body_pixels": 4,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 126,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.6102073880430945,
        "required_common_rows": 2.3685876357110147,
        "xheight_px": 11.842938178555073,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          767.98,
          1568,
          807.779
        ],
        "boundary_path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "row_id": "row-00086"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.261234375930226,
        "required_common_rows": 2.293738079190871,
        "xheight_px": 11.468690395954354,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          869,
          797.896,
          1567,
          833.842
        ],
        "boundary_path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "row_id": "row-00087"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            819.0,
            1728.0
          ],
          [
            819.0,
            1992.0
          ]
        ],
        "width": 30,
        "extent": [
          804,
          1728,
          834,
          1992
        ],
        "source": "detector",
        "proposal_id": "proposal-0006",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 11.916477220731394,
          "width_xh": 2.51752253995067,
          "required_width_px": 17.87471583109709,
          "spacing_sides": [
            {
              "samples": 74,
              "letter_q25_xh": 0.08586565293489502,
              "median_xh": 0.16968501280117906,
              "word_q75_xh": 0.17389930563561726,
              "q90_xh": 0.462246801457529
            },
            {
              "samples": 50,
              "letter_q25_xh": 0.08587437834100385,
              "median_xh": 0.16783483599671134,
              "word_q75_xh": 0.2615305933499593,
              "q90_xh": 0.7570180262935844
            }
          ],
          "side_row_counts": [
            8,
            6
          ],
          "side_span_xh": [
            19.15801085935259,
            15.753565128577321
          ],
          "shared_span_xh": 15.753565128577321,
          "occupied_rows": 11,
          "bilateral_rows": 7,
          "participants": [
            {
              "line_index": 112,
              "xheight": 11.500908486608523
            },
            {
              "line_index": 113,
              "xheight": 11.76368880264613
            },
            {
              "line_index": 114,
              "xheight": 11.5380847210389
            },
            {
              "line_index": 115,
              "xheight": 11.608473727100545
            },
            {
              "line_index": 116,
              "xheight": 11.646100225409327
            },
            {
              "line_index": 117,
              "xheight": 11.405116480082143
            },
            {
              "line_index": 118,
              "xheight": 11.786544768944395
            },
            {
              "line_index": 120,
              "xheight": 11.67743940148307
            },
            {
              "line_index": 121,
              "xheight": 11.806868066662219
            },
            {
              "line_index": 123,
              "xheight": 11.552267431804466
            },
            {
              "line_index": 124,
              "xheight": 11.444075871056157
            },
            {
              "line_index": 125,
              "xheight": 11.916477220731394
            },
            {
              "line_index": 126,
              "xheight": 11.644916904423326
            },
            {
              "line_index": 127,
              "xheight": 11.768330411588067
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            62,
            0.0,
            0.0,
            66,
            66,
            72,
            49,
            0.0,
            123,
            123
          ],
          "white_rows": 7,
          "baseline_matching_reach_px": 13.125499999999988,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "51c27ed949896ec4c16f4d3af370b1b3e4e821916c88ce49decd17b8c3d63572"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 180,
    "axis_confidence": 0.6879743548104094,
    "polarity_confidence": 0.7692307692307693,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--73f0e4003296ba2e--s000-l0097

Card `k1b063946c1`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/7c8d29f4a461033d31bf54639a2d0eaff623ce552ed48064a86755c6ccaa4691.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/7c8d29f4a461033d31bf54639a2d0eaff623ce552ed48064a86755c6ccaa4691.png`; SHA-256 `7c8d29f4a461033d31bf54639a2d0eaff623ce552ed48064a86755c6ccaa4691`.

Triggers: {"mismatches": {"union": "FN", "merged": "FN", "neighbour_words": "FN", "orientation": "FN", "geometry_unavailable": "FN", "crossing": "FN"}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k1b063946c1",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_clipped"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "yes",
  "horizontally_missegmented_reason": "The right boundary cuts the final letter of the line.",
  "line_id": "gazette_modern--73f0e4003296ba2e--s000-l0097"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00087",
  "neighbour_rows": [
    {
      "row_id": "row-00088",
      "column_id": "single:column-0001",
      "xheight": 11.971254728320787,
      "profile_runs": [
        [
          847,
          859
        ],
        [
          860,
          878
        ],
        [
          887,
          909
        ],
        [
          910,
          919
        ],
        [
          928,
          935
        ],
        [
          937,
          948
        ],
        [
          949,
          960
        ],
        [
          961,
          993
        ],
        [
          994,
          998
        ],
        [
          1006,
          1016
        ],
        [
          1017,
          1029
        ],
        [
          1031,
          1055
        ],
        [
          1056,
          1065
        ],
        [
          1067,
          1072
        ],
        [
          1073,
          1084
        ],
        [
          1086,
          1102
        ],
        [
          1103,
          1112
        ],
        [
          1121,
          1132
        ],
        [
          1133,
          1146
        ],
        [
          1147,
          1152
        ],
        [
          1160,
          1170
        ],
        [
          1172,
          1182
        ],
        [
          1184,
          1199
        ],
        [
          1200,
          1210
        ],
        [
          1212,
          1221
        ],
        [
          1223,
          1227
        ],
        [
          1229,
          1240
        ],
        [
          1242,
          1258
        ],
        [
          1259,
          1268
        ],
        [
          1277,
          1288
        ],
        [
          1290,
          1312
        ],
        [
          1315,
          1331
        ],
        [
          1332,
          1341
        ],
        [
          1343,
          1348
        ],
        [
          1357,
          1367
        ],
        [
          1368,
          1380
        ],
        [
          1381,
          1392
        ],
        [
          1393,
          1405
        ],
        [
          1406,
          1417
        ],
        [
          1418,
          1430
        ],
        [
          1437,
          1447
        ],
        [
          1448,
          1465
        ],
        [
          1466,
          1475
        ],
        [
          1483,
          1494
        ],
        [
          1495,
          1507
        ],
        [
          1509,
          1522
        ],
        [
          1523,
          1535
        ],
        [
          1537,
          1546
        ],
        [
          1548,
          1554
        ]
      ],
      "profile_gaps": [
        [
          859,
          860
        ],
        [
          878,
          887
        ],
        [
          909,
          910
        ],
        [
          919,
          928
        ],
        [
          935,
          937
        ],
        [
          948,
          949
        ],
        [
          960,
          961
        ],
        [
          993,
          994
        ],
        [
          998,
          1006
        ],
        [
          1016,
          1017
        ],
        [
          1029,
          1031
        ],
        [
          1055,
          1056
        ],
        [
          1065,
          1067
        ],
        [
          1072,
          1073
        ],
        [
          1084,
          1086
        ],
        [
          1102,
          1103
        ],
        [
          1112,
          1121
        ],
        [
          1132,
          1133
        ],
        [
          1146,
          1147
        ],
        [
          1152,
          1160
        ],
        [
          1170,
          1172
        ],
        [
          1182,
          1184
        ],
        [
          1199,
          1200
        ],
        [
          1210,
          1212
        ],
        [
          1221,
          1223
        ],
        [
          1227,
          1229
        ],
        [
          1240,
          1242
        ],
        [
          1258,
          1259
        ],
        [
          1268,
          1277
        ],
        [
          1288,
          1290
        ],
        [
          1312,
          1315
        ],
        [
          1331,
          1332
        ],
        [
          1341,
          1343
        ],
        [
          1348,
          1357
        ],
        [
          1367,
          1368
        ],
        [
          1380,
          1381
        ],
        [
          1392,
          1393
        ],
        [
          1405,
          1406
        ],
        [
          1417,
          1418
        ],
        [
          1430,
          1437
        ],
        [
          1447,
          1448
        ],
        [
          1465,
          1466
        ],
        [
          1475,
          1483
        ],
        [
          1494,
          1495
        ],
        [
          1507,
          1509
        ],
        [
          1522,
          1523
        ],
        [
          1535,
          1537
        ],
        [
          1546,
          1548
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 20127
      },
      "groups": [
        {
          "box": [
            928,
            884,
            998,
            910
          ],
          "body_count": 6,
          "width_xh": 5.84734028208411,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1006,
            884,
            1152,
            909
          ],
          "body_count": 12,
          "width_xh": 12.195881159775428,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1357,
            881,
            1431,
            907
          ],
          "body_count": 6,
          "width_xh": 6.181474012488915,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1483,
            881,
            1555,
            907
          ],
          "body_count": 6,
          "width_xh": 6.014407147286513,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      870,
      849,
      1554,
      885
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00087"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0001",
        "row_ids": [
          "row-00087"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00087",
      "column_id": "single:column-0001",
      "xheight": 11.963923337810911,
      "assigned_pixels": 4132,
      "supported": null,
      "runs": [
        {
          "x0": 876,
          "x1": 890,
          "body_cut_fraction": 0.0,
          "body_pixels": 92,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 892,
          "x1": 904,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 906,
          "x1": 916,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 918,
          "x1": 928,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 930,
          "x1": 939,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 941,
          "x1": 946,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 947,
          "x1": 956,
          "body_cut_fraction": 0.0,
          "body_pixels": 36,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 957,
          "x1": 968,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 969,
          "x1": 978,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 980,
          "x1": 984,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 985,
          "x1": 993,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 994,
          "x1": 1002,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1010,
          "x1": 1020,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1021,
          "x1": 1026,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1027,
          "x1": 1036,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1044,
          "x1": 1054,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1056,
          "x1": 1061,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1062,
          "x1": 1074,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1075,
          "x1": 1085,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1086,
          "x1": 1096,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1097,
          "x1": 1109,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1110,
          "x1": 1120,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1122,
          "x1": 1130,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1132,
          "x1": 1136,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1138,
          "x1": 1147,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1154,
          "x1": 1164,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1165,
          "x1": 1192,
          "body_cut_fraction": 0.0,
          "body_pixels": 153,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1199,
          "x1": 1212,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1213,
          "x1": 1220,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 10,
          "complete": true
        },
        {
          "x0": 1222,
          "x1": 1225,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1227,
          "x1": 1238,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1240,
          "x1": 1250,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1252,
          "x1": 1262,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1264,
          "x1": 1272,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1273,
          "x1": 1284,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1285,
          "x1": 1294,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1296,
          "x1": 1300,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1302,
          "x1": 1318,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1319,
          "x1": 1328,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1336,
          "x1": 1348,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1350,
          "x1": 1360,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1362,
          "x1": 1372,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1378,
          "x1": 1390,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1393,
          "x1": 1402,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1403,
          "x1": 1411,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1412,
          "x1": 1415,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1417,
          "x1": 1427,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1429,
          "x1": 1434,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1435,
          "x1": 1448,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1449,
          "x1": 1459,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1460,
          "x1": 1473,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1474,
          "x1": 1485,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1486,
          "x1": 1491,
          "body_cut_fraction": 0.0,
          "body_pixels": 36,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1492,
          "x1": 1502,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1504,
          "x1": 1514,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1515,
          "x1": 1524,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1525,
          "x1": 1535,
          "body_cut_fraction": 0.0,
          "body_pixels": 54,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1536,
          "x1": 1548,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1550,
          "x1": 1554,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00088",
      "column_id": "single:column-0001",
      "xheight": 11.971254728320787,
      "assigned_pixels": 108,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 128,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.725418465320663,
        "required_common_rows": 2.392784667562182,
        "xheight_px": 11.963923337810911,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          849.323,
          1554,
          883.074
        ],
        "boundary_path": [
          [
            832.0,
            0.0
          ],
          [
            832.0,
            2339.0
          ]
        ],
        "row_id": "row-00087"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.732437590813712,
        "required_common_rows": 2.3942509456641576,
        "xheight_px": 11.971254728320787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          870,
          879.807,
          1554,
          910.592
        ],
        "boundary_path": [
          [
            832.0,
            0.0
          ],
          [
            832.0,
            2339.0
          ]
        ],
        "row_id": "row-00088"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.725418465320663,
        "required_common_rows": 2.392784667562182,
        "xheight_px": 11.963923337810911,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          849.323,
          1554,
          883.074
        ],
        "boundary_path": [
          [
            826.5,
            188.0
          ],
          [
            826.5,
            458.0
          ]
        ],
        "row_id": "row-00087"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.732437590813712,
        "required_common_rows": 2.3942509456641576,
        "xheight_px": 11.971254728320787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          870,
          879.807,
          1554,
          910.592
        ],
        "boundary_path": [
          [
            826.5,
            188.0
          ],
          [
            826.5,
            458.0
          ]
        ],
        "row_id": "row-00088"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.725418465320663,
        "required_common_rows": 2.392784667562182,
        "xheight_px": 11.963923337810911,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          849.323,
          1554,
          883.074
        ],
        "boundary_path": [
          [
            834.0,
            1312.0
          ],
          [
            834.0,
            1583.0
          ]
        ],
        "row_id": "row-00087"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.732437590813712,
        "required_common_rows": 2.3942509456641576,
        "xheight_px": 11.971254728320787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          870,
          879.807,
          1554,
          910.592
        ],
        "boundary_path": [
          [
            834.0,
            1312.0
          ],
          [
            834.0,
            1583.0
          ]
        ],
        "row_id": "row-00088"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.725418465320663,
        "required_common_rows": 2.392784667562182,
        "xheight_px": 11.963923337810911,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          849.323,
          1554,
          883.074
        ],
        "boundary_path": [
          [
            838.0,
            1760.0
          ],
          [
            838.0,
            2045.0
          ]
        ],
        "row_id": "row-00087"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.732437590813712,
        "required_common_rows": 2.3942509456641576,
        "xheight_px": 11.971254728320787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          870,
          879.807,
          1554,
          910.592
        ],
        "boundary_path": [
          [
            838.0,
            1760.0
          ],
          [
            838.0,
            2045.0
          ]
        ],
        "row_id": "row-00088"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.725418465320663,
        "required_common_rows": 2.392784667562182,
        "xheight_px": 11.963923337810911,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          875,
          849.323,
          1554,
          883.074
        ],
        "boundary_path": [
          [
            838.5,
            2045.0
          ],
          [
            838.5,
            2201.0
          ]
        ],
        "row_id": "row-00087"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.732437590813712,
        "required_common_rows": 2.3942509456641576,
        "xheight_px": 11.971254728320787,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          870,
          879.807,
          1554,
          910.592
        ],
        "boundary_path": [
          [
            838.5,
            2045.0
          ],
          [
            838.5,
            2201.0
          ]
        ],
        "row_id": "row-00088"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            832.0,
            0.0
          ],
          [
            832.0,
            2339.0
          ]
        ],
        "width": 30,
        "extent": [
          817,
          0,
          847,
          2339
        ],
        "source": "detector",
        "proposal_id": "proposal-0000",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 19.558161573542975,
          "width_xh": 1.5338864998733865,
          "required_width_px": 29.337242360314463,
          "spacing_sides": [
            {
              "samples": 444,
              "letter_q25_xh": 0.08382673588289082,
              "median_xh": 0.1609390902895883,
              "word_q75_xh": 0.1703491851077475,
              "q90_xh": 0.6077597646322168
            },
            {
              "samples": 427,
              "letter_q25_xh": 0.08353343260120157,
              "median_xh": 0.16666621975535942,
              "word_q75_xh": 0.2525666505614373,
              "q90_xh": 0.7550895053459095
            }
          ],
          "side_row_counts": [
            48,
            54
          ],
          "side_span_xh": [
            105.97885144807708,
            105.84363935311322
          ],
          "shared_span_xh": 105.79590991819215,
          "occupied_rows": 79,
          "bilateral_rows": 52,
          "participants": [
            {
              "line_index": 0,
              "xheight": 12.889729367310153
            },
            {
              "line_index": 1,
              "xheight": 11.976793819913098
            },
            {
              "line_index": 2,
              "xheight": 12.001448851666566
            },
            {
              "line_index": 3,
              "xheight": 11.971527658178019
            },
            {
              "line_index": 5,
              "xheight": 11.961893170900794
            },
            {
              "line_index": 6,
              "xheight": 11.731459754942989
            },
            {
              "line_index": 7,
              "xheight": 11.956120624987648
            },
            {
              "line_index": 9,
              "xheight": 11.88800892221309
            },
            {
              "line_index": 12,
              "xheight": 12.758679582458967
            },
            {
              "line_index": 13,
              "xheight": 11.126620104283802
            },
            {
              "line_index": 14,
              "xheight": 19.558161573542975
            },
            {
              "line_index": 15,
              "xheight": 11.864836810358952
            },
            {
              "line_index": 16,
              "xheight": 11.991524279872806
            },
            {
              "line_index": 17,
              "xheight": 12.000205848777796
            },
            {
              "line_index": 19,
              "xheight": 12.654268082429553
            },
            {
              "line_index": 21,
              "xheight": 11.972110214138524
            },
            {
              "line_index": 22,
              "xheight": 11.882325727885245
            },
            {
              "line_index": 24,
              "xheight": 11.948546253944755
            },
            {
              "line_index": 25,
              "xheight": 11.98766651342578
            },
            {
              "line_index": 26,
              "xheight": 11.892049894870297
            },
            {
              "line_index": 27,
              "xheight": 11.517708817456878
            },
            {
              "line_index": 28,
              "xheight": 11.599675645141815
            },
            {
              "line_index": 29,
              "xheight": 11.804225419086606
            },
            {
              "line_index": 31,
              "xheight": 11.753613458458176
            },
            {
              "line_index": 32,
              "xheight": 11.720141273012132
            },
            {
              "line_index": 33,
              "xheight": 10.997539039938147
            },
            {
              "line_index": 34,
              "xheight": 11.219977890776363
            },
            {
              "line_index": 35,
              "xheight": 11.857945632691553
            },
            {
              "line_index": 37,
              "xheight": 11.249854302485119
            },
            {
              "line_index": 38,
              "xheight": 11.69563392803525
            },
            {
              "line_index": 39,
              "xheight": 11.89912394505427
            },
            {
              "line_index": 40,
              "xheight": 11.929368231599028
            },
            {
              "line_index": 42,
              "xheight": 12.106751918233385
            },
            {
              "line_index": 43,
              "xheight": 13.476222992756902
            },
            {
              "line_index": 44,
              "xheight": 12.050607851071618
            },
            {
              "line_index": 46,
              "xheight": 12.427061669115119
            },
            {
              "line_index": 47,
              "xheight": 11.466057065671066
            },
            {
              "line_index": 48,
              "xheight": 11.99191550616706
            },
            {
              "line_index": 49,
              "xheight": 11.888897907683031
            },
            {
              "line_index": 50,
              "xheight": 11.74363705022688
            },
            {
              "line_index": 51,
              "xheight": 11.989167080186917
            },
            {
              "line_index": 52,
              "xheight": 11.2937473346135
            },
            {
              "line_index": 53,
              "xheight": 11.956283479581316
            },
            {
              "line_index": 54,
              "xheight": 11.964925363421571
            },
            {
              "line_index": 56,
              "xheight": 11.965015174484279
            },
            {
              "line_index": 57,
              "xheight": 12.001289507487627
            },
            {
              "line_index": 59,
              "xheight": 11.987455461765421
            },
            {
              "line_index": 61,
              "xheight": 12.001899000361846
            },
            {
              "line_index": 62,
              "xheight": 11.642472946097314
            },
            {
              "line_index": 64,
              "xheight": 12.042483182422075
            },
            {
              "line_index": 65,
              "xheight": 11.920198040270407
            },
            {
              "line_index": 66,
              "xheight": 13.242637359788105
            },
            {
              "line_index": 67,
              "xheight": 12.011673218344981
            },
            {
              "line_index": 68,
              "xheight": 11.996937399271673
            },
            {
              "line_index": 69,
              "xheight": 11.969100404407357
            },
            {
              "line_index": 70,
              "xheight": 12.05768914940245
            },
            {
              "line_index": 71,
              "xheight": 12.080847783965623
            },
            {
              "line_index": 72,
              "xheight": 11.99575084492642
            },
            {
              "line_index": 73,
              "xheight": 12.003628223178794
            },
            {
              "line_index": 74,
              "xheight": 11.781345761870568
            },
            {
              "line_index": 75,
              "xheight": 17.270494838130674
            },
            {
              "line_index": 76,
              "xheight": 14.461653179828545
            },
            {
              "line_index": 79,
              "xheight": 12.796419968353803
            },
            {
              "line_index": 80,
              "xheight": 11.333038880602885
            },
            {
              "line_index": 81,
              "xheight": 11.979448497544809
            },
            {
              "line_index": 82,
              "xheight": 12.17484617888067
            },
            {
              "line_index": 84,
              "xheight": 11.958085737056763
            },
            {
              "line_index": 85,
              "xheight": 11.999331453255309
            },
            {
              "line_index": 86,
              "xheight": 11.963923337810911
            },
            {
              "line_index": 87,
              "xheight": 11.971254728320787
            },
            {
              "line_index": 88,
              "xheight": 12.0
            },
            {
              "line_index": 89,
              "xheight": 11.711357172726935
            },
            {
              "line_index": 90,
              "xheight": 11.991576048076695
            },
            {
              "line_index": 91,
              "xheight": 11.815497648534006
            },
            {
              "line_index": 92,
              "xheight": 11.688466787465586
            },
            {
              "line_index": 93,
              "xheight": 11.27967421260496
            },
            {
              "line_index": 94,
              "xheight": 11.615870006020032
            },
            {
              "line_index": 95,
              "xheight": 11.99850081931254
            },
            {
              "line_index": 96,
              "xheight": 11.981447591938377
            },
            {
              "line_index": 97,
              "xheight": 11.95503476190288
            },
            {
              "line_index": 98,
              "xheight": 11.04376224966768
            },
            {
              "line_index": 99,
              "xheight": 11.348673229446604
            },
            {
              "line_index": 100,
              "xheight": 11.780350145826787
            },
            {
              "line_index": 101,
              "xheight": 11.827436097777309
            },
            {
              "line_index": 102,
              "xheight": 12.20007163869866
            },
            {
              "line_index": 103,
              "xheight": 11.866317387425624
            },
            {
              "line_index": 104,
              "xheight": 11.989917603453023
            },
            {
              "line_index": 105,
              "xheight": 11.889811361067814
            },
            {
              "line_index": 106,
              "xheight": 11.919116788515112
            },
            {
              "line_index": 107,
              "xheight": 12.008205932222381
            },
            {
              "line_index": 108,
              "xheight": 11.97569961526142
            },
            {
              "line_index": 109,
              "xheight": 15.676728070184595
            },
            {
              "line_index": 114,
              "xheight": 12.702709919803738
            },
            {
              "line_index": 116,
              "xheight": 11.953891669593759
            },
            {
              "line_index": 117,
              "xheight": 11.994203243780476
            },
            {
              "line_index": 118,
              "xheight": 12.025239058182251
            },
            {
              "line_index": 119,
              "xheight": 12.000032177700405
            },
            {
              "line_index": 121,
              "xheight": 11.94477747802739
            },
            {
              "line_index": 122,
              "xheight": 12.051387899677593
            },
            {
              "line_index": 123,
              "xheight": 12.010229834112806
            },
            {
              "line_index": 124,
              "xheight": 12.016816784127059
            },
            {
              "line_index": 125,
              "xheight": 11.981349698465692
            },
            {
              "line_index": 126,
              "xheight": 11.934926323337095
            },
            {
              "line_index": 127,
              "xheight": 12.030274619690772
            },
            {
              "line_index": 128,
              "xheight": 11.999777878576424
            },
            {
              "line_index": 129,
              "xheight": 12.01059546771421
            }
          ],
          "observed_gap_widths_px": [
            43,
            38,
            38,
            63,
            0.0,
            38,
            38,
            39,
            0.0,
            94,
            0.0,
            0.0,
            233,
            0.0,
            0.0,
            0.0,
            36,
            36,
            44,
            44,
            0.0,
            158,
            64,
            64,
            35,
            35,
            0.0,
            0.0,
            35,
            35,
            0.0,
            66,
            66,
            35,
            35,
            35,
            35,
            63,
            63,
            0.0,
            34,
            34,
            63,
            63,
            34,
            34,
            35,
            35,
            63,
            0.0,
            36,
            36,
            62,
            34,
            34,
            0.0,
            34,
            0.0,
            183,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            36,
            38,
            70,
            69,
            70,
            0.0,
            93,
            0.0,
            38,
            0.0,
            66,
            42,
            0.0,
            41,
            42
          ],
          "white_rows": 55,
          "baseline_matching_reach_px": 14.04600000000005,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            826.5,
            188.0
          ],
          [
            826.5,
            458.0
          ]
        ],
        "width": 31,
        "extent": [
          811,
          188,
          842,
          458
        ],
        "source": "detector",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 31.0,
          "local_xheight_max_px": 17.270494838130674,
          "width_xh": 1.7949688350305186,
          "required_width_px": 25.90574225719601,
          "spacing_sides": [
            {
              "samples": 54,
              "letter_q25_xh": 0.08360889772611663,
              "median_xh": 0.16664654615615618,
              "word_q75_xh": 0.16823675125806326,
              "q90_xh": 0.6691133563239928
            },
            {
              "samples": 69,
              "letter_q25_xh": 0.08336285180705867,
              "median_xh": 0.11580444096971088,
              "word_q75_xh": 0.16672570361411734,
              "q90_xh": 0.6419805765757534
            }
          ],
          "side_row_counts": [
            6,
            9
          ],
          "side_span_xh": [
            11.415249061927796,
            13.377786923041487
          ],
          "shared_span_xh": 11.415249061927796,
          "occupied_rows": 9,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 2,
              "xheight": 12.001448851666566
            },
            {
              "line_index": 3,
              "xheight": 11.971527658178019
            },
            {
              "line_index": 5,
              "xheight": 11.961893170900794
            },
            {
              "line_index": 6,
              "xheight": 11.731459754942989
            },
            {
              "line_index": 7,
              "xheight": 11.956120624987648
            },
            {
              "line_index": 9,
              "xheight": 11.88800892221309
            },
            {
              "line_index": 68,
              "xheight": 11.996937399271673
            },
            {
              "line_index": 69,
              "xheight": 11.969100404407357
            },
            {
              "line_index": 70,
              "xheight": 12.05768914940245
            },
            {
              "line_index": 71,
              "xheight": 12.080847783965623
            },
            {
              "line_index": 72,
              "xheight": 11.99575084492642
            },
            {
              "line_index": 73,
              "xheight": 12.003628223178794
            },
            {
              "line_index": 74,
              "xheight": 11.781345761870568
            },
            {
              "line_index": 75,
              "xheight": 17.270494838130674
            },
            {
              "line_index": 76,
              "xheight": 14.461653179828545
            }
          ],
          "observed_gap_widths_px": [
            38,
            63,
            0.0,
            38,
            38,
            39,
            0.0,
            94,
            0.0
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 14.207625000000007,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            834.0,
            1312.0
          ],
          [
            834.0,
            1583.0
          ]
        ],
        "width": 30,
        "extent": [
          819,
          1312,
          849,
          1583
        ],
        "source": "detector",
        "proposal_id": "proposal-0004",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 15.676728070184595,
          "width_xh": 1.9136646285940677,
          "required_width_px": 23.515092105276892,
          "spacing_sides": [
            {
              "samples": 58,
              "letter_q25_xh": 0.08382673588289082,
              "median_xh": 0.16519707461651198,
              "word_q75_xh": 0.17100398424799024,
              "q90_xh": 0.5042388017559754
            },
            {
              "samples": 68,
              "letter_q25_xh": 0.08340340885345252,
              "median_xh": 0.16667979548808182,
              "word_q75_xh": 0.5219170872322514,
              "q90_xh": 0.7813790838149588
            }
          ],
          "side_row_counts": [
            6,
            8
          ],
          "side_span_xh": [
            14.952514258751167,
            13.055721773299204
          ],
          "shared_span_xh": 12.54391216838172,
          "occupied_rows": 10,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 37,
              "xheight": 11.249854302485119
            },
            {
              "line_index": 38,
              "xheight": 11.69563392803525
            },
            {
              "line_index": 39,
              "xheight": 11.89912394505427
            },
            {
              "line_index": 40,
              "xheight": 11.929368231599028
            },
            {
              "line_index": 42,
              "xheight": 12.106751918233385
            },
            {
              "line_index": 43,
              "xheight": 13.476222992756902
            },
            {
              "line_index": 44,
              "xheight": 12.050607851071618
            },
            {
              "line_index": 102,
              "xheight": 12.20007163869866
            },
            {
              "line_index": 103,
              "xheight": 11.866317387425624
            },
            {
              "line_index": 104,
              "xheight": 11.989917603453023
            },
            {
              "line_index": 105,
              "xheight": 11.889811361067814
            },
            {
              "line_index": 106,
              "xheight": 11.919116788515112
            },
            {
              "line_index": 107,
              "xheight": 12.008205932222381
            },
            {
              "line_index": 108,
              "xheight": 11.97569961526142
            },
            {
              "line_index": 109,
              "xheight": 15.676728070184595
            }
          ],
          "observed_gap_widths_px": [
            36,
            36,
            62,
            34,
            34,
            0.0,
            34,
            0.0,
            183,
            0.0
          ],
          "white_rows": 7,
          "baseline_matching_reach_px": 14.222999999999956,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0002",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            838.0,
            1760.0
          ],
          [
            838.0,
            2045.0
          ]
        ],
        "width": 32,
        "extent": [
          822,
          1760,
          854,
          2045
        ],
        "source": "detector",
        "proposal_id": "proposal-0007",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 32.0,
          "local_xheight_max_px": 12.051387899677593,
          "width_xh": 2.6552958270354976,
          "required_width_px": 18.07708184951639,
          "spacing_sides": [
            {
              "samples": 65,
              "letter_q25_xh": 0.08357699387899878,
              "median_xh": 0.16664875876481408,
              "word_q75_xh": 0.16727606060993427,
              "q90_xh": 0.5624693611018
            },
            {
              "samples": 64,
              "letter_q25_xh": 0.08326235332813428,
              "median_xh": 0.08371859600059658,
              "word_q75_xh": 0.1673095302584391,
              "q90_xh": 0.6389305583804168
            }
          ],
          "side_row_counts": [
            7,
            8
          ],
          "side_span_xh": [
            18.981174774576775,
            20.91082803888022
          ],
          "shared_span_xh": 18.491646095464404,
          "occupied_rows": 9,
          "bilateral_rows": 6,
          "participants": [
            {
              "line_index": 51,
              "xheight": 11.989167080186917
            },
            {
              "line_index": 52,
              "xheight": 11.2937473346135
            },
            {
              "line_index": 53,
              "xheight": 11.956283479581316
            },
            {
              "line_index": 54,
              "xheight": 11.964925363421571
            },
            {
              "line_index": 56,
              "xheight": 11.965015174484279
            },
            {
              "line_index": 57,
              "xheight": 12.001289507487627
            },
            {
              "line_index": 59,
              "xheight": 11.987455461765421
            },
            {
              "line_index": 116,
              "xheight": 11.953891669593759
            },
            {
              "line_index": 117,
              "xheight": 11.994203243780476
            },
            {
              "line_index": 118,
              "xheight": 12.025239058182251
            },
            {
              "line_index": 119,
              "xheight": 12.000032177700405
            },
            {
              "line_index": 121,
              "xheight": 11.94477747802739
            },
            {
              "line_index": 122,
              "xheight": 12.051387899677593
            },
            {
              "line_index": 123,
              "xheight": 12.010229834112806
            },
            {
              "line_index": 124,
              "xheight": 12.016816784127059
            }
          ],
          "observed_gap_widths_px": [
            38,
            70,
            69,
            70,
            0.0,
            93,
            0.0,
            38,
            0.0
          ],
          "white_rows": 6,
          "baseline_matching_reach_px": 13.964374999999961,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0003",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            838.5,
            2045.0
          ],
          [
            838.5,
            2201.0
          ]
        ],
        "width": 31,
        "extent": [
          823,
          2045,
          854,
          2201
        ],
        "source": "detector",
        "proposal_id": "proposal-0008",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 31.0,
          "local_xheight_max_px": 12.042483182422075,
          "width_xh": 2.5742199121564435,
          "required_width_px": 18.063724773633112,
          "spacing_sides": [
            {
              "samples": 36,
              "letter_q25_xh": 0.08332014791741299,
              "median_xh": 0.08589240487221497,
              "word_q75_xh": 0.16778244734217776,
              "q90_xh": 0.41690050335731743
            },
            {
              "samples": 43,
              "letter_q25_xh": 0.08333487587177185,
              "median_xh": 0.16624724399278995,
              "word_q75_xh": 0.37558372915000227,
              "q90_xh": 0.5860593789499816
            }
          ],
          "side_row_counts": [
            4,
            5
          ],
          "side_span_xh": [
            9.51946523515456,
            9.171447310901387
          ],
          "shared_span_xh": 9.171447310901387,
          "occupied_rows": 5,
          "bilateral_rows": 4,
          "participants": [
            {
              "line_index": 61,
              "xheight": 12.001899000361846
            },
            {
              "line_index": 62,
              "xheight": 11.642472946097314
            },
            {
              "line_index": 64,
              "xheight": 12.042483182422075
            },
            {
              "line_index": 65,
              "xheight": 11.920198040270407
            },
            {
              "line_index": 125,
              "xheight": 11.981349698465692
            },
            {
              "line_index": 126,
              "xheight": 11.934926323337095
            },
            {
              "line_index": 127,
              "xheight": 12.030274619690772
            },
            {
              "line_index": 128,
              "xheight": 11.999777878576424
            },
            {
              "line_index": 129,
              "xheight": 12.01059546771421
            }
          ],
          "observed_gap_widths_px": [
            66,
            42,
            0.0,
            41,
            42
          ],
          "white_rows": 4,
          "baseline_matching_reach_px": 13.905874999999924,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0004",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "fc8cb85ad5e84b010f5c7d726e3f5a9cc3e91b6993adeb075fe89b42ea5ca69c"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.9689555557211397,
    "polarity_confidence": 0.7142857142857143,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## bsb_poly1850--9342f9a56a4065cd--s004-l0005

Card `ke4d0646b2d`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/a65bbebe910032fbdeba31ee6abcb328c7e129cbd04eea562aa60b02410e2357.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/a65bbebe910032fbdeba31ee6abcb328c7e129cbd04eea562aa60b02410e2357.png`; SHA-256 `a65bbebe910032fbdeba31ee6abcb328c7e129cbd04eea562aa60b02410e2357`.

Triggers: {"mismatches": {"union": "FN", "merged": "FN", "neighbour_words": "FN", "orientation": "FN", "geometry_unavailable": "FN", "crossing": "FN"}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "ke4d0646b2d",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_clipped"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "yes",
  "horizontally_missegmented_reason": "The right boundary cuts the final letter of the line.",
  "line_id": "bsb_poly1850--9342f9a56a4065cd--s004-l0005"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00003",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      169,
      255,
      1177,
      307
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00003"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00003"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00003",
      "column_id": "single:column-0000",
      "xheight": 19.466244901065522,
      "assigned_pixels": 10380,
      "supported": null,
      "runs": [
        {
          "x0": 172,
          "x1": 190,
          "body_cut_fraction": 0.0,
          "body_pixels": 199,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 191,
          "x1": 212,
          "body_cut_fraction": 0.0,
          "body_pixels": 259,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 214,
          "x1": 230,
          "body_cut_fraction": 0.0,
          "body_pixels": 162,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 244,
          "x1": 264,
          "body_cut_fraction": 0.0,
          "body_pixels": 252,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 266,
          "x1": 285,
          "body_cut_fraction": 0.0,
          "body_pixels": 242,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 290,
          "x1": 305,
          "body_cut_fraction": 0.0,
          "body_pixels": 162,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 307,
          "x1": 327,
          "body_cut_fraction": 0.0,
          "body_pixels": 232,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 329,
          "x1": 345,
          "body_cut_fraction": 0.0,
          "body_pixels": 163,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 364,
          "x1": 385,
          "body_cut_fraction": 0.0,
          "body_pixels": 264,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 387,
          "x1": 401,
          "body_cut_fraction": 0.0,
          "body_pixels": 165,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 406,
          "x1": 416,
          "body_cut_fraction": 0.0,
          "body_pixels": 124,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 432,
          "x1": 452,
          "body_cut_fraction": 0.0,
          "body_pixels": 207,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 455,
          "x1": 473,
          "body_cut_fraction": 0.0,
          "body_pixels": 210,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 475,
          "x1": 500,
          "body_cut_fraction": 0.0,
          "body_pixels": 302,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 504,
          "x1": 528,
          "body_cut_fraction": 0.0,
          "body_pixels": 292,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 532,
          "x1": 552,
          "body_cut_fraction": 0.0,
          "body_pixels": 218,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 566,
          "x1": 585,
          "body_cut_fraction": 0.0,
          "body_pixels": 233,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 587,
          "x1": 607,
          "body_cut_fraction": 0.0,
          "body_pixels": 251,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 611,
          "x1": 621,
          "body_cut_fraction": 0.0,
          "body_pixels": 130,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 635,
          "x1": 655,
          "body_cut_fraction": 0.0,
          "body_pixels": 249,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 657,
          "x1": 681,
          "body_cut_fraction": 0.0,
          "body_pixels": 268,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 682,
          "x1": 699,
          "body_cut_fraction": 0.0,
          "body_pixels": 201,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 702,
          "x1": 723,
          "body_cut_fraction": 0.0,
          "body_pixels": 224,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 725,
          "x1": 742,
          "body_cut_fraction": 0.0,
          "body_pixels": 221,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 746,
          "x1": 766,
          "body_cut_fraction": 0.0,
          "body_pixels": 213,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 768,
          "x1": 782,
          "body_cut_fraction": 0.0,
          "body_pixels": 146,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 785,
          "x1": 810,
          "body_cut_fraction": 0.0,
          "body_pixels": 331,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 813,
          "x1": 834,
          "body_cut_fraction": 0.0,
          "body_pixels": 222,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 846,
          "x1": 863,
          "body_cut_fraction": 0.0,
          "body_pixels": 186,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 865,
          "x1": 882,
          "body_cut_fraction": 0.0,
          "body_pixels": 196,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 885,
          "x1": 905,
          "body_cut_fraction": 0.0,
          "body_pixels": 203,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 924,
          "x1": 944,
          "body_cut_fraction": 0.0,
          "body_pixels": 236,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 947,
          "x1": 967,
          "body_cut_fraction": 0.0,
          "body_pixels": 214,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 969,
          "x1": 988,
          "body_cut_fraction": 0.0,
          "body_pixels": 214,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 992,
          "x1": 1008,
          "body_cut_fraction": 0.0,
          "body_pixels": 148,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1009,
          "x1": 1029,
          "body_cut_fraction": 0.0,
          "body_pixels": 222,
          "body_extent_px": 20,
          "complete": true
        },
        {
          "x0": 1032,
          "x1": 1050,
          "body_cut_fraction": 0.0,
          "body_pixels": 215,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1053,
          "x1": 1071,
          "body_cut_fraction": 0.0,
          "body_pixels": 206,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1074,
          "x1": 1091,
          "body_cut_fraction": 0.0,
          "body_pixels": 164,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1092,
          "x1": 1112,
          "body_cut_fraction": 0.0,
          "body_pixels": 230,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1115,
          "x1": 1133,
          "body_cut_fraction": 0.0,
          "body_pixels": 182,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1134,
          "x1": 1151,
          "body_cut_fraction": 0.0,
          "body_pixels": 205,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1155,
          "x1": 1166,
          "body_cut_fraction": 0.0,
          "body_pixels": 104,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1168,
          "x1": 1175,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 6,
          "complete": false
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 32,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "validated": [],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            1242.3886713594611,
            7
          ],
          [
            1233.1484875488939,
            1974
          ]
        ],
        "radius": 2.0,
        "source": "continued_rule",
        "proposal_id": "proposal-0001",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": true,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 19.827773597061082,
          "support_fraction": 0.17083333333333334,
          "supported_rows": 156,
          "thin_support_fraction": 0.9512195121951219,
          "original_ink_rows": 164,
          "sampled_rows": 1968,
          "extent_xh": 48.416933716768554,
          "thickness_q90_xh": 0.05043430595496724,
          "residual_q90_xh": 0.10028037238497783,
          "dash_lengths_xh": [
            1.0086861190993448,
            0.6556459774145742,
            0.05043430595496724,
            0.2521715297748362,
            2.2191094620185585,
            0.10086861190993449,
            0.40347444763973794,
            1.210423342919214,
            0.45390875359470517,
            0.45390875359470517,
            1.059120425054312,
            0.3026058357298035,
            0.10086861190993449
          ],
          "gap_lengths_xh": [
            0.10086861190993449,
            5.144299207406659,
            13.818999831661024,
            19.16503626288755,
            0.10086861190993449,
            0.20173722381986897,
            0.10086861190993449,
            0.3530401416847707,
            0.10086861190993449,
            0.3530401416847707,
            0.15130291786490174,
            0.5547773655046396
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1239.7327290475107,
            0.0
          ],
          [
            1236.7045200348696,
            1975.0
          ]
        ],
        "id": "boundary-0000",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "no_long_unprinted_gap"
        ]
      }
    ],
    "inventory_sha256": "7633da8c70c73da247bed15fb604d91c77f2f029f4d512514b4cfc41dd96c7b0"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 1.0,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## nlg--3d71f4f87abea186--s027-l0004

Card `k0cb24c0490`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/893df4382bb251b851f87ad9a79b53336f414436cef2d9db4ce34f02e61ab4fb.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/893df4382bb251b851f87ad9a79b53336f414436cef2d9db4ce34f02e61ab4fb.png`; SHA-256 `893df4382bb251b851f87ad9a79b53336f414436cef2d9db4ce34f02e61ab4fb`.

Triggers: {"mismatches": {"union": "FP", "geometry_unavailable": "FP"}, "flag": false, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k0cb24c0490",
  "letters": "y",
  "marks": "y",
  "crop_ok": "y",
  "errors": [],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "nlg--3d71f4f87abea186--s027-l0004"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": null,
  "neighbour_words": null,
  "orientation": null,
  "orientation_unknown": true,
  "geometry_unavailable": true,
  "screen_drop": true,
  "composed": {
    "measured_drop": null,
    "geometry_unavailable": true,
    "drop": true,
    "orientation_status": "orientation_unknown",
    "verified_keep": false,
    "crossing_status": "unavailable"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "unavailable",
  "structural_reason": "invalid_source_frame_or_labels",
  "target_row_id": null,
  "neighbour_rows": [],
  "row_inclusion": {},
  "row_inclusion_rows": [],
  "omitted_zero_ink_rows": 0,
  "crossing": {
    "status": "unavailable",
    "drop": null,
    "reason": "geometry_unavailable"
  },
  "axis": {
    "status": "orientation_unknown",
    "reason": "line_block_disagreement",
    "decision_source": "unknown",
    "source": "native_crop_toolkit",
    "axis": "unknown",
    "orientation_cw": null,
    "axis_confidence": 0.006045283374874261,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--b7f412819cdbb91a--s000-l0097

Card `k35bf7bb3fa`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/de5023a8ffc46865d415fd2b4c16e5c08e77994679dd85e3bcfe0db1ed4e5696.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/de5023a8ffc46865d415fd2b4c16e5c08e77994679dd85e3bcfe0db1ed4e5696.png`; SHA-256 `de5023a8ffc46865d415fd2b4c16e5c08e77994679dd85e3bcfe0db1ed4e5696`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k35bf7bb3fa",
  "letters": "n",
  "marks": "y",
  "crop_ok": "y",
  "errors": [
    "hyphen"
  ],
  "detail": "καθη- → καθη",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--b7f412819cdbb91a--s000-l0097"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00098",
  "neighbour_rows": [
    {
      "row_id": "row-00096",
      "column_id": "single:column-0000",
      "xheight": 13.041164813436126,
      "profile_runs": [
        [
          875,
          883
        ],
        [
          887,
          894
        ],
        [
          902,
          913
        ],
        [
          916,
          927
        ],
        [
          930,
          942
        ],
        [
          944,
          952
        ],
        [
          955,
          967
        ],
        [
          968,
          981
        ],
        [
          984,
          995
        ],
        [
          998,
          1008
        ],
        [
          1011,
          1020
        ],
        [
          1024,
          1028
        ],
        [
          1031,
          1039
        ],
        [
          1042,
          1051
        ],
        [
          1064,
          1074
        ],
        [
          1077,
          1085
        ],
        [
          1088,
          1098
        ],
        [
          1110,
          1128
        ],
        [
          1129,
          1139
        ],
        [
          1142,
          1152
        ],
        [
          1154,
          1166
        ],
        [
          1168,
          1180
        ],
        [
          1183,
          1191
        ],
        [
          1194,
          1207
        ],
        [
          1209,
          1217
        ],
        [
          1220,
          1229
        ],
        [
          1240,
          1251
        ],
        [
          1254,
          1263
        ],
        [
          1276,
          1285
        ],
        [
          1288,
          1297
        ],
        [
          1300,
          1313
        ],
        [
          1315,
          1326
        ],
        [
          1328,
          1337
        ],
        [
          1341,
          1346
        ],
        [
          1348,
          1361
        ],
        [
          1362,
          1375
        ],
        [
          1386,
          1401
        ],
        [
          1404,
          1425
        ],
        [
          1427,
          1439
        ],
        [
          1451,
          1468
        ],
        [
          1471,
          1475
        ],
        [
          1480,
          1487
        ],
        [
          1491,
          1501
        ],
        [
          1505,
          1517
        ],
        [
          1520,
          1529
        ],
        [
          1534,
          1538
        ],
        [
          1540,
          1553
        ],
        [
          1556,
          1564
        ],
        [
          1566,
          1576
        ]
      ],
      "profile_gaps": [
        [
          883,
          887
        ],
        [
          894,
          902
        ],
        [
          913,
          916
        ],
        [
          927,
          930
        ],
        [
          942,
          944
        ],
        [
          952,
          955
        ],
        [
          967,
          968
        ],
        [
          981,
          984
        ],
        [
          995,
          998
        ],
        [
          1008,
          1011
        ],
        [
          1020,
          1024
        ],
        [
          1028,
          1031
        ],
        [
          1039,
          1042
        ],
        [
          1051,
          1064
        ],
        [
          1074,
          1077
        ],
        [
          1085,
          1088
        ],
        [
          1098,
          1110
        ],
        [
          1128,
          1129
        ],
        [
          1139,
          1142
        ],
        [
          1152,
          1154
        ],
        [
          1166,
          1168
        ],
        [
          1180,
          1183
        ],
        [
          1191,
          1194
        ],
        [
          1207,
          1209
        ],
        [
          1217,
          1220
        ],
        [
          1229,
          1240
        ],
        [
          1251,
          1254
        ],
        [
          1263,
          1276
        ],
        [
          1285,
          1288
        ],
        [
          1297,
          1300
        ],
        [
          1313,
          1315
        ],
        [
          1326,
          1328
        ],
        [
          1337,
          1341
        ],
        [
          1346,
          1348
        ],
        [
          1361,
          1362
        ],
        [
          1375,
          1386
        ],
        [
          1401,
          1404
        ],
        [
          1425,
          1427
        ],
        [
          1439,
          1451
        ],
        [
          1468,
          1471
        ],
        [
          1475,
          1480
        ],
        [
          1487,
          1491
        ],
        [
          1501,
          1505
        ],
        [
          1517,
          1520
        ],
        [
          1529,
          1534
        ],
        [
          1538,
          1540
        ],
        [
          1553,
          1556
        ],
        [
          1564,
          1566
        ]
      ],
      "directional_missing": {
        "above": 18895,
        "below": 0
      },
      "groups": [
        {
          "box": [
            874,
            1541,
            895,
            1564
          ],
          "body_count": 1,
          "width_xh": 1.6102856071847202,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            902,
            1549,
            1051,
            1568
          ],
          "body_count": 12,
          "width_xh": 11.425359784310634,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1064,
            1541,
            1229,
            1568
          ],
          "body_count": 12,
          "width_xh": 12.652244056451373,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1276,
            1547,
            1375,
            1567
          ],
          "body_count": 8,
          "width_xh": 7.591346433870823,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1386,
            1541,
            1439,
            1566
          ],
          "body_count": 3,
          "width_xh": 4.064054151466198,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00099",
      "column_id": "single:column-0000",
      "xheight": 13.167375322678936,
      "profile_runs": [
        [
          871,
          883
        ],
        [
          886,
          897
        ],
        [
          901,
          910
        ],
        [
          914,
          924
        ],
        [
          927,
          931
        ],
        [
          945,
          958
        ],
        [
          960,
          968
        ],
        [
          983,
          996
        ],
        [
          1001,
          1011
        ],
        [
          1013,
          1024
        ],
        [
          1027,
          1035
        ],
        [
          1039,
          1043
        ],
        [
          1047,
          1059
        ],
        [
          1074,
          1083
        ],
        [
          1086,
          1095
        ],
        [
          1097,
          1106
        ],
        [
          1121,
          1122
        ],
        [
          1125,
          1133
        ],
        [
          1137,
          1140
        ],
        [
          1141,
          1163
        ],
        [
          1166,
          1175
        ],
        [
          1178,
          1190
        ],
        [
          1204,
          1205
        ],
        [
          1206,
          1211
        ],
        [
          1217,
          1229
        ],
        [
          1232,
          1247
        ],
        [
          1251,
          1261
        ],
        [
          1264,
          1273
        ],
        [
          1275,
          1285
        ],
        [
          1288,
          1293
        ],
        [
          1296,
          1308
        ],
        [
          1311,
          1322
        ],
        [
          1325,
          1335
        ],
        [
          1350,
          1360
        ],
        [
          1363,
          1373
        ],
        [
          1374,
          1383
        ],
        [
          1397,
          1399
        ],
        [
          1401,
          1410
        ],
        [
          1413,
          1429
        ],
        [
          1431,
          1442
        ],
        [
          1443,
          1457
        ],
        [
          1460,
          1471
        ],
        [
          1474,
          1483
        ],
        [
          1486,
          1495
        ],
        [
          1498,
          1508
        ],
        [
          1522,
          1530
        ],
        [
          1536,
          1539
        ],
        [
          1541,
          1550
        ],
        [
          1552,
          1577
        ]
      ],
      "profile_gaps": [
        [
          883,
          886
        ],
        [
          897,
          901
        ],
        [
          910,
          914
        ],
        [
          924,
          927
        ],
        [
          931,
          945
        ],
        [
          958,
          960
        ],
        [
          968,
          983
        ],
        [
          996,
          1001
        ],
        [
          1011,
          1013
        ],
        [
          1024,
          1027
        ],
        [
          1035,
          1039
        ],
        [
          1043,
          1047
        ],
        [
          1059,
          1074
        ],
        [
          1083,
          1086
        ],
        [
          1095,
          1097
        ],
        [
          1106,
          1121
        ],
        [
          1122,
          1125
        ],
        [
          1133,
          1137
        ],
        [
          1140,
          1141
        ],
        [
          1163,
          1166
        ],
        [
          1175,
          1178
        ],
        [
          1190,
          1204
        ],
        [
          1205,
          1206
        ],
        [
          1211,
          1217
        ],
        [
          1229,
          1232
        ],
        [
          1247,
          1251
        ],
        [
          1261,
          1264
        ],
        [
          1273,
          1275
        ],
        [
          1285,
          1288
        ],
        [
          1293,
          1296
        ],
        [
          1308,
          1311
        ],
        [
          1322,
          1325
        ],
        [
          1335,
          1350
        ],
        [
          1360,
          1363
        ],
        [
          1373,
          1374
        ],
        [
          1383,
          1397
        ],
        [
          1399,
          1401
        ],
        [
          1410,
          1413
        ],
        [
          1429,
          1431
        ],
        [
          1442,
          1443
        ],
        [
          1457,
          1460
        ],
        [
          1471,
          1474
        ],
        [
          1483,
          1486
        ],
        [
          1495,
          1498
        ],
        [
          1508,
          1522
        ],
        [
          1530,
          1536
        ],
        [
          1539,
          1541
        ],
        [
          1550,
          1552
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 23198
      },
      "groups": [
        {
          "box": [
            1120,
            1602,
            1220,
            1628
          ],
          "body_count": 6,
          "width_xh": 7.594527956362282,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1396,
            1600,
            1508,
            1627
          ],
          "body_count": 7,
          "width_xh": 8.505871311125755,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1522,
            1601,
            1577,
            1623
          ],
          "body_count": 3,
          "width_xh": 4.176990375999255,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      863,
      1563,
      1577,
      1603
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00098"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00098"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00096",
      "column_id": "single:column-0000",
      "xheight": 13.041164813436126,
      "assigned_pixels": 149,
      "supported": null,
      "runs": [
        {
          "x0": 955,
          "x1": 967,
          "body_cut_fraction": 0.9791172768111046,
          "body_pixels": 2,
          "body_extent_px": 1,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00098",
      "column_id": "single:column-0000",
      "xheight": 12.836570462641248,
      "assigned_pixels": 3611,
      "supported": null,
      "runs": [
        {
          "x0": 872,
          "x1": 887,
          "body_cut_fraction": 0.0,
          "body_pixels": 73,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 890,
          "x1": 899,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 903,
          "x1": 910,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 914,
          "x1": 922,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 924,
          "x1": 932,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 936,
          "x1": 947,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 950,
          "x1": 960,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 964,
          "x1": 967,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 970,
          "x1": 984,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 985,
          "x1": 993,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 996,
          "x1": 1005,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1024,
          "x1": 1030,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1037,
          "x1": 1043,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1051,
          "x1": 1059,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1062,
          "x1": 1071,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1074,
          "x1": 1084,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1086,
          "x1": 1101,
          "body_cut_fraction": 0.0,
          "body_pixels": 87,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1104,
          "x1": 1116,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1119,
          "x1": 1123,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1126,
          "x1": 1138,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1141,
          "x1": 1149,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1151,
          "x1": 1160,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1163,
          "x1": 1167,
          "body_cut_fraction": 0.0,
          "body_pixels": 14,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 1182,
          "x1": 1193,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1195,
          "x1": 1204,
          "body_cut_fraction": 0.0,
          "body_pixels": 53,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1207,
          "x1": 1219,
          "body_cut_fraction": 0.0,
          "body_pixels": 85,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1233,
          "x1": 1243,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1247,
          "x1": 1258,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1259,
          "x1": 1273,
          "body_cut_fraction": 0.0,
          "body_pixels": 79,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1275,
          "x1": 1289,
          "body_cut_fraction": 0.0,
          "body_pixels": 79,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1291,
          "x1": 1298,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1312,
          "x1": 1323,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1339,
          "x1": 1348,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1351,
          "x1": 1359,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1362,
          "x1": 1371,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1385,
          "x1": 1386,
          "body_cut_fraction": 0.0,
          "body_pixels": 2,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1387,
          "x1": 1416,
          "body_cut_fraction": 0.0,
          "body_pixels": 183,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1418,
          "x1": 1423,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1425,
          "x1": 1438,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1440,
          "x1": 1459,
          "body_cut_fraction": 0.0,
          "body_pixels": 123,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1463,
          "x1": 1471,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1474,
          "x1": 1482,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1485,
          "x1": 1494,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1509,
          "x1": 1521,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1525,
          "x1": 1536,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1539,
          "x1": 1552,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1555,
          "x1": 1567,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 1568,
          "x1": 1576,
          "body_cut_fraction": 0.0,
          "body_pixels": 21,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00099",
      "column_id": "single:column-0000",
      "xheight": 13.167375322678936,
      "assigned_pixels": 132,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 117,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.80287918764818,
        "required_common_rows": 2.608232962687225,
        "xheight_px": 13.041164813436126,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          874,
          1536.25,
          1576,
          1575.363
        ],
        "boundary_path": [
          [
            848.5,
            1737.0
          ],
          [
            848.5,
            2026.0
          ]
        ],
        "row_id": "row-00096"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.59110164969415,
        "required_common_rows": 2.5673140925282496,
        "xheight_px": 12.836570462641248,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 0.0,
          "threshold": 127.5
        },
        "line_extent": [
          871,
          1566.481,
          1576,
          1600.81
        ],
        "boundary_path": [
          [
            848.5,
            1737.0
          ],
          [
            848.5,
            2026.0
          ]
        ],
        "row_id": "row-00098"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.935190915531769,
        "required_common_rows": 2.633475064535787,
        "xheight_px": 13.167375322678936,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 255.0,
          "ink_q10": 255.0,
          "threshold": 255.0
        },
        "line_extent": [
          871,
          1596.502,
          1577,
          1630.845
        ],
        "boundary_path": [
          [
            848.5,
            1737.0
          ],
          [
            848.5,
            2026.0
          ]
        ],
        "row_id": "row-00099"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            848.5,
            1737.0
          ],
          [
            848.5,
            2026.0
          ]
        ],
        "width": 39,
        "extent": [
          829,
          1737,
          868,
          2026
        ],
        "source": "detector",
        "proposal_id": "proposal-0004",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 39.0,
          "local_xheight_max_px": 13.858776950971333,
          "width_xh": 2.814101138792523,
          "required_width_px": 24.328362188081385,
          "spacing_sides": [
            {
              "samples": 87,
              "letter_q25_xh": 0.15133579859285598,
              "median_xh": 0.22657622775581202,
              "word_q75_xh": 0.30238661709673065,
              "q90_xh": 1.1702986621955007
            },
            {
              "samples": 71,
              "letter_q25_xh": 0.22757346415601243,
              "median_xh": 0.30553660164384616,
              "word_q75_xh": 0.38596860162946656,
              "q90_xh": 1.1617593810899494
            }
          ],
          "side_row_counts": [
            9,
            9
          ],
          "side_span_xh": [
            17.521928584252187,
            17.54613706968976
          ],
          "shared_span_xh": 16.96152559721547,
          "occupied_rows": 14,
          "bilateral_rows": 14,
          "participants": [
            {
              "line_index": 101,
              "xheight": 13.02525813625789
            },
            {
              "line_index": 102,
              "xheight": 13.21564374454897
            },
            {
              "line_index": 103,
              "xheight": 13.329077672391122
            },
            {
              "line_index": 104,
              "xheight": 13.240577044266047
            },
            {
              "line_index": 105,
              "xheight": 13.293161217577335
            },
            {
              "line_index": 106,
              "xheight": 13.04170413665588
            },
            {
              "line_index": 107,
              "xheight": 13.069345792057447
            },
            {
              "line_index": 108,
              "xheight": 12.8912012828755
            },
            {
              "line_index": 109,
              "xheight": 13.327646919027757
            },
            {
              "line_index": 110,
              "xheight": 13.048416000399811
            },
            {
              "line_index": 111,
              "xheight": 13.274660685400022
            },
            {
              "line_index": 112,
              "xheight": 13.091721183253412
            },
            {
              "line_index": 113,
              "xheight": 12.634709578597949
            },
            {
              "line_index": 114,
              "xheight": 12.911451582966492
            },
            {
              "line_index": 115,
              "xheight": 12.693535413881136
            },
            {
              "line_index": 117,
              "xheight": 12.769572758591494
            },
            {
              "line_index": 118,
              "xheight": 12.997678638052548
            },
            {
              "line_index": 119,
              "xheight": 13.858776950971333
            }
          ],
          "observed_gap_widths_px": [
            72,
            72,
            44,
            44,
            44,
            44,
            44,
            44,
            46,
            46,
            44,
            44,
            45,
            75
          ],
          "white_rows": 14,
          "baseline_matching_reach_px": 15.153750000000002,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      }
    ],
    "rejected": [],
    "inventory_sha256": "27e54813a50cb768882f03ad9bd57ffdc7e4f573d2e02d4e323d4023067d2248"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.7401814550323826,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## ia_poly1850--c3f3a531e277da9a--s011-l0019

Card `k5633590226`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/38e42d1474e28878c9c1dca7e1657285b7d72a3e145ee8eebfcef9d03d93b367.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/38e42d1474e28878c9c1dca7e1657285b7d72a3e145ee8eebfcef9d03d93b367.png`; SHA-256 `38e42d1474e28878c9c1dca7e1657285b7d72a3e145ee8eebfcef9d03d93b367`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k5633590226",
  "letters": "y",
  "marks": "n",
  "crop_ok": "y",
  "errors": [
    "missing_mark"
  ],
  "detail": "ἀπαντᾷ → ἀπαντᾶ",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "ia_poly1850--c3f3a531e277da9a--s011-l0019"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00017",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      117,
      1388,
      1629,
      1458
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00017"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00017"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00017",
      "column_id": "single:column-0000",
      "xheight": 24.924835876624456,
      "assigned_pixels": 11774,
      "supported": null,
      "runs": [
        {
          "x0": 120,
          "x1": 130,
          "body_cut_fraction": 0.0,
          "body_pixels": 140,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 146,
          "x1": 169,
          "body_cut_fraction": 0.0,
          "body_pixels": 222,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 173,
          "x1": 187,
          "body_cut_fraction": 0.0,
          "body_pixels": 178,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 188,
          "x1": 202,
          "body_cut_fraction": 0.0,
          "body_pixels": 140,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 207,
          "x1": 226,
          "body_cut_fraction": 0.0,
          "body_pixels": 237,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 230,
          "x1": 253,
          "body_cut_fraction": 0.0,
          "body_pixels": 201,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 258,
          "x1": 281,
          "body_cut_fraction": 0.0,
          "body_pixels": 226,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 286,
          "x1": 307,
          "body_cut_fraction": 0.0,
          "body_pixels": 170,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 336,
          "x1": 365,
          "body_cut_fraction": 0.0,
          "body_pixels": 323,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 371,
          "x1": 389,
          "body_cut_fraction": 0.0,
          "body_pixels": 150,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 395,
          "x1": 416,
          "body_cut_fraction": 0.0,
          "body_pixels": 147,
          "body_extent_px": 22,
          "complete": true
        },
        {
          "x0": 449,
          "x1": 472,
          "body_cut_fraction": 0.0,
          "body_pixels": 253,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 477,
          "x1": 497,
          "body_cut_fraction": 0.0,
          "body_pixels": 188,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 501,
          "x1": 504,
          "body_cut_fraction": 0.0,
          "body_pixels": 14,
          "body_extent_px": 6,
          "complete": false
        },
        {
          "x0": 505,
          "x1": 516,
          "body_cut_fraction": 0.0,
          "body_pixels": 135,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 549,
          "x1": 551,
          "body_cut_fraction": 0.0,
          "body_pixels": 11,
          "body_extent_px": 8,
          "complete": false
        },
        {
          "x0": 553,
          "x1": 562,
          "body_cut_fraction": 0.0,
          "body_pixels": 122,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 563,
          "x1": 564,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 567,
          "x1": 577,
          "body_cut_fraction": 0.0,
          "body_pixels": 121,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 624,
          "x1": 649,
          "body_cut_fraction": 0.0,
          "body_pixels": 263,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 654,
          "x1": 672,
          "body_cut_fraction": 0.0,
          "body_pixels": 191,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 678,
          "x1": 698,
          "body_cut_fraction": 0.0,
          "body_pixels": 173,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 704,
          "x1": 718,
          "body_cut_fraction": 0.0,
          "body_pixels": 156,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 723,
          "x1": 745,
          "body_cut_fraction": 0.0,
          "body_pixels": 193,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 774,
          "x1": 795,
          "body_cut_fraction": 0.0,
          "body_pixels": 248,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 797,
          "x1": 799,
          "body_cut_fraction": 0.0,
          "body_pixels": 6,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 820,
          "x1": 844,
          "body_cut_fraction": 0.0,
          "body_pixels": 245,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 865,
          "x1": 884,
          "body_cut_fraction": 0.0,
          "body_pixels": 251,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 902,
          "x1": 925,
          "body_cut_fraction": 0.0,
          "body_pixels": 252,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 947,
          "x1": 974,
          "body_cut_fraction": 0.0,
          "body_pixels": 321,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 991,
          "x1": 994,
          "body_cut_fraction": 0.0,
          "body_pixels": 12,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 996,
          "x1": 1006,
          "body_cut_fraction": 0.0,
          "body_pixels": 110,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1025,
          "x1": 1047,
          "body_cut_fraction": 0.0,
          "body_pixels": 215,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1071,
          "x1": 1092,
          "body_cut_fraction": 0.0,
          "body_pixels": 186,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1112,
          "x1": 1121,
          "body_cut_fraction": 0.0,
          "body_pixels": 116,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1127,
          "x1": 1134,
          "body_cut_fraction": 0.0,
          "body_pixels": 91,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1135,
          "x1": 1137,
          "body_cut_fraction": 0.0,
          "body_pixels": 9,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 1157,
          "x1": 1180,
          "body_cut_fraction": 0.0,
          "body_pixels": 201,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1208,
          "x1": 1231,
          "body_cut_fraction": 0.0,
          "body_pixels": 228,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1235,
          "x1": 1248,
          "body_cut_fraction": 0.0,
          "body_pixels": 139,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1249,
          "x1": 1251,
          "body_cut_fraction": 0.0,
          "body_pixels": 6,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1253,
          "x1": 1254,
          "body_cut_fraction": 0.0,
          "body_pixels": 3,
          "body_extent_px": 3,
          "complete": false
        },
        {
          "x0": 1255,
          "x1": 1263,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 22,
          "complete": true
        },
        {
          "x0": 1269,
          "x1": 1291,
          "body_cut_fraction": 0.0,
          "body_pixels": 186,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1296,
          "x1": 1324,
          "body_cut_fraction": 0.0,
          "body_pixels": 359,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1328,
          "x1": 1329,
          "body_cut_fraction": 0.0,
          "body_pixels": 4,
          "body_extent_px": 4,
          "complete": false
        },
        {
          "x0": 1332,
          "x1": 1338,
          "body_cut_fraction": 0.0,
          "body_pixels": 100,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1343,
          "x1": 1355,
          "body_cut_fraction": 0.0,
          "body_pixels": 108,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 1361,
          "x1": 1384,
          "body_cut_fraction": 0.0,
          "body_pixels": 230,
          "body_extent_px": 23,
          "complete": true
        },
        {
          "x0": 1389,
          "x1": 1416,
          "body_cut_fraction": 0.0,
          "body_pixels": 259,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1448,
          "x1": 1475,
          "body_cut_fraction": 0.0,
          "body_pixels": 275,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1480,
          "x1": 1508,
          "body_cut_fraction": 0.0,
          "body_pixels": 369,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1514,
          "x1": 1542,
          "body_cut_fraction": 0.0,
          "body_pixels": 312,
          "body_extent_px": 25,
          "complete": true
        },
        {
          "x0": 1549,
          "x1": 1560,
          "body_cut_fraction": 0.0,
          "body_pixels": 88,
          "body_extent_px": 22,
          "complete": true
        },
        {
          "x0": 1564,
          "x1": 1567,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": false
        },
        {
          "x0": 1574,
          "x1": 1596,
          "body_cut_fraction": 0.0,
          "body_pixels": 167,
          "body_extent_px": 24,
          "complete": true
        },
        {
          "x0": 1600,
          "x1": 1628,
          "body_cut_fraction": 0.0,
          "body_pixels": 295,
          "body_extent_px": 24,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 25,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "4bbb2f41aec81ca4909b12b2490260b10dc62484b1fbdb404f937cc31e12e372"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 1.0,
    "polarity_confidence": 0.5294117647058824,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--42cb41d9c3e7bbcf--s000-l0108

Card `k7e4beb9fbb`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/7dc3a366c4c231e6aa8c0066ab83660c2d0196a721036816987303386d6e1f6a.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/7dc3a366c4c231e6aa8c0066ab83660c2d0196a721036816987303386d6e1f6a.png`; SHA-256 `7dc3a366c4c231e6aa8c0066ab83660c2d0196a721036816987303386d6e1f6a`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k7e4beb9fbb",
  "letters": "y",
  "marks": "y",
  "crop_ok": "n",
  "errors": [
    "crop_overrun"
  ],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "Only upper parts of characters and a number from the lower line are visible.",
  "multi_line": "no",
  "multi_line_reason": "The lower line is clipped through its characters; only the target line is complete.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--42cb41d9c3e7bbcf--s000-l0108"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00105",
  "neighbour_rows": [
    {
      "row_id": "row-00106",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "profile_runs": [
        [
          854,
          880
        ],
        [
          882,
          892
        ],
        [
          903,
          915
        ],
        [
          916,
          928
        ],
        [
          930,
          940
        ],
        [
          942,
          950
        ],
        [
          961,
          969
        ],
        [
          971,
          981
        ],
        [
          983,
          992
        ],
        [
          995,
          1004
        ],
        [
          1006,
          1015
        ],
        [
          1016,
          1028
        ],
        [
          1040,
          1052
        ],
        [
          1053,
          1066
        ],
        [
          1067,
          1078
        ],
        [
          1079,
          1088
        ],
        [
          1089,
          1101
        ],
        [
          1103,
          1107
        ],
        [
          1108,
          1116
        ],
        [
          1118,
          1122
        ],
        [
          1124,
          1140
        ],
        [
          1142,
          1152
        ],
        [
          1154,
          1161
        ],
        [
          1164,
          1180
        ],
        [
          1182,
          1191
        ],
        [
          1202,
          1214
        ],
        [
          1216,
          1220
        ],
        [
          1222,
          1234
        ],
        [
          1245,
          1255
        ],
        [
          1256,
          1267
        ],
        [
          1269,
          1278
        ],
        [
          1289,
          1301
        ],
        [
          1303,
          1312
        ],
        [
          1314,
          1326
        ],
        [
          1327,
          1337
        ],
        [
          1339,
          1351
        ],
        [
          1366,
          1371
        ],
        [
          1377,
          1390
        ],
        [
          1393,
          1405
        ],
        [
          1407,
          1420
        ],
        [
          1423,
          1426
        ]
      ],
      "profile_gaps": [
        [
          880,
          882
        ],
        [
          892,
          903
        ],
        [
          915,
          916
        ],
        [
          928,
          930
        ],
        [
          940,
          942
        ],
        [
          950,
          961
        ],
        [
          969,
          971
        ],
        [
          981,
          983
        ],
        [
          992,
          995
        ],
        [
          1004,
          1006
        ],
        [
          1015,
          1016
        ],
        [
          1028,
          1040
        ],
        [
          1052,
          1053
        ],
        [
          1066,
          1067
        ],
        [
          1078,
          1079
        ],
        [
          1088,
          1089
        ],
        [
          1101,
          1103
        ],
        [
          1107,
          1108
        ],
        [
          1116,
          1118
        ],
        [
          1122,
          1124
        ],
        [
          1140,
          1142
        ],
        [
          1152,
          1154
        ],
        [
          1161,
          1164
        ],
        [
          1180,
          1182
        ],
        [
          1191,
          1202
        ],
        [
          1214,
          1216
        ],
        [
          1220,
          1222
        ],
        [
          1234,
          1245
        ],
        [
          1255,
          1256
        ],
        [
          1267,
          1269
        ],
        [
          1278,
          1289
        ],
        [
          1301,
          1303
        ],
        [
          1312,
          1314
        ],
        [
          1326,
          1327
        ],
        [
          1337,
          1339
        ],
        [
          1351,
          1366
        ],
        [
          1371,
          1377
        ],
        [
          1390,
          1393
        ],
        [
          1405,
          1407
        ],
        [
          1420,
          1423
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 15788
      },
      "groups": [
        {
          "box": [
            903,
            1784,
            950,
            1804
          ],
          "body_count": 4,
          "width_xh": 3.9166666666666665,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            961,
            1784,
            1028,
            1809
          ],
          "body_count": 6,
          "width_xh": 5.583333333333333,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1040,
            1783,
            1191,
            1808
          ],
          "body_count": 12,
          "width_xh": 12.583333333333334,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1289,
            1780,
            1426,
            1806
          ],
          "body_count": 10,
          "width_xh": 11.416666666666666,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      877,
      1746,
      1572,
      1785
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00105"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00105"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00105",
      "column_id": "single:column-0000",
      "xheight": 11.975834009919936,
      "assigned_pixels": 3769,
      "supported": null,
      "runs": [
        {
          "x0": 882,
          "x1": 894,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 898,
          "x1": 902,
          "body_cut_fraction": 0.0,
          "body_pixels": 14,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 911,
          "x1": 917,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 919,
          "x1": 926,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 928,
          "x1": 940,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 942,
          "x1": 954,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 956,
          "x1": 978,
          "body_cut_fraction": 0.0,
          "body_pixels": 104,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 979,
          "x1": 991,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 992,
          "x1": 1013,
          "body_cut_fraction": 0.0,
          "body_pixels": 100,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1015,
          "x1": 1018,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1025,
          "x1": 1035,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1036,
          "x1": 1053,
          "body_cut_fraction": 0.0,
          "body_pixels": 98,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1054,
          "x1": 1064,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1072,
          "x1": 1085,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1086,
          "x1": 1094,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1096,
          "x1": 1107,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1108,
          "x1": 1124,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1125,
          "x1": 1135,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1143,
          "x1": 1152,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1154,
          "x1": 1164,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1166,
          "x1": 1176,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1185,
          "x1": 1197,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1200,
          "x1": 1204,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1206,
          "x1": 1216,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1218,
          "x1": 1223,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1224,
          "x1": 1235,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1236,
          "x1": 1243,
          "body_cut_fraction": 0.0,
          "body_pixels": 41,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1245,
          "x1": 1248,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1250,
          "x1": 1259,
          "body_cut_fraction": 0.0,
          "body_pixels": 45,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1261,
          "x1": 1266,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1267,
          "x1": 1278,
          "body_cut_fraction": 0.0,
          "body_pixels": 70,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1280,
          "x1": 1290,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1292,
          "x1": 1302,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1310,
          "x1": 1324,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1326,
          "x1": 1335,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1337,
          "x1": 1350,
          "body_cut_fraction": 0.0,
          "body_pixels": 74,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1352,
          "x1": 1354,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1355,
          "x1": 1363,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1365,
          "x1": 1375,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1377,
          "x1": 1387,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1389,
          "x1": 1399,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1401,
          "x1": 1405,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1407,
          "x1": 1417,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1419,
          "x1": 1429,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1437,
          "x1": 1448,
          "body_cut_fraction": 0.0,
          "body_pixels": 71,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 1449,
          "x1": 1461,
          "body_cut_fraction": 0.0,
          "body_pixels": 80,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1463,
          "x1": 1468,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1476,
          "x1": 1484,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1485,
          "x1": 1496,
          "body_cut_fraction": 0.0,
          "body_pixels": 56,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1497,
          "x1": 1505,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1507,
          "x1": 1519,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1521,
          "x1": 1532,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1533,
          "x1": 1542,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1544,
          "x1": 1561,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 1562,
          "x1": 1571,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 11,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00106",
      "column_id": "single:column-0000",
      "xheight": 12.0,
      "assigned_pixels": 144,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 116,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "b086d00196c7234f3b862503c599db839dc3f7145504ff54eba7deb4541701db"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.9095688545673682,
    "polarity_confidence": 0.3333333333333333,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## bsb_poly1850--0ab5fcea9a6fd52e--s025-l0022

Card `k190260536e`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/71bd0280f7be76fe8c0337d77292081dba0aa6c6349cf2508a0b0f8edd68c17f.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/71bd0280f7be76fe8c0337d77292081dba0aa6c6349cf2508a0b0f8edd68c17f.png`; SHA-256 `71bd0280f7be76fe8c0337d77292081dba0aa6c6349cf2508a0b0f8edd68c17f`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k190260536e",
  "letters": "n",
  "marks": "y",
  "crop_ok": "y",
  "errors": [
    "wrong_letter",
    "digits"
  ],
  "detail": "299ᵇ31 → 299631",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "bsb_poly1850--0ab5fcea9a6fd52e--s025-l0022"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00021",
  "neighbour_rows": [],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      342,
      1316,
      1695,
      1369
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00021"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00021"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00021",
      "column_id": "single:column-0000",
      "xheight": 17.158535971697688,
      "assigned_pixels": 7406,
      "supported": null,
      "runs": [
        {
          "x0": 348,
          "x1": 360,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 364,
          "x1": 371,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 373,
          "x1": 380,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 401,
          "x1": 406,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 410,
          "x1": 415,
          "body_cut_fraction": 0.0,
          "body_pixels": 43,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 420,
          "x1": 424,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 440,
          "x1": 453,
          "body_cut_fraction": 0.0,
          "body_pixels": 87,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 457,
          "x1": 462,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 466,
          "x1": 471,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 474,
          "x1": 479,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 483,
          "x1": 488,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 497,
          "x1": 502,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 504,
          "x1": 509,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 515,
          "x1": 520,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 523,
          "x1": 530,
          "body_cut_fraction": 0.0,
          "body_pixels": 61,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 538,
          "x1": 543,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 599,
          "x1": 604,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 608,
          "x1": 611,
          "body_cut_fraction": 0.0,
          "body_pixels": 15,
          "body_extent_px": 7,
          "complete": false
        },
        {
          "x0": 614,
          "x1": 620,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 8,
          "complete": false
        },
        {
          "x0": 627,
          "x1": 641,
          "body_cut_fraction": 0.0,
          "body_pixels": 81,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 648,
          "x1": 655,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 678,
          "x1": 692,
          "body_cut_fraction": 0.0,
          "body_pixels": 85,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 701,
          "x1": 708,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 732,
          "x1": 751,
          "body_cut_fraction": 0.0,
          "body_pixels": 138,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 758,
          "x1": 772,
          "body_cut_fraction": 0.0,
          "body_pixels": 105,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 778,
          "x1": 791,
          "body_cut_fraction": 0.0,
          "body_pixels": 78,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 815,
          "x1": 834,
          "body_cut_fraction": 0.0,
          "body_pixels": 123,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 840,
          "x1": 856,
          "body_cut_fraction": 0.0,
          "body_pixels": 99,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 864,
          "x1": 881,
          "body_cut_fraction": 0.0,
          "body_pixels": 112,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 890,
          "x1": 897,
          "body_cut_fraction": 0.0,
          "body_pixels": 52,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 900,
          "x1": 908,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 915,
          "x1": 928,
          "body_cut_fraction": 0.0,
          "body_pixels": 87,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 936,
          "x1": 944,
          "body_cut_fraction": 0.0,
          "body_pixels": 58,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 968,
          "x1": 971,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 973,
          "x1": 983,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 991,
          "x1": 1008,
          "body_cut_fraction": 0.0,
          "body_pixels": 131,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1016,
          "x1": 1029,
          "body_cut_fraction": 0.0,
          "body_pixels": 98,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1037,
          "x1": 1051,
          "body_cut_fraction": 0.0,
          "body_pixels": 113,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1059,
          "x1": 1073,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1080,
          "x1": 1093,
          "body_cut_fraction": 0.0,
          "body_pixels": 100,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1101,
          "x1": 1115,
          "body_cut_fraction": 0.0,
          "body_pixels": 112,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1122,
          "x1": 1139,
          "body_cut_fraction": 0.0,
          "body_pixels": 147,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1163,
          "x1": 1178,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1185,
          "x1": 1203,
          "body_cut_fraction": 0.0,
          "body_pixels": 155,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1227,
          "x1": 1243,
          "body_cut_fraction": 0.0,
          "body_pixels": 132,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1250,
          "x1": 1257,
          "body_cut_fraction": 0.0,
          "body_pixels": 66,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1260,
          "x1": 1273,
          "body_cut_fraction": 0.0,
          "body_pixels": 111,
          "body_extent_px": 15,
          "complete": true
        },
        {
          "x0": 1283,
          "x1": 1288,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1289,
          "x1": 1290,
          "body_cut_fraction": 0.0,
          "body_pixels": 2,
          "body_extent_px": 2,
          "complete": false
        },
        {
          "x0": 1291,
          "x1": 1302,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1309,
          "x1": 1326,
          "body_cut_fraction": 0.0,
          "body_pixels": 162,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1334,
          "x1": 1348,
          "body_cut_fraction": 0.0,
          "body_pixels": 101,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1350,
          "x1": 1367,
          "body_cut_fraction": 0.0,
          "body_pixels": 172,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1391,
          "x1": 1405,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1412,
          "x1": 1419,
          "body_cut_fraction": 0.0,
          "body_pixels": 67,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1421,
          "x1": 1435,
          "body_cut_fraction": 0.0,
          "body_pixels": 123,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1443,
          "x1": 1455,
          "body_cut_fraction": 0.0,
          "body_pixels": 97,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1480,
          "x1": 1493,
          "body_cut_fraction": 0.0,
          "body_pixels": 113,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1500,
          "x1": 1520,
          "body_cut_fraction": 0.0,
          "body_pixels": 124,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1526,
          "x1": 1533,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1540,
          "x1": 1560,
          "body_cut_fraction": 0.0,
          "body_pixels": 140,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1566,
          "x1": 1579,
          "body_cut_fraction": 0.0,
          "body_pixels": 108,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1586,
          "x1": 1601,
          "body_cut_fraction": 0.0,
          "body_pixels": 134,
          "body_extent_px": 17,
          "complete": true
        },
        {
          "x0": 1608,
          "x1": 1616,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 16,
          "complete": true
        },
        {
          "x0": 1617,
          "x1": 1632,
          "body_cut_fraction": 0.0,
          "body_pixels": 139,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1638,
          "x1": 1651,
          "body_cut_fraction": 0.0,
          "body_pixels": 103,
          "body_extent_px": 18,
          "complete": true
        },
        {
          "x0": 1666,
          "x1": 1679,
          "body_cut_fraction": 0.0,
          "body_pixels": 149,
          "body_extent_px": 19,
          "complete": true
        },
        {
          "x0": 1680,
          "x1": 1693,
          "body_cut_fraction": 0.0,
          "body_pixels": 142,
          "body_extent_px": 18,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 42,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "239566f5ab77c0be282205e21cef452b85e6716347ece1669940f00552c1cf21"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.8957581407429381,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## lekythos--0fc3672826ddd6b3--s000-l0033

Card `ka79c120979`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/5066944082050b58862f59d07f0ff76f33d4f84a735a5ac56d142857ff6e2b8d.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/5066944082050b58862f59d07f0ff76f33d4f84a735a5ac56d142857ff6e2b8d.png`; SHA-256 `5066944082050b58862f59d07f0ff76f33d4f84a735a5ac56d142857ff6e2b8d`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "ka79c120979",
  "letters": "y",
  "marks": "n",
  "crop_ok": "y",
  "errors": [
    "wrong_mark"
  ],
  "detail": "πραγματικὰ → πραγματικά",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "lekythos--0fc3672826ddd6b3--s000-l0033"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00055",
  "neighbour_rows": [
    {
      "row_id": "row-00054",
      "column_id": "left:column-0003",
      "xheight": 12.388807412235565,
      "profile_runs": [
        [
          220,
          225
        ],
        [
          227,
          232
        ],
        [
          235,
          247
        ],
        [
          250,
          260
        ],
        [
          262,
          266
        ],
        [
          281,
          292
        ],
        [
          298,
          302
        ],
        [
          303,
          304
        ],
        [
          307,
          312
        ],
        [
          314,
          318
        ],
        [
          322,
          328
        ],
        [
          329,
          332
        ],
        [
          343,
          354
        ],
        [
          357,
          361
        ],
        [
          362,
          363
        ],
        [
          364,
          370
        ],
        [
          372,
          379
        ],
        [
          380,
          383
        ],
        [
          385,
          389
        ],
        [
          391,
          398
        ],
        [
          400,
          413
        ],
        [
          416,
          424
        ],
        [
          439,
          450
        ],
        [
          453,
          457
        ],
        [
          458,
          459
        ],
        [
          460,
          466
        ],
        [
          470,
          472
        ],
        [
          491,
          502
        ],
        [
          505,
          509
        ],
        [
          510,
          518
        ],
        [
          521,
          531
        ],
        [
          532,
          534
        ],
        [
          537,
          544
        ],
        [
          545,
          547
        ],
        [
          549,
          552
        ],
        [
          558,
          568
        ],
        [
          569,
          582
        ],
        [
          586,
          591
        ],
        [
          592,
          595
        ],
        [
          598,
          606
        ],
        [
          610,
          613
        ],
        [
          643,
          647
        ],
        [
          651,
          654
        ],
        [
          659,
          663
        ],
        [
          666,
          670
        ],
        [
          675,
          680
        ],
        [
          682,
          684
        ],
        [
          710,
          721
        ],
        [
          723,
          727
        ],
        [
          730,
          736
        ],
        [
          739,
          743
        ],
        [
          744,
          746
        ]
      ],
      "profile_gaps": [
        [
          225,
          227
        ],
        [
          232,
          235
        ],
        [
          247,
          250
        ],
        [
          260,
          262
        ],
        [
          266,
          281
        ],
        [
          292,
          298
        ],
        [
          302,
          303
        ],
        [
          304,
          307
        ],
        [
          312,
          314
        ],
        [
          318,
          322
        ],
        [
          328,
          329
        ],
        [
          332,
          343
        ],
        [
          354,
          357
        ],
        [
          361,
          362
        ],
        [
          363,
          364
        ],
        [
          370,
          372
        ],
        [
          379,
          380
        ],
        [
          383,
          385
        ],
        [
          389,
          391
        ],
        [
          398,
          400
        ],
        [
          413,
          416
        ],
        [
          424,
          439
        ],
        [
          450,
          453
        ],
        [
          457,
          458
        ],
        [
          459,
          460
        ],
        [
          466,
          470
        ],
        [
          472,
          491
        ],
        [
          502,
          505
        ],
        [
          509,
          510
        ],
        [
          518,
          521
        ],
        [
          531,
          532
        ],
        [
          534,
          537
        ],
        [
          544,
          545
        ],
        [
          547,
          549
        ],
        [
          552,
          558
        ],
        [
          568,
          569
        ],
        [
          582,
          586
        ],
        [
          591,
          592
        ],
        [
          595,
          598
        ],
        [
          606,
          610
        ],
        [
          613,
          643
        ],
        [
          647,
          651
        ],
        [
          654,
          659
        ],
        [
          663,
          666
        ],
        [
          670,
          675
        ],
        [
          680,
          682
        ],
        [
          684,
          710
        ],
        [
          721,
          723
        ],
        [
          727,
          730
        ],
        [
          736,
          739
        ],
        [
          743,
          744
        ]
      ],
      "directional_missing": {
        "above": 12642,
        "below": 0
      },
      "groups": [
        {
          "box": [
            643,
            1421,
            654,
            1438
          ],
          "body_count": 2,
          "width_xh": 0.8878982160248987,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00056",
      "column_id": "left:column-0003",
      "xheight": 12.787943853199067,
      "profile_runs": [
        [
          219,
          222
        ],
        [
          223,
          231
        ],
        [
          233,
          245
        ],
        [
          248,
          253
        ],
        [
          254,
          261
        ],
        [
          262,
          274
        ],
        [
          277,
          286
        ],
        [
          288,
          292
        ],
        [
          297,
          306
        ],
        [
          309,
          318
        ],
        [
          322,
          325
        ],
        [
          329,
          332
        ]
      ],
      "profile_gaps": [
        [
          222,
          223
        ],
        [
          231,
          233
        ],
        [
          245,
          248
        ],
        [
          253,
          254
        ],
        [
          261,
          262
        ],
        [
          274,
          277
        ],
        [
          286,
          288
        ],
        [
          292,
          297
        ],
        [
          306,
          309
        ],
        [
          318,
          322
        ],
        [
          325,
          329
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 913
      },
      "groups": [
        {
          "box": [
            219,
            1468,
            332,
            1493
          ],
          "body_count": 10,
          "width_xh": 8.836447930738421,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      304,
      1436,
      750,
      1469
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00055"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "left",
        "column_id": "left:column-0003",
        "row_ids": [
          "row-00055"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00054",
      "column_id": "left:column-0003",
      "xheight": 12.388807412235565,
      "assigned_pixels": 8,
      "supported": null,
      "runs": []
    },
    {
      "row_id": "row-00055",
      "column_id": "left:column-0003",
      "xheight": 12.15346087213402,
      "assigned_pixels": 1494,
      "supported": null,
      "runs": [
        {
          "x0": 307,
          "x1": 320,
          "body_cut_fraction": 0.0,
          "body_pixels": 55,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 323,
          "x1": 327,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 330,
          "x1": 335,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 337,
          "x1": 341,
          "body_cut_fraction": 0.0,
          "body_pixels": 30,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 344,
          "x1": 350,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 351,
          "x1": 358,
          "body_cut_fraction": 0.0,
          "body_pixels": 23,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 359,
          "x1": 363,
          "body_cut_fraction": 0.0,
          "body_pixels": 16,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 366,
          "x1": 369,
          "body_cut_fraction": 0.0,
          "body_pixels": 33,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 373,
          "x1": 376,
          "body_cut_fraction": 0.0,
          "body_pixels": 31,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 380,
          "x1": 384,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 387,
          "x1": 393,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 397,
          "x1": 404,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 408,
          "x1": 411,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 417,
          "x1": 428,
          "body_cut_fraction": 0.0,
          "body_pixels": 59,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 431,
          "x1": 435,
          "body_cut_fraction": 0.0,
          "body_pixels": 24,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 438,
          "x1": 443,
          "body_cut_fraction": 0.0,
          "body_pixels": 35,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 482,
          "x1": 485,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 491,
          "x1": 495,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 499,
          "x1": 502,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 505,
          "x1": 516,
          "body_cut_fraction": 0.0,
          "body_pixels": 62,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 519,
          "x1": 523,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 527,
          "x1": 530,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 557,
          "x1": 568,
          "body_cut_fraction": 0.0,
          "body_pixels": 57,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 570,
          "x1": 575,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 577,
          "x1": 583,
          "body_cut_fraction": 0.0,
          "body_pixels": 39,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 586,
          "x1": 596,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 599,
          "x1": 603,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 607,
          "x1": 610,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 641,
          "x1": 645,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 648,
          "x1": 653,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 656,
          "x1": 661,
          "body_cut_fraction": 0.0,
          "body_pixels": 38,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 664,
          "x1": 667,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 7,
          "complete": true
        },
        {
          "x0": 670,
          "x1": 679,
          "body_cut_fraction": 0.0,
          "body_pixels": 41,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 682,
          "x1": 690,
          "body_cut_fraction": 0.0,
          "body_pixels": 46,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 694,
          "x1": 703,
          "body_cut_fraction": 0.0,
          "body_pixels": 47,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 727,
          "x1": 731,
          "body_cut_fraction": 0.0,
          "body_pixels": 28,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 735,
          "x1": 738,
          "body_cut_fraction": 0.0,
          "body_pixels": 26,
          "body_extent_px": 11,
          "complete": true
        },
        {
          "x0": 742,
          "x1": 746,
          "body_cut_fraction": 0.0,
          "body_pixels": 27,
          "body_extent_px": 12,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00056",
      "column_id": "left:column-0003",
      "xheight": 12.787943853199067,
      "assigned_pixels": 1,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 189,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.139301963898515,
        "required_common_rows": 2.477761482447113,
        "xheight_px": 12.388807412235565,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 225.0,
          "threshold": 225.0
        },
        "line_extent": [
          304,
          1407.245,
          746,
          1441.178
        ],
        "boundary_path": [
          [
            1339.0,
            0.0
          ],
          [
            1339.0,
            1939.0
          ]
        ],
        "row_id": "row-00054"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.908264446819705,
        "required_common_rows": 2.430692174426804,
        "xheight_px": 12.15346087213402,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 101.0,
          "threshold": 163.0
        },
        "line_extent": [
          304,
          1436.619,
          747,
          1469.639
        ],
        "boundary_path": [
          [
            1339.0,
            0.0
          ],
          [
            1339.0,
            1939.0
          ]
        ],
        "row_id": "row-00055"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0000",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.5412603197028725,
        "required_common_rows": 2.5575887706398137,
        "xheight_px": 12.787943853199067,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 224.0,
          "ink_q10": 224.0,
          "threshold": 224.0
        },
        "line_extent": [
          304,
          1465.38,
          332,
          1495.407
        ],
        "boundary_path": [
          [
            1339.0,
            0.0
          ],
          [
            1339.0,
            1939.0
          ]
        ],
        "row_id": "row-00056"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.139301963898515,
        "required_common_rows": 2.477761482447113,
        "xheight_px": 12.388807412235565,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 225.0,
          "threshold": 225.0
        },
        "line_extent": [
          304,
          1407.245,
          746,
          1441.178
        ],
        "boundary_path": [
          [
            1915.0,
            0.0
          ],
          [
            1915.0,
            1939.0
          ]
        ],
        "row_id": "row-00054"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.908264446819705,
        "required_common_rows": 2.430692174426804,
        "xheight_px": 12.15346087213402,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 101.0,
          "threshold": 163.0
        },
        "line_extent": [
          304,
          1436.619,
          747,
          1469.639
        ],
        "boundary_path": [
          [
            1915.0,
            0.0
          ],
          [
            1915.0,
            1939.0
          ]
        ],
        "row_id": "row-00055"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0001",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.5412603197028725,
        "required_common_rows": 2.5575887706398137,
        "xheight_px": 12.787943853199067,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 224.0,
          "ink_q10": 224.0,
          "threshold": 224.0
        },
        "line_extent": [
          304,
          1465.38,
          332,
          1495.407
        ],
        "boundary_path": [
          [
            1915.0,
            0.0
          ],
          [
            1915.0,
            1939.0
          ]
        ],
        "row_id": "row-00056"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.139301963898515,
        "required_common_rows": 2.477761482447113,
        "xheight_px": 12.388807412235565,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 225.0,
          "threshold": 225.0
        },
        "line_extent": [
          304,
          1407.245,
          746,
          1441.178
        ],
        "boundary_path": [
          [
            765.5,
            1379.0
          ],
          [
            765.5,
            1616.0
          ]
        ],
        "row_id": "row-00054"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          53,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.908264446819705,
        "required_common_rows": 2.430692174426804,
        "xheight_px": 12.15346087213402,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 101.0,
          "threshold": 163.0
        },
        "line_extent": [
          304,
          1436.619,
          747,
          1469.639
        ],
        "boundary_path": [
          [
            765.5,
            1379.0
          ],
          [
            765.5,
            1616.0
          ]
        ],
        "row_id": "row-00055"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0002",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.5412603197028725,
        "required_common_rows": 2.5575887706398137,
        "xheight_px": 12.787943853199067,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 224.0,
          "ink_q10": 224.0,
          "threshold": 224.0
        },
        "line_extent": [
          304,
          1465.38,
          332,
          1495.407
        ],
        "boundary_path": [
          [
            765.5,
            1379.0
          ],
          [
            765.5,
            1616.0
          ]
        ],
        "row_id": "row-00056"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.139301963898515,
        "required_common_rows": 2.477761482447113,
        "xheight_px": 12.388807412235565,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 225.0,
          "threshold": 225.0
        },
        "line_extent": [
          304,
          1407.245,
          746,
          1441.178
        ],
        "boundary_path": [
          [
            1335.5,
            1379.0
          ],
          [
            1335.5,
            1616.0
          ]
        ],
        "row_id": "row-00054"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.908264446819705,
        "required_common_rows": 2.430692174426804,
        "xheight_px": 12.15346087213402,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 101.0,
          "threshold": 163.0
        },
        "line_extent": [
          304,
          1436.619,
          747,
          1469.639
        ],
        "boundary_path": [
          [
            1335.5,
            1379.0
          ],
          [
            1335.5,
            1616.0
          ]
        ],
        "row_id": "row-00055"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0003",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.5412603197028725,
        "required_common_rows": 2.5575887706398137,
        "xheight_px": 12.787943853199067,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 224.0,
          "ink_q10": 224.0,
          "threshold": 224.0
        },
        "line_extent": [
          304,
          1465.38,
          332,
          1495.407
        ],
        "boundary_path": [
          [
            1335.5,
            1379.0
          ],
          [
            1335.5,
            1616.0
          ]
        ],
        "row_id": "row-00056"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 0,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.139301963898515,
        "required_common_rows": 2.477761482447113,
        "xheight_px": 12.388807412235565,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 225.0,
          "threshold": 225.0
        },
        "line_extent": [
          304,
          1407.245,
          746,
          1441.178
        ],
        "boundary_path": [
          [
            1358.0,
            1616.0
          ],
          [
            1358.0,
            1852.0
          ]
        ],
        "row_id": "row-00054"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 1,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 5.908264446819705,
        "required_common_rows": 2.430692174426804,
        "xheight_px": 12.15346087213402,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 225.0,
          "ink_q10": 101.0,
          "threshold": 163.0
        },
        "line_extent": [
          304,
          1436.619,
          747,
          1469.639
        ],
        "boundary_path": [
          [
            1358.0,
            1616.0
          ],
          [
            1358.0,
            1852.0
          ]
        ],
        "row_id": "row-00055"
      },
      {
        "classification": "unresolved envelope overlap",
        "line_index": 2,
        "boundary_id": "boundary-0004",
        "boundary_kind": "gutter",
        "own_ink_pixels_sides": [
          0,
          0
        ],
        "common_ink_rows": 0,
        "required_ink_pixels_per_side": 6.5412603197028725,
        "required_common_rows": 2.5575887706398137,
        "xheight_px": 12.787943853199067,
        "rule_exclusion_margin_px": 0.0,
        "excluded_rule_components": [],
        "foreground_contrast": {
          "paper": 224.0,
          "ink_q10": 224.0,
          "threshold": 224.0
        },
        "line_extent": [
          304,
          1465.38,
          332,
          1495.407
        ],
        "boundary_path": [
          [
            1358.0,
            1616.0
          ],
          [
            1358.0,
            1852.0
          ]
        ],
        "row_id": "row-00056"
      }
    ],
    "validated": [
      {
        "kind": "gutter",
        "path": [
          [
            1339.0,
            0.0
          ],
          [
            1339.0,
            1939.0
          ]
        ],
        "width": 50,
        "extent": [
          1314,
          0,
          1364,
          1939
        ],
        "source": "detector",
        "proposal_id": "proposal-0002",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 50.0,
          "local_xheight_max_px": 13.859404675035648,
          "width_xh": 3.6076585663208793,
          "required_width_px": 21.00883078257797,
          "spacing_sides": [
            {
              "samples": 376,
              "letter_q25_xh": 0.15880951906126828,
              "median_xh": 0.2381102100026649,
              "word_q75_xh": 0.32981830621360153,
              "q90_xh": 1.0105691778820427
            },
            {
              "samples": 523,
              "letter_q25_xh": 0.1513755131513647,
              "median_xh": 0.22877399841884444,
              "word_q75_xh": 0.3196361348165946,
              "q90_xh": 0.8932330624842119
            }
          ],
          "side_row_counts": [
            33,
            53
          ],
          "side_span_xh": [
            85.11007706735903,
            110.72095345942793
          ],
          "shared_span_xh": 84.82117576936804,
          "occupied_rows": 77,
          "bilateral_rows": 52,
          "participants": [
            {
              "line_index": 4,
              "xheight": 13.064702148344452
            },
            {
              "line_index": 6,
              "xheight": 12.798765497094337
            },
            {
              "line_index": 10,
              "xheight": 12.921030454001652
            },
            {
              "line_index": 14,
              "xheight": 12.733612629881804
            },
            {
              "line_index": 16,
              "xheight": 12.797924531069725
            },
            {
              "line_index": 18,
              "xheight": 12.76900878961294
            },
            {
              "line_index": 22,
              "xheight": 12.741376332191862
            },
            {
              "line_index": 24,
              "xheight": 12.971935209783396
            },
            {
              "line_index": 26,
              "xheight": 12.610230606174696
            },
            {
              "line_index": 28,
              "xheight": 12.420255057994495
            },
            {
              "line_index": 30,
              "xheight": 12.793657374368422
            },
            {
              "line_index": 32,
              "xheight": 12.615295104995425
            },
            {
              "line_index": 34,
              "xheight": 12.777495421520825
            },
            {
              "line_index": 36,
              "xheight": 12.731586433293387
            },
            {
              "line_index": 38,
              "xheight": 12.249519387178225
            },
            {
              "line_index": 40,
              "xheight": 12.726750759018387
            },
            {
              "line_index": 42,
              "xheight": 12.463105051572938
            },
            {
              "line_index": 44,
              "xheight": 12.515231817931635
            },
            {
              "line_index": 46,
              "xheight": 12.852904987785905
            },
            {
              "line_index": 48,
              "xheight": 12.6622425465971
            },
            {
              "line_index": 50,
              "xheight": 12.58820412059913
            },
            {
              "line_index": 52,
              "xheight": 12.129188359221644
            },
            {
              "line_index": 56,
              "xheight": 12.123994920099449
            },
            {
              "line_index": 59,
              "xheight": 12.697399350200726
            },
            {
              "line_index": 61,
              "xheight": 12.264502327017908
            },
            {
              "line_index": 63,
              "xheight": 12.167074094562622
            },
            {
              "line_index": 67,
              "xheight": 12.224242117059703
            },
            {
              "line_index": 76,
              "xheight": 12.62932412561213
            },
            {
              "line_index": 77,
              "xheight": 12.181553101187774
            },
            {
              "line_index": 78,
              "xheight": 12.276913289647382
            },
            {
              "line_index": 80,
              "xheight": 11.822349697784148
            },
            {
              "line_index": 82,
              "xheight": 12.095347469831722
            },
            {
              "line_index": 83,
              "xheight": 12.30158002688836
            },
            {
              "line_index": 85,
              "xheight": 11.990186158975376
            },
            {
              "line_index": 86,
              "xheight": 12.537709847522251
            },
            {
              "line_index": 87,
              "xheight": 12.448392777786808
            },
            {
              "line_index": 88,
              "xheight": 12.28513632323245
            },
            {
              "line_index": 89,
              "xheight": 12.39053501702466
            },
            {
              "line_index": 90,
              "xheight": 12.602558840856148
            },
            {
              "line_index": 91,
              "xheight": 12.881958490264026
            },
            {
              "line_index": 92,
              "xheight": 12.471249006466792
            },
            {
              "line_index": 93,
              "xheight": 12.386305731453206
            },
            {
              "line_index": 94,
              "xheight": 12.355846159757562
            },
            {
              "line_index": 95,
              "xheight": 12.234846782509294
            },
            {
              "line_index": 96,
              "xheight": 12.187283178693747
            },
            {
              "line_index": 97,
              "xheight": 12.553891853974392
            },
            {
              "line_index": 98,
              "xheight": 12.546147351569516
            },
            {
              "line_index": 99,
              "xheight": 12.579262854123613
            },
            {
              "line_index": 100,
              "xheight": 12.56501899694706
            },
            {
              "line_index": 101,
              "xheight": 12.569803511438522
            },
            {
              "line_index": 102,
              "xheight": 12.734662913678335
            },
            {
              "line_index": 103,
              "xheight": 12.514229663974561
            },
            {
              "line_index": 104,
              "xheight": 13.0
            },
            {
              "line_index": 105,
              "xheight": 12.792973193475746
            },
            {
              "line_index": 106,
              "xheight": 12.943756045732357
            },
            {
              "line_index": 107,
              "xheight": 13.0019365946996
            },
            {
              "line_index": 108,
              "xheight": 12.754625878096249
            },
            {
              "line_index": 109,
              "xheight": 12.919340463848584
            },
            {
              "line_index": 110,
              "xheight": 13.00376787882135
            },
            {
              "line_index": 111,
              "xheight": 12.967399088434945
            },
            {
              "line_index": 112,
              "xheight": 12.18054031590168
            },
            {
              "line_index": 113,
              "xheight": 12.912201777521204
            },
            {
              "line_index": 114,
              "xheight": 13.113378359141734
            },
            {
              "line_index": 115,
              "xheight": 13.199822412902904
            },
            {
              "line_index": 116,
              "xheight": 13.30226225360002
            },
            {
              "line_index": 117,
              "xheight": 13.070967293270087
            },
            {
              "line_index": 118,
              "xheight": 13.630499483508174
            },
            {
              "line_index": 119,
              "xheight": 13.424693381881752
            },
            {
              "line_index": 120,
              "xheight": 13.205160732573859
            },
            {
              "line_index": 121,
              "xheight": 13.091558014626798
            },
            {
              "line_index": 122,
              "xheight": 12.918051897723672
            },
            {
              "line_index": 123,
              "xheight": 13.087497232327905
            },
            {
              "line_index": 124,
              "xheight": 13.212176516291265
            },
            {
              "line_index": 125,
              "xheight": 13.323991535353343
            },
            {
              "line_index": 126,
              "xheight": 13.373456772711052
            },
            {
              "line_index": 127,
              "xheight": 13.268728930896259
            },
            {
              "line_index": 128,
              "xheight": 13.387541586971793
            },
            {
              "line_index": 129,
              "xheight": 13.859404675035648
            },
            {
              "line_index": 130,
              "xheight": 13.532748791031054
            },
            {
              "line_index": 131,
              "xheight": 13.30832415283362
            },
            {
              "line_index": 132,
              "xheight": 13.314361080057779
            },
            {
              "line_index": 133,
              "xheight": 13.009207491732013
            },
            {
              "line_index": 134,
              "xheight": 12.73200390872762
            },
            {
              "line_index": 135,
              "xheight": 12.739233052728423
            },
            {
              "line_index": 136,
              "xheight": 12.778363110246573
            },
            {
              "line_index": 137,
              "xheight": 13.398400798265357
            }
          ],
          "observed_gap_widths_px": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            52,
            106,
            0.0,
            50,
            50,
            0.0,
            116,
            116,
            51,
            51,
            52,
            52,
            0.0,
            0.0,
            69,
            69,
            0.0,
            84,
            84,
            120,
            62,
            62,
            55,
            55,
            0.0,
            58,
            58,
            114,
            57,
            57,
            57,
            57,
            58,
            58,
            70,
            70,
            0.0,
            60,
            60,
            90,
            61,
            61,
            60,
            60,
            0.0,
            0.0,
            0.0,
            62,
            62,
            68,
            68,
            63,
            63,
            65,
            65,
            0.0,
            93,
            0.0,
            67,
            66,
            71,
            75,
            70,
            0.0,
            135
          ],
          "white_rows": 52,
          "baseline_matching_reach_px": 14.769250000000028,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0000",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            1915.0,
            0.0
          ],
          [
            1915.0,
            1939.0
          ]
        ],
        "width": 30,
        "extent": [
          1900,
          0,
          1930,
          1939
        ],
        "source": "detector",
        "proposal_id": "proposal-0003",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 30.0,
          "local_xheight_max_px": 13.859404675035648,
          "width_xh": 2.1645951397925276,
          "required_width_px": 20.789107012553472,
          "spacing_sides": [
            {
              "samples": 501,
              "letter_q25_xh": 0.15035036611601427,
              "median_xh": 0.1593131455379574,
              "word_q75_xh": 0.24099496646292104,
              "q90_xh": 0.9606326253994948
            },
            {
              "samples": 573,
              "letter_q25_xh": 0.14968392004389025,
              "median_xh": 0.16202863463384506,
              "word_q75_xh": 0.2411096962869151,
              "q90_xh": 0.8634468246963563
            }
          ],
          "side_row_counts": [
            45,
            54
          ],
          "side_span_xh": [
            116.44049927388738,
            116.11819105757229
          ],
          "shared_span_xh": 115.56520915252662,
          "occupied_rows": 98,
          "bilateral_rows": 87,
          "participants": [
            {
              "line_index": 84,
              "xheight": 10.274302607434123
            },
            {
              "line_index": 85,
              "xheight": 11.990186158975376
            },
            {
              "line_index": 87,
              "xheight": 12.448392777786808
            },
            {
              "line_index": 88,
              "xheight": 12.28513632323245
            },
            {
              "line_index": 90,
              "xheight": 12.602558840856148
            },
            {
              "line_index": 92,
              "xheight": 12.471249006466792
            },
            {
              "line_index": 93,
              "xheight": 12.386305731453206
            },
            {
              "line_index": 94,
              "xheight": 12.355846159757562
            },
            {
              "line_index": 95,
              "xheight": 12.234846782509294
            },
            {
              "line_index": 96,
              "xheight": 12.187283178693747
            },
            {
              "line_index": 97,
              "xheight": 12.553891853974392
            },
            {
              "line_index": 98,
              "xheight": 12.546147351569516
            },
            {
              "line_index": 99,
              "xheight": 12.579262854123613
            },
            {
              "line_index": 100,
              "xheight": 12.56501899694706
            },
            {
              "line_index": 101,
              "xheight": 12.569803511438522
            },
            {
              "line_index": 102,
              "xheight": 12.734662913678335
            },
            {
              "line_index": 103,
              "xheight": 12.514229663974561
            },
            {
              "line_index": 104,
              "xheight": 13.0
            },
            {
              "line_index": 105,
              "xheight": 12.792973193475746
            },
            {
              "line_index": 106,
              "xheight": 12.943756045732357
            },
            {
              "line_index": 107,
              "xheight": 13.0019365946996
            },
            {
              "line_index": 109,
              "xheight": 12.919340463848584
            },
            {
              "line_index": 110,
              "xheight": 13.00376787882135
            },
            {
              "line_index": 111,
              "xheight": 12.967399088434945
            },
            {
              "line_index": 113,
              "xheight": 12.912201777521204
            },
            {
              "line_index": 114,
              "xheight": 13.113378359141734
            },
            {
              "line_index": 115,
              "xheight": 13.199822412902904
            },
            {
              "line_index": 116,
              "xheight": 13.30226225360002
            },
            {
              "line_index": 117,
              "xheight": 13.070967293270087
            },
            {
              "line_index": 119,
              "xheight": 13.424693381881752
            },
            {
              "line_index": 120,
              "xheight": 13.205160732573859
            },
            {
              "line_index": 121,
              "xheight": 13.091558014626798
            },
            {
              "line_index": 122,
              "xheight": 12.918051897723672
            },
            {
              "line_index": 123,
              "xheight": 13.087497232327905
            },
            {
              "line_index": 124,
              "xheight": 13.212176516291265
            },
            {
              "line_index": 125,
              "xheight": 13.323991535353343
            },
            {
              "line_index": 126,
              "xheight": 13.373456772711052
            },
            {
              "line_index": 127,
              "xheight": 13.268728930896259
            },
            {
              "line_index": 129,
              "xheight": 13.859404675035648
            },
            {
              "line_index": 130,
              "xheight": 13.532748791031054
            },
            {
              "line_index": 131,
              "xheight": 13.30832415283362
            },
            {
              "line_index": 132,
              "xheight": 13.314361080057779
            },
            {
              "line_index": 133,
              "xheight": 13.009207491732013
            },
            {
              "line_index": 134,
              "xheight": 12.73200390872762
            },
            {
              "line_index": 135,
              "xheight": 12.739233052728423
            },
            {
              "line_index": 136,
              "xheight": 12.778363110246573
            },
            {
              "line_index": 137,
              "xheight": 13.398400798265357
            },
            {
              "line_index": 138,
              "xheight": 10.02851775650035
            },
            {
              "line_index": 139,
              "xheight": 12.343497212820637
            },
            {
              "line_index": 140,
              "xheight": 12.547096845351462
            },
            {
              "line_index": 141,
              "xheight": 12.420710342168036
            },
            {
              "line_index": 142,
              "xheight": 12.617808172137131
            },
            {
              "line_index": 143,
              "xheight": 12.9261330870645
            },
            {
              "line_index": 144,
              "xheight": 12.442469324958495
            },
            {
              "line_index": 145,
              "xheight": 12.491205276747735
            },
            {
              "line_index": 146,
              "xheight": 12.568346942081007
            },
            {
              "line_index": 147,
              "xheight": 12.732495211975902
            },
            {
              "line_index": 148,
              "xheight": 12.548036164911196
            },
            {
              "line_index": 149,
              "xheight": 12.671351342310913
            },
            {
              "line_index": 150,
              "xheight": 12.55140054359947
            },
            {
              "line_index": 151,
              "xheight": 12.233452895924188
            },
            {
              "line_index": 152,
              "xheight": 12.981563992390534
            },
            {
              "line_index": 153,
              "xheight": 12.596093258475776
            },
            {
              "line_index": 154,
              "xheight": 12.726157719334196
            },
            {
              "line_index": 155,
              "xheight": 12.633842847615824
            },
            {
              "line_index": 156,
              "xheight": 12.676865835944682
            },
            {
              "line_index": 157,
              "xheight": 12.768289595668534
            },
            {
              "line_index": 158,
              "xheight": 12.89609523028787
            },
            {
              "line_index": 159,
              "xheight": 12.975263094786328
            },
            {
              "line_index": 160,
              "xheight": 13.098805116399717
            },
            {
              "line_index": 161,
              "xheight": 12.530813271725037
            },
            {
              "line_index": 162,
              "xheight": 12.980099490570637
            },
            {
              "line_index": 163,
              "xheight": 13.087422800393256
            },
            {
              "line_index": 164,
              "xheight": 12.848407775151031
            },
            {
              "line_index": 165,
              "xheight": 12.95686359812862
            },
            {
              "line_index": 166,
              "xheight": 12.583233582506637
            },
            {
              "line_index": 167,
              "xheight": 12.81746190909439
            },
            {
              "line_index": 168,
              "xheight": 12.929162012448614
            },
            {
              "line_index": 169,
              "xheight": 13.108449687600569
            },
            {
              "line_index": 170,
              "xheight": 13.176285021889726
            },
            {
              "line_index": 171,
              "xheight": 13.397582760462456
            },
            {
              "line_index": 172,
              "xheight": 13.367366500406433
            },
            {
              "line_index": 173,
              "xheight": 13.36148865832456
            },
            {
              "line_index": 174,
              "xheight": 13.370028267295993
            },
            {
              "line_index": 175,
              "xheight": 13.196821167842472
            },
            {
              "line_index": 176,
              "xheight": 13.350659503931183
            },
            {
              "line_index": 177,
              "xheight": 13.1926263375708
            },
            {
              "line_index": 178,
              "xheight": 13.398442521426205
            },
            {
              "line_index": 179,
              "xheight": 13.163672416460031
            },
            {
              "line_index": 180,
              "xheight": 13.017284349534748
            },
            {
              "line_index": 181,
              "xheight": 13.612758185482562
            },
            {
              "line_index": 182,
              "xheight": 13.307123866456095
            },
            {
              "line_index": 183,
              "xheight": 13.359573689628633
            },
            {
              "line_index": 184,
              "xheight": 13.593759881515325
            },
            {
              "line_index": 185,
              "xheight": 13.606278202513522
            },
            {
              "line_index": 186,
              "xheight": 13.27452778193333
            },
            {
              "line_index": 187,
              "xheight": 13.205535623738797
            },
            {
              "line_index": 188,
              "xheight": 12.92031383298422
            },
            {
              "line_index": 189,
              "xheight": 12.746533739576307
            },
            {
              "line_index": 190,
              "xheight": 12.714320931505426
            },
            {
              "line_index": 191,
              "xheight": 13.15478617244753
            }
          ],
          "observed_gap_widths_px": [
            37,
            37,
            46,
            46,
            0.0,
            46,
            46,
            46,
            46,
            0.0,
            43,
            43,
            0.0,
            44,
            44,
            43,
            43,
            41,
            41,
            41,
            41,
            49,
            49,
            41,
            41,
            42,
            42,
            40,
            40,
            40,
            40,
            158,
            158,
            39,
            39,
            38,
            38,
            38,
            38,
            70,
            70,
            39,
            78,
            78,
            0.0,
            39,
            39,
            38,
            38,
            39,
            39,
            0.0,
            40,
            40,
            80,
            80,
            38,
            38,
            38,
            38,
            38,
            38,
            0.0,
            38,
            38,
            38,
            38,
            38,
            38,
            158,
            158,
            38,
            38,
            38,
            38,
            39,
            81,
            81,
            40,
            40,
            0.0,
            42,
            42,
            47,
            47,
            73,
            73,
            44,
            44,
            47,
            76,
            76,
            51,
            51,
            138,
            138,
            50,
            50
          ],
          "white_rows": 91,
          "baseline_matching_reach_px": 14.819500000000005,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0001",
        "track_id": "separator-0001"
      },
      {
        "kind": "gutter",
        "path": [
          [
            765.5,
            1379.0
          ],
          [
            765.5,
            1616.0
          ]
        ],
        "width": 35,
        "extent": [
          748,
          1379,
          783,
          1616
        ],
        "source": "detector",
        "proposal_id": "proposal-0024",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 35.0,
          "local_xheight_max_px": 12.62932412561213,
          "width_xh": 2.7713280340173063,
          "required_width_px": 21.18530903078363,
          "spacing_sides": [
            {
              "samples": 73,
              "letter_q25_xh": 0.1614360392772543,
              "median_xh": 0.24677561452873062,
              "word_q75_xh": 0.32912435742245016,
              "q90_xh": 1.1183131585967747
            },
            {
              "samples": 82,
              "letter_q25_xh": 0.16133166247838207,
              "median_xh": 0.16917110820828268,
              "word_q75_xh": 0.3218306057387095,
              "q90_xh": 0.4881245655733915
            }
          ],
          "side_row_counts": [
            6,
            8
          ],
          "side_span_xh": [
            16.336582856527176,
            17.301796820374904
          ],
          "shared_span_xh": 16.336582856527176,
          "occupied_rows": 10,
          "bilateral_rows": 8,
          "participants": [
            {
              "line_index": 68,
              "xheight": 12.504915058701044
            },
            {
              "line_index": 69,
              "xheight": 12.388807412235565
            },
            {
              "line_index": 70,
              "xheight": 12.15346087213402
            },
            {
              "line_index": 72,
              "xheight": 12.156792743598771
            },
            {
              "line_index": 73,
              "xheight": 12.162112265270935
            },
            {
              "line_index": 75,
              "xheight": 12.563299290835403
            },
            {
              "line_index": 76,
              "xheight": 12.62932412561213
            },
            {
              "line_index": 77,
              "xheight": 12.181553101187774
            },
            {
              "line_index": 78,
              "xheight": 12.276913289647382
            },
            {
              "line_index": 79,
              "xheight": 12.428898708432826
            },
            {
              "line_index": 80,
              "xheight": 11.822349697784148
            },
            {
              "line_index": 81,
              "xheight": 12.048097223562081
            },
            {
              "line_index": 82,
              "xheight": 12.095347469831722
            },
            {
              "line_index": 83,
              "xheight": 12.30158002688836
            }
          ],
          "observed_gap_widths_px": [
            39,
            38,
            38,
            39,
            39,
            0.0,
            70,
            38,
            0.0,
            37
          ],
          "white_rows": 8,
          "baseline_matching_reach_px": 14.582749999999919,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0002",
        "track_id": "separator-0003"
      },
      {
        "kind": "gutter",
        "path": [
          [
            1335.5,
            1379.0
          ],
          [
            1335.5,
            1616.0
          ]
        ],
        "width": 43,
        "extent": [
          1314,
          1379,
          1357,
          1616
        ],
        "source": "detector",
        "proposal_id": "proposal-0025",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 43.0,
          "local_xheight_max_px": 13.859404675035648,
          "width_xh": 3.1025863670359564,
          "required_width_px": 21.101497631845508,
          "spacing_sides": [
            {
              "samples": 71,
              "letter_q25_xh": 0.16535283545912263,
              "median_xh": 0.2462740157252594,
              "word_q75_xh": 0.33834221641656537,
              "q90_xh": 1.015026649249696
            },
            {
              "samples": 70,
              "letter_q25_xh": 0.14939262649583984,
              "median_xh": 0.1502818820034646,
              "word_q75_xh": 0.22592733629089606,
              "q90_xh": 0.8335308918146538
            }
          ],
          "side_row_counts": [
            6,
            8
          ],
          "side_span_xh": [
            15.766189466535506,
            14.816076506509232
          ],
          "shared_span_xh": 14.816076506509232,
          "occupied_rows": 11,
          "bilateral_rows": 9,
          "participants": [
            {
              "line_index": 76,
              "xheight": 12.62932412561213
            },
            {
              "line_index": 77,
              "xheight": 12.181553101187774
            },
            {
              "line_index": 78,
              "xheight": 12.276913289647382
            },
            {
              "line_index": 80,
              "xheight": 11.822349697784148
            },
            {
              "line_index": 82,
              "xheight": 12.095347469831722
            },
            {
              "line_index": 83,
              "xheight": 12.30158002688836
            },
            {
              "line_index": 125,
              "xheight": 13.323991535353343
            },
            {
              "line_index": 126,
              "xheight": 13.373456772711052
            },
            {
              "line_index": 127,
              "xheight": 13.268728930896259
            },
            {
              "line_index": 128,
              "xheight": 13.387541586971793
            },
            {
              "line_index": 129,
              "xheight": 13.859404675035648
            },
            {
              "line_index": 130,
              "xheight": 13.532748791031054
            },
            {
              "line_index": 131,
              "xheight": 13.30832415283362
            },
            {
              "line_index": 132,
              "xheight": 13.314361080057779
            }
          ],
          "observed_gap_widths_px": [
            68,
            68,
            63,
            63,
            65,
            65,
            0.0,
            93,
            0.0,
            67,
            66
          ],
          "white_rows": 9,
          "baseline_matching_reach_px": 14.612250000000131,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0003",
        "track_id": "separator-0000"
      },
      {
        "kind": "gutter",
        "path": [
          [
            1358.0,
            1616.0
          ],
          [
            1358.0,
            1852.0
          ]
        ],
        "width": 38,
        "extent": [
          1339,
          1616,
          1377,
          1852
        ],
        "source": "detector",
        "proposal_id": "proposal-0028",
        "evidence": {
          "method": "line-local-spacing-v1",
          "accepted": true,
          "checks": {
            "spacing_observed": true,
            "wide_at_local_scale": true,
            "separate_blocks": true,
            "persistent": true,
            "bilateral_support": true,
            "original_whitespace": true
          },
          "width_px": 38.0,
          "local_xheight_max_px": 13.398400798265357,
          "width_xh": 2.8361593724618035,
          "required_width_px": 20.097601197398035,
          "spacing_sides": [
            {
              "samples": 34,
              "letter_q25_xh": 0.16360932488476104,
              "median_xh": 0.24599053647279384,
              "word_q75_xh": 0.32837174806082664,
              "q90_xh": 0.895095134278548
            },
            {
              "samples": 54,
              "letter_q25_xh": 0.15373726656839762,
              "median_xh": 0.19049589106037895,
              "word_q75_xh": 0.23562669486329169,
              "q90_xh": 0.8284570798506854
            }
          ],
          "side_row_counts": [
            4,
            5
          ],
          "side_span_xh": [
            8.689581820471691,
            8.789817663556317
          ],
          "shared_span_xh": 8.390740185541759,
          "occupied_rows": 5,
          "bilateral_rows": 4,
          "participants": [
            {
              "line_index": 59,
              "xheight": 12.697399350200726
            },
            {
              "line_index": 61,
              "xheight": 12.264502327017908
            },
            {
              "line_index": 63,
              "xheight": 12.167074094562622
            },
            {
              "line_index": 67,
              "xheight": 12.224242117059703
            },
            {
              "line_index": 133,
              "xheight": 13.009207491732013
            },
            {
              "line_index": 134,
              "xheight": 12.73200390872762
            },
            {
              "line_index": 135,
              "xheight": 12.739233052728423
            },
            {
              "line_index": 136,
              "xheight": 12.778363110246573
            },
            {
              "line_index": 137,
              "xheight": 13.398400798265357
            }
          ],
          "observed_gap_widths_px": [
            71,
            75,
            70,
            0.0,
            135
          ],
          "white_rows": 4,
          "baseline_matching_reach_px": 14.558749999999975,
          "interpiece_spacing_samples": [
            0,
            0
          ]
        },
        "id": "boundary-0004",
        "track_id": "separator-0000"
      },
      {
        "kind": "fold",
        "path": [
          [
            1339.0,
            0.0
          ],
          [
            1339.0,
            1939.0
          ]
        ],
        "width": 50,
        "extent": [
          1314,
          0,
          1364,
          1939
        ],
        "source": "inferred-wide-scan-central-separation",
        "proposal_id": "proposal-0034",
        "evidence": {
          "method": "spread-fold",
          "accepted": true,
          "source": "inferred-wide-scan-central-separation"
        },
        "id": "boundary-0006",
        "track_id": "separator-0002"
      }
    ],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            1335.788096031111,
            0
          ],
          [
            1340.857846565066,
            1938
          ]
        ],
        "radius": 2.75,
        "source": "continued_rule",
        "proposal_id": "proposal-0033",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": true,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": false
          },
          "xheight_px": 12.736947983203379,
          "support_fraction": 0.11606217616580311,
          "supported_rows": 8,
          "thin_support_fraction": 0.03571428571428571,
          "original_ink_rows": 224,
          "sampled_rows": 1939,
          "extent_xh": 151.52766601113177,
          "thickness_q90_xh": 0.15702348809443706,
          "residual_q90_xh": 0.05495726189276561,
          "dash_lengths_xh": [
            2.9834462737943044,
            3.6115402261720524,
            1.6487466249915892,
            1.7272583690388077,
            1.5702348809443707,
            1.177676160708278,
            1.7272583690388077,
            2.5908875535582117,
            0.07851174404721853,
            0.47107046428331123
          ],
          "gap_lengths_xh": [
            3.847075458313708,
            4.31814592259702,
            0.7851174404721853,
            0.15702348809443706,
            0.3925587202360927,
            0.15702348809443706,
            3.6115402261720524,
            84.55714833885436,
            36.115402261720526
          ],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            1336.5284636210909,
            0.0
          ],
          [
            1339.9464117606235,
            1939.0
          ]
        ],
        "id": "boundary-0005",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "sustained_straight_thin_ink",
          "isolated_thin_support",
          "no_long_unprinted_gap"
        ]
      }
    ],
    "inventory_sha256": "573d9856cc53382870dcecfec69ca729607ceeee61428d21dd75818ea32711d3"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": 0,
    "axis_confidence": 0.9213302264791973,
    "polarity_confidence": 0.7142857142857143,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--175d8def80c70cfd--s000-l0142

Card `k69ae28f853`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/4a4c3365058ec612b720949f96de6921c6a88e8e4182e0ea3b8d34bfb35846a9.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/4a4c3365058ec612b720949f96de6921c6a88e8e4182e0ea3b8d34bfb35846a9.png`; SHA-256 `4a4c3365058ec612b720949f96de6921c6a88e8e4182e0ea3b8d34bfb35846a9`.

Triggers: {"mismatches": {"geometry_unavailable": "FN", "crossing": "FN"}, "flag": false, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k69ae28f853",
  "letters": "y",
  "marks": "y",
  "crop_ok": "y",
  "errors": [],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "yes",
  "rotated_reason": "The complete line runs vertically, rotated approximately 90 degrees.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--175d8def80c70cfd--s000-l0142"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": true,
  "neighbour_words": true,
  "orientation": true,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": true,
  "composed": {
    "measured_drop": true,
    "geometry_unavailable": false,
    "drop": true,
    "orientation_status": "measured",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00168",
  "neighbour_rows": [
    {
      "row_id": "row-00167",
      "column_id": "single:column-0000",
      "xheight": 7.5,
      "profile_runs": [
        [
          1046,
          1060
        ],
        [
          1066,
          1081
        ]
      ],
      "profile_gaps": [
        [
          1060,
          1066
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1046,
            745,
            1060,
            753
          ],
          "body_count": 1,
          "width_xh": 1.8666666666666667,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00190",
      "column_id": "single:column-0000",
      "xheight": 7.0,
      "profile_runs": [
        [
          1042,
          1059
        ],
        [
          1070,
          1080
        ]
      ],
      "profile_gaps": [
        [
          1059,
          1070
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1041,
            823,
            1059,
            831
          ],
          "body_count": 1,
          "width_xh": 2.5714285714285716,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      1036,
      689,
      1065,
      853
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00167",
      "row-00190"
    ],
    "supported_row_count": 2,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00167",
          "row-00190"
        ],
        "count": 2
      }
    ],
    "merged": true
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00167",
      "column_id": "single:column-0000",
      "xheight": 7.5,
      "assigned_pixels": 77,
      "supported": null,
      "runs": [
        {
          "x0": 1046,
          "x1": 1060,
          "body_cut_fraction": 0.0,
          "body_pixels": 68,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00168",
      "column_id": "single:column-0000",
      "xheight": 9.0,
      "assigned_pixels": 221,
      "supported": null,
      "runs": [
        {
          "x0": 1042,
          "x1": 1057,
          "body_cut_fraction": 0.0,
          "body_pixels": 88,
          "body_extent_px": 9,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00190",
      "column_id": "single:column-0000",
      "xheight": 7.0,
      "assigned_pixels": 173,
      "supported": null,
      "runs": [
        {
          "x0": 1042,
          "x1": 1056,
          "body_cut_fraction": 0.0,
          "body_pixels": 49,
          "body_extent_px": 6,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 509,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "validated": [],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            232.46903528938904,
            1461
          ],
          [
            228.76373080617904,
            2054
          ]
        ],
        "radius": 3.2199999999999998,
        "source": "direct_rule",
        "proposal_id": "proposal-0047",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 20.0,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 594,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            232.45918043835772,
            1461.0
          ],
          [
            228.7331816168063,
            2054.0
          ]
        ],
        "id": "boundary-0000",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      }
    ],
    "inventory_sha256": "61acc42a55513a6d72c0ad0e91d36dabb9b03656f82df7722d63f7228b6d0ece"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "vertical",
    "orientation_cw": null,
    "axis_confidence": 0.5334955565238337,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--990bd5a6e79a5eda--s000-l0011

Card `k1814c0830b`; context `segcp7_b`; reader truth **KEEP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/5f7134ce9b73aaec2580da4e4abb771de65df958ba7b4c64e0bc139918ba10ec.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/5f7134ce9b73aaec2580da4e4abb771de65df958ba7b4c64e0bc139918ba10ec.png`; SHA-256 `5f7134ce9b73aaec2580da4e4abb771de65df958ba7b4c64e0bc139918ba10ec`.

Triggers: {"mismatches": {}, "flag": true, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k1814c0830b",
  "letters": "y",
  "marks": "n",
  "crop_ok": "y",
  "errors": [
    "missing_mark"
  ],
  "detail": "Λικοτϊναρέ → Λικοτιναρέ",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "no",
  "rotated_reason": "The text follows its normal horizontal reading axis.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--990bd5a6e79a5eda--s000-l0011"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": false,
  "neighbour_words": false,
  "orientation": false,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": false,
  "composed": {
    "measured_drop": false,
    "geometry_unavailable": false,
    "drop": false,
    "orientation_status": "measured",
    "verified_keep": true,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00008",
  "neighbour_rows": [
    {
      "row_id": "row-00007",
      "column_id": "single:column-0000",
      "xheight": 12.21241274581439,
      "profile_runs": [
        [
          109,
          125
        ],
        [
          126,
          162
        ],
        [
          163,
          187
        ],
        [
          188,
          198
        ],
        [
          199,
          216
        ],
        [
          217,
          230
        ],
        [
          231,
          241
        ],
        [
          243,
          248
        ],
        [
          249,
          261
        ],
        [
          262,
          286
        ],
        [
          300,
          312
        ],
        [
          313,
          325
        ],
        [
          326,
          331
        ],
        [
          346,
          357
        ],
        [
          358,
          370
        ],
        [
          372,
          381
        ],
        [
          383,
          393
        ],
        [
          395,
          404
        ],
        [
          406,
          411
        ],
        [
          412,
          423
        ],
        [
          424,
          437
        ],
        [
          438,
          448
        ],
        [
          449,
          459
        ],
        [
          472,
          483
        ],
        [
          484,
          494
        ],
        [
          496,
          501
        ],
        [
          502,
          519
        ],
        [
          520,
          529
        ],
        [
          531,
          535
        ],
        [
          550,
          562
        ],
        [
          563,
          582
        ],
        [
          595,
          608
        ],
        [
          609,
          617
        ],
        [
          619,
          628
        ],
        [
          630,
          635
        ],
        [
          636,
          647
        ],
        [
          648,
          658
        ],
        [
          660,
          664
        ],
        [
          666,
          676
        ],
        [
          678,
          690
        ],
        [
          691,
          708
        ],
        [
          709,
          718
        ],
        [
          732,
          742
        ],
        [
          744,
          754
        ],
        [
          756,
          806
        ],
        [
          808,
          817
        ]
      ],
      "profile_gaps": [
        [
          125,
          126
        ],
        [
          162,
          163
        ],
        [
          187,
          188
        ],
        [
          198,
          199
        ],
        [
          216,
          217
        ],
        [
          230,
          231
        ],
        [
          241,
          243
        ],
        [
          248,
          249
        ],
        [
          261,
          262
        ],
        [
          286,
          300
        ],
        [
          312,
          313
        ],
        [
          325,
          326
        ],
        [
          331,
          346
        ],
        [
          357,
          358
        ],
        [
          370,
          372
        ],
        [
          381,
          383
        ],
        [
          393,
          395
        ],
        [
          404,
          406
        ],
        [
          411,
          412
        ],
        [
          423,
          424
        ],
        [
          437,
          438
        ],
        [
          448,
          449
        ],
        [
          459,
          472
        ],
        [
          483,
          484
        ],
        [
          494,
          496
        ],
        [
          501,
          502
        ],
        [
          519,
          520
        ],
        [
          529,
          531
        ],
        [
          535,
          550
        ],
        [
          562,
          563
        ],
        [
          582,
          595
        ],
        [
          608,
          609
        ],
        [
          617,
          619
        ],
        [
          628,
          630
        ],
        [
          635,
          636
        ],
        [
          647,
          648
        ],
        [
          658,
          660
        ],
        [
          664,
          666
        ],
        [
          676,
          678
        ],
        [
          690,
          691
        ],
        [
          708,
          709
        ],
        [
          718,
          732
        ],
        [
          742,
          744
        ],
        [
          754,
          756
        ],
        [
          806,
          808
        ]
      ],
      "directional_missing": {
        "above": 17973,
        "below": 0
      },
      "groups": [
        {
          "box": [
            108,
            380,
            286,
            407
          ],
          "body_count": 14,
          "width_xh": 14.575334432666196,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            300,
            381,
            459,
            407
          ],
          "body_count": 13,
          "width_xh": 13.01954030783104,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            472,
            389,
            535,
            408
          ],
          "body_count": 7,
          "width_xh": 5.158685782348148,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            595,
            389,
            718,
            408
          ],
          "body_count": 11,
          "width_xh": 10.071719860774955,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            732,
            382,
            817,
            409
          ],
          "body_count": 7,
          "width_xh": 6.960131611104644,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00009",
      "column_id": "single:column-0000",
      "xheight": 12.798057416007623,
      "profile_runs": [
        [
          141,
          187
        ],
        [
          197,
          220
        ],
        [
          221,
          231
        ],
        [
          242,
          250
        ],
        [
          251,
          264
        ],
        [
          265,
          277
        ],
        [
          279,
          301
        ],
        [
          303,
          332
        ],
        [
          343,
          358
        ],
        [
          359,
          372
        ],
        [
          373,
          384
        ],
        [
          385,
          397
        ],
        [
          398,
          408
        ],
        [
          410,
          419
        ],
        [
          421,
          437
        ],
        [
          438,
          448
        ],
        [
          449,
          459
        ],
        [
          461,
          471
        ],
        [
          482,
          491
        ],
        [
          493,
          503
        ],
        [
          504,
          515
        ],
        [
          526,
          540
        ],
        [
          544,
          547
        ],
        [
          560,
          576
        ],
        [
          577,
          600
        ],
        [
          601,
          624
        ],
        [
          625,
          635
        ],
        [
          637,
          641
        ]
      ],
      "profile_gaps": [
        [
          187,
          197
        ],
        [
          220,
          221
        ],
        [
          231,
          242
        ],
        [
          250,
          251
        ],
        [
          264,
          265
        ],
        [
          277,
          279
        ],
        [
          301,
          303
        ],
        [
          332,
          343
        ],
        [
          358,
          359
        ],
        [
          372,
          373
        ],
        [
          384,
          385
        ],
        [
          397,
          398
        ],
        [
          408,
          410
        ],
        [
          419,
          421
        ],
        [
          437,
          438
        ],
        [
          448,
          449
        ],
        [
          459,
          461
        ],
        [
          471,
          482
        ],
        [
          491,
          493
        ],
        [
          503,
          504
        ],
        [
          515,
          526
        ],
        [
          540,
          544
        ],
        [
          547,
          560
        ],
        [
          576,
          577
        ],
        [
          600,
          601
        ],
        [
          624,
          625
        ],
        [
          635,
          637
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 15681
      },
      "groups": [
        {
          "box": [
            141,
            436,
            187,
            455
          ],
          "body_count": 4,
          "width_xh": 3.5942954860058585,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            242,
            437,
            515,
            462
          ],
          "body_count": 20,
          "width_xh": 21.331362340860856,
          "complete": false,
          "resolved": false,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            526,
            437,
            641,
            457
          ],
          "body_count": 9,
          "width_xh": 8.985738715014646,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      137,
      404,
      821,
      438
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00008"
    ],
    "supported_row_count": 1,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00008"
        ],
        "count": 1
      }
    ],
    "merged": false
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00007",
      "column_id": "single:column-0000",
      "xheight": 12.21241274581439,
      "assigned_pixels": 179,
      "supported": null,
      "runs": []
    },
    {
      "row_id": "row-00008",
      "column_id": "single:column-0000",
      "xheight": 12.65859800070956,
      "assigned_pixels": 4645,
      "supported": null,
      "runs": [
        {
          "x0": 141,
          "x1": 174,
          "body_cut_fraction": 0.0,
          "body_pixels": 239,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 175,
          "x1": 185,
          "body_cut_fraction": 0.0,
          "body_pixels": 75,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 187,
          "x1": 196,
          "body_cut_fraction": 0.0,
          "body_pixels": 69,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 203,
          "x1": 214,
          "body_cut_fraction": 0.0,
          "body_pixels": 88,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 215,
          "x1": 233,
          "body_cut_fraction": 0.0,
          "body_pixels": 132,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 235,
          "x1": 239,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 241,
          "x1": 251,
          "body_cut_fraction": 0.0,
          "body_pixels": 79,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 253,
          "x1": 265,
          "body_cut_fraction": 0.0,
          "body_pixels": 90,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 266,
          "x1": 277,
          "body_cut_fraction": 0.0,
          "body_pixels": 84,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 278,
          "x1": 288,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 290,
          "x1": 299,
          "body_cut_fraction": 0.0,
          "body_pixels": 65,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 307,
          "x1": 332,
          "body_cut_fraction": 0.0,
          "body_pixels": 177,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 334,
          "x1": 343,
          "body_cut_fraction": 0.0,
          "body_pixels": 72,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 345,
          "x1": 367,
          "body_cut_fraction": 0.0,
          "body_pixels": 155,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 370,
          "x1": 375,
          "body_cut_fraction": 0.0,
          "body_pixels": 18,
          "body_extent_px": 5,
          "complete": false
        },
        {
          "x0": 383,
          "x1": 397,
          "body_cut_fraction": 0.0,
          "body_pixels": 77,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 398,
          "x1": 449,
          "body_cut_fraction": 0.0,
          "body_pixels": 319,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 457,
          "x1": 468,
          "body_cut_fraction": 0.0,
          "body_pixels": 82,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 470,
          "x1": 482,
          "body_cut_fraction": 0.0,
          "body_pixels": 95,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 484,
          "x1": 489,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 496,
          "x1": 502,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 504,
          "x1": 511,
          "body_cut_fraction": 0.0,
          "body_pixels": 51,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 514,
          "x1": 518,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 519,
          "x1": 531,
          "body_cut_fraction": 0.0,
          "body_pixels": 89,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 532,
          "x1": 542,
          "body_cut_fraction": 0.0,
          "body_pixels": 76,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 543,
          "x1": 553,
          "body_cut_fraction": 0.0,
          "body_pixels": 60,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 554,
          "x1": 583,
          "body_cut_fraction": 0.0,
          "body_pixels": 215,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 584,
          "x1": 594,
          "body_cut_fraction": 0.0,
          "body_pixels": 86,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 596,
          "x1": 603,
          "body_cut_fraction": 0.0,
          "body_pixels": 64,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 611,
          "x1": 644,
          "body_cut_fraction": 0.0,
          "body_pixels": 228,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 652,
          "x1": 668,
          "body_cut_fraction": 0.0,
          "body_pixels": 107,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 670,
          "x1": 680,
          "body_cut_fraction": 0.0,
          "body_pixels": 83,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 682,
          "x1": 697,
          "body_cut_fraction": 0.0,
          "body_pixels": 96,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 698,
          "x1": 732,
          "body_cut_fraction": 0.0,
          "body_pixels": 233,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 733,
          "x1": 742,
          "body_cut_fraction": 0.0,
          "body_pixels": 63,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 744,
          "x1": 766,
          "body_cut_fraction": 0.0,
          "body_pixels": 169,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 773,
          "x1": 788,
          "body_cut_fraction": 0.0,
          "body_pixels": 91,
          "body_extent_px": 13,
          "complete": true
        },
        {
          "x0": 789,
          "x1": 809,
          "body_cut_fraction": 0.0,
          "body_pixels": 141,
          "body_extent_px": 12,
          "complete": true
        },
        {
          "x0": 810,
          "x1": 817,
          "body_cut_fraction": 0.0,
          "body_pixels": 20,
          "body_extent_px": 3,
          "complete": false
        }
      ]
    },
    {
      "row_id": "row-00009",
      "column_id": "single:column-0000",
      "xheight": 12.798057416007623,
      "assigned_pixels": 43,
      "supported": null,
      "runs": []
    }
  ],
  "omitted_zero_ink_rows": 127,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "inventory_sha256": "5df238704660c71b1883a5cb0ff327b578da53d8bcd7ea62202c8c18ca8d8f2f"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "horizontal",
    "orientation_cw": null,
    "axis_confidence": 0.3406261316430365,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.

## gazette_modern--4902d5359ff861d2--s000-l0170

Card `k93c8e4509b`; context `segcp7_b`; reader truth **DROP**.

Crop: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7_b/r1/crops/cb94439a2d61b472ba91f712f992c50b2e5acadaa13205d2894b89f67d490427.png`

Byte-identical repository crop: `docs/records/harvest/collect_v3_admission/seg/cp7/crops/cb94439a2d61b472ba91f712f992c50b2e5acadaa13205d2894b89f67d490427.png`; SHA-256 `cb94439a2d61b472ba91f712f992c50b2e5acadaa13205d2894b89f67d490427`.

Triggers: {"mismatches": {"geometry_unavailable": "FN", "crossing": "FN"}, "flag": false, "unreadable": false}.

Reader answers and one-line reasons:

```json
{
  "card_id": "k93c8e4509b",
  "letters": "y",
  "marks": "y",
  "crop_ok": "y",
  "errors": [],
  "detail": "",
  "neighbour_whole_word": "no",
  "neighbour_whole_word_reason": "No complete word from another line is visible.",
  "multi_line": "no",
  "multi_line_reason": "Only one complete printed line is visible.",
  "rotated": "yes",
  "rotated_reason": "The complete line runs vertically, rotated approximately 90 degrees.",
  "horizontally_missegmented": "no",
  "horizontally_missegmented_reason": "The line is continuous within one column.",
  "line_id": "gazette_modern--4902d5359ff861d2--s000-l0170"
}
```

Sealed screen decisions (null remains unknown/unavailable):

```json
{
  "merged": true,
  "neighbour_words": true,
  "orientation": true,
  "orientation_unknown": false,
  "geometry_unavailable": false,
  "screen_drop": true,
  "composed": {
    "measured_drop": true,
    "geometry_unavailable": false,
    "drop": true,
    "orientation_status": "measured",
    "verified_keep": false,
    "crossing_status": "measured"
  }
}
```

Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):

```json
{
  "structural_status": "measured",
  "structural_reason": null,
  "target_row_id": "row-00209",
  "neighbour_rows": [
    {
      "row_id": "row-00210",
      "column_id": "single:column-0002",
      "xheight": 8.5,
      "profile_runs": [
        [
          1147,
          1156
        ],
        [
          1167,
          1174
        ]
      ],
      "profile_gaps": [
        [
          1156,
          1167
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1167,
            721,
            1177,
            731
          ],
          "body_count": 1,
          "width_xh": 1.1764705882352942,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00211",
      "column_id": "single:column-0002",
      "xheight": 8.0,
      "profile_runs": [
        [
          1147,
          1160
        ],
        [
          1164,
          1174
        ]
      ],
      "profile_gaps": [
        [
          1160,
          1164
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1146,
            739,
            1160,
            748
          ],
          "body_count": 1,
          "width_xh": 1.75,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": false
        },
        {
          "box": [
            1164,
            741,
            1178,
            751
          ],
          "body_count": 1,
          "width_xh": 1.75,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00212",
      "column_id": "single:column-0002",
      "xheight": 7.5,
      "profile_runs": [
        [
          1147,
          1156
        ],
        [
          1167,
          1174
        ]
      ],
      "profile_gaps": [
        [
          1156,
          1167
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1167,
            776,
            1177,
            796
          ],
          "body_count": 1,
          "width_xh": 1.3333333333333333,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00213",
      "column_id": "single:column-0002",
      "xheight": 7.5,
      "profile_runs": [
        [
          1147,
          1156
        ],
        [
          1163,
          1174
        ]
      ],
      "profile_gaps": [
        [
          1156,
          1163
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 0
      },
      "groups": [
        {
          "box": [
            1163,
            796,
            1177,
            807
          ],
          "body_count": 1,
          "width_xh": 1.8666666666666667,
          "complete": true,
          "resolved": true,
          "positive": true,
          "unresolved": false
        }
      ]
    },
    {
      "row_id": "row-00216",
      "column_id": "single:column-0002",
      "xheight": 6.5,
      "profile_runs": [
        [
          1147,
          1156
        ],
        [
          1163,
          1174
        ]
      ],
      "profile_gaps": [
        [
          1156,
          1163
        ]
      ],
      "directional_missing": {
        "above": 0,
        "below": 30
      },
      "groups": [
        {
          "box": [
            1163,
            825,
            1176,
            830
          ],
          "body_count": 1,
          "width_xh": 2.0,
          "complete": false,
          "resolved": true,
          "positive": false,
          "unresolved": true
        }
      ]
    }
  ],
  "row_inclusion": {
    "status": "measured",
    "decision_status": "unqualified_cp3",
    "crop_box": [
      1159,
      622,
      1184,
      835
    ],
    "invalid_geometry_count": 0,
    "supported_row_ids": [
      "row-00203",
      "row-00204",
      "row-00205",
      "row-00206",
      "row-00209",
      "row-00210",
      "row-00211",
      "row-00212",
      "row-00213",
      "row-00216"
    ],
    "supported_row_count": 10,
    "columns": [
      {
        "page_side": "single",
        "column_id": "single:column-0000",
        "row_ids": [
          "row-00203",
          "row-00204",
          "row-00205",
          "row-00206"
        ],
        "count": 4
      },
      {
        "page_side": "single",
        "column_id": "single:column-0002",
        "row_ids": [
          "row-00209",
          "row-00210",
          "row-00211",
          "row-00212",
          "row-00213",
          "row-00216"
        ],
        "count": 6
      }
    ],
    "merged": true
  },
  "row_inclusion_rows": [
    {
      "row_id": "row-00203",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 50,
      "supported": null,
      "runs": [
        {
          "x0": 1165,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 50,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00204",
      "column_id": "single:column-0000",
      "xheight": 8.5,
      "assigned_pixels": 47,
      "supported": null,
      "runs": [
        {
          "x0": 1169,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 32,
          "body_extent_px": 8,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00205",
      "column_id": "single:column-0000",
      "xheight": 6.0,
      "assigned_pixels": 25,
      "supported": null,
      "runs": [
        {
          "x0": 1168,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 25,
          "body_extent_px": 6,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00206",
      "column_id": "single:column-0000",
      "xheight": 10.0,
      "assigned_pixels": 40,
      "supported": null,
      "runs": [
        {
          "x0": 1168,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 40,
          "body_extent_px": 10,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00209",
      "column_id": "single:column-0002",
      "xheight": 8.5,
      "assigned_pixels": 44,
      "supported": null,
      "runs": [
        {
          "x0": 1167,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 44,
          "body_extent_px": 8,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00210",
      "column_id": "single:column-0002",
      "xheight": 8.5,
      "assigned_pixels": 41,
      "supported": null,
      "runs": [
        {
          "x0": 1167,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 9,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00211",
      "column_id": "single:column-0002",
      "xheight": 8.0,
      "assigned_pixels": 54,
      "supported": null,
      "runs": [
        {
          "x0": 1159,
          "x1": 1160,
          "body_cut_fraction": 0.0,
          "body_pixels": 1,
          "body_extent_px": 1,
          "complete": false
        },
        {
          "x0": 1164,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 37,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00212",
      "column_id": "single:column-0002",
      "xheight": 7.5,
      "assigned_pixels": 77,
      "supported": null,
      "runs": [
        {
          "x0": 1167,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 29,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00213",
      "column_id": "single:column-0002",
      "xheight": 7.5,
      "assigned_pixels": 51,
      "supported": null,
      "runs": [
        {
          "x0": 1163,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 42,
          "body_extent_px": 7,
          "complete": true
        }
      ]
    },
    {
      "row_id": "row-00216",
      "column_id": "single:column-0002",
      "xheight": 6.5,
      "assigned_pixels": 34,
      "supported": null,
      "runs": [
        {
          "x0": 1163,
          "x1": 1174,
          "body_cut_fraction": 0.0,
          "body_pixels": 34,
          "body_extent_px": 5,
          "complete": true
        }
      ]
    }
  ],
  "omitted_zero_ink_rows": 577,
  "crossing": {
    "status": "measured",
    "reason": null,
    "drop": false,
    "crossings": [],
    "validated": [],
    "rejected": [
      {
        "kind": "rule",
        "path": [
          [
            321.9714855483185,
            711
          ],
          [
            318.6245786933466,
            1691
          ]
        ],
        "radius": 2.2199999999999998,
        "source": "direct_rule",
        "proposal_id": "proposal-0066",
        "evidence": {
          "method": "original-thin-stroke-v1",
          "accepted": false,
          "checks": {
            "long_enough": false,
            "sustained_straight_thin_ink": false,
            "isolated_thin_support": false,
            "no_long_unprinted_gap": true
          },
          "xheight_px": 10.0,
          "support_fraction": 0.0,
          "supported_rows": 0,
          "thin_support_fraction": 0.0,
          "original_ink_rows": 0,
          "sampled_rows": 981,
          "extent_xh": 0.0,
          "thickness_q90_xh": null,
          "residual_q90_xh": null,
          "dash_lengths_xh": [],
          "gap_lengths_xh": [],
          "style": "unsupported"
        },
        "proposal_path": [
          [
            322.4763035353721,
            711.0
          ],
          [
            316.58490321440445,
            1691.0
          ]
        ],
        "id": "boundary-0000",
        "track_id": "separator-0000",
        "rejection_reasons": [
          "long_enough",
          "sustained_straight_thin_ink",
          "isolated_thin_support"
        ]
      }
    ],
    "inventory_sha256": "55a811b6e02453f61558c62e4fb9f2e0dd6df32baf6c677058334542862091a2"
  },
  "axis": {
    "status": "measured",
    "reason": null,
    "decision_source": "measured",
    "source": "native_crop_toolkit",
    "axis": "vertical",
    "orientation_cw": null,
    "axis_confidence": 0.5308397886753313,
    "polarity_confidence": 0.0,
    "regional": null,
    "regional_evidence": null
  }
}
```

Lead pixel adjudication: **pending**.
