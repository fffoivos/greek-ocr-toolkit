# R-eff: independent review of adjudication efficiency

17 October 2026. Offline, read-only review; the sole repository write is this report. No readers were started or resumed, and the live `collect_v3/` package was neither imported nor changed.

**Verdict: the primary E1 scores satisfy the owner's observed E0-repeat tolerance on both beds, and the recorded token saving is substantial. The conclusion is not certain. Practical reliance is OK with conditions, within the tested sizes and endpoints.** A stronger claim covering every protocol answer needs qualification: yer `pre1918=unclear` rises in E1, although the scorer's glyph `u`/`other` counts do not.

## Reproduction and scope

I ran the supplied [score.py](score.py) with Python `-B`, all 20 existing BSB/yer output files, the four partial owner39 answer files, and measured usage transcribed from `usage_log.tsv`. Both original C1 BSB verdict partitions, both `ink_*.jsonl` partitions, and the yer table were supplied as cross-check arguments. The scorer exited 0; its external-reference checks matched the fixed primary truth snapshot. Outputs and helper files are in `/tmp/r-eff-thuwwy8w/`, including `scores.json`, `command.json`, `verdicts.json`, `usage.json`, `positions.json`, and input hashes. Because `--output` refuses a path outside `efficiency/`, I redirected scorer stdout to the temporary score file instead of changing the scorer.

For a repeat, the exact invocation is stored in `command.json`. In abbreviated form:

```sh
python3 -B docs/records/harvest/collect_v3/c1/efficiency/score.py \
  --verdicts /tmp/r-eff-thuwwy8w/verdicts.json \
  --usage /tmp/r-eff-thuwwy8w/usage.json \
  --bsb-truth docs/records/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl \
  --bsb-truth docs/records/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__b.jsonl \
  --yer-truth docs/records/harvest/collect_v3/c1/yer_adjudication/ink_a.jsonl \
  --yer-truth docs/records/harvest/collect_v3/c1/yer_adjudication/ink_b.jsonl \
  --yer-table docs/records/harvest/collect_v3/c1/yer_adjudication/table.json \
  > /tmp/r-eff-thuwwy8w/scores.json
```

The complete arms have no missing items or slots. Each BSB/yer item gets **one read per arm**: E0's two readers divide the bed; E1's one reader covers it all. Thus E1 reduces contexts, not reads per item. This does not establish the quality of a future two-reader consensus or resolver.

“Truth” below means the supplied scoring reference. BSB uses earlier C1 reader verdicts, not an independent owner adjudication. Yer uses blind ink adjudication: 65 slots in **31** items, with 28 zero-slot items; truth has 52 hard signs and 13 soft signs, one slot marked low confidence. Agreement is not proof of physical correctness.

## Complete-arm score tables

Every cell is **agreements / compared units**. BSB joint equality requires all three fields on a card; the three fields are not 300 independent observations.

| BSB comparison | Letters | Crop | Marks | All three per card |
| --- | ---: | ---: | ---: | ---: |
| **E0a–E0b variance bar** | **98/100** | **97/100** | **97/100** | **93/100** |
| E0a vs C1 truth | 100/100 | 98/100 | 96/100 | 95/100 |
| E0b vs C1 truth | 98/100 | 99/100 | 99/100 | 96/100 |
| **E1 vs C1 truth** | **100/100** | **99/100** | **98/100** | **97/100** |
| E2 vs C1 truth | 99/100 | 97/100 | 98/100 | 94/100 |
| E0a vs E0a | 100/100 | 100/100 | 100/100 | 100/100 |
| E0b vs E0a | 98/100 | 97/100 | 97/100 | 93/100 |
| **E1 vs E0a** | **100/100** | **97/100** | **98/100** | **95/100** |
| E2 vs E0a | 99/100 | 97/100 | 96/100 | 93/100 |

All four complete BSB arms have **0/100 cards with `u`**, and zero `u` in every field. The cache's “96 / 94 / 90” for E1 counts *passing labels*, not agreement with truth. Truth itself has 96 letters-y, 95 crop-y and 92 marks-y cards; matching those marginal counts would not establish matching decisions.

