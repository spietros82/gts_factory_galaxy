# Stage 5 GitHub delivery

- Repository: [spietros82/gts_factory_galaxy](https://github.com/spietros82/gts_factory_galaxy), visibility verified public and unchanged.
- Review: [PR #5 — Stage 5 experimental full-frame vision](https://github.com/spietros82/gts_factory_galaxy/pull/5), open and unmerged. It is stacked on the open Stage 4 PR branch `stage4-independent-lines-capacity`; base commit `4bfb3d0f53656984a89d807ec4cc011596d2079f`.
- Public branch: `stage5-full-frame-vision-public`. The source-only implementation commit created for the PR was `055730493c5ad0a873ffed18129156493cfdbc5a`, parented directly on the public Stage 4 head. This delivery note and the root handover/status references are a documentation-only follow-up on the same PR branch.
- Installed/private branch: `stage5-full-frame-vision`, based on local accepted Stage4 tag `stage4-accepted-before-stage5-20261014` (`585e7b6`). This branch retains full local history and raw evidence; it was not pushed.

The public projection has44 intended files (Unity source/material/shader, Stage5 runtime/source/tests/docs, root status summaries, capacity SVG and two actual synthetic Unity screenshots). Its tree SHA was checked identical to the local source projection before PR creation. It excludes model weights, virtual environments, downloads, raw evaluation frames/labels, runtime records, local service config, binaries/builds/caches, private history and local host/network details. The screenshot files are explicitly curated actual application captures; no evaluator image or label is included.

Git command-line push was unavailable because this environment has no configured Git HTTPS credential. The connected GitHub repository integration created the source-only ref/commit and PR; it did not expose or store a personal access token. No merge, force-push or visibility change occurred.

The PR description prominently states the failed locked recall result and that the demo is not an accept/reject inspection system. Review the diff and evaluate the quality failure before considering any merge.
