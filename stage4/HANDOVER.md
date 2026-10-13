# Stage 4 handover for Pietro and external ChatGPT

Stage 4 extends the existing Factory Galaxy application. Local branch: `stage4-independent-lines-capacity`. Stage 3 source `ad1f773`, tag `stage3-before-stage4-20261013` and compiled `builds/stage3-stage4-baseline` remain available. GitHub receives a source-only projection onto the reviewed Stage 3 history. See DELIVERY.md for final commits and the stacked PR; nothing is merged.

## What changed

Reusable line instances now have independent simulation state, counters, buffers, faults, sessions, PLC tags and three camera transforms. One scheduler advances every active line, including off-screen lines. Products cycle through Lager, IPA and Stout. The compact resizable interface adds line selection, count presets/custom guard, per-line controls, selected-line evidence and expanded Debug metrics.

`MultiLineClock`, `MultiLineFactory`, `MultiLineCapture` and `MultiLineFixtures` are new. Small compatible changes to FactoryApp, FactoryGeometry and PlcTelemetry preserve the original default. The Stage 4 Python engine supplies a fair bounded queue, current-session registry, unchanged CPU/GPU model adapter and bounded evidence storage. Start/stop/build scripts and an independent benchmark supervisor affect this prototype only.

No model, threshold or preprocessing change; no training, old locked-test reuse, language-model request, streaming change or driver installation.

## Findings to carry forward

- **24 lines passed; 48 was the first tested failure**, with two 60-second confirmations for full CPU, full GPU and rendering-only. Counts between these points were not measured. Default remains one line/CPU.
- At 24 lines, normal acquisition completed **31.2 images/s**, or 10.4 three-view bottle batches/s. CPU averaged 57.20–58.91 FPS; GPU 58.89–58.96 FPS. Trigger-to-result p95 was approximately 438–457 ms, including camera scheduling. All lines received inspections, with no normal-cadence drops/deadline misses.
- At 48 lines, full factory averaged approximately 37 FPS; rendering-only approximately 54 FPS. Scene update and synchronous readback grew while classifier/queue latency stayed short. This suggests a mixed presentation/acquisition constraint, not a demonstrated neural-inference maximum. Exact thread/GPU attribution is unavailable.
- CPU was sufficient for these tiny frozen MLPs. GPU execution was verified on Radeon OpenGL compute, with identical weights; no GPU latency benefit was observed. Saved-crop replay passed the ceiling of **1,200 images/s** on both devices, excluding acquisition, rendering, transport and storage.
- The separate faster acquisition sweep failed at its first rate: 1 batch/line/s on three lines. Whole-phase missing-target drops were 3 CPU images and 6 GPU images. Higher rates were not run. Failure retained; no tuning/retest cycle.
- The measured candidate wrote seconds into `acquisition_wait_ms`. Original records remain unchanged. A version-specific ×1000 reporting correction joins batch IDs to expose trigger-to-result latency. Future writer fixed. Later safety/metric closure is functionally checked, not a second capacity measurement.

## Verification and remaining limits

58 distinct offline tests passed. Original Unity simulation/presentation/telemetry checks (11/8/15) and 12 new multi-line checks passed. Native functional 29/29 and closure 7/7 passed, including service outage/restart while the simulator continued. New 81-crop integration fixtures agreed with their synthetic expected outcomes and between CPU/GPU; maximum score difference 2.3841858e-7. This is integration consistency, not industrial accuracy. Canonical images at different origins differed by at most one pixel-component byte; no byte-identity claim.

Old models, frozen datasets, reports and ledgers remain intact; Qwen ledger still 3/6. Raw evidence is under `reports/stage4/`; public summaries, screenshots and charts under `stage4/`. Performance applies to measured source `9ea0b8132c9266778630a93d65a246bd652f3455`. The original measured Stage 4 binary was replaced by closure builds; source and per-phase metadata survive, but no archived byte-identical candidate binary is claimed. Previous stage builds are preserved.

Historical evidence files persist, but the backend does not reload previous in-memory operator review after restart. Association and delayed target positioning are simulator-assisted. Real optics, lighting, triggering, speed, tracking and independent real-image labels remain unvalidated. Pixels cannot prove volume, torque, seal, readability or cause. No production security, sustained industrial capacity or need for an A395 versus cheaper hardware has been established.

## Demonstration

Run `./stage4/start.sh`; stop with `./stage4/stop.sh`. Default resizable 1600×900, one line/CPU/normal acquisition. Formal comparisons used fixed 1920×1080. Loopback API 8830 supports the native application; it is not a browser dashboard.

Show one line, then three. Select Line02, inspect its PLC tags/camera evidence, block its outfeed and watch its buffer while other lines continue. Clear it, switch CPU/GPU and show actual new execution. Open Debug, then the measured capacity charts. Use Stop benchmark to return to one line/CPU. Follow DEMO.md for the five-minute script.

Pietro's Stage 4 acceptance is pending. Stop here; discuss the findings before authorising another stage.
