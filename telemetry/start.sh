#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
unit=braemac-factory-stage2-player
[[ -x builds/stage2/FactoryGalaxy.x86_64 ]] || { echo 'Build first: ./telemetry/build.sh' >&2; exit 2; }
mkdir -p runtime/stage2-native
exec 9>runtime/stage2-native/launcher.lock
flock -w 20 9
if systemctl --user is-active --quiet "$unit"; then
 [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo 'Stage 2 unit belongs to another directory; untouched.' >&2; exit 2; }
 echo 'Stage 2 already running.'; exit 0
fi
systemctl --user reset-failed "$unit" 2>/dev/null || true
systemd-run --user --collect --unit="$unit" --property=WorkingDirectory="$PWD" "$PWD/builds/stage2/FactoryGalaxy.x86_64" -screen-fullscreen 0 -screen-width "${STAGE2_WIDTH:-1600}" -screen-height "${STAGE2_HEIGHT:-900}" -logFile "$PWD/runtime/stage2-native/player.log" --data-path "$PWD/runtime/stage2-native" --focused-inspection true --profile 1 --frame-target 60 --presentation true --plc-demo true --disable-explanations true "$@"
sleep 1
systemctl --user is-active --quiet "$unit"
echo 'Stage 2 ready. 1/2/3 modes; B blockage; C clear; R reset; Space pause. No inference.'
