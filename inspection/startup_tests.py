"""Startup regression checks only; no learned or language-model inference."""
import json
import socket
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .startup import check_port, configuration, wait_ready


class StartupTests(unittest.TestCase):
    def test_available_port(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        check_port('127.0.0.1', port)

    def test_listener_preserved(self):
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            port = listener.getsockname()[1]
            with self.assertRaisesRegex(RuntimeError, 'No existing process was stopped'):
                check_port('127.0.0.1', port)
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                accepted, _ = listener.accept()
                accepted.close()

    def test_linux_time_wait_does_not_block_restart(self):
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            port = listener.getsockname()[1]
            with socket.create_connection(('127.0.0.1', port), timeout=1) as client:
                accepted, _ = listener.accept()
                accepted.close()  # server actively closes, leaving its TIME_WAIT
                self.assertEqual(client.recv(1), b'')
        with socket.socket() as old_probe:
            with self.assertRaises(OSError):
                old_probe.bind(('127.0.0.1', port))
        check_port('127.0.0.1', port)

    def test_rejects_external_binding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.json'
            path.write_text(json.dumps({'host': '0.0.0.0', 'port': 8810}))
            with self.assertRaisesRegex(ValueError, '127.0.0.1'):
                configuration(path)

    def test_health_and_invalid_contract(self):
        class Handler(BaseHTTPRequestHandler):
            contract = 'gts.focused-frame/1'
            def log_message(self, *args):
                pass
            def do_GET(self):
                body = json.dumps({'state': 'ready', 'contract': self.contract,
                                   'backend': 'fake/startup-only'}).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        with HTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            endpoint = f'http://127.0.0.1:{server.server_port}'
            try:
                self.assertEqual(wait_ready(endpoint, .5)['backend'], 'fake/startup-only')
                Handler.contract = 'unrelated'
                with self.assertRaisesRegex(RuntimeError, 'Unexpected inspection health contract'):
                    wait_ready(endpoint, .2)
            finally:
                server.shutdown()
                thread.join()


if __name__ == '__main__':
    unittest.main()
