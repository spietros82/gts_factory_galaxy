#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
# Historical measured cycle is immutable. A fresh cycle requires a new user milestone.
if [[ -e reports/stage4/capacity ]]; then
 echo "Stage4 measured cycle already exists. Preserved; no automatic rerun."; exit 2
fi
./stage4/stop.sh
cleanup() { ./stage4/start.sh --line-count 1 --vision-device cpu; }
trap cleanup EXIT
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 stage3/.venv/bin/python -m stage4.bench
