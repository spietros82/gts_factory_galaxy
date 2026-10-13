# Stage 3 — three-station visual inspection

Completed local implementation and bounded verification, 1920×1080 only. Pietro accepted Stages1/2; Stage3 operator acceptance remains pending. Source branch stage3-three-station-inspection. Implementation/measurement freeze1f4e52e; later commits contain documentation/publication evidence. Reviewed public history is projected separately from the full local history; stacked PR targets stage2-plc-telemetry. Neither earlier PR nor Stage3 is merged automatically.

## What is ready

One accepted brewery line; Lager/IPA/Stout; Machine data/Digital twin/Combined retained. New light provisional Braemac interface, Inspection, Failure review, Debug and labelled synthetic Examples. Three controlled rendered station views of the same simulator-associated bottle assess cap presence/alignment, visible liquid boundary and label presence/alignment. No physical volume, seal/torque/attachment, label readability or cause claim.

Identical float32 MLP48 weights/preprocessing/policy execute on selected CPU NumPy or verified Radeon8060S OpenGL compute. Device switch applies between complete batches; no GPU-labelled CPU fallback. CPU handles image preprocessing, abstention, queues/storage/monitoring; Unity camera rendering uses GPU, readback/PNG CPU. Old CPU random forest and experimental Gemma remain separate preserved baselines, not another execution device of this model. New renderer/crops differ from that earlier cap-only dataset, so accuracy numbers are not a matched comparison.

Bounded image queue, timestamps/IDs, actual image evidence/age, historical pause/reset handling, duplicate rejection, explicit unavailability and persistent event audit. Latest60 defect/uncertain events remain reviewable independently of healthy recent results, with protected crops within bounded image retention. Presenter examples change visible geometry only. No real PLC writes, AI control, repairs, additional lines or streaming changes.

Manual local Qwen review uses recorded inspection fields and demo procedure S3-DEMO-1; cannot modify decisions. New persistent six-call ledger, three verification calls consumed, no retries. Language drafts and application fallback clearly differ. Qwen is optional; all inspections and factory operation remain usable without it.

## Verification evidence

- Final1440crops:864train/288validation/288test, complete36/12/12appearance groups,3products. First flawed development capture/probes preserved; total2904images≤3000. Training1.286s totalwall, within30minutes. Additional isolated downloads347,834bytes, within5GB; no system/driver changes.
- Frozen held-out evaluation once/device:96images per station,24/class. Each CPU/GPU confusion matrix diagonal24/24; no observed missed defects/false rejects;100%decidable coverage;24/24poor-quality abstained/station. Each product8/class correct. Correlated synthetic samples, no real-camera proof;0/24critical false accepts has Wilson95%upper13.8%, not zero risk.
- Thirteen new offline checks;18 original Python;22 preserved focused/startup;actual Unity Editor checks11simulation/8presentation/15telemetry, all PASS. Counts describe separate suites, not summed reruns.
- Native initial25assertions:24PASS/1early navigation-audit failure retained. Settled Machine data check and focused four-view recheck PASS. All7visible defect/poor-image fixtures, same-bottle identities, all3products, CPU/GPU actual batches, pause/newsession/history, Debug, zero automatic Qwen calls checked. Six boundary assertions PASS: stale/missing/ambiguous withheld;duplicate/hiddentruth rejected. Own service outage left native clock advancing with unavailable/N/A display. No other services stopped.
- Three exact Qwen replies:6.701s/4.351s/3.206s. Cap useful but discusses uncalibrated score; fill useful raw reply initially falsely rejected by ML-versus-mL guard bug, preserved fallback and failure. Bug fixed with offline regression/saved-reply replay only. Label reply generic and omitted recorded misalignment: material usefulness failure despite valid references. No claim that schema membership proves support. All3vision records unchanged.
- Two warmed60s runs per disabled/CPU/GPU condition; same1920scene/product schedule/capture cadence. Original runs retained; post-fix comparison recorded separately. Bounded replay uses saved validation crops and reaches tested100batches/s ceiling without establishing saturation. Total measured budget remains below20minutes. See PERFORMANCE.md for final tables, source/configuration, inference/resource definitions and limits.

## Launch and review

```bash
cd /home/braemac/GTS_factory_galaxy
./stage3/start.sh
./stage3/stop.sh
journalctl --user -u braemac-factory-stage3-player -u braemac-factory-stage3-service -f
```

Native window, no browser dashboard. Own service127.0.0.1:8820, two user units above; do not expose it publicly. Earlier launchers ./telemetry/start.sh, ./presentation/start.sh and ./inspection/start.sh unchanged. Demo script DEMO.md; architecture ARCHITECTURE.md; dependency/model reproduction README.md / DEPENDENCIES.md / MODEL.md. Screenshots are actual native captures; local full-resolution originals reports/stage3/gui, reviewed reduced copies stage3/screenshots. No generated mockups.

## Limits and stopping point

Synthetic controlled isolated cameras and simulator-assisted identities; no real-camera localisation/occlusion/tracking reliability. Small scene-conditioned model, uncalibrated scores, appearance shortcuts possible. Difficult examples do not cover every unknown distribution. Physical pilot requires controlled optics/light, production speeds/spacing, independently labelled real images and unseen product variation. No industrial approval, production security, recovery guarantee, NPU/Qualcomm integration, hardware-sizing proof or time-saving claim. GPU utilisation is whole-device and includes background work; no invented task shares. CPU can be sufficient, GPU advantage must not be assumed.

Source package excludes weights/datasets/runtime/binaries/secrets/caches; locally reproduced model/build dependencies required. No separate host tested. No further training, locked retest, language retry, streaming work or follow-on scope. Stage3 ready for operator review after final launcher health check; acceptance pending until Pietro tries it.

Final measured outcome:59.917–59.950FPS; CPUcapture-to-result mean13.571–13.987ms, GPU16.493–16.546ms (see exact PERFORMANCE.md table);78steady inspections/60s/run,zero drops/stale/deadlines. Total performance1020.058s. Final unit/PR/package closure recorded below.
