# Stage 3 compact operator layout — 13 October 2026

Focused revision requested by Pietro after Stage3 delivery. Local branch stage3-compact-operator-layout starts from a3cc609; earlier milestone tag stage3-local-milestone-20261013 remains unchanged. No new milestone, training, locked evaluation, language-model request, streaming work or performance cycle.

## Visible change

Combined/Digital twin now keep the line as the main view. The previous full-width bottom row of three155px crops is replaced by a side rail with92px thumbnails. Click Open evidence for the original full-size result/image/identity/timing record; dedicated Inspection and Failure review remain available. Main Combined viewport height increases from530 to866pixels at1920×1080; this is a layout dimension, not a measured performance improvement.

Navigation is one compact row; line pause/reset and presentation cameras are grouped beneath it. Product selection and vision-device controls are grouped on the right. Neutral buttons have dark readable text; selected controls have teal backgrounds/white text. Digital twin uses short machine-state labels; Machine data/Combined retain original tags, units, quality and source time. Mode changes reset the relevant scroll offset. Scope, evidence age and actual execution device remain explicit.

## CPU conclusion from the saved matched comparison

The three small vision models can run on CPU at the tested demonstration load. Each shared bottle trigger produces three256×256 station frames/160×160 crops, reduced to24×24RGB features for a small MLP48. This is not three continuous camera streams.

|Saved measurement|CPU vision|Inspection disabled|
|---|---|---|
|Completed results/60s|78 =1.3individual inspections/s (~0.433three-view bottle batches/s)|0|
|Host CPU, all32logical processors=100%|2.90–2.92%|2.80–2.86%|
|Inspection-service CPU, one logical core=100%|2.01–2.02%|1.23–1.25%|
|Capture→result mean|13.571–13.987ms|N/A|
|Unity FPS|59.935–59.937|59.941–59.950|
|Drops/stale/missed2s deadlines|0|N/A|

GPU vision means16.493–16.546ms: no measured advantage for these small models. Resource differences are small and subject to host variation. CPU-service2% of one core corresponds to about0.063% of total32logical-processor capacity, not2% of the entire host. Camera rendering and Unity remain GPU workloads. Qwen was loaded but idle; CPU language-model inference was not measured. Higher-rate real cameras, larger networks and other hardware remain unproven. Saved replay is not a full camera-acquisition capacity test. Full matched results and timing definitions are in PERFORMANCE.md; no new benchmark numbers are claimed for this revised viewport.

## Preservation and launch

Capture cameras/lighting/materials/geometry, crop association, timestamps, backend weights/preprocessing/thresholds, source contracts and Qwen ledger are unchanged. Only presentation viewport, GUI and optional build-path selection changed.2423earlier preservation hashes and5candidate-freeze hashes checked unchanged. New Qwen calls0; ledger remains3/6. Prior full-history/private data never pushed.

Current revised native demo:

```bash
cd /home/braemac/GTS_factory_galaxy
./stage3/start.sh
./stage3/stop.sh
```

Preserved original Stage3 layout build on this host:

```bash
./stage3/stop.sh
STAGE3_BUILD_DIR=builds/stage3-original-layout ./stage3/start.sh
```

Stop again and use the ordinary start command to return to the revised build. Build-path selection only applies when starting a stopped player; it does not replace a running player. Both builds use the same frozen local service and preserve evidence/ledgers. The previous source remains at the milestone tag; binaries are excluded from Git/package. Earlier Stage1/2 launchers remain unchanged.

## Verification and evidence

Native release built with pinned Unity6000.6.5f1, Built-in/OpenGLCore,1920×1080.14offline safety checks PASS. Focused native check covers all7pages, all3products, same-bottle three-frame association, compact-preview→full evidence, pause, reset/new session, retained historical evidence, CPU selection and no new Qwen calls. Final result count and actual screenshots are recorded in reports/stage3/ui-revision/native-checks.json. No failed attempts deleted: initial text-escaping compilation failure corrected, test foreground/pointer settling and session-query errors corrected; first/second raw UI attempts remain alongside final results. These are GUI/test-harness fixes, not tuned inspection evaluation.

Actual full-resolution screenshots: reports/stage3/ui-revision/before-combined.png, after-combined.png, after-digital-twin.png, after-inspection.png, after-evidence-review.png, after-paused.png, after-debug.png. Reviewed JPEG copies in stage3/screenshots/ui-*.jpg. No mockups. Original reports/screenshots/builds retained.

No matched performance run added: saved measurements describe the earlier measured layout/configuration. New layout checked visually and functionally; no claim of improved frame rate, inspection accuracy, industrial reliability, full-video capacity or CPU language-model capacity. Operator acceptance of this revised arrangement remains pending.

Final native UI smoke result: 18/18 PASS. Final14offline safety checks PASS. Earlier failed UI attempts retained, not added to test counts. Original-layout launch path exercised to capture the actual before image; revised build then checked again.
