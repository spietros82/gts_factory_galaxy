# Stage 2 rendering comparison

Accepted Stage1 binary versus Stage2 sourced516dd3. Unity6000.6.5f1 Linux Mono release, Built-in / Standard / OpenGLCore, A395 Ryzen AI Max+395 / Radeon8060S, Ubuntu24.04.5.1600×900, target60FPS,VSync0,4MSAA. Same seed42/healthy/1×/PLC, original overview transform and full77% viewport held by --comparison-camera. The default customer viewport/layout differs; this is a common-view controlled comparison, not a benchmark of every view.

Two35s runs per version, first5s frame intervals excluded; raw Unity unscaled wall intervals and separate simulated timestamps. Resource warm-up uses5s from process launch, not the Unity Awake clock. Initial Stage2 measurements89cce14/fbe388a are retained checkpoints, excluded after the Data-view-only camera fix. Background inspection service PID41095 remains active; other demos/services unchanged. No inference.

| Metric | Stage1 | Stage2 |
|---|---:|---:|
| Mean FPS | 59.968 | 59.991 |
| Mean frame | 16.676 ms | 16.669 ms |
| Frame p95 | 16.675 ms | 16.668 ms |
| Frame p99 | 16.954 ms | 16.695 ms |
| Worst frame | 17.394 ms | 17.429 ms |
| Native CPU (one core=100%) | 55.396% | 65.697% |
| Host CPU (32logical CPU capacity) | 2.618% | 2.916% |
| Native sampled peak RSS | 330.420 MB | 347.632 MB |
| Device-wide GPU busy | 7.375% | 9.046% |

Packed counts per run: Stage1 [44, 44]; Stage2 [44, 44]. Simulation endpoint seconds: [74.7, 74.75] versus [74.75, 74.75]; wall-clock stopping can differ by a process tick. No invented exact timing match.

Near60FPS retained in this short comparison. Resource use is reported without claiming a performance benefit or causal GPU allocation. GPU busy is a device-wide sysfs sample including desktop/background work; no process GPU percentages. Native RSS and shared GPU/host memory domains overlap and are not added. No CPU/GPU inference benchmark, comparative appliance result or production-sizing proof.

Exact commands, config, frames, resource samples and player logs: reports/stage2/raw/{before-stage1-1,before-stage1-2,after-stage2-freeze-1,after-stage2-freeze-2}; JSON summary reports/stage2/performance-summary.json. The final native Data-view screenshots show16.7ms recent frame averages after the camera fix; that display is not a separate percentile benchmark.
