# Stage 1 verification

Completed on the installed A395; not customer acceptance or cross-host proof.

- Native Linux release built with Unity6000.6.5f1, Built-in pipeline. Prior build folders456 files and existing local configurations retained and hash checked.
-18 existing Python regression checks PASS;17 focused-inspection checks PASS;5 existing startup checks PASS. Fake/offline adapters only; no Qwen/Gemma request.
-11 existing C# simulation checks PASS, including healthy flow, conservation, seeded replay, existing faults/alarms and missing observations. Output redirected to Stage1 to preserve earlier results.
-8 new Editor checks PASS: all three product selectors, no process-state mutation, old cap geometry/material unchanged, original/presentation layer separation including dynamic bottles, matching population and unsupported identity handling. No test-count inflation from reruns.
-11 native workflow checks PASS: pause clock, three real product buttons while paused with the same overview, four views, resume/bottle movement/capper animation, reset with identity retained, and actual old-inspector crop with zero explanation calls. Screenshot review checks readability separately from audit fields.
-1600×900 and1920×1080 actual native views inspected. Header, product/view controls and relevant station labels remain readable; the default presentation camera reserves header/footer space. Neighbouring signs can leave the frame during close-up; the selected station remains identifiable.
-Three fresh unscored poses × Lager/IPA/Stout: nine full-frame/neck-crop/ROI comparisons identical to original standalone, zero changed crop pixels. These are three fixture poses repeated under three visual identities, not nine independent accuracy samples. No held-out data, classifier evaluation or training used. Normal native inspector forwarding also checked, but not scored for accuracy.
-Two35s before and two final35s after render runs. Same scene/seed/clock, original comparison camera and viewport,1600×900,60 target,VSync0,4MSAA; first5s frames excluded. All runs packed44 at sim74.75s with zero rejects. Native mean59.994→59.987FPS; frame p9916.690→16.823ms. Short-run result, not a soak or general sizing claim.

## Failures and fixes retained

First build failed on an int/long test-counter assignment; corrected type. The initial geometry Editor test emitted edit-mode Destroy errors; use DestroyImmediate only outside play mode. Initial signs were oversized; fitted glyph advances and reduced text. Initial close-ups put signs behind the HUD; default camera now reserves screen space. Initial pointer automation timed out, while a settled repeated real click succeeded; separate motion/button timing. A later initial pause check read an audit record persisted by the previous run; wait for fresh runtime audit before input. Failed logs/screenshots stay under reports/stage1/raw; none are relabelled as passes.

A relative screenshot-path attempt did not produce the expected project file; subsequent evidence captures use absolute paths. No poor result was replaced with generated imagery. Baseline measurements, initial after checkpoints and final after measurements remain separate.

## Evidence and limits

reports/stage1/native-ui.json; desktop-1920.json; presentation-checks.json; simulation-checks.json; inspection-compatibility-final.json; performance-summary.json; before/after JSON/PNG; product/view/desktop PNGs. Exact commands, frames/resources/logs and failed attempts stay in reports/stage1/raw and runtime/stage1. Public delivery includes selected compressed copies of real screenshots and these documentation summaries, not raw runtime evidence.

Inspection separation retains the old cyan-cap/old-material camera scene with associated simulation IDs; it does not classify the new amber/product visual scene. Upgraded presentation pixels remain unvalidated for accuracy. Frozen model, policies, prompts and split/test records unchanged. No retraining, held-out reuse, budget reset or language-model inference. Streaming was not modified or revalidated; its earlier mobile-data issue remains unresolved. Customer visual acceptance pending.