| Yer comparison | Slot equality | All slots per item | Slot-bearing items only |
| --- | ---: | ---: | ---: |
| **E0a–E0b variance bar** | **64/65** | **58/59** | **30/31** |
| E0a vs ink truth | 64/65 | 58/59 | 30/31 |
| E0b vs ink truth | 63/65 | 57/59 | 29/31 |
| **E1 vs ink truth** | **64/65** | **58/59** | **30/31** |
| E2 vs ink truth | 62/65 | 57/59 | 29/31 |
| E0a vs E0a | 65/65 | 59/59 | 31/31 |
| E0b vs E0a | 64/65 | 58/59 | 30/31 |
| **E1 vs E0a** | **65/65** | **59/59** | **31/31** |
| E2 vs E0a | 63/65 | 57/59 | 29/31 |

All four complete yer arms have **0/65 `u` and 0/65 `other` calls**. Low-confidence slot counts are E0a 4/65, E0b 4/65, E1 2/65, E2 4/65; all slots report confidence. Zero-slot equality contributes 28 automatic matches to each per-item total, so the slot result is the relevant glyph measure.

## Does E1 pass the owner's quality condition?

**Yes for the scorer's primary fields on both beds.** Treat the observed E0a–E0b disagreement count as the empirical tolerance, not a confidence interval:

| Primary endpoint | E0 disagreement allowance | E1 truth score; E0a / E0b truth scores | E1 disagreement with E0a | Result |
| --- | ---: | --- | ---: | --- |
| BSB letters | 2/100 | 100; 100 / 98 | 0/100 | Within |
| BSB crop | 3/100 | 99; 98 / 99 | 3/100 | Within, at boundary |
| BSB marks | 3/100 | 98; 96 / 99 | 2/100 | Within |
| BSB joint | 7/100 | 97; 95 / 96 | 5/100 | Within |
| Yer slots | 1/65 | 64; 64 / 63 | 0/65 | Within |

This passes both the interpretation based on truth-accuracy loss and the additional check that E1 changes no more E0a calls than a control repeat does. Against the better control, the only lower primary truth score is BSB marks, by 1/100, inside its 3/100 allowance. Primary unresolved counts do not rise.

The paired outcomes clarify what happened. Versus E0a, E1 has letters **0 better / 0 worse**, crop **2 better / 1 worse**, marks **2 better / 0 worse**, and yer slots **0 better / 0 worse**. E1's reference disagreements are BSB `c041` marks, `c052` marks, `c074` crop, and yer `a010:2`. The same `a010:2` error occurs in **all four arms**. All four also disagree with C1 on `c052` marks. These shared calls merit independent native-ink adjudication, not automatic correction of either the readers or the key. For example, [ink_a.jsonl:10](../yer_adjudication/ink_a.jsonl:10) explicitly distinguishes the short two-sided serif in a010 slot 2 from slot 3's flag. I also inspected the saved enlarged c052 and a010 witnesses; this was a spot check, not a fresh blind truth audit.

**Qualification: the complete protocol has another uncertainty answer that `score.py` does not score.** A direct count of the same yer outputs gives:

| Auxiliary yer answer | E0a | E0b | E1 | E2 |
| --- | ---: | ---: | ---: | ---: |
| `pre1918=unclear` | 10/59 | 5/59 | **14/59** | 36/59 |
| `pre1918` agreement with saved truth | 57/59 | 50/59 | 53/59 | 35/59 |
| `unmarked_final_hard_signs` list equality with truth | 59/59 | 59/59 | 59/59 | 58/59 |

The auxiliary E0a–E0b pre1918 agreement is 52/59, and E1–E0a is 53/59. E1's accuracy loss of 4/59 versus E0a remains inside that 7/59 disagreement allowance, **but its unclear count rises by 4 versus E0a and 9 versus E0b**. Some truth entries are themselves unclear; this is not evidence that every unclear call is bad. It nevertheless prevents claiming literal compliance with “unresolved answers do not rise” across *all* answers. If the owner intended glyph `u`/`other` only, the primary gate passes; if the condition covers `pre1918` too, broad adoption has not passed it. The endpoint must not be narrowed after seeing this result without the owner's agreement.

