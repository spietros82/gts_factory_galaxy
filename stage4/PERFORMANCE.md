# Stage 4 measured capacity — ASRock A395

One frozen cycle completed in **30.60 minutes (1,836.006 seconds)**, below the 45-minute wall budget. 32 live factory/render/rate phases and 10 saved-crop replay phases. Zero Qwen requests, no training or old held-out evaluation. Measured implementation: `9ea0b8132c9266778630a93d65a246bd652f3455`. Later closure fixes correct timing units, reserve queued frame IDs, recover after service restart, measure full monitoring cost and abort the entire future cycle on a resource/operator stop. They do not change model weights, scene geometry, rendering settings or acquisition scheduling. These saved measurements apply to the frozen candidate; no second capacity cycle was run for closure fixes.

## What passed

The highest tested count satisfying all frozen presentation criteria was **24**, confirmed twice for full CPU, full GPU and rendering-only. **48** was the first tested failure in each mode, confirmed twice. Counts 25–47 were not tested, so the exact boundary is unknown. The software allocation guard is 48; it is not a performance promise. Default one line/CPU/normal cadence remains safe for demonstration. Twenty-four is close to the allowed frame-time margin, not a conservative industrial recommendation.

Criterion: target 60 FPS; warmed mean ≥57 FPS, frame interval p95 ≤20 ms, p99 ≤33.34 ms; zero explicit native drops/deadline misses, every line serviced and selected device actually executing. Frame interval is not GPU render duration. 24-line CPU confirm1 averaged 57.20 FPS: PASS by the predeclared tolerance, not a sustained 60 FPS claim.

|Workload/device|Lines|Repeat|Mean FPS|Frame p95/p99 ms|Images/s|Capture→result p95 ms|Trigger→result p95 ms|Criteria|
|---|---:|---|---:|---:|---:|---:|---:|---|
|full/cpu|24|confirm1|57.20|19.23/22.04|31.2|20.20|456.8|PASS|
|full/cpu|24|confirm2|58.91|18.94/21.75|31.2|20.20|437.9|PASS|
|full/cpu|48|confirm1|37.63|37.24/40.38|62.4|27.76|1533.3|FAIL|
|full/cpu|48|confirm2|36.89|37.73/41.15|62.4|28.05|1559.2|FAIL|
|full/gpu|24|confirm1|58.89|19.10/21.11|31.2|22.53|440.3|PASS|
|full/gpu|24|confirm2|58.96|18.89/21.08|31.2|22.29|437.1|PASS|
|full/gpu|48|confirm1|37.54|37.36/39.88|62.4|31.77|1538.8|FAIL|
|full/gpu|48|confirm2|37.69|37.07/40.05|62.4|31.34|1536.3|FAIL|
|render/cpu|24|confirm1|60.00|16.67/16.67|0.0|0.00|0.0|PASS|
|render/cpu|24|confirm2|58.46|16.67/16.67|0.0|0.00|0.0|PASS|
|render/cpu|48|confirm1|54.11|22.16/24.06|0.0|0.00|0.0|FAIL|
|render/cpu|48|confirm2|54.37|22.03/24.18|0.0|0.00|0.0|FAIL|

Rendering-only has no active capture/inference; its latency/rate zeros above mean not applicable, not instantaneous processing. Normal full-factory confirmation completed 31.2 images/s at 24 lines (10.4 three-view bottle batches/s), and 62.4 images/s at 48 (20.8 batches/s). Each line completed 78 images per 60-second confirmation; no off-screen starvation. Configured ceiling 0.667 batches/line/s is not the achieved station-trigger arrival rate. Actual captured/accepted/completed rates match within each confirmation window. Full runs at 48 failed the presentation target despite meeting inspection criteria. Full run terminal drops and joined trigger/capture 2-second deadline misses were zero.

## Camera waiting and a preserved timing defect

Frozen candidate wrote seconds into a trace field named `acquisition_wait_ms`. Original records and `summary.json` remain unchanged. `correct_saved_timings.py` joins actual batch IDs, explicitly multiplies that field by 1000, and saves `corrected-summary.json` and per-phase joined timing records. Capture→result was already correct milliseconds. Final runtime fixes the writer; this is a reporting correction, not new inference or favourable retesting.

Trigger→result includes the pre-capture scheduling wait; capture→result alone does not. CPU 24 confirmation p95 trigger latency 437.9–456.8 ms, CPU 48 1,533.3–1,559.2 ms; GPU 24 437.1–440.3 ms, GPU 48 1,536.3–1,538.8 ms. Maximum joined trigger interval across the 48 confirmation windows remained below 1.69 s. Joined results do not assign an invented completion to dropped/expired requests; those have explicit drop counters.

## Acquisition-rate sweep: retained failure

At three lines, configured benchmark demand 1 batch/line/s (9 images/s aggregate) was the **first tested rate**. CPU offered/accepted/completed 8.8 images/s; GPU 8.6 images/s in the 15-second measurement window. Whole-phase native drops: CPU 3 images/one bottle batch; GPU 6 images/two batches. Backend accepted all actually submitted images. Inspection/rendering latencies remained short, but the predeclared zero-drop requirement failed. The sweep stopped; 2/4/8 rates were not run.

Native code drops associations if the selected simulated bottle disappears before camera service. The posed-target benchmark picked an exiting target; this is consistent with the observed missing-target drops, rather than inference saturation. Raw counters and failure retained; not tuned and rerun. Presenter benchmark cadence is experimental and not recommended as the normal demonstration mode. Increasing simulation speed is not an acquisition-rate benchmark.

## Vision-only replay ceiling, not camera capacity

