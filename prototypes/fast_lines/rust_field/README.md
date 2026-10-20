# Experimental M15 numerical batch

Default Python requires no extension. Build the Rust C ABI library sequentially:

```sh
sh prototypes/fast_lines/rust_field/build.sh
FAST_LINES_FIELD_TEST_NATIVE=1 python -m pytest -q prototypes/fast_lines/rust_field
FAST_LINES_FIELD_BACKEND=rust python -m pytest -q prototypes/fast_lines
```

Use an absolute `CARGO_TARGET_DIR` when sharing it between build and Python.
Set the backend before importing the stack. Explicit Rust without a library fails
immediately; there is no fallback. `COUNTERS` counts actual Python/FFI entries,
field preparations and copied typed-array bytes; read differences around calls.
The default stays Python pending independent adoption. No Python callbacks execute
inside Rust. Python still prepares windows, sweeps dependent columns, smooths with
SciPy and runs both refinements, certification and all physical decisions.

This dependency-free cdylib needs no Python linker flags, Python development ABI,
absolute interpreter path, vendor directory or Cargo-home setup. The lockfile
and release profile are committed. Standard Cargo `RUSTFLAGS`, `CARGO_TARGET_DIR`
and `CARGO_BUILD_TARGET` remain configurable. For a custom build location/target,
set `FAST_LINES_FIELD_LIBRARY` to the complete library filename. Default discovery
uses `CARGO_TARGET_DIR/release` or this crate's `target/release`. Only the recorded
Apple aarch64 compiler/NumPy combination is qualified; other targets need parity
qualification (especially interpolation FMA/reduction details).

`CONTRACT.md` freezes the typed boundary. `fixtures/` contains actual measured
profiles/windows and six complete numeric render/certify consumers. The consumer
fixtures replace pixel preparation/remap with the frozen inputs, then execute the
real seed/mesh/row/certification logic. They do not claim pixel-preparation tests.
Native tests are enabled explicitly; missing builds then fail rather than skip.
No test skips when a capture is absent. The full raster/230-page/clock ledgers are
local replay evidence under `.astra`, separate from these reproducible tests.

The fixture pool stores each bit-identical measured profile identity once in
`fixtures/profiles.npz`. Batch files retain their other arrays; manifest references
bind exact profile dtype, shape, order and bytes. The six compact render JSON files
retain original prepared-component provenance and expected consumer output;
component dictionaries use one shared column-name list with lossless value rows;
`fixture_data.py` checks archive hashes before reconstructing test inputs. No test
requires `.astra` or a second checkout. `test_real_render_through_certify` checks
actual backend counter deltas, and a selector-bypass mutation must fail that
assertion even when the Python calculation would preserve the expected geometry.
