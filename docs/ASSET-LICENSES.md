# Dependency and asset manifest

- Machine forms, conveyors, PET-bottle lathe mesh, materials, lighting and signs: procedural source authored in this project; no purchased/downloaded artwork.
- Braemac / GTS words: user-requested branding. No third-party logo asset was copied.
- Unity Editor/player, built-in shaders/font/engine: Unity's applicable licence. Pietro performed account/licence/terms interaction. Eligibility and redistribution compliance are the operator's responsibility; this report does not claim a free corporate licence.
- Unity6000.6.5f1; built-in module packages1.0.0. Exact package lock in UnityProject/Packages/packages-lock.json. Built-in pipeline remains supported but deprecated for new projects.
- Python3.12.3 standard library runtime. Existing .venv package versions recorded in reports/dependencies.json; the service does not depend on NumPy/scikit-learn.
- Existing qwen3:8b Q4_K_M and gemma3:27b-it-q4_K_M tags/digests recorded in reports/environment-check.json and resource records. Model weights are NOT distributed in the package. Check each model's licence before redistribution or commercial deployment; no new model acquired here.
- tools/offline_socket_guard.c: project-authored, process-scoped verification shim. Compiled with the existing GCC. Not a general security boundary or physical network isolation.

## Optional streaming dependencies

Project-local isolated Python environment, exact versions in streaming/dependencies.lock.txt. aiortc1.14.0 (BSD-3-Clause project), aiohttp3.13.2 (Apache-2.0 project), PyAV16.1.0 (BSD project bindings), NumPy2.3.5 (BSD-3-Clause); transitive components retain their own terms. PyAV binary wheel includes FFmpeg/libx264 codec components whose GPL/codec-patent/distribution obligations differ from the Python binding. The streaming package deliberately excludes the virtual environment and codec binaries; dependency installation instructions are included, not a commercial licence certification. Licence texts are available in installed distribution .dist-info/licenses and each official source repository. No model weights, private Editor/licence files or purchased assets distributed. Native player retains Unity terms from the original manifest. Review actual commercial distribution/use terms before redistribution; this milestone is local PoC verification only.

Public signalling enablement13October2026 adds only a project-local cloudflared2026.10.0 executable, pinned to its official GitHub release digest. Apache License2.0 text preserved in docs/CLOUDFLARED-LICENSE.txt; installed binary excluded from Git/earlier packages. Reproduction helper downloads and verifies that exact release without global installation/auto-update. Quick Tunnel is temporary test hosting, not a permanent account-managed service or a TURN relay. No model weights/dependencies/graphics driver changes in this enablement.
