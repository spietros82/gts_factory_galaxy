# Full-frame evaluation erratum v1.2

This erratum supersedes only the **label validity and test-sequence specification** in the original frozen `stage5/PROTOCOL.md`. It does not change the detector, weights, preprocessing, thresholds, tracker, or acceptance targets.

## Retired captures

- v1.0 used geometry projection with a display-aspect mismatch. Its CPU/GPU inference pass is preserved locally but is invalid and is not a quality result.
- v1.1 corrected square aspect, but the projected labels still counted simulator bottles fully hidden by scene occluders. The images were captured and visually reviewed; they were not passed through the detector.

Both failures remain archived locally; neither informed model/settings selection.

## Corrected v1.2 capture and labels

The camera uses a square aspect and the final presentation-only camera layer, with duplicate legacy geometry and station text excluded. Development sequences `d201`–`d209` and locked sequences `t201`–`t209` contain12 adjacent frames each (216 frames total). Splits are by complete sequence and use distinct seeds/scene conditions. The locked set contains three products, normal scenes, partial occlusion and empty fields.

Evaluator labels are visible pixel extents from a second same-state render with flat per-bottle ID colors and depth/occlusion. A visible object requires at least24 exact mask pixels. Empty frames have no objects. Label colors/IDs, simulator identities, target positions, fault state, crops and expected results are not sent to the detector or runtime service. Representative per-sequence overlays were inspected before the dataset was frozen. The local 435-file dataset manifest has SHA-256 `34336bb18f3a203bb7c7e32dc8ff4d54463d6ba6c1e2170aa554bfd90170bf74`; the sequence plan hash is `c2eb4e7c45a8cc655f06cfcbbd70721604cc1e736301ca58472bdfbb1e97de31`.

After this freeze, the exact locked set was run once through each device. The detector weights/settings remained unchanged. The raw per-frame results and image/label files are retained on the test host and excluded from the public source projection; this erratum intentionally does not distribute held-out examples or evaluator labels.

The corrected result failed the frozen≥90% precision and recall target: 66 true positives,5 false positives and118 missed visible objects across108 test frames. All95 visible objects in partial-occlusion scenes were missed. Do not tune or rerun on this spent locked set. The result is synthetic localization evidence only.
