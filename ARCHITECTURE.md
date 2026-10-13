# Current architecture: Stage 5 experimental full-frame path

See [Stage5 architecture](stage5/ARCHITECTURE.md). Unity performs request-owned async full-frame capture; a bounded loopback service runs the same YOLO11n ncnn model on CPU or verified Radeon Vulkan (two CPU MatMul graph partitions). Runtime inputs contain neutral frame/session/camera identity and pixels, not simulator/evaluator truth. Detector-derived regions remain uncertain; locked recall was35.9%. Stage4 is preserved.

---

## Preserved Stage 4 architecture

Read [the Stage 4 document](stage4/ARCHITECTURE.md) and [delivery](stage4/DELIVERY.md). Older stage material remains in its source branches/folders and history.
