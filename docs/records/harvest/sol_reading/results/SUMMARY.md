| definition | scope / denominator |
| --- | --- |
| accuracy | correct/n scored units; unknown and unresolved are incorrect; bsb uses the C1 reader reference |
| yer_item | all slots correct; all 59 items included, including 28 zero-slot items |
| owner39 | scored heads only; breathing excluded on one card; joint = base and all scored heads |
| owner39_pool | 33 card-reads, retaining repeated cards once per Opus read; each head uses its eligible card-reads |
| variance | official scorer agreement; owner unknown/unknown is not confirmed agreement; accuracy differences use the same overlap |
| changes | per scored field/slot and joint/item; unresolved answers count as wrong and remain in denominators |
| Sol_total | input + output; cached input is part of input; reasoning is part of output; do not add either twice |
| cost_run_denominator | assigned items including controls; r3 includes only disputed items plus controls |
| cost_arm_denominator | unique scored bed items excluding controls; S1 is one reader, S2 is r1+r2+r3 |
| weekly | 10080-minute bucket; before/after are endpoint probes; delta_sum sums within-run deltas, excludes intervening work |
| credits | null before balance or spent means unavailable, not zero; ratios with zero or unavailable denominators are null |
| meters | Sol rollout tokens/limits and Opus usage-log tokens are separate; no conversion |
| build | launcher session id mapped to rollout; current B4 is a timestamped lower-bound snapshot; excluded from completed build totals |

| r3 bed | scan | violations | mapped scored items | controls | mapping complete |
| --- | --- | --- | --- | --- | --- |
| bsb | ok | 0 | 5 | 1 | True |
| yer | ok | 0 | 1 | 1 | True |
| owner39 | ok | 0 | 11 | 2 | True |

| bsb reader | scope | letters correct/n | marks correct/n | crop_ok correct/n | joint correct/n |
| --- | --- | --- | --- | --- | --- |
| Sol r1 | full | 99/100 | 96/100 | 98/100 | 93/100 |
| Sol r2 | full | 99/100 | 97/100 | 98/100 | 94/100 |
| Sol S2 | full | 99/100 | 96/100 | 98/100 | 93/100 |
| Opus E0a | full | 100/100 | 96/100 | 98/100 | 95/100 |
| Opus E0b | full | 98/100 | 99/100 | 99/100 | 96/100 |
| Opus E1 | full | 100/100 | 98/100 | 99/100 | 97/100 |

| yer reader | scope | slot correct/n | item correct/n |
| --- | --- | --- | --- |
| Sol r1 | full | 64/65 | 58/59 |
| Sol r2 | full | 63/65 | 57/59 |
| Sol S2 | full | 64/65 | 58/59 |
| Opus E0a | full | 64/65 | 58/59 |
| Opus E0b | full | 63/65 | 57/59 |
| Opus E1 | full | 64/65 | 58/59 |

| owner39 reader | scope | base correct/n | breathing correct/n | accent correct/n | diaeresis correct/n | subscript correct/n | joint_anchor correct/n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sol r1 | full | 39/39 | 35/38 | 34/39 | 39/39 | 39/39 | 33/39 |
| Sol r2 | full | 39/39 | 28/38 | 33/39 | 39/39 | 39/39 | 28/39 |
| Sol S2 | full | 36/39 | 33/38 | 33/39 | 36/39 | 36/39 | 33/39 |
| Opus E0a r1 | partial | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 | 4/5 |
| Opus E0a r2 | partial | 13/13 | 11/13 | 12/13 | 13/13 | 12/13 | 10/13 |
| Opus E0b r1 | partial | 8/8 | 5/8 | 7/8 | 8/8 | 7/8 | 4/8 |
| Opus E0b r2 | partial | 7/7 | 7/7 | 6/7 | 7/7 | 7/7 | 6/7 |
| Sol r1 on Opus partial pooled | partial pooled card-reads | 33/33 | 30/33 | 30/33 | 33/33 | 33/33 | 30/33 |
| Opus partial pooled | partial pooled card-reads | 33/33 | 28/33 | 30/33 | 33/33 | 30/33 | 24/33 |
| Sol r2 on Opus partial pooled | partial pooled card-reads | 33/33 | 22/33 | 29/33 | 33/33 | 33/33 | 22/33 |
| Sol S2 on Opus partial pooled | partial pooled card-reads | 33/33 | 30/33 | 30/33 | 33/33 | 33/33 | 30/33 |

