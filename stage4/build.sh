#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for unit in braemac-factory-stage4-player braemac-factory-stage3-player; do
 if systemctl --user is-active --quiet "$unit"; then echo "Stop this project's player before building: $unit"; exit 2; fi
done
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
mkdir -p builds/stage4 reports/stage4/raw
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/stage4/raw/build.log" --build-output "$PWD/builds/stage4/FactoryGalaxy.x86_64" --resizable-window true
