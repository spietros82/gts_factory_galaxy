"""Local launcher checks; never stop listeners or invoke a model."""
import argparse
import json
import socket
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener


def configuration(path):
    cfg = json.loads(Path(path).read_text())
    if cfg['host'] != '127.0.0.1':
        raise ValueError('Inspection service must remain on 127.0.0.1')
    if type(cfg['port']) is not int or not 1024 <= cfg['port'] <= 65535:
        raise ValueError('Inspection port must be an integer from 1024 to 65535')
    return cfg


def check_port(host, port):
    # Match ThreadingHTTPServer.allow_reuse_address. A plain bind can reject
    # TIME_WAIT connections even though no application is listening anymore.
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((host, port))
        except OSError as exc:
            raise RuntimeError(
                f'Cannot start inspector at {host}:{port}: {exc.strerror}. '
                f'Inspect the listener with: ss -ltnp \'( sport = :{port} )\'. '
                'No existing process was stopped. Do not stop an unrelated listener; '
                'choose an unused loopback port in inspection/config.local.json '
                'or stop a separately launched inspector you own.'
            ) from exc


def wait_ready(endpoint, timeout=15):
    # Bypass environment proxies: this check must only use the local endpoint.
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    last_error = 'No reply'
    while time.monotonic() < deadline:
        try:
            with opener.open(endpoint + '/health', timeout=min(1, timeout)) as reply:
                health = json.loads(reply.read(4096))
            if not isinstance(health, dict):
                raise ValueError('Invalid inspection health response')
            if health.get('state') == 'ready' and health.get('contract') == 'gts.focused-frame/1':
                return health
            last_error = 'Unexpected inspection health contract'
        except (OSError, ValueError) as exc:
            last_error = str(exc)
        time.sleep(min(.1, max(0, deadline - time.monotonic())))
    raise RuntimeError(
        f'Inspector at {endpoint} did not become ready: {last_error}. '
        'See: journalctl --user -u braemac-factory-inspection-service -n 30 --no-pager. '
        'The native player was not newly started.'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['port', 'ready', 'endpoint'])
    parser.add_argument('--config', default='inspection/config.local.json')
    args = parser.parse_args()
    try:
        cfg = configuration(args.config)
        endpoint = f"http://{cfg['host']}:{cfg['port']}"
        if args.operation == 'port':
            check_port(cfg['host'], cfg['port'])
        elif args.operation == 'ready':
            health = wait_ready(endpoint)
            print(f"Inspector ready: {endpoint} ({health['backend']})")
        else:
            print(endpoint)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f'Inspection startup failed: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
