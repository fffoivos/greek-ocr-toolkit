#!/usr/bin/env bash
# Build only a pre-staged, owner-verified CPython tarball; no downloads.
set -euo pipefail
set +x
[[ $# == 3 ]] || { echo 'Usage: install_python.sh Python-3.11.3.tar.xz EXPECTED_SHA256 /absolute/install/prefix' >&2; exit 2; }
[[ $(uname -s) == Linux && $(uname -m) == x86_64 && $3 == /* && $2 =~ ^[a-f0-9]{64}$ ]] || exit 2
if [[ -x $3/bin/python3.11 ]] && [[ $("$3/bin/python3.11" -c 'import platform; print(platform.python_version())') == 3.11.3 ]]; then exit 0; fi
printf '%s  %s\n' "$2" "$1" | sha256sum --check --status
BUILD=$(mktemp -d)
trap 'rm -rf -- "$BUILD"' EXIT
tar -xJf "$1" -C "$BUILD" --no-same-owner
cd "$BUILD/Python-3.11.3"
./configure --prefix="$3" --with-ensurepip=install
make -j2
make altinstall
"$3/bin/python3.11" -c 'import ssl,sqlite3,bz2,lzma,venv; assert __import__("sys").version_info[:3] == (3,11,3)'
