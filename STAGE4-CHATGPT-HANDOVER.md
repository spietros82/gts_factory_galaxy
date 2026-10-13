# Braemac GTS Factory Galaxy — Stage4 consolidated handover

Compact upload-ready record. PR: https://github.com/spietros82/gts_factory_galaxy/pull/4 . Measured source9ea0b81; final runtime dbc0595. Reviewed public source ancestry is separate from full local history; final public head/archive in local reports/stage4/delivery.json. No secrets, images, weights or raw logs embedded. Acceptance pending Pietro; stop atStage4.


---

# Stage 4 completion summary

Delivered independent synthetic brewery lines in the existing Unity application. The compact resizable interface supports line-count presets/custom guard, cyclic products, per-line PLC state/faults/counters and three controlled image inspections. One coordinated scheduler keeps off-screen lines active. Results retain line/session/bottle/station/frame identity; removal/reset cannot attach old results to new instances. CPU/GPU selection uses unchanged weights and policy.

The software allocation guard is 48; safe default is one line/CPU. The single bounded performance cycle took 30.60 minutes with zero Qwen requests. Highest confirmed presentation pass: **24**. First tested failure: **48**, on frame timing, for complete CPU, complete GPU and rendering-only. The exact boundary is unknown. At 24 lines, normal acquisition completed 31.2 images/s; CPU averaged 57.20–58.91 FPS and GPU 58.89–58.96 FPS.

Faster live acquisition failed at its first rate with explicit missing-target drops; higher live rates are unproven. Saved-crop replay reached the tested ceiling of 1,200 images/s on both devices, excluding camera/rendering/transport/storage. CPU was sufficient for this model; no GPU advantage claimed.

Verification: 60 offline tests, original Unity checks plus 12 multi-line checks, 29 native functional and 7 native closure assertions passed. New 81-crop integration fixtures agreed with expected synthetic outcomes and between CPU/GPU. No retraining, old locked-test evaluation or new accuracy claim. Cross-origin images have small pixel differences; real-camera validation remains necessary.

Preserved previous source/builds/results/models/ledgers. Measurement source is `9ea0b8132c9266778630a93d65a246bd652f3455`; final source/PR IDs are in DELIVERY.md. Original timing-unit error and other failures remain recorded; explicit corrected timing reports do not replace raw evidence. Later safety/metric closure was functionally verified without another capacity cycle.

Launch/stop: README.md. Walkthrough: DEMO.md. Exact results/charts: PERFORMANCE.md and RESULTS.csv. Evidence/failures: VERIFICATION.md. Screenshots: screenshots/. Source-only GitHub delivery excludes private history, raw data, weights, builds and credentials.

Stage 4 is ready for review; acceptance pending Pietro. Known limitations include experimental faster cadence, simulator-assisted image acquisition, bounded/non-reloaded review history and unproven real-camera/industrial reliability. No conclusion about hardware necessity or a cheaper alternative. No Stage 5 started.


---

# Stage 4 handover for Pietro and external ChatGPT

Stage 4 extends the existing Factory Galaxy application. Local branch: `stage4-independent-lines-capacity`. Stage 3 source `ad1f773`, tag `stage3-before-stage4-20261013` and compiled `builds/stage3-stage4-baseline` remain available. GitHub receives a source-only projection onto the reviewed Stage 3 history. See DELIVERY.md for final commits and the stacked PR; nothing is merged.

## What changed

Reusable line instances now have independent simulation state, counters, buffers, faults, sessions, PLC tags and three camera transforms. One scheduler advances every active line, including off-screen lines. Products cycle through Lager, IPA and Stout. The compact resizable interface adds line selection, count presets/custom guard, per-line controls, selected-line evidence and expanded Debug metrics.

`MultiLineClock`, `MultiLineFactory`, `MultiLineCapture` and `MultiLineFixtures` are new. Small compatible changes to FactoryApp, FactoryGeometry and PlcTelemetry preserve the original default. The Stage 4 Python engine supplies a fair bounded queue, current-session registry, unchanged CPU/GPU model adapter and bounded evidence storage. Start/stop/build scripts and an independent benchmark supervisor affect this prototype only.