## Position effect and actual E1 work order

I reconstructed position from the **first image Read for each item**, not output sort order or the manifest's seeded order. BSB E1 explicitly sorts IDs ([transcript:27](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:27)) and visits c001 through c100. Yer E1 reads all 31 slot-bearing items first, then the 28 zero-slot items. Neither follows its manifest order. Order and work strategy therefore accompany the context-size change; this is not a perfectly isolated one-factor execution.

| Actual E1 positions | Letters vs truth | Crop vs truth | Marks vs truth | Joint vs truth | E0a / E0b joint on the same cards |
| --- | ---: | ---: | ---: | ---: | ---: |
| BSB 1–50, c001–c050 | 50/50 | 50/50 | 49/50 | 49/50 | 49/50; 48/50 |
| BSB 51–100, c051–c100 | 50/50 | 49/50 | 49/50 | 48/50 | 46/50; 48/50 |

BSB marks and letters are flat; the second half has one additional crop disagreement. There are 65 image Reads for the first 50 cards and 62 for the second 50, including extra inspections. Late targeted zooms and detections continue through c085–c090, and c100 is opened ([E1:590–708](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:590)). There is no conspicuous late collapse in this sample. Source/difficulty and position remain confounded by ID sorting.

| Actual yer E1 positions | Items with slots / zero slots | Slots vs truth | All slots per item vs truth | E0a / E0b slots on the same items |
| --- | ---: | ---: | ---: | ---: |
| 1–30 | 30 / 0 | 60/61 | 29/30 | 60/61; 59/61 |
| 31–59 | 1 / 28 | 4/4 | 29/29 | 4/4; 4/4 |

The 31st item is a015, and its final letter receives an 8x targeted zoom ([E1:507–519](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab95cdd6ca8ae5b3a.output:507)). **The second-half 4/4 is far too small to establish flat late-context glyph quality.** Almost all glyph work ends near the midpoint of the 59-item context. The zero-slot items still require line-wide inspection, but cannot test late masked-letter fatigue. The increased auxiliary uncertainty is another reason not to call the whole protocol flat.

## Measured efficiency

Denominators here are completed card/item reads, one per item in these arms. Duration is the sum of reader durations, not concurrent elapsed time.

| Bed / arm | Readers; completed items | Total recorded tokens | Tokens per item | Tool uses total / per item | Summed reader seconds / per item |
| --- | --- | ---: | ---: | ---: | ---: |
| BSB E0a | 2; 100 | 245,376 | 2,453.76 | 277 / 2.77 | 954.572 / 9.546 |
| BSB E0b | 2; 100 | 225,108 | 2,251.08 | 238 / 2.38 | 818.633 / 8.186 |
| **BSB E1** | **1; 100** | **133,135** | **1,331.35** | **150 / 1.50** | **525.297 / 5.253** |
| BSB E2 | 2; 100 | 244,409 | 2,444.09 | 167 / 1.67 | 748.327 / 7.483 |
| Yer E0a | 2; 59 | 223,643 | 3,790.56 | 193 / 3.27 | 786.782 / 13.335 |
| Yer E0b | 2; 59 | 198,060 | 3,356.95 | 189 / 3.20 | 619.059 / 10.493 |
| **Yer E1** | **1; 59** | **131,449** | **2,227.95** | **136 / 2.31** | **441.106 / 7.476** |
| Yer E2 | 2; 59 | 195,754 | 3,317.86 | 86 / 1.46 | 393.981 / 6.678 |

Pooled E0a/E0b controls cost 2,352.42 tokens per BSB card and 3,573.75 per yer item. E1 reduces this measured metric by **43.4% BSB and 37.7% yer**. Separately against E0a/E0b, the savings are 45.7%/40.9% BSB and 41.2%/33.6% yer. They survive the observed control-run variation and are real in the supplied `total_tokens` metric.

