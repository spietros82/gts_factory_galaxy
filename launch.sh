#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x builds/linux/FactoryGalaxy.x86_64 ]]; then echo 'Standalone build missing; run ./build.sh after Unity licence and Linux support are available.' >&2; exit 2; fi
task_data_path="${GTS_DATA_PATH:-$PWD/runtime}"
args=("$@")
for ((i=0;i<${#args[@]};i++)); do
 if [[ "${args[i]}" == --data-path ]] && (( i+1 < ${#args[@]} )); then task_data_path="${args[i+1]}"; fi
done
mkdir -p "$task_data_path"
exec ./builds/linux/FactoryGalaxy.x86_64 -screen-fullscreen 0 -screen-width 1600 -screen-height 900 -logFile "$PWD/runtime/player.log" --data-path "$task_data_path" "$@"
