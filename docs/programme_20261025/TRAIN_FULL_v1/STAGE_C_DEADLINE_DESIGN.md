# Stage C deadline-warning repair — design only

Stage B package `3c9e5d5f4fb8702e` stays unchanged. Its observed failure was the
2-hour job's `B:TERM@600` warning at approximately 1h50, rather than a training
error. The batch shell forwards TERM to the node controller, which sends TERM
to each `srun` client. A client can terminate its step/launcher while another
lane is waiting for step creation; exit 137/1 reaches `node()` and raises.
The existing trainer's boundary stop/checkpoint handler does not make TERM to
the launcher safe. Its independent deadline check is at end-minus-300 seconds,
five minutes later than the batch warning. Keep all failed attempts as evidence.

Implement in a separately sealed and reviewed Stage C package:

1. Handle `TERM@600` as a controller yield request. Set a persistent, per-job
   and restart-bound stop-request receipt before acknowledging it. Do not send
   TERM to `srun` clients. Expose the request to each live Python lane using a
   shared control file checked by the existing optimizer-boundary stop hook
   (or a worker-only signal with attested worker PID/step identity). A signal
   during controller startup must prevent new work and request a yield too.
2. Each lane stops at its next valid optimizer boundary, commits model,
   optimizer, scheduler, RNG, sampler/draw position and append-only evaluation
   progress, then publishes its checkpoint SHA/yield and final allocation end
   before returning 75. A currently running evaluation must finish atomically
   or retain its existing restartable journal protocol. A completed lane stays
   0; completed claims validate/skip when the job restarts.
3. Stop launching new lanes when warning is pending. Pending `srun` step
   creation must be cancelled/acknowledged without labelling a never-started
   trial as a scientific failure; distinguish it from a lane that actually
   ran. Preserve per-attempt evidence. Leave sufficient checkpoint/evaluation
   time before hard expiry; align the internal deadline with this warning.
4. Wait for every launched lane's durable 0/75 outcome; yield overall with 75
   if any work remains. The batch wrapper waits through interrupted `wait`
   calls and invokes `scontrol requeue` only after this barrier. The next
   allocation resumes the same claims. All unexpected codes, missing durable
   checkpoints, and genuine trainer errors remain failures with diagnostics.
   Never convert arbitrary 137/1 exits to 75 or hide a real failure just because
   another lane saw a warning.
5. Record `SLURM_STEP_ID` plus physical host, job, restart, CPU/GPU identity and
   start/end before/after each attempt; fsync relevant receipts. This reduces
   future accounting reconciliation ambiguity. Keep the existing host-aware
   CPU/global-GPU isolation checks and append logs.

Qualification: tests for TERM before launch, during concurrent step creation,
inside a training update, and inside loss/final CER/checkpoint publication;
mixed complete/yield/error lanes; repeated TERM and interrupted shell waits;
no new lanes after warning; exactly one requeue; all claims/eval points intact.
Then a real four-lane short CUDA warning-path requeue smoke, BIT_IDENTICAL
against an uninterrupted twin, complete accounting and hardware isolation,
followed by focused Astra review before Stage C launch. The earlier voluntary
forced-step smoke alone does not exercise this failed launcher path.

For B2 only, an 8-hour override shifts the same warning to 7h50, beyond the
measured roughly one-hour trials. It avoids the observed 1h50 warning under
that duration assumption; it is not a fix for future warnings, prolonged
storage stalls or external preemptions. Retain exact resume and monitor actual
completion. No Stage C implementation or launch is included in this change.
