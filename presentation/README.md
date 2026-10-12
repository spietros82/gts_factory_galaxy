# Stage 1 — brewery presentation

One existing synthetic bottling line with fictional Braemac Lager / IPA / Stout identities. Product selection changes visual materials only. Production logic, bottle IDs and process clock remain the existing LineSimulation implementation.

## Installed machine

```bash
cd /home/braemac/GTS_factory_galaxy
./presentation/start.sh
./presentation/stop.sh
journalctl --user -u braemac-factory-stage1-player -f
```

Start is idempotent. New native build: `builds/stage1/FactoryGalaxy.x86_64`. User unit: `braemac-factory-stage1-player`. Existing inspection service is reused without restarting it or resetting its explanation budget. Stop stops only the Stage 1 player. Prior player and streaming units are untouched. No language-model calls are enabled by this launch.

Use LAGER / IPA / STOUT in the top bar. Views: Overview F5/Home; Filler F6; Capper F7; Inspection F8. Existing machine clicking, right-drag orbit, mouse-wheel zoom, Pause/Space, Reset replay and speed controls remain. Product selection survives process replay reset. The initial profile is PLC-only; Entry → Evidence shows the preserved inspection image separately.

1920×1080: `STAGE1_WIDTH=1920 STAGE1_HEIGHT=1080 ./presentation/start.sh` after stopping this Stage 1 player. Other desktop dimensions are unverified.

## Prior working demonstration

```bash
./presentation/stop.sh
./inspection/start.sh
# stop that prior player/service with ./inspection/stop.sh when desired
```

The prior `builds/inspection` executable and its original launcher/configuration remain untouched. The earlier original `./start.sh` / `./stop.sh` paths are also retained. Source baseline tag: `stage1-working-baseline-20261013` at9f9be74. Do not checkout over user changes. Inspection raw data, frozen classifier, policies and held-out dataset remain on the host.

## Build and source delivery

`./presentation/build.sh` uses installed licensed Unity6000.6.5f1 and writes only builds/stage1. Set UNITY_EDITOR for another licensed Editor path. Existing Python dependencies are used; no installation performed. Shared service requires the locally preserved trusted cap-rf artifact, never an uploaded/untrusted pickle. The public source delivery intentionally excludes model weights and dataset/runtime evidence.

On a compatible host with no frozen inspection artifact, build the native source and launch the executable directly with `--presentation true --focused-inspection true --profile 1 --disable-explanations true`. The visual PLC-only line runs; inspection service is unavailable, not fabricated. Supply trusted authorised model/configuration separately to enable the old inspector. Cross-host performance and graphics compatibility are untested.

## Inspection boundary

Old scene objects use render layer8; brewery objects use9. Original key/rim lighting is restricted to8, presentation lights to9. Original camera transform, optics, resolution, material values, cap dimensions and ROI association remain. The main presentation camera excludes8; focused inspection camera sees8 only. Original RenderSettings remain unchanged. No reflection probe/global lighting change introduced.

This is a preserved alternate inspection view, not a claim that Lager/IPA/Stout glass or labels are represented in the classifier's input. Upgraded presentation pixels are NOT validated for inspection accuracy. See inspection-compatibility evidence and Stage1 report for the bounded pixel comparison. There was no training, held-out evaluation, threshold change or Qwen call in this stage.

## Checks and evidence

See STAGE1.md, VERIFICATION.md, PERFORMANCE.md, ASSETS.md and reports/stage1. Short rendering runs hold the original overview camera, 1600×900, cap60/VSync0, 4MSAA, normal seed42/1×, PLC-only. Five warm-up seconds excluded from each35-second run. No inference or claim of per-process GPU allocation.

Public GitHub delivery is a reviewed source-only history based on a clean baseline; the full local history and previous evidence remain preserved separately. No credentials, private addresses/configurations, raw logs/data, Unity caches, builds or weights are published.
