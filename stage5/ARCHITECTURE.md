# Stage 5 architecture — experimental full-frame path

```text
Unity shared process clock + synthetic line state
  ├─ Stage 4: station-triggered simulator-assisted crops (preserved)
  └─ Stage 5: isolated square inspection camera
       → AsyncGPUReadback ring (request-owned frame/session/camera/time)
       → PNG frame + neutral metadata over loopback HTTP
       → bounded Python queue (12; duplicate/order/session/age checks)
       → same YOLO11n ncnn weights and FP32 preprocessing
            ├─ CPU: ncnn CPU execution
            └─ GPU: Vulkan/RADV Radeon 8060S + two CPU MatMul partitions
       → confidence/NMS → image-only IoU tracks and candidate regions
       → captured evidence, overlays, timings; new station findings = uncertain
```

Stage 5 is separate from the Stage 4 classifier path. Runtime detector inputs include the full 640×640 RGB image and neutral line/session/camera/frame identity, sequence, dimensions and capture time. No simulator bottle ID/position, evaluator label, expected class, segmentation mask, fault flag or injected cause is included. Simulator positions are used only by the separate evaluator's segmentation pass to label visible pixels. Those labels are stored outside model/service requests.

The detector is a pretrained COCO bottle-class model, not a cap/fill/label defect model. It proposes bottle boxes from pixels. The tracker associates detections across images only; it does not recover simulator bottle identity. The application proposes cap/fill/label regions as geometric fractions of a detected box, but these crops do not satisfy the frozen Stage 4 classifier input contract. Therefore no old classifier is run on them, and the interface reports downstream inspection as uncertain.

Unity checks `SystemInfo.supportsAsyncGPUReadback` on the actual player. Four camera RenderTexture slots are request-owned and are not reused before completion/copy. Readback/capture failures, stale frames, queue full, duplicate, reset and retired-session cases are counted with reasons. The service queue and evidence retention are bounded. Benchmark Stop and the phase supervisor stop only this project's own Stage 5 player/service. Stage 5 is loopback-only; no PLC, remote access, public API, Qwen or physical camera integration was added.

GPU execution evidence is two-level: ncnn selects the enumerated Radeon Vulkan device, and each synchronized inference call records the process-scoped amdgpu DRM compute-engine counter before and after extraction. All 108 GPU locked-test calls showed a positive counter delta. The graph contains two CPU `MatMul` partitions. The counter delta is not a kernel-only duration or GPU utilization percentage. Host device utilization is reported separately and includes all GPU workloads.

Unity's asynchronous readback can reduce main-thread blocking while retaining latency. Its current measured readback is tens of milliseconds; the precise separation of camera rendering, readback, transport, image preprocessing, graph execution and scheduling is reported where instrumented. GPU transfer/kernel-only measurements remain unavailable. No derived GPU share is claimed.
