import io
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from stage5.service import Engine, validate


def png_bytes():
    out = io.BytesIO()
    Image.new('RGB', (640, 640), (40, 60, 80)).save(out, format='PNG')
    return out.getvalue()


def metadata(frame='frame1', sequence=1, session='session1', line='line1', camera='cam1'):
    return {'line_id': line, 'session_id': session, 'camera_id': camera,
            'frame_id': frame, 'sequence': sequence,
            'capture_utc': datetime.now(timezone.utc).isoformat(),
            'source_time': time.monotonic(), 'width': 640, 'height': 640}


class FakeDetector:
    cold_load_ms = 0
    cpu_partitions = []
    gpu_name = None

    def __init__(self, gate=None, detections=None):
        self.gate = gate
        self.detections = detections or []

    def infer(self, image):
        if self.gate:
            self.gate.wait(2)
        return [dict(d, box=list(d['box'])) for d in self.detections], {'actual_device': 'fake/offline', 'detector_ms': 0.1,
                    'gpu_compute_delta_ns': None, 'preprocessing_ms': 0.0,
                    'inference_completed_ms': 0.1, 'postprocessing_ms': 0.0}


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.image = png_bytes()
        self.registry = {'line1': 'session1'}

    def test_accepts_bounded_current_png(self):
        self.assertGreater(validate(metadata(), self.image, self.registry), 0)

    def test_rejects_truth_fields_and_wrong_format(self):
        m = metadata(); m['bottle_id'] = 'hidden'
        with self.assertRaisesRegex(ValueError, 'Unexpected metadata'):
            validate(m, self.image, self.registry)
        with self.assertRaisesRegex(ValueError, '640'):
            validate(metadata(), b'not png', self.registry)

    def test_rejects_stale_and_unregistered_session(self):
        m = metadata(); m['capture_utc'] = '2000-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError, 'stale'):
            validate(m, self.image, self.registry)
        with self.assertRaisesRegex(ValueError, 'session'):
            validate(metadata(session='retired'), self.image, self.registry)

    def make_engine(self, gate=None, queue_capacity=2, detections=None):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        return Engine({'data_path': str(Path(root.name) / 'data'),
                       'queue_capacity': queue_capacity, 'device': 'cpu',
                       'deadline_seconds': 0.5, 'image_limit': 8,
                       'monitoring': False}, {'cpu': FakeDetector(gate, detections)}), root

    def test_registry_reset_clears_sessions_and_rejects_retired_work(self):
        e, _ = self.make_engine()
        self.addCleanup(e.close)
        e.register([{'line_id': 'line1', 'session_id': 'session1'}])
        e.register([{'line_id': 'line1', 'session_id': 'session2'}])
        with self.assertRaisesRegex(ValueError, 'session'):
            e.submit(metadata(), self.image)
        self.assertEqual(e.state()['queue_depth'], 0)

    def test_old_inference_cannot_publish_after_session_reset(self):
        gate = threading.Event()
        e, _ = self.make_engine(gate)
        self.addCleanup(e.close)
        e.register([{'line_id': 'line1', 'session_id': 'session1'}])
        e.submit(metadata('old-frame', 1), self.image)
        deadline = time.time() + 1
        while e.current != 'processing' and time.time() < deadline:
            time.sleep(.005)
        e.register([{'line_id': 'line1', 'session_id': 'session2'}])
        gate.set()
        e.queue.join()
        self.assertEqual(e.latest, {})
        self.assertEqual(e.counts['cancelled'], 1)
        e.submit(metadata('new-frame', 1, session='session2'), self.image)
        e.queue.join()
        self.assertEqual(e.latest[('line1', 'session2', 'cam1')]['metadata']['frame_id'], 'new-frame')

    def test_tracks_are_isolated_per_line_and_camera(self):
        detections = [{'box': [20, 20, 80, 150], 'score': .9, 'class_name': 'bottle'}]
        e, _ = self.make_engine(detections=detections)
        self.addCleanup(e.close)
        e.register([{'line_id': 'line1', 'session_id': 'session1'},
                    {'line_id': 'line2', 'session_id': 'session2'}])
        e.submit(metadata('frame1', 1, line='line1'), self.image)
        e.submit(metadata('frame2', 1, session='session2', line='line2'), self.image)
        e.queue.join()
        self.assertEqual(set(e.trackers), {('line1', 'session1', 'cam1'), ('line2', 'session2', 'cam1')})
        self.assertIsNot(e.trackers[('line1', 'session1', 'cam1')],
                         e.trackers[('line2', 'session2', 'cam1')])
        for key in e.trackers:
            self.assertEqual(e.trackers[key].next_id, 1)

    def test_duplicate_and_out_of_order_frames_are_rejected(self):
        e, _ = self.make_engine()
        self.addCleanup(e.close)
        e.register([{'line_id': 'line1', 'session_id': 'session1'}])
        e.submit(metadata('frame2', 2), self.image)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            e.submit(metadata('frame2', 3), self.image)
        with self.assertRaisesRegex(ValueError, 'out-of-order'):
            e.submit(metadata('frame1', 1), self.image)

    def test_queue_is_bounded_and_backpressure_is_explicit(self):
        gate = threading.Event()
        e, _ = self.make_engine(gate, queue_capacity=1)
        self.addCleanup(e.close)
        e.register([{'line_id': 'line1', 'session_id': 'session1'}])
        e.submit(metadata('frame1', 1), self.image)
        deadline = time.time() + 1
        while e.current != 'processing' and time.time() < deadline:
            time.sleep(.005)
        e.submit(metadata('frame2', 2), self.image)
        with self.assertRaisesRegex(ValueError, 'queue-full'):
            e.submit(metadata('frame3', 3), self.image)
        self.assertEqual(e.queue.qsize(), 1)
        self.assertEqual(e.state()['drop_reasons'].get('queue-full'), 1)
        gate.set()
        e.queue.join()


if __name__ == '__main__':
    unittest.main()
