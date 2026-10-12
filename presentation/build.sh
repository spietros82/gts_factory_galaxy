#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if systemctl --user is-active --quiet braemac-factory-stage1-player; then echo 'Stop the Stage 1 player with ./presentation/stop.sh before rebuilding.' >&2; exit 2; fi
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
mkdir -p builds/stage1 reports/stage1/raw
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/stage1/raw/build.log" --build-output "$PWD/builds/stage1/FactoryGalaxy.x86_64"