| bed | variance pair | unit | agreement/n | left correct/n | right correct/n | absolute accuracy difference pp (same n) |
| --- | --- | --- | --- | --- | --- | --- |
| bsb | Sol r1 vs Sol r2 | letters | 100/100 | 99/100 | 99/100 | 0 |
| bsb | Sol r1 vs Sol r2 | marks | 99/100 | 96/100 | 97/100 | 1 |
| bsb | Sol r1 vs Sol r2 | crop_ok | 96/100 | 98/100 | 98/100 | 0 |
| bsb | Sol r1 vs Sol r2 | joint | 95/100 | 93/100 | 94/100 | 1 |
| bsb | Opus E0a vs Opus E0b | letters | 98/100 | 100/100 | 98/100 | 2 |
| bsb | Opus E0a vs Opus E0b | marks | 97/100 | 96/100 | 99/100 | 3 |
| bsb | Opus E0a vs Opus E0b | crop_ok | 97/100 | 98/100 | 99/100 | 1 |
| bsb | Opus E0a vs Opus E0b | joint | 93/100 | 95/100 | 96/100 | 1 |
| yer | Sol r1 vs Sol r2 | slot | 64/65 | 64/65 | 63/65 | 1.53846153846 |
| yer | Sol r1 vs Sol r2 | item | 58/59 | 58/59 | 57/59 | 1.69491525424 |
| yer | Opus E0a vs Opus E0b | slot | 64/65 | 64/65 | 63/65 | 1.53846153846 |
| yer | Opus E0a vs Opus E0b | item | 58/59 | 58/59 | 57/59 | 1.69491525424 |
| owner39 | Sol r1 vs Sol r2 | base | 39/39 | 39/39 | 39/39 | 0 |
| owner39 | Sol r1 vs Sol r2 | breathing | 28/38 | 35/38 | 28/38 | 18.4210526316 |
| owner39 | Sol r1 vs Sol r2 | accent | 32/39 | 34/39 | 33/39 | 2.5641025641 |
| owner39 | Sol r1 vs Sol r2 | diaeresis | 39/39 | 39/39 | 39/39 | 0 |
| owner39 | Sol r1 vs Sol r2 | subscript | 39/39 | 39/39 | 39/39 | 0 |
| owner39 | Sol r1 vs Sol r2 | joint_anchor | 27/39 | 33/39 | 28/39 | 12.8205128205 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | base | 8/8 | 8/8 | 8/8 | 0 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | breathing | 6/8 | 7/8 | 6/8 | 12.5 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | accent | 7/8 | 7/8 | 7/8 | 0 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | diaeresis | 8/8 | 8/8 | 8/8 | 0 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | subscript | 7/8 | 7/8 | 7/8 | 0 |
| owner39 | Opus E0a partial combined vs Opus E0b partial combined | joint_anchor | 5/8 | 6/8 | 5/8 | 12.5 |

| bed | S1 | unit | n | changed/n | to correct/n | to wrong/n | between wrong/n | net correct/n | net accuracy pp (n) | unresolved/n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bsb | Sol r1 | letters | 100 | 0/100 | 0/100 | 0/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r1 | marks | 100 | 0/100 | 0/100 | 0/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r1 | crop_ok | 100 | 4/100 | 2/100 | 2/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r1 | joint | 100 | 4/100 | 2/100 | 2/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r2 | letters | 100 | 0/100 | 0/100 | 0/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r2 | marks | 100 | 1/100 | 0/100 | 1/100 | 0/100 | -1/100 | -1 | 0/100 |
| bsb | Sol r2 | crop_ok | 100 | 0/100 | 0/100 | 0/100 | 0/100 | 0/100 | 0 | 0/100 |
| bsb | Sol r2 | joint | 100 | 1/100 | 0/100 | 1/100 | 0/100 | -1/100 | -1 | 0/100 |
| yer | Sol r1 | slot | 65 | 0/65 | 0/65 | 0/65 | 0/65 | 0/65 | 0 | 0/65 |
| yer | Sol r1 | item | 59 | 0/59 | 0/59 | 0/59 | 0/59 | 0/59 | 0 | 0/59 |
| yer | Sol r2 | slot | 65 | 1/65 | 1/65 | 0/65 | 0/65 | 1/65 | 1.53846153846 | 0/65 |
| yer | Sol r2 | item | 59 | 1/59 | 1/59 | 0/59 | 0/59 | 1/59 | 1.69491525424 | 0/59 |
| owner39 | Sol r1 | base | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r1 | breathing | 38 | 3/38 | 0/38 | 2/38 | 1/38 | -2/38 | -5.26315789474 | 3/38 |
| owner39 | Sol r1 | accent | 39 | 3/39 | 0/39 | 1/39 | 2/39 | -1/39 | -2.5641025641 | 3/39 |
| owner39 | Sol r1 | diaeresis | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r1 | subscript | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r1 | joint_anchor | 39 | 4/39 | 0/39 | 0/39 | 4/39 | 0/39 | 0 | 3/39 |
| owner39 | Sol r2 | base | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r2 | breathing | 38 | 7/38 | 6/38 | 1/38 | 0/38 | 5/38 | 13.1578947368 | 3/38 |
| owner39 | Sol r2 | accent | 39 | 2/39 | 1/39 | 1/39 | 0/39 | 0/39 | 0 | 3/39 |
| owner39 | Sol r2 | diaeresis | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r2 | subscript | 39 | 3/39 | 0/39 | 3/39 | 0/39 | -3/39 | -7.69230769231 | 3/39 |
| owner39 | Sol r2 | joint_anchor | 39 | 9/39 | 6/39 | 1/39 | 2/39 | 5/39 | 12.8205128205 | 3/39 |

