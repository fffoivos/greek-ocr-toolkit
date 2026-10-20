#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
set -euo pipefail
root=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018
cmake -S "$root/runtime/zlib-ng-src" -B "$root/runtime/zlib-ng-build" -DCMAKE_BUILD_TYPE=Release -DZLIB_COMPAT=ON -DZLIB_ENABLE_TESTS=OFF -DWITH_GTEST=OFF -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX="$root/runtime/png-codec"
cmake --build "$root/runtime/zlib-ng-build" --parallel 4
cmake --install "$root/runtime/zlib-ng-build"
lib=$(find "$root/runtime/png-codec" -name 'libz.so.*' -type f -print -quit)
[[ -n "$lib" ]]
export LD_PRELOAD="$lib"
srun --cpu-bind=none /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B "$root/crop_probe.py"
