# Stage 3 — three-station brewery inspection

Native Unity6000.6.5f1 Linux/Built-in/OpenGLCore, sole supported presentation1920×1080. One synthetic line, three image-based assessments of the same simulator-associated bottle. Provisional light Braemac theme, fictional beer identities; exact corporate logo/colour approval not available. Earlier brewery geometry, telemetry contract/mapped mechanisms, product controls and accepted builds retained. Stage3-only transparent-glass shader makes visible liquid boundary inspectable; old inspection configuration/build remains frozen.

```bash
cd /home/braemac/GTS_factory_galaxy
./stage3/start.sh
./stage3/stop.sh
journalctl --user -u braemac-factory-stage3-player -u braemac-factory-stage3-service -f
```

Native window; no dashboard URL. Own loopback service127.0.0.1:8820. Start reuses own active units, checks ownership/port/readiness; no port-owner kill. Config example→excluded local configuration, endpoint/model/data paths configurable.1920×1080 always; crops stay160×160 and neural features24×24. Source camera configuration stage3/cameras.json / packaged StreamingAssets/stage3-cameras.json; override --stage3-camera-config. Renderer camera isolation/localisation is simulator-assisted, not independent real tracking.

Top navigation Machine data / Digital twin / Combined preserves Stage2 concepts.1/2/3 shortcuts; F5–F8 camera views; Space pause/Rreset/Boutfeed/Cclear. Inspection shows three actual crops and selected/actual backend. Examples offers labelled presenter-only synthetic visible defects; these alter bottle appearance, not PLC readings or diagnosed causes. Failure review lists detected defects and uncertain events separately by result wording; select evidence to see image, exact IDs/times/score/timings. Explain this event is a manual local Qwen action. Debug shows bounded measured counters and limitations. No automatic inference explanations or repairs.

Pause marks imagery historical. Reset makes a new process/inspection session while retaining event audit. Stale/missing/poor-quality evidence cannot be a current pass. Switching CPU/GPU applies between complete shared-bottle batches. GPU unavailable is explicit; no silent device fallback. Qwen unavailable/invalid uses labelled application factual fallback; raw reply preserved, vision result immutable. Persistent new six-request Stage3 verification ledger does not reset on player/service restart.

## Reproduce excluded data/models locally

Existing .venv supplies pinned NumPy/Pillow/scikit-learn/SciPy; stage3/.venv adds pinned ModernGL5.12.0/glcontext3.0.0 without modifying it. DEPENDENCIES.md explains this reuse and wheel hashes/licences. On another compatible host create an isolated environment with recorded requirements; compatibility/performance elsewhere is unverified. Do not alter drivers for this demo.

1. Read PROTOCOL.md. Run `stage3/.venv/bin/python -m stage3.prepare` (new output only).
2. Build with `./stage3/build.sh` using existing licensed Unity6000.6.5f1/Linux support. This writes builds/stage3 only; stop Stage3 first.
3. Run the built player with `--presentation true --plc-demo true --stage3 true --stage3-dataset "$PWD/stage3/dataset" --data-path "$PWD/runtime/stage3-dataset" -screen-width 1920 -screen-height 1080` (pass width/height as separate options/values). Dataset capture exits after1440 images. Keep source images/manifest locally, never commit them.
4. `stage3/.venv/bin/python -m stage3.finalize_data`; inspect development review sheets, never use locked images for tuning.
5. `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 stage3/.venv/bin/python -m stage3.train`. Frozen policy records model SHA256. Weight artifacts safe NPZ, no untrusted pickles.
6. Runtime needs local stage3/models/{cap,fill,label}.npz and policy.json. GitHub excludes datasets/weights/binaries. `evaluate` refuses an already-attempted locked device; do not remove markers or rerun held-out tests to hide errors. Reproduction is a fresh deployment, not permission for another evaluation on this host.

Prior Stage2: ./telemetry/start.sh / stop.sh; Stage1: ./presentation/start.sh / stop.sh. Old focused ./inspection/start.sh preserved. Avoid concurrent demo render windows unless explicitly measuring concurrency. Stage3 scripts never stop those services or modify Ollama/WebUI/remote access/streaming.

Scope: synthetic visual categories, not physical volume, mechanical attachment/torque/seal, label readability or causal diagnosis. No independent industrial validation, safety-control integration, production security or cross-hardware sizing proof. Stop after Stage3; operator acceptance pending.

Verification summary: MILESTONE-3.md and VERIFICATION.md. Final machine comparisons PERFORMANCE.md; metric definitions METRICS.md. Three verification language calls consumed; no automatic background explanations. Previous raw errors retained. Stage3 user acceptance pending.

Reviewed stacked [Stage3 PR#3](https://github.com/spietros82/gts_factory_galaxy/pull/3); not merged. Delivery record DELIVERY.md. Measured vision/render code1f4e52e, final language-only guard f75d808; no extra inference or evaluation. Source-only ZIP dist/FactoryGalaxy-Stage3-source.zip.
