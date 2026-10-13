Layout revision note: the UI revision in UI-REVISION.md was verified natively without another benchmark cycle. The exact measurements below remain from source1f4e52e and its original viewport. CPU meets the tested small-model three-view acquisition workload; this is not full-video or CPU-Qwen capacity evidence.

# Final Stage3 measured performance

Final implementation1f4e52e, native release Unity6000.6.5f1/Built-in/OpenGLCore/Mono; AI BOX-A395, RyzenAI Max+395/Radeon8060S, Ubuntu24.04.5/Mesa25.2.8. Same1920×1080,60FPS target,VSync0,4MSAA,one line/overview/seed42/process1×; Lager/IPA/Stout20s wall schedule,3controlled views/shared bottle trigger≤every1.5s.

Each condition repeated twice:10s warm-up followed by60s measured frame interval. Same weights/preprocessing/thresholds/cadence in CPU/GPU conditions. Disabled captures0; backends may be loaded but idle. Final runs all have qwen3:8b resident after three earlier manual requests, no active Qwen request during benchmark. Residency is not inference. Other services remained unchanged; process names recorded.

|Condition/run|FPS|Frame p50/p95/p99 ms|Capture→result mean/p95/p99 ms|Completed inspections/60s|
|---|---:|---|---|---:|
|disabled/1|59.950|16.667/16.698/16.991|N/A|0|
|disabled/2|59.941|16.667/16.796/17.046|N/A|0|
|cpu/1|59.937|16.667/16.878/17.025|13.987/18.263/19.065|78|
|cpu/2|59.935|16.667/16.879/17.036|13.571/17.002/17.703|78|
|gpu/1|59.917|16.667/16.935/17.123|16.493/21.294/22.942|78|
|gpu/2|59.936|16.667/16.858/17.068|16.546/21.409/22.835|78|

Zero drops/stale/missed2s deadlines in all final runs; GPU actual records/GL hardware timer verify execution. Each enabled run90total including warm-up,78steady,1.3individual inspections/s (~0.433bottle batches/s). Actual bottle-trigger/cadence availability controls the rate, not camera refresh. CPU meets this load. GPU complete path slower: no GPU advantage or industrial throughput claim. Small frame differences/host variation do not establish a significant performance benefit.

|Condition/run|Host CPU %|Native CPU %|Backend CPU %|Native RSS MB|Backend RSS MB|Device-wide GPU %|GPU sensor °C|Available RAM GiB|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|disabled/1|2.80|60.04|1.25|328.65|122.93|6.09|32.33|111.02|
|disabled/2|2.86|61.55|1.23|325.46|122.79|6.20|32.49|111.01|
|cpu/1|2.90|62.92|2.01|335.96|124.38|6.20|32.49|111.02|
|cpu/2|2.92|63.89|2.02|336.77|124.78|6.29|32.59|111.02|
|gpu/1|2.92|64.19|2.08|337.89|126.48|6.19|32.75|110.99|
|gpu/2|2.95|64.04|2.10|335.91|126.09|6.22|32.86|110.97|

Host100%=all32logical processors; process100%=one logical core. GPUcounterwhole-device, includes desktop/Unity/vision/background; no per-process shares. RSSCPUresidentmemory and MemAvailable overlap other memory accounting; not summed. Resources sampled1Hz, means over launch-clock steady samples; slightly different origin from Unity frame clock. METRICS.md defines timing boundaries.

|Run|Preprocess mean ms|Transfer/readback mean ms|Arithmetic/submission mean ms|GPU shader mean ms|Queue mean ms|
|---|---:|---:|---:|---:|---:|
|cpu/1|0.139|0.000|0.034|0.000|2.498|
|cpu/2|0.137|0.000|0.033|0.000|2.413|
|gpu/1|0.142|1.146|0.030|0.919|3.803|
|gpu/2|0.140|1.140|0.032|0.918|3.882|

Cold backend construction CPU6.450–8.067ms, GPU40.908–44.212ms, separate from process/native startup and steady inference. GPU transfer/readback includes synchronous completion wait and overlaps shader elapsed, so do not add them. CPU inference is arithmetic, GPU inference_ms CPU submission time, gpu_shader_ms actual hardware region elapsed.

Combined measured performance wall budget: initial442.580s + final476.806s + replay/monitoring100.672s = **1020.058s (17.00minutes)**, below20min. Initial runs preserved, final recheck required by retention/display fixes; no training/locked-test/Qwen reruns. Saved replay below uses validation images, not locked test; reaches bounded100batches/s without establishing saturation.

Raw final reports/stage3/performance-final/, initial reports/stage3/performance/, complete configs/commands/frameCSV/resources/queues/results/coldstartup/backgroundnames retained. Earlier and final checkpoints differ in host residency/background state and code; do not subtract their GPU percentages to attribute workloads. Only final six runs form the final matched comparison.

---

## Preserved initial checkpoint and replay

# Stage 3 performance

Measured native/service source c328b17; final UI historical-label/highlight/offline-state changes afterward do not change model, preprocessing, thresholds, camera dimensions/positions, capture cadence or work schedule. Final button contrast/wrapping fixes are also display-only. Their display is checked natively; these measured results are not a new performance run of that final wording. Native release Unity6000.6.5f1/Mono/Built-in/OpenGLCore; A395/RyzenAI Max+395/Radeon8060S; Ubuntu24.04.5/Mesa25.2.8.1920×1080,60FPS target,VSync0,4MSAA,original overview camera,seed42/1×,same20s Lager/IPA/Stout wall schedule,3controlled station cameras,one shared batch≤every1.5s. Rendering and process clocks distinct.

