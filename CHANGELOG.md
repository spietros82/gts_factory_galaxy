# Stage 5 — experimental full-frame vision

Added Unity async-readback full-frame capture, bounded local detector service, YOLO11n/ncnn CPU and RADV Vulkan paths, image-space tracking, corrected evaluator masks, tests and performance reporting. One locked evaluation per device failed:66/184 targets found and0/95 partial-occlusion targets. Saved-frame GPU replay was faster, but three-view live capacity was similar on CPU/GPU. Nine-view workload hit safe guards. No held-out tuning/retest, Qwen, training or system/driver changes. See [Stage5 results](stage5/RESULTS.md) and [handover](stage5/HANDOVER.md).

---

## Preserved Stage 4 changelog

Read [the Stage 4 document](stage4/CHANGELOG.md) and [delivery](stage4/DELIVERY.md). Older stage material remains in its source branches/folders and history.
