# Stage 5 dependencies and model provenance

Verified on an ASRock AI BOX A395 running Ubuntu 24.04.5, kernel `7.0.0-38-generic`, Ryzen AI Max+ 395 / Radeon 8060S. Unity Linux standalone, Editor `6000.6.5f1`. The Stage 5 Python service uses the existing project-local `stage5/.venv` (Python 3.12.3); observed packages: `ncnn==1.0.20260526`, `numpy==2.3.5`, `pillow==11.3.0`, `opencv-python==5.0.0.93`. The detector path uses ncnn, NumPy and Pillow; OpenCV is installed in the isolated environment but is not used by this detector. No global package, driver or system service was changed.

The ncnn Python wheel is from the ncnn project and is BSD-3-Clause. Runtime operation on this A395 used Mesa/RADV Vulkan and ncnn's Vulkan backend; device enumeration returned `Radeon 8060S Graphics (RADV GFX1151)` plus llvmpipe. The frozen model was downloaded earlier from the `nihui/ncnn-assets` repository at commit `45681cf121a3b12caab69c94f8b0ca336024e054`:

- `yolo11n.ncnn.param`, 21,413 bytes, SHA-256 `3e928cc8b0718835af46d04c01266705c8a430159d0e48739549a873e7294ec1`.
- `yolo11n.ncnn.bin`, 5,249,340 bytes, SHA-256 `2e1b06fa4210739a71d0bf3132e2f6560e46281e8e071292f2857b3bda726285`.

The model family is Ultralytics YOLO11n, pretrained COCO, converted for ncnn. Ultralytics documents AGPL-3.0 and Enterprise licensing options. The public repository does not include the weights because their redistribution rights and the converted artifact's exact licensing chain have not been independently cleared. No paid license was accepted. The public source projection therefore requires an operator-provided, lawfully obtained artifact matching the hashes above; the project must stop clearly on a hash mismatch. Do not copy the local weights into a customer package or public Git branch.

No training/fine-tuning occurred (0 minutes). No new model download was made during the implementation continuation; the preserved detector asset totals approximately 5.25 MB and package wheels approximately 106.3 MB. The Stage 5 weights are not bundled in the milestone source package. Model source: [ncnn-assets pinned revision](https://github.com/nihui/ncnn-assets/tree/45681cf121a3b12caab69c94f8b0ca336024e054); runtime: [ncnn Vulkan documentation](https://github.com/Tencent/ncnn/wiki/vulkan-notes); model licensing: [Ultralytics YOLO11 documentation](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo11.md).

AMD's current ROCm compatibility information lists Ryzen AI Max+ 395/gfx1151, but its native Linux setup guidance identifies a supported OEM kernel requirement; this host is on kernel 7.0.0-38 and has no ROCm installation. No ROCm, HIP or driver setup was attempted. The verified accelerator route is ncnn Vulkan through RADV, not ROCm.