No model, threshold or preprocessing change; no training, old locked-test reuse, language-model request, streaming change or driver installation.

## Findings to carry forward

- **24 lines passed; 48 was the first tested failure**, with two 60-second confirmations for full CPU, full GPU and rendering-only. Counts between these points were not measured. Default remains one line/CPU.
- At 24 lines, normal acquisition completed **31.2 images/s**, or 10.4 three-view bottle batches/s. CPU averaged 57.20–58.91 FPS; GPU 58.89–58.96 FPS. Trigger-to-result p95 was approximately 438–457 ms, including camera scheduling. All lines received inspections, with no normal-cadence drops/deadline misses.
- At 48 lines, full factory averaged approximately 37 FPS; rendering-only approximately 54 FPS. Scene update and synchronous readback grew while classifier/queue latency stayed short. This suggests a mixed presentation/acquisition constraint, not a demonstrated neural-inference maximum. Exact thread/GPU attribution is unavailable.
- CPU was sufficient for these tiny frozen MLPs. GPU execution was verified on Radeon OpenGL compute, with identical weights; no GPU latency benefit was observed. Saved-crop replay passed the ceiling of **1,200 images/s** on both devices, excluding acquisition, rendering, transport and storage.
- The separate faster acquisition sweep failed at its first rate: 1 batch/line/s on three lines. Whole-phase missing-target drops were 3 CPU images and 6 GPU images. Higher rates were not run. Failure retained; no tuning/retest cycle.
- The measured candidate wrote seconds into `acquisition_wait_ms`. Original records remain unchanged. A version-specific ×1000 reporting correction joins batch IDs to expose trigger-to-result latency. Future writer fixed. Later safety/metric closure is functionally checked, not a second capacity measurement.

## Verification and remaining limits

60 distinct offline tests passed. Original Unity simulation/presentation/telemetry checks (11/8/15) and 12 new multi-line checks passed. Native functional 29/29 and closure 7/7 passed, including service outage/restart while the simulator continued. New 81-crop integration fixtures agreed with their synthetic expected outcomes and between CPU/GPU; maximum score difference 2.3841858e-7. This is integration consistency, not industrial accuracy. Canonical images at different origins differed by at most one pixel-component byte; no byte-identity claim.

Old models, frozen datasets, reports and ledgers remain intact; Qwen ledger still 3/6. Raw evidence is under `reports/stage4/`; public summaries, screenshots and charts under `stage4/`. Performance applies to measured source `9ea0b8132c9266778630a93d65a246bd652f3455`. The original measured Stage 4 binary was replaced by closure builds; source and per-phase metadata survive, but no archived byte-identical candidate binary is claimed. Previous stage builds are preserved.

Historical evidence files persist, but the backend does not reload previous in-memory operator review after restart. Association and delayed target positioning are simulator-assisted. Real optics, lighting, triggering, speed, tracking and independent real-image labels remain unvalidated. Pixels cannot prove volume, torque, seal, readability or cause. No production security, sustained industrial capacity or need for an A395 versus cheaper hardware has been established.

## Demonstration

Run `./stage4/start.sh`; stop with `./stage4/stop.sh`. Default resizable 1600×900, one line/CPU/normal acquisition. Formal comparisons used fixed 1920×1080. Loopback API 8830 supports the native application; it is not a browser dashboard.

Show one line, then three. Select Line02, inspect its PLC tags/camera evidence, block its outfeed and watch its buffer while other lines continue. Clear it, switch CPU/GPU and show actual new execution. Open Debug, then the measured capacity charts. Use Stop benchmark to return to one line/CPU. Follow DEMO.md for the five-minute script.

Pietro's Stage 4 acceptance is pending. Stop here; discuss the findings before authorising another stage.


---

# Stage 4 measured capacity — ASRock A395

