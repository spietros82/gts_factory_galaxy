# Frozen locally trained model artifacts

Preprocessing RGB24×24bilinear flattenedfloat32/255;48ReLUhidden neurons/four outputlogits perstation, shared softmax/qualitypolicyCPU. Class order in policy; threshold0.8uncalibratedscore. CPU NumPy vs AMD OpenGL compute uses identical float32 matrices. In GPUmode dense layers execute GPU; preprocessing/softmax/qualitypolicy remainCPU. No pretrained weights, NPU or ROCm neural backend.

| Artifact | SHA256 |
|---|---|
| cap.npz |745de03a30015b5219e21c48f8ee1ab5d8f5cd68b34620975f58dae13b2e4d8d|
| fill.npz |4443e885a8065f0e7dddfdd5138a464bfe011e386114763857f92944c5d02fe7|
| label.npz |72852fefe773ce797db4f58de4a23fe12f57a99afe2197e0902fb6d91213b411|

No weights/datasets distributed publicly. Source scripts/pinned dependencies/capture controls reproduce artifacts locally on a compatible licensed Unity host; numerical/driver behaviour elsewhere unverified. Old capRF f7561e9d… remains untouched as a different-model/old-render baseline, never presented as a pure CPUhardware comparison. Do not retrain/tune on this locked test after milestone completion.
