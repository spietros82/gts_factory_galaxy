# Stage 5 — experimental full-frame vision

Stage 5 adds an experimental full-frame bottle detector and image-space tracks while preserving Stage 4 as the established inspection demonstration. It is a synthetic, single-line brewery scene; it is not a physical-camera or industrial inspection validation. The candidate detector failed the locked recall target, so all detector-derived cap/fill/label findings remain **uncertain**.

## Run the local demonstration

On the prepared A395, from the repository root:

```bash
./stage5/start.sh
./stage5/stop.sh
journalctl --user -u braemac-factory-stage5-player -u braemac-factory-stage5-service -n 100 --no-pager
```

The native Unity window is the interface. The Python service binds only to `127.0.0.1:8840`. Defaults are one line, CPU inference and one analysis view. Select **Full-frame** to view the experimental path; select **CPU/GPU** to change the detector device; select **1/3/9 views** and **5/10/20 Hz** to vary offered work. These are demand controls, not capacity guarantees. **Debug** shows observed rates, actual execution, device-wide utilization and bounded queues. Use **STOP BENCHMARK** to return to a safe presenter profile.

To stop only this prototype, use `./stage5/stop.sh`. Stage 4 remains independently available with `./stage4/start.sh` / `./stage4/stop.sh`. Do not run two Unity presentation windows during a matched measurement. Stage 5 start/stop does not stop the other project services.

Build with `./stage5/build.sh` when the Stage 5 player is stopped. It uses the installed Unity Editor 6000.6.5f1 and produces the local Linux player under `builds/stage5/`; no global installation is performed.

## Five-minute walkthrough

1. Start Stage 5 and leave the default CPU/one-view setting in place. Point out the synthetic PLC state and moving line.
2. Open **Full-frame**. Explain that pixels, not simulator bottle IDs, go to the detector; boxes and track IDs are detector/image-derived. A missing box is not a pass.
3. Select the bottle-camera view and inspect frame age and the always-uncertain downstream finding.
4. Select GPU and confirm **actual** execution. The GPU route includes two CPU MatMul partitions; availability or model residency alone is not the evidence.
5. Open **Debug**. At 3 views × 5 Hz, show that the short final-layout run stayed near 60 FPS; at the higher 9-view workload the earlier bounded test hit queue and responsiveness limits.
6. State the quality result plainly: only 66 of 184 visible bottle instances were found on the locked synthetic set. Stage 5 is an experimental localisation visualisation, not an inspection decision system.

## Frozen artifact and reproducibility

The local model and isolated packages are not included in the public source branch. See [dependencies and artifact provenance](DEPENDENCIES.md), [frozen settings](PROTOCOL.md), [label-validity erratum](EVALUATION-ERRATUM-1.2.md), [results](RESULTS.md), and [architecture](ARCHITECTURE.md). The v1.2 test images/labels and per-frame results stay in ignored local `runtime/` and `reports/` paths. The handover includes curated actual application screenshots; it does not include test labels or model weights.

Run offline service-contract checks with `stage5/.venv/bin/python -m unittest discover -s stage5/tests -v`; they use a fake detector and do not run model inference. `stage5/final_layout_check.py` performs one short CPU and one GPU live camera sanity run and restores the normal one-line CPU launcher afterward; it is not the full capacity sweep.

The Stage 5 detector should not be used to accept/reject actual products. Physical optics, lighting, camera triggering, line speed, packaging variation and independently labelled real images have not been assessed.