One frozen cycle completed in **30.60 minutes (1,836.006 seconds)**, below the 45-minute wall budget. 32 live factory/render/rate phases and 10 saved-crop replay phases. Zero Qwen requests, no training or old held-out evaluation. Measured implementation: `9ea0b8132c9266778630a93d65a246bd652f3455`. Later closure fixes correct timing units, reserve queued frame IDs, recover after service restart, measure full monitoring cost and abort the entire future cycle on a resource/operator stop. They do not change model weights, scene geometry, rendering settings or acquisition scheduling. These saved measurements apply to the frozen candidate; no second capacity cycle was run for closure fixes.

## What passed

The highest tested count satisfying all frozen presentation criteria was **24**, confirmed twice for full CPU, full GPU and rendering-only. **48** was the first tested failure in each mode, confirmed twice. Counts 25–47 were not tested, so the exact boundary is unknown. The software allocation guard is 48; it is not a performance promise. Default one line/CPU/normal cadence remains safe for demonstration. Twenty-four is close to the allowed frame-time margin, not a conservative industrial recommendation.

Criterion: target 60 FPS; warmed mean ≥57 FPS, frame interval p95 ≤20 ms, p99 ≤33.34 ms; zero explicit native drops/deadline misses, every line serviced and selected device actually executing. Frame interval is not GPU render duration. 24-line CPU confirm1 averaged 57.20 FPS: PASS by the predeclared tolerance, not a sustained 60 FPS claim.

|Workload/device|Lines|Repeat|Mean FPS|Frame p95/p99 ms|Images/s|Capture→result p95 ms|Trigger→result p95 ms|Criteria|
|---|---:|---|---:|---:|---:|---:|---:|---|
|full/cpu|24|confirm1|57.20|19.23/22.04|31.2|20.20|456.8|PASS|
|full/cpu|24|confirm2|58.91|18.94/21.75|31.2|20.20|437.9|PASS|
|full/cpu|48|confirm1|37.63|37.24/40.38|62.4|27.76|1533.3|FAIL|
|full/cpu|48|confirm2|36.89|37.73/41.15|62.4|28.05|1559.2|FAIL|
|full/gpu|24|confirm1|58.89|19.10/21.11|31.2|22.53|440.3|PASS|
|full/gpu|24|confirm2|58.96|18.89/21.08|31.2|22.29|437.1|PASS|
|full/gpu|48|confirm1|37.54|37.36/39.88|62.4|31.77|1538.8|FAIL|
|full/gpu|48|confirm2|37.69|37.07/40.05|62.4|31.34|1536.3|FAIL|
|render/cpu|24|confirm1|60.00|16.67/16.67|0.0|0.00|0.0|PASS|
|render/cpu|24|confirm2|58.46|16.67/16.67|0.0|0.00|0.0|PASS|
|render/cpu|48|confirm1|54.11|22.16/24.06|0.0|0.00|0.0|FAIL|
|render/cpu|48|confirm2|54.37|22.03/24.18|0.0|0.00|0.0|FAIL|

Rendering-only has no active capture/inference; its latency/rate zeros above mean not applicable, not instantaneous processing. Normal full-factory confirmation completed 31.2 images/s at 24 lines (10.4 three-view bottle batches/s), and 62.4 images/s at 48 (20.8 batches/s). Each line completed 78 images per 60-second confirmation; no off-screen starvation. Configured ceiling 0.667 batches/line/s is not the achieved station-trigger arrival rate. Actual captured/accepted/completed rates match within each confirmation window. Full runs at 48 failed the presentation target despite meeting inspection criteria. Full run terminal drops and joined trigger/capture 2-second deadline misses were zero.

## Camera waiting and a preserved timing defect

Frozen candidate wrote seconds into a trace field named `acquisition_wait_ms`. Original records and `summary.json` remain unchanged. `correct_saved_timings.py` joins actual batch IDs, explicitly multiplies that field by 1000, and saves `corrected-summary.json` and per-phase joined timing records. Capture→result was already correct milliseconds. Final runtime fixes the writer; this is a reporting correction, not new inference or favourable retesting.

