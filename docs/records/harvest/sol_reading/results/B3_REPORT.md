# SR-B3 completion report

All work ran offline with no git or codex commands. Pillow tools used the requested x86_64 Python 3.11 with -B.

## Scanner v3

The name/path filter now recognizes the own absolute reader prefix before checking forbidden ancestors. Literal template interpolations are resolved statically; suffixes attached to computed expressions are relative. Sibling reader/bed paths and the pack root remain violations. Original scan files are preserved as scan.v1.json or scan.v2.json beside each current scan.

| bed | reader | status | violations | matched returned images |
| --- | --- | --- | --- | --- |
| owner39 | r1 | ok | 0 | 62 |
| yer | r1 | ok | 0 | 133 |
| bsb | r1 | ok | 0 | 122 |
| owner39 | r2 | ok | 0 | 78 |
| yer | r2 | ok | 0 | 72 |
| bsb | r2 | ok | 0 | 124 |

## Agreement matrix fix

The previous matrix intersected all reader card sets before scoring every cell. The four partial owner39 Opus sets have an empty global intersection, producing 0/0 even for Sol self comparisons. Each cell now uses its own pair overlap; pairwise denominators and the global diagnostic intersection remain in results.json. bsb and yer used the same matrix construction; their full readers had no empty-cohort failure. Self denominators now cover 100 bsb cards, 65 yer slots and 39 owner39 cards. Unknown calls retain the original scorer policy: unknown/unknown is not confirmed agreement. Synthetic fully decided self agreement is n/n.

## Matched owner39 joint-anchor accuracy

Each row scores exactly that Opus reader's cards; pooled counts preserve all 33 card-reads, including repeated cards. Same counts both-correct and both-wrong. All per-head metrics and bsb/yer paired counts appear in TABLES.md and results.json.

| Sol | Opus cohort | Sol correct/n | Opus correct/n | better | worse | same |
| --- | --- | --- | --- | --- | --- | --- |
| Sol r1 | Opus E0a r1 | 4/5 | 4/5 | 1 | 1 | 3 |
| Sol r1 | Opus E0a r2 | 13/13 | 10/13 | 3 | 0 | 10 |
| Sol r1 | Opus E0b r1 | 8/8 | 4/8 | 4 | 0 | 4 |
| Sol r1 | Opus E0b r2 | 5/7 | 6/7 | 0 | 1 | 6 |
| Sol r1 | Opus partial pooled | 30/33 | 24/33 | 8 | 2 | 23 |
| Sol r2 | Opus E0a r1 | 2/5 | 4/5 | 1 | 3 | 1 |
| Sol r2 | Opus E0a r2 | 11/13 | 10/13 | 3 | 2 | 8 |
| Sol r2 | Opus E0b r1 | 5/8 | 4/8 | 2 | 1 | 5 |
| Sol r2 | Opus E0b r2 | 4/7 | 6/7 | 0 | 2 | 5 |
| Sol r2 | Opus partial pooled | 22/33 | 24/33 | 6 | 8 | 19 |
| Sol S2 | Opus E0a r1 | 2/5 | 4/5 | 1 | 3 | 1 |
| Sol S2 | Opus E0a r2 | 11/13 | 10/13 | 3 | 2 | 8 |
| Sol S2 | Opus E0b r1 | 5/8 | 4/8 | 2 | 1 | 5 |
| Sol S2 | Opus E0b r2 | 4/7 | 6/7 | 0 | 2 | 5 |
| Sol S2 | Opus partial pooled | 22/33 | 24/33 | 6 | 8 | 19 |

## Tie-break packs

| bed | disputed items | disputed units | controls | r3 items | pack scan |
| --- | --- | --- | --- | --- | --- |
| bsb | 5 | 5 | 1 | 6 | ok |
| yer | 1 | 1 | 1 | 2 | ok |
| owner39 | 11 | 11 | 2 | 13 | ok |

r3 packs are built and scanned; no readers were launched. S2 was regenerated from r1/r2, leaving disputed units undecided until r3 answers exist.

## Outputs and validation

Regenerated results/results.json, results/TABLES.md and results/ERRORS.md. ERRORS.md has one private table per bed, including original efficiency source IDs and each available Opus answer (MISSING for absent reads). All 60 B1/B1b/B2/B3 tests passed; see TEST_RESULTS_B3.txt. Additional artifact checks verified all six run scans, all three pack scans, self-comparison denominators, complete Sol coverage and paired count arithmetic.

SR-B3 READY: tests=60/60 r3 items bsb/yer/owner39=6/2/13