Nine newly authored healthy crops (three products × three stations); images already in memory; same weights, RGB preprocessing, thresholds and policy. Excludes Unity, live camera render/readback, PNG/HTTP and persistent evidence. 2-second warm-up plus 8-second measurement at 10, 50, 100, 200 and 400 offered batches/s on each device; all passed with zero drops/deadlines. **At least the tested ceiling of 400 batches/s / 1,200 images/s** was achieved; no maximum established.

|Device|Offered/accepted/completed batches/s|Images/s|Replay batch latency mean/p95/p99 ms|Max queue|
|---|---:|---:|---:|---:|
|cpu|400 / 400 / 400|1200|1.200/1.649/1.997|5|
|gpu|400 / 400 / 400|1200|1.814/2.568/4.872|5|

These tiny MLPs do not demonstrate GPU advantage: CPU capture→result was about 20 ms versus GPU 22–23 ms at 24-line normal cadence, and CPU replay p95 was lower at the tested ceiling. GPU dense layers actually execute on Radeon OpenGL compute (verified renderer and shader queries); preprocessing/softmax/policy remain CPU. Model residency/availability alone is not inference execution.

## Bottleneck interpretation and resource use

24-line confirmation host CPU means 12.35–12.74% across all 32 logical processors; native process 367.9–376.7% with one core=100%; device-wide GPU 12.74–15.34%; native RSS 446–459 MB. 48 full-factory host CPU 15.85–16.09%, native 466–474%, device-wide GPU 14.74–20.89%, native RSS 568–583 MB. Rendering-only at 48 averaged about 54 FPS and higher native CPU (645–649%); frame limiting and camera/readback pacing alter the workload, so separate-run subtraction cannot allocate exact task cost.

Exploratory CPU 24→48: visual update mean 3.60→8.17 ms/frame, active three-view ReadPixels+Apply mean 5.89→11.69 ms/batch; inference classifier mean approximately 0.425 ms/image, backend queue p95 approximately 4.2–4.4 ms. Low host CPU and GPU percentages do not exclude a constrained main/render submission thread or readback synchronization. Evidence points to a **mixed native scene/submission and synchronous camera-acquisition bottleneck**, not neural inference saturation. Exact thread/GPU attribution remains unavailable; detailed profiling was outside this milestone.

All factory/rate phase sampled available RAM averages ≥116.63 GiB, max CPU Tctl79°C, GPU temp1 50°C; no resource guard fired. Sampling 1 Hz; brief unsampled excursions are unproven. Device-wide GPU includes desktop/background workloads, never vision-only. Native/backend RSS overlap with shared memory; do not add them as a physical total. Base monitoring averages 7.39–9.51 ms/sample, maximum18.16 ms; original extra Stage4 PID/Tctl overhead was not in that field. Closure adds full monitor timing. No monitoring-off comparison was run, so sampling cost does not prove zero impact.

## Complete configuration and measurement boundaries

ASRock AI BOX-A395/IMB-A395, Ryzen AI Max+395 16-core/32-thread, Radeon8060S, approximately124.94GiB usable shared RAM; Ubuntu24.04.5/kernel7.0.0-38, amdgpu/Mesa25.2.8. Unity6000.6.5f1 LinuxStandalone release/Mono/Built-in/OpenGLCore,1920×1080 fullscreen window,4MSAA,VSync0,target60. Static fitted overview camera; independent grid instances seeded42+index, Lager/IPA/Stout cyclic, speed1/shared0.05s scheduler. Three disabled-between-capture orthographic cameras/line,256×256 rendered frame and160×160 ROI; same frozen Stage3 weights. Python3.12.3/NumPy2.3.5/ModernGL5.12/glcontext3/Pillow11.3,BLAS/OMP2threads.

10-second warmup and20-second exploratory windows;10+60seconds ×two boundary confirmations;5+15seconds rate phases. Cold model creation and time to first native heartbeat separately saved; GPU initialized in every service but only selected backend executes inference. No Qwen/Gemma requests and Ollama `/api/ps` showed no resident models before the cycle. GNOME/UnityHub/Firefox/Fleet/old focused inspector/WebUI/system services left running; old inspector idle158/158. Background process names and unit snapshot retained. No artificial utilisation loads, CPU-mode LLM benchmark or physical hardware comparison.

Frame interval uses Unity unscaled time. Capture interval starts UTC before camera rendering and ends after per-image crop/inference/policy/image writes (audit append follows); trigger interval adds directly measured station-acquisition wait. Transport, queue, preprocessing, transfer, dense inference and shader query intervals separately retained. Shared-host UTC and stopwatch anchoring have clock uncertainty. Replay timing is offered enqueue→completed three-image batch. Rates use completed timestamps within the declared steady window; lifetime UI rates are distinct. Raw p50/p95/p99/sample counts in local phase summaries.

## Evidence and charts

Local immutable evidence: `reports/stage4/capacity/` contains freeze, background snapshot, per-phase commands/configuration/frameCSV/capture traces/requests/results/resources/cold-start/logs, raw summary, explicit corrected summary, replay, boundaries and duration. `RESULTS.csv` is a public source-safe summary without host paths, payloads or weights.

- [Frame time](charts/frame-time.svg)
- [Capture latency](charts/latency.svg) and [trigger latency](charts/trigger-latency.svg)
- [Completed images](charts/throughput.svg)
- [Host CPU](charts/host-cpu.svg), [whole-device GPU](charts/gpu.svg), [native RSS](charts/memory.svg)

Runs are bounded synthetic demonstrations, not industrial capacity, real-camera accuracy, continuous production reliability or evidence that an A395 is required instead of a cheaper machine. Untested counts, real optics/lighting/triggers/speeds, production data transport/storage and sustained runs remain unproven.