Trigger→result includes the pre-capture scheduling wait; capture→result alone does not. CPU 24 confirmation p95 trigger latency 437.9–456.8 ms, CPU 48 1,533.3–1,559.2 ms; GPU 24 437.1–440.3 ms, GPU 48 1,536.3–1,538.8 ms. Maximum joined trigger interval across the 48 confirmation windows remained below 1.69 s. Joined results do not assign an invented completion to dropped/expired requests; those have explicit drop counters.

## Acquisition-rate sweep: retained failure

At three lines, configured benchmark demand 1 batch/line/s (9 images/s aggregate) was the **first tested rate**. CPU offered/accepted/completed 8.8 images/s; GPU 8.6 images/s in the 15-second measurement window. Whole-phase native drops: CPU 3 images/one bottle batch; GPU 6 images/two batches. Backend accepted all actually submitted images. Inspection/rendering latencies remained short, but the predeclared zero-drop requirement failed. The sweep stopped; 2/4/8 rates were not run.

Native code rejects expired or disappeared target associations. Low measured camera waits and no backend rejections point to target lifetime/association as the likely source. The frozen run did not retain a per-drop reason/target trace, so the exact dropped transition remains unconfirmed; this is not evidence of inference saturation. Raw counters and failure retained; not tuned and rerun. Presenter benchmark cadence is experimental and not recommended as the normal demonstration mode. Increasing simulation speed is not an acquisition-rate benchmark.

## Vision-only replay ceiling, not camera capacity

Nine newly authored healthy crops (three products × three stations); images already in memory; same weights, RGB preprocessing, thresholds and policy. Excludes Unity, live camera render/readback, PNG/HTTP and persistent evidence. 2-second warm-up plus 8-second measurement at 10, 50, 100, 200 and 400 offered batches/s on each device; all passed with zero drops/deadlines. **At least the tested ceiling of 400 batches/s / 1,200 images/s** was achieved; no maximum established.

|Device|Offered/accepted/completed batches/s|Images/s|Replay batch latency mean/p95/p99 ms|Max queue|
|---|---:|---:|---:|---:|
|cpu|400 / 400 / 400|1200|1.200/1.649/1.997|5|
|gpu|400 / 400 / 400|1200|1.814/2.568/4.872|5|

These tiny MLPs do not demonstrate GPU advantage: CPU capture→result was about 20 ms versus GPU 22–23 ms at 24-line normal cadence, and CPU replay p95 was lower at the tested ceiling. GPU dense layers actually execute on Radeon OpenGL compute (verified renderer and shader queries); preprocessing/softmax/policy remain CPU. Model residency/availability alone is not inference execution.

## Bottleneck interpretation and resource use

24-line confirmation host CPU means 12.35–12.74% across all 32 logical processors; native process 367.9–376.7% with one core=100%; device-wide GPU 12.74–15.34%; native RSS 446–459 MB. 48 full-factory host CPU 15.85–16.09%, native 466–474%, device-wide GPU 14.74–20.89%, native RSS 568–583 MB. Rendering-only at 48 averaged about 54 FPS and higher native CPU (645–649%); frame limiting and camera/readback pacing alter the workload, so separate-run subtraction cannot allocate exact task cost.

Exploratory CPU 24→48: visual update mean 3.60→8.17 ms/frame, active three-view ReadPixels+Apply mean 5.89→11.69 ms/batch; inference classifier mean approximately 0.425 ms/image, backend queue p95 approximately 4.2–4.4 ms. Low host CPU and GPU percentages do not exclude a constrained main/render submission thread or readback synchronization. Evidence points to a **mixed native scene/submission and synchronous camera-acquisition bottleneck**, not neural inference saturation. Exact thread/GPU attribution remains unavailable; detailed profiling was outside this milestone.