| bed | run | control passes/n | failures/n | flagged |
| --- | --- | --- | --- | --- |
| bsb | r1 | 10/10 | 0/10 | False |
| bsb | r2 | 10/10 | 0/10 | False |
| bsb | r3 | 1/1 | 0/1 | False |
| yer | r1 | 5/5 | 0/5 | False |
| yer | r2 | 5/5 | 0/5 | False |
| yer | r3 | 1/1 | 0/1 | False |
| owner39 | r1 | 4/4 | 0/4 | False |
| owner39 | r2 | 4/4 | 0/4 | False |
| owner39 | r3 | 2/2 | 0/2 | False |

| Sol bed | run / arm | items n | item denominator | wall s / run or arm | input tokens / run or arm | cached_input tokens / run or arm | uncached_input tokens / run or arm | output tokens / run or arm | reasoning tokens / run or arm | total tokens / run or arm | total tokens/item n | tool calls / run or arm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bsb | r1 | 110 | assigned items including controls | 174 | 1077603 | 998016 | 79587 | 7537 | 2406 | 1085140 | 9864.90909091 | 19 |
| bsb | r2 | 110 | assigned items including controls | 204 | 1341729 | 1256576 | 85153 | 8328 | 2428 | 1350057 | 12273.2454545 | 21 |
| bsb | r3 | 6 | assigned items including controls | 58 | 136895 | 115328 | 21567 | 2279 | 716 | 139174 | 23195.6666667 | 5 |
| yer | r1 | 64 | assigned items including controls | 139 | 837668 | 762752 | 74916 | 4279 | 809 | 841947 | 13155.421875 | 20 |
| yer | r2 | 64 | assigned items including controls | 108 | 499618 | 448512 | 51106 | 3715 | 549 | 503333 | 7864.578125 | 12 |
| yer | r3 | 2 | assigned items including controls | 36 | 102398 | 79488 | 22910 | 1425 | 177 | 103823 | 51911.5 | 4 |
| owner39 | r1 | 43 | assigned items including controls | 137 | 459926 | 414208 | 45718 | 6398 | 1757 | 466324 | 10844.744186 | 13 |
| owner39 | r2 | 43 | assigned items including controls | 145 | 605917 | 556928 | 48989 | 7521 | 1449 | 613438 | 14266 | 16 |
| owner39 | r3 | 13 | assigned items including controls | 86 | 225879 | 194560 | 31319 | 4110 | 1290 | 229989 | 17691.4615385 | 8 |
| bsb | S2 | 100 | unique scored bed items | 436 | 2556227 | 2369920 | 186307 | 18144 | 5550 | 2574371 | 25743.71 | 45 |
| bsb | S1 r1 | 100 | unique scored bed items | 174 | 1077603 | 998016 | 79587 | 7537 | 2406 | 1085140 | 10851.4 | 19 |
| bsb | S1 r2 | 100 | unique scored bed items | 204 | 1341729 | 1256576 | 85153 | 8328 | 2428 | 1350057 | 13500.57 | 21 |
| yer | S2 | 59 | unique scored bed items | 283 | 1439684 | 1290752 | 148932 | 9419 | 1535 | 1449103 | 24561.0677966 | 36 |
| yer | S1 r1 | 59 | unique scored bed items | 139 | 837668 | 762752 | 74916 | 4279 | 809 | 841947 | 14270.2881356 | 20 |
| yer | S1 r2 | 59 | unique scored bed items | 108 | 499618 | 448512 | 51106 | 3715 | 549 | 503333 | 8531.06779661 | 12 |
| owner39 | S2 | 39 | unique scored bed items | 368 | 1291722 | 1165696 | 126026 | 18029 | 4496 | 1309751 | 33583.3589744 | 37 |
| owner39 | S1 r1 | 39 | unique scored bed items | 137 | 459926 | 414208 | 45718 | 6398 | 1757 | 466324 | 11957.025641 | 13 |
| owner39 | S1 r2 | 39 | unique scored bed items | 145 | 605917 | 556928 | 48989 | 7521 | 1449 | 613438 | 15729.1794872 | 16 |

