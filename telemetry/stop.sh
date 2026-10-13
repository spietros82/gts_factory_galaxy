#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/stage2-native
exec 9>runtime/stage2-native/launcher.lock
flock -w 20 9
unit=braemac-factory-stage2-player
if systemctl --user is-active --quiet "$unit"; then
 [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo 'Unit belongs elsewhere; untouched.' >&2; exit 2; }
 systemctl --user stop "$unit"
fi