All factory/rate phase sampled available RAM averages ≥116.63 GiB, max CPU Tctl79°C, GPU temp1 50°C; no resource guard fired. Sampling 1 Hz; brief unsampled excursions are unproven. Device-wide GPU includes desktop/background workloads, never vision-only. Native/backend RSS overlap with shared memory; do not add them as a physical total. Base monitoring averages 7.39–9.51 ms/sample, maximum18.16 ms; original extra Stage4 PID/Tctl overhead was not in that field. Closure adds full monitor timing. No monitoring-off comparison was run, so sampling cost does not prove zero impact.

## Complete configuration and measurement boundaries

ASRock AI BOX-A395/IMB-A395, Ryzen AI Max+395 16-core/32-thread, Radeon8060S, approximately124.94GiB usable shared RAM; Ubuntu24.04.5/kernel7.0.0-38, amdgpu/Mesa25.2.8. Unity6000.6.5f1 LinuxStandalone release/Mono/Built-in/OpenGLCore,1920×1080 fullscreen window,4MSAA,VSync0,target60. Static fitted overview camera; independent grid instances seeded42+index, Lager/IPA/Stout cyclic, speed1/shared0.05s scheduler. Three disabled-between-capture orthographic cameras/line,256×256 rendered frame and160×160 ROI; same frozen Stage3 weights. Python3.12.3/NumPy2.3.5/ModernGL5.12/glcontext3/Pillow11.3,BLAS/OMP2threads.

10-second warmup and20-second exploratory windows;10+60seconds ×two boundary confirmations;5+15seconds rate phases. Cold model creation and time to first native heartbeat separately saved; GPU initialized in every service but only selected backend executes inference. No Qwen/Gemma requests and Ollama `/api/ps` showed no resident models before the cycle. GNOME/UnityHub/Firefox/Fleet/old focused inspector/WebUI/system services left running; old inspector idle158/158. Background process names and unit snapshot retained. No artificial utilisation loads, CPU-mode LLM benchmark or physical hardware comparison.

Frame interval uses Unity unscaled time. Capture interval starts UTC before camera rendering and ends after per-image crop/inference/policy/image writes (audit append follows); trigger interval adds directly measured station-acquisition wait. Transport, queue, preprocessing, transfer, dense inference and shader query intervals separately retained. Shared-host UTC and stopwatch anchoring have clock uncertainty. Replay timing is offered enqueue→completed three-image batch. Rates use completed timestamps within the declared steady window; lifetime UI rates are distinct. Raw p50/p95/p99/sample counts in local phase summaries.

## Evidence and charts

Local immutable evidence: `reports/stage4/capacity/` contains freeze, background snapshot, per-phase commands/configuration/frameCSV/capture traces/requests/results/resources/cold-start/logs, raw summary, explicit corrected summary, replay, boundaries and duration. `RESULTS.csv` is a public source-safe summary without host paths, payloads or weights.

- [Frame time](charts/frame-time.svg)
- [Capture latency](charts/latency.svg) and [trigger latency](charts/trigger-latency.svg)
- [Completed images](charts/throughput.svg)
- [Host CPU](charts/host-cpu.svg), [whole-device GPU](charts/gpu.svg), [native RSS](charts/memory.svg)

Red outlines in charts mark failure of the overall phase criteria, usually frame timing; they do not mean every plotted metric failed. Lines connect tested counts for readability, not measured intermediate counts.

Runs are bounded synthetic demonstrations, not industrial capacity, real-camera accuracy, continuous production reliability or evidence that an A395 is required instead of a cheaper machine. Untested counts, real optics/lighting/triggers/speeds, production data transport/storage and sustained runs remain unproven.


---

# Stage4 verification

Measured candidate9ea0b8132c9266778630a93d65a246bd652f3455, baselinead1f773. No training, locked-test evaluation or language request. Original localhistory/results/builds preserved;4,628protectedfilehashes unchanged before capacity. Final closure checks below apply to the completed source; performance remains scoped to the measured candidate.

