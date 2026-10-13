# Stage 5 results — 14 October 2026

## Result and decision

The full-frame path runs end-to-end and uses verified AMD Radeon Vulkan execution. The selected pretrained bottle detector **fails the frozen synthetic localization target**. At IoU ≥ 0.50 it found 66/184 visible bottle instances: precision 66/71 = 92.96%, recall 66/184 = 35.87%, with 5 false detections and 118 missed visible bottles. Wilson 95% intervals are approximately 84.6–97.0% for precision and 29.3–43.0% for recall. This does not meet the predeclared 90% precision/recall target. Do not use the detector to accept or reject products.

By held-out appearance group, normal scenes had 66 TP, 5 FP and 23 FN over 89 visible targets (recall 74.2%); partial-occlusion scenes had 0/95 targets detected; 36 empty-field frames had 0 detections. A zero count on 36 empty frames does not establish zero false-positive risk (rule-of-three upper bound is about 8%). Across products: Lager 24/60 TP, 2 FP, 36 FN (P 92.3%, R 40.0%); IPA 23/62 TP, 3 FP, 39 FN (P 88.5%, R 37.1%); Stout 19/62 TP, 0 FP, 43 FN (P 100%, R 30.6%). Product counts include normal, partial-occlusion and empty sequences.

Temporal association is also weak: the recorded evaluator proxy found 41 track-ID changes and 41 fragments among matched observations. It is not validated physical tracking. CPU and GPU prediction sets agreed at IoU ≥0.99 for all 71 CPU predictions in the same frames. Identical predictions do not correct the missed-bottle problem.

## Frozen quality protocol and evidence

One candidate only: pretrained YOLO11n COCO bottle class, ncnn 1.0.20260526, RGB/255 FP32, 640×640, confidence 0.25, NMS IoU 0.45, image tracker IoU 0.20. No fine-tuning. Development and test used separate complete synthetic capture sequences/seeds; the 108 locked test images were scored once on CPU and once on Vulkan GPU after development-only warm-up. Labels are evaluator-only visible-pixel masks from the same-state segmentation render. The rendered contact sheet was manually inspected before inference. The runtime API does not accept evaluator labels or simulator truth. The corrected label process and retired attempts are detailed in [evaluation erratum v1.2](EVALUATION-ERRATUM-1.2.md).

The final manifest covers 216 PNG frames, 216 per-frame label sidecars and two capture metadata records (435 files, 17,165,659 bytes); SHA-256 `34336bb18f3a203bb7c7e32dc8ff4d54463d6ba6c1e2170aa554bfd90170bf74`. Capture plan SHA-256 `c2eb4e7c45a8cc655f06cfcbbd70721604cc1e736301ca58472bdfbb1e97de31`. Locked CPU/GPU raw JSONL contains 108 per-image records per device in the local ignored `reports/stage5/evaluator/`. Earlier v1.0 invalid results and v1.1 retired data remain preserved and are not used here.

The held-out frames are synthetic Unity renders, not representative production camera data. The poor partial-occlusion result means the model does not meet its demo target even on these controlled pixels. No tuning or retest on the held-out set was performed. A future candidate needs new development data and a genuinely new locked set; the v1.2 test is spent.

## Vision-only saved-frame performance

108 identical 640×640 test frames per device. Wall throughput includes image decode, preprocessing, completed inference and postprocessing, but excludes Unity rendering/readback, HTTP transport, tracking overhead and concurrent presentation.

| Device | Verified execution | Cold model load | Dev warm-up | p50 frame time | p95 | p99 | Wall throughput | Quality |
|---|---|---:|---:|---:|---:|---:|---:|---|
| CPU | ncnn CPU | 26.4 ms | 33.3 ms | 22.79 ms | 28.91 ms | 32.36 ms | 43.49 images/s | P 92.96%, R 35.87% |
| GPU | Radeon 8060S Vulkan + 2 CPU MatMul partitions; positive process-scoped DRM compute delta on 108/108 calls | 157.2 ms | 15.2 ms | 11.74 ms | 14.36 ms | 15.82 ms | 84.19 images/s | P 92.96%, R 35.87% |

The replay throughput is about 1.94× higher on this saved-frame workload. This is a measured difference for this ncnn graph on this host, not a production-camera capacity or a claim that the machine needs a GPU. GPU compute-counter delta median was 4.08 ms; it is not a kernel-only time. The exported graph runs two `MatMul` partitions on CPU. Process CPU/RSS sampled after sequential device runs are cumulative and are not reported as per-device values.

## Complete live pipeline and combined rendering

