#!/bin/sh
set -eu
cd "$(dirname "$0")"
# No Python ABI, vendor tree, cargo-home config or third-party dependencies.
# CARGO_TARGET_DIR and RUSTFLAGS are standard configurable Cargo inputs.
cargo build --release --locked --offline -j 1
