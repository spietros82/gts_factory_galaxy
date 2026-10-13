# Current demonstrator: Stage 5 experimental full-frame vision

Stage 5 adds an experimental full-frame bottle detector and image tracking. The corrected locked synthetic test **failed the frozen quality target**: 66/184 visible bottles found (35.9% recall), with all derived cap/fill/label inspection kept uncertain. This is a visualization prototype, not product acceptance. Start `./stage5/start.sh`; stop with `./stage5/stop.sh`. See [Stage 5 README](stage5/README.md), [results](stage5/RESULTS.md), [architecture](stage5/ARCHITECTURE.md), [dependencies/licensing](stage5/DEPENDENCIES.md) and [handover](stage5/HANDOVER.md). Stage 4 remains available independently.

---

## Preserved Stage 4 demonstration

Independent synthetic brewery lines with simulated PLC data, three image inspections per line and same-weight CPU/GPU selection. Native Unity is the primary application.

Start with [Stage 4 README](stage4/README.md), [walkthrough](stage4/DEMO.md), [measured results](stage4/PERFORMANCE.md), [verification](stage4/VERIFICATION.md) and [handover](stage4/HANDOVER.md). One line/CPU is the default. Highest confirmed passing count24; first tested failure48. No industrial capacity or hardware superiority claim.

This branch is source-only and stacked on reviewed Stage3. No private history, builds, weights, datasets, credentials or raw runtime records are included. Dependencies/licensed Unity and frozen local models are required; see [manifest](stage4/DEPENDENCIES.md). Earlier stage source remains in its own branches and stage folders. Stage4 was accepted by Pietro before Stage5.
