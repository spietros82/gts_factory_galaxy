# Stage 2 — simulated PLC telemetry milestone

Delivered a working native Machine data / Digital twin / Combined demonstration on the accepted brewery visuals.19typed tags expose the existing single process clock with source simulation timestamps, GUID sessions, quality and calculated-value labels. Station status and filling-head/capper/pusher mechanisms consume the contract through freshness/missing-value mapping. Continuous bottle geometry, fill and cap appearance remain directly simulator-driven; UI and SCHEMA.md state that boundary.

Start/clear outfeed blockage uses the existing slow-pack mechanism and spacing accumulation, with conventional threshold and concise simulated-time timeline. No invented simultaneous line stop. Clear restores cadence and recovery is verified; historical alarms retained until reset. Pause holds the source clock with explicit paused heartbeat; reset creates a new session. Missing/Stale states do not silently imply Running. F9/F10 development injections are opt-in only; normal review launch excludes them.

## Run and show

```bash
./telemetry/start.sh
./telemetry/stop.sh
journalctl --user -u braemac-factory-stage2-player -f
```

Normal default Combined/Lager/healthy/1×/60target, native window; no web URL/new listener. Prior accepted Stage1: stop Stage2, then ./presentation/start.sh; its159-file preservation set and launch/build paths remain untouched. Project guidance and old reports/history preserved. Same installed Unity6000.6.5f1 release/Built-in, no packages, models, drivers or assets installed.

Five minutes: Machine data (select packer/read tags) → Digital twin (follow same stations) → Combined (click machine/tag) → Start blockage (observe gradual accumulation/upstream waiting) → Clear blockage (observe flow recovery) → pause/reset/new session. 1/2/3 modes; B/C/R scenario; Space pause; F5–F8 views; Lager/IPA/Stout visual identity only. Tables/status panels scroll where needed. DEMO.md contains the presenter wording.

## Verification and performance

18original Python,17focused and5startup offline checks pass.11C# process,8Stage1 geometry and15new telemetry checks pass.20actual native checks per desktop resolution1600×900 and1920×1080; repeated suites are not added as distinct coverage. Final display/camera rechecks preserve their checkpoints. Inspector endpoint unavailable test confirms the workflow has no AI dependency. Shared inspector PID41095/captured158/completed158/explanation0 preserved;159 hashed original build/source/model/policy files unchanged.

Final measured native sourced516dd3: two35s runs per version, five warm-up seconds excluded, same1600×900/original fixed overview/full viewport/60target/VSync0/4MSAA/seed42/healthy1×. Stage1→Stage2 meanFPS59.968→59.991; meanframe16.676→16.669ms; p9916.954→16.695ms. Sampled peakRSS330.4→347.6MB; nativeCPU55.4→65.7% (one-core100%); whole-device GPU7.38→9.05%. Small timing difference is not a performance improvement claim. Metrics include host/background activity; no exact GPU shares or overlapping memory sums. Not a soak or sizing benchmark.

Actual screenshots: telemetry/screenshots/{data,twin,combined,blockage,recovery,data-1920,twin-1920,combined-1920}.jpg, reduced unretouched copies. Full PNGs, raw logs/resources/audits and results retained in reports/stage2. Source schema/diagram: SCHEMA.md; results: VERIFICATION.md / PERFORMANCE.md. No new external assets; Stage1 procedural asset provenance remains presentation/ASSETS.md.

## Delivery and limitations

Local full history stays separate from reviewed public history. Stage2 branch stage2-plc-telemetry is a clean source projection parented on accepted public Stage187869ee. Its review PR targets stage1-brewery-presentation (stacked on unmerged PR1); neither PR merged, repository remains public. Private configurations/history, logs/data, weights, builds, Unity cache and environments excluded. Final delivery commit/PR recorded in GITHUB-DELIVERY.md.

No real PLC, OPC UA/MQTT, AI analysis, camera inspection/inference, additional line/camera, streaming work or new operating procedure. Frozen old cyan-cap configuration remains distinct from unvalidated brewery pixels. Simulated unit/state definitions are not physical commissioning evidence. A future real adapter needs independent transport, timing, units, tracking and safety review. Stale contract-driven mechanisms hold while simulator-driven bottles can keep moving, intentionally labelled. The UI displays the latest three timeline events from a bounded32-event session list. No production reliability, cross-hardware performance or independent inspection accuracy claim.

Stage2 implementation complete, operator acceptance pending. Stop at this milestone; no automatic next stage.


Stage2 GitHub closure: PR2 https://github.com/spietros82/gts_factory_galaxy/pull/2 open/unmerged, stacked on Stage1. Reviewed public code9326825, local native d516dd3;163paths verified before documentation-only closure, zero byte/path mismatches. Normal review unit active at1600x900/Combined/Lager/healthy1x, QA flags removed. Prior build/inspection counters preserved. Operator acceptance pending; work stopped at Stage2. See telemetry/GITHUB-DELIVERY.md.


## Stage 2 display correction — 13 October 2026

Fixed retained old panel pixels beside the 3D viewport after view changes by repainting all camera margins with an opaque background. Native rebuilt; six mode transitions at each1600×900/1920×1080 pass margin pixel checks; pause/reset and actual blockage/clear controls pass.159 preserved files and inspector158/158/0 counters unchanged. Prior Stage2 build retained; no inference or simulation/inspection changes. See DISPLAY-FIX.md for actual before/after screenshots, retained automation failures and test limits. Same ./telemetry/start.sh / stop.sh; user correction acceptance pending.
