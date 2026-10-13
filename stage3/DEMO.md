Compact layout revision: [UI-REVISION.md](UI-REVISION.md). Small side previews; Open evidence expands; grouped navigation/line/product/device controls. Original layout can be launched with STAGE3_BUILD_DIR=builds/stage3-original-layout after stopping the player. No new model/benchmark results.

# Five-minute Stage 3 walkthrough

Launch ./stage3/start.sh; use1920×1080. This is a synthetic demonstration, not production inspection.

1. Combined: follow the accepted brewery line. Switch Lager/IPA/Stout; show that PLC tags describe the process while bottle appearance follows the simulator. Machine data/Digital twin/Combined remain available; F5–F8 focus views.
2. Inspection: show cap, visible liquid boundary and label crops of the same bottle. Read target/frame identity, image age, selected and actual inference device. Pause: results become historical; resume. Reset: new session, prior review history retained.
3. Examples → Cap missing, then Inspection: watch the actual missing-cap crop and learned result. These controls alter synthetic appearance only. Try under/overfill and missing/tilted label. Poor image should show Unable to assess, not a pass. Model results can still be wrong outside the narrow development distribution.
4. Failure review: pick a defect or uncertain event. Inspect image, timing and uncertainty. Explain this event requests Qwen explicitly; no per-bottle language calls. Six-call Stage3 verification budget persists, and remaining calls are shown. Language advice cannot modify the vision result or PLC.
5. Select GPU or CPU; next whole inspection batch uses it. Debug: see actual CPU/GPU path, completed inspections versus captures, queue/deadlines, Unity frame statistics and device-wide GPU. These are this appliance’s measurements, not exact GPU allocation or comparisons with another machine. Finish with Healthy/Reset/Combined.

An appearance finding does not prove cap torque/seal/attachment, physical volume, label readability or cause. Operator review remains necessary. No physical equipment connected; no action repairs hardware.