-48offline tests PASS:16newStage4 registry/fairness/sessionretirement/duplicate/queue/filebounds/unknown/stale/missing/unavailableGPU/benchmarkQwenprohibition/pause/reset plus14existingStage3 and18originalservice/activity/failure checks. Count is distincttests in the finalsuite, not summedreruns. Rawfinalreports/stage4/regression-tests.txt. Import-path invocation and temporary-directory cleanup race preserved separately; test teardown now waits for ownedworker writes.
-C#Editor actualsharedsimulation/presentation/telemetry checks11/8/15 PASS;12newindependent-line checksPASS (identities,products,tagprefixes,sharedscheduler,independentfaults/buffers,recovery,survivorresize/reset,pause,upperguard). reports/stage4/editor-checks.json andraw/editor-checks.log. These are offlineEditorchecks, not nativeperformance or inference.
-Native functional29assertions PASS: actual1920×1080,1/3/24instances,counters/sessions/cyclicproducts,offscreencompletions,Line02-onlyunderfill/blockage/accumulation/clear,productchanges,pauseallclocks/historicalresults,reset/removal/readdsessionisolation,threepresentationmodes,Debug/review,selected/actualGPUbatch,Stop→1lineCPU,unchangedQwenledger. reports/stage4/native-qa/checks.json andactualPNGcaptures. Initial24linecheck failedstarvation; retainednative-qa-first. Acquisitionqueuefix checkedbeforeperformancefreeze. Earlyresolutionchecks retained; finalwaitsforactualfullscreenclient.
-New authored27batches/81crops:3products×8knownvisibleconditions plus3canonicalLagercapturesatdifferentlineorigins. Expectations/splits neutralcaptureIDs frozenbefore capture underreports/stage4/integration;nooldlockedimages. FrozenCPU/GPUdecisionagreement81/81,expectedfixtureoutcomes81/81,scoremaxdifference2.3841858e-7≤1e-4. Integrationcheck, not populationaccuracy. Exactrecords/images/conflictingfailures retained. Representativecontactsheet manuallyinspected; no training/tuning.
-Cross-linecaptureisolation: onlyselectedtargetlayer10,farclip4,gridspacing12;three canonicalorigins maxpixelcomponentdifference1byte andmaxmean.002735byte acrossallRGBcomponents. Bytehashesnotidentical; this is explicit, no renewedinspectionaccuracyclaim. Originalframe/crop/IDs retained. Otherlinegeometry/lights do not enter controlledcapturelayer. Simulator-assistedassociation/temporarystationpose not realtracking proof.
-ShutdownNullReference from destroyed camera fixed with null guard. The original detailed shutdown trace was overwritten by subsequent capture and is unavailable; its occurrence/fix remains documented. Earlier project results were not affected. Syntaxbuildfailure retained; currentreleasebuildsucceeds withoutnewdependencies.

Saved capacities/confirmation/rates/replay belong to PERFORMANCE.md andcharts, not abovequalitychecks. GPUmodelbackendhardwareGLverified withactualcompletedbatches/shaderqueries; residentmodelisnotactiveinference. Qwenledger remains3/6; older focusedservice/ledgers untouched. No realPLC/camera,productionsecurityorindustrialcapacityapproval.


## Final closure and acceptance record

