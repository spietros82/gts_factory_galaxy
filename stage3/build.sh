#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if systemctl --user is-active --quiet braemac-factory-stage3-player; then echo 'Stop Stage 3 before rebuilding: ./stage3/stop.sh' >&2; exit 2; fi
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
mkdir -p builds/stage3 reports/stage3/raw
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/stage3/raw/build.log" --build-output "$PWD/builds/stage3/FactoryGalaxy.x86_64"
