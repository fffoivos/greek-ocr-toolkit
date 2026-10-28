# Sol — Stage B recovered-allocation reconciliation (26 October 2026)

Objective: execute the owner's latest TRAIN_FULL resume: reconcile the 26 killed
lane ends against uniquely matched Slurm accounting steps, preserve the sealed
scientific payload, supply collection/B2 commands, and document the Stage C
deadline-warning repair without implementing it in Stage B.

Write scope: `docs/programme_20261025/TRAIN_FULL_v1/collection/`, small receipts
under `evidence/STAGE_B_COLLECT_ISOLATION/`, a reconciliation report and Stage C
design under TRAIN_FULL_v1, `out/TRAIN_FULL_v1/COMMANDS.md`, this brief, and an
append-only entry in `EXECUTION_STATE.md`. Leave package/ and all original
allocation, recovery, accounting and study records unchanged.

Inputs: payload SHA256
`3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8`;
study PLAN SHA256
`01cc2ae0bb09d2b61d3b6a7fc15627366d3a131e385efe30028e82cb81903f38`.
The produced reconciliation binds the accounting capture and every allocation
and recovery by SHA256, bytes and original remote path. Source revision is
recorded in the implementation receipt.

Checks: copied-evidence offline audit; positive and adversarial matching,
ambiguity, interval and hardware tests; production collector/B2 integration
without fixture bypass; unchanged full package suite; payload verification
before/after. Scratch <=1 GB; remove only this run's pytest basetemp after a
passing suite and retain its size/cleanup receipt. No data/cache copies, remote
commands, Slurm submissions, network, deletion of other files or git mutations.
