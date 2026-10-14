#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for unit in braemac-factory-stage5-dataset-player braemac-factory-stage5-player braemac-factory-stage5-service; do
  if systemctl --user is-active --quiet "$unit"; then
    [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo "Unit belongs elsewhere; untouched: $unit" >&2; exit 2; }
    systemctl --user stop "$unit"
  fi
done
echo 'Stopped this project’s Stage5 player/service units.'
