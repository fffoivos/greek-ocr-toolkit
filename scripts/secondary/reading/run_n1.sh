#!/usr/bin/env bash
# Outputs: artifacts/n1/answers/<root>/<context>.<reader>.*
# Prepared launcher; tests inject an entirely local fake reader and limit probe.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec python3 -B "$S/n1_launch.py" "$@"
