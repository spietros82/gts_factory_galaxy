# Stage 5 handover for Pietro — 14 October 2026

## What to open

On the A395, open a terminal at the repository root:

```bash
./stage5/start.sh
./stage5/stop.sh
```

The native Unity window is the UI. The Python inference endpoint is loopback-only at `127.0.0.1:8840`. Current review build runs with one synthetic line, CPU selected, 1600×900 resizable. Stage4 remains separately launchable with `./stage4/start.sh` / `./stage4/stop.sh`. This is not a browser application.

## Five-minute walkthrough

1. Open Full-frame and point to the camera crop: the detector sees image pixels; it is not supplied a bottle identity or defect label.
2. Show the cyan/green boxes and transient image-track IDs when detections occur. Point out the separate no-detection screenshot: absence of a box does not mean a bottle passed.
3. Open Debug; compare selected versus actual CPU/GPU, queue depth, image throughput, capture-to-result age, Unity frame time and device-wide GPU metric.
4. Select GPU and verify the app reports actual Vulkan execution. Explain that two graph partitions remain CPU and device-wide GPU is shared by the whole desktop.
5. Return to Stage4 to show the established station-assisted cap/fill/label inspection. Its previous quality result is preserved; Stage5 candidate regions do not invoke those classifiers.
6. State the locked test outcome: 66/184 visible bottle targets found overall, and0/95 partial-occlusion targets. It fails the frozen target and is not an acceptance/quality-control tool.

The detector is pretrained YOLO11n over COCO's generic bottle class; it does not identify cap/fill/label defects. The Stage5 area labels all detector-derived inspection as uncertain. Do not describe the screenshot or throughput as production camera performance.

## Important result

The A395 ran the same frozen model on CPU and the Radeon 8060S Vulkan path. GPU execution was confirmed on all108 held-out replay calls by process-scoped AMD DRM compute-counter increments; two MatMul partitions remained CPU. Replay throughput was84.19 images/s GPU vs43.49 CPU, with identical outputs. The combined live 3-camera,5Hz check stayed around60FPS and ~14.3 completed frames/s for either device. The nine-camera/45fps requested workload failed the queue/responsiveness guard. Read [results](RESULTS.md), [verification](VERIFICATION.md), [architecture](ARCHITECTURE.md), [dependencies](DEPENDENCIES.md) and [capacity chart](capacity-chart.svg) for definitions and limits.

## Files and evidence

- Actual Unity screenshots: [detector overlay](screenshots/full-frame-detection-overlay.png), [a frame with no detections](screenshots/full-frame-no-detections.png).
- Raw locked CPU/GPU per-image results, capture plans, evaluator-only labels, failed v1.0/v1.1 experiments and capacity JSONL are preserved locally beneath ignored `reports/stage5/` and `runtime/stage5-eval-v1.2/`; no private or evaluator data is included in the reviewed public source projection.
- Reproduce the short final-scene CPU/GPU sanity check with `stage5/.venv/bin/python stage5/final_layout_check.py`. It stops/restarts only Stage5's own units, writes per-run records, restores `config.local.json`, and brings the demo back in one-line CPU mode. This is not the longer full capacity cycle.

## Acceptance and next action

The full-frame mode is ready to view as an experimental pixel-localization prototype; the detector did not pass its locked quality target. Stage5 is therefore a partial demonstration milestone, not an inspection-quality acceptance. The next safe technical direction, if later authorized, is to select an open-licensed detector appropriate for this synthetic rendering or collect a new development dataset and a new never-before-scored locked set. Do not tune on v1.2. A real pilot would separately need camera/lens/lighting, trigger/line-speed characterization, target packaging variety, independently labelled real images and physical validation.

## Source delivery

See [GitHub delivery record](GITHUB-DELIVERY.md) for local commit, source-only public projection and review PR. Stage4 history remains the base; no merge, force push or repository visibility change occurred.
