# Braemac GTS Factory Galaxy — source baseline

This repository is a reviewed source-only snapshot of the existing synthetic Factory Galaxy demonstration. Local baseline: 9f9be74. The full local history, raw reports, runtime data, private settings, builds, credentials and trained weights remain on Pietro's machine; they are deliberately not published into this public repository.

Unity6000.6.5f1 Linux Mono release / Built-in pipeline. A suitable Unity licence and Linux Build Support are required to build. Original source entry point: ./inspection/build.sh; installed-host launcher: ./inspection/start.sh. Existing pinned local Python dependencies are documented in inspection/DEPENDENCIES.md. Frozen trusted cap-rf weights must be supplied separately with authorisation; they are not bundled. Do not load untrusted pickle/joblib artifacts.

Equipment, imagery and procedures are synthetic/unapproved. No physical controls, real PLC writes or production accuracy claims. The Stage 1 pull request adds presentation only and supplies current launch/verification documentation.