| Sol bed | run / arm | weekly % before | weekly % after | within-run weekly pp sum | credits before | credits after | credits spent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bsb | r1 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| bsb | r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| bsb | r3 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | r1 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | r3 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | r1 | 32 | 32 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | r3 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| bsb | S2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| bsb | S1 r1 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| bsb | S1 r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | S2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | S1 r1 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| yer | S1 r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | S2 | 32 | 33 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | S1 r1 | 32 | 32 | 0 | unavailable | 59974.713745 | unavailable |
| owner39 | S1 r2 | 33 | 33 | 0 | unavailable | 59974.713745 | unavailable |

| bed | ratio denominator S1 | numerator | input tokens ratio | cached_input tokens ratio | uncached_input tokens ratio | output tokens ratio | reasoning tokens ratio | total tokens ratio | wall ratio | tool calls ratio | weekly delta ratio | credits spent ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bsb | S1 r1 | S2 | 2.37214168854 | 2.37463126844 | 2.34092251247 | 2.40732386891 | 2.30673316708 | 2.37238605157 | 2.50574712644 | 2.36842105263 | unavailable | unavailable |
| bsb | S1 r2 | S2 | 1.90517384658 | 1.88601405725 | 2.18790882294 | 2.17867435159 | 2.28583196046 | 1.90686096957 | 2.13725490196 | 2.14285714286 | unavailable | unavailable |
| yer | S1 r1 | S2 | 1.71868090938 | 1.69223023997 | 1.98798654493 | 2.2012152372 | 1.89740420272 | 1.72113327799 | 2.03597122302 | 1.8 | unavailable | unavailable |
| yer | S1 r2 | S2 | 2.88156951911 | 2.87785388128 | 2.91417837436 | 2.53539703903 | 2.79599271403 | 2.87901448941 | 2.62037037037 | 3 | unavailable | unavailable |
| owner39 | S1 r1 | S2 | 2.80854311346 | 2.81427688504 | 2.75659477667 | 2.81791184745 | 2.55890722823 | 2.80867165319 | 2.68613138686 | 2.84615384615 | unavailable | unavailable |
| owner39 | S1 r2 | S2 | 2.13184644101 | 2.0930820501 | 2.57253669191 | 2.39715463369 | 3.10282953761 | 2.13509922763 | 2.53793103448 | 2.3125 | unavailable | unavailable |

