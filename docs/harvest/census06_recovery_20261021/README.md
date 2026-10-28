# External census_06 recovery tools

These tools live outside sealed code/31316332c860d411. They do not change that
package, its configuration, tool versions or the ledger binding. The coordinator
commits this directory before any retry deployment/execution. RUNNER1 only stages
files and returns submit lines; it never submits or cancels a real job.

`isolate_native.py` remeasures the captured INFRA_ERROR observations using the
same NativeWorker, 120-second timeout, predictor, versions, runtime and crop paths.
Sixteen reusable workers fit a debug allocation; this is a diagnostic concurrency,
not a change to native_workers=64 in the census configuration. Every request reports
cohort, cold/warm state, native wall time and result/error. An equally sized control set has persisted successful segmentation results and matches the failed-row parent and book counts. Plain crop reads are timed before native calls in both cohorts, with size/hash/PNG dimensions recorded separately. The pre-read may warm the cache; native wall time includes worker startup and internal I/O and is not pure CPU time. Missing, mismatched or overlapping controls are rejected before native work. Calls interleave the two cohorts with alternating pair order.
No ledger is opened. All outputs go to the separate /capstor job directory.

`retry_errors.py` defaults to read-only test-only. It imports census04 from the
explicit sealed code root and calls its existing `run` API with `execute=True`,
`retry_errors=True`, `retry_holds=False`. It uses the existing prepared config
`attempts/full-split-002/inputs/config.json`, the same attempt, unchanged code,
versions and runtime environment. There is no raised timeout or CLI patch inside
the sealed package. It checks the original Slurm job is terminal before execution.
UNPROCESSED must be zero: otherwise the existing retry API would also process those
rows. A timed-out original run therefore needs its ordinary same-binding resume
to finish outstanding rows before an errors-only retry.

Acceptance compares the binding, decision key set and every former non-error
payload byte; generation must advance exactly once, INFRA_ERROR and UNPROCESSED
must reach zero, and the returned publication summary must be complete. Built-in
deduplication/export still runs. If deduplication changes a former non-error row,
the receipt is HOLD; it never silently waives the unchanged-row condition. A HOLD
preserves the actual new generation as evidence; it does not roll back writes.
The ordinary census runtime validation and Ledger binding check remain active.

Tests use the real census04/census from commit 33d28dfc, injecting only synthetic
native evidence into tiny fixture inputs. They check retry selection, unchanged
ADMIT/DROP/HOLD, generation/publication, read-only preflight, binding/config and
UNPROCESSED rejection, surviving errors, running-job refusal, and detection of an
unexpected non-error mutation. `CENSUS_RETRY_TEST_CODE` identifies that code root.
Use a dedicated pytest basetemp and delete it afterwards. The isolation job reruns
these tests on the actual deployed Linux code before measuring native requests.

Recovery choice B is preferred provisionally: errors cluster at the initial
native request batch and the next W1 book boundary. The isolated measurements must show whether cold startup,
I/O or inherently slow geometry is responsible. Option B still repeats full input
hash/registration, correction loading and split-rebinding, deduplication and export;
it does not cost only the failed native calls. Option A changes the timeout/configuration,
requires a new package and binding/ledger, the qualification gates, and a complete
592,466-row rerun. Its earlier 2h37 estimate is unqualified by the stalled full run.
Do not change the live run or launch a retry before the isolation result and
coordinator decision. Repeated >120-second isolated rows would support A, with the
proposed timeout based on measured isolated maxima, rather than changing B's binding.

Job 3711130 completed with all 125 failed rows passing in isolation (maximum 1.274 s), but its staged script lacked the succeeded controls. It is preserved as uncontrolled evidence and cannot satisfy the sourcing guard. Use only the corrected stage in out/runner1/NEXT_SUBMIT.sh, which includes 125 matched controls and reruns all nine adapter/diagnostic tests. Retry remains gated on the controlled result, terminal original job and a fresh I/O-health probe.
