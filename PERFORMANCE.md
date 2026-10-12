# Stage 1 rendering comparison

Measured native source18d1692, Unity6000.6.5f1 Linux Mono release, Built-in / Standard / OpenGLCore. A395 Ryzen AI Max+395, Radeon8060S, Ubuntu24.04.5.1600×900,4MSAA,VSync0,target60. Healthy seed42/1×/PLC profile; same original overview transform and full viewport held by --comparison-camera. The customer default view now reserves room for the HUD and uses a separate presentation composition; this table is the controlled common view, not a benchmark of every close-up.

Two35-second runs per version, excluding first5seconds of frame intervals. Early after runs are retained as checkpoints, not added to the final sample. Frames use Unity unscaled wall intervals from Awake; resource samples use monotonic process-launch time with first5seconds excluded. Simulated timestamps are distinct.

| Metric | Before | Stage 1 |
|---|---:|---:|
| Mean FPS | 59.994 | 59.987 |
| Mean frame | 16.668 ms | 16.670 ms |
| Frame p95 | 16.668 ms | 16.669 ms |
| Frame p99 | 16.690 ms | 16.823 ms |
| Worst frame | 17.215 ms | 17.373 ms |
| Native CPU (one core =100%) | 37.313% | 52.639% |
| Host CPU (32 logical CPU capacity) | 2.743% | 2.812% |
| Native sampled peak RSS | 315.310 MB | 333.316 MB |
| Device-wide GPU busy | 8.484% | 7.711% |

Both versions packed44 bottles at simulated74.75s in each run, with zero rejects. No material60FPS regression observed in this short test. CPU and resident memory increased due to the extra presentation geometry/materials. This is not a measured inference workload benchmark.

GPU busy is directly measured sysfs device occupancy including desktop/background work; no per-process percentage attribution or claimed GPU optimisation. Host memory, DRM accounting and process RSS overlap and are never added. Background service states were held: original inspection service active throughout; prior/native/streaming units inactive as found. Read-only Ollama residency polling is not inference. No Qwen/Gemma call, model reload, driver/backend change or budget reset.

Raw frame CSVs, resource samples, run configuration and logs: reports/stage1/raw/{before-1,before-2,after-final-1,after-final-2}; summaries: reports/stage1/performance-summary.json and corresponding JSON/PNG files. Raw data remains local, excluded from public source delivery. No hardware necessity/superiority or broader workload claim.