This is not a demonstrated 40% reduction in billed cost or the owner's usage-limit consumption. The supplied usage log has no cached/uncached split or quota conversion, and no modality breakdown establishing that images dominate. Readers also used different zooming and batching strategies. Fewer tools and lower summed time corroborate less total work, but do not isolate its cause. E1's individual context is slightly longer than any control reader: 525.297 seconds BSB versus a maximum 495.125; 441.106 seconds yer versus 434.557. Parallel control readers can finish earlier in elapsed time despite consuming more aggregate resources.

The log totals **2,371,792 tokens over 24 recorded readers: 14 complete and 10 partial**. The cached total tokens match, but its “29 runs, 19 complete” tally is not supported by these records. Partial E3/E4 usage must not be divided by *assigned* full-bed counts to estimate completed-run efficiency: the scorer's cost denominator is assignments even when output is incomplete. Preparation and pause handling are already charged, while most answers are absent.

## Transcript findings: what is and is not available

I streamed the 24 mapped transcripts, enumerated their 1,832 tool calls, sampled actions and visible explanations for every arm, and checked pause events. **All 570 `thinking` blocks contain an empty `thinking` string** (with signatures). Thus the requested internal chains of thought are unavailable in these files. I cannot certify or quote hidden reasoning. The quotations below are visible handbacks, output notes, and executable work, with physical JSONL line numbers in the original `.output` files. They establish observable method and stated justification, not a complete reasoning audit.

| Arm / sample | Observable evidence and short quotation | Assessment |
| --- | --- | --- |
| E0a BSB | [a442…:38](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a442e54a94831b34a.output:38) creates overlapping 3x line halves. [Handback:656](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a442e54a94831b34a.output:656): “Low-confidence calls, all left as y”; it names ambiguous breathings and c074. | Real zoom work; zero unresolved does not mean zero doubt. Passing ambiguous supplied labels can inflate agreement even in the control. |
| E0b BSB | [ac80…:34](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ac80d29889bd64586.output:34) enlarges every line 2x. [Handback:434](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ac80d29889bd64586.output:434): “the rough and smooth breathings are hard to tell apart in these faces.” | Close calls are acknowledged, but passed. The tolerance is measured against readers with their own shared limits. |
| E0a/E0b yer | Segmented 3x line zooms in [ab310…:32](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab310d642a1532238.output:32) and [a3ff…:32](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a3ff3c5ed5f7302e8.output:32). [E0b handback:430](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a3ff3c5ed5f7302e8.output:430): a005 slot 3 “only reaches the x-height and has a short serif at the top.” | Ink- and same-face comparisons support the observable approach; the disputed a005 call explains the one control-repeat disagreement. |
| E1 BSB | [ab471…:33](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:33) enlarges every line 2x; all 100 IDs have image Reads, with 27 extra image inspections. Late targeted 4–5x crops appear at lines 597, 632 and 650. [Handback:719](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:719): c074 “but this is uncertain”; c042 “the upright ‘Ε’ could be a Latin or a Greek capital; I accepted the Greek label.” | No evidence of skipping the second half or accepting everything without zooming. Ambiguity is sometimes resolved toward the label, and uncertain c074 becomes a definite n rather than u. These are limits on certainty, not evidence of truth access. |
| E1 yer | [ab95…:33](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab95cdd6ca8ae5b3a.output:33) makes overlapping 3x segments; [225–245](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab95cdd6ca8ae5b3a.output:225) targets a010 at 5x. [Output-writing command:320](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab95cdd6ca8ae5b3a.output:320): “slot 1 stem has only a small serif, no left flag; slots 2-3 have left flag”. | Concrete pixel-based rationale, but slot 2 disagrees with ink truth with high confidence. Exact E0a agreement can preserve a shared error. The handback's 29 slot-bearing / 30 zero-slot counts are also wrong; the files give 31 / 28. |
| E2 BSB r1 | [a092…:33–39](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a0920daaa687ea3f0.output:33) builds word and glyph montages; glyph tiles use `96x129` geometry. [Handback:434](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a0920daaa687ea3f0.output:434): “Rather than opening the 2,469 crops one by one”; “Where the label was linguistically correct I accepted it.” | A material shortcut and explicit label/linguistic anchoring. Montages resize the supplied 8x glyphs and rearrange context; this is not direct inspection of every close-up as supplied. It passes all 50 crops and explains reversing c072's crop failure because the *derived word crops* also clip letters. Lost line-boundary evidence is decisive. |
| E2 BSB r2 | [a022…:372](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a022f198157e8e228.output:372) generates final rows from an exception dictionary with default y/y/y; [handback:377](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a022f198157e8e228.output:377): “without the full-line crop, crop_ok rests on what the word crops show”. | Montage Reads and targeted zooms precede output generation. Default-pass code warrants scrutiny, but is not itself proof of unread cards or copied answers. Whole-line crop validity is not recoverable from these inputs. |
| E2 yer | [a8fd…:33–39](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a8fdbbb313bc7be6c.output:33) and [a570…:38](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a570d7eb63b5014b8.output:38) make composites. [r1 handback:269](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a8fdbbb313bc7be6c.output:269): a020 close-up “is aimed at the wrong letters”. [r2 handback:176](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a570d7eb63b5014b8.output:176): a025 “seems to take the last glyph of the whole hyphenated token”. | Both readers rescue mis-targeted slots using word crops. This supports the reported build defect, but means success there does not validate the close-up construction. All 28 zero-slot items lack images; unmarked signs in a031 are missed. |
| E3 | BSB uses enlarged overlapping halves ([a650…:34](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a650161bf6f8209a4.output:34)); yer uses targeted slot zooms ([a1c2…:52, 101, 139](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a1c2d159bb4675236.output:52)). [Yer r1 pause handback:204](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a1c2d159bb4675236.output:204): “I worked the slot items first”. | Actual visual work, but non-random partial coverage. No complete compact-prompt quality or efficiency conclusion follows. |
| E4 | Whole-bed zoom preparation occurs before most reading ([BSB:34,49](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a5a3f5a1d5d99198a.output:34); [yer:34](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/aa6c305d136af6283.output:34)). Only one answer per bed is saved. | Their usage includes substantial preparation for unanswered cards. A one-card partial cannot measure prompt gain or an E1×E3 interaction. |

