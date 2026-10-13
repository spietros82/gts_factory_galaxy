# Stage 2 acceptance evidence

Expected checks were written in ACCEPTANCE.md before evaluation. No physical equipment, AI inference, held-out inspection evaluation or request-budget reset.

| Check group | Result / evidence |
|---|---|
| Original Python regression |18 PASS; reports/stage2/raw/python-tests.txt |
| Focused inspector + launcher offline |17 +5 PASS; reports/stage2/raw/inspection-tests.txt; fake/offline only |
| Original C# simulation |11 PASS; simulation-checks.json; seeded flow/conservation/earlier faults preserved |
| Stage1 geometry/products |8 PASS; presentation-checks.json; output redirected to Stage2, old results retained |
| New telemetry C# |15 PASS; telemetry-final-checks.json; typed19tags, units, actual counts/positions, JSON, timestamps, paused heartbeat/new session, missing/stale, controlled healthy-vs-restricted comparison, slowed upstream admissions, recovery and alarm retention |
| Actual native workflow |20 checks PASS at1600×900 and20 PASS at1920×1080; native-1600.json/native-1920.json. Same repeated suite, not40distinct coverage checks |
| Final display corrections |Final-camera-1600/1920.json and *-cleared.png: all modes, clean data-only background, readable fixed inspection boundary, tag association, blockage/recovery rechecks. Not an additional accuracy evaluation |
| No inspector dependency |final-layout-1920.json: loopback inspection endpoint deliberately unavailable, line/modes remained live. Existing service was not stopped |
| Preservation |159 baseline build/source/model/policy files hashed unchanged; inspector service PID41095 unchanged, captured/completed158 unchanged during QA, explanation calls0. preservation-check.json |
| Short rendering |Two35s final runs per version, saved frame/resource distributions; PERFORMANCE.md. No inference benchmark or soak |

Native workflow checks exercise real window buttons/keys and audited actual application state: mode selection, tag→machine, machine→tag, product identity without changing paused process time, four cameras, pause/resume/reset, progressive restriction/accumulation, observed upstream state, clear/recovery, stale withholding with frozen mechanisms while simulator moves, and missing filler Unknown. The controlled C# replay also verifies reduced admission count at the same process time against an unrestricted seeded line; a transient Waiting/Blocked label alone is not proof of an outfeed cause.

Full workflow/sourcea8ead65; final display/sourcefbe388a, final provenance labels/source d516dd3. Adapter/mapping/physics unchanged during UI correction. Final C# check was strengthened to compare admissions, and rerun; rendering measured final native binaryd516dd3. Final screenshots reviewed at both resolutions. Panels can scroll, including the status list when the timeline is long. Tiny world signs are supplementary; readable status/tag panels and close-ups provide the evidence.

## Retained defects and fixes

First visual review showed a wrapped Speed caption and event timeline below tag-table scroll. Caption widened; timeline moved outside the scroll with flexible allocation. Generic packer→True timeline text replaced by explicit conventional accumulation message. Initial Data view disabled the only camera, leaving previous scene pixels at panel edges and a recent frame average near50ms. Existing camera now clears the full data background with scene culling0, retaining the UI cadence; final native screenshot shows16.7ms recent average. No extra camera, render-pipeline or graphics redesign. Initial images/measurement checkpoints/raw audit records remain local; only final source/screenshot copies published. Earlier failed experiments/results unchanged.

## Inspection limits

FocusedInspection.cs, BreweryPresentation.cs, frozen models/policies and accepted Stage1 executable hashes unchanged. No new captures/classifier requests/LLM calls; no evaluation dataset read for tuning, no retraining, no ledger reset. No new pixel equality or accuracy claim: the old cyan-cap configuration is preserved and disabled for this PLC profile, while current presentation pixels remain unvalidated. Stage1's previous nine fixture comparisons remain historical evidence for that stage only.

This is a simulated adapter, not real PLC/transport validation. State semantics are calculated from current simulated activity/queues; a normal local queue can be Blocked without a fault. Snapshot state persists while simulation_paused is explicit. No historical network-loss transport, physical speed calibration, plant safety/production reliability, real-camera performance or other-host sizing proven. Stage2 user acceptance pending until Pietro tries it.
