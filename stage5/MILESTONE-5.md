# Stage 5 milestone summary

**Status: partial demonstration delivered; full-frame detector quality gate failed.**

Unity now submits full 640×640 inspection-camera frames through four-slot asynchronous readback with frame identity/timestamps to a bounded loopback service. A pretrained YOLO11n/ncnn detector runs on CPU or verified Radeon8060S Vulkan; CPU and GPU output is numerically aligned for the evaluated boxes. The live panel shows detections and image tracks, and does not treat detector-derived candidate regions as cap/fill/label findings. Stage4 remains the stable previous demonstration.

The sole corrected locked test detected66 of184 visible synthetic bottle instances (precision92.96%, recall35.87%), with118 misses and zero detections among95 partial-occlusion objects. It fails the pre-set 90% precision/recall targets. No held-out tuning/retest was done. The detector is not safe for product acceptance; the UI labels downstream findings uncertain.

At the combined workload boundary, one line/three views at5Hz per view completed about14.3 images/s and kept Unity near60FPS on CPU and GPU. The first tested nine-view/45Hz demand hit the bounded queue and responsiveness guard; Unity fell to about7.3FPS. Saved-frame replay showed 84.2 GPU vs43.5 CPU images/s, but this is not a live camera capacity claim or a requirement for this hardware. The bottleneck is mixed/unknown. No training, Qwen, driver/system change, physical camera or PLC was involved.

Source implementation, runtime instructions, tests, result summaries, screenshots, capacity graph and this handover are reviewable. The Stage5 public PR is source-only and explicitly states the quality failure. Stop at Stage5 pending Pietro's review; do not begin model tuning on the spent v1.2 test.
