# Stage4 frozen capacity protocol (before measurements)

One planned cycle; automated performance wall budget≤2700s including warmups, replay and confirmations. No Qwen calls; no training or locked-test reuse. Frozen models/policy/camera contract from Stage3. Linux release6000.6.5f1, Built-in/OpenGLCore,1920×1080,4MSAA,VSync0,target60,overview path fixed (static overview fitting the grid), seed42+line index, coordinated0.05s process tick, speed1. Cyclic Lager/IPA/Stout. Same seeds/configuration between CPU/GPU at a count. Offscreen lines remain active.

## Three workloads

A Full factory: independent line state, full visual updates, three manual camera Render/ReadPixels/PNG views per capture, HTTP transport, crop/decode, frozen inference/policy and bounded evidence writes. Normal station crossing≤0.667three-view batches/s/line, bounded round-robin acquisition queue,2s association expiry; delayed synthetic target reposed at station only for capture; actual rate is constrained by arrival at the station and reported, not assumed. Benchmark acquisition explicitly reposes a real live bottle at the station for each acquisition, then restores its visual transform; this isolates service demand from simulation speed and does not alter process state. No invisible simulated work/dummy arithmetic.

B Rendering-only: same scene/line counts/seeds, acquisition and inference disabled. It does not contain cameras actively rendering.

C Vision-only replay: newly captured integration crops; same weights/preprocessing/policy on CPU/GPU, increasing offered batch rates. Excludes Unity/acquisition/HTTP/evidence storage. Rates cannot establish physical camera capacity.

## Passing criteria and guards

Normal presentation target60FPS, warmed average≥57FPS, frame interval p95≤20ms and p99≤33.34ms. All captured work explicitly accepted/completed or rejected/cancelled with counters; zero queue-overload/native acquisition drops, zero2s deadlines, nonzero inspections for every active line and no line starved (≥1completed batch/measurement for phases≥20s), no upward unbounded queues. Presentation count passing includes BOTH rendering and inspection criteria. GPU availability failures are failures, not hidden fallback. Loaded cold-start and warmup recorded separately.

Software guard48lines,48queued batches,1pending-or-running batch/line,1acquisition batch/frame (round robin),bounded3060-ish image history (configured3072),3×4MiB segments per audit stream. Minimum available RAM16GiB;10s sustained AMD GPU temp1≥85°C or CPU Tctl≥90°C stops phase. CPU vendor Tjmax100°C: https://www.amd.com/en/products/processors/laptop/ryzen/ai-300-series/amd-ryzen-ai-max-plus-395.html ;90°C is conservative project guard. GPU85°C conservative project guard, not asserted vendor maximum. Missing sensors N/A; memory/heartbeat guards still apply. Native heartbeat gap8s, rolling FPS<10 sustained3s, transport>3s, global2700s or phase deadline stop own phase. Independent Python harness/supervisor can terminate ONLY its own child, then start stable one-line CPU app. Prominent Stop benchmark requests cancel, CPU/1line locally. No system changes or unrelated kills.

## Planned sequence

Exploratory ACPU/AGPU and B counts1,3,6,12,24,48 (advance only while prior count passes and resources safe). Each10s warmup+20s measured. At first failure stop that mode's growth; compare CPU/GPU at common tested counts. Confirm highest pass and first fail (or ceiling) twice:10s warmup+60s measurement, bounded by remaining budget. Separate acquisition rate sweep:3lines, CPU/GPU, posed-target benchmark cadence1,2,4,8batches/s/line,5s warmup+15smeasure, stop increases once deadlines/drop/frame criteria fail. Saved-crop replay CPU/GPU rates10,50,100,200,400batches/s,2swarm+8smeasure; stop on2sdeadline/queuebound. All durations are wall clock; replay offered3images/batch, no claim configured rate achieved. Resource limits may shorten cycle; preserve reason/actual interval.

Intervals: frame interval=Unity unscaledDeltaTime; camera Render/readback+encode measured main-thread stopwatch; capture→result=UTC before capture through completed result including render/encode/transport/decode/queue/inference/write; preprocessing/transfer/shader and classifier intervals from frozen backend. CPU/GPU clock synchronisation uncertainty same-hostUTC. Stats p50/p95/p99, sample counts; CPUhostall32logical100%,processonecore100%,RSSresident;GPUwhole-deviceamdgpu sysfs,not task attribution;no overlappingmemorysum. Monitoring1Hz, overhead measured.

## Integration checks separate from quality

New neutral-ID captures, not old locked data:3products×healthy/cap/fill/label/poor-image scenarios, association uniqueness/line removal/reset/stale/duplicate/hidden-metadata rejection/fair queue/no contamination and CPU/GPUscore agreement≤1e-4. Deterministic expected synthetic appearance frozen before capture. Integration mismatches retained; no training/tuning. Old synthetic quality result remains scoped to Stage3 capture; verify equivalent crop differences rather than asserting unchanged pixels by configuration alone.
