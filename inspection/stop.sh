#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/inspection-native
exec 9>runtime/inspection-native/launcher.lock
if ! flock -w 20 9; then echo 'Another inspection start/stop is in progress; try again shortly.' >&2; exit 2; fi
for unit in braemac-factory-inspection-player braemac-factory-inspection-service; do
 if systemctl --user is-active --quiet "$unit"; then
  if [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" != "$PWD" ]]; then
   echo "Unit $unit belongs to another working directory; not stopped." >&2; exit 2
  fi
  systemctl --user stop "$unit"
 fi
done