Two70s runs per condition;10s warm-up excluded,60s frame interval. Inspection completions matched same UTC window10–70s from Unity startup. First shader/model startup saved separately. Model weights/policy/preprocessing identical CPU/GPU, no random forest comparison. No Qwen calls during these runs. Existing inspector/Fleet/desktop/WebUI/Ollama preserved; names recorded in raw process list. Monitoring1Hz identical all conditions. Sysfs GPUbusy is whole-device, not task shares. METRICS.md defines every time/resource denominator.

| Condition | Run | FPS | Frame p99 ms | Capture→result mean/p95 ms | Completed inspections/60s |
|---|---:|---:|---:|---:|---:|
| Disabled |1|59.991|16.695|N/A|0|
| Disabled |2|59.988|16.845|N/A|0|
| CPU |1|59.994|16.692|13.991 /18.119|78|
| CPU |2|59.991|16.681|13.739 /17.667|78|
| GPU |1|59.993|16.689|15.981 /20.647|78|
| GPU |2|59.986|16.871|15.851 /20.456|78|

All inspection-enabled runs90total results including warm-up,78steady,1.3completed inspections/s. Actual trigger/line/capture cadence controls throughput; refresh is not counted as inspection. Zero queue-overflow drops/stale/missed2s deadlines. CPU is sufficient at this workload; GPU end-to-end is slightly slower, so no GPU advantage claimed. Separate GPU shader timings show actual dispatch, not CPU fallback. Small rendering differences are not a demonstrated gain/regression. Replay/resource/cold/monitoring tables are added from saved summaries after the fixed sweep.

Raw reports/stage3/performance/{disabled,cpu,gpu}-{1,2}/ contain commands, frame CSV, resources, startup, results and summaries. All failed/development records retained elsewhere; no performance reruns hidden. Total measured performance budget includes six runs plus fixed replay/overhead comparisons,≤20minutes. No physical-camera, multi-line, other-hardware, industrial throughput or sizing guarantee.

## Resource and component timings
Host CPU normalised over32logical processors; service/native100%means one logical core. RSS is CPU process resident memory, not dedicated GPU memory. GPUbusydevicewide, amdgpu temperature sensor; no per-process shares. Values below are means over saved steady resource samples; sampling launch-clock origin slightly differs from Unity-clock frame window.
|Condition/run|Host CPU %|Native CPU %|Service CPU %|Native RSS MB|Service RSS MB|GPU busy %|GPU sensor °C|Available RAM GiB|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|disabled/1|2.72|59.07|1.18|326.60|121.68|6.77|32.48|118.15|
|disabled/2|2.63|58.18|1.18|323.13|122.83|6.97|32.88|118.19|
|cpu/1|2.55|54.86|2.04|336.08|125.31|7.41|32.79|118.15|
|cpu/2|2.68|56.94|2.00|337.04|124.27|7.32|32.97|118.16|
|gpu/1|2.70|56.96|2.03|336.25|125.74|7.51|32.90|118.16|
|gpu/2|2.60|57.13|2.04|335.31|127.37|6.83|32.98|118.16|

|Run|Preprocess mean ms|Transfer/readback mean ms|CPU arithmetic/submission mean ms|GPU shader mean ms|Queue mean ms|
|---|---:|---:|---:|---:|---:|
|cpu/1|0.148|0.000|0.037|0.000|2.568|
|cpu/2|0.144|0.000|0.034|0.000|2.450|
|gpu/1|0.139|1.090|0.029|0.865|3.648|
|gpu/2|0.142|1.120|0.028|0.896|3.751|

GPU transfer/readback waits for completion and overlaps GPU shader time: do not add those metrics. Inference_ms on GPU is dispatch submission CPU time; shader query is hardware elapsed. Model/context cold-start records retained in each service/cold-start.jsonl; cold creation is not steady inference.

## Saved-crop replay sweep
Replay uses saved validation crops, same weights/policy, one worker and two queued batches,10s each rate/device. Includes neither rendering, camera readback, HTTP nor disk writes. It measures batch completion latency, not the native capture-to-result metric.

|Device|Requested batches/s|Completed inspections/s|Batch latency p95 ms|Dropped batches|Missed2s deadlines|
|---|---:|---:|---:|---:|---:|
|cpu|2|6.00|2.209|0|0|
|cpu|10|29.99|2.012|0|0|
|cpu|50|148.78|1.895|0|0|
|cpu|100|297.29|1.834|0|0|
|gpu|2|6.00|7.555|0|0|
|gpu|10|29.98|6.560|0|0|
|gpu|50|148.73|5.538|0|0|
|gpu|100|297.22|3.980|0|0|

No tested rate exceeded queue/deadline limits;100batches/s was the bounded ceiling, so saturation remains unknown. CPU50batches/s mean latency without/with1Hz monitoring: 1.4579/1.4825ms. Single paired sample, no claim of zero overhead. Host monitor sampling wall cost recorded separately. Total all native/replay/overhead runs543.252s, within20minutes.

Cold backend creation over six starts: CPU5.099–7.311ms; GPU40.605–43.889ms. Includes local model load/context/shader preparation in backend construction, excludes Python process startup/native launch. No model loading included in steady tables.

Simulation starts with800pre-fill ticks (40simulated seconds) before measured wall-clock launch;1× thereafter. These process timestamps are not processing latency. Final resource/throughput intervals remain wall clock.
