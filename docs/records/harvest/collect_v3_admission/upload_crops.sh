#!/bin/sh
# Preparation only: no transport occurs unless this script is explicitly invoked.
set -eu
exec python3 "$(dirname "$0")/upload_crops.py" "$@"
