# Stage 1 presentation architecture

LineSimulation (unchanged, one clock/seed) drives FactoryGeometry (legacy scene) and BreweryPresentation (presentation scene). The presentation copies original bottle transforms, cap poses and machine motion; only materials/labels/contents appearance varies. It never feeds product names or visual choices into diagnostics.

Legacy geometry and dynamic bottles: layer8. Original key/rim: mask8. FocusedInspection fixed camera: mask8, existing512×384 optics/trigger/ROI/IDs/timestamps. Main camera excludes8. Presentation static/dynamic geometry: layer9 with separate lights restricted to9. Existing global ambient/shadow quality unchanged. No extra inspection camera, inference route or model/backend introduced.

Product identities use shared materials/textures and a small SetProduct interface; later lines could compose this visual component independently, but multiple lines are not implemented. Presenter view buttons/F5–F8 remain local application controls. Stage1 uses the existing inspection service, does not restart it, and disables explanation requests in the native UI/action path. Model/results/procedures remain application-authoritative as before.

The new standalone is built into builds/stage1 and uses its own user unit. Baseline builds/linux, builds/inspection and builds/streaming stay intact. Configuration remains outside compiled runtime paths; no network configuration changes. Raw verification stays local; reviewed source projection is published separately to the pre-existing public GitHub repository.