- **60 distinct offline tests PASS**, final suite:21 Stage4engine +7safety/timing/supervisor +14unchangedStage3 +18original checks. `reports/stage4/final-offline-health.txt`. Earlier module-path invocations are preserved, not counted as extra successful tests. New queued cross-line frame-ID reuse test first failed; raw `frame-reservation-first-failed.txt` retained, then admission reservation fixed. Dedup caches bounded8192batches/24576frames.
- Final Unity release builds and final Editor checks PASS; original11simulation/8presentation/15telemetry plus12multiline assertions. Final log `reports/stage4/raw/final-editor-checks.log`, summary `final-editor-checks.json`. Compiler/build logs retained. The original frozen measured Stage4executable was replaced by the closure build; its source commit and exact per-phase commands/native metadata remain. No byte-identical archived candidate binary is claimed. Earlier Stage1/2/3builds preserved separately.
- Final native29/29 functional assertions PASS again (`reports/stage4/final-native-qa/checks.json`); rerun replaces the accepted functional result rather than inflating counts. Additional **7/7 closure assertions** PASS (`closure-native-qa/checks.json`): joined trigger timing, full monitor timing, service outage with continuing simulator, restart registry/current-session recovery and new CPU inspection. Actual outage screenshot shows N/A resources; no hardware fault reproduction. GPU/new batch verified in native workflow. Screens are actual native captures, not mockups.
- Stop/recovery: native control returns1lineCPU; offline guard result aborts the whole future harness cycle; independent supervisor deadline test terminated only an owned synthetic sleeping child while an unrelated test child remained alive. No unsafe resource limit was induced on this host. No actual temperature/memory guard fired during capacity. Supervisor terminating an unresponsive Unity cannot keep that same process running; wrapper launches a stable replacement. Completed cycle protected from rerun.
- Full/render criteria highest confirmed24, first tested failure48. Normal inspection drops/deadlines0; all lines serviced. Separate faster acquisition fails at first demand due explicit missing-target drops, preserved; no tuning/retry. Saved-crop replay reaches400batches/s/1200images/s ceiling onbothdevices; no physical-camera maximum claim. See PERFORMANCE.md for exact timing/rates/resources and reporting-unit correction.
- Post-cycle changes are safety, metric correctness, recovery and small caption corrections, not model/policy/camera/schedule tuning. Final functional verification is separate from the one performance cycle. No second benchmark or oldheldout test.
- Inspectable historical evidence retained on disk; in-memory operator review is bounded and starts empty on backend restart. Persistence/reloading of previous operator-review sessions is not implemented. Service restart does not reset old Stage3Qwenledger; no calls made. This is a local demonstrator, not a hardened multi-user service.

Stage4 functional implementation and bounded verification complete; presenter benchmark cadence failure remains a known limitation. Pietro's Stage4 acceptance pending. Earlier stage acceptance is preserved. No Stage5 begun.

Earlier closure source commit: `010b83d`; release build succeeded. Full Debug shows trigger latency/oldest acquisition and measured monitoring cost. Completed-cycle wrapper refuses another run before touching running services. All 4,628 protected hashes unchanged (`final-preservation.json`). Final caption probe initially hit a missing startup field; corrected wait uses optional fields, and the actual screenshot was captured. This was QA plumbing, not a simulation failure.

Final metric closure adds two meaningful fake tests (per-line registration denominator and health aggregation), bringing the final distinct suite to60. Native screenshots verify per-line rates/health, visible averaging periods and backend activity state; health-native-qa. These display/counter changes and retired-review clearing are not model/camera/scheduling changes. No additional performance cycle or quality evaluation was run.

Final runtime `dbc0595`:60-test suite PASS, compiled release PASS, final-list-native-qa actual1080p1/3/24screens reviewed. Per-line inspection state and averaging periods visible without horizontal overflow. Old source/build/measurement records remain.


---

# Five-minute presenter walkthrough

1. Start `./stage4/start.sh`. One line/CPU/normal acquisition is the safe initial workload. Say: “Everything here is simulated. The machine signals and three controlled camera images belong to the same line and bottle.” Use Combined, Machine data and Digital twin; F5overview/F6filler/F7capper/F8inspection,Spacepause,Homeoverview. Window may resize; formal measurements use1920×1080.
2. Select3lines. Lager/IPA/Stout are cyclic. Each line has its own counters, buffer and session. SelectLine02 and Selected line. Other lines keep simulating and inspecting when offscreen.
3. Block Line02's outfeed. Watch its buffer/counters and mapped PLC activity; other lines remain healthy. Clear blockage to restore simulated flow. Reset this line creates a new session; old images stay historical. Controls affect the simulator only, never physical equipment.
4. Select Cap displaced, Underfill or Label tilted for this line. Open an actual crop and recorded result. Missing/poor images say Unable to assess. These are synthetic visible appearances; no physical volume, torque/seal, label readability or root-cause proof. Optional Qwen action consumes the preserved budget; no automatic request. Avoid it during this Stage4capacity walkthrough unless you explicitly want to use a remaining request.
5. Switch CPU/GPU, show selected versus actual execution device and completed new batch. Debug shows actual captured/completed rate, queue/deadlines, frame times and host resource counters. Increase lines only within documented tested range. Normal cadence and Benchmark cadence are different workloads. Use Stop benchmark to return to one-lineCPU. Explain CPU/GPUresults honestly: same weights, no fabricated advantage, no physical-camera capacity claim.

