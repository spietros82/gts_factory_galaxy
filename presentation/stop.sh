#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/inspection-native
exec 9>runtime/inspection-native/launcher.lock
flock -w 20 9 || { echo 'Another launch/stop is in progress.' >&2; exit 2; }
unit=braemac-factory-stage1-player
if systemctl --user is-active --quiet "$unit"; then
 if [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" != "$PWD" ]]; then echo 'Stage 1 unit belongs to another directory; not stopped.' >&2; exit 2; fi
 systemctl --user stop "$unit"
fi
echo 'Stage 1 player stopped. Shared inspection service and prior demos left unchanged.'
