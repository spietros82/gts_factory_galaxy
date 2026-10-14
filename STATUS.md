# Current status: Stage 5 experimental full-frame vision

The native Stage 5 app and loopback service run with `./stage5/start.sh` / `./stage5/stop.sh` (API `127.0.0.1:8840`). Stage 4 is preserved. Detector-quality gate **failed**: CPU and verified Radeon Vulkan each found66/184 visible bottle instances, missing118; partial-occlusion found0/95. Do not use for accept/reject. Saved-frame replay:84.19GPU vs43.49CPU images/s; live one-line three-view×5Hz remained near60FPS at ~14.3images/s for either device. Nine views×5Hz hit bounded queue/responsiveness guards. See [Stage5 results](stage5/RESULTS.md), [handover](stage5/HANDOVER.md), [verification](stage5/VERIFICATION.md) and [GitHub delivery](stage5/GITHUB-DELIVERY.md). Review [PR #5](https://github.com/spietros82/gts_factory_galaxy/pull/5), open and unmerged.

---

## Preserved Stage 4 completion

See [milestone](stage4/MILESTONE-4.md), [delivery](stage4/DELIVERY.md), [performance](stage4/PERFORMANCE.md) and [known limits](stage4/VERIFICATION.md). Default one line/CPU/normal cadence. Highest confirmed pass24; first tested failure48. Faster acquisition retained failure; saved-crop replay is separate from camera capacity. Pietro accepted Stage4 before Stage5 work started.
