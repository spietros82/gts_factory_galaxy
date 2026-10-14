# Stage 5 verification record

## Frozen build and environment

- Branch started from accepted Stage4 tag `stage4-accepted-before-stage5-20261014` at `585e7b6`.
- Unity `6000.6.5f1`, standalone Linux player, Ubuntu24.04.5, kernel7.0.0-38, AMD Ryzen AI Max+395/Radeon8060S, Mesa RADV. Matched capacity runs were fixed 1920×1080, VSync0, 4×MSAA, 60Hz target.
- CPU and GPU used the same YOLO11n ncnn parameter/weights, FP32, 640×640 RGB/255, confidence/NMS and tracking thresholds. No fine-tuning and no Qwen calls.
- Stage5 built successfully. `git restore -- UnityProject/Assets/Scenes/Factory.unity` removed Unity's build-time scene reserialization only; no other user files were touched.

## Checks

| Check | Result | Evidence |
|---|---|---|
| Eight isolated service-contract tests using fake adapter | PASS | `stage5/.venv/bin/python -m unittest discover -s stage5/tests -v` |
| Existing Stage3/4 Python suite | PASS,18/18 | `python3 -m unittest discover -s tests -v` |
| Unity standalone compile | PASS | `reports/stage5/build.log`, `FACTORY_BUILD Succeeded bytes 93557632` (latest build size differs only by screenshot-on-detection test hook) |
| Async GPU readback support in player | PASS | `SystemInfo.supportsAsyncGPUReadback` true in native capture reports; ring has4 owned slots |
| One-shot v1.2 locked detector evaluation | FAIL quality target | `reports/stage5/evaluator/locked-results-v1.2.json` and `locked-raw-v1.2-{cpu,gpu}.jsonl` |
| GPU actual execution | PASS | 108/108 locked calls had positive process-scoped AMD DRM compute counter delta; ncnn reported Radeon8060S Vulkan and CPU MatMul partitions |
| CPU/GPU same-image detection agreement | PASS for agreement only | Saved raw frames agree for71/71 CPU predictions at IoU≥.99; this does not imply correctness |
| Final post-layer-isolation three-view short smoke | PASS, sanity only | `reports/stage5/benchmark/final-layout-sanity.json`; 11.8s/device |
| 9-view overload and recovery guard | PASS safety behavior; workload fails | CPU/GPU queue reached12 and Unity fell below10FPS; harness stopped phase and restored one-line CPU profile |
| Actual native screenshot with detection overlay | PASS | `stage5/screenshots/full-frame-detection-overlay.png` |
| Actual native screenshot with no detector output | PASS | `stage5/screenshots/full-frame-no-detections.png` |

The v1.0 projection labels are archived with their invalid0TP/431FP/FN detector result and are explicitly retired. v1.1 captured but was not evaluated because its geometry labels included fully occluded simulator objects. The corrected v1.2 labels are derived from same-state pixel segmentation and were visually inspected before inference. v1.2 is the sole Stage5 quality result; no model/settings selection used its test outputs.

## Known defects and limitations

- Recall is35.9%, and all95 visible targets in the partial-occlusion subset were missed. The quality target is not met. The detector cannot safely support accept/reject.
- Track identity is image-space only and has41 track switch/fragment proxies; it does not establish a bottle's real physical identity.
- Detection regions are geometric proposals only. The Stage4 classifiers are not run on these changed crops; all downstream cap/fill/label status is uncertain.
- The 9-view failure is a mixed bottleneck; exact attribution among Unity submission/render work, asynchronous readback, transport, Python scheduling and image I/O is unresolved.
- No real camera/optics/lighting/line speed, PLC, production variability, fail-safe reject, other machine, concurrent Qwen, real-time operating constraints or industrial acceptance was tested.

The only follow-up test after the locked pass was the bounded live-layout smoke; it used the same public synthetic scene, not the held-out evaluator frames, and did not change detector/model thresholds.
