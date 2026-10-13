# Braemac Factory Galaxy — Stage 4

Independent synthetic brewery lines with simulated PLC data and three image inspections per line. Native Unity is the primary interface. One line is the default; 1/3/6/12/24 presets and custom1–48 are guarded options, not performance guarantees. Cyclic Lager/IPA/Stout, independent buffers/faults/sessions, off-screen acquisition, selected-line evidence and bounded CPU/GPU queues. No real PLC/camera, automatic repair or industrial capacity claim.

## Launch on this prepared machine

```bash
cd /home/braemac/GTS_factory_galaxy
./stage4/start.sh
./stage4/stop.sh
journalctl --user -u braemac-factory-stage4-player -u braemac-factory-stage4-service -n 100 --no-pager
```

Defaults resizable1600×900/CPU/one line/normal station-triggered acquisition. Rendering measurements use1920×1080. To launch the same fixed resolution for a visual comparison: `./stage4/start.sh --fixed-1080p true` after stopping this prototype. API only at loopback8830; this is not a browser dashboard or streaming change. Use Debug for actual device, rates, latency and resources. Start is idempotent and does not restart an already active player; stop then start to change launch arguments. Units are user-level transient services, not boot-enabled.

Preserved Stage3: `STAGE3_BUILD_DIR=builds/stage3-stage4-baseline ./stage3/start.sh` after stopping Stage4; `./stage3/stop.sh` stops that version only. Stage1/2 launch paths, prior source tag `stage3-before-stage4-20261013` and old builds/results remain. Never run both presentation windows for a matched measurement.

## Controls and review

Preset/custom line count (guard48); CPU/GPU effective between complete bottle batches; inspection ON/OFF; normal/explicit benchmark cadence; factory overview/selected-line/station cameras. Click a line, use per-line blockage/clear/reset and synthetic visible-defect controls. Machine data/Digital twin/Combined/Failure review/Debug; Space pause, Home/F5overview,F6filler,F7capper,F8inspection,1/2/3presentation modes. Right-drag orbit/scroll zoom.

Only current matching line/session results enter evidence cards. Pause/reset marks old evidence historical; missing/stale/poor-quality evidence is uncertain. Select failure to inspect actual crop and timing. Language explanations remain optional under the preserved Stage3budget; none were requested for Stage4. They cannot alter decisions. Simulator-only controls never send PLC commands.

`STOP BENCHMARK` returns this application to one-line CPU/normal cadence. The independent automated supervisor may instead terminate its owned unresponsive child; the wrapper restores the stable application. Whole-cycle guard abort is offline tested. The completed cycle is immutable; benchmark.sh refuses an automatic rerun. Presenter benchmark cadence has a retained missing-target drop failure and is experimental.

## Reproduction and limits

See [dependencies](DEPENDENCIES.md), [architecture](ARCHITECTURE.md), [contracts](SCHEMA.md), [metric definitions](METRICS.md), [frozen protocol](PROTOCOL.md), [measured results](PERFORMANCE.md), [verification](VERIFICATION.md), [milestone](MILESTONE-4.md), [handover](HANDOVER.md) and [walkthrough](DEMO.md).

Use the existing licensed Unity6000.6.5f1 and stage3/.venv, with locally present frozen Stage3models. `./stage4/build.sh` builds a Linux release using relative project files. UNITY_EDITOR can override Editor path. Stage4config.local.json (excluded) derives from config.example.json; backend/model paths and loopback port configurable. Launch detects missing artifacts/busy unrelated port and stops clearly. No Stage4 downloads or installations.

Public source/package excludes builds, weights, datasets, private/full history, runtime records/secrets. Reproduction requires compatible licensed Unity, pinned dependencies and separately available frozen model artifacts, with hashes in stage3/MODEL.md. Recreating weights is a separate authorised training task, not part of launching this milestone; do not retrain old held-out data. Package is source-only, not a turnkey binary or proof on another host.

Highest confirmed passing count24, first tested failing48; exact boundary unmeasured. CPU was sufficient for this tiny synthetic model; GPU did not improve the reported latency. Synthetic inspection consistency does not validate a real production camera. Stage4 acceptance is pending Pietro's review; no Stage5 started.
