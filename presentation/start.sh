#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
vision_python="${VISION_PYTHON:-$PWD/.venv/bin/python}"
if [[ ! -x "$vision_python" || ! -x builds/stage1/FactoryGalaxy.x86_64 ]]; then echo 'Stage 1 build or existing Python environment unavailable; see presentation/README.md.' >&2; exit 2; fi
if [[ ! -f inspection/config.local.json ]]; then cp inspection/config.example.json inspection/config.local.json; fi
mkdir -p runtime/stage1-native runtime/inspection-native
exec 9>runtime/inspection-native/launcher.lock
flock -w 20 9 || { echo 'Another launch/stop is in progress.' >&2; exit 2; }
for unit in braemac-factory-inspection-service braemac-factory-stage1-player; do
 if systemctl --user is-active --quiet "$unit" && [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" != "$PWD" ]]; then echo "Unit $unit belongs to another working directory; no changes made." >&2; exit 2; fi
done
endpoint="$("$vision_python" -m inspection.startup endpoint)"
if ! systemctl --user is-active --quiet braemac-factory-inspection-service; then
 "$vision_python" -m inspection.startup port
 systemctl --user reset-failed braemac-factory-inspection-service 2>/dev/null || true
 systemd-run --user --collect --unit=braemac-factory-inspection-service --property=WorkingDirectory="$PWD" --property=Environment=OMP_NUM_THREADS=2 --property=Environment=OPENBLAS_NUM_THREADS=2 "$vision_python" -m inspection.service --config inspection/config.local.json
fi
"$vision_python" -m inspection.startup ready
if ! systemctl --user is-active --quiet braemac-factory-stage1-player; then
 systemctl --user reset-failed braemac-factory-stage1-player 2>/dev/null || true
 systemd-run --user --collect --unit=braemac-factory-stage1-player --property=WorkingDirectory="$PWD" "$PWD/builds/stage1/FactoryGalaxy.x86_64" -screen-fullscreen 0 -screen-width "${STAGE1_WIDTH:-1600}" -screen-height "${STAGE1_HEIGHT:-900}" -logFile "$PWD/runtime/stage1-native/player.log" --focused-inspection true --inspection-endpoint "$endpoint" --data-path "$PWD/runtime/stage1-native" --profile 1 --frame-target 60 "$@" --presentation true --disable-explanations true
 sleep 1
fi
systemctl --user is-active --quiet braemac-factory-stage1-player || { echo 'Stage 1 native player failed; inspect its user-unit journal.' >&2; exit 2; }
echo 'Stage 1 brewery ready. Products: LAGER / IPA / STOUT. Views: F5 / F6 / F7 / F8. No language-model inference.'
