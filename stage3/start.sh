#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p runtime/stage3-native
exec 9>runtime/stage3-native/launcher.lock
flock -w 20 9
player=braemac-factory-stage3-player
service=braemac-factory-stage3-service
build_dir="${STAGE3_BUILD_DIR:-builds/stage3}"
width="${STAGE3_WIDTH:-1600}"
height="${STAGE3_HEIGHT:-900}"
[[ "$width" =~ ^[1-9][0-9]{2,3}$ && "$height" =~ ^[1-9][0-9]{2,3}$ ]] || { echo 'STAGE3_WIDTH/HEIGHT must be positive integer pixel dimensions (3–4 digits)'; exit 2; }
[[ -x "$build_dir/FactoryGalaxy.x86_64" ]] || { echo 'Build first: ./stage3/build.sh'; exit 2; }
[[ -f stage3/models/policy.json ]] || { echo 'Frozen models absent: see stage3/README.md reproduction instructions'; exit 2; }
[[ -f stage3/config.local.json ]] || cp stage3/config.example.json stage3/config.local.json
for unit in "$service" "$player"; do
 if systemctl --user is-active --quiet "$unit"; then
  [[ "$(systemctl --user show "$unit" -p WorkingDirectory --value)" == "$PWD" ]] || { echo 'Unit belongs elsewhere; untouched'; exit 2; }
 fi
done
if ! systemctl --user is-active --quiet "$service"; then
 stage3/.venv/bin/python - <<'PY'
import json,socket
from pathlib import Path
c=json.loads(Path('stage3/config.local.json').read_text());assert c['host']=='127.0.0.1'
with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind((c['host'],c['port']))
PY
 systemd-run --user --collect --unit="$service" --property=WorkingDirectory="$PWD" --setenv=OPENBLAS_NUM_THREADS=2 --setenv=OMP_NUM_THREADS=2 "$PWD/stage3/.venv/bin/python" -m stage3.service --config stage3/config.local.json
fi
endpoint="$(stage3/.venv/bin/python -c 'import json; c=json.load(open("stage3/config.local.json")); print("http://127.0.0.1:"+str(c["port"]))')"
stage3/.venv/bin/python - "$endpoint" <<'PY'
import json,sys,time,urllib.request
for _ in range(80):
 try:
  with urllib.request.urlopen(sys.argv[1]+'/health',timeout=.5) as r:v=json.load(r)
  if v['contract']=='gts.three-frame/1' and v['ready']:break
 except Exception:pass
 time.sleep(.25)
else:raise SystemExit('Stage3 service not ready; inspect journalctl --user -u braemac-factory-stage3-service')
PY
if ! systemctl --user is-active --quiet "$player"; then
 systemd-run --user --collect --unit="$player" --property=WorkingDirectory="$PWD" "$(realpath -- "$build_dir/FactoryGalaxy.x86_64")" -screen-fullscreen 0 -screen-width "$width" -screen-height "$height" -logFile "$PWD/runtime/stage3-native/player.log" --data-path "$PWD/runtime/stage3-native" --profile 1 --frame-target 60 --presentation true --plc-demo true --stage3 true --stage3-endpoint "$endpoint" "$@"
fi
echo "Stage3 started at ${width}×${height}; resize the native window as needed. Qwen only by explicit action."