Capacity report/charts separate full factory, rendering-only and saved-crop replay. This machine's synthetic demonstration does not establish a need for an A395 over a cheaper computer. Operator acceptance remains pending until Pietro reviews Stage4.


---

# Stage 4 delivery record

- Local branch: `stage4-independent-lines-capacity`.
- Measured source: `9ea0b8132c9266778630a93d65a246bd652f3455`.
- Final runtime source: `dbc0595`; source/configuration hashes in SOURCE-FREEZE.json.
- Public source projection: `c06222f0a3500b1985033e0494a4bc074e0d8cd0`, parent reviewed Stage3 `08afde87cac67cae6edd4bfc5027c15cbef77f89`. A subsequent documentation-only commit records this delivery.
- [Stage 4 PR #4](https://github.com/spietros82/gts_factory_galaxy/pull/4), open/clean, stacked on unmerged Stage3 PR #3. Not merged; public repository visibility unchanged. No private/full local ancestry pushed.
- Preserved local Stage3 source `ad1f773`, tag `stage3-before-stage4-20261013`, compiled `builds/stage3-stage4-baseline`; earlier launchers/results/models remain.

Native review launch `./stage4/start.sh`, stop `./stage4/stop.sh`; default resizable1600×900/1lineCPU/normal acquisition. Own user units `braemac-factory-stage4-player/service`, loopback API8830. Final matching current results were cap aligned, fill within range, label aligned; no physical equipment. QA/benchmark child processes stopped; only the fresh review prototype was left running. Logs via user journal and runtime/stage4-native/player.log.

One 30.60-minute cycle:24 highest confirmed presentation pass;48 first tested failure. Faster acquisition failed at its first demand; higher rates untested. Replay ceiling1,200 images/s excludes acquisition/render/transport/storage. No GPU advantage or industrial capacity claim. Final closure functionally verified; capacity not repeated.

60 distinct offline tests, original Unity checks plus12new,29native functional and7closure assertions passed. 81new synthetic integration crops reviewed once, not old locked-test reuse. All4,628protected file hashes unchanged, existingQwenledger3/6unchanged and zeroStage4calls. Source/model/binary/configuration evidence retained locally in reports/stage4; failures remain available.

Public source archive: `packages/FactoryGalaxy-Stage4-reviewed-source.zip`, generated from the reviewed public tree after delivery documentation. It excludes private records, credentials, weights, datasets, binaries and caches. Archive hash/size, final public commit and content checks are in the local `reports/stage4/delivery.json`; existing licensed Unity/pinned dependencies/frozen models are required. Source portability does not prove performance on another computer.

Stage4 acceptance pending Pietro; noStage5 begun. Exact capacity, acquisition failure, unit correction, resource limits and unproven real-camera reliability in PERFORMANCE.md/VERIFICATION.md. Five-minute walkthrough DEMO.md; actual screenshots screenshots/; charts charts/.

Final runtime closure is `dbc0595` (per-line rates/health, explicit averaging periods, retired-selection clearing and narrow-list fit). The final public PR head is recorded in local delivery.json after the reviewed projection. Earlier public sourcec06222f/documentationd58cd63 are preserved; no force update. Final60-test suite and native display proof supersede the earlier58-test closure, without adding reruns to the count or repeating capacity measurements.