| Opus bed | arm | run | scope | answered items n | total tokens | tool uses | duration ms | tokens/item n | tools/item n | ms/item n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yer | E0b | r2 | full | 29 | 99052 | 97 | 306930 | 3415.5862069 | 3.34482758621 | 10583.7931034 |
| yer | E0b | r1 | full | 30 | 99008 | 92 | 312129 | 3300.26666667 | 3.06666666667 | 10404.3 |
| bsb | E0b | r2 | full | 50 | 105151 | 93 | 339450 | 2103.02 | 1.86 | 6789 |
| yer | E0a | r1 | full | 30 | 110301 | 91 | 352225 | 3676.7 | 3.03333333333 | 11740.8333333 |
| yer | E0a | r2 | full | 29 | 113342 | 102 | 434557 | 3908.34482759 | 3.51724137931 | 14984.7241379 |
| bsb | E0a | r2 | full | 50 | 116904 | 139 | 459447 | 2338.08 | 2.78 | 9188.94 |
| bsb | E0b | r1 | full | 50 | 119957 | 145 | 479183 | 2399.14 | 2.9 | 9583.66 |
| bsb | E0a | r1 | full | 50 | 128472 | 138 | 495125 | 2569.44 | 2.76 | 9902.5 |
| yer | E1 | r1 | full | 59 | 131449 | 136 | 441106 | 2227.94915254 | 2.30508474576 | 7476.37288136 |
| bsb | E1 | r1 | full | 100 | 133135 | 150 | 525297 | 1331.35 | 1.5 | 5252.97 |
| owner39 | E0a | r1 | partial | 5 | 95911 | 60 | 283625 | 19182.2 | 12 | 56725 |
| owner39 | E0a | r2 | partial | 13 | 95975 | 84 | 292208 | 7382.69230769 | 6.46153846154 | 22477.5384615 |
| owner39 | E0b | r1 | partial | 8 | 98367 | 54 | 302265 | 12295.875 | 6.75 | 37783.125 |
| owner39 | E0b | r2 | partial | 7 | 97879 | 57 | 300862 | 13982.7142857 | 8.14285714286 | 42980.2857143 |
| bsb | E0a | arm total | full | 100 | 245376 | 277 | 954572 | 2453.76 | 2.77 | 9545.72 |
| bsb | E0b | arm total | full | 100 | 225108 | 238 | 818633 | 2251.08 | 2.38 | 8186.33 |
| bsb | E1 | arm total | full | 100 | 133135 | 150 | 525297 | 1331.35 | 1.5 | 5252.97 |
| yer | E0a | arm total | full | 59 | 223643 | 193 | 786782 | 3790.55932203 | 3.27118644068 | 13335.2881356 |
| yer | E0b | arm total | full | 59 | 198060 | 189 | 619059 | 3356.94915254 | 3.20338983051 | 10492.5254237 |
| yer | E1 | arm total | full | 59 | 131449 | 136 | 441106 | 2227.94915254 | 2.30508474576 | 7476.37288136 |

| whole experiment meter | run denominator | assigned card-reads | input tokens | cached_input tokens | uncached_input tokens | output tokens | reasoning tokens | total tokens | weekly % first probe | weekly % last probe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sol reading | 9 | 455 | 5287633 | 4826368 | 461265 | 45592 | 11581 | 5333225 | 32.0 | 33.0 |
| completed Sol build/brief | 4 | N/A | 6347038 | 5977216 | 369822 | 76629 | 11686 | 6423667 | N/A | N/A |

| reading endpoint | ledger probe |
| --- | --- |
| first | 2026-10-17 12:46:05 before:owner39/r1 limit_id=codex primary=32.0%/10080m reset Thu 09:13 secondary=- |
| last | 2026-10-17 13:19:03 after:bsb/r3 limit_id=codex primary=33.0%/10080m reset Thu 09:13 secondary=- |

| build/brief run (n=1 each) | status | session id | usage timestamp UTC | input tokens | cached_input tokens | uncached_input tokens | output tokens | reasoning tokens | total tokens | rollout |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SR-B1 | completed | 01a14935-415b-7ab0-aa3a-e578e161a8f6 | 2026-10-17T09:40:25.386Z | 2912774 | 2802560 | 110214 | 29934 | 4660 | 2942708 | /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T12-33-09-01a14935-415b-7ab0-aa3a-e578e161a8f6.jsonl |
| SR-B1b | completed | 01a1493d-76d1-7300-833b-382240248dc2 | 2026-10-17T09:45:38.089Z | 1087215 | 1009792 | 77423 | 9015 | 1531 | 1096230 | /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T12-42-07-01a1493d-76d1-7300-833b-382240248dc2.jsonl |
| SR-B2 | completed | 01a14944-4465-7d81-b0a3-5e5cb20be905 | 2026-10-17T09:57:10.170Z | 1391539 | 1303040 | 88499 | 28020 | 4914 | 1419559 | /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T12-49-33-01a14944-4465-7d81-b0a3-5e5cb20be905.jsonl |
| SR-B3 | completed | 01a14958-e6e4-72f0-8791-72c5101747d1 | 2026-10-17T10:15:14.655Z | 955510 | 861824 | 93686 | 9660 | 581 | 965170 | /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T13-12-05-01a14958-e6e4-72f0-8791-72c5101747d1.jsonl |
| SR-B4 | in progress; lower-bound snapshot | 01a1495f-5d97-70a1-a28a-3a0757b0380e | 2026-10-17T10:24:32.929Z | 656819 | 576768 | 80051 | 10216 | 1177 | 667035 | /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T13-19-09-01a1495f-5d97-70a1-a28a-3a0757b0380e.jsonl |
