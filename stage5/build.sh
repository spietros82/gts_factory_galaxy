#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for unit in braemac-factory-stage5-player braemac-factory-stage4-player braemac-factory-stage3-player; do
  if systemctl --user is-active --quiet "$unit"; then
    echo "Stop the project's player before building: $unit" >&2
    exit 2
  fi
done
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
[[ -x "$editor" ]] || { echo "Unity Editor not found: $editor" >&2; exit 2; }
mkdir -p builds/stage5 reports/stage5
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" \
  -executeMethod BuildFactory.Build \
  -logFile "$PWD/reports/stage5/build.log" \
  --build-output "$PWD/builds/stage5/FactoryGalaxy.x86_64" \
  --resizable-window true