**Key access / copying:** no Read or Bash input in the mapped transcripts names `keys/`, `truth.json`, reference `verdicts/`, `ink_a/b`, or the scorer. I found no observed reading of another reader's answer file or copying of earlier-arm calls. Own-output appends, summaries, and the E2 exception dictionary are visible; agreement alone is not evidence of copying. Isolation was a file-layout/instruction boundary, not an OS sandbox, so absence of visible access is the supported finding. BSB E1 did briefly write helpers one level above its allowed zoom folder and listed `scratchpad/eff/` before moving them ([420–426](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:420), acknowledged at 719). That weakens strict isolation discipline but does not demonstrate answer leakage.

**Pause behavior:** all ten partial readers receive an explicit queued PAUSE and finish/save their current item. Examples: [BSB E3 r1:145,153](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a650161bf6f8209a4.output:145), [BSB E4:53,67](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a5a3f5a1d5d99198a.output:53), [yer E3 r1:177–204](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/a1c2d159bb4675236.output:177), [yer E4:48,56](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/aa6c305d136af6283.output:48), and [owner39 E0a r1:325,333](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/acdc8579e0d7c56f6.output:325). Their saved row counts match their final status. No actual RESUME command appears in these ten supplied transcripts. BSB E1 receives PAUSE after completing its first handback and answers “there is nothing left to resume” ([724–730](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/ab47186e116590309.output:724)). The cache's reference to pause-and-resume cost should therefore be read as pause/control overhead, not evidence of completed resumed experiments.

## What the statistics can establish

