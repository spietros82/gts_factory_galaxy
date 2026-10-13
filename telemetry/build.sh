#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if systemctl --user is-active --quiet braemac-factory-stage2-player; then echo 'Stop Stage 2 before rebuilding: ./telemetry/stop.sh' >&2; exit 2; fi
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
mkdir -p builds/stage2 reports/stage2/raw
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/stage2/raw/build.log" --build-output "$PWD/builds/stage2/FactoryGalaxy.x86_64"
