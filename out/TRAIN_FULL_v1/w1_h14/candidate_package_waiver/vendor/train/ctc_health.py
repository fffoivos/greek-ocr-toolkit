"""CTC health gates (WP-A iii, REV H appendix): make silent CTC degeneracy LOUD.

`nn.CTCLoss(zero_infinity=True)` returns 0 (not inf) for an *infeasible* alignment, so a sample the
model can never fit contributes no gradient AND is invisible to a `isfinite(loss)` check. A CTC
alignment is feasible only when the input length T is at least U + R, where U is the target length
and R is the number of adjacent-equal target labels (each needs a separating blank). This module:
  * `infeasible_samples` — per-sample T ≥ U+R feasibility screen (what zero_infinity would hide),
  * `CtcHealth` — accumulates infeasible / NaN-batch / rare-token counters across an epoch/run, and
    `check_abort()` fails LOUD (compound-abort) if the infeasible or NaN fraction crosses a threshold.

Counters are plain ints/floats (`as_dict()`), meant to be persisted into checkpoint_meta + train_log.
For FUTURE runs only — never applied retroactively to the frozen S16 results.
"""

from __future__ import annotations


def required_blanks(seq) -> int:
    """R — count of adjacent-equal labels in a target (each forces a separating blank in CTC)."""
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b)


def infeasible_samples(targets_1d, target_lengths, input_lengths):
    """Per-sample CTC feasibility screen. `targets_1d` is the CTC-concatenated target ids;
    `target_lengths`[i] = U_i, `input_lengths`[i] = T_i. Returns a list of dicts (one per sample
    with T < U+R): {i, T, U, R, need=U+R}. Empty list ⇒ all samples feasible."""
    out = []
    off = 0
    tl = [int(u) for u in target_lengths]
    il = [int(t) for t in input_lengths]
    for i, (U, T) in enumerate(zip(tl, il)):
        seq = [int(v) for v in targets_1d[off:off + U]]
        off += U
        R = required_blanks(seq)
        if T < U + R:
            out.append({"i": i, "T": T, "U": U, "R": R, "need": U + R})
    return out


class CtcHealth:
    """Accumulate CTC health across a run + a compound-abort gate.

    abort_*_frac: fail the run if the fraction of infeasible samples / NaN batches exceeds this
    (after a warmup min count, so a tiny early batch can't trip it). rare_ids: optional set of rare
    atom ids to count exposures of (feeds rare-token starvation diagnostics)."""

    def __init__(self, abort_infeasible_frac: float = 0.02, abort_nan_frac: float = 0.05,
                 rare_ids=None, min_samples: int = 200, min_batches: int = 50) -> None:
        self.samples = 0
        self.batches = 0
        self.infeasible = 0
        self.nan_batches = 0
        self.rare_exposures = 0
        self.abort_infeasible_frac = abort_infeasible_frac
        self.abort_nan_frac = abort_nan_frac
        self.rare_ids = set(int(i) for i in (rare_ids or []))
        self.min_samples = min_samples
        self.min_batches = min_batches

    def update_batch(self, targets_1d, target_lengths, input_lengths):
        """Screen one batch; accumulate counters; return the infeasible-sample list for logging."""
        self.batches += 1
        self.samples += len(target_lengths)
        infe = infeasible_samples(targets_1d, target_lengths, input_lengths)
        self.infeasible += len(infe)
        if self.rare_ids:
            self.rare_exposures += sum(1 for t in targets_1d if int(t) in self.rare_ids)
        return infe

    def note_nan_batch(self) -> None:
        self.nan_batches += 1

    def infeasible_frac(self) -> float:
        return self.infeasible / max(1, self.samples)

    def nan_frac(self) -> float:
        return self.nan_batches / max(1, self.batches)

    def as_dict(self) -> dict:
        return {
            "samples": self.samples,
            "batches": self.batches,
            "infeasible": self.infeasible,
            "infeasible_frac": round(self.infeasible_frac(), 6),
            "nan_batches": self.nan_batches,
            "nan_frac": round(self.nan_frac(), 6),
            "rare_exposures": self.rare_exposures,
        }

    def check_abort(self) -> None:
        """Raise RuntimeError (compound-abort) if infeasible/NaN fractions exceed thresholds. No-op
        until warmup minimums are met, so a tiny early sample can't trip a spurious abort."""
        if self.samples >= self.min_samples and self.infeasible_frac() > self.abort_infeasible_frac:
            raise RuntimeError(
                f"CTC compound-abort: {self.infeasible}/{self.samples} "
                f"({self.infeasible_frac():.1%}) samples INFEASIBLE (T < U+R) > "
                f"{self.abort_infeasible_frac:.1%}. zero_infinity would silently zero these — the run "
                f"is training on a degenerate signal. Fix strip widths / stride / codec before retrying."
            )
        if self.batches >= self.min_batches and self.nan_frac() > self.abort_nan_frac:
            raise RuntimeError(
                f"CTC compound-abort: {self.nan_batches}/{self.batches} "
                f"({self.nan_frac():.1%}) batches had non-finite loss > {self.abort_nan_frac:.1%}. "
                f"Numerics are unstable (check fp32-CTC cast, lr, grad clip)."
            )
