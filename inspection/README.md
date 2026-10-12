# Focused single-bottle synthetic cap inspector

Separate launch inside the existing Factory Galaxy project. Preserved native/streaming baseline remains available; this launch does not start/stop its units. No mobile streaming fixes, new scenarios or graphics makeover.

```
cd /home/braemac/GTS_factory_galaxy
./inspection/start.sh
./inspection/stop.sh
journalctl --user -u braemac-factory-inspection-service -u braemac-factory-inspection-player -f
```

The native interface is primary; loopback8810 is its inspection API, not a browser dashboard. Set config.local.json endpoint/model/data paths outside code. Do not expose the API. If the baseline is already running, leave it alone; this build is a separate player/service. Use existing project .venv; no packages or weights downloaded.

Choose Entry and Evidence. A fixed camera triggers once per target at the inspection station. The neck ROI comes from simulator identity/position and fixed geometric dimensions, explicitly simulator-assisted. Pixels only reach the learned classifier. No cap flags, object names/masks, fault labels or scoring truth in runtime inputs. Identity/crop association is not learned tracking or physical camera validation. Missing trigger evidence, ambiguous count, tiny/dark/detail-poor/stale crops abstain. Unknown occlusions can still be missed; the trained uncertain class covers only its declared examples.

Image -> association/localisation -> quality policy -> supervised random forest -> frozen decision -> evidence and optional qwen explanation. RF is trained machine learning on spatial RGB/edge features, not a pretrained deep detector. Classical cyan-centroid heuristic is labelled non-learned and available in config (`backend: classical`, corresponding baseline-policy). Original Gemma runs are preserved in the old baseline and never automatically called here.

See PROTOCOL.md before reading training/test records. 960 images, group-disjoint train576/validation192/test192. No external weights. Training/validation selects the one abstention threshold; locked test runs once. Scores are uncalibrated, not reliability probabilities. Runtime model hash must match frozen policy; only load this trusted project-generated joblib artifact (pickle formats can execute code). Do not accept uploaded models.

No mechanical security, torque, seal integrity or leak-tightness inference. No real PLC/reject action; original conventional simulated rejection remains separate. Language cannot alter findings. Raw requests/replies preserved; unsafe wording/invalid references produce labelled application fallback. Six explanation calls maximum per service session, no automatic retries. Restarting service resets this local demonstration budget; it does not grant licence for automatic extra evaluation.

Portable distribution requires existing pinned dependencies and a trusted local copy of the frozen model. The distribution archive excludes the weight artifact pending project-owner redistribution confirmation; no third-party pretrained licence assumed. Synthetic Unity geometry/assets remain under existing project ownership; package is for Pietro's internal review, not public redistribution. model hash/provenance provided for controlled local copy. Another host/backend is unverified.

## Copied archive / other compatible host

The ZIP excludes learned weights: supply the trusted locally generated `inspection/models/cap-rf.joblib` (SHA256 in policy/training report) only where authorised. Retain original library licences/project asset rights; seek permission before external weight/asset redistribution. No pretrained weights were used. Set `VISION_PYTHON=/path/to/existing/compatible/python` for start.sh. Copy config.example.json to config.local.json, choose an unused loopback port and relative data paths; installed dependencies are listed in DEPENDENCIES.md. The supplied binary requires compatible Linux/OpenGLCore libraries. Editing/building requires Unity6000.6.5f1 and appropriate licence/build support. Do not overwrite the original local or streaming build. No automatic dependency/model installation.

Same-host packaging check explicitly supplies the trusted artifact locally; that does not make the distributed archive a self-contained model bundle or prove another hardware platform. Original Gemma/full-frame runs and new cropped RF results are different tasks/inputs, not a controlled accuracy ablation. New synthetic test figures must not be presented as real inspection reliability.


## Safe repeat launch / port conflicts

`start.sh` reuses this project's running inspector and player, waits for the inspection health contract before launching the player, and serialises rapid start/stop operations. A recently stopped server's TIME_WAIT connections do not block restart. A real listener on the configured port remains protected: the script reports the conflict and exits without stopping it. Inspect ownership with `ss -ltnp '( sport = :8810 )'`; do not kill an unrelated listener. For a separately launched inspector you own, use its original stop method. For an unrelated listener, choose an unused loopback port in `inspection/config.local.json`; the player endpoint follows the same configuration. Changing configuration while the inspector is active requires stopping this prototype first.

A readiness failure gives the journal command; it does not launch a new native player or retry model inference. `flock` (installed util-linux) serialises these scripts. Startup regression checks: `.venv/bin/python -m unittest inspection.startup_tests -v` (or invoke the existing Python interpreter selected by `VISION_PYTHON`; no LLM requests). See reports/inspection/startup-fix-20261013 for the reported failure and subsequent checks. The preserved milestone archive predates this launcher-only patch.
