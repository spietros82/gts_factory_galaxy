#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/stage4-native
exec 9>runtime/stage4-native/launcher.lock
flock -w 20 9
player=braemac-factory-stage4-player
service=braemac-factory-stage4-service
[[ -x builds/stage4/FactoryGalaxy.x86_64 ]] || { echo 'Build first: ./stage4/build.sh'; exit 2; }
[[ -f stage3/models/policy.json ]] || { echo 'Frozen models absent; follow stage3/MODEL.md'; exit 2; }
[[ -f stage4/config.local.json ]] || cp stage4/config.example.json stage4/config.local.json
for unit in "$service" "$player"; do
 if systemctl --user is-active --quiet "$unit"; then
  [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo 'Unit belongs elsewhere; untouched'; exit 2; }
 fi
done
if ! systemctl --user is-active --quiet "$service"; then
 stage3/.venv/bin/python - <<'PY'
import json,socket
from pathlib import Path
c=json.loads(Path('stage4/config.local.json').read_text());assert c['host']=='127.0.0.1'
with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind((c['host'],c['port']))
PY
 systemd-run --user --collect --unit="$service" --property=WorkingDirectory="$PWD" --setenv=OPENBLAS_NUM_THREADS=2 --setenv=OMP_NUM_THREADS=2 "$PWD/stage3/.venv/bin/python" -m stage4.service --config stage4/config.local.json
fi
endpoint="$(stage3/.venv/bin/python -c 'import json;c=json.load(open("stage4/config.local.json"));print("http://127.0.0.1:"+str(c["port"]))')"
stage3/.venv/bin/python - "$endpoint" <<'PY'
import json,time,sys,urllib.request
for _ in range(80):
 try:
  with urllib.request.urlopen(sys.argv[1]+'/health',timeout=.5) as r:v=json.load(r)
  if v['contract']=='gts.multi-state/1' and v['ready']:break
 except Exception:pass
 time.sleep(.25)
else:raise SystemExit('Stage4 service not ready; inspect user journal')
PY
if ! systemctl --user is-active --quiet "$player"; then
 systemd-run --user --collect --unit="$player" --property=WorkingDirectory="$PWD" "$PWD/builds/stage4/FactoryGalaxy.x86_64" -screen-fullscreen 0 -screen-width "${STAGE4_WIDTH:-1600}" -screen-height "${STAGE4_HEIGHT:-900}" -logFile "$PWD/runtime/stage4-native/player.log" --data-path "${STAGE4_DATA_PATH:-$PWD/runtime/stage4-native}" --stage4 true --stage4-endpoint "$endpoint" "$@"
fi
echo 'Stage4 native player started; local API only (no browser dashboard).'
