#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/stage5-native
run_id="${STAGE5_RUN_ID:-demo}"
[[ "$run_id" =~ ^[A-Za-z0-9_-]{1,48}$ ]] || { echo 'STAGE5_RUN_ID must be a short safe identifier' >&2; exit 2; }
player_data="$PWD/runtime/stage5-native/$run_id"
mkdir -p "$player_data"
exec 9>runtime/stage5-native/launcher.lock
flock -w 20 9
[[ -x builds/stage5/FactoryGalaxy.x86_64 ]] || { echo 'Build first: ./stage5/build.sh' >&2; exit 2; }
[[ -x stage5/.venv/bin/python ]] || { echo 'Stage5 isolated Python environment is absent; see stage5/DEPENDENCIES.md' >&2; exit 2; }
[[ -f stage5/config.local.json ]] || cp stage5/config.example.json stage5/config.local.json
service=braemac-factory-stage5-service
player=braemac-factory-stage5-player
for unit in "$service" "$player"; do
  if systemctl --user is-active --quiet "$unit"; then
    [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo "Unit belongs elsewhere; untouched: $unit" >&2; exit 2; }
  fi
done
if ! systemctl --user is-active --quiet "$service"; then
  stage5/.venv/bin/python - <<'PY'
import json,socket
from pathlib import Path
c=json.loads(Path('stage5/config.local.json').read_text())
assert c['host']=='127.0.0.1'
with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((c['host'],c['port']))
PY
  systemd-run --user --collect --unit="$service" --property=WorkingDirectory="$PWD" \
    --setenv=OMP_NUM_THREADS=1 --setenv=OPENBLAS_NUM_THREADS=1 \
    "$PWD/stage5/.venv/bin/python" -m stage5.service --config stage5/config.local.json
fi
endpoint="$(stage5/.venv/bin/python -c 'import json;c=json.load(open("stage5/config.local.json"));print("http://127.0.0.1:"+str(c["port"]))')"
stage5/.venv/bin/python - "$endpoint" <<'PY'
import json,time,sys,urllib.request
for _ in range(120):
    try:
        with urllib.request.urlopen(sys.argv[1]+'/health',timeout=.5) as r:v=json.load(r)
        if v.get('contract')=='gts.full-state/1' and 'cpu' in v.get('cold',{}):break
    except Exception:pass
    time.sleep(.25)
else:raise SystemExit('Stage5 service not ready; inspect its user journal')
PY
if ! systemctl --user is-active --quiet "$player"; then
  systemd-run --user --collect --unit="$player" --property=WorkingDirectory="$PWD" \
    "$PWD/builds/stage5/FactoryGalaxy.x86_64" \
    -screen-fullscreen 0 -screen-width "${STAGE5_WIDTH:-1600}" -screen-height "${STAGE5_HEIGHT:-900}" \
    -logFile "$player_data/player.log" \
    --data-path "$player_data" --stage4 true --stage5 true \
    --stage4-endpoint "$endpoint" --stage5-endpoint "$endpoint" \
    --line-count "${STAGE5_LINES:-1}" --analysis-views "${STAGE5_VIEWS:-1}" \
    --analysis-hz "${STAGE5_HZ:-5}" --detector-device "${STAGE5_DEVICE:-cpu}" "$@"
fi
echo 'Stage5 local full-frame demo started; loopback API only.'
