#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/stage4-native
exec 9>runtime/stage4-native/launcher.lock
flock -w 20 9
for unit in braemac-factory-stage4-player braemac-factory-stage4-service; do
 if systemctl --user is-active --quiet "$unit"; then
  [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo 'Unit belongs elsewhere; untouched'; exit 2; }
  systemctl --user stop "$unit"
 fi
done
