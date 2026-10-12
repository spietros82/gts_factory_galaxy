#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
vision_python="${VISION_PYTHON:-$PWD/.venv/bin/python}"
if [[ ! -x "$vision_python" || ! -x builds/inspection/FactoryGalaxy.x86_64 ]]; then
 echo 'Inspection Python environment or native build unavailable; see inspection/README.md' >&2; exit 2
fi
if [[ ! -f inspection/models/cap-rf.joblib ]]; then echo 'Frozen learned artifact unavailable; see inspection/README.md' >&2; exit 2; fi
if [[ ! -f inspection/config.local.json ]]; then cp inspection/config.example.json inspection/config.local.json; fi
mkdir -p runtime/inspection-native
# Serialise start/stop and rapid repeated clicks without changing other units.
exec 9>runtime/inspection-native/launcher.lock
if ! flock -w 20 9; then echo 'Another inspection start/stop is in progress; try again shortly.' >&2; exit 2; fi
task_endpoint="$("$vision_python" -m inspection.startup endpoint)"
for unit in braemac-factory-inspection-service braemac-factory-inspection-player; do
 if systemctl --user is-active --quiet "$unit" && [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" != "$PWD" ]]; then
  echo "Unit $unit belongs to another working directory; no changes made." >&2; exit 2
 fi
done
if ! systemctl --user is-active --quiet braemac-factory-inspection-service; then
 "$vision_python" -m inspection.startup port
 systemctl --user reset-failed braemac-factory-inspection-service 2>/dev/null || true
 systemd-run --user --collect --unit=braemac-factory-inspection-service --property=WorkingDirectory="$PWD" --property=Environment=OMP_NUM_THREADS=2 --property=Environment=OPENBLAS_NUM_THREADS=2 "$vision_python" -m inspection.service --config inspection/config.local.json
fi
echo 'Checking inspection service readiness...'
"$vision_python" -m inspection.startup ready
systemctl --user is-active --quiet braemac-factory-inspection-service || { echo 'Inspection service is not active; native player was not newly started.' >&2; exit 2; }
if ! systemctl --user is-active --quiet braemac-factory-inspection-player; then
 systemctl --user reset-failed braemac-factory-inspection-player 2>/dev/null || true
 systemd-run --user --collect --unit=braemac-factory-inspection-player --property=WorkingDirectory="$PWD" "$PWD/builds/inspection/FactoryGalaxy.x86_64" -screen-fullscreen 0 -screen-width 1600 -screen-height 900 -logFile "$PWD/runtime/inspection-native/player.log" --focused-inspection true --inspection-endpoint "$task_endpoint" --data-path "$PWD/runtime/inspection-native" --profile 2 --frame-target 60 "$@"
 sleep 1
fi
systemctl --user is-active --quiet braemac-factory-inspection-player || { echo 'Native inspector failed to stay running; inspect its user-unit journal.' >&2; exit 2; }
echo 'Focused inspection is running. Existing instances are reused; stop with ./inspection/stop.sh'
