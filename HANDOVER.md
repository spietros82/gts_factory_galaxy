# Stage 1 — brewery visual presentation completion

## Delivered

The existing single Factory Galaxy bottling line now reads as a fictional Braemac brewery. Amber glass forms, visible synthetic liquid, reusable Lager/gold, IPA/green and Stout/purple identity materials, wrap labels and matching signs/cartons. Procedural brushed metal, textured belts/epoxy floor/cartons, feet, rails, flow arrows, fixtures and brewery holding vessels. Warm industrial key/cool fill lighting, readable shadows and restrained specular reflections; existing Built-in pipeline retained. No reflection probe/global ambient change that would disturb inspection.

Numbered Infeed/Filler/Capper/Inspection/Pack signs explain operations. Presenter's toolbar supplies product selection and F5–F8 views. Customer view reserves HUD space; machine descriptions explain what to watch. One authoritative process clock; duplicate visuals follow original bottle positions, cap pose and machine motion. Product selection has no production recipe/process effect.

## Run / review

`./presentation/start.sh` / `./presentation/stop.sh` in this project. Native unit braemac-factory-stage1-player; binary builds/stage1/FactoryGalaxy.x86_64. Start reuses the already-running inspection service without restarting or resetting its six-call budget. Stage1 explanations disabled, PLC profile initially selected. No browser URL: primary interface is the native window.

Prior version: stop Stage1, then `./inspection/start.sh`; prior executable/launchers/config remain preserved. Full local source baseline9f9be74, tag stage1-working-baseline-20261013. Dedicated branch stage1-brewery-presentation. Graphics/native measured source18d1692; final docs/test-tool commits recorded in Git history. Local full history stays separate from reviewed GitHub source-only history, since the destination was empty/public and older local commits contain bulk/raw/private context.

## Five-minute walkthrough

1. Overview/Home/F5: name the fictional beer, follow the floor arrows from empty bottle infeed through the five signs.
2. Switch LAGER → IPA → STOUT: show labels, cap/accent colours, contents and signage changing on the same line.
3. F6 Filler: watch bottles stop/fill and heads cycle. F7 Capper: watch cap application and turret movement.
4. F8 Inspection: show the station and simulator-only reject lane. Entry → Evidence displays the preserved original inspection render; it is separate from the new brewery materials. No new AI explanation in Stage1.
5. Pause/resume and Reset replay; return to PLC/Overview/LAGER. The line is synthetic and unchanged in production logic.

## Acceptance

Existing18 Python +17 focused +5 startup checks pass;11 C# process checks +8 new presentation checks pass;11 real native workflow checks pass. These are separate suites, not a single inflated coverage/accuracy number. Desktop1600×900 and1920×1080 native screenshots inspected. Nine pixel comparisons across three fresh fixture poses and three products match original crops/frames/ROI exactly. Synthetic accuracy claims are still limited to the older frozen inspection evaluation, not new brewery visuals.

Controlled rendering:59.994→59.987FPS, mean16.668→16.670ms, p9916.690→16.823ms, sampled peakRSS315.3→333.3MB. Native CPU37.3→52.6% on one-core100% scale; device-wide GPU busy8.48→7.71% in these short runs, not attributable process shares or evidence of GPU optimisation. Background workloads preserved. See PERFORMANCE.md for exact configuration and limits.

## Scope and limitations

One line only. Beer identity is decorative; no ABV/recipe/real brewery claim. Geometry/glass/liquid/shadows/reflections are lightweight illustrative rendering, not optical/process validation. Legacy inspection renders the old bottle/cap appearance; the new view is not independently accuracy-validated. No trained-model change, held-out evaluation, Qwen/Gemma call, inference backend benchmark, PLC integration, extra inspection camera or streaming change. No licences purchased/accepted or external assets downloaded. Prior results and known mobile-streaming failure preserved.

GitHub remains public; reviewed source/assets/docs only, no local history, private settings, credentials, raw data/logs, weights, builds or Unity cache. Stage1 pull request is for review and is not merged. Original local history remains intact. Visual acceptance remains pending until Pietro tries it. Stop at Stage1; no automatic telemetry/camera/multiple-line follow-on.

Performance/native workflow measurements use graphics source18d1692. The subsequent inspection-panel wording explicitly identifies the old render; no scene, camera, inference or procedure change followed the measurement. Final native warning screenshot checked separately.

Screenshots: presentation/screenshots/{before,after,lager,ipa,stout,filler,capper,inspection,desktop-1920}.jpg are reduced copies of actual native PNGs retained under reports/stage1. The before/after pair uses the common measurement camera.


### Stage 1 operator visual acceptance — 2026-10-12T23:42:58.331405+00:00

Pietro reported: “yes, works really well.” Recorded as positive operator visual acceptance of the Stage 1 brewery presentation, superseding the earlier pending status. This is user-reported acceptance, not additional technical verification or approval of inspection accuracy, production reliability, hardware sizing or external/mobile streaming. Published measurements and known limitations are unchanged. No further milestone work started; the existing demo remains available.
