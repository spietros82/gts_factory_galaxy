#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ -f config.local.json ]] || cp config.example.json config.local.json
python3 - <<'PY'
import json,socket
cfg=json.load(open('config.local.json'))
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:s.bind((cfg['host'],cfg['port']))
except OSError:raise SystemExit('Configured factory service port occupied; no listener stopped.')
finally:s.close()
PY
systemd-run --user --unit=braemac-factory-edge --property=WorkingDirectory="$PWD" /usr/bin/python3 -m factory.service --config config.local.json
