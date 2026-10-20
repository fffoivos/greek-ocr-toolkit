# Frozen M15 batch boundary, 14 October 2026

Oracle: e8a29a2 runtime geometry_page_field.render nested shifts_many; H changes only protect.
One call scores C independent columns, K knot windows, W padded samples and L lags.
Prepared per field: profiles (Y,X), ys(Y), lag(L), lengths(K). Float inputs are finite float64;
profiles originally float32, promoted exactly once. Coordinates/lag/delta are native pixels.
The call consumes before(C,K,W), moved(C,K,W), columns(C), optional energy(1 or C,K).
The broadcast before/energy are immutable. No caller input may be changed. Views stay owned
and alive across synchronous ctypes; Rust borrows C-contiguous arrays only for the call.
Python explicitly copies non-contiguous/broadcast views. Profiles transpose/promote once per
field, not once per column; this conversion is part of render cost. Outputs are owned NumPy
float64 delta/weight(C,K). A diagnostic scores(C,K,L) output supports first-difference tests.

Preserve np.interp zero outside and closed endpoints, current platform FMA, original sample
sum order, masked mean/energy (padded slots zero), 1e-9 denominator floor, first argmax ties,
parabolic interior lag refinement and nonnegative weights; lengths<5 forces both outputs zero.
No cross-column outward dependency moves: before/moved prepared by existing render, batches
of at most8 only in joint refinements. Gaussian filtering, mesh updates, templates and their
shared immutable energy, seed/scale/pixel decisions and certify/invert_points remain Python.
Empty pages bypass the batch; actual calls require C,K,W>0, Y>=2, L>=2, W>=lengths>=0.
Profiles are the measured bounded body-occupancy values of this caller, before is demeaned
from them, and no NaN/overflow-producing arbitrary numerical inputs are part of this ABI.
Inverse-domain NaNs and consumers are unchanged outside this boundary.

This is a bounded partial port, not the desired entire per-field mesh kernel. Native selection
replaces the scoring work and has no numerical callbacks or fallback. Default remains Python;
this explicit experimental route and offline oracle coexist pending independent adoption.
No coordinate tolerance is allowed: require bit-exact intermediate scores and outputs first,
then exact field/certificate/discrete decisions and final masks. A mismatch keeps Rust experimental.
