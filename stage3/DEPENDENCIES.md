# Dependencies, licences and reproducibility

Host verified Ubuntu24.04.5 / Ryzen AI Max+395 / Radeon8060S /32logical CPUs. Unity6000.6.5f1 Linux Mono release / Built-in/OpenGLCore; installed Unity licence/build support retained, not redistributed as open source. Existing project-owned procedural machinery/bottle/fictional labels; presentation/ASSETS.md retains provenance. New glass shader and interface are project-authored; no external logo, artwork, paid asset or pretrained model. Provisional colour theme is not official-brand compliance.

Existing factory environment: Python3.12.3; NumPy2.3.5 (BSD3), Pillow11.3.0 (HPND), scikit-learn1.8.0 (BSD3), SciPy1.18.1 (BSD3), joblib1.6.0 (BSD3). Stage3 creates its own venv and adds a .pth reference to the existing factory environment’s site-packages, so it reuses those read-only packages; it is not a fully self-contained environment. No existing package was installed/upgraded. On another host install pinned requirements only in an isolated environment and retain their licence notices.

Additional downloads: ModernGL5.12.0 and glcontext3.0.0 wheels, MIT licences, PyPI source. Total347,834bytes (artifact ledger reports exact bytes/SHA256; no model-weight downloads). Runtime test executed an OpenGL4.3+ compute shader through EGL on AMD Radeon8060S / Mesa25.2.8; shader timing/result returned. No driver, global package, ROCm or Ollama changes. Neural weights trained locally with scikit-learn, exported safe float32 NPZ; public GitHub/package excludes weights/datasets as requested. Reproduction scripts generate new synthetic data and artifacts on a compatible licensed Unity host. No third-party pretrained weight terms assumed.

Official runtime references:
- https://moderngl.readthedocs.io/en/latest/topics/context.html
- https://moderngl.readthedocs.io/en/latest/reference/compute_shader.html
- https://github.com/moderngl/glcontext
- https://docs.mesa3d.org/relnotes/25.2.8.html
- https://pypi.org/project/moderngl/5.12.0/
- https://pypi.org/project/glcontext/3.0.0/

Actual installed dependency versions/wheel hashes, GPU probe, model hashes/training duration, frozen manifests and per-device results are retained in reports/stage3. Portable source package is internal review, not proof of weight redistribution, another GPU, industrial accuracy or comparable host performance.

Wheel hashes:
- glcontext3.0.0:04921720740438ceea8fb8a38b5665963520c7c8f27bef03df8aeb3ea3cfbfb6 (51,440bytes).
- ModernGL5.12.0:b6c4972f3ddd10a3de6c30311da2c25bc493d023796e16c5d4e0f8bd6d5770be (296,394bytes).
