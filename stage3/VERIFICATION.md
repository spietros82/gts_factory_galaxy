# Stage 3 verification

Protocol written before training/evaluation in PROTOCOL.md. Final1440crops:864train/288validation/288test,36/12/12complete groups,20groups perproduct. Two adjacent crops/class/group remain together; complete group/seed/appearance split before training. Initial1440development captures and24probe crops retained, total2904acquired≤3000; no additional weight downloads. Codex manually inspected36representative training images and probe sheets; not independent annotation. First opaque-glass/correlated fixture defects corrected before training, locked images never used for tuning. Final condition combinations vary independently across groups; narrow scene still permits synthetic shortcuts.

One MLP48 candidate per station, existing scikit-learn training;≈1s totalfit, within30min. Cap196/Fill200/Label130iterations. Fill convergence warning retained, no training retry. Validation-only threshold0.8allstations. Float32 safe NPZ weights, hashes in MODEL.md.72validation-crop device parity comparisons: identical CPU/GPU decisions, maximum score difference4.292e-6. AMD hardware GLrenderer/dispatch timer/result verified; model availability alone not used as proof.

## Locked synthetic result (one run/device)

Each device, each station:24samples/class, four classes,96samples/station. Matrix in class order protocol (healthy,defect1,defect2,uncertain):

```
24  0  0  0
 0 24  0  0
 0  0 24  0
 0  0  0 24
```

All three decidable classes observed precision/recall100%, decidable coverage100%;24/24poor-quality withheld/station,0misseddefects,0healthyfalse rejects. Capmissing→aligned0/24. Perproduct8samples/class/station/device, no observed product-specific errors. CPU/GPU both match the above; not repeated/pooled as extra independent testdata. Sample Wilson95%recall/precision86.20–100%; missingfalseaccept0–13.80%. Adjacent/group correlations make these optimistic as independent intervals. Zero observed error is not zero risk. Declared demo targets PASS; real-camera inspection remains unproven.

Offline13new schema/scope/fakefailure checks pass; original/focused/startup and native results are recorded in delivery closure after execution. Native UI expectations frozen separately NATIVE-ACCEPTANCE.md. Live development initially exposed uncentred fixed crops due interpolated bottle position; crop now computed from bottle-origin geometry, never hidden cap/label/fill state. Earlier uncertain results retained. This is acquisition correction, not model tuning or locked retest. CPU/GPU live/native observations are not automatically truth-scored as quality evaluation.

Qwen verification: at most3planned serial event-selected requests of the permitted6, no retries. Exact inputs/raw replies/provider timings and separate application guard/factual review recorded later. No automatic per-bottle Qwen. All older ledgers/models/datasets/builds preserved. Source-only GitHub projection excludes private/full history, raw logs/data, weights, builds, environments/caches. No service/remote access/streaming changes outside Stage3.

## Delivery closure

Original Python18 / preserved inspection-startup22 / C#11simulation+8presentation+15telemetry checks PASS, separate suites. Native25original assertions include one initial Machine data audit timing failure; correct screenshot and settled boundary assertion/four-view recheck passed. Seven defect/poor-quality fixtures, products, same-bottle identities, actual device batches, pause/reset/history and debug verified at1920×1080. No other supported presentation resolution claimed. Six bounded boundary checks PASS; own service outage kept native clock advancing and displayed unavailable/N/A. Native launch harness initially queried before window creation; bounded window wait added, failure retained. Review list contrast/wrapping and persistent defect retention corrected and inspected; thirteen offline tests include retention after healthy history/restart and ML-versus-mL guard regression.

Qwen exact sequential replies preserved under reports/stage3/qwen: cap6.701s/live validationPASS/useful but unnecessary score framing; fill4.351s/live validationFAIL due application guard false positive on “ML decision”, raw content useful; label3.206s/live validationPASS but omitted misalignment and generic uncertainty. Guard false positive fixed without inference retry; offline saved reply validates, original failed record/fallback untouched. All three vision record snapshots unchanged. References exact on3/3, scope no unsupported physical property/cause claims found; usefulness PARTIAL. Guard is a conservative text/schema/reference check, not a semantic correctness guarantee. Operator scrutiny remains necessary. Report original live quality separately from offline guard replay.

Model qwen3:8b, installed local Ollama, all3done_reason stop, thinkfalse/temp0/seed42/context8192/predict512. Ollama reported6,295,440,588bytes model placement and equal size_vram, recorded read-only; this is provider-reported placement, not independent GPU kernel attribution. First request load2.400s, later0.002s; machine waiting not operator time. No additional explanation calls; remaining verification ledger3/6. Full prompts/raw responses/provider durations/tokens retained, no hidden fault labels in those messages.

Preservation2423/2423initial file hashes unchanged; frozenbackend/policy/protocol/lockedsplit hashes unchanged, two locked-device attempt markers retained. Images/models/builds/oldraw replies/ledgers preserved. Improvements compared to old RF are functionality (three brewery views, same-weight devices, evidence review), not a matched quality/hardware comparison.

Final post-fix measured implementation1f4e52e:59.917–59.950FPS; all four enabled runs78steady inspections/60s,zero drops/stale/deadlines. Total native+replay+monitoring performance1020.058s (17.00min), below20min. Fresh GPU Debug screenshot confirms actual OpenGL device; old comparison checkpoint preserved separately.

Language model metadata: qwen3:8b /8.2B/GGUF/Q4_K_M; exact tag, raw timing/token metadata and provider placement saved read-only.