This is a useful pilot, not an equivalence or non-inferiority trial. There are 100 BSB cards, 65 yer slots nested in 31 positive items, two beds, **one E1 context per bed**, and no E1 repeat. Cards share pages, typefaces and error mechanisms. Reader/context strategy is confounded with treatment. An item-level confidence interval cannot estimate between-context variability from one E1 run per bed; treating all 165 units as exchangeable would be unjustified. E0 disagreement is an observed tolerance, not a stable estimate of all reader variance.

A single mismatch is descriptively visible: 1 percentage point BSB or 1/65 = 1.54 points yer. Reliable detection is much coarser. For scale only, under optimistic independent pairs, a perfect control, and *only harmful discordances*, a one-sided exact paired test at 5% needs at least **5 worse / 0 better** pairs (p=1/32). That is 5/100 or 5/65 = 7.69 points of observed loss. A two-sided version needs 6 such discordances. With the one-sided rule, about **6.63% true loss for n=100** or **10.12% for n=65** gives 80% power. At 2% loss, power is only about 5.1% / 1.0%; at 5% loss, about 56.4% / 22.5%. These are binomial calculations for an illustrative favorable design, not achieved power after accounting for clustering or imperfect controls.

Even zero newly harmed independent units would leave a one-sided 95% upper bound of **2.95%** at n=100 and **4.50%** at n=65 (`1 - 0.05**(1/n)`). Yer has zero E1-versus-E0a changes yet cannot exclude a modest population loss under even that favorable model. The design therefore cannot certify losses smaller than its 1–3-point empirical field tolerances, rare failure modes, or performance in new fonts/bed sizes. Failure to detect harm is not certainty of no harm.

## Was stopping decision-relevant work reasonable?

**Stopping was reasonable under the 40-hour usage constraint. It does not lower the evidentiary meaning of “no quality loss.”** E0/E1/E2 had completed enough to make the primary E1 decision reviewable offline. The missing arms answer different questions:

- **E2:** reject the tested implementation. Yer loses 2/65 correct slots versus E0a, exceeding the 1/65 control-repeat bar. BSB loses line-boundary evidence and one reader passes every crop; marks also change 4/100 E0a calls against a 3/100 repeat bar. Its BSB token cost is essentially E0a's, although yer is cheaper than E0a. Montage shortcuts and mis-targeted glyphs prevent attributing every difference solely to “remove full line,” but do not justify adoption. A repaired E2 is a new experiment.
- **E3/E4:** completing them could discover an extra prompt saving or an interaction; leaving them unfinished loses that optimization information, **not the existing E1 primary comparison**. The cached “<5%” extra gain and “images dominate” rationale are expectations, not measured conclusions from these partials. It is sensible to defer them; it is not justified to call them ineffective or quality-neutral.
- **owner39:** no E1/E4 arm was planned because 39 cards fit inside the existing practice batch. Its absence does not remove a direct E1 comparison that should have existed. It **does** leave decision-relevant uncertainty about absolute accuracy on the owner's difficult mark judgments and transfer from C1 agreement to practice. The partials already show uncertainty/errors that the BSB headline conceals.

| Owner39 partial, supplied key | Saved / assigned card reads | All scored anchor fields agree | Missing |
| --- | ---: | ---: | ---: |
| E0a r1 | 5/39 | 4/5 | 34 |
| E0a r2 | 13/39 | 10/13 | 26 |
| E0b r1 | 8/39 | 4/8 | 31 |
| E0b r2 | 7/39 | 6/7 | 32 |

These are separate reader prefixes, not 33 independent unique cards, not a completed consensus, and not an estimate of final owner39 accuracy. The scored key already sets the exceptional s33 accent to circumflex and excludes its unknown breathing, but its `truth_word` still says ἤγε while the cache requests ἦγε with a confirmed breathing. I applied no truth fix. The exceptional card does not occur in the four saved prefixes, so that pending reconciliation does not explain the partial scores. Owner39 E2/E3 have no saved answers in the supplied tree.

## Answers to the owner's three questions