Main matched cycle settings: Unity 1920×1080, 60 FPS target, VSync off, 4× MSAA, same synthetic line seed/product mix, full camera readback/PNG transport, analysis at 5 frames/s per view; queue cap 12 and explicit safe-stop guards. Stage 4 acceptance targets: mean FPS ≥57, frame p95 ≤20 ms, p99 ≤33.34 ms; ≥95% configured rate; explicit drops ≤1%; E2E p95 ≤500 ms. Camera views are meaningful inspection renders; simulation speed is independent from acquisition cadence.

| Condition | Offered / accepted / completed | Unity FPS; frame p95/p99 | Capture-to-result p95 | Queue / outcome |
|---|---:|---:|---:|---|
| Rendering only, 3 lines | 0 / 0 / 0 images/s | 59.99; 16.67 / 16.67 ms | N/A | Stable baseline |
| 1 view × 5 Hz, CPU | 4.78 / 4.78 / 4.86 images/s | 59.97; 16.67 / 16.90 ms | 119.7 ms | Pass |
| 3 views × 5 Hz, CPU, 58.7 s confirmation | 14.32 / 14.32 / 14.34 of 15 images/s | 59.96; 16.67 / 17.01 ms | 136.8 ms | Pass, no queue growth |
| 3 views × 5 Hz, GPU, two 58.8 s confirmations | 14.30–14.31 / same / 14.33–14.34 of 15 images/s | 59.99–60.00; 16.67 / 16.67 ms | 111.5–135.5 ms | Pass, GPU verified |
| 9 views × 5 Hz, CPU (3 lines) | 8.0–8.2 offered; 6.4–6.5 accepted; 3.23 completed of 45 images/s | 7.34–7.43; frame p95 ~2.70–2.74 s | 474–481 ms | Queue reached 12; guarded failure |
| 9 views × 5 Hz, GPU (3 lines) | ~8.2 offered; 7.4 accepted; 4.22 completed of 45 images/s | 7.33–7.38; frame p95 ~2.72–2.74 s | 407–418 ms | Queue reached 12; guarded failure |

After the final camera-layer isolation change, one additional short (11.8 s/device) 3-view check passed on both devices: CPU 14.34 offered / 14.34 accepted / 14.42 completed images/s, 59.98 FPS, frame p95 16.67 ms and E2E p95 152.2 ms; GPU 14.24 / 14.24 / 14.24 images/s, 59.46 FPS, frame p95 16.67 ms and E2E p95 134.7 ms, GPU counter verified. This short smoke is not a replacement for the longer matched confirmations. It shows similar combined throughput and no meaningful GPU advantage in this workload.

The 9-view test hit both the backend queue cap and a severe Unity responsiveness collapse. A mixed acquisition/main-thread/readback/scheduling/service bottleneck is most plausible; exact attribution is unknown. Device-wide GPU readings were about 22–26% in failing samples and include all host workloads, so this was not evidence of saturated GPU compute. No exact per-process GPU share is available. At the tested 3-view/5 Hz setting, this single-line full-frame camera pipeline is the highest confirmed passing demand. Nine views at 5 Hz is the first tested failing workload; higher rate/size/batch demands were not tested because the compact candidate and live pipeline already failed quality/capacity conditions. This is not a physical-camera capacity rating.

The short post-change CPU/GPU check and actual overlay screenshot are `reports/stage5/benchmark/final-layout-sanity.json` and `reports/stage5/screenshots/full-frame-detection-overlay.png` locally. Curated screenshot copies are in `stage5/screenshots/`. Detailed sweep raw records remain local in `reports/stage5/benchmark/`; raw image-level evaluation and evaluator sidecars are not published.

## Acquisition and limits

The previous synchronous capture path's missing-target/drop behavior remains in Stage 4 raw evidence. Stage 5 uses Unity 6000.6 `AsyncGPUReadback`, runtime support check, four request-owned RenderTexture slots, preserved frame/session/camera/capture timestamp, bounded backend queue and explicit drop/stale/retired/invalid reasons. In the final image path, the Stage 5 camera submits around 0.2–0.45 ms, readback is typically about 38–50 ms and compressed PNG transport roughly 3–8 ms in the earlier measured build. The failure is not hidden by retargeting frames to another bottle.

No camera image/model result establishes cap presence/placement, fill range, label quality, seal/torque, safety, cause or remaining life. All derived regions stay uncertain. No physical camera, lens, lighting, trigger, line-speed, actual package diversity, PLC, fail-safe reject or operator study was evaluated. No Qwen calls were made. No hardware comparison against a cheaper CPU system was performed.
