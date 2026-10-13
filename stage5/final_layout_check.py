"""Bounded CPU/GPU live smoke on final Stage5 camera layers; not a capacity sweep."""
import json, os, subprocess, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'stage5/config.local.json'
OUT = ROOT / 'reports/stage5/benchmark/final-layout-sanity.json'
API = 'http://127.0.0.1:8840'
original = CFG.read_bytes()
results = []

def stop():
    subprocess.run([str(ROOT / 'stage5/stop.sh')], cwd=ROOT,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=15, check=False)

try:
    stop()
    base = json.loads(original)
    for device in ('cpu', 'gpu'):
        cfg = dict(base, device=device,
                   data_path=f'runtime/stage5-layout-final-{device}')
        CFG.write_text(json.dumps(cfg, indent=2) + '\n')
        env = os.environ.copy()
        env.update(STAGE5_RUN_ID=f'final-layout-{device}', STAGE5_LINES='1',
                   STAGE5_VIEWS='3', STAGE5_HZ='5', STAGE5_DEVICE=device,
                   STAGE5_WIDTH='1920', STAGE5_HEIGHT='1080')
        subprocess.run([str(ROOT / 'stage5/start.sh'), '--no-build',
                        '--fixed-1080p', 'true', '--duration', '19'],
                       cwd=ROOT, env=env, check=True, timeout=15,
                       stdout=subprocess.DEVNULL)
        samples = []
        started = time.monotonic()
        while time.monotonic() - started < 21:
            try:
                with urllib.request.urlopen(API + '/state', timeout=1) as response:
                    state = json.load(response)
                samples.append({'elapsed_s': time.monotonic()-started,
                                'counts': state.get('counts'), 'queue': state.get('queue_depth'),
                                'drops': state.get('drop_reasons'), 'actual': state.get('actual_device'),
                                'gpu_verified': state.get('gpu_verified'),
                                'metrics': state.get('metrics'), 'native': state.get('native')})
            except Exception:
                pass
            time.sleep(.25)
        selected = [s for s in samples if 6 <= s['elapsed_s'] <= 18]
        first = selected[0] if selected else samples[0]
        last = selected[-1] if selected else samples[-1]
        dt = max(.001, last['elapsed_s'] - first['elapsed_s'])
        def delta(key):
            return (last['counts'].get(key, 0) - first['counts'].get(key, 0)) / dt
        nf, ni = last['native'], first['native']
        results.append({'device': device, 'target_hz': 5, 'views': 3,
                        'resolution': '1920x1080', 'window_s': dt,
                        'offered_fps': delta('offered'), 'accepted_fps': delta('accepted'),
                        'completed_fps': delta('completed'),
                        'drops': last['drops'], 'queue_depth': last['queue'],
                        'actual_device': last['actual'], 'gpu_verified': last['gpu_verified'],
                        'unity_fps': nf.get('fps'), 'frame_p95_ms': nf.get('frame_p95_ms'),
                        'frame_p99_ms': nf.get('frame_p99_ms'),
                        'e2e_p95_ms': state.get('latency_p95_ms'),
                        'host_cpu_percent': (last['metrics'] or {}).get('host_cpu_percent'),
                        'native_cpu_percent': (last['metrics'] or {}).get('native_cpu_percent'),
                        'service_cpu_percent': (last['metrics'] or {}).get('service_cpu_percent'),
                        'device_gpu_busy_percent': (last['metrics'] or {}).get('gpu_busy_percent'),
                        'samples': samples})
        stop()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'purpose': 'short final-layout regression smoke; not a full confirmation',
                               'results': results}, indent=2, allow_nan=False) + '\n')
finally:
    stop()
    CFG.write_bytes(original)
    env = os.environ.copy()
    env.update(STAGE5_RUN_ID='stage5-review-cpu', STAGE5_LINES='1', STAGE5_VIEWS='1',
               STAGE5_HZ='5', STAGE5_DEVICE='cpu', STAGE5_WIDTH='1600', STAGE5_HEIGHT='900')
    subprocess.run([str(ROOT / 'stage5/start.sh'), '--no-build'], cwd=ROOT,
                   env=env, check=False, timeout=20,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(json.dumps([{k:v for k,v in r.items() if k!='samples'} for r in results], indent=2))