**(1) Certain? No.** The arithmetic and primary empirical gate are verified; the general “no quality loss” conclusion is not. One E1 run per bed, no fair late yer glyph test, imperfect/shared truth, unavailable internal reasoning, observable label anchoring, and increased auxiliary uncertainty leave real uncertainty. The cached adoption preceded its formal score; this review supplies that score, without upgrading a pilot into proof.

**(2) Ideally, do more work, in this priority order.** A reader run here means one independent model context; a resumed partial consumes another execution segment but is not a fresh independent repeat.

1. **Audit the shared errors and endpoint definition — 0 new model-reader runs.** Independently adjudicate native witnesses for c041/c052/c074 and a010:2, retaining the original calls. Specify whether `pre1918=unclear` belongs to the unresolved gate, and report it explicitly. Reconcile the owner39 exception before completing that bed. Human adjudication is work even though its model-run cost is zero.
2. **Minimum E1 replication — 2 fresh reader runs**, one 100-card BSB context and one 59-item yer context, blinded to previous answers, with counterbalanced order and matched hard/soft and difficult-slot counts across early/late positions. Retain the original prompt, full lines and required zooms. This is the most useful next use of refreshed quota. A stronger contemporaneous comparison costs **6 fresh runs total**: those two E1 runs plus one fresh split E0 pass per bed, requiring four E0 contexts. This is an alternative package, not 2+6.
3. **Complete owner39 controls — 4 resumptions, 123 remaining card reads** (34+26+31+32); or **4 fresh full reader runs** if a clean uninterrupted repeat is wanted. This answers absolute owner-reference quality, not E1 batch scaling. Preserve two independent reads per card. To test 100-card batching on owner-adjudicated material, first build a sufficiently large blinded bed: for 100 cards and two reads per card, one control-vs-E1 comparison needs **6 runs** (four 50-card control contexts, two 100-card E1 contexts); independently repeating both conditions costs **12 total**.
4. **Broaden generalization before a universal claim.** For each new 100-item bed with one read per item per arm, two split E0 passes plus two 100-item E1 passes cost **6 runs**; two new beds cost **12 runs**. Keep difficult evidence throughout each context and predeclare the loss margin. Smaller margins require substantially more independent material/context repeats; even a zero-harm 1% bound needs about 299 independent units, before clustering or observed errors.
5. **Only if further prompt savings matter: E3/E4 completion — 6 resumptions**, four E3 readers and two E4 readers, leaving 83+99 BSB and 44+58 yer items unanswered. Fresh uninterrupted replacements cost **6 full reader runs**, preferable for an unbiased completed-run usage comparison. Owner39 E3 would add **2 new runs**. Do not spend quota repairing/rerunning E2 unless its objective is still valuable; a complete repaired BSB+yer E2 costs **4 runs** and needs the missing line-wide evidence addressed first.

These are recommendations, not authorizations to resume or launch anything. Under the owner's constraint, the offline scoring and narrow practical use can precede the ideal expansion.

**(3) Practical reliance? OK with conditions.** Rely on E1 as a reversible efficiency choice for **the tested primary checks**, while retaining the following conditions:

- Preserve the number and independence of readers **per item**, the original full-line inputs, the full protocol, and required zooming. No copied earlier calls or linguistic acceptance of unreadable marks. This is support for E1, not E2/E3/E4.
- Keep the evidence scope explicit: 100 BSB cards and 59 yer items. The tested yer context contains only 65 masked positions; a blanket 100-item yer rule, more glyph-dense material, and owner39-scale accuracy are not qualified here.
- Count all relevant uncertainty outputs. If the owner's unchanged condition includes pre1918, **do not describe the full-protocol adoption as passing**: retain the control for that work, or resolve and repeat that endpoint before broad reliance. Restricting the gate to primary glyph calls requires the owner's agreement; this review does not silently waive the condition.
- Treat “about 40%” as the recorded token-metric saving. Preserve fresh-context repetition and a small ongoing paired audit when quota returns; a failure outside the control tolerance or an unresolved-count rise should trigger review/reversion rather than being hidden in pooled averages.

R-eff: done | E1 within E0 variance: bsb yes yer yes | certain: no | rely in practice: ok-with-conditions
