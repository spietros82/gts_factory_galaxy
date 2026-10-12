#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
editor="${UNITY_EDITOR:-$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity}"
mkdir -p builds/inspection reports/inspection
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/inspection/build.log" --build-output "$PWD/builds/inspection/FactoryGalaxy.x86_64"
