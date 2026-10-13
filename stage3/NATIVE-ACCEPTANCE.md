# Native acceptance expectations (before GUI verification)

1920×1080 only. No Qwen calls during GUI QA.

- Three presenter modes retained; product selection and F5–F8 views, pause/reset still operate.
- Inspection healthy triplet: same line/session/bottle/batch/captureUTC, three distinct frame IDs and camera station IDs; displayed crops resolve to stored evidence. No crop inferred from class labels.
- Presenter-only cap missing/displaced, under/overfill, missing/tilted label: actual rendered changes visible and corresponding result or honest uncertainty retained. Poor image: uncertain, never pass. Live results are separate from locked quality counts; QA expected fixture state stored only in evaluator report.
- CPU/GPU buttons: selected/actual display, next entire batch consistent device; hardware shader timing/renderer evidence for GPU. No CPU fallback labelled GPU.
- Pause: source clock held, historical label; reset:new session, prior review history retained. Stale>3s/currentserviceoutage cannot imply pass.
- Failure review:event-selected image/timing/IDs, unknown/missing images explicit. Detected defects and uncertain observations distinguishable. Language request manual only; six-call ledger persistent; normal QA0requests.
- Debug: host/own/native CPU denominator, GPUdevicewide source, available temperature/memory, frame percentiles, cameras/captures/completions/queue/deadlines, actual vision and Qwen state; N/A on unavailability.
- Inject bounded invalid input/missing observations/ambiguous association/stale frame via loopback test requests; all abstain or fail visibly. Duplicate request rejected without another observation. Backend unavailable retains factory operation.
- Existing builds/models/datasets/olderledgers unchanged. Independent real tracking, physical measurements, production security and different hardware unproven.
