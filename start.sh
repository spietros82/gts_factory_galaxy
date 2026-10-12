#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! systemctl --user is-active --quiet braemac-factory-edge; then ./start-services.sh; fi
if ! systemctl --user is-active --quiet braemac-factory-galaxy; then
 systemd-run --user --unit=braemac-factory-galaxy --property=WorkingDirectory="$PWD" "$PWD/launch.sh" "$@"
else
 echo 'Factory Galaxy is already running; no additional player started.'
fi
