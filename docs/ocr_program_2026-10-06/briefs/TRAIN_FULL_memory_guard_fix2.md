# Sol task — guard concurrency fix (Astra R5 H1-R5), 27 Oct, coordinator

Read docs/programme_20261025/TRAIN_FULL_v1/ASTRA_STAGE_C_R5_GUARD_FIX_REVIEW.md (HOLD 0/1). Fix ONLY H1-R5 in docs/programme_20261025/TRAIN_FULL_v1/memory_fix/memory_guard.py (reviewed sha 1ab95862…):
1. Every read and write of shared guard state (self.intents, self.triggers, self.held, self.armed and any other cross-lane container) happens under self.mutex; iterate over snapshots taken under the mutex. Audit the whole file for other cross-thread mutations of shared state, not just the line Astra cites.
2. A lane-cycle exception must never terminate the guard or stop the other lanes: catch per lane in cycle(), log a GUARD_LANE_ERROR event (exception type/message, lane, job, restart) and still write the heartbeat; the lane is retried next cycle. A fatal error in the main loop itself must log GUARD_FATAL before exiting. Do not let error handling suppress a pending trigger.
3. Tests: Astra's deterministic two-lane interleaving (pause B after SIGNAL_INTENT event, start A's escape scan, resume B) must now give lane A its own restart-1 trigger + TERM and no exception; lane-error isolation; existing 88 tests pass.
4. Do NOT change workaround_recover.py, schema, policy numbers, or the sealed package. Update GUARD_PROTOCOL.md briefly.
No remote actions, no rm, do not touch unrelated files. End with "MEMORY GUARD FIX2 READY" and the new guard SHA256.
