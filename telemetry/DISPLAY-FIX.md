# Stage 2 display correction — 13 October 2026

Pietro’s 12-24-58 screenshot showed remnants of the previous machine-data panel beside the 3D viewport. Reproduced natively by switching Combined → Digital twin: the narrow strip between the camera and status panel retained old text/buttons. The camera clears its own rectangle, while the UI had not repainted uncovered margins.

PlcPresentation now paints an opaque background on all four regions outside the actual camera pixel rectangle before drawing panels. The 3D viewport is preserved. No extra camera, materials, simulation, telemetry mapping, inspection configuration, model calls or streaming changes. Same Stage2 launch/stop commands. Original Stage2 build retained locally in builds/stage2-pre-display-fix-20261013; Stage1 remains untouched.

Native release rebuilt with installed Unity6000.6.5f1. Six mode transitions covering Machine data, Digital twin and Combined at each of 1600×900 and1920×1080 passed: ten sampled margin/viewport-gap assertions per resolution, each a uniform opaque dark region. The reproduced Twin gap changed from325 distinct pixel colours (old controls/text) to one. Actual screenshots visually inspected. Pause, new-session reset and Start/Clear blockage buttons pass. All159 prior build/source/model/policy hashes unchanged; shared inspector captured158/inspected158/explanation_calls0 unchanged.

QA limitations/failures retained: the first test rectangle included legitimate rendered floor pixels and was corrected; one1600 run missed a mode keyboard event, and a separate short B-key event was missed. Complete mode check rerun and actual Start/Clear buttons passed without further application changes. These are input-automation failures, not established application keyboard defects. Raw records and originals: reports/stage2/display-fix/. This correction does not repeat the full Stage2 acceptance suite or its rendering benchmark. Previous performance results remain results for the earlier frozen code;16.7ms visible UI samples are not a new statistical benchmark.

Before/after actual app images: screenshots/display-fix-before.jpg and screenshots/display-fix-after.jpg (reduced copies). Acceptance of this correction remains pending Pietro’s visual review. No new milestone started.

API background: Unity documents that GL.Clear is limited to the active viewport: https://docs.unity.com/en-us/engine/6000.5/script-reference/unityengine/gl/clear . The fix uses UI drawing outside the viewport rather than changing camera/inference rendering.
