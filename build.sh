#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
editor="${UNITY_EDITOR:-}"
if [[ -z "$editor" ]]; then
 editor="$HOME/Unity/Hub/Editor/6000.6.5f1/Editor/Unity"
fi
if [[ ! -x "$editor" ]]; then echo 'Unity Editor unavailable. Set UNITY_EDITOR to a licensed Editor executable.' >&2; exit 2; fi
mkdir -p reports builds/linux
"$editor" -batchmode -nographics -quit -projectPath "$PWD/UnityProject" -executeMethod BuildFactory.Build -logFile "$PWD/reports/unity-build.log" --build-output "$PWD/builds/linux/FactoryGalaxy.x86_64"
