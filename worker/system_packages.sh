#!/usr/bin/env bash
# Owner runs this ON THE LINUX BOX. No invocation by the W1d build.
set -euo pipefail
set +x
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'Linux x86_64 required' >&2; exit 1; }
. /etc/os-release
[[ ${ID:-} == debian && ${VERSION_ID:-} == 12 ]] || { echo 'Supported distro: Debian 12' >&2; exit 1; }
SUDO=()
if [[ $(id -u) != 0 ]]; then command -v sudo >/dev/null; SUDO=(sudo); fi
"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y bash coreutils tar gzip git ca-certificates rsync openssh-client util-linux procps \
  libjpeg62-turbo libpng16-16 libgomp1 fonts-dejavu-core \
  build-essential pkg-config libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
  libsqlite3-dev libffi-dev liblzma-dev xz-utils
