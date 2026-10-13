# Stage 4 completion summary

Delivered independent synthetic brewery lines in the existing Unity application. The compact resizable interface supports line-count presets/custom guard, cyclic products, per-line PLC state/faults/counters and three controlled image inspections. One coordinated scheduler keeps off-screen lines active. Results retain line/session/bottle/station/frame identity; removal/reset cannot attach old results to new instances. CPU/GPU selection uses unchanged weights and policy.

The software allocation guard is 48; safe default is one line/CPU. The single bounded performance cycle took 30.60 minutes with zero Qwen requests. Highest confirmed presentation pass: **24**. First tested failure: **48**, on frame timing, for complete CPU, complete GPU and rendering-only. The exact boundary is unknown. At 24 lines, normal acquisition completed 31.2 images/s; CPU averaged 57.20–58.91 FPS and GPU 58.89–58.96 FPS.

Faster live acquisition failed at its first rate with explicit missing-target drops; higher live rates are unproven. Saved-crop replay reached the tested ceiling of 1,200 images/s on both devices, excluding camera/rendering/transport/storage. CPU was sufficient for this model; no GPU advantage claimed.

Verification: 60 offline tests, original Unity checks plus 12 multi-line checks, 29 native functional and 7 native closure assertions passed. New 81-crop integration fixtures agreed with expected synthetic outcomes and between CPU/GPU. No retraining, old locked-test evaluation or new accuracy claim. Cross-origin images have small pixel differences; real-camera validation remains necessary.

Preserved previous source/builds/results/models/ledgers. Measurement source is `9ea0b8132c9266778630a93d65a246bd652f3455`; final source/PR IDs are in DELIVERY.md. Original timing-unit error and other failures remain recorded; explicit corrected timing reports do not replace raw evidence. Later safety/metric closure was functionally verified without another capacity cycle.

Launch/stop: README.md. Walkthrough: DEMO.md. Exact results/charts: PERFORMANCE.md and RESULTS.csv. Evidence/failures: VERIFICATION.md. Screenshots: screenshots/. Source-only GitHub delivery excludes private history, raw data, weights, builds and credentials.

Stage 4 is ready for review; acceptance pending Pietro. Known limitations include experimental faster cadence, simulator-assisted image acquisition, bounded/non-reloaded review history and unproven real-camera/industrial reliability. No conclusion about hardware necessity or a cheaper alternative. No Stage 5 started.
